from __future__ import annotations

import re
import shutil
import unicodedata
import uuid
from pathlib import Path
from typing import BinaryIO

from fastapi import UploadFile

from app.core.config import settings


def ensure_storage_directories() -> None:
    for name in ("uploads", "results", "violations", "exports"):
        (settings.storage_root / name).mkdir(parents=True, exist_ok=True)


def safe_filename(filename: str) -> str:
    source = Path(filename or "file").name
    normalized = unicodedata.normalize("NFKD", source).encode("ascii", "ignore").decode("ascii")
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(normalized).stem).strip("._") or "file"
    suffix = Path(source).suffix.lower()
    return f"{stem[:80]}_{uuid.uuid4().hex[:10]}{suffix}"


def storage_relative(path: Path) -> str:
    return path.resolve().relative_to(settings.storage_root).as_posix()


def storage_url(relative_path: str | None) -> str | None:
    return f"/storage/{relative_path}" if relative_path else None


def absolute_storage_path(relative_path: str) -> Path:
    candidate = (settings.storage_root / relative_path).resolve()
    candidate.relative_to(settings.storage_root)
    return candidate


async def save_upload(upload: UploadFile, destination: Path) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    try:
        with destination.open("wb") as output:
            while chunk := await upload.read(1024 * 1024):
                total += len(chunk)
                if total > settings.max_file_size_bytes:
                    raise ValueError(
                        f"File '{upload.filename}' vượt quá giới hạn {settings.max_file_size_mb} MB."
                    )
                output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()
    return total


def copy_stream(source: BinaryIO, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as output:
        shutil.copyfileobj(source, output)
