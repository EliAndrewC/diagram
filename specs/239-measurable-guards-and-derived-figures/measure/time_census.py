#!/usr/bin/env python3
"""Where a session's wall clock went, from its own transcript.

    python3 specs/239-*/measure/time_census.py <session-id> [--from "text"] [--to "text"]

Pairs every `tool_use` with its `tool_result` to get tool execution time, counts the gap from a
result to the next assistant message as model turn latency, and reports what is left as idle - which
is what waiting on a background agent looks like from inside a transcript. `--from`/`--to` bound the
window by a substring of a user message, so a census can name the work rather than the session.

Written for feature 239 R1, over the session that delivered feature 236's second amendment.
"""

from __future__ import annotations

import collections
import datetime
import json
import pathlib
import re
import sys

BUCKETS = (
    ("the window replays", r"replay|final2|final\.py|residue|d11\.py|split\.py|diffverdict|measure_bash"),
    ("sleeping on a background run", r"\bsleep\b"),
    ("tests and checks", r"hooks-test|test-house-style|test-file|make quick|spec-lint|_hm_house\.py"),
    ("git and the push", r"\bgit \b|sync-with-main"),
)


def load(session: str) -> list[dict]:
    path = next(pathlib.Path.home().glob(f".claude/projects/*/{session}.jsonl"))
    out = []
    for line in path.open(errors="replace"):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("timestamp"):
            out.append(rec)
    return sorted(out, key=lambda r: r["timestamp"])


def stamp(rec: dict) -> datetime.datetime:
    return datetime.datetime.fromisoformat(rec["timestamp"].replace("Z", "+00:00"))


def text_of(rec: dict) -> str:
    body = (rec.get("message") or {}).get("content")
    if isinstance(body, str):
        return body
    return " ".join(c.get("text", "") for c in (body or []) if isinstance(c, dict))


def bucket(name: str, payload: str) -> str:
    if name != "Bash":
        return name
    for label, pattern in BUCKETS:
        if re.search(pattern, payload, re.I):
            return f"Bash: {label}"
    return "Bash: other"


def census(recs: list[dict], first: datetime.datetime, last: datetime.datetime) -> dict:
    spent: collections.Counter[str] = collections.Counter()
    calls: collections.Counter[str] = collections.Counter()
    latency, pending, after_result = 0.0, {}, None
    for rec in recs:
        now = stamp(rec)
        if not first <= now <= last:
            continue
        if rec.get("type") == "assistant":
            if after_result:
                latency += (now - after_result).total_seconds()
                after_result = None
            for c in (rec.get("message") or {}).get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    pending[c["id"]] = (now, c.get("name"), json.dumps(c.get("input"))[:400])
        elif rec.get("type") == "user":
            for c in (rec.get("message") or {}).get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("tool_use_id") in pending:
                    began, name, payload = pending.pop(c["tool_use_id"])
                    spent[bucket(name, payload)] += (now - began).total_seconds()
                    calls[bucket(name, payload)] += 1
            after_result = now
    total = (last - first).total_seconds()
    return {"total": total, "spent": dict(spent), "calls": dict(calls), "latency": latency,
            "idle": total - sum(spent.values()) - latency}


def main(argv: list[str]) -> int:
    session = argv[0]
    want_from = argv[argv.index("--from") + 1] if "--from" in argv else None
    want_to = argv[argv.index("--to") + 1] if "--to" in argv else None
    recs = load(session)
    first, last = stamp(recs[0]), stamp(recs[-1])
    for rec in recs:
        if rec.get("type") != "user":
            continue
        body = text_of(rec)
        if want_from and want_from in body:
            first = stamp(rec)
            want_from = None
        elif want_to and want_to in body:
            last = stamp(rec)
            break
    got = census(recs, first, last)
    print(f"window {first:%H:%M} -> {last:%H:%M} = {got['total']/60:.0f} min")
    rows = sorted(got["spent"].items(), key=lambda kv: -kv[1])
    for name, secs in rows:
        print(f"  {secs/60:6.1f} min  {secs/got['total']*100:4.1f}%  n={got['calls'][name]:3d}  {name}")
    print(f"  {got['latency']/60:6.1f} min  {got['latency']/got['total']*100:4.1f}%         model turn latency")
    print(f"  {got['idle']/60:6.1f} min  {got['idle']/got['total']*100:4.1f}%         idle (waiting on a background agent)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
