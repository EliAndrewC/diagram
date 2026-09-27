#!/bin/bash
# canon-read-hooks.sh - the GM's setting canon is searched with `make canon`, every term at once (feature 250 D16).
# GUARD_EDIT_OK: feature 250 D16 - a NEW guard, the GM's request of 2026-09-26 that R7's recommendation 1 be
# mechanically enforced ("simply saying that we should do a certain thing is probably not enough to make it happen").
#
# THE FAILURE. On `cities/fabric` (R7) a write session checked two canon claims with about fifteen greps through
# `budgets.md` and `l7r.md`, one a turn, each turn re-reading a context that peaked at 137,000 tokens.
#
# TWO RULES. (1) DIRECT: a Read or Grep on a canon file, or a shell read verb naming one, is refused - `make canon
# TERMS="a|b|c"` (scripts/_canon.py) answers every term in one call and names each hit's heading. (2) REPEAT: a
# `make canon` within three tool calls of another is refused unless it names all of the other's terms too - that
# is the fold, and it is also what makes the retry after a refusal pass. The decision is `_hm_canon.py`'s.
#
# ESCAPE: CANON_OK="<reason>" in the command, for a read `make canon` cannot give (a whole section, in order).
#
# Modes:
#   pretool (PreToolUse, Bash|Read|Grep)   refuse / pass, recorded
set -uo pipefail

MODE=${1:-}
CR_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$CR_HERE/_guardlog.sh"

pretool() {
  local verdict
  INPUT="$(cat)"
  verdict="$(printf '%s' "$INPUT" | python3 "$CR_HERE/_hm_canon.py" 2>/dev/null)" || exit 0
  [ "$verdict" = direct ] || [ "$verdict" = repeat ] || exit 0
  escape_or_refuse canon-read CANON_OK "$verdict" "$CR_HERE" && exit 0
  guard_log canon-read blocked "$(guard_cmd)" "$verdict"
  if [ "$verdict" = direct ]; then
    printf 'BLOCKED: read the setting canon with one call naming every term of the claim:\n    make canon TERMS="<term>|<term>|<term>"   (in .claude/skills/diagram)\n' >&2
  else
    printf 'BLOCKED: fold these terms into the last `make canon` - one call, every term:\n    make canon TERMS="<the earlier terms>|<these>"\n' >&2
  fi
  exit 2
}

case "$MODE" in
  pretool) pretool ;;
  *) echo "canon-read-hooks: unknown mode '$MODE' (want: pretool)" >&2; exit 1 ;;
esac
