"""
Q&A API Router – POST /api/qa
──────────────────────────────
Accepts a user question and the previously generated artwork analysis
context, then returns an AI-generated answer grounded in that context.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

# pyrefly: ignore [missing-import]
from app.agents.qa_agent import run_qa
from app.schemas.artwork import QARequest, QAResponse

router = APIRouter(prefix="/api", tags=["Q&A"])


@router.post(
    "/qa",
    response_model=QAResponse,
    summary="Ask a question about the artwork",
    description=(
        "Send a natural language question along with the artwork analysis context "
        "returned by POST /api/analyze. The AI grounds its answer in that context."
    ),
    status_code=status.HTTP_200_OK,
)
async def qa_endpoint(body: QARequest) -> QAResponse:
    try:
        return await run_qa(
            question=body.question,
            artwork_context=body.artwork_context,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Q&A failed: {exc}",
        ) from exc
