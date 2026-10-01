"""
app/agents/root_agent.py  –  KalaKatha AI Root Orchestrator
══════════════════════════════════════════════════════════════════════════════
KalaKathaRootAgent  —  Google ADK Master Orchestrator (Streamlined)
══════════════════════════════════════════════════════════════════════════════

RESPONSIBILITY
───────────────
Coordinates the streamlined KalaKatha AI workflow:

Artwork Image
      ↓
ArtAnalystAgent        (single multimodal pass: visual + identity + context + spatial mapping)
      ↓
StorytellerAgent       (synthesizes artwork understanding into multi-chapter audio tour)
      ↓
Session Store          (persists experience; AskAgent & TTS access on-demand)

All downstream learning and interactive questions are answered by AskAgent
from the stored session without invoking additional models during initial analysis.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Union

from app.config import get_settings
from app.agents.art_analyst import ArtAnalystAgent, analyze_image
from app.agents.storyteller_agent import StorytellerAgent, generate_story
from app.schemas.artwork import (
    AccessibilityAnalysis,
    ArtworkIdentification,
    ArtworkMetadata,
    ArtworkRegion,
    ArtworkUnderstanding,
    ContextAnalysis,
    ExploreContent,
    GuideMode,
    InteractiveQuestion,
    KalaKathaExperience,
    LearningAnalysis,
    RegionPosition,
    SpatialDescription,
    StoryAnalysis,
    VisualAnalysis,
)

logger = logging.getLogger("kalakatha.root_agent")


# ─────────────────────────────────────────────────────────────────────────────
#  CONTROLLED ERROR HANDLING
# ─────────────────────────────────────────────────────────────────────────────

class OrchestrationError(Exception):
    """Raised when an ADK specialist agent fails during root orchestration."""

    def __init__(
        self,
        agent_name: str,
        stage: str,
        message: str,
        cause: Exception | None = None,
    ):
        super().__init__(f"[{agent_name}] Stage '{stage}' failed: {message}")
        self.agent_name = agent_name
        self.stage = stage
        self.message = message
        self.cause = cause

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "error",
            "failed_agent": self.agent_name,
            "failed_stage": self.stage,
            "error_message": self.message,
            "cause": str(self.cause) if self.cause else None,
        }


# ─────────────────────────────────────────────────────────────────────────────
#  ADK TOOLS FOR ROOT AGENT (Delegation interfaces)
# ─────────────────────────────────────────────────────────────────────────────

async def run_art_analyst_stage(image_path_str: str) -> ArtworkUnderstanding:
    """Tool: Run ArtAnalystAgent to perform unified multimodal analysis of the artwork image."""
    path = Path(image_path_str)
    if not path.exists():
        raise FileNotFoundError(f"Artwork image file not found at: {image_path_str}")
    return await analyze_image(path)


async def run_storyteller_stage(
    understanding: ArtworkUnderstanding | VisualAnalysis,
    guide_mode: Union[GuideMode, str] = GuideMode.STORYTELLER,
) -> StoryAnalysis:
    """Tool: Run StorytellerAgent to create an interactive 4-6 chapter museum audio tour."""
    return await generate_story(
        understanding_or_visual=understanding,
        guide_mode=guide_mode,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  ROOT AGENT SYSTEM INSTRUCTIONS & CONFIG
# ─────────────────────────────────────────────────────────────────────────────

_ROOT_SYSTEM_INSTRUCTIONS = """\
You are KalaKathaRootAgent — the master orchestrator for KalaKatha AI.

Your responsibility is coordinating the specialist Google ADK agents in this streamlined architecture:
1. ArtAnalystAgent: Single multimodal pass producing comprehensive visual observation,
   artwork identification with epistemic uncertainty, historical/cultural context, and spatial mapping.
2. StorytellerAgent: Synthesizes the artwork understanding into an immersive multi-chapter museum audio guide
   tailored to the active guide persona.
3. KalaKathaExperience: Synthesizes and saves the final unified experience in the session store.
"""


@dataclass
class RootAgentConfig:
    """Lightweight config holder for KalaKathaRootAgent."""
    system_instructions: str = field(default=_ROOT_SYSTEM_INSTRUCTIONS)
    model: str = "gemini-2.0-flash"
    tools: list = field(default_factory=list)


def build_root_agent_config() -> RootAgentConfig:
    """Build the RootAgentConfig for the KalaKathaRootAgent."""
    settings = get_settings()
    model = settings.model_or_default or "gemini-2.0-flash"
    return RootAgentConfig(
        model=model,
        tools=[
            run_art_analyst_stage,
            run_storyteller_stage,
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
#  ROOT AGENT CLASS
# ─────────────────────────────────────────────────────────────────────────────

class KalaKathaRootAgent:
    """
    Streamlined Google ADK Master Orchestration Agent for KalaKatha AI.

    Workflow:
    Artwork Image
            ↓
    ArtAnalystAgent (single multimodal pass: visual + identity + context + spatial mapping)
            ↓
    StorytellerAgent (synthesizes artwork understanding into multi-chapter audio tour)
            ↓
    KalaKathaExperience (synthesized & session-stored for AskAgent & TTS)
    """

    def __init__(self):
        self.config = build_root_agent_config()
        self.art_analyst = ArtAnalystAgent()
        self.storyteller_agent = StorytellerAgent()

    async def execute_experience(
        self,
        image_path: Path,
        filename: str,
        guide_mode: Union[GuideMode, str] = GuideMode.STORYTELLER,
        session_id: str | None = None,
    ) -> KalaKathaExperience:
        """
        Orchestrate the streamlined pipeline: ArtAnalyst -> Storyteller -> SessionStore.
        """
        if not session_id:
            session_id = f"kk_{uuid.uuid4().hex[:12]}"
        logger.info(
            "Starting KalaKathaExperience orchestration session=%s for %s (mode=%s)",
            session_id,
            filename,
            guide_mode,
        )

        # ── Pre-flight check ───────────────────────────────────────────────────
        if not image_path.exists():
            raise OrchestrationError(
                agent_name="KalaKathaRootAgent",
                stage="pre_flight",
                message=f"Artwork image file does not exist: {image_path}",
            )

        # ── STAGE 1: UNIFIED ARTWORK UNDERSTANDING (Single multimodal pass) ───
        logger.info("[%s] Stage 1: Invoking ArtAnalystAgent (unified artwork understanding)...", session_id)
        try:
            understanding = await self.art_analyst.analyze(image_path)
        except Exception as exc:
            logger.error("ArtAnalystAgent failed: %s", exc)
            raise OrchestrationError(
                agent_name="ArtAnalystAgent",
                stage="visual_analysis",
                message="Artwork understanding failed. The image could not be interpreted.",
                cause=exc,
            ) from exc

        self._validate_output(understanding, (ArtworkUnderstanding, VisualAnalysis), "ArtAnalystAgent", "visual_analysis")

        # Normalize to ArtworkUnderstanding if a legacy VisualAnalysis was passed
        if isinstance(understanding, VisualAnalysis):
            understanding = ArtworkUnderstanding(
                identification=ArtworkIdentification(
                    title=understanding.artwork_title,
                    artist=understanding.artist,
                    style=understanding.style,
                    period=understanding.period,
                    confidence="high" if understanding.artwork_title != "unknown" else "uncertain",
                    basis="Direct visual analysis",
                ),
                summary=understanding.summary,
                objects=understanding.objects,
                people=understanding.people,
                animals=understanding.animals,
                environment=understanding.environment,
                architecture=understanding.architecture,
                colors=understanding.colors,
                lighting=understanding.lighting,
                composition=understanding.composition,
                perspective=understanding.perspective,
                visual_focus=understanding.visual_focus,
                visible_actions=understanding.visible_actions,
                mood=understanding.mood,
                confidence_notes=understanding.confidence_notes,
                spatial_description=SpatialDescription(
                    top=understanding.environment,
                    bottom="Lower portion",
                    left="Left portion",
                    right="Right portion",
                    center=understanding.visual_focus,
                    foreground=understanding.visual_focus,
                    background=understanding.environment,
                    relationships="Spatial layout across foreground and background",
                ),
                accessibility_description=understanding.summary,
                alt_text=understanding.summary,
            )

        # ── STAGE 2: STORY SYNTHESIS ─────────────────────────────────────────
        logger.info("[%s] Stage 2: Invoking StorytellerAgent (mode=%s)...", session_id, guide_mode)
        try:
            story = await self.storyteller_agent.generate_story(
                understanding_or_visual=understanding,
                guide_mode=guide_mode,
            )
        except Exception as exc:
            logger.error("StorytellerAgent failed: %s", exc)
            raise OrchestrationError(
                agent_name="StorytellerAgent",
                stage="story_generation",
                message="Museum audio guide generation failed.",
                cause=exc,
            ) from exc

        self._validate_output(story, StoryAnalysis, "StorytellerAgent", "story_generation")

        # ── STAGE 3: SYNTHESIS & SESSION PERSISTENCE ─────────────────────────
        logger.info("[%s] Stage 3: Synthesizing final KalaKathaExperience...", session_id)
        artwork_meta = understanding.to_artwork_metadata(filename)
        visual = understanding.to_visual_analysis()
        context = understanding.to_context_analysis()
        accessibility = understanding.to_accessibility_analysis()
        learning = understanding.to_learning_analysis(str(guide_mode))
        explore = understanding.to_explore_content()

        experience = KalaKathaExperience(
            session_id=session_id,
            artwork=artwork_meta,
            visual_analysis=visual,
            context=context,
            story=story,
            learning=learning,
            accessibility=accessibility,
            explore=explore,
            guide_mode=str(guide_mode),
        )

        try:
            from app.services.session_store import session_store
            session_store.save(session_id, experience, guide_mode=str(guide_mode))
        except Exception as exc:
            logger.warning("Failed to save session %s in store: %s", session_id, exc)

        logger.info("[%s] KalaKathaExperience synthesized successfully with 2 model stages.", session_id)
        return experience

    @staticmethod
    def _validate_output(obj: Any, expected_type: Union[type, tuple[type, ...]], agent_name: str, stage: str) -> None:
        """Validate that an upstream specialist agent returned a valid output model."""
        if not isinstance(obj, expected_type):
            type_names = expected_type.__name__ if isinstance(expected_type, type) else "/".join(t.__name__ for t in expected_type)
            raise OrchestrationError(
                agent_name=agent_name,
                stage=stage,
                message=(
                    f"Agent {agent_name} produced invalid output. "
                    f"Expected {type_names}, got {type(obj).__name__}."
                ),
            )
