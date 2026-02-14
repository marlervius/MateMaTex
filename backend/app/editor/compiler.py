"""
Incremental LaTeX compiler with process pool and caching.

Provides a compile endpoint that returns base64-encoded PDF or
structured error messages with line numbers.
"""

from __future__ import annotations

import base64
import hashlib
import os
import subprocess
import tempfile
from collections import OrderedDict
from threading import Semaphore
from dataclasses import dataclass, field
from typing import Any

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import get_current_user
from app.latex.preamble import wrap_with_preamble

logger = structlog.get_logger()

router = APIRouter(prefix="/editor", tags=["editor"])

# ---------------------------------------------------------------------------
# Compilation cache & pool
# ---------------------------------------------------------------------------
_MAX_CONCURRENT = 4
_compile_semaphore = Semaphore(_MAX_CONCURRENT)

# LRU cache: hash → (pdf_base64, errors)
_MAX_CACHE_SIZE = 128
_compile_cache: OrderedDict[str, tuple[str, list[dict]]] = OrderedDict()


@dataclass
class CompileError:
    line: int
    message: str
    severity: str = "error"  # error | warning


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class EditorCompileRequest(BaseModel):
    """LaTeX body to compile. Preamble is added automatically if missing."""
    latex_body: str
    filename: str = "preview"

    class Config:
        json_schema_extra = {
            "example": {
                "latex_body": "\\section{Test}\nHello $x^2$",
                "filename": "preview",
            }
        }


class EditorCompileResponse(BaseModel):
    success: bool
    pdf_base64: str = ""
    errors: list[dict] = []
    warnings: list[dict] = []
    cached: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "pdf_base64": "JVBERi0x...",
                "errors": [],
                "warnings": [],
                "cached": False,
            }
        }


# ---------------------------------------------------------------------------
# Core compilation logic
# ---------------------------------------------------------------------------
def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:24]


def _parse_log_errors(log_content: str) -> tuple[list[dict], list[dict]]:
    """Extract errors and warnings from pdflatex log output."""
    errors: list[dict] = []
    warnings: list[dict] = []

    lines = log_content.split("\n")
    for i, line in enumerate(lines):
        # Errors: lines starting with ! or containing error keywords
        if line.startswith("!"):
            # Try to find line number
            line_num = 0
            for j in range(max(0, i - 5), i):
                if lines[j].startswith("l."):
                    try:
                        line_num = int(lines[j].split(".")[1].split()[0])
                    except (IndexError, ValueError):
                        pass
            errors.append({
                "line": line_num,
                "message": line.lstrip("! ").strip(),
                "severity": "error",
            })

        # Warnings
        elif "Warning:" in line and "LaTeX" in line:
            warnings.append({
                "line": 0,
                "message": line.strip(),
                "severity": "warning",
            })

    return errors, warnings


def _compile_latex(full_content: str, filename: str) -> tuple[str, list[dict], list[dict]]:
    """
    Run pdflatex and return (pdf_base64, errors, warnings).
    Uses a semaphore to limit concurrent compilations.
    """
    with _compile_semaphore:
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = os.path.join(tmpdir, f"{filename}.tex")
            pdf_path = os.path.join(tmpdir, f"{filename}.pdf")
            log_path = os.path.join(tmpdir, f"{filename}.log")

            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(full_content)

            try:
                result = subprocess.run(
                    [
                        "pdflatex",
                        "-interaction=nonstopmode",
                        "-halt-on-error",
                        f"-output-directory={tmpdir}",
                        tex_path,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            except subprocess.TimeoutExpired:
                return "", [{"line": 0, "message": "Compilation timed out (30s)", "severity": "error"}], []
            except FileNotFoundError:
                return "", [{"line": 0, "message": "pdflatex not found on system", "severity": "error"}], []

            # Parse log for errors/warnings
            log_content = ""
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                    log_content = f.read()

            errors, warnings = _parse_log_errors(log_content)

            # Read PDF if successful
            pdf_base64 = ""
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_base64 = base64.b64encode(f.read()).decode()

            return pdf_base64, errors, warnings


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.post(
    "/compile",
    response_model=EditorCompileResponse,
    summary="Compile LaTeX body to PDF (with caching and process pool)",
)
async def compile_editor_latex(req: EditorCompileRequest, user_id: str = Depends(get_current_user)) -> EditorCompileResponse:
    """
    Compile LaTeX content to PDF.

    - Automatically wraps with standard preamble if \\documentclass is missing
    - Uses a pool of max 4 concurrent pdflatex processes
    - Caches compiled PDFs by content hash
    - Returns structured errors with line numbers on failure
    """
    content = req.latex_body
    if r"\documentclass" not in content:
        content = wrap_with_preamble(content)

    content_hash = _content_hash(content)

    # Check cache
    if content_hash in _compile_cache:
        _compile_cache.move_to_end(content_hash)
        cached_pdf, cached_errors = _compile_cache[content_hash]
        return EditorCompileResponse(
            success=bool(cached_pdf),
            pdf_base64=cached_pdf,
            errors=cached_errors,
            cached=True,
        )

    # Compile
    pdf_base64, errors, warnings = _compile_latex(content, req.filename)

    # Cache result
    _compile_cache[content_hash] = (pdf_base64, errors)
    if len(_compile_cache) > _MAX_CACHE_SIZE:
        _compile_cache.popitem(last=False)

    return EditorCompileResponse(
        success=bool(pdf_base64),
        pdf_base64=pdf_base64,
        errors=errors,
        warnings=warnings,
        cached=False,
    )
