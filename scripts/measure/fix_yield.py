#!/usr/bin/env python3
"""`make fix-yield F=<feature>` - did each tooling fix save the time it was meant to (feature 385 T119, D140)?

WHY (the GM 2026-10-19, amendment 10, change 3: each fix's yield measured against the time it was meant to save, "so a fix
that saves nothing is retired"). 49 of the first 60 hourly step-backs named a tooling fix, and nothing said afterwards whether
any of them saved what it was meant to. Since T119 a ruling that names a `tooling_fix` carries `fix_measure` - a regex over the
main session's Bash commands, or `agent:<kind>` - and `fix_minutes` (`hm_arbiter.fix_measure_of`, D139).

For each fix settled done this reads the sessions' transcripts and compares the measure's rate - minutes of matching commands,
or dispatches of that check, per hour of session time - over the `YIELD_BEFORE_HOURS` of session time before its ruling and
since its settling. Session time is the transcripts' active time: each gap between two records, up to `ACTIVE_GAP_S`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "reviews"))
import stepback_bundle as sb  # noqa: E402

#: a tooling window, not a research figure: three session hours is three step-backs, the fewest over which a rate spans more
#: than one task (T119 Approach item 10)
YIELD_MIN_HOURS = 3.0
#: the before-window, the same doubled, so a fix ruled early in a feature still has a rate to compare (item 10)
YIELD_BEFORE_HOURS = 6.0
#: a gap between two transcript records counted as session time; a longer one is the session idle or waiting
ACTIVE_GAP_S = 300.0

Item = tuple[float, float, float]  # (when, session seconds, measured amount: seconds of matching commands, or dispatches)


def activity(records: Sequence[Mapping[str, Any]], measure: str) -> list[Item]:
    """The transcripts as a timeline of session time and the measure's amount, main-session records only."""
    main = [d for d in records if "timestamp" in d and not d.get("isSidechain")]
    main.sort(key=lambda d: sb._ts(d["timestamp"]))  # noqa: SLF001
    out: list[Item] = []
    agent = measure[6:].strip() if measure.startswith("agent:") else ""
    pattern = None if agent else re.compile(measure)
    started: dict[str, float] = {}
    prev = None
    for d in main:
        t = sb._ts(d["timestamp"])  # noqa: SLF001
        if prev is not None and 0 < t - prev <= ACTIVE_GAP_S:
            out.append((prev, t - prev, 0.0))
        prev = t
        content = (d.get("message") or {}).get("content")
        for b in content if isinstance(content, list) else ():
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                inp = b.get("input") or {}
                if agent and b.get("name") == "Agent" and str(inp.get("subagent_type")) == agent:
                    out.append((t, 0.0, 1.0))
                elif pattern is not None and b.get("name") == "Bash" and pattern.search(str(inp.get("command") or "")):
                    started[str(b.get("id"))] = t
            elif b.get("type") == "tool_result" and str(b.get("tool_use_id")) in started:
                t0 = started.pop(str(b.get("tool_use_id")))
                out.append((t0, 0.0, max(t - t0, 0.0)))
    return out


def rate(items: Iterable[Item]) -> tuple[float, float]:
    """(the measure per session hour - minutes of commands, or dispatches - and the session hours) of the items."""
    hours = amount = 0.0
    for _t, active, got in items:
        hours += active / 3600
        amount += got
    return amount / hours if hours else 0.0, hours


def windows(items: Sequence[Item], ruled: float, settled: float) -> tuple[list[Item], list[Item]]:
    """(the `YIELD_BEFORE_HOURS` of session time before the ruling, everything since the settling)."""
    before: list[Item] = []
    hours = 0.0
    for it in sorted((i for i in items if i[0] < ruled), reverse=True):
        if hours >= YIELD_BEFORE_HOURS:
            break
        before.append(it)
        hours += it[1] / 3600
    return before, [i for i in items if i[0] >= settled]


def fixes(rows: Sequence[Mapping[str, Any]], assigned: Mapping[str, Mapping[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Every ruling naming a fix, with its settling (`fix_of` rows: done or declined) and when; a fix ruled before T119 takes its
    measure from `assigned` (the feature's `fix-measures.json`, read from each fix's own sentence - the plan review of T119)."""
    settled = {str(r["fix_of"]): r for r in rows if r.get("fix_of")}
    out = []
    for r in rows:
        if r.get("tooling_fix"):
            s = settled.get(str(r.get("trigger")), {})
            given = {k: v for k, v in (assigned or {}).get(str(r.get("trigger")), {}).items() if k in ("fix_measure", "fix_minutes")}
            out.append({**given, **r, "status": s.get("status", "open"), "settled": s.get("utc", "")})
    return out


def verdict(fix: Mapping[str, Any], records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """One fix's yield row."""
    row = {"trigger": fix.get("trigger"), "measure": fix.get("fix_measure", ""), "fix_minutes": fix.get("fix_minutes")}
    if not fix.get("fix_measure"):
        return {**row, "verdict": "unmeasured - give it a measure in fix-measures.json"}
    if fix.get("status") != "done":
        return {**row, "verdict": f"not made ({fix.get('status')})"}
    before, after = windows(activity(records, str(fix["fix_measure"])), sb._ts(str(fix["utc"])), sb._ts(str(fix["settled"])))  # noqa: SLF001
    (b, bh), (a, ah) = rate(before), rate(after)
    unit = 60.0 if not str(fix["fix_measure"]).startswith("agent:") else 1.0  # command seconds shown as minutes
    row |= {"before": round(b / unit, 2), "before_hours": round(bh, 1), "after": round(a / unit, 2), "after_hours": round(ah, 1)}
    if ah < YIELD_MIN_HOURS:
        return {**row, "verdict": "too early"}
    return {**row, "verdict": "saves nothing - retire it or say why it stays" if a >= b else "saving"}


def table(rows: Sequence[Mapping[str, Any]]) -> str:
    lines = ["| fix (trigger) | measure | cost ruled (min) | before /h | after /h | after hours | verdict |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(
            f"| {r['trigger']} | `{r['measure']}` | {r.get('fix_minutes') if r.get('fix_minutes') is not None else '-'} | "
            f"{r.get('before', '-')} | {r.get('after', '-')} | {r.get('after_hours', '-')} | {r['verdict']} |"
        )
    return (
        "\n".join(lines)
        + "\n\n(per hour of session time: minutes of matching commands, or dispatches for `agent:<kind>`; a rate moves with the mix of work too - a run of claim fixes raises impl-drift's - so weigh 'saves nothing' against what the hours held)\n"
    )


def report(root: Path, feature_dir: Path, sids: Sequence[str] | None = None, projects: Path = sb.PROJECTS) -> str:
    """The yield table of a feature's fixes, read from its arbiter record and the clone's sessions' transcripts."""
    rows = sb._lines(feature_dir / "arbiter.jsonl")  # noqa: SLF001
    given = feature_dir / "fix-measures.json"
    fx = fixes(rows, json.loads(given.read_text(encoding="utf-8")) if given.is_file() else {})
    if not fx:
        return "(no tooling fix ruled)\n"
    records: list[dict] = []
    if any(f.get("fix_measure") and f.get("status") == "done" for f in fx):
        g = sb.ro._gitdir(root)  # noqa: SLF001
        events = [e for f in sorted((g / "l7r-events").glob("*.jsonl")) for e in sb._lines(f)] if g is not None and (g / "l7r-events").is_dir() else []  # noqa: SLF001
        sids = list(sids) if sids is not None else sb.sessions_of(events, 0.0, time.time())
        records, _read, _missing = sb._records(list(sids), None, projects)  # noqa: SLF001
    return table([verdict(f, records) for f in fx])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("feature")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    dirs = sorted((root / "specs").glob(f"{args.feature}*"))
    if len(dirs) != 1:
        print(f"fix-yield: no single specs/{args.feature}* directory", file=sys.stderr)
        return 2
    print(report(root, dirs[0]), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
