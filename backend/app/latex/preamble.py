"""
Standard LaTeX preamble for MateMaTeX documents.

Ported from v1 src/tools/pdf_generator.py with improvements from the forbedringsplan.
"""

from __future__ import annotations

# The standard preamble is imported from the v1 codebase to maintain consistency.
# We re-export it here so the v2 pipeline uses the same preamble.
import sys
from pathlib import Path

_V1_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_V1_ROOT))

from src.tools.pdf_generator import STANDARD_PREAMBLE  # noqa: E402


def wrap_with_preamble(body_content: str) -> str:
    """
    Wrap body content with the standard preamble.

    Args:
        body_content: LaTeX body content (no \\documentclass).

    Returns:
        Complete LaTeX document ready for compilation.
    """
    body = body_content.strip()

    return (
        STANDARD_PREAMBLE
        + r"\begin{document}"
        + "\n"
        + r"\thispagestyle{plain}"
        + "\n\n"
        + body
        + "\n\n"
        + r"\end{document}"
    )
