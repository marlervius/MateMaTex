"""Tests for persisted cancel flags."""

from app.pipeline.cancel import cancel_job, clear_cancel, is_cancelled


def test_cancel_flag_persists_in_memory_and_disk(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))
    from app.config import get_settings

    get_settings.cache_clear()

    job_id = "abc123deadbeef"
    assert not is_cancelled(job_id)
    cancel_job(job_id)
    assert is_cancelled(job_id)

    clear_cancel(job_id)
    assert not is_cancelled(job_id)

    get_settings.cache_clear()
