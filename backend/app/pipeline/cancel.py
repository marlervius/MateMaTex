"""
Cooperative cancellation for in-flight generation jobs.

Uses an in-process set plus on-disk flags under OUTPUT_DIR/cancel_flags/ so
abort signals survive process restarts and are visible to other workers that
share the same persistent volume (e.g. Render with OUTPUT_DIR on disk).
"""

from __future__ import annotations

import threading
from pathlib import Path

import structlog

from app.config import get_settings
from app.job_store import is_safe_job_id

logger = structlog.get_logger()

_lock = threading.Lock()
_cancelled: set[str] = set()


def _cancel_dir() -> Path:
    d = Path(get_settings().output_dir) / "cancel_flags"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _flag_path(job_id: str) -> Path:
    return _cancel_dir() / f"{job_id}.flag"


def cancel_job(job_id: str) -> None:
    with _lock:
        _cancelled.add(job_id)
    if not is_safe_job_id(job_id):
        logger.warning("cancel_rejected_unsafe_job_id", job_id=job_id)
        return
    try:
        _flag_path(job_id).write_text("1", encoding="utf-8")
        logger.info("cancel_flag_persisted", job_id=job_id)
    except OSError as e:
        logger.warning("cancel_flag_write_failed", job_id=job_id, error=str(e))


def is_cancelled(job_id: str) -> bool:
    with _lock:
        if job_id in _cancelled:
            return True
    if not is_safe_job_id(job_id):
        return False
    flag = _flag_path(job_id)
    if flag.is_file():
        with _lock:
            _cancelled.add(job_id)
        return True
    return False


def clear_cancel(job_id: str) -> None:
    with _lock:
        _cancelled.discard(job_id)
    if not is_safe_job_id(job_id):
        return
    try:
        _flag_path(job_id).unlink(missing_ok=True)
    except OSError as e:
        logger.warning("cancel_flag_remove_failed", job_id=job_id, error=str(e))


def cleanup_old_cancel_flags(max_age_days: int = 7) -> int:
    """Remove stale cancel flag files (same retention as job snapshots)."""
    from datetime import datetime, timedelta

    cutoff = datetime.now() - timedelta(days=max_age_days)
    removed = 0
    try:
        for path in _cancel_dir().glob("*.flag"):
            try:
                if datetime.fromtimestamp(path.stat().st_mtime) < cutoff:
                    path.unlink(missing_ok=True)
                    removed += 1
            except OSError:
                continue
    except OSError:
        return 0
    if removed:
        logger.info("cancel_flags_cleaned", removed=removed)
    return removed
