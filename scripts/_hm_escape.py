#!/usr/bin/env python3
"""The ESCAPE family - did a session escape a guard, and did it say WHY (feature 172).

Split out of `_hookmatch.py`. Nearly every guard reaches this, because `_guardlog.sh`'s
`escape_or_refuse` calls it, so a change here re-runs ~20 of 21 suites. That is correct: they really
do all depend on it, and no arrangement of files changes that. Features 169 (an escape is an
INVOCATION, not a mention) and 170 (an escape must state a REASON) are what live here."""

from __future__ import annotations

import json
import os.path
import re
import sys

from _hm_shape import _strip_heredocs, _strip_quotes

# An escape token is a SEARCH TARGET in these; anywhere else in a command it is being used.
# `git grep` is covered because the segment's leading word is `git` and `grep` follows it, which the
# scan below allows for; `for tok in GATE_OK POLL_OK ...` is handled separately, since a word list is
# not a command at all.
_SEARCHERS = ("grep", "egrep", "fgrep", "rg", "ack", "ag", "ripgrep")

_FOR_IN = re.compile(r"\bfor\s+\w+\s+in\b[^;\n]*(?:;|\n|$)")

# THE REASON FLOOR (feature 170, GM 2026-08-30): *"should we just always record that they happened and
# force the Claude Code session, which is performing the workaround to specify why they are doing it?
# Otherwise, we have no way to audit later when this workaround was taken and whether the stated
# reasons were valid use cases."* Every guard documented "with a reason" and every guard accepted a
# BARE token, so the audit the GM describes could not be run: there was often no reason to read.
#
# TWO WORDS AND EIGHT CHARACTERS, and the number matters less than what it excludes. It rejects a bare
# token and `GATE_OK: ok`; it admits `CI is down`, which is ten characters and a perfectly good reason.
# The first draft said fifteen characters and justified itself by the map waiver's sixty - a mechanism
# this repository RETIRED (`dev/gate.md`: "Waivers are gone") - and would have refused that true short
# reason. This is a floor on EFFORT, not on quality: no tool can grade a reason, and the audit is a
# person reading them.
_REASON_WORDS, _REASON_CHARS = 2, 8


def escape_reason(text: str, token: str) -> str:
    """The reason the session gave for this escape, or "" if it gave none.

    Accepts every form the repository actually uses, measured rather than assumed: `TOKEN: why` (135
    occurrences, the marker convention), `TOKEN="why"` and `TOKEN='why'` (the GM's own documented form
    for `PAIR_OK`), and `TOKEN=why`. A bare `TOKEN` yields "". A `TOKEN:` reason runs to the end of its
    line, because that is how a trailing comment is written.
    """
    m = re.search(rf"{re.escape(token)}(\s*[:=]|\s|$)(.*)", text)
    if not m:
        return ""
    sep, rest = m.group(1).strip(), m.group(2)
    q = re.match(r"""\s*(["'])(.*?)\1""", rest)
    if q:
        return q.group(2).strip()
    # AN ASSIGNMENT'S REASON IS ITS VALUE, NOT THE REST OF THE LINE (feature 170). `MEASURE_OK=1 make
    # test-full` must be refused - `1` is not a reason - but taking the rest of the line would read it
    # as "1 make test-full" and pass. A comment (`TOKEN: why`) or a bare note (`TOKEN why`) runs to the
    # end of the line, because that is how a trailing comment is written; an unquoted `=` takes one
    # shell word, because that is what an assignment IS. The suites of `discard` and `no-branch` are
    # what found the other half of this: both carry vectors in the `TOKEN why` form with no colon at
    # all, which the first draft refused - a guard refusing correct work, from the feature whose whole
    # subject is guards that fire on the wrong thing.
    if sep == "=":
        return rest.strip().split()[0].strip("\"'") if rest.strip() else ""
    return rest.split("\n")[0].strip().strip("\"'")

def reason_is_enough(reason: str) -> bool:
    """Does the reason clear the floor? Deliberately generous - see the note above.

    A HYPHENATED COMPOUND COUNTS AS THE WORDS IT IS MADE OF. The repository's own documented vector
    for `HOST_GIT_OK` is `read-only`, which is one whitespace-word, nine characters, and a perfectly
    informative reason for touching the GM's repository - a bare word-count refused it, and refusing
    the form the project itself documents is the failure this whole feature is about. Splitting on
    hyphens and slashes admits `read-only` while still refusing `required`, `manual` and `because`,
    which are one word however you split them and say nothing.
    """
    return len(reason) >= _REASON_CHARS and len(re.split(r"[\s\-/]+", reason.strip())) >= _REASON_WORDS

def escape_used(cmd: str, token: str) -> bool:
    """Did the session put `token` in this command AS AN ESCAPE, or merely mention it?

    THE LAST SUBSTRING TESTS IN THE REPOSITORY WERE THE ESCAPE BRANCHES (feature 169). Every
    BLOCKING decision here has been anchored since 2026-08-25 - `targets` carries the story of the
    six pieces of correct work a bare substring test refused in one day - but every guard still
    decided its own ESCAPE with `case "$CMD" in *TOKEN*)`. Measured on 2026-08-30, all six recorded
    `measure escaped` entries were mentions: four commit messages and heredoc bodies, and two word
    lists from an audit that was itself enumerating the tokens. So `make audit` reported
    `measure escape rate 100%` for a guard nobody had escaped.

    That is worse than a bad statistic, and the statistic is not cosmetic either - the escape RATE is
    what this project acts on (feature 162 retired a refusal escaped in 62% of its firings). Two
    guards also RESET their state on that branch (`measure` clears its repeat-measurement counter,
    `gate` removes its state file), so a command that merely named the token silently disarmed the
    guard for the next command. A session grepping for `MEASURE_OK` to find out how the escape works
    thereby switched it off.

    What counts as a mention: a heredoc body, a quoted string (both already blanked here, which is
    where four of the six came from), a search pattern, and a `for VAR in ...` word list. What still
    counts as an escape: a trailing `# TOKEN: reason` comment, a bare word in a command, and a
    `TOKEN="reason"` assignment prefix - every form `CLAUDE.md` shows.
    """
    clean = _FOR_IN.sub(" ", _strip_quotes(_strip_heredocs(cmd)))
    kept = []
    for seg in re.split(r";|\|\||\||&&|\n", clean):
        words = [w for w in seg.split() if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=\S*", w)]
        # `sudo`/`command`/`git` may stand in front of the searcher; skip them to find the real head
        head = next((w for w in words if w not in ("sudo", "command", "git", "time", "env")), "")
        if os.path.basename(head) in _SEARCHERS:
            # ...but a COMMENT in that segment is still the session talking, not a search pattern.
            # `tail -f log | grep -q done  # POLL_OK: an external port` puts the escape in the LAST
            # segment, whose head is `grep`; dropping it whole would refuse a legitimate escape,
            # which is the failure this repository fears most in a guard. Found by reading the
            # matcher against `no-poll`'s real vectors rather than by a test.
            kept.append(seg.split("#", 1)[1] if "#" in seg else "")
            continue
        kept.append(seg)
    return token in " ".join(kept)


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
    RAW, CMD, CONTENT = _payload()
    TEXT = CMD or CONTENT
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    token = sys.argv[2] if len(sys.argv) > 2 else ""
    if mode == "reason-ok":
        sys.exit(0 if reason_is_enough(RAW.strip()) else 1)
    elif mode == "escape" and token:
        if escape_used(CMD, token):
            print("yes")
    elif mode == "escape-reason" and token:
        reason = escape_reason(TEXT, token)
        if (escape_used(TEXT, token) or (CONTENT and token in CONTENT)) and reason_is_enough(reason):
            print(reason)
