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

from datetime import datetime
from typing import Literal

import structlog
from langgraph.graph import END, StateGraph

from app.config import get_config
from app.latex.preamble import wrap_with_preamble
from app.models.state import (
    GenerationRequest,
    PipelineState,
    PipelineStatus,
)
from app.pipeline.agents.author import run_author
from app.pipeline.agents.editor import run_editor
from app.pipeline.agents.latex_fixer import run_latex_fixer
from app.pipeline.agents.latex_validator import run_latex_validator
from app.pipeline.agents.math_verifier import run_math_verifier
from app.pipeline.agents.pedagogue import run_pedagogue

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Routing functions (conditional edges)
# ---------------------------------------------------------------------------

def should_retry_math(state: PipelineState) -> Literal["author", "editor"]:
    """
    After math verification: retry author if errors found and retries remain.
    """
    config = get_config()
    max_retries = config.max_verification_retries

    if (
        not state.math_verification.all_correct
        and state.math_verification_attempts < max_retries
        and state.math_verification.claims_incorrect > 0
    ):
        logger.info(
            "math_retry_decision",
            decision="retry",
            attempt=state.math_verification_attempts,
            max_retries=max_retries,
            errors=state.math_verification.claims_incorrect,
        )
        return "author"
    else:
        if not state.math_verification.all_correct:
            logger.warning(
                "math_retry_decision",
                decision="proceed_with_errors",
                errors=state.math_verification.claims_incorrect,
            )
        return "editor"


def should_retry_latex(state: PipelineState) -> Literal["latex_fixer", "finalize"]:
    """
    After LaTeX validation: retry with fixer if compilation failed and retries remain.
    """
    config = get_config()
    max_retries = config.max_verification_retries

    if (
        not state.latex_compilation.success
        and state.latex_fix_attempts < max_retries
    ):
        logger.info(
            "latex_retry_decision",
            decision="retry",
            attempt=state.latex_fix_attempts,
            max_retries=max_retries,
        )
        return "latex_fixer"
    else:
        return "finalize"


# ---------------------------------------------------------------------------
# Terminal nodes
# ---------------------------------------------------------------------------

def finalize(state: PipelineState) -> PipelineState:
    """
    Final node: assemble the complete document and compute summary stats.
    """
    # Ensure we have a full document
    if not state.full_document:
        body = state.final_latex_body or state.edited_latex_body or state.verified_latex_body or state.raw_latex_body
        state.full_document = wrap_with_preamble(body)

    # Compute totals
    state.total_duration_seconds = sum(s.duration_seconds for s in state.steps)
    state.total_tokens = sum(s.total_tokens for s in state.steps)
    state.status = PipelineStatus.COMPLETED
    state.current_agent = None

    logger.info(
        "pipeline_complete",
        job_id=state.job_id,
        total_steps=len(state.steps),
        total_duration=round(state.total_duration_seconds, 1),
        math_verification_attempts=state.math_verification_attempts,
        latex_fix_attempts=state.latex_fix_attempts,
        latex_compiled=state.latex_compilation.success,
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
                              editor → latex_validator
                                              ↑          |
                                              |   (retry if errors)
                                              +----------+
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
    graph.add_node("latex_validator", run_latex_validator)
    graph.add_node("latex_fixer", run_latex_fixer)
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
        },
    )

    # Linear: editor → latex validation
    graph.add_edge("editor", "latex_validator")

    # Conditional: latex validation → retry with fixer OR finalize
    graph.add_conditional_edges(
        "latex_validator",
        should_retry_latex,
        {
            "latex_fixer": "latex_fixer",
            "finalize": "finalize",
        },
    )

    # LaTeX fixer goes back to validation
    graph.add_edge("latex_fixer", "latex_validator")

    # Finalize → END
    graph.add_edge("finalize", END)

    return graph


# ---------------------------------------------------------------------------
# Convenience runner
# ---------------------------------------------------------------------------

def run_pipeline(request: GenerationRequest) -> PipelineState:
    """
    Run the full pipeline synchronously.

    Args:
        request: The generation request from the user.

    Returns:
        Final PipelineState with all outputs and observability data.
    """
    logger.info(
        "pipeline_start",
        grade=request.grade,
        topic=request.topic,
        material_type=request.material_type,
    )

    # Build initial state
    state = PipelineState(
        request=request,
        status=PipelineStatus.RUNNING,
    )

    # Create and compile the graph
    graph = create_pipeline()
    compiled = graph.compile()

    # Run
    try:
        final_state = compiled.invoke(state)

        # LangGraph returns a dict — reconstruct PipelineState
        if isinstance(final_state, dict):
            final_state = PipelineState(**final_state)

        return final_state

    except Exception as e:
        state.status = PipelineStatus.FAILED
        state.error_message = str(e)
        logger.error("pipeline_failed", error=str(e), job_id=state.job_id)
        return state
