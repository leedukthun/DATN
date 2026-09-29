from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(slots=True)
class Detection:
    bbox: tuple[int, int, int, int]
    confidence: float
    class_id: int
    class_name: str

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    @property
    def area(self) -> int:
        x1, y1, x2, y2 = self.bbox
        return max(0, x2 - x1) * max(0, y2 - y1)


class DetectorError(RuntimeError):
    pass


def resolve_device(device: str) -> str:
    """'auto' picks CUDA, then Apple MPS, then CPU."""
    if device.strip().lower() != "auto":
        return device
    try:
        import torch
    except ImportError:
        return "cpu"
    if torch.cuda.is_available():
        return "0"
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _tile_origins(width: int, height: int, grid: int, overlap: float) -> list[tuple[int, int, int, int]]:
    tile_w = int(width / (grid - (grid - 1) * overlap))
    tile_h = int(height / (grid - (grid - 1) * overlap))
    origins = []
    for row in range(grid):
        for col in range(grid):
            x = min(width - tile_w, int(col * tile_w * (1 - overlap)))
            y = min(height - tile_h, int(row * tile_h * (1 - overlap)))
            origins.append((x, y, tile_w, tile_h))
    return origins


def _merge(detections: list[Detection], iou_threshold: float = 0.5, containment: float = 0.7) -> list[Detection]:
    """Per-class NMS across tiles; also drops partial boxes cut by a tile edge."""
    kept: list[Detection] = []
    for det in sorted(detections, key=lambda item: item.confidence, reverse=True):
        duplicate = False
        for other in kept:
            if other.class_id != det.class_id:
                continue
            ix1, iy1 = max(det.bbox[0], other.bbox[0]), max(det.bbox[1], other.bbox[1])
            ix2, iy2 = min(det.bbox[2], other.bbox[2]), min(det.bbox[3], other.bbox[3])
            inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
            if inter == 0:
                continue
            smaller = max(1, min(det.area, other.area))
            union = max(1, det.area + other.area - inter)
            if inter / union >= iou_threshold or inter / smaller >= containment:
                duplicate = True
                break
        if not duplicate:
            kept.append(det)
    return kept


class Detector:
    """Thin, replaceable adapter around an Ultralytics detection model."""

    def __init__(
        self,
        model_path: Path,
        confidence_threshold: float,
        iou_threshold: float,
        device: str = "cpu",
        imgsz: int = 640,
        tiles: int = 1,
        tile_overlap: float = 0.25,
        class_filter: list[str] | None = None,
    ) -> None:
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.device = resolve_device(device)
        self.imgsz = imgsz
        # Tiled inference: small, distant heads are enlarged when each tile is scaled to imgsz.
        self.tiles = max(1, tiles)
        self.tile_overlap = tile_overlap
        # Only keep these class names (e.g. "motorcycle" from a general COCO model).
        self.class_filter = [name.lower() for name in class_filter] if class_filter else None
        self._model: Any | None = None
        self._load_lock = threading.Lock()
        self._predict_lock = threading.Lock()

    def _load(self) -> Any:
        if self._model is not None:
            return self._model
        with self._load_lock:
            if self._model is not None:
                return self._model
            if not self.model_path.exists():
                raise DetectorError(f"Không tìm thấy model: {self.model_path}")
            try:
                from ultralytics import YOLO
            except ImportError as exc:
                raise DetectorError(
                    "Chưa cài thư viện ultralytics. Hãy chạy: pip install -r requirements.txt"
                ) from exc
            try:
                self._model = YOLO(str(self.model_path))
            except Exception as exc:  # model deserialization errors vary by version
                raise DetectorError(f"Không thể nạp model '{self.model_path.name}': {exc}") from exc
        return self._model

    @property
    def class_names(self) -> dict[int, str]:
        model = self._load()
        names = getattr(model, "names", {})
        if isinstance(names, list):
            return {index: value for index, value in enumerate(names)}
        return {int(key): str(value) for key, value in dict(names).items()}

    def predict(self, image_bgr: np.ndarray) -> list[Detection]:
        if image_bgr is None or image_bgr.size == 0:
            raise DetectorError("Ảnh đầu vào rỗng hoặc không hợp lệ.")
        model = self._load()
        height, width = image_bgr.shape[:2]
        # The full frame keeps large, close objects intact; tiles recover small ones.
        crops = [(0, 0, image_bgr)]
        if self.tiles > 1:
            crops += [
                (x, y, image_bgr[y : y + h, x : x + w])
                for x, y, w, h in _tile_origins(width, height, self.tiles, self.tile_overlap)
            ]
        classes = None
        if self.class_filter is not None:
            classes = [index for index, name in self.class_names.items() if name.lower() in self.class_filter]
        try:
            with self._predict_lock:
                results = model.predict(
                    source=[crop for _, _, crop in crops],
                    conf=self.confidence_threshold,
                    iou=self.iou_threshold,
                    imgsz=self.imgsz,
                    device=self.device,
                    classes=classes,
                    verbose=False,
                )
        except Exception as exc:
            raise DetectorError(f"Lỗi khi chạy AI inference: {exc}") from exc

        detections: list[Detection] = []
        for (offset_x, offset_y, _), result in zip(crops, results or []):
            names = result.names if hasattr(result, "names") else self.class_names
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue
            for box in boxes:
                xyxy = box.xyxy[0].detach().cpu().tolist()
                confidence = float(box.conf[0].detach().cpu().item())
                class_id = int(box.cls[0].detach().cpu().item())
                class_name = str(names[class_id] if isinstance(names, (dict, list)) else class_id)
                x1, y1, x2, y2 = (int(round(value)) for value in xyxy)
                detections.append(
                    Detection(
                        bbox=(x1 + offset_x, y1 + offset_y, x2 + offset_x, y2 + offset_y),
                        confidence=confidence,
                        class_id=class_id,
                        class_name=class_name,
                    )
                )
        return _merge(detections) if len(crops) > 1 else detections


class CompositeDetector:
    """Head-state detector plus an optional dedicated vehicle detector, behind one predict()."""

    def __init__(self, primary: Detector, vehicle: Detector | None = None) -> None:
        self.primary = primary
        self.vehicle = vehicle

    @property
    def model_path(self) -> Path:
        return self.primary.model_path

    @property
    def device(self) -> str:
        return self.primary.device

    @property
    def class_names(self) -> dict[int, str]:
        names = dict(self.primary.class_names)
        if self.vehicle is not None:
            offset = max(names, default=-1) + 1
            names.update(
                {offset + index: name for index, name in self.vehicle.class_names.items()
                 if self.vehicle.class_filter is None or name.lower() in self.vehicle.class_filter}
            )
        return names

    def predict(self, image_bgr: np.ndarray) -> list[Detection]:
        detections = self.primary.predict(image_bgr)
        if self.vehicle is not None:
            # Offset ids so vehicle classes never collide with the head model's class ids.
            offset = max(self.primary.class_names, default=-1) + 1
            for item in self.vehicle.predict(image_bgr):
                item.class_id += offset
                detections.append(item)
        return detections
