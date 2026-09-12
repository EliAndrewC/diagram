#!/usr/bin/env bash
# shell-check-hooks.sh - the four things a Bash command can be wrong about before it runs
# (feature 236, the GM's items 2 and 3).
#
# GUARD_EDIT_OK: feature 236 - this file IS the guard; the marker is here because a guard file cannot
# be created or repaired without one, and the reason is the header you are reading.
#
# THE GM'S WORDS (`specs/236-catch-mistakes-early-and-cheaply/request.md`): *"if we are running a
# command in bash, and that command has a syntax error such that it is not going to work ... can we
# not have a hook which checks the syntax of the command before we run it and rejects it early?"* and
# *"putting backticks in a place that they do not belong ... have a hook detect that and then reject
# it early"*, and item 3, banning `git commit -m` for a message that needs a heredoc.
#
# WHY EACH ONE IS A REFUSAL RATHER THAN A REWRITE (the feature-164 ladder, applied branch by branch):
#
#   parse             - there is nothing to rewrite. Bash will refuse it anyway; refusing here costs
#                       the same round trip and arrives with the parser's own message.
#   executing-backtick- the fix is a DECISION between two forms with different meanings (single
#                       quotes for text, `$(...)` for a substitution the session actually wants), and
#                       a guard that guesses at meaning writes the wrong command.
#   commit-dash-m     - the broken form parses CLEANLY into the WRONG message: an inner quote closes
#                       the string early, so any rewrite would faithfully preserve a message nobody
#                       wrote. Measured: the instance on record was caught by `bash -n` only by the
#                       accident of a later `(` (`research.md` R2 row 3), so the ban stands alone.
#   coauthor-address  - only the session knows why another address appeared; the placeholder that
#                       reached main did so through an `||` fallback, and history is never rewritten.
#
# The verdicts themselves are in `_hm_shell.py`, which is where they are unit-tested; this file is the
# wiring, the escape and the record. Companion: `scripts/test-shell-check-hooks.sh`.
set -uo pipefail

MODE="${1:-pretool}"
[ "$MODE" = pretool ] || exit 0
INPUT=$(cat)

SC_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$SC_HERE/_guardlog.sh"

# THE ESCAPE IS CHECKED FIRST, or the guard cannot be repaired through the channel it guards - one of
# the three properties this project learned by getting it wrong. `escape_or_refuse` records the reason
# and permits, or refuses a bare token (feature 170: an escape nobody can audit is the rule not
# existing).
if escape_or_refuse shell-check SHELL_CHECK_OK shell-check-ok "$SC_HERE"; then exit 0; fi

VERDICT=$(printf '%s' "$INPUT" | python3 "$SC_HERE/_hm_shell.py" 2>/dev/null)
[ -z "$VERDICT" ] && exit 0

RULE=$(printf '%s' "$VERDICT" | head -1)
MESSAGE=$(printf '%s' "$VERDICT" | tail -n +2)
guard_log shell-check blocked "$(guard_cmd)" "$RULE"

{
  printf 'BLOCKED: %s\n\n' "$MESSAGE"
  printf 'This is caught here because it is cheap here: the same mistake found by running the\n'
  printf 'command costs a failed command, a model turn reading the failure, and a second attempt.\n'
  printf '(scripts/shell-check-hooks.sh, rule "%s"; feature 236, the GM: "reject it early")\n\n' "$RULE"
  printf 'If this fired on correct work, that is a defect in the guard worth fixing rather than\n'
  printf 'working around - the escape is SHELL_CHECK_OK with a reason, and it is recorded:\n\n'
  printf '    <your command>  # SHELL_CHECK_OK: <why this case is legitimate>\n'
} >&2
exit 2
