from __future__ import annotations

from fastapi import HTTPException, status

from app.models import AnalysisSession, Location, Project, User, Violation


def can_access_project(project: Project | None, user: User) -> bool:
    if project is None:
        return False
    return project.owner_id is None or project.owner_id == user.id


def require_project(project: Project | None, user: User) -> Project:
    if not can_access_project(project, user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dự án.")
    return project


def require_location(location: Location | None, user: User) -> Location:
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy địa điểm.")
    require_project(location.project, user)
    return location


def require_analysis(analysis: AnalysisSession | None, user: User) -> AnalysisSession:
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phiên phân tích.")
    require_location(analysis.location, user)
    return analysis


def require_violation(violation: Violation | None, user: User) -> Violation:
    if violation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dữ liệu vi phạm.")
    require_analysis(violation.session, user)
    return violation
