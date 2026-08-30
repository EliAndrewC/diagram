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
import os.path
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
    # The escape is checked FIRST and stays first (CLAUDE.md: a guard that cannot be repaired
    # through the channel it guards is a worse defect) - what changed in feature 169 is the MATCH.
    # `grep -rn GUARD_EDIT_OK scripts/` used to classify the whole command as `ok`, which switched
    # this guard off for the rest of that command.
    if not cmd or escape_used(cmd, "GUARD_EDIT_OK"):
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
    if any(re.search(pat, raw) for pat in _GUARD_WRITE) or _guard_write_via_name(raw):
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


# An escape token is a SEARCH TARGET in these; anywhere else in a command it is being used.
# `git grep` is covered because the segment's leading word is `git` and `grep` follows it, which the
# scan below allows for; `for tok in GATE_OK POLL_OK ...` is handled separately, since a word list is
# not a command at all.
_SEARCHERS = ("grep", "egrep", "fgrep", "rg", "ack", "ag", "ripgrep")
_FOR_IN = re.compile(r"\bfor\s+\w+\s+in\b[^;\n]*(?:;|\n|$)")


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


# The bracket trick, APPLIED rather than recommended: `no-poll` refuses a literal process-matching
# pattern because it matches the searching shell itself, then names the fix in prose. The fix is
# mechanical, so it is performed.
_PROCMATCH = re.compile(
    r"\b(pgrep|pkill)\b((?:\s+-[a-zA-Z]+)*\s+-[a-zA-Z]*f[a-zA-Z]*)\s+(['\"]?)([^'\"|;&]+)\3"
)


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


if __name__ == "__main__":
    # GUARD_EDIT_OK: feature 165 - the raw payload is kept as well as the command, because one mode
    # (`file-wait`) needs a field beside it (`run_in_background`). Every other mode is unchanged.
    RAW = sys.stdin.read()
    try:
        payload = json.loads(RAW).get("tool_input", {}).get("command", "")
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
    # GUARD_EDIT_OK: feature 164 - the two corrections. Each prints the corrected command, or nothing
    # at all, and silence always means "leave the session's command exactly as it is".
    elif len(sys.argv) > 1 and sys.argv[1] == "as-make-target":
        got = as_make_target(payload)
        if got:
            print(got)
    elif len(sys.argv) > 1 and sys.argv[1] == "bracket":
        got = bracket_pattern(payload)
        if got:
            print(got)
    # GUARD_EDIT_OK: feature 164 - THE COMMAND WITH ITS PROSE BLANKED, for the guards that still match
    # substrings. A heredoc body and a quoted string are payload, never commands, so a hook that
    # matches its shapes against THIS answers "is it invoked" instead of "is it mentioned". Three
    # guards fired on this feature's own documents for naming the shapes they forbid; two of them are
    # fixed by running their existing patterns against this instead of the raw text.
    elif len(sys.argv) > 1 and sys.argv[1] == "as-paired":
        got = as_paired(payload)
        if got:
            print(got)
    # GUARD_EDIT_OK: feature 165 - prints `yes` for the one wait shape the GM permitted (backgrounded,
    # watching a file) and nothing otherwise. Reads the WHOLE payload, because the decision needs
    # `run_in_background` as well as the command.
    elif len(sys.argv) > 1 and sys.argv[1] == "file-wait":
        try:
            whole = json.loads(RAW)
        except Exception:
            whole = {}
        if file_watching_wait(whole):
            print("yes")
    elif len(sys.argv) > 1 and sys.argv[1] == "sanitize":
        print(_strip_quotes(_strip_heredocs(payload)))
    elif len(sys.argv) > 2 and sys.argv[1] == "escape":
        # `escape <TOKEN>` - prints `yes` when the token was USED as an escape, nothing when it was
        # only mentioned. Every guard's escape branch asks this instead of `case "$CMD" in *TOKEN*)`.
        if escape_used(payload, sys.argv[2]):
            print("yes")
    else:
        print(classify(payload))
