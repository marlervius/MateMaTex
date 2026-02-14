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
