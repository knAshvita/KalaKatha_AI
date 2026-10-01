"""
KalaKatha AI – Pydantic Schemas
All request/response models used by the REST API.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator


# ── Shared enums ──────────────────────────────────────────────────────────────

class AnalysisStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


# ─────────────────────────────────────────────────────────────────────────────
#  Artwork Analysis  (POST /api/analyze)
# ─────────────────────────────────────────────────────────────────────────────

class VisualAnalysis(BaseModel):
    """
    Structured output of the Art Analyst ADK Agent.

    Principle: OBSERVATION only — no invented history, no guessed authorship.

    Every field captures what can be DIRECTLY SEEN in the image.
    Fields that cannot be reliably determined must contain 'unknown'.
    The agent must NEVER invent the artist, date, location, or historical narrative.
    """

    # ── Identity (uncertain by default — requires visual evidence) ────────────
    artwork_title: str = Field(
        description=(
            "Title if legible from an inscription or label in the image. "
            "Use 'unknown' if not visible."
        )
    )
    artist: str = Field(
        description=(
            "Artist name ONLY if a legible signature appears in the image. "
            "Do NOT guess from style. Use 'unknown' if absent."
        )
    )
    style: str = Field(
        description=(
            "Art style or movement inferred from visible technique, brushwork, "
            "or rendering method. E.g. 'Impressionism', 'Baroque'. "
            "Use 'unknown' if not visually determinable."
        )
    )
    period: str = Field(
        description=(
            "Approximate historical period inferred from depicted "
            "clothing, technology, or materials visible in the image. "
            "Use 'unknown' if uncertain."
        )
    )

    # ── Narrative overview ────────────────────────────────────────────────────
    summary: str = Field(
        description=(
            "2–3 sentence description of what is visually present. "
            "Observation only — no invented backstory or historical claims."
        )
    )

    # ── Scene inventory ───────────────────────────────────────────────────────
    objects: list[str] = Field(
        description=(
            "Identifiable objects visible in the scene "
            "(e.g. 'wooden chair', 'red apple', 'sailing ship'). "
            "Empty list if none."
        )
    )
    people: list[str] = Field(
        description=(
            "Each visible person described by observable traits: "
            "approximate age, gender presentation, attire, pose. "
            "E.g. ['young woman, facing left, wearing white headscarf']. "
            "Empty list if no people."
        )
    )
    animals: list[str] = Field(
        description=(
            "Each visible animal described by species and observable state. "
            "E.g. ['brown horse, grazing']. Empty list if none."
        )
    )
    environment: str = Field(
        description=(
            "Observable setting: indoor/outdoor, landscape type, weather, "
            "sky conditions, water presence. Use 'unknown' if indeterminate."
        )
    )
    architecture: str = Field(
        description=(
            "Visible architectural elements: building type, structural style, "
            "visible materials. Use 'none visible' if absent."
        )
    )

    # ── Visual properties ─────────────────────────────────────────────────────
    colors: str = Field(
        description=(
            "Color palette description: dominant hues, tonal range, "
            "warm/cool balance, use of contrast or harmony."
        )
    )
    lighting: str = Field(
        description=(
            "Observable lighting: apparent direction, quality (harsh/soft/diffuse), "
            "visible light source if any, shadow behavior, chiaroscuro presence."
        )
    )
    composition: str = Field(
        description=(
            "Compositional structure: describe foreground, middle ground, and "
            "background layers separately. Note symmetry/asymmetry, leading lines, "
            "framing, negative space, depth cues."
        )
    )
    perspective: str = Field(
        description=(
            "Perspective technique: linear/atmospheric/isometric/flat. "
            "Viewpoint height (eye-level/bird's-eye/worm's-eye). "
            "Visible depth cues."
        )
    )
    visual_focus: str = Field(
        description=(
            "Primary focal point of the composition and the visual reason "
            "the eye is drawn there (contrast, placement, detail, gaze direction, etc.)."
        )
    )

    # ── Dynamics & mood ───────────────────────────────────────────────────────
    visible_actions: list[str] = Field(
        description=(
            "Observable actions or dynamic events "
            "(e.g. 'figure reaching toward a candle', 'horse mid-gallop'). "
            "Empty list if scene is fully static."
        )
    )
    mood: str = Field(
        description=(
            "Apparent emotional tone grounded in specific visual evidence. "
            "Cite the cues: e.g. 'melancholic — cool blue palette, downcast gaze, "
            "dim diffuse light'. Do not impose narrative."
        )
    )

    # ── Epistemic safety ──────────────────────────────────────────────────────
    confidence_notes: str = Field(
        description=(
            "Explicit caveats about uncertain observations. "
            "E.g. 'Face partially obscured, expression uncertain. "
            "Style attribution tentative due to low image resolution.' "
            "Use 'none' if all observations are confident."
        )
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Context Agent  –  ContextAnalysis
# ─────────────────────────────────────────────────────────────────────────────

class ContextFact(BaseModel):
    """
    A single contextual claim with an explicit epistemic certainty label.

    Every piece of context produced by the Context Agent must be one of:
      'verified'    — established art-historical or cultural fact
      'interpreted' — reasonable scholarly inference from visual evidence
      'uncertain'   — possible but speculative; requires external verification
    """

    claim: str = Field(
        description="The factual or interpretive statement about the artwork."
    )
    certainty: Literal["verified", "interpreted", "uncertain"] = Field(
        description=(
            "'verified': established art-historical fact; "
            "'interpreted': reasonable scholarly inference; "
            "'uncertain': speculative — would benefit from search/lookup."
        )
    )
    basis: str = Field(
        description=(
            "What grounds this claim. E.g.: "
            "'visible sfumato technique consistent with Leonardesque school', "
            "'art-historical consensus', or "
            "'inferred from depicted attire — uncertain without verification'."
        )
    )


class ArtworkIdentification(BaseModel):
    """
    Structured identification of the artwork by the Context Agent.

    Strictly follows uncertainty protocol:
      - If the artwork can be confidently identified: title, artist, period, style populated.
      - If only some information is known: unsupported fields remain 'unknown'.
      - If uncertain: title, artist, and period are 'unknown' with 'uncertain' confidence.
    """
    title: str = Field(
        default="unknown",
        description="Identified title of the artwork, or 'unknown' if uncertain.",
    )
    artist: str = Field(
        default="unknown",
        description="Identified artist, creator, or school, or 'unknown' if uncertain.",
    )
    period: str = Field(
        default="unknown",
        description="Identified art-historical period or era, or 'unknown' if uncertain.",
    )
    style: str = Field(
        default="unknown",
        description="Identified artistic movement or style, or 'unknown' if uncertain.",
    )
    confidence: Literal["high", "medium", "low", "uncertain"] = Field(
        default="uncertain",
        description="Confidence level in the identification: 'high', 'medium', 'low', or 'uncertain'.",
    )
    basis: str = Field(
        default="",
        description="Visual and contextual reasoning explaining why this identification was made or why uncertain.",
    )


class ContextAnalysis(BaseModel):
    """
    Structured output from the Context ADK Agent.

    Six contextual dimensions, each as a list of ContextFact objects
    with explicit certainty labelling. Never contains fabricated dates,
    locations, artist names, or cultural facts. Includes structured artwork
    identification adhering to the uncertainty protocol.
    """

    identification: ArtworkIdentification = Field(
        default_factory=ArtworkIdentification,
        description=(
            "Structured identification of the artwork based on visual and contextual analysis. "
            "Populated when identifiable, otherwise retains 'unknown' defaults."
        ),
    )
    historical_context: list[ContextFact] = Field(
        description=(
            "Historical facts and inferences: period, events, social climate "
            "relevant to the artwork. Each claim tagged with certainty."
        )
    )
    cultural_context: list[ContextFact] = Field(
        description=(
            "Cultural, geographic, and societal context visible in or "
            "inferable from the artwork."
        )
    )
    artistic_context: list[ContextFact] = Field(
        description=(
            "Artistic movement, school, influences, and place in art history. "
            "Only reference movements/artists that can be grounded visually."
        )
    )
    symbolism: list[ContextFact] = Field(
        description=(
            "Symbolic elements visible in the artwork: objects, colours, "
            "gestures, or compositional choices with potential symbolic meaning."
        )
    )
    artistic_techniques: list[ContextFact] = Field(
        description=(
            "Specific techniques observable in the artwork: brushwork, "
            "chiaroscuro, impasto, sfumato, glazing, etc."
        )
    )
    interesting_facts: list[ContextFact] = Field(
        description=(
            "Engaging facts or observations about the artwork, its subject, "
            "or its historical significance that would interest a general audience."
        )
    )
    summary: str = Field(
        description=(
            "A concise 2–3 sentence synthesis of the most important contextual "
            "findings, noting overall confidence level."
        )
    )
    search_queries_suggested: list[str] = Field(
        description=(
            "Specific search queries the agent would run (or did run) to verify "
            "uncertain claims. Populated even when search is unavailable, "
            "so the queries can be executed later."
        )
    )


class ArtisticContext(BaseModel):
    """Legacy model — use ContextAnalysis for new code."""
    artist_or_school: str = Field(description="Likely artist or school of art")
    cultural_background: str
    historical_period: str
    influences: list[str] = Field(description="Artistic influences detected")
    significance: str = Field(description="Cultural or artistic significance")


class SpatialDescription(BaseModel):
    """
    Structured spatial layout specifically designed to build a coherent mental model
    for visually impaired individuals.
    """
    top: str = Field(
        description="Elements and setting situated in the upper portion of the frame (e.g., sky, ceiling, upper background)."
    )
    bottom: str = Field(
        description="Elements in the lower portion of the frame (e.g., ground, floor, foreground objects, lower attire)."
    )
    left: str = Field(
        description="Elements and figures positioned on the left side of the composition."
    )
    right: str = Field(
        description="Elements and figures positioned on the right side of the composition."
    )
    center: str = Field(
        description="Central focal subjects and elements occupying the central portion of the artwork."
    )
    foreground: str = Field(
        description="Elements closest in depth to the viewer."
    )
    background: str = Field(
        description="Elements in the distance providing environmental depth and setting."
    )
    relationships: str = Field(
        description="Spatial and narrative relationships between important objects and figures (e.g., scale, proximity, interaction)."
    )


class AccessibilityAnalysis(BaseModel):
    """
    Structured output of the Accessibility ADK Agent.
    Strictly designed for visually impaired users without sight-dependent idioms
    ('as you can see', 'look here', etc.) and organized in a clear, sequential flow.
    """
    accessibility_description: str = Field(
        description=(
            "Audio description following a logical sequence: overall orientation, "
            "dominant subjects, shapes, colors, lighting, textures, and mood. "
            "Free of idioms like 'as you can see' or 'you can see that'."
        )
    )
    spatial_description: SpatialDescription = Field(
        description="Detailed spatial mapping across all axes (top, bottom, left, right, center, foreground, background, relationships)."
    )
    short_description: str = Field(
        default="",
        description="A concise 1-2 sentence high-level overview of the artwork."
    )
    alt_text: str = Field(
        default="",
        description="Screen-reader alt text under 125 characters."
    )


class AccessibilityDescription(BaseModel):
    """Legacy alias / fallback model for backward compatibility."""
    short_description: str = Field(description="One-sentence description")
    detailed_description: str = Field(description="Full descriptive passage (3–5 sentences)")
    alt_text: str = Field(description="Screen-reader alt text (<125 chars)")


class GuideMode(str, Enum):
    STORYTELLER = "storyteller"
    PROFESSOR = "professor"
    FRIENDLY = "friendly"
    ACCESSIBILITY = "accessibility"


class StoryChapter(BaseModel):
    chapter_id: str = Field(description="Identifier for the chapter, e.g. 'chapter_1', 'chapter_2'")
    title: str = Field(description="Title for this tour chapter")
    narration: str = Field(description="Museum guide spoken narration for this chapter")
    focus_region: str = Field(description="Region of the artwork focused on (e.g. 'center', 'upper background', 'lower left')")
    visual_elements: list[str] = Field(description="List of visual elements referenced in this chapter")
    estimated_duration_seconds: int = Field(default=30, description="Approximate narration duration in seconds")


class StoryAnalysis(BaseModel):
    """
    Museum-style storytelling experience generated by the Storyteller Agent.
    Transforms visual, contextual, and accessibility analyses into an interactive guided tour.
    """
    story_title: str = Field(description="Title of the storytelling experience")
    opening: str = Field(description="Welcoming opening hook that invites the museum visitor into the experience")
    chapters: list[StoryChapter] = Field(description="4 to 6 tour chapters guiding the visitor through the artwork")
    closing: str = Field(description="Memorable closing thought and parting reflection")

    @property
    def title(self) -> str:
        return self.story_title

    @property
    def narrative(self) -> str:
        parts = [self.story_title, self.opening] + [f"{c.title}: {c.narration}" for c in self.chapters] + [self.closing]
        return "\n\n".join(parts)


ImmersiveStory = StoryAnalysis


class MultipleChoiceQuestion(BaseModel):
    """
    A single multiple-choice question testing observation or understanding.
    """
    question_id: str = Field(description="Unique question identifier, e.g. 'q1', 'q2', 'q3'")
    question: str = Field(description="Multiple-choice question suitable for a student or museum visitor")
    options: list[str] = Field(description="Four distinct answer choices")
    correct_option: str = Field(description="The correct answer choice (matching one of the options)")
    explanation: str = Field(description="Clear explanation of why this answer is correct")


class LearningAnalysis(BaseModel):
    """
    Structured educational content generated by the Learning ADK Agent.
    Designed for students and museum visitors.
    """
    key_concepts: list[str] = Field(
        description="Key art-historical, visual, or cultural concepts featured in the artwork"
    )
    simple_explanations: list[str] = Field(
        default_factory=list,
        description="Clear, accessible explanations of key concepts without overwhelming academic jargon"
    )
    interesting_facts: list[str] = Field(
        description="Engaging, verifiable facts about the artwork, artist, or era"
    )
    things_to_notice: list[str] = Field(
        description="Specific visual details, clues, and compositional elements for the visitor to look for"
    )
    multiple_choice_questions: list[MultipleChoiceQuestion] = Field(
        default_factory=list,
        description="3 multiple-choice questions testing observation and understanding"
    )

    @model_validator(mode="before")
    @classmethod
    def _remap_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "simple_explanations" in data:
                se = data["simple_explanations"]
                if isinstance(se, dict):
                    data["simple_explanations"] = [f"{k}: {v}" for k, v in se.items()]
                elif isinstance(se, str):
                    data["simple_explanations"] = [se]
            if "multiple_choice_questions" not in data:
                for alt in ("questions", "quiz", "mcq", "multiple_choice"):
                    if alt in data:
                        data["multiple_choice_questions"] = data[alt]
                        break
        return data

    @property
    def fun_facts(self) -> list[str]:
        return self.interesting_facts

    @property
    def art_techniques(self) -> list[str]:
        return self.key_concepts


LearningContent = LearningAnalysis


class InteractiveQuestion(BaseModel):
    question: str
    hint: str = ""
    category: str = Field(description="e.g. 'observation', 'interpretation', 'creativity'")


class ArtworkMetadata(BaseModel):
    """Core artwork identity metadata grounded in analysis."""
    filename: str = Field(description="Uploaded filename or image identifier")
    title: str = Field(default="unknown", description="Determined or legible title of the artwork")
    artist: str = Field(default="unknown", description="Verified artist or 'unknown' if uncertain")
    style: str = Field(default="unknown", description="Inferred visual or historical style")
    period: str = Field(default="unknown", description="Historical period or era")


class RegionPosition(BaseModel):
    """
    Normalized bounding box coordinates (0.0 to 1.0) for frontend interactive hotspots.
    Origin (0,0) represents the top-left corner of the artwork.
    Note: Coordinates are approximate region indicators for interactive exploration,
    not pixel-perfect computer-vision segmentations.
    """
    x: float = Field(
        ge=0.0,
        le=1.0,
        description="Normalized horizontal start coordinate (0.0 to 1.0) from top-left",
    )
    y: float = Field(
        ge=0.0,
        le=1.0,
        description="Normalized vertical start coordinate (0.0 to 1.0) from top-left",
    )
    width: float = Field(
        ge=0.0,
        le=1.0,
        description="Normalized width of the bounding region (0.0 to 1.0)",
    )
    height: float = Field(
        ge=0.0,
        le=1.0,
        description="Normalized height of the bounding region (0.0 to 1.0)",
    )


class ArtworkRegion(BaseModel):
    """
    A meaningful, interactive visual region or hotspot within the artwork.
    """
    region_id: str = Field(
        description="Unique region identifier, e.g. 'region_1', 'pearl_earring'",
    )
    label: str = Field(
        description="Concise human-readable label for this hotspot, e.g. 'The Pearl Earring'",
    )
    description: str = Field(
        description="Engaging explanation of what makes this specific region visually or symbolically intriguing",
    )
    importance: str = Field(
        description="Why this region matters, e.g. 'Primary focal point', 'Symbolic highlight'",
    )
    related_visual_elements: list[str] = Field(
        default_factory=list,
        description="Specific visible objects, strokes, or colors contained in this region",
    )
    position: RegionPosition = Field(
        description="Normalized bounding box coordinates (x, y, width, height) between 0.0 and 1.0",
    )


class ExploreContent(BaseModel):
    """
    Interactive exploration capabilities and hotspots for the artwork.
    """
    regions: list[ArtworkRegion] = Field(
        default_factory=list,
        description="Meaningful visual regions and hotspots with normalized bounding boxes",
    )
    interactive_questions: list[InteractiveQuestion] = Field(
        default_factory=list,
        description="Thought-provoking questions to spark conversation and inquiry",
    )
    topics_to_explore: list[str] = Field(
        default_factory=list,
        description="Suggested curiosity topics and historical threads to explore further",
    )
    coordinate_disclaimer: str = Field(
        default=(
            "Normalized hotspot coordinates are approximate bounding estimates "
            "designed for interactive exploration, not pixel-perfect segmentations."
        ),
        description="Note regarding coordinate approximation",
    )


class ArtworkUnderstanding(BaseModel):
    """
    Unified, comprehensive artwork understanding produced by the single ArtAnalystAgent multimodal pass.
    Combines:
      1. Identification (title, artist, period, style, confidence, basis)
      2. Visual observation (summary, objects, people, animals, environment, architecture,
         colors, lighting, composition, perspective, visual_focus, visible_actions, mood, confidence_notes)
      3. Context & Art History (historical_context, cultural_context, artistic_context, symbolism, artistic_techniques)
      4. Accessibility / Spatial mapping (spatial_description, accessibility_description, alt_text)
    """
    identification: ArtworkIdentification = Field(
        default_factory=ArtworkIdentification,
        description="Structured identification of the artwork following the uncertainty protocol",
    )

    # ── Visual observation ───────────────────────────────────────────────────
    summary: str = Field(description="2-3 sentence visual summary of the artwork")
    objects: list[str] = Field(default_factory=list, description="Identifiable visible objects")
    people: list[str] = Field(default_factory=list, description="Descriptions of visible people")
    animals: list[str] = Field(default_factory=list, description="Visible animals")
    environment: str = Field(default="unknown", description="Observable setting/environment")
    architecture: str = Field(default="none visible", description="Observable architectural features")
    colors: str = Field(description="Dominant color palette and tonal balance")
    lighting: str = Field(description="Lighting direction, quality, chiaroscuro")
    composition: str = Field(description="Compositional arrangement across planes")
    perspective: str = Field(description="Perspective system and viewpoint")
    visual_focus: str = Field(description="Primary focal point and visual reason")
    visible_actions: list[str] = Field(default_factory=list, description="Visible actions or events")
    mood: str = Field(description="Observable emotional tone grounded in visual evidence")
    confidence_notes: str = Field(default="none", description="Caveats on uncertain observations")

    # ── Context & Art History ────────────────────────────────────────────────
    historical_context: list[ContextFact] = Field(
        default_factory=list,
        description="Historical era, dates, events, patronage, tagged with certainty",
    )
    cultural_context: list[ContextFact] = Field(
        default_factory=list,
        description="Cultural significance, social/religious customs, tagged with certainty",
    )
    artistic_context: list[ContextFact] = Field(
        default_factory=list,
        description="Art movement, school, artistic innovations, tagged with certainty",
    )
    symbolism: list[ContextFact] = Field(
        default_factory=list,
        description="Iconographic and symbolic motifs grounded in art-historical literature",
    )
    artistic_techniques: list[ContextFact] = Field(
        default_factory=list,
        description="Observable art-historical techniques (sfumato, impasto, chiaroscuro, etc.)",
    )

    # ── Accessibility & Spatial Description ──────────────────────────────────
    spatial_description: SpatialDescription = Field(
        description="Precise 8-zone spatial layout (top, bottom, left, right, center, foreground, background, relationships)",
    )
    accessibility_description: str = Field(
        description="Audio-described sequential narration following audio description standards without visual idioms",
    )
    alt_text: str = Field(
        description="Concise 1-2 sentence screen reader description",
    )

    @property
    def artwork_title(self) -> str:
        return self.identification.title

    @property
    def artist(self) -> str:
        return self.identification.artist

    @property
    def style(self) -> str:
        return self.identification.style

    @property
    def period(self) -> str:
        return self.identification.period

    def to_artwork_metadata(self, filename: str) -> ArtworkMetadata:
        title = self.identification.title.strip() if self.identification.title and self.identification.title.strip().lower() not in ("unknown", "", "none") else "Untitled Artwork"
        artist = self.identification.artist.strip() if self.identification.artist and self.identification.artist.strip().lower() not in ("unknown", "", "none") else "Unknown Artist"
        period = self.identification.period.strip() if self.identification.period and self.identification.period.strip().lower() not in ("unknown", "", "none") else "Unspecified Period"
        style = self.identification.style.strip() if self.identification.style and self.identification.style.strip().lower() not in ("unknown", "", "none") else "Unspecified Style"
        return ArtworkMetadata(
            filename=filename,
            title=title,
            artist=artist,
            style=style,
            period=period,
        )

    def to_visual_analysis(self) -> VisualAnalysis:
        return VisualAnalysis(
            artwork_title=self.identification.title if self.identification.confidence in ("high", "medium") else "unknown",
            artist=self.identification.artist if self.identification.confidence in ("high", "medium") else "unknown",
            style=self.identification.style if self.identification.style != "unknown" else "unknown",
            period=self.identification.period if self.identification.period != "unknown" else "unknown",
            summary=self.summary,
            objects=self.objects,
            people=self.people,
            animals=self.animals,
            environment=self.environment,
            architecture=self.architecture,
            colors=self.colors,
            lighting=self.lighting,
            composition=self.composition,
            perspective=self.perspective,
            visual_focus=self.visual_focus,
            visible_actions=self.visible_actions,
            mood=self.mood,
            confidence_notes=self.confidence_notes,
        )

    def to_context_analysis(self) -> ContextAnalysis:
        return ContextAnalysis(
            identification=self.identification,
            historical_context=self.historical_context,
            cultural_context=self.cultural_context,
            artistic_context=self.artistic_context,
            symbolism=self.symbolism,
            artistic_techniques=self.artistic_techniques,
            interesting_facts=[],
            summary=self.summary,
            search_queries_suggested=[],
        )

    def to_accessibility_analysis(self) -> AccessibilityAnalysis:
        return AccessibilityAnalysis(
            accessibility_description=self.accessibility_description,
            spatial_description=self.spatial_description,
            short_description=self.alt_text,
            alt_text=self.alt_text,
        )

    def to_learning_analysis(self, guide_mode: str = "storyteller") -> LearningAnalysis:
        concepts = [t.claim.split(":")[0].strip() for t in self.artistic_techniques[:3] if t.claim]
        if not concepts:
            concepts = [s.claim.split(":")[0].strip() for s in self.symbolism[:3] if s.claim]
        if not concepts:
            concepts = ["Composition", "Lighting & Contrast", "Visual Form"]

        explanations = [
            f"{t.claim}. Grounded in: {t.basis}." for t in self.artistic_techniques[:3] if t.claim
        ]
        if not explanations:
            explanations = [f"{c}: Demonstrates key principles of the artwork's artistic composition." for c in concepts]

        title = self.identification.title if self.identification.title != "unknown" else "this artwork"

        q1 = MultipleChoiceQuestion(
            question_id="q1",
            question=f"What is the primary visual focus of {title}?",
            options=[self.visual_focus, "Upper background sky only", "Geometric frame only", "Outside border"],
            correct_option=self.visual_focus,
            explanation=f"The composition directs the viewer's eye to {self.visual_focus}.",
        )
        tech_name = self.artistic_techniques[0].claim if self.artistic_techniques else "Chiaroscuro"
        q2 = MultipleChoiceQuestion(
            question_id="q2",
            question="Which artistic technique or principle is prominently featured in this work?",
            options=[tech_name, "Halftone printmaking", "Digital photorealism", "Stained glass mosaic"],
            correct_option=tech_name,
            explanation=f"The work features {tech_name}.",
        )
        period_name = self.identification.period if self.identification.period != "unknown" else "Historical Masterpiece"
        q3 = MultipleChoiceQuestion(
            question_id="q3",
            question=f"Which historical era or artistic context is associated with {title}?",
            options=[period_name, "Cyberpunk Era", "Futurist Movement 1912", "Modernist Architecture 1960"],
            correct_option=period_name,
            explanation=f"This work is grounded in {period_name}.",
        )

        return LearningAnalysis(
            key_concepts=concepts,
            simple_explanations=explanations,
            interesting_facts=[f.claim for f in self.historical_context[:3]],
            things_to_notice=[self.visual_focus] + self.objects[:3],
            multiple_choice_questions=[q1, q2, q3],
        )

    def to_explore_content(self) -> ExploreContent:
        regions = [
            ArtworkRegion(
                region_id="region_focus",
                label=self.visual_focus[:35] if self.visual_focus else "Primary Focal Region",
                description=f"The composition centers attention on {self.visual_focus}.",
                importance="Primary focal point",
                related_visual_elements=self.objects[:3] if self.objects else ["focal subject"],
                position=RegionPosition(x=0.25, y=0.20, width=0.50, height=0.55),
            )
        ]
        if self.objects:
            for idx, obj in enumerate(self.objects[:2], start=2):
                regions.append(
                    ArtworkRegion(
                        region_id=f"region_obj_{idx}",
                        label=obj[:35],
                        description=f"A distinct visual element: {obj}.",
                        importance="Prominent detail",
                        related_visual_elements=[obj],
                        position=RegionPosition(
                            x=min(0.70, 0.15 * idx),
                            y=min(0.65, 0.25 + (0.15 * idx)),
                            width=0.25,
                            height=0.25,
                        ),
                    )
                )

        return ExploreContent(
            regions=regions,
            interactive_questions=[
                InteractiveQuestion(
                    question="What draws your eye first in this composition?",
                    hint="Consider the interplay of lighting and contrast.",
                    category="observation",
                )
            ],
            topics_to_explore=[t.claim for t in self.historical_context[:2]],
            coordinate_disclaimer="Normalized hotspot coordinates are approximate bounding estimates designed for interactive exploration, not pixel-perfect segmentations.",
        )


class KalaKathaExperience(BaseModel):
    """
    Final comprehensive artwork experience synthesized by the KalaKathaRootAgent.
    Validates that outputs from all specialist agents are unified into a cohesive journey.
    """
    session_id: str = Field(description="Unique session identifier for this analysis run")
    artwork: ArtworkMetadata = Field(description="Artwork identity and file metadata")
    visual_analysis: VisualAnalysis = Field(description="Visual observation from Art Analyst Agent")
    context: ContextAnalysis = Field(description="Historical and cultural context from Context Agent")
    story: StoryAnalysis = Field(description="Museum audio tour experience from Storyteller Agent")
    learning: LearningAnalysis = Field(description="Educational content and quiz from Learning Agent")
    accessibility: AccessibilityAnalysis = Field(description="Accessible description and spatial map from Accessibility Agent")
    explore: ExploreContent = Field(description="Interactive exploration prompts and questions")
    guide_mode: Optional[str] = Field(default="storyteller", description="Active tour guide persona")


class ArtworkAnalysisResponse(BaseModel):
    """Aggregated response envelope from the KalaKatha AI multi-agent pipeline."""
    status: AnalysisStatus = AnalysisStatus.SUCCESS
    session_id: Optional[str] = Field(default=None, description="Unique session identifier for this analysis run")
    filename: str
    visual_analysis: VisualAnalysis
    context: ContextAnalysis
    accessibility: AccessibilityAnalysis
    immersive_story: ImmersiveStory
    learning_content: LearningContent
    interactive_questions: list[InteractiveQuestion] = Field(
        default_factory=list,
        description="5 interactive questions about the artwork"
    )
    experience: Optional[KalaKathaExperience] = Field(
        default=None,
        description="Full validated KalaKathaExperience produced by KalaKathaRootAgent"
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Artwork Q&A  (POST /api/ask)
# ─────────────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    """Request payload for artwork-specific Q&A."""
    session_id: str = Field(description="Active session ID from a previous artwork analysis")
    question: str = Field(min_length=2, max_length=1000, description="Natural language question about the current artwork")


class AskResponse(BaseModel):
    """Response payload from the AskAgent."""
    session_id: str = Field(description="Session ID of the analyzed artwork")
    question: str = Field(description="Question asked by the user")
    answer: str = Field(description="Artwork-specific answer grounded in specialist analyses and persona")
    source_context: list[str] = Field(
        default_factory=list,
        description="List of specialist analyses referenced to answer the question (e.g. 'VisualAnalysis', 'ContextAnalysis')",
    )


class QARequest(BaseModel):
    """Legacy request schema — use AskRequest for new code."""
    question: str = Field(min_length=3, max_length=500)
    artwork_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Previously generated analysis to ground the answer",
    )


class QAResponse(BaseModel):
    """Legacy response schema — use AskResponse for new code."""
    status: AnalysisStatus = AnalysisStatus.SUCCESS
    question: str
    answer: str
    confidence: str = Field(default="high", description="'high' | 'medium' | 'low'")


# ─────────────────────────────────────────────────────────────────────────────
#  TTS Narration  (POST /api/narrate)
# ─────────────────────────────────────────────────────────────────────────────

class NarrateRequest(BaseModel):
    text: str = Field(min_length=10, max_length=3000)
    voice: str = Field(default="en-US-Studio-O", description="Gemini TTS voice ID")


class NarrateResponse(BaseModel):
    status: AnalysisStatus = AnalysisStatus.SUCCESS
    audio_base64: str = Field(description="Base64-encoded WAV audio bytes")
    text: str
    voice: str


# ─────────────────────────────────────────────────────────────────────────────
#  Story Audio  (POST /api/story/audio)
# ─────────────────────────────────────────────────────────────────────────────

class StoryAudioRequest(BaseModel):
    """Request payload for chapter-level Gemini TTS narration."""
    session_id: str = Field(
        description="Active session ID from a previous artwork analysis"
    )
    chapter_id: str = Field(
        description=(
            "ID of the StoryChapter to narrate, e.g. 'chapter_1'. "
            "Use 'opening' or 'closing' to narrate those special sections."
        )
    )


class StoryAudioResponse(BaseModel):
    """Response from the story audio narration endpoint."""
    session_id: str = Field(description="Session ID of the artwork")
    chapter_id: str = Field(description="Chapter ID that was narrated")
    chapter_title: str = Field(description="Human-readable title of the chapter")
    narration: str = Field(description="The narration text that was synthesized")
    audio_url: str = Field(
        description="Relative URL to stream the generated WAV audio file, e.g. /audio/<uuid>.wav"
    )
    guide_mode: str = Field(description="Guide persona used for narration")
    voice: str = Field(description="Gemini TTS voice name used")
    duration_hint_seconds: int = Field(
        default=30,
        description="Approximate expected duration from the StorytellerAgent estimate",
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Quiz Answer  (POST /api/quiz/answer)
# ─────────────────────────────────────────────────────────────────────────────

class QuizAnswerRequest(BaseModel):
    """Request payload to answer a multiple choice quiz question."""
    session_id: str = Field(description="Active session ID from a previous artwork analysis")
    question_id: str = Field(description="ID of the question being answered, e.g. 'q1'")
    selected_option: str = Field(default="", description="The option selected by the user (letter e.g. 'A' or option text)")
    answer: str | None = Field(default=None, description="Alternative alias for selected_option")

    @model_validator(mode="before")
    @classmethod
    def resolve_selected_option(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("selected_option") and data.get("answer"):
                data["selected_option"] = data["answer"]
        return data


class QuizAnswerResponse(BaseModel):
    """Response payload for quiz answer verification."""
    session_id: str = Field(description="Session ID of the analyzed artwork")
    question_id: str = Field(description="Question ID answered")
    selected_option: str = Field(description="The option submitted by the user")
    is_correct: bool = Field(description="Whether the selected option was correct")
    correct_option: str = Field(description="The canonical correct option")
    explanation: str = Field(description="Clear explanation of why this answer is correct")


# ─────────────────────────────────────────────────────────────────────────────
#  Health check
# ─────────────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    gemini_api_key_set: bool
