from fastapi import APIRouter

from app.api import analyses, auth, downloads, locations, projects, statistics, violations

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(locations.router)
api_router.include_router(analyses.router)
api_router.include_router(violations.router)
api_router.include_router(statistics.router)
api_router.include_router(downloads.router)
