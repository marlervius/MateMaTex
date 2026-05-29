"""Persistent exercise store — memory cache with disk JSON backing."""

from __future__ import annotations

import json
from pathlib import Path

import structlog

from app.config import get_settings

logger = structlog.get_logger()

_memory: dict[str, dict] = {}
_loaded = False


def _store_dir() -> Path:
    d = Path(get_settings().output_dir) / "exercise_store"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _ensure_loaded() -> None:
    global _loaded
    if _loaded:
        return
    for path in _store_dir().glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("id"):
                _memory[data["id"]] = data
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("exercise_store_load_failed", path=str(path), error=str(e))
    _loaded = True


def _persist_one(exercise: dict) -> None:
    path = _store_dir() / f"{exercise['id']}.json"
    path.write_text(json.dumps(exercise, ensure_ascii=False, indent=2), encoding="utf-8")


def save(exercise: dict) -> dict:
    _ensure_loaded()
    _memory[exercise["id"]] = exercise
    try:
        _persist_one(exercise)
    except OSError as e:
        logger.warning("exercise_store_persist_failed", id=exercise["id"], error=str(e))
    return exercise


def get(exercise_id: str) -> dict | None:
    _ensure_loaded()
    d = _memory.get(exercise_id)
    if d and not d.get("deleted"):
        return d
    return None


def list_active(*, user_id: str | None = None) -> list[dict]:
    _ensure_loaded()
    items = [d for d in _memory.values() if not d.get("deleted")]
    if user_id and user_id not in ("anonymous", "api-user"):
        items = [d for d in items if d.get("owner_id", user_id) == user_id or not d.get("owner_id")]
    return items


def soft_delete(exercise_id: str) -> bool:
    _ensure_loaded()
    d = _memory.get(exercise_id)
    if not d:
        return False
    d["deleted"] = True
    try:
        _persist_one(d)
    except OSError:
        pass
    return True
