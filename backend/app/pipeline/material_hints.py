"""
Material-type specific instructions for pedagogue and author agents.
"""

from __future__ import annotations


def pedagogue_material_instructions(material_type: str) -> str:
    """Extra planning rules per material type."""
    if material_type == "prøve":
        return """
TYPE: PRØVE/EKSAMEN
- Lag struktur: forside/tittel, instruksjoner (tid, hjelpemidler), oppgaver med poeng
- Oppgaver nummerert; deloppgaver a), b), c)
- Ingen løsningsforslag i elevversjonen (løsninger i egen \\section*{Løsningsforslag} kun hvis løsninger er påkrevd)
- Inkluder poengskjema-tabell (booktabs) til slutt
- Varier vanskelighet: ca. 40% lett, 40% middels, 20% vanskelig
"""
    if material_type == "differensiert":
        return """
TYPE: DIFFERENSIERT ARBEIDSARK
- Planlegg én felles introduksjon, deretter tre nivåer: Grunnleggende, Standard, Avansert
- Standard-nivå er hovedinnholdet (ca. 70% av oppgavene)
- Grunnleggende: færre oppgaver, enklere tall, flere hint
- Avansert: utfordringsoppgaver og sammensatte problemer
"""
    if material_type == "kapittel":
        return """
TYPE: KAPITTEL
- Struktur: introduksjon → definisjoner → eksempler → oppgaver → oppsummering
- Teori før oppgaver; minst 2 worked examples
"""
    return ""


def author_material_instructions(material_type: str, include_solutions: bool) -> str:
    """Extra authoring rules per material type."""
    if material_type == "prøve":
        sol = (
            "Inkluder \\section*{Løsningsforslag} på slutten med komplette løsninger."
            if include_solutions
            else "IKKE inkluder løsningsforslag — kun elevprøve."
        )
        return f"""
PRØVE-MODUS:
- Start med \\title, tid (f.eks. 90 min), og korte instruksjoner
- Oppgaver i \\begin{{taskbox}}{{Oppgave N}} med poeng i tittelen, f.eks. {{Oppgave 1 (4 poeng)}}
- Avslutt med poengskjema-tabell (booktabs): Oppgave | Poeng | Oppnådd
- {sol}
"""
    if material_type == "differensiert":
        return """
DIFFERENSIERT MODUS:
- Etter tittel: \\section*{{Grunnleggende}}, deretter \\section*{{Standard}}, deretter \\section*{{Avansert}}
- Standard-seksjonen inneholder hovedoppgavene (taskbox)
- Grunnleggende: enklere tall og Tips-bokser; Avansert: utfordringer
"""
    return ""
