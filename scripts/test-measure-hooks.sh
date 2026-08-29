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

echo "1. THE MOTIVATING CASE: measure, write one test, measure, write one test, measure"
setup
run "$(bash_ev 'make test-full')"; check "the first measurement is allowed" ok $?
run "$(edit_ev '/diagram/.claude/skills/diagram/tests/settlement/test_geom.py')"
run "$(bash_ev 'make test-full')"; check "the second is allowed (a before/after pair is legitimate)" ok $?
run "$(edit_ev '/diagram/.claude/skills/diagram/tests/settlement/test_geom.py')"
run "$(bash_ev 'make test-full')"; check "the THIRD is BLOCKED" blocked $?
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

echo "6. FULL=1 counts too - it is the same expensive run"
setup
run "$(bash_ev 'make done FULL=1')"; run "$(bash_ev 'make done FULL=1')"
run "$(bash_ev 'make done FULL=1')"; check "the third done FULL=1 is BLOCKED" blocked $?
teardown

echo "7. a MENTION is treated as a run (the stated limitation), and fails safe"
setup
run "$(bash_ev 'grep -rn \"make test-full\" docs/')"; run "$(bash_ev 'grep -rn \"make test-full\" docs/')"
run "$(bash_ev 'grep -rn \"make test-full\" docs/')"; check "a third mention blocks - the known false positive" blocked $?
run "$(bash_ev 'grep -rn \"make test-full\" docs/  # MEASURE_OK: a grep, not a run')"; check "...and MEASURE_OK clears it" ok $?
teardown

echo "8. status reports the count"
setup
run "$(bash_ev 'make test-full')"
"$HOOK" status <<<"$(bash_ev 'x')" | grep -q "measurements_since_reset=1" && { echo "  ok    status"; PASS=$((PASS+1)); } || { echo "  FAIL  status"; FAIL=$((FAIL+1)); }
teardown

echo
echo "measure-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
