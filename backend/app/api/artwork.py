"""
app/api/artwork.py  –  POST /api/analyze
═════════════════════════════════════════
Accepts a multipart image upload and passes it to the root ADK orchestrator.
Returns the full ArtworkAnalysisResponse.
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.agents.root_agent import KalaKathaRootAgent, OrchestrationError
from app.config import get_settings
from app.schemas.artwork import AnalysisStatus, ArtworkAnalysisResponse, GuideMode
from app.utils.image_utils import save_temp_file, validate_image_bytes

router = APIRouter(prefix="/api", tags=["Artwork Analysis"])

# Root orchestrator singleton instance
root_agent = KalaKathaRootAgent()


@router.post(
    "/analyze",
    response_model=ArtworkAnalysisResponse,
    summary="Analyze an artwork image",
    description=(
        "Upload an artwork image (JPEG, PNG, WebP, GIF, BMP, TIFF — max 10 MB). "
        "The Google ADK KalaKathaRootAgent coordinates 6 specialist agents and returns "
        "a complete analysis: visual analysis, artistic context, accessibility "
        "description, immersive museum story, educational content, interactive questions, "
        "and the unified KalaKathaExperience."
    ),
    status_code=status.HTTP_200_OK,
)
async def analyze_artwork_endpoint(
    file: Annotated[UploadFile, File(description="Artwork image file")],
    guide_mode: Annotated[
        str,
        Form(
            description=(
                "Persona for the museum tour guide: "
                "'storyteller' | 'professor' | 'friendly' | 'accessibility'"
            )
        ),
    ] = "storyteller",
) -> ArtworkAnalysisResponse:
    settings = get_settings()

    # ── 1. Request Validation (HTTP Layer) ────────────────────────────────────
    contents = await file.read()

    if len(contents) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File exceeds {settings.max_upload_size_bytes // (1024 * 1024)} MB limit."
            ),
        )

    filename = file.filename or "artwork.png"
    try:
        validate_image_bytes(contents, filename)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc

    # Validate guide_mode
    valid_modes = {"storyteller", "professor", "friendly", "accessibility"}
    normalized_guide_mode = guide_mode.strip().lower()
    if normalized_guide_mode not in valid_modes:
        normalized_guide_mode = "storyteller"

    # ── 2. Session Identification (FastAPI Layer) ─────────────────────────────
    session_id = f"kk_{uuid.uuid4().hex[:12]}"

    # ── 3. Delegate to Google ADK Orchestration Layer ─────────────────────────
    suffix = Path(filename).suffix or ".png"
    temp_path: Path | None = None
    try:
        temp_path = save_temp_file(contents, suffix=suffix)
        experience = await root_agent.execute_experience(
            image_path=temp_path,
            filename=filename,
            guide_mode=normalized_guide_mode,
            session_id=session_id,
        )

        # ── 4. Response Serialization (FastAPI Layer) ─────────────────────────
        result = ArtworkAnalysisResponse(
            status=AnalysisStatus.SUCCESS,
            session_id=experience.session_id,
            filename=filename,
            visual_analysis=experience.visual_analysis,
            context=experience.context,
            accessibility=experience.accessibility,
            immersive_story=experience.story,
            learning_content=experience.learning,
            interactive_questions=experience.explore.interactive_questions,
            experience=experience,
        )
    except OrchestrationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.to_dict(),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline failed: {exc}",
        ) from exc
    finally:
        if temp_path and temp_path.exists():
            os.unlink(temp_path)

    return result
