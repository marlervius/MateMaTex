"""
LaTeX compilation checker — uses actual pdflatex to validate documents.

This is NOT pattern matching. We compile the document and check for real errors.
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

import structlog

from app.models.state import LatexCompilationResult

logger = structlog.get_logger()


class LatexChecker:
    """
    Validates LaTeX by actually compiling it with pdflatex.
    """

    def __init__(self, pdflatex_path: str = "pdflatex"):
        self._pdflatex = pdflatex_path

    def check(self, full_latex_document: str) -> LatexCompilationResult:
        """
        Compile the full LaTeX document and return the result.

        Args:
            full_latex_document: Complete LaTeX document with preamble.

        Returns:
            LatexCompilationResult with success status and any errors.
        """
        result = LatexCompilationResult()

        with tempfile.TemporaryDirectory(prefix="matematex_check_") as tmpdir:
            tex_path = Path(tmpdir) / "check.tex"
            pdf_path = Path(tmpdir) / "check.pdf"
            log_path = Path(tmpdir) / "check.log"

            # Write the .tex file
            tex_path.write_text(full_latex_document, encoding="utf-8")

            try:
                proc = subprocess.run(
                    [
                        self._pdflatex,
                        "-interaction=nonstopmode",
                        "-halt-on-error",
                        "-output-directory", str(tmpdir),
                        str(tex_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=tmpdir,
                )

                # Read the log
                if log_path.exists():
                    log_text = log_path.read_text(encoding="utf-8", errors="replace")
                    result.errors = self._extract_errors(log_text)
                    result.warnings = self._extract_warnings(log_text)
                    # Keep last 50 lines of log for debugging
                    log_lines = log_text.strip().split("\n")
                    result.log_excerpt = "\n".join(log_lines[-50:])

                if pdf_path.exists() and proc.returncode == 0:
                    result.success = True
                    result.pdf_path = str(pdf_path)
                    logger.info("latex_compilation_success")
                else:
                    result.success = False
                    if not result.errors:
                        result.errors = [
                            f"pdflatex exited with code {proc.returncode}"
                        ]
                    logger.warning(
                        "latex_compilation_failed",
                        errors=result.errors[:3],
                        return_code=proc.returncode,
                    )

            except FileNotFoundError:
                result.success = False
                result.errors = [
                    f"pdflatex not found at '{self._pdflatex}'. "
                    "Install texlive or set MATEMATEX_PDFLATEX_PATH."
                ]
                logger.error("pdflatex_not_found", path=self._pdflatex)

            except subprocess.TimeoutExpired:
                result.success = False
                result.errors = ["pdflatex compilation timed out (>30s)"]
                logger.error("pdflatex_timeout")

        return result

    @staticmethod
    def _extract_errors(log_text: str) -> list[str]:
        """Extract error messages from pdflatex log."""
        errors: list[str] = []
        patterns = [
            re.compile(r'^!\s*(.+)$', re.MULTILINE),
            re.compile(r'^l\.(\d+)\s*(.+)$', re.MULTILINE),
        ]

        for pattern in patterns:
            for match in pattern.finditer(log_text):
                err_msg = match.group(0).strip()
                if err_msg and err_msg not in errors:
                    errors.append(err_msg)

        return errors[:20]  # Cap at 20 errors

    @staticmethod
    def _extract_warnings(log_text: str) -> list[str]:
        """Extract warning messages from pdflatex log."""
        warnings: list[str] = []

        # LaTeX warnings
        for match in re.finditer(r'LaTeX Warning:\s*(.+?)(?:\n|$)', log_text):
            warnings.append(match.group(1).strip())

        # Overfull/underfull boxes
        for match in re.finditer(r'((?:Over|Under)full \\[hv]box.+?)(?:\n|$)', log_text):
            warnings.append(match.group(1).strip())

        return warnings[:20]


def format_latex_errors_for_agent(result: LatexCompilationResult) -> str:
    """Format compilation errors into instructions for the LaTeX fixer agent."""
    if result.success:
        return ""

    lines = [
        "=== LaTeX KOMPILERINGSFEIL ===",
        f"pdflatex feilet med {len(result.errors)} feil.\n",
    ]

    for i, err in enumerate(result.errors[:10], 1):
        lines.append(f"FEIL {i}: {err}")

    lines.append(f"\nSiste del av loggen:\n{result.log_excerpt[-500:]}")
    lines.append("\nRETT ALLE FEILENE og returner hele det korrigerte LaTeX-dokumentet.")

    return "\n".join(lines)
