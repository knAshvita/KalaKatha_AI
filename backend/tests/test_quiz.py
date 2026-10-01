"""
tests/test_quiz.py  –  Tests for Quiz Answer Endpoint and Verification Service
═════════════════════════════════════════════════════════════════════════════
Tests:
  1. check_option_match logic (letters, prefixes, text, case-insensitivity)
  2. verify_quiz_answer service logic
  3. POST /api/quiz/answer endpoint via FastAPI TestClient
  4. Error handling (404 on missing session / question, 422 on validation)
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.artwork import (
    AccessibilityAnalysis,
    ArtworkMetadata,
    ArtworkRegion,
    ContextAnalysis,
    ExploreContent,
    KalaKathaExperience,
    LearningAnalysis,
    MultipleChoiceQuestion,
    QuizAnswerRequest,
    QuizAnswerResponse,
    RegionPosition,
    SpatialDescription,
    StoryAnalysis,
    VisualAnalysis,
)
from app.services.quiz_service import check_option_match, verify_quiz_answer
from app.services.session_store import session_store

client = TestClient(app)


def _seed_test_session(session_id: str = "test_quiz_session") -> KalaKathaExperience:
    mcqs = [
        MultipleChoiceQuestion(
            question_id="q1",
            question="What is the primary medium used in this artwork?",
            options=["A) Oil on canvas", "B) Fresco", "C) Watercolor", "D) Tempera"],
            correct_option="A) Oil on canvas",
            explanation="The visible brushwork and layered glazing indicate oil paint on canvas.",
        ),
        MultipleChoiceQuestion(
            question_id="q2",
            question="Which art movement does this painting belong to?",
            options=["Impressionism", "Baroque", "Cubism", "Surrealism"],
            correct_option="Baroque",
            explanation="The dramatic chiaroscuro and intense emotion are hallmarks of the Baroque era.",
        ),
        MultipleChoiceQuestion(
            question_id="q3",
            question="What focal object catches the light in the composition?",
            options=["A. Golden goblet", "B. Pearl earring", "C. Silver mirror", "D. Glass vase"],
            correct_option="B",
            explanation="The spherical pearl earring reflects the primary light source.",
        ),
    ]

    exp = KalaKathaExperience(
        session_id=session_id,
        artwork=ArtworkMetadata(
            filename="artwork.jpg",
            title="Masterpiece",
            artist="Old Master",
            style="Baroque",
            period="17th century",
        ),
        visual_analysis=VisualAnalysis(
            artwork_title="Masterpiece",
            artist="Old Master",
            style="Baroque",
            period="17th century",
            summary="A dramatic Baroque portrait.",
            objects=["earring", "collar"],
            people=["noble person"],
            animals=[],
            environment="studio interior",
            architecture="none",
            colors="Dark shadows, warm golden light",
            lighting="Single directional light",
            composition="Diagonal orientation",
            perspective="Close-up",
            visual_focus="The pearl earring",
            visible_actions=[],
            mood="Introspective",
            confidence_notes="none",
        ),
        context=ContextAnalysis(
            historical_context=[],
            cultural_context=[],
            artistic_context=[],
            symbolism=[],
            artistic_techniques=[],
            interesting_facts=[],
            summary="Historical overview.",
            search_queries_suggested=[],
        ),
        story=StoryAnalysis(
            story_title="Tales of Light",
            opening="Welcome to the gallery.",
            chapters=[],
            closing="Thank you for visiting.",
        ),
        learning=LearningAnalysis(
            key_concepts=["Chiaroscuro", "Tenebrism"],
            simple_explanations={"Chiaroscuro": "High contrast between light and dark."},
            interesting_facts=["Painted in 1665."],
            things_to_notice=["Observe the glint of the pearl."],
            multiple_choice_questions=mcqs,
        ),
        accessibility=AccessibilityAnalysis(
            accessibility_description="Description for screen readers.",
            spatial_description=SpatialDescription(
                top="Dark background",
                bottom="Mantle",
                left="Shadow",
                right="Lit face",
                center="Subject",
                foreground="Earring",
                background="Darkness",
                relationships="Earring links light and shadow",
            ),
            short_description="Short summary",
            alt_text="Alt text",
        ),
        explore=ExploreContent(
            regions=[
                ArtworkRegion(
                    region_id="r1",
                    label="Earring",
                    description="Focal highlight",
                    importance="Focal point",
                    related_visual_elements=["earring"],
                    position=RegionPosition(x=0.4, y=0.4, width=0.1, height=0.1),
                )
            ],
            interactive_questions=[],
            topics_to_explore=[],
            coordinate_disclaimer="Approximate",
        ),
        guide_mode="storyteller",
    )
    session_store.save(session_id, exp, guide_mode="storyteller")
    return exp


# ── Option Matching Tests ────────────────────────────────────────────────────

def test_check_option_match_exact():
    options = ["A) Oil on canvas", "B) Fresco", "C) Watercolor", "D) Tempera"]
    assert check_option_match("A) Oil on canvas", "A) Oil on canvas", options) is True
    assert check_option_match("B) Fresco", "A) Oil on canvas", options) is False


def test_check_option_match_single_letter():
    options = ["A) Oil on canvas", "B) Fresco", "C) Watercolor", "D) Tempera"]
    # User submits 'a' or 'A', correct_option is 'A) Oil on canvas'
    assert check_option_match("A", "A) Oil on canvas", options) is True
    assert check_option_match("a", "A) Oil on canvas", options) is True
    assert check_option_match("B", "A) Oil on canvas", options) is False


def test_check_option_match_body_text_to_letter():
    options = ["A. Golden goblet", "B. Pearl earring", "C. Silver mirror", "D. Glass vase"]
    # Correct is 'B', user submits 'Pearl earring'
    assert check_option_match("Pearl earring", "B", options) is True
    assert check_option_match("pearl earring", "B", options) is True
    assert check_option_match("Golden goblet", "B", options) is False


def test_check_option_match_prefixed_variants():
    options = ["Impressionism", "Baroque", "Cubism", "Surrealism"]
    assert check_option_match("Baroque", "Baroque", options) is True
    assert check_option_match("baroque", "Baroque", options) is True
    assert check_option_match("Option B", "Baroque", options) is True


# ── Service Tests ─────────────────────────────────────────────────────────────

def test_verify_quiz_answer_correct():
    session_id = "test_svc_quiz"
    _seed_test_session(session_id)

    res = verify_quiz_answer(session_id=session_id, question_id="q1", selected_option="A")
    assert res.is_correct is True
    assert res.question_id == "q1"
    assert "oil paint on canvas" in res.explanation.lower()


def test_verify_quiz_answer_incorrect():
    session_id = "test_svc_quiz"
    _seed_test_session(session_id)

    res = verify_quiz_answer(session_id=session_id, question_id="q1", selected_option="D")
    assert res.is_correct is False
    assert res.correct_option == "A) Oil on canvas"


def test_verify_quiz_answer_missing_session():
    with pytest.raises(KeyError, match="Session 'unknown_session' not found"):
        verify_quiz_answer(session_id="unknown_session", question_id="q1", selected_option="A")


def test_verify_quiz_answer_missing_question():
    session_id = "test_svc_quiz"
    _seed_test_session(session_id)

    with pytest.raises(KeyError, match="Question 'q99' not found"):
        verify_quiz_answer(session_id=session_id, question_id="q99", selected_option="A")


# ── FastAPI Endpoint Tests ────────────────────────────────────────────────────

def test_api_quiz_answer_endpoint_correct():
    session_id = "test_api_quiz"
    _seed_test_session(session_id)

    payload = {
        "session_id": session_id,
        "question_id": "q2",
        "selected_option": "Baroque",
    }
    response = client.post("/api/quiz/answer", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["question_id"] == "q2"
    assert data["selected_option"] == "Baroque"
    assert data["is_correct"] is True
    assert data["correct_option"] == "Baroque"
    assert "chiaroscuro" in data["explanation"].lower()


def test_api_quiz_answer_endpoint_incorrect():
    session_id = "test_api_quiz"
    _seed_test_session(session_id)

    payload = {
        "session_id": session_id,
        "question_id": "q2",
        "selected_option": "Cubism",
    }
    response = client.post("/api/quiz/answer", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is False
    assert data["correct_option"] == "Baroque"


def test_api_quiz_answer_endpoint_404_session():
    payload = {
        "session_id": "nonexistent_session",
        "question_id": "q1",
        "selected_option": "A",
    }
    response = client.post("/api/quiz/answer", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_api_quiz_answer_endpoint_404_question():
    session_id = "test_api_quiz"
    _seed_test_session(session_id)

    payload = {
        "session_id": session_id,
        "question_id": "nonexistent_question",
        "selected_option": "A",
    }
    response = client.post("/api/quiz/answer", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_api_quiz_answer_endpoint_422_invalid_body():
    # Missing selected_option
    payload = {
        "session_id": "test_api_quiz",
        "question_id": "q1",
    }
    response = client.post("/api/quiz/answer", json=payload)
    assert response.status_code == 422
