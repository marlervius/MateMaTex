"""
Standard LaTeX preamble for MateMaTeX documents.
Self-contained — no dependency on v1 src/ codebase.
"""

from __future__ import annotations


STANDARD_PREAMBLE = r"""\documentclass[a4paper,11pt]{article}

% Encoding and language
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[norsk]{babel}

% Modern fonts
\usepackage{lmodern}
\usepackage{microtype}

% Mathematics (mathtools extends amsmath with better spacing)
\usepackage{mathtools}
\usepackage{amssymb, amsthm}
\usepackage{bm}
\usepackage{siunitx}

% Graphics
\usepackage{tikz, pgfplots}
\pgfplotsset{compat=1.18}
\usetikzlibrary{arrows.meta, calc, patterns, positioning, shapes.geometric, decorations.pathreplacing}

% Layout
\usepackage[margin=2.5cm]{geometry}
\usepackage{float}
\usepackage{parskip}
\usepackage{enumitem}
\usepackage{booktabs}
\usepackage{multicol}

% Paragraph spacing
\setlength{\parskip}{0.8em}
\setlength{\parindent}{0pt}
\setlist{itemsep=0.3em, parsep=0.2em, topsep=0.3em}

% Float placement
\floatplacement{figure}{H}

% Colors and colored boxes
\usepackage{xcolor}
\usepackage[most]{tcolorbox}

% Custom Color Definitions (must come BEFORE hyperref)
\definecolor{mainBlue}{RGB}{0, 102, 204}
\definecolor{lightBlue}{RGB}{230, 242, 255}
\definecolor{mainGreen}{RGB}{0, 153, 76}
\definecolor{lightGreen}{RGB}{232, 250, 240}
\definecolor{mainOrange}{RGB}{230, 126, 34}
\definecolor{lightOrange}{RGB}{255, 245, 235}
\definecolor{mainPurple}{RGB}{102, 51, 153}
\definecolor{lightPurple}{RGB}{245, 240, 255}
\definecolor{mainTeal}{RGB}{0, 128, 128}
\definecolor{lightTeal}{RGB}{235, 250, 250}
\definecolor{mainGray}{RGB}{80, 80, 90}
\definecolor{lightGray}{RGB}{248, 248, 252}

% Hyperlinks (load AFTER color definitions)
\usepackage[colorlinks=true, linkcolor=mainBlue, urlcolor=mainBlue, citecolor=mainGreen]{hyperref}

% Shared box style
\tcbset{matebox/.style={
  enhanced, breakable,
  arc=3mm,
  left=8pt, right=8pt, top=8pt, bottom=8pt,
  attach boxed title to top left={yshift*=-\tcboxedtitleheight/2, xshift=5mm},
  sharp corners=downhill,
}}

% Definition Box (Blue)
\newtcolorbox{definitionbox}[1][]{
  matebox,
  colback=lightBlue, colframe=mainBlue,
  fonttitle=\bfseries\sffamily, title={Definisjon},
  boxed title style={colback=mainBlue, colframe=mainBlue},
  #1
}
\newtcolorbox{definisjon}[1][]{
  matebox,
  colback=lightBlue, colframe=mainBlue,
  fonttitle=\bfseries\sffamily, title={Definisjon},
  boxed title style={colback=mainBlue, colframe=mainBlue},
  #1
}

% Example Box (Green)
\newtcolorbox{examplebox}[1][]{
  matebox,
  colback=lightGreen, colframe=mainGreen,
  fonttitle=\bfseries\sffamily, title={Eksempel},
  boxed title style={colback=mainGreen, colframe=mainGreen},
  #1
}
\newtcolorbox{eksempel}[1][]{
  matebox,
  colback=lightGreen, colframe=mainGreen,
  fonttitle=\bfseries\sffamily, title={Eksempel},
  boxed title style={colback=mainGreen, colframe=mainGreen},
  #1
}

% Task Box (Purple)
\newtcolorbox{taskbox}[1][]{
  matebox,
  colback=lightPurple, colframe=mainPurple,
  fonttitle=\bfseries\sffamily\color{white}, title={#1},
  boxed title style={colback=mainPurple, colframe=mainPurple},
  left=10pt, right=10pt, top=10pt, bottom=10pt,
}

% Tip/Note Box (Orange)
\newtcolorbox{tipbox}[1][]{
  matebox,
  colback=lightOrange, colframe=mainOrange,
  fonttitle=\bfseries\sffamily, title={Tips},
  boxed title style={colback=mainOrange, colframe=mainOrange},
  #1
}

% Merk/Warning Box (Orange)
\newtcolorbox{merk}[1][]{
  matebox,
  colback=lightOrange, colframe=mainOrange,
  fonttitle=\bfseries\sffamily, title={Merk!},
  boxed title style={colback=mainOrange, colframe=mainOrange},
  #1
}

% Solution Box (Teal)
\newtcolorbox{losning}[1][]{
  matebox,
  colback=lightTeal, colframe=mainTeal,
  fonttitle=\bfseries\sffamily\color{white}, title={Løsning},
  boxed title style={colback=mainTeal, colframe=mainTeal},
  left=10pt, right=10pt, top=10pt, bottom=10pt,
  #1
}

% Theorem environments (fallback)
\newtheorem{theorem}{Teorem}[section]
\newtheorem{definition}[theorem]{Definisjon}
\newtheorem{example}[theorem]{Eksempel}
\newtheorem{exercise}{Oppgave}[section]

% Custom math commands
\newcommand{\N}{\mathbb{N}}
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\R}{\mathbb{R}}

% Section styling
\usepackage{titlesec}
\titleformat{\section}{\Large\bfseries\sffamily\color{mainBlue}}{\thesection}{1em}{}[\color{mainBlue}\titlerule]
\titleformat{\subsection}{\large\bfseries\sffamily\color{mainPurple}}{\thesubsection}{1em}{}

% Graph defaults
\pgfplotsset{
    every axis/.append style={
        width=0.75\textwidth,
        height=0.5\textwidth,
        line width=0.8pt,
        tick style={line width=0.6pt},
        tick label style={font=\small},
        label style={font=\small},
        legend style={font=\small, draw=none, fill=white, fill opacity=0.8},
        grid=major,
        grid style={dashed, gray!30},
        axis lines=middle,
    },
    every axis plot/.append style={
        line width=1.2pt,
    },
    cycle list={
        {mainBlue, thick},
        {mainGreen, thick},
        {mainOrange, thick},
        {mainPurple, thick},
        {mainTeal, thick},
    },
}

% ============================================================
% MateMaTeX Figure Macros — AI calls these, never raw TikZ
% ============================================================

% \MMArettvinklet{a}{b}{c}  — right-angled triangle, legs a,b, hypotenuse c
% Usage: \MMArettvinklet{3}{4}{5}
\newcommand{\MMArettvinklet}[3]{%
  \begin{tikzpicture}[scale=0.9, font=\small]
    \coordinate (A) at (0,0);
    \coordinate (B) at (#1,0);
    \coordinate (C) at (#1,#2);
    \fill[lightBlue!60] (A) -- (B) -- (C) -- cycle;
    \draw[thick, mainBlue] (A) -- (B) -- (C) -- cycle;
    \draw[mainBlue] (#1,0.3) -- (#1-0.3,0.3) -- (#1-0.3,0);
    \node[below] at (#1/2,0) {$a = #1$};
    \node[right] at (#1,#2/2) {$b = #2$};
    \node[above left] at (#1/2,#2/2) {$c = #3$};
    \node[below left] at (A) {$A$};
    \node[below right] at (B) {$B$};
    \node[above right] at (C) {$C$};
  \end{tikzpicture}%
}

% \MMAtrigfig  — right-angled triangle with trig labels
\newcommand{\MMAtrigfig}{%
  \begin{tikzpicture}[scale=0.85, font=\small]
    \coordinate (O) at (0,0);
    \coordinate (A) at (5,0);
    \coordinate (B) at (5,3.75);
    \fill[lightBlue!50] (O) -- (A) -- (B) -- cycle;
    \draw[thick, mainBlue] (O) -- (A) -- (B) -- cycle;
    \draw[mainBlue] (5,0.35) -- (4.65,0.35) -- (4.65,0);
    \draw[mainOrange, thick] (0.8,0) arc(0:36.87:0.8);
    \node at (1.2,0.28) {$v$};
    \node[below, mainBlue] at (2.5,0) {Hosliggende};
    \node[right, mainBlue] at (5,1.875) {Motstående};
    \node[above left, mainBlue] at (2.5,2.0) {Hypotenus};
    \node[below left] at (O) {$O$};
    \node[below right] at (A) {$A$};
    \node[above right] at (B) {$B$};
  \end{tikzpicture}%
}

% \MMArektangel{l}{b}  — rectangle with dimension arrows
% Usage: \MMArektangel{5}{3}
\newcommand{\MMArektangel}[2]{%
  \begin{tikzpicture}[scale=0.8, font=\small]
    \fill[lightBlue!40] (0,0) rectangle (#1,#2);
    \draw[thick, mainBlue] (0,0) rectangle (#1,#2);
    \node at (#1/2, #2/2) {$A = #1 \cdot #2$};
    \draw[<->, mainOrange, thick] (0,-0.5) -- (#1,-0.5) node[midway,below] {$#1$ cm};
    \draw[<->, mainOrange, thick] (#1+0.5,0) -- (#1+0.5,#2) node[midway,right] {$#2$ cm};
  \end{tikzpicture}%
}

% \MMAsylinder  — simple cylinder
\newcommand{\MMAsylinder}{%
  \begin{tikzpicture}[scale=0.7, font=\small]
    \fill[lightBlue!30] (-1.2,-2.5) arc(180:360:1.2 and 0.4) -- (1.2,0) arc(0:180:1.2 and 0.4) -- cycle;
    \fill[lightBlue!50] (0,0) ellipse (1.2 and 0.4);
    \draw[thick, mainBlue] (0,0) ellipse (1.2 and 0.4);
    \draw[thick, mainBlue] (-1.2,0) -- (-1.2,-2.5);
    \draw[thick, mainBlue] (1.2,0) -- (1.2,-2.5);
    \draw[thick, mainBlue] (0,-2.5) ellipse (1.2 and 0.4);
    \draw[<->, mainOrange, thick] (1.6,0) -- (1.6,-2.5) node[midway,right]{$h$};
    \draw[<->, mainOrange, thick] (0,0) -- (1.2,0) node[midway,above]{$r$};
    \node[below] at (0,-3.1) {Sylinder};
  \end{tikzpicture}%
}

% \MMAkjegle  — simple cone
\newcommand{\MMAkjegle}{%
  \begin{tikzpicture}[scale=0.7, font=\small]
    \fill[lightBlue!30] (-1.2,-2.5) -- (0,0) -- (1.2,-2.5) arc(0:-180:1.2 and 0.4) -- cycle;
    \draw[thick, mainBlue] (-1.2,-2.5) -- (0,0) -- (1.2,-2.5);
    \draw[thick, mainBlue] (0,-2.5) ellipse (1.2 and 0.4);
    \draw[<->, mainOrange, thick] (1.6,0) -- (1.6,-2.5) node[midway,right]{$h$};
    \draw[<->, mainOrange, thick] (0,-2.5) -- (1.2,-2.5) node[midway,below]{$r$};
    \node[below] at (0,-3.1) {Kjegle};
  \end{tikzpicture}%
}

% \MMAkule  — simple sphere
\newcommand{\MMAkule}{%
  \begin{tikzpicture}[scale=0.7, font=\small]
    \fill[lightBlue!30] (0,0) circle (1.5);
    \draw[thick, mainBlue] (0,0) circle (1.5);
    \draw[thick, mainBlue, dashed] (0,0) ellipse (1.5 and 0.45);
    \draw[<->, mainOrange, thick] (0,0) -- (1.5,0) node[midway,above]{$r$};
    \node[below] at (0,-1.9) {Kule};
  \end{tikzpicture}%
}

% \MMAromfigurer  — all three solids side by side
\newcommand{\MMAromfigurer}{%
  \begin{figure}[H]
  \centering
  \MMAsylinder\qquad\MMAkjegle\qquad\MMAkule
  \caption{Sylinder, kjegle og kule med radius $r$ og høyde $h$.}
  \end{figure}%
}

% \MMAprosent{N}  — 10x10 percent grid with N cells filled
% Usage: \MMAprosent{35}  →  35% filled
\newcommand{\MMAprosent}[1]{%
  \begin{tikzpicture}[scale=0.35, font=\scriptsize]
    \foreach \r in {0,...,9} {
      \foreach \c in {0,...,9} {
        \pgfmathsetmacro{\idx}{int(\r*10 + \c + 1)}
        \ifnum\idx>#1
          \fill[lightGray] (\c,\r) rectangle (\c+1,\r+1);
        \else
          \fill[mainBlue!70] (\c,\r) rectangle (\c+1,\r+1);
        \fi
        \draw[white, thin] (\c,\r) rectangle (\c+1,\r+1);
      }
    }
    \draw[thick, mainBlue] (0,0) rectangle (10,10);
  \end{tikzpicture}%
}

% \MMAGraf command is NOT a macro — use pgfplots \begin{axis} directly for graphs.
% ============================================================

% Header/Footer
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\color{mainGray}\textit{Generert av MateMaTeX AI}}
\fancyhead[R]{\small\color{mainGray}\today}
\fancyfoot[C]{\small\color{mainGray}\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}

\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\small\color{mainGray}\thepage}\renewcommand{\headrulewidth}{0pt}}

"""


def wrap_with_preamble(body_content: str) -> str:
    """
    Wrap body content with the standard preamble.

    Args:
        body_content: LaTeX body content (no \\documentclass).

    Returns:
        Complete LaTeX document ready for compilation.
    """
    body = body_content.strip()

    return (
        STANDARD_PREAMBLE
        + r"\begin{document}"
        + "\n"
        + r"\thispagestyle{plain}"
        + "\n\n"
        + body
        + "\n\n"
        + r"\end{document}"
    )
