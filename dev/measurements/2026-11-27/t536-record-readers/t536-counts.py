#!/usr/bin/env python3
"""451 T536: how often each trigger of a 451-record reader fired on 2026-11-27 (UTC), from the event logs (read-only).

Usage: python3 -I t536-counts.py <451 log copy> <cutoff ISO> [other logs...] > t536-counts.txt
Counts each line whose `t` (a Phase row's too) is on 2026-11-27 and before the cutoff (the snapshot's time): hook calls by event,
Agent dispatches by type, make targets (PreToolUse lines, the `make` field), Edit/Write calls by the file they name under specs/451,
and the landings (`src` land, step `end`, `landed` true). The 451 log is the feature's; the others (461, 462, _unassigned) are listed
apart, since a reader of 451's records runs whatever feature a call is filed to.
"""
import collections, json, sys

DAY = "2026-11-27"
log451, cutoff, others = sys.argv[1], sys.argv[2], sys.argv[3:]
TARGETS = ["decide", "plan-delta", "plan-verdict", "plan-section", "queue", "builder-next", "builder-done", "builder-brief",
           "land", "carry", "tick", "task-add", "task-start", "task-time", "claims-triage", "quick", "closing-checks",
           "feature-report", "arbiter-bundle", "task-withdraw"]


def count(path):
    ev, ag, mk, ed, lands = (collections.Counter() for _ in range(5))
    n = 0
    first = last = None
    for line in open(path, errors="replace"):
        if DAY not in line:
            continue
        try:
            v = json.loads(line)
        except Exception:
            continue
        t = v.get("t", "")
        if not t.startswith(DAY) or t > cutoff:
            continue
        n += 1
        first = first or t
        last = t
        e = v.get("ev")
        ev[e] += 1
        if e == "PreToolUse" and v.get("tool") == "Agent":
            ag[v.get("agent") or "?"] += 1
        if e == "PreToolUse" and v.get("make"):
            mk[v["make"]] += 1
        if e == "PreToolUse" and v.get("tool") in ("Edit", "Write") and "specs/451-" in str(v.get("path", "")):
            ed[str(v["path"]).rsplit("/", 1)[-1]] += 1
        if e == "Phase" and v.get("src") == "land" and v.get("step") == "end":
            lands["landed" if v.get("landed") else "not landed"] += 1
    return n, first, last, ev, ag, mk, ed, lands


for path in [log451] + others:
    n, first, last, ev, ag, mk, ed, lands = count(path)
    print(f"== {path.rsplit('/', 1)[-1]}: {n:,} lines on {DAY}, {first} to {last} (cutoff {cutoff})")
    hooks = sum(c for e, c in ev.items() if e in ("PreToolUse", "PostToolUse", "PostToolUseFailure", "SubagentStart",
                                                  "SubagentStop", "UserPromptSubmit", "Stop"))
    print(f"  hook calls (the hook events' rows; SessionStart is not logged): {hooks:,}; by row kind: {dict(ev.most_common())}")
    print(f"  Agent dispatches: {dict(ag.most_common())}")
    print(f"  make targets: {', '.join(f'{t} {mk[t]}' for t in TARGETS if mk[t])}")
    print(f"  Edit/Write of a 451 file: {dict(ed.most_common())}")
    print(f"  landings: {dict(lands)}")
