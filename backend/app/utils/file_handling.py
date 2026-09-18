import hashlib
import os
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException, status

from app.config import get_settings

settings = get_settings()


class FileValidationError(Exception):
    pass


def validate_file(file: UploadFile, contents: bytes) -> str:
    """Validate extension and size. Returns the normalized extension (e.g. '.pdf')."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(settings.allowed_extensions_list)}",
        )

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds max size of {settings.MAX_FILE_SIZE_MB}MB",
        )

    if len(contents) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    return ext


def compute_file_hash(contents: bytes) -> str:
    return hashlib.sha256(contents).hexdigest()


def save_upload(contents: bytes, ext: str, owner_id: str) -> str:
    """Save file bytes to disk under a per-user subfolder, return the stored path."""
    upload_dir = Path(settings.UPLOAD_DIR) / owner_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    path = upload_dir / filename
    with open(path, "wb") as f:
        f.write(contents)
    return str(path)


def delete_file(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
