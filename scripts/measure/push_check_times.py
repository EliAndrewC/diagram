#!/usr/bin/env python3
"""What the push's checks cost, each timed as the push runs it (feature 383, SC-001).

WHY. Feature 383 was asked for on a measurement taken by hand (2026-10-13: the push's checks about 24 s, each timed alone
in a clone); its success criterion is the same measurement repeated after each phase, back to back, warm. This is that
measurement as a command, so the before and the after are the same instrument.

    push_check_times.py [--root <clone>] [--runs N] [--json <out>]

Each command is run N times (default 2: the first warms what a cache keeps, the last is the one reported) and its wall time
printed; the total is the sum of the last runs. The commands are the push's own (`scripts/sync-with-main.sh`'s `push_cmd`),
those that read the tree whole; a check the clone does not have is skipped and named. Nothing here refuses: a check's exit
status is printed beside its time.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

#: (label, argv with `{root}`): the push's checks as `push_cmd` runs them, selftests included
COMMANDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("push checks (one process)", ("python3", "{root}/scripts/gates/push_checks.py", "{root}")),
    ("duplicate-defs selftest", ("python3", "{root}/scripts/gates/check-duplicate-defs.py", "--selftest")),
    ("duplicate-defs", ("python3", "{root}/scripts/gates/check-duplicate-defs.py", "{root}")),
    ("file-scale selftest", ("python3", "{root}/scripts/gates/check-file-scale.py", "--selftest")),
    ("stale-dirs selftest", ("python3", "{root}/scripts/gates/check-stale-dirs.py", "--selftest")),
    ("stale-dirs", ("python3", "{root}/scripts/gates/check-stale-dirs.py", "{root}")),
    ("old-layout selftest", ("python3", "{root}/scripts/gates/check-old-layout.py", "--selftest")),
    ("old-layout", ("python3", "{root}/scripts/gates/check-old-layout.py", "{root}")),
    ("file-scale", ("python3", "{root}/scripts/gates/check-file-scale.py", "{root}")),
    ("function-cap selftest", ("python3", "{root}/scripts/gates/check-function-cap.py", "--selftest")),
    ("function-cap", ("python3", "{root}/scripts/gates/check-function-cap.py", "{root}")),
    ("ledger-owed", ("python3", "{root}/scripts/reviews/ledger_owed.py", "--ledger", "{root}/dev/review-ledger.md", "--refuse")),
    ("entry-headings selftest", ("python3", "{root}/scripts/gates/check-entry-headings.py", "--selftest")),
    ("entry-headings", ("python3", "{root}/scripts/gates/check-entry-headings.py", "{root}")),
    ("research-pointers selftest", ("python3", "{root}/scripts/gates/check-research-pointers.py", "--selftest")),
    ("research-pointers", ("python3", "{root}/scripts/gates/check-research-pointers.py", "{root}")),
    ("partial-citations", ("python3", "-B", "{root}/scripts/gates/check-partial-citations.py", "{root}")),
    ("downloads selftest", ("python3", "{root}/scripts/record/downloads.py", "selftest")),
    ("downloads", ("python3", "{root}/scripts/record/downloads.py", "check")),
    ("record CHECK=1", ("make", "--no-print-directory", "record", "CHECK=1")),
    ("glossary CHECK=1", ("make", "--no-print-directory", "glossary", "CHECK=1")),
    ("spec-lint selftest", ("python3", "{root}/scripts/gates/spec-lint.py", "--selftest")),
    ("spec-lint", ("python3", "{root}/scripts/gates/spec-lint.py", "--delta", "{root}")),
    ("speckit-todo check", ("python3", "{root}/scripts/speckit-todo.py", "--root", "{root}", "--check")),
    ("conflict selftest", ("python3", "{root}/scripts/hooks/lib/hm_conflict.py", "--selftest")),
    ("conflict", ("python3", "{root}/scripts/hooks/lib/hm_conflict.py", "--tracked", "{root}")),
    ("gate-stamp selftest", ("python3", "{root}/scripts/gates/gate-stamp.py", "--selftest")),
)


def present(root: Path, argv: tuple[str, ...]) -> bool:
    """A command whose script the clone does not have (retired, or not yet built) is skipped."""
    return all(Path(a.replace("{root}", str(root))).exists() for a in argv if "{root}/" in a)


def measure(root: Path, runs: int) -> list[dict]:
    out = []
    for label, argv in COMMANDS:
        if not present(root, argv):
            out.append({"check": label, "skipped": "not in this clone"})
            continue
        cmd = [a.replace("{root}", str(root)) for a in argv]
        wall, code = 0.0, 0
        for _ in range(max(runs, 1)):
            t = time.monotonic()
            code = subprocess.run(cmd, cwd=root, capture_output=True, check=False, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}).returncode
            wall = time.monotonic() - t
        out.append({"check": label, "wall_s": round(wall, 2), "exit": code})
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    rows = measure(root, args.runs)
    for r in rows:
        print(f"{r['wall_s']:6.2f} s  exit {r['exit']}  {r['check']}" if "wall_s" in r else f"     -    {r['check']} ({r['skipped']})")
    total = round(sum(r.get("wall_s", 0.0) for r in rows), 2)
    print(f"{total:6.2f} s  in all, load {os.getloadavg()[0]:.1f}")
    if args.json:
        Path(args.json).write_text(json.dumps({"total_s": total, "load": round(os.getloadavg()[0], 1), "rows": rows}, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
