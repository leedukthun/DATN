from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.access import require_analysis, require_location, require_violation
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import AnalysisSession, Location, Project, User, Violation
from app.repositories.analyses import get_analysis, get_violation
from app.repositories.locations import get_location
from app.utils.serializers import violation_dict

router = APIRouter(tags=["Violations"])


@router.get("/analyses/{analysis_id}/violations")
def analysis_violations(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_analysis(get_analysis(db, analysis_id, include_details=False), current_user)
    statement = (
        select(Violation)
        .where(Violation.session_id == analysis_id)
        .options(joinedload(Violation.media))
        .order_by(Violation.created_at.desc())
    )
    return [violation_dict(item) for item in db.scalars(statement).unique().all()]


@router.get("/locations/{location_id}/violations")
def location_violations(
    location_id: int,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_location(get_location(db, location_id), current_user)
    statement = (
        select(Violation)
        .join(Violation.session)
        .join(AnalysisSession.location)
        .join(Location.project)
        .where(AnalysisSession.location_id == location_id)
        .where(or_(Project.owner_id == current_user.id, Project.owner_id.is_(None)))
        .options(joinedload(Violation.media))
        .order_by(Violation.created_at.desc())
        .limit(max(1, min(limit, 1000)))
    )
    return [violation_dict(item) for item in db.scalars(statement).unique().all()]


@router.get("/violations/{violation_id}")
def read_violation(
    violation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    violation = require_violation(get_violation(db, violation_id), current_user)
    return violation_dict(violation)
