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
_GREP_PATH = re.compile(r"(?:^|\s)grep\b[^|;<>]*\s(?:\$\{?\w+\}?)?(?:(?:~?[\w.-]*/)+[\w.-]+|[\w.-]+\.[\w-]+)\s*$", re.M)
# ...and the path may carry a shell-variable prefix (`$S/gate.log`), which is how the record writes
# it - a variable in front of a path operand is still a path operand (feature 212)

# GUARD_EDIT_OK: feature 227 - ...AND THE WHOLE PATH MAY BE A VARIABLE. `grep -qE "pat" $G` is the same wait with
# the log's name held in a variable, and it was refused: the operand above has to END in path text, which `$G`
# has none of. Caught the way the other two were, by the guard refusing a correct command (2026-09-12, a waiter on
# a detached gate's log). A bare variable qualifies only as the LAST of at least two operands, so `grep -q $PAT`
# with nothing to read - which waits on stdin - is not admitted by it.
_GREP_VAR = re.compile(r"(?:^|\s)grep\b[^|;<>]*?\s(?!-)\S+\s(?:\$\{?\w+\}?)\s*$", re.M)

_IN_REDIR = re.compile(r"<\s*(?:\./|/|~/)?[\w./-]+")

_LOOP_HEAD = re.compile(r"\b(?P<kw>until|while)\b(?P<cond>.*?)(?:;\s*do\b|\bdo\b)", re.S)

# ---- AND THE PROOF OF LIFE, which is what makes a file wait safe (feature 227, GM 2026-09-12) ----
#
# GUARD_EDIT_OK: feature 227 - a wait on a file asks whether the WRITER is still there. A loop that waits
# for a pattern in a log and never asks whether the thing writing that log is alive waits forever when it
# is not: measured at 51 minutes on a detached `make` run that had finished its work and was then killed
# before it could flush stdout, by the kernel's OOM killer, which has fired 36 times in this container
# (`oom_kill 36` in /proc/vmstat). The pattern the loop waited for was never going to be printed.
#
# The GM's ruling is the tooling principle this project already works by - *"if you are waiting on output to
# appear somewhere, but not checking to see whether the process that is supposed to generate that output is
# still alive, then when possible, the hook should add the second proof of life check to what is being
# waited for"*, because *"simply telling you to set a watch properly next time is bad engineering practice
# ... that's just another version of making you remember to do something."* So this module does two things:
#
#   - a LIVENESS TEST IS A QUALIFYING PART of a file-watching condition. It was not, and the guard therefore
#     REFUSED the very shape it should be producing: `until grep -q EXIT= $S/maps.log || ! pgrep -f
#     "ma[p]s" >/dev/null; do sleep 15; done` was blocked as a busy-wait on 2026-09-12. A liveness clause can
#     only make a loop end SOONER, never later, so admitting one is not the "permit whenever backgrounded"
#     bypass the GM declined in feature 165 - and a condition still has to carry at least one real file form,
#     so a bare process wait stays refused exactly as before.
#   - `proof_of_life` ADDS the clause where there is none, naming the file the loop itself is watching.
#     `_writer-alive.sh` answers from the kernel's open-file table rather than from a process pattern, which
#     is the 2026-07-25 self-match trap this guard's other half exists for.
_PROOF_OF_LIFE = re.compile(r"(?:^|\s)!?\s*(?:\S*/)?(?:pgrep|pkill|_writer-alive\.sh)\b|(?:^|\s)!?\s*kill\s+-0\b|(?:^|\s)!?\s*ps\s+-p\b")

# writing to /dev/null is not producing a file, and a liveness clause carries `>/dev/null` as a matter of
# course - without this the `>` test below would disqualify every condition the hook had just corrected
_NULL_OUT = re.compile(r"\s1?>\s*/dev/null")

# the operand to hand the helper: the LAST path-shaped word in the condition, which is the file being watched
# in every form the boundary permits (`grep -q PAT <path>`, `[ -s <path> ]`, `< <path>`)
_PATH_OPERAND = re.compile(r"(?:\$\{?\w+\}?)(?:(?:~?[\w.-]*/)+[\w.-]+|[\w.-]+\.[\w-]+)?|(?:(?:~?[\w.-]*/)+[\w.-]+|[\w.-]+\.[\w-]+)")


def _cond_grammar(cond: str) -> str | None:
    """The condition as the GRAMMAR tests should read it - quoted text neutralized and discarded stderr
    dropped - or None when it carries a command substitution, which nothing legitimate hides in quotes.

    Shared by `file_watching_loop` and `proof_of_life` so the question "is this the permitted shape?" and the
    question "where do I add the liveness clause?" cannot answer differently."""
    if "$(" in cond or "`" in cond:
        return None
    return _STDERR_NULL.sub(" ", _QUOTED.sub(lambda m: re.sub(r"[|<>;&]", "", m.group(0)[1:-1]), cond))


def _part_kind(part: str) -> str:
    """What one `&&`/`||`-joined part of a condition IS: `"file"` (one of the three permitted file reads),
    `"alive"` (a liveness test), or `""` - which disqualifies the whole loop.

    THE OUTPUT-FILE RULE IS PER PART, and deliberately (feature 227). It is the GM's from feature 165 - the
    clause that stops `>/dev/null` on any condition at all from becoming a general bypass - and it was
    written over the whole condition, which is why a wait that ALSO asked whether its producer was alive got
    refused: a liveness test silences its own stdout as a matter of course (`! pgrep -f "[m]ake" >/dev/null`).
    So a redirect is forgiven on a liveness part and on nothing else: `until grep -q x /tmp/a.log >/dev/null`
    is refused today exactly as it was, and `until curl ... > /tmp/out` never qualified on any other ground
    either."""
    alive = bool(_PROOF_OF_LIFE.search(part))
    if alive:
        part = _NULL_OUT.sub(" ", part)
    if _SINGLE_PIPE.search(part) or ">" in part:
        return ""
    if _FILE_TEST.search(part) or _GREP_PATH.search(part) or _GREP_VAR.search(part) or _IN_REDIR.search(part):
        return "file"
    return "alive" if alive else ""


def _watches_a_file(cond: str) -> str | None:
    """The neutralized condition when it is the permitted file-watching shape, else None.

    Every part must qualify and at least one must actually READ A FILE, so a loop whose only clause is a
    liveness test is a process wait and is refused exactly as it always was."""
    c = _cond_grammar(cond)
    if c is None:
        return None
    kinds = [_part_kind(p) for p in _JOIN.split(c)]
    return c if kinds and "" not in kinds and "file" in kinds else None


def proof_of_life(cmd: str, helper: str) -> str | None:
    """`cmd` with a proof-of-life clause added to every file-watching loop that lacks one, or None when
    there is nothing to add (no qualifying loop, or each already asks).

    The clause is ANDed for a `while` loop and `||`-negated for an `until` one, because the two loop while
    opposite things are true and the wait must end in both when the writer is gone."""
    out, shift, added = cmd, 0, False
    for m in _LOOP_HEAD.finditer(cmd):
        c = _watches_a_file(m.group("cond"))
        if c is None or _PROOF_OF_LIFE.search(c):
            continue
        paths = _PATH_OPERAND.findall(c)
        if not paths:
            continue
        clause = f' || ! {helper} "{paths[-1]}"' if m.group("kw") == "until" else f' && {helper} "{paths[-1]}"'
        at = m.end("cond") + shift
        out, shift, added = out[:at] + clause + out[at:], shift + len(clause), True
    return out if added else None

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
    heads = [m.group("cond") for m in _LOOP_HEAD.finditer(cmd)]
    if not heads:
        return False
    # GUARD_EDIT_OK: feature 227 - A LIVENESS CLAUSE IS A QUALIFYING PART, and a condition must still carry
    # at least one real FILE form. Every part had to be one of the three file forms, so the correct shape - a
    # file wait that also asks whether its producer is alive - was refused as a busy-wait. The reading lives in
    # `_watches_a_file` / `_part_kind` now, shared with `proof_of_life` so the shape test and the rewrite
    # cannot answer differently; the boundary itself is unmoved, part by part.
    return all(_watches_a_file(cond) is not None for cond in heads)

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
    elif mode == "proof":
        # GUARD_EDIT_OK: feature 227 - the liveness clause, added to the wait that lacks one. Argument 2 is
        # the helper's absolute path, resolved by the calling hook from its own location.
        _with = proof_of_life(CMD, sys.argv[2] if len(sys.argv) > 2 else "_writer-alive.sh")
        if _with:
            print(_with)
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
