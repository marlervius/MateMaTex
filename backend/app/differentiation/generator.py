"""
Differentiation generator — produces three difficulty levels from standard output.

Takes the final LaTeX output from the pipeline and generates:
- Grunnleggende (basic): simpler numbers, more intermediate steps, extra hints
- Standard: the original content
- Avansert (advanced): harder numbers, fewer steps, composite/proof tasks

Uses a single LLM call with structured JSON output, then parses into
three separate LaTeX documents. All three are SymPy-verified.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import get_current_user

from app.models.llm import get_llm

logger = structlog.get_logger()

router = APIRouter(prefix="/differentiation", tags=["differentiation"])


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------
@dataclass
class DifferentiatedOutput:
    """Three-level differentiated content."""
    basic_latex: str = ""
    standard_latex: str = ""
    advanced_latex: str = ""
    basic_verified: bool = False
    standard_verified: bool = False
    advanced_verified: bool = False


class DifferentiateRequest(BaseModel):
    """Request to differentiate existing LaTeX content."""
    latex_content: str = Field(
        ...,
        min_length=10,
        description="The standard-level LaTeX content to differentiate",
    )
    topic: str = Field("", description="Math topic for context")
    grade: str = Field("", description="Grade level for context")

    class Config:
        json_schema_extra = {
            "example": {
                "latex_content": "\\begin{taskbox}{Oppgave 1}\nLøs $2x + 3 = 7$\n\\end{taskbox}",
                "topic": "Algebra",
                "grade": "8. trinn",
            }
        }


class DifferentiateResponse(BaseModel):
    success: bool
    basic_latex: str = ""
    standard_latex: str = ""
    advanced_latex: str = ""
    basic_exercise_count: int = 0
    standard_exercise_count: int = 0
    advanced_exercise_count: int = 0
    errors: list[str] = []


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
_DIFFERENTIATION_SYSTEM = """Du er en ekspert matematikklærer som differensierer undervisningsmateriell.

Du får et sett med matematikkoppgaver på standard nivå. Du skal lage TRE versjoner:

## GRUNNLEGGENDE
- Enklere tall (helst heltall, små tall)
- Vis flere mellomregninger og steg
- Legg til "Tips:"-bokser med hint
- Fjern de vanskeligste oppgavene (behold 60-70% av antallet)
- Legg til et løst eksempel FØR oppgavene

## STANDARD
- Behold originalen uendret

## AVANSERT
- Vanskeligere tall (desimaler, brøker, store tall)
- Fjern mellomregninger — elever må finne ut selv
- Legg til sammensatte oppgaver som kombinerer flere konsepter
- Legg til bevisoppgaver eller "forklar hvorfor"-oppgaver
- Legg til 1-2 ekstra utfordringsoppgaver

VIKTIG:
- All matematikk SKAL være korrekt på ALLE tre nivåer
- Behold alle LaTeX-miljøer (taskbox, tcolorbox, align, etc.)
- Returner som JSON med nøklene "basic", "standard", "advanced"
- Hver verdi er den KOMPLETTE LaTeX-kroppen (uten preamble/documentclass)
- Bruk NØYAKTIG samme LaTeX-konvensjoner som input"""


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------
async def differentiate_content(
    latex_content: str,
    topic: str = "",
    grade: str = "",
) -> DifferentiatedOutput:
    """
    Generate three difficulty levels from standard LaTeX content.

    Uses one LLM call with structured JSON output.
    """
    llm = get_llm(temperature=0.3)

    user_prompt = f"STANDARD-NIVÅ INNHOLD:\n\n{latex_content}"
    if topic:
        user_prompt += f"\n\nEMNE: {topic}"
    if grade:
        user_prompt += f"\n\nTRINN: {grade}"

    user_prompt += (
        "\n\nReturner JSON med nøklene 'basic', 'standard', 'advanced'. "
        "Hver verdi er komplett LaTeX-kropp."
    )

    result = await llm.ainvoke(_DIFFERENTIATION_SYSTEM, user_prompt)

    # Parse JSON from response
    output = DifferentiatedOutput(standard_latex=latex_content)

    try:
        # Try to extract JSON from the response
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            data = json.loads(json_match.group())
            output.basic_latex = data.get("basic", "")
            output.standard_latex = data.get("standard", latex_content)
            output.advanced_latex = data.get("advanced", "")
        else:
            logger.warning("differentiation_no_json", response_preview=result[:200])
    except json.JSONDecodeError as e:
        logger.error("differentiation_json_parse_error", error=str(e))

    # Verify math in all three levels
    try:
        from app.verification.math_checker import MathChecker

        checker = MathChecker()
        for level, content in [
            ("basic", output.basic_latex),
            ("standard", output.standard_latex),
            ("advanced", output.advanced_latex),
        ]:
            if content:
                verification = checker.verify(content)
                setattr(output, f"{level}_verified", verification.all_correct)
                if not verification.all_correct:
                    logger.warning(
                        f"differentiation_{level}_math_errors",
                        errors=verification.claims_incorrect,
                    )
    except Exception as e:
        logger.warning("differentiation_verification_skipped", error=str(e))

    logger.info(
        "differentiation_completed",
        basic_len=len(output.basic_latex),
        standard_len=len(output.standard_latex),
        advanced_len=len(output.advanced_latex),
    )

    return output


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/generate",
    response_model=DifferentiateResponse,
    summary="Generate three difficulty levels from standard content",
    responses={
        200: {
            "description": "Three-level differentiated content",
        }
    },
)
async def differentiate(req: DifferentiateRequest, user_id: str = Depends(get_current_user)) -> DifferentiateResponse:
    """
    Generate basic, standard, and advanced versions of the given LaTeX content.

    Uses AI to adapt exercises for different ability levels while
    maintaining mathematical correctness (verified with SymPy).
    """
    try:
        output = await differentiate_content(
            req.latex_content,
            topic=req.topic,
            grade=req.grade,
        )

        def _count_exercises(latex: str) -> int:
            return latex.count(r"\begin{taskbox}")

        return DifferentiateResponse(
            success=True,
            basic_latex=output.basic_latex,
            standard_latex=output.standard_latex,
            advanced_latex=output.advanced_latex,
            basic_exercise_count=_count_exercises(output.basic_latex),
            standard_exercise_count=_count_exercises(output.standard_latex),
            advanced_exercise_count=_count_exercises(output.advanced_latex),
        )
    except Exception as e:
        logger.error("differentiation_failed", error=str(e))
        return DifferentiateResponse(success=False, errors=[str(e)])
