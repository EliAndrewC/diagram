#!/usr/bin/env bash
# ledger-hooks.sh - REFUSE a `git commit` that stages the review ledger while a row of its measured table is short of its check,
# its class or its cost. (GUARD_EDIT_OK: feature 294 - a NEW guard, the spec's US7: "a review row without cost, class or check is
# refused at commit".)
#
# WHY (feature 294, GM 2026-10-01: "I am concerned about both the amount of time and the number of tokens that are spent on this
# review process"). The ledger is where "is the review pulling its weight" is answered, and it answered by impression: 7 of 133
# settlement-review rows recorded a wall time, none a token count, and the "author had missed?" column went empty for a week
# (research R0). A row typed from memory is the failure; so the measured table's cells are checked where they land, at the
# commit, by `scripts/_ledger_lint.py`, and the cost cells are `make review-cost AGENT=<id>`'s.
#
# WHY IT REFUSES: the missing cell is a measurement only the session can take (`make review-cost`) or a judgment only it can make
# (the finding's class) - nothing the guard can supply (feature 164's ladder).
#
# ESCAPE: LEDGER_LINT_OK="<reason>" in the command. Matched as an INVOCATION, refused bare, recorded.
#
# Wired from .claude/settings.json beside the others. Tested by test-ledger-hooks.sh.

set -u
MODE="${1:-}"
INPUT=$(cat 2>/dev/null || true)
[ "$MODE" = "pretool" ] || exit 0

CMD=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("tool_input",{}).get("command",""))
except Exception: print("")' 2>/dev/null || true)
case "$CMD" in *git*commit*) ;; *) exit 0 ;; esac

LH_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$LH_HERE/_guardlog.sh"
if escape_or_refuse ledger LEDGER_LINT_OK ledger-lint-ok "$LH_HERE"; then exit 0; fi

# AN INVOCATION, NOT A MENTION (feature 169): a `git` word whose subcommand - past its global options - is `commit`; and the
# tree it runs in, `git -C <path>` when it names one, else the shell's. Prints nothing when no commit is invoked.
ROOT=$(printf '%s' "$CMD" | python3 -c '
import shlex, sys
try:
    words = shlex.split(sys.stdin.read(), comments=True)
except ValueError:
    words = []
for i, w in enumerate(words):
    if w != "git":
        continue
    j, where = i + 1, ""
    while j < len(words) and words[j].startswith("-"):
        if words[j] == "-C" and j + 1 < len(words):
            where, j = words[j + 1], j + 2
        elif words[j] in ("-c",) and j + 1 < len(words):
            j += 2
        else:
            j += 1
    if j < len(words) and words[j] == "commit":
        print(where or ".")
        break' 2>/dev/null)
[ -n "$ROOT" ] || exit 0
[ "$ROOT" = "." ] && ROOT="$PWD"
ROOT=$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null) || exit 0
LEDGER="docs/review-ledger.md"
[ -f "$ROOT/$LEDGER" ] || exit 0
STAGED=$(git -C "$ROOT" diff --cached --name-only 2>/dev/null)
case " $CMD " in *" -a "*|*" -am "*|*" --all "*) STAGED="$STAGED $(git -C "$ROOT" diff --name-only 2>/dev/null)" ;; esac
case " $STAGED " in *"$LEDGER"*) ;; *) exit 0 ;; esac

LINT="$ROOT/scripts/_ledger_lint.py"
[ -f "$LINT" ] || LINT="$LH_HERE/_ledger_lint.py"
BAD=$(python3 "$LINT" "$ROOT/$LEDGER" 2>/dev/null) && exit 0

{
  printf '\n\033[1mBLOCKED: the review ledger'"'"'s measured table has a row short of a cell.\033[0m\n'
  printf '%s\n' "$BAD" | sed 's/^/  /'
  printf '\nEach row names its CHECK, its finding'"'"'s CLASS (geometric | judgment | paperwork | nothing), whether the author had\n'
  printf 'missed it, and the run'"'"'s WALL and TOKENS copied from:\n\n    make review-cost AGENT=<the agent id>\n\n'
  printf '(feature 294: the ledger measures every check by itself, so "is it pulling its weight" is a total, not an impression.)\n'
  printf 'A row that genuinely cannot carry a cell: LEDGER_LINT_OK="<reason>" in the command.\n\n'
} >&2
guard_log ledger blocked "$(guard_cmd)" ledger-row-short
exit 2
