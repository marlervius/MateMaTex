"""
Tools module for MateMaTeX.
Contains custom tools for LaTeX generation, PDF compilation, etc.
"""

from .pdf_generator import (
    compile_latex_to_pdf,
    clean_ai_output,
    ensure_preamble,
    validate_latex_syntax,
    STANDARD_PREAMBLE
)

from .word_exporter import (
    latex_to_word,
    convert_latex_file_to_word,
    is_word_export_available,
)

__all__ = [
    # PDF tools
    "compile_latex_to_pdf",
    "clean_ai_output",
    "ensure_preamble",
    "validate_latex_syntax",
    "STANDARD_PREAMBLE",
    # Word tools
    "latex_to_word",
    "convert_latex_file_to_word",
    "is_word_export_available",
]
