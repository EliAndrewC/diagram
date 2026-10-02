"""`scripts/_bundle_owed.py` - no bundle for a check nothing owes (feature 311, plan D9), and the intro-check bundle (D4).

The GM, 2026-10-02: *"I do worry about a future session making some extremely minor formatting tweak or something and then
having that literally rerun every subagent check for all 2,000 something of our resources"*. The owed units are stubbed, so
each case states exactly what the delta owes."""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bo = _load("_bundle_owed")
cb = _load("_check_bundle")
U = bo.ru.Unit


@pytest.fixture
def owing(monkeypatch: pytest.MonkeyPatch):  # noqa: ANN201
    def owe(*slugs: str) -> None:
        monkeypatch.setattr(bo.ro, "units", lambda root, *a: [U(s, "test", "fp-" + s) for s in slugs])

    return owe


def test_a_bundle_for_a_check_nothing_owes_is_refused_with_the_owed_list(owing) -> None:  # noqa: ANN001
    owing("record-format:0094", "intro-check:0094")
    units, checks, refusal = bo.owed_for_question(REPO, "0094", "quote-check", "")
    assert units == [] and "no quote-check check is owed on question 0094" in refusal and "intro-check:0094" in refusal
    units, checks, refusal = bo.owed_for_question(REPO, "0094", "record-format", "")
    assert refusal == "" and checks == "record-format" and [u.slug for u in units] == ["record-format:0094"]


def test_all_is_owed_when_anything_is_and_the_manifest_lists_what(owing) -> None:  # noqa: ANN001
    owing("record-format:0094", "quote-check:0094#k", "record-format:0110")
    units, checks, refusal = bo.owed_for_question(REPO, "0094-rooms-for-a-parley-across-a-border.html", "all", "")
    assert refusal == "" and checks == "record-format quote-check"
    text = bo.manifest_lines(units, checks)
    assert "owed-checks: record-format quote-check" in text and "unit: quote-check:0094#k fp-quote-check:0094#k" in text
    assert "0110" not in text


def test_a_reason_builds_it_anyway_and_a_bare_token_does_not(owing) -> None:  # noqa: ANN001
    owing()
    assert "needs a REASON" in bo.owed_for_question(REPO, "0094", "intro-check", "x")[2]
    units, checks, refusal = bo.owed_for_question(REPO, "0094", "intro-check", "feature 311 backfill")
    assert refusal == "" and checks == "intro-check" and [u.slug for u in units] == ["intro-check:0094"]
    assert bo.manifest_lines(units, checks, "feature 311 backfill").count("not-owed: feature 311 backfill") == 1


def test_record_style_is_owed_by_its_sweep_not_by_the_delta(owing) -> None:  # noqa: ANN001
    owing()
    assert bo.owed_for_question(REPO, "0094", "record-style", "") == ([], "record-style", "")


def test_quote_check_is_cut_to_the_owed_notes_unless_the_unfootnoted_reading_is_owed() -> None:
    assert bo.owed_notes([U("quote-check:0094#a", ""), U("quote-check:0094.drawing#b", ""), U("record-format:0094", "")]) == {"a", "b"}
    assert bo.owed_notes([U("quote-check:0094#a", ""), U("quote-check:0094#unfootnoted", "")]) == frozenset()


def test_a_key_bundle_is_owed_by_its_write_up_or_a_note_citing_it_or_a_declared_new_claim(owing, monkeypatch) -> None:  # noqa: ANN001
    owing("source-applicability:edo-enwiki")
    assert bo.owed_for_key(REPO, "edo-enwiki", False, "", "")[1] == "source-applicability"
    assert "no source-applicability is owed on `kyakhta-trade-enwiki`" in bo.owed_for_key(REPO, "kyakhta-trade-enwiki", False, "", "")[2]
    assert "NEW=" in bo.owed_for_key(REPO, "kyakhta-trade-enwiki", True, "", "")[2]
    assert bo.owed_for_key(REPO, "kyakhta-trade-enwiki", True, "", "a claim about the post")[2] == ""
    assert "needs a REASON" in bo.owed_for_key(REPO, "kyakhta-trade-enwiki", True, "", "x")[2]
    owing("source-reader:0094#kyakhta-trade-enwiki")
    units, checks, refusal = bo.owed_for_key(REPO, "kyakhta-trade-enwiki", True, "", "")
    assert refusal == "" and checks == "source-reader" and [u.slug for u in units] == ["source-reader:0094#kyakhta-trade-enwiki"]


def test_the_intro_bundle_holds_the_body_the_drawing_page_and_the_map_elements(owing, tmp_path: pathlib.Path) -> None:  # noqa: ANN001
    text = bo.intro_bundle_text(REPO, "0094")
    assert "--- the research page" in text and "Kyakhta" in text and "<!--" not in text
    assert "--- how our maps draw it" in text and "- parley room (label: deviation)" in text
    assert bo.intro_bundle_text(REPO, "9999") == ""
    owing()
    assert cb.main(["--for", "intro-check", "--qs", "0094 0083", "--out", str(tmp_path / "b"), "--root", str(REPO)]) == 3
    assert cb.main(["--for", "intro-check", "--qs", "0094 0083", "--not-owed-ok", "a seeded run", "--out", str(tmp_path / "b"), "--root", str(REPO)]) == 0
    manifest = (tmp_path / "b" / "MANIFEST.md").read_text(encoding="utf-8")
    assert "2 questions, for intro-check" in manifest and "unit: intro-check:0083 " in manifest and "owed-checks: intro-check" in manifest
    assert cb.main(["--for", "intro-check", "--qs", "9999", "--not-owed-ok", "a seeded run", "--out", str(tmp_path / "c"), "--root", str(REPO)]) == 2


def test_the_refusals_reach_the_command_line(owing, tmp_path: pathlib.Path) -> None:  # noqa: ANN001
    owing()
    assert cb.main(["0094", "--for", "record-format", "--out", str(tmp_path / "q"), "--root", str(REPO)]) == 3
    assert cb.main(["--key", "kyakhta-trade-enwiki", "--out", str(tmp_path / "k"), "--root", str(REPO)]) == 3
    assert cb.main(["9999", "--out", str(tmp_path / "n"), "--root", str(REPO)]) == 2
