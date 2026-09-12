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

# ---- A BACKTICK THAT WOULD RUN (feature 236, the GM's item 2) -----------------------------------
#
# `bash -n` cannot see this one, because it is VALID SYNTAX that runs: inside double quotes, and in
# the body of an UNQUOTED heredoc, a backtick span is command substitution. The usual way one arrives
# is a markdown code span written into prose - a commit message, an echo, a heredoc'd note - which is
# exactly how the Makefile recipe-comment guard came to exist after `make test-full` ran itself from
# inside a comment and recursed 914 levels. That guard covers Makefiles; this covers commands.
#
# It lives HERE, in the shape leaf, because it is the same question both callers ask - what does this
# text literally do - and `_hm_make.recipe_comment_hazards` now asks it through this function rather
# than keeping a second copy of the rule (feature 236 FR-004a).
_QUOTED_HEREDOC = re.compile(r"<<-?\s*(?:'(\w+)'|\"(\w+)\"|\\(\w+))(.*?)^[ \t]*(?:\1|\2|\3)[ \t]*$", re.S | re.M)
#: an UNQUOTED heredoc body is expanded like double-quoted text: a backtick span in it RUNS, and the
#: quote characters in it are literal - an apostrophe there must not hide a later span
_UNQUOTED_HEREDOC = re.compile(r"<<-?\s*([A-Za-z_]\w*)[^\n]*\n(.*?)^[ \t]*\1[ \t]*$", re.S | re.M)
_BACKTICK_SPAN = re.compile(r"(?<!\\)`[^`\n]*(?<!\\)`")


def executing_backticks(text: str, in_double: bool = False) -> list[str]:
    """Every backtick span in `text` that bash would EXECUTE, in order.

    The quote walk is the whole of it: a span inside single quotes or an ANSI-C `$'...'` string does
    not run, nor does one in a heredoc whose delimiter is quoted any of the three ways (`<<'X'`,
    `<<"X"`, `<<\\X`), nor does an escaped backtick open anything, nor does one after an unquoted `#`,
    which begins a comment. A span in an unquoted heredoc body DOES run, and that body's quote
    characters are literal text - the case a plain walker gets wrong, hiding a later span behind an
    apostrophe.

    `in_double=True` starts the walk inside a double-quoted string, which is what a Makefile recipe
    comment's `: "..."` payload is.
    """
    spans: list[str] = []
    text = _QUOTED_HEREDOC.sub(" ", text)

    def _take(m: re.Match[str]) -> str:
        spans.extend(_BACKTICK_SPAN.findall(m.group(2)))
        return " "

    text = _UNQUOTED_HEREDOC.sub(_take, text)
    sq = ansi = esc = False
    dq = in_double
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if esc:
            esc = False
        elif ch == "\\" and not sq:
            esc = True                       # a backslash is literal inside single quotes only
        elif sq:
            if ch == "'":
                sq = ansi = False
        elif ch == "'" and not dq:
            sq, ansi = True, text[i - 1:i] == "$"
        elif ch == '"':
            dq = not dq
        elif ch == "#" and not dq and (i == 0 or text[i - 1] in " \t\n;&|("):
            j = text.find("\n", i)           # a comment runs to the end of the line and executes nothing
            i = n if j < 0 else j
        elif ch == "`":
            j = i + 1
            while j < n and not (text[j] == "`" and text[j - 1] != "\\"):
                j += 1
            if j < n:
                spans.append(text[i:j + 1])
                i = j
        i += 1
    return spans


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
_GREP_PATH = re.compile(r"(?:^|\s)grep\b[^|;<>]*\s(?:\$\{?\w+\}?)?(?:(?:~?[\w.-]*/)+[\w.-]+|[\w.-]+\.[\w-]+)\s*$", re.M)
# ...and the path may carry a shell-variable prefix (`$S/gate.log`), which is how the record writes
# it - a variable in front of a path operand is still a path operand (feature 212)

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
    return file_watching_loop(inp.get("command", "") or "")


# stderr discarded is not a file written: `grep -q x f 2>/dev/null` reads f and writes nothing
_STDERR_NULL = re.compile(r"\s2>\s*/dev/null")
_SINGLE_PIPE = re.compile(r"(?<!\|)\|(?!\|)")
_JOIN = re.compile(r"&&|\|\|")
_QUOTED = re.compile(r"([\"'])(?:\\.|(?!\1).)*\1", re.S)


def file_watching_loop(cmd: str) -> bool:
    """Would `cmd` be the permitted file-watching wait if it were backgrounded? The condition test,
    separated from the `run_in_background` test so a FOREGROUND loop of the same shape can be
    recognized and backgrounded rather than refused (feature 212).

    GUARD_EDIT_OK: feature 212 - THE QUALIFIER MISREAD THE PERMITTED SHAPE. Of the eight real
    backgrounded log-watching waits in the record, it refused SEVEN (specs/212 R1): it read the
    condition RAW, so the `|` inside `grep -qE "gate green|GATE FAILED"` counted as a pipeline, a
    `2>/dev/null` counted as an output redirection, and `[ -s f ] && grep -q x f` matched none of
    the three forms. Quoted strings are blanked before the pipeline and substitution tests, stderr
    sent to /dev/null is not a written file, and a condition of `&&`/`||`-joined parts qualifies
    when EVERY part is one of the three forms. The boundary itself is the GM's from feature 165:
    an output file, a substitution, a real pipeline, a process or network test all still fail it.
    """
    heads = _LOOP_HEAD.findall(cmd)
    if not heads:
        return False
    for cond in heads:
        # a substitution cannot hide inside quotes legitimately, so it is tested on the RAW condition
        if "$(" in cond or "`" in cond:
            return False
        # a `|`, `>` or `;` INSIDE a quoted string is regex or message text, not shell grammar - it is
        # dropped from the copy the grammar tests read, while the rest of the quoted text (a path)
        # stays so `grep -q x "$S/gate.log"` still reads as a wait on a file
        c = _STDERR_NULL.sub(" ", _QUOTED.sub(lambda m: re.sub(r"[|<>;&]", "", m.group(0)[1:-1]), cond))
        if _SINGLE_PIPE.search(c) or ">" in c:
            return False
        for part in _JOIN.split(c):
            if not (_FILE_TEST.search(part) or _GREP_PATH.search(part) or _IN_REDIR.search(part)):
                return False
    return True

# The bracket trick, APPLIED rather than recommended: `no-poll` refuses a literal process-matching
# pattern because it matches the searching shell itself, then names the fix in prose. The fix is
# mechanical, so it is performed.
_PROCMATCH = re.compile(
    r"\b(pgrep|pkill)\b((?:\s+-[a-zA-Z]+)*\s+-[a-zA-Z]*f[a-zA-Z]*)\s+(['\"]?)([^'\"|;&]+)\3"
)


def bracket_pattern(cmd: str) -> str | None:
    """`cmd` with EVERY literal process-match pattern bracketed, or None when there is nothing to fix.

    GUARD_EDIT_OK: 2026-09-08 - every match, not the first one. The first-match form returned None as
    soon as the first pattern was already bracketed, which left a second, self-matching one untouched.
    """
    out = cmd
    for m in reversed(list(_PROCMATCH.finditer(cmd))):
        pat = m.group(4)
        if not pat.strip() or "[" in pat or "$" in pat:
            continue                      # already bracketed, or built from a variable: cannot self-match
        first, rest = pat[0], pat[1:]
        if not first.isalnum():
            continue
        quoted = m.group(3) or "'"
        out = out[: m.start()] + f"{m.group(1)}{m.group(2)} {quoted}[{first}]{rest}{quoted}" + out[m.end() :]
    return None if out == cmd else out


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
    elif mode == "file-wait-loop":
        # would this loop qualify if it were backgrounded? (feature 212: the foreground form is
        # backgrounded rather than refused)
        if file_watching_loop(CMD):
            print("yes")
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
