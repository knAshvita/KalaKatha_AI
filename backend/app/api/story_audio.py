"""
app/api/story_audio.py  –  POST /api/story/audio
══════════════════════════════════════════════════
Chapter-level museum narration endpoint.

Given a session_id and chapter_id, this endpoint:
  1. Retrieves the active KalaKathaExperience from SessionStore.
  2. Finds the requested StoryChapter (or opening/closing section).
  3. Calls the TTS service (Gemini speech generation) with the chapter
     narration text, artwork context, and active guide_mode persona.
  4. Saves the resulting WAV file to the audio_cache directory.
  5. Returns a StoryAudioResponse with the audio_url the frontend can use
     to stream or play the file via an HTML5 <audio> element.

Design Decisions
─────────────────
  • The StorytellerAgent (Google ADK) is NOT invoked here — narration text
    was already generated during the main analysis pipeline.
  • TTS is kept entirely in the service layer (app/services/tts_service.py),
    preserving clean separation from the ADK agent layer.
  • Audio files are served via FastAPI StaticFiles mounted at /audio.
  • The 'opening' and 'closing' special IDs narrate the story opening/closing.
  • Unknown chapter_id returns HTTP 404.
  • No browser Web Speech API is used anywhere in this flow.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.artwork import StoryAudioRequest, StoryAudioResponse
from app.services.session_store import session_store
from app.services.tts_service import _GUIDE_VOICE_MAP, _DEFAULT_VOICE, synthesize_chapter

router = APIRouter(prefix="/api/story", tags=["Story Audio"])


@router.post(
    "/audio",
    response_model=StoryAudioResponse,
    summary="Narrate a story chapter via Gemini TTS",
    description=(
        "Generate expressive museum-guide narration for a specific story chapter "
        "using Google Gemini speech generation. The narration voice and style adapt "
        "to the active guide_mode persona stored in the session. "
        "Returns a streamable WAV audio URL — no browser Web Speech API is used."
    ),
    status_code=status.HTTP_200_OK,
)
async def story_audio_endpoint(body: StoryAudioRequest) -> StoryAudioResponse:
    # ── 1. Retrieve active session ────────────────────────────────────────────
    session = session_store.get(body.session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Session '{body.session_id}' not found. "
                "Please analyze an artwork first via POST /api/analyze."
            ),
        )

    exp = session.experience
    guide_mode = session.guide_mode or "storyteller"
    artwork_title = exp.artwork.title

    # ── 2. Find the requested chapter ────────────────────────────────────────
    chapter_id = body.chapter_id.strip().lower()

    if chapter_id == "opening":
        narration_text = exp.story.opening
        chapter_title = "Opening"
        duration_hint = 20
    elif chapter_id == "closing":
        narration_text = exp.story.closing
        chapter_title = "Closing"
        duration_hint = 20
    else:
        # Search by chapter_id (case-insensitive)
        chapter = next(
            (c for c in exp.story.chapters if c.chapter_id.lower() == chapter_id),
            None,
        )
        if chapter is None:
            available = (
                ["opening", "closing"]
                + [c.chapter_id for c in exp.story.chapters]
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Chapter '{body.chapter_id}' not found in session '{body.session_id}'. "
                    f"Available chapter IDs: {available}"
                ),
            )
        narration_text = chapter.narration
        chapter_title = chapter.title
        duration_hint = chapter.estimated_duration_seconds

    # ── 3 & 4. Synthesize and save audio ─────────────────────────────────────
    try:
        _file_path, audio_url = await synthesize_chapter(
            narration=narration_text,
            artwork_title=artwork_title,
            chapter_title=chapter_title,
            guide_mode=guide_mode,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gemini TTS synthesis failed: {exc}",
        ) from exc

    voice = _GUIDE_VOICE_MAP.get(guide_mode.lower(), _DEFAULT_VOICE)

    # ── 5. Return audio URL ──────────────────────────────────────────────────
    return StoryAudioResponse(
        session_id=body.session_id,
        chapter_id=body.chapter_id,
        chapter_title=chapter_title,
        narration=narration_text,
        audio_url=audio_url,
        guide_mode=guide_mode,
        voice=voice,
        duration_hint_seconds=duration_hint,
    )
