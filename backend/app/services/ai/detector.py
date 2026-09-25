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


class Detector:
    """Thin, replaceable adapter around an Ultralytics detection model."""

    def __init__(
        self,
        model_path: Path,
        confidence_threshold: float,
        iou_threshold: float,
        device: str = "cpu",
    ) -> None:
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.device = device
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
        try:
            # Reduce lock time by extracting results quickly
            with self._predict_lock:
                results = model.predict(
                    source=image_bgr,
                    conf=self.confidence_threshold,
                    iou=self.iou_threshold,
                    device=self.device,
                    verbose=False,
                )
        except Exception as exc:
            raise DetectorError(f"Lỗi khi chạy AI inference: {exc}") from exc

        if not results:
            return []
        result = results[0]
        names = result.names if hasattr(result, "names") else self.class_names
        detections: list[Detection] = []
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return detections

        for box in boxes:
            xyxy = box.xyxy[0].detach().cpu().tolist()
            confidence = float(box.conf[0].detach().cpu().item())
            class_id = int(box.cls[0].detach().cpu().item())
            class_name = str(names[class_id] if isinstance(names, (dict, list)) else class_id)
            x1, y1, x2, y2 = (int(round(value)) for value in xyxy)
            detections.append(
                Detection(
                    bbox=(x1, y1, x2, y2),
                    confidence=confidence,
                    class_id=class_id,
                    class_name=class_name,
                )
            )
        return detections
