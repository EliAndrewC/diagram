"""The box that lands open and the feature that waits (feature 375, plan D18).

375 lands batch by batch and must stay open between them, so one standing task carries `[lands-open]`. The plan review
(rounds 2 and 3) bounded the mark: it is honored only on the GM-review box of a feature with a row for the GM, or on a task
the CLEAR plan's `**Lands open**:` line names - a hand-typed mark is no exemption, at the push or at `make tick`. And a
spec that must wait for another declares `**Waits on**: NNN`, which `make tick` holds.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys

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

PLAN = "# plan\n\n**Lands open**: T99\n"


def _feature(root: pathlib.Path, name: str, tasks: str, plan: str | None = PLAN, clear: bool = True, spec: str = "") -> pathlib.Path:
    d = root / "specs" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "tasks.md").write_text(tasks)
    (d / "spec.md").write_text(spec or "# Feature: x\n\n**Status**: In progress\n")
    if plan is not None:
        (d / "plan.md").write_text(plan)
        sha = hashlib.sha256(plan.encode()).hexdigest()
        (d / "plan-review.json").write_text(json.dumps({"plan_sha256": sha, "plan_text": plan, "decisions": [], "verdict": "CLEAR" if clear else "BLOCKED"}))
    return d


def test_only_the_plan_named_and_the_gm_boxes_land_open(tmp_path: pathlib.Path) -> None:
    d = _feature(tmp_path, "375-x", "- [x] T01 a\n- [ ] T99 later [lands-open]\n")
    assert todo.holding(d) == [] and todo.feature(d).state == "in progress", "open to every reader, holding nothing"
    d = _feature(tmp_path, "376-x", "- [ ] T99 later [lands-open]\n", clear=False)
    assert "honored only" in todo.holding(d)[0], "a BLOCKED plan names nothing"
    d = _feature(tmp_path, "377-x", "- [ ] T98 later [lands-open]\n")
    assert "honored only" in todo.holding(d)[0], "a task the plan does not name"
    d = _feature(tmp_path, "378-x", "- [ ] T01 a\n  - [ ] research pass\n", plan=None)
    assert todo.holding(d) == ["T01 a", "research pass"]
    gm = "- [x] T01 a\n- [ ] GM review (make gm-reviewed F=379) [lands-open]\n"
    d = _feature(tmp_path, "379-x", gm, plan=None)
    assert "honored only" in todo.holding(d)[0], "no row for the GM: no such box"
    (d / "gm-review.jsonl").write_text('{"row": 1, "reviewed": "2026-10-11"}\n')
    assert todo.holding(d) != [], "a reviewed row is not open"
    (d / "gm-review.jsonl").write_text('{"row": 1, "reviewed": "2026-10-11"}\n{"row": 2}\n\n')
    assert todo.holding(d) == []
    assert todo.holding(tmp_path / "specs" / "no-such") == []
    d = _feature(tmp_path, "381-x", "- [ ] T07 build the `[lands-open]` mark and test it\n")
    assert todo.holding(d) == ["T07 build the `[lands-open]` mark and test it"], "a mention is an ordinary open box, never a mark"
    assert todo.lands_open_ids(_feature(tmp_path, "380-x", "", plan="# plan\n")) == set()


def test_make_tick_holds_a_waiting_feature_and_a_hand_typed_mark(tmp_path: pathlib.Path) -> None:
    _feature(tmp_path, "375-x", "- [x] T01 a\n- [ ] T99 later [lands-open]\n")
    waiting = _feature(tmp_path, "374-y", "- [ ] T01 a\n", plan=None, spec="# Feature\n\n**Waits on**: 375 (its D18)\n")
    why = tt.waits_or_marks(tmp_path, waiting)
    assert "waits on feature 375 (375-x), which is still open" in why
    (tmp_path / "specs" / "375-x" / "tasks.md").write_text("- [x] T01 a\n- [x] T99 later [lands-open]\n")
    assert tt.waits_or_marks(tmp_path, waiting) == "", "375 closed: 374 may tick"
    gone = _feature(tmp_path, "373-z", "- [ ] T01 a\n", plan=None, spec="**Waits on**: 999\n")
    assert tt.waits_or_marks(tmp_path, gone) == "", "a feature that does not exist holds nothing"
    marked = _feature(tmp_path, "372-w", "- [ ] T01 a [lands-open]\n", plan=None)
    assert tt.waits_or_marks(tmp_path, marked).startswith("a [lands-open] mark the tooling did not put here: T01 a")


def test_tick_loads_the_todo_module_as_the_command_does() -> None:
    """`make tick` runs tick-task.py in a fresh interpreter, where nothing has registered `speckit-todo.py`: loading it there
    failed on its dataclass (found at batch 1's own first tick), while a test that had loaded it first passed."""
    sys.modules.pop("speckit_todo", None)
    assert tt._todo().CLOSING == ("done", "superseded by", "withdrawn")


def test_the_holding_command_line(tmp_path: pathlib.Path, capsys) -> None:  # noqa: ANN001
    d = _feature(tmp_path, "377-x", "- [ ] T01 a\n- [ ] T99 later [lands-open]\n")
    assert todo.main(["--holding", str(d)]) == 0
    assert capsys.readouterr().out == "T01 a\n"
