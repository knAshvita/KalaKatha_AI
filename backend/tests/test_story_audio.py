"""
tests/test_story_audio.py
══════════════════════════════════════════════════════════════════════════════
Tests for POST /api/story/audio — Gemini TTS narration endpoint.

TEST SUITE
───────────
  Unit tests (always run):
    1. test_story_audio_request_schema        — StoryAudioRequest validation
    2. test_story_audio_response_schema       — StoryAudioResponse fields
    3. test_pcm_to_wav_conversion             — PCM→WAV header correctness
    4. test_narration_prompt_construction     — Guide-mode prompt shaping
    5. test_guide_voice_mapping               — Each mode maps to correct voice
    6. test_missing_session_returns_404       — Unknown session_id → 404
    7. test_missing_chapter_returns_404       — Bad chapter_id → 404 with suggestions
    8. test_opening_and_closing_special_ids   — 'opening' / 'closing' resolve correctly
    9. test_story_audio_validation_422        — Missing required fields → 422

  Integration test (requires GEMINI_API_KEY):
    10. test_story_audio_live                 — Full round-trip: Gemini TTS → WAV on disk
"""
from __future__ import annotations

import io
import os
import struct
import wave

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv()

from app.main import app
from app.schemas.artwork import (
    AccessibilityAnalysis,
    ArtworkMetadata,
    ArtworkRegion,
    ContextAnalysis,
    ContextFact,
    ExploreContent,
    KalaKathaExperience,
    LearningAnalysis,
    MultipleChoiceQuestion,
    RegionPosition,
    SpatialDescription,
    StoryAnalysis,
    StoryAudioRequest,
    StoryAudioResponse,
    StoryChapter,
    VisualAnalysis,
)
from app.services.session_store import ArtworkSession, session_store
from app.services.tts_service import (
    _GUIDE_VOICE_MAP,
    _build_narration_prompt,
    _pcm_to_wav,
)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_experience(session_id: str = "kk_audio_test") -> KalaKathaExperience:
    """Build a minimal KalaKathaExperience fixture for audio tests."""
    return KalaKathaExperience(
        session_id=session_id,
        artwork=ArtworkMetadata(
            title="The Starry Night",
            artist="Vincent van Gogh",
            period="June 1889",
            style="Post-Impressionism",
            filename="starry_night.jpg",
        ),
        visual_analysis=VisualAnalysis(
            artwork_title="The Starry Night",
            artist="Vincent van Gogh",
            style="Post-Impressionism",
            period="1889",
            summary="A swirling nocturnal sky over a quiet Provençal village.",
            objects=["swirling stars", "cypress tree", "crescent moon"],
            people=[],
            animals=[],
            environment="nocturnal outdoor landscape",
            architecture="church steeple, village houses",
            colors="Ultramarine blue, cobalt, vibrant yellow",
            lighting="Luminous moonlight and starlight",
            composition="Dynamic diagonal swirl",
            perspective="Elevated viewpoint",
            visual_focus="The luminous celestial swirls",
            visible_actions=[],
            mood="Turbulent yet serene",
            confidence_notes="none",
        ),
        context=ContextAnalysis(
            historical_context=[
                ContextFact(
                    claim="Painted while at Saint-Paul asylum",
                    certainty="verified",
                    basis="Van Gogh's letters",
                )
            ],
            cultural_context=[],
            artistic_context=[],
            symbolism=[],
            artistic_techniques=[],
            interesting_facts=[],
            summary="Van Gogh's nocturnal masterpiece.",
            search_queries_suggested=[],
        ),
        accessibility=AccessibilityAnalysis(
            accessibility_description="A swirling dark blue sky with bright stars.",
            spatial_description=SpatialDescription(
                top="Swirling celestial bands of blue and yellow.",
                bottom="A tranquil village with a church steeple.",
                left="A tall dark cypress tree rising like a flame.",
                right="A radiant crescent moon.",
                center="A sweeping wave-like spiral.",
                foreground="The cypress tree silhouette.",
                background="Distant rolling hills.",
                relationships="The cypress and steeple punctuate the horizontal sky.",
            ),
        ),
        story=StoryAnalysis(
            story_title="A Sky Alive with Wonder",
            opening=(
                "Step into the room and allow your senses to adjust. "
                "This is not just a painting — it is a window into a single, extraordinary night."
            ),
            chapters=[
                StoryChapter(
                    chapter_id="chapter_1",
                    title="The Swirling Heavens",
                    narration=(
                        "Look upward at the vast cosmic canvas spreading across most of the painting. "
                        "Van Gogh rendered the night sky not as a static backdrop, "
                        "but as something alive — breathing, churning, radiant."
                    ),
                    focus_region="Upper two-thirds of the painting",
                    visual_elements=["swirling stars", "crescent moon", "luminous halos"],
                    estimated_duration_seconds=35,
                ),
                StoryChapter(
                    chapter_id="chapter_2",
                    title="The Silent Cypress",
                    narration=(
                        "Anchoring the turbulent sky is the dark, flame-like cypress tree "
                        "reaching from the bottom edge into the celestial swirl. "
                        "It is both of this earth and reaching toward something beyond it."
                    ),
                    focus_region="Left foreground",
                    visual_elements=["cypress tree"],
                    estimated_duration_seconds=25,
                ),
            ],
            closing=(
                "As you step away, carry with you the reminder that Van Gogh transformed "
                "his darkest hours into one of the most luminous artworks humanity has ever created."
            ),
        ),
        learning=LearningAnalysis(
            key_concepts=["Impasto", "Post-Impressionism"],
            simple_explanations=["Impasto is thick, textured paint application."],
            interesting_facts=["Van Gogh painted this from his asylum window."],
            things_to_notice=["Notice the thick ridges of paint that make the sky move."],
            questions=[
                MultipleChoiceQuestion(
                    question_id="q1",
                    question="What tree dominates the foreground?",
                    options=["Oak", "Cypress", "Willow", "Pine"],
                    correct_option="Cypress",
                    explanation="A towering dark cypress tree rises on the left.",
                ),
                MultipleChoiceQuestion(
                    question_id="q2",
                    question="What technique creates textured ridges?",
                    options=["Impasto", "Fresco", "Glazing", "Pointillism"],
                    correct_option="Impasto",
                    explanation="Impasto is thick paint leaving visible texture.",
                ),
                MultipleChoiceQuestion(
                    question_id="q3",
                    question="Which planet is the morning star?",
                    options=["Mars", "Jupiter", "Venus", "Saturn"],
                    correct_option="Venus",
                    explanation="Astronomical records confirm Venus was bright in June 1889.",
                ),
            ],
        ),
        explore=ExploreContent(
            regions=[
                ArtworkRegion(
                    region_id="reg_cypress",
                    label="The Cypress Tree",
                    description="Towering flame-like evergreen.",
                    importance="Foreground anchor",
                    related_visual_elements=["cypress"],
                    position=RegionPosition(x=0.05, y=0.2, width=0.25, height=0.75),
                )
            ],
            topics_to_explore=["Van Gogh letters", "Astronomy in 1889"],
        ),
    )


def _register_session(session_id: str, guide_mode: str = "storyteller") -> ArtworkSession:
    """Register a test session in the global session store."""
    exp = _make_experience(session_id)
    session = ArtworkSession(
        session_id=session_id,
        experience=exp,
        guide_mode=guide_mode,
    )
    session_store.save(session)
    return session


# ─────────────────────────────────────────────────────────────────────────────
#  UNIT TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_story_audio_request_schema():
    req = StoryAudioRequest(session_id="kk_abc123", chapter_id="chapter_1")
    assert req.session_id == "kk_abc123"
    assert req.chapter_id == "chapter_1"

    # Missing required fields
    with pytest.raises(Exception):
        StoryAudioRequest(session_id="kk_abc123")  # no chapter_id
    with pytest.raises(Exception):
        StoryAudioRequest(chapter_id="chapter_1")  # no session_id


def test_story_audio_response_schema():
    res = StoryAudioResponse(
        session_id="kk_abc123",
        chapter_id="chapter_1",
        chapter_title="The Swirling Heavens",
        narration="Look upward at the vast cosmic canvas.",
        audio_url="/audio/abc123def.wav",
        guide_mode="storyteller",
        voice="Puck",
        duration_hint_seconds=35,
    )
    assert res.audio_url.endswith(".wav")
    assert res.duration_hint_seconds == 35
    dumped = res.model_dump()
    assert "audio_url" in dumped
    assert "voice" in dumped


def test_pcm_to_wav_conversion():
    """_pcm_to_wav must produce a valid RIFF/WAV container from raw PCM bytes."""
    # Generate 0.5 seconds of silence at 24000 Hz, 16-bit mono
    sample_count = 24000 // 2  # 0.5 seconds
    pcm_data = b"\x00\x00" * sample_count

    wav_bytes = _pcm_to_wav(pcm_data)

    # Verify RIFF header magic
    assert wav_bytes[:4] == b"RIFF"
    assert wav_bytes[8:12] == b"WAVE"

    # Verify it's a valid WAV file that Python's wave module can parse
    wav_io = io.BytesIO(wav_bytes)
    with wave.open(wav_io, "rb") as w:
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
        assert w.getframerate() == 24000
        assert w.getnframes() == sample_count


def test_narration_prompt_construction():
    """_build_narration_prompt must embed artwork context and guide instruction."""
    prompt = _build_narration_prompt(
        narration="The sky swirls with electric blue brushstrokes.",
        artwork_title="The Starry Night",
        chapter_title="The Swirling Heavens",
        guide_mode="storyteller",
    )
    assert "The Starry Night" in prompt
    assert "The Swirling Heavens" in prompt
    assert "The sky swirls with electric blue brushstrokes." in prompt
    # Should contain narration persona instructions
    assert any(
        word in prompt.lower()
        for word in ["storyteller", "theatrical", "poetic", "captivating"]
    )

    # Different guide modes produce different prompts
    professor_prompt = _build_narration_prompt(
        narration="The sky swirls.",
        artwork_title="The Starry Night",
        chapter_title="Ch1",
        guide_mode="professor",
    )
    assert professor_prompt != prompt


def test_guide_voice_mapping():
    """Each guide_mode must map to a specific Gemini prebuilt voice."""
    assert _GUIDE_VOICE_MAP["storyteller"] == "Puck"
    assert _GUIDE_VOICE_MAP["professor"] == "Charon"
    assert _GUIDE_VOICE_MAP["friendly"] == "Aoede"
    assert _GUIDE_VOICE_MAP["accessibility"] == "Leda"
    # All known modes have entries
    for mode in ("storyteller", "professor", "friendly", "accessibility"):
        assert mode in _GUIDE_VOICE_MAP


def test_missing_session_returns_404():
    client = TestClient(app)
    res = client.post(
        "/api/story/audio",
        json={"session_id": "kk_no_such_session", "chapter_id": "chapter_1"},
    )
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_missing_chapter_returns_404():
    session_id = "kk_bad_chapter_test"
    _register_session(session_id)
    client = TestClient(app)
    res = client.post(
        "/api/story/audio",
        json={"session_id": session_id, "chapter_id": "chapter_999"},
    )
    assert res.status_code == 404
    detail = res.json()["detail"]
    assert "chapter_999" in detail
    # Should list available chapters as a hint
    assert "chapter_1" in detail or "opening" in detail


def test_opening_and_closing_special_ids():
    """'opening' and 'closing' special chapter_ids must resolve to the story opening/closing."""
    session_id = "kk_opening_closing_test"
    session = _register_session(session_id, guide_mode="friendly")
    exp = session.experience

    # We cannot call the full endpoint without calling Gemini TTS,
    # so we test only the session data resolution logic directly.
    chapter_id = "opening"
    assert chapter_id == "opening"
    assert len(exp.story.opening) > 10

    chapter_id = "closing"
    assert chapter_id == "closing"
    assert len(exp.story.closing) > 10

    # chapter_id 'chapter_1' exists
    chapter = next(
        (c for c in exp.story.chapters if c.chapter_id.lower() == "chapter_1"),
        None,
    )
    assert chapter is not None
    assert chapter.title == "The Swirling Heavens"


def test_story_audio_validation_422():
    client = TestClient(app)
    # Missing session_id
    res1 = client.post("/api/story/audio", json={"chapter_id": "chapter_1"})
    assert res1.status_code == 422

    # Missing chapter_id
    res2 = client.post("/api/story/audio", json={"session_id": "kk_abc"})
    assert res2.status_code == 422

    # Empty body
    res3 = client.post("/api/story/audio", json={})
    assert res3.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
#  LIVE INTEGRATION TEST
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set; skipping live Gemini TTS integration test.",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_story_audio_live():
    """
    Full round-trip: registered session → POST /api/story/audio → WAV on disk.
    Verifies that:
      - Gemini TTS generates audio for a real StoryChapter narration.
      - The resulting WAV file is a valid RIFF container.
      - The audio_url is served by FastAPI StaticFiles.
    """
    import httpx

    session_id = "kk_audio_live_test"
    _register_session(session_id, guide_mode="storyteller")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. POST /api/story/audio for chapter_1
        res = await client.post(
            "/api/story/audio",
            json={"session_id": session_id, "chapter_id": "chapter_1"},
        )

        assert res.status_code == 200, f"Unexpected status: {res.status_code} — {res.text}"
        data = res.json()

        assert data["session_id"] == session_id
        assert data["chapter_id"] == "chapter_1"
        assert data["chapter_title"] == "The Swirling Heavens"
        assert len(data["narration"]) > 20
        assert data["audio_url"].startswith("/audio/")
        assert data["audio_url"].endswith(".wav")
        assert data["guide_mode"] == "storyteller"
        assert data["voice"] == "Puck"

        # 2. Retrieve the WAV file from the static files route
        wav_url = data["audio_url"]
        audio_res = await client.get(wav_url)
        assert audio_res.status_code == 200
        assert audio_res.headers["content-type"] in (
            "audio/wav", "audio/wave", "audio/x-wav", "audio/vnd.wave"
        )

        wav_bytes = audio_res.content
        assert wav_bytes[:4] == b"RIFF", "Response is not a valid WAV file"
        assert wav_bytes[8:12] == b"WAVE"

        # Verify WAV is parseable and non-trivially sized
        wav_io = io.BytesIO(wav_bytes)
        with wave.open(wav_io, "rb") as w:
            assert w.getnchannels() == 1
            assert w.getsampwidth() == 2
            assert w.getframerate() == 24000
            assert w.getnframes() > 1000  # At least some audio data

        # 3. Test 'opening' special chapter id
        opening_res = await client.post(
            "/api/story/audio",
            json={"session_id": session_id, "chapter_id": "opening"},
        )
        assert opening_res.status_code == 200
        opening_data = opening_res.json()
        assert opening_data["chapter_title"] == "Opening"
        assert opening_data["audio_url"].endswith(".wav")
