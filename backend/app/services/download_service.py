from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import defaultdict
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.config import settings
from app.models import AnalysisSession, Location, Violation
from app.utils.files import absolute_storage_path


def _add_file(archive: zipfile.ZipFile, relative_path: str | None, archive_name: str) -> None:
    if not relative_path:
        return
    path = absolute_storage_path(relative_path)
    if path.exists() and path.is_file():
        archive.write(path, archive_name)


def _analysis_payload(analysis: AnalysisSession) -> dict:
    hourly_data = {}
    if analysis.hourly_violations_json:
        try:
            hourly_data = json.loads(analysis.hourly_violations_json)
        except (json.JSONDecodeError, TypeError):
            pass
    
    return {
        "analysis_id": analysis.id,
        "project": analysis.location.project.name,
        "location": analysis.location.name,
        "date": analysis.analysis_date.isoformat(),
        "time_slot": f"{analysis.start_time.strftime('%H:%M')} - {analysis.end_time.strftime('%H:%M')}",
        "status": analysis.status,
        "total_files": analysis.total_files,
        "total_vehicles": analysis.total_vehicles,
        "helmet_count": analysis.helmet_count,
        "no_helmet_count": analysis.no_helmet_count,
        "violation_count": analysis.violation_count,
        "violation_rate": analysis.violation_rate,
        "hourly_violations": hourly_data,
    }


def _write_analysis(archive: zipfile.ZipFile, analysis: AnalysisSession, prefix: str = "") -> None:
    base = f"{prefix}analysis_{analysis.id}"
    archive.writestr(f"{base}/summary.json", json.dumps(_analysis_payload(analysis), ensure_ascii=False, indent=2))

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(
        [
            "violation_id",
            "file",
            "vehicle_id",
            "frame_number",
            "timestamp_seconds",
            "confidence",
            "status",
        ]
    )
    for violation in analysis.violations:
        writer.writerow(
            [
                violation.id,
                violation.media.original_filename,
                violation.vehicle_id or "",
                violation.frame_number if violation.frame_number is not None else "",
                violation.timestamp_seconds if violation.timestamp_seconds is not None else "",
                violation.confidence,
                violation.status,
            ]
        )
    archive.writestr(f"{base}/violations.csv", csv_buffer.getvalue().encode("utf-8-sig"))

    for media in analysis.media_files:
        _add_file(archive, media.original_path, f"{base}/original/{media.original_filename}")
        suffix = Path(media.result_path).suffix if media.result_path else ""
        _add_file(archive, media.result_path, f"{base}/results/{Path(media.original_filename).stem}_result{suffix}")
    for violation in analysis.violations:
        filename = Path(violation.evidence_path).name
        _add_file(archive, violation.evidence_path, f"{base}/violations/{filename}")


def _load_analysis(db: Session, analysis_id: int) -> AnalysisSession | None:
    statement = (
        select(AnalysisSession)
        .where(AnalysisSession.id == analysis_id)
        .options(
            joinedload(AnalysisSession.location).joinedload(Location.project),
            selectinload(AnalysisSession.media_files),
            selectinload(AnalysisSession.violations).joinedload(Violation.media),
        )
    )
    return db.scalar(statement)


def create_analysis_zip(db: Session, analysis_id: int) -> Path | None:
    analysis = _load_analysis(db, analysis_id)
    if analysis is None:
        return None
    output = settings.storage_root / "exports" / f"analysis_{analysis_id}.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        _write_analysis(archive, analysis)
    return output


def create_location_zip(db: Session, location_id: int) -> Path | None:
    location = db.get(Location, location_id)
    if location is None:
        return None
    statement = (
        select(AnalysisSession)
        .where(AnalysisSession.location_id == location_id)
        .options(
            joinedload(AnalysisSession.location).joinedload(Location.project),
            selectinload(AnalysisSession.media_files),
            selectinload(AnalysisSession.violations).joinedload(Violation.media),
        )
        .order_by(AnalysisSession.analysis_date.desc())
    )
    analyses = list(db.scalars(statement).unique().all())
    output = settings.storage_root / "exports" / f"location_{location_id}.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        # Write all analyses
        for analysis in analyses:
            _write_analysis(archive, analysis, prefix=f"{location.name}/")
        
        # Calculate and write location hourly statistics
        hourly_data: dict[str, dict[str, int]] = {}
        total_violations = 0
        
        for session in analyses:
            if session.hourly_violations_json:
                try:
                    data = json.loads(session.hourly_violations_json)
                    if "hourly_violations" in data:
                        for slot_info in data["hourly_violations"]:
                            slot = slot_info["time_slot"]
                            count = slot_info["count"]
                            if slot not in hourly_data:
                                hourly_data[slot] = {"count": 0, "sessions": 0}
                            hourly_data[slot]["count"] += count
                            hourly_data[slot]["sessions"] += 1
                            total_violations += count
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
        
        # Sort by violation count (descending)
        sorted_slots = sorted(
            hourly_data.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        hourly_violations = [
            {
                "time_slot": slot,
                "count": data["count"],
                "sessions": data["sessions"]
            }
            for slot, data in sorted_slots
        ]
        
        peak = hourly_violations[0] if hourly_violations else None
        
        hourly_stats = {
            "total_sessions": len(analyses),
            "total_violations": total_violations,
            "hourly_violations": hourly_violations,
            "peak_hour": peak,
        }
        
        archive.writestr(
            f"{location.name}/hourly_statistics.json",
            json.dumps(hourly_stats, ensure_ascii=False, indent=2)
        )
    
    return output


def create_project_zip(db: Session, project_id: int) -> Path | None:
    statement = (
        select(AnalysisSession)
        .join(AnalysisSession.location)
        .where(Location.project_id == project_id)
        .options(
            joinedload(AnalysisSession.location).joinedload(Location.project),
            selectinload(AnalysisSession.media_files),
            selectinload(AnalysisSession.violations).joinedload(Violation.media),
        )
        .order_by(AnalysisSession.analysis_date.desc())
    )
    analyses = list(db.scalars(statement).unique().all())
    output = settings.storage_root / "exports" / f"project_{project_id}.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    
    if not analyses:
        # Distinguish an empty project from a missing project in the API layer.
        # Create empty zip for empty project
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("README.txt", "Dự án này không có dữ liệu phân tích.\n")
        return output
    
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for analysis in analyses:
            prefix = f"{analysis.location.project.name}/{analysis.location.name}/"
            _write_analysis(archive, analysis, prefix=prefix)
    
    return output
