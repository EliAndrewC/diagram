"""`scripts/budget_change.py` - the one writer of `dev/work-budget.json` (feature 443 T03, plan D6; FR-005, SC-003).

A first budget only from a SOUND MODE BUDGET verdict; every later change, and the program's budget, only with WORDS (the GM's,
checked by `budget-change-hooks.sh`, `tests/hooks/test-budget-change-hooks.sh`), and logged with them.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import pathlib
import shutil

import pytest

from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("budget_change", script("budget_change"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bc = _load()


@pytest.fixture
def root(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / "dev").mkdir()
    shutil.copy(REPO / bc.TABLE, tmp_path / bc.TABLE)
    (tmp_path / "d.md").write_text("the derivation\n")
    for word in ("SOUND", "LOOSE", "UNDERIVED"):
        (tmp_path / f"{word}.txt").write_text(f"{word} - the reason\n\nthe body\n")
    return tmp_path


def test_the_table_holds_every_stage_of_the_pipeline_unbudgeted() -> None:
    """The table's stages are `STAGES`, named as `make work-budget` names them, so it cannot drift from the engine."""
    tree = ast.parse((REPO / "l7r/diagram/hamletgen/driver.py").read_text(encoding="utf-8"))
    stages = next(n.value for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "STAGES")
    names = [e.id.removeprefix("stage_") for e in stages.elts]  # type: ignore[attr-defined]
    table = json.loads((REPO / bc.TABLE).read_text(encoding="utf-8"))
    assert list(table["stages"]) == names
    assert set(table["program"]) == {"ops_at_40", "exponent"}


@pytest.mark.parametrize("word", ["LOOSE", "UNDERIVED"])
def test_a_first_budget_needs_a_sound_verdict(root: pathlib.Path, word: str) -> None:
    why = bc.set_budget(root, "web", 40, 1.0, "d.md", f"{word}.txt")
    assert f"reads {word}, not SOUND" in why and "make work-budget-bundle MODE=budget" in why
    assert bc.load(root)["stages"]["web"] == {"status": "unbudgeted"}


def test_a_sound_verdict_sets_a_first_budget_and_a_second_set_is_refused(root: pathlib.Path) -> None:
    assert "no items at 20, 40, 80 households" in bc.set_budget(root, "web", 40, 1.1, "d.md", "SOUND.txt"), "the derivation's items are owed"
    assert bc.main(["--root", str(root), "set", "web", "40", "1.1", "d.md", "SOUND.txt", "--items-at-20", "10", "--items-at-40", "20", "--items-at-80", "40"]) == 0
    assert bc.load(root)["stages"]["web"] == {
        "status": "budgeted",
        "per_thing": 40,
        "exponent": 1.1,
        "derivation": "d.md",
        "verdict": "SOUND.txt",
        "items_at_20": 10,
        "items_at_40": 20,
        "items_at_80": 40,
    }
    why = bc.set_budget(root, "web", 30, 1.0, "d.md", "SOUND.txt")
    assert "budgeted already" in why and "make budget-change PHASE=web" in why, "a budgeted stage changes only with the GM's words"
    assert "no derivation at x.md" in bc.set_budget(root, "track", 1, 1, "x.md", "SOUND.txt")
    assert "no stage `nope`" in bc.set_budget(root, "nope", 1, 1, "d.md", "SOUND.txt")
    assert "reads nothing" in bc.set_budget(root, "track", 1, 1, "d.md", "missing.txt")


def test_a_change_needs_words_and_a_budget_and_is_logged_with_the_words(root: pathlib.Path) -> None:
    assert "no WORDS" in bc.change_budget(root, "web", 50, None, "  ")
    assert "make budget-set PHASE=web" in bc.change_budget(root, "web", 50, None, "the GM's words here")
    assert "no stage `nope`" in bc.change_budget(root, "nope", 50, None, "the GM's words here")
    bc.set_budget(root, "web", 40, 1.1, "d.md", "SOUND.txt", {20: 10, 40: 20, 80: 40})
    assert bc.main(["--root", str(root), "change", "web", "50", "--words", "raise it to fifty", "--items-at-80", "45"]) == 0
    assert bc.load(root)["stages"]["web"]["items_at_80"] == 45 and bc.load(root)["stages"]["web"]["items_at_40"] == 20
    assert bc.load(root)["stages"]["web"]["per_thing"] == 50 and bc.load(root)["stages"]["web"]["exponent"] == 1.1
    assert bc.change_budget(root, "web", 55, 1.2, "and the exponent too") == ""
    rows = [json.loads(ln) for ln in (root / bc.LOG).read_text().splitlines()]
    assert [r["words"] for r in rows] == ["raise it to fifty", "and the exponent too"]
    assert rows[1]["from"] == {"per_thing": 50, "exponent": 1.1} and rows[1]["to"] == {"per_thing": 55, "exponent": 1.2}


def test_the_programs_budget_needs_words_and_is_logged(root: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert bc.main(["--root", str(root), "program", "1000000", "1.2"]) == 1
    assert "no WORDS" in capsys.readouterr().err
    assert bc.main(["--root", str(root), "program", "1000000", "1.2", "--words", "a million at forty"]) == 0
    assert bc.load(root)["program"] == {"ops_at_40": 1000000, "exponent": 1.2}
    row = json.loads((root / bc.LOG).read_text().splitlines()[-1])
    assert row["what"] == "program" and row["words"] == "a million at forty"


def test_an_arbiter_accept_pins_a_first_budget_bound_to_its_derivation(root: pathlib.Path) -> None:
    """Feature 444 FR-013, SC-008 (the GM 2026-10-28, answering 444#0: "Yes, I am okay with option one, letting the arbiters acceptance
    pin it"): `budget-set ARBITER=` pins only on an accept the arbiter's log holds naming the stage, and the pin is bound to the
    derivation - a change after it is flagged as owing the arbiter's ruling."""
    feat = root / "specs" / "444-x"
    (feat / "phases").mkdir(parents=True)
    (feat / "phases" / "web.derivation.md").write_text("the derivation\n")
    d = "specs/444-x/phases/web.derivation.md"
    items = {20: 10, 40: 20, 80: 40}
    assert "holds no accept at ask:444-T05-r9 naming `web`" in bc.set_budget(root, "web", 40, 1.1, d, "", items, "ask:444-T05-r9"), "no log"
    log = feat / "arbiter.jsonl"
    log.write_text(json.dumps({"trigger": "ask:444-T05-r9", "ruling": "continue", "what": "web again"}) + "\n")
    assert "holds no accept" in bc.set_budget(root, "web", 40, 1.1, d, "", items, "ask:444-T05-r9"), "a continue is no accept"
    log.write_text(json.dumps({"trigger": "ask:444-T05-r9", "ruling": "accept", "what": "the track stands"}) + "\n")
    assert "holds no accept" in bc.set_budget(root, "web", 40, 1.1, d, "", items, "ask:444-T05-r9"), "an accept that names another stage"
    log.write_text(json.dumps({"trigger": "ask:444-T05-r9", "ruling": "accept", "what": "web stands as it reads"}) + "\n")
    assert "its totals' spread" in bc.set_budget(root, "web", 40, 1.1, d, "", items, "ask:444-T05-r9"), "the spread is owed"
    for n in (1, 2, 3):
        (feat / "phases" / f"web.verdict-{n}.txt").write_text("UNDERIVED - x\n")
    args = ["--arbiter", "ask:444-T05-r9", "--spread", "32,280-38,506 at 20", "--items-at-20", "10", "--items-at-40", "20", "--items-at-80", "40"]
    assert bc.main(["--root", str(root), "set", "web", "40", "1.1", d, "", *args]) == 0
    row = bc.load(root)["stages"]["web"]
    assert row["pinned_on"] == "accept" and row["verdict"] == "ask:444-T05-r9" and row["derivation_sha"] == bc.derivation_sha(root, d)
    assert row["rounds"] == 3 and row["spread"] == "32,280-38,506 at 20", "the rounds and the spread, for the program target"

    import importlib  # noqa: PLC0415

    wb = importlib.import_module("l7r.diagram.tools.work_budget")
    assert wb.stale_pins(bc.load(root), str(root)) == [], "the derivation as pinned"
    (feat / "phases" / "web.derivation.md").write_text("the derivation, one figure changed\n")
    bad = wb.stale_pins(bc.load(root), str(root))
    assert len(bad) == 1 and "changed since the arbiter's accept pinned it (ask:444-T05-r9)" in bad[0] and "make arbiter-ask" in bad[0]
    assert bad[0] in wb.held(bc.load(root), {"stages": {}}), "the push's ratchet refuses it too"
