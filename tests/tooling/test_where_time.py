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
    assert round(c[wt.BETWEEN] / 60) == 290, "10 -> 300: between turns, every piece of it"
    assert round(c["model"] / 60) == 7 and round(c["gate/tests"] / 60) == 5 and round(c["tools"] / 60) == 3, "the turns' own work keeps its buckets"
    table = wt.render(out, _agents, _secs, ["T05"])
    assert "| T05 | 305 |" in table and wt.BETWEEN in table.splitlines()[0]
