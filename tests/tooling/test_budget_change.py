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
    assert bc.main(["--root", str(root), "set", "web", "40", "1.1", "d.md", "SOUND.txt"]) == 0
    assert bc.load(root)["stages"]["web"] == {"status": "budgeted", "per_thing": 40, "exponent": 1.1, "derivation": "d.md", "verdict": "SOUND.txt"}
    why = bc.set_budget(root, "web", 30, 1.0, "d.md", "SOUND.txt")
    assert "budgeted already" in why and "make budget-change PHASE=web" in why, "a budgeted stage changes only with the GM's words"
    assert "no derivation at x.md" in bc.set_budget(root, "track", 1, 1, "x.md", "SOUND.txt")
    assert "no stage `nope`" in bc.set_budget(root, "nope", 1, 1, "d.md", "SOUND.txt")
    assert "reads nothing" in bc.set_budget(root, "track", 1, 1, "d.md", "missing.txt")


def test_a_change_needs_words_and_a_budget_and_is_logged_with_the_words(root: pathlib.Path) -> None:
    assert "no WORDS" in bc.change_budget(root, "web", 50, None, "  ")
    assert "make budget-set PHASE=web" in bc.change_budget(root, "web", 50, None, "the GM's words here")
    assert "no stage `nope`" in bc.change_budget(root, "nope", 50, None, "the GM's words here")
    bc.set_budget(root, "web", 40, 1.1, "d.md", "SOUND.txt")
    assert bc.main(["--root", str(root), "change", "web", "50", "--words", "raise it to fifty"]) == 0
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
