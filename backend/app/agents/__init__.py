"""
KalaKatha AI  –  Agents Package
════════════════════════════════
Streamlined Google ADK specialist agents, plus the root orchestrator.

TARGET ARCHITECTURE:
  1. art_analyst       →  analyze_image(image_path) → ArtworkUnderstanding
  2. storyteller_agent →  generate_story(understanding, guide_mode) → StoryAnalysis
  3. ask_agent         →  answer_question(session_id, question) → AskResponse
  4. root_agent        →  KalaKathaRootAgent (linear orchestrator)
"""
from app.agents.art_analyst import (
    ArtAnalystAgent,
    analyze_image,
    agent_config as art_analyst_config,
)
from app.agents.storyteller_agent import (
    StorytellerAgent,
    generate_story,
    agent_config as storyteller_config,
)
from app.agents.ask_agent import (
    AskAgent,
    answer_question,
    generate_questions,
)
from app.agents.root_agent import (
    KalaKathaRootAgent,
    OrchestrationError,
    build_root_agent_config,
)

__all__ = [
    # Classes & Specialist Agents
    "KalaKathaRootAgent",
    "OrchestrationError",
    "ArtAnalystAgent",
    "StorytellerAgent",
    "AskAgent",
    # Runner functions
    "analyze_image",
    "generate_story",
    "answer_question",
    "generate_questions",
    # Exported configs
    "art_analyst_config",
    "storyteller_config",
]
