"""
Integration tests for the LangGraph pipeline.

Tests the pipeline graph structure and routing logic.
"""

import pytest

from app.models.state import (
    GenerationRequest,
    LatexCompilationResult,
    PipelineState,
    PipelineStatus,
    VerificationResult,
)
from app.pipeline.graph import (
    create_pipeline,
    finalize,
    should_retry_latex,
    should_retry_math,
)


# ---------------------------------------------------------------------------
# Routing logic tests
# ---------------------------------------------------------------------------
class TestMathRetryRouting:
    """Test the math verification retry routing logic."""

    def test_retry_on_errors(self):
        """Should retry author when math errors exist and attempts remain."""
        state = PipelineState(
            request=GenerationRequest(grade="8. trinn", topic="Algebra"),
            math_verification=VerificationResult(
                claims_checked=5,
                claims_incorrect=2,
                all_correct=False,
            ),
            math_verification_attempts=1,
        )
        assert should_retry_math(state) == "author"

    def test_proceed_when_correct(self):
        """Should proceed to editor when all math is correct."""
        state = PipelineState(
            request=GenerationRequest(grade="8. trinn", topic="Algebra"),
            math_verification=VerificationResult(
                claims_checked=5,
                claims_correct=5,
                claims_incorrect=0,
                all_correct=True,
            ),
            math_verification_attempts=1,
        )
        assert should_retry_math(state) == "editor"

    def test_proceed_after_max_retries(self):
        """Should proceed to editor after max retries even with errors."""
        state = PipelineState(
            request=GenerationRequest(grade="8. trinn", topic="Algebra"),
            math_verification=VerificationResult(
                claims_checked=5,
                claims_incorrect=2,
                all_correct=False,
            ),
            math_verification_attempts=3,  # At max
        )
        assert should_retry_math(state) == "editor"

    def test_skip_retry_when_mostly_unparseable(self):
        """Few SymPy errors among many unparseable claims should not re-run author."""
        state = PipelineState(
            request=GenerationRequest(grade="8. trinn", topic="Algebra"),
            math_verification=VerificationResult(
                claims_checked=69,
                claims_incorrect=3,
                claims_unparseable=66,
                all_correct=False,
            ),
            math_verification_attempts=1,
        )
        assert should_retry_math(state) == "editor"


class TestLatexRetryRouting:
    """Test the LaTeX validation retry routing logic."""

    def test_retry_on_compilation_failure(self):
        """Should retry with fixer when compilation fails and attempts remain."""
        state = PipelineState(
            request=GenerationRequest(grade="8. trinn", topic="Algebra"),
            latex_compilation=LatexCompilationResult(
                success=False,
                errors=["! Undefined control sequence."],
            ),
            latex_fix_attempts=1,
        )
        assert should_retry_latex(state) == "latex_fixer"

    def test_proceed_when_compiled(self):
        """Should finalize when compilation succeeds."""
        state = PipelineState(
            request=GenerationRequest(grade="8. trinn", topic="Algebra"),
            latex_compilation=LatexCompilationResult(success=True),
            latex_fix_attempts=1,
        )
        assert should_retry_latex(state) == "finalize"

    def test_proceed_after_max_retries(self):
        """Should use latex_fallback after max fixer retries when still failing."""
        state = PipelineState(
            request=GenerationRequest(grade="8. trinn", topic="Algebra"),
            latex_compilation=LatexCompilationResult(
                success=False,
                errors=["! Emergency stop."],
            ),
            latex_fix_attempts=3,
        )
        assert should_retry_latex(state) == "latex_fallback"


class TestFinalizeStatus:
    """Test final status reflects math verification quality."""

    def test_completed_with_warnings_when_math_issues(self):
        state = PipelineState(
            request=GenerationRequest(grade="8. trinn", topic="Algebra"),
            raw_latex_body="\\title{T}\\maketitle",
            math_verification=VerificationResult(
                claims_checked=3,
                claims_incorrect=1,
                claims_unparseable=0,
                all_correct=False,
            ),
        )
        result = finalize(state)
        assert result.status == PipelineStatus.COMPLETED_WITH_WARNINGS

    def test_completed_when_math_clean(self):
        state = PipelineState(
            request=GenerationRequest(grade="8. trinn", topic="Algebra"),
            raw_latex_body="\\title{T}\\maketitle",
            math_verification=VerificationResult(
                claims_checked=3,
                claims_correct=3,
                all_correct=True,
            ),
        )
        result = finalize(state)
        assert result.status == PipelineStatus.COMPLETED


class TestGraphStructure:
    """Test that the graph is constructed correctly."""

    def test_graph_compiles(self):
        """The graph should compile without errors."""
        graph = create_pipeline()
        compiled = graph.compile()
        assert compiled is not None

    def test_graph_has_all_nodes(self):
        """The graph should have all expected nodes."""
        graph = create_pipeline()
        # LangGraph stores nodes internally
        expected_nodes = {
            "pedagogue",
            "author",
            "math_verifier",
            "editor",
            "tikz_validator",
            "table_validator",
            "latex_validator",
            "latex_fixer",
            "latex_fallback",
            "finalize",
        }
        assert set(graph.nodes.keys()) == expected_nodes
        compiled = graph.compile()
        assert compiled is not None
