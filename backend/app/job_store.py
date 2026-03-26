"""
Persist terminal pipeline jobs to disk so results survive process restarts (single instance).

Running jobs exist only in memory; completed/failed jobs are written as JSON under
output_dir/job_snapshots/.
"""

from __future__ import annotations

from pathlib import Path

import structlog

from app.config import get_settings
from app.models.state import PipelineState, PipelineStatus

logger = structlog.get_logger()


def _snapshots_dir() -> Path:
    s = get_settings()
    d = Path(s.output_dir) / "job_snapshots"
    d.mkdir(parents=True, exist_ok=True)
    return d


def persist_terminal_job(state: PipelineState) -> None:
    """Write COMPLETED or FAILED jobs to disk (no-op for other statuses)."""
    if state.status not in (PipelineStatus.COMPLETED, PipelineStatus.FAILED):
        return
    try:
        path = _snapshots_dir() / f"{state.job_id}.json"
        path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        logger.debug("job_persisted", job_id=state.job_id, status=state.status.value)
    except OSError as e:
        logger.warning("job_persist_failed", job_id=state.job_id, error=str(e))


def load_job_from_disk(job_id: str) -> PipelineState | None:
    path = _snapshots_dir() / f"{job_id}.json"
    if not path.is_file():
        return None
    try:
        return PipelineState.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        logger.warning("job_load_failed", job_id=job_id, error=str(e))
        return None


def resolve_job(job_id: str, memory: dict[str, PipelineState]) -> PipelineState | None:
    """Prefer in-memory state; otherwise load from disk and warm the cache."""
    if job_id in memory:
        return memory[job_id]
    loaded = load_job_from_disk(job_id)
    if loaded is not None:
        memory[job_id] = loaded
    return loaded
