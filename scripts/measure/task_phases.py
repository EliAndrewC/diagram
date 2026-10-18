"""Whose time, each task's phases, and its decision-log skeleton - for `make feature-report` (feature 385 amendment 4, plan D30-D33).

WHY (the GM, 2026-10-18, asking T03's 2 h 25 min broken down before T04): the report put 64% of T03 under "thinking", but 202 of
the 549 tool calls in T03's window were its SUBAGENTS' - a subagent's tool calls reach the session's hooks under the session's
id with no marker - so it could not say what the session did and what its reviewers did. And T03's decision log was written from
memory, up to an hour off.

WHOSE CALL (D30). A tool event is a subagent's when its tool_use id is in a subagent transcript of its session
(`<projects>/<project>/<sid>/subagents/agent-<aid>.jsonl`; measured exact on T03: 347 of its calls matched the session, 202 a
subagent, none neither), or when the hook recorded `by` (the payload's `agent_id`, `event_log.line`). Where neither can say -
a session with no subagent transcripts found and a call with no `by` - a call inside a subagent's start-to-stop window is that
subagent's, an ESTIMATE (the GM's "otherwise use each agent's start and stop window"). Every other is the session's.
`attribute` marks each subagent's call with `by` and `how`; the report's time table then reads the session's events alone.

THE PHASES (D31, D32). A task's segments between decision points (`feature_report.task_rows` makes the cuts): for each, the
session's calls, its WORKING time (its tool time and the gaps between its own events) and its WAITING time (a `Stop` until what
woke it), and the subagent runs that started in it.

THE SKELETON (D33). A task's start, every agent returned, every cohort and gate run, every plan heading stamped `part B (<UTC>)`
or `Approach (re-answered <UTC>)`, and its tick, in time order, each with an empty "what decided it" cell for the retro.
"""

from __future__ import annotations

import datetime
import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

PROJECTS = Path.home() / ".claude" / "projects"
_TOOL_ID = re.compile(r'"id":\s*"(toolu_[A-Za-z0-9_-]+)"')


def measured_run(e: Mapping[str, Any]) -> bool:
    """A cohort or gate run, the skeleton's (D33): a make target starting `cohort`, one the event log files as a `gate`, or
    `verify` - "every cohort and gate run" is the rule, not a list."""
    target = str(e.get("make") or "")
    return bool(target) and (target.startswith("cohort") or e.get("cat") == "gate" or target == "verify")


_STAMP = re.compile(r"^#{3,4}\s+(T\d+)\s+(part B|Approach \(re-answered)\s*\(?\s*(\d{4}-\d\d-\d\dT\d\d:\d\d)(?::\d\d)?Z", re.M)
#: a session gap longer than this, with no Stop in it, is the session left alone, not working (`feature_report.IDLE_CAP_S`)
IDLE_CAP_S = 3600


def _t(s: str) -> float:
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def subagent_calls(sids: Iterable[str], projects: Path = PROJECTS) -> tuple[dict[str, str], set[str]]:
    """(tool_use id -> the subagent (`aid`) that made it, the subagent runs whose transcripts were found)."""
    out: dict[str, str] = {}
    found: set[str] = set()
    for sid in {s for s in sids if s}:
        for f in projects.glob(f"*/{sid}/subagents/agent-*.jsonl"):
            aid = f.name[len("agent-") : -len(".jsonl")]
            found.add(aid)
            for m in _TOOL_ID.finditer(f.read_text(encoding="utf-8", errors="replace")):
                out.setdefault(m.group(1), aid)
    return out, found


def _windows(events: Iterable[Mapping[str, Any]]) -> dict[str, list[tuple[float, float, str]]]:
    """sid -> (start, stop, aid) of every subagent run logged with both ends."""
    started: dict[str, float] = {}
    out: dict[str, list[tuple[float, float, str]]] = {}
    for e in events:
        aid = str(e.get("aid") or "")
        if aid and not e.get("tool") and e.get("ev") == "SubagentStart":
            started.setdefault(aid, _t(e["t"]))
        elif aid and not e.get("tool") and e.get("ev") == "SubagentStop" and aid in started:
            out.setdefault(str(e.get("sid")), []).append((started[aid], _t(e["t"]), aid))
    return {sid: sorted(w) for sid, w in out.items()}  # overlapping windows: the earliest-started run's (D30)


def attribute(events: Sequence[Mapping[str, Any]], calls: Mapping[str, str], found: Iterable[str] = ()) -> list[dict[str, Any]]:
    """The events, each subagent's tool event marked `by` its subagent and `how` it was told (D30): `transcript`, `hook`, or -
    inside the window of a run whose own transcript was not `found` - `window`, the estimate (decided per RUN)."""
    have = set(found)
    windows = _windows(events)
    out = []
    for e in events:
        e = dict(e)
        if e.get("tool"):
            if e.get("by"):
                e.setdefault("how", "hook")
            elif calls.get(str(e.get("id"))):
                e.update(by=calls[str(e["id"])], how="transcript")
            elif e.get("tool") != "Agent":  # the session's own launch is never its agent's
                t = _t(e["t"])
                hit = next((aid for a, b, aid in windows.get(str(e.get("sid")), []) if a <= t <= b and aid not in have), "")
                if hit:
                    e.update(by=hit, how="window")
        out.append(e)
    return out


def attribution(events: Iterable[Mapping[str, Any]]) -> Counter[str]:
    """How each subagent tool call was told from the session's: `transcript`, `hook`, `window`."""
    return Counter(str(e.get("how")) for e in events if e.get("ev") == "PreToolUse" and e.get("by"))


def session_events(events: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """The session's own events: every event but a subagent's tool call."""
    return [e for e in events if not (e.get("tool") and e.get("by"))]


def call_counts(events: Iterable[Mapping[str, Any]]) -> tuple[int, int]:
    """(the session's tool calls, its subagents' tool calls)."""
    n = Counter("sub" if e.get("by") else "own" for e in events if e.get("ev") == "PreToolUse")
    return n["own"], n["sub"]


def subagent_runs(events: Iterable[Mapping[str, Any]]) -> list[tuple[float, float, str, str]]:
    """(start, stop, type, verdict) of every subagent run with both ends logged."""
    started: dict[str, tuple[float, str]] = {}
    out = []
    for e in events:
        aid = str(e.get("aid") or "")
        if not aid or e.get("tool"):
            continue
        if e.get("ev") == "SubagentStart":
            started.setdefault(aid, (_t(e["t"]), str(e.get("agent") or "")))
        elif e.get("ev") == "SubagentStop" and aid in started and e.get("agent"):
            t0, kind = started.pop(aid)
            out.append((t0, _t(e["t"]), str(e.get("agent") or kind), str(e.get("verdict") or "")))
    return out


def foreground_spans(events: Iterable[Mapping[str, Any]]) -> list[tuple[float, float, str]]:
    """(launch, return, type) of every session `Agent` call that ran in the foreground - its run's `SubagentStop` came before the
    call returned (D31): the session waits through it, no `Stop` marking the wait."""
    evs = list(events)
    pre = {str(e.get("id")): e for e in evs if e.get("ev") == "PreToolUse" and e.get("tool") == "Agent"}
    stops: dict[str, list[float]] = {}
    for e in evs:
        if e.get("ev") == "SubagentStop" and e.get("aid") and not e.get("tool"):
            stops.setdefault(str(e["aid"]), []).append(_t(e["t"]))
    out = []
    for e in evs:
        a = pre.get(str(e.get("id")))
        if e.get("ev") == "PostToolUse" and e.get("tool") == "Agent" and a is not None:
            t0, t1 = _t(a["t"]), _t(e["t"])
            if any(t0 <= s <= t1 for s in stops.get(str(e.get("aid") or ""), [])):
                out.append((t0, t1, str(a.get("agent") or "subagent")))
    return out


def in_span(t: float, spans: Iterable[tuple[float, float, str]]) -> str:
    """The type of the foreground run whose span holds `t`, or ''."""
    return next((k for a, b, k in spans if a <= t < b), "")


def _gaps(events: Sequence[Mapping[str, Any]]) -> list[tuple[float, float, str]]:
    """(start, end, 'work' | 'wait' | 'idle') of every gap between two of the session's events, per session (D31): a gap past
    the hour cap is idle, counted apart, never dropped."""
    fg = foreground_spans(events)
    by_sid: dict[str, list[Mapping[str, Any]]] = {}
    for e in session_events(events):
        by_sid.setdefault(str(e.get("sid")), []).append(e)
    out = []
    for evs in by_sid.values():
        for a, b in zip(evs, evs[1:], strict=False):
            t0, t1 = _t(a["t"]), _t(b["t"])
            if t1 > t0:
                waits = a.get("ev") == "Stop" or in_span(t0, fg)  # a foreground run is waited on, never worked (D31)
                out.append((t0, t1, "idle" if t1 - t0 > IDLE_CAP_S else "wait" if waits else "work"))
    return out


def _clip(spans: Iterable[tuple[float, float, str]], lo: float, hi: float) -> Counter[str]:
    out: Counter[str] = Counter()
    for t0, t1, kind in spans:
        out[kind] += max(0.0, min(t1, hi) - max(t0, lo))
    return out


def _hhmm(t: float) -> str:
    return datetime.datetime.fromtimestamp(t, datetime.UTC).strftime("%H:%M")


def _cuts(events: Sequence[Mapping[str, Any]], start: float, end: float, decision_agents: frozenset[str]) -> list[tuple[float, str]]:
    """The task's decision points as (time, what), the plan and arbiter rulings returned between `start` and `end`."""
    return sorted(
        (t, f"{e.get('agent')} {e.get('verdict') or ''}".strip()) for e in events if e.get("ev") == "SubagentStop" and e.get("agent") in decision_agents for t in [_t(e["t"])] if start <= t <= end
    )


def phase_rows(events: Sequence[Mapping[str, Any]], task: str, start: float, end: float, decision_agents: frozenset[str]) -> list[str]:
    """One row per phase of `task` (D32): span, what ended it, the session's calls, working, waiting and idle minutes, the
    subagents that started in it."""
    gaps, runs = _gaps(events), subagent_runs(events)
    own = [e for e in session_events(events) if e.get("ev") == "PreToolUse"]
    points = _cuts(events, start, end, decision_agents)
    bounds = [(start, ""), *points, (end, "the tick or the last event")]
    rows = []
    for (a, _w), (b, what) in zip(bounds, bounds[1:], strict=False):
        c = _clip(gaps, a, b)
        calls = sum(1 for e in own if a <= _t(e["t"]) < b)
        kinds = Counter(k for t0, _t1, k, _v in runs if a <= t0 < b)
        mins = sum(t1 - t0 for t0, t1, _k, _v in runs if a <= t0 < b)
        subs = ", ".join(f"{k} x{n}" for k, n in sorted(kinds.items())) + (f" ({mins / 60:.0f} min)" if kinds else "") or "-"
        rows.append(f"| {task} | {_hhmm(a)}-{_hhmm(b)} | {what} | {calls} | {c['work'] / 60:.0f} | {c['wait'] / 60:.0f} | {c['idle'] / 60:.0f} | {subs} |")
    return rows


def skeleton_rows(events: Sequence[Mapping[str, Any]], task: str, start: float, end: float, plan_text: str, ticked: bool) -> list[str]:
    """`task`'s decision-log skeleton (D33), in time order, each with an empty cell for what decided it."""
    items: list[tuple[float, str]] = [(start, "started (`make task-start`)")]
    items += [(t1, f"{kind} returned{' ' + verdict if verdict else ''} ({(t1 - t0) / 60:.0f} min)") for t0, t1, kind, verdict in subagent_runs(events) if start <= t1 <= end]
    items += [
        (_t(e["t"]), f"`make {e['make']}` ({float(e.get('ms') or 0) / 60000:.0f} min)")
        for e in session_events(events)
        if e.get("ev") == "PostToolUse" and measured_run(e) and start <= _t(e["t"]) <= end
    ]
    for m in _STAMP.finditer(plan_text):
        when = _t(m.group(3) + ":00Z")
        if m.group(1) == task and start <= when <= end:
            items.append((when, "part B written" if m.group(2) == "part B" else "Approach re-answered"))
    if ticked:
        items.append((end, "ticked"))
    return [f"| {task} | {_hhmm(t)} | {what} | |" for t, what in sorted(items)]
