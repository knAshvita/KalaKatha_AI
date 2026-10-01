"""
tests/test_session_api.py  –  Tests for GET /api/session/{session_id}
═══════════════════════════════════════════════════════════════════
Validates:
  1. Successful retrieval of KalaKathaExperience by session_id
  2. Complete payload validation across all 8 experience components
  3. 404 response on unknown session_id
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
    RegionPosition,
    SpatialDescription,
    StoryAnalysis,
    StoryChapter,
    VisualAnalysis,
)
from app.services.session_store import session_store

client = TestClient(app)


def _seed_sample_session(session_id: str = "test_session_fetch") -> KalaKathaExperience:
    exp = KalaKathaExperience(
        session_id=session_id,
        artwork=ArtworkMetadata(
            filename="sunflowers.jpg",
            title="Sunflowers",
            artist="Vincent van Gogh",
            style="Post-Impressionism",
            period="1888",
        ),
        visual_analysis=VisualAnalysis(
            artwork_title="Sunflowers",
            artist="Vincent van Gogh",
            style="Post-Impressionism",
            period="1888",
            summary="A vase of bright yellow sunflowers against a pale background.",
            objects=["sunflowers", "vase", "table"],
            people=[],
            animals=[],
            environment="indoor still life",
            architecture="none",
            colors="Luminous chrome yellow, ochre, soft green",
            lighting="Bright warm daylight",
            composition="Vertical arrangement centered on the vase",
            perspective="Slightly elevated view",
            visual_focus="The open sunflower blossoms",
            visible_actions=[],
            mood="Vibrant and joyful",
            confidence_notes="none",
        ),
        context=ContextAnalysis(
            historical_context=[],
            cultural_context=[],
            artistic_context=[],
            symbolism=[],
            artistic_techniques=[],
            interesting_facts=[],
            summary="Painted in Arles, France.",
            search_queries_suggested=[],
        ),
        story=StoryAnalysis(
            story_title="A Symphony of Yellow",
            opening="Step into the sun-drenched studio of Arles.",
            chapters=[
                StoryChapter(
                    chapter_id="chapter_1",
                    title="The Yellow House",
                    narration="Van Gogh sought to decorate his yellow house with warmth.",
                    focus_region="vase",
                    visual_elements=["yellow flowers"],
                    estimated_duration_seconds=25,
                )
            ],
            closing="A testament to enduring friendship and creative passion.",
        ),
        learning=LearningAnalysis(
            key_concepts=["Impasto", "Color Theory"],
            simple_explanations={"Impasto": "Thick paint applied with visible stroke texture."},
            interesting_facts=["Van Gogh painted multiple sunflower versions."],
            things_to_notice=["Notice the heavy paint ridges on each petal."],
            multiple_choice_questions=[
                MultipleChoiceQuestion(
                    question_id="q1",
                    question="Which city was this series painted in?",
                    options=["Paris", "Arles", "Amsterdam", "London"],
                    correct_option="Arles",
                    explanation="Van Gogh created the sunflower series in Arles in the south of France.",
                )
            ],
        ),
        accessibility=AccessibilityAnalysis(
            accessibility_description="Still life featuring a bouquet of fourteen sunflowers in a two-tone ceramic vase.",
            spatial_description=SpatialDescription(
                top="Open sunflower heads reaching upward",
                bottom="Flat circular base of the vase",
                left="Drooping sunflower heads",
                right="Upright blossoming sunflowers",
                center="Round ceramic vase",
                foreground="Vase resting on wooden surface",
                background="Pale turquoise wall",
                relationships="Blossoms radiate from the center vase outward",
            ),
            short_description="Fourteen sunflowers in a yellow vase.",
            alt_text="Post-Impressionist still life of sunflowers in a vase by Vincent van Gogh.",
        ),
        explore=ExploreContent(
            regions=[
                ArtworkRegion(
                    region_id="reg_vase",
                    label="Ceramic Vase",
                    description="Two-toned yellow and terracotta vase",
                    importance="Structural anchor of the still life",
                    related_visual_elements=["vase", "table"],
                    position=RegionPosition(x=0.35, y=0.55, width=0.30, height=0.35),
                )
            ],
            interactive_questions=[],
            topics_to_explore=["Use of chrome yellow pigments in the 19th century"],
            coordinate_disclaimer="Approximate interactive regions.",
        ),
        guide_mode="friendly",
    )
    session_store.save(session_id, exp, guide_mode="friendly")
    return exp


def test_get_session_success():
    session_id = "test_get_session_ok"
    _seed_sample_session(session_id)

    response = client.get(f"/api/session/{session_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["session_id"] == session_id
    assert data["artwork"]["title"] == "Sunflowers"
    assert data["artwork"]["artist"] == "Vincent van Gogh"
    assert data["visual_analysis"]["style"] == "Post-Impressionism"
    assert len(data["story"]["chapters"]) == 1
    assert data["story"]["chapters"][0]["chapter_id"] == "chapter_1"
    assert len(data["learning"]["multiple_choice_questions"]) == 1
    assert data["accessibility"]["alt_text"].startswith("Post-Impressionist")
    assert len(data["explore"]["regions"]) == 1
    assert data["explore"]["regions"][0]["region_id"] == "reg_vase"
    assert data["guide_mode"] == "friendly"


def test_get_session_not_found():
    response = client.get("/api/session/nonexistent_session_id_12345")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
