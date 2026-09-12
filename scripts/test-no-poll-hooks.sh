#!/usr/bin/env bash
# Tests for no-poll-hooks.sh. Feeds the hook a PreToolUse payload for a Bash command and asserts
# whether it blocks. Run: scripts/test-no-poll-hooks.sh   (exit 0 = all green)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/no-poll-hooks.sh"
# GUARD_EDIT_OK: feature 164 - this guard RECORDS its firings now (feature 162's log), so the suite
# must write its fixtures to a throwaway directory. Without it the suite pollutes `make audit`, whose
# whole purpose is to price a guard from real firings: 24 fixture entries appeared there the first
# time these conversions ran their suites.
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
trap 'rm -rf "$GUARD_LOG_ROOT"' EXIT

PASS=0; FAIL=0

run() {  # feed a Bash command through the hook, return its exit code
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t1","tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$1" \
    | "$HOOK" pretool 2>/tmp/np.err
}

check() { # label, expected(ok|blocked), command
  run "$3" >/dev/null; local rc=$?
  if { [ "$2" = ok ] && [ "$rc" -eq 0 ]; } || { [ "$2" = blocked ] && [ "$rc" -ne 0 ]; }; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else
    echo "  FAIL    $1 (expected $2, rc=$rc)"; [ -s /tmp/np.err ] && sed 's/^/          /' /tmp/np.err; FAIL=$((FAIL+1))
  fi
}

echo "1. the exact 2026-07-25 bug and its relatives are blocked"
check "the real one: pgrep-self-match poll loop" blocked \
  'for i in $(seq 1 80); do if ! pgrep -f "make done" >/dev/null 2>&1; then break; fi; command sleep 5; done; tail -18 /tmp/out'
# GUARD_EDIT_OK: feature 164 - a STANDALONE self-matching pattern is now CORRECTED rather than
# refused (GM 2026-08-30), so these two vectors move from "blocked" to "rewritten, with the bracket".
# The loop above KEEPS its block, and that ordering is the point: the correction runs last, after the
# busy-wait refusals, because when it ran first it rewrote the original 2026-07-25 command and let
# the 10.9-minute busy-wait through. This suite caught that.
rewritten() { # label, command, the text the corrected command must contain
  out=$(run "$2" 2>/dev/null)
  got=$(printf '%s' "$out" | python3 -c 'import json,sys
try: print(json.load(sys.stdin)["hookSpecificOutput"]["updatedInput"]["command"])
except Exception: pass' 2>/dev/null)
  case "$got" in
    *"$3"*) echo "  ok      $1  ->  $got"; PASS=$((PASS+1)) ;;
    *) echo "  FAIL    $1 was not corrected (got '${got:-<nothing>}', wanted '$3')"; FAIL=$((FAIL+1)) ;;
  esac
}
rewritten "bare literal pattern is bracketed" 'pgrep -f "make done"' '[m]ake done'
rewritten "pkill literal pattern is bracketed" 'pkill -f "cherryd"' '[c]herryd'
# GUARD_EDIT_OK: feature 212 - a FOREGROUND file-watching wait is BACKGROUNDED now (section 5b), so
# the busy-wait vector here waits on something that is not a file
check "while + sleep busy-wait" blocked 'while ! nc -z localhost 8080; do sleep 2; done'
check "until + sleep busy-wait" blocked 'until curl -s localhost:8080 >/dev/null; do sleep 3; done'
check "for + sleep busy-wait" blocked 'for i in 1 2 3; do sleep 10; done'
check "command sleep (foreground-sleep guard bypass)" blocked 'command sleep 30'
check "/bin/sleep bypass" blocked '/bin/sleep 20'
check "env sleep bypass" blocked 'env sleep 15'
check "backslash-escaped sleep bypass" blocked '\sleep 12'

echo "2. the block explains the fault and the alternative"
# GUARD_EDIT_OK: feature 164 - the self-match is CORRECTED now, so its explanation travels as the
# rewrite's own context rather than as a refusal. The busy-wait block below still owes its message.
SELF=$(run 'pgrep -f "make done"' 2>/dev/null)
printf '%s' "$SELF" | grep -q "finds the searching shell itself" && { echo "  ok      the correction names the self-match fault"; PASS=$((PASS+1)); } || { echo "  FAIL    self-match not explained"; FAIL=$((FAIL+1)); }
printf '%s' "$SELF" | grep -q "Corrected rather than refused" && { echo "  ok      ...and says why it was corrected rather than refused"; PASS=$((PASS+1)); } || { echo "  FAIL    the correction does not say why"; FAIL=$((FAIL+1)); }
run 'while :; do sleep 5; done' >/dev/null
grep -q "completion notification" /tmp/np.err && { echo "  ok      a real busy-wait still points at the notification"; PASS=$((PASS+1)); } || { echo "  FAIL    no alternative offered"; FAIL=$((FAIL+1)); }
run 'while :; do sleep 5; done' >/dev/null
grep -q "POLL_OK" /tmp/np.err && { echo "  ok      documents the escape hatch"; PASS=$((PASS+1)); } || { echo "  FAIL    escape hatch not documented"; FAIL=$((FAIL+1)); }

# GUARD_EDIT_OK: feature 164 - A MENTION IS NOT AN INVOCATION. This guard refused four pieces of
# correct work in one session, every one of them a DOCUMENT about the guard: the command writing its
# own specification, a plan quoting the shapes, a set of test vectors, and the script that moved this
# very branch. `_hookmatch.py sanitize` blanks heredoc bodies and quoted strings before the patterns
# run, so text that TALKS about a busy-wait passes and one that RUNS it does not.
echo "2b. a MENTION is not an invocation (feature 164)"
check "a heredoc writing prose about a busy-wait" ok 'python3 - <<PY
print("a loop containing sleep 5 is a busy-wait; do not write one")
PY'
check "a heredoc naming the self-match shape" ok 'python3 - <<PY
text = "pgrep -f \"make done\" matches its own shell"
print(text)
PY'
check "a grep for the forbidden shape in the docs" ok 'grep -rn "while true; do sleep" docs/'
check "a commit message describing the fix" ok 'git commit -m "no-poll: a loop with sleep is refused, a literal pgrep -f is corrected"'
check "...but a REAL busy-wait beside a heredoc is still blocked" blocked 'python3 - <<PY
print("hello")
PY
while :; do sleep 5; done'

# GUARD_EDIT_OK: feature 165 - THE ONE WAIT THAT IS NOT A BUSY-WAIT (the GM ruling, 2026-08-30). A
# BACKGROUNDED loop watching a FILE is the harness own documented shape for a single completion
# notification, and the only way to wait on a run detached with `setsid --fork`. The boundary is
# CLOSED and narrower than the ruling words, because the GM was offered "permit whenever
# backgrounded" and declined it as usable for a general bypass - so these vectors carry the
# discriminating cases `spec-fidelity` demanded, not just the happy one.
echo "5. the detached-run wait, and nothing wider (feature 165)"
bgrun() {  # feed a Bash command with run_in_background set, return the exit code
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t1","tool_name":"Bash","tool_input":{"command":sys.argv[1],"run_in_background":sys.argv[2]=="1"}}))' "$1" "$2" \
    | "$HOOK" pretool 2>/tmp/np.err
}
bgcheck() { # label, expected, command, background(1|0)
  bgrun "$3" "$4" >/dev/null; local rc=$?
  if { [ "$2" = ok ] && [ "$rc" -eq 0 ]; } || { [ "$2" = blocked ] && [ "$rc" -ne 0 ]; }; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else
    echo "  FAIL    $1 (expected $2, rc=$rc)"; FAIL=$((FAIL+1))
  fi
}
bgcheck "a backgrounded watch on a log file" ok "until grep -q 'gate green' /tmp/gate.log; do sleep 10; done" 1
bgcheck "a backgrounded file test" ok "until [ -s /tmp/gate.log ]; do sleep 5; done" 1
# GUARD_EDIT_OK: feature 212 - the qualifier reads the permitted shape the way the record writes it
# (a `|` inside the quoted regex, a `$S/` path, a `2>/dev/null`, `[ -s f ] && grep`): seven of the
# eight real backgrounded waits in the record were refused by the raw reading. The boundary is the
# GM's from feature 165, unchanged - a substitution inside quotes, an output file, a network or a
# process wait all still fail it, and the every-part rule is TIGHTER than the whole-condition search.
bgcheck "the corpus shape: a | inside the quoted regex" ok 'until grep -qE "gate green|GATE FAILED|EXIT=" /tmp/161-done2.log; do sleep 5; done; tail -3 /tmp/161-done2.log' 1
bgcheck "the corpus shape: a variable in front of the path" ok 'until grep -qE "[0-9]+ (passed|failed|error)" $S/test-full.log; do sleep 5; done' 1
bgcheck "the corpus shape: stderr discarded" ok 'until grep -q DONE-BASELINE /tmp/x/baseline.log 2>/dev/null; do sleep 10; done; echo BASELINE-COMPLETE' 1
bgcheck "the corpus shape: a file test AND a grep" ok 'until [ -s /tmp/t/b.output ] && grep -qE "^real|passed|failed" /tmp/t/b.output; do sleep 5; done' 1
bgcheck "a quoted path is still a path" ok 'until grep -q "gate green" "$S/gate.log"; do sleep 10; done' 1
bgcheck "a substitution INSIDE quotes still disqualifies" blocked 'until grep -q "$(curl -s https://h/x)" /tmp/f; do sleep 5; done' 1
bgcheck "a file test AND a network call (every part must qualify)" blocked 'until [ -f x ] && curl -sf https://h; do sleep 5; done' 1
bgcheck "a backtick in the condition" blocked 'until grep -q x `cat f`; do sleep 5; done' 1
# GUARD_EDIT_OK: feature 212 - THE FOREGROUND FORM IS BACKGROUNDED, NOT REFUSED (GM 2026-09-07): the
# permitted shape is this command with run_in_background set, so the hook sets it and says so.
backgrounded() { # label, command
  local out; out=$(bgrun "$2" 0 2>/dev/null); local rc=$?
  local flag; flag=$(printf '%s' "$out" | python3 -c 'import json,sys
try: print(json.load(sys.stdin)["hookSpecificOutput"]["updatedInput"]["run_in_background"])
except Exception: print("")' 2>/dev/null)
  if [ "$rc" -eq 0 ] && [ "$flag" = "True" ] && printf '%s' "$out" | grep -q "BACKGROUNDED"; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else
    echo "  FAIL    $1 (rc=$rc, run_in_background='${flag:-<unset>}')"; FAIL=$((FAIL+1))
  fi
}
backgrounded "the SAME watch in the foreground is backgrounded and told" "until grep -q 'gate green' /tmp/gate.log; do sleep 10; done"
backgrounded "...with what follows the loop kept" "until grep -q x /tmp/a.log; do sleep 5; done; tail /tmp/a.log"
backgrounded "the file-test form, foreground" 'while [ ! -f /tmp/done ]; do sleep 2; done'
bgcheck "a foreground NETWORK wait is still refused" blocked "until curl -sf https://host/x; do sleep 5; done" 0
bgcheck "a foreground PROCESS wait is still refused" blocked "until pgrep -f '[m]ake done'; do sleep 5; done" 0
bgcheck "a backgrounded NETWORK wait" blocked "until curl -sf https://host/x; do sleep 5; done" 1
bgcheck "...even with an output redirect (a redirect is not a file read)" blocked "until curl -sf https://host/x > /tmp/out; do sleep 5; done" 1
bgcheck "a backgrounded PROCESS check through a pipe" blocked "until ps aux | grep -q make; do sleep 5; done" 1
bgcheck "a command substitution in the condition" blocked "until [ -n \"\$(pgrep -f make)\" ]; do sleep 5; done" 1
bgcheck "an output redirect on an otherwise real file watch" blocked "until grep -q x /tmp/a.log >/dev/null; do sleep 5; done" 1
bgcheck "a disguised bare sleep, backgrounded" blocked "command sleep 30" 1

echo "3. legitimate commands are NOT blocked (no false positives)"
check "the gate itself" ok 'make done'
check "pytest" ok 'python3 -m pytest test_settlement.py -n auto'
check "a loop with no sleep" ok 'while read -r line; do echo "$line"; done < /tmp/f'
check "a for loop over maps, regenerating each" ok 'for g in a b c; do python3 $g.gen.py && python3 -m check_village $g.json; done'
check "pgrep with the bracket trick" ok "pgrep -f '[m]ake done'"
check "pgrep -f on a variable pattern" ok 'pgrep -f "$PATTERN"'
check "pgrep without -f (matches process NAME, not the command line)" ok 'pgrep resvg'
check "running a script that happens to sleep internally" ok 'scripts/test-clone-sync-hooks.sh'
check "timeout wrapping a real command" ok 'timeout 60 ./slow-thing.sh'
check "git" ok 'git log --oneline -1'
check "a word merely containing sleep" ok 'grep -rn "sleepy" .'
check "the word sleep inside a string, not invoked" ok 'echo "do not sleep 5 here"'

echo "4. the escape hatch works for genuine external waits"
check "POLL_OK allows a real port wait" ok '# POLL_OK: waiting for the dev server port to open
until curl -s localhost:8080 >/dev/null; do sleep 2; done'
check "POLL_OK allows a bare sleep bypass" ok 'command sleep 5  # POLL_OK: external deploy settling'

# GUARD_EDIT_OK: GM 2026-09-08 - THE ESCAPE DOES NOT SKIP THE SELF-MATCH CORRECTION. The real one: a
# waiter on a detached `make page-check`, escaped with POLL_OK because it read the run's log, whose
# exit condition ALSO asked `! pgrep -f "make page-check"` - which matched the waiter's own shell, so
# the loop ran for hours on a gate that had finished in 7 s. The escape used to exit before the
# correction ran. Now the wait is permitted AND the pattern is bracketed, and both are recorded.
echo "4b. an escaped wait still gets the self-match correction"
ESCAPED_SELF='true POLL_OK waits on the detached page-check gate writing its log; L=/tmp/pc.log; until grep -qE "passed|failed" $L 2>/dev/null && ! pgrep -f "make page-check" >/dev/null; do sleep 5; done; tail -6 $L'
rewritten "the 2026-09-08 waiter: escaped AND bracketed" "$ESCAPED_SELF" '[m]ake page-check'
# GUARD_EDIT_OK: 2026-09-08 - both entries land: the escape (rule poll-ok) and the rewrite
if grep -rlq 'poll-ok' "$GUARD_LOG_ROOT" && grep -rlq 'escaped-self-match' "$GUARD_LOG_ROOT"; then
  echo "  ok      the escaped-and-corrected wait records both the escape and the rewrite"; PASS=$((PASS+1))
else
  echo "  FAIL    the escaped-and-corrected wait did not record both entries"; FAIL=$((FAIL+1))
fi
check "an escaped wait with a bracketed pattern is untouched" ok 'until ! pgrep -f "[m]ake done" >/dev/null; do sleep 5; done  # POLL_OK: a run detached by another session'
rewritten "two literal patterns are BOTH bracketed" 'pgrep -f "make done"; pgrep -f "make quick"' '[m]ake quick'
rewritten "...and the first of them too" 'pgrep -f "make done"; pgrep -f "make quick"' '[m]ake done'

# GUARD_EDIT_OK: feature 227 (GM 2026-09-12) - THE WAIT GETS A PROOF OF LIFE, and the shape that already
# carries one stops being refused. The incident: a detached `make placement-stages` finished its work and was
# then killed before it could flush stdout - by the kernel's OOM killer, 36 firings in this container - and
# the waiter sat on a pattern that was never going to be printed. The GM: *"the hook should add the second
# proof of life check to what is being waited for"*, because *"simply telling you to set a watch properly next
# time is bad engineering practice."*
echo "6. the proof of life (feature 227)"
bgrewritten() { # label, command, background(1|0), the text the corrected command must contain
  local out; out=$(bgrun "$2" "$3" 2>/dev/null)
  local got; got=$(printf '%s' "$out" | python3 -c 'import json,sys
try: print(json.load(sys.stdin)["hookSpecificOutput"]["updatedInput"]["command"])
except Exception: pass' 2>/dev/null)
  case "$got" in
    *"$4"*) echo "  ok      $1"; PASS=$((PASS+1)) ;;
    *) echo "  FAIL    $1 (got '${got:-<nothing>}', wanted '$4')"; FAIL=$((FAIL+1)) ;;
  esac
}
untouched() { # label, command, background(1|0) - permitted with NO rewrite at all
  local out; out=$(bgrun "$2" "$3" 2>/dev/null); local rc=$?
  if [ "$rc" -eq 0 ] && ! printf '%s' "$out" | grep -q updatedInput; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else
    echo "  FAIL    $1 (rc=$rc, out='${out:-<nothing>}')"; FAIL=$((FAIL+1))
  fi
}
bgrewritten "a backgrounded log watch gains the liveness clause" \
  'until grep -qE "^wrote |Error|Traceback" /tmp/stages.log; do sleep 15; done; tail -5 /tmp/stages.log' 1 '_writer-alive.sh "/tmp/stages.log"'
bgrewritten "...an UNTIL loop gets it negated, so the wait ends when the writer is gone" \
  'until grep -q DONE /tmp/a.log; do sleep 5; done' 1 '|| ! '
bgrewritten "...a WHILE loop gets it ANDed, for the same reason in the other direction" \
  'while [ ! -s /tmp/a.log ]; do sleep 5; done' 1 '&& '
bgrewritten "the variable form names the variable, which expands when the loop runs" \
  'until grep -qE "passed|failed" $S/gate.log; do sleep 10; done' 1 '_writer-alive.sh "$S/gate.log"'
bgrewritten "a foreground one is backgrounded AND proofed in one rewrite" \
  'until grep -q x /tmp/a.log; do sleep 5; done' 0 '_writer-alive.sh'
# THE SHAPE THIS GUARD SHOULD BE PRODUCING WAS THE SHAPE IT REFUSED. Measured 2026-09-12: this exact command,
# a log watch that also asks whether the producer is alive, was BLOCKED as a busy-wait, because every part of
# a condition had to be one of the three file forms. A liveness clause can only end the loop sooner.
untouched "a wait that already asks whether its producer is alive is permitted, unchanged" \
  'until grep -q "^EXIT=" $S/maps.log || ! pgrep -f "ma[p]s227b" > /dev/null; do sleep 15; done; tail -6 $S/maps.log' 1
untouched "...the same, through the helper itself (idempotent: the hook does not re-proof its own rewrite)" \
  'until grep -q DONE /tmp/a.log || ! /diagram/scripts/_writer-alive.sh "/tmp/a.log"; do sleep 5; done' 1
untouched "...and the kill -0 form" 'until grep -q DONE /tmp/a.log || ! kill -0 $PID; do sleep 5; done' 1
# GUARD_EDIT_OK: feature 227 - the log's whole name may be a VARIABLE (`grep -qE "pat" $G`), which the path operand
# did not admit; caught by the guard refusing a correct waiter on a detached gate's log on 2026-09-12.
bgrewritten "a log named entirely by a variable is a file wait, and is proofed" \
  'until grep -qE "passed|failed" $G; do sleep 20; done' 1 '_writer-alive.sh "$G"'
bgcheck "...but a grep with nothing to read (stdin) is not a file wait" blocked 'until grep -q $PAT; do sleep 5; done' 1
bgcheck "a loop with ONLY a liveness test is still a process wait, and refused" blocked \
  'until ! pgrep -f "[m]ake done"; do sleep 5; done' 1
bgcheck "a liveness test beside a NETWORK call is still refused" blocked \
  'until curl -sf https://h/x || ! pgrep -f "[m]ake done"; do sleep 5; done' 1

echo "6b. _writer-alive.sh answers from the file, not from a pattern"
alive() { # label, expected(alive|dead), args...
  local lbl="$1" want="$2"; shift 2
  "$HERE/_writer-alive.sh" "$@" >/dev/null 2>&1; local rc=$?
  if { [ "$want" = alive ] && [ "$rc" -eq 0 ]; } || { [ "$want" = dead ] && [ "$rc" -ne 0 ]; }; then
    echo "  ok      $lbl"; PASS=$((PASS+1))
  else
    echo "  FAIL    $lbl (expected $want, rc=$rc)"; FAIL=$((FAIL+1))
  fi
}
WA_DIR=$(mktemp -d)
alive "nothing named: no claim either way" alive
alive "a file that does not exist yet: the producer is starting" alive "$WA_DIR/not-yet.log"
: > "$WA_DIR/fresh.log"
alive "a file just written: alive on the staleness belt" alive "$WA_DIR/fresh.log"
touch -d "2 hours ago" "$WA_DIR/fresh.log"
alive "...unheld and long unwritten: the producer is gone" dead "$WA_DIR/fresh.log"
# a process holding it open says ALIVE even when the file has not been written for ages - this is the branch
# that answers for every detached run in this repository, since `cmd > log` holds that descriptor throughout
( exec 9>>"$WA_DIR/fresh.log"; "$HERE/_writer-alive.sh" "$WA_DIR/fresh.log" >/dev/null 2>&1 ) && \
  { echo "  ok      a process holding it open: alive"; PASS=$((PASS+1)); } || \
  { echo "  FAIL    a process holding it open should read alive"; FAIL=$((FAIL+1)); }
rm -rf "$WA_DIR"

echo
echo "no-poll-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
