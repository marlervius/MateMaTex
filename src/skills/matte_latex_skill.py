"""
Matte-LaTeX Skill — Profesjonell matematikk-PDF-generering.

Denne skill-modulen inneholder instruksjoner, maler og retningslinjer
som AI-agentene bruker for å produsere profesjonelt matematisk innhold
via LaTeX → PDF-pipeline.

Grunnprinsipp: ALLTID LaTeX (pdflatex) for matematikkdokumenter.
Aldri ReportLab, WeasyPrint eller HTML-til-PDF.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Kjerneprinsipper
# ---------------------------------------------------------------------------

CORE_PRINCIPLE = """
=== MATTE-LATEX SKILL: PROFESJONELL PDF-GENERERING ===

GRUNNPRINSIPP: Alltid LaTeX for matematisk innhold.
- ALDRI ReportLab, WeasyPrint eller HTML-til-PDF for matematikkdokumenter
- ALLTID pdflatex for PDF-generering
- Matematiske uttrykk ALLTID i korrekt LaTeX-syntaks

Dette gir overlegen matematisk typesetting som er uoppnåelig med andre metoder.
"""


# ---------------------------------------------------------------------------
# Matematiske LaTeX-konstruksjoner
# ---------------------------------------------------------------------------

MATH_LATEX_GUIDE = r"""
=== MATEMATISKE LaTeX-KONSTRUKSJONER ===

BRØK, POTENSER, RØTTER:
  \frac{a}{b}           % Brøk — ALDRI a/b i display math
  x^{n}                 % Potens
  \sqrt{x}              % Kvadratrot
  \sqrt[n]{x}           % n-te rot

LIGNINGSSYSTEMER:
  \begin{align}
    2x + 3y &= 7 \\
    x - y   &= 1
  \end{align}

  \begin{equation}
    \begin{cases}
      2x + 3y = 7 \\
      x - y = 1
    \end{cases}
  \end{equation}

DERIVASJON OG INTEGRASJON:
  f'(x), \quad f''(x)                  % Newtons notasjon
  \frac{\mathrm{d}f}{\mathrm{d}x}      % Leibniz-notasjon
  \int_a^b f(x)\,\mathrm{d}x           % Bestemt integral (bruk \dd)
  \lim_{x \to \infty} f(x)             % Grenseverdi
  \sum_{k=1}^{n} k^2                   % Sum

GEOMETRI OG TRIGONOMETRI:
  \sin, \cos, \tan, \arcsin, \arccos, \arctan
  \angle ABC                            % Vinkel
  \overrightarrow{AB}                  % Vektor
  \|\vec{v}\|                          % Vektorlengde
  \vec{v} \cdot \vec{u}               % Skalarprodukt

STATISTIKK:
  \bar{x}               % Gjennomsnitt
  \sigma, \sigma^2      % Standardavvik, varians
  P(A \cup B)           % Sannsynlighet
  \binom{n}{k}          % Binomialkoeffisient

MULTIPLIKASJON: \cdot (ALDRI *)
BRØK i display: \frac{}{} (ALDRI a/b)
TABELLER: booktabs (\toprule, \midrule, \bottomrule) — INGEN vertikale linjer
"""


# ---------------------------------------------------------------------------
# Vanskelighetsgrads-system (stjerner)
# ---------------------------------------------------------------------------

DIFFICULTY_STAR_SYSTEM = r"""
=== VANSKELIGHETSGRADS-SYSTEM MED STJERNER ===

Merk HVER oppgave tydelig med vanskelighetsgrad i taskbox-tittelen:

\begin{taskbox}{Oppgave 1 \hfill \textcolor{green!60!black}{★☆☆ Grunnleggende}}
Tekst...
\end{taskbox}

\begin{taskbox}{Oppgave 2 \hfill \textcolor{orange}{★★☆ Middels}}
Tekst...
\end{taskbox}

\begin{taskbox}{Oppgave 3 \hfill \textcolor{red}{★★★ Utfordrende}}
Tekst...
\end{taskbox}

REGEL for vanskelighetsgrader:
- ★☆☆ Grunnleggende: Direkte anvendelse av én formel/metode
- ★★☆ Middels: Krever to steg eller litt problemforståelse
- ★★★ Utfordrende: Krever kombinasjon av metoder eller kreativ tenking
"""


# ---------------------------------------------------------------------------
# Kontekstrike oppgaver
# ---------------------------------------------------------------------------

CONTEXTUAL_TASK_GUIDE = """
=== KONTEKSTRIKE OPPGAVER ===

Legg ALLTID til realistisk kontekst når det er pedagogisk hensiktsmessig:

GODE KONTEKSTER:
- Priser, avstand, areal, befolkningsvekst
- Norske navn (Ola, Kari, Lars, Sofie) og steder (Oslo, Bergen, Trondheim)
- Aldersrelevante situasjoner:
  * 1.-7. trinn: baking, sport, dyr, leker, klasserom
  * 8.-10. trinn: økonomi, reise, idrett, teknologi
  * VG1-VG3: økonomi, fysikk, statistikk, ingeniørfag

EKSEMPEL (VG1):
  "Sofie investerer 15 000 kr i aksjer. Verdien øker med 8% per år.
   a) Hvor mye er aksjene verdt etter 5 år?
   b) Etter hvor mange år har verdien doblet seg?"

EKSEMPEL (8. trinn):
  "Et fotballstadion i Trondheim har 21 166 plasser.
   Under en kamp er 73% av plassene fylt.
   Hvor mange tilskuere er det?"
"""


# ---------------------------------------------------------------------------
# Eksamens-/prøvemal
# ---------------------------------------------------------------------------

EXAM_TEMPLATE_GUIDE = r"""
=== EKSAMENS-/PRØVEMAL ===

For prøver og eksamener, bruk følgende struktur:

\begin{center}
  {\LARGE\bfseries Prøve i [Fag]}\\[0.5em]
  {\large [Dato] \quad Varighet: [X] timer}\\[0.3em]
  {\normalsize Hjelpemidler: [Tillatte hjelpemidler]}
\end{center}

\vspace{1em}
\noindent\rule{\textwidth}{0.5pt}
\vspace{0.5em}

\noindent\textbf{Navn:} \underline{\hspace{8cm}} \quad
\textbf{Klasse:} \underline{\hspace{3cm}}

\vspace{1em}

\begin{tcolorbox}[colback=blue!5, colframe=blue!40, title=Informasjon]
  Vis all utregning. Delpoeng gis for delvis korrekt løsning.
  Totalt: \textbf{[X] poeng}
\end{tcolorbox}

\vspace{1em}

\section*{Del 1 — Uten hjelpemidler}

\begin{enumerate}[label=\textbf{Oppgave \arabic*.}, leftmargin=*, itemsep=2em]

\item Løs ligningen:
  \[
    2x^2 - 5x + 3 = 0
  \]
  \textit{(3 poeng)}

\end{enumerate}

\newpage
\section*{Del 2 — Med hjelpemidler}
"""


# ---------------------------------------------------------------------------
# TikZ-guide
# ---------------------------------------------------------------------------

TIKZ_GUIDE = r"""
=== TikZ OG PGFPLOTS-GUIDE ===

KOORDINATSYSTEM MED FUNKSJON:
\begin{figure}[H]
\centering
\begin{tikzpicture}
\begin{axis}[
  xlabel={$x$}, ylabel={$y$},
  axis lines=center,
  xmin=-3, xmax=3, ymin=-2, ymax=6,
  grid=major,
  grid style={line width=0.2pt, draw=gray!30},
  width=10cm, height=8cm,
]
  \addplot[mainBlue, thick, domain=-3:3, samples=100] {x^2};
  \addlegendentry{$f(x) = x^2$}
\end{axis}
\end{tikzpicture}
\caption{Parabelen $f(x) = x^2$.}
\end{figure}

GEOMETRISK FIGUR:
\begin{figure}[H]
\centering
\begin{tikzpicture}[scale=1.5]
  \draw[thick] (0,0) -- (4,0) -- (4,3) -- cycle;
  \draw[|<->|] (0,-0.5) -- node[below]{$a = 4$} (4,-0.5);
  \draw[|<->|] (4.5,0) -- node[right]{$b = 3$} (4.5,3);
  \node at (2,1) {$A = \frac{1}{2}ab$};
\end{tikzpicture}
\caption{Rettvinklet trekant med kateter $a$ og $b$.}
\end{figure}

TILGJENGELIGE TikZ-BIBLIOTEKER (forhåndslastet):
  arrows.meta, calc, patterns, positioning, shapes.geometric,
  decorations.pathreplacing, decorations.pathmorphing

TILGJENGELIGE FARGER:
  mainBlue, lightBlue, mainGreen, lightGreen,
  mainOrange, lightOrange, mainPurple, lightPurple,
  mainTeal, lightTeal, mainGray, lightGray
"""


# ---------------------------------------------------------------------------
# Komplett arbeidsflyt
# ---------------------------------------------------------------------------

WORKFLOW = """
=== KOMPLETT ARBEIDSFLYT FOR MATTE-LATEX ===

1. Les oppdraget nøye
   → noter fag, nivå (VG1/VG2/VG3), emne, antall oppgaver, materialtype

2. Planlegg innhold (Pedagogen)
   → struktur, læringsmål, kompetansemål fra LK20

3. Skriv LaTeX-innhold (Skriveren)
   → teori i definisjon-bokser, eksempler i eksempel-bokser
   → oppgaver i taskbox med vanskelighetsgrads-stjerner
   → TikZ-figurer direkte inline (ALDRI [INSERT FIGURE])
   → realistisk norsk kontekst

4. Kvalitetssikre (Redaktøren)
   → verifiser fasit matematisk
   → sjekk LaTeX-syntaks og miljøbalanse
   → fjern preamble (legges til automatisk)

5. Kompiler via pdflatex (systemet)
   → to pass for korrekte referanser
   → automatisk feilretting ved kompileringsfeil

6. Lever ferdig PDF
"""


# ---------------------------------------------------------------------------
# Skill-klasse (samler alt)
# ---------------------------------------------------------------------------

class MatteLatexSkill:
    """
    Matte-LaTeX Skill — instruksjoner for profesjonell matematikk-PDF-generering.

    Gir AI-agentene den kunnskap og de retningslinjer de trenger for å produsere
    høy-kvalitets matematisk innhold via LaTeX → PDF-pipeline.

    Bruk:
        skill = MatteLatexSkill()
        instructions = skill.get_writer_instructions(content_type="prøve")
    """

    name = "Matte-LaTeX"
    description = "Profesjonell matematikk-PDF-generering via LaTeX"

    def get_core_principle(self) -> str:
        return CORE_PRINCIPLE

    def get_math_guide(self) -> str:
        return MATH_LATEX_GUIDE

    def get_difficulty_system(self) -> str:
        return DIFFICULTY_STAR_SYSTEM

    def get_contextual_guide(self) -> str:
        return CONTEXTUAL_TASK_GUIDE

    def get_exam_template(self) -> str:
        return EXAM_TEMPLATE_GUIDE

    def get_tikz_guide(self) -> str:
        return TIKZ_GUIDE

    def get_workflow(self) -> str:
        return WORKFLOW

    def get_writer_instructions(self, content_type: str = "arbeidsark") -> str:
        """
        Returns the full set of writing instructions for the given content type.

        Args:
            content_type: "arbeidsark", "kapittel", "prøve", or "eksamen"

        Returns:
            Combined instruction string for the writer agent.
        """
        base = (
            CORE_PRINCIPLE
            + "\n"
            + MATH_LATEX_GUIDE
            + "\n"
            + DIFFICULTY_STAR_SYSTEM
            + "\n"
            + CONTEXTUAL_TASK_GUIDE
            + "\n"
            + TIKZ_GUIDE
        )

        if content_type in ("prøve", "eksamen"):
            base += "\n" + EXAM_TEMPLATE_GUIDE

        base += "\n" + WORKFLOW

        return base

    def get_editor_checklist(self) -> str:
        """Quality-control checklist for the editor agent."""
        return """
=== MATTE-LATEX REDAKTØR-SJEKKLISTE ===

a) DEFINISJONER: Ren tekst "Definisjon:" → \\begin{definisjon}...\\end{definisjon}
b) EKSEMPLER: Ren tekst "Eksempel:" → \\begin{eksempel}[title=Beskrivende]...\\end{eksempel}
c) OPPGAVER: → \\begin{taskbox}{Oppgave N \\hfill STJERNER}...\\end{taskbox}
d) FIGURER: \\begin{figure} → \\begin{figure}[H] + \\centering + \\caption{}
e) MATEMATIKK: \\frac{}{}, \\sqrt{}, \\cdot (ALDRI *)
f) TABELLER: booktabs (\\toprule, \\midrule, \\bottomrule) — ingen vertikale linjer
g) KLAMMER: alle { har matchende }
h) MILJØER: alle \\begin{} har matchende \\end{}
i) FASIT: verifiser ALLE svar matematisk steg for steg
j) PREAMBLE: FJERN all \\documentclass, \\usepackage, \\begin{document}
k) KONTEKST: oppgaver har norske navn/steder der det er naturlig
l) STJERNER: oppgaver har vanskelighetsgrads-stjerner (★☆☆ / ★★☆ / ★★★)
"""
