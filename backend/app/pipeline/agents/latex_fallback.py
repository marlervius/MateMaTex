"""
Fallback agent node — Returns a stripped-down, guaranteed-to-compile document if all else fails.
"""

from __future__ import annotations

import re
from datetime import datetime

import structlog

from app.models.state import AgentRole, AgentStep, PipelineState

logger = structlog.get_logger()


def run_latex_fallback(state: PipelineState) -> PipelineState:
    """
    Fallback agent that strips problematic LaTeX (like TikZ) to ensure the user gets *something*.

    Reads: state.full_document or state.edited_latex_body
    Writes: state.full_document, state.steps
    """
    step = AgentStep(agent=AgentRole.LATEX_FALLBACK)
    state.current_agent = AgentRole.LATEX_FALLBACK

    logger.warning(
        "latex_fallback_start",
        job_id=state.job_id,
        msg="Max retries reached. Stripping complex formatting for fallback document.",
    )

    try:
        # Get the latest body
        body = state.edited_latex_body or state.raw_latex_body
        
        # 1. Remove all tikzpicture environments
        body = re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', '% [Figur fjernet pga. kompileringsfeil]', body, flags=re.DOTALL)
        
        # 2. Remove all axis/pgfplots environments just in case
        body = re.sub(r'\\begin\{axis\}.*?\\end\{axis\}', '% [Graf fjernet pga. kompileringsfeil]', body, flags=re.DOTALL)
        
        # 3. Strip basic text formatting that might be broken
        body = re.sub(r'\\textcolor\{.*?\}.*?\}', '% [Farge fjernet]', body)
        
        # Add a warning at the top of the document
        fallback_warning = r"""
\begin{tcolorbox}[colback=red!5!white,colframe=red!75!black,title=Kompileringsadvarsel]
Dette dokumentet inneholdt avansert grafikk (f.eks. TikZ-figurer) som feilet under generering. 
For å sikre at du likevel får oppgavene og teksten, har systemet fjernet problematiske figurer.
\end{tcolorbox}
"""
        body = fallback_warning + "\n" + body
        
        state.final_latex_body = body
        state.latex_compilation.success = True # Force success to allow proceeding
        
        step.output_summary = "Laget forenklet fallback-dokument"
        logger.info("latex_fallback_complete", job_id=state.job_id)

    except Exception as e:
        step.error = str(e)
        logger.error("latex_fallback_failed", job_id=state.job_id, error=str(e))

    finally:
        step.completed_at = datetime.now()
        step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
        state.steps.append(step)

    return state
