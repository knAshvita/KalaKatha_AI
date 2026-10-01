"""
tests/test_ask_agent.py
══════════════════════════════════════════════════════════════════════════════
Tests for AskAgent  —  Google ADK Specialist
(app/agents/ask_agent.py, app/api/ask.py)

TEST SUITE
───────────
  1. test_ask_request_response_schemas
       — Validates AskRequest and AskResponse field constraints and serializability.
  2. test_session_store_operations
       — Validates save, get, and add_turn on SessionStore.
  3. test_ask_config_personas
       — Verifies LocalAgentConfig setup for storyteller, professor, friendly, accessibility.
  4. test_ask_agent_missing_session_raises_key_error
       — Ensures answer_question raises KeyError on nonexistent session.
  5. test_api_ask_missing_session_404
       — Tests POST /api/ask returns HTTP 404 for unknown session_id.
  6. test_api_ask_validation_422
       — Tests POST /api/ask returns HTTP 422 for missing required fields.
  7. test_ask_agent_class
       — Tests AskAgent class interface.
  8. test_ask_agent_live (integration)
       — Runs live with Gemini ADK when GEMINI_API_KEY is present.
"""
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

# pyrefly: ignore [missing-import]
import pytest
from fastapi.testclient import TestClient

from app.agents.ask_agent import (
    AskAgent,
    answer_question,
    build_ask_config,
)
from app.main import app
from app.schemas.artwork import (
    AccessibilityAnalysis,
    ArtworkMetadata,
    ArtworkRegion,
    AskRequest,
    AskResponse,
    ContextAnalysis,
    ContextFact,
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
from app.services.session_store import ArtworkSession, session_store


def _build_dummy_experience(session_id: str = "kk_test_123") -> KalaKathaExperience:
    """Helper to construct a fully populated KalaKathaExperience for testing."""
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
            summary="A swirling night sky over a quiet town with a towering cypress tree.",
            objects=["swirling stars", "crescent moon", "cypress tree", "village church steeple"],
            people=[],
            animals=[],
            environment="outdoor nocturnal landscape",
            architecture="village houses with church steeple",
            colors="Ultramarine blue, cobalt, vibrant yellow, dark green",
            lighting="Luminous moonlight and starlight",
            composition="Dynamic diagonal swirl",
            perspective="Elevated viewpoint",
            visual_focus="The giant luminous celestial swirls",
            visible_actions=[],
            mood="Turbulent yet serene",
            confidence_notes="none",
        ),
        context=ContextAnalysis(
            historical_context=[
                ContextFact(
                    claim="Painted while at Saint-Paul asylum in Saint-Rémy",
                    certainty="verified",
                    basis="Van Gogh's letters to his brother Theo",
                )
            ],
            cultural_context=[],
            artistic_context=[
                ContextFact(
                    claim="Pioneered expressive post-impressionist impasto brushwork",
                    certainty="verified",
                    basis="Art historical consensus",
                )
            ],
            symbolism=[
                ContextFact(
                    claim="Cypress trees traditionally symbolize mourning and eternity",
                    certainty="interpreted",
                    basis="Iconographical study",
                )
            ],
            artistic_techniques=[
                ContextFact(
                    claim="Thick impasto applied with vigorous rhythmic brushstrokes",
                    certainty="verified",
                    basis="Physical canvas inspection",
                )
            ],
            interesting_facts=[
                ContextFact(
                    claim="The morning star depicted was likely the planet Venus",
                    certainty="verified",
                    basis="Astronomical reconstruction",
                )
            ],
            summary="Van Gogh's nocturnal masterpiece combining observation and imagination.",
            search_queries_suggested=[],
        ),
        accessibility=AccessibilityAnalysis(
            accessibility_description=(
                "A large oil painting dominated by a swirling dark blue and golden yellow night sky. "
                "In the foreground stands a dark cypress tree shaped like a flame. Below lies a peaceful village."
            ),
            spatial_description=SpatialDescription(
                top="Luminous swirling bands of blue, white, and yellow light with a glowing crescent moon on the right.",
                bottom="A calm village with small houses and a prominent church spire pointing upward.",
                left="A massive dark green cypress tree rising vertically into the sky.",
                right="A vibrant crescent moon emitting radiant yellow and white light.",
                center="A sweeping, wave-like spiral connecting the celestial elements.",
                foreground="The towering silhouette of the cypress tree anchoring the lower left.",
                background="The undulating blue hills of the Alpilles under the swirling sky.",
                relationships="The vertical cypress tree and church spire punctuate the horizontal celestial rhythm.",
            ),
        ),
        story=StoryAnalysis(
            story_title="A Sky Alive with Wonder",
            opening="Welcome to Saint-Rémy in the quiet hours just before dawn in June 1889.",
            chapters=[
                StoryChapter(
                    chapter_id="chap_1",
                    title="The Swirling Heavens",
                    narration="Look upward at the cosmic dance painted with electric urgency.",
                    focus_region="Upper center sky",
                    visual_elements=["swirls", "stars"],
                    estimated_duration_seconds=30,
                ),
                StoryChapter(
                    chapter_id="chap_2",
                    title="The Silent Cypress",
                    narration="Anchoring this tempest of light is a dark cypress rising like a green flame.",
                    focus_region="Left foreground",
                    visual_elements=["cypress"],
                    estimated_duration_seconds=25,
                ),
            ],
            closing="Vincent has shown us not just what the night looked like, but what it felt like.",
        ),
        learning=LearningAnalysis(
            key_concepts=["Impasto", "Post-Impressionism", "Expressive Color"],
            simple_explanations=[
                "Impasto means laying paint on thickly so the brush strokes and texture stand out."
            ],
            interesting_facts=[
                "Van Gogh painted this scene from his asylum window, blending memory and imagination."
            ],
            things_to_notice=[
                "Notice the thick ridges of paint that make the sky appear to actually move."
            ],
            questions=[
                MultipleChoiceQuestion(
                    question_id="q1",
                    question="What tree dominates the foreground?",
                    options=["Oak", "Cypress", "Willow", "Pine"],
                    correct_option="Cypress",
                    explanation="A towering dark cypress tree rises prominently on the left.",
                ),
                MultipleChoiceQuestion(
                    question_id="q2",
                    question="What painting technique creates the textured ridges?",
                    options=["Impasto", "Fresco", "Glazing", "Pointillism"],
                    correct_option="Impasto",
                    explanation="Impasto is the thick application of paint leaving visible texture.",
                ),
                MultipleChoiceQuestion(
                    question_id="q3",
                    question="Which planet is believed to be represented by the morning star?",
                    options=["Mars", "Jupiter", "Venus", "Saturn"],
                    correct_option="Venus",
                    explanation="Astronomical records confirm Venus was especially bright in June 1889.",
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


# ─────────────────────────────────────────────────────────────────────────────
#  UNIT TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_ask_request_response_schemas():
    req = AskRequest(session_id="kk_12345", question="Why are the stars swirling?")
    assert req.session_id == "kk_12345"
    assert req.question == "Why are the stars swirling?"

    res = AskResponse(
        session_id="kk_12345",
        question="Why are the stars swirling?",
        answer="The swirling represents Van Gogh's expressive emotional turbulence.",
        source_context=["VisualAnalysis", "ContextAnalysis"],
    )
    dumped = res.model_dump()
    assert dumped["session_id"] == "kk_12345"
    assert len(dumped["source_context"]) == 2
    assert "VisualAnalysis" in dumped["source_context"]


def test_session_store_operations():
    session_id = "kk_test_store_1"
    exp = _build_dummy_experience(session_id)
    session = ArtworkSession(session_id=session_id, experience=exp, guide_mode="professor")

    session_store.save(session)
    retrieved = session_store.get(session_id)
    assert retrieved is not None
    assert retrieved.session_id == session_id
    assert retrieved.guide_mode == "professor"
    assert len(retrieved.history) == 0

    session_store.add_turn(
        session_id,
        "What kind of paint was used?",
        "Van Gogh used thick oil paint with heavy impasto.",
    )
    updated = session_store.get(session_id)
    assert len(updated.history) == 1
    assert updated.history[0].question == "What kind of paint was used?"
    assert "impasto" in updated.history[0].answer


def test_ask_config_personas():
    for mode in ["storyteller", "professor", "friendly", "accessibility"]:
        config = build_ask_config(guide_mode=mode)
        assert config.response_schema is AskResponse or "AskResponse" in str(config.response_schema)
        assert (
            "gallery docent" in config.system_instructions.lower()
            or "kalakatha" in config.system_instructions.lower()
            or "ask agent" in config.system_instructions.lower()
        ), f"system_instructions for mode={mode!r} missing expected identity phrase"


@pytest.mark.asyncio
async def test_ask_agent_missing_session_raises_key_error():
    with pytest.raises(KeyError) as exc_info:
        await answer_question(session_id="kk_nonexistent_999", question="Who painted this?")
    assert "not found" in str(exc_info.value).lower()


def test_api_ask_missing_session_404():
    client = TestClient(app)
    response = client.post(
        "/api/ask",
        json={"session_id": "kk_unknown_xyz", "question": "What is the meaning of the tree?"},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_api_ask_validation_422():
    client = TestClient(app)
    # Missing session_id
    res1 = client.post("/api/ask", json={"question": "What is this?"})
    assert res1.status_code == 422

    # Question too short (< 2 chars)
    res2 = client.post("/api/ask", json={"session_id": "kk_123", "question": "?"})
    assert res2.status_code == 422


def test_ask_agent_class():
    agent = AskAgent(guide_mode="friendly")
    assert agent.guide_mode == "friendly"
    assert agent.config is not None


# ─────────────────────────────────────────────────────────────────────────────
#  LIVE ADK INTEGRATION TEST
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set; skipping live ADK integration test.",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_ask_agent_live():
    session_id = "kk_live_test_42"
    exp = _build_dummy_experience(session_id)
    session = ArtworkSession(session_id=session_id, experience=exp, guide_mode="storyteller")
    session_store.save(session)

    # 1. Ask initial question
    question_1 = "What does the tall dark tree on the left represent?"
    res_1 = await answer_question(session_id=session_id, question=question_1)

    assert isinstance(res_1, AskResponse)
    assert res_1.session_id == session_id
    assert res_1.question == question_1
    assert len(res_1.answer) > 20
    assert len(res_1.source_context) > 0
    # Must refer to cypress or mourning or eternity or foreground
    answer_lower = res_1.answer.lower()
    assert any(w in answer_lower for w in ["cypress", "tree", "eternity", "mourning", "flame", "foreground"])

    # 2. Ask follow-up question utilizing conversation history
    question_2 = "Did Van Gogh mention it in his letters?"
    res_2 = await answer_question(session_id=session_id, question=question_2)
    assert isinstance(res_2, AskResponse)
    assert len(res_2.answer) > 20

    # Verify session store recorded both turns
    stored_session = session_store.get(session_id)
    assert len(stored_session.history) == 2
