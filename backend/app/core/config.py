from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


def _csv(name: str, default: str) -> list[str]:
    return [part.strip() for part in os.getenv(name, default).split(",") if part.strip()]


def _extensions(name: str, default: str) -> set[str]:
    return {value.lower() if value.startswith(".") else f".{value.lower()}" for value in _csv(name, default)}


@dataclass(frozen=True)
class Settings:
    app_name: str = "PHÁT HIỆN KHÔNG ĐỘI MŨ"
    api_prefix: str = "/api"

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./helmet_detection.db")
    model_path: Path = field(
        default_factory=lambda: (BACKEND_DIR / os.getenv("MODEL_PATH", "./models/best.pt")).resolve()
    )
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.40"))
    iou_threshold: float = float(os.getenv("IOU_THRESHOLD", "0.50"))
    device: str = os.getenv("DEVICE", "cpu")

    helmet_class_names: list[str] = field(
        default_factory=lambda: _csv("HELMET_CLASS_NAMES", "with helmet,helmet,wearing helmet")
    )
    no_helmet_class_names: list[str] = field(
        default_factory=lambda: _csv(
            "NO_HELMET_CLASS_NAMES", "without helmet,no helmet,no_helmet,without_helmet"
        )
    )
    vehicle_class_names: list[str] = field(
        default_factory=lambda: _csv("VEHICLE_CLASS_NAMES", "motorcycle,motorbike,bike")
    )

    storage_root: Path = field(default_factory=lambda: (BACKEND_DIR / "storage").resolve())
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
    allowed_image_extensions: set[str] = field(
        default_factory=lambda: _extensions("ALLOWED_IMAGE_EXTENSIONS", ".jpg,.jpeg,.png,.bmp,.webp")
    )
    allowed_video_extensions: set[str] = field(
        default_factory=lambda: _extensions("ALLOWED_VIDEO_EXTENSIONS", ".mp4,.avi,.mov,.mkv,.webm,.m4v")
    )

    video_frame_stride: int = max(1, int(os.getenv("VIDEO_FRAME_STRIDE", "1")))
    video_max_width: int = max(320, int(os.getenv("VIDEO_MAX_WIDTH", "1280")))
    track_max_missing: int = max(1, int(os.getenv("TRACK_MAX_MISSING", "18")))
    violation_confirmation_frames: int = max(1, int(os.getenv("VIOLATION_CONFIRMATION_FRAMES", "3")))
    track_max_distance_ratio: float = float(os.getenv("TRACK_MAX_DISTANCE_RATIO", "0.08"))
    cors_origins: list[str] = field(
        default_factory=lambda: _csv(
            "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        )
    )
    jwt_secret: str = os.getenv("JWT_SECRET", "change-this-secret-for-demo-helmet-app")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


settings = Settings()
