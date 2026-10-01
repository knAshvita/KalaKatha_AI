"""
app/api/ask.py  –  POST /api/ask
══════════════════════════════════
Artwork Q&A endpoint. Accepts a session_id and user question.
Uses the Google ADK AskAgent to provide an artwork-specific answer
grounded in the 5 specialist analyses and previous conversation turns.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.agents.ask_agent import answer_question
from app.schemas.artwork import AskRequest, AskResponse

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Q&A"])


@router.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask a question about the active artwork",
    description=(
        "Send a natural language question referencing an active artwork session_id. "
        "The Google ADK AskAgent grounds its answer specifically in the artwork's "
        "visual, context, accessibility, story, and learning analyses."
    ),
    status_code=status.HTTP_200_OK,
)
async def ask_endpoint(body: AskRequest) -> AskResponse:
    try:
        return await answer_question(
            session_id=body.session_id,
            question=body.question,
        )
    except KeyError as exc:
        logger.warning("Session not found in ask_endpoint: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc).strip("'\""),
        ) from exc
    except Exception as exc:
        logger.exception("AskAgent error during question processing: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AskAgent failed: {type(exc).__name__}: {exc}",
        ) from exc

