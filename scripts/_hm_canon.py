#!/usr/bin/env python3
"""The decision behind `canon-read-hooks.sh` (feature 250 D16): pass, or which rule a canon read breaks.

Reads the hook payload on stdin and prints one word:

    pass      not a canon read; or `make canon` with no other among the last three tool calls, or one that
              names every term those calls named (the fold, and the retry after a refusal)
    direct    a canon file read directly - a Read or Grep on it, or a shell read verb naming it
    repeat    `make canon` again within three tool calls - the terms were not folded into one call

WHAT IS A CANON READ. A `Read`/`Grep` whose path is under a setting directory; or a Bash command that names one
(absolutely, or `setting/` after a `cd /host-l7r-repo`) AND carries a read verb (grep, rg, sed, awk, cat, head,
tail, less, python). A MENTION is not a read: an `echo` of the path, a commit message, a `make canon` that names
nothing is not refused (the doctrine every guard here is held to - match invocations, not mentions).
"""

from __future__ import annotations

import json
import re
import sys

CANON = re.compile(r"/host-l7r-repo/(?:gm-assistant/)?setting\b")
CD_HOST = re.compile(r"\bcd\s+/host-l7r-repo(?:/gm-assistant)?/?(?:\s|;|&|$)")
REL = re.compile(r"(?<![\w/])(?:gm-assistant/)?setting/")
VERB = re.compile(r"(?:^|[\s;&|(`$])(?:grep|rg|ugrep|sed|awk|cat|head|tail|less|python3?)\b")
MAKE_CANON = re.compile(r"(?:^|[\s;&|(])make\s+(?:-[Cs]\s*\S+\s+)*canon\b")
TERMS = re.compile(r"""\bTERMS=(?:"([^"]*)"|'([^']*)'|(\S+))""")
WINDOW = 3


def terms_of(cmd: str) -> set[str]:
    """The lower-cased terms every `make canon` in a command names."""
    out: set[str] = set()
    for m in TERMS.finditer(cmd):
        out |= {t.strip().lower() for t in (m.group(1) or m.group(2) or m.group(3) or "").split("|") if t.strip()}
    return out


def is_direct(tool: str, ti: dict) -> bool:
    if tool in ("Read", "Grep"):
        return bool(CANON.search(str(ti.get("file_path") or ti.get("path") or "")))
    if tool != "Bash":
        return False
    cmd = str(ti.get("command") or "")
    if MAKE_CANON.search(cmd) and not VERB.search(MAKE_CANON.sub(" ", cmd)):
        return False
    names = CANON.search(cmd) or (CD_HOST.search(cmd) and REL.search(cmd))
    return bool(names and VERB.search(cmd))


def recent_commands(transcript: str, this_id: str, window: int = WINDOW) -> list[str]:
    """The Bash commands of the last `window` main-thread tool calls before this one, oldest first."""
    calls: list[tuple[str, str]] = []
    try:
        lines = open(transcript, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return []
    for line in lines:
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("type") != "assistant" or rec.get("isSidechain"):
            continue
        for c in (rec.get("message") or {}).get("content") or []:
            if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("id") != this_id:
                calls.append((c.get("id") or "", str((c.get("input") or {}).get("command") or "")))
    seen: dict[str, str] = dict(calls)  # a message written twice lists its calls twice
    return list(seen.values())[-window:]


def decide(payload: dict) -> str:
    tool = payload.get("tool_name") or ""
    ti = payload.get("tool_input") or {}
    if is_direct(tool, ti):
        return "direct"
    if tool == "Bash" and MAKE_CANON.search(str(ti.get("command") or "")):
        before = [c for c in recent_commands(payload.get("transcript_path") or "", payload.get("tool_use_id") or "") if MAKE_CANON.search(c)]
        # a call naming every term of the recent ones IS the fold the refusal asked for (and the retry after it)
        if before and not set().union(*map(terms_of, before)) <= terms_of(str(ti.get("command") or "")):
            return "repeat"
    return "pass"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("pass")
        return 0
    print(decide(payload if isinstance(payload, dict) else {}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
