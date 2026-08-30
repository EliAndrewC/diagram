#!/usr/bin/env python3
"""Command SHAPE - what a command literally IS, before anything judges it (feature 172).

Split out of `_hookmatch.py` so a change to the make/rewrite family stops re-running every guard
suite. This is the BASE of the three: the escape family and the make family both stand on
`_strip_heredocs` and `_strip_quotes`, so a change here is felt everywhere. That is honest rather
than unfortunate - and it is why the split stops at three modules instead of going finer, since past
cohesion the closure through these primitives dominates anyway (specs/172-hooks-test-deps)."""

from __future__ import annotations

import json
import re
import sys

# a command position: start of input or after a separator, then optional leading noise
_POS = r"(?:^|[\n;|]|&&|\|\|)\s*(?:timeout\s+\S+\s+|env\s+|[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*"

_PY = r"(?:\S*/)?python3?"

def _strip_heredocs(cmd: str) -> str:
    """A heredoc body is the payload of a command, never a command. Removed before matching."""
    return re.sub(r"<<-?\s*['\"]?(\w+)['\"]?\n.*?\n\s*\1\b", " <<BODY ", cmd, flags=re.S)

def _strip_quotes(cmd: str) -> str:
    """A quoted string is an argument, never a command - EXCEPT the one after `-c`, which an
    interpreter executes. Blanked before matching, because `_POS` counts `;` and `|` as command
    separators and a quoted regex or message carries them freely: `grep -E "^(ruff|pytest)="`
    fired as a bare pytest run (2026-08-25, the split repository's first session, writing a
    requirements file), which is the mention-versus-invocation defect this module exists to
    prevent. `python3 -c "import pytest; pytest.main()"` keeps its quote and stays blocked."""
    return re.sub(r"(?<!-c )(?<!-c\t)([\"'])(?:\\.|(?!\1).)*\1", r"\1\1", cmd, flags=re.S)

# ---- THE ONE WAIT THAT IS NOT A BUSY-WAIT (feature 165, the GM's ruling 2026-08-30) ------------
#
# `no-poll` refuses every loop containing `sleep`, and it is right about the foreground: that is the
# 10.9-minute incident it was built for. It is wrong about ONE shape - a BACKGROUNDED loop watching a
# FILE, which is the harness's own documented way to get a single completion notification and the only
# way to wait on a run detached with `setsid --fork`. It fired on exactly that twice on 2026-08-30.
#
# THE BOUNDARY IS DELIBERATELY CLOSED, and it is narrower than the ruling's words. The GM was offered
# "permit it whenever backgrounded" and DECLINED it as usable for a general bypass, so a condition
# qualifies only in these three forms, and only with no way to smuggle other work inside it:
_FILE_TEST = re.compile(r"(?:^|\s)(?:test|\[)\s+[^;]*-(?:e|f|s|r|d|w|x)\s+\S", re.M)

# the match target must be a PATH OPERAND and the LAST thing in the condition - either something with
# a directory in it or something with an extension. The first cut allowed only ONE directory segment,
# so `/tmp/164-done.log` - the exact command this ruling exists for - did not qualify.
_GREP_PATH = re.compile(r"(?:^|\s)grep\b[^|;<>]*\s(?:(?:~?[\w.-]*/)+[\w.-]+|[\w.-]+\.[\w-]+)\s*$", re.M)

_IN_REDIR = re.compile(r"<\s*(?:\./|/|~/)?[\w./-]+")

_LOOP_HEAD = re.compile(r"\b(?:until|while)\b(.*?)(?:;\s*do\b|\bdo\b)", re.S)

def file_watching_wait(payload: dict) -> bool:
    """Is this the ONE wait shape the GM permitted - backgrounded, and watching a file?

    Everything else stays refused, including a backgrounded loop that waits on a network call or a
    process. An OUTPUT redirection is not a file read: without that rule `until curl ... > /tmp/out`
    qualifies and `>/dev/null` on any condition at all becomes a general bypass, which is the exact
    risk the GM named when declining the wider option.
    """
    inp = payload.get("tool_input") or {}
    if not inp.get("run_in_background"):
        return False
    cmd = inp.get("command", "") or ""
    heads = _LOOP_HEAD.findall(cmd)
    if not heads:
        return False
    for cond in heads:
        # nothing may hide inside the condition
        if "$(" in cond or "`" in cond or "|" in cond or ">" in cond:
            return False
        if not (_FILE_TEST.search(cond) or _GREP_PATH.search(cond) or _IN_REDIR.search(cond)):
            return False
    return True

# The bracket trick, APPLIED rather than recommended: `no-poll` refuses a literal process-matching
# pattern because it matches the searching shell itself, then names the fix in prose. The fix is
# mechanical, so it is performed.
_PROCMATCH = re.compile(
    r"\b(pgrep|pkill)\b((?:\s+-[a-zA-Z]+)*\s+-[a-zA-Z]*f[a-zA-Z]*)\s+(['\"]?)([^'\"|;&]+)\3"
)


def bracket_pattern(cmd: str) -> str | None:
    """`cmd` with a literal process-match pattern bracketed, or None when there is nothing to fix."""
    m = _PROCMATCH.search(cmd)
    if not m:
        return None
    pat = m.group(4)
    if not pat.strip() or "[" in pat or "$" in pat:
        return None                       # already bracketed, or built from a variable: cannot self-match
    first, rest = pat[0], pat[1:]
    if not first.isalnum():
        return None
    quoted = m.group(3) or "'"
    return cmd[: m.start()] + f"{m.group(1)}{m.group(2)} {quoted}[{first}]{rest}{quoted}" + cmd[m.end() :]


# ---------------------------------------------------------------------------------------------
# A LEAF CLI, so a guard can depend on the module it uses rather than on all of them (feature 172).
# A split behind an umbrella that imports everything changes no dependency set at all: the closure is
# what matters, not the file count. Guards invoke this file directly.
def _payload() -> tuple[str, str, str]:
    raw = sys.stdin.read()
    try:
        ti = json.loads(raw).get("tool_input", {}) or {}
    except Exception:
        ti = {}
    cmd = ti.get("command", "") or ""
    content = (ti.get("new_string") or "") + (ti.get("content") or "")
    return raw, cmd, content


if __name__ == "__main__":
    RAW, CMD, _CONTENT = _payload()
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "sanitize":
        print(_strip_quotes(_strip_heredocs(CMD)))
    elif mode == "bracket":
        out = bracket_pattern(CMD)
        if out:
            print(out)
    elif mode == "file-wait":
        try:
            whole = json.loads(RAW)
        except Exception:
            whole = {}
        if file_watching_wait(whole):
            print("yes")
