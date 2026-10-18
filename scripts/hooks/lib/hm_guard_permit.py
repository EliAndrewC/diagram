#!/usr/bin/env python3
"""A guard file's edit permit: the reason stated once, outside the file (feature 170 amendment 1, FR-006).

guard-file-hooks.sh used to accept an Edit of a guard file only when the new text itself held `GUARD_EDIT_OK` and a reason,
so every edit left a marker comment behind: the root Makefile had grown to 2,452 lines, more than half of them markers.
`make guard-edit FILE=<file> WHY="<reason>"` records the reason here instead, and the hook honors it for an hour.

    hm_guard_permit.py grant <file> <reason>   record a permit (exit 2, with the command to run, when refused)
    hm_guard_permit.py check <file>            print the live permit's reason, or nothing
    hm_guard_permit.py root-makefile <file>    exit 0 when <file> is the root Makefile of its checkout

Permits are JSON lines in the file's own checkout's git directory, so they are per clone and never committed.
`L7R_PERMIT_NOW` overrides the clock for the suite.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hm_escape import reason_is_enough  # noqa: E402

PERMIT_SECONDS = 3600
STORE = "l7r-guard-permits.jsonl"
_GUARD = re.compile(r"(/scripts/[\w-]+-hooks\.sh|/\.claude/settings\.json|/dev/switches\.json|/tests/rolls\.py)$")
_SUITE = re.compile(r"/tests/hooks/test-[\w-]+-hooks\.sh$")


def _git(path: str, *args: str) -> str:
    d = path if os.path.isdir(path) else os.path.dirname(path) or "."
    return subprocess.run(["git", "-C", d, *args], capture_output=True, text=True).stdout.strip()


def root_makefile(path: str) -> bool:
    return path.endswith("/Makefile") and os.path.dirname(path) == _git(path, "rev-parse", "--show-toplevel")


def is_guard(path: str) -> bool:
    """The files guard-file-hooks.sh holds (the same list as its `case`)."""
    return bool(_GUARD.search(path) and not _SUITE.search(path)) or root_makefile(path)


def _now() -> float:
    return float(os.environ.get("L7R_PERMIT_NOW") or time.time())


def _store(path: str) -> str:
    gd = _git(path, "rev-parse", "--absolute-git-dir")
    return os.path.join(gd, STORE) if gd else ""


def _live(store: str) -> list[dict]:
    try:
        with open(store, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
    except (OSError, ValueError):
        return []
    return [r for r in rows if _now() - float(r.get("at", 0)) < PERMIT_SECONDS]


def grant(path: str, reason: str) -> int:
    path = os.path.realpath(path)
    cmd = 'make guard-edit FILE=<guard file> WHY="<why this edit to a guard is legitimate>"'
    if not is_guard(path):
        print(f"make guard-edit: {path} is not a guard file, so its edits need no permit. Usage: {cmd}", file=sys.stderr)
        return 2
    if not reason_is_enough(reason):
        print(f"make guard-edit: give a reason of two words and eight characters or more. Usage: {cmd}", file=sys.stderr)
        return 2
    store = _store(path)
    rows = _live(store) + [{"file": path, "reason": reason, "at": _now()}]
    with open(store, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    until = time.strftime("%H:%M", time.localtime(_now() + PERMIT_SECONDS))
    print(f"guard-edit: {path} may be edited until {until} - {reason}")
    return 0


def check(path: str) -> str:
    path = os.path.realpath(path)
    hits = [r for r in _live(_store(path)) if r.get("file") == path]
    return str(hits[-1]["reason"]) if hits else ""


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["grant"] and len(args) == 3:
        sys.exit(grant(args[1], args[2]))
    if args[:1] == ["check"] and len(args) == 2:
        reason = check(args[1])
        if reason:
            print(reason)
        sys.exit(0)
    if args[:1] == ["root-makefile"] and len(args) == 2:
        sys.exit(0 if root_makefile(os.path.realpath(args[1])) else 1)
    print(__doc__, file=sys.stderr)
    sys.exit(2)
