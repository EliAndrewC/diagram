"""`scripts/gates/phase_sources.py` (feature 444, the GM 2026-10-30): a phase task's stage held off-limits as `make task-start`
records it - its stage module's package, the modules its counters name, an `old-code:` glob - and one file let through by
`make phase-read` for ten minutes."""

from __future__ import annotations

import datetime
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "gates"))
import phase_sources as ps  # noqa: E402

pytestmark = pytest.mark.tooling


def _repo(tmp: pathlib.Path) -> pathlib.Path:
    root = tmp / "repo"
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    water = root / "l7r" / "diagram" / "hamletgen" / "water"
    water.mkdir(parents=True)
    (water / "fields.py").write_text("def stage_field():\n    pass\n")
    (water / "comb.py").write_text("x = 1\n")
    (root / "l7r" / "diagram" / "waterfields").mkdir(parents=True)
    (root / "l7r" / "diagram" / "waterfields" / "lay.py").write_text("def lay_comb():\n    pass\n")
    (root / "l7r" / "diagram" / "settlement").mkdir(parents=True)
    (root / "l7r" / "diagram" / "settlement" / "bunds.py").write_text("y = 2\n")
    runs = root / "dev" / "work-budget"
    runs.mkdir(parents=True)
    (runs / "1.json").write_text(json.dumps({"rows": [{"stages": {"field": {"ops": {"candidate@lay_comb": 3}}}}]}))
    return root


def test_a_phase_task_holds_its_stage_its_counted_modules_and_its_old_code_globs(tmp_path: pathlib.Path) -> None:
    root = _repo(tmp_path)
    block = "- [ ] T16 phase: field\n      phase: field\n      old-code: l7r/diagram/settlement/*.py\n"
    line = ps.record(root, "444-x", "T16", block)
    state = json.loads((root / ".git" / ps.STATE).read_text())
    assert state["phase"] == "field" and state["task"] == "T16" and "4 file(s)" in line
    assert state["files"] == [
        "l7r/diagram/hamletgen/water/comb.py",
        "l7r/diagram/hamletgen/water/fields.py",
        "l7r/diagram/settlement/bunds.py",
        "l7r/diagram/waterfields/lay.py",
    ], "the stage's package, the counted module, the old-code glob"
    assert ps.record(root, "444-x", "T17", "- [ ] T17 a tooling task\n") == "" and not (root / ".git" / ps.STATE).exists(), "another task clears it"


def test_phase_read_lets_one_held_file_through_for_ten_minutes(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _repo(tmp_path)
    assert ps.allow(root, "l7r/diagram/hamletgen/water/fields.py", "nothing held") == 2
    ps.record(root, "444-x", "T16", "      phase: field\n")
    assert ps.allow(root, "l7r/diagram/hamletgen/water/fields.py", "why") == 2, "a reason of two words"
    assert ps.allow(root, "l7r/diagram/settlement/bunds.py", "not held here") == 2
    now = datetime.datetime(2026, 10, 30, 20, 0, tzinfo=datetime.UTC)
    assert ps.allow(root, str(root / "l7r/diagram/hamletgen/water/fields.py"), "replacing the stage function", now) == 0
    allow = json.loads((root / ".git" / ps.STATE).read_text())["allow"]
    assert allow == [{"file": "l7r/diagram/hamletgen/water/fields.py", "until": "2026-10-30T20:10:00Z", "why": "replacing the stage function"}]
    assert "may be read until 20:10" in capsys.readouterr().out


def test_main_takes_allow_and_nothing_else(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _repo(tmp_path)
    monkeypatch.chdir(root)
    assert ps.main(["bogus"]) == 2
    assert ps.main(["allow", "x.py", "two words"]) == 2, "no hold yet"


def test_a_repo_with_no_work_budget_run_holds_the_stage_package_alone(tmp_path: pathlib.Path) -> None:
    root = _repo(tmp_path)
    for p in (root / "dev" / "work-budget").glob("*.json"):
        p.unlink()
    ps.record(root, "444-x", "T16", "      phase: field\n")
    assert json.loads((root / ".git" / ps.STATE).read_text())["files"] == ["l7r/diagram/hamletgen/water/comb.py", "l7r/diagram/hamletgen/water/fields.py"]
