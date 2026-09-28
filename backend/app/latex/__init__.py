"""LaTeX preamble and compilation."""

from .compiler import compile_to_pdf, resolve_engine
from .preamble import (
    STANDARD_PREAMBLE,
    THEMES,
    build_preamble,
    wrap_with_preamble,
    wrap_with_style,
)

__all__ = [
    "STANDARD_PREAMBLE",
    "THEMES",
    "build_preamble",
    "wrap_with_preamble",
    "wrap_with_style",
    "compile_to_pdf",
    "resolve_engine",
]
