"""`scripts/record/money_candidates.py` - every unmarked amount of money a built era could convert (feature 413, plan D6).

The amount nearest a built era is listed first, with its distance; a marked amount, a compound one inside a mark ("9 ryo 2 bu")
included, is not listed; a note takes the years of the sentence that cites it; a coin no row carries (a gold bu) is still
listed; `--check` passes only when every listed amount is marked or named, a `*` line covering every amount of its fragment -
no distance in years decides what it may cover (the GM withdrew the 25-year default, #14)."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

from tests._scripts import script

KYOTO = {"years": "1745-1754", "units": {"mon": {}, "ryo": {}}}


def _mod():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("money_candidates", script("money_candidates"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["money_candidates"] = mod  # a dataclass looks its module up by name
    spec.loader.exec_module(mod)
    return mod


def _repo(tmp_path: pathlib.Path, page: str, notes: str = "") -> pathlib.Path:
    (tmp_path / "research" / "questions").mkdir(parents=True)
    (tmp_path / "research" / "assets").mkdir()
    (tmp_path / "research" / "assets" / "money-conversions.json").write_text(json.dumps({"eras": {"kyoto-1745": KYOTO}}), encoding="utf-8")
    (tmp_path / "research" / "questions" / "0001-x.html").write_text(page, encoding="utf-8")
    if notes:
        (tmp_path / "research" / "questions" / "0001-x.notes.html").write_text(notes, encoding="utf-8")
    return tmp_path


PAGE = (
    '<h2 id="x">X</h2>\n<p>In 1750 it cost 20 mon and <span class="money" data-amount="9.5" data-coin="ryo">9 ryo 2 bu</span>.</p>\n'
    '<p>In 1840 a room was 300 mon a month, and a bu of gold 1 bu.<sup class="fn" data-note="k"></sup></p>\n<p>No year: 5 mon.</p>\n'
)


def test_it_lists_near_first_and_skips_what_is_marked(tmp_path: pathlib.Path) -> None:
    mc = _mod()
    found = mc.amounts(str(_repo(tmp_path, PAGE, '<li data-note="k">「the room, 300 mon」</li>\n')))
    assert [(a.stem, a.text, a.near, a.gap) for a in found][:1] == [("0001-x", "20 mon", "kyoto-1745", 0)]
    texts = [a.text for a in found]
    assert "9 ryo" not in texts and "2 bu" not in texts, "a compound amount inside a mark is marked"
    assert "1 bu" in texts, "a coin no built row carries is still listed"
    note = next(a for a in found if a.stem == "0001-x.notes")
    assert note.years == (1840,) and (note.near, note.gap) == ("kyoto-1745", 86), "a note takes the years of the sentence that cites it"
    assert next(a for a in found if a.text == "5 mon").years == ()


def test_check_needs_every_amount_marked_or_named_and_a_star_covers_its_whole_fragment(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    mc = _mod()
    root = _repo(tmp_path, PAGE, '<li data-note="k">「the room, 300 mon」</li>\n')
    backfill = root / mc.BACKFILL
    backfill.parent.mkdir(parents=True)
    backfill.write_text("- 0001-x.notes | 300 mon | a test\n", encoding="utf-8")
    assert mc.main(["--check"], str(root)) == 1
    out = capsys.readouterr()
    assert "0 yr from kyoto-1745         0001-x | 20 mon" in out.out and "no year or no era" in out.out and "0001-x.notes | 300 mon" not in out.out
    assert "neither marked nor named" in out.err
    backfill.write_text(backfill.read_text(encoding="utf-8") + "- 0001-x | * | the author's one reason for every amount here\n", encoding="utf-8")
    assert mc.main(["--check"], str(root)) == 0
    assert "0 amount(s) owed" in capsys.readouterr().out


def test_no_table_lists_the_periods_coins_and_no_backfill_names_nothing(tmp_path: pathlib.Path) -> None:
    mc = _mod()
    root = _repo(tmp_path, "<p>It cost 20 mon in 1750.</p>")
    (root / "research" / "assets" / "money-conversions.json").unlink()
    assert [a.text for a in mc.amounts(str(root))] == ["20 mon"]
    assert mc.passed_over(str(root)) == set()
    (root / "research" / "assets" / "money-conversions.json").write_text(json.dumps({"eras": {"x": {"years": "none", "units": {}}}}), encoding="utf-8")
    assert (mc.amounts(str(root))[0].near, mc.amounts(str(root))[0].gap) == ("", None)
