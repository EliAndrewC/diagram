"""An escape taken from Python, read and recorded the way `_guardlog.sh` records a hook's (feature 274).

WHY. The write cap on a page session (`WRITE_CAP_OK`, the runner) and the key cap on `make reserve` (`KEY_CAP_OK`) are
refused in Python, not in a hook, and the guard doctrine asks that every escape state a reason of two words or more
and be counted by `make audit`. So the reason is held to `_hm_escape.reason_is_enough` - the floor every hook uses - and
the entry is written in `~/.claude/guard-log/`'s own format, one file per entry, serialized before it is renamed into
place, exactly as `guard_log` in `_guardlog.sh` does.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _hm_escape import reason_is_enough  # noqa: E402


class NoReason(Exception):
    """The escape was set with no reason worth the name."""


def escape(token: str, guard: str, rule: str, context: dict | None = None, env: dict[str, str] | None = None) -> bool:
    """True when `token` is set in the environment with a reason, having logged it; False when it is not set.

    Raises `NoReason` when it is set with too little to audit: the missing thing is the session's reasoning, which no
    tool can supply, so that is a refusal rather than a pass (the doctrine `escape_or_refuse` states)."""
    reason = (os.environ if env is None else env).get(token, "").strip()
    if not reason:
        return False
    if not reason_is_enough(reason):
        log(guard, "blocked", reason, f"{token}-no-reason", context)
        raise NoReason(f"{token} needs a REASON, not just a value - two words and eight characters; say why this case is legitimate")
    log(guard, "escaped", reason, rule, context)
    return True


def log(guard: str, event: str, detail: str, rule: str, context: dict | None = None) -> None:
    """One guard-log entry; never raises - a failed log must not take the caller down with it."""
    try:
        d = pathlib.Path(os.environ.get("GUARD_LOG_DIR") or pathlib.Path.home() / ".claude" / "guard-log")
        d.mkdir(parents=True, exist_ok=True)
        sid = os.environ.get("L7R_PAGE_SESSION") or os.environ.get("CLAUDE_SESSION_ID") or "unknown"
        entry = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "guard": guard, "event": event, "rule": rule,
                 "session": sid, "session_name": pathlib.Path.cwd().name, "cwd": str(pathlib.Path.cwd()), "tool": "",
                 "transcript": "", "detail": detail[:200], "command": " ".join(sys.argv), "context": context}
        now = time.time()  # the name sorts by time, to the microsecond, as `_guardlog.sh`'s `%6N` does
        path = d / f"{time.strftime('%Y%m%dT%H%M%S', time.gmtime(now))}{int(now * 1e6) % 1_000_000:06d}-{os.getpid()}.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(entry, indent=2), encoding="utf-8")
        tmp.replace(path)
    except OSError:
        pass
