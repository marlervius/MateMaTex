"""
MateMaTeX 2.0 — FastAPI backend entry point.

Exposes:
- POST /generate              — Start a generation job
- GET  /generate/{id}/stream  — SSE stream of agent progress
- GET  /generate/{id}/result  — Get the final result
- POST /compile               — Compile LaTeX to PDF
- /exercises/*                — Exercise bank (CRUD, search, export)
- /editor/*                   — Interactive LaTeX editor (compile, AI actions)
- /differentiation/*          — Multi-level differentiation
- /export/*                   — PDF/Word/PowerPoint/QR export
- /sharing/*                  — Shareable links
- /school/*, /generations/*   — Collaboration (comments, versions, school bank)
"""

import asyncio
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import AsyncGenerator, Optional

import structlog
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.auth import get_current_user
from app.config import get_config, get_settings
from app.models.state import GenerationRequest, PipelineState, PipelineStatus

logger = structlog.get_logger()

settings = get_settings()

app = FastAPI(
    title="MateMaTeX 2.0 API",
    version="2.0.0",
    description="AI-powered math education content generator for Norwegian schools",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
    openapi_tags=[
        {"name": "generation", "description": "AI content generation pipeline"},
        {"name": "exercises", "description": "Exercise bank — CRUD, search, export"},
        {"name": "editor", "description": "Interactive LaTeX editor — compile, AI actions"},
        {"name": "differentiation", "description": "Multi-level differentiation and hints"},
        {"name": "export", "description": "PDF, Word, PowerPoint, QR export"},
        {"name": "sharing", "description": "Shareable links with password/expiry"},
        {"name": "collaboration", "description": "School bank, comments, version history"},
    ],
)

# ---------------------------------------------------------------------------
# CORS — restrict in production
# ---------------------------------------------------------------------------
allowed_origins = [settings.frontend_url]
if settings.environment == "development":
    allowed_origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Startup / Shutdown (database pool)
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    if settings.database_url:
        try:
            from app.db import get_pool
            await get_pool()
            logger.info("startup_complete", environment=settings.environment)
        except Exception as e:
            logger.error("startup_database_failed", error=str(e))
            logger.warning("startup_continuing_without_db", msg="App will start but DB features are unavailable")
    else:
        logger.warning("startup_no_database", msg="DATABASE_URL not set — running without DB")


@app.on_event("shutdown")
async def shutdown():
    from app.db import close_pool
    await close_pool()
    logger.info("shutdown_complete")


# ---------------------------------------------------------------------------
# Mount sub-routers (Fase 2 modules)
# ---------------------------------------------------------------------------
from app.exercises.router import router as exercises_router
from app.editor.compiler import router as editor_compile_router
from app.editor.ai_actions import router as editor_ai_router
from app.differentiation.generator import router as diff_router
from app.differentiation.hint_engine import router as hint_router
from app.export.router import router as export_router
from app.export.qr import router as qr_router
from app.sharing.router import router as sharing_router
from app.collaboration.router import router as collab_router

app.include_router(exercises_router)
app.include_router(editor_compile_router)
app.include_router(editor_ai_router)
app.include_router(diff_router)
app.include_router(hint_router)
app.include_router(export_router)
app.include_router(qr_router)
app.include_router(sharing_router)
app.include_router(collab_router)

# In-memory job store (replace with Redis/DB in production)
_jobs: dict[str, PipelineState] = {}
_executor = ThreadPoolExecutor(max_workers=4)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class GenerateResponse(BaseModel):
    job_id: str
    status: str
    message: str


class CompileRequest(BaseModel):
    latex_content: str
    filename: str = "document"


class CompileResponse(BaseModel):
    success: bool
    pdf_path: Optional[str] = None
    errors: list[str] = []


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/generate", response_model=GenerateResponse)
async def start_generation(request: GenerationRequest, user_id: str = Depends(get_current_user)) -> GenerateResponse:
    """Start an asynchronous generation job."""
    state = PipelineState(
        request=request,
        status=PipelineStatus.PENDING,
    )
    _jobs[state.job_id] = state

    loop = asyncio.get_event_loop()
    loop.run_in_executor(_executor, _run_job, state.job_id, request)

    logger.info("generation_started", job_id=state.job_id, topic=request.topic)

    return GenerateResponse(
        job_id=state.job_id,
        status="pending",
        message="Generering startet. Bruk /generate/{id}/stream for fremdrift.",
    )


@app.get("/generate/{job_id}/stream")
async def stream_progress(job_id: str) -> StreamingResponse:
    """Stream agent progress via Server-Sent Events."""

    async def event_generator() -> AsyncGenerator[str, None]:
        last_step_count = 0

        while True:
            state = _jobs.get(job_id)
            if state is None:
                yield _sse_event("error", {"message": "Job not found"})
                break

            while last_step_count < len(state.steps):
                step = state.steps[last_step_count]
                yield _sse_event("step", {
                    "agent": step.agent.value,
                    "started_at": step.started_at.isoformat(),
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "duration_seconds": step.duration_seconds,
                    "output_summary": step.output_summary,
                    "error": step.error,
                    "retries": step.retries,
                })
                last_step_count += 1

            if state.current_agent:
                yield _sse_event("current_agent", {
                    "agent": state.current_agent.value,
                })

            if state.status in (PipelineStatus.COMPLETED, PipelineStatus.FAILED):
                yield _sse_event("complete", {
                    "status": state.status.value,
                    "total_duration": state.total_duration_seconds,
                    "total_steps": len(state.steps),
                    "math_checks": state.math_verification.claims_checked,
                    "math_correct": state.math_verification.claims_correct,
                    "latex_compiled": state.latex_compilation.success,
                    "error": state.error_message,
                })
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.get("/generate/{job_id}/result")
async def get_result(job_id: str, user_id: str = Depends(get_current_user)):
    """Get the result of a completed generation job."""

    state = _jobs.get(job_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if state.status == PipelineStatus.RUNNING:
        raise HTTPException(status_code=202, detail="Job still running")

    return {
        "job_id": state.job_id,
        "status": state.status.value,
        "full_document": state.full_document,
        "pdf_path": state.pdf_path,
        "math_verification": state.math_verification.model_dump(),
        "latex_compilation": state.latex_compilation.model_dump(),
        "steps": [s.model_dump() for s in state.steps],
        "total_duration_seconds": state.total_duration_seconds,
        "total_tokens": state.total_tokens,
        "error": state.error_message,
    }


@app.post("/compile", response_model=CompileResponse)
async def compile_latex(request: CompileRequest, user_id: str = Depends(get_current_user)) -> CompileResponse:
    """Compile LaTeX content to PDF."""
    from app.latex.compiler import compile_to_pdf
    from app.latex.preamble import wrap_with_preamble

    content = request.latex_content
    if r"\documentclass" not in content:
        content = wrap_with_preamble(content)

    config = get_config()
    pdf_path = compile_to_pdf(
        latex_content=content,
        output_path=f"{config.output_dir}/{request.filename}.pdf",
        pdflatex_path=config.pdflatex_path,
    )

    if pdf_path:
        return CompileResponse(success=True, pdf_path=pdf_path)
    else:
        return CompileResponse(success=False, errors=["Compilation failed"])


@app.post("/estimate")
async def estimate_cost(request: GenerationRequest, user_id: str = Depends(get_current_user)):
    """Estimate token cost BEFORE generation."""
    from app.cache import get_cache
    cache = get_cache()
    tokens = cache.estimate_tokens(request)
    similar = cache.find_similar(request)

    return {
        **tokens,
        "similar_cached": len(similar),
        "cache_available": len(similar) > 0,
    }


@app.get("/cache/stats")
async def cache_stats(user_id: str = Depends(get_current_user)):
    """Get cache statistics."""
    from app.cache import get_cache
    return get_cache().stats()


@app.delete("/cache")
async def clear_cache(user_id: str = Depends(get_current_user)):
    """Clear the semantic cache."""
    from app.cache import get_cache
    count = get_cache().clear()
    return {"cleared": count}


@app.get("/health")
async def health():
    """Health check for Render."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "environment": settings.environment,
        "timestamp": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _run_job(job_id: str, request: GenerationRequest) -> None:
    """Run a generation job in a background thread."""
    from app.pipeline.graph import run_pipeline

    try:
        _jobs[job_id].status = PipelineStatus.RUNNING
        result = run_pipeline(request)
        _jobs[job_id] = result
    except Exception as e:
        state = _jobs.get(job_id)
        if state:
            state.status = PipelineStatus.FAILED
            state.error_message = str(e)
        logger.error("job_failed", job_id=job_id, error=str(e))


def _sse_event(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event."""
    return f"event: {event_type}\ndata: {json.dumps(data, default=str)}\n\n"
