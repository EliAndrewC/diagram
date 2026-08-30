#!/usr/bin/env bash
# Tests for gate-hooks.sh. Feeds PreToolUse events and asserts when `make done` is blocked.
# Run: scripts/test-gate-hooks.sh   (exit 0 = all green)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/gate-hooks.sh"
PASS=0; FAIL=0

setup() { STATE_DIR=$(mktemp -d); export GATE_STATE_DIR="$STATE_DIR"; }
teardown() { rm -rf "$STATE_DIR"; }

bash_ev() { printf '{"session_id":"g1","tool_name":"Bash","tool_input":{"command":"%s"}}' "$1"; }
edit_ev() { printf '{"session_id":"g1","tool_name":"Edit","tool_input":{"file_path":"%s"}}' "$1"; }
run()  { "$HOOK" pretool <<<"$1" 2>/tmp/gt.err; }

check() { # label expected(ok|blocked) rc
  if { [ "$2" = ok ] && [ "$3" -eq 0 ]; } || { [ "$2" = blocked ] && [ "$3" -ne 0 ]; }; then
    echo "  ok    $1"; PASS=$((PASS+1))
  else
    echo "  FAIL  $1 (expected $2, rc=$3)"; [ -s /tmp/gt.err ] && sed 's/^/        /' /tmp/gt.err; FAIL=$((FAIL+1))
  fi
}

echo "1. THE MOTIVATING CASE: a -k subset, then the gate"
setup
run "$(bash_ev 'python3 -m pytest test_settlement.py -q -n auto --no-cov -k \"kura_side or punishment\"')"; check "the subset run itself is allowed" ok $?
run "$(bash_ev 'make done')"; check "make done BLOCKED after a subset-only run" blocked $?
grep -q "WHOLE test file" /tmp/gt.err && { echo "  ok    message says what to run instead"; PASS=$((PASS+1)); } || { echo "  FAIL  message unhelpful"; FAIL=$((FAIL+1)); }
run "$(bash_ev 'make done')"; check "re-issuing the gate goes through (blocks once, no deadlock)" ok $?
teardown

echo "2. a WHOLE-FILE run clears the flag"
setup
run "$(bash_ev 'pytest test_settlement.py -k foo')"
run "$(bash_ev 'python3 -m pytest test_settlement.py test_checks.py -q -n auto --no-cov')"
run "$(bash_ev 'make done')"; check "gate allowed after the whole file ran" ok $?
teardown

echo "3. an EDIT after a subset run clears the flag (the run predates the code)"
setup
run "$(bash_ev 'pytest test_settlement.py -k foo')"
run "$(edit_ev '/gm-assistant/.clones/x/.claude/skills/diagram/settlement.py')"
run "$(bash_ev 'make done')"; check "gate allowed - the stale subset cannot vouch either way" ok $?
teardown

echo "4. no local test run at all: the hook has no opinion"
setup
run "$(bash_ev 'make done')"; check "gate allowed (docs-only diffs must not be blocked)" ok $?
teardown

echo "5. the GATE_OK escape hatch"
setup
run "$(bash_ev 'pytest test_settlement.py -k foo')"
run "$(bash_ev 'make done  # GATE_OK: docs-only since the subset run')"; check "GATE_OK passes" ok $?
run "$(bash_ev 'make done')"; check "...and clears the flag" ok $?
teardown

echo "6. non-Python edits do not clear the flag (a .md edit is not a code change)"
setup
run "$(bash_ev 'pytest test_settlement.py -k foo')"
run "$(edit_ev '/gm-assistant/.clones/x/docs/iteration-loop.md')"
run "$(bash_ev 'make done')"; check "still blocked" blocked $?
teardown

echo "7. sessions are independent"
setup
run "$(bash_ev 'pytest test_settlement.py -k foo')"
"$HOOK" pretool <<<'{"session_id":"other","tool_name":"Bash","tool_input":{"command":"make done"}}' 2>/dev/null
check "another session is unaffected" ok $?
teardown

# GUARD_EDIT_OK: feature 162 - the REFUSAL IS RETIRED and its two vectors go with it, deleted rather
# than left passing vacuously (GM 2026-08-30: *"does that mean our tooling should detect when both are
# being run and then combine them into `make done` automatically instead of rejecting?"*). Measured
# cause: 37 firings of that refusal, 23 escaped with GATE_OK in the very next call, to save one warm
# `make quick`. What replaces it is a REWRITE, and what it must never do is guess - so the vectors
# below check both halves: the shapes it rebuilds, and the shapes it leaves alone.
echo "8. quick and done in one command are COMBINED, not rejected (GM 2026-08-30)"
setup
rewrote() { # command, expected rewritten command
  got=$("$HOOK" pretool <<<"$(bash_ev "$1")" 2>/dev/null | python3 -c 'import json,sys
try: print(json.load(sys.stdin)["hookSpecificOutput"]["updatedInput"]["command"])
except Exception: pass' 2>/dev/null)
  if [ "$got" = "$2" ]; then echo "  ok    $1  ->  $2"; PASS=$((PASS+1));
  else echo "  FAIL  $1  ->  ${got:-<nothing>}  (expected $2)"; FAIL=$((FAIL+1)); fi
}
untouched() { # a command the rewrite must NOT touch
  got=$("$HOOK" pretool <<<"$(bash_ev "$1")" 2>/dev/null)
  if printf '%s' "$got" | grep -q updatedInput; then echo "  FAIL  rewrote a command it should have left alone: $1"; FAIL=$((FAIL+1));
  else echo "  ok    left alone: $1"; PASS=$((PASS+1)); fi
}
rewrote 'make quick && make done' 'make done'
rewrote 'make quick done' 'make done'
rewrote 'make quick 2>&1 | tail -2; make done 2>&1 | tail -2' 'make done 2>&1 | tail -2'
rewrote 'make done 2>&1 | tail -1 && make quick' 'make done 2>&1 | tail -1'
rewrote 'cd /x && make quick ALL=1 && make done' 'cd /x && make done'
rewrote '( cd /x/.claude/skills/diagram && make quick && make done )' '( cd /x/.claude/skills/diagram && make done )'
rewrote 'make -C /x quick && make -C /x done' 'make -C /x done'
untouched 'make quick'
untouched 'make done'
untouched 'make -C done quick'   # `-C`'s ARGUMENT is not a goal; this call names one target, not two
untouched 'GATE_OK: comparing the two; make quick; make done'
run "$(bash_ev 'make quick 2>&1 | tail -2; make done 2>&1 | tail -2')"; check "...and nothing is refused any more" ok $?
run "$(bash_ev 'make quick')"; check "quick alone ok" ok $?
run "$(bash_ev 'make done')"; check "done alone ok" ok $?
teardown

echo "8b. the rewrite is RECORDED, and never fires on a mention (feature 162)"
setup
GL=$(mktemp -d); export GUARD_LOG_DIR="$GL"
run "$(bash_ev 'make quick && make done')"
grep -lq '"event": "rewrote"' "$GL"/*.json 2>/dev/null && { echo "  ok    a rewrote entry was written"; PASS=$((PASS+1)); } || { echo "  FAIL  the rewrite was not recorded"; FAIL=$((FAIL+1)); }
rm -rf "$GL"; unset GUARD_LOG_DIR
untouched 'grep -n "make quick.*make done" docs/iteration-loop.md'
untouched 'git commit -m "make quick while iterating, make done once at the end"'
untouched 'echo "make quick; make done" > /tmp/notes.txt'
teardown

echo "9. a MENTION is not an INVOCATION (GM 2026-08-29: the small follow-up)"
# Six pieces of correct work were blocked in one day by substring matching: a script ANALYSING how often
# the two targets had run, a plan document quoting them, this file twice, and the command that fixed it.
setup
run "$(bash_ev 'python3 - <<PY
print("counting the make quick and make done runs in the transcript")
PY')"; check "a heredoc that talks about both targets" ok $?
run "$(bash_ev 'grep -n "make quick.*make done" docs/iteration-loop.md')"; check "a quoted grep for both" ok $?
run "$(bash_ev 'git commit -m "make quick while iterating, make done once at the end"')"; check "a commit message quoting both" ok $?
run "$(bash_ev 'echo "make quick; make done" > /tmp/notes.txt')"; check "writing them into a file as text" ok $?
teardown
# a pytest MENTION must not arm the subset flag either - the seventh false positive of the day was this
# file's own vectors (a quoted `-k foo`) arming a block for a run nobody made
setup
run "$(bash_ev 'python3 - <<PY
print("the vector reads: pytest tests/test_x.py -k foo")
PY')"
run "$(bash_ev 'make done')"; check "a pytest mention does not arm the subset block" ok $?
teardown
# ...and the real thing is still caught, with the flag machinery untouched
setup
run "$(bash_ev 'pytest tests/test_x.py -k foo')"
run "$(bash_ev 'echo "make done is what I will run next"')"; check "a mention does not consume the subset block" ok $?
run "$(bash_ev 'make done')"; check "...and the real gate is still blocked once" blocked $?
teardown

echo
if [ "$FAIL" -eq 0 ]; then echo "test-gate-hooks: all $PASS checks passed"; exit 0; fi
echo "test-gate-hooks: $FAIL FAILED, $PASS passed"; exit 1
