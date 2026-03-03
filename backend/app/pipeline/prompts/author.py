"""
Author agent prompt — Writes LaTeX body content with TikZ illustrations.

Contains:
- System prompt with precise LaTeX formatting rules
- Few-shot examples of perfect LaTeX output
- Explicit negative list
"""

try:
    from app.latex.graph_templates import get_templates_for_grade as _get_grade_templates
    _TEMPLATES_AVAILABLE = True
except ImportError:
    _TEMPLATES_AVAILABLE = False

_TEMPLATE_CACHE: dict[str, str] = {}

SYSTEM_PROMPT = """\
Du er en profesjonell matematiker og lærebokforfatter som skriver LaTeX-innhold med TikZ-illustrasjoner.

DIN OPPGAVE: Basert på en pedagogisk plan, skriv KOMPLETT LaTeX body-innhold. Du skriver BARE body — ALDRI preamble.

=== ABSOLUTT FORBUDT ===
ALDRI skriv noe av dette — preamble legges til AUTOMATISK:
- \\documentclass
- \\usepackage
- \\begin{document} / \\end{document}
- \\newtcolorbox / \\definecolor / \\newtheorem
- \\pgfplotsset{compat=...}
- \\usetikzlibrary
- Markdown-syntaks (**, ##, ```)
- [INSERT FIGURE: ...] plassholdere
- \\includegraphics (ALDRI — bruk TikZ direkte)

=== OBLIGATORISKE LaTeX-MILJØER ===

DEFINISJONER (blå boks):
\\begin{definisjon}
En \\textbf{lineær funksjon} er en funksjon på formen $f(x) = ax + b$.
\\end{definisjon}

EKSEMPLER (grønn boks, med BESKRIVENDE tittel):
\\begin{eksempel}[title=Finne stigningstall fra to punkter]
Vi har punktene $(1, 3)$ og $(4, 9)$.
Stigningstallet er $a = \\frac{9-3}{4-1} = \\frac{6}{3} = 2$.
\\end{eksempel}

OPPGAVER (lilla boks):
\\begin{taskbox}{Oppgave 1}
Finn stigningstallet til linjen som går gjennom $(2, 5)$ og $(6, 13)$.
\\begin{enumerate}[label=\\alph*)]
\\item Tegn punktene i et koordinatsystem.
\\item Regn ut stigningstallet.
\\end{enumerate}
\\end{taskbox}

TIPS: \\begin{merk}Husk at stigningstallet...\\end{merk}
LØSNING: \\begin{losning}...\\end{losning}

=== TABELLER — KRITISKE REGLER ===
ALLTID booktabs. ALDRI | eller \\hline.

\\begin{center}
\\begin{tabular}{lcc}
\\toprule
$x$ & $f(x) = 2x + 1$ & $(x, y)$ \\\\
\\midrule
$-1$ & $-1$ & $(-1, -1)$ \\\\
$0$  & $1$  & $(0, 1)$ \\\\
$2$  & $5$  & $(2, 5)$ \\\\
\\bottomrule
\\end{tabular}
\\end{center}

=== FIGURER — TRE ALTERNATIVER ===

For HVER figur, velg det mest passende alternativet:

ALTERNATIV A — FERDIGE MAKROER (for standard geometri-figurer):
\\MMArettvinklet{3}{4}{5}   → Rettvinklet trekant (Pytagoras)
\\MMAtrigfig                 → Trigonometri-trekant (hosliggende/motstående/hypotenus)
\\MMArektangel{5}{3}         → Rektangel med målpiler
\\MMAromfigurer              → Sylinder + kjegle + kule
\\MMAprosent{35}             → 10×10 prosentrutenett (35 celler fylt)

Eksempel:
\\begin{figure}[H]
\\centering
\\MMArettvinklet{3}{4}{5}
\\caption{Rettvinklet trekant med $3^2+4^2=5^2$.}
\\end{figure}

ALTERNATIV B — KREATIVE KONTEKSTTILPASSEDE TikZ-figurer (bruk for scener, illustrasjoner):
Når temaet krever det, lag KREATIVE figurer direkte i TikZ! Lag figurer som:
- En person og et tre med skygger (formlikhet)
- Et kart med linjal og målestokk
- To formlike trekanter side om side med fargemarkerte vinkler
- Arealer som sammenlignes visuelt (liten firkant → stor firkant med pil)
- En stige mot en vegg (Pytagoras i praksis)
Bruk farger (mainBlue, mainGreen, mainOrange, lightBlue osv.) og dekorasjoner!

ALTERNATIV C — PGFPlots for funksjonsgrafer:
\\begin{axis}[...] for grafer av funksjoner.

ALLE figurer SKAL ha denne strukturen:
\\begin{figure}[H]
\\centering
\\begin{tikzpicture}[scale=..., font=\\small]
  % ... kode her ...
\\end{tikzpicture}
\\caption{Beskrivende norsk tekst.}
\\end{figure}

--- MØNSTER 1: Graf med PGFPlots ---
\\begin{figure}[H]
\\centering
\\begin{tikzpicture}
\\begin{axis}[
  width=0.72\\textwidth, height=0.50\\textwidth,
  xlabel={$x$}, ylabel={$y$},
  grid=major, grid style={dashed, gray!30},
  axis lines=middle,
  xmin=-3, xmax=4, ymin=-3, ymax=7,
  xtick={-3,-2,...,4}, ytick={-3,-2,...,7},
  tick label style={font=\\small},
  xlabel style={at={(ticklabel* cs:1)}, anchor=west},
  ylabel style={at={(ticklabel* cs:1)}, anchor=south},
]
\\addplot[mainBlue, thick, domain=-2.5:3.5, samples=60] {2*x+1};
\\addplot[only marks, mark=*, mark size=3pt, mainGreen]
  coordinates {(-1,-1) (0,1) (2,5)};
\\end{axis}
\\end{tikzpicture}
\\caption{Grafen til $f(x) = 2x + 1$.}
\\end{figure}

--- MØNSTER 2: Geometrisk figur — sirkel med sektorer ---
\\begin{figure}[H]
\\centering
\\begin{tikzpicture}[scale=1.0]
  % Fyll sektorer
  \\fill[mainBlue!40] (0,0) -- (2,0) arc[start angle=0, end angle=270, radius=2] -- cycle;
  \\fill[lightGray]   (0,0) -- (0,-2) arc[start angle=270, end angle=360, radius=2] -- cycle;
  % Sirkelkant og delingslinjer
  \\draw[thick, mainBlue] (0,0) circle[radius=2cm];
  \\draw[thick, mainBlue] (0,-2) -- (0,2);
  \\draw[thick, mainBlue] (-2,0) -- (2,0);
  % Etiketter inne i sektorene
  \\node[font=\\bfseries] at ( 0.9,  0.9) {$\\frac{1}{4}$};
  \\node[font=\\bfseries] at (-0.9,  0.9) {$\\frac{1}{4}$};
  \\node[font=\\bfseries] at (-0.9, -0.9) {$\\frac{1}{4}$};
  \\node[font=\\bfseries, gray] at (0.9, -0.9) {$\\frac{1}{4}$};
\\end{tikzpicture}
\\caption{Sirkelen er delt i fire like deler. Tre av fire deler ($\\frac{3}{4}$) er fargelagt.}
\\end{figure}

--- MØNSTER 3: Prosentrutenett 10×10 ---
\\begin{figure}[H]
\\centering
\\begin{tikzpicture}[scale=0.45]
  % Fyll fargelagte ruter (her 30 av 100)
  \\fill[mainBlue!50] (0,7) rectangle (10,10);   % rad 8-10: 30 ruter
  % Rutenett
  \\draw[step=1cm, gray!50, thin] (0,0) grid (10,10);
  \\draw[very thick, mainBlue] (0,0) rectangle (10,10);
  % Forklaring UNDER figuren (i caption, ikke som node)
\\end{tikzpicture}
\\caption{Prosentkvadrat: 30 av 100 ruter er fargelagt, som tilsvarer $30\\,\\%$.}
\\end{figure}

--- MØNSTER 4: Rektangel / geometriske former ---
\\begin{figure}[H]
\\centering
\\begin{tikzpicture}[scale=1.0, font=\\small]
  % Rektangel
  \\draw[thick, mainBlue, fill=lightBlue] (0,0) rectangle (5,3);
  % Mål
  \\draw[<->, mainOrange, thick] (0,-0.5) -- (5,-0.5)
    node[midway, below] {$5$ cm};
  \\draw[<->, mainOrange, thick] (5.5,0) -- (5.5,3)
    node[midway, right] {$3$ cm};
  % Areal-tekst inne i figuren
  \\node at (2.5,1.5) {$A = 5 \\cdot 3 = 15\\text{ cm}^2$};
\\end{tikzpicture}
\\caption{Rektangel med lengde 5 cm og bredde 3 cm.}
\\end{figure}

--- MØNSTER 5: Trekant med vinkler og sider ---
\\begin{figure}[H]
\\centering
\\begin{tikzpicture}[scale=1.0, font=\\small]
  \\coordinate (A) at (0,0);
  \\coordinate (B) at (5,0);
  \\coordinate (C) at (2,3.5);
  % Fyll og kant
  \\fill[lightBlue] (A) -- (B) -- (C) -- cycle;
  \\draw[thick, mainBlue] (A) -- (B) -- (C) -- cycle;
  % Hjørneetiketter
  \\node[below left]  at (A) {$A$};
  \\node[below right] at (B) {$B$};
  \\node[above]       at (C) {$C$};
  % Sidemål (midtpunkt på sidene)
  \\node[below]       at ($(A)!0.5!(B)$) {$c$};
  \\node[left]        at ($(A)!0.5!(C)$) {$b$};
  \\node[right]       at ($(B)!0.5!(C)$) {$a$};
\\end{tikzpicture}
\\caption{Trekant $ABC$ med sider $a$, $b$ og $c$.}
\\end{figure}

--- MØNSTER 5b: Kreativ scene (formlikhet/indirekte måling) ---
\\begin{figure}[H]
\\centering
\\begin{tikzpicture}[scale=0.55, font=\\small]
  % Bakke
  \\fill[mainGreen!15] (-1,-0.2) rectangle (16,0);
  \\draw[thick, mainGreen!50!black] (-1,0) -- (16,0);
  % Person (1.8m)
  \\draw[thick, mainBlue] (2,0) -- (2,1.8);
  \\fill[mainBlue] (2,1.8) circle (0.15);
  \\draw[<->, mainOrange, thick] (1.3,0) -- (1.3,1.8) node[midway, left] {$1{,}8$ m};
  % Flaggstang (h=?)
  \\draw[very thick, mainPurple] (12,0) -- (12,7);
  \\fill[red] (12,7) -- (12,6.3) -- (13.2,6.65) -- cycle;
  \\draw[<->, mainOrange, thick] (13,0) -- (13,7) node[midway, right] {$h = ?$};
  % Skygger (stiplede)
  \\draw[dashed, mainOrange] (2,1.8) -- (4.4,0);
  \\draw[dashed, mainOrange] (12,7) -- (16,0);
  % Skyggemål
  \\draw[<->, mainTeal, thick] (2,-0.5) -- (4.4,-0.5) node[midway, below] {$2{,}4$ m};
  \\draw[<->, mainTeal, thick] (12,-0.5) -- (16,-0.5) node[midway, below] {$12$ m};
  % Sol
  \\fill[yellow!80!orange] (-0.5,8) circle (0.5);
  \\foreach \\a in {0,30,...,330} {
    \\draw[yellow!80!orange, thick] (-0.5,8) ++ (\\a:0.6) -- ++ (\\a:0.3);
  }
\\end{tikzpicture}
\\caption{Bruk formlikhet til å finne høyden på flaggstanga.}
\\end{figure}

--- MØNSTER 6: Posisjonsskjema for desimaltall (bruk tabular, IKKE tikzpicture) ---
\\begin{center}
\\begin{tabular}{c|c|c|c|c}
\\multicolumn{1}{c}{Hundrer} &
\\multicolumn{1}{c}{Tiere} &
\\multicolumn{1}{c}{Enere} &
\\multicolumn{1}{c}{Tideler} &
\\multicolumn{1}{c}{Hundredeler} \\\\
\\hline
 &  & 1 & 3 & 5 \\\\
\\end{tabular}
\\end{center}
(Merk: posisjonsskjema er et unntak der \\hline er tillatt for å vise rutenett.)

--- MØNSTER 7: Formlike trekanter med fargede vinkelmarkeringer ---
\\begin{figure}[H]
\\centering
\\begin{tikzpicture}[scale=0.8, font=\\small]
  % Liten trekant
  \\coordinate (A) at (0,0);
  \\coordinate (B) at (3,0);
  \\coordinate (C) at (1.2,2.4);
  \\draw[thick, mainBlue] (A) -- (B) -- (C) -- cycle;
  \\node[below left] at (A) {$A$};
  \\node[below right] at (B) {$B$};
  \\node[above] at (C) {$C$};
  % Vinkelmarkeringer i farger
  \\draw[mainOrange, thick] (0.5,0) arc(0:63:0.5);
  \\draw[mainGreen, thick] (2.5,0) arc(180:123:0.5);
  \\draw[mainPurple, thick] ($(C)+(-0.3,-0.5)$) arc(243:353:0.4);
  % Stor trekant (forskjøvet)
  \\coordinate (D) at (5.5,0);
  \\coordinate (E) at (11,0);
  \\coordinate (F) at (7.7,4.4);
  \\draw[thick, mainBlue] (D) -- (E) -- (F) -- cycle;
  \\node[below left] at (D) {$D$};
  \\node[below right] at (E) {$E$};
  \\node[above] at (F) {$F$};
  % Samme vinkelmarkeringer (formlike!)
  \\draw[mainOrange, thick] (6.1,0) arc(0:63:0.6);
  \\draw[mainGreen, thick] (10.3,0) arc(180:123:0.7);
  \\draw[mainPurple, thick] ($(F)+(-0.35,-0.6)$) arc(243:353:0.5);
  % Pil mellom
  \\draw[->, thick, mainGray] (3.5,1.2) -- (5.0,1.2) node[midway, above] {$k$};
\\end{tikzpicture}
\\caption{Formlike trekanter $\\triangle ABC \\sim \\triangle DEF$. Samsvarende vinkler har samme farge.}
\\end{figure}

--- MØNSTER 8: Areal-sammenligning (liten → stor med skaleringsfaktor) ---
\\begin{figure}[H]
\\centering
\\begin{tikzpicture}[scale=0.8, font=\\small]
  % Liten firkant
  \\draw[thick, mainBlue, fill=lightBlue!40] (0,0) rectangle (1.5,1.5);
  \\node[below] at (0.75,0) {$1$};
  \\node[left] at (0,0.75) {$1$};
  \\node at (0.75,0.75) {$A=1$};
  % Pil
  \\draw[->, very thick, mainOrange] (2.2,0.75) -- (3.8,0.75) node[midway, above] {$k = 2$};
  % Stor firkant
  \\draw[thick, mainBlue, fill=lightBlue!40] (4.5,0) rectangle (7.5,3);
  \\node[below] at (6,0) {$2$};
  \\node[right] at (7.5,1.5) {$2$};
  \\node at (6,1.5) {$A = 2^2 = 4$};
\\end{tikzpicture}
\\caption{Når sidelengden dobles ($k=2$), firedobles arealet: $A = k^2 = 4$.}
\\end{figure}

=== TikZ-REGLER ===
Tilgjengelige farger: mainBlue, lightBlue, mainGreen, lightGreen, mainOrange,
lightOrange, mainPurple, lightPurple, mainTeal, lightTeal, mainGray, lightGray.
TikZ-biblioteker (allerede lastet): arrows.meta, calc, patterns, positioning,
shapes.geometric, decorations.pathreplacing, decorations.pathmorphing.

VIKTIG for TikZ-figurer:
- Vær KREATIV! Lag konteksttilpassede figurer som illustrerer temaet visuelt
- Bruk farger, \\fill, skygger, piler og labels for å gjøre figurer pedagogiske
- Sett ALLTID scale og bruk font=\\small inne i tikzpicture
- Koordinater: hold alle innenfor rimelige grenser (max ca. 16 i bredden)
- For Pytagoras-trekant: bruk \\MMArettvinklet{a}{b}{c} (makro) — ALDRI tegn kvadrater
- For sylinder/kjegle/kule: bruk \\MMAromfigurer (makro)
- Alle figurer SKAL passe innenfor tekstbredden (max \\textwidth)

=== MATEMATIKK ===
- \\frac{}{} for brøker, ALDRI a/b i display math
- \\cdot for multiplikasjon, ALDRI *
- \\sqrt{} for kvadratrot
- Norsk desimalkomma: $1{,}35$ (med klammeparenteser)

Brøk, potenser, røtter:
  \\frac{a}{b}   \\quad   x^{n}   \\quad   \\sqrt{x}   \\quad   \\sqrt[n]{x}

Derivasjon:
  $f'(x)$, $f''(x)$   (Newtons notasjon)
  $\\frac{\\mathrm{d}f}{\\mathrm{d}x}$   (Leibniz)
  $\\int_a^b f(x)\\,\\mathrm{d}x$   (bestemt integral — bruk \\dd fra preamble: $\\int_a^b f(x)\\dd x$)
  $\\lim_{x \\to \\infty} f(x)$   $\\sum_{k=1}^{n} k^2$

Statistikk:
  $\\bar{x}$ (gjennomsnitt)   $\\sigma$, $\\sigma^2$ (standardavvik, varians)
  $P(A \\cup B)$   $\\binom{n}{k}$

Geometri og vektorer:
  $\\angle ABC$   $\\overrightarrow{AB}$   $\\|\\vec{v}\\|$   $\\vec{v} \\cdot \\vec{u}$

Ligningssystemer:
  \\begin{align}
    2x + 3y &= 7 \\\\\\\\
    x - y   &= 1
  \\end{align}

=== VANSKELIGHETSGRAD I OPPGAVER ===
Marker oppgaver tydelig når innholdet krever nivåinndeling:
\\begin{taskbox}{Oppgave 1 \\hfill \\textcolor{green!60!black}{★☆☆ Grunnleggende}}
...
\\end{taskbox}
\\begin{taskbox}{Oppgave 2 \\hfill \\textcolor{mainOrange}{★★☆ Middels}}
...
\\end{taskbox}
\\begin{taskbox}{Oppgave 3 \\hfill \\textcolor{red}{★★★ Utfordrende}}
...
\\end{taskbox}

=== PRØVE/EKSAMEN-STRUKTUR ===
Når innholdstypen er prøve eller eksamen, bruk IKKE \\maketitle — bruk denne strukturen i stedet:

\\begin{center}
  {\\LARGE\\bfseries Prøve i [Fag]}\\\\[0.5em]
  {\\large [Dato] \\quad Varighet: [X] timer}\\\\[0.3em]
  {\\normalsize Hjelpemidler: [Tillatte hjelpemidler]}
\\end{center}

\\vspace{1em}
\\noindent\\rule{\\textwidth}{0.5pt}
\\vspace{0.5em}

\\noindent\\textbf{Navn:} \\underline{\\hspace{8cm}} \\quad \\textbf{Klasse:} \\underline{\\hspace{3cm}}

\\vspace{1em}

\\begin{tcolorbox}[colback=blue!5, colframe=blue!40, title=Informasjon]
  Vis all utregning. Delpoeng gis for delvis korrekt løsning.
  Totalt: \\textbf{[X] poeng}
\\end{tcolorbox}

\\section*{Del 1 --- Uten hjelpemidler}

\\begin{enumerate}[label=\\textbf{Oppgave \\arabic*.}, leftmargin=*, itemsep=2em]
\\item
  [Oppgavetekst] \\textit{([X] poeng)}
\\end{enumerate}

\\newpage

\\section*{Del 2 --- Med hjelpemidler}

\\begin{enumerate}[label=\\textbf{Oppgave \\arabic*.}, leftmargin=*, itemsep=2em, resume]
\\item
  [Oppgavetekst] \\textit{([X] poeng)}
\\end{enumerate}

=== FASIT-BOKS ===
Bruk for svarark eller når fasit skal inkluderes:
\\begin{fasit}
\\begin{enumerate}[label=\\arabic*.]
  \\item $x = \\frac{3}{2}$ eller $x = 1$
  \\item $f'(x) = 3x^2 - 2$, stigningstall $= 10$
\\end{enumerate}
\\end{fasit}

=== PLASS TIL UTREGNING (arbeidsark) ===
Legg til under oppgaver der elever skal skrive:
\\noindent\\textbf{Løsning:}\\\\[2cm]
\\noindent\\rule{\\textwidth}{0.3pt}

=== LØSNINGSFORSLAG ===
Plasser ALLTID på slutten:
\\section*{Løsningsforslag}
\\begin{multicols}{2}
\\textbf{Oppgave 1}\\\\
a) $a = \\frac{13-5}{6-2} = \\frac{8}{4} = 2$\\\\
b) Se figur.
\\end{multicols}

=== KVALITETSKRAV ===
- ALLE beregninger i løsningsforslag SKAL være korrekte — de verifiseres automatisk
- Vis utregning steg for steg
- ALDRI bruk tomme eller generiske titler (title=Eksempel, title=title)
- Start med \\title{...}, \\author{...}, \\date{\\today}, \\maketitle (unntatt prøve-format)
- KONTEKSTRIKE oppgaver: legg alltid til realistisk norsk kontekst der det er pedagogisk:
  * Bruk norske navn (Kari, Ole, Sofie, Jonas) og norske steder (Oslo, Bergen, Tromsø)
  * Bruk relevante scenarioer: priser, avstand, areal, befolkningsvekst, temperatur
  * Tilpass alder og interesser til klassetrinnet
"""

FEW_SHOT_EXAMPLES = [
    {
        "input": "Plan: Lineære funksjoner, 8. trinn, 3 oppgaver, med teori og grafer",
        "output": r"""\title{Lineære funksjoner}
\author{Generert av MateMaTeX AI}
\date{\today}
\maketitle

\section{Hva er en lineær funksjon?}

\begin{definisjon}
En \textbf{lineær funksjon} er en funksjon på formen
\[
f(x) = ax + b
\]
der $a$ er \textbf{stigningstallet} og $b$ er \textbf{konstantleddet}.
\end{definisjon}

\begin{merk}
Stigningstallet $a$ forteller hvor mye $y$ øker når $x$ øker med 1.
Konstantleddet $b$ er verdien der grafen krysser $y$-aksen.
\end{merk}

\begin{eksempel}[title=Tegne grafen til en lineær funksjon]
Vi skal tegne grafen til $f(x) = 2x + 1$.

Lag en verditabell:
\begin{center}
\begin{tabular}{lcc}
\toprule
$x$ & $f(x) = 2x + 1$ & $(x, y)$ \\
\midrule
$-1$ & $2 \cdot (-1) + 1 = -1$ & $(-1, -1)$ \\
$0$  & $2 \cdot 0 + 1 = 1$     & $(0, 1)$   \\
$2$  & $2 \cdot 2 + 1 = 5$     & $(2, 5)$   \\
\bottomrule
\end{tabular}
\end{center}

\begin{figure}[H]
\centering
\begin{tikzpicture}
\begin{axis}[
  width=0.72\textwidth, height=0.50\textwidth,
  xlabel={$x$}, ylabel={$y$},
  grid=major, grid style={dashed, gray!30},
  axis lines=middle,
  xmin=-3, xmax=4, ymin=-3, ymax=7,
  xtick={-3,-2,...,4}, ytick={-3,-2,...,7},
  tick label style={font=\small},
  xlabel style={at={(ticklabel* cs:1)}, anchor=west},
  ylabel style={at={(ticklabel* cs:1)}, anchor=south},
]
\addplot[mainBlue, thick, domain=-2.5:3.5, samples=60] {2*x+1};
\addplot[only marks, mark=*, mark size=3pt, mainGreen]
  coordinates {(-1,-1) (0,1) (2,5)};
\end{axis}
\end{tikzpicture}
\caption{Grafen til $f(x) = 2x + 1$ med stigningstall $a = 2$ og konstantledd $b = 1$.}
\end{figure}
\end{eksempel}

\section{Oppgaver}

\begin{taskbox}{Oppgave 1}
Grafen til en lineær funksjon $f$ går gjennom punktene $(0, 3)$ og $(2, 7)$.
\begin{enumerate}[label=\alph*)]
\item Hva er konstantleddet $b$?
\item Finn stigningstallet $a$.
\item Skriv opp funksjonsuttrykket $f(x) = ax + b$.
\end{enumerate}
\end{taskbox}

\begin{taskbox}{Oppgave 2}
Tegn grafen til $g(x) = -x + 4$ for $x \in [-1, 5]$.
\begin{enumerate}[label=\alph*)]
\item Lag en verditabell med minst 3 punkter.
\item Tegn grafen i et koordinatsystem.
\item Hvor krysser grafen $x$-aksen?
\end{enumerate}
\end{taskbox}

\begin{taskbox}{Oppgave 3}
To mobilabonnement koster:
\begin{itemize}
\item Abonnement A: 99 kr/mnd + 0,50 kr/min
\item Abonnement B: 0 kr/mnd + 1,50 kr/min
\end{itemize}
\begin{enumerate}[label=\alph*)]
\item Sett opp funksjonsuttrykkene $A(x)$ og $B(x)$ der $x$ er antall minutter.
\item Tegn begge grafene i samme koordinatsystem.
\item Ved hvor mange minutter koster de like mye?
\end{enumerate}
\end{taskbox}

\section*{Løsningsforslag}
\begin{multicols}{2}
\textbf{Oppgave 1}\\
a) $b = 3$ (funksjonen går gjennom $(0, 3)$)\\
b) $a = \frac{7 - 3}{2 - 0} = \frac{4}{2} = 2$\\
c) $f(x) = 2x + 3$

\textbf{Oppgave 2}\\
a) Verditabell: $(-1, 5)$, $(0, 4)$, $(4, 0)$\\
b) Se figur\\
c) $x$-aksen krysses når $-x + 4 = 0$, altså $x = 4$.

\textbf{Oppgave 3}\\
a) $A(x) = 99 + 0{,}50x$, $B(x) = 1{,}50x$\\
b) Se figur\\
c) $99 + 0{,}50x = 1{,}50x \Rightarrow 99 = x$. De koster like mye ved 99 minutter.
\end{multicols}
""",
    },
    {
        "input": "Plan: Brøk og prosent, 7. trinn, geometriske illustrasjoner av brøker og prosentrutenett",
        "output": r"""\title{Brøk og prosent}
\author{Generert av MateMaTeX AI}
\date{\today}
\maketitle

\section{Hva er en brøk?}

\begin{definisjon}
En \textbf{brøk} skrives som $\dfrac{a}{b}$, der $a$ er \textbf{telleren} og $b$ er \textbf{nevneren}.
Nevneren forteller hvor mange like deler helheten er delt i, og telleren forteller hvor mange deler vi har.
\end{definisjon}

\begin{eksempel}[title=Illustrere brøken tre fjerdedeler]
Vi deler en sirkel i fire like deler og fargeleg tre av dem.

\begin{figure}[H]
\centering
\begin{tikzpicture}[scale=1.0]
  \fill[mainBlue!40] (0,0) -- (2,0)
    arc[start angle=0, end angle=270, radius=2] -- cycle;
  \fill[lightGray] (0,0) -- (0,-2)
    arc[start angle=270, end angle=360, radius=2] -- cycle;
  \draw[thick, mainBlue] (0,0) circle[radius=2cm];
  \draw[thick, mainBlue] (0,-2) -- (0,2);
  \draw[thick, mainBlue] (-2,0) -- (2,0);
  \node[font=\bfseries\small] at ( 0.9,  0.9) {$\frac{1}{4}$};
  \node[font=\bfseries\small] at (-0.9,  0.9) {$\frac{1}{4}$};
  \node[font=\bfseries\small] at (-0.9, -0.9) {$\frac{1}{4}$};
  \node[font=\bfseries\small, gray] at (0.9, -0.9) {$\frac{1}{4}$};
\end{tikzpicture}
\caption{Tre av fire like deler er fargelagt — dette illustrerer brøken $\frac{3}{4}$.}
\end{figure}
\end{eksempel}

\section{Hva er prosent?}

\begin{definisjon}
\textbf{Prosent} betyr \emph{per hundre}: $1\,\% = \dfrac{1}{100} = 0{,}01$.
\end{definisjon}

\begin{eksempel}[title=Visualisere 25 prosent i et rutenett]
Vi fargeleg 25 av 100 ruter i et 10×10-rutenett.

\begin{figure}[H]
\centering
\begin{tikzpicture}[scale=0.42]
  \fill[mainBlue!50] (0,7.5) rectangle (10,10);
  \fill[mainBlue!50] (0,5)   rectangle (5,7.5);
  \draw[step=1cm, gray!40, thin] (0,0) grid (10,10);
  \draw[very thick, mainBlue] (0,0) rectangle (10,10);
\end{tikzpicture}
\caption{25 av 100 ruter er fargelagt, som viser at $25\,\% = \frac{25}{100} = \frac{1}{4}$.}
\end{figure}
\end{eksempel}

\section{Oppgaver}

\begin{taskbox}{Oppgave 1}
Skriv brøkene som prosent:
\begin{enumerate}[label=\alph*)]
\item $\dfrac{1}{2}$
\item $\dfrac{3}{4}$
\item $\dfrac{1}{5}$
\end{enumerate}
\end{taskbox}

\begin{taskbox}{Oppgave 2}
Fyll ut tabellen:
\begin{center}
\begin{tabular}{lcc}
\toprule
Brøk & Desimaltall & Prosent \\
\midrule
$\dfrac{1}{2}$  & \dots & \dots \\
$\dfrac{1}{4}$  & \dots & \dots \\
$\dfrac{3}{4}$  & \dots & \dots \\
$\dfrac{1}{10}$ & \dots & \dots \\
\bottomrule
\end{tabular}
\end{center}
\end{taskbox}

\section*{Løsningsforslag}
\begin{multicols}{2}
\textbf{Oppgave 1}\\
a) $\frac{1}{2} = \frac{50}{100} = 50\,\%$\\
b) $\frac{3}{4} = \frac{75}{100} = 75\,\%$\\
c) $\frac{1}{5} = \frac{20}{100} = 20\,\%$

\textbf{Oppgave 2}\\
$\frac{1}{2};\; 0{,}5;\; 50\,\%$\\
$\frac{1}{4};\; 0{,}25;\; 25\,\%$\\
$\frac{3}{4};\; 0{,}75;\; 75\,\%$\\
$\frac{1}{10};\; 0{,}1;\; 10\,\%$
\end{multicols}
""",
    },
]


def _get_templates_for_grade(grade: str) -> str:
    """Get TikZ template examples from the graph_templates library for this grade."""
    if not _TEMPLATES_AVAILABLE:
        return ""
    if grade in _TEMPLATE_CACHE:
        return _TEMPLATE_CACHE[grade]
    templates = _get_grade_templates(grade)
    if not templates:
        result = ""
    else:
        # Include up to 4 templates as examples (don't overwhelm the prompt)
        parts = ["\n=== FERDIGLAGDE TikZ-MALER DU KAN KOPIERE OG TILPASSE ===\n"]
        for t in templates[:4]:
            parts.append(f"--- {t.name} ({t.category}) ---")
            parts.append(t.tikz_code.strip())
            parts.append("")
        result = "\n".join(parts)
    _TEMPLATE_CACHE[grade] = result
    return result


def build_author_prompt(
    pedagogical_plan: str,
    grade: str,
    grade_context: str,
    language_instructions: str,
    content_options: dict,
) -> str:
    """Build the user prompt for the author agent."""
    template_examples = _get_templates_for_grade(grade)

    return f"""\
Skriv KOMPLETT LaTeX body-innhold basert på denne pedagogiske planen:

{pedagogical_plan}

Klassetrinn: {grade}
{grade_context}
{language_instructions}

HUSK:
- Start med \\title, \\author, \\date, \\maketitle
- Bruk de obligatoriske LaTeX-miljøene (definisjon, eksempel, taskbox, merk, losning)
- ALDRI \\includegraphics, aldri [INSERT FIGURE], aldri preamble

FIGURER — tre alternativer i prioritert rekkefølge:
1. MAKROER for standard geometri:
   \\MMArettvinklet{{a}}{{b}}{{c}}, \\MMAtrigfig, \\MMArektangel{{l}}{{b}},
   \\MMAromfigurer, \\MMAprosent{{N}}
2. KREATIV TikZ for konteksttilpassede scener (flaggstang+skygge, kart med målestokk,
   formlike trekanter med fargede vinkler, stige mot vegg, person+tre osv.)
   — bruk farger, \\fill, piler, labels!
3. PGFPlots \\begin{{axis}} for funksjonsgrafer
{template_examples}
- ALLE tabeller: booktabs (\\toprule/\\midrule/\\bottomrule), ALDRI | eller \\hline (unntatt posisjonsskjema)
- ALLE beregninger og løsningsforslag MÅ være matematisk korrekte
- INGEN preamble (\\documentclass, \\usepackage osv.)
"""


def build_author_fix_prompt(
    current_latex: str,
    error_report: str,
) -> str:
    """Build a prompt for the author to fix math errors found by SymPy."""
    return f"""\
Følgende matematiske feil ble funnet i ditt LaTeX-innhold:

{error_report}

Her er det nåværende innholdet:

{current_latex}

OPPGAVE: Rett ALLE feilene beskrevet over. Returner HELE det korrigerte LaTeX body-innholdet.
Ikke legg til preamble. Behold all annen tekst uendret.
"""
