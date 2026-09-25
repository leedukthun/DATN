from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Location
from app.schemas.location import LocationCreate, LocationUpdate


def list_locations(db: Session, project_id: int) -> list[Location]:
    statement = (
        select(Location)
        .where(Location.project_id == project_id)
        .order_by(Location.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_location(db: Session, location_id: int, with_sessions: bool = False) -> Location | None:
    statement = select(Location).where(Location.id == location_id)
    if with_sessions:
        statement = statement.options(selectinload(Location.analysis_sessions))
    return db.scalar(statement)


def get_location_by_name(db: Session, project_id: int, name: str) -> Location | None:
    return db.scalar(
        select(Location).where(Location.project_id == project_id, Location.name == name.strip())
    )


def create_location(db: Session, project_id: int, payload: LocationCreate) -> Location:
    location = Location(project_id=project_id, **payload.model_dump())
    location.name = location.name.strip()
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


def update_location(db: Session, location: Location, payload: LocationUpdate) -> Location:
    values = payload.model_dump(exclude_unset=True)
    if "name" in values and values["name"] is not None:
        values["name"] = values["name"].strip()
    for key, value in values.items():
        setattr(location, key, value)
    db.commit()
    db.refresh(location)
    return location


def delete_location(db: Session, location: Location) -> None:
    db.delete(location)
    db.commit()
