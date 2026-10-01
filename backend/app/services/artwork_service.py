"""
app/services/artwork_service.py  –  KalaKatha AI
══════════════════════════════════════════════════
NOTICE: Artwork orchestration is handled by the Google ADK Root Agent.

The multi-agent pipeline is coordinated by:
  app/agents/root_agent.py  →  KalaKathaRootAgent.execute_experience()

Which is invoked directly from the FastAPI layer:
  app/api/artwork.py  →  POST /api/analyze

This file is intentionally empty — it is kept so that any legacy import
paths do not cause ImportError during refactor transitions.

Pipeline (sequential, run by KalaKathaRootAgent):
  Stage 1 – ArtAnalystAgent       → ArtworkUnderstanding (visual, identity, context, spatial)
  Stage 2 – StorytellerAgent      → StoryAnalysis (multi-chapter audio guide)
  Stage 3 – KalaKathaExperience   (synthesized by root orchestrator & saved in session store)
  On-demand – AskAgent            (answers visitor follow-ups and educational queries)
  On-demand – TTSService          (synthesizes audio for tour chapters)
"""

