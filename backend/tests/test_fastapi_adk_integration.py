"""
tests/test_fastapi_adk_integration.py  –  FastAPI & Google ADK Integration Tests
══════════════════════════════════════════════════════════════════════════════
Validates:
  1. Clear separation of concerns:
     - FastAPI handles HTTP requests, validation, upload, errors, CORS, serialization.
     - Google ADK handles agent reasoning, orchestration, specialist agents.
     - No agent reasoning / workflow implemented directly inside route functions.
  2. POST /api/analyze:
     - Rejects oversized files (> 10MB) with HTTP 413.
     - Rejects non-image files with HTTP 415.
     - Passes valid uploads to KalaKathaRootAgent.execute_experience.
     - Performs session identification.
     - Returns serialized ArtworkAnalysisResponse with KalaKathaExperience.
     - Handles OrchestrationError gracefully with HTTP 502 Bad Gateway.
  3. End-to-end integration across all 5 endpoints:
     - POST /api/analyze
     - GET /api/session/{session_id}
     - POST /api/quiz/answer
     - POST /api/ask
     - POST /api/story/audio
"""
from __future__ import annotations

import io
import inspect
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.agents.root_agent import OrchestrationError
import app.api.artwork as artwork_api_mod
import app.api.ask as ask_api_mod
import app.api.quiz as quiz_api_mod
import app.api.session_api as session_api_mod
import app.api.story_audio as story_audio_api_mod
from app.main import app
from app.schemas.artwork import (
    AccessibilityAnalysis,
    ArtworkMetadata,
    ArtworkRegion,
    ContextAnalysis,
    ExploreContent,
    KalaKathaExperience,
    LearningAnalysis,
    MultipleChoiceQuestion,
    RegionPosition,
    SpatialDescription,
    StoryAnalysis,
    StoryChapter,
    VisualAnalysis,
)
from app.services.session_store import session_store

client = TestClient(app)

# Minimal 1x1 valid PNG image bytes
TINY_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00"
    b"\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _build_mock_experience(session_id: str = "kk_mock123") -> KalaKathaExperience:
    return KalaKathaExperience(
        session_id=session_id,
        artwork=ArtworkMetadata(
            filename="mona_lisa.png",
            title="Mona Lisa",
            artist="Leonardo da Vinci",
            style="High Renaissance",
            period="16th century",
        ),
        visual_analysis=VisualAnalysis(
            artwork_title="Mona Lisa",
            artist="Leonardo da Vinci",
            style="High Renaissance",
            period="16th century",
            summary="A seated woman with an enigmatic expression against a distant landscape.",
            objects=["chair", "veil", "landscape"],
            people=["seated woman"],
            animals=[],
            environment="distant misty landscape",
            architecture="loggia parapet",
            colors="Subdued browns, greens, and ochres",
            lighting="Soft chiaroscuro and sfumato",
            composition="Pyramidal half-length portrait",
            perspective="Eye-level",
            visual_focus="The subject's face and smile",
            visible_actions=[],
            mood="Mysterious, serene",
            confidence_notes="none",
        ),
        context=ContextAnalysis(
            historical_context=[],
            cultural_context=[],
            artistic_context=[],
            symbolism=[],
            artistic_techniques=[],
            interesting_facts=[],
            summary="Florentine Renaissance portrait.",
            search_queries_suggested=[],
        ),
        story=StoryAnalysis(
            story_title="The Unfolding Smile",
            opening="Gaze into the misty horizon behind Mona Lisa.",
            chapters=[
                StoryChapter(
                    chapter_id="chapter_1",
                    title="The Sfumato Technique",
                    narration="Notice how boundaries soften into smoke without harsh lines.",
                    focus_region="face",
                    visual_elements=["soft smile", "eyes"],
                    estimated_duration_seconds=30,
                )
            ],
            closing="A masterpiece that redefined portraiture forever.",
        ),
        learning=LearningAnalysis(
            key_concepts=["Sfumato", "Chiaroscuro"],
            simple_explanations={"Sfumato": "Blending colors without abrupt transitions."},
            interesting_facts=["Painted on a poplar wood panel."],
            things_to_notice=["Observe the absence of visible eyelashes."],
            multiple_choice_questions=[
                MultipleChoiceQuestion(
                    question_id="q1",
                    question="What technique did Leonardo use to soften the transitions around the eyes and mouth?",
                    options=["A) Sfumato", "B) Impasto", "C) Pointillism", "D) Fresco"],
                    correct_option="A) Sfumato",
                    explanation="Sfumato produces soft, gradual transitions between tones without harsh contours.",
                )
            ],
        ),
        accessibility=AccessibilityAnalysis(
            accessibility_description="Half-length portrait of a woman seated with folded hands.",
            spatial_description=SpatialDescription(
                top="Misty sky and distant mountainous landscape",
                bottom="Folded hands resting on the arm of a chair",
                left="Winding path and rocky hills",
                right="Stone bridge across a river",
                center="The face of Lisa Gherardini with dark wavy hair",
                foreground="Her dark attire and folded hands",
                background="Aerial perspective landscape",
                relationships="The pyramid of the figure sits in front of the vast backdrop",
            ),
            short_description="Portrait of a smiling woman.",
            alt_text="Renaissance portrait of Mona Lisa by Leonardo da Vinci.",
        ),
        explore=ExploreContent(
            regions=[
                ArtworkRegion(
                    region_id="reg_smile",
                    label="The Enigmatic Smile",
                    description="Subtle sfumato modeling around the corners of the lips",
                    importance="Famous focal ambiguity",
                    related_visual_elements=["smile", "lips"],
                    position=RegionPosition(x=0.45, y=0.35, width=0.15, height=0.08),
                )
            ],
            interactive_questions=[],
            topics_to_explore=["Leonardo's optical studies"],
            coordinate_disclaimer="Approximate interactive regions.",
        ),
        guide_mode="storyteller",
    )


# ── Architectural Separation Tests ───────────────────────────────────────────

def test_routes_do_not_import_specialist_agent_classes_directly():
    """
    Ensure FastAPI route modules do NOT directly import specialist agents.
    Only the Root Agent or specific specialized entrypoints should coordinate them.
    """
    import ast

    forbidden_specialists = {
        "ArtAnalystAgent",
        "ContextAgent",
        "AccessibilityAgent",
        "StorytellerAgent",
        "LearningAgent",
        "ExploreAgent",
    }

    for mod in [artwork_api_mod, quiz_api_mod, session_api_mod]:
        source = inspect.getsource(mod)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    assert alias.name not in forbidden_specialists, (
                        f"{mod.__name__} directly imports {alias.name}"
                    )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in forbidden_specialists, (
                        f"{mod.__name__} directly imports {alias.name}"
                    )


def test_artwork_route_delegates_to_root_agent():
    """Verify that POST /api/analyze invokes root_agent.execute_experience."""
    assert hasattr(artwork_api_mod, "root_agent")
    assert hasattr(artwork_api_mod.root_agent, "execute_experience")


# ── POST /api/analyze Tests ──────────────────────────────────────────────────

def test_analyze_rejects_oversized_file(monkeypatch):
    """File exceeding max_upload_size_bytes returns 413."""
    from app.config import get_settings
    settings = get_settings()
    monkeypatch.setattr(settings, "max_upload_size_bytes", 50)

    files = {"file": ("large.png", b"x" * 100, "image/png")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"].lower()


def test_analyze_rejects_invalid_image_bytes():
    """Non-image / unsupported file returns 415."""
    files = {"file": ("corrupt.txt", b"NOT AN IMAGE AT ALL", "text/plain")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 415
    assert "unsupported" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_analyze_successful_flow():
    """
    Upload a valid image:
    1. FastAPI validates input and generates/identifies session
    2. KalaKathaRootAgent executes experience
    3. Serialized ArtworkAnalysisResponse is returned
    4. KalaKathaExperience is attached and session is accessible
    """
    mock_exp = _build_mock_experience(session_id="kk_integration_test")

    with patch.object(
        artwork_api_mod.root_agent,
        "execute_experience",
        new_callable=AsyncMock,
        return_value=mock_exp,
    ) as mock_exec:
        files = {"file": ("mona_lisa.png", TINY_PNG_BYTES, "image/png")}
        data = {"guide_mode": "storyteller"}

        response = client.post("/api/analyze", files=files, data=data)
        assert response.status_code == 200
        res_json = response.json()

        # Check call delegation
        mock_exec.assert_called_once()
        _, kwargs = mock_exec.call_args
        assert kwargs["filename"] == "mona_lisa.png"
        assert kwargs["guide_mode"] == "storyteller"
        assert kwargs["session_id"].startswith("kk_")

        # Response structure
        assert res_json["status"] == "success"
        assert res_json["session_id"] == "kk_integration_test"
        assert res_json["filename"] == "mona_lisa.png"
        assert res_json["visual_analysis"]["artwork_title"] == "Mona Lisa"
        assert res_json["experience"]["session_id"] == "kk_integration_test"
        assert res_json["experience"]["artwork"]["artist"] == "Leonardo da Vinci"


def test_analyze_handles_orchestration_error():
    """Controlled OrchestrationError from root agent returns HTTP 502 with diagnostics."""
    with patch.object(
        artwork_api_mod.root_agent,
        "execute_experience",
        side_effect=OrchestrationError(
            agent_name="ArtAnalystAgent",
            stage="visual_analysis",
            message="Visual parsing failed on low-contrast input.",
        ),
    ):
        files = {"file": ("mona_lisa.png", TINY_PNG_BYTES, "image/png")}
        response = client.post("/api/analyze", files=files)
        assert response.status_code == 502
        detail = response.json()["detail"]
        assert detail["status"] == "error"
        assert detail["failed_agent"] == "ArtAnalystAgent"
        assert detail["failed_stage"] == "visual_analysis"
        assert "visual parsing failed" in detail["error_message"].lower()


# ── Full 5-Endpoint Pipeline Integration Test ────────────────────────────────

def test_full_pipeline_multi_endpoint_journey():
    """
    Test interaction across all 5 endpoints:
      1. POST /api/analyze (via mocked RootAgent)
      2. GET /api/session/{session_id}
      3. POST /api/quiz/answer
      4. POST /api/ask
      5. POST /api/story/audio (via mocked TTS)
    """
    session_id = "kk_full_journey_01"
    mock_exp = _build_mock_experience(session_id=session_id)

    # 1. Analyze artwork
    with patch.object(
        artwork_api_mod.root_agent,
        "execute_experience",
        new_callable=AsyncMock,
        return_value=mock_exp,
    ):
        # Also ensure session_store saves it as KalaKathaRootAgent does
        session_store.save(session_id, mock_exp, guide_mode="storyteller")

        files = {"file": ("mona_lisa.png", TINY_PNG_BYTES, "image/png")}
        res_analyze = client.post("/api/analyze", files=files, data={"guide_mode": "storyteller"})
        assert res_analyze.status_code == 200
        assert res_analyze.json()["session_id"] == session_id

    # 2. GET /api/session/{session_id}
    res_session = client.get(f"/api/session/{session_id}")
    assert res_session.status_code == 200
    session_data = res_session.json()
    assert session_data["session_id"] == session_id
    assert session_data["artwork"]["title"] == "Mona Lisa"
    assert len(session_data["story"]["chapters"]) == 1

    # 3. POST /api/quiz/answer
    res_quiz = client.post(
        "/api/quiz/answer",
        json={"session_id": session_id, "question_id": "q1", "selected_option": "A"},
    )
    assert res_quiz.status_code == 200
    quiz_data = res_quiz.json()
    assert quiz_data["is_correct"] is True
    assert "sfumato" in quiz_data["explanation"].lower()

    # 4. POST /api/ask (mocking answer_question)
    with patch(
        "app.api.ask.answer_question",
        new_callable=AsyncMock,
        return_value={
            "session_id": session_id,
            "question": "What is sfumato?",
            "answer": "Sfumato is Leonardo's smoke-like blending technique.",
            "source_context": ["VisualAnalysis", "LearningAnalysis"],
        },
    ):
        res_ask = client.post(
            "/api/ask",
            json={"session_id": session_id, "question": "What is sfumato?"},
        )
        assert res_ask.status_code == 200
        ask_data = res_ask.json()
        assert "sfumato" in ask_data["answer"].lower()
        assert ask_data["session_id"] == session_id

    # 5. POST /api/story/audio (mocking synthesize_chapter)
    with patch(
        "app.api.story_audio.synthesize_chapter",
        new_callable=AsyncMock,
        return_value=(Path("audio_cache/test.wav"), "/audio/test.wav"),
    ):
        res_audio = client.post(
            "/api/story/audio",
            json={"session_id": session_id, "chapter_id": "chapter_1"},
        )
        assert res_audio.status_code == 200
        audio_data = res_audio.json()
        assert audio_data["audio_url"] == "/audio/test.wav"
        assert audio_data["chapter_id"] == "chapter_1"
