"""`scripts/measure/where_time.py` - `make where-time` (feature 385 T77, plan D96): the time from a session's Stop to its next
prompt is between turns, however many events fall inside; work inside a turn goes to the task active at its start."""

from __future__ import annotations

import importlib.util
import sys

from tests._scripts import script

_spec = importlib.util.spec_from_file_location("where_time", script("where_time.py"))
assert _spec and _spec.loader
wt = importlib.util.module_from_spec(_spec)
sys.modules["where_time"] = wt
_spec.loader.exec_module(wt)


def _t(minute: float) -> str:
    h, m = divmod(int(minute * 60), 3600)
    mm, ss = divmod(m, 60)
    return f"2026-10-18T{h:02d}:{mm:02d}:{ss:02d}Z"


def ev(kind: str, minute: float, **kw: str) -> dict:
    return {"sid": "s1", "ev": kind, "t": _t(minute), **kw}


def test_the_stall_between_turns_is_its_own_column_and_never_thinking() -> None:
    starts = [(wt.fr.parse_t(_t(0)), "T05")]
    events = [
        ev("UserPromptSubmit", 0),
        ev("PreToolUse", 1, tool="Bash", cat="gate"),
        ev("PostToolUse", 6, tool="Bash"),
        ev("Stop", 10),
        # the overnight stall: hook events every 50 minutes, each under the hour - booked "thinking" before T77
        ev("PostToolUse", 60, tool="Bash"),
        ev("PreToolUse", 110, tool="Bash", cat="gate"),
        ev("PostToolUse", 160, tool="Bash"),
        ev("UserPromptSubmit", 300),
        ev("PreToolUse", 302, tool="Edit", cat="edit"),
        ev("Stop", 305),
    ]
    out, _agents, _secs = wt.tables(events, starts)
    c = out["T05"]
    assert round(c[wt.GM_AWAY] / 60) == 290, "10 -> 300: one window, ended by the GM after an hour, every piece of it"
    assert round(c["model"] / 60) == 7 and round(c["gate/tests"] / 60) == 5 and round(c["tools"] / 60) == 3, "the turns' own work keeps its buckets"
    table = wt.render(out, _agents, _secs, ["T05"])
    assert "| T05 | 305 |" in table and wt.GM_AWAY in table.splitlines()[0]


def test_a_window_is_classed_by_the_prompt_that_ends_it() -> None:
    """T90 (plan D111): a notification - waiting on work; the GM within the hour - the GM; past it - the GM away."""
    starts = [(wt.fr.parse_t(_t(0)), "T05")]
    events = [
        ev("UserPromptSubmit", 0),
        ev("Stop", 1),
        ev("UserPromptSubmit", 4, gm=False),  # a background notification
        ev("Stop", 5),
        ev("UserPromptSubmit", 25, gm=True),  # the GM, twenty minutes on
    ]
    c = wt.tables(events, starts)[0]["T05"]
    assert round(c[wt.WAIT_WORK] / 60) == 3 and round(c[wt.WAIT_GM] / 60) == 20 and c[wt.GM_AWAY] == 0


def test_a_gap_is_booked_to_the_task_its_call_names_else_the_last_named_else_the_mark() -> None:
    """T89 (plan D110): booked by the mark, T10 showed 320 min of other tasks' planning; a call names its own task."""
    assert wt.named_task('{"command": "make decide F=385 T=T60"}', "385") == "T60"
    assert wt.named_task('{"command": "git commit -m \\"385 T61: x\\""}', "385") == "T61"
    assert wt.named_task('{"prompt": "read /tmp/l7r-check/plan-385-approach-checklist-T62/MANIFEST.md"}', "385") == "T62"
    assert wt.named_task('{"command": "ticked T59-T64 and T65"}', "385") == "", "a range or a list names no one task"
    starts = [(wt.fr.parse_t(_t(0)), "T10")]
    events = [
        ev("UserPromptSubmit", 0),
        ev("PreToolUse", 1, tool="Bash", cat="gate", id="a"),
        ev("PostToolUse", 3, tool="Bash"),
        ev("PreToolUse", 4, tool="Bash", cat="gate", id="b"),
        ev("Stop", 6),
    ]
    rules = wt.Counter()
    out = wt.tables(events, starts, {"a": '{"command": "make decide F=385 T=T60"}'}, "385", rules)[0]
    assert round(out["T60"]["gate/tests"] / 60) == 4, "named, then carried to the next call that names none"
    assert out["T10"] == wt.Counter({"model": 60.0}), "before any call names a task: the mark"
    assert round(rules["named"] / 60) == 2 and round(rules["the mark"] / 60) == 1


def test_each_task_s_time_is_its_tick_window() -> None:
    """Feature 385 T115 (plan D132): the GM's speed question was answered by a hand script over tasks.md's history - each task's
    span from the tick before it to its own, a batch sharing one window."""
    log = "\n".join(
        [
            "@@2026-10-19T05:00:00-04:00",
            "+- [x] T96 a",
            "+- [x] T98 b",
            "@@2026-10-19T05:30:00-04:00",
            "+- [ ] T99 not ticked",
            "-- [ ] T97 c",
            "+- [x] T97 c",
            "@@2026-10-19T06:00:00-04:00",
            "+- [x] T97 c (a reflow of the same tick)",
        ]
    )
    ticks = wt.parse_ticks(log)
    assert [k for _t, k in ticks] == ["T96", "T98", "T97"], "a box's first tick only; an open box is no tick"
    t0 = ticks[0][0] - 600.0
    wins = wt.tick_windows(ticks, t0)
    assert [(k, round((e - s) / 60)) for s, e, k in wins] == [("T96+T98", 10), ("T97", 30)]
    assert wt.tick_windows(ticks, ticks[0][0] + 1) == [(ticks[0][0] + 1, ticks[2][0], "T97")], "a tick before SINCE is outside"
