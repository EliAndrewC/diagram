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


def test_a_unit_answered_at_the_tree_s_key_before_the_checkpoint_holds_nothing(clone: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 374 wave 151: two glyph checks passed at the current engine key minutes before the step-back, and the tick was held
    for them as undispatched. A verdict at the tree's key answers the unit; one at an older key does not."""
    _map(clone, "inashiro", {"farmhouse": 9, "kiln": 1})
    trigger = cp.open_checkpoint(clone, T0 + 3600)
    units = cp.state(clone, T0 + 3600)["units"]
    _rule(clone, trigger, {"ruling": "continue", "why": "steady"})
    d = clone / ".git" / "review-verdicts"
    d.mkdir(exist_ok=True)
    for u in units:
        (d / f"{u}.json").write_text(json.dumps({"verdict": "PASS", "engine_key": "old"}))
    monkeypatch.setattr(cp, "current_key", lambda root: "now")
    assert "not yet dispatched" in cp.hold(clone, T0 + 3700), "a verdict at an older key answers nothing"
    for u in units:
        (d / f"{u}.json").write_text(json.dumps({"verdict": "PASS", "engine_key": "now"}))
    assert cp.hold(clone, T0 + 3700) == ""
    assert cp.current_key(clone) == "" or isinstance(cp.current_key(clone), str)


def test_the_bundle_carries_the_hour(clone: Path, tmp_path: Path) -> None:
    t1 = T0 + 3600
    lines = [
        {
            "type": "assistant",
            "timestamp": _iso(t1 + 10),
            "message": {"content": [{"type": "text", "text": "Trying a fifth seating order."}, {"type": "tool_use", "id": "a", "name": "Bash", "input": {"command": "make hamlet SEED=3"}}]},
        },
        {"type": "user", "timestamp": _iso(t1 + 70), "message": {"content": [{"type": "tool_result", "tool_use_id": "a", "content": "rolled"}]}},
        {
            "type": "assistant",
            "timestamp": _iso(t1 + 80),
            "requestId": "r",
            "message": {
                "usage": {"input_tokens": 10},
                "content": [{"type": "tool_use", "id": "b", "name": "Edit", "input": {"file_path": "bamboo.py", "old_string": "BAND = 40", "new_string": "BAND = 38"}}],
            },
        },
    ]
    tr = tmp_path / "s1.jsonl"
    tr.write_text("\n".join(json.dumps(x) for x in lines) + "\n")
    (clone / ".git" / "l7r-events" / "999-test.jsonl").write_text(
        "\n".join(
            json.dumps(x)
            for x in (
                {"t": _iso(T0), "ev": "", "sid": "s1"},
                {"t": _iso(t1 + 20), "ev": "SubagentStart", "aid": "x", "agent": "glyph-check", "cat": "review check", "sid": "s1"},
                {"t": _iso(t1 + 200), "ev": "SubagentStop", "aid": "x", "agent": "glyph-check", "verdict": "NEEDS-WORK", "sid": "s1"},
            )
        )
        + "\n"
    )
    out = tmp_path / "bundle"
    manifest = sb.build("hour:999-test@1", clone, out, t1, t1 + 3600, tr)
    assert "hour:999-test@1" in manifest.read_text() and "Room before packing" in manifest.read_text()
    assert "make hamlet" in (out / "time.md").read_text() and "1.0 min" in (out / "time.md").read_text()
    words = (out / "words.md").read_text()
    assert "fifth seating order" in words and "BAND = 40" in words and "rolled" not in words, "the session's words, no tool output"
    assert "glyph-check (review check): 180 s, NEEDS-WORK" in (out / "dispatches.md").read_text()
    assert "T01 a task" in (out / "task.md").read_text()


def test_the_bundle_reads_every_session_of_the_hour_and_names_one_it_left_out(clone: Path, tmp_path: Path) -> None:
    """The round arbiter's tooling fix on hour:385-approach-checklist@16: three sessions worked the feature that hour and the
    busiest - a page session - was the only one read, so the working session's words were missing. Every session is read now,
    each entry labeled; one with no transcript is named, and a cut says so."""
    t1 = T0 + 3600

    def said(text: str, at: float) -> dict:
        return {"type": "assistant", "timestamp": _iso(at), "message": {"content": [{"type": "text", "text": text}]}}

    projects = tmp_path / "projects"
    (projects / "p").mkdir(parents=True)
    (projects / "p" / "busy0000-page.jsonl").write_text(json.dumps(said("page session checks 0081", t1 + 30)) + "\n")
    (projects / "p" / "work0000-main.jsonl").write_text(json.dumps(said("T07 asks the arbiter", t1 + 60)) + "\n")
    events = [{"t": _iso(t1 + i), "ev": "", "sid": "busy0000-page"} for i in range(5)]
    events += [{"t": _iso(t1 + 50 + i), "ev": "", "sid": sid} for i, sid in enumerate(("work0000-main", "work0000-main", "gone0000-lost"))]
    (clone / ".git" / "l7r-events" / "999-test.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n")
    out = tmp_path / "bundle"
    sb.build("hour:999-test@1", clone, out, t1, t1 + 3600, None, projects=projects)
    words = (out / "words.md").read_text()
    assert "page session checks 0081" in words and "T07 asks the arbiter" in words, "every session's words, not the busiest's alone"
    assert words.index("page session") < words.index("T07 asks"), "merged in time order"
    assert "busy0000] SAID" in words and "work0000] SAID" in words, "each entry labeled by its session"
    assert "left out (no transcript found): gone0000" in words
    assert "summed over 2 sessions" in (out / "time.md").read_text()
    long = [said("x" * 500 + f" {i}", t1 + 100 + i) for i in range(100)]
    (projects / "p" / "work0000-main.jsonl").write_text("\n".join(json.dumps(r) for r in long) + "\n")
    sb.build("hour:999-test@1", clone, out, t1, t1 + 3600, None, projects=projects)
    assert "cut to the cap" in (out / "words.md").read_text().split("\n\n")[1], "a cut is named at the top"


def test_the_bundle_reads_a_session_logged_under_another_feature_and_names_minutes_with_no_words(clone: Path, tmp_path: Path) -> None:
    """The round arbiter's tooling fix on hour:395-shrine-building-costs@2: the main session's events went to 397's log while
    `.specify/feature.json` named 397, so its last 16 minutes of 395's work were in no session the bundle read. Sessions come
    from every feature log of the clone now, and a stretch of the window with no words is named in `words.md`."""
    t1 = T0 + 3600

    def said(text: str, at: float) -> dict:
        return {"type": "assistant", "timestamp": _iso(at), "message": {"content": [{"type": "text", "text": text}]}}

    projects = tmp_path / "projects"
    (projects / "p").mkdir(parents=True)
    (projects / "p" / "page0000-s.jsonl").write_text(json.dumps(said("page session applies round 2", t1 + 30)) + "\n")
    (projects / "p" / "main0000-m.jsonl").write_text(json.dumps(said("the tooling fixes landed", t1 + 3000)) + "\n")
    (clone / ".git" / "l7r-events" / "999-test.jsonl").write_text(json.dumps({"t": _iso(t1 + 30), "ev": "", "sid": "page0000-s"}) + "\n")
    (clone / ".git" / "l7r-events" / "998-other.jsonl").write_text(json.dumps({"t": _iso(t1 + 3000), "ev": "", "sid": "main0000-m"}) + "\n")
    out = tmp_path / "bundle"
    sb.build("hour:999-test@1", clone, out, t1, t1 + 3600, None, projects=projects)
    words = (out / "words.md").read_text()
    assert "the tooling fixes landed" in words, "a session logged under another feature of the clone is read"
    assert "NO WORDS FOUND for" in words and sb.silent_minutes([said("x", t1 + 30)], t1, t1 + 600) == [f"{_iso(t1 + 30)[11:16]}-{_iso(t1 + 600)[11:16]}"]


def test_over_the_cap_commands_shrink_before_any_reply_is_dropped() -> None:
    """The round arbiter's tooling fix on hour:383@1: long heredoc commands filled the cap and the hour's first replies were
    cut. Now each command keeps its first line and every reply stays, while they fit."""
    t1 = T0 + 3600
    recs = []
    for i in range(6):
        recs.append(
            {
                "type": "assistant",
                "timestamp": _iso(t1 + i * 60),
                "message": {
                    "content": [{"type": "text", "text": f"reply {i}"}, {"type": "tool_use", "id": str(i), "name": "Bash", "input": {"command": "python3 - <<'EOF'\n" + "x = 1\n" * 400 + "EOF"}}]
                },
            }
        )
    out = sb.words(recs, t1, t1 + 3600, cap=2000)
    assert all(f"reply {i}" in out for i in range(6)), "every reply kept"
    assert "RAN: python3 - <<'EOF'" in out and "x = 1" not in out, "each command cut to its first line"


def test_past_the_hour_a_gate_or_a_dispatch_is_refused_until_the_step_back_opens(clone: Path) -> None:
    assert cp.due(clone, "Bash", now=T0 + 3599) == "", "under the hour: nothing"
    assert "make step-back" in cp.due(clone, "Bash", now=T0 + 3600)
    assert "make step-back" in cp.due(clone, "Agent", "glyph-check", now=T0 + 3600)
    assert cp.due(clone, "Agent", "round-arbiter", now=T0 + 3600) == "", "the round arbiter is the step-back"
    cp.open_checkpoint(clone, T0 + 3601)
    assert cp.due(clone, "Agent", "glyph-check", now=T0 + 3700) == "", "open: the hour's work goes on"
    assert cp.main(["due", "--root", str(clone), "--tool", "Bash"]) in (0, 1)


def test_an_hour_spent_waiting_on_the_gm_opens_no_step_back(clone: Path) -> None:
    """The round arbiter's tooling fix on hour:385-approach-checklist@4 (feature 385): the clock counts the session's time - a
    63-minute window holding a 30-minute wait on the GM (a Stop, then the GM's typed prompt) is not due; the same wait ended by a
    background notification is the session's time, and is."""
    ev = clone / ".git" / "l7r-events" / "999-test.jsonl"
    rows = [{"t": _iso(T0), "ev": "", "sid": "s1"}, {"t": _iso(T0 + 600), "ev": "Stop", "sid": "s1"}, {"t": _iso(T0 + 600 + 1800), "ev": "UserPromptSubmit", "sid": "s1", "gm": True}]
    ev.write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert cp.gm_waits(clone, "999-test", T0, T0 + 63 * 60) == 1800.0
    assert not cp.state(clone, T0 + 63 * 60)["due"], "33 minutes of the session's own time"
    assert cp.state(clone, T0 + 91 * 60)["due"], "an hour of its own time once the wait is taken off"
    rows[-1]["gm"] = False  # a notification, not the GM
    ev.write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert cp.gm_waits(clone, "999-test", T0, T0 + 63 * 60) == 0.0 and cp.state(clone, T0 + 63 * 60)["due"]


def test_the_hour_is_decided_once_per_message_and_its_refusals_reach_the_step_back(clone: Path, tmp_path: Path) -> None:
    """The round arbiter's tooling fix on hour:385-approach-checklist@10: the hour turned between the second and third of five
    dispatches in one message, so the batch was split and three were re-sent; and the step-back's refusals.md missed the pair
    guard's refusals, logged `refused`, not `blocked`."""
    assert cp.due(clone, "Agent", "impl-drift", now=T0 + 3598) == "", "under the hour: admitted, and marked"
    assert cp.due(clone, "Agent", "quote-check", now=T0 + 3601) == "", "the same message: admitted though the hour turned"
    assert "make step-back" in cp.due(clone, "Agent", "quote-check", now=T0 + 3610), "a later message is refused"
    assert "make step-back" in cp.due(clone, "Agent", "quote-check", now=T0 + 3604), (
        "the window counts from the last dispatch admitted under the hour, not from a grace admission: it never chains into the next message (T05's plan review, the ruling's limit)"
    )
    assert "make step-back" in cp.due(clone, "Bash", now=T0 + 3601), "the grace is the message's dispatches, not a gate"
    log = tmp_path / "guard-log"
    log.mkdir()
    (log / "20261018T031500Z-a.json").write_text(json.dumps({"event": "refused", "guard": "pair", "rule": "step-back-due", "detail": "Agent quote-check", "sid": "s1"}))
    (log / "20261018T031600Z-b.json").write_text(json.dumps({"event": "escaped", "guard": "pair", "sid": "s1"}))
    got = sb.refusals(["s1"], cp.time.mktime((2026, 10, 18, 3, 0, 0, 0, 0, 0)) - cp.time.timezone, 2e9, log)
    assert got == ["- 03:15 pair: step-back-due - Agent quote-check"]
