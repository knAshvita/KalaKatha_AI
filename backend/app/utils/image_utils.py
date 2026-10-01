"""
Utility helpers shared across agents and services.
"""
from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/bmp",
    "image/tiff",
}


def validate_image_bytes(data: bytes, filename: str) -> str:
    """
    Validate image bytes and return their MIME type.
    Raises ValueError for unsupported types.
    """
    mime, _ = mimetypes.guess_type(filename)
    if mime not in ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Unsupported file type '{mime}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
        )
    return mime


def bytes_to_base64(data: bytes) -> str:
    """Encode raw bytes to a base64 string."""
    return base64.b64encode(data).decode("utf-8")


def base64_to_bytes(b64: str) -> bytes:
    """Decode a base64 string to raw bytes."""
    return base64.b64decode(b64)


def save_temp_file(data: bytes, suffix: str = ".png") -> Path:
    """
    Write bytes to a temporary file in the OS temp directory.
    Returns the Path so callers can pass it to the ADK Image helper.
    Callers are responsible for deleting the file after use.
    """
    import tempfile

    fd, path_str = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
    except Exception:
        os.close(fd)
        raise
    return Path(path_str)
