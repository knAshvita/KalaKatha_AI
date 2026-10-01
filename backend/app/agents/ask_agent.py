"""
app/agents/ask_agent.py  –  KalaKatha AI
══════════════════════════════════════════
Ask Agent  —  Google ADK Specialist
══════════════════════════════════════════

RESPONSIBILITY
───────────────
Answers natural language questions about the currently analyzed artwork.
Grounded exclusively in the stored ArtworkUnderstanding and StoryAnalysis from the session.
No independent ContextAgent, AccessibilityAgent, LearningAgent, or ExploreAgent are invoked.
The image is never re-analyzed.

BEHAVIORAL CONTRACT
───────────────────
  • Dedicated artwork guide — NOT a generic chatbot.
  • Answers specifically about the current artwork and its artistic/historical sphere.
  • If information is not determinable, explicitly states that it is uncertain or unknown.
  • Never invents historical facts, dates, biographies, or visual features.
  • Adopts the tone and persona of the active guide_mode.
  • Tracks and outputs source_context indicating which analysis aspects provided the facts.

OUTPUT  →  AskResponse (Pydantic)
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
    AskResponse,
    ContextAnalysis,
    GuideMode,
    InteractiveQuestion,
    KalaKathaExperience,
    LearningAnalysis,
    StoryAnalysis,
    VisualAnalysis,
)
from app.services.session_store import ArtworkSession, session_store

# ─────────────────────────────────────────────────────────────────────────────
#  GUIDE MODE PERSONA PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

_PERSONA_INSTRUCTIONS: dict[str, str] = {
    "storyteller": (
        "TONE & STYLE: Storyteller persona. Answer with rich, evocative, narrative cadence. "
        "Engage the visitor's imagination while remaining strictly grounded in known facts."
    ),
    "professor": (
        "TONE & STYLE: Art History Professor persona. Answer with academic precision, curatorial depth, "
        "and clear art-historical terminology. Cite visual evidence and historical context."
    ),
    "friendly": (
        "TONE & STYLE: Friendly Docent persona. Answer with warm, conversational enthusiasm. "
        "Explain complex art concepts simply and warmly as if talking directly to a curious friend in the gallery."
    ),
    "accessibility": (
        "TONE & STYLE: Accessibility specialist persona. Focus on spatial arrangement, tactile textures, "
        "and sensory navigation so visually impaired listeners can easily visualize the details."
    ),
}

_BASE_SYSTEM_INSTRUCTIONS = """\
You are the Ask Agent for KalaKatha AI — a specialized museum gallery docent.

Your sole duty is to answer questions specifically and accurately about the
currently analyzed artwork using ONLY the stored ArtworkUnderstanding and StoryAnalysis:
  - Visual observations (composition, colors, focus, actions, depicted subjects)
  - Historical, cultural, and artistic context (provenance, period, symbolism, techniques)
  - Spatial and accessible description (8-zone layout, audio description)
  - Story chapters (museum tour narrative, thematic arcs)
  - Previous conversation history (for multi-turn dialogue continuity)

════════════════════════════  STRICT RULES  ════════════════════════════════

RULE 1 — NEVER BE A GENERIC CHATBOT
Answer exclusively about this specific artwork, its creator, its style, and its immediate artistic context.
If asked an off-topic question unrelated to the artwork or art history:
Politely redirect the visitor back to the artwork.

RULE 2 — STRICT HONESTY & EPISTEMIC HUMILITY
DO NOT INVENT FACTS.
If the information is not present in the stored understanding or verifiable art history,
explicitly state that it is uncertain, disputed, or unknown.

RULE 3 — MULTI-TURN CONTINUITY
Consider the previous conversation turns. If the visitor uses pronouns ("who is she?", "what about his left hand?"),
resolve references based on conversation context and the artwork.

RULE 4 — SOURCE ATTRIBUTION
Identify which aspects of the artwork understanding or story informed your response in `source_context`.
Allowed values: "ArtworkUnderstanding", "VisualAnalysis", "ContextAnalysis", "AccessibilityAnalysis", "StoryAnalysis", "LearningAnalysis".

RULE 5 — EDUCATIONAL TEACHING & PEDAGOGY (ABSORBED LEARNING)
You are the educational mentor for the artwork.
When the visitor asks "What can I learn from this artwork?", "Explain the symbolism", "What technique was used?", "Teach me about this period/artist", or requests learning points:
Provide structured, illuminating educational explanations grounded in the stored techniques, symbolism, and historical facts.
Deliver the explanation matching the chosen guide persona.

RULE 6 — NEVER CALL ART ANALYST
You must exclusively use the stored session data. Never invoke ArtAnalyst or trigger image re-analysis.

RULE 7 — OUTPUT FORMAT
Return ONE valid JSON object conforming to the AskResponse schema.
"""

_ASK_PROMPT_TEMPLATE = """\
Artwork: "{artwork_title}" by {artist} ({period}, {style})
Guide Mode: {guide_mode}
{persona_guidance}

════════════════════  STORED ARTWORK UNDERSTANDING & STORY  ════════════════════

1. VISUAL OBSERVATIONS:
{visual_json}

2. ART-HISTORICAL CONTEXT & SYMBOLISM:
{context_json}

3. ACCESSIBLE SPATIAL DESCRIPTION:
{accessibility_json}

4. STORY TOUR CHAPTERS:
{story_json}

5. EDUCATIONAL CONCEPTS:
{learning_json}

════════════════════  CONVERSATION HISTORY  ════════════════════
{history_text}

════════════════════  CURRENT VISITOR QUESTION  ════════════════════
Question: "{question}"

Answer the visitor's question thoroughly and engagingly. Return ONE JSON object:
{{
  "session_id": "{session_id}",
  "question": "{question}",
  "answer": "<your thorough, grounded answer in the chosen persona tone>",
  "source_context": ["<AnalysisName1>", "<AnalysisName2>"]
}}
"""


# ─────────────────────────────────────────────────────────────────────────────
#  AGENT CLASS & CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

class AskAgent(KalaKathaBaseAgent):
    """
    Google ADK Specialist Agent: AskAgent
    Answers visitor inquiries grounded in the 5 specialist analyses and conversation history.
    """

    guide_mode: str = "storyteller"

    def __init__(self, guide_mode: str = "storyteller", **kwargs: Any) -> None:
        settings = get_settings()
        persona_text = _PERSONA_INSTRUCTIONS.get(guide_mode, _PERSONA_INSTRUCTIONS["storyteller"])
        full_instructions = f"{_BASE_SYSTEM_INSTRUCTIONS}\n\n{persona_text}"

        init_kwargs: dict[str, Any] = {
            "name": f"ask_agent_{guide_mode}",
            "model": settings.model_or_default,
            "instruction": full_instructions,
            "output_schema": AskResponse,
            "output_key": "ask_response",
            "guide_mode": guide_mode,
        }
        init_kwargs.update(kwargs)
        super().__init__(**init_kwargs)

    async def answer(
        self,
        session_id: str,
        question: str,
        session: ArtworkSession | None = None,
    ) -> AskResponse:
        return await answer_question(session_id=session_id, question=question, session=session)


def build_agent(guide_mode: str = "storyteller") -> AskAgent:
    """Build the official Google ADK AskAgent."""
    return AskAgent(guide_mode=guide_mode)


def build_ask_config(guide_mode: str = "storyteller") -> AskAgent:
    """Alias for backwards compatibility with tests and callers."""
    return build_agent(guide_mode=guide_mode)


# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC ENTRY POINT — Q&A
# ─────────────────────────────────────────────────────────────────────────────

async def answer_question(
    session_id: str,
    question: str,
    session: ArtworkSession | None = None,
) -> AskResponse:
    """
    Answer an artwork-specific question via the AskAgent.
    """
    if session is None:
        session = session_store.get(session_id)
        if session is None:
            raise KeyError(
                f"Session '{session_id}' not found. Please analyze an artwork first via POST /api/analyze."
            )

    exp: KalaKathaExperience = session.experience
    guide_mode = session.guide_mode or "storyteller"
    persona_guidance = _PERSONA_INSTRUCTIONS.get(guide_mode, _PERSONA_INSTRUCTIONS["storyteller"])

    if session.history:
        history_lines = []
        for turn in session.history[-5:]:
            history_lines.append(f"Visitor: {turn.question}")
            history_lines.append(f"Guide: {turn.answer}")
        history_text = "\n".join(history_lines)
    else:
        history_text = "(No previous conversation turns. This is the first question.)"

    agent = build_agent(guide_mode=guide_mode)

    prompt_text = _ASK_PROMPT_TEMPLATE.format(
        artwork_title=exp.artwork.title,
        artist=exp.artwork.artist,
        period=exp.artwork.period,
        style=exp.artwork.style,
        guide_mode=guide_mode,
        persona_guidance=persona_guidance,
        visual_json=exp.visual_analysis.model_dump_json(indent=2),
        context_json=exp.context.model_dump_json(indent=2),
        accessibility_json=exp.accessibility.model_dump_json(indent=2),
        story_json=exp.story.model_dump_json(indent=2),
        learning_json=exp.learning.model_dump_json(indent=2),
        history_text=history_text,
        question=question,
        session_id=session_id,
    )
    prompt_part = create_text_part(prompt_text)

    data, raw_text = await run_adk_agent(agent, parts=[prompt_part])

    parsed: dict[str, Any] = {}
    if isinstance(data, dict):
        parsed = dict(data)
    elif raw_text:
        raw = strip_code_fences(raw_text)
        try:
            loaded = json.loads(raw)
            if isinstance(loaded, dict):
                parsed = loaded
            else:
                parsed = {"answer": str(loaded)}
        except Exception:
            parsed = {"answer": raw.strip()}
    else:
        raise ValueError("AskAgent returned an empty response from Google ADK runner.")

    parsed.setdefault("session_id", session_id)
    parsed.setdefault("question", question)
    parsed.setdefault("source_context", ["VisualAnalysis", "ContextAnalysis"])
    if not parsed.get("answer"):
        parsed["answer"] = (raw_text or "").strip() or "No detailed answer was provided."

    try:
        ask_response = AskResponse(**parsed)
    except Exception as exc:
        raise ValueError(
            f"AskAgent output failed AskResponse validation: {exc}\nData: {parsed}"
        ) from exc

    session_store.add_turn(session_id, question, ask_response.answer)
    return ask_response



# ─────────────────────────────────────────────────────────────────────────────
#  INTERACTIVE QUESTIONS GENERATOR (Used by Root Orchestrator)
# ─────────────────────────────────────────────────────────────────────────────

_QUESTIONS_SYSTEM = """\
You are an interactive museum engagement specialist.
Generate exactly 5 interactive questions about this artwork covering:
  - "observation" (noticing visual details)
  - "interpretation" (reading emotional tone, symbolism)
  - "creativity" (imaginative engagement)
Return valid JSON array only.
"""

_QUESTIONS_PROMPT = """\
Visual analysis:
{visual_analysis_json}

Artistic context:
{artistic_context_json}

Generate 5 interactive questions as a JSON array of objects:
[
  {{
    "question": "<the question>",
    "hint": "<a helpful hint>",
    "category": "<observation | interpretation | creativity>"
  }}
]
"""


async def generate_questions(
    image_path: Path,
    visual: VisualAnalysis,
    context: ContextAnalysis,
) -> list[InteractiveQuestion]:
    """Generate 5 interactive reflection questions for exploration."""
    settings = get_settings()
    agent = Agent(
        name="questions_agent",
        model=settings.model_or_default,
        instruction=_QUESTIONS_SYSTEM,
    )

    prompt_text = _QUESTIONS_PROMPT.format(
        visual_analysis_json=visual.model_dump_json(indent=2),
        artistic_context_json=context.model_dump_json(indent=2),
    )
    prompt_part = create_text_part(prompt_text)

    try:
        _, raw_text = await run_adk_agent(agent, parts=[prompt_part])
        if raw_text:
            cleaned = strip_code_fences(raw_text)
            items = json.loads(cleaned)
            if isinstance(items, list):
                return [InteractiveQuestion(**q) for q in items]
    except Exception:
        pass

    # Graceful fallback if formatting issues occur
    return [
        InteractiveQuestion(
            question="What is the first detail that captures your gaze in this artwork?",
            hint="Consider the lighting and colors.",
            category="observation",
        ),
        InteractiveQuestion(
            question="What mood does the artist convey through the color palette?",
            hint="Observe the contrast between warm and cool tones.",
            category="interpretation",
        ),
        InteractiveQuestion(
            question="If you could step into this artwork, what sounds would you hear?",
            hint="Imagine the environment surrounding the subject.",
            category="creativity",
        ),
    ]
