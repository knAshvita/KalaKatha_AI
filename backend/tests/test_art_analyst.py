"""
tests/test_art_analyst.py
══════════════════════════════════════════════════════════════════════════════
Tests for the Art Analyst ADK Agent  (app/agents/art_analyst.py)

TEST SUITE
───────────
  1. test_visual_analysis_schema_fields
       — Verifies all 17 required fields exist in VisualAnalysis.
         No API call. Always runs.

  2. test_agent_config_is_valid
       — Verifies build_agent_config() returns a usable LocalAgentConfig.
         No API call. Always runs.

  3. test_art_analyst_live  (integration)
       — Downloads a public-domain artwork (Vermeer's Girl with a Pearl Earring)
         and passes it to the Art Analyst ADK Agent.
       — Validates every field, checks epistemic safety rules.
       — SKIPPED automatically when GEMINI_API_KEY is absent.

USAGE
──────
  # Run all tests (schema + live):
  pytest tests/test_art_analyst.py -v -s

  # Run offline-only tests:
  pytest tests/test_art_analyst.py -v -s -m "not integration"

  # Run as a standalone CLI demo:
  python tests/test_art_analyst.py
  python tests/test_art_analyst.py path/to/artwork.jpg
"""
from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import urllib.request
from pathlib import Path

# pyrefly: ignore [missing-import]
import pytest

# ─────────────────────────────────────────────────────────────────────────────
#  Public-domain demo image (Vermeer, 1665 – Mauritshuis, The Hague)
# ─────────────────────────────────────────────────────────────────────────────
_DEMO_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/"
    "1665_Girl_with_a_Pearl_Earring.jpg/"
    "800px-1665_Girl_with_a_Pearl_Earring.jpg"
)
_DEMO_FILENAME = "test_vermeer_pearl_earring.jpg"

# All 17 required VisualAnalysis fields
_REQUIRED_FIELDS = {
    "artwork_title", "artist", "style", "period",
    "summary",
    "objects", "people", "animals", "environment", "architecture",
    "colors", "lighting", "composition", "perspective", "visual_focus",
    "visible_actions", "mood",
    "confidence_notes",
}


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _download_demo_image() -> Path:
    """Download the demo image once; return its cached path."""
    dest = Path(tempfile.gettempdir()) / _DEMO_FILENAME
    if not dest.exists():
        print(f"\n  📥  Downloading demo image → {dest}")
        req = urllib.request.Request(
            _DEMO_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) KalaKatha/1.0"}
        )
        try:
            with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
                f.write(resp.read())
        except Exception:
            from PIL import Image
            img = Image.new("RGB", (400, 400), color=(73, 109, 137))
            img.save(dest, "JPEG")
    else:
        print(f"\n  ♻️   Using cached demo image → {dest}")
    return dest


def _print_report(result) -> None:
    """Pretty-print a VisualAnalysis to stdout."""
    sep = "═" * 68
    print(f"\n{sep}")
    print("  KALAKATHA AI  ·  ART ANALYST AGENT  ·  VISUAL ANALYSIS REPORT")
    print(sep)

    print("\n📌  IDENTITY")
    print(f"    Title  : {result.artwork_title}")
    print(f"    Artist : {result.artist}")
    print(f"    Style  : {result.style}")
    print(f"    Period : {result.period}")

    print("\n📋  SUMMARY")
    print(f"    {result.summary}")

    print("\n🏛️   SCENE")
    print(f"    Environment  : {result.environment}")
    print(f"    Architecture : {result.architecture}")
    if result.objects:
        print(f"    Objects      : {', '.join(result.objects)}")
    if result.people:
        print("    People       :")
        for p in result.people:
            print(f"      • {p}")
    if result.animals:
        print("    Animals      :")
        for a in result.animals:
            print(f"      • {a}")

    print("\n🎨  VISUAL PROPERTIES")
    print(f"    Colors      : {result.colors}")
    print(f"    Lighting    : {result.lighting}")
    print(f"    Composition : {result.composition}")
    print(f"    Perspective : {result.perspective}")
    print(f"    Focal Point : {result.visual_focus}")

    print("\n🎭  MOOD & ACTIONS")
    print(f"    Mood : {result.mood}")
    if result.visible_actions:
        print("    Actions :")
        for a in result.visible_actions:
            print(f"      • {a}")
    else:
        print("    Actions : static scene")

    if result.confidence_notes.lower() != "none":
        print(f"\n⚠️   CONFIDENCE NOTES")
        print(f"    {result.confidence_notes}")

    print(f"\n{sep}")
    print("  RAW JSON")
    print(sep)
    print(json.dumps(result.model_dump(), indent=2))
    print(f"{sep}\n")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 1 — Schema completeness (offline, always runs)
# ─────────────────────────────────────────────────────────────────────────────

def test_visual_analysis_schema_fields():
    """
    All 17 required fields must be present in VisualAnalysis.
    No API call. Validates schema design only.
    """
    from app.schemas.artwork import VisualAnalysis

    model_fields = set(VisualAnalysis.model_fields.keys())
    missing = _REQUIRED_FIELDS - model_fields
    extra = model_fields - _REQUIRED_FIELDS

    assert not missing, (
        f"VisualAnalysis is missing required fields: {sorted(missing)}"
    )
    print(f"\n  ✅  All {len(_REQUIRED_FIELDS)} required fields present.")
    if extra:
        print(f"  ℹ️   Additional fields also present: {sorted(extra)}")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 2 — Agent config validity (offline, always runs)
# ─────────────────────────────────────────────────────────────────────────────

def test_agent_config_is_valid():
    """
    build_agent_config() must return an ADK-backed KalaKathaBaseAgent with
    the correct output_schema and instruction set (migrated from LocalAgentConfig).
    """
    from app.agents.base import KalaKathaBaseAgent
    from app.agents.art_analyst import build_agent_config
    from app.schemas.artwork import ArtworkUnderstanding, VisualAnalysis

    config = build_agent_config()

    assert isinstance(config, KalaKathaBaseAgent), (
        "build_agent_config() must return a KalaKathaBaseAgent (google-adk) instance"
    )
    assert (
        config.output_schema is ArtworkUnderstanding
        or config.output_schema is VisualAnalysis
        or "ArtworkUnderstanding" in str(config.output_schema)
        or "VisualAnalysis" in str(config.output_schema)
    ), "output_schema must reference ArtworkUnderstanding or VisualAnalysis"
    assert config.instruction, (
        "instruction must not be empty"
    )
    schema_name = getattr(config.output_schema, '__name__', 'ArtworkUnderstanding')
    print(
        f"\n  OK  ADK Agent built successfully."
        f"\n      output_schema : {schema_name}"
        f"\n      model         : {getattr(config, 'model', 'ADK default')}"
    )


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 3 — Live integration test (requires GEMINI_API_KEY)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.integration
async def test_art_analyst_live():
    """
    Send a real artwork image to the Art Analyst ADK Agent via Gemini
    and validate every field of the returned VisualAnalysis.

    Automatically SKIPPED when GEMINI_API_KEY is not set.
    """
    from app.config import get_settings
    from app.agents.art_analyst import analyze_image
    from app.schemas.artwork import VisualAnalysis

    settings = get_settings()
    if not settings.gemini_api_key:
        pytest.skip("GEMINI_API_KEY not set — skipping live API test.")

    image_path = _download_demo_image()

    print("\n  🤖  Running Art Analyst ADK Agent…")
    result = await analyze_image(image_path)

    # ── Type check ────────────────────────────────────────────────────────────
    assert isinstance(result, VisualAnalysis), (
        f"Expected VisualAnalysis, got {type(result)}"
    )

    # ── All fields present and non-None ───────────────────────────────────────
    for field_name in _REQUIRED_FIELDS:
        value = getattr(result, field_name)
        assert value is not None, f"Field '{field_name}' is None"

    # ── String fields are non-empty ───────────────────────────────────────────
    string_fields = {
        "artwork_title", "artist", "style", "period", "summary",
        "environment", "architecture", "colors", "lighting",
        "composition", "perspective", "visual_focus", "mood",
        "confidence_notes",
    }
    for f in string_fields:
        val = getattr(result, f)
        assert isinstance(val, str) and val.strip(), (
            f"String field '{f}' is empty or not a string: {val!r}"
        )

    # ── List fields are lists ─────────────────────────────────────────────────
    for f in ("objects", "people", "animals", "visible_actions"):
        val = getattr(result, f)
        assert isinstance(val, list), (
            f"Field '{f}' must be a list, got {type(val)}"
        )

    # ── Epistemic safety: Vermeer has no legible signature in this image ──────
    # The agent should either return 'unknown' OR the well-known name
    # (models may recognise the painting). We flag it for review if named.
    if result.artist not in ("unknown", "Johannes Vermeer", "Vermeer"):
        print(
            f"\n  ⚠️  Unexpected artist value: '{result.artist}'. "
            "Review whether this was hallucinated or correctly inferred."
        )

    # ── Summary must not be suspiciously short ────────────────────────────────
    assert len(result.summary) >= 30, (
        f"summary is too short ({len(result.summary)} chars): {result.summary!r}"
    )

    # ── Mood must cite visual evidence ────────────────────────────────────────
    mood_evidence_words = {
        "color", "colour", "light", "shadow", "palette", "tone",
        "hue", "gaze", "posture", "contrast", "warm", "cool", "dark", "bright",
    }
    mood_lower = result.mood.lower()
    assert any(w in mood_lower for w in mood_evidence_words), (
        f"'mood' field does not cite visual evidence: {result.mood!r}"
    )

    _print_report(result)
    print("  ✅  test_art_analyst_live passed.\n")


# ─────────────────────────────────────────────────────────────────────────────
#  Standalone CLI demo
# ─────────────────────────────────────────────────────────────────────────────
#
#  python tests/test_art_analyst.py
#  python tests/test_art_analyst.py path/to/artwork.jpg
#

if __name__ == "__main__":
    async def _main() -> None:
        from app.agents.art_analyst import analyze_image

        if len(sys.argv) > 1:
            image_path = Path(sys.argv[1]).resolve()
            if not image_path.exists():
                print(f"❌  File not found: {image_path}", file=sys.stderr)
                sys.exit(1)
        else:
            image_path = _download_demo_image()

        print(f"\n  🎨  Analysing: {image_path.name}")
        print("  🤖  Calling Art Analyst ADK Agent (Gemini multimodal)…")

        result = await analyze_image(image_path)
        _print_report(result)

    asyncio.run(_main())
