#!/bin/bash
# Tests for agent-prefix-hooks.sh - a large block shared with an earlier dispatch, after a part that differs, is refused
# (feature 383 amendment 6, FR-034, plan D37). Run: tests/hooks/test-agent-prefix-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 383 amendment 6 - a NEW guard's companion suite.
#
# Every case drives the REAL hook with a REAL payload against a fixture repository.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="${AGENT_PREFIX_HOOK:-$HERE/../../scripts/hooks/agent-prefix-hooks.sh}"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT
FIX="$T/clone"; mkdir -p "$FIX"; git -C "$FIX" init -q 2>/dev/null

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
SHARED=$(python3 -c 'print("\n".join(f"Context line {i}: what every check of this kind needs to know about the record." for i in range(130)))')
dispatch() { # dispatch <session> <type> <prompt> -> rc in $T/rc, stderr in $T/err
  python3 -c 'import json,sys; print(json.dumps({"session_id":sys.argv[1],"cwd":sys.argv[4],"tool_name":"Agent","tool_input":{"subagent_type":sys.argv[2],"prompt":sys.argv[3],"description":"x"}}))' "$1" "$2" "$3" "$FIX" \
    | ( cd "$FIX" && "$HOOK" pretool 2>"$T/err" ); echo $? > "$T/rc"
}
rc() { cat "$T/rc"; }
logged() { grep -rlq "$1" "$GUARD_LOG_ROOT" 2>/dev/null; }

echo "1. the GM's shape: a unique sentence, then a shared ~10 KB"
dispatch s1 modal-form "Judge the byre's pop-up.
$SHARED"
[ "$(rc)" -eq 0 ] && ok "the first dispatch passes (nothing earlier to share with)" || no "the first was refused" "(rc=$(rc))"
dispatch s1 modal-form "Judge the well's pop-up.
$SHARED"
[ "$(rc)" -eq 2 ] && ok "the second, its short unique sentence before the same block, is refused" || no "it was allowed" "(rc=$(rc))"
grep -q "START of the prompt" "$T/err" && grep -q ".claude/agents" "$T/err" && ok "...the refusal names both fixes" || no "the fixes are not named" "$(cat "$T/err")"
logged shared-after-difference && ok "...recorded" || no "not recorded"

echo "2. what passes"
dispatch s1 modal-form "$SHARED
Judge the well's pop-up."
[ "$(rc)" -eq 0 ] && ok "the same block FIRST, the unit after it, passes" || no "the fixed form was refused" "(rc=$(rc))"
dispatch s1 modal-form "$SHARED
Judge the gate's pop-up."
[ "$(rc)" -eq 0 ] && ok "...and the next of that form, sharing the block as its prefix" || no "a shared prefix was refused" "(rc=$(rc))"
dispatch s1 modal-research "Judge the well's pop-up.
$SHARED"
[ "$(rc)" -eq 0 ] && ok "another agent type does not share the cache: no comparison across types" || no "refused across types" "(rc=$(rc))"
dispatch s2 modal-form "Judge the barn's pop-up.
$SHARED"
[ "$(rc)" -eq 0 ] && ok "another session's dispatches are not compared" || no "refused across sessions" "(rc=$(rc))"
dispatch s1 modal-form "Read /tmp/l7r-check/x/MANIFEST.md and rule on it."
[ "$(rc)" -eq 0 ] && ok "a short prompt with nothing shared passes" || no "refused" "(rc=$(rc))"
dispatch s1 modal-form "Judge the shed's pop-up. AGENT_PREFIX_OK: a seeded measurement run
$SHARED"
[ "$(rc)" -eq 0 ] && ok "the escape, with a reason, passes" || no "the escape was refused" "(rc=$(rc))"
logged escape && ok "...and is recorded" || no "the escape is not recorded"
dispatch s1 modal-form "Judge the byre again. AGENT_PREFIX_OK
$SHARED"
[ "$(rc)" -eq 2 ] && ok "a bare escape with no reason does not" || no "a bare escape passed" "(rc=$(rc))"

echo "-----"
if [ "$FAIL" -eq 0 ]; then echo "all agent-prefix-hook tests passed ($PASS)"; exit 0; fi
echo "SOME TESTS FAILED ($FAIL of $((PASS+FAIL)))"; exit 1
