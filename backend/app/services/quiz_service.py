"""
app/services/quiz_service.py  –  KalaKatha AI Quiz Verification Service
═══════════════════════════════════════════════════════════════════════
Provides logic to evaluate user answers against multiple-choice questions
generated during artwork analysis and stored in SessionStore.
"""
from __future__ import annotations

import re
from typing import Sequence

from app.schemas.artwork import MultipleChoiceQuestion, QuizAnswerResponse
from app.services.session_store import session_store


def check_option_match(selected: str, correct: str, options: Sequence[str]) -> bool:
    """
    Robust comparison between the user's selected choice and the question's correct_option.

    Handles:
      - Single-letter answers: 'A', 'b', 'c', 'd'
      - Prefixed options: 'A) Fresco', 'B. Tempera', 'Option C'
      - Full option text: 'Oil on canvas'
      - Case-insensitive and whitespace-stripped
    """
    sel = selected.strip()
    cor = correct.strip()

    if not sel or not cor:
        return False

    # Exact case-insensitive match
    if sel.lower() == cor.lower():
        return True

    letter_map = {"a": 0, "b": 1, "c": 2, "d": 3}

    # Extract leading choice letter if present: e.g. "A)", "B.", "A -", "Option C"
    def extract_letter(text: str) -> str | None:
        cleaned = text.strip()
        opt_match = re.match(r"^(?:option\s+)?([a-dA-D])(?:\s*[\)\.\:\-]\s*|\s+|$)", cleaned, re.IGNORECASE)
        if opt_match:
            return opt_match.group(1).lower()
        if len(cleaned) == 1 and cleaned.lower() in letter_map:
            return cleaned.lower()
        return None

    # Strip choice letter and prefix from text: e.g. "A) Oil on canvas" -> "oil on canvas"
    def extract_body(text: str) -> str:
        cleaned = text.strip()
        body = re.sub(r"^(?:option\s+)?([a-dA-D])(?:\s*[\)\.\:\-]\s*|\s+)", "", cleaned, flags=re.IGNORECASE)
        return body.strip().lower()

    sel_letter = extract_letter(sel)
    cor_letter = extract_letter(cor)

    # 1. Both resolved to option letters (e.g. 'a' == 'A')
    if sel_letter and cor_letter:
        return sel_letter == cor_letter

    # 2. Selected is a letter, correct is option body text or full option
    if sel_letter and sel_letter in letter_map:
        idx = letter_map[sel_letter]
        if idx < len(options):
            opt_body = extract_body(options[idx])
            cor_body = extract_body(cor)
            if cor_body and (cor_body == opt_body or cor_body in opt_body or opt_body in cor_body):
                return True

    # 3. Correct is a letter, selected is option body text or full option
    if cor_letter and cor_letter in letter_map:
        idx = letter_map[cor_letter]
        if idx < len(options):
            opt_body = extract_body(options[idx])
            sel_body = extract_body(sel)
            if sel_body and (sel_body == opt_body or sel_body in opt_body or opt_body in sel_body):
                return True

    # 4. Compare stripped option bodies directly
    sel_body = extract_body(sel)
    cor_body = extract_body(cor)
    if sel_body and cor_body and sel_body == cor_body:
        return True

    return False


def verify_quiz_answer(
    session_id: str,
    question_id: str,
    selected_option: str,
) -> QuizAnswerResponse:
    """
    Validate a user's answer to a multiple choice question in the given artwork session.

    Raises:
        KeyError: If session_id is not found or question_id does not exist.
    """
    session = session_store.get(session_id)
    if not session:
        raise KeyError(f"Session '{session_id}' not found. Please analyze an artwork first.")

    exp = session.experience
    mcqs = exp.learning.multiple_choice_questions
    if not mcqs:
        raise KeyError(f"No quiz questions available for session '{session_id}'.")

    # Match question_id (case-insensitive, optional 'q' prefix)
    target_id = question_id.strip().lower()
    matched_q: MultipleChoiceQuestion | None = None

    for q in mcqs:
        curr_id = q.question_id.strip().lower()
        if curr_id == target_id or curr_id.lstrip("q") == target_id.lstrip("q"):
            matched_q = q
            break

    if not matched_q:
        available = [q.question_id for q in mcqs]
        raise KeyError(
            f"Question '{question_id}' not found in session '{session_id}'. "
            f"Available questions: {available}"
        )

    is_correct = check_option_match(
        selected=selected_option,
        correct=matched_q.correct_option,
        options=matched_q.options,
    )

    return QuizAnswerResponse(
        session_id=session_id,
        question_id=matched_q.question_id,
        selected_option=selected_option,
        is_correct=is_correct,
        correct_option=matched_q.correct_option,
        explanation=matched_q.explanation,
    )
