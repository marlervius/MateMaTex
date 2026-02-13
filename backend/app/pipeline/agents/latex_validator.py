"""
LaTeX validator node — Compiles the document with pdflatex to check for errors.
"""

from __future__ import annotations

from datetime import datetime

import structlog

from app.config import get_config
from app.latex.preamble import wrap_with_preamble
from app.models.state import AgentRole, AgentStep, PipelineState
from app.verification.latex_checker import LatexChecker

logger = structlog.get_logger()


def run_latex_validator(state: PipelineState) -> PipelineState:
    """
    Compile the document with pdflatex to validate it.

    Reads: state.edited_latex_body
    Writes: state.full_document, state.latex_compilation, state.latex_fix_attempts
    """
    step = AgentStep(agent=AgentRole.LATEX_VALIDATOR)
    state.current_agent = AgentRole.LATEX_VALIDATOR

    logger.info(
        "latex_validator_start",
        job_id=state.job_id,
        attempt=state.latex_fix_attempts + 1,
    )

    try:
        # Wrap with preamble
        body = state.edited_latex_body
        if state.latex_fix_attempts > 0 and state.full_document:
            # On retry, use the fixed full document directly
            full_doc = state.full_document
        else:
            full_doc = wrap_with_preamble(body)

        state.full_document = full_doc

        # Compile
        config = get_config()
        checker = LatexChecker(pdflatex_path=config.pdflatex_path)
        result = checker.check(full_doc)

        state.latex_compilation = result
        state.latex_fix_attempts += 1

        if result.success:
            state.final_latex_body = state.edited_latex_body
            state.pdf_path = result.pdf_path
            logger.info("latex_validation_passed", job_id=state.job_id)
        else:
            logger.warning(
                "latex_validation_failed",
                job_id=state.job_id,
                errors=result.errors[:3],
                attempt=state.latex_fix_attempts,
            )

        step.output_summary = (
            f"{'PASS' if result.success else 'FAIL'}: "
            f"{len(result.errors)} errors, {len(result.warnings)} warnings"
        )

    except Exception as e:
        step.error = str(e)
        # On checker error, proceed with unvalidated content
        state.final_latex_body = state.edited_latex_body
        state.latex_fix_attempts += 1
        logger.error("latex_validator_error", job_id=state.job_id, error=str(e))

    finally:
        step.completed_at = datetime.now()
        step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
        state.steps.append(step)

    return state
