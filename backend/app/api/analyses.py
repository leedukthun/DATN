from __future__ import annotations

import shutil
from datetime import date, time
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.access import require_analysis, require_location
from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import AnalysisSession, Location, MediaFile, Project, User
from app.repositories.analyses import get_analysis
from app.services.analysis_service import process_analysis
from app.utils.files import safe_filename, save_upload, storage_relative
from app.utils.serializers import analysis_dict

router = APIRouter(prefix="/analyses", tags=["Analysis"])


def _list_query(user_id: int, project_id: int | None, location_id: int | None, limit: int, offset: int = 0):
    statement = (
        select(AnalysisSession)
        .join(AnalysisSession.location)
        .join(Location.project)
        .where(or_(Project.owner_id == user_id, Project.owner_id.is_(None)))
        .options(joinedload(AnalysisSession.location).joinedload(Location.project))
        .order_by(AnalysisSession.created_at.desc(), AnalysisSession.id.desc())
        .limit(max(1, min(limit, 500)))
        .offset(max(0, offset))
    )
    if location_id is not None:
        statement = statement.where(AnalysisSession.location_id == location_id)
    elif project_id is not None:
        statement = statement.where(Location.project_id == project_id)
    return statement


@router.get("")
def list_analyses(
    project_id: int | None = None,
    location_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analyses = list(db.scalars(_list_query(current_user.id, project_id, location_id, limit, offset)).unique().all())
    return [analysis_dict(item) for item in analyses]


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_analysis(
    background_tasks: BackgroundTasks,
    project_id: int = Form(...),
    location_id: int = Form(...),
    analysis_date: date = Form(...),
    start_time: time = Form(...),
    end_time: time = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not files:
        raise HTTPException(status_code=400, detail="Vui lòng chọn ít nhất một ảnh hoặc video.")
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="Giờ kết thúc phải sau giờ bắt đầu.")

    location = db.scalar(
        select(Location).where(Location.id == location_id).options(joinedload(Location.project))
    )
    location = require_location(location, current_user)
    if location.project_id != project_id:
        raise HTTPException(status_code=400, detail="Địa điểm không thuộc dự án đã chọn.")

    invalid = []
    typed_files: list[tuple[UploadFile, str]] = []
    for upload in files:
        extension = Path(upload.filename or "").suffix.lower()
        if extension in settings.allowed_image_extensions:
            typed_files.append((upload, "image"))
        elif extension in settings.allowed_video_extensions:
            typed_files.append((upload, "video"))
        else:
            invalid.append(upload.filename or "không tên")
    if invalid:
        raise HTTPException(
            status_code=415,
            detail=f"Định dạng file không hỗ trợ: {', '.join(invalid)}",
        )

    analysis = AnalysisSession(
        location_id=location_id,
        analysis_date=analysis_date,
        start_time=start_time,
        end_time=end_time,
        total_files=len(typed_files),
        status="PENDING",
        progress=0,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    upload_dir = settings.storage_root / "uploads" / f"session_{analysis.id}"
    try:
        for upload, file_type in typed_files:
            stored_filename = safe_filename(upload.filename or f"upload{Path(upload.filename or '').suffix}")
            destination = upload_dir / stored_filename
            await save_upload(upload, destination)
            db.add(
                MediaFile(
                    session_id=analysis.id,
                    original_filename=Path(upload.filename or stored_filename).name,
                    stored_filename=stored_filename,
                    file_type=file_type,
                    original_path=storage_relative(destination),
                    status="PENDING",
                )
            )
        db.commit()
    except ValueError as exc:
        db.rollback()
        db.delete(analysis)
        db.commit()
        shutil.rmtree(upload_dir, ignore_errors=True)
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        persisted = db.get(AnalysisSession, analysis.id)
        if persisted is not None:
            db.delete(persisted)
            db.commit()
        shutil.rmtree(upload_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Không thể lưu file upload: {exc}") from exc

    background_tasks.add_task(process_analysis, analysis.id)
    loaded = get_analysis(db, analysis.id, include_details=True)
    return analysis_dict(loaded, include_media=True, include_violations=True)


@router.get("/{analysis_id}")
def read_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = require_analysis(get_analysis(db, analysis_id, include_details=True), current_user)
    return analysis_dict(analysis, include_media=True, include_violations=True)


@router.get("/{analysis_id}/status")
def read_analysis_status(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = require_analysis(get_analysis(db, analysis_id, include_details=True), current_user)
    return {
        "id": analysis.id,
        "status": analysis.status,
        "progress": analysis.progress,
        "processed_files": analysis.processed_files,
        "total_files": analysis.total_files,
        "error_message": analysis.error_message,
        "media_files": [
            {
                "id": item.id,
                "original_filename": item.original_filename,
                "status": item.status,
                "progress": item.progress,
                "error_message": item.error_message,
            }
            for item in analysis.media_files
        ],
    }


@router.get("/{analysis_id}/results")
def read_analysis_results(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = require_analysis(get_analysis(db, analysis_id, include_details=True), current_user)
    return analysis_dict(analysis, include_media=True, include_violations=True)
