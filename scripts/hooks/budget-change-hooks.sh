#!/usr/bin/env bash
# budget-change-hooks.sh - BLOCK `make budget-change` and `make budget-program` unless WORDS quotes the GM.
# GUARD_EDIT_OK: feature 443 T03 - a NEW guard, plan D6, the GM's approval of the design 2026-10-28
#
# WHY: a work budget a session could raise by itself would be a figure to defend, not a goal (443 FR-005). A make target cannot
# read the session's transcript; a hook can, so WORDS is checked here as an `**Approved**:` line is (lib/hm_budget.py, over
# lib/hm_approval.py): three words or more, verbatim in a message the GM wrote in this session. `make budget-set` (a FIRST
# budget, from a SOUND verdict) needs no words and is not read.
#
# ESCAPE: none, deliberately. The GM's words are the way through.
#
# Wired from .claude/settings.json beside feature-approval-hooks.sh. Tested by tests/hooks/test-budget-change-hooks.sh.

set -u
MODE="${1:-}"
INPUT=$(cat 2>/dev/null || true)
[ "$MODE" = "pretool" ] || exit 0
case "$INPUT" in *budget-change*|*budget-program*) ;; *) exit 0 ;; esac

BC_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BAD=$(printf '%s' "$INPUT" | python3 "$BC_HERE/lib/hm_budget.py" judge 2>/dev/null || true)
[ -n "$BAD" ] || exit 0

# shellcheck source=/dev/null
. "$BC_HERE/lib/guardlog.sh"
{
  printf '\n\033[1mBLOCKED: a work budget changes only with the GM'"'"'s own words (feature 443, FR-005).\033[0m\n'
  case "$BAD" in
    no-words)  printf '  no WORDS= given\n' ;;
    short)     printf '  WORDS is under three words - a bare "yes" approves nothing\n' ;;
    not-found) printf '  the WORDS are in no message the GM wrote in this session\n' ;;
    *)         printf '  %s\n' "$BAD" ;;
  esac
  printf '\nAsk the GM (through escalation-check), then quote the words verbatim:\n'
  printf '  make budget-change PHASE=<stage> TO=<per thing> [EXPONENT=<e>] WORDS="<the GM'"'"'s words>"\n'
  printf '  make budget-program OPS_AT_40=<ops> EXPONENT=<e> WORDS="<the GM'"'"'s words>"\n'
} >&2
guard_log budget-change blocked "budget" "$BAD"
exit 2
