"""Tests for M1 report JSON API."""

from pathlib import Path

from m1.scorer import report_json, resolve_m1_csv_path


def test_report_json_example_has_levels():
    path = resolve_m1_csv_path()
    data = report_json(str(path))
    assert data["levels"]
    assert any(l["level"] == "1T" for l in data["levels"])
    assert data["topics"]


def test_resolve_prefers_example_when_primary_empty():
    root = Path(__file__).resolve().parents[2]
    primary = root / "m1_skjema.csv"
    if primary.is_file():
        rows = primary.read_text(encoding="utf-8").strip().splitlines()
        if len(rows) <= 1:
            assert resolve_m1_csv_path().name == "m1_skjema_eksempel.csv"
