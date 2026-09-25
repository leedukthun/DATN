from __future__ import annotations

import shutil

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models import Location, Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def list_projects(db: Session, owner_id: int) -> list[Project]:
    statement = (
        select(Project)
        .where(or_(Project.owner_id == owner_id, Project.owner_id.is_(None)))
        .options(selectinload(Project.locations))
        .order_by(Project.created_at.desc())
    )
    return list(db.scalars(statement).unique().all())


def get_project(db: Session, project_id: int, with_locations: bool = True) -> Project | None:
    statement = select(Project).where(Project.id == project_id)
    if with_locations:
        statement = statement.options(selectinload(Project.locations))
    return db.scalar(statement)


def get_project_by_name(db: Session, name: str, owner_id: int | None) -> Project | None:
    statement = select(Project).where(Project.name == name.strip())
    if owner_id is None:
        statement = statement.where(Project.owner_id.is_(None))
    else:
        statement = statement.where(Project.owner_id == owner_id)
    return db.scalar(statement)


def create_project(db: Session, payload: ProjectCreate, owner_id: int) -> Project:
    project = Project(owner_id=owner_id, name=payload.name.strip(), description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project: Project, payload: ProjectUpdate) -> Project:
    values = payload.model_dump(exclude_unset=True)
    if "name" in values and values["name"] is not None:
        values["name"] = values["name"].strip()
    for key, value in values.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def _cleanup_project_files(project: Project) -> None:
    for location in project.locations:
        for session in location.analysis_sessions:
            for folder in ("uploads", "results", "violations"):
                shutil.rmtree(settings.storage_root / folder / f"session_{session.id}", ignore_errors=True)


def delete_project(db: Session, project: Project) -> None:
    loaded = db.scalar(
        select(Project)
        .where(Project.id == project.id)
        .options(selectinload(Project.locations).selectinload(Location.analysis_sessions))
    )
    if loaded is not None:
        _cleanup_project_files(loaded)
        db.delete(loaded)
    else:
        db.delete(project)
    db.commit()
