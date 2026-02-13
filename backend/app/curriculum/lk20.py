"""
LK20 curriculum data and grade boundary logic.

This module re-exports key functions from the v1 curriculum.py so that
the new pipeline can use them. In a future migration, this will be
replaced by a database-backed curriculum service.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add v1 src to path so we can import the existing curriculum module
_V1_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # backend/../
sys.path.insert(0, str(_V1_ROOT))

from src.curriculum import (  # noqa: E402
    format_boundaries_for_prompt,
    get_grade_boundaries,
    get_topics_for_grade,
    get_competency_goals,
)

# Language level definitions (v2 — enhanced from v1)
LANGUAGE_LEVELS = {
    "standard": {
        "name": "Standard norsk",
        "code": "C1-C2",
        "description": "Vanlig akademisk norsk",
        "instructions": "",
    },
    "b2": {
        "name": "Forenklet norsk (B2)",
        "code": "B2",
        "description": "For elever med norsk som andrespråk — øvre mellomnivå",
        "instructions": (
            "SPRÅKNIVÅ B2: Korte setninger (15-20 ord maks), én idé per setning. "
            "Vanlige, konkrete ord — unngå idiomer. "
            "Forklar fagbegreper første gang de brukes. "
            "Bruk samme ord for samme begrep konsekvent. "
            "Matematisk nivå er UENDRET."
        ),
    },
    "b1": {
        "name": "Enklere norsk (B1)",
        "code": "B1",
        "description": "For elever med norsk som andrespråk — nedre mellomnivå",
        "instructions": (
            "SPRÅKNIVÅ B1: Veldig korte setninger (10-15 ord maks). "
            "De 3000 vanligste norske ordene. "
            "Forklar ALLE fagbegreper som om eleven hører det første gang. "
            "Del komplekse oppgaver i steg: 'Steg 1:', 'Steg 2:'. "
            "Legg til 'Tips:' der det hjelper. "
            "Matematisk nivå er UENDRET."
        ),
    },
}


def get_language_level_instructions(level: str) -> str:
    """Get language simplification instructions for the given level."""
    return LANGUAGE_LEVELS.get(level, {}).get("instructions", "")
