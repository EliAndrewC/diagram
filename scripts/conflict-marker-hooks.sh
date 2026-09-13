#!/usr/bin/env bash
# conflict-marker-hooks.sh - BLOCK a `git add` or `git commit` that would stage a file still carrying an
# unresolved merge conflict. (GUARD_EDIT_OK: feature 241 - a NEW guard, the GM's instruction 2026-09-13.)
#
# WHY (the GM, 2026-09-13: "let's talk about a tooling fix for the `git add -A` issue that keeps
# happening"). Twice in one day a conflicted merge was committed with its markers in it:
#
#   1. 2026-09-12 morning - one file, pool/hamlets/kuwabata/kuwabata.json. Caught by ACCIDENT, when
#      `make notes-census` could not parse it.
#   2. 2026-09-13 ~02:00 - TWENTY-THREE files, merging main's feature 230 into the 227/237 clone: six
#      engine modules, five test modules, five manifests, five notes files, two research pages. Caught by
#      the gate's lint phase, after the commit. The merge had to be redone from the merge base, because
#      the history here is never rewritten, and that cost about an hour of an eight-hour session.
#
# Both times the command was `git add -A` and both times the harm was the COMMIT, not the staging.
#
# WHY THE RULE IS ON CONTENT AND NOT ON MERGE STATE. The obvious guard is "refuse `add -A` while
# MERGE_HEAD exists". It would have caught both and it is still wrong: the end of every RESOLVED merge is
# exactly `git add -A` with MERGE_HEAD present, so it would refuse the correct command - and a guard that
# fires on correct work teaches a session to pattern-match past every guard, which is the more expensive
# failure. It would also miss a marker that arrived from a `git am`, a patch script or a typo. So the rule
# is the harm itself: a file holding the TRIPLE git leaves (seven `<`, a line of seven `=`, seven `>`) is
# not stageable. A resolved merge has none, and `add -A` passes untouched.
#
# WHY IT REFUSES RATHER THAN FIXING (feature 212's ladder). The compliant command stages the files that
# are RESOLVED, and which those are is the session's knowledge, not the guard's - the same reason
# `make-only`'s guard-write and `guard-file`'s no-marker branch stayed refusals.
#
# ESCAPE: CONFLICT_MARKERS_OK="<reason>" in the command, for the file that carries a marker on purpose (a
# fixture, a doc). Matched as an INVOCATION (feature 169), refused bare (feature 170), recorded (168).
#
# Wired from .claude/settings.json beside the others. Tested by test-conflict-marker-hooks.sh.

set -u
MODE="${1:-}"
INPUT=$(cat 2>/dev/null || true)
[ "$MODE" = "pretool" ] || exit 0

CMD=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("tool_input",{}).get("command",""))
except Exception: print("")' 2>/dev/null || true)
[ -n "$CMD" ] || exit 0

CM_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$CM_HERE/_guardlog.sh"
if escape_or_refuse conflict-marker CONFLICT_MARKERS_OK conflict-markers-ok "$CM_HERE"; then exit 0; fi

case "$CMD" in *"git add"*|*"git commit"*) ;; *) exit 0 ;; esac

BAD=$(printf '%s' "$CMD" | CM_CWD="$PWD" CM_HERE="$CM_HERE" python3 -c '
import os, re, shlex, subprocess, sys

sys.path.insert(0, os.environ["CM_HERE"])
from _hm_conflict import conflicted  # noqa: E402

cmd = sys.stdin.read()
paths: list[str] = []
for piece in re.split(r"&&|\|\||;|\|", cmd):
    try:
        toks = shlex.split(piece, comments=True)
    except ValueError:
        toks = piece.split()
    if "git" not in toks:
        continue
    rest = toks[toks.index("git") + 1 :]
    repo = os.environ.get("CM_CWD", ".")
    while rest and rest[0] in ("-C", "-c") and len(rest) >= 2:
        if rest[0] == "-C":
            repo = rest[1]
        rest = rest[2:]
    if not rest:
        continue
    sub, args = rest[0], rest[1:]
    if sub not in ("add", "commit"):
        continue

    def _git(*a: str) -> list[str]:
        r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=False)
        return [ln for ln in r.stdout.splitlines() if ln]

    named = [a for a in args if not a.startswith("-")]
    if sub == "add":
        whole = any(a in ("-A", "--all", ".", "-u", "--update") for a in args) or "." in named
        if whole or not named:
            # everything the tree would hand it: tracked changes plus untracked files
            paths += [os.path.join(repo, p) for p in _git("diff", "--name-only")]
            paths += [os.path.join(repo, p) for p in _git("ls-files", "-o", "--exclude-standard")]
        else:
            paths += [p if os.path.isabs(p) else os.path.join(repo, p) for p in named]
    else:  # commit
        if any(a in ("-a", "--all") for a in args) or any(a.startswith("-") and not a.startswith("--") and "a" in a[1:] for a in args):
            paths += [os.path.join(repo, p) for p in _git("diff", "--name-only")]
        paths += [os.path.join(repo, p) for p in _git("diff", "--cached", "--name-only")]

print("\n".join(conflicted(sorted(set(paths)))))
' 2>/dev/null || true)

[ -n "$BAD" ] || exit 0

{
  printf '\n\033[1mBLOCKED: this would stage a file that still carries a merge conflict.\033[0m\n'
  printf '%s\n' "$BAD" | sed 's/^/  /'
  printf '\nEach file above still holds the triple `git merge` left in it. Resolve them and stage what you\n'
  printf 'resolved - this guard will not pick which is which, because only you know that.\n'
  printf '\nWhy this is refused rather than narrowed to the clean files: the harm is the COMMIT. The history\n'
  printf 'here is never rewritten, so a marker that lands cannot be amended away - it took an hour to redo a\n'
  printf 'merge from its base on 2026-09-13, and one file went unnoticed on 2026-09-12 until `make\n'
  printf 'notes-census` could not parse it. `git add -A` is not the problem and is not blocked; an\n'
  printf 'UNRESOLVED file is.\n'
  printf '\nA file that carries a marker on purpose - a fixture, a doc about merges - passes with\n'
  printf 'CONFLICT_MARKERS_OK="<reason>" in the command.\n\n'
} >&2
guard_log conflict-marker blocked "git-$( [ "${BAD#*$'\n'}" != "$BAD" ] && echo many || echo one )" staged-conflict
exit 2
