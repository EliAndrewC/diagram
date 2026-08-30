#!/usr/bin/env python3
"""The MAKE and REWRITE family - which target a command invokes, and the compliant form (feature 172).

Split out of `_hookmatch.py`, and this is the module the split was FOR: only `gate`, `make-only` and
`pair` use it, so a change to `combine`, `as_make_target`, `as_paired` or `targets` now re-runs three
suites instead of twenty-one. Features 162 (combine rather than reject) and 164 (correct rather than
refuse) live here."""

from __future__ import annotations

import json
import re
import sys

from _hm_escape import escape_used
from _hm_shape import _POS, _PY, _strip_heredocs, _strip_quotes

# a guard file, as the TARGET of a write - the filename adjacent to the operator that writes it
_GUARD = r"[\w./-]*(?:Makefile|[\w-]*-hooks\.sh|settings\.json)"

# GUARD_EDIT_OK: feature 169 - TWO FALSE POSITIVES, one of which blocked a command that wrote
# nothing at all. These were matched against the RAW command, so:
#   * `printf '... -> scripts/main-tree-hooks.sh (new) ...'` was refused, because the ARROW in a
#     printf string reads as a redirect. Fixed by `(?<![-\w])`: `->` and `2>` are not `>`.
#   * a guard filename inside a QUOTED STRING is prose, not a target. The shell patterns now match
#     the sanitized command (heredoc bodies and quoted strings blanked), which is what every other
#     decision in this file already does.
# The python-write patterns keep matching RAW on purpose: there the filename IS inside quotes -
# `Path("...settings.json").write_text(...)` - so sanitizing would blank the very thing they detect.
# Fourth and fifth time this repository has made the mention-versus-invocation mistake in this one
# function; proximity is the signal, presence never is.
_GUARD_WRITE_SHELL = (
    rf"(?<![-\w])>>?\s*{_GUARD}(?:\s|$)",         # cat > Makefile ; echo x >> scripts/a-hooks.sh
    rf"sed\s+-i\b[^;|&]*?{_GUARD}(?:\s|$)",        # sed -i 's/a/b/' scripts/a-hooks.sh
    rf"tee\s+(?:-a\s+)?{_GUARD}(?:\s|$)",          # tee Makefile
)

_GUARD_WRITE_PY = (rf"{_GUARD}[\"\']\s*\)?\s*\)?\s*\.write_text",)  # Path("...Makefile").write_text(

# GUARD_EDIT_OK: feature 164 - THE VARIABLE ROUTE, found by walking through it. The patterns above
# need the guard filename ADJACENT to the write, so the ordinary two-line python shape slips past:
#
#     p = pathlib.Path(".claude/settings.json")
#     p.write_text(json.dumps(d))          # <- writes a guard file, matched nothing
#
# This session used exactly that to wire a hook into settings.json while implementing this feature.
# Proximity is still the signal rather than presence (a docstring naming a hook must stay legal), so
# the two halves are tied by the VARIABLE NAME: a name bound to a guard path, and that same name
# writing. `_guard_write_via_name` is separate from the tuple above because it needs two matches.
_GUARD_BIND = re.compile(rf"(\w+)\s*=\s*(?:pathlib\.)?Path\(\s*[\"'][^\"']*{_GUARD}[\"']\s*\)")

def _guard_write_via_name(raw: str) -> bool:
    for m in _GUARD_BIND.finditer(raw):
        if re.search(rf"\b{re.escape(m.group(1))}\.write_text\s*\(", raw):
            return True
    return False

_TARGET = re.compile(_POS + r"(?:\$\(MAKE\)|make)\s+(?:-\S+(?:\s+\S+)?\s+)*(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*([a-z][\w-]*)")

def targets(cmd: str) -> set[str]:
    """Every make TARGET this command actually INVOKES - a mention is not an invocation.

    The same anchoring `classify` uses, for the hooks that care about WHICH target: heredoc bodies and
    quoted strings are blanked first, and a target only counts at a command position (start, or after
    `;`, `|`, `&&`, `||`, a newline), past any flags and `VAR=value` prefixes. `gate-hooks.sh` used a
    bare substring test until 2026-08-29 and blocked six pieces of correct work in one day: a script
    ANALYSING how often its two targets had been run, a plan document quoting them, twice the test file
    that exists to prove guards do not do this, and finally the very command that fixed it. Fourth time
    this repository has made the mention-versus-invocation mistake, which is why the answer lives here
    rather than in another `case`.
    """
    return {m.group(1) for m in _TARGET.finditer(_strip_quotes(_strip_heredocs(cmd)))}

def classify(cmd: str) -> str:
    # The escape is checked FIRST and stays first (CLAUDE.md: a guard that cannot be repaired
    # through the channel it guards is a worse defect) - what changed in feature 169 is the MATCH.
    # `grep -rn GUARD_EDIT_OK scripts/` used to classify the whole command as `ok`, which switched
    # this guard off for the rest of that command.
    if not cmd:
        return "ok"
    # GUARD_EDIT_OK: feature 170 - A DISTINCT VERDICT, so the escape can be RECORDED. It used to
    # return plain `ok` - the same value a command that matched nothing returns - so `make-only`
    # could not tell an escape from an ordinary permitted command and recorded neither. That was
    # feature 169's R13, deferred with a sketch because it changes this function's return contract;
    # the audit that deferral asked for found two consumers, and only `make-only` dispatches on the
    # whole value (`gate-hooks.sh` compares one arm), whose `case` falls through to a permit - so a
    # new value is safe by construction and the arm that records it is explicit.
    if escape_used(cmd, "GUARD_EDIT_OK"):
        return "guard-edit-ok"
    raw = cmd
    c = _strip_quotes(_strip_heredocs(cmd))

    def at(pat: str) -> bool:
        return re.search(_POS + pat, c) is not None

    if at(r"make\s+(?:-\S+\s+)*(?:-f|--file|--makefile)(?:[=\s]|$)"):
        return "foreign-makefile"
    if at(rf"{_PY}\s+(?:-\S+\s+)*-m\s+l7r\.diagram\.") or at(rf"{_PY}\s+\S*l7r/diagram/(?:pipeline/regen|hamletgen/__main__)\.py"):
        return "engine-entry-point"
    if at(rf"(?:{_PY}\s+(?:-\S+\s+)*-m\s+)?pytest\b"):
        return "bare-pytest"
    # AN OVERRIDE COUNTS WHEREVER IT SITS ON THE COMMAND. `REF_WHY=x make done` puts it in front;
    # `make done FULL=1 REF_WHY=x` passes it as a make argument. Both skip the prompt, so both are
    # tier 2 - the first cut only matched the leading form and the suite caught it immediately.
    if re.search(r"\b(?:REF_WHY|REF_OK|GATE_OK)=", c) and (at(r"make\b") or re.search(_POS + r"(?:REF_WHY|REF_OK|GATE_OK)=", c)):
        return "inline-override"
    # GUARD-WRITE READS THE RAW COMMAND, NOT THE STRIPPED ONE, and this is the one place that is
    # right: everywhere else a heredoc body is prose to ignore, but here it is the payload that does
    # the writing - `python3 - <<PY ... write_text("...Makefile") ... PY` is exactly the route that
    # slipped past layer 3 all day.
    #
    # THE GUARD FILE MUST BE THE TARGET OF THE WRITE, not merely present somewhere. The first cut
    # asked "does a guard filename appear AND does a write appear", which blocked a command creating
    # an ordinary test file whose DOCSTRING mentioned a hook by name. Third time this feature has
    # made the mention-versus-invocation mistake - a grep, a commit message, and now a docstring -
    # which is worth stating plainly: proximity is the signal, presence never is.
    if (
        any(re.search(pat, c) for pat in _GUARD_WRITE_SHELL)          # sanitized: see feature 169
        or any(re.search(pat, raw) for pat in _GUARD_WRITE_PY)        # raw: the name lives in quotes
        or _guard_write_via_name(raw)
    ):
        return "guard-write"
    return "ok"

# ---- COMBINE, DO NOT REJECT (feature 162) ---------------------------------------------------
#
# WHY (GM 2026-08-30): *"does that mean our tooling should detect when both are being run and then
# combine them into `make done` automatically instead of rejecting?"* It does. `gate-hooks.sh` used
# to refuse a command naming both targets, and the refusal cost a round trip - measured over this
# project's transcripts, 37 firings of which 23 were escaped with `GATE_OK` in the very next call,
# so 62% of the time the guard spent a turn and prevented nothing. A `PreToolUse` hook may instead
# return the command REWRITTEN (`updatedInput`), which costs nothing at all.
_SEP = re.compile(r"(\s*(?:&&|\|\||;|\n)\s*)")

_MAKE_HEAD = re.compile(r"^(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*(?:\$\(MAKE\)|make)\b")

# EVERY GOAL OF ONE MAKE CALL, not just the first. `targets()` answers "which targets does this
# command invoke" and stops at the first goal of each call, which is enough for a yes/no guard and is
# NOT enough to rewrite `make quick done` - the shape the GM asked to be combined. Kept local so the
# eleven other guards keep the matcher they were tested against.
# The `[./~]\S*` arm exists so a PATH argument does not end the scan: `make -C /x quick` would
# otherwise stop at `/x` and never see the goal behind it, and the rewrite would silently decline a
# command it understands perfectly well. _TAKES_ARG below is what keeps that path from counting as a
# goal itself.
_GOALS = re.compile(
    _POS + r"(?:\$\(MAKE\)|make)((?:\s+(?:-\S+|[A-Za-z_][A-Za-z0-9_]*=\S*|[./~]\S*|[a-z][\w-]*))*)"
)

# `-C dir` and `-f file` take an ARGUMENT, and the argument is not a goal. Without this, `make -C done
# quick` reads as a call carrying both goals and the rewrite would "combine" it into `make -C done`,
# which runs the default target somewhere else entirely. No such command exists in this repository
# today; a rewrite that must never guess does not get to rely on that.
_TAKES_ARG = ("-C", "-f", "--directory", "--file", "--makefile", "-o", "--old-file", "-W")

def _goals(seg: str) -> set[str]:
    out = set()
    for m in _GOALS.finditer(_strip_quotes(_strip_heredocs(seg))):
        skip = False
        for word in m.group(1).split():
            if skip:
                skip = False
                continue
            if word in _TAKES_ARG:
                skip = True
                continue
            if re.fullmatch(r"[a-z][\w-]*", word):
                out.add(word)
    return out

def _balanced(text: str) -> bool:
    return text.count("(") == text.count(")") and text.count('"') % 2 == 0 and text.count("'") % 2 == 0

def combine(cmd: str) -> str | None:
    """`cmd` with the `make quick` work removed, when it invokes BOTH quick and done.

    None means "leave it alone": the shape is not one that can be rebuilt exactly, so the command
    goes through UNCHANGED rather than being guessed at. A guessed rewrite costs a session its
    command; the fallback costs one warm `quick` (4.1 s). `done` is a superset of `quick` - it runs
    the same lint, format and typecheck and a strict superset of the tests - so dropping `quick`
    never drops a question that was asked.
    """
    if not cmd or "GATE_OK" in cmd or "<<" in cmd:
        return None
    if "quick" not in _goals(cmd) or "done" not in _goals(cmd):
        return None
    parts = _SEP.split(cmd)                       # [seg, sep, seg, sep, ...]
    segs, seps = parts[0::2], parts[1::2]
    kept: list[tuple[str, str]] = []
    dropped = False
    for i, seg in enumerate(segs):
        sep = seps[i] if i < len(seps) else ""
        got = _goals(seg)
        makeish = bool(_MAKE_HEAD.match(seg.strip())) and _balanced(seg)
        if makeish and "quick" in got and "done" not in got:
            dropped = True                        # a whole segment whose work `done` supersedes
            continue
        if makeish and got >= {"quick", "done"}:
            rebuilt = re.sub(r"\s+quick\b", "", seg, count=1)
            if _goals(rebuilt) != got - {"quick"}:
                return None
            kept.append((rebuilt, sep))
            dropped = True
            continue
        kept.append((seg, sep))
    if not dropped:
        return None
    out = "".join(s + (p if j < len(kept) - 1 else "") for j, (s, p) in enumerate(kept))
    out = out.strip().rstrip("&|; \n").strip()
    if not out or out == cmd or "done" not in _goals(out) or "quick" in _goals(out):
        return None
    return out

# ---- CORRECT, DO NOT REFUSE (feature 164) ----------------------------------------------------
#
# GUARD_EDIT_OK: new shared decisions for the guards, at the GM's request (2026-08-30): *"are there
# places where a makefile command is refusing to do something but a tool could do a rewrite or return
# additional context or whatever?"* There are. The audit found 280 refusals in six days, each one
# spending a model round trip; where the guard already KNOWS the compliant command - it names it in
# its own refusal - it may as well produce it. These decisions live here rather than in the hooks so
# they can be tested with plain strings instead of through bash quoting.

# What `make test-file` runs: pytest with workers, `-q` and `--no-cov` on ONE file. A flag that target
# already supplies, or one that only asks for less output, is safe to drop. Anything that changes
# WHICH tests run or HOW they are measured is not, so those keep the refusal - the same never-guess
# rule feature 162 set for the quick/done rewrite.
_DROPPABLE = re.compile(
    r"^(-q|-qq|--quiet|-x|--exitfirst|--no-cov|--no-header|-p|no:cacheprovider|-n|auto|\d+"
    r"|--dist|worksteal|-v|--tb=\S+|--color=\S+)$"
)

_TESTPATH = re.compile(r"^[\w./-]+/test_[\w-]+\.py$|^test_[\w-]+\.py$")

_PYTEST_RUN = re.compile(r"(?:\S*/)?python3?\s+(?:-\S+\s+)*-m\s+pytest\s+|(?:^|\s)pytest\s+")

def as_make_target(cmd: str) -> str | None:
    """A bare pytest of ONE test file as `make test-file FILE=...`, or None to keep refusing.

    None means the shape is not one that can be rebuilt exactly - a filter, a coverage flag, a second
    path, a directory, a pipeline - and the guard refuses it as it always has. What the rewrite
    preserves is feature 127's invariant, that every test invocation goes through a make target; it
    does NOT preserve coverage floors, because neither this command nor the target holds them.
    """
    m = _PYTEST_RUN.search(cmd)
    if not m:
        return None
    head, tail = cmd[: m.start()], cmd[m.end() :]
    if any(sep in tail for sep in ("|", ">", "&&", ";", "<<")):
        return None                       # a pipeline or a chain: not ours to rebuild
    # `( cd <abs> && ... )` is this project's own convention for a command needing a cwd, so the
    # closing paren is part of the shape rather than an argument. Kept and re-appended verbatim.
    close = ""
    if tail.rstrip().endswith(")"):
        tail, close = tail.rstrip()[:-1], " )"
    paths, unknown = [], []
    for word in tail.split():
        if _TESTPATH.match(word):
            paths.append(word)
        elif not _DROPPABLE.match(word):
            unknown.append(word)
    if len(paths) != 1 or unknown:
        return None
    return f"{head}make test-file FILE={paths[0]}{close}"


def as_paired(cmd: str) -> str | None:
    """`make done` as `make verify` - the paired command - or None to keep refusing.

    `pair-hooks` refuses the gate when no review is beside it, and names `make verify` in the refusal.
    That is a substitution, so it is performed: the gate still runs, and the session is told to
    dispatch the review in the same turn. Only an invocation whose goals are EXACTLY `done` converts;
    `make done FULL=1` and anything carrying another goal keep the refusal, because `verify` is not
    defined to take them and a guard may not guess at what a session meant.
    """
    if not cmd or "FULL" in cmd:
        return None
    # TWO REWRITES MUST NOT RACE FOR ONE COMMAND. `gate-hooks` combines a `quick`+`done` command into
    # `make done`; if this one also fired, the outcome would depend on hook order, and a guard whose
    # result is unpredictable is worse than one that refuses. So a command naming `quick` is left to
    # that conversion, and this one declines it.
    if "quick" in _goals(cmd):
        return None
    segs = _SEP.split(cmd)[0::2]
    hits = [s for s in segs if _MAKE_HEAD.match(s.strip()) and _goals(s) == {"done"}]
    if len(hits) != 1:
        return None
    seg = hits[0]
    rebuilt = re.sub(r"(?<=\s)done(?=\s|$)", "verify", seg, count=1)
    if _goals(rebuilt) != {"verify"}:
        return None
    return cmd.replace(seg, rebuilt, 1)


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
    if mode == "targets":
        print("\n".join(sorted(targets(CMD))))
    elif mode == "combine":
        out = combine(CMD)
        if out:
            print(out)
    elif mode == "as-make-target":
        out = as_make_target(CMD)
        if out:
            print(out)
    elif mode == "as-paired":
        out = as_paired(CMD)
        if out:
            print(out)
    else:
        print(classify(CMD))
