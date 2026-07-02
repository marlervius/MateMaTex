"""Streamlit-only curriculum helpers (not used by FastAPI pipeline)."""

from __future__ import annotations

from matematex_core.curriculum.lk20 import (
    COMPETENCY_GOALS,
    TOPIC_LIBRARY,
    get_competency_goals,
    get_topics_for_grade,
)

# Oppgavetyper
EXERCISE_TYPES = {
    "standard": {
        "name": "📝 Regneoppgaver",
        "description": "Klassiske oppgaver med beregninger",
        "instruction": "Lag tradisjonelle regneoppgaver med tydelig oppgavetekst og krav om utregning. Vis mellomregninger i løsningsforslaget."
    },
    "multiple_choice": {
        "name": "🔘 Flervalg",
        "description": "Oppgaver med svaralternativer A, B, C, D",
        "instruction": "Lag flervalgsoppgaver med 4 svaralternativer (A, B, C, D). Kun ett svar er riktig. Bruk \\begin{enumerate}[label=\\Alph*)] for alternativene. Inkluder distraktorer som tester vanlige feil."
    },
    "fill_blank": {
        "name": "📋 Utfylling",
        "description": "Fyll inn manglende tall/uttrykk",
        "instruction": "Lag utfyllingsoppgaver der eleven må fylle inn manglende tall eller uttrykk. Bruk \\underline{\\hspace{2cm}} for blanke felt. Oppgavene skal teste forståelse av konsepter."
    },
    "word_problem": {
        "name": "📖 Tekstoppgaver",
        "description": "Praktiske problemstillinger",
        "instruction": "Lag praktiske tekstoppgaver med hverdagslige situasjoner som krever matematisk modellering. Bruk norske navn og realistiske tall. Oppgavene skal kreve at eleven setter opp og løser likninger eller beregninger."
    },
    "true_false": {
        "name": "✓✗ Sant/Usant",
        "description": "Vurder om påstander er sanne",
        "instruction": "Lag sant/usant-påstander der eleven må avgjøre om matematiske utsagn er korrekte. Inkluder både sanne og usanne påstander. Krever begrunnelse i løsningsforslaget."
    },
    "matching": {
        "name": "🔗 Kobling",
        "description": "Match uttrykk med svar",
        "instruction": "Lag koblingsoppgaver der eleven må matche matematiske uttrykk i venstre kolonne med riktige svar i høyre kolonne. Bruk tabeller for oversiktlig layout."
    },
    "proof": {
        "name": "📐 Bevisoppgaver",
        "description": "Matematiske bevis og resonnementer",
        "instruction": "Lag oppgaver der eleven må bevise matematiske sammenhenger eller resonnere seg frem til løsningen. Krev tydelig argumentasjon og logisk oppbygging."
    },
    "graphical": {
        "name": "📊 Grafiske oppgaver",
        "description": "Tegne, lese av eller tolke grafer",
        "instruction": "Lag oppgaver som involverer grafer og figurer. Eleven kan bli bedt om å tegne grafer, lese av verdier, eller tolke grafiske fremstillinger. Inkluder koordinatsystem eller figur i oppgaven."
    },
    "open_ended": {
        "name": "💭 Åpne oppgaver",
        "description": "Utforskende oppgaver med flere løsninger",
        "instruction": "Lag åpne oppgaver der eleven kan utforske og finne flere mulige løsninger. Oppgavene skal stimulere til matematisk tenkning og kreativitet."
    },
}


# Tidsestimater for ulike materialtyper (minutter)
TIME_ESTIMATES = {
    "arbeidsark": {
        "base": 15,
        "per_exercise": 3,
        "theory_multiplier": 1.0,
        "examples_multiplier": 1.2,
    },
    "kapittel": {
        "base": 45,
        "per_exercise": 5,
        "theory_multiplier": 1.5,
        "examples_multiplier": 1.3,
    },
    "prøve": {
        "base": 20,
        "per_exercise": 4,
        "theory_multiplier": 1.0,
        "examples_multiplier": 1.0,
    },
    "lekseark": {
        "base": 10,
        "per_exercise": 2,
        "theory_multiplier": 1.0,
        "examples_multiplier": 1.1,
    },
}


def get_all_topics_flat(grade: str) -> list:
    """Get a flat list of all topics for a grade."""
    topics = get_topics_for_grade(grade)
    flat_list = []
    for category, topic_list in topics.items():
        flat_list.extend(topic_list)
    return flat_list


def get_exercise_types() -> dict:
    """Get all available exercise types."""
    return EXERCISE_TYPES


def estimate_generation_time(
    material_type: str,
    num_exercises: int = 10,
    include_theory: bool = True,
    include_examples: bool = True,
    include_graphs: bool = True
) -> tuple[int, int]:
    """
    Estimate generation time in minutes.
    
    Args:
        material_type: Type of material (arbeidsark, kapittel, etc.)
        num_exercises: Number of exercises to generate.
        include_theory: Whether theory is included.
        include_examples: Whether examples are included.
        include_graphs: Whether graphs are included.
    
    Returns:
        Tuple of (min_minutes, max_minutes).
    """
    estimates = TIME_ESTIMATES.get(material_type, TIME_ESTIMATES["arbeidsark"])
    
    base = estimates["base"]
    exercise_time = estimates["per_exercise"] * num_exercises
    
    total = base + exercise_time
    
    if include_theory:
        total *= estimates["theory_multiplier"]
    if include_examples:
        total *= estimates["examples_multiplier"]
    if include_graphs:
        total *= 1.2  # Graphs add complexity
    
    # Add some variance
    min_time = int(total * 0.7)
    max_time = int(total * 1.3)
    
    return (max(2, min_time), max(3, max_time))


def search_topics(query: str, grade: str = None) -> list[dict]:
    """
    Search for topics matching a query.
    
    Args:
        query: Search query string.
        grade: Optional grade to filter by.
    
    Returns:
        List of matching topics with their grade and category.
    """
    results = []
    query_lower = query.lower()
    
    grades_to_search = [grade] if grade else TOPIC_LIBRARY.keys()
    
    for g in grades_to_search:
        if g not in TOPIC_LIBRARY:
            continue
        
        for category, topics in TOPIC_LIBRARY[g].items():
            for topic in topics:
                if query_lower in topic.lower() or query_lower in category.lower():
                    results.append({
                        "topic": topic,
                        "category": category,
                        "grade": g,
                    })
    
    return results


def get_related_topics(topic: str, grade: str) -> list[str]:
    """
    Get topics related to the given topic within the same grade.
    
    Args:
        topic: The topic to find related topics for.
        grade: The grade level.
    
    Returns:
        List of related topic names.
    """
    topics_by_category = get_topics_for_grade(grade)
    
    # Find which category the topic belongs to
    topic_category = None
    for category, topics in topics_by_category.items():
        if topic in topics:
            topic_category = category
            break
    
    if not topic_category:
        return []
    
    # Return other topics in the same category
    return [t for t in topics_by_category[topic_category] if t != topic]
