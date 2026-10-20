"""What holds a landing, and the feature that waits (feature 375 plan D18; rewritten by feature 405 T32, D4).

The GM, 2026-10-20, after 405's first claim spent four minutes on a reviewed `**Lands open**:` line: "I do not want each
landing to owe a lands open line ... because that's going to slow things down." So a feature in progress holds a landing only
through the task being worked: the clone's active task (`make task-start`), while it is open and the landing does not tick it
(`L7R_LAND_TICKS`, which `make land` sets once that task's tick checks pass). A task nobody has started holds nothing, and a
`[lands-open]` mark is plain text. A spec that must wait for another still declares `**Waits on**: NNN`, which `make tick` holds.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

from tests._scripts import script


def _load(name: str, as_: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(as_, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[as_] = mod
    spec.loader.exec_module(mod)
    return mod


todo = _load("speckit-todo.py", "speckit_todo_t")
tt = _load("tick-task.py", "tick_task_t")


def _repo(root: pathlib.Path) -> pathlib.Path:
    if not (root / ".git").exists():
        subprocess.run(["git", "init", "-q", str(root)], check=True)
    return root


def _feature(root: pathlib.Path, name: str, tasks: str, spec: str = "") -> pathlib.Path:
    d = _repo(root) / "specs" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "tasks.md").write_text(tasks)
    (d / "spec.md").write_text(spec or "# Feature: x\n\n**Status**: In progress\n")
    return d


def _start(root: pathlib.Path, feature: str, task: str) -> None:
    (root / ".git" / "active-task").write_text(json.dumps({"feature": feature, "task": task}) + "\n")


def test_a_task_nobody_has_started_holds_nothing(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("L7R_LAND_TICKS", raising=False)
    d = _feature(tmp_path, "405-x", "- [x] T12 a\n- [ ] T01 later\n- [ ] T02 later [lands-open]\n  - [ ] research pass\n")
    assert todo.holding(d) == [] and todo.feature(d).state == "in progress", "open to every reader, holding no landing"
    assert todo.holding(tmp_path / "specs" / "no-such") == []


def test_the_active_task_holds_until_the_landing_ticks_it(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("L7R_LAND_TICKS", raising=False)
    d = _feature(tmp_path, "405-x", "- [ ] T12 the claim\n- [ ] T01 later\n")
    _start(tmp_path, "405-x", "T12")
    assert todo.holding(d) == ["T12 the claim  <- the active task (make task-start), open: land it with make land F=405 T=T12"]
    monkeypatch.setenv("L7R_LAND_TICKS", "T30 T12")
    assert todo.holding(d) == [], "make land ticks it once the push succeeds"
    monkeypatch.delenv("L7R_LAND_TICKS")
    (d / "tasks.md").write_text("- [x] T12 the claim\n- [ ] T01 later\n")
    assert todo.holding(d) == [], "ticked: nothing is mid-task"
    (d / "tasks.md").write_text("- [x] T12 the claim\n      - [ ] research pass\n- [ ] T01 later\n")
    assert todo.holding(d)[0].startswith("research pass  <- open under the active task T12"), "a box nested under it: not done"
    _start(tmp_path, "406-y", "T01")
    (d / "tasks.md").write_text("- [ ] T12 the claim\n- [ ] T01 later\n")
    assert todo.holding(d) == [], "another feature's active task holds this one nothing"


def test_the_gm_review_box_never_holds(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("L7R_LAND_TICKS", raising=False)
    d = _feature(tmp_path, "379-x", "- [x] T01 a\n- [ ] GM review (make gm-reviewed F=379) [lands-open]\n")
    assert todo.holding(d) == []


def test_make_tick_holds_a_waiting_feature_and_no_mark(tmp_path: pathlib.Path) -> None:
    _feature(tmp_path, "375-x", "- [x] T01 a\n- [ ] T99 later [lands-open]\n")
    waiting = _feature(tmp_path, "374-y", "- [ ] T01 a\n", spec="# Feature\n\n**Waits on**: 375 (its D18)\n")
    why = tt.waits_or_marks(tmp_path, waiting)
    assert "waits on feature 375 (375-x), which is still open" in why
    (tmp_path / "specs" / "375-x" / "tasks.md").write_text("- [x] T01 a\n- [x] T99 later [lands-open]\n")
    assert tt.waits_or_marks(tmp_path, waiting) == "", "375 closed: 374 may tick"
    gone = _feature(tmp_path, "373-z", "- [ ] T01 a\n", spec="**Waits on**: 999\n")
    assert tt.waits_or_marks(tmp_path, gone) == "", "a feature that does not exist holds nothing"
    marked = _feature(tmp_path, "372-w", "- [ ] T01 a [lands-open]\n")
    assert tt.waits_or_marks(tmp_path, marked) == "", "a mark is text; it neither exempts nor refuses"


def test_tick_loads_the_todo_module_as_the_command_does() -> None:
    """`make tick` runs tick-task.py in a fresh interpreter, where nothing has registered `speckit-todo.py`: loading it there
    failed on its dataclass (found at batch 1's own first tick), while a test that had loaded it first passed."""
    sys.modules.pop("speckit_todo", None)
    assert tt._todo().CLOSING == ("done", "superseded by", "withdrawn")


def test_the_holding_command_line(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("L7R_LAND_TICKS", raising=False)
    d = _feature(tmp_path, "377-x", "- [ ] T01 a\n- [ ] T99 later\n")
    _start(tmp_path, "377-x", "T01")
    assert todo.main(["--holding", str(d)]) == 0
    assert capsys.readouterr().out.startswith("T01 a  <- the active task")
