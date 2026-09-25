from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import BACKEND_DIR, settings
from app.core.schema import ensure_schema
from app.utils.files import ensure_storage_directories

ensure_storage_directories()
ensure_schema()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Hệ thống phát hiện người điều khiển xe máy không đội mũ bảo hiểm từ ảnh/video.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_prefix)
app.mount("/storage", StaticFiles(directory=settings.storage_root), name="storage")


@app.get("/api/health", tags=["System"])
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "model_exists": settings.model_path.exists(),
        "model_path": str(settings.model_path),
    }


frontend_dist = (BACKEND_DIR.parent / "frontend" / "dist").resolve()
if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend(full_path: str):
        requested = (frontend_dist / full_path).resolve()
        try:
            requested.relative_to(frontend_dist)
        except ValueError:
            return FileResponse(frontend_dist / "index.html")
        if requested.is_file():
            return FileResponse(requested)
        return FileResponse(frontend_dist / "index.html")
else:

    @app.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {
            "message": settings.app_name,
            "api_docs": "/docs",
            "frontend": "Chạy React/Vite tại http://localhost:5173 hoặc build thư mục frontend.",
        }
