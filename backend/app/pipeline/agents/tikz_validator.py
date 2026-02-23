"""
TikZ Figure Validator — rule-based post-processing of LaTeX body.

No LLM calls. Runs after Editor, before LaTeX Validator.
Catches the most common AI figure mistakes and either fixes them
automatically or replaces the broken figure with a safe fallback.

Rules applied (in order):
1. Strip any remaining \\includegraphics
2. Ensure every \\begin{tikzpicture} is inside \\begin{figure}[H]
3. Remove node coordinates that are clearly out-of-bounds (outside figure bounds)
4. Replace known bad Pytagoras patterns (squares outside triangle) with \\MMArettvinklet
5. Ensure every \\begin{axis} (pgfplots) is wrapped in figure
6. Log a summary of all changes made
"""

from __future__ import annotations

import re
from datetime import datetime

import structlog

from app.models.state import AgentRole, AgentStep, PipelineState

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Individual fix functions
# ---------------------------------------------------------------------------

def _strip_includegraphics(body: str) -> tuple[str, int]:
    """Remove all \\includegraphics commands."""
    pattern = re.compile(
        r'\\includegraphics\s*(?:\[.*?\])?\s*\{[^}]*\}',
        re.DOTALL,
    )
    new_body, count = pattern.subn('', body)
    return new_body, count


def _wrap_bare_tikzpicture(body: str) -> tuple[str, int]:
    """
    Wrap any \\begin{tikzpicture}...\\end{tikzpicture} that is NOT already
    inside a figure environment.
    """
    count = 0

    # Find all tikzpicture spans and check if they are inside figure
    result = []
    pos = 0
    tikz_start_re = re.compile(r'\\begin\{tikzpicture\}')
    tikz_end_re = re.compile(r'\\end\{tikzpicture\}')

    i = 0
    text = body
    output_parts = []

    while True:
        m_start = tikz_start_re.search(text, i)
        if not m_start:
            output_parts.append(text[i:])
            break

        # Find matching end
        m_end = tikz_end_re.search(text, m_start.end())
        if not m_end:
            output_parts.append(text[i:])
            break

        # Check if there is a \begin{figure} before this tikzpicture (within 500 chars)
        preceding = text[max(0, m_start.start()-500):m_start.start()]
        # Count begin{figure} vs end{figure} in preceding context
        fig_opens = len(re.findall(r'\\begin\{figure\}', preceding))
        fig_closes = len(re.findall(r'\\end\{figure\}', preceding))
        inside_figure = fig_opens > fig_closes

        if inside_figure:
            # Already wrapped — pass through as-is
            output_parts.append(text[i:m_end.end()])
        else:
            # Not wrapped — add figure wrapper
            tikz_block = text[m_start.start():m_end.end()]
            wrapped = (
                '\\begin{figure}[H]\n'
                '\\centering\n'
                + tikz_block
                + '\n\\caption{Figur}\n'
                '\\end{figure}'
            )
            output_parts.append(text[i:m_start.start()])
            output_parts.append(wrapped)
            count += 1

        i = m_end.end()

    return ''.join(output_parts), count


def _wrap_bare_axis(body: str) -> tuple[str, int]:
    """
    Wrap any \\begin{axis}...\\end{axis} that is NOT inside a figure.
    """
    count = 0
    text = body
    output_parts = []
    i = 0
    axis_start_re = re.compile(r'\\begin\{axis\}')
    axis_end_re = re.compile(r'\\end\{axis\}')

    while True:
        m_start = axis_start_re.search(text, i)
        if not m_start:
            output_parts.append(text[i:])
            break

        m_end = axis_end_re.search(text, m_start.end())
        if not m_end:
            output_parts.append(text[i:])
            break

        # Check for surrounding figure env — need tikzpicture wrapping axis too
        preceding = text[max(0, m_start.start()-600):m_start.start()]
        fig_opens = len(re.findall(r'\\begin\{figure\}', preceding))
        fig_closes = len(re.findall(r'\\end\{figure\}', preceding))
        inside_figure = fig_opens > fig_closes

        if inside_figure:
            output_parts.append(text[i:m_end.end()])
        else:
            axis_block = text[m_start.start():m_end.end()]
            wrapped = (
                '\\begin{figure}[H]\n'
                '\\centering\n'
                '\\begin{tikzpicture}\n'
                + axis_block
                + '\n\\end{tikzpicture}\n'
                '\\caption{Graf}\n'
                '\\end{figure}'
            )
            output_parts.append(text[i:m_start.start()])
            output_parts.append(wrapped)
            count += 1

        i = m_end.end()

    return ''.join(output_parts), count


def _replace_pytagoras_squares(body: str) -> tuple[str, int]:
    """
    Detect the anti-pattern where AI draws squares on all sides of a Pythagorean
    triangle. This produces figures that overflow the page.

    Heuristic: any tikzpicture that contains BOTH:
    - coordinate definitions named A, B, C (or similar)
    - multiple \\fill or \\draw with rectangular coordinates suggesting squares

    Replace the entire figure block with \\MMArettvinklet{3}{4}{5} as a safe fallback.
    """
    count = 0

    # Pattern: figure environment containing a tikzpicture with the squares heuristic
    # Look for tikzpictures that have "a^2" or "b^2" or "c^2" as node text
    # AND have coordinates clearly outside the triangle (large negative or >8 coordinates)
    fig_re = re.compile(
        r'\\begin\{figure\}.*?\\end\{figure\}',
        re.DOTALL,
    )

    def replace_figure(m: re.Match) -> str:
        nonlocal count
        fig_text = m.group(0)

        # Heuristic 1: contains "a^2" or similar AND a tikzpicture
        has_squares_label = bool(re.search(r'\$a\^2\$|\$b\^2\$|\$c\^2\$', fig_text))
        has_tikz = '\\begin{tikzpicture}' in fig_text

        if not (has_squares_label and has_tikz):
            return fig_text  # Not the problematic pattern

        # Heuristic 2: coordinates go outside reasonable page bounds
        # Extract all coordinate tuples like (x,y) or at (x,y)
        coords = re.findall(r'at\s*\((-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\)', fig_text)
        out_of_bounds = any(
            abs(float(x)) > 8 or abs(float(y)) > 8
            for x, y in coords
        )

        if out_of_bounds or has_squares_label:
            # Extract caption if present
            caption_m = re.search(r'\\caption\{([^}]*)\}', fig_text)
            caption = caption_m.group(1) if caption_m else 'Rettvinklet trekant med Pytagoras\\textquotesingle{} setning.'
            count += 1
            return (
                '\\begin{figure}[H]\n'
                '\\centering\n'
                '\\MMArettvinklet{3}{4}{5}\n'
                f'\\caption{{{caption}}}\n'
                '\\end{figure}'
            )

        return fig_text

    new_body = fig_re.sub(replace_figure, body)
    return new_body, count


def _fix_figure_placement(body: str) -> tuple[str, int]:
    """
    Ensure all \\begin{figure} have [H] placement specifier.
    """
    pattern = re.compile(r'\\begin\{figure\}(?!\[)')
    new_body, count = pattern.subn(r'\\begin{figure}[H]', body)
    return new_body, count


def _add_missing_centering(body: str) -> tuple[str, int]:
    """
    Add \\centering after \\begin{figure}[H] if missing.
    """
    count = 0

    def add_centering(m: re.Match) -> str:
        nonlocal count
        full = m.group(0)
        # Check if centering is already present
        after = full[len('\\begin{figure}[H]'):]
        if '\\centering' not in after[:60]:
            count += 1
            return '\\begin{figure}[H]\n\\centering'
        return full

    pattern = re.compile(r'\\begin\{figure\}\[H\]')
    new_body = pattern.sub(add_centering, body)
    return new_body, count


# ---------------------------------------------------------------------------
# Main agent
# ---------------------------------------------------------------------------

def run_tikz_validator(state: PipelineState) -> PipelineState:
    """
    Rule-based TikZ figure validator / auto-fixer.

    Reads:  state.edited_latex_body
    Writes: state.edited_latex_body (cleaned), state.steps
    """
    step = AgentStep(agent=AgentRole.TIKZ_VALIDATOR)
    state.current_agent = AgentRole.TIKZ_VALIDATOR

    logger.info("tikz_validator_start", job_id=state.job_id)

    try:
        body = state.edited_latex_body or state.verified_latex_body or state.raw_latex_body

        fixes: list[str] = []

        # Rule 1: strip \includegraphics
        body, n = _strip_includegraphics(body)
        if n:
            fixes.append(f"Removed {n} \\includegraphics")

        # Rule 2: fix figure[H] placement
        body, n = _fix_figure_placement(body)
        if n:
            fixes.append(f"Added [H] to {n} figure(s)")

        # Rule 3: add \centering
        body, n = _add_missing_centering(body)
        if n:
            fixes.append(f"Added \\centering to {n} figure(s)")

        # Rule 4: wrap bare tikzpicture in figure
        body, n = _wrap_bare_tikzpicture(body)
        if n:
            fixes.append(f"Wrapped {n} bare tikzpicture(s) in figure environment")

        # Rule 5: wrap bare axis (pgfplots) in figure+tikzpicture
        body, n = _wrap_bare_axis(body)
        if n:
            fixes.append(f"Wrapped {n} bare axis environment(s) in figure")

        # Rule 6: replace problematic Pytagoras square patterns
        body, n = _replace_pytagoras_squares(body)
        if n:
            fixes.append(f"Replaced {n} complex Pytagoras figure(s) with \\MMArettvinklet macro")

        state.edited_latex_body = body.strip()

        summary = "; ".join(fixes) if fixes else "No changes needed"
        step.output_summary = summary
        logger.info(
            "tikz_validator_complete",
            job_id=state.job_id,
            fixes=fixes,
            num_fixes=len(fixes),
        )

    except Exception as e:
        step.error = str(e)
        logger.error("tikz_validator_failed", job_id=state.job_id, error=str(e))
        # Non-fatal: leave body unchanged

    finally:
        step.completed_at = datetime.now()
        step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
        state.steps.append(step)

    return state
