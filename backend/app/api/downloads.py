from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.access import require_analysis, require_location, require_project
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.repositories.analyses import get_analysis
from app.repositories.locations import get_location
from app.repositories.projects import get_project
from app.services.download_service import create_analysis_zip, create_location_zip, create_project_zip

router = APIRouter(prefix="/downloads", tags=["Downloads"])


@router.get("/analyses/{analysis_id}")
def download_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_analysis(get_analysis(db, analysis_id, include_details=False), current_user)
    path = create_analysis_zip(db, analysis_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên phân tích.")
    return FileResponse(path, filename=path.name, media_type="application/zip")


@router.get("/locations/{location_id}")
def download_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_location(get_location(db, location_id), current_user)
    path = create_location_zip(db, location_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy địa điểm.")
    return FileResponse(path, filename=path.name, media_type="application/zip")


@router.get("/projects/{project_id}")
def download_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project(get_project(db, project_id, with_locations=False), current_user)
    path = create_project_zip(db, project_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    if not path.exists():
        raise HTTPException(status_code=500, detail="Không thể tạo file tải xuống.")
    return FileResponse(path, filename=path.name, media_type="application/zip")
