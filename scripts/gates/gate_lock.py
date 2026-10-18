#!/usr/bin/env python3
"""One `make done` at a time in a clone (feature 375 follow-up, the GM 2026-10-10).

WHY. On 2026-10-10 the "Diagram research" session started a background `make done` at 22:12 UTC and a second in the same
clone at 22:16, while the first still ran. Two gates on one tree write the same pool maps, coverage data and failure markers:
both went red together on the same 11 tests, the red-gate tripwire fired twice for one event, and the round arbiter ruled twice
- recommending, in its own words, that "the gate should refuse to start while another make done is running in the same
clone". CLAUDE.md already said never to run a test beside a running gate; nothing held it.

THE LOCK. `<git dir>/gate.lock` names the `make` process that owns the gate. A `make done` that finds a LIVE owner - the process
exists and is still a `make` running `done` - is refused, naming it. An owner that died (killed, crashed, the container
restarted) is no owner, so there is never a stale lock to clear by hand.

    gate_lock.py acquire <git dir> <make pid>    exit 0 and own the gate, or exit 1 naming the running one
    gate_lock.py held <git dir>                  exit 0 while a live gate owns the clone, 1 otherwise - asked before anything
                                                 merges into the clone (feature 385 T30: main was merged in under two gates)
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

LOCK = "gate.lock"


def cmdline(pid: int) -> str:
    try:
        return Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace").strip()
    except OSError:
        return ""


def running_gate(pid: int) -> bool:
    """Whether `pid` is alive and still a make running the gate (a reused pid is some other program)."""
    words = cmdline(pid).split()
    return bool(words) and Path(words[0]).name in ("make", "gmake") and "done" in words[1:]


def acquire(git_dir: Path, pid: int, now: float | None = None) -> str:
    """Own the clone's gate for `pid`, or say who already does."""
    path = git_dir / LOCK
    try:
        held = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        held = {}
    other = int(held.get("pid") or 0)
    if other and other != pid and running_gate(other):
        since = time.strftime("%H:%M:%S", time.localtime(float(held.get("t") or 0)))
        return (f"a `make done` is already running in this clone (pid {other}, started {since}): two gates on one tree write the "
                "same maps and coverage files and fail together (feature 375 follow-up). Wait for its notification, or stop it first.")
    path.write_text(json.dumps({"pid": pid, "t": time.time() if now is None else now}), encoding="utf-8")
    return ""


def held(git_dir: Path) -> bool:
    """Whether a live gate owns the clone (feature 385 T30, the round arbiter's fix on red-gate@2026-10-18T12:36:36Z: nothing may
    merge into a tree while its gate runs - a dead owner holds nothing)."""
    try:
        pid = int(json.loads((git_dir / LOCK).read_text(encoding="utf-8")).get("pid") or 0)
    except (OSError, ValueError):
        return False
    return bool(pid) and running_gate(pid)


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "held":
        return 0 if held(Path(argv[1])) else 1
    if len(argv) == 3 and argv[0] == "acquire":
        why = acquire(Path(argv[1]), int(argv[2]))
        if why:
            print(f"\nGATE REFUSED: {why}", file=sys.stderr)
            return 1
        return 0
    print(__doc__.split("\n\n")[-1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
