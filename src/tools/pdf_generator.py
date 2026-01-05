"""
PDF Generator Tool for MateMaTeX.
Compiles LaTeX content to PDF using pdflatex.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


# Standard preamble for Norwegian math documents - Modern Textbook Style
STANDARD_PREAMBLE = r"""\documentclass[a4paper,11pt]{article}

% Encoding and language
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[norsk]{babel}

% Modern fonts
\usepackage{lmodern}
\usepackage{microtype}

% Mathematics
\usepackage{amsmath, amssymb, amsthm}

% Graphics
\usepackage{tikz, pgfplots}
\pgfplotsset{compat=1.18}
\usetikzlibrary{arrows.meta, calc, patterns, positioning, shapes.geometric}

% Layout
\usepackage[margin=2.5cm]{geometry}
\usepackage{float}
\usepackage{parskip}
\usepackage{enumitem}
\usepackage{booktabs}
\usepackage{multicol}

% Paragraph spacing - more air between paragraphs
\setlength{\parskip}{1em}
\setlength{\parindent}{0pt}

% Float placement - keep figures where they are defined
\floatplacement{figure}{H}

% Colors and colored boxes
\usepackage{xcolor}
\usepackage[most]{tcolorbox}

% --- Custom Color Definitions ---
\definecolor{mainBlue}{RGB}{0, 102, 204}
\definecolor{lightBlue}{RGB}{235, 245, 255}
\definecolor{mainGreen}{RGB}{0, 153, 76}
\definecolor{lightGreen}{RGB}{235, 250, 235}
\definecolor{mainOrange}{RGB}{230, 126, 34}
\definecolor{lightOrange}{RGB}{255, 245, 235}
\definecolor{mainGray}{RGB}{100, 100, 100}
\definecolor{lightGray}{RGB}{245, 245, 245}

% --- Definition Box (Blue) - Modern Style ---
\newtcolorbox{definitionbox}[1][]{
  enhanced,
  colback=lightBlue,
  colframe=mainBlue,
  fonttitle=\bfseries\sffamily,
  title={Definisjon},
  attach boxed title to top left={yshift*=-\tcboxedtitleheight/2, xshift=5mm},
  boxed title style={colback=mainBlue, colframe=mainBlue},
  sharp corners=downhill,
  arc=3mm,
  left=8pt, right=8pt, top=8pt, bottom=8pt,
  #1
}

% Alias for Norwegian naming
\newtcolorbox{definisjon}[1][]{
  enhanced,
  colback=lightBlue,
  colframe=mainBlue,
  fonttitle=\bfseries\sffamily,
  title={Definisjon},
  attach boxed title to top left={yshift*=-\tcboxedtitleheight/2, xshift=5mm},
  boxed title style={colback=mainBlue, colframe=mainBlue},
  sharp corners=downhill,
  arc=3mm,
  left=8pt, right=8pt, top=8pt, bottom=8pt,
  #1
}

% --- Example Box (Green) - Modern Style ---
\newtcolorbox{examplebox}[1][]{
  enhanced,
  colback=lightGreen,
  colframe=mainGreen,
  fonttitle=\bfseries\sffamily,
  title={Eksempel},
  attach boxed title to top left={yshift*=-\tcboxedtitleheight/2, xshift=5mm},
  boxed title style={colback=mainGreen, colframe=mainGreen},
  sharp corners=downhill,
  arc=3mm,
  left=8pt, right=8pt, top=8pt, bottom=8pt,
  #1
}

% Alias for Norwegian naming
\newtcolorbox{eksempel}[1][]{
  enhanced,
  colback=lightGreen,
  colframe=mainGreen,
  fonttitle=\bfseries\sffamily,
  title={Eksempel},
  attach boxed title to top left={yshift*=-\tcboxedtitleheight/2, xshift=5mm},
  boxed title style={colback=mainGreen, colframe=mainGreen},
  sharp corners=downhill,
  arc=3mm,
  left=8pt, right=8pt, top=8pt, bottom=8pt,
  #1
}

% --- Task Box (Gray) - Clean Style ---
\newtcolorbox{taskbox}[1][]{
  enhanced,
  colback=lightGray,
  colframe=mainGray,
  fonttitle=\bfseries\sffamily,
  title={#1},
  attach boxed title to top left={yshift*=-\tcboxedtitleheight/2, xshift=5mm},
  boxed title style={colback=mainGray, colframe=mainGray},
  arc=3mm,
  left=8pt, right=8pt, top=8pt, bottom=8pt
}

% --- Tip/Note Box (Orange/Yellow) ---
\newtcolorbox{tipbox}[1][]{
  enhanced,
  colback=lightOrange,
  colframe=mainOrange,
  fonttitle=\bfseries\sffamily,
  title={Tips},
  attach boxed title to top left={yshift*=-\tcboxedtitleheight/2, xshift=5mm},
  boxed title style={colback=mainOrange, colframe=mainOrange},
  arc=3mm,
  left=8pt, right=8pt, top=8pt, bottom=8pt,
  #1
}

% --- Merk/Warning Box ---
\newtcolorbox{merk}[1][]{
  enhanced,
  colback=yellow!10!white,
  colframe=orange!80!black,
  fonttitle=\bfseries\sffamily,
  title={Merk!},
  arc=3mm,
  left=8pt, right=8pt, top=8pt, bottom=8pt,
  #1
}

% --- Solution Box (for answers) ---
\newtcolorbox{losning}[1][]{
  enhanced,
  colback=white,
  colframe=mainBlue!50,
  fonttitle=\bfseries\sffamily,
  title={Løsning},
  attach boxed title to top left={yshift*=-\tcboxedtitleheight/2, xshift=5mm},
  boxed title style={colback=mainBlue!50, colframe=mainBlue!50},
  arc=3mm,
  left=8pt, right=8pt, top=8pt, bottom=8pt,
  #1
}

% Theorem environments (fallback for simple usage)
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
\titleformat{\section}{\Large\bfseries\sffamily\color{mainBlue}}{\thesection}{1em}{}
\titleformat{\subsection}{\large\bfseries\sffamily\color{mainBlue!80}}{\thesubsection}{1em}{}

"""


def clean_ai_output(latex_content: str) -> str:
    """
    Clean up AI-generated LaTeX content.
    Removes markdown code blocks and extracts clean LaTeX.
    
    Args:
        latex_content: Raw AI output that may contain markdown formatting.
    
    Returns:
        Clean LaTeX content.
    """
    import re
    
    content = latex_content.strip()
    
    # Remove markdown code blocks (```latex ... ``` or ``` ... ```)
    # Pattern matches ```latex or ``` at start and ``` at end
    code_block_pattern = r'```(?:latex|tex)?\s*\n?(.*?)\n?```'
    matches = re.findall(code_block_pattern, content, re.DOTALL)
    
    if matches:
        # If we found code blocks, use the content from the largest one
        content = max(matches, key=len).strip()
    
    # If content still has markdown code fences, remove them
    content = re.sub(r'^```(?:latex|tex)?\s*\n?', '', content)
    content = re.sub(r'\n?```\s*$', '', content)
    
    # Check for duplicate document structure
    # If there's \begin{document} followed by another \documentclass, extract inner content
    doc_start_count = content.count(r'\begin{document}')
    doc_class_count = content.count(r'\documentclass')
    
    if doc_start_count > 1 or doc_class_count > 1:
        # There's a nested document - extract the inner content
        # Find the LAST \begin{document} and LAST \end{document}
        inner_match = re.search(
            r'\\begin\{document\}(.*?)\\end\{document\}\s*$',
            content,
            re.DOTALL
        )
        if inner_match:
            # Return just the body content (without the nested preamble)
            inner_content = inner_match.group(1).strip()
            
            # Check if inner content itself has another begin/end document
            if r'\begin{document}' in inner_content:
                # Extract from the innermost document
                innermost = re.search(
                    r'\\begin\{document\}(.*?)\\end\{document\}',
                    inner_content,
                    re.DOTALL
                )
                if innermost:
                    inner_content = innermost.group(1).strip()
            
            return inner_content
    
    return content


def ensure_preamble(latex_content: str) -> str:
    """
    Ensure the LaTeX content has a valid preamble.
    If the content doesn't start with \\documentclass, prepend the standard preamble.

    Args:
        latex_content: The LaTeX content to check.

    Returns:
        LaTeX content with a guaranteed preamble.
    """
    content_stripped = latex_content.strip()

    # Check if content already has a documentclass
    if content_stripped.startswith(r"\documentclass"):
        # Content has preamble, but let's ensure critical packages are present
        return _ensure_critical_packages(content_stripped)

    # Check if content starts with \begin{document} (preamble missing entirely)
    if content_stripped.startswith(r"\begin{document}"):
        return STANDARD_PREAMBLE + content_stripped

    # Content is just the body - wrap it completely
    return STANDARD_PREAMBLE + r"\begin{document}" + "\n\n" + content_stripped + "\n\n" + r"\end{document}"


def _ensure_critical_packages(latex_content: str) -> str:
    """
    Ensure critical packages are present in existing preamble.
    Injects missing packages after \\documentclass line if needed.

    Args:
        latex_content: LaTeX content that already has a documentclass.

    Returns:
        LaTeX content with critical packages ensured.
    """
    critical_packages = [
        (r"\usepackage[utf8]{inputenc}", r"[utf8]{inputenc}"),
        (r"\usepackage[norsk]{babel}", r"babel"),
        (r"\usepackage{amsmath", r"amsmath"),
        (r"\usepackage{tikz", r"tikz"),
        (r"\usepackage{pgfplots}", r"pgfplots"),
        (r"\usepackage[most]{tcolorbox}", r"tcolorbox"),
        (r"\usepackage{xcolor}", r"xcolor"),
        (r"\usepackage{float}", r"float"),
    ]

    missing_packages = []
    for package_line, check_string in critical_packages:
        if check_string not in latex_content:
            missing_packages.append(package_line)

    if not missing_packages:
        return latex_content

    # Find the end of documentclass line and inject missing packages
    lines = latex_content.split("\n")
    result_lines = []
    packages_injected = False

    for line in lines:
        result_lines.append(line)
        if not packages_injected and line.strip().startswith(r"\documentclass"):
            result_lines.append("\n% Auto-injected critical packages")
            result_lines.extend(missing_packages)
            result_lines.append("")
            packages_injected = True

    return "\n".join(result_lines)


def compile_latex_to_pdf(
    latex_content: str,
    filename: str,
    output_dir: Optional[str] = None,
    cleanup_aux: bool = True
) -> str:
    """
    Compile LaTeX content to PDF using pdflatex.

    Args:
        latex_content: The LaTeX source code to compile.
        filename: Base name for the output file (without extension).
        output_dir: Directory to save output files. Defaults to 'output/'.
        cleanup_aux: Whether to remove auxiliary files after compilation.

    Returns:
        Path to the generated PDF file.

    Raises:
        FileNotFoundError: If pdflatex is not installed.
        RuntimeError: If LaTeX compilation fails.
    """
    # Set default output directory
    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent / "output"
    else:
        output_dir = Path(output_dir)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Ensure filename doesn't have extension
    filename = filename.replace(".tex", "").replace(".pdf", "")

    # Clean up AI output (remove markdown blocks, nested documents)
    latex_content = clean_ai_output(latex_content)
    
    # Ensure valid preamble
    latex_content = ensure_preamble(latex_content)

    # Define file paths
    tex_file = output_dir / f"{filename}.tex"
    pdf_file = output_dir / f"{filename}.pdf"
    log_file = output_dir / f"{filename}.log"

    # Write the .tex file
    tex_file.write_text(latex_content, encoding="utf-8")
    print(f"[OK] LaTeX source saved to: {tex_file}")

    # Check if pdflatex is available
    try:
        subprocess.run(
            ["pdflatex", "--version"],
            capture_output=True,
            check=True
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "pdflatex not found. Please install TeX Live or MiKTeX.\n"
            "- Windows: https://miktex.org/download\n"
            "- Linux: sudo apt install texlive-full\n"
            "- macOS: brew install --cask mactex"
        )

    # Run pdflatex (twice for proper cross-references)
    for run_num in range(2):
        print(f"  Running pdflatex (pass {run_num + 1}/2)...")
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={output_dir}",
                str(tex_file)
            ],
            capture_output=True,
            text=True,
            cwd=output_dir
        )

        if result.returncode != 0:
            # Extract relevant error information from log
            error_msg = _extract_latex_errors(log_file, result.stdout)
            raise RuntimeError(
                f"LaTeX compilation failed:\n{error_msg}\n\n"
                f"Full log available at: {log_file}"
            )

    # Verify PDF was created
    if not pdf_file.exists():
        raise RuntimeError(
            f"PDF was not generated. Check the log file: {log_file}"
        )

    print(f"[OK] PDF generated: {pdf_file}")

    # Cleanup auxiliary files
    if cleanup_aux:
        _cleanup_auxiliary_files(output_dir, filename)

    return str(pdf_file)


def _extract_latex_errors(log_file: Path, stdout: str) -> str:
    """
    Extract meaningful error messages from LaTeX output.

    Args:
        log_file: Path to the .log file.
        stdout: Standard output from pdflatex.

    Returns:
        Formatted error message string.
    """
    errors = []

    # Try to read the log file for detailed errors
    if log_file.exists():
        try:
            log_content = log_file.read_text(encoding="utf-8", errors="ignore")
            # Find lines starting with "!" which indicate errors
            for line in log_content.split("\n"):
                if line.startswith("!"):
                    errors.append(line)
                elif errors and line.strip() and not line.startswith("!"):
                    # Include context lines after error
                    if len(errors) < 10:
                        errors.append(line)
        except Exception:
            pass

    if errors:
        return "\n".join(errors[:10])  # Limit to first 10 error lines

    # Fallback to stdout if log parsing failed
    if stdout:
        return stdout[-2000:]  # Last 2000 characters of output

    return "Unknown error. Check the log file for details."


def _cleanup_auxiliary_files(output_dir: Path, filename: str) -> None:
    """
    Remove auxiliary files generated by pdflatex.

    Args:
        output_dir: Directory containing the files.
        filename: Base name of the files.
    """
    aux_extensions = [".aux", ".log", ".out", ".toc", ".lof", ".lot", ".fls", ".fdb_latexmk"]

    for ext in aux_extensions:
        aux_file = output_dir / f"{filename}{ext}"
        if aux_file.exists():
            try:
                aux_file.unlink()
            except Exception:
                pass  # Ignore cleanup errors


def validate_latex_syntax(latex_content: str) -> tuple[bool, list[str]]:
    """
    Perform basic validation of LaTeX syntax.

    Args:
        latex_content: The LaTeX content to validate.

    Returns:
        Tuple of (is_valid, list of issues found).
    """
    issues = []

    # Check for matching begin/end document
    if r"\begin{document}" not in latex_content:
        issues.append("Missing \\begin{document}")
    if r"\end{document}" not in latex_content:
        issues.append("Missing \\end{document}")

    # Check for unmatched braces (basic check)
    open_braces = latex_content.count("{")
    close_braces = latex_content.count("}")
    if open_braces != close_braces:
        issues.append(f"Unmatched braces: {open_braces} open, {close_braces} close")

    # Check for common environment mismatches
    environments = [
        "equation", "align", "itemize", "enumerate", "tikzpicture", "figure", "table",
        "definitionbox", "examplebox", "taskbox", "tipbox",
        "definisjon", "eksempel", "merk", "losning"
    ]
    for env in environments:
        opens = latex_content.count(f"\\begin{{{env}}}")
        closes = latex_content.count(f"\\end{{{env}}}")
        if opens != closes:
            issues.append(f"Unmatched {env} environment: {opens} begin, {closes} end")

    return len(issues) == 0, issues
