"""M1 — empirisk verifikasjonsdekning (MateMaTeX grunnlov §1, milepæl M1)."""

from m1.scorer import (
    MISMATCH,
    UNCERTAIN,
    VERIFIED,
    aggregate,
    answer_check,
    autoscore,
    report,
)

__all__ = [
    "VERIFIED",
    "MISMATCH",
    "UNCERTAIN",
    "answer_check",
    "autoscore",
    "aggregate",
    "report",
]
