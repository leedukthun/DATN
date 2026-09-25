from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue
from threading import Thread

import cv2
import numpy as np

from app.core.config import settings
from app.services.ai.detector import Detector
from app.services.ai.tracker import CentroidTracker
from app.services.ai.violation import DetectionKind, ViolationLogic
from app.services.evidence_service import draw_subject, draw_summary, save_evidence_crop
from app.services.processing_types import ProcessResult, ViolationArtifact
from app.utils.files import storage_relative

ProgressCallback = Callable[[int], None]


def _resize_frame(frame):
    height, width = frame.shape[:2]
    if width <= settings.video_max_width:
        return frame
    ratio = settings.video_max_width / width
    return cv2.resize(frame, (settings.video_max_width, int(height * ratio)), interpolation=cv2.INTER_AREA)


def _open_writer(path: Path, fps: float, size: tuple[int, int]) -> cv2.VideoWriter:
    path.parent.mkdir(parents=True, exist_ok=True)
    for codec in ("avc1", "mp4v"):
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*codec), fps, size)
        if writer.isOpened():
            return writer
        writer.release()
    raise RuntimeError("Không thể khởi tạo bộ ghi video MP4 trên máy này.")


class _FrameWriter(Thread):
    """Non-blocking frame writer to disk."""

    def __init__(self, writer: cv2.VideoWriter, queue: Queue):
        super().__init__(daemon=True)
        self.writer = writer
        self.queue = queue
        self.running = True

    def run(self):
        while self.running:
            frame = self.queue.get()
            if frame is None:
                break
            self.writer.write(frame)


class _EvidenceSaver(Thread):
    """Async evidence image saver."""

    def __init__(self, queue: Queue):
        super().__init__(daemon=True)
        self.queue = queue
        self.running = True

    def run(self):
        while self.running:
            task = self.queue.get()
            if task is None:
                break
            frame, subject, path, track_id, timestamp = task
            try:
                save_evidence_crop(frame, subject, path, track_id=track_id, timestamp_seconds=timestamp)
            except Exception:
                pass


def process_video(
    *,
    source_path: Path,
    detector: Detector,
    violation_logic: ViolationLogic,
    session_id: int,
    media_id: int,
    project_id: int,
    location_id: int,
    analysis_date: str,
    progress_callback: ProgressCallback | None = None,
) -> ProcessResult:
    capture = cv2.VideoCapture(str(source_path))
    if not capture.isOpened():
        raise ValueError(f"Không thể mở video: {source_path.name}")

    total_frames = max(0, int(capture.get(cv2.CAP_PROP_FRAME_COUNT)))
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    if fps <= 0 or fps > 240:
        fps = 25.0

    ok, first_frame = capture.read()
    if not ok or first_frame is None:
        capture.release()
        raise ValueError(f"Video không có frame hợp lệ: {source_path.name}")
    first_frame = _resize_frame(first_frame)
    frame_height, frame_width = first_frame.shape[:2]

    result_path = settings.storage_root / "results" / f"session_{session_id}" / f"media_{media_id}.mp4"
    writer = _open_writer(result_path, fps, (frame_width, frame_height))

    # Async IO threads for non-blocking writes
    write_queue: Queue = Queue(maxsize=15)
    frame_writer = _FrameWriter(writer, write_queue)
    frame_writer.start()

    evidence_queue: Queue = Queue(maxsize=10)
    evidence_saver = _EvidenceSaver(evidence_queue)
    evidence_saver.start()

    tracker = CentroidTracker(
        max_missing=settings.track_max_missing,
        max_distance_ratio=settings.track_max_distance_ratio,
        confirmation_frames=settings.violation_confirmation_frames,
    )
    evidence_dir = (
        settings.storage_root
        / "violations"
        / analysis_date
        / f"project_{project_id}"
        / f"location_{location_id}"
        / f"session_{session_id}"
    )
    evidence_dir.mkdir(parents=True, exist_ok=True)

    violations: list[ViolationArtifact] = []
    saved_tracks: set[int] = set()
    last_progress = -1
    
    # Honor the explicitly configured sampling rate, regardless of video length.
    adaptive_stride = settings.video_frame_stride

    frame_index = 0
    current_frame = first_frame
    try:
        while True:
            infer_this_frame = frame_index % adaptive_stride == 0
            annotated = current_frame.copy()
            
            if infer_this_frame:
                detections = detector.predict(current_frame)
                subjects = violation_logic.build_subjects(detections)
                tracked_subjects = tracker.update(subjects, current_frame.shape)

                for tracked in tracked_subjects:
                    draw_subject(annotated, tracked.subject, track_id=tracked.track_id)
                    if (
                        tracked.first_no_helmet
                        and tracked.track_id not in saved_tracks
                    ):
                        saved_tracks.add(tracked.track_id)
                        timestamp_seconds = frame_index / fps
                        evidence_path = evidence_dir / (
                            f"media_{media_id}_track_{tracked.track_id:05d}_frame_{frame_index:08d}.jpg"
                        )
                        # Async evidence saving
                        evidence_queue.put(
                            (current_frame, tracked.subject, evidence_path, tracked.track_id, timestamp_seconds)
                        )
                        violations.append(
                            ViolationArtifact(
                                confidence=tracked.subject.confidence,
                                evidence_path=storage_relative(evidence_path),
                                bbox=tracked.subject.bbox,
                                vehicle_id=f"V{tracked.track_id:05d}",
                                frame_number=frame_index,
                                timestamp_seconds=timestamp_seconds,
                            )
                        )

                total, helmet, no_helmet = tracker.summary()
                draw_summary(
                    annotated,
                    total=total,
                    helmet=helmet,
                    no_helmet=no_helmet,
                    progress_text=f"Frame {frame_index}",
                )
            
            # Async frame writing
            try:
                write_queue.put(annotated, timeout=1.0)
            except Exception:
                writer.write(annotated)

            frame_index += 1
            if total_frames > 0:
                progress = min(99, int(frame_index * 100 / total_frames))
                if progress != last_progress and (progress % 2 == 0 or progress > 96):
                    last_progress = progress
                    if progress_callback:
                        progress_callback(progress)

            ok, next_frame = capture.read()
            if not ok or next_frame is None:
                break
            current_frame = _resize_frame(next_frame)
    finally:
        capture.release()
        
        # Drain queue and shutdown async writers
        write_queue.put(None)
        frame_writer.join(timeout=5.0)
        writer.release()
        
        evidence_queue.put(None)
        evidence_saver.join(timeout=5.0)

    if progress_callback:
        progress_callback(100)
    total, helmet, no_helmet = tracker.summary()
    return ProcessResult(
        result_path=storage_relative(result_path),
        total_vehicles=total,
        helmet_count=helmet,
        no_helmet_count=no_helmet,
        violations=violations,
    )
