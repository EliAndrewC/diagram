"""Is this the only Claude Code session in the container? Exit 0 if it is, 1 if another runs (feature 444 T36).

WHY. The clone-sync prompt hook fetches GitHub main, refreshes the mirror and merges main into the clone on every message (0.65 s,
measured 2026-11-07), because sessions run side by side and each must build on what the others landed. With no other session, main
moves only when this one lands - and the landing (`sync-with-main.sh done`) fetches and checks for itself - so the GM, 2026-11-07:
"Can we also skip the clone-sync hook on every message when no claude code session is running? And then cache the whether another
claude code session is running for up to like 5 minutes so that the check becomes extremely quick?" - and: "We should make sure not
to count our own subagents, of course."

WHAT COUNTS. Every process named `claude` but this session's own and its descendants (a page session it started, `claude -p`, is
its own work; a subagent runs inside the session's process and is never a process of its own). A session that started this one is
counted: it is another session. Read from `/proc`, no `ps`.

THE CACHE. The answer is kept for `CACHE_S` seconds under `~/.cache/l7r/`, keyed by the session's process id, so a check is one file
read. A session started inside that window is seen at the next check; its own hook syncs it meanwhile.

`L7R_SOLO=1` or `0` answers without looking (the hook's own test suite, or the GM's override).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

CACHE_S = 300
NAME = "claude"


def _stat(d: Path) -> tuple[int, str] | None:
    """(parent pid, command name) from `/proc/<pid>/stat`, or None for a process gone or unreadable."""
    try:
        stat = (d / "stat").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    # `pid (comm) state ppid ...`: the name is between the first ( and the LAST ), since a name may hold either
    fields = stat[stat.rfind(")") + 2 :].split()
    return (int(fields[1]) if len(fields) > 1 else 0, stat[stat.find("(") + 1 : stat.rfind(")")])


def processes(proc: Path = Path("/proc")) -> dict[int, tuple[int, str]]:
    """{pid: (parent pid, command name)} of every process this one can read."""
    return {int(d.name): s for d in proc.iterdir() if d.name.isdigit() and (s := _stat(d)) is not None}


def chain(start: int, proc: Path = Path("/proc")) -> dict[int, tuple[int, str]]:
    """`start` and its ancestors only - the few reads that name the session, where `processes` reads them all."""
    out: dict[int, tuple[int, str]] = {}
    pid = start
    while pid > 1 and pid not in out and (s := _stat(proc / str(pid))) is not None:
        out[pid] = s
        pid = s[0]
    return out


def ancestors(procs: dict[int, tuple[int, str]], pid: int) -> list[int]:
    """`pid`'s parent, its parent's parent, ... to the root."""
    out: list[int] = []
    while pid in procs and procs[pid][0] not in (0, pid) and len(out) < 256:
        pid = procs[pid][0]
        out.append(pid)
    return out


def session(procs: dict[int, tuple[int, str]], start: int) -> int | None:
    """The `claude` process `start` runs under: itself, or its nearest such ancestor."""
    return next((p for p in [start, *ancestors(procs, start)] if p in procs and procs[p][1] == NAME), None)


def others(procs: dict[int, tuple[int, str]], me: int | None) -> list[int]:
    """The `claude` processes that are neither this session nor one it started."""
    return sorted(p for p, (_, name) in procs.items() if name == NAME and p != me and (me is None or me not in ancestors(procs, p)))


def solo(start: int, cache: Path, now: float, procs_of=processes) -> bool:  # noqa: ANN001 - the process reader, a seam for tests
    """Is the session `start` runs under alone? Kept in `cache` for `CACHE_S` seconds per session."""
    key = cache / f"solo-{os.getuid()}.json"
    try:
        kept = json.loads(key.read_text(encoding="utf-8"))
    except OSError, ValueError:
        kept = {}
    entry = kept.get(str(start)) if isinstance(kept, dict) else None
    if isinstance(entry, dict) and now - float(entry.get("t", 0)) < CACHE_S:
        return bool(entry.get("solo"))
    procs = procs_of()
    me = session(procs, start)
    alone = not others(procs, me)
    fresh = {k: v for k, v in (kept if isinstance(kept, dict) else {}).items() if isinstance(v, dict) and now - float(v.get("t", 0)) < CACHE_S}
    fresh[str(start)] = {"t": now, "solo": alone}
    try:
        cache.mkdir(parents=True, exist_ok=True)
        tmp = key.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(fresh), encoding="utf-8")
        tmp.replace(key)
    except OSError:
        pass
    return alone


def main(argv: list[str] | None = None) -> int:
    forced = os.environ.get("L7R_SOLO", "")
    if forced in ("0", "1"):
        return 0 if forced == "1" else 1
    me = session(chain(os.getppid()), os.getppid())
    return 0 if solo(me if me is not None else os.getppid(), Path.home() / ".cache" / "l7r", time.time()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
