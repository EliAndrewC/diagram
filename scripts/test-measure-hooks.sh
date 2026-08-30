#!/usr/bin/env bash
# GUARD_EDIT_OK: the test companion of the new measure-hooks.sh guard (feature 146, at the GM's request).
#
# Tests for measure-hooks.sh. Feeds PreToolUse events and asserts when an expensive measurement is
# blocked. Run: scripts/test-measure-hooks.sh   (exit 0 = all green)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/measure-hooks.sh"
PASS=0; FAIL=0

setup() { STATE_DIR=$(mktemp -d); export MEASURE_STATE_DIR="$STATE_DIR"; }
teardown() { rm -rf "$STATE_DIR"; }

bash_ev() { printf '{"session_id":"m1","tool_name":"Bash","tool_input":{"command":"%s"}}' "$1"; }
edit_ev() { printf '{"session_id":"m1","tool_name":"Edit","tool_input":{"file_path":"%s"}}' "$1"; }
run() { "$HOOK" pretool <<<"$1" 2>/tmp/mt.err; }

check() { # label expected(ok|blocked) rc
  if { [ "$2" = ok ] && [ "$3" -eq 0 ]; } || { [ "$2" = blocked ] && [ "$3" -ne 0 ]; }; then
    echo "  ok    $1"; PASS=$((PASS+1))
  else
    echo "  FAIL  $1 (expected $2, rc=$3)"; [ -s /tmp/mt.err ] && sed 's/^/        /' /tmp/mt.err; FAIL=$((FAIL+1))
  fi
}

# GUARD_EDIT_OK: feature 161 - the budget is 1 now (GM 2026-08-30: *"should we make it so we start
# blocking at 2 in a row instead of 3 in a row?"*), so the vectors move from "the third" to "the
# second". Nothing else about the state machine changed and every other vector below is untouched.
echo "1. THE MOTIVATING CASE: measure, write one test, measure"
setup
run "$(bash_ev 'make test-full')"; check "the first measurement is allowed" ok $?
run "$(edit_ev '/diagram/.claude/skills/diagram/tests/settlement/test_geom.py')"
run "$(bash_ev 'make test-full')"; check "the SECOND is BLOCKED" blocked $?
grep -q "Measure ONCE" /tmp/mt.err && { echo "  ok    the message says what to do instead"; PASS=$((PASS+1)); } || { echo "  FAIL  message unhelpful"; FAIL=$((FAIL+1)); }
grep -q "make quick" /tmp/mt.err && { echo "  ok    the message names the cheap loop"; PASS=$((PASS+1)); } || { echo "  FAIL  message does not name make quick"; FAIL=$((FAIL+1)); }
# ...AND THE COMMAND THAT ANSWERS THE BLOCKED QUESTION. A session reaching for `make test-full` a third time
# is almost always asking "which lines does this test reach?", and `make quick` does not answer that - so a
# message that names only the cheap loop sends it back to the expensive call (GM 2026-08-29: *"Does the make
# cov-file get suggested automatically when you are warned about running make test-full too often"* - it did
# not). A guard that blocks a legitimate question without giving the route is one that gets worked around.
grep -q "make cov-file" /tmp/mt.err && { echo "  ok    the message names the targeted coverage probe"; PASS=$((PASS+1)); } || { echo "  FAIL  message does not name make cov-file"; FAIL=$((FAIL+1)); }
run "$(bash_ev 'make test-full')"; check "re-issuing goes through (blocks once, no deadlock)" ok $?
teardown

echo "2. an ENGINE edit resets it - the numbers really are stale now"
setup
run "$(bash_ev 'make test-full')"; run "$(bash_ev 'make test-full')"
run "$(edit_ev '/diagram/.claude/skills/diagram/l7r/diagram/hamletgen/ways.py')"
run "$(bash_ev 'make test-full')"; check "allowed after an engine edit" ok $?
teardown

echo "3. a COMMIT resets it - a landed batch is the unit this rule is about"
setup
run "$(bash_ev 'make test-full')"; run "$(bash_ev 'make test-full')"
run "$(bash_ev 'git commit -q -m \"a batch of tests\"')"
run "$(bash_ev 'make test-full')"; check "allowed after a commit" ok $?
teardown

echo "4. the CHEAP loop is never blocked, however often it runs"
setup
for _ in 1 2 3 4 5 6; do run "$(bash_ev 'make quick ALL=1')"; done
check "six make quick runs, still fine" ok $?
for _ in 1 2 3 4 5 6; do run "$(bash_ev 'make test-file FILE=tests/settlement/test_geom.py')"; done
check "six make test-file runs, still fine" ok $?
run "$(bash_ev 'make done')"; check "the ordinary gate is not a measurement" ok $?
teardown

echo "5. the ESCAPE works, and is checked BEFORE the count"
setup
run "$(bash_ev 'make test-full')"; run "$(bash_ev 'make test-full')"
run "$(bash_ev 'make test-full  # MEASURE_OK: re-run after fixing the red this very measurement found')"; check "MEASURE_OK passes at the budget" ok $?
run "$(bash_ev 'make test-full')"; check "...and it reset the count, so the next one is fine too" ok $?
teardown

# GUARD_EDIT_OK: feature 161 - both sequences lose one run, for the same reason as section 1: at a
# budget of 1 the SECOND is the blocked one, and a third would be allowed again (the block clears the
# counter so it can never deadlock).
echo "6. FULL=1 counts too - it is the same expensive run"
setup
run "$(bash_ev 'make done FULL=1')"
run "$(bash_ev 'make done FULL=1')"; check "the second done FULL=1 is BLOCKED" blocked $?
teardown

echo "7. a MENTION is treated as a run (the stated limitation), and fails safe"
setup
run "$(bash_ev 'grep -rn \"make test-full\" docs/')"
run "$(bash_ev 'grep -rn \"make test-full\" docs/')"; check "a second mention blocks - the known false positive" blocked $?
run "$(bash_ev 'grep -rn \"make test-full\" docs/  # MEASURE_OK: a grep, not a run')"; check "...and MEASURE_OK clears it" ok $?
teardown

# GUARD_EDIT_OK: feature 161 - two NEW behaviors, both non-blocking: the reminder that arrives on the
# first run (so a session is told before it is ever refused) and the firing log that makes "is this
# guard worth what it costs" a total. Neither refuses anything that was not refused before.
echo "9. the REMINDER arrives on the FIRST successful measurement, not at the first failure"
setup
FIRST=$("$HOOK" pretool <<<"$(bash_ev 'make test-full')" 2>/dev/null)
printf '%s' "$FIRST" | grep -q '"additionalContext"' && { echo "  ok    the first run carries a reminder"; PASS=$((PASS+1)); } || { echo "  FAIL  no reminder on the first run"; FAIL=$((FAIL+1)); }
printf '%s' "$FIRST" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null && { echo "  ok    ...as valid JSON on stdout"; PASS=$((PASS+1)); } || { echo "  FAIL  the reminder is not valid JSON"; FAIL=$((FAIL+1)); }
printf '%s' "$FIRST" | grep -q 'make cov-file' && { echo "  ok    ...naming the command that answers the usual question"; PASS=$((PASS+1)); } || { echo "  FAIL  the reminder does not name make cov-file"; FAIL=$((FAIL+1)); }
SECOND=$("$HOOK" pretool <<<"$(bash_ev 'make test-full')" 2>/dev/null || true)
printf '%s' "$SECOND" | grep -q '"additionalContext"' && { echo "  FAIL  the reminder repeated on the blocked run"; FAIL=$((FAIL+1)); } || { echo "  ok    it is not repeated - a reminder that repeats is skimmed"; PASS=$((PASS+1)); }
CHEAP=$("$HOOK" pretool <<<"$(bash_ev 'make quick')" 2>/dev/null)
[ -z "$CHEAP" ] && { echo "  ok    the cheap loop gets no reminder at all"; PASS=$((PASS+1)); } || { echo "  FAIL  make quick was given a reminder"; FAIL=$((FAIL+1)); }
teardown

echo "10. every firing is RECORDED (feature 161)"
setup
GL=$(mktemp -d); export GUARD_LOG_DIR="$GL"
run "$(bash_ev 'make test-full')"                  # reminded
run "$(bash_ev 'make test-full')"                  # blocked
run "$(bash_ev 'make test-full  # MEASURE_OK: the record')"   # escaped
for want in reminded blocked escaped; do
  grep -lq "\"event\": \"$want\"" "$GL"/*.json 2>/dev/null && { echo "  ok    a $want entry was written"; PASS=$((PASS+1)); } || { echo "  FAIL  no $want entry in the guard log"; FAIL=$((FAIL+1)); }
done
grep -hq '"detail": "make test-full"' "$GL"/*.json 2>/dev/null && { echo "  ok    the entry records the command, parsed rather than greedily matched"; PASS=$((PASS+1)); } || { echo "  FAIL  the recorded detail is not the command"; FAIL=$((FAIL+1)); }
rm -rf "$GL"; unset GUARD_LOG_DIR
teardown

echo "11. a log that cannot be written never takes the guard down with it"
setup
export GUARD_LOG_DIR=/proc/nonexistent/guard-log
run "$(bash_ev 'make test-full')"; check "the first run still succeeds with an unwritable log" ok $?
run "$(bash_ev 'make test-full')"; check "...and the second is still blocked" blocked $?
unset GUARD_LOG_DIR
teardown

echo "8. status reports the count"
setup
run "$(bash_ev 'make test-full')"
"$HOOK" status <<<"$(bash_ev 'x')" | grep -q "measurements_since_reset=1" && { echo "  ok    status"; PASS=$((PASS+1)); } || { echo "  FAIL  status"; FAIL=$((FAIL+1)); }
teardown

echo
echo "measure-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
