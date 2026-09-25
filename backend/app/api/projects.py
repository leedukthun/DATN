from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.access import require_project
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.repositories import projects as repository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.utils.serializers import project_dict

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("")
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [project_dict(project) for project in repository.list_projects(db, current_user.id)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if repository.get_project_by_name(db, payload.name, current_user.id):
        raise HTTPException(status_code=409, detail="Tên dự án đã tồn tại.")
    try:
        project = repository.create_project(db, payload, current_user.id)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tên dự án đã tồn tại.") from exc
    project.locations = []
    return project_dict(project)


@router.get("/{project_id}")
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = require_project(repository.get_project(db, project_id), current_user)
    return project_dict(project)


@router.put("/{project_id}")
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = require_project(repository.get_project(db, project_id, with_locations=False), current_user)
    if payload.name and payload.name.strip() != project.name:
        duplicate = repository.get_project_by_name(db, payload.name, current_user.id)
        if duplicate is not None and duplicate.id != project.id:
            raise HTTPException(status_code=409, detail="Tên dự án đã tồn tại.")
    try:
        project = repository.update_project(db, project, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tên dự án đã tồn tại.") from exc
    return project_dict(project, include_locations=False)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = require_project(repository.get_project(db, project_id, with_locations=False), current_user)
    repository.delete_project(db, project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
