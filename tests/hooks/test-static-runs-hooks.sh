#!/usr/bin/env bash
# Tests for static-runs-hooks (feature 451 T14, FR-007, plan D11): a task's third `make static` since its last landing that went out,
# or since its first start, is refused naming the crate-scoped checks; STATIC_OK="<reason>" escapes, recorded.
# Run: tests/hooks/test-static-runs-hooks.sh   (exit 0 = all green)
#
# Every case drives the REAL guard (through the shim, `l7r-guard --only static-runs-hooks PreToolUse`) with a REAL payload against a
# fixture clone: its `.git/task-starts.jsonl` and its feature's event log, the lines the event log writer and `make land` write.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/static-runs-hooks.sh"
PASS=0; FAIL=0
T=$(mktemp -d); export GUARD_LOG_DIR="$T/guard-log"
unset L7R_EVENTS_DIR L7R_FEATURE_DIRECTORY SPECIFY_FEATURE
trap 'rm -rf "$T"' EXIT

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

C="$T/clone"; F=451-x; LOG="$C/.git/l7r-events/$F.jsonl"
mkdir -p "$C/.git/l7r-events" "$C/specs/$F" "$C/.specify"
printf '{"feature_directory": "specs/%s"}\n' "$F" > "$C/.specify/feature.json"

starts() { : > "$C/.git/task-starts.jsonl"; for s in "$@"; do printf '{"feature": "%s", "task": "%s", "utc": "%s"}\n' "$F" "${s%@*}" "${s#*@}" >> "$C/.git/task-starts.jsonl"; done; }
fresh() { : > "$LOG"; }
ran() {  # ran <id> <time> [task]: a make static call that ran
  printf '{"t":"%s","ev":"PreToolUse","tool":"Bash","id":"%s","make":"static","task":"%s"}\n' "$2" "$1" "${3:-T06}" >> "$LOG"
  printf '{"t":"%s","ev":"PostToolUse","tool":"Bash","id":"%s","make":"static","task":"%s"}\n' "$2" "$1" "${3:-T06}" >> "$LOG"
}
landing() {  # landing <time> <landed> <code> <tasks json>: make land's end line
  printf '{"ev":"Phase","src":"land","step":"end","t":"%s","code":%s,"make":"land","tasks":%s,"landed":%s}\n' "$1" "$3" "$4" "$2" >> "$LOG"
}
run() {  # run <command>: OUT and RC
  OUT=$(jq -nc '{"hook_event_name":"PreToolUse","session_id":"t","tool_name":"Bash","tool_use_id":"toolu_now","cwd":$ARGS.positional[1],"tool_input":{"command":$ARGS.positional[0]}}' --args -- "$1" "$C" \
        | "$HOOK" pretool 2>&1); RC=$?
}

echo "1. the third run since the task's first start is refused, naming the crate-scoped checks"
starts T06@2026-11-20T10:00:00Z; fresh
ran a 2026-11-20T10:01:00.000Z
run "make static"
[ "$RC" -eq 0 ] && ok "one run before: the second passes" || no "the second run refused" "(rc=$RC: $OUT)"
ran b 2026-11-20T10:02:00.000Z
run "make static"
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q 'T06 of 451-x has run `make static` 2 times' && ok "two runs before: the third is refused" || no "the third passed" "(rc=$RC: $OUT)"
printf '%s' "$OUT" | grep -q 'make quick' && printf '%s' "$OUT" | grep -q 'STATIC_OK="<reason>"' && ok "...naming the edit loop (no crate in this delta) and the escape" || no "the refusal names no check" "($OUT)"
ls "$GUARD_LOG_DIR" 2>/dev/null | grep -q . && ok "...and the firing is logged" || no "no guard-log record"
run "make rust-test CRATE=rust/guard && make static"
[ "$RC" -eq 2 ] && ok "a make static after another target is read" || no "the second target passed" "(rc=$RC)"

echo "2. a landing that went out starts the count again, whatever its exit code; a refused one does not"
fresh; ran a 2026-11-20T10:01:00.000Z; ran b 2026-11-20T10:02:00.000Z
landing 2026-11-20T10:03:00.000Z true 3 '["T06"]'
run "make static"
[ "$RC" -eq 0 ] && ok "after an exit-3 landing whose push went out (landed true): passes" || no "an exit-3 landing did not count" "(rc=$RC: $OUT)"
fresh; ran a 2026-11-20T10:01:00.000Z; ran b 2026-11-20T10:02:00.000Z
landing 2026-11-20T10:03:00.000Z true 0 '["T18","T06","T30"]'
run "make static"
[ "$RC" -eq 0 ] && ok "after a batch landing naming the task second: passes" || no "a batch landing did not count" "(rc=$RC)"
fresh; ran a 2026-11-20T10:01:00.000Z; ran b 2026-11-20T10:02:00.000Z
landing 2026-11-20T10:03:00.000Z false 0 '["T06"]'
run "make static"
[ "$RC" -eq 2 ] && ok "after a refused landing (landed false, exit 0): refused" || no "a refused landing reset the count" "(rc=$RC)"
landing 2026-11-20T10:04:00.000Z false 1 '["T06"]'
run "make static"
[ "$RC" -eq 2 ] && ok "after a refused landing (landed false, exit 1): refused" || no "a failed landing reset the count" "(rc=$RC)"

echo "3. a later task-start resets nothing; a run before the first start is not counted"
starts T06@2026-11-20T10:00:00Z T06@2026-11-20T10:03:00Z; fresh
ran a 2026-11-20T10:01:00.000Z; ran b 2026-11-20T10:02:00.000Z
run "make static"
[ "$RC" -eq 2 ] && ok "two runs, a second task-start, a third: refused" || no "a second task-start reset the count" "(rc=$RC)"
starts T06@2026-11-20T10:00:00Z; fresh
ran old 2026-11-20T09:59:00.000Z; ran a 2026-11-20T10:01:00.000Z
run "make static"
[ "$RC" -eq 0 ] && ok "a run before the first start is not counted" || no "a run before the start counted" "(rc=$RC)"

echo "4. only the task's runs that ran count"
fresh; ran a 2026-11-20T10:01:00.000Z; ran x 2026-11-20T10:01:30.000Z T07
printf '{"t":"2026-11-20T10:02:00.000Z","ev":"PreToolUse","tool":"Bash","id":"refused","make":"static","task":"T06"}\n' >> "$LOG"
run "make static"
[ "$RC" -eq 0 ] && ok "another task's run and a call refused by another guard are not counted" || no "they counted" "(rc=$RC)"

echo "5. the escape"
fresh; ran a 2026-11-20T10:01:00.000Z; ran b 2026-11-20T10:02:00.000Z
before=$(ls "$GUARD_LOG_DIR" | wc -l)
run 'STATIC_OK="the landing gate needs it" make static'
[ "$RC" -eq 0 ] && ok "STATIC_OK with a reason passes" || no "the escape was refused" "(rc=$RC: $OUT)"
[ "$(ls "$GUARD_LOG_DIR" | wc -l)" -gt "$before" ] && grep -lq 'the landing gate needs it' "$GUARD_LOG_DIR"/* && ok "...and is recorded" || no "the escape left no record"
run "make static STATIC_OK"
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q 'STATIC_OK with no reason' && ok "a bare STATIC_OK is refused" || no "a bare escape passed" "(rc=$RC)"

echo "6. a mention is not a run; a call with no task passes"
for cmd in "grep static Makefile" "echo 'make static'" "make quick"; do
  run "$cmd"; [ "$RC" -eq 0 ] || no "'$cmd' refused" "(rc=$RC)"
done
ok "a mention or another target passes"
starts; fresh; ran a 2026-11-20T10:01:00.000Z; ran b 2026-11-20T10:02:00.000Z
rm -f "$C/.git/task-starts.jsonl"
run "make static"
[ "$RC" -eq 0 ] && ok "a call whose line carries no task passes" || no "a call with no task refused" "(rc=$RC)"

echo
echo "static-runs-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
