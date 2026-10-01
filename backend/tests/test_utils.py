"""
Tests – Image Utilities
"""
import pytest

from app.utils.image_utils import bytes_to_base64, base64_to_bytes, validate_image_bytes


def test_base64_roundtrip():
    original = b"hello kalakatha"
    encoded = bytes_to_base64(original)
    assert isinstance(encoded, str)
    decoded = base64_to_bytes(encoded)
    assert decoded == original


def test_validate_image_bytes_unsupported():
    with pytest.raises(ValueError, match="Unsupported file type"):
        validate_image_bytes(b"", "malware.exe")


def test_validate_image_bytes_png():
    mime = validate_image_bytes(b"fake-png-data", "artwork.png")
    assert mime == "image/png"


def test_validate_image_bytes_jpeg():
    mime = validate_image_bytes(b"fake-jpg-data", "photo.jpg")
    assert mime == "image/jpeg"
