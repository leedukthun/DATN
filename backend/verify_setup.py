from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.services.ai.detector import Detector
from app.utils.files import ensure_storage_directories


def ok(message: str) -> None:
    print(f"[OK] {message}")


def fail(message: str) -> None:
    print(f"[LOI] {message}")
    raise SystemExit(1)


def main() -> None:
    print("=== KIEM TRA HE THONG PHAT HIEN KHONG DOI MU ===")
    print(f"Python: {sys.version.split()[0]}")

    if not settings.model_path.exists():
        fail(f"Khong tim thay model: {settings.model_path}")
    ok(f"Model ton tai: {settings.model_path.name} ({settings.model_path.stat().st_size / 1024 / 1024:.1f} MB)")

    ensure_storage_directories()
    probe = settings.storage_root / "exports" / ".write_test"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError as exc:
        fail(f"Storage khong ghi duoc: {exc}")
    ok(f"Storage ghi duoc: {settings.storage_root}")

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        fail(f"Khong ket noi duoc database: {exc}")
    ok("Database ket noi thanh cong")

    detector = Detector(
        settings.model_path,
        settings.confidence_threshold,
        settings.iou_threshold,
        settings.device,
    )
    try:
        names = detector.class_names
    except Exception as exc:
        fail(f"Khong nap duoc Ultralytics/model: {exc}")
    ok(f"Nap model thanh cong. Classes: {names}")

    print("\nHe thong san sang. Chay python run.py va npm run dev.")


if __name__ == "__main__":
    main()
