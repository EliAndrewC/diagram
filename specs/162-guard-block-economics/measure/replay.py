#!/usr/bin/env python3
"""Replay this project's Claude Code transcripts to price a guard.

Feature 162. Every number in ../research.md comes from here. Run it from anywhere:

    python3 measure/replay.py budgets   # R1: blocks and runs at each measure-hook budget
    python3 measure/replay.py blocks    # R3: what a session did in the turn after each block
    python3 measure/replay.py runlog    # R5: recorded `make done` cost by day

WHY A REPLAY AND NOT A COUNTER: no guard records when it fires (research.md R6), so the only
surviving record of a refusal is the transcript that received it. FR-006 replaces this script for
everything after 2026-08-30; it stays for the history before that.
"""

import collections
import glob
import json
import os
import re
import statistics
import sys

TRANSCRIPTS = os.path.expanduser("~/.claude/projects/-diagram/*.jsonl")
RUNLOG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../../.claude/skills/diagram/dev/run-log/*.json",
)

REFUSALS = {
    "measure": "EXPENSIVE measurement",
    "quick+done": "in ONE command",
    "subset": "`-k` SUBSET",
    "pair": "pair-hooks.sh",
    "batching": "batching-hooks.sh",
}
EXPENSIVE = re.compile(r"\bmake\b[^&|;]*\btest-full\b|done FULL=1")


def events(path):
    """(kind, name, text) for every tool call and tool result in one transcript, in order."""
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            content = (rec.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    inp = block.get("input") or {}
                    yield "use", block.get("name"), inp.get("command", "") or inp.get("file_path", "")
                elif block.get("type") == "tool_result":
                    body = block.get("content")
                    yield "res", None, body if isinstance(body, str) else json.dumps(body)


def budgets():
    """R1: replay the measure-hook state machine at each candidate budget."""
    for budget in (1, 2, 3):
        blocked = ran = 0
        sessions = set()
        for path in glob.glob(TRANSCRIPTS):
            streak = 0
            for kind, name, text in events(path):
                if kind != "use":
                    continue
                if name in ("Edit", "Write", "NotebookEdit"):
                    if text.endswith(".py") and "l7r/" in text and "/tests/" not in text:
                        streak = 0          # an engine edit makes the numbers genuinely stale
                elif name == "Bash":
                    if "MEASURE_OK" in text or "git commit" in text:
                        streak = 0
                    elif EXPENSIVE.search(text):
                        streak += 1
                        if streak > budget:
                            blocked += 1
                            streak = 0      # block once, so re-issuing goes through
                            sessions.add(path)
                        else:
                            ran += 1
        mark = "  <- this feature" if budget == 1 else ("  <- today" if budget == 2 else "")
        print(f"budget={budget}: blocked={blocked} ran={ran} sessions={len(sessions)}{mark}")


def blocks():
    """R3: every real refusal, and what the session did in the next Bash call."""
    fired = collections.Counter()
    followed = collections.defaultdict(collections.Counter)
    for path in glob.glob(TRANSCRIPTS):
        seq = list(events(path))
        for i, (kind, _name, text) in enumerate(seq):
            if kind != "res" or "BLOCKED" not in text:
                continue
            for guard, needle in REFUSALS.items():
                if needle not in text:
                    continue
                fired[guard] += 1
                nxt = [e for e in seq[i + 1 : i + 6] if e[0] == "use" and e[1] == "Bash"]
                cmd = nxt[0][2] if nxt else ""
                if re.search(r"\b(GATE|MEASURE|PAIR|REF|POLL|DISCARD)_OK\b", cmd):
                    followed[guard]["escaped in the next turn"] += 1
                elif EXPENSIVE.search(cmd) or re.search(r"\bmake\b[^&|;]*\bdone\b", cmd):
                    followed[guard]["ran a make target"] += 1
                elif cmd:
                    followed[guard]["something else"] += 1
                else:
                    followed[guard]["nothing"] += 1
                break
    for guard, n in fired.most_common():
        detail = ", ".join(f"{k}: {v}" for k, v in followed[guard].most_common())
        print(f"{guard}: {n} firings ({detail})")


def runlog():
    """R5: what `make done` has actually cost, by day, from the recorded runs."""
    by_day = collections.defaultdict(list)
    for path in glob.glob(RUNLOG):
        try:
            rec = json.load(open(path))
        except ValueError:
            continue
        if rec.get("target") != "done" or rec.get("result") != "green":
            continue
        by_day[rec["utc"][:10]].append(rec["seconds"])
    for day in sorted(by_day):
        got = by_day[day]
        print(f"{day} n={len(got):3d} median={statistics.median(got):6.0f}s min={min(got):5d} max={max(got):5d}")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "budgets"
    {"budgets": budgets, "blocks": blocks, "runlog": runlog}[which]()
