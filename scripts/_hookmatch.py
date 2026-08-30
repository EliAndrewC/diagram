#!/usr/bin/env python3
"""Decide whether a Bash command STARTS an operation that must go through make (feature 127).

WHY THIS IS A FILE AND NOT A `case` IN THE HOOK. The first version matched substrings anywhere in
the command text, and inside one hour it fired on three pieces of correct work:

  - `grep -n 'def stage_ways' l7r/diagram/hamletgen/ways.py`  - a READ, blocked for naming a path
  - a `git commit` whose MESSAGE quoted the patterns being matched
  - a test harness passing a blocked command as a STRING to check that it gets blocked

All three are the same defect: **a mention is not an invocation.** A guard that fires on correct work
is the one failure this feature cannot have, because it is exactly what teaches a session to reach
for the escape as a matter of routine - which is tier 2 of the threat model, the workaround that
actually happened three times.

So matching is anchored to COMMAND POSITIONS: the start of the input, or just after a `;`, `|`, `&&`,
`||` or newline, skipping any leading `timeout`, `env` or `VAR=value` prefixes. A quoted string, a
heredoc body and a commit message all fail that test by construction, and no list of exceptions has
to be maintained for them.
"""

from __future__ import annotations

import json
import re
import sys

# a command position: start of input or after a separator, then optional leading noise
_POS = r"(?:^|[\n;|]|&&|\|\|)\s*(?:timeout\s+\S+\s+|env\s+|[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*"
_PY = r"(?:\S*/)?python3?"

# a guard file, as the TARGET of a write - the filename adjacent to the operator that writes it
_GUARD = r"[\w./-]*(?:Makefile|[\w-]*-hooks\.sh|settings\.json)"
_GUARD_WRITE = (
    rf">>?\s*{_GUARD}(?:\s|$)",                    # cat > Makefile ; echo x >> scripts/a-hooks.sh
    rf"sed\s+-i\b[^;|&]*?{_GUARD}(?:\s|$)",        # sed -i 's/a/b/' scripts/a-hooks.sh
    rf"tee\s+(?:-a\s+)?{_GUARD}(?:\s|$)",          # tee Makefile
    rf"{_GUARD}[\"\']\s*\)?\s*\)?\s*\.write_text",  # Path("...Makefile").write_text(
)


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
    if not cmd or "GUARD_EDIT_OK" in cmd:
        return "ok"
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
    if any(re.search(pat, raw) for pat in _GUARD_WRITE):
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


if __name__ == "__main__":
    try:
        payload = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except Exception:
        payload = ""
    # `_hookmatch.py targets` prints the make targets the command invokes, one per line, for the hooks
    # that need to know WHICH; with no argument it prints the make-only classification as it always has.
    if len(sys.argv) > 1 and sys.argv[1] == "targets":
        print("\n".join(sorted(targets(payload))))
    # `_hookmatch.py combine` prints the command with the `make quick` work removed when it invokes
    # BOTH quick and done, and prints NOTHING when the shape is one it cannot rebuild exactly. Silence
    # means "leave the session's command alone", which is always the safe answer.
    elif len(sys.argv) > 1 and sys.argv[1] == "combine":
        got = combine(payload)
        if got:
            print(got)
    else:
        print(classify(payload))
