"""
LaTeX fixer agent node — Automatically fixes compilation errors.
"""

from __future__ import annotations

from datetime import datetime

import structlog

from app.config import get_config
from app.models.llm import LLMInterface
from app.models.state import AgentRole, AgentStep, PipelineState
from app.pipeline.prompts.latex_fixer import SYSTEM_PROMPT, build_fixer_prompt
from app.verification.latex_checker import format_latex_errors_for_agent

logger = structlog.get_logger()


def run_latex_fixer(state: PipelineState) -> PipelineState:
    """
    Fix LaTeX compilation errors using an LLM.

    Reads: state.full_document, state.latex_compilation
    Writes: state.full_document, state.edited_latex_body, state.steps
    """
    step = AgentStep(agent=AgentRole.LATEX_FIXER)
    state.current_agent = AgentRole.LATEX_FIXER

    logger.info(
        "latex_fixer_start",
        job_id=state.job_id,
        errors=len(state.latex_compilation.errors),
    )

    try:
        config = get_config()
        llm = LLMInterface(temperature=0.1)  # Very low temp for precise fixes

        error_report = format_latex_errors_for_agent(state.latex_compilation)
        user_prompt = build_fixer_prompt(
            full_document=state.full_document,
            compilation_errors=error_report,
        )

        response = llm.invoke(SYSTEM_PROMPT, user_prompt)
        fixed_doc = response.strip()

        # Clean LLM output: strip markdown code fences that LLMs often add
        import re as _re
        # Remove ```latex ... ``` or ``` ... ``` wrapping
        fixed_doc = _re.sub(r'^```(?:latex|tex)?\s*\n?', '', fixed_doc)
        fixed_doc = _re.sub(r'\n?```\s*$', '', fixed_doc)
        fixed_doc = fixed_doc.strip()

        # Validate that the fixed document still contains \begin{document}
        if r'\begin{document}' not in fixed_doc:
            logger.warning("latex_fixer_missing_begin_document", doc_start=fixed_doc[:100])
            # Fall back to the original document — don't overwrite with garbage
            fixed_doc = state.full_document
        else:
            # The fixer returns the full document (with preamble)
            state.full_document = fixed_doc

        # Also extract body for consistency
        import re
        body_match = re.search(
            r'\\begin\{document\}(.*?)\\end\{document\}',
            fixed_doc,
            re.DOTALL,
        )
        if body_match:
            state.edited_latex_body = body_match.group(1).strip()

        step.output_summary = f"Fixed document ({len(fixed_doc)} chars)"
        logger.info("latex_fixer_complete", job_id=state.job_id)

    except Exception as e:
        step.error = str(e)
        logger.error("latex_fixer_failed", job_id=state.job_id, error=str(e))

    finally:
        step.completed_at = datetime.now()
        step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
        state.steps.append(step)

    return state
