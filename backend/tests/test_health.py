"""
Tests – Health Check
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "gemini_api_key_set" in data


def test_health_check_response_shape():
    response = client.get("/api/health")
    data = response.json()
    assert set(data.keys()) == {"status", "version", "gemini_api_key_set"}
