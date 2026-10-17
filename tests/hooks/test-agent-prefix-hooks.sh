#!/bin/bash
# Tests for agent-prefix-hooks.sh - a large block repeated from an earlier dispatch of its type is refused wherever it sits, and a
# fan-out of one type launches its first alone (feature 383 amendment 6: FR-034 as corrected, FR-039; plans D41, D42).
# Run: tests/hooks/test-agent-prefix-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 383 amendment 6 - the guard's companion suite; reopened: a block placed first is refused too.
#
# Every case drives the REAL hook with a REAL payload against a fixture repository. The decider's clock is L7R_AGENT_NOW: each
# dispatch here is a minute after the last unless a case sets it, so only the fan-out cases sit inside the fan-out window.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="${AGENT_PREFIX_HOOK:-$HERE/../../scripts/hooks/agent-prefix-hooks.sh}"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT
FIX="$T/clone"; mkdir -p "$FIX"; git -C "$FIX" init -q 2>/dev/null
NOW=1000000

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
SHARED=$(python3 -c 'print("\n".join(f"Context line {i}: what every check of this kind needs to know about the record." for i in range(130)))')
dispatch() { # dispatch <session> <type> <prompt> [<seconds after the last>] -> rc in $T/rc, stderr in $T/err
  NOW=$((NOW + ${4:-60}))
  python3 -c 'import json,sys; print(json.dumps({"session_id":sys.argv[1],"cwd":sys.argv[4],"tool_name":"Agent","tool_input":{"subagent_type":sys.argv[2],"prompt":sys.argv[3],"description":"x"}}))' "$1" "$2" "$3" "$FIX" \
    | ( cd "$FIX" && L7R_AGENT_NOW="$NOW" "$HOOK" pretool 2>"$T/err" ); echo $? > "$T/rc"
}
rc() { cat "$T/rc"; }
logged() { grep -rlq "$1" "$GUARD_LOG_ROOT" 2>/dev/null; }

echo "1. a repeated block is refused wherever it sits"
dispatch s1 modal-form "Judge the byre's pop-up.
$SHARED"
[ "$(rc)" -eq 0 ] && ok "the first dispatch passes (nothing earlier to share with)" || no "the first was refused" "(rc=$(rc))"
dispatch s1 modal-form "Judge the well's pop-up.
$SHARED"
[ "$(rc)" -eq 2 ] && ok "the GM's shape - a short unique sentence, then the same block - is refused" || no "it was allowed" "(rc=$(rc))"
grep -q ".claude/agents" "$T/err" && ok "...the refusal names the agent-file fix" || no "the agent file is not named" "$(cat "$T/err")"
grep -qi "START of the prompt\|put the shared text first\|shared text FIRST" "$T/err" && no "...it still says to put the shared text first" || ok "...and never says to put it first (research R16)"
logged repeated-block && ok "...recorded" || no "not recorded"
dispatch s1 modal-form "$SHARED
Judge the well's pop-up."
[ "$(rc)" -eq 2 ] && ok "the same block FIRST is refused too - a launch prompt has no cache breakpoint" || no "a block placed first was allowed" "(rc=$(rc))"

echo "2. what passes"
dispatch s1 modal-form "Judge the byre's pop-up.
$SHARED"
[ "$(rc)" -eq 0 ] && ok "a prompt identical to an earlier one as a whole passes (the cache reuses that)" || no "an identical prompt was refused" "(rc=$(rc))"
dispatch s1 modal-research "Judge the well's pop-up.
$SHARED"
[ "$(rc)" -eq 0 ] && ok "another agent type: no comparison across types (its fix is its own file)" || no "refused across types" "(rc=$(rc))"
dispatch s2 modal-form "Judge the barn's pop-up.
$SHARED"
[ "$(rc)" -eq 0 ] && ok "another session's dispatches are not compared" || no "refused across sessions" "(rc=$(rc))"
dispatch s1 modal-form "Read /tmp/l7r-check/x/MANIFEST.md and rule on it."
[ "$(rc)" -eq 0 ] && ok "a short prompt with nothing repeated passes" || no "refused" "(rc=$(rc))"
dispatch s1 modal-form "Judge the shed's pop-up. AGENT_PREFIX_OK: a seeded measurement run
$SHARED"
[ "$(rc)" -eq 0 ] && ok "the escape, with a reason, passes" || no "the escape was refused" "(rc=$(rc))"
logged escape && ok "...and is recorded" || no "the escape is not recorded"
dispatch s1 modal-form "Judge the byre again. AGENT_PREFIX_OK
$SHARED"
[ "$(rc)" -eq 2 ] && ok "a bare escape with no reason does not" || no "a bare escape passed" "(rc=$(rc))"

echo "3. every repeated run is judged, not the longest alone"
B=$(python3 -c 'print("\n".join(f"Block B line {i}: the standing rules every dispatch of this check carries along." for i in range(60)))')
C=$(python3 -c 'print("\n".join(f"Block C line {i}: a second shared context, after the unit this time." for i in range(35)))')
dispatch s3 record-format "$C
$B"
dispatch s3 record-format "Judge question 0087 alone.
$C"
[ "$(rc)" -eq 2 ] && grep -q "Block C line 0" "$T/err" && ok "a shorter repeated block is refused on its own" || no "it was allowed" "(rc=$(rc)) $(head -3 "$T/err")"

echo "4. a fan-out launches its first alone"
dispatch s4 quote-check "Read /tmp/l7r-check/a/MANIFEST.md and rule on it." 400
[ "$(rc)" -eq 0 ] && ok "the first of a fan-out, nothing of its type in the cache's lifetime, goes" || no "the first was refused" "(rc=$(rc))"
dispatch s4 quote-check "Read /tmp/l7r-check/b/MANIFEST.md and rule on it." 1
[ "$(rc)" -eq 2 ] && grep -q "next message" "$T/err" && ok "a second of its type a second later is refused: send it in the next message" || no "the fan-out's second went" "(rc=$(rc)) $(head -3 "$T/err")"
logged fan-out && ok "...recorded" || no "the fan-out refusal is not recorded"
dispatch s4 quote-check "Read /tmp/l7r-check/b/MANIFEST.md and rule on it." 20
[ "$(rc)" -eq 0 ] && ok "...and goes in the next message, the first's prefix now written" || no "the next message's dispatch was refused" "(rc=$(rc))"
dispatch s4 quote-check "Read /tmp/l7r-check/c/MANIFEST.md and rule on it." 1
[ "$(rc)" -eq 0 ] && ok "dispatches after a warm one are not a cold fan-out" || no "a warm burst was refused" "(rc=$(rc))"
dispatch s4 glyph-check "Judge the byre's glyph." 1
[ "$(rc)" -eq 0 ] && ok "another type's first dispatch is its own" || no "another type was refused" "(rc=$(rc))"

echo "-----"
if [ "$FAIL" -eq 0 ]; then echo "all agent-prefix-hook tests passed ($PASS)"; exit 0; fi
echo "SOME TESTS FAILED ($FAIL of $((PASS+FAIL)))"; exit 1
