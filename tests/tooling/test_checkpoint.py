"""Feature 383, phase 3 (SC-007): the feature's hourly checkpoint - the step-back and every owed review, held at `make tick`.

WHAT THESE PROVE, on a real git fixture with a feature's event log: under an hour nothing is held and the checkpoint will not
open; on the hour `make tick`'s hold names the step-back; `make step-back` opens one trigger the round arbiter rules on; its
bundle carries the hour; a quiet `continue` adds nothing to the GM's review and restarts the clock; a `tooling_fix` opens a
379 item that holds the next tick; a `change-route` needs its route; a review unit owed at the checkpoint holds the tick until
it is dispatched.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from tests._scripts import script


def _mod(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), script(name))
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


cp = _mod("checkpoint")
sb = _mod("stepback_bundle")
arb = sys.modules.get("hm_arbiter") or _mod("hm_arbiter")
T0 = 1_800_000_000.0


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


def _iso(t: float) -> str:
    return datetime.datetime.fromtimestamp(t, datetime.UTC).isoformat().replace("+00:00", "Z")


def _map(root: Path, name: str, classes: dict[str, int]) -> None:
    d = root / "pool" / "hamlets" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps({"meta": {"name": name}, "houses": [[1, 1]], "ink_classes": classes}))
    (d / f"{name}.notes.md").write_text(f"# {name}\n")
    for ext in ("svg", "png", "html"):
        (d / f"{name}.{ext}").write_text("x")


@pytest.fixture
def clone(tmp_path: Path) -> Path:
    """A pool hamlet at `origin/main`, and a live feature 999 whose event log began at T0."""
    root = tmp_path / "clone"
    root.mkdir()
    git(root.parent, "init", "-q", str(root))
    git(root, "config", "user.email", "t@t")
    git(root, "config", "user.name", "t")
    _map(root, "inashiro", {"farmhouse": 9})
    git(root, "add", "-A")
    git(root, "commit", "-qm", "the pool")
    git(root, "update-ref", "refs/remotes/origin/main", git(root, "rev-parse", "HEAD"))
    d = root / "specs" / "999-test"
    d.mkdir(parents=True)
    (d / "spec.md").write_text("# Feature 999\n\n**Status**: In progress\n")
    (d / "tasks.md").write_text("# Tasks\n\n## Occasions\n\n- none: fixture\n\n## Work\n\n- [ ] T01 a task\n      research: rendering\n")
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/999-test"}))
    ev = root / ".git" / "l7r-events"
    ev.mkdir(parents=True)
    (ev / "999-test.jsonl").write_text(json.dumps({"t": _iso(T0), "ev": "", "sid": "s1"}) + "\n")
    return root


def _rule(root: Path, trigger: str, ruling: dict) -> dict:
    import os

    here = os.getcwd()
    try:
        os.chdir(root)
        return arb.record_ruling(root, trigger, ruling, "round-arbiter")
    finally:
        os.chdir(here)


def _gm_rows(root: Path) -> list[dict]:
    f = root / "specs" / "999-test" / "gm-review.jsonl"
    return [json.loads(x) for x in f.read_text().splitlines()] if f.is_file() else []


def test_under_an_hour_nothing_is_held_and_the_checkpoint_will_not_open(clone: Path) -> None:
    assert cp.hold(clone, T0 + 3599) == ""
    with pytest.raises(ValueError, match="not due"):
        cp.open_checkpoint(clone, T0 + 3599)


def test_on_the_hour_the_tick_is_held_until_the_step_back_is_ruled(clone: Path) -> None:
    assert "make step-back" in cp.hold(clone, T0 + 3600)
    trigger = cp.open_checkpoint(clone, T0 + 3601)
    assert trigger == "hour:999-test@1"
    assert cp.open_checkpoint(clone, T0 + 3700) == trigger, "opened once"
    assert trigger in arb.owed(clone), "the round arbiter's trigger is recorded"
    assert "round-arbiter" in cp.hold(clone, T0 + 3700) and "step-back-999-test-1" in cp.hold(clone, T0 + 3700)
    _rule(clone, trigger, {"ruling": "continue", "why": "a quiet hour of steady progress"})
    assert cp.hold(clone, T0 + 3800) == "", "ruled, and nothing owed: the tick passes"
    assert _gm_rows(clone) == [], "a quiet continue adds nothing to the GM's review"
    st = cp.state(clone, T0 + 3800)
    assert st["hour"] == 2 and st["since"] == T0 + 3601, "the clock restarts from when the checkpoint opened"
    assert "make step-back" in cp.hold(clone, T0 + 3601 + 3600), "and the next hour comes due"


def test_a_ruling_s_tooling_fix_opens_an_item_that_holds_the_next_tick(clone: Path) -> None:
    trigger = cp.open_checkpoint(clone, T0 + 3600)
    _rule(clone, trigger, {"ruling": "continue", "why": "progress, but one probe ran ten times", "tooling_fix": "make probe keeps its rolls"})
    assert cp.hold(clone, T0 + 3700) == ""
    assert "make probe keeps its rolls" in arb.fix_hold(clone / "specs" / "999-test"), "the 379 hold names the fix"
    assert [r.get("tooling_fix") for r in _gm_rows(clone)] == ["make probe keeps its rolls"]


def test_a_change_of_route_names_its_route_and_reaches_the_gm(clone: Path) -> None:
    trigger = cp.open_checkpoint(clone, T0 + 3600)
    with pytest.raises(ValueError, match="change-route"):
        _rule(clone, trigger, {"ruling": "change-route", "why": "five seating orders tried"})
    with pytest.raises(ValueError, match="one of"):
        _rule(clone, trigger, {"ruling": "accept", "why": "an hour has no accept"})
    _rule(clone, trigger, {"ruling": "change-route", "why": "five seating orders tried", "what": "widen the strip band (a convenience number) before another order"})
    assert [r["ruling"] for r in _gm_rows(clone)] == ["change-route"]


def test_something_for_the_gm_reaches_the_gm_under_a_continue(clone: Path) -> None:
    trigger = cp.open_checkpoint(clone, T0 + 3600)
    _rule(clone, trigger, {"ruling": "continue", "why": "steady", "for_gm": "the tier's packing rule wants the GM's word"})
    assert [r.get("for_gm") for r in _gm_rows(clone)] == ["the tier's packing rule wants the GM's word"]


def test_a_review_owed_at_the_checkpoint_holds_the_tick_until_it_is_dispatched(clone: Path) -> None:
    _map(clone, "inashiro", {"farmhouse": 9, "kiln": 1})  # an element new to the map: a glyph unit owed
    trigger = cp.open_checkpoint(clone, T0 + 3600)
    units = cp.state(clone, T0 + 3600)["units"]
    assert units and all(u.startswith("glyph-check") for u in units)
    _rule(clone, trigger, {"ruling": "continue", "why": "steady"})
    assert "not yet dispatched" in cp.hold(clone, T0 + 3700)
    p = clone / ".git" / "pairing-state.json"
    p.write_text(json.dumps({"dispatched": {u: {"key": "k", "at": int(T0 + 3650)} for u in units}}))
    assert cp.hold(clone, T0 + 3700) == ""


def test_the_bundle_carries_the_hour(clone: Path, tmp_path: Path) -> None:
    t1 = T0 + 3600
    lines = [
        {"type": "assistant", "timestamp": _iso(t1 + 10), "message": {"content": [{"type": "text", "text": "Trying a fifth seating order."},
                                                                                   {"type": "tool_use", "id": "a", "name": "Bash", "input": {"command": "make hamlet SEED=3"}}]}},
        {"type": "user", "timestamp": _iso(t1 + 70), "message": {"content": [{"type": "tool_result", "tool_use_id": "a", "content": "rolled"}]}},
        {"type": "assistant", "timestamp": _iso(t1 + 80), "requestId": "r", "message": {"usage": {"input_tokens": 10}, "content": [
            {"type": "tool_use", "id": "b", "name": "Edit", "input": {"file_path": "bamboo.py", "old_string": "BAND = 40", "new_string": "BAND = 38"}}]}},
    ]
    tr = tmp_path / "s1.jsonl"
    tr.write_text("\n".join(json.dumps(x) for x in lines) + "\n")
    (clone / ".git" / "l7r-events" / "999-test.jsonl").write_text("\n".join(json.dumps(x) for x in (
        {"t": _iso(T0), "ev": "", "sid": "s1"},
        {"t": _iso(t1 + 20), "ev": "SubagentStart", "aid": "x", "agent": "glyph-check", "cat": "review check", "sid": "s1"},
        {"t": _iso(t1 + 200), "ev": "SubagentStop", "aid": "x", "agent": "glyph-check", "verdict": "NEEDS-WORK", "sid": "s1"},
    )) + "\n")
    out = tmp_path / "bundle"
    manifest = sb.build("hour:999-test@1", clone, out, t1, t1 + 3600, tr)
    assert "hour:999-test@1" in manifest.read_text() and "Room before packing" in manifest.read_text()
    assert "make hamlet" in (out / "time.md").read_text() and "1.0 min" in (out / "time.md").read_text()
    words = (out / "words.md").read_text()
    assert "fifth seating order" in words and "BAND = 40" in words and "rolled" not in words, "the session's words, no tool output"
    assert "glyph-check (review check): 180 s, NEEDS-WORK" in (out / "dispatches.md").read_text()
    assert "T01 a task" in (out / "task.md").read_text()
