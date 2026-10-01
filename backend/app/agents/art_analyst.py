"""
app/agents/art_analyst.py
══════════════════════════════════════════════════════════════════════════════
Art Analyst Agent  –  KalaKatha AI
══════════════════════════════════════════════════════════════════════════════

PURPOSE
────────
A unified Google ADK specialist agent whose responsibility is the complete
multimodal understanding of an artwork image in a single pass.

It produces:
  1. Artwork Identification (title, artist, period, style, confidence, basis)
     following the epistemic uncertainty protocol.
  2. Pure Visual Observation (objects, people, colors, lighting, composition, mood).
  3. Context & Art History (historical, cultural, artistic movement, symbolism, craft).
  4. Spatial & Accessibility Mapping (8-zone spatial breakdown, WCAG audio description).

EPISTEMIC SAFETY RULES
──────────────────────
  • Never invent identity; if uncertain, set title, artist, period to "unknown"
    and confidence to "uncertain".
  • Describe only observable evidence for visual fields.
  • Tag contextual claims with certainty ("verified", "interpreted", "uncertain").
  • Do not use visual idioms ("as you can see") in accessibility descriptions.

OUTPUT
──────
  ArtworkUnderstanding (Pydantic model containing all grounding dimensions).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from google.adk.agents import Agent
from google.genai import types as genai_types

from app.agents.base import KalaKathaBaseAgent
from app.agents.adk_runner import create_image_part, create_text_part, run_adk_agent, strip_code_fences
from app.config import get_settings
from app.schemas.artwork import ArtworkUnderstanding, VisualAnalysis

# ─────────────────────────────────────────────────────────────────────────────
#  SYSTEM INSTRUCTIONS  –  unified artwork understanding contract
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM_INSTRUCTIONS = """\
You are the Art Analyst Agent for KalaKatha AI — the unified artwork understanding specialist.
You conduct an expert, comprehensive multimodal analysis of the artwork in a single pass:

═══════════════════════════  ABSOLUTE RULES  ════════════════════════════════

RULE 1 — IDENTIFICATION & UNCERTAINTY PROTOCOL
  - If the artwork is a known, recognizable work (e.g. Mona Lisa, The Starry Night,
    Girl with a Pearl Earring) or has a legible inscription/signature:
    Identify title, artist, period, and style. Set confidence to "high" or "medium"
    and state the visual/contextual grounds in "basis".
  - If the artwork cannot be confidently identified:
    Set title, artist, and period to "unknown" and confidence to "uncertain".
    Do NOT fabricate names or turn weak visual similarity into a definite claim.

RULE 2 — RIGOROUS VISUAL OBSERVATION
  Describe what is physically observable in the image:
  - summary: 2-3 sentence overview of the composition, subject, and medium.
  - objects: all inanimate objects, tools, furniture, vegetation, still life items.
  - people: count, apparent age groups, clothing, postures, facial expressions.
  - animals: any depicted creatures.
  - environment: setting, weather, time of day cues, background setting.
  - architecture: visible buildings, arches, walls, columns.
  - colors: dominant palette, tonal values, warm/cool balance, contrast levels.
  - lighting: light direction, quality, shadows, highlights, chiaroscuro.
  - composition: arrangement across planes, focal point, leading lines.
  - perspective: linear/atmospheric/flat depth cues, viewpoint height.
  - visual_focus: where the eye is drawn first and why.
  - visible_actions: physical actions depicted.
  - mood: emotional tone grounded in visual evidence (color, light, posture).
  - confidence_notes: caveats on uncertain observations ("none" if confident).

RULE 3 — CONTEXT & ART HISTORY
  Provide contextual grounding, tagging every claim with certainty ("verified", "interpreted", "uncertain") and basis:
  - historical_context: Era, dates, political climate, patronage, historical events.
  - cultural_context: Cultural traditions, societal norms, religious significance.
  - artistic_context: Art movement, school, innovations, historical place.
  - symbolism: Iconographic and allegorical motifs grounded in art history.
  - artistic_techniques: Observable techniques (e.g. sfumato, impasto, chiaroscuro, glazing).

RULE 4 — ACCESSIBILITY & SPATIAL MAPPING
  Build a spatial mental model for visually impaired visitors:
  - spatial_description: Describe 8 zones (top, bottom, left, right, center, foreground, background, relationships).
  - accessibility_description: Sequential audio-described narration. NEVER use sight-presupposing idioms ("as you can see", "look here", "you see").
  - alt_text: Concise 1-2 sentence screen reader description.

RULE 5 — OUTPUT FORMAT
  Return ONE valid JSON object conforming to the ArtworkUnderstanding schema.
  Do NOT wrap in markdown code blocks.
"""

_ANALYSIS_PROMPT = """\
Conduct a complete multimodal analysis of this artwork image.
Adhere strictly to the epistemic safety rules and uncertainty protocol.

Return valid JSON conforming to the ArtworkUnderstanding schema:
{
  "identification": {
    "title": "<identified title or 'unknown'>",
    "artist": "<identified artist or 'unknown'>",
    "period": "<identified period or 'unknown'>",
    "style": "<identified style or 'unknown'>",
    "confidence": "<high|medium|low|uncertain>",
    "basis": "<reasoning for identification or uncertainty>"
  },
  "summary": "<2-3 sentence visual summary>",
  "objects": ["<object 1>", "<object 2>"],
  "people": ["<person 1 description>"],
  "animals": ["<animal 1>"],
  "environment": "<observable setting>",
  "architecture": "<observable architectural elements or 'none visible'>",
  "colors": "<dominant palette, warm/cool balance, contrast>",
  "lighting": "<light direction, quality, chiaroscuro>",
  "composition": "<foreground/middle/background layout, leading lines>",
  "perspective": "<viewpoint, depth cues>",
  "visual_focus": "<primary focal point and why>",
  "visible_actions": ["<visible action 1>"],
  "mood": "<emotional tone citing color/lighting cues>",
  "confidence_notes": "<caveats on uncertain fields or 'none'>",
  "historical_context": [
    {"claim": "<claim>", "certainty": "<verified|interpreted|uncertain>", "basis": "<basis>"}
  ],
  "cultural_context": [
    {"claim": "<claim>", "certainty": "<verified|interpreted|uncertain>", "basis": "<basis>"}
  ],
  "artistic_context": [
    {"claim": "<claim>", "certainty": "<verified|interpreted|uncertain>", "basis": "<basis>"}
  ],
  "symbolism": [
    {"claim": "<claim>", "certainty": "<verified|interpreted|uncertain>", "basis": "<basis>"}
  ],
  "artistic_techniques": [
    {"claim": "<claim>", "certainty": "<verified|interpreted|uncertain>", "basis": "<basis>"}
  ],
  "spatial_description": {
    "top": "<upper elements>",
    "bottom": "<lower elements>",
    "left": "<left elements>",
    "right": "<right elements>",
    "center": "<central subjects>",
    "foreground": "<closest depth elements>",
    "background": "<distant environmental setting>",
    "relationships": "<relative spatial and narrative relationships>"
  },
  "accessibility_description": "<concise sequential audio description without sight idioms>",
  "alt_text": "<concise 1-2 sentence screen reader description>"
}
"""


# ─────────────────────────────────────────────────────────────────────────────
#  AGENT CONFIGURATION & CLASS
# ─────────────────────────────────────────────────────────────────────────────

class ArtAnalystAgent(KalaKathaBaseAgent):
    """Google ADK specialist agent for unified artwork understanding."""

    def __init__(self, **kwargs: Any) -> None:
        settings = get_settings()
        init_kwargs: dict[str, Any] = {
            "name": "art_analyst",
            "model": settings.model_or_default,
            "instruction": _SYSTEM_INSTRUCTIONS,
            "output_schema": ArtworkUnderstanding,
            "output_key": "artwork_understanding",
        }
        init_kwargs.update(kwargs)
        super().__init__(**init_kwargs)

    async def analyze(self, image_path: Path) -> ArtworkUnderstanding:
        return await analyze_image(image_path)


def build_agent() -> ArtAnalystAgent:
    """Build the official Google ADK ArtAnalystAgent."""
    return ArtAnalystAgent()


def build_agent_config() -> ArtAnalystAgent:
    """Alias for backwards compatibility with tests and orchestrator."""
    return build_agent()


# Exported singleton
agent_config: ArtAnalystAgent = build_agent()


# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

async def analyze_image(image_path: Path) -> ArtworkUnderstanding:
    """
    Run the Art Analyst Google ADK Agent on a single artwork image.
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Artwork image not found: {image_path}")

    agent = build_agent()
    image_part = create_image_part(image_path)
    prompt_part = create_text_part(_ANALYSIS_PROMPT)

    data, raw_text = await run_adk_agent(agent, parts=[image_part, prompt_part])

    if data is not None:
        return _validate(data)

    if raw_text:
        raw = strip_code_fences(raw_text)
        try:
            data = json.loads(raw)
            return _validate(data)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Art Analyst Agent returned unparseable output.\n"
                f"--- Raw response ---\n{raw_text}\n"
                f"JSON error: {exc}"
            ) from exc

    raise ValueError("Art Analyst Agent returned an empty response from Google ADK runner.")


def _validate(data: dict) -> ArtworkUnderstanding:
    """Validate a raw dict against ArtworkUnderstanding with backwards compatibility."""
    try:
        # Support legacy visual analysis format if passed in tests
        if "identification" not in data and "artwork_title" in data:
            data = dict(data)
            data["identification"] = {
                "title": data.get("artwork_title", "unknown"),
                "artist": data.get("artist", "unknown"),
                "style": data.get("style", "unknown"),
                "period": data.get("period", "unknown"),
                "confidence": "high" if data.get("artwork_title", "unknown") != "unknown" else "uncertain",
                "basis": "Inferred from visual observation",
            }
        if "spatial_description" not in data:
            data = dict(data)
            data["spatial_description"] = {
                "top": data.get("environment", "Upper area"),
                "bottom": "Lower area",
                "left": "Left side",
                "right": "Right side",
                "center": data.get("visual_focus", "Central composition"),
                "foreground": data.get("visual_focus", "Foreground elements"),
                "background": data.get("environment", "Background elements"),
                "relationships": "Spatial elements arranged across planes",
            }
        if "accessibility_description" not in data:
            data = dict(data)
            data["accessibility_description"] = data.get("summary", "Visual description of the artwork.")
        if "alt_text" not in data:
            data = dict(data)
            data["alt_text"] = data.get("summary", "Artwork visual description.")

        return ArtworkUnderstanding(**data)
    except Exception as exc:
        raise ValueError(
            f"Art Analyst Agent output failed ArtworkUnderstanding validation.\n"
            f"Validation error: {exc}\n"
            f"Data received: {json.dumps(data, indent=2)}"
        ) from exc
