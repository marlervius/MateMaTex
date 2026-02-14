"""
Author agent node — Writes LaTeX body content with TikZ illustrations.

This is the second agent. It takes the pedagogical plan and produces
complete LaTeX body content. It may be called multiple times if
the math verifier finds errors (retry loop).
"""

from __future__ import annotations

from datetime import datetime

import structlog

from app.config import get_config
from app.curriculum import format_boundaries_for_prompt, get_language_level_instructions
from app.models.llm import LLMInterface
from app.models.state import AgentRole, AgentStep, PipelineState
from app.pipeline.prompts.author import (
    SYSTEM_PROMPT,
    FEW_SHOT_EXAMPLES,
    build_author_prompt,
    build_author_fix_prompt,
)

logger = structlog.get_logger()


def run_author(state: PipelineState) -> PipelineState:
    """
    Execute the author agent: write LaTeX body content.

    If this is a retry (math_verification_attempts > 0), the author receives
    the error report and current content to fix.

    Reads: state.pedagogical_plan, state.math_verification, state.raw_latex_body
    Writes: state.raw_latex_body, state.steps
    """
    step = AgentStep(agent=AgentRole.AUTHOR)
    state.current_agent = AgentRole.AUTHOR

    is_retry = state.math_verification_attempts > 0

    logger.info(
        "author_start",
        job_id=state.job_id,
        is_retry=is_retry,
        attempt=state.math_verification_attempts,
    )

    try:
        config = get_config()
        llm = LLMInterface(temperature=config.llm.temperature)

        # Build system prompt with few-shot examples
        system_parts = [SYSTEM_PROMPT, "\n=== EKSEMPLER PÅ PERFEKT OUTPUT ===\n"]
        for ex in FEW_SHOT_EXAMPLES:
            system_parts.append(f"INPUT: {ex['input']}\nOUTPUT:\n{ex['output']}\n---\n")

        full_system = "\n".join(system_parts)

        if is_retry:
            # Retry mode: fix errors found by math verifier
            from app.verification.math_checker import format_errors_for_agent

            error_report = format_errors_for_agent(state.math_verification)
            user_prompt = build_author_fix_prompt(
                current_latex=state.raw_latex_body,
                error_report=error_report,
            )
            step.input_summary = f"RETRY #{state.math_verification_attempts}: fixing {state.math_verification.claims_incorrect} math errors"
        else:
            # First run: generate from plan
            grade_context = state.curriculum_context or format_boundaries_for_prompt(
                state.request.grade
            )
            language_instructions = get_language_level_instructions(
                state.request.language_level
            )

            user_prompt = build_author_prompt(
                pedagogical_plan=state.pedagogical_plan,
                grade=state.request.grade,
                grade_context=grade_context,
                language_instructions=language_instructions,
                content_options=state.request.model_dump(),
            )
            step.input_summary = f"Plan: {state.pedagogical_plan[:100]}..."

        # Call LLM
        response = llm.invoke(full_system, user_prompt)
        body = response.strip()

        # Clean LLM output: strip markdown code fences
        import re as _re
        body = _re.sub(r'^```(?:latex|tex)?\s*\n?', '', body)
        body = _re.sub(r'\n?```\s*$', '', body)
        state.raw_latex_body = body.strip()

        step.output_summary = f"LaTeX body ({len(state.raw_latex_body)} chars)"
        logger.info(
            "author_complete",
            job_id=state.job_id,
            body_length=len(state.raw_latex_body),
            is_retry=is_retry,
        )

    except Exception as e:
        step.error = str(e)
        logger.error("author_failed", job_id=state.job_id, error=str(e))
        raise

    finally:
        step.completed_at = datetime.now()
        step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
        step.retries = state.math_verification_attempts
        state.steps.append(step)

    return state
