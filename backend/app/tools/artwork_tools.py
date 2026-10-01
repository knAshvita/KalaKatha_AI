"""
tools/artwork_tools.py
──────────────────────
Reusable ADK tool functions that can be injected into any agent via
`LocalAgentConfig(tools=[...])`.

These are standalone Python callables following the ADK tool contract
(descriptive docstring + typed args). They complement the agent modules
in app/agents/ by providing helper capabilities that agents can invoke.
"""
from __future__ import annotations


def get_art_style_info(style_name: str) -> str:
    """Return a brief factual description of an art style or movement.

    Args:
        style_name: The name of the art style or movement, e.g. 'Impressionism'.
    """
    # Hardcoded for hackathon speed; extend with an API call if needed.
    styles: dict[str, str] = {
        "impressionism": (
            "Impressionism (1860s–1880s) is a 19th-century French movement "
            "characterised by loose brushwork and an emphasis on capturing light "
            "and atmosphere rather than precise detail. Key artists: Monet, Renoir, Degas."
        ),
        "baroque": (
            "Baroque (1600–1750) is a highly ornate style with dramatic light/dark "
            "contrasts (chiaroscuro), intense emotion, and grandeur. Key artists: "
            "Caravaggio, Rembrandt, Rubens."
        ),
        "renaissance": (
            "Renaissance (14th–17th century) revived classical Greco-Roman ideals "
            "with humanist themes, mathematical perspective, and idealised forms. "
            "Key artists: Leonardo da Vinci, Michelangelo, Raphael."
        ),
        "surrealism": (
            "Surrealism (1920s–1940s) explores the unconscious mind through dreamlike, "
            "irrational imagery. Key artists: Salvador Dalí, René Magritte, Frida Kahlo."
        ),
        "abstract expressionism": (
            "Abstract Expressionism (1940s–1950s) is a post-WWII American movement "
            "emphasising spontaneous, gestural, non-representational painting. "
            "Key artists: Pollock, de Kooning, Rothko."
        ),
    }

    key = style_name.lower().strip()
    return styles.get(
        key,
        f"No built-in description found for '{style_name}'. "
        "The style may be lesser-known or a regional variation.",
    )


def estimate_artwork_era(visual_clues: str) -> str:
    """Estimate the approximate historical era of an artwork from visual clues.

    Args:
        visual_clues: A comma-separated list of visual observations such as
            'oil paint, dark background, religious subject, dramatic lighting'.
    """
    clues = [c.lower().strip() for c in visual_clues.split(",")]

    if any(word in clues for word in ["digital", "pixel", "vector", "neon"]):
        return "Contemporary / Digital (20th–21st century)"
    if any(word in clues for word in ["impressionist", "plein air", "loose brushwork"]):
        return "Late 19th century (ca. 1860–1900)"
    if any(word in clues for word in ["chiaroscuro", "religious", "dramatic lighting", "dark background"]):
        return "Baroque period (ca. 1600–1750)"
    if any(word in clues for word in ["perspective", "humanist", "classical", "sfumato"]):
        return "Renaissance (ca. 1400–1600)"
    if any(word in clues for word in ["gold leaf", "flat", "religious icon", "byzantine"]):
        return "Medieval / Byzantine (ca. 500–1400)"

    return "Era uncertain — requires expert appraisal."
