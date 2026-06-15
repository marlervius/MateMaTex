"""
Rule-based content quality gate for kapittel (and light checks for other types).

Scores pedagogical completeness: curriculum coverage, examples, graphs,
explore/analyze/draw (LK20), and off-topic guards.
"""

from __future__ import annotations

import re
from typing import Literal

from app.curriculum.topic_coverage import (
    get_topic_coverage_spec,
    keywords_for_subtopic,
)
from app.models.state import ContentQualityIssue, ContentQualityReport, GenerationRequest
def _count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE))


def _has_any(text_lower: str, keywords: list[str]) -> bool:
    return any(kw.lower() in text_lower for kw in keywords)


def _subtopic_covered(text_lower: str, subtopic: str) -> bool:
    return _has_any(text_lower, keywords_for_subtopic(subtopic))


def evaluate_content_quality(
    latex_body: str,
    request: GenerationRequest,
) -> ContentQualityReport:
    """
    Evaluate LaTeX body. Strict for material_type=kapittel; lenient otherwise.
    """
    body = latex_body or ""
    text_lower = body.lower()
    spec = get_topic_coverage_spec(
        request.grade,
        request.topic,
        material_type=request.material_type,
        num_exercises=request.num_exercises,
        competency_goals=request.competency_goals,
    )

    issues: list[ContentQualityIssue] = []
    missing_subtopics: list[str] = []

    section_count = _count_pattern(body, r"\\section\*?\{")
    example_count = _count_pattern(body, r"\\begin\{eksempel\}")
    graph_count = _count_pattern(body, r"\\begin\{axis\}") + _count_pattern(
        body, r"\\begin\{tikzpicture\}"
    )
    exercise_count = _count_pattern(body, r"\\begin\{taskbox\}")
    if exercise_count == 0:
        exercise_count = _count_pattern(body, r"\\textbf\{Oppgave\s+\d+")
    body_chars = len(body)

    report = ContentQualityReport(
        section_count=section_count,
        example_count=example_count,
        graph_count=graph_count,
        exercise_count=exercise_count,
        body_chars=body_chars,
    )

    if request.material_type != "kapittel":
        report.passed = True
        report.score = 100
        return report

    # --- Off-topic guards ---
    for pattern in spec.forbidden_section_patterns:
        if re.search(pattern, body):
            issues.append(
                ContentQualityIssue(
                    code="off_topic_section",
                    message=f"Urelatert seksjon funnet (mønster: {pattern})",
                )
            )

    for kw in spec.forbidden_body_keywords:
        hits = text_lower.count(kw.lower())
        if hits >= 2:
            issues.append(
                ContentQualityIssue(
                    code="off_topic_content",
                    message=f"Urelatert innhold «{kw}» forekommer {hits} ganger",
                )
            )

    # --- Subtopic coverage ---
    for sub in spec.required_subtopics:
        if not _subtopic_covered(text_lower, sub):
            missing_subtopics.append(sub)
            issues.append(
                ContentQualityIssue(
                    code="missing_subtopic",
                    message=f"Mangler deltema: {sub}",
                )
            )
    report.missing_subtopics = missing_subtopics

    # --- Structure minimums ---
    if section_count < spec.min_theory_sections:
        issues.append(
            ContentQualityIssue(
                code="few_sections",
                message=(
                    f"For få seksjoner: {section_count} "
                    f"(krav: {spec.min_theory_sections}+)"
                ),
            )
        )

    if request.include_examples and example_count < spec.min_examples:
        issues.append(
            ContentQualityIssue(
                code="few_examples",
                message=(
                    f"For få eksempler: {example_count} "
                    f"(krav: {spec.min_examples}+)"
                ),
            )
        )

    if request.include_graphs and graph_count < spec.min_graphs:
        issues.append(
            ContentQualityIssue(
                code="few_graphs",
                message=(
                    f"For få grafer: {graph_count} (krav: {spec.min_graphs}+)"
                ),
            )
        )

    if body_chars < spec.min_body_chars:
        issues.append(
            ContentQualityIssue(
                code="thin_content",
                message=(
                    f"For kort innhold: {body_chars} tegn "
                    f"(krav: {spec.min_body_chars}+)"
                ),
            )
        )

    if not re.search(r"\\begin\{laeringsmaal\}", body):
        issues.append(
            ContentQualityIssue(
                code="missing_laeringsmaal",
                message="Mangler \\begin{laeringsmaal}",
            )
        )

    if not re.search(r"\\begin\{oppsummering\}", body):
        issues.append(
            ContentQualityIssue(
                code="missing_oppsummering",
                message="Mangler \\begin{oppsummering}",
            )
        )

    if _count_pattern(body, r"\\begin\{utforsk\}") < 1:
        issues.append(
            ContentQualityIssue(
                code="missing_utforsk",
                message="Mangler \\begin{utforsk} (LK20: utforske)",
            )
        )

    if _count_pattern(body, r"\\begin\{vanligfeil\}") < 2:
        issues.append(
            ContentQualityIssue(
                code="few_vanligfeil",
                message="Minst 2 \\begin{vanligfeil} kreves",
            )
        )

    if _count_pattern(body, r"\\begin\{definisjon\}") < 3:
        issues.append(
            ContentQualityIssue(
                code="few_definisjoner",
                message="Minst 3 \\begin{definisjon} kreves",
            )
        )

    # Representations: table, graph, formula
    has_table = "tabell" in text_lower or "\\begin{tabular}" in body
    has_graph = graph_count > 0 or "graf" in text_lower
    has_formula = "formel" in text_lower or "f(x)" in text_lower
    if not (has_table and has_graph and has_formula):
        issues.append(
            ContentQualityIssue(
                code="missing_representations",
                message=(
                    "Mangler kobling mellom representasjoner "
                    f"(tabell={has_table}, graf={has_graph}, formel={has_formula})"
                ),
            )
        )

    # Analyze / discuss
    if not _has_any(text_lower, ["analys", "drøft", "egenskap", "tolke"]):
        issues.append(
            ContentQualityIssue(
                code="missing_analysis",
                message="Mangler analyse/drøfting av funksjonsegenskaper",
            )
        )

    if request.include_exercises and exercise_count < spec.min_exercises:
        issues.append(
            ContentQualityIssue(
                code="few_exercises",
                message=(
                    f"For få oppgaver: {exercise_count} "
                    f"(krav: {spec.min_exercises})"
                ),
            )
        )

    if not re.search(r"\\section\*?\{[^}]*[Oo]ppgav", body):
        issues.append(
            ContentQualityIssue(
                code="missing_exercise_section",
                message="Mangler \\section{Oppgaver} til slutt",
            )
        )

    # --- Score ---
    error_count = sum(1 for i in issues if i.severity == "error")
    max_checks = max(
        12,
        len(spec.required_subtopics) + 10,
    )
    penalty = min(100, error_count * (100 // max_checks))
    report.score = max(0, 100 - penalty)
    report.issues = issues
    report.passed = error_count == 0 and report.score >= 90
    return report


def format_quality_report_for_author(report: ContentQualityReport) -> str:
    """Format issues as instructions for an author retry."""
    if report.passed:
        return "Ingen kvalitetsproblemer."

    lines = [
        "KVALITETSGATE — følgende MÅ rettes før dokumentet godkjennes:",
        f"Score: {report.score}/100",
        "",
    ]
    for issue in report.issues:
        lines.append(f"- [{issue.code}] {issue.message}")

    if report.missing_subtopics:
        lines.append("")
        lines.append("MANGLENDE DELTEMAER (lag egen \\section med teori + 2 eksempler + graf for hver):")
        for sub in report.missing_subtopics:
            lines.append(f"  • {sub}")

    lines.extend(
        [
            "",
            "UTVID dokumentet — ikke bare legg til én setning. Skriv full teori,",
            "flere \\begin{eksempel} med \\forklaring{}, og fjern alt urelatert innhold.",
        ]
    )
    return "\n".join(lines)
