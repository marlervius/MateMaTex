"""Tests for the LaTeX fixer agent's deterministic fast path."""

from app.models.state import GenerationRequest, LatexCompilationResult, PipelineState
from app.pipeline.agents.latex_fixer import run_latex_fixer


def test_rule_based_fix_completes_without_error():
    """An unclosed environment is repaired without an LLM call and without a step error."""
    doc = (
        "\\documentclass{article}\n\\begin{document}\n"
        "\\begin{itemize}\n\\item $x^2$\n"
        "\\end{document}\n"
    )
    state = PipelineState(
        request=GenerationRequest(grade="VG1 1T", topic="Algebra"),
        full_document=doc,
        latex_compilation=LatexCompilationResult(success=False, errors=["Missing \\end{itemize}"]),
    )

    result = run_latex_fixer(state)

    step = result.steps[-1]
    assert not step.error
    assert step.output_summary == "Rettet med regler (uten LLM)"
    assert "\\end{itemize}" in result.full_document
    assert result.edited_latex_body.endswith("\\end{itemize}")
