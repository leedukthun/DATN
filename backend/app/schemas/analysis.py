from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from pydantic import BaseModel, ConfigDict


class MediaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    original_filename: str
    file_type: str
    original_url: str
    result_url: str | None
    status: str
    progress: int
    total_vehicles: int
    helmet_count: int
    no_helmet_count: int
    violation_count: int
    error_message: str | None


class ViolationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    media_id: int
    vehicle_id: str | None
    frame_number: int | None
    timestamp_seconds: float | None
    confidence: float
    status: str
    evidence_url: str
    bbox: list[int] | None
    created_at: datetime


class AnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    project_name: str
    location_id: int
    location_name: str
    analysis_date: date
    start_time: time
    end_time: time
    total_files: int
    processed_files: int
    total_vehicles: int
    helmet_count: int
    no_helmet_count: int
    violation_count: int
    violation_rate: float
    hourly_violations: dict[str, Any] | None
    status: str
    progress: int
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None
    media_files: list[MediaRead] = []
    violations: list[ViolationRead] = []
