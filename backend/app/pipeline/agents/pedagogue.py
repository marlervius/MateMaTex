"""
Pedagogue agent node — Plans pedagogical content structure.

This is the first agent in the pipeline. It takes the user request and
produces a structured pedagogical plan that the author will implement.
"""

from __future__ import annotations

from datetime import datetime

import structlog

from app.config import get_config
from app.curriculum import format_boundaries_for_prompt, get_language_level_instructions
from app.models.llm import LLMInterface
from app.models.state import AgentRole, AgentStep, PipelineState
from app.pipeline.prompts.pedagogue import (
    SYSTEM_PROMPT,
    FEW_SHOT_EXAMPLES,
    build_pedagogue_prompt,
)

logger = structlog.get_logger()


def run_pedagogue(state: PipelineState) -> PipelineState:
    """
    Execute the pedagogue agent: produce a pedagogical plan.

    Reads: state.request
    Writes: state.pedagogical_plan, state.curriculum_context, state.steps
    """
    step = AgentStep(agent=AgentRole.PEDAGOGUE)
    state.current_agent = AgentRole.PEDAGOGUE

    logger.info(
        "pedagogue_start",
        job_id=state.job_id,
        grade=state.request.grade,
        topic=state.request.topic,
    )

    try:
        # Build context
        grade_context = format_boundaries_for_prompt(state.request.grade)
        state.curriculum_context = grade_context

        language_instructions = get_language_level_instructions(state.request.language_level)

        # Build the few-shot system prompt
        system_parts = [SYSTEM_PROMPT, "\n=== EKSEMPLER PÅ PERFEKT OUTPUT ===\n"]
        for ex in FEW_SHOT_EXAMPLES:
            system_parts.append(f"INPUT: {ex['input']}\nOUTPUT:\n{ex['output']}\n---\n")

        full_system = "\n".join(system_parts)

        # Build user prompt
        user_prompt = build_pedagogue_prompt(
            grade=state.request.grade,
            topic=state.request.topic,
            material_type=state.request.material_type,
            num_exercises=state.request.num_exercises,
            grade_context=grade_context,
            language_instructions=language_instructions,
            content_options=state.request.model_dump(),
        )

        # Check cache first
        from app.cache import get_cache
        cache = get_cache()
        cached_plan = cache.get_pedagogue_plan(state.request)
        if cached_plan:
            state.pedagogical_plan = cached_plan
            step.output_summary = "[CACHED] " + cached_plan[:200] + "..."
            logger.info("pedagogue_cache_hit", job_id=state.job_id)
            return state

        # Call LLM
        config = get_config()
        llm = LLMInterface(temperature=config.llm.temperature)
        response = llm.invoke(full_system, user_prompt)

        state.pedagogical_plan = response.strip()

        # Cache the plan
        cache.set_pedagogue_plan(state.request, state.pedagogical_plan)

        step.output_summary = state.pedagogical_plan[:200] + "..."
        logger.info(
            "pedagogue_complete",
            job_id=state.job_id,
            plan_length=len(state.pedagogical_plan),
        )

    except Exception as e:
        step.error = str(e)
        logger.error("pedagogue_failed", job_id=state.job_id, error=str(e))
        raise

    finally:
        step.completed_at = datetime.now()
        step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
        state.steps.append(step)

    return state
