"""
Tests – Schemas
Validates that Pydantic schema models and validations work correctly.
"""
import pytest

from app.schemas.artwork import (
    AccessibilityDescription,
    AnalysisStatus,
    ContextAnalysis,
    ContextFact,
    ImmersiveStory,
    InteractiveQuestion,
    LearningContent,
    QARequest,
    QAResponse,
    VisualAnalysis,
)


def test_visual_analysis_schema():
    va = VisualAnalysis(
        artwork_title="unknown",
        artist="unknown",
        style="Impressionism",
        period="Late 19th century",
        summary="A peaceful water pond with lilies floating on reflective water.",
        objects=["water lilies", "floating pads"],
        people=[],
        animals=[],
        environment="outdoor pond garden",
        architecture="none visible",
        colors="Cool blues, greens with soft white and violet highlights",
        lighting="Diffuse natural daylight",
        composition="Foreground filled with lily pads, water fills the frame",
        perspective="High-angle downward view onto the water surface",
        visual_focus="Cluster of white lilies in the lower left",
        visible_actions=[],
        mood="Serene, contemplative",
        confidence_notes="none",
    )
    assert va.style == "Impressionism"
    assert len(va.objects) == 2
    assert va.environment == "outdoor pond garden"


def test_context_analysis_schema():
    ca = ContextAnalysis(
        historical_context=[
            ContextFact(
                claim="Created during late 19th-century European industrial expansion.",
                certainty="interpreted",
                basis="Matches late 19th-century French Impressionist movement context.",
            )
        ],
        cultural_context=[
            ContextFact(
                claim="Reflects the French passion for cultivated nature and plein-air painting.",
                certainty="interpreted",
                basis="Depiction of ornamental water gardens typical of Giverny.",
            )
        ],
        artistic_context=[
            ContextFact(
                claim="Exemplifies Impressionist focus on light reflection on water.",
                certainty="verified",
                basis="Documented hallmark of Impressionist movement.",
            )
        ],
        symbolism=[
            ContextFact(
                claim="Water lilies often symbolize tranquility and spiritual purity.",
                certainty="interpreted",
                basis="Common iconography in Western art and Asian influences.",
            )
        ],
        artistic_techniques=[
            ContextFact(
                claim="Visible impasto and broken brushstrokes capture shifting light.",
                certainty="verified",
                basis="Observable short, layered strokes visible in the paint surface.",
            )
        ],
        interesting_facts=[
            ContextFact(
                claim="Monet planted exotic water lily cultivars specifically to paint them.",
                certainty="uncertain",
                basis="Requires verification of whether this specific scene is Monet's Giverny.",
            )
        ],
        summary="A hallmark example of Impressionist nature study emphasizing light and reflection.",
        search_queries_suggested=["French impressionism water lily series historical background"],
    )
    assert len(ca.historical_context) == 1
    assert ca.artistic_techniques[0].certainty == "verified"
    assert ca.interesting_facts[0].certainty == "uncertain"
    assert len(ca.search_queries_suggested) == 1


def test_qa_request_min_length():
    with pytest.raises(Exception):
        QARequest(question="hi")  # too short (min_length=3)


def test_qa_request_valid():
    req = QARequest(question="What is the medium of this artwork?")
    assert req.question.startswith("What")
    assert req.artwork_context == {}


def test_interactive_question_schema():
    q = InteractiveQuestion(
        question="What emotions does this artwork evoke?",
        hint="Look at the color palette.",
        category="interpretation",
    )
    assert q.category == "interpretation"


def test_analysis_status_enum():
    assert AnalysisStatus.SUCCESS == "success"
    assert AnalysisStatus.ERROR == "error"
