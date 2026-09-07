#!/usr/bin/env python3
"""`make guard-log` - the guard firings, listed so a refusal can be audited after the fact (feature 204).

WHY (GM 2026-09-07): *"anytime we block a command invocation, we can see what specifically was
happening and whether the command was rewritable safely."* `make audit` prints the CENSUS (how often
each guard fired, the escape rate); this prints the ROWS - when, which session, standing where, what
command - which is the question a guard improvement actually starts from. Feature 204's own census
was the first one: 173 refusals, 2 of them the shape the guard was built for.

A reader, not a report generator: filters and columns, nothing derived. Entries written before
feature 204 carry no `session_name`, `cwd` or full `command`; they show their recorded id (most of
them `unknown`, which is the defect feature 204 fixed going forward). No transcript is read here -
the spec's D1 declines the transcripts as an index because Claude Code prunes them.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

DEFAULT_DIR = os.path.expanduser("~/.claude/guard-log")


def _load(directory: str) -> list[dict]:
    rows = []
    for f in glob.glob(os.path.join(directory, "*.json")):
        try:
            with open(f) as fh:
                rows.append(json.load(fh))
        except (OSError, ValueError):
            continue
    rows.sort(key=lambda r: r.get("utc", ""))
    return rows


def session_name(row: dict) -> str:
    if row.get("session_name"):
        return str(row["session_name"])
    sid = str(row.get("session") or "unknown")
    return "unknown" if sid in ("unknown", "nosession", "") else sid[:8]


def matches(row: dict, guard: str | None, since: str | None, event: str | None) -> bool:
    if guard and row.get("guard") != guard:
        return False
    if since and row.get("utc", "") < since:
        return False
    return not event or row.get("event") == event


def render(rows: list[dict], full: bool) -> list[str]:
    out = []
    for r in rows:
        name = session_name(r)
        command = str(r.get("command") or r.get("detail") or "")
        first = command.split("\n", 1)[0]
        head = (
            f"{r.get('utc', '')[:19]}  {name[:18]:<18}  {r.get('guard', ''):<12}  "
            f"{r.get('event', '')}/{r.get('rule') or r.get('event', '')}"
        )
        if full:
            out.append(head)
            out.append(f"    cwd: {r.get('cwd') or '-'}    tool: {r.get('tool') or '-'}")
            out.append("    command: " + command.replace("\n", "\n             "))
            if r.get("context"):
                out.append("    context: " + json.dumps(r["context"], ensure_ascii=False))
        else:
            out.append(f"{head}  {str(r.get('cwd') or '-')[:36]:<36}  {first[:80]}")
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="list the guard firings recorded in ~/.claude/guard-log/")
    ap.add_argument("--guard")
    ap.add_argument("--since", help="YYYY-MM-DD (UTC)")
    ap.add_argument("--event", choices=["blocked", "rewrote", "escaped", "reminded"])
    ap.add_argument("--full", action="store_true", help="the whole command and the guard's context")
    ap.add_argument("--dir", default=DEFAULT_DIR)
    a = ap.parse_args(argv)
    rows = [r for r in _load(a.dir) if matches(r, a.guard, a.since, a.event)]
    if not rows:
        print("(no matching firings)")
        return 0
    print("\n".join(render(rows, a.full)))
    print(f"{len(rows)} firing(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
