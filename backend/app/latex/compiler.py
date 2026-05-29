"""
LaTeX compilation — wraps pdflatex with proper error handling.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import structlog

logger = structlog.get_logger()


_DOUBLE_PASS_TRIGGERS = (
    "\\ref{",
    "\\pageref{",
    "\\tableofcontents",
    "\\listoffigures",
    "\\listoftables",
    "\\cite{",
    "\\printindex",
)


def compile_to_pdf_with_log(
    latex_content: str,
    output_path: str | Path | None = None,
    pdflatex_path: str = "pdflatex",
) -> tuple[str | None, str]:
    """
    Compile a LaTeX document and return (pdf_path_or_None, log_excerpt).

    The log excerpt is the last portion of the pdflatex .log file, suitable
    for surfacing to end users on failure. ``compile_to_pdf`` wraps this and
    discards the log for back-compat.
    """
    log_excerpt = ""

    with tempfile.TemporaryDirectory(prefix="matematex_") as tmpdir:
        tex_path = Path(tmpdir) / "document.tex"
        tex_path.write_text(latex_content, encoding="utf-8")

        needs_double_pass = any(t in latex_content for t in _DOUBLE_PASS_TRIGGERS)
        passes = 2 if needs_double_pass else 1

        last_return_code: int | None = None
        for _pass_num in range(passes):
            try:
                proc = subprocess.run(
                    [
                        pdflatex_path,
                        "-interaction=nonstopmode",
                        # halt on first hard error so we don't loop on a broken doc
                        "-halt-on-error",
                        "-file-line-error",
                        "-output-directory", str(tmpdir),
                        str(tex_path),
                    ],
                    capture_output=True,
                    text=False,  # pdflatex mixes UTF-8 and latin1
                    timeout=120,
                    cwd=tmpdir,
                )
                last_return_code = proc.returncode
                if proc.returncode != 0:
                    # No point running another pass after a hard failure.
                    break
            except FileNotFoundError as e:
                logger.error("pdflatex_not_found", path=pdflatex_path, error=str(e))
                return None, f"pdflatex ikke funnet på '{pdflatex_path}'."
            except subprocess.TimeoutExpired as e:
                logger.error("pdflatex_timeout", error=str(e))
                return None, "pdflatex tidsavbrudd (>120s)."

        # Capture log excerpt (last ~80 lines is usually enough to find the cause)
        log_path = Path(tmpdir) / "document.log"
        if log_path.exists():
            try:
                full_log = log_path.read_text(encoding="utf-8", errors="replace")
                log_excerpt = "\n".join(full_log.splitlines()[-80:])
            except OSError:
                log_excerpt = ""

        pdf_in_tmp = Path(tmpdir) / "document.pdf"
        if not pdf_in_tmp.exists() or (last_return_code not in (0, None)):
            logger.error(
                "pdf_not_generated",
                return_code=last_return_code,
                has_log=bool(log_excerpt),
            )
            return None, log_excerpt

        if output_path:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf_in_tmp, out)
            return str(out), log_excerpt

        # Caller is responsible for reading the file before tmpdir cleanup.
        return str(pdf_in_tmp), log_excerpt


def compile_to_pdf(
    latex_content: str,
    output_path: str | Path | None = None,
    pdflatex_path: str = "pdflatex",
) -> str | None:
    """Backwards-compatible wrapper that discards the log excerpt."""
    pdf_path, _log = compile_to_pdf_with_log(
        latex_content=latex_content,
        output_path=output_path,
        pdflatex_path=pdflatex_path,
    )
    return pdf_path


def compile_latex_to_bytes(
    latex_content: str,
    pdflatex_path: str = "pdflatex",
) -> tuple[bytes | None, str]:
    """Compile LaTeX and return PDF bytes plus log excerpt."""
    with tempfile.TemporaryDirectory(prefix="matematex_bytes_") as tmpdir:
        out = Path(tmpdir) / "document.pdf"
        pdf_path, log_excerpt = compile_to_pdf_with_log(
            latex_content=latex_content,
            output_path=out,
            pdflatex_path=pdflatex_path,
        )
        if pdf_path and Path(pdf_path).is_file():
            return Path(pdf_path).read_bytes(), log_excerpt
        return None, log_excerpt
