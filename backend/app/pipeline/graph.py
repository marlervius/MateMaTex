"""
LangGraph pipeline definition — the heart of MateMaTeX 2.0.

Implements the multi-agent pipeline with verification loops:

    User Input
        ↓
    [Pedagogue] → Pedagogical plan
        ↓
    [Author] → LaTeX body content
        ↓
    [Math Verifier] → SymPy verification of all calculations
        ↓ ← ERRORS? → [Author] retries (max 3)
        ↓
    [Editor] → Quality control & cleanup
        ↓
    [LaTeX Validator] → Actual pdflatex compilation
        ↓ ← ERRORS? → [LaTeX Fixer] retries (max 3)
        ↓
    Final Document
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Callable, Literal

import structlog
from langgraph.graph import END, StateGraph

from app.config import get_config
from app.latex.preamble import wrap_with_style
from app.models.state import (
    GenerationRequest,
    PipelineState,
    PipelineStatus,
)
from app.pipeline.agents.author import run_author
from app.pipeline.agents.editor import run_editor
from app.pipeline.agents.latex_fixer import run_latex_fixer
from app.pipeline.agents.latex_fallback import run_latex_fallback
from app.pipeline.agents.latex_validator import run_latex_validator
from app.pipeline.agents.layout import run_layout
from app.pipeline.agents.math_verifier import run_math_verifier
from app.pipeline.agents.pedagogue import run_pedagogue
from app.pipeline.agents.tikz_validator import run_tikz_validator
from app.pipeline.agents.table_validator import run_table_validator
from app.pipeline.cancel import clear_cancel, is_cancelled

logger = structlog.get_logger()

_ABORT_MESSAGE = "Avbrutt av bruker"


# ---------------------------------------------------------------------------
# Routing functions (conditional edges)
# ---------------------------------------------------------------------------

def _over_time_budget(state: PipelineState) -> bool:
    """True when the job has used more than its wall-clock budget."""
    try:
        budget = get_config().pipeline_max_seconds
    except Exception:
        return False
    elapsed = (datetime.now() - state.created_at).total_seconds()
    if elapsed > budget:
        logger.warning(
            "pipeline_time_budget_exceeded",
            job_id=state.job_id,
            elapsed=round(elapsed, 1),
            budget=budget,
        )
        return True
    return False


def _math_errors_worth_author_retry(state: PipelineState) -> bool:
    """Skip author retry when SymPy mostly could not parse (false positives)."""
    mv = state.math_verification
    incorrect = mv.claims_incorrect
    if incorrect <= 0:
        return False
    if mv.claims_unparseable >= incorrect * 10:
        return False
    verified = max(0, mv.claims_checked - mv.claims_unparseable)
    if incorrect <= 3 and verified < 10 and mv.claims_unparseable > verified:
        return False
    return True


def _should_skip_editor(state: PipelineState) -> bool:
    """Skip the slow LLM editor for worksheets/exams (saves ~3–5 min per job)."""
    config = get_config()
    if config.skip_editor:
        return True
    fast_types = {
        t.strip()
        for t in config.skip_editor_material_types.split(",")
        if t.strip()
    }
    return state.request.material_type in fast_types


def should_retry_math(
    state: PipelineState,
) -> Literal["author", "editor", "tikz_validator"]:
    """
    After math verification: retry author if errors found and retries remain.
    Otherwise proceed to editor or skip straight to validators.
    """
    config = get_config()
    max_retries = config.max_verification_retries

    if (
        not state.math_verification.all_correct
        and state.math_verification_attempts < max_retries
        and _math_errors_worth_author_retry(state)
        and not _over_time_budget(state)
    ):
        logger.info(
            "math_retry_decision",
            decision="retry",
            attempt=state.math_verification_attempts,
            max_retries=max_retries,
            errors=state.math_verification.claims_incorrect,
        )
        return "author"

    if not state.math_verification.all_correct:
        logger.warning(
            "math_retry_decision",
            decision="proceed_with_errors",
            errors=state.math_verification.claims_incorrect,
        )

    if _should_skip_editor(state):
        logger.info(
            "editor_skip_decision",
            material_type=state.request.material_type,
            job_id=state.job_id,
        )
        state.edited_latex_body = state.verified_latex_body
        return "tikz_validator"

    return "editor"


def should_retry_latex(state: PipelineState) -> Literal["latex_fixer", "latex_fallback", "finalize"]:
    """
    After LaTeX validation: retry with fixer if compilation failed and retries remain.
    If max retries reached and still failing, go to fallback.
    """
    config = get_config()
    max_retries = config.max_verification_retries

    if state.latex_compilation.success:
        return "finalize"

    if _over_time_budget(state):
        logger.warning(
            "latex_retry_decision",
            decision="fallback",
            msg="Time budget exceeded. Using fallback document.",
        )
        return "latex_fallback"

    if state.latex_fix_attempts < max_retries:
        logger.info(
            "latex_retry_decision",
            decision="retry",
            attempt=state.latex_fix_attempts,
            max_retries=max_retries,
        )
        return "latex_fixer"
    else:
        logger.warning(
            "latex_retry_decision",
            decision="fallback",
            msg="Max retries reached. Using fallback document.",
        )
        return "latex_fallback"


# ---------------------------------------------------------------------------
# Terminal nodes
# ---------------------------------------------------------------------------

def _apply_differentiation(state: PipelineState) -> None:
    """Build a three-level document when material_type is differensiert."""
    from app.differentiation.generator import differentiate_content_sync

    body = (
        state.final_latex_body
        or state.edited_latex_body
        or state.verified_latex_body
        or state.raw_latex_body
    )
    if not body.strip():
        return

    logger.info("differentiation_pipeline_start", job_id=state.job_id)
    output = differentiate_content_sync(
        body,
        topic=state.request.topic,
        grade=state.request.grade,
    )
    state.differentiated_basic = output.basic_latex
    state.differentiated_advanced = output.advanced_latex

    combined_body = (
        "\\section*{Grunnleggende}\n"
        + (output.basic_latex or body)
        + "\n\n\\section*{Standard}\n"
        + (output.standard_latex or body)
        + "\n\n\\section*{Avansert}\n"
        + (output.advanced_latex or body)
    )
    state.final_latex_body = combined_body
    state.full_document = wrap_with_style(combined_body, state.request.pdf_style)


def finalize(state: PipelineState) -> PipelineState:
    """
    Final node: assemble the complete document and compute summary stats.
    """
    body = (
        state.final_latex_body
        or state.edited_latex_body
        or state.verified_latex_body
        or state.raw_latex_body
    )

    if state.request.material_type == "differensiert":
        _apply_differentiation(state)
        try:
            from app.verification.latex_checker import LatexChecker

            config = get_config()
            checker = LatexChecker(pdflatex_path=config.pdflatex_path)
            compile_result = checker.check(state.full_document)
            state.latex_compilation = compile_result
            if compile_result.pdf_base64:
                state.pdf_base64 = compile_result.pdf_base64
        except Exception as e:
            logger.warning(
                "differentiation_recompile_failed",
                error=str(e),
                job_id=state.job_id,
            )
    elif not state.full_document:
        state.full_document = wrap_with_style(body, state.request.pdf_style)
    elif state.final_latex_body and state.full_document:
        state.full_document = wrap_with_style(state.final_latex_body, state.request.pdf_style)

    if not state.pdf_base64 and state.latex_compilation.pdf_base64:
        state.pdf_base64 = state.latex_compilation.pdf_base64

    state.used_latex_fallback = (
        state.used_latex_fallback or state.latex_compilation.used_fallback
    )

    # Compute totals
    state.total_duration_seconds = sum(s.duration_seconds for s in state.steps)
    state.total_tokens = sum(s.total_tokens for s in state.steps)
    state.current_agent = None

    has_math_issues = (
        state.math_verification.claims_incorrect > 0
        or state.math_verification.claims_unparseable > 0
    )
    reasons: list[str] = []
    if has_math_issues:
        reasons.append("math")
    if state.used_latex_fallback:
        reasons.append("fallback")

    if reasons:
        state.warning_reason = ",".join(reasons)
        state.status = PipelineStatus.COMPLETED_WITH_WARNINGS
    else:
        state.warning_reason = ""
        state.status = PipelineStatus.COMPLETED

    try:
        from app.cache import get_cache

        get_cache().set_full_result(state.request, state.model_dump_json())
    except Exception as e:
        logger.warning("cache_full_result_failed", error=str(e), job_id=state.job_id)

    logger.info(
        "pipeline_complete",
        job_id=state.job_id,
        status=state.status.value,
        total_steps=len(state.steps),
        total_duration=round(state.total_duration_seconds, 1),
        math_verification_attempts=state.math_verification_attempts,
        latex_fix_attempts=state.latex_fix_attempts,
        latex_compiled=state.latex_compilation.success,
        used_fallback=state.used_latex_fallback,
    )

    return state


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def create_pipeline() -> StateGraph:
    """
    Build the LangGraph pipeline.

    Graph topology:

        pedagogue → author → math_verifier
                        ↑           |
                        |    (retry if errors)
                        +-----------+
                                    |
                                    ↓
                              editor → tikz_validator → table_validator → latex_validator
                                                                                  ↑         |
                                                                                  |  (retry if errors)
                                                                                  +---------+
                                                                                            |
                                                                                            ↓
                                                                                        finalize → END
    """
    # Define the graph with PipelineState
    graph = StateGraph(PipelineState)

    # Add nodes
    graph.add_node("pedagogue", run_pedagogue)
    graph.add_node("author", run_author)
    graph.add_node("math_verifier", run_math_verifier)
    graph.add_node("editor", run_editor)
    graph.add_node("tikz_validator", run_tikz_validator)    # Rule-based figure fixer
    graph.add_node("table_validator", run_table_validator)  # Rule-based table fixer
    graph.add_node("latex_validator", run_latex_validator)
    graph.add_node("latex_fixer", run_latex_fixer)
    graph.add_node("latex_fallback", run_latex_fallback)
    graph.add_node("layout", run_layout)  # Track E: non-destructive layout QA
    graph.add_node("finalize", finalize)

    # Set entry point
    graph.set_entry_point("pedagogue")

    # Linear edges
    graph.add_edge("pedagogue", "author")
    graph.add_edge("author", "math_verifier")

    # Conditional: math verification → retry author OR proceed to editor
    graph.add_conditional_edges(
        "math_verifier",
        should_retry_math,
        {
            "author": "author",
            "editor": "editor",
            "tikz_validator": "tikz_validator",
        },
    )

    # Linear: editor → tikz_validator → table_validator → latex validation
    graph.add_edge("editor", "tikz_validator")
    graph.add_edge("tikz_validator", "table_validator")
    graph.add_edge("table_validator", "latex_validator")

    # Conditional: latex validation → retry with fixer OR fallback OR finalize
    graph.add_conditional_edges(
        "latex_validator",
        should_retry_latex,
        {
            "latex_fixer": "latex_fixer",
            "latex_fallback": "latex_fallback",
            "finalize": "layout",
        },
    )

    # LaTeX fixer goes back to validation
    graph.add_edge("latex_fixer", "latex_validator")

    # Fallback runs layout QA too, then finalize
    graph.add_edge("latex_fallback", "layout")

    # Layout QA → finalize → END
    graph.add_edge("layout", "finalize")
    graph.add_edge("finalize", END)

    return graph


# ---------------------------------------------------------------------------
# Convenience runner
# ---------------------------------------------------------------------------

def _coerce_state(value: object) -> PipelineState:
    """LangGraph may yield a dict or a PipelineState — normalise to PipelineState."""
    if isinstance(value, PipelineState):
        return value
    if isinstance(value, dict):
        return PipelineState(**value)
    raise TypeError(f"Unexpected pipeline state type: {type(value)!r}")


def run_pipeline(
    request: GenerationRequest,
    *,
    job_id: str | None = None,
    owner_id: str = "",
    on_progress: "Callable[[PipelineState], None] | None" = None,
) -> PipelineState:
    """
    Run the full pipeline synchronously.

    Args:
        request: The generation request from the user.
        job_id: Reuse this job id (so the API and SSE clients can track the same
            job). When omitted a fresh id is generated.
        owner_id: User id that owns this job (for authorization checks).
        on_progress: Optional callback invoked with the latest state after every
            graph super-step, enabling live SSE progress streaming.

    Returns:
        Final PipelineState with all outputs and observability data.
    """
    logger.info(
        "pipeline_start",
        grade=request.grade,
        topic=request.topic,
        material_type=request.material_type,
        job_id=job_id,
    )

    # Build initial state, reusing the caller's job id so persistence and
    # streaming all key off a single, stable id.
    state = PipelineState(
        request=request,
        status=PipelineStatus.RUNNING,
        owner_id=owner_id,
    )
    if job_id:
        state.job_id = job_id

    # Exact cache hit — return prior result with the active job id
    try:
        from app.cache import get_cache

        cached_json = get_cache().get_full_result(request)
        if cached_json:
            data = json.loads(cached_json)
            restored = PipelineState(**data)
            restored.job_id = state.job_id
            restored.created_at = state.created_at
            restored.from_cache = True
            if owner_id and not restored.owner_id:
                restored.owner_id = owner_id
            restored.status = (
                PipelineStatus.COMPLETED_WITH_WARNINGS
                if (
                    restored.math_verification.claims_incorrect > 0
                    or restored.math_verification.claims_unparseable > 0
                )
                else PipelineStatus.COMPLETED
            )
            logger.info("pipeline_cache_hit", job_id=restored.job_id)
            if on_progress:
                on_progress(restored)
            return restored
    except Exception as e:
        logger.warning("pipeline_cache_restore_failed", error=str(e))

    graph = create_pipeline()
    compiled = graph.compile()

    # Run, streaming intermediate state so the SSE endpoint sees live progress.
    final_state = state
    try:
        # stream_mode="values" yields the full accumulated state after each
        # node, so we can publish incremental progress to SSE clients.
        for chunk in compiled.stream(state, stream_mode="values"):
            if job_id and is_cancelled(job_id):
                final_state = _coerce_state(chunk)
                if job_id:
                    final_state.job_id = job_id
                final_state.status = PipelineStatus.FAILED
                final_state.error_message = _ABORT_MESSAGE
                logger.info("pipeline_cancelled", job_id=job_id)
                clear_cancel(job_id)
                return final_state

            final_state = _coerce_state(chunk)
            # job_id/owner_id are not mutated by nodes, but re-assert to be safe.
            if job_id:
                final_state.job_id = job_id
            if owner_id and not final_state.owner_id:
                final_state.owner_id = owner_id
            if on_progress is not None:
                try:
                    on_progress(final_state)
                except Exception as cb_err:  # never let a callback kill the run
                    logger.warning("pipeline_progress_callback_failed", error=str(cb_err))

        return final_state

    except Exception as e:
        final_state.status = PipelineStatus.FAILED
        final_state.error_message = str(e)
        if job_id:
            final_state.job_id = job_id
        logger.error("pipeline_failed", error=str(e), job_id=final_state.job_id)
        return final_state
