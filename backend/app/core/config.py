from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


def _csv(name: str, default: str) -> list[str]:
    return [part.strip() for part in os.getenv(name, default).split(",") if part.strip()]


def _bool(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _zones(name: str) -> list[tuple[float, float, float, float]]:
    """Parse "x1,y1,x2,y2;x1,y1,x2,y2" with coordinates normalized to 0..1."""
    zones: list[tuple[float, float, float, float]] = []
    for chunk in os.getenv(name, "").split(";"):
        parts = [part.strip() for part in chunk.split(",") if part.strip()]
        if len(parts) != 4:
            continue
        x1, y1, x2, y2 = (float(part) for part in parts)
        zones.append((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
    return zones


def _optional_path(name: str, default: str) -> Path | None:
    value = os.getenv(name, default).strip()
    return (BACKEND_DIR / value).resolve() if value else None


def _extensions(name: str, default: str) -> set[str]:
    return {value.lower() if value.startswith(".") else f".{value.lower()}" for value in _csv(name, default)}


@dataclass(frozen=True)
class Settings:
    app_name: str = "PHÁT HIỆN KHÔNG ĐỘI MŨ"
    api_prefix: str = "/api"

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./helmet_detection.db")
    model_path: Path = field(
        default_factory=lambda: (BACKEND_DIR / os.getenv("MODEL_PATH", "./models/best_3class.pt")).resolve()
    )
    # General COCO model used only to find motorbikes; a head on a motorbike is a rider.
    # Its "motorcycle" class is far more reliable than the helmet model's "bike".
    # Leave VEHICLE_MODEL_PATH empty to disable.
    vehicle_model_path: Path | None = field(
        default_factory=lambda: _optional_path("VEHICLE_MODEL_PATH", "./models/yolo11s.pt")
    )
    vehicle_model_classes: list[str] = field(default_factory=lambda: _csv("VEHICLE_MODEL_CLASSES", "motorcycle"))
    # Motorbikes are much larger than heads, so the full frame alone is usually enough.
    vehicle_model_tiles: int = max(1, int(os.getenv("VEHICLE_MODEL_TILES", "1")))
    vehicle_confidence_threshold: float = float(os.getenv("VEHICLE_CONFIDENCE_THRESHOLD", "0.25"))
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
    iou_threshold: float = float(os.getenv("IOU_THRESHOLD", "0.50"))
    device: str = os.getenv("DEVICE", "auto")
    # Heads are only ~15-35px in CCTV footage; 640 shrinks them below what the model can see.
    inference_imgsz: int = max(320, int(os.getenv("INFERENCE_IMGSZ", "1280")))
    # Split each frame into an NxN grid (plus the full frame) to recover small, distant riders.
    inference_tiles: int = max(1, int(os.getenv("INFERENCE_TILES", "2")))
    # Frames a lost track keeps its box on screen, to bridge detector misses.
    track_display_hold: int = max(0, int(os.getenv("TRACK_DISPLAY_HOLD", "12")))

    helmet_class_names: list[str] = field(
        default_factory=lambda: _csv("HELMET_CLASS_NAMES", "with helmet,helmet,wearing helmet")
    )
    no_helmet_class_names: list[str] = field(
        default_factory=lambda: _csv(
            "NO_HELMET_CLASS_NAMES", "without helmet,no helmet,no_helmet,without_helmet"
        )
    )
    vehicle_class_names: list[str] = field(
        default_factory=lambda: _csv("VEHICLE_CLASS_NAMES", "bike,biker,motorcycle,motorbike")
    )

    # When the model has a vehicle class, only heads that sit on a vehicle count as riders.
    # This filters out pedestrians, traffic signs and cargo detected as heads.
    require_vehicle_association: bool = _bool("REQUIRE_VEHICLE_ASSOCIATION", "true")
    ignore_zones: list[tuple[float, float, float, float]] = field(default_factory=lambda: _zones("IGNORE_ZONES"))

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
    violation_window_frames: int = max(1, int(os.getenv("VIOLATION_WINDOW_FRAMES", "60")))
    violation_min_ratio: float = float(os.getenv("VIOLATION_MIN_RATIO", "0.6"))
    track_min_speed: float = max(0.0, float(os.getenv("TRACK_MIN_SPEED", "2.5")))
    track_min_hits: int = max(1, int(os.getenv("TRACK_MIN_HITS", "3")))
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
