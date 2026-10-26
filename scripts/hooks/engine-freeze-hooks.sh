#!/usr/bin/env bash
# engine-freeze-hooks.sh - no engine edit while a map review this session launched is still running (feature 429 FR-001).
# (GUARD_EDIT_OK: a NEW guard, feature 429 - the GM 2026-10-26: "our tooling must enforce the correct behavior every time")
#
# THE DEFECT (feature 261, 2026-09-27; again feature 317, 2026-10-03): a map review's verdict is recorded against the
# engine it reviewed. Engine code was edited while reviews were still running - once mid-round, once after three of
# five had returned, once only a docstring - and every review still running recorded NOT-REVIEWABLE, costing a whole
# extra round each time. The rule ("count the notifications; draft fixes in scratch until the last review is in")
# lived only in a session memory until 2026-10-26, which said a guard was "proposed, not built".
#
# WHAT IS JUDGED (`lib/hm_engine_freeze.py`): an Edit/Write/NotebookEdit of an engine path (`delta.is_engine`) while a
# map-review agent (`pair-hooks.sh`'s REVIEW_AGENTS_RE) launched by this session has not finished - stalled or not.
# No escape: the compliant routes are to wait, or to stop the review (TaskStop) and ack it.
# Test: tests/hooks/test-engine-freeze-hooks.sh.
set -uo pipefail
[ "${1:-}" = "pretool" ] || exit 0
INPUT=$(cat 2>/dev/null || true)
EF_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "$INPUT" in *'"transcript_path"'*) ;; *) exit 0 ;; esac
LIVE=$(printf '%s' "$INPUT" | python3 "$EF_HERE/lib/hm_engine_freeze.py" judge 2>/dev/null) && exit 0
[ -n "$LIVE" ] || exit 0
. "$EF_HERE/lib/guardlog.sh"
TP=$(printf '%s' "$INPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("transcript_path",""))' 2>/dev/null)
SUB="${TP%.jsonl}/subagents"
{
  printf 'BLOCKED: an engine edit while a map review is still running - its verdict would come back NOT-REVIEWABLE.\n'
  printf '%s\n' "$LIVE" | sed 's/^/  running: /'
  printf 'Draft the fix outside the clone (the scratchpad) and make it once every review has returned.\n'
  case "$LIVE" in *stalled*)
    printf 'A stalled review is still running until stopped: TaskStop it, then run exactly:\n'
    printf '%s\n' "$LIVE" | awk -v d="$SUB" '$3=="stalled"{print "  scripts/hooks/agent-stall-hooks.sh ack " d " " $1}' ;;
  esac
} >&2
guard_log engine-freeze blocked "$(guard_cmd)" review-running
exit 2
