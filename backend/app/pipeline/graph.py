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

import base64
from datetime import datetime
from pathlib import Path
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
from app.pipeline.agents.latex_fallback import run_latex_fallback
from app.pipeline.agents.latex_validator import run_latex_validator
from app.pipeline.agents.math_verifier import run_math_verifier
from app.pipeline.agents.pedagogue import run_pedagogue
from app.pipeline.agents.tikz_validator import run_tikz_validator
from app.pipeline.agents.table_validator import run_table_validator

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


def should_retry_latex(state: PipelineState) -> Literal["latex_fixer", "latex_fallback", "finalize"]:
    """
    After LaTeX validation: retry with fixer if compilation failed and retries remain.
    If max retries reached and still failing, go to fallback.
    """
    config = get_config()
    max_retries = config.max_verification_retries

    if state.latex_compilation.success:
        return "finalize"
        
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

def finalize(state: PipelineState) -> PipelineState:
    """
    Final node: assemble the complete document and compute summary stats.
    """
    # Ensure we have a full document
    if not state.full_document:
        body = state.final_latex_body or state.edited_latex_body or state.verified_latex_body or state.raw_latex_body
        state.full_document = wrap_with_preamble(body)

    # Compile full document to PDF and encode as base64
    try:
        from app.latex.compiler import compile_to_pdf
        config = get_config()
        pdf_path = compile_to_pdf(
            latex_content=state.full_document,
            output_path=f"{config.output_dir}/{state.job_id}.pdf",
            pdflatex_path=config.pdflatex_path,
        )
        if pdf_path:
            state.pdf_path = pdf_path
            state.pdf_base64 = base64.b64encode(Path(pdf_path).read_bytes()).decode()
    except Exception as e:
        logger.warning("finalize_pdf_compilation_failed", error=str(e))

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
            "finalize": "finalize",
        },
    )

    # LaTeX fixer goes back to validation
    graph.add_edge("latex_fixer", "latex_validator")
    
    # Fallback goes straight to finalize
    graph.add_edge("latex_fallback", "finalize")

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
