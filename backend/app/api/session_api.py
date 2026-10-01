"""
app/api/session_api.py  –  GET /api/session/{session_id}
════════════════════════════════════════════════════════
Endpoint to retrieve an active artwork session's full KalaKathaExperience.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.artwork import KalaKathaExperience
from app.services.session_store import session_store

router = APIRouter(prefix="/api/session", tags=["Session"])


@router.get(
    "/{session_id}",
    response_model=KalaKathaExperience,
    summary="Retrieve full artwork session experience",
    description=(
        "Fetch the complete, validated KalaKathaExperience for a given session ID, "
        "including visual analysis, context, story chapters, learning quiz, "
        "accessibility description, and interactive explore regions."
    ),
    status_code=status.HTTP_200_OK,
)
async def get_session_endpoint(session_id: str) -> KalaKathaExperience:
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found. Please analyze an artwork first.",
        )
    return session.experience
