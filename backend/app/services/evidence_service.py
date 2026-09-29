from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from app.services.ai.violation import DetectionKind, SubjectDetection


COLORS: dict[DetectionKind, tuple[int, int, int]] = {
    DetectionKind.NO_HELMET: (40, 40, 230),
    DetectionKind.HELMET: (40, 180, 70),
    DetectionKind.VEHICLE: (230, 140, 20),
    DetectionKind.UNKNOWN: (160, 160, 160),
    DetectionKind.OTHER: (180, 110, 180),
}

LABELS: dict[DetectionKind, str] = {
    DetectionKind.NO_HELMET: "KHONG DOI MU",
    DetectionKind.HELMET: "CO DOI MU",
    DetectionKind.VEHICLE: "XE MAY",
    DetectionKind.UNKNOWN: "CHUA XAC DINH",
    DetectionKind.OTHER: "DOI TUONG",
}


def _clip_bbox(
    bbox: tuple[int, int, int, int], frame_shape: tuple[int, ...]
) -> tuple[int, int, int, int]:
    height, width = frame_shape[:2]
    x1, y1, x2, y2 = bbox
    x1 = max(0, min(width - 1, x1))
    y1 = max(0, min(height - 1, y1))
    x2 = max(x1 + 1, min(width, x2))
    y2 = max(y1 + 1, min(height, y2))
    return x1, y1, x2, y2


def draw_subject(
    frame: np.ndarray,
    subject: SubjectDetection,
    *,
    track_id: int | None = None,
) -> None:
    x1, y1, x2, y2 = _clip_bbox(subject.bbox, frame.shape)
    color = COLORS.get(subject.status, COLORS[DetectionKind.UNKNOWN])
    thickness = max(2, round(max(frame.shape[:2]) / 500))
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

    label = f"{LABELS.get(subject.status, subject.status.value)} {subject.confidence:.2f}"
    if track_id is not None:
        label = f"ID {track_id:03d} | {label}"
    font_scale = max(0.45, min(0.8, max(frame.shape[:2]) / 1200))
    (text_width, text_height), baseline = cv2.getTextSize(
        label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, max(1, thickness - 1)
    )
    top = max(0, y1 - text_height - baseline - 8)
    cv2.rectangle(frame, (x1, top), (min(frame.shape[1], x1 + text_width + 10), y1), color, -1)
    cv2.putText(
        frame,
        label,
        (x1 + 5, y1 - baseline - 3),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (255, 255, 255),
        max(1, thickness - 1),
        cv2.LINE_AA,
    )


def draw_summary(
    frame: np.ndarray,
    *,
    total: int,
    helmet: int,
    no_helmet: int,
    progress_text: str | None = None,
) -> None:
    lines = [
        f"Tong doi tuong: {total}",
        f"Co doi mu: {helmet}",
        f"Khong doi mu: {no_helmet}",
    ]
    if progress_text:
        lines.append(progress_text)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.55
    thickness = 1
    widths = [cv2.getTextSize(line, font, scale, thickness)[0][0] for line in lines]
    panel_width = max(widths, default=0) + 30
    panel_height = 22 * len(lines) + 18
    overlay = frame.copy()
    cv2.rectangle(overlay, (12, 12), (12 + panel_width, 12 + panel_height), (10, 18, 32), -1)
    cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)
    for index, line in enumerate(lines):
        cv2.putText(
            frame,
            line,
            (26, 39 + index * 22),
            font,
            scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA,
        )


def save_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise RuntimeError(f"Không thể lưu ảnh kết quả: {path}")


EVIDENCE_MIN_SIDE = 360
EVIDENCE_MAX_UPSCALE = 4.0
EVIDENCE_BAND_HEIGHT = 34


def _band(width: int, text: str, color: tuple[int, int, int]) -> np.ndarray:
    band = np.full((EVIDENCE_BAND_HEIGHT, width, 3), color, dtype=np.uint8)
    scale = 0.55
    while scale > 0.3 and cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)[0][0] > width - 16:
        scale -= 0.05
    cv2.putText(band, text, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), 1, cv2.LINE_AA)
    return band


def save_evidence_crop(
    frame: np.ndarray,
    subject: SubjectDetection,
    destination: Path,
    *,
    track_id: int | None = None,
    timestamp_seconds: float | None = None,
) -> None:
    x1, y1, x2, y2 = subject.bbox
    for extra_box in (subject.head_bbox, subject.vehicle_bbox):
        if extra_box is not None:
            ex1, ey1, ex2, ey2 = extra_box
            x1, y1, x2, y2 = min(x1, ex1), min(y1, ey1), max(x2, ex2), max(y2, ey2)
    width = max(1, x2 - x1)
    height = max(1, y2 - y1)
    # Heads in CCTV footage are tiny; keep a minimum amount of surrounding context.
    padding_x = max(int(width * 0.45), 40)
    padding_y = max(int(height * 0.55), 40)
    cx1, cy1, cx2, cy2 = _clip_bbox((x1 - padding_x, y1 - padding_y, x2 + padding_x, y2 + padding_y), frame.shape)
    crop = frame[cy1:cy2, cx1:cx2].copy()

    scale = min(EVIDENCE_MAX_UPSCALE, max(1.0, EVIDENCE_MIN_SIDE / max(1, min(crop.shape[:2]))))
    if scale > 1.0:
        crop = cv2.resize(crop, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    def to_crop(box: tuple[int, int, int, int]) -> tuple[int, int]:
        bx1, by1, bx2, by2 = box
        return (int((bx1 - cx1) * scale), int((by1 - cy1) * scale)), (int((bx2 - cx1) * scale), int((by2 - cy1) * scale))

    # Draw outlines only; labels go in separate bands so they never cover the rider's head.
    color = COLORS.get(subject.status, COLORS[DetectionKind.UNKNOWN])
    if subject.vehicle_bbox is not None:
        cv2.rectangle(crop, *to_crop(subject.vehicle_bbox), COLORS[DetectionKind.VEHICLE], 1)
    cv2.rectangle(crop, *to_crop(subject.bbox), color, 2)
    if subject.head_bbox is not None and subject.head_bbox != subject.bbox:
        cv2.rectangle(crop, *to_crop(subject.head_bbox), COLORS[DetectionKind.NO_HELMET], 2)

    header = f"{LABELS.get(subject.status, subject.status.value)} {subject.confidence:.2f}"
    if track_id is not None:
        header = f"ID {track_id:03d} | {header}"
    footer = "VI PHAM: KHONG DOI MU"
    if timestamp_seconds is not None:
        minutes = int(timestamp_seconds // 60)
        seconds = timestamp_seconds - minutes * 60
        footer += f" | {minutes:02d}:{seconds:05.2f}"
    evidence = np.vstack([_band(crop.shape[1], header, color), crop, _band(crop.shape[1], footer, (10, 18, 32))])
    save_image(destination, evidence)
