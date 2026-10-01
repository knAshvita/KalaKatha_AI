"""
Health Check Router – GET /api/health
──────────────────────────────────────
Simple liveness endpoint the React frontend and deployment infra can ping.
"""
from fastapi import APIRouter

from app.config import get_settings
from app.schemas.artwork import HealthResponse

router = APIRouter(prefix="/api", tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the service status and confirms the API key is loaded.",
)
async def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        gemini_api_key_set=bool(settings.gemini_api_key),
    )
