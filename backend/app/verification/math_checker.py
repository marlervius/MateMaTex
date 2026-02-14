"""
SymPy-based mathematical verification engine.

Extracts mathematical claims from LaTeX and verifies them programmatically.
This is NOT an LLM — it is a symbolic computation engine that catches
arithmetic errors, incorrect solutions, and invalid equations.
"""

from __future__ import annotations

import re
import signal
import structlog
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from sympy import (
    Eq,
    Float,
    Rational,
    S,
    Symbol,
    simplify,
    solve,
    sqrt,
    sympify,
    oo,
)
from sympy.parsing.latex import parse_latex

from app.models.state import MathClaim, VerificationResult

logger = structlog.get_logger()

# Timeout per individual claim verification (seconds)
_CLAIM_TIMEOUT = 5
# Timeout for the entire verification pass (seconds)
_TOTAL_TIMEOUT = 60
_executor = ThreadPoolExecutor(max_workers=2)


class MathChecker:
    """
    Extracts and verifies mathematical claims from LaTeX content.

    Supports:
    - Equation verification (LHS = RHS)
    - Solution verification (check that x=a satisfies the original equation)
    - Arithmetic computations (2 + 3 = 5)
    - Fraction/root simplification
    """

    # Patterns to extract mathematical claims from LaTeX
    _EQUATION_PATTERNS = [
        # Standalone equation: $expr = expr$
        re.compile(r'\$([^$]+?)\s*=\s*([^$]+?)\$'),
        # Display equation: \[ expr = expr \]
        re.compile(r'\\\[([^\\]+?)\s*=\s*([^\\]+?)\\\]'),
        # align environment lines: expr &= expr \\
        re.compile(r'([^&\\]+?)\s*&=\s*([^\\]+?)\\\\'),
    ]

    # Pattern for "Oppgave N ... fasit: answer" or solution blocks
    _SOLUTION_PATTERNS = [
        # a) $x = 3$  or  a) x = 3
        re.compile(r'[a-z]\)\s*\$?\\?x\s*=\s*([^$\\\n,]+)\$?'),
    ]

    # Patterns to find equations inside taskbox environments
    _TASK_EQUATION_PATTERN = re.compile(
        r'\\begin\{taskbox\}\{([^}]*)\}(.*?)\\end\{taskbox\}',
        re.DOTALL,
    )

    _SOLUTION_SECTION_PATTERN = re.compile(
        r'\\section\*\{Løsningsforslag\}(.*?)(?:\\section|\Z)',
        re.DOTALL,
    )

    def verify(self, latex_content: str) -> VerificationResult:
        """
        Run full mathematical verification on the LaTeX content.

        Returns a VerificationResult with details on every claim checked.
        Each claim has a per-claim timeout to prevent SymPy from hanging
        on complex expressions.
        """
        claims = self._extract_claims(latex_content)
        result = VerificationResult()
        result.claims_checked = len(claims)

        import time
        start_time = time.monotonic()

        for claim in claims:
            # Check total timeout
            if time.monotonic() - start_time > _TOTAL_TIMEOUT:
                logger.warning("math_verification_total_timeout", checked_so_far=result.claims_correct + result.claims_incorrect + result.claims_unparseable)
                break

            # Run each claim with a timeout to prevent SymPy hangs
            try:
                future = _executor.submit(self._verify_claim, claim)
                future.result(timeout=_CLAIM_TIMEOUT)
            except FuturesTimeoutError:
                claim.is_correct = None
                claim.error_message = f"Verification timed out ({_CLAIM_TIMEOUT}s)"
                logger.debug("claim_timeout", claim=claim.latex_expression[:60])
            except Exception as e:
                claim.is_correct = None
                claim.error_message = f"Verification error: {e}"

            if claim.is_correct is True:
                result.claims_correct += 1
            elif claim.is_correct is False:
                result.claims_incorrect += 1
                result.errors.append(claim)
            else:
                result.claims_unparseable += 1

        result.all_correct = result.claims_incorrect == 0
        result.summary = (
            f"Checked {result.claims_checked} claims: "
            f"{result.claims_correct} correct, "
            f"{result.claims_incorrect} incorrect, "
            f"{result.claims_unparseable} unparseable."
        )

        logger.info(
            "math_verification_complete",
            checked=result.claims_checked,
            correct=result.claims_correct,
            incorrect=result.claims_incorrect,
            unparseable=result.claims_unparseable,
            duration=round(time.monotonic() - start_time, 1),
        )

        return result

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------
    def _extract_claims(self, latex_content: str) -> list[MathClaim]:
        """Extract verifiable mathematical claims from the LaTeX."""
        claims: list[MathClaim] = []

        # 1. Extract equation claims (a = b style)
        claims.extend(self._extract_equation_claims(latex_content))

        # 2. Extract solution claims (match exercises with their solutions)
        claims.extend(self._extract_solution_claims(latex_content))

        return claims

    def _extract_equation_claims(self, content: str) -> list[MathClaim]:
        """Extract 'LHS = RHS' equations from inline/display math."""
        claims: list[MathClaim] = []

        for pattern in self._EQUATION_PATTERNS:
            for match in pattern.finditer(content):
                lhs_raw = match.group(1).strip()
                rhs_raw = match.group(2).strip()

                # Skip trivial definitions (x = ...) with no computation
                if self._is_definition(lhs_raw, rhs_raw):
                    continue

                claim = MathClaim(
                    latex_expression=f"{lhs_raw} = {rhs_raw}",
                    claim_type="equation",
                    context=content[max(0, match.start() - 40):match.end() + 40],
                )
                claims.append(claim)

        return claims

    def _extract_solution_claims(self, content: str) -> list[MathClaim]:
        """
        Extract exercise-solution pairs and verify solutions are correct.

        Looks for exercises with equations and matches them to solutions.
        """
        claims: list[MathClaim] = []

        # Find the solution section
        sol_match = self._SOLUTION_SECTION_PATTERN.search(content)
        if not sol_match:
            return claims

        solution_text = sol_match.group(1)

        # Extract tasks and their equations
        for task_match in self._TASK_EQUATION_PATTERN.finditer(content):
            task_title = task_match.group(1)
            task_body = task_match.group(2)

            # Find equations in the task (e.g., "Løs likningen $2x + 3 = 7$")
            equations_in_task = re.findall(r'\$([^$]*?[=<>][^$]*?)\$', task_body)

            # Find the corresponding solution
            task_num = re.search(r'(\d+)', task_title)
            if task_num:
                sol_pattern = re.compile(
                    rf'\\textbf\{{Oppgave\s*{task_num.group(1)}\}}(.*?)(?=\\textbf|$)',
                    re.DOTALL,
                )
                sol_match_task = sol_pattern.search(solution_text)
                if sol_match_task:
                    sol_text = sol_match_task.group(1)

                    # For each sub-answer (a), b), etc.)
                    sub_answers = re.findall(
                        r'([a-z])\)\s*\$?([^$\n,]+?)\$?(?:\s|\\|$)',
                        sol_text,
                    )
                    for sub_letter, answer in sub_answers:
                        if '=' in answer:
                            claim = MathClaim(
                                latex_expression=answer.strip(),
                                claim_type="solution",
                                context=f"Oppgave {task_num.group(1)}{sub_letter}): equations={equations_in_task}",
                            )
                            claims.append(claim)

        return claims

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------
    def _verify_claim(self, claim: MathClaim) -> None:
        """Verify a single mathematical claim using SymPy."""
        try:
            if claim.claim_type == "equation":
                self._verify_equation(claim)
            elif claim.claim_type == "solution":
                self._verify_solution(claim)
            else:
                self._verify_equation(claim)
        except Exception as e:
            claim.is_correct = None
            claim.error_message = f"Verification failed: {e}"
            logger.debug(
                "claim_verification_error",
                claim=claim.latex_expression,
                error=str(e),
            )

    def _verify_equation(self, claim: MathClaim) -> None:
        """Verify that LHS = RHS symbolically."""
        expr_str = claim.latex_expression

        if '=' not in expr_str:
            claim.is_correct = None
            claim.error_message = "No equality found"
            return

        parts = expr_str.split('=', 1)
        lhs_latex = parts[0].strip()
        rhs_latex = parts[1].strip()

        try:
            lhs = self._parse_latex_expr(lhs_latex)
            rhs = self._parse_latex_expr(rhs_latex)
        except Exception as e:
            claim.is_correct = None
            claim.error_message = f"Parse error: {e}"
            return

        if lhs is None or rhs is None:
            claim.is_correct = None
            claim.error_message = "Could not parse one or both sides"
            return

        # Check symbolic equality
        try:
            diff = simplify(lhs - rhs)
            claim.expected_result = str(rhs)
            claim.actual_result = str(simplify(lhs))

            if diff == 0:
                claim.is_correct = True
            elif abs(complex(diff)) < 1e-10:
                claim.is_correct = True  # Numerically equal
            else:
                claim.is_correct = False
                claim.error_message = (
                    f"LHS ({simplify(lhs)}) ≠ RHS ({simplify(rhs)}), "
                    f"difference = {diff}"
                )
        except (TypeError, ValueError):
            # Can't evaluate numerically — try symbolic
            try:
                claim.is_correct = bool(Eq(lhs, rhs))
            except Exception:
                claim.is_correct = None
                claim.error_message = "Could not determine equality"

    def _verify_solution(self, claim: MathClaim) -> None:
        """
        Verify a solution claim like 'x = 3' against its equation context.
        """
        # Extract variable and value from the solution
        sol_match = re.match(r'\\?([a-z])\s*=\s*(.+)', claim.latex_expression.strip())
        if not sol_match:
            claim.is_correct = None
            claim.error_message = "Could not parse solution format"
            return

        var_name = sol_match.group(1)
        value_str = sol_match.group(2).strip()

        try:
            value = self._parse_latex_expr(value_str)
        except Exception:
            claim.is_correct = None
            claim.error_message = f"Could not parse solution value: {value_str}"
            return

        # Try to find and parse the original equation from context
        eq_strs = re.findall(r"equations=\['([^']+)'\]", claim.context)
        if not eq_strs:
            eq_strs = re.findall(r'equations=\["([^"]+)"\]', claim.context)

        if not eq_strs:
            claim.is_correct = None
            claim.error_message = "No equation found in context to verify against"
            return

        var = Symbol(var_name)

        for eq_str in eq_strs:
            if '=' not in eq_str:
                continue

            parts = eq_str.split('=', 1)
            try:
                lhs = self._parse_latex_expr(parts[0].strip())
                rhs = self._parse_latex_expr(parts[1].strip())
            except Exception:
                continue

            if lhs is None or rhs is None:
                continue

            # Substitute the claimed solution
            try:
                diff = simplify((lhs - rhs).subs(var, value))
                if diff == 0:
                    claim.is_correct = True
                    return
                elif abs(complex(diff)) < 1e-10:
                    claim.is_correct = True
                    return
                else:
                    # Compute actual solution for error message
                    actual = solve(Eq(lhs, rhs), var)
                    claim.is_correct = False
                    claim.expected_result = str(actual)
                    claim.actual_result = str(value)
                    claim.error_message = (
                        f"Substituting {var_name}={value} gives difference={diff}. "
                        f"Actual solution(s): {actual}"
                    )
                    return
            except Exception:
                continue

        claim.is_correct = None
        claim.error_message = "Could not verify against any equation"

    # ------------------------------------------------------------------
    # LaTeX → SymPy parsing
    # ------------------------------------------------------------------
    def _parse_latex_expr(self, latex_expr: str):
        """
        Parse a LaTeX math expression into a SymPy expression.
        Uses sympy.parsing.latex.parse_latex with fallback to manual parsing.
        """
        # Clean the expression
        expr = latex_expr.strip()
        expr = expr.replace('\\,', '')
        expr = expr.replace('\\;', '')
        expr = expr.replace('\\!', '')
        expr = expr.replace('\\text{', '').rstrip('}')

        # Try sympy's LaTeX parser first
        try:
            return parse_latex(expr)
        except Exception:
            pass

        # Fallback: manual conversion for common patterns
        return self._manual_parse(expr)

    def _manual_parse(self, expr: str):
        """Manual fallback parser for common LaTeX math patterns."""
        s = expr

        # \frac{a}{b} → (a)/(b)
        while '\\frac' in s:
            s = re.sub(
                r'\\frac\{([^{}]+)\}\{([^{}]+)\}',
                r'((\1)/(\2))',
                s,
            )

        # \sqrt{x} → sqrt(x)
        s = re.sub(r'\\sqrt\{([^{}]+)\}', r'sqrt(\1)', s)

        # \cdot → *
        s = s.replace('\\cdot', '*')
        s = s.replace('\\times', '*')
        s = s.replace('\\div', '/')

        # Clean remaining LaTeX
        s = s.replace('\\left', '').replace('\\right', '')
        s = s.replace('\\', '')
        s = s.replace('^', '**')

        try:
            return sympify(s)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _is_definition(lhs: str, rhs: str) -> bool:
        """Check if this is a variable definition rather than a verifiable claim."""
        # Single variable = expression is usually a definition (e.g., f(x) = 2x+1)
        if re.match(r'^[a-zA-Z]\(?[a-z]?\)?$', lhs.strip()):
            return True
        return False


def format_errors_for_agent(result: VerificationResult) -> str:
    """Format verification errors into instructions for the author agent to fix."""
    if result.all_correct:
        return ""

    lines = [
        "=== MATEMATISKE FEIL FUNNET ===",
        f"SymPy fant {result.claims_incorrect} feil av {result.claims_checked} sjekket.\n",
    ]

    for i, err in enumerate(result.errors, 1):
        lines.append(f"FEIL {i}:")
        lines.append(f"  Uttrykk: {err.latex_expression}")
        lines.append(f"  Type: {err.claim_type}")
        if err.expected_result:
            lines.append(f"  Forventet: {err.expected_result}")
        if err.actual_result:
            lines.append(f"  Faktisk: {err.actual_result}")
        lines.append(f"  Detalj: {err.error_message}")
        lines.append(f"  Kontekst: ...{err.context}...")
        lines.append("")

    lines.append("RETT ALLE FEILENE OVER og returner hele dokumentet med korreksjoner.")
    return "\n".join(lines)
