"""
app/api/quiz.py  –  POST /api/quiz/answer
═════════════════════════════════════════
Endpoint for validating user answers to multiple-choice quiz questions
generated during artwork analysis and stored in the session.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.artwork import QuizAnswerRequest, QuizAnswerResponse
from app.services.quiz_service import verify_quiz_answer

router = APIRouter(prefix="/api/quiz", tags=["Quiz"])


@router.post(
    "/answer",
    response_model=QuizAnswerResponse,
    summary="Submit and check a quiz answer",
    description=(
        "Submit a user answer to a multiple-choice question from an active artwork session. "
        "Evaluates the answer against the session's quiz and returns correctness, "
        "the correct option, and an educational explanation."
    ),
    status_code=status.HTTP_200_OK,
)
async def submit_quiz_answer_endpoint(body: QuizAnswerRequest) -> QuizAnswerResponse:
    try:
        return verify_quiz_answer(
            session_id=body.session_id,
            question_id=body.question_id,
            selected_option=body.selected_option,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc).strip("'\""),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quiz verification failed: {exc}",
        ) from exc
