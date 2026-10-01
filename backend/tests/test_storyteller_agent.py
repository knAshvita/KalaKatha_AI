"""
tests/test_storyteller_agent.py
══════════════════════════════════════════════════════════════════════════════
Tests for StorytellerAgent  —  Google ADK Specialist
(app/agents/storyteller_agent.py)

TEST SUITE
───────────
  1. test_story_analysis_schema
       — Validates StoryAnalysis model with 4–6 chapters and all required fields.
  2. test_guide_modes
       — Validates persona config generation for all 4 guide modes.
  3. test_storyteller_agent_config
       — Verifies LocalAgentConfig and response_schema setup.
  4. test_storyteller_agent_live (integration)
       — Runs live with Gemini ADK when GEMINI_API_KEY is present.
"""
from __future__ import annotations

import os
# pyrefly: ignore [missing-import]
import pytest
from pathlib import Path

from app.schemas.artwork import (
    AccessibilityAnalysis,
    ContextAnalysis,
    ContextFact,
    GuideMode,
    SpatialDescription,
    StoryAnalysis,
    StoryChapter,
    VisualAnalysis,
)
from app.agents.storyteller_agent import (
    build_agent_config,
    generate_story,
)


def test_story_analysis_schema():
    chapters = [
        StoryChapter(
            chapter_id="chapter_1",
            title="The Enigmatic Gaze",
            narration="Step closer to the threshold of 17th-century Delft. A young girl looks back over her shoulder.",
            focus_region="center",
            visual_elements=["young girl", "large dark eyes", "parted lips"],
            estimated_duration_seconds=30,
        ),
        StoryChapter(
            chapter_id="chapter_2",
            title="Silk from the East",
            narration="Notice the exotic turban crowning her head, shimmering in ultramarine blue and warm ochre.",
            focus_region="upper center",
            visual_elements=["blue turban", "yellow wrap"],
            estimated_duration_seconds=35,
        ),
        StoryChapter(
            chapter_id="chapter_3",
            title="The Drop of Liquid Light",
            narration="At the dark junction between her collar and jaw hangs the famous pearl, composed of two simple strokes.",
            focus_region="lower center",
            visual_elements=["pearl earring", "specular highlight"],
            estimated_duration_seconds=30,
        ),
        StoryChapter(
            chapter_id="chapter_4",
            title="The Dark Intimacy",
            narration="Surrounding her is nothing but an obsidian void, drawing you into an eternal private dialogue.",
            focus_region="background",
            visual_elements=["dark background", "chiaroscuro shadows"],
            estimated_duration_seconds=25,
        ),
    ]

    story = StoryAnalysis(
        story_title="Whispers in the Dark: A Delft Mystery",
        opening="Welcome to the Mauritshuis. Before us rests one of the world's most quietly mesmerizing masterpieces.",
        chapters=chapters,
        closing="As you step away, remember that in Vermeer's world, light does not just illuminate—it speaks.",
    )

    data = story.model_dump()
    assert "story_title" in data
    assert "opening" in data
    assert "chapters" in data
    assert "closing" in data
    assert len(data["chapters"]) == 4
    assert data["chapters"][0]["chapter_id"] == "chapter_1"
    assert data["chapters"][0]["focus_region"] == "center"
    assert data["chapters"][0]["estimated_duration_seconds"] == 30
    assert story.title == "Whispers in the Dark: A Delft Mystery"
    assert "Whispers in the Dark" in story.narrative


def test_guide_modes():
    modes = [
        GuideMode.STORYTELLER,
        GuideMode.PROFESSOR,
        GuideMode.FRIENDLY,
        GuideMode.ACCESSIBILITY,
    ]
    for mode in modes:
        cfg = build_agent_config(guide_mode=mode)
        assert cfg.system_instructions
        assert cfg.response_schema is StoryAnalysis or "StoryAnalysis" in str(cfg.response_schema)
        if mode == GuideMode.PROFESSOR:
            assert "professor" in cfg.system_instructions.lower() or "scholar" in cfg.system_instructions.lower()
        elif mode == GuideMode.FRIENDLY:
            assert "docent" in cfg.system_instructions.lower() or "friendly" in cfg.system_instructions.lower()


def test_storyteller_agent_config():
    from app.agents.base import KalaKathaBaseAgent

    config = build_agent_config()
    assert isinstance(config, KalaKathaBaseAgent)
    assert config.response_schema is StoryAnalysis or "StoryAnalysis" in str(config.response_schema)
    assert "chapter" in config.system_instructions.lower()


def test_storyteller_agent_class():
    from app.agents.storyteller_agent import StorytellerAgent

    agent = StorytellerAgent(guide_mode="professor")
    assert agent.guide_mode == "professor"
    assert "professor" in agent.config.system_instructions.lower() or "scholar" in agent.config.system_instructions.lower()


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set; skipping live ADK integration test.",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_storyteller_agent_live():
    mock_visual = VisualAnalysis(
        artwork_title="Girl with a Pearl Earring",
        artist="Johannes Vermeer",
        style="Dutch Golden Age",
        period="circa 1665",
        summary="A young girl wearing an oriental turban and a large pearl earring looking over her shoulder.",
        objects=["earring", "turban"],
        people=["young girl facing viewer"],
        animals=[],
        environment="dark studio interior",
        architecture="none visible",
        colors="Deep blue, ochre yellow, creamy white",
        lighting="Chiaroscuro, directional light from left",
        composition="Close-up portrait against dark background",
        perspective="Eye level",
        visual_focus="The girl's eye and glinting pearl earring",
        visible_actions=[],
        mood="Enigmatic and contemplative",
        confidence_notes="none",
    )

    mock_context = ContextAnalysis(
        historical_context=[
            ContextFact(
                claim="Delft in the 1660s.",
                certainty="verified",
                basis="Historical consensus.",
            )
        ],
        cultural_context=[],
        artistic_context=[
            ContextFact(
                claim="A Dutch tronie study.",
                certainty="verified",
                basis="Genre conventions.",
            )
        ],
        symbolism=[],
        artistic_techniques=[
            ContextFact(
                claim="Delicate liquid highlights.",
                certainty="verified",
                basis="Visible paint strokes.",
            )
        ],
        interesting_facts=[],
        summary="Classic Dutch tronie study.",
        search_queries_suggested=[],
    )

    mock_accessibility = AccessibilityAnalysis(
        accessibility_description="A portrait of a girl in a turban.",
        spatial_description=SpatialDescription(
            top="Dark background",
            bottom="Draped mantle",
            left="Shadowed shoulder",
            right="Illuminated face",
            center="The girl's face",
            foreground="The glowing pearl",
            background="Dark void",
            relationships="The earring links shadow and light.",
        ),
        short_description="Portrait of girl with pearl.",
        alt_text="Girl with a pearl earring.",
    )

    result = await generate_story(
        visual=mock_visual,
        context=mock_context,
        accessibility=mock_accessibility,
        guide_mode="friendly",
    )
    assert isinstance(result, StoryAnalysis)
    assert result.story_title
    assert len(result.chapters) >= 4
    assert result.chapters[0].narration
