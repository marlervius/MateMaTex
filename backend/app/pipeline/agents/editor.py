"""
Editor agent node — Quality control, cleanup, final validation.
"""

from __future__ import annotations

from datetime import datetime

import structlog

from app.config import get_config
from app.models.llm import LLMInterface
from app.models.state import AgentRole, AgentStep, PipelineState
from app.pipeline.prompts.editor import SYSTEM_PROMPT, build_editor_prompt

logger = structlog.get_logger()


def run_editor(state: PipelineState) -> PipelineState:
    """
    Execute the editor agent: quality-check and clean the LaTeX content.

    Reads: state.verified_latex_body
    Writes: state.edited_latex_body, state.steps
    """
    step = AgentStep(agent=AgentRole.EDITOR)
    state.current_agent = AgentRole.EDITOR

    logger.info("editor_start", job_id=state.job_id)

    try:
        config = get_config()
        llm = LLMInterface(temperature=config.llm.temperature)

        user_prompt = build_editor_prompt(
            latex_content=state.verified_latex_body,
            language_level=state.request.language_level,
        )

        response = llm.invoke(SYSTEM_PROMPT, user_prompt)
        state.edited_latex_body = response.strip()

        step.output_summary = f"Edited LaTeX ({len(state.edited_latex_body)} chars)"
        logger.info(
            "editor_complete",
            job_id=state.job_id,
            body_length=len(state.edited_latex_body),
        )

    except Exception as e:
        step.error = str(e)
        # Fallback: use verified content as-is
        state.edited_latex_body = state.verified_latex_body
        logger.error("editor_failed", job_id=state.job_id, error=str(e))

    finally:
        step.completed_at = datetime.now()
        step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
        state.steps.append(step)

    return state
