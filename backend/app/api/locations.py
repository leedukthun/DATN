from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.access import require_location, require_project
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.repositories import locations as repository
from app.repositories import projects as project_repository
from app.schemas.location import LocationCreate, LocationUpdate
from app.utils.serializers import location_dict

router = APIRouter(tags=["Locations"])


@router.get("/projects/{project_id}/locations")
def list_locations(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project(project_repository.get_project(db, project_id, with_locations=False), current_user)
    return [location_dict(item, include_project=False) for item in repository.list_locations(db, project_id)]


@router.post("/projects/{project_id}/locations", status_code=status.HTTP_201_CREATED)
def create_location(
    project_id: int,
    payload: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project(project_repository.get_project(db, project_id, with_locations=False), current_user)
    if repository.get_location_by_name(db, project_id, payload.name):
        raise HTTPException(status_code=409, detail="Tên địa điểm đã tồn tại trong dự án.")
    location = repository.create_location(db, project_id, payload)
    return location_dict(location, include_project=False)


@router.get("/locations/{location_id}")
def get_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    location = require_location(repository.get_location(db, location_id), current_user)
    return location_dict(location)


@router.put("/locations/{location_id}")
def update_location(
    location_id: int,
    payload: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    location = require_location(repository.get_location(db, location_id), current_user)
    if payload.name and payload.name.strip() != location.name:
        duplicate = repository.get_location_by_name(db, location.project_id, payload.name)
        if duplicate is not None:
            raise HTTPException(status_code=409, detail="Tên địa điểm đã tồn tại trong dự án.")
    location = repository.update_location(db, location, payload)
    return location_dict(location, include_project=False)


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    location = require_location(repository.get_location(db, location_id), current_user)
    repository.delete_location(db, location)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
