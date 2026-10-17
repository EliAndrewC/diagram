#!/usr/bin/env python3
"""A wave's cost, through `check-wave` against the last wave launched by hand (feature 383 amendment 7, FR-046, plan D50).

The GM's recommendations (diagram-fanout-workflows.md, step 5): *"run one real wave ... (or compare with the last
hand-launched wave of the same job): the workflow's agents, first request: the 2nd and later should READ about the size of
tools + definition body, and should NOT write ~35k ... Main session: count notification wakes during the wave (should be 1)
and the median context they re-read."* So, for a workflow run (newest by default) and for the last hand-launched wave before
it (4 or more Agent calls of one type in one message):

    wave_report.py [--run <.../subagents/workflows/wf_*>] [--root ~/.claude/projects/-diagram]

each agent's type and FIRST request's cache read and write, in start order; then the main session's wakes - the turns a
`<task-notification>` started - for the wave, and the median context those wakes re-read.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import statistics
import sys
from collections.abc import Iterator

ROOT = pathlib.Path.home() / ".claude" / "projects" / "-diagram"
WAVE_N = 4


def _records(path: pathlib.Path) -> Iterator[dict]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return
    for line in lines:
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if isinstance(d, dict):
            yield d


def first_request(path: pathlib.Path) -> tuple[str, int, int] | None:
    """An agent transcript's first request: its time, cache read, cache written."""
    for r in _records(path):
        u = (r.get("message") or {}).get("usage") if r.get("type") == "assistant" else None
        if u:
            return str(r.get("timestamp", "")), int(u.get("cache_read_input_tokens") or 0), int(u.get("cache_creation_input_tokens") or 0)
    return None


def _meta(agent: pathlib.Path) -> dict:
    try:
        return json.loads(agent.with_suffix(".meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def agents(paths: list[pathlib.Path]) -> list[dict]:
    """Each agent's type and first request, in start order."""
    out = []
    for p in paths:
        got = first_request(p)
        if got:
            out.append({"id": p.stem.removeprefix("agent-"), "type": _meta(p).get("agentType", "?"), "t": got[0], "read": got[1], "written": got[2]})
    return sorted(out, key=lambda a: a["t"])


def wakes(main: pathlib.Path, ids: set[str] | None, start: str, end: str) -> list[int]:
    """The main session's turns a task notification started - for these tool-use ids, or (ids None) any within [start, end] -
    each with the context its first request re-read."""
    recs = [r for r in _records(main) if r.get("type") in ("user", "assistant")]
    out = []
    for i, r in enumerate(recs):
        c = (r.get("message") or {}).get("content") if r["type"] == "user" else None
        c = c if isinstance(c, str) else "".join(str(b.get("text", "")) for b in c or [] if isinstance(b, dict)) if r["type"] == "user" else ""
        if not c.lstrip().startswith("<task-notification>"):
            continue
        if ids is not None:
            if not ids & set(re.findall(r"<tool-use-id>(\S+?)</tool-use-id>", c)):
                continue  # a wake carrying several queued notifications counts once, if any is the wave's
        elif not start <= str(r.get("timestamp", "")) <= end:
            continue
        nxt = next((x for x in recs[i + 1 :] if x["type"] == "assistant"), None)
        u = ((nxt or {}).get("message") or {}).get("usage") or {}
        out.append(int(u.get("cache_read_input_tokens") or 0) + int(u.get("cache_creation_input_tokens") or 0))
    return out


def last_hand_wave(main: pathlib.Path, before: str) -> tuple[str, list[str]] | None:
    """The last message before `before` that launched WAVE_N or more Agent calls of one type: its type and tool-use ids."""
    # one message's tool calls are written one record each, under the message's id: grouped back together here
    by_msg: dict[str, dict[str, list[str]]] = {}
    for r in _records(main):
        if r.get("type") != "assistant" or str(r.get("timestamp", "")) >= before:
            continue
        msg = r.get("message") or {}
        kinds = by_msg.setdefault(str(msg.get("id") or r.get("uuid")), {})
        for b in msg.get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in ("Agent", "Task"):
                kinds.setdefault(str((b.get("input") or {}).get("subagent_type") or "general-purpose"), []).append(str(b.get("id")))
    best = None
    for kinds in by_msg.values():  # in the order the messages were written: the last wave wins
        for kind, ids in kinds.items():
            if len(ids) >= WAVE_N:
                best = (kind, ids)
    return best


def _table(rows: list[dict]) -> list[str]:
    return [f"  {a['t'][11:23]}  {a['type']:<22} read {a['read']:>7,}  written {a['written']:>7,}" for a in rows]


def _wake_line(ws: list[int]) -> str:
    return f"  main-session wakes: {len(ws)}" + (f", median context re-read {round(statistics.median(ws) / 1000)}k" if ws else "")


def report(run: pathlib.Path) -> str:
    session = run.parents[2]
    main = session.parent / f"{session.name}.jsonl"
    rows = agents(sorted(run.glob("agent-*.jsonl")))
    if not rows:
        return f"wave-report: {run} has no agent with a request yet"
    lines = [f"WORKFLOW RUN {run.name} ({session.name}): {len(rows)} agent(s)", *_table(rows)]
    last = max(a["t"] for a in rows)
    ends = [str(r.get("timestamp", "")) for r in _records(run / "journal.jsonl") if r.get("type") == "result"]
    lines.append(_wake_line(wakes(main, None, rows[0]["t"], max([last, *ends])[:19] + "~")))
    # the last hand-launched wave: this session's, else the newest session under the projects root that has one
    others = sorted((p for p in session.parents[1].glob("-diagram*/*.jsonl") if p != main), key=lambda p: p.stat().st_mtime, reverse=True)
    for m in [main, *others]:
        hand = last_hand_wave(m, rows[0]["t"])
        if hand:
            kind, ids = hand
            sub = m.with_suffix("") / "subagents"
            metas = {mt.get("toolUseId"): p for p in sub.glob("agent-*.jsonl") if (mt := _meta(p)).get("toolUseId")}
            hrows = agents([metas[i] for i in ids if i in metas])
            lines += [f"LAST HAND-LAUNCHED WAVE: {len(ids)} {kind} in one message ({m.parent.name}/{m.stem})", *_table(hrows), _wake_line(wakes(m, set(ids), "", ""))]
            break
    else:
        lines.append(f"no hand-launched wave of {WAVE_N}+ before it")
    return "\n".join(lines)


def newest_run(root: pathlib.Path) -> pathlib.Path | None:
    # a session started in a clone keeps its transcripts under `<root>--clones-<name>`: every one of the project's is looked in
    runs = [p for p in root.parent.glob(f"{root.name}*/*/subagents/workflows/wf_*") if p.is_dir()]
    return max(runs, key=lambda p: p.stat().st_mtime) if runs else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--run", type=pathlib.Path)
    ap.add_argument("--root", type=pathlib.Path, default=ROOT)
    a = ap.parse_args(argv)
    run = a.run or newest_run(a.root)
    if run is None:
        print(f"wave-report: no workflow run under {a.root}")
        return 1
    print(report(run))
    return 0


if __name__ == "__main__":
    sys.exit(main())
