"""
LaTeX compilation — wraps pdflatex with proper error handling.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import structlog

logger = structlog.get_logger()


def compile_to_pdf(
    latex_content: str,
    output_path: str | Path | None = None,
    pdflatex_path: str = "pdflatex",
) -> str | None:
    """
    Compile a complete LaTeX document to PDF.

    Args:
        latex_content: Full LaTeX document with preamble.
        output_path: Where to save the PDF. If None, uses a temp directory.
        pdflatex_path: Path to pdflatex binary.

    Returns:
        Path to the generated PDF, or None on failure.
    """
    with tempfile.TemporaryDirectory(prefix="matematex_") as tmpdir:
        tex_path = Path(tmpdir) / "document.tex"
        tex_path.write_text(latex_content, encoding="utf-8")

        # Run pdflatex (run twice only if references/table of contents are present)
        needs_double_pass = any(
            ref in latex_content 
            for ref in ["\\ref{", "\\pageref{", "\\tableofcontents", "\\listoffigures", "\\listoftables", "\\cite{", "\\printindex"]
        )
        passes = 2 if needs_double_pass else 1

        for pass_num in range(passes):
            try:
                proc = subprocess.run(
                    [
                        pdflatex_path,
                        "-interaction=nonstopmode",
                        "-output-directory", str(tmpdir),
                        str(tex_path),
                    ],
                    capture_output=True,
                    text=False,  # Read as bytes — pdflatex may output latin1
                    timeout=120,
                    cwd=tmpdir,
                )
                # Decode stdout/stderr safely (pdflatex mixes UTF-8 and latin1)
                proc.stdout = proc.stdout.decode("utf-8", errors="replace") if proc.stdout else ""
                proc.stderr = proc.stderr.decode("utf-8", errors="replace") if proc.stderr else ""
            except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                logger.error("pdflatex_error", error=str(e))
                return None

        pdf_in_tmp = Path(tmpdir) / "document.pdf"
        if not pdf_in_tmp.exists():
            logger.error("pdf_not_generated")
            return None

        # Copy to output path if specified
        if output_path:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(pdf_in_tmp, out)
            return str(out)

        # Return from temp (caller must use before cleanup)
        return str(pdf_in_tmp)
