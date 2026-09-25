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


def save_evidence_crop(
    frame: np.ndarray,
    subject: SubjectDetection,
    destination: Path,
    *,
    track_id: int | None = None,
    timestamp_seconds: float | None = None,
) -> None:
    x1, y1, x2, y2 = subject.bbox
    if subject.head_bbox is not None:
        hx1, hy1, hx2, hy2 = subject.head_bbox
        x1, y1, x2, y2 = min(x1, hx1), min(y1, hy1), max(x2, hx2), max(y2, hy2)
    width = max(1, x2 - x1)
    height = max(1, y2 - y1)
    padding_x = int(width * 0.45)
    padding_y = int(height * 0.55)
    crop_box = _clip_bbox((x1 - padding_x, y1 - padding_y, x2 + padding_x, y2 + padding_y), frame.shape)
    cx1, cy1, cx2, cy2 = crop_box
    crop = frame[cy1:cy2, cx1:cx2].copy()

    relative_subject = SubjectDetection(
        bbox=(
            max(0, subject.bbox[0] - cx1),
            max(0, subject.bbox[1] - cy1),
            min(crop.shape[1], subject.bbox[2] - cx1),
            min(crop.shape[0], subject.bbox[3] - cy1),
        ),
        confidence=subject.confidence,
        status=subject.status,
        source_label=subject.source_label,
        head_bbox=None,
    )
    draw_subject(crop, relative_subject, track_id=track_id)
    extra = "VI PHAM: KHONG DOI MU"
    if timestamp_seconds is not None:
        minutes = int(timestamp_seconds // 60)
        seconds = timestamp_seconds - minutes * 60
        extra += f" | {minutes:02d}:{seconds:05.2f}"
    cv2.putText(
        crop,
        extra,
        (12, max(24, crop.shape[0] - 14)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    save_image(destination, crop)
