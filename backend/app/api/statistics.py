from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.access import require_location, require_project
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.repositories.locations import get_location
from app.repositories.projects import get_project
from app.services.statistics_service import location_statistics, location_hourly_statistics, project_statistics

router = APIRouter(tags=["Statistics"])


@router.get("/locations/{location_id}/statistics")
def read_location_statistics(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_location(get_location(db, location_id), current_user)
    return location_statistics(db, location_id)


@router.get("/locations/{location_id}/hourly-statistics")
def read_location_hourly_statistics(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_location(get_location(db, location_id), current_user)
    return location_hourly_statistics(db, location_id)


@router.get("/projects/{project_id}/statistics")
def read_project_statistics(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project(get_project(db, project_id, with_locations=False), current_user)
    return project_statistics(db, project_id)
