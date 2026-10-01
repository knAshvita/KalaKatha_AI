"""
Narration API Router – POST /api/narrate
─────────────────────────────────────────
Converts artwork story text to speech using Gemini TTS and returns
the audio as a base64-encoded MP3 string.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.artwork import NarrateRequest, NarrateResponse, AnalysisStatus
from app.services.tts_service import synthesize_speech

router = APIRouter(prefix="/api", tags=["Narration"])


@router.post(
    "/narrate",
    response_model=NarrateResponse,
    summary="Narrate artwork story via TTS",
    description=(
        "Convert a text passage (e.g. the immersive story) to speech using "
        "Gemini TTS. Returns a base64-encoded MP3 the frontend can play directly."
    ),
    status_code=status.HTTP_200_OK,
)
async def narrate_endpoint(body: NarrateRequest) -> NarrateResponse:
    try:
        audio_b64 = await synthesize_speech(text=body.text, voice=body.voice)
    except RuntimeError as exc:
        # GEMINI_API_KEY not configured
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS synthesis failed: {exc}",
        ) from exc

    return NarrateResponse(
        status=AnalysisStatus.SUCCESS,
        audio_base64=audio_b64,
        text=body.text,
        voice=body.voice,
    )
