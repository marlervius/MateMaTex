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
TYPE: KAPITTEL (lærebok-kapittel — teoritungt!)
Et kapittel skal ligne en ordentlig lærebok-del, IKKE et arbeidsark. Teorien er
hovedsaken; oppgavene kommer til slutt. Planlegg GRUNDIG og OMFATTENDE.

KRAV TIL STRUKTUR:
- Innledning/motivasjon: hvorfor er temaet nyttig, hva skal eleven lære, kobling
  til det eleven kan fra før.
- 4–7 teoriseksjoner som bygger logisk fra grunnleggende til avansert. Del gjerne
  hver hovedteknikk/begrep i egen seksjon.
- For HVER seksjon, spesifiser:
  * Læringsmål og nøkkelbegreper
  * Definisjon(er) og/eller regel/setning som skal presenteres
  * Intuisjon/forklaring og (der det passer) en kort begrunnelse/utledning av regelen
  * MINST 2 gjennomregnede eksempler per teknikk/regel, med stigende vanskelighet
  * Vanlige feil / typiske misforståelser eleven bør unngå
  * Illustrasjonsbehov (TikZ/PGFPlots) markert NØDVENDIG/valgfri
- En tabell over standard­resultater/formler der det er relevant (f.eks. tabell over
  kjente integraler/deriverte).
- Oppsummering til slutt: de viktigste formlene og metodene samlet.
- Oppgaveseksjon HELT til slutt (teori FØR oppgaver), med stigende vanskelighet.

OMFANG: Et R1/R2/VG3-kapittel skal være rikt og detaljert. Hver hovedteknikk
fortjener egen seksjon med forklarende tekst, ikke bare en boks. Planlegg nok
innhold til flere sider teori.
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
    if material_type == "kapittel":
        return """
KAPITTEL-MODUS (lærebok-kapittel — skriv UTFYLLENDE teori!):
Dette er det viktigste: et kapittel skal være TEORITUNGT og grundig, som en ekte
lærebok-del. IKKE bare lister med definisjoner og bokser — skriv FORKLARENDE TEKST.

OBLIGATORISK DYBDE:
- Start med en innledning (løpende tekst) som motiverer temaet og knytter det til
  det eleven kan fra før.
- Bruk \\section{{...}} for hver hovedteknikk/begrep, og \\subsection{{...}} ved behov.
  Et fullverdig kapittel har typisk 4–7 seksjoner.
- For HVER teknikk/regel:
  * Skriv først forklarende brødtekst (intuisjon — hvorfor virker dette?).
  * Presenter regelen/setningen i \\begin{{definisjon}} eller en \\begin{{merk}}-boks.
  * Der det er naturlig: vis en kort begrunnelse/utledning av formelen.
  * Gi MINST 2 fullt gjennomregnede \\begin{{eksempel}}[title=...] med ALLE
    mellomregninger og forklaring av hvert steg — ikke bare svaret.
  * Legg gjerne inn en \\begin{{merk}}-boks med vanlige feil.
- Inkluder en formel-/resultattabell (booktabs) der det passer (f.eks. standardintegraler).
- Avslutt teoridelen med \\section*{{Oppsummering}} som samler de viktigste formlene.
- LEGG oppgaveseksjonen (\\section{{Oppgaver}} med taskbox) HELT til slutt, etter all teori.
- Bruk rikelig med figurer (PGFPlots/TikZ) for å illustrere begreper.

VIKTIG: Skriv langt og grundig. Et tynt kapittel med bare noen få bokser er feil —
mål på flere sider sammenhengende teori med mange eksempler før oppgavene.
"""
    return ""
