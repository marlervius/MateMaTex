"""
Export API — PDF (enhanced), Word (DOCX), PowerPoint (PPTX).

All endpoints accept LaTeX content and return downloadable documents.
"""

from __future__ import annotations

import base64
import io
import os
import subprocess
import tempfile

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import get_current_user

from app.latex.compiler import compile_to_pdf
from app.latex.preamble import wrap_with_preamble

logger = structlog.get_logger()

router = APIRouter(prefix="/export", tags=["export"])


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class PdfExportRequest(BaseModel):
    latex_content: str = Field(..., min_length=10)
    include_solutions: bool = True
    include_cover: bool = False
    cover_school: str = ""
    cover_teacher: str = ""
    cover_subject: str = "Matematikk"
    cover_topic: str = ""
    print_optimized: bool = False
    include_qr: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "latex_content": "\\section{Test}...",
                "include_cover": True,
                "cover_school": "Oslo Skole",
                "cover_teacher": "Kari Nordmann",
            }
        }


class DocxExportRequest(BaseModel):
    latex_content: str = Field(..., min_length=10)
    title: str = "Oppgaveark"
    include_solutions: bool = True


class PptxExportRequest(BaseModel):
    latex_content: str = Field(..., min_length=10)
    title: str = "Matematikk"
    solutions_as: str = Field(
        "speaker_notes",
        description="'speaker_notes' or 'hidden_slides'",
    )


class ExportFileResponse(BaseModel):
    success: bool
    content_base64: str = ""
    filename: str = ""
    mime_type: str = ""
    errors: list[str] = []


# ---------------------------------------------------------------------------
# Cover page LaTeX
# ---------------------------------------------------------------------------
def _build_cover_page(
    school: str,
    teacher: str,
    subject: str,
    topic: str,
) -> str:
    """Generate a LaTeX cover page."""
    return rf"""
\thispagestyle{{empty}}
\begin{{center}}
\vspace*{{3cm}}

{{\Huge\bfseries\sffamily {subject}}}

\vspace{{1cm}}

{{\LARGE\sffamily {topic}}}

\vspace{{2cm}}

{{\large {school}}}

\vspace{{0.5cm}}

{{\large {teacher}}}

\vspace{{1cm}}

{{\large \today}}

\vspace*{{\fill}}

{{\small Generert av MateMaTeX AI}}

\end{{center}}
\newpage
"""


def _make_print_optimized(latex: str) -> str:
    """Convert to grayscale print-friendly version."""
    replacements = {
        r"colback=lightBlue": r"colback=white",
        r"colback=lightGreen": r"colback=white",
        r"colback=lightOrange": r"colback=white",
        r"colback=lightPurple": r"colback=white",
        r"colframe=mainBlue": r"colframe=black!60",
        r"colframe=mainGreen": r"colframe=black!60",
        r"colframe=mainOrange": r"colframe=black!60",
        r"colframe=mainPurple": r"colframe=black!60",
        r"colback=mainBlue": r"colback=black!10",
        r"colback=mainGreen": r"colback=black!10",
    }
    for old, new in replacements.items():
        latex = latex.replace(old, new)
    return latex


# ---------------------------------------------------------------------------
# PDF Export
# ---------------------------------------------------------------------------
@router.post(
    "/pdf",
    response_model=ExportFileResponse,
    summary="Export to PDF with optional cover page and print optimization",
)
async def export_pdf(req: PdfExportRequest, user_id: str = Depends(get_current_user)) -> ExportFileResponse:
    """
    Export LaTeX content to PDF.

    Options:
    - Cover page with school name, teacher, date, subject, topic
    - Print-optimized variant (grayscale, no background colors)
    - QR codes for digital solutions
    """
    content = req.latex_content

    if req.print_optimized:
        content = _make_print_optimized(content)

    # Build full document
    body_parts = []
    if req.include_cover:
        body_parts.append(_build_cover_page(
            school=req.cover_school,
            teacher=req.cover_teacher,
            subject=req.cover_subject,
            topic=req.cover_topic,
        ))

    body_parts.append(content)
    full_body = "\n".join(body_parts)

    if r"\documentclass" not in full_body:
        full_doc = wrap_with_preamble(full_body)
    else:
        full_doc = full_body

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "export.pdf")
        pdf_path = compile_to_pdf(full_doc, out_path)

        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            return ExportFileResponse(
                success=True,
                content_base64=base64.b64encode(pdf_bytes).decode(),
                filename="matematikk.pdf",
                mime_type="application/pdf",
            )
        else:
            return ExportFileResponse(
                success=False,
                errors=["PDF compilation failed"],
            )


# ---------------------------------------------------------------------------
# DOCX Export
# ---------------------------------------------------------------------------
@router.post(
    "/docx",
    response_model=ExportFileResponse,
    summary="Export to Word (DOCX)",
)
async def export_docx(req: DocxExportRequest, user_id: str = Depends(get_current_user)) -> ExportFileResponse:
    """
    Export LaTeX content to Word document.

    Uses python-docx to build the document programmatically for
    maximum control over formatting. Math is rendered as OMML.
    """
    try:
        from app.export.word import latex_to_docx

        docx_bytes = latex_to_docx(
            req.latex_content,
            title=req.title,
            include_solutions=req.include_solutions,
        )

        return ExportFileResponse(
            success=True,
            content_base64=base64.b64encode(docx_bytes).decode(),
            filename="matematikk.docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        logger.error("docx_export_failed", error=str(e))
        return ExportFileResponse(
            success=False,
            errors=[str(e)],
        )


# ---------------------------------------------------------------------------
# PPTX Export
# ---------------------------------------------------------------------------
@router.post(
    "/pptx",
    response_model=ExportFileResponse,
    summary="Export to PowerPoint (PPTX)",
)
async def export_pptx(req: PptxExportRequest, user_id: str = Depends(get_current_user)) -> ExportFileResponse:
    """
    Export exercises as a PowerPoint presentation.

    Each exercise becomes its own slide. Solutions are placed as
    speaker notes or hidden slides, depending on the request.
    """
    try:
        from app.export.powerpoint import latex_to_pptx

        pptx_bytes = latex_to_pptx(
            req.latex_content,
            title=req.title,
            solutions_as=req.solutions_as,
        )

        return ExportFileResponse(
            success=True,
            content_base64=base64.b64encode(pptx_bytes).decode(),
            filename="matematikk.pptx",
            mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
    except Exception as e:
        logger.error("pptx_export_failed", error=str(e))
        return ExportFileResponse(
            success=False,
            errors=[str(e)],
        )
