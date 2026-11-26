#!/usr/bin/env bash
# Tests for the set-down guard (rust/guard, replayed through its link) - a feature is worked until it is set down (feature 385 T70, plan D89/D90).
# Run: tests/hooks/test-set-down-hooks.sh   (exit 0 = all green)
#
# Each case drives the REAL hook - a Stop payload through the idle check (451 T183) (`cwd`, `transcript_path`) on a fixture clone: its `task-starts.jsonl`,
# a feature's `tasks.md`, and a transcript in the harness's JSONL form, whose background launches and task notifications say
# what is still running.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/seen.sh"  # seen VAR <grep args>: a run's text grepped from a here-string, never a pipe (451 T253)
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/set-down-hooks.sh"
SETDOWN="$HERE/../../scripts/gates/l7r-gate.sh"  # `l7r-gate set-down`, set-down.py's port (feature 449 T135)
T=$(mktemp -d)
GUARD_LOG_DIR="$T/log"; export GUARD_LOG_DIR
USAGE_CAP_DIR="$T/cap"; export USAGE_CAP_DIR  # never the real session's cap
trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
C="$T/clone"; mkdir -p "$C/specs/385-x"; git -C "$C" init -q
G="$C/.git"
printf -- '- [x] T01 done\n- [ ] T02 the next thing\n- [ ] GM review (make gm-reviewed F=385)\n' > "$C/specs/385-x/tasks.md"
: > "$T/tr.jsonl"
stop() { printf '{"cwd": "%s", "transcript_path": "%s"}' "$C" "$T/tr.jsonl" | SET_DOWN_ROOT="$C" "$HOOK" stop 2>"$T/err"; echo $?; }
line() { jq -nc '{"type": "user", "message": {"content": $ARGS.positional[0]}}' --args -- "$1" >> "$T/tr.jsonl"; }

echo "1. silent where no feature was begun"
[ "$(stop)" = 0 ] && ok "no task-start: the turn ends" || no "no task-start"

echo "2. an open task, nothing running, not set down: refused, naming the next task and make set-down"
printf '{"feature": "385-x", "task": "T02", "utc": "2026-10-18T23:00:00Z"}\n' > "$G/task-starts.jsonl"
rc=$(stop)
[ "$rc" = 2 ] && grep -q "T02 the next thing" "$T/err" && grep -q 'make set-down F=385 WHY=' "$T/err" && ok "refused with the next step" || no "refused" "rc=$rc $(cat "$T/err")"
ls "$GUARD_LOG_DIR" >/dev/null 2>&1 && ok "the refusal is recorded in the guard log" || no "guard log"

echo "3. work still running lets the turn end; reported back, it does not"
launch() { jq -nc '{"type": "user", "message": {"content": [{"type": "tool_result", "content": $ARGS.positional[1]}]}, "toolUseResult": {($ARGS.positional[0]): $ARGS.positional[2]}}' --args -- "$1" "$2" "$3" >> "$T/tr.jsonl"; }
launch backgroundTaskId "Command running in background with ID: b1abc. Output is being written to: x" b1abc
[ "$(stop)" = 0 ] && ok "a background command not reported back" || no "background running"
line "<task-notification><task-id>b1abc</task-id><status>completed</status></task-notification>"
[ "$(stop)" = 2 ] && ok "reported back: refused again" || no "reported back"
launch agentId "Async agent launched successfully. agentId: a9f00 (internal ID)" a9f00
[ "$(stop)" = 0 ] && ok "an async agent not reported back" || no "agent running"
line "<task-id>a9f00</task-id>"
launch backgroundTaskId "Command running in background with ID: b2stop. Output is being written to: x" b2stop
[ "$(stop)" = 0 ] && ok "a second background command running" || no "second running"
jq -nc '{"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "t1", "name": "TaskStop", "input": {"task_id": "b2stop"}}]}}' >> "$T/tr.jsonl"
[ "$(stop)" = 2 ] && ok "stopped with TaskStop: no notification comes, the stop is its end - refused again (2026-10-28)" || no "TaskStop left it running"
jq -nc '{"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "t2", "name": "Bash", "input": {"command": "echo Command running in background with ID: b3quote"}}]}}' >> "$T/tr.jsonl"
[ "$(stop)" = 2 ] && ok "a launch notice quoted in the session's own command is not a launch - refused (2026-10-28)" || no "a quoted notice counted as running"
line "Note: a file changed - Command running in background with ID: b4note. Output is being written to: x"
[ "$(stop)" = 2 ] && ok "a launch notice quoted in a system note is not a launch - refused (2026-10-28)" || no "a noted notice counted as running"

jq -nc '{"type": "user", "message": {"content": [{"type": "tool_result", "content": "Workflow launched in background. Task ID: w9wave"}]}, "toolUseResult": {"status": "async_launched", "taskId": "w9wave", "taskType": "local_workflow"}}' >> "$T/tr.jsonl"
[ "$(stop)" = 0 ] && ok "a workflow not reported back is running (2026-11-01)" || no "a running workflow read as nothing running"
line "<task-notification><task-id>w9wave</task-id><status>completed</status></task-notification>"
[ "$(stop)" = 2 ] && ok "the workflow reported back: refused again" || no "workflow reported back"

echo "4. a question is no way out (the plan review, 2026-10-19)"
jq -nc '{"type": "assistant", "message": {"content": [{"type": "text", "text": "Shall I go on to the next task?"}]}}' >> "$T/tr.jsonl"
[ "$(stop)" = 2 ] && ok "a turn ending on a question is refused" || no "question"

echo "4b. the next named: a performance task first, or none where each waits (451 T174: both forms rendered for the budget check)"
printf -- '- [x] T01 done\n- [ ] T02 the next thing\n- [ ] T03 [perf] a faster loop\n- [ ] GM review (make gm-reviewed F=385)\n' > "$C/specs/385-x/tasks.md"
rc=$(stop)
[ "$rc" = 2 ] && grep -q 'start the next (T03 \[perf\] a faster loop - performance work first, FR-013: make task-start F=385 T=T03)' "$T/err" && ok "a performance task is named first" || no "performance first" "rc=$rc $(cat "$T/err")"
printf -- '- [x] T01 done\n- [ ] T02 the next thing, after T03\n- [ ] T03 the other thing, after T02\n- [ ] GM review (make gm-reviewed F=385)\n' > "$C/specs/385-x/tasks.md"
rc=$(stop)
[ "$rc" = 2 ] && grep -q 'start the next (none can start yet: each waits on a day or a landing' "$T/err" && ok "each waits: none named" || no "none can start" "rc=$rc $(cat "$T/err")"
printf -- '- [x] T01 done\n- [ ] T02 the next thing\n- [ ] GM review (make gm-reviewed F=385)\n' > "$C/specs/385-x/tasks.md"

echo "5. make set-down: a reason of two words or more, recorded; it counts after the task-start only"
( cd "$C" && SET_DOWN_WHY="waiting" "$SETDOWN" set-down 385 >/dev/null 2>&1 ); [ $? -ne 0 ] && ok "a one-word reason is refused" || no "one-word reason"
printf '{"feature": "385-x", "why": "an old one", "utc": "2026-10-18T22:00:00Z"}\n' > "$G/set-downs.jsonl"
[ "$(stop)" = 2 ] && ok "a set-down before the task-start does not count" || no "old set-down"
o=$(cd "$C" && SET_DOWN_WHY="awaiting the GM on the cohort" "$SETDOWN" set-down 385) && seen o -q "385-x set down" && ok "make set-down records it" || no "set-down records"
[ "$(stop)" = 0 ] && ok "set down: the turn ends" || no "set down"

echo "6. only the GM's review box open: the turn ends"
rm -f "$G/set-downs.jsonl"
printf -- '- [x] T02 done\n- [ ] GM review (make gm-reviewed F=385)\n' > "$C/specs/385-x/tasks.md"
[ "$(stop)" = 0 ] && ok "the GM-review box holds nothing" || no "gm box"

echo "7. a read error fails open, recorded"
printf -- "- [ ] T03 x\n" > "$C/specs/385-x/tasks.md"; chmod 000 "$C/specs/385-x/tasks.md"
[ "$(stop)" = 0 ] && grep -rq "read-error" "$GUARD_LOG_DIR" && ok "an unreadable tasks.md lets the turn end, logged" || no "fail open"

echo "8. a part B owed with no arbiter ruling since: set-down refused, naming make arbiter-ask (feature 405, GM 2026-10-21)"
chmod 644 "$C/specs/385-x/tasks.md"
printf -- '- [ ] T26 the wood shed\n- [x] T103 the nub\n' > "$C/specs/385-x/tasks.md"
printf '[{"feature": "385-x", "task": "T26", "trigger": "cohort@x: seed(s) 10 newly failing", "part": "B", "utc": "2026-10-21T19:28:05Z"}]\n' > "$G/approach-owed.json"
( cd "$C" && SET_DOWN_WHY="the GM sees it first" "$SETDOWN" set-down 385 >/dev/null 2>"$T/err" ); rc=$?
[ "$rc" = 2 ] && grep -q "make arbiter-ask SUBJECT=set-down-T26" "$T/err" && grep -q "more room" "$T/err" && ok "refused, naming the arbiter ask" || no "unruled set-down" "rc=$rc $(cat "$T/err")"
( cd "$C" && SET_DOWN_OK="the usage cap wind-down" SET_DOWN_WHY="the cap is reached" "$SETDOWN" set-down 385 >/dev/null 2>&1 ) && ok "the escape lets it through" || no "escape"
printf '{"trigger": "ask:set-down-T26", "ruling": "continue", "utc": "2026-10-21T19:20:00Z"}\n' > "$C/specs/385-x/arbiter.jsonl"
( cd "$C" && SET_DOWN_WHY="the GM sees it first" "$SETDOWN" set-down 385 >/dev/null 2>&1 ); [ $? = 2 ] && ok "a ruling from before the trigger answers nothing" || no "old ruling"
printf '{"trigger": "ask:set-down-T26", "ruling": "continue", "utc": "2026-10-21T19:40:00Z"}\n' >> "$C/specs/385-x/arbiter.jsonl"
( cd "$C" && SET_DOWN_WHY="the arbiter ruled it" "$SETDOWN" set-down 385 >/dev/null 2>&1 ) && ok "ruled since: set down" || no "ruled set-down"
printf -- '- [x] T26 the wood shed\n' > "$C/specs/385-x/tasks.md"; rm -f "$C/specs/385-x/arbiter.jsonl"
( cd "$C" && SET_DOWN_WHY="nothing owed now" "$SETDOWN" set-down 385 >/dev/null 2>&1 ) && ok "a ticked task's part B holds nothing" || no "ticked owed"

echo "9. a usage cap armed and not reached: set-down refused until the arbiter rules on a set-down ask (the GM 2026-10-23)"
mkdir -p "$T/cap"; export CLAUDE_CODE_SESSION_ID=s-1
printf -- '- [ ] T07 the merge\n' > "$C/specs/385-x/tasks.md"; rm -f "$G/approach-owed.json"
printf '{"cap": 80.0, "goal": "385 to completion"}' > "$T/cap/budget-s-1.json"
printf '{"seven_day": 69}' > "$T/cap/latest-s-1.json"
( cd "$C" && SET_DOWN_WHY="past the usage left" "$SETDOWN" set-down 385 >/dev/null 2>"$T/err" ); rc=$?
[ "$rc" = 2 ] && grep -q "the weekly cap is 80% and the 7-day figure is 69%" "$T/err" && grep -q "make arbiter-ask SUBJECT=set-down-385" "$T/err" && ok "under the cap: refused, naming the arbiter ask" || no "under cap" "rc=$rc $(cat "$T/err")"
printf '{"trigger": "ask:set-down-385", "ruling": "accept", "utc": "2026-10-18T22:30:00Z"}\n' > "$C/specs/385-x/arbiter.jsonl"
( cd "$C" && SET_DOWN_WHY="past the usage left" "$SETDOWN" set-down 385 >/dev/null 2>&1 ); [ $? = 2 ] && ok "a ruling before the task-start answers nothing" || no "old cap ruling"
printf '{"trigger": "ask:set-down-385", "ruling": "accept", "utc": "2026-10-19T01:00:00Z"}\n' >> "$C/specs/385-x/arbiter.jsonl"
( cd "$C" && SET_DOWN_WHY="the arbiter ruled it" "$SETDOWN" set-down 385 >/dev/null 2>&1 ) && ok "ruled since the task-start: set down" || no "cap ruled"
rm -f "$C/specs/385-x/arbiter.jsonl"; printf '{"seven_day": 80}' > "$T/cap/latest-s-1.json"
( cd "$C" && SET_DOWN_WHY="the cap is reached" "$SETDOWN" set-down 385 >/dev/null 2>&1 ) && ok "at the cap: set down" || no "at cap"
rm -f "$T/cap/budget-s-1.json"

echo "10. no goal cap (retired, the GM 2026-10-24): the account's weekly soft cap holds the set-down"
printf '{"seven_day": 76, "account": {"uuid": "u-1"}}' > "$T/cap/latest-s-1.json"
( cd "$C" && SET_DOWN_WHY="past the usage left" "$SETDOWN" set-down 385 >/dev/null 2>"$T/err" ); rc=$?
[ "$rc" = 2 ] && grep -q "the weekly cap is 90% and the 7-day figure is 76%" "$T/err" && ok "under the default soft cap: refused" || no "soft default" "rc=$rc $(cat "$T/err")"
printf '{"u-1": {"cap": 70}}' > "$T/cap/caps.json"
( cd "$C" && SET_DOWN_WHY="the cap is reached" "$SETDOWN" set-down 385 >/dev/null 2>&1 ) && ok "past the account's own soft cap: set down" || no "soft set"
printf '{"u-1": {"cap": 95}}' > "$T/cap/caps.json"
( cd "$C" && SET_DOWN_WHY="past the usage left" "$SETDOWN" set-down 385 >/dev/null 2>&1 ); [ $? = 2 ] && ok "the cap raised mid-work: refused at the next call" || no "raised cap"
printf '{"u-1": {"cap": 70}}' > "$T/cap/caps.json"
( cd "$C" && SET_DOWN_WHY="the cap is reached" "$SETDOWN" set-down 385 >/dev/null 2>&1 ) && ok "lowered again: set down at the next call" || no "lowered cap"
printf '{"u-1": {"cap": 95}}' > "$T/cap/caps.json"
printf '{"seven_day": 76, "seven_day_resets_at": 1, "account": {"uuid": "u-1"}}' > "$T/cap/latest-s-1.json"
( cd "$C" && SET_DOWN_WHY="a new week" "$SETDOWN" set-down 385 >/dev/null 2>&1 ) && ok "last week's reading decides nothing" || no "stale reading"
rm -f "$T/cap/latest-s-1.json"
( cd "$C" && SET_DOWN_WHY="no reading here" "$SETDOWN" set-down 385 >/dev/null 2>&1 ) && ok "no reading: set down" || no "no reading"

echo "9. only parked stages left (449 T244): the stop names the GM's ruling, never a stage to start, and make set-down takes it under the cap"
P="$T/parked"; mkdir -p "$P/specs/444-x" "$P/rust/parked/src"; git -C "$P" init -q; : > "$P/rust/parked/src/homesteads.rs"
printf -- '- [x] T29 phase: seat - done\n- [ ] T30 phase: homesteads - every household\n- [ ] GM review (make gm-reviewed F=444)\n' > "$P/specs/444-x/tasks.md"
printf '{"feature": "444-x", "task": "T29", "utc": "2026-11-21T10:00:00Z"}\n' > "$P/.git/task-starts.jsonl"
: > "$T/tr9.jsonl"
rc=$(printf '{"cwd": "%s", "transcript_path": "%s"}' "$P" "$T/tr9.jsonl" | SET_DOWN_ROOT="$P" "$HOOK" stop 2>"$T/err"; echo $?)
[ "$rc" = 2 ] && grep -q "Stop before homesteads, and talk first" "$T/err" && ! grep -q "task-start F=444 T=T30" "$T/err" && ok "the ruling named, no stage task to start" || no "parked stop" "rc=$rc $(cat "$T/err")"
printf '{"seven_day": 50}' > "$T/cap/latest-s-9.json"
out=$(cd "$P" && CLAUDE_CODE_SESSION_ID=s-9 SET_DOWN_WHY="the parked stages wait for the GM" "$SETDOWN" set-down 444 2>&1) && seen out -q "the stop the GM asked for" && ok "set down under the cap, naming the ruling" || no "parked set-down" "$out"

echo "11. builders running: the Stop is silent, and a report back names no free slot (451 T183's MODE 4, D10: a free slot is named only by the idle check, once nothing runs)"
L="$T/land"; mkdir -p "$L/specs/449-x" "$L/scripts"; git -C "$L" init -q
printf -- '- [ ] T259 a\n- [ ] T277 b\n- [ ] T289 c\n- [ ] T295 d\n- [ ] T301 e\n' > "$L/specs/449-x/tasks.md"
printf '{"feature": "449-x", "task": "T259", "utc": "2026-11-22T10:00:00Z"}\n' > "$L/.git/task-starts.jsonl"
: > "$T/trL.jsonl"; mkdir -p "$T/trL/subagents"
builder() { launch agentId "Async agent launched successfully. agentId: $1 (internal ID)" "$1" >/dev/null
  jq -nc '{"spawnDepth": 1, "description": $ARGS.positional[0]}' --args -- "$2" > "$T/trL/subagents/agent-$1.meta.json"; }
NOTE='<task-notification><task-id>x</task-id></task-notification>'
# a report back: the prompt with a notice; whatever it is told, or nothing
reportL() { jq -nc --arg c "$L" --arg t "$T/trL.jsonl" --arg p "$NOTE" '{cwd: $c, transcript_path: $t, prompt: $p}' \
  | SET_DOWN_ROOT="$L" "$HOOK" prompt 2>"$T/err" > "$T/out"; cat "$T/out"; }
stopL() { printf '{"cwd": "%s", "transcript_path": "%s"}' "$L" "$T/trL.jsonl" | SET_DOWN_ROOT="$L" "$HOOK" stop 2>"$T/err"; echo $?; }
launch() { jq -nc '{"type": "user", "message": {"content": [{"type": "tool_result", "content": $ARGS.positional[1]}]}, "toolUseResult": {($ARGS.positional[0]): $ARGS.positional[2]}}' --args -- "$1" "$2" "$3" >> "$T/trL.jsonl"; }
builder ab1 "449 bundle T259, T277: the two"
builder ab2 "449 T289-T300 bundle (fresh): twelve"
[ "$(stopL)" = 0 ] && [ ! -s "$T/err" ] && ok "builders running: the Stop is silent, their end wakes the session" || no "a Stop over running builders" "$(cat "$T/err")"
[ -z "$(reportL)" ] && ok "a report back with a slot free: nothing said" || no "a report back's notice" "$(cat "$T/out")"

echo "12. a compaction's SessionStart says nothing (451 T171)"
startS() { printf '{"session_id": "s12", "cwd": "%s", "source": "%s"}' "$L" "$1" | SET_DOWN_ROOT="$L" "$HOOK" SessionStart 2>"$T/err"; echo $?; }
rc=$(startS compact)
[ "$rc" = 0 ] && [ ! -s "$T/err" ] && ok "a SessionStart after a compaction says nothing" || no "session start" "rc=$rc $(cat "$T/err")"

echo "13. a ruling that holds new work (451 T183, today's ask:set-down-451-gm-stop-for-convergence-talk): the idle check names no task"
printf '{"trigger": "ask:set-down-449-gm-stop-for-convergence-talk", "kind": "ask", "ruling": "continue", "what": "Go on as the question proposes. 449 starts no new task, and the set-down hook stops asking 449 for one.", "utc": "2026-11-23T14:42:15Z"}\n' > "$L/specs/449-x/arbiter.jsonl"
for id in ab1 ab2; do jq -nc --arg i "$id" '{"type": "user", "message": {"content": ("<task-notification><task-id>" + $i + "</task-id><status>completed</status></task-notification>")}}' >> "$T/trL.jsonl"; done
[ "$(stopL)" = 0 ] && [ ! -s "$T/err" ] && ok "idle with open tasks under the hold: the idle check is silent" || no "held idle" "$(cat "$T/err")"
printf '{"trigger": "ask:set-down-449-after-talk", "kind": "ask", "ruling": "continue", "what": "Do not set down. Resume the work now.", "utc": "2026-11-23T18:00:00Z"}\n' >> "$L/specs/449-x/arbiter.jsonl"
[ "$(stopL)" = 2 ] && grep -q "make set-down F=449" "$T/err" && ok "a later ruling sends the work on: the idle check speaks" || no "released" "$(cat "$T/err")"

echo "14. the idle check: silent for what the harness tracks, and for a session that turned while it waited (451 T183)"
printf '{"cwd": "%s", "transcript_path": "%s", "background_tasks": [{"id": "b9", "type": "subagent", "status": "running"}]}' "$L" "$T/trL.jsonl" | SET_DOWN_ROOT="$L" "$HOOK" stop >/dev/null 2>&1
[ $? = 0 ] && ok "a tracked run: silent" || no "tracked run"
( sleep 0.5; jq -nc '{"type": "user", "message": {"content": "the GM answers"}}' >> "$T/trL.jsonl" ) &
rc=$(printf '{"cwd": "%s", "transcript_path": "%s", "background_tasks": []}' "$L" "$T/trL.jsonl" | L7R_IDLE_CHECK_SECS=2 SET_DOWN_ROOT="$L" "$HOOK" stop 2>"$T/err"; echo $?)
wait
[ "$rc" = 0 ] && [ ! -s "$T/err" ] && ok "a prompt while it waited: silent, that turn's Stop arms the next" || no "turned" "rc=$rc $(cat "$T/err")"
rc=$(printf '{"cwd": "%s", "transcript_path": "%s", "background_tasks": []}' "$L" "$T/trL.jsonl" | L7R_IDLE_CHECK_SECS=1 SET_DOWN_ROOT="$L" "$HOOK" stop 2>"$T/err"; echo $?)
[ "$rc" = 2 ] && grep -q "make set-down F=449" "$T/err" && ok "idle through its wait: the block, exit 2 (asyncRewake wakes the session)" || no "idle" "rc=$rc $(cat "$T/err")"

echo "set-down-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
