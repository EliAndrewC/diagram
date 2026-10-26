"""The call counts are what is watched (feature 427 T03, D3; the GM 2026-10-26, `specs/427-call-volume-refactors/request.md` 4).

WHY. "One of our problems with timings has been that it is difficult to take consistent timings, because which processor we were
using and what the current system load is really throws them off ... keep recording the timings, but completely stop using timings
as a gate on anything ... the call counts themselves are the thing that we are gating on, because as you say, that is consistent.
... it would not necessarily be a gate, but rather something that would need to be accepted by the arbiter and possibly raised to
my attention if it is increasing by too much." A stage's Python call count changes only when the code or the seed does
(`perf_snapshot.count_calls`, T02), so an increase is real and points at the chain that moved (`make perf-fanout`).

WHAT IT JUDGES: a feature's newest `-start` / `-end` pair, seed by seed, stage by stage, at each size it holds. An increase over
`CALLS_STAGE_LINE` in any stage of any seed, or over `CALLS_TOTAL_LINE` in the total, owes the round arbiter's acceptance before
the push lands it; a pair taken on different interpreter or library versions is not compared and owes the same - the `-start`
re-taken on the current versions, or a ruling (D3: it never passes silently); so does a `-start` from before the counts existed.
A decrease is printed and needs nothing. The arbiter's accept on the pair's subject (`subject`) clears it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

#: an increase over this share of a stage's calls on any seed owes the arbiter's acceptance - GUESS, the design note's starting
#: value (`call-count-flag.md`): to be tuned on the first landings that meet it, the reason recorded here
CALLS_STAGE_LINE = 0.05
#: ...and over this share of the pair's total calls - GUESS, as above
CALLS_TOTAL_LINE = 0.02
#: a stage this small moves by a handful of calls on any change; its share is not judged under this many calls - CONVENTION
CALLS_STAGE_FLOOR = 1000


@dataclass
class CallVerdict:
    """What a pair's counts say: `owed` is why the push needs the arbiter (empty: nothing owed), `lines` what to print."""

    owed: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)
    total_was: int = 0
    total_now: int = 0


def _counts(snap: dict[str, Any]) -> dict[tuple[Any, int, str], int]:
    """{(size or None, seed, stage): calls} over a snapshot's reference rows and its scaling rows."""
    out: dict[tuple[Any, int, str], int] = {}
    for row in [*snap.get("rows", []), *snap.get("scaling", [])]:
        for stage, n in (row.get("calls") or {}).items():
            out[(row.get("households"), int(row["seed"]), str(stage))] = int(n)
    return out


def compare(base: dict[str, Any], cur: dict[str, Any]) -> CallVerdict:
    """The pair's call-count verdict: refused to compare across versions or without counts; else each increase over the line."""
    v = CallVerdict()
    if base.get("versions") != cur.get("versions"):
        v.owed.append(f"the pair was taken on different versions ({base.get('versions') or 'none recorded'} -> {cur.get('versions') or 'none recorded'}): not compared")
        return v
    was, now = _counts(base), _counts(cur)
    if not was or not now:
        v.owed.append(f"the {'-start' if not was else '-end'} carries no call counts (a snapshot from before feature 427 T02): not compared")
        return v
    v.total_was, v.total_now = sum(was[k] for k in was if k in now), sum(now[k] for k in now if k in was)
    for key in sorted(set(was) & set(now), key=str):
        a, b = was[key], now[key]
        if b > a and a >= CALLS_STAGE_FLOOR and (b - a) / a > CALLS_STAGE_LINE:
            size, seed, stage = key
            v.owed.append(f"{stage} on seed {seed}{'' if size is None else f' at {size} households'}: {a:,} -> {b:,} calls (+{(b - a) / a:.0%})")
    if v.total_was and (v.total_now - v.total_was) / v.total_was > CALLS_TOTAL_LINE:
        v.owed.append(f"the total: {v.total_was:,} -> {v.total_now:,} calls (+{(v.total_now - v.total_was) / v.total_was:.1%})")
    change = (v.total_now - v.total_was) / v.total_was if v.total_was else 0.0
    v.lines.append(f"calls: {v.total_was:,} -> {v.total_now:,} ({change:+.1%}) over {len(set(was) & set(now))} stage rolls")
    return v


def subject(feature_number: str, cur: dict[str, Any]) -> str:
    """The `make arbiter-ask` subject of a pair's call-count question, bound to the `-end` it judges."""
    return f"{feature_number}-calls-{cur.get('commit', 'unknown')}"


def accepted(specs: Path, feature_number: str, cur: dict[str, Any]) -> bool:
    """Has the round arbiter accepted this pair's question (its `arbiter.jsonl`, trigger `ask:<subject>`)?"""
    want = f"ask:{subject(feature_number, cur)}"
    for f in sorted(specs.glob(f"{feature_number}-*/arbiter.jsonl")):
        for ln in f.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(ln)
            except ValueError:
                continue
            if row.get("trigger") == want and row.get("ruling") == "accept":
                return True
    return False


def refusal(feature_number: str, cur: dict[str, Any], owed: list[str]) -> str:
    """The push's refusal: what is owed and the command that asks the round arbiter, filled in."""
    why = "; ".join(owed)[:600].replace('"', "'")
    return (
        "perf-review: REFUSED - the call counts owe the round arbiter's acceptance (feature 427 T03; timings refuse nothing):\n  "
        + "\n  ".join(owed)
        + f'\n  make arbiter-ask SUBJECT={subject(feature_number, cur)} WHY="{why} - the chains that grew: make perf-fanout"'
        + "\n  (the arbiter accepts the cost of a rule the feature adds, rules to optimize first, or sends it to the GM; re-take the"
        + " -start on the current versions where they differ)"
    )
