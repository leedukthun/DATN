from __future__ import annotations

import json
from typing import Any

from app.models import AnalysisSession, Location, MediaFile, Project, Violation
from app.utils.files import storage_url


def project_dict(project: Project, *, include_locations: bool = True) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }
    if include_locations:
        data["locations"] = [location_dict(item, include_project=False) for item in project.locations]
    return data


def location_dict(location: Location, *, include_project: bool = True) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": location.id,
        "project_id": location.project_id,
        "name": location.name,
        "description": location.description,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "created_at": location.created_at,
        "updated_at": location.updated_at,
    }
    if include_project and getattr(location, "project", None) is not None:
        data["project_name"] = location.project.name
    return data


def media_dict(media: MediaFile) -> dict[str, Any]:
    return {
        "id": media.id,
        "session_id": media.session_id,
        "original_filename": media.original_filename,
        "file_type": media.file_type,
        "original_url": storage_url(media.original_path),
        "result_url": storage_url(media.result_path),
        "status": media.status,
        "progress": media.progress,
        "total_vehicles": media.total_vehicles,
        "helmet_count": media.helmet_count,
        "no_helmet_count": media.no_helmet_count,
        "violation_count": media.violation_count,
        "error_message": media.error_message,
    }


def violation_dict(violation: Violation) -> dict[str, Any]:
    bbox = None
    if violation.bbox_json:
        try:
            bbox = json.loads(violation.bbox_json)
        except json.JSONDecodeError:
            bbox = None
    return {
        "id": violation.id,
        "session_id": violation.session_id,
        "media_id": violation.media_id,
        "media_filename": violation.media.original_filename if getattr(violation, "media", None) else None,
        "vehicle_id": violation.vehicle_id,
        "frame_number": violation.frame_number,
        "timestamp_seconds": violation.timestamp_seconds,
        "confidence": violation.confidence,
        "status": violation.status,
        "evidence_url": storage_url(violation.evidence_path),
        "bbox": bbox,
        "created_at": violation.created_at,
    }


def analysis_dict(
    analysis: AnalysisSession,
    *,
    include_media: bool = False,
    include_violations: bool = False,
) -> dict[str, Any]:
    location = analysis.location
    project = location.project
    
    hourly_violations = None
    if analysis.hourly_violations_json:
        try:
            hourly_violations = json.loads(analysis.hourly_violations_json)
        except json.JSONDecodeError:
            hourly_violations = None
    
    data: dict[str, Any] = {
        "id": analysis.id,
        "project_id": project.id,
        "project_name": project.name,
        "location_id": location.id,
        "location_name": location.name,
        "analysis_date": analysis.analysis_date,
        "start_time": analysis.start_time,
        "end_time": analysis.end_time,
        "total_files": analysis.total_files,
        "processed_files": analysis.processed_files,
        "total_vehicles": analysis.total_vehicles,
        "helmet_count": analysis.helmet_count,
        "no_helmet_count": analysis.no_helmet_count,
        "violation_count": analysis.violation_count,
        "violation_rate": analysis.violation_rate,
        "hourly_violations": hourly_violations,
        "status": analysis.status,
        "progress": analysis.progress,
        "error_message": analysis.error_message,
        "created_at": analysis.created_at,
        "completed_at": analysis.completed_at,
    }
    if include_media:
        data["media_files"] = [media_dict(item) for item in analysis.media_files]
    if include_violations:
        data["violations"] = [violation_dict(item) for item in analysis.violations]
    return data
