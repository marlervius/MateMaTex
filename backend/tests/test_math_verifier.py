"""
Tests for the SymPy-based math verification engine.

These tests ensure that the math checker correctly identifies:
- Correct equations
- Incorrect equations
- Correct solutions
- Incorrect solutions
"""

import pytest

from app.verification.math_checker import MathChecker


@pytest.fixture
def checker():
    return MathChecker()


# ---------------------------------------------------------------------------
# Equation verification
# ---------------------------------------------------------------------------
class TestEquationVerification:
    """Test verification of mathematical equations."""

    def test_correct_simple_equation(self, checker: MathChecker):
        """Simple arithmetic: 2 + 3 = 5."""
        latex = r"Summen er $2 + 3 = 5$."
        result = checker.verify(latex)
        assert result.claims_incorrect == 0

    def test_incorrect_simple_equation(self, checker: MathChecker):
        """Simple arithmetic error: 2 + 3 = 6."""
        latex = r"Summen er $2 + 3 = 6$."
        result = checker.verify(latex)
        assert result.claims_incorrect > 0

    def test_correct_fraction(self, checker: MathChecker):
        """Fraction: 6/3 = 2."""
        latex = r"Vi får $\frac{6}{3} = 2$."
        result = checker.verify(latex)
        assert result.claims_incorrect == 0

    def test_incorrect_fraction(self, checker: MathChecker):
        """Fraction error: 6/4 = 2."""
        latex = r"Vi forenkler: $\frac{6}{4} = 2$."
        result = checker.verify(latex)
        assert result.claims_incorrect > 0

    def test_correct_multiplication(self, checker: MathChecker):
        """Multiplication: 3 * 4 = 12."""
        latex = r"Produktet er $3 \cdot 4 = 12$."
        result = checker.verify(latex)
        assert result.claims_incorrect == 0

    def test_correct_negative_numbers(self, checker: MathChecker):
        """Negative: -3 + 8 = 5."""
        latex = r"Vi regner ut $-3 + 8 = 5$."
        result = checker.verify(latex)
        assert result.claims_incorrect == 0

    def test_correct_square_root(self, checker: MathChecker):
        """Square root: sqrt(9) = 3."""
        latex = r"Vi får $\sqrt{9} = 3$."
        result = checker.verify(latex)
        assert result.claims_incorrect == 0


class TestMultipleEquations:
    """Test documents with multiple equations."""

    def test_all_correct(self, checker: MathChecker):
        """Multiple correct equations."""
        latex = r"""
        Vi regner ut:
        $2 + 3 = 5$
        $10 - 4 = 6$
        $3 \cdot 7 = 21$
        """
        result = checker.verify(latex)
        assert result.claims_incorrect == 0

    def test_one_error_among_correct(self, checker: MathChecker):
        """One error among several correct equations."""
        latex = r"""
        Vi regner ut:
        $2 + 3 = 5$
        $10 - 4 = 7$
        $3 \cdot 7 = 21$
        """
        result = checker.verify(latex)
        assert result.claims_incorrect >= 1
        # The error should be the second equation
        errors = result.errors
        assert any("10" in e.latex_expression or "7" in e.latex_expression for e in errors)


class TestSolutionVerification:
    """Test verification of exercise solutions."""

    def test_correct_linear_solution(self, checker: MathChecker):
        """Verify that x=3 satisfies 2x+1=7."""
        latex = r"""
        \begin{taskbox}{Oppgave 1}
        Løs likningen $2x + 1 = 7$.
        \end{taskbox}

        \section*{Løsningsforslag}
        \textbf{Oppgave 1}\\
        a) $x = 3$
        """
        result = checker.verify(latex)
        # Should find and verify the solution
        assert result.claims_checked > 0


class TestEdgeCases:
    """Test edge cases and robustness."""

    def test_empty_content(self, checker: MathChecker):
        """Empty content should not crash."""
        result = checker.verify("")
        assert result.claims_checked == 0
        assert result.all_correct is True  # Vacuously true

    def test_no_math(self, checker: MathChecker):
        """Content without math should not crash."""
        latex = r"""
        \title{En tittel}
        \section{Introduksjon}
        Dette er en tekst uten matematikk.
        """
        result = checker.verify(latex)
        assert result.claims_checked == 0

    def test_unparseable_expression(self, checker: MathChecker):
        """Unparseable expressions should be counted but not block."""
        latex = r"Vi har $\mathbb{R} \setminus \{0\} = \text{noe rart}$."
        result = checker.verify(latex)
        # Should handle gracefully
        assert result.claims_incorrect == 0  # Can't verify ≠ incorrect

    def test_definition_skipped(self, checker: MathChecker):
        """Definitions like f(x) = 2x+1 should be skipped (not verifiable)."""
        latex = r"La $f(x) = 2x + 1$ være en funksjon."
        result = checker.verify(latex)
        # Definitions should be ignored
        assert result.claims_incorrect == 0
