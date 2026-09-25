from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import AnalysisSession, Location


def _aggregate(sessions: list[AnalysisSession]) -> dict[str, Any]:
    completed = [item for item in sessions if item.status == "COMPLETED"]
    total_vehicles = sum(item.total_vehicles for item in completed)
    total_violations = sum(item.violation_count for item in completed)
    by_time: dict[str, int] = defaultdict(int)
    by_location: dict[str, int] = defaultdict(int)

    for item in completed:
        slot = f"{item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')}"
        by_time[slot] += item.violation_count
        by_location[item.location.name] += item.violation_count

    time_rows = [
        {"time_slot": key, "violations": value}
        for key, value in sorted(by_time.items(), key=lambda pair: pair[0])
    ]
    location_rows = [
        {"location": key, "violations": value}
        for key, value in sorted(by_location.items(), key=lambda pair: pair[1], reverse=True)
    ]
    peak = max(time_rows, key=lambda row: row["violations"], default=None)
    return {
        "total_sessions": len(completed),
        "total_vehicles": total_vehicles,
        "total_violations": total_violations,
        "violation_rate": round(total_violations / total_vehicles * 100, 2) if total_vehicles else 0.0,
        "by_time_slot": time_rows,
        "peak_time_slot": peak,
        "by_location": location_rows,
    }


def location_statistics(db: Session, location_id: int) -> dict[str, Any]:
    statement = (
        select(AnalysisSession)
        .where(AnalysisSession.location_id == location_id)
        .options(joinedload(AnalysisSession.location))
        .order_by(AnalysisSession.analysis_date.desc())
    )
    sessions = list(db.scalars(statement).unique().all())
    return _aggregate(sessions)


def project_statistics(db: Session, project_id: int) -> dict[str, Any]:
    statement = (
        select(AnalysisSession)
        .join(AnalysisSession.location)
        .where(Location.project_id == project_id)
        .options(joinedload(AnalysisSession.location))
        .order_by(AnalysisSession.analysis_date.desc())
    )
    sessions = list(db.scalars(statement).unique().all())
    return _aggregate(sessions)


def location_hourly_statistics(db: Session, location_id: int) -> dict[str, Any]:
    """Aggregate hourly violations for all sessions at a location."""
    statement = (
        select(AnalysisSession)
        .where(AnalysisSession.location_id == location_id)
        .where(AnalysisSession.status == "COMPLETED")
        .order_by(AnalysisSession.analysis_date.desc())
    )
    sessions = list(db.scalars(statement).all())
    
    hourly_data: dict[str, dict[str, Any]] = {}
    total_violations = 0
    
    for session in sessions:
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
    
    return {
        "total_sessions": len(sessions),
        "total_violations": total_violations,
        "hourly_violations": hourly_violations,
        "peak_hour": peak,
    }

