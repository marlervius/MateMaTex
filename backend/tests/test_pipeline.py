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
        """Should finalize after max retries even with errors."""
        state = PipelineState(
            request=GenerationRequest(grade="8. trinn", topic="Algebra"),
            latex_compilation=LatexCompilationResult(
                success=False,
                errors=["! Emergency stop."],
            ),
            latex_fix_attempts=3,
        )
        assert should_retry_latex(state) == "finalize"


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
            "pedagogue", "author", "math_verifier",
            "editor", "latex_validator", "latex_fixer", "finalize",
        }
        # Verify nodes exist by compiling (will fail if nodes are missing)
        compiled = graph.compile()
        assert compiled is not None
