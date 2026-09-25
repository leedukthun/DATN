from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import AnalysisSession, Location, MediaFile, Violation


def list_analyses(
    db: Session,
    *,
    project_id: int | None = None,
    location_id: int | None = None,
    limit: int = 100,
) -> list[AnalysisSession]:
    statement = (
        select(AnalysisSession)
        .options(joinedload(AnalysisSession.location).joinedload(Location.project))
        .order_by(AnalysisSession.created_at.desc())
        .limit(limit)
    )
    if location_id is not None:
        statement = statement.where(AnalysisSession.location_id == location_id)
    elif project_id is not None:
        statement = statement.join(AnalysisSession.location).where(
            AnalysisSession.location.has(project_id=project_id)
        )
    return list(db.scalars(statement).unique().all())


def get_analysis(db: Session, analysis_id: int, include_details: bool = True) -> AnalysisSession | None:
    statement = (
        select(AnalysisSession)
        .where(AnalysisSession.id == analysis_id)
        .options(joinedload(AnalysisSession.location).joinedload(Location.project))
    )
    if include_details:
        statement = statement.options(
            selectinload(AnalysisSession.media_files),
            selectinload(AnalysisSession.violations).joinedload(Violation.media),
        )
    return db.scalar(statement)


def get_media(db: Session, media_id: int) -> MediaFile | None:
    return db.get(MediaFile, media_id)


def get_violation(db: Session, violation_id: int) -> Violation | None:
    statement = (
        select(Violation)
        .where(Violation.id == violation_id)
        .options(
            joinedload(Violation.session)
            .joinedload(AnalysisSession.location)
            .joinedload(Location.project),
            joinedload(Violation.media),
        )
    )
    return db.scalar(statement)
