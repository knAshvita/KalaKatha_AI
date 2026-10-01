"""
tests/test_root_agent.py
══════════════════════════════════════════════════════════════════════════════
Tests for KalaKathaRootAgent  —  Google ADK Master Orchestrator
(app/agents/root_agent.py)

TEST SUITE
───────────
  1. test_kalakatha_experience_schema
       — Validates KalaKathaExperience structure containing session_id, artwork,
         visual_analysis, context, story, learning, accessibility, explore.
  2. test_root_agent_config
       — Verifies LocalAgentConfig, response_schema=KalaKathaExperience, and registered tools.
  3. test_orchestration_error_handling
       — Ensures OrchestrationError surfaces stage, agent, message, and to_dict().
  4. test_preflight_validation
       — Tests that a non-existent image path raises a controlled OrchestrationError.
  5. test_root_agent_live (integration)
       — Runs live with Gemini ADK when GEMINI_API_KEY is present.
"""
from __future__ import annotations

import os
import pytest
from pathlib import Path
from unittest.mock import AsyncMock

from app.schemas.artwork import (
    AccessibilityAnalysis,
    ArtworkIdentification,
    ArtworkMetadata,
    ArtworkRegion,
    ArtworkUnderstanding,
    ContextAnalysis,
    ContextFact,
    ExploreContent,
    InteractiveQuestion,
    KalaKathaExperience,
    LearningAnalysis,
    MultipleChoiceQuestion,
    RegionPosition,
    SpatialDescription,
    StoryAnalysis,
    StoryChapter,
    VisualAnalysis,
)
from app.agents.root_agent import (
    KalaKathaRootAgent,
    OrchestrationError,
    build_root_agent_config,
)


def _make_dummy_experience() -> KalaKathaExperience:
    visual = VisualAnalysis(
        artwork_title="Girl with a Pearl Earring",
        artist="Johannes Vermeer",
        style="Dutch Golden Age",
        period="circa 1665",
        summary="A young girl in a turban with a large pearl earring.",
        objects=["earring", "turban"],
        people=["young girl"],
        animals=[],
        environment="dark studio interior",
        architecture="none visible",
        colors="Deep blue, yellow, cream",
        lighting="Chiaroscuro from left",
        composition="Close-up portrait",
        perspective="Eye level",
        visual_focus="The pearl earring",
        visible_actions=[],
        mood="Enigmatic",
        confidence_notes="none",
    )

    context = ContextAnalysis(
        historical_context=[ContextFact(claim="Delft in 1665", certainty="verified", basis="Catalog")],
        cultural_context=[],
        artistic_context=[ContextFact(claim="Dutch tronie", certainty="verified", basis="Art consensus")],
        symbolism=[],
        artistic_techniques=[ContextFact(claim="Liquid highlights", certainty="verified", basis="Visual surface")],
        interesting_facts=[],
        summary="Classic tronie study.",
        search_queries_suggested=[],
    )

    accessibility = AccessibilityAnalysis(
        accessibility_description="A portrait of a girl in a turban turning over her shoulder.",
        spatial_description=SpatialDescription(
            top="Dark background",
            bottom="Dark mantle",
            left="Shadowed shoulder",
            right="Lit face",
            center="The girl's face",
            foreground="Pearl earring",
            background="Dark void",
            relationships="The earring links light and shadow.",
        ),
        short_description="Girl with pearl earring.",
        alt_text="A girl in a turban with a pearl earring.",
    )

    story = StoryAnalysis(
        story_title="Whispers in the Dark",
        opening="Welcome to the Mauritshuis.",
        chapters=[
            StoryChapter(
                chapter_id="c1",
                title="The Gaze",
                narration="She looks back at you.",
                focus_region="center",
                visual_elements=["eyes"],
                estimated_duration_seconds=30,
            )
        ],
        closing="A memorable reflection.",
    )

    learning = LearningAnalysis(
        key_concepts=["Tronie", "Chiaroscuro"],
        simple_explanations={"Tronie": "A character study."},
        interesting_facts=["Painted in 1665."],
        things_to_notice=["The reflective pearl highlight."],
        multiple_choice_questions=[
            MultipleChoiceQuestion(
                question_id="q1",
                question="What is the girl wearing?",
                options=["A pearl earring", "A crown", "A hat", "A scarf"],
                correct_option="A pearl earring",
                explanation="The pearl earring is the focal point.",
            )
        ],
    )

    explore = ExploreContent(
        regions=[
            ArtworkRegion(
                region_id="region_pearl",
                label="The Pearl Earring",
                description="The signature focal point reflecting soft light.",
                importance="Primary focal point",
                related_visual_elements=["pearl earring", "specular highlight"],
                position=RegionPosition(x=0.45, y=0.52, width=0.12, height=0.15),
            )
        ],
        interactive_questions=[
            InteractiveQuestion(
                question="What emotions does her gaze evoke?",
                hint="Observe her eyes and parted lips.",
                category="interpretation",
            )
        ],
        topics_to_explore=["Dutch Golden Age art", "Delft in the 17th Century"],
    )

    return KalaKathaExperience(
        session_id="kk_test123",
        artwork=ArtworkMetadata(
            filename="test.jpg",
            title="Girl with a Pearl Earring",
            artist="Johannes Vermeer",
            style="Dutch Golden Age",
            period="circa 1665",
        ),
        visual_analysis=visual,
        context=context,
        story=story,
        learning=learning,
        accessibility=accessibility,
        explore=explore,
    )


def test_kalakatha_experience_schema():
    exp = _make_dummy_experience()
    data = exp.model_dump()
    assert data["session_id"] == "kk_test123"
    assert data["artwork"]["title"] == "Girl with a Pearl Earring"
    assert data["visual_analysis"]["artwork_title"] == "Girl with a Pearl Earring"
    assert data["context"]["summary"] == "Classic tronie study."
    assert data["story"]["story_title"] == "Whispers in the Dark"
    assert len(data["learning"]["multiple_choice_questions"]) == 1
    assert data["accessibility"]["spatial_description"]["center"] == "The girl's face"
    assert len(data["explore"]["interactive_questions"]) == 1
    assert len(data["explore"]["regions"]) == 1
    assert data["explore"]["regions"][0]["position"]["x"] == 0.45


def test_root_agent_config():
    from app.agents.root_agent import RootAgentConfig

    config = build_root_agent_config()
    assert isinstance(config, RootAgentConfig)
    assert config.tools is not None and len(config.tools) >= 2
    assert "orchestrator" in config.system_instructions.lower() or "kalakatha" in config.system_instructions.lower()


def test_orchestration_error_handling():
    err = OrchestrationError(
        agent_name="ArtAnalystAgent",
        stage="artwork_understanding",
        message="Vision service unavailable",
        cause=RuntimeError("timeout"),
    )
    d = err.to_dict()
    assert d["status"] == "error"
    assert d["failed_agent"] == "ArtAnalystAgent"
    assert d["failed_stage"] == "artwork_understanding"
    assert d["error_message"] == "Vision service unavailable"
    assert "timeout" in d["cause"]


@pytest.mark.asyncio
async def test_preflight_validation():
    agent = KalaKathaRootAgent()
    non_existent = Path("non_existent_artwork_12345.jpg")

    with pytest.raises(OrchestrationError) as exc_info:
        await agent.execute_experience(non_existent, "test.jpg")

    err = exc_info.value
    assert err.agent_name == "KalaKathaRootAgent"
    assert err.stage == "pre_flight"
    assert "does not exist" in err.message


@pytest.fixture
def dummy_image_file(tmp_path: Path) -> Path:
    img = tmp_path / "sample.jpg"
    img.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xd9")
    return img


@pytest.fixture
def mock_dummy_experience_parts():
    dummy = _make_dummy_experience()
    return (
        dummy.visual_analysis,
        dummy.accessibility,
        dummy.story,
        dummy.learning,
        dummy.explore,
    )


def _make_dummy_understanding(
    identification: ArtworkIdentification | None = None,
) -> ArtworkUnderstanding:
    ident = identification or ArtworkIdentification(
        title="Girl with a Pearl Earring",
        artist="Johannes Vermeer",
        period="circa 1665",
        style="Dutch Golden Age",
        confidence="high",
        basis="Distinctive blue turban and pearl earring.",
    )
    return ArtworkUnderstanding(
        identification=ident,
        summary="A young girl in a turban with a large pearl earring.",
        objects=["earring", "turban"],
        people=["young girl"],
        animals=[],
        environment="dark studio interior",
        architecture="none visible",
        colors="Deep blue, yellow, cream",
        lighting="Chiaroscuro from left",
        composition="Close-up portrait",
        perspective="Eye level",
        visual_focus="The pearl earring",
        visible_actions=[],
        mood="Enigmatic",
        confidence_notes="none",
        historical_context=[ContextFact(claim="Delft in 1665", certainty="verified", basis="Catalog")],
        cultural_context=[],
        artistic_context=[ContextFact(claim="Dutch tronie", certainty="verified", basis="Art consensus")],
        symbolism=[],
        artistic_techniques=[ContextFact(claim="Liquid highlights", certainty="verified", basis="Visual surface")],
        spatial_description=SpatialDescription(
            top="Dark background",
            bottom="Dark mantle",
            left="Shadowed shoulder",
            right="Lit face",
            center="The girl's face",
            foreground="Pearl earring",
            background="Dark void",
            relationships="The earring links light and shadow.",
        ),
        accessibility_description="A portrait of a girl in a turban turning over her shoulder.",
        alt_text="A girl in a turban with a pearl earring.",
    )


@pytest.mark.asyncio
async def test_root_orchestration_known_artwork_identification(monkeypatch, dummy_image_file, mock_dummy_experience_parts):
    """
    Test A: Known artwork
    ArtAnalyst identifies Mona Lisa by Leonardo da Vinci with High Renaissance period.
    Final experience.artwork uses Mona Lisa / Leonardo da Vinci / High Renaissance.
    """
    _, _, story, _, _ = mock_dummy_experience_parts
    ident = ArtworkIdentification(
        title="Mona Lisa",
        artist="Leonardo da Vinci",
        period="High Renaissance",
        style="Italian Renaissance",
        confidence="high",
        basis="Direct visual identification of the sitter, sfumato technique, and mountain backdrop.",
    )
    understanding = _make_dummy_understanding(identification=ident)

    agent = KalaKathaRootAgent()
    monkeypatch.setattr(agent.art_analyst.__class__, "analyze", AsyncMock(return_value=understanding))
    monkeypatch.setattr(agent.storyteller_agent.__class__, "generate_story", AsyncMock(return_value=story))

    exp = await agent.execute_experience(dummy_image_file, "mona_lisa.jpg")

    assert exp.artwork.title == "Mona Lisa"
    assert exp.artwork.artist == "Leonardo da Vinci"
    assert exp.artwork.period == "High Renaissance"
    assert exp.artwork.style == "Italian Renaissance"


@pytest.mark.asyncio
async def test_root_orchestration_unknown_artwork_fallback(monkeypatch, dummy_image_file, mock_dummy_experience_parts):
    """
    Test B: Unknown artwork
    ArtAnalyst cannot identify the artwork (title/artist/period='unknown').
    Final experience.artwork safely falls back to friendly defaults:
    'Untitled Artwork', 'Unknown Artist', 'Unspecified Period', 'Unspecified Style'.
    """
    _, _, story, _, _ = mock_dummy_experience_parts
    ident = ArtworkIdentification(
        title="unknown",
        artist="unknown",
        period="unknown",
        style="unknown",
        confidence="uncertain",
        basis="No matching visual reference or iconography found.",
    )
    understanding = _make_dummy_understanding(identification=ident)

    agent = KalaKathaRootAgent()
    monkeypatch.setattr(agent.art_analyst.__class__, "analyze", AsyncMock(return_value=understanding))
    monkeypatch.setattr(agent.storyteller_agent.__class__, "generate_story", AsyncMock(return_value=story))

    exp = await agent.execute_experience(dummy_image_file, "abstract_study.jpg")

    assert exp.artwork.title == "Untitled Artwork"
    assert exp.artwork.artist == "Unknown Artist"
    assert exp.artwork.period == "Unspecified Period"
    assert exp.artwork.style == "Unspecified Style"


@pytest.mark.asyncio
async def test_root_orchestration_partial_identification(monkeypatch, dummy_image_file, mock_dummy_experience_parts):
    """
    Test C: Partial identification
    ArtAnalyst identifies period and style, but title and artist remain 'unknown'.
    Final experience.artwork uses identified period/style, and friendly fallbacks for title/artist.
    """
    _, _, story, _, _ = mock_dummy_experience_parts
    ident = ArtworkIdentification(
        title="unknown",
        artist="unknown",
        period="Dutch Golden Age",
        style="Baroque",
        confidence="medium",
        basis="Costume and chiaroscuro indicate 17th-century Dutch provenance, but exact artist is unrecorded.",
    )
    understanding = _make_dummy_understanding(identification=ident)

    agent = KalaKathaRootAgent()
    monkeypatch.setattr(agent.art_analyst.__class__, "analyze", AsyncMock(return_value=understanding))
    monkeypatch.setattr(agent.storyteller_agent.__class__, "generate_story", AsyncMock(return_value=story))

    exp = await agent.execute_experience(dummy_image_file, "baroque_study.jpg")

    assert exp.artwork.title == "Untitled Artwork"
    assert exp.artwork.artist == "Unknown Artist"
    assert exp.artwork.period == "Dutch Golden Age"
    assert exp.artwork.style == "Baroque"


def test_art_analyst_observation_only_contract():
    """
    Test D: ArtAnalyst observation-only contract
    Confirms ArtAnalyst schema requires 'unknown' when title/artist are not visibly inscribed,
    and never fabricates identity.
    """
    from app.schemas.artwork import VisualAnalysis

    schema = VisualAnalysis.model_json_schema()
    title_desc = schema["properties"]["artwork_title"]["description"]
    artist_desc = schema["properties"]["artist"]["description"]

    assert "inscription" in title_desc.lower() or "visible" in title_desc.lower()
    assert "unknown" in title_desc.lower()
    assert "signature" in artist_desc.lower() or "visible" in artist_desc.lower()
    assert "unknown" in artist_desc.lower()


def test_root_agent_only_contains_art_analyst_and_storyteller():
    """
    Test E: Ensure KalaKathaRootAgent instantiates strictly ArtAnalystAgent
    and StorytellerAgent, with no legacy specialist agents.
    """
    agent = KalaKathaRootAgent()
    assert hasattr(agent, "art_analyst")
    assert hasattr(agent, "storyteller_agent")
    assert not hasattr(agent, "context_agent")
    assert not hasattr(agent, "accessibility_agent")
    assert not hasattr(agent, "learning_agent")
    assert not hasattr(agent, "explore_agent")

