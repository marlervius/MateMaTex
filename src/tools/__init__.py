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

from .section_editor import (
    parse_sections,
    get_section_summary,
    replace_section,
    extract_section,
    generate_section_prompt,
)

from .topic_suggester import (
    get_topic_suggestions,
    get_related_topics,
    get_prerequisite_topics,
)

from .print_optimizer import (
    create_print_version,
    optimize_for_ink_saving,
    add_page_breaks,
    create_answer_sheet,
    remove_solutions,
    PRINT_PREAMBLE,
)

from .batch_generator import (
    BatchJob,
    BatchResult,
    create_batch_jobs,
    run_batch,
    merge_batch_results,
    get_batch_summary,
    estimate_batch_time,
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
    # Section editor
    "parse_sections",
    "get_section_summary",
    "replace_section",
    "extract_section",
    "generate_section_prompt",
    # Topic suggester
    "get_topic_suggestions",
    "get_related_topics",
    "get_prerequisite_topics",
    # Print optimizer
    "create_print_version",
    "optimize_for_ink_saving",
    "add_page_breaks",
    "create_answer_sheet",
    "remove_solutions",
    "PRINT_PREAMBLE",
    # Batch generator
    "BatchJob",
    "BatchResult",
    "create_batch_jobs",
    "run_batch",
    "merge_batch_results",
    "get_batch_summary",
    "estimate_batch_time",
]
