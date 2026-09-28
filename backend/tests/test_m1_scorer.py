"""Tests for M1 reference scorer (M1-testprotokoll)."""

import pytest

from m1.scorer import MISMATCH, UNCERTAIN, VERIFIED, aggregate, answer_check


class TestAnswerCheck:
    def test_identical_expr(self):
        assert answer_check("2*x + 3", "3 + 2*x") == VERIFIED

    def test_wrong_expr(self):
        assert answer_check("x**2", "x**3") == MISMATCH

    def test_equivalent_form(self):
        assert answer_check("(x+1)**2", "x**2 + 2*x + 1") == VERIFIED

    def test_integral_up_to_constant(self):
        assert answer_check("x**2", "x**2 + 5", mode="integral") == VERIFIED

    def test_set_mode(self):
        assert answer_check("1, -2", "-2, 1", mode="set") == VERIFIED

    def test_prose_not_mismatch(self):
        assert answer_check("vis at linjen er parallell", "vis at linjen er parallell") == UNCERTAIN

    def test_unparseable(self):
        assert answer_check("not valid sympy {{{", "also bad") == UNCERTAIN


class TestAggregate:
    def test_example_csv_totals(self):
        from pathlib import Path

        csv_path = Path(__file__).resolve().parents[2] / "m1_skjema_eksempel.csv"
        by_level, _ = aggregate(str(csv_path))
        assert "1T" in by_level
        assert "R1" in by_level
        assert by_level["1T"]["poeng"] == 35
        assert by_level["R1"]["poeng"] == 34
        assert pytest.approx(by_level["1T"]["groenn"], rel=0.01) == 24


class TestAutoscore:
    HEADER = "nivaa,emne,oppgavetype,poeng,fasit,kandidat,modus,resultat,kommentar\n"

    def _run(self, tmp_path, body):
        import csv

        from m1.scorer import autoscore

        src = tmp_path / "in.csv"
        dst = tmp_path / "out.csv"
        src.write_text(self.HEADER + body, encoding="utf-8")
        counts = autoscore(str(src), str(dst))
        with dst.open(encoding="utf-8") as handle:
            return counts, list(csv.DictReader(handle))

    def test_fills_verified_and_mismatch(self, tmp_path):
        counts, rows = self._run(
            tmp_path,
            '1T,Likninger,andregrad,3,"2, -3","-3, 2",set,,\n'
            "1T,Derivasjon,polynom,2,6*x**2,6*x**3,expr,,\n",
        )
        assert [r["resultat"] for r in rows] == ["verified", "mismatch"]
        assert "bekreft manuelt" in rows[1]["kommentar"]
        assert counts["verified"] == 1 and counts["mismatch"] == 1

    def test_uncertain_left_for_human(self, tmp_path):
        counts, rows = self._run(tmp_path, "R1,Bevis,induksjon,6,,,,,bevismetode\n")
        assert rows[0]["resultat"] == ""
        assert rows[0]["kommentar"].startswith("bevismetode; MANUELL")
        assert counts["manual"] == 1

    def test_existing_result_is_kept(self, tmp_path):
        counts, rows = self._run(tmp_path, "R1,Bevis,induksjon,6,x,y,expr,unverifiable,\n")
        assert rows[0]["resultat"] == "unverifiable"
        assert counts["kept"] == 1

    def test_unknown_mode_rejected(self, tmp_path):
        with pytest.raises(ValueError):
            self._run(tmp_path, "1T,A,b,1,x,x,feil,,\n")

    def test_unscored_rows_are_reported(self, tmp_path):
        from m1.scorer import report_json

        path = tmp_path / "skjema.csv"
        path.write_text(
            "nivaa,emne,oppgavetype,poeng,resultat,kommentar\n"
            "1T,Algebra,a,3,verified,\n"
            "1T,Algebra,b,1,,\n",
            encoding="utf-8",
        )
        level = report_json(str(path))["levels"][0]
        assert level["green_pct"] == 75.0
        assert level["unscored_pct"] == 25.0
