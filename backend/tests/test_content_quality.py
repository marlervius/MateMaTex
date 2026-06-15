"""
Tests for topic coverage specs and content quality gate.
"""

from app.curriculum.topic_coverage import (
    format_coverage_for_prompt,
    get_topic_coverage_spec,
    keywords_for_subtopic,
)
from app.models.state import GenerationRequest
from app.pipeline.graph import should_retry_content
from app.verification.content_quality import evaluate_content_quality

THIN_FUNKSJONER_LATEX = r"""
\title{Funksjoner og modeller}
\maketitle
\begin{laeringsmaal}
\begin{itemize}
\item Forstå funksjonsbegrepet.
\end{itemize}
\end{laeringsmaal}
\section{Funksjonsbegrepet og polynomfunksjoner}
\begin{definisjon}
En polynomfunksjon er $f(x)=a_n x^n + \cdots + a_0$.
\end{definisjon}
\begin{eksempel}[title={Nullpunkter}]
Finn nullpunktene til $f(x)=x^2-4$.
\end{eksempel}
\begin{axis}
\addplot {x^2-4};
\end{axis}
\section{Rasjonale funksjoner}
Vertikal asymptote der nevneren er null.
\begin{vanligfeil}
Grafen kan krysse horisontal asymptote.
\end{vanligfeil}
\section{Eksponentialfunksjoner}
$f(x)=a\cdot b^x$.
\begin{eksempel}[title={Log}]
Løs $2^x=10$ med logaritmer.
\end{eksempel}
\section{Vektorer i planet}
Skalarprodukt $\vec u\cdot\vec v$.
\section{Oppsummering}
\begin{oppsummering}
Eksponentialfunksjon $f(x)=a\cdot b^x$.
\end{oppsummering}
\section{Oppgaver}
\begin{taskbox}{Oppgave 1}
Finn nullpunkter.
\end{taskbox}
""" + "\n" * 50


def _build_passing_kapittel_latex() -> str:
    """Synthetic kapittel that satisfies the quality gate for VG1 1T Funksjoner."""
    sections = [
        (
            "Funksjonsbegrepet og representasjoner",
            "lineær funksjon tabell graf formel definisjonsmengde verdimengde",
            "x^2-1",
        ),
        ("Lineære funksjoner", "stigningstall konstantledd lineær", "2*x+1"),
        ("Andregradsfunksjoner", "andregrad parabel toppunkt nullpunkt", "x^2-4"),
        ("Polynomfunksjoner", "polynom graden til funksjonen", "x^3-x"),
        ("Rasjonale funksjoner", "rasjonal asymptot vertikal horisontal", "2/(x-1)"),
        (
            "Eksponentialfunksjoner og logaritmer",
            "eksponential vekstfaktor logaritm lg eksponentiallikning",
            "2^x",
        ),
        (
            "Logaritmeregler",
            "logaritmeregel lg(a lg a",
            "10^x",
        ),
    ]
    parts = [
        r"\title{Funksjoner}",
        r"\maketitle",
        r"\begin{laeringsmaal}",
        r"\begin{itemize}",
        r"\item Utforske, analysere og tegne funksjoner.",
        r"\end{itemize}",
        r"\end{laeringsmaal}",
        r"\begin{husk}Lineære funksjoner fra ungdomsskolen.\end{husk}",
        r"\begin{utforsk}Undersøk hvordan stigningstall endrer grafen.\end{utforsk}",
    ]
    for title, keywords, _formula in sections:
        parts.append(f"\\section{{{title}}}")
        parts.append(
            f"Vi analyserer og drøfter egenskaper. "
            f"Kobling mellom tabell, graf og formel. {keywords}."
        )
        for i in range(2):
            parts.append(
                f"\\begin{{definisjon}}\\textbf{{{title}}} — definisjon {i}."
                f" \\end{{definisjon}}"
            )
            parts.append(
                f"\\begin{{eksempel}}[title={{Eksempel {i+1}}}]\n"
                f"Løs med \\forklaring{{steg}}.\n\\end{{eksempel}}"
            )
        parts.append("\\begin{axis}[width=8cm,height=5cm]\n\\addplot {x};\n\\end{axis}")
        parts.append("\\begin{vanligfeil}Typisk feil: glemmer definisjonsmengde.\\end{vanligfeil}")
        parts.append("\\begin{vanligfeil}Typisk feil: blander asymptoter.\\end{vanligfeil}")
    parts.append("\\begin{oppsummering}Formler for alle funksjonstyper.\\end{oppsummering}")
    parts.append("\\section{Oppgaver}")
    for n in range(1, 11):
        parts.append(
            f"\\begin{{taskbox}}{{Oppgave {n}}}\n"
            f"Tegn grafen til en lineær funksjon og analyser nullpunkter.\n"
            f"\\end{{taskbox}}"
        )
    body = "\n".join(parts)
    body += "\n% " + ("utfylling " * 2500)
    return body


class TestTopicCoverage:
    def test_funksjoner_1t_resolves_category(self):
        spec = get_topic_coverage_spec("VG1 1T", "Funksjoner", material_type="kapittel")
        assert spec.category == "Funksjoner"
        assert "Lineære funksjoner" in spec.required_subtopics
        assert "Logaritmer" in spec.required_subtopics
        assert len(spec.required_subtopics) >= 6

    def test_funksjoner_1t_forbids_vectors(self):
        spec = get_topic_coverage_spec("VG1 1T", "Funksjoner 1T", material_type="kapittel")
        assert "skalarprodukt" in spec.forbidden_body_keywords

    def test_coverage_prompt_lists_subtopics(self):
        text = format_coverage_for_prompt(
            "VG1 1T",
            "Funksjoner",
            material_type="kapittel",
            competency_goals=["1T-03"],
        )
        assert "Lineære funksjoner" in text
        assert "vektorer" in text.lower()
        assert "utforsk" in text.lower()

    def test_keywords_for_subtopic(self):
        kws = keywords_for_subtopic("Andregradsfunksjoner")
        assert "andregrad" in kws or "parabel" in kws


class TestContentQuality:
    def test_thin_funksjoner_chapter_fails(self):
        req = GenerationRequest(
            grade="VG1 1T",
            topic="Funksjoner",
            material_type="kapittel",
            num_exercises=10,
            competency_goals=["1T-03: Utforske funksjoner"],
        )
        report = evaluate_content_quality(THIN_FUNKSJONER_LATEX, req)
        assert not report.passed
        assert report.score < 90
        codes = {i.code for i in report.issues}
        assert "missing_subtopic" in codes or "few_examples" in codes
        assert "off_topic_section" in codes or "off_topic_content" in codes

    def test_synthetic_complete_chapter_passes(self):
        req = GenerationRequest(
            grade="VG1 1T",
            topic="Funksjoner",
            material_type="kapittel",
            num_exercises=10,
        )
        body = _build_passing_kapittel_latex()
        report = evaluate_content_quality(body, req)
        assert report.passed, [i.message for i in report.issues]
        assert report.score >= 90

    def test_arbeidsark_always_passes(self):
        req = GenerationRequest(
            grade="VG1 1T",
            topic="Funksjoner",
            material_type="arbeidsark",
        )
        report = evaluate_content_quality("kort", req)
        assert report.passed


class TestContentQualityRouting:
    def test_retry_when_failing(self):
        from app.models.state import ContentQualityIssue, ContentQualityReport, PipelineState

        state = PipelineState(
            request=GenerationRequest(grade="VG1 1T", topic="Funksjoner", material_type="kapittel"),
            content_quality=ContentQualityReport(
                passed=False,
                score=40,
                issues=[
                    ContentQualityIssue(code="few_examples", message="x"),
                ],
            ),
            content_quality_attempts=0,
        )
        assert should_retry_content(state) == "author"

    def test_proceed_when_passed(self):
        from app.models.state import ContentQualityReport, PipelineState

        state = PipelineState(
            request=GenerationRequest(grade="VG1 1T", topic="Funksjoner", material_type="kapittel"),
            content_quality=ContentQualityReport(passed=True, score=100),
        )
        assert should_retry_content(state) == "tikz_validator"
