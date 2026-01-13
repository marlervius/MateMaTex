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

from .formula_library import (
    Formula,
    FORMULA_LIBRARY,
    get_all_formulas,
    get_formulas_by_category,
    get_categories,
    search_formulas,
    get_formula_latex_block,
    get_formula_for_topic,
)

from .qr_generator import (
    is_qr_available,
    generate_qr_code,
    generate_answer_qr,
    decode_answer_qr,
    extract_answers_from_latex,
    generate_qr_for_worksheet,
    get_qr_latex_code,
)

from .difficulty_analyzer import (
    ExerciseAnalysis,
    ContentAnalysis,
    analyze_exercise,
    analyze_content,
    get_difficulty_distribution_chart_data,
    get_difficulty_emoji,
    format_analysis_summary,
)

from .template_builder import (
    CustomTemplate,
    load_custom_templates,
    save_custom_templates,
    create_template,
    update_template,
    delete_template,
    get_template,
    increment_usage,
    get_popular_templates,
    get_recent_templates,
    search_templates,
    export_template,
    import_template,
    get_preset_templates,
    PRESET_TEMPLATES,
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
    # Formula library
    "Formula",
    "FORMULA_LIBRARY",
    "get_all_formulas",
    "get_formulas_by_category",
    "get_categories",
    "search_formulas",
    "get_formula_latex_block",
    "get_formula_for_topic",
    # QR generator
    "is_qr_available",
    "generate_qr_code",
    "generate_answer_qr",
    "decode_answer_qr",
    "extract_answers_from_latex",
    "generate_qr_for_worksheet",
    "get_qr_latex_code",
    # Difficulty analyzer
    "ExerciseAnalysis",
    "ContentAnalysis",
    "analyze_exercise",
    "analyze_content",
    "get_difficulty_distribution_chart_data",
    "get_difficulty_emoji",
    "format_analysis_summary",
    # Template builder
    "CustomTemplate",
    "load_custom_templates",
    "save_custom_templates",
    "create_template",
    "update_template",
    "delete_template",
    "get_template",
    "increment_usage",
    "get_popular_templates",
    "get_recent_templates",
    "search_templates",
    "export_template",
    "import_template",
    "get_preset_templates",
    "PRESET_TEMPLATES",
]
