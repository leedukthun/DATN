from __future__ import annotations

import json
import traceback
from datetime import datetime, time, timezone

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import AnalysisSession, Location, MediaFile, Violation
from app.services.ai.detector import Detector
from app.services.ai.violation import ViolationLogic
from app.services.image_processor import process_image
from app.services.video_processor import process_video
from app.utils.files import absolute_storage_path

_detector: Detector | None = None
_violation_logic: ViolationLogic | None = None


def get_detector() -> Detector:
    global _detector
    # Recreate detector if model_path changed at runtime (e.g., .env updated)
    if _detector is None or getattr(_detector, "model_path", None) != settings.model_path:
        _detector = Detector(
            model_path=settings.model_path,
            confidence_threshold=settings.confidence_threshold,
            iou_threshold=settings.iou_threshold,
            device=settings.device,
        )
    return _detector


def get_violation_logic() -> ViolationLogic:
    global _violation_logic
    if _violation_logic is None:
        _violation_logic = ViolationLogic(
            helmet_names=settings.helmet_class_names,
            no_helmet_names=settings.no_helmet_class_names,
            vehicle_names=settings.vehicle_class_names,
        )
    return _violation_logic


def _load_analysis(db, analysis_id: int) -> AnalysisSession | None:
    statement = (
        select(AnalysisSession)
        .where(AnalysisSession.id == analysis_id)
        .options(
            joinedload(AnalysisSession.location).joinedload(Location.project),
            selectinload(AnalysisSession.media_files),
        )
    )
    return db.scalar(statement)


def _set_media_progress(analysis_id: int, media_id: int, media_index: int, total_media: int, value: int) -> None:
    """Persist video progress in a short-lived transaction so inference never holds a DB lock."""
    try:
        with SessionLocal() as db:
            media = db.get(MediaFile, media_id)
            analysis = db.get(AnalysisSession, analysis_id)
            if media is None or analysis is None:
                return
            media.progress = max(0, min(100, value))
            analysis.progress = max(
                analysis.progress,
                min(99, int(((media_index + media.progress / 100.0) / max(total_media, 1)) * 100)),
            )
            db.commit()
    except Exception:
        # Progress updates are best-effort and must not abort the analysis itself.
        pass


def _refresh_aggregate(analysis_id: int, total_media: int) -> None:
    with SessionLocal() as db:
        analysis = _load_analysis(db, analysis_id)
        if analysis is None:
            return
        finished_files = [item for item in analysis.media_files if item.status in {"COMPLETED", "FAILED"}]
        successful_files = [item for item in analysis.media_files if item.status == "COMPLETED"]
        analysis.processed_files = len(finished_files)
        analysis.total_vehicles = sum(item.total_vehicles for item in successful_files)
        analysis.helmet_count = sum(item.helmet_count for item in successful_files)
        analysis.no_helmet_count = sum(item.no_helmet_count for item in successful_files)
        analysis.violation_count = sum(item.violation_count for item in successful_files)
        analysis.violation_rate = (
            round(analysis.violation_count / analysis.total_vehicles * 100, 2)
            if analysis.total_vehicles
            else 0.0
        )
        analysis.progress = min(99, int(len(finished_files) * 100 / max(total_media, 1)))
        db.commit()


def _calculate_hourly_violations(analysis_id: int) -> None:
    """Calculate violations grouped by hour for the analysis session."""
    with SessionLocal() as db:
        analysis = _load_analysis(db, analysis_id)
        if analysis is None:
            return
        
        # Get all violations for this analysis
        statement = select(Violation).where(Violation.session_id == analysis_id)
        violations = list(db.scalars(statement).all())
        
        # Convert start_time and end_time to total seconds since midnight
        start_seconds = analysis.start_time.hour * 3600 + analysis.start_time.minute * 60 + analysis.start_time.second
        end_seconds = analysis.end_time.hour * 3600 + analysis.end_time.minute * 60 + analysis.end_time.second
        
        # If end_time < start_time, it means it goes past midnight
        crosses_midnight = end_seconds < start_seconds
        if crosses_midnight:
            end_seconds += 24 * 3600
        
        # Create hourly buckets
        hourly_buckets = []
        current_seconds = start_seconds
        while current_seconds < end_seconds:
            bucket_start = current_seconds
            bucket_end = min(current_seconds + 3600, end_seconds)
            
            # Format time string for display
            start_hour = (bucket_start % (24 * 3600)) // 3600
            start_min = (bucket_start % 3600) // 60
            end_hour = (bucket_end % (24 * 3600)) // 3600
            end_min = (bucket_end % 3600) // 60
            
            time_slot = f"{start_hour:02d}:{start_min:02d}-{end_hour:02d}:{end_min:02d}"
            hourly_buckets.append({
                "time_slot": time_slot,
                "start_seconds": bucket_start,
                "end_seconds": bucket_end,
                "count": 0
            })
            
            current_seconds = bucket_end
        
        # Count violations in each hour
        for violation in violations:
            if violation.timestamp_seconds is None:
                continue
            
            # Calculate absolute time of violation (start_time + timestamp)
            violation_absolute_seconds = start_seconds + violation.timestamp_seconds
            
            # Find which bucket this violation belongs to
            for bucket in hourly_buckets:
                if bucket["start_seconds"] <= violation_absolute_seconds < bucket["end_seconds"]:
                    bucket["count"] += 1
                    break
        
        # Create result with sorted buckets
        hourly_violations = [
            {"time_slot": bucket["time_slot"], "count": bucket["count"]}
            for bucket in hourly_buckets
        ]
        
        # Find peak hour
        peak_hour = max(hourly_violations, key=lambda x: x["count"], default=None)
        
        # Create result object
        result = {
            "hourly_violations": hourly_violations,
            "peak_hour": peak_hour,
        }
        
        # Save as JSON
        analysis.hourly_violations_json = json.dumps(result, ensure_ascii=False)
        db.commit()


def process_analysis(analysis_id: int) -> None:
    """Background task entrypoint; inference remains outside API routes and long DB transactions."""
    detector = get_detector()
    violation_logic = get_violation_logic()
    any_failed = False

    with SessionLocal() as db:
        analysis = _load_analysis(db, analysis_id)
        if analysis is None:
            return
        analysis.status = "PROCESSING"
        analysis.progress = 1
        analysis.error_message = None
        for media in analysis.media_files:
            media.status = "PENDING"
            media.progress = 0
            media.error_message = None
        media_ids = [media.id for media in analysis.media_files]
        db.commit()

    for media_index, media_id in enumerate(media_ids):
        # Read only the immutable information needed by the processor, then close the DB session.
        with SessionLocal() as db:
            analysis = _load_analysis(db, analysis_id)
            media = db.get(MediaFile, media_id)
            if analysis is None or media is None:
                continue
            media.status = "PROCESSING"
            media.progress = 1
            db.commit()
            source_path = absolute_storage_path(media.original_path)
            file_type = media.file_type
            original_filename = media.original_filename
            project_id = analysis.location.project.id
            location_id = analysis.location.id
            analysis_date = analysis.analysis_date.isoformat()

        try:
            if file_type == "image":
                result = process_image(
                    source_path=source_path,
                    detector=detector,
                    violation_logic=violation_logic,
                    session_id=analysis_id,
                    media_id=media_id,
                    project_id=project_id,
                    location_id=location_id,
                    analysis_date=analysis_date,
                )
                _set_media_progress(analysis_id, media_id, media_index, len(media_ids), 100)
            elif file_type == "video":
                result = process_video(
                    source_path=source_path,
                    detector=detector,
                    violation_logic=violation_logic,
                    session_id=analysis_id,
                    media_id=media_id,
                    project_id=project_id,
                    location_id=location_id,
                    analysis_date=analysis_date,
                    progress_callback=lambda value, aid=analysis_id, mid=media_id, idx=media_index, total=len(media_ids): _set_media_progress(
                        aid, mid, idx, total, value
                    ),
                )
            else:
                raise ValueError(f"Loại file không hỗ trợ: {file_type}")

            with SessionLocal() as db:
                media = db.get(MediaFile, media_id)
                if media is None:
                    continue
                media.result_path = result.result_path
                media.total_vehicles = result.total_vehicles
                media.helmet_count = result.helmet_count
                media.no_helmet_count = result.no_helmet_count
                media.violation_count = result.violation_count
                media.status = "COMPLETED"
                media.progress = 100
                for item in result.violations:
                    db.add(
                        Violation(
                            session_id=analysis_id,
                            media_id=media_id,
                            vehicle_id=item.vehicle_id,
                            frame_number=item.frame_number,
                            timestamp_seconds=item.timestamp_seconds,
                            confidence=item.confidence,
                            status="NO_HELMET",
                            evidence_path=item.evidence_path,
                            bbox_json=json.dumps(list(item.bbox)),
                        )
                    )
                db.commit()
        except Exception as exc:
            any_failed = True
            with SessionLocal() as db:
                media = db.get(MediaFile, media_id)
                analysis = db.get(AnalysisSession, analysis_id)
                if media is not None:
                    media.status = "FAILED"
                    media.error_message = str(exc)
                    media.progress = 100
                if analysis is not None:
                    message = f"{original_filename}: {exc}"
                    analysis.error_message = (
                        f"{analysis.error_message}\n{message}".strip() if analysis.error_message else message
                    )
                db.commit()
            traceback.print_exc()

        _refresh_aggregate(analysis_id, len(media_ids))
        _calculate_hourly_violations(analysis_id)

    with SessionLocal() as db:
        analysis = _load_analysis(db, analysis_id)
        if analysis is None:
            return
        successful_files = [item for item in analysis.media_files if item.status == "COMPLETED"]
        analysis.status = "FAILED" if any_failed and not successful_files else "COMPLETED"
        if any_failed and successful_files:
            analysis.error_message = (
                "Một số file xử lý thất bại; các file còn lại đã hoàn thành.\n"
                + (analysis.error_message or "")
            ).strip()
        analysis.progress = 100
        analysis.processed_files = len(analysis.media_files)
        analysis.completed_at = datetime.now(timezone.utc)
        db.commit()
