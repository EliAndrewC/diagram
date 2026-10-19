#!/usr/bin/env python3
"""`make where-time F=<feature> [SINCE=<ISO>]` - where a feature's time went, by task (feature 385 T77, plan D96).

WHY. The GM's step-back of 2026-10-18 asked for each task's time by piece; the scratch script that answered it booked T05 224
minutes, about 80 of them the overnight stall: hook events cut the 04:20-09:15 gap into pieces under an hour, each booked
"thinking". So from a session's `Stop` to its next `UserPromptSubmit` every gap is BETWEEN TURNS - waiting on background work or
idle; the agents table and the background-run column say what ran. A notification that wakes the session fires the prompt
hooks (measured 2026-10-19), so a woken turn's work is booked to its task.

THE TABLES. Each gap between a session's events goes to the task the clone's last `make task-start` had made active at its start,
in `feature_report.split_time`'s categories, grouped into buckets; the agents table counts each subagent and its minutes by the
task active at its launch. The step-back checklist (specs/385-approach-checklist/step-back-2026-10-18.md, item 1) runs this.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import feature_report as fr  # noqa: E402

BETWEEN = "between turns"
BUCKET = {
    "thinking": "model",
    "writing the spec": "model",
    "waiting: spec-fidelity": "plan review",
    "waiting: spec-fidelity-verify": "plan review",
    "dispatching: spec review": "plan review",
    "waiting: impl-drift": "claims check",
    "waiting: claims-triage": "claims check",
    "dispatching: claims check": "claims check",
    "waiting: glyph-check": "glyph check",
    "waiting: round-arbiter": "arbiter",
    "dispatching: round arbiter": "arbiter",
    "gate": "gate/tests",
    "quick test": "gate/tests",
    "test file": "gate/tests",
    "waiting: a background run": "background run",
    "waiting: the GM": "the GM",
    "idle (over an hour)": "idle",
    BETWEEN: BETWEEN,
}
RECORD = ("quote-check", "record-format", "source-reader", "source-applicability", "translation-check", "intro-check", "modal-", "entry-drift", "research-pass")
COLUMNS = ["model", "tools", "gate/tests", "background run", "plan review", "claims check", "record/modal checks", "glyph check", "arbiter", "other subagent", "the GM", BETWEEN, "idle"]


def bucket(cat: str) -> str:
    if cat in BUCKET:
        return BUCKET[cat]
    if (cat.startswith("waiting: ") and any(r in cat for r in RECORD)) or cat in ("dispatching: record check", "dispatching: review check"):
        return "record/modal checks"
    if cat.startswith(("waiting: ", "dispatching")):
        return "other subagent"
    return "tools"


def task_at(starts: Sequence[tuple[float, str]], t: float) -> str:
    cur = "-"
    for s, k in starts:
        if s > t:
            break
        cur = k
    return cur


def tables(events: Sequence[Mapping[str, Any]], starts: Sequence[tuple[float, str]]) -> tuple[dict[str, Counter], dict[str, Counter], dict[str, Counter]]:
    """(seconds by task and bucket, agents by task and kind, agent seconds by task and kind)."""
    out: dict[str, Counter] = defaultdict(Counter)
    by_sid: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for e in sorted(events, key=lambda e: fr.parse_t(e["t"])):
        by_sid[str(e.get("sid"))].append(e)
    fg = fr.tp.foreground_spans(events)
    for evs in by_sid.values():
        between = False
        for a, b in zip(evs, evs[1:], strict=False):
            between = (between or a["ev"] == "Stop") and a["ev"] != "UserPromptSubmit"
            gap = fr.parse_t(b["t"]) - fr.parse_t(a["t"])
            if gap <= 0:
                continue
            t0 = fr.parse_t(a["t"])
            if between:
                cat = BETWEEN
            elif gap > fr.IDLE_CAP_S:
                cat = "idle (over an hour)"
            elif run := fr.tp.in_span(t0, fg):
                cat = f"waiting: {run}"
            elif a["ev"] == "PreToolUse":
                cat = fr._tool_cat(a)
            else:
                cat = "thinking"
            out[task_at(starts, t0)][bucket(cat)] += gap
    agents: dict[str, Counter] = defaultdict(Counter)
    secs: dict[str, Counter] = defaultdict(Counter)
    open_a: dict[str, tuple[float, str, str]] = {}
    for e in sorted(events, key=lambda e: fr.parse_t(e["t"])):
        if e.get("ev") == "SubagentStart":
            t = fr.parse_t(e["t"])
            open_a[str(e.get("aid"))] = (t, str(e.get("agent") or "?"), task_at(starts, t))
        elif e.get("ev") == "SubagentStop" and str(e.get("aid")) in open_a:
            t0, kind, task = open_a.pop(str(e.get("aid")))
            agents[task][kind] += 1
            secs[task][kind] += fr.parse_t(e["t"]) - t0
    return out, agents, secs


def render(out: Mapping[str, Counter], agents: Mapping[str, Counter], secs: Mapping[str, Counter], order: Iterable[str]) -> str:
    order = [k for k in order if k in out or k in agents]
    lines = ["| task | total | " + " | ".join(COLUMNS) + " |", "|---|---|" + "---|" * len(COLUMNS)]
    tot: Counter = Counter()
    for k in order:
        c = out.get(k, Counter())
        tot.update(c)
        lines.append(f"| {k} | {sum(c.values()) / 60:.0f} | " + " | ".join(f"{c[x] / 60:.0f}" for x in COLUMNS) + " |")
    lines.append(f"| all | {sum(tot.values()) / 60:.0f} | " + " | ".join(f"{tot[x] / 60:.0f}" for x in COLUMNS) + " |")
    lines += ["", "| task | agents | agent minutes | by kind (count) |", "|---|---|---|---|"]
    lines += [f"| {k} | {sum(agents[k].values())} | {sum(secs[k].values()) / 60:.0f} | " + ", ".join(f"{a} {n}" for a, n in agents[k].most_common()) + " |" for k in order if agents.get(k)]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("feature")
    ap.add_argument("--since", default="")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    root = Path(fr._git(Path(args.root), "rev-parse", "--show-toplevel").strip() or args.root)
    d = fr.spec_dir(root, args.feature)
    if d is None:
        print(f"where-time: no specs/{args.feature}-* directory", file=sys.stderr)
        return 2
    common = Path(fr._git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").strip())
    rows = [json.loads(x) for x in (common / "task-starts.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()] if (common / "task-starts.jsonl").is_file() else []
    starts = sorted((fr.parse_t(r["utc"]), r["task"]) for r in rows if r.get("feature") == d.name and (not args.since or r["utc"] >= args.since))
    events = fr.load_events(fr.event_logs(root, d.name), [], args.since, "")
    out, agents, secs = tables(events, starts)
    first = {k: min(s for s, t in starts if t == k) for _s, k in starts}
    print(render(out, agents, secs, sorted(set(out) | set(agents), key=lambda k: first.get(k, 0))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
