"""LK20 curriculum data — ported from the v1 src/curriculum.py."""

from .lk20 import (
    LANGUAGE_LEVELS,
    format_boundaries_for_prompt,
    get_competency_goals,
    get_grade_boundaries,
    get_language_level_instructions,
    get_topics_for_grade,
)
from .topic_coverage import (
    format_coverage_for_prompt,
    get_topic_coverage_spec,
)

__all__ = [
    "get_grade_boundaries",
    "format_boundaries_for_prompt",
    "get_topics_for_grade",
    "get_competency_goals",
    "get_language_level_instructions",
    "format_coverage_for_prompt",
    "get_topic_coverage_spec",
    "LANGUAGE_LEVELS",
]
