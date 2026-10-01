"""
app/agent.py  –  KalaKatha AI Root Orchestrator
═══════════════════════════════════════════════════════════════════════════════
Main orchestration interface coordinating the KalaKatha AI multi-agent
workflow using the Google ADK KalaKathaRootAgent.

WORKFLOW:
  Artwork Image
        ↓
  ArtAnalystAgent        (unified multimodal pass: visual + identity + context + spatial mapping)
        ↓
  StorytellerAgent       (synthesizes understanding into multi-chapter audio tour)
        ↓
  KalaKathaExperience    (persisted in session store for AskAgent & TTSService)
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

from app.agents.root_agent import (
    KalaKathaRootAgent,
    OrchestrationError,
    build_root_agent_config,
)
from app.schemas.artwork import (
    ArtworkAnalysisResponse,
    AnalysisStatus,
    GuideMode,
    KalaKathaExperience,
)

# Root agent singleton instance
root_agent = KalaKathaRootAgent()


async def run_experience(
    image_path: Path,
    filename: str,
    guide_mode: Union[GuideMode, str] = GuideMode.STORYTELLER,
    session_id: str | None = None,
) -> KalaKathaExperience:
    """
    Execute the multi-agent workflow using KalaKathaRootAgent and return
    the complete KalaKathaExperience model.

    Raises:
        OrchestrationError: If any specialist agent in the chain fails,
                            with diagnostic error details.
    """
    return await root_agent.execute_experience(
        image_path=image_path,
        filename=filename,
        guide_mode=guide_mode,
        session_id=session_id,
    )


async def run_analysis(
    image_path: Path,
    filename: str,
    guide_mode: Union[GuideMode, str] = GuideMode.STORYTELLER,
    session_id: str | None = None,
) -> ArtworkAnalysisResponse:
    """
    Execute the KalaKathaRootAgent pipeline and return an ArtworkAnalysisResponse
    envelope with the unified KalaKathaExperience attached.
    """
    experience = await run_experience(
        image_path=image_path,
        filename=filename,
        guide_mode=guide_mode,
        session_id=session_id,
    )

    return ArtworkAnalysisResponse(
        status=AnalysisStatus.SUCCESS,
        session_id=experience.session_id,
        filename=filename,
        visual_analysis=experience.visual_analysis,
        context=experience.context,
        accessibility=experience.accessibility,
        immersive_story=experience.story,
        learning_content=experience.learning,
        interactive_questions=experience.explore.interactive_questions,
        experience=experience,
    )
