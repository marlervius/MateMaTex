"""
Pipeline state model — the single source of truth flowing through the LangGraph.

Every node in the graph reads from and writes to this state.
Uses Pydantic v2 for strict validation.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class PipelineStatus(str, Enum):
    """Overall pipeline status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRole(str, Enum):
    """Every agent in the pipeline."""
    PEDAGOGUE = "pedagogue"
    AUTHOR = "author"
    MATH_VERIFIER = "math_verifier"
    LATEX_VALIDATOR = "latex_validator"
    LATEX_FIXER = "latex_fixer"
    EDITOR = "editor"
    LAYOUT = "layout"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------
class GenerationRequest(BaseModel):
    """User's input to the pipeline."""
    grade: str = Field(description="Grade level, e.g. '10. trinn', 'VG2 R1'")
    topic: str = Field(description="Math topic")
    material_type: str = Field(default="arbeidsark", description="arbeidsark|kapittel|prøve")
    language_level: str = Field(default="standard", description="standard|b2|b1")
    num_exercises: int = Field(default=10, ge=1, le=50)
    difficulty: str = Field(default="Middels", description="Lett|Middels|Vanskelig")
    include_theory: bool = True
    include_examples: bool = True
    include_exercises: bool = True
    include_solutions: bool = True
    include_graphs: bool = True
    competency_goals: list[str] = Field(default_factory=list)
    extra_instructions: str = ""


class MathClaim(BaseModel):
    """A single mathematical claim extracted from the LaTeX for verification."""
    claim_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    latex_expression: str = Field(description="Raw LaTeX of the claim")
    claim_type: str = Field(description="equation|inequality|computation|solution")
    context: str = Field(default="", description="Surrounding text for context")
    sympy_expression: str = Field(default="", description="SymPy-parseable form")
    is_verified: bool = False
    is_correct: bool | None = None
    error_message: str = ""
    expected_result: str = ""
    actual_result: str = ""


class VerificationResult(BaseModel):
    """Result of the SymPy math verification pass."""
    claims_checked: int = 0
    claims_correct: int = 0
    claims_incorrect: int = 0
    claims_unparseable: int = 0
    errors: list[MathClaim] = Field(default_factory=list)
    all_correct: bool = False
    summary: str = ""


class LatexCompilationResult(BaseModel):
    """Result of actual pdflatex compilation check."""
    success: bool = False
    pdf_path: str = ""
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    log_excerpt: str = ""


class AgentStep(BaseModel):
    """Observability record for a single agent execution."""
    agent: AgentRole
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None
    duration_seconds: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    input_summary: str = ""
    output_summary: str = ""
    error: str = ""
    retries: int = 0


# ---------------------------------------------------------------------------
# Main pipeline state — flows through every node in the LangGraph
# ---------------------------------------------------------------------------
class PipelineState(BaseModel):
    """
    The single state object that flows through the entire LangGraph pipeline.

    LangGraph nodes read from and write to this state.
    Each field is updated by the responsible agent/node.
    """

    # --- Identifiers ---
    job_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = Field(default_factory=datetime.now)
    status: PipelineStatus = PipelineStatus.PENDING

    # --- User input ---
    request: GenerationRequest = Field(default_factory=GenerationRequest)

    # --- Curriculum context (set by pedagogue) ---
    grade_boundaries: dict[str, Any] = Field(default_factory=dict)
    curriculum_context: str = ""

    # --- Agent outputs ---
    pedagogical_plan: str = ""
    raw_latex_body: str = ""
    verified_latex_body: str = ""
    edited_latex_body: str = ""
    final_latex_body: str = ""
    full_document: str = ""  # With preamble

    # --- Verification ---
    math_verification: VerificationResult = Field(default_factory=VerificationResult)
    math_verification_attempts: int = 0
    latex_compilation: LatexCompilationResult = Field(default_factory=LatexCompilationResult)
    latex_fix_attempts: int = 0

    # --- Observability ---
    steps: list[AgentStep] = Field(default_factory=list)
    total_tokens: int = 0
    total_duration_seconds: float = 0.0
    current_agent: AgentRole | None = None

    # --- Output ---
    pdf_path: str = ""
    error_message: str = ""
