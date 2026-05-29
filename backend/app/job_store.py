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

# Central in-memory job registry (single-worker deployments)
_memory_jobs: dict[str, PipelineState] = {}
_shared_resources: dict[str, dict] = {}


def get_job_memory() -> dict[str, PipelineState]:
    return _memory_jobs


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


def resolve_job(job_id: str, memory: dict[str, PipelineState] | None = None) -> PipelineState | None:
    """Prefer in-memory state; otherwise load from disk and warm the cache."""
    store = memory if memory is not None else _memory_jobs
    if job_id in store:
        return store[job_id]
    loaded = load_job_from_disk(job_id)
    if loaded is not None:
        store[job_id] = loaded
    return loaded


def get_resource_snapshot(resource_type: str, resource_id: str) -> dict | None:
    """Build a shareable content snapshot for a resource."""
    if resource_type == "generation":
        state = resolve_job(resource_id)
        if state is None:
            return None
        return {
            "full_document": state.full_document,
            "topic": state.request.topic,
            "grade": state.request.grade,
            "material_type": state.request.material_type,
            "job_id": state.job_id,
            "status": state.status.value,
        }
    return _shared_resources.get(resource_id)


def store_shared_resource(resource_id: str, content: dict) -> None:
    _shared_resources[resource_id] = content


def cleanup_old_snapshots(max_age_days: int = 7) -> int:
    """Remove job snapshot files older than max_age_days."""
    from datetime import datetime, timedelta

    cutoff = datetime.now() - timedelta(days=max_age_days)
    removed = 0
    for path in _snapshots_dir().glob("*.json"):
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            if mtime < cutoff:
                path.unlink(missing_ok=True)
                removed += 1
        except OSError:
            continue
    if removed:
        logger.info("job_snapshots_cleaned", removed=removed)
    return removed
