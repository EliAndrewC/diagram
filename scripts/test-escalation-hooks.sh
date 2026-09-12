#!/usr/bin/env bash
# Tests for escalation-hooks.sh - a review's findings do not reach the GM unfiltered (2026-09-12).
# Run: scripts/test-escalation-hooks.sh   (exit 0 = all green)
#
# Every case drives the REAL hook with a REAL payload, because a grep proves a call site exists and
# not that it fires - the rule `tests/tooling/test_guard_firing_log.py` was written to enforce.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/escalation-hooks.sh"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0

# a throwaway git work tree, so the hook's clone detection and its state file are real
FIX=$(mktemp -d)/test-clone; mkdir -p "$FIX"
git -C "$FIX" init -q 2>/dev/null
trap 'rm -rf "$GUARD_LOG_ROOT" "$(dirname "$FIX")"' EXIT

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

agent() { # agent <subagent_type> <prompt> -> run the pretool hook in the fixture, print its stdout
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t1","tool_name":"Agent","tool_input":{"subagent_type":sys.argv[1],"prompt":sys.argv[2]}}))' "$1" "$2" \
    | ( cd "$FIX" && "$HOOK" pretool 2>/dev/null )
}
bash_call() { # a non-Agent tool must be ignored entirely
  python3 -c 'import json; print(json.dumps({"session_id":"t1","tool_name":"Bash","tool_input":{"command":"make done"}}))' \
    | ( cd "$FIX" && "$HOOK" pretool 2>/dev/null )
}
stop_call() { # run the stop hook in the fixture, return its exit code, stderr to a file
  printf '{"session_id":"t1"}' | ( cd "$FIX" && "$HOOK" stop 2>/tmp/eh.err );
}
armed_by() { ( cd "$FIX" && "$HOOK" state ) | awk '/^armed by/{print $3}'; }

echo "1. a review dispatch ARMS the requirement, and says so for free"
out=$(agent settlement-review "DELTA review of Inashiro")
[ "$(armed_by)" = "settlement-review" ] && ok "settlement-review arms it" || no "settlement-review did not arm it"
printf '%s' "$out" | grep -q additionalContext && ok "...and the dispatch carries the context, costing no round trip" || no "no additionalContext on the dispatch"
printf '%s' "$out" | grep -q "escalation-check" && ok "...naming the filter to dispatch" || no "the context does not name the filter"

echo "2. the turn cannot close while findings are unfiltered"
stop_call; rc=$?
[ "$rc" -ne 0 ] && ok "stop refuses with a review armed" || no "stop allowed the turn to close" "(rc=$rc)"
grep -q "FINDINGS UNFILTERED" /tmp/eh.err && ok "...and says what is wrong" || no "the refusal does not say what is wrong"
grep -q "process narrative" /tmp/eh.err && ok "...and what the filter is for" || no "the refusal does not say what the filter cuts"
stop_call; rc=$?
[ "$rc" -eq 0 ] && ok "ONCE per armed review, never a loop" || no "stop refused twice for one review" "(rc=$rc)"

echo "3. the filter DISARMS it"
agent escalation-check "here is my draft writeup" >/dev/null
[ -z "$(armed_by)" ] && ok "an escalation-check dispatch disarms it" || no "still armed after the filter ran"
stop_call; rc=$?
[ "$rc" -eq 0 ] && ok "...and the turn may close" || no "stop still refuses after the filter" "(rc=$rc)"

echo "4. the escape works, and it is recorded"
agent settlement-review "review Sawada" >/dev/null
agent settlement-review 'review Sawada ESCALATION_OK="nothing from this pass is relayed, it is a confirmation run"' >/dev/null
[ -z "$(armed_by)" ] && ok "ESCALATION_OK in the dispatch disarms it" || no "the escape did not disarm it"
grep -rlq "escalation-ok" "$GUARD_LOG_ROOT" && ok "...and the escape is recorded with its rule" || no "the escape was not recorded"

echo "5. what must NOT arm it"
agent source-reader "read these three pages" >/dev/null
[ -z "$(armed_by)" ] && ok "an agent whose output the session does not relay (source-reader) does not arm it" || no "source-reader armed it"
agent quote-check "check these footnotes" >/dev/null
[ -z "$(armed_by)" ] && ok "quote-check does not arm it" || no "quote-check armed it"
bash_call >/dev/null
[ -z "$(armed_by)" ] && ok "a Bash call is ignored entirely" || no "a Bash call armed it"
agent building-review "review this manor plan" >/dev/null
[ "$(armed_by)" = "building-review" ] && ok "building-review arms it too" || no "building-review did not arm it"
agent escalation-check "draft" >/dev/null

echo "6. the guard records every acting branch, per RULE (feature 168)"
for rule in review-dispatched filter-ran escalation-ok findings-unfiltered; do
  grep -rlq "$rule" "$GUARD_LOG_ROOT" && ok "recorded: $rule" || no "never recorded: $rule"
done

echo "7. the seams refuse outside a fixture"
( cd "$FIX" && "$HOOK" arm /diagram/.clones/diagram-performance >/dev/null 2>&1 ) && no "arm took a real clone path" || ok "arm refuses a path that is not a fixture"
( cd "$FIX" && "$HOOK" disarm /diagram >/dev/null 2>&1 ) && no "disarm took the mirror" || ok "disarm refuses the mirror"

echo "8. outside a work tree the hook does nothing"
OUT=$(mktemp -d)
rc=0; printf '{"session_id":"t1"}' | ( cd "$OUT" && "$HOOK" stop 2>/dev/null ) || rc=$?
[ "$rc" -eq 0 ] && ok "stop is silent outside a git tree" || no "stop fired outside a git tree" "(rc=$rc)"
rm -rf "$OUT"

echo
echo "escalation-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
