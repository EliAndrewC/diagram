#!/usr/bin/env python3
"""What a make target has ACTUALLY been costing, from the recorded runs (feature 161).

    _gatecost.py done          -> e.g. "137" (seconds), or nothing at all
    _gatecost.py done full     -> the same question for one recorded SCOPE

WHY (GM 2026-08-30): *"I think those numbers for `make quick` are wrong and outdated."* They were,
twice over - `gate-hooks.sh` said "~70 s with scope locked" while the scope had been UNLOCKED for
three days and the gate was costing 111 s. A number typed into a shell string in August is wrong in
September and nothing tells anybody, so no guard message states one any more: it asks here, and says
nothing when the log cannot answer. Printing nothing is a deliberate outcome, not a failure - a
message with no number is honest, a message with a stale one is not.

Green runs only: a failed gate's elapsed time measures where it stopped, not what it costs.
"""

from __future__ import annotations

import glob
import json
import os
import statistics
import subprocess
import sys

RECENT = 25


def _logs(cwd: str) -> list[str]:
    """Every run-log directory worth reading: this tree's, and the mirror's."""
    out = []
    top = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True).stdout.strip()
    for root in (top, "/diagram"):
        if root:
            out.append(os.path.join(root, ".claude/skills/diagram/dev/run-log/*.json"))
    return out


def median_seconds(target: str, scope: str | None = None, cwd: str | None = None) -> int | None:
    seen: dict[str, dict] = {}
    for pattern in _logs(cwd or os.getcwd()):
        for path in glob.glob(pattern):
            try:
                rec = json.load(open(path))
            except Exception:
                continue
            if rec.get("target") != target or rec.get("result") != "green":
                continue
            if scope is None or rec.get("scope") == scope:
                seen[os.path.basename(path)] = rec        # same entry in clone and mirror counts once
    runs = sorted(seen.values(), key=lambda r: r.get("utc", ""))[-RECENT:]
    if not runs:
        return None
    return int(statistics.median(r["seconds"] for r in runs))


if __name__ == "__main__":
    got = median_seconds(*sys.argv[1:3]) if len(sys.argv) > 1 else None
    if got is not None:
        print(got)
