#!/usr/bin/env python3
"""One record for every tool that leaves none of its own (feature 406 T01, D160).

WHY (the GM 2026-10-19, feature 406's request): "Whether or not it's doing something for us should be a measurable question"
for "basically ... every tool". A guard's firings are in the guard log, a make target's runs in the event log; a refusing check,
an automatic step inside another tool, or a target run by a timer left no trace, so `make tool-yield` could not say how often it
ran or whether it changed anything.

    record(root, tool, kind, outcome)       one line in <git common dir>/tool-usage.jsonl
    exited(tool, code, root=None) -> code   a check's exit recorded as `passed` (0) or `refused`, the code handed back
    usage_log.py record --tool <name> --kind <step|check|hook|target> --outcome <word> [--root <dir>]   (for shell callers)
    usage_log.py goals <goal>...            each make goal recorded `ran` (the Makefile's parse-time line, feature 406 D161)

A record never fails its tool: every error is swallowed. Every tool that records here is listed in `scripts/tool-registry.json`
with its kind and what it does; `scripts/gates/check-tool-signals.py` holds the two in step.
"""

from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path

USAGE = "tool-usage.jsonl"


def _common(root: Path | str | None) -> Path | None:
    out = subprocess.run(
        ["git", "-C", str(root or os.getcwd()), "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True,
        text=True,
    )
    return Path(out.stdout.strip()) if out.returncode == 0 and out.stdout.strip() else None


def record(root: Path | str | None, tool: str, kind: str, outcome: str) -> None:
    """Append one run of `tool` with its `outcome`; never raises."""
    try:
        common = _common(root)
        if common is None:
            return
        row = {
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tool": tool,
            "kind": kind,
            "outcome": outcome,
            "session": os.environ.get("CLAUDE_SESSION_ID", ""),
        }
        with (common / USAGE).open("a", encoding="utf-8") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            fh.write(json.dumps(row) + "\n")
    except Exception:  # noqa: BLE001 - a record must never fail the tool it records
        return


def exited(tool: str, code: int | None, root: Path | str | None = None) -> int | None:
    """A refusing check's exit, recorded as `passed` or `refused`; returns `code` so `sys.exit(exited(...))` reads as before."""
    record(root, tool, "check", "passed" if not code else "refused")
    return code


def main(argv: list[str]) -> int:
    import argparse  # noqa: PLC0415

    if argv[:1] == ["goals"]:  # every make invocation, from a session, a recipe, a script or a timer (D161)
        for goal in argv[1:]:
            record(None, goal, "target", "ran")
        return 0
    ap = argparse.ArgumentParser(description="record one run of a tool (feature 406)")
    ap.add_argument("verb", choices=("record",))
    ap.add_argument("--tool", required=True)
    ap.add_argument("--kind", required=True, choices=("step", "check", "hook", "target"))
    ap.add_argument("--outcome", required=True)
    ap.add_argument("--root", default=None)
    a = ap.parse_args(argv)
    record(a.root, a.tool, a.kind, a.outcome)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
