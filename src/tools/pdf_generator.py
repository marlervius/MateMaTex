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

% --- Task Box (Purple/Blue) - Elegant Worksheet Style ---
\newtcolorbox{taskbox}[1][]{
  enhanced,
  colback=lightPurple,
  colframe=mainPurple,
  fonttitle=\bfseries\sffamily\color{white},
  title={#1},
  attach boxed title to top left={yshift*=-\tcboxedtitleheight/2, xshift=5mm},
  boxed title style={colback=mainPurple, colframe=mainPurple},
  sharp corners=downhill,
  arc=3mm,
  left=10pt, right=10pt, top=10pt, bottom=10pt,
  shadow={2mm}{-2mm}{0mm}{black!20}
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

% --- Solution Box (for answers) - Teal Style ---
\newtcolorbox{losning}[1][]{
  enhanced,
  colback=lightTeal,
  colframe=mainTeal,
  fonttitle=\bfseries\sffamily\color{white},
  title={Løsning},
  attach boxed title to top left={yshift*=-\tcboxedtitleheight/2, xshift=5mm},
  boxed title style={colback=mainTeal, colframe=mainTeal},
  sharp corners=downhill,
  arc=3mm,
  left=10pt, right=10pt, top=10pt, bottom=10pt,
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
\titleformat{\section}{\Large\bfseries\sffamily\color{mainBlue}}{\thesection}{1em}{}[\color{mainBlue}\titlerule]
\titleformat{\subsection}{\large\bfseries\sffamily\color{mainPurple}}{\thesubsection}{1em}{}

% Colored graph defaults
\pgfplotsset{
    every axis/.append style={
        line width=1pt,
        tick style={line width=0.8pt}
    },
    every axis plot/.append style={
        line width=1.5pt
    }
}

% Header/Footer styling for worksheets
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\color{mainGray}\textit{Generert av MateMaTeX AI}}
\fancyhead[R]{\small\color{mainGray}\today}
\fancyfoot[C]{\small\color{mainGray}\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}

"""


def clean_ai_output(latex_content: str) -> str:
    """
    Clean up AI-generated LaTeX content.
    
    1. Removes markdown code blocks
    2. Strips any preamble the AI generated (documentclass, usepackage, etc.)
    3. Extracts only the body content
    
    The system's STANDARD_PREAMBLE is always used, so AI-generated preambles
    must be removed to prevent duplicates and compilation errors.
    
    Args:
        latex_content: Raw AI output that may contain markdown formatting.
    
    Returns:
        Clean LaTeX body content (no preamble).
    """
    import re
    
    content = latex_content.strip()
    
    # Step 1: Remove markdown code blocks (```latex ... ``` or ``` ... ```)
    code_block_pattern = r'```(?:latex|tex)?\s*\n?(.*?)\n?```'
    matches = re.findall(code_block_pattern, content, re.DOTALL)
    
    if matches:
        content = max(matches, key=len).strip()
    
    # Remove remaining markdown fences
    content = re.sub(r'^```(?:latex|tex)?\s*\n?', '', content)
    content = re.sub(r'\n?```\s*$', '', content)
    
    # Step 2: Strip AI-generated preamble
    # If there's a \begin{document}, extract just the body content
    if r'\begin{document}' in content:
        # Find body content between \begin{document} and \end{document}
        body_match = re.search(
            r'\\begin\{document\}(.*?)(?:\\end\{document\}|$)',
            content,
            re.DOTALL
        )
        if body_match:
            content = body_match.group(1).strip()
            
            # Handle nested documents (AI sometimes generates double wrapping)
            if r'\begin{document}' in content:
                inner_match = re.search(
                    r'\\begin\{document\}(.*?)(?:\\end\{document\}|$)',
                    content,
                    re.DOTALL
                )
                if inner_match:
                    content = inner_match.group(1).strip()
    
    # Step 3: Remove stray preamble commands that slipped through
    # These should NEVER be in body content
    preamble_patterns = [
        r'\\documentclass\[?[^\]]*\]?\{[^}]*\}',
        r'\\usepackage\[?[^\]]*\]?\{[^}]*\}',
        r'\\newtcolorbox\{[^}]*\}.*?(?=\n\n|\n\\)',
        r'\\newtcolorbox\[[^\]]*\]\{[^}]*\}.*?(?=\n\n|\n\\)',
        r'\\definecolor\{[^}]*\}\{[^}]*\}\{[^}]*\}',
        r'\\newtheorem\{[^}]*\}.*',
        r'\\newtheorem\[[^\]]*\]\{[^}]*\}.*',
        r'\\pgfplotsset\{compat=[^}]*\}',
        r'\\usetikzlibrary\{[^}]*\}',
        r'\\titleformat\{[^}]*\}.*',
        r'\\pagestyle\{[^}]*\}',
        r'\\fancyhf\{\}',
        r'\\fancyhead\[?[^\]]*\]?\{[^}]*\}',
        r'\\fancyfoot\[?[^\]]*\]?\{[^}]*\}',
        r'\\renewcommand\{\\headrulewidth\}.*',
        r'\\renewcommand\{\\footrulewidth\}.*',
        r'\\setlength\{\\parskip\}.*',
        r'\\setlength\{\\parindent\}.*',
        r'\\floatplacement\{[^}]*\}\{[^}]*\}',
    ]
    
    for pattern in preamble_patterns:
        content = re.sub(pattern, '', content)
    
    # Remove any standalone \end{document} at the end
    content = re.sub(r'\\end\{document\}\s*$', '', content)
    
    # Clean up multiple blank lines left after stripping
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    return content.strip()


def ensure_preamble(latex_content: str) -> str:
    """
    Ensure the LaTeX content has a valid preamble.
    
    After clean_ai_output(), the content should always be just body content.
    This function wraps it with the STANDARD_PREAMBLE.
    
    If the content somehow still has a \\documentclass (legacy path),
    we strip it and use our own preamble instead — our preamble defines
    all the custom environments (definisjon, eksempel, taskbox, etc.).

    Args:
        latex_content: The LaTeX content to check.

    Returns:
        Complete LaTeX document with standard preamble.
    """
    import re
    
    content_stripped = latex_content.strip()

    # If content has a documentclass, it means clean_ai_output didn't fully strip it.
    # Extract just the body and use our standard preamble.
    if r"\documentclass" in content_stripped:
        body_match = re.search(
            r'\\begin\{document\}(.*?)(?:\\end\{document\}|$)',
            content_stripped,
            re.DOTALL
        )
        if body_match:
            content_stripped = body_match.group(1).strip()
        else:
            # No \begin{document} found — try to skip everything before \title or \section
            title_match = re.search(r'(\\(?:title|section|maketitle).*)', content_stripped, re.DOTALL)
            if title_match:
                content_stripped = title_match.group(1).strip()

    # Remove any stray \begin{document} or \end{document}
    content_stripped = re.sub(r'\\begin\{document\}', '', content_stripped)
    content_stripped = re.sub(r'\\end\{document\}', '', content_stripped)
    content_stripped = content_stripped.strip()

    # Wrap with standard preamble
    return (
        STANDARD_PREAMBLE
        + r"\begin{document}"
        + "\n\n"
        + content_stripped
        + "\n\n"
        + r"\end{document}"
    )


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
    cleanup_aux: bool = True,
    max_retries: int = 3
) -> str:
    """
    Compile LaTeX content to PDF using pdflatex.

    Args:
        latex_content: The LaTeX source code to compile.
        filename: Base name for the output file (without extension).
        output_dir: Directory to save output files. Defaults to 'output/'.
        cleanup_aux: Whether to remove auxiliary files after compilation.
        max_retries: Maximum number of compilation attempts for recoverable errors.

    Returns:
        Path to the generated PDF file.

    Raises:
        FileNotFoundError: If pdflatex is not installed.
        RuntimeError: If LaTeX compilation fails after all retries.
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
    
    # Fix common AI-generated LaTeX issues
    latex_content = _fix_common_latex_issues(latex_content)
    
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
    pdflatex_cmd = _find_pdflatex()
    if not pdflatex_cmd:
        raise FileNotFoundError(
            "pdflatex not found. Please install TeX Live or MiKTeX.\n"
            "- Windows: https://miktex.org/download\n"
            "- Linux: sudo apt install texlive-full\n"
            "- macOS: brew install --cask mactex\n\n"
            "After installation, restart your terminal/IDE."
        )

    # Run pdflatex with retry logic
    last_error = None
    for attempt in range(max_retries):
        success = True
        
        # Run pdflatex (twice for proper cross-references)
        for run_num in range(2):
            print(f"  Running pdflatex (attempt {attempt + 1}, pass {run_num + 1}/2)...")
            
            try:
                result = subprocess.run(
                    [
                        pdflatex_cmd,
                        "-interaction=nonstopmode",
                        "-halt-on-error",
                        f"-output-directory={output_dir}",
                        str(tex_file)
                    ],
                    capture_output=True,
                    text=True,
                    cwd=output_dir,
                    timeout=120  # 2 minute timeout per pass
                )
            except subprocess.TimeoutExpired:
                last_error = "LaTeX compilation timed out (>2 minutes). The document may be too complex."
                success = False
                break

            if result.returncode != 0:
                # Extract error and try to fix
                error_msg = _extract_latex_errors(log_file, result.stdout)
                last_error = error_msg
                
                # Try to auto-fix common errors
                if attempt < max_retries - 1:
                    fixed_content = _try_autofix_latex(latex_content, error_msg)
                    if fixed_content != latex_content:
                        latex_content = fixed_content
                        tex_file.write_text(latex_content, encoding="utf-8")
                        print(f"  [RETRY] Auto-fixed LaTeX issues, retrying...")
                
                success = False
                break
        
        if success:
            break
    else:
        # All retries exhausted
        raise RuntimeError(
            f"LaTeX compilation failed after {max_retries} attempts:\n{last_error}\n\n"
            f"Full log available at: {log_file}\n"
            f"LaTeX source at: {tex_file}"
        )

    # Verify PDF was created
    if not pdf_file.exists():
        raise RuntimeError(
            f"PDF was not generated despite successful compilation.\n"
            f"Check the log file: {log_file}"
        )

    print(f"[OK] PDF generated: {pdf_file}")

    # Cleanup auxiliary files
    if cleanup_aux:
        _cleanup_auxiliary_files(output_dir, filename)

    return str(pdf_file)


def _find_pdflatex() -> Optional[str]:
    """
    Find pdflatex executable on the system.
    
    Returns:
        Path to pdflatex or None if not found.
    """
    import shutil
    
    # Try standard command first
    if shutil.which("pdflatex"):
        return "pdflatex"
    
    # Common installation paths on Windows
    windows_paths = [
        r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe",
        r"C:\Program Files (x86)\MiKTeX\miktex\bin\pdflatex.exe",
        r"C:\texlive\2024\bin\windows\pdflatex.exe",
        r"C:\texlive\2023\bin\windows\pdflatex.exe",
    ]
    
    for path in windows_paths:
        if Path(path).exists():
            return path
    
    return None


def _fix_common_latex_issues(latex_content: str) -> str:
    """
    Fix common LaTeX issues that AI models tend to generate.
    
    Args:
        latex_content: The LaTeX content to fix.
    
    Returns:
        Fixed LaTeX content.
    """
    import re
    
    content = latex_content
    
    # Fix unescaped percent signs in text (not comments)
    # This is tricky - we need to avoid breaking actual comments
    # Only fix % that appears after letters/numbers without backslash
    content = re.sub(r'(\d)%(?!\s*$)', r'\1\\%', content)
    
    # Fix unescaped ampersands outside of tables/align
    # (This is context-sensitive, so we're conservative)
    
    # Fix common Norwegian character issues
    content = content.replace('æ', 'æ')  # Ensure proper encoding
    content = content.replace('ø', 'ø')
    content = content.replace('å', 'å')
    
    # Fix missing spaces after commands
    content = re.sub(r'\\textbf\{([^}]+)\}(?=[a-zA-ZæøåÆØÅ])', r'\\textbf{\1} ', content)
    
    # Fix double backslashes that should be single (common AI mistake)
    content = re.sub(r'\\\\(?=begin|end|section|subsection|textbf|frac|sqrt)', r'\\', content)
    
    # Remove any stray markdown that might have slipped through
    content = re.sub(r'^\s*#{1,6}\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', content)
    content = re.sub(r'\*([^*]+)\*', r'\\textit{\1}', content)
    
    # Fix missing closing braces in common patterns
    # Count braces to detect obvious mismatches
    open_count = content.count('{')
    close_count = content.count('}')
    
    if open_count > close_count:
        # Add missing closing braces at the end (before \end{document} if present)
        diff = open_count - close_count
        if r'\end{document}' in content:
            content = content.replace(r'\end{document}', '}' * diff + r'\end{document}')
        else:
            content += '}' * diff
    
    return content


def _try_autofix_latex(latex_content: str, error_msg: str) -> str:
    """
    Try to automatically fix LaTeX errors based on error message.
    
    Args:
        latex_content: The LaTeX content with errors.
        error_msg: The error message from pdflatex.
    
    Returns:
        Potentially fixed LaTeX content.
    """
    import re
    
    content = latex_content
    
    # Fix undefined control sequence errors
    if "Undefined control sequence" in error_msg:
        # Extract the undefined command
        match = re.search(r'\\([a-zA-Z]+)', error_msg)
        if match:
            undefined_cmd = match.group(1)
            # Common fixes for undefined commands
            fixes = {
                'R': r'\mathbb{R}',  # Real numbers
                'N': r'\mathbb{N}',  # Natural numbers
                'Z': r'\mathbb{Z}',  # Integers
                'Q': r'\mathbb{Q}',  # Rationals
            }
            if undefined_cmd in fixes:
                content = content.replace(f'\\{undefined_cmd}', fixes[undefined_cmd])
    
    # Fix missing $ errors (math mode)
    if "Missing $" in error_msg:
        # This is harder to auto-fix, but we can try wrapping isolated math symbols
        pass
    
    # Fix runaway argument (usually missing closing brace)
    if "Runaway argument" in error_msg:
        # Try to find and close unclosed environments
        environments = ['definisjon', 'eksempel', 'taskbox', 'merk', 'losning', 'figure', 'align']
        for env in environments:
            opens = content.count(f'\\begin{{{env}}}')
            closes = content.count(f'\\end{{{env}}}')
            if opens > closes:
                # Add missing end tags
                content += f'\n\\end{{{env}}}' * (opens - closes)
    
    return content


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
