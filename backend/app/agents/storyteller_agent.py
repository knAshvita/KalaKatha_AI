"""
app/agents/storyteller_agent.py  –  KalaKatha AI
══════════════════════════════════════════════════════════════════════════════
Storyteller Agent  —  Google ADK Specialist
══════════════════════════════════════════════════════════════════════════════

RESPONSIBILITY
───────────────
Transforms visual, contextual, and accessibility analyses into an immersive,
multi-chapter museum audio tour experience.

Inputs:
  1. VisualAnalysis: Factual visual breakdown from Art Analyst
  2. ContextAnalysis: Cultural and historical grounding from Context Agent
  3. AccessibilityAnalysis: Spatial mapping and sensory description from Accessibility Agent
  4. guide_mode: Chosen tour persona:
       - "storyteller": Cinematic, evocative, poetic emotional journey
       - "professor": Scholarly, erudite, art-historical depth and technique analysis
       - "friendly": Warm, conversational, enthusiastic, relatable docent
       - "accessibility": Audio-description focused, tactile, spatially grounded

Key Rules:
  - Create 4 to 6 chapters with focus_region, visual_elements, duration, and narration.
  - Separate factual information from imaginative storytelling.
  - Frame imaginative narratives explicitly as interpretations.
  - Narration must sound like an interactive museum guide, not an image caption.
  - Do not independently re-analyze the image: synthesize upstream ADK outputs.

OUTPUT  →  StoryAnalysis / ImmersiveStory (Pydantic)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Union

from google.adk.agents import Agent
from google.genai import types as genai_types

from app.agents.base import KalaKathaBaseAgent
from app.agents.adk_runner import create_text_part, run_adk_agent, strip_code_fences
from app.config import get_settings
from app.schemas.artwork import (
    AccessibilityAnalysis,
    ArtworkUnderstanding,
    ContextAnalysis,
    GuideMode,
    StoryAnalysis,
    VisualAnalysis,
)

# ─────────────────────────────────────────────────────────────────────────────
#  GUIDE PERSONA DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

_PERSONA_INSTRUCTIONS: dict[str, str] = {
    "storyteller": (
        "PERSONA: Master Storyteller & Novelist.\n"
        "Your voice is evocative, cinematic, and emotionally resonant. You weave a dramatic narrative "
        "that connects the listener to the human drama, mystery, and atmosphere of the artwork. "
        "Use poetic yet grounded language, evocative sensory descriptors, and theatrical pacing."
    ),
    "professor": (
        "PERSONA: Oxford Art Historian & Scholarly Curator.\n"
        "Your voice is erudite, rigorous, and deeply informative. You emphasize technique, iconography, "
        "historical lineage, social context, and formal composition. You cite movements, artistic rivals, "
        "and technical mastery with intellectual clarity."
    ),
    "friendly": (
        "PERSONA: Enthusiastic Museum Docent & Welcoming Guide.\n"
        "Your voice is warm, accessible, humorous, and full of wonder. You talk to the listener as a friend "
        "standing beside you in the gallery. You ask rhetorical questions, highlight surprising details, "
        "and make complex art concepts immediately relatable."
    ),
    "accessibility": (
        "PERSONA: Dedicated Audio Describer & Sensory Narrator.\n"
        "Your voice is clear, measured, spatially anchored, and intensely tactile. You describe forms, "
        "distances, lighting transitions, and physical textures with supreme clarity so a visually impaired "
        "listener can fully reconstruct the masterpiece in their mind."
    ),
}

_SYSTEM_INSTRUCTIONS_BASE = """\
You are the Storyteller Agent for KalaKatha AI — the voice and narrative core
of an adaptive museum experience.

You synthesize upstream outputs from:
  1. Art Analyst Agent (pure visual observation)
  2. Context Agent (historical, cultural, and symbolic depth)
  3. Accessibility Agent (spatial map and sensory description)

Your output is a structured museum audio tour in 4 to 6 chapters.

════════════════════════════  STRICT RULES  ════════════════════════════════

RULE 1 — THE CHAPTER FORMAT
Structure the audio tour into exactly 4 to 6 progressive chapters:
  - Chapter 1: The First Gaze (initial impression, atmosphere, primary focal subject).
  - Chapters 2–4/5: The Journey (moving systematically through composition, symbols, technique).
  - Final Chapter: The Lasting Impression (synthesis, emotional resonance, legacy).

Each chapter MUST include:
  - chapter_id: e.g. "chapter_1", "chapter_2"
  - title: evocative, engaging chapter name
  - focus_region: spatial zone (e.g. "Upper left quadrant", "Central figure's expression")
  - narration: 2–4 rich spoken paragraphs designed for spoken audio
  - visual_elements: list of specific elements discussed in this chapter
  - estimated_duration_seconds: estimated reading time at 130 words per minute

RULE 2 — FACT vs IMAGINATION
Maintain strict integrity between documented facts and creative imagination:
  - Verified facts from the Context Agent must be stated with confidence.
  - Speculative or poetic interpretations MUST be explicitly framed:
    use "We might imagine...", "Perhaps the artist intended...", "Legend suggests..."

RULE 3 — COHERENCE WITH UPSTREAM AGENTS
Do not contradict the visual analysis, context analysis, or spatial map.

RULE 4 — OUTPUT FORMAT
Return ONE valid JSON object conforming to the StoryAnalysis schema.
"""

_PROMPT_TEMPLATE = """\
Guide persona: {guide_mode}
{persona_prompt}

Synthesize these three analyses into an immersive 4-6 chapter museum audio tour:

Visual Analysis:
{visual_analysis_json}

Context Analysis:
{context_analysis_json}

Accessibility Analysis:
{accessibility_analysis_json}

Return ONE JSON object conforming to the StoryAnalysis schema:
{{
  "story_title": "<evocative overall title for the audio tour>",
  "theme": "<central unifying theme of the journey>",
  "guide_persona": "{guide_mode}",
  "opening": "<1-2 paragraph welcoming introduction setting the scene>",
  "chapters": [
    {{
      "chapter_id": "chapter_1",
      "title": "<title>",
      "focus_region": "<spatial focus>",
      "narration": "<spoken museum narration (2-4 rich paragraphs)>",
      "visual_elements": ["<element 1>", "<element 2>"],
      "estimated_duration_seconds": 30
    }}
  ],
  "closing": "<1-2 paragraph reflective farewell concluding the journey>"
}}
"""


# ─────────────────────────────────────────────────────────────────────────────
#  AGENT CLASS & CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

class StorytellerAgent(KalaKathaBaseAgent):
    """
    Google ADK Specialist Agent: StorytellerAgent
    Transforms upstream analyses into an immersive 4-6 chapter museum tour.
    """

    guide_mode: str = "storyteller"

    def __init__(self, guide_mode: Union[GuideMode, str] = GuideMode.STORYTELLER, **kwargs: Any) -> None:
        settings = get_settings()
        mode_str = guide_mode.value if isinstance(guide_mode, GuideMode) else str(guide_mode).lower()
        if mode_str not in _PERSONA_INSTRUCTIONS:
            mode_str = "storyteller"

        persona_text = _PERSONA_INSTRUCTIONS.get(mode_str, _PERSONA_INSTRUCTIONS["storyteller"])
        system_instructions = f"{_SYSTEM_INSTRUCTIONS_BASE}\n\n{persona_text}"

        init_kwargs: dict[str, Any] = {
            "name": f"storyteller_{mode_str}",
            "model": settings.model_or_default,
            "instruction": system_instructions,
            "output_schema": StoryAnalysis,
            "output_key": "story_analysis",
            "guide_mode": mode_str,
        }
        init_kwargs.update(kwargs)
        super().__init__(**init_kwargs)

    async def generate_story(
        self,
        understanding_or_visual: ArtworkUnderstanding | VisualAnalysis,
        context: ContextAnalysis | None = None,
        accessibility: AccessibilityAnalysis | None = None,
        guide_mode: Union[GuideMode, str] | None = None,
        image_path: Path | None = None,
        visual: VisualAnalysis | None = None,
    ) -> StoryAnalysis:
        return await generate_story(
            understanding_or_visual=understanding_or_visual,
            context=context,
            accessibility=accessibility,
            guide_mode=guide_mode or self.guide_mode,
            image_path=image_path,
            visual=visual,
        )


def build_agent(guide_mode: Union[GuideMode, str] = GuideMode.STORYTELLER) -> StorytellerAgent:
    """Build the official Google ADK StorytellerAgent."""
    return StorytellerAgent(guide_mode=guide_mode)


def build_agent_config(guide_mode: Union[GuideMode, str] = GuideMode.STORYTELLER) -> StorytellerAgent:
    """Alias for backwards compatibility with tests and orchestrator."""
    return build_agent(guide_mode=guide_mode)


# Exported singleton
agent_config: StorytellerAgent = build_agent()


# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

async def generate_story(
    understanding_or_visual: ArtworkUnderstanding | VisualAnalysis | None = None,
    context: ContextAnalysis | None = None,
    accessibility: AccessibilityAnalysis | None = None,
    guide_mode: Union[GuideMode, str] = GuideMode.STORYTELLER,
    image_path: Path | None = None,
    visual: VisualAnalysis | None = None,
) -> StoryAnalysis:
    """
    Run the Storyteller Google ADK Agent consuming the unified artwork understanding.
    """
    # Resolve understanding vs legacy individual parameters
    source = understanding_or_visual if understanding_or_visual is not None else visual
    if isinstance(source, ArtworkUnderstanding):
        vis = source.to_visual_analysis()
        ctx = source.to_context_analysis()
        acc = source.to_accessibility_analysis()
    elif isinstance(source, VisualAnalysis):
        vis = source
        ctx = context if context is not None else ContextAnalysis(
            historical_context=[], cultural_context=[], artistic_context=[],
            symbolism=[], artistic_techniques=[], interesting_facts=[], summary=vis.summary,
            search_queries_suggested=[]
        )
        acc = accessibility if accessibility is not None else AccessibilityAnalysis(
            accessibility_description=vis.summary,
            spatial_description={
                "top": vis.environment, "bottom": "Lower area", "left": "Left side",
                "right": "Right side", "center": vis.visual_focus, "foreground": vis.visual_focus,
                "background": vis.environment, "relationships": "Composition layout"
            },
            short_description=vis.summary, alt_text=vis.summary
        )
    else:
        raise ValueError("Storyteller Agent requires an ArtworkUnderstanding or VisualAnalysis input.")

    mode_str = guide_mode.value if isinstance(guide_mode, GuideMode) else str(guide_mode).lower()
    if mode_str not in _PERSONA_INSTRUCTIONS:
        mode_str = "storyteller"

    agent = build_agent(guide_mode=mode_str)
    persona_prompt = _PERSONA_INSTRUCTIONS.get(mode_str, "")

    prompt_text = _PROMPT_TEMPLATE.format(
        guide_mode=mode_str,
        persona_prompt=persona_prompt,
        visual_analysis_json=vis.model_dump_json(indent=2),
        context_analysis_json=ctx.model_dump_json(indent=2),
        accessibility_analysis_json=acc.model_dump_json(indent=2),
    )
    prompt_part = create_text_part(prompt_text)

    data, raw_text = await run_adk_agent(agent, parts=[prompt_part])

    if data is not None:
        return _validate(data)

    if raw_text:
        raw = strip_code_fences(raw_text)
        try:
            data = json.loads(raw)
            return _validate(data)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Storyteller Agent returned unparseable output.\n"
                f"Raw:\n{raw_text}\nError: {exc}"
            ) from exc

    raise ValueError("Storyteller Agent returned an empty response from Google ADK runner.")


def _validate(data: dict) -> StoryAnalysis:
    try:
        return StoryAnalysis(**data)
    except Exception as exc:
        raise ValueError(
            f"Storyteller Agent output failed StoryAnalysis validation.\n"
            f"Error: {exc}\nData: {json.dumps(data, indent=2)}"
        ) from exc
