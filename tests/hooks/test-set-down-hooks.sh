#!/usr/bin/env bash
# Tests for set-down-hooks.sh - a feature is worked until it is set down (feature 385 T70, plan D89/D90).
# Run: tests/hooks/test-set-down-hooks.sh   (exit 0 = all green)
#
# Each case drives the REAL hook with a Stop payload (`cwd`, `transcript_path`) on a fixture clone: its `task-starts.jsonl`,
# a feature's `tasks.md`, and a transcript in the harness's JSONL form, whose background launches and task notifications say
# what is still running.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/../../scripts/hooks/set-down-hooks.sh"
SETDOWN="$HERE/../../scripts/set-down.py"
T=$(mktemp -d)
GUARD_LOG_DIR="$T/log"; export GUARD_LOG_DIR
trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
C="$T/clone"; mkdir -p "$C/specs/385-x"; git -C "$C" init -q
G="$C/.git"
printf -- '- [x] T01 done\n- [ ] T02 the next thing\n- [ ] GM review (make gm-reviewed F=385)\n' > "$C/specs/385-x/tasks.md"
: > "$T/tr.jsonl"
stop() { printf '{"cwd": "%s", "transcript_path": "%s"}' "$C" "$T/tr.jsonl" | SET_DOWN_ROOT="$C" "$HOOK" stop 2>"$T/err"; echo $?; }
line() { python3 -c 'import json,sys; print(json.dumps({"type": "user", "message": {"content": sys.argv[1]}}))' "$1" >> "$T/tr.jsonl"; }

echo "1. silent where no feature was begun"
[ "$(stop)" = 0 ] && ok "no task-start: the turn ends" || no "no task-start"

echo "2. an open task, nothing running, not set down: refused, naming the next task and make set-down"
printf '{"feature": "385-x", "task": "T02", "utc": "2026-10-18T23:00:00Z"}\n' > "$G/task-starts.jsonl"
rc=$(stop)
[ "$rc" = 2 ] && grep -q "T02 the next thing" "$T/err" && grep -q 'make set-down F=385 WHY=' "$T/err" && ok "refused with the next step" || no "refused" "rc=$rc $(cat "$T/err")"
ls "$GUARD_LOG_DIR" >/dev/null 2>&1 && ok "the refusal is recorded in the guard log" || no "guard log"

echo "3. work still running lets the turn end; reported back, it does not"
line "Command running in background with ID: b1abc. Output is being written to: x"
[ "$(stop)" = 0 ] && ok "a background command not reported back" || no "background running"
line "<task-notification><task-id>b1abc</task-id><status>completed</status></task-notification>"
[ "$(stop)" = 2 ] && ok "reported back: refused again" || no "reported back"
line "Async agent launched successfully. agentId: a9f00 (internal ID)"
[ "$(stop)" = 0 ] && ok "an async agent not reported back" || no "agent running"
line "<task-id>a9f00</task-id>"

echo "4. a question is no way out (the plan review, 2026-10-19)"
python3 -c 'import json; print(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "Shall I go on to the next task?"}]}}))' >> "$T/tr.jsonl"
[ "$(stop)" = 2 ] && ok "a turn ending on a question is refused" || no "question"

echo "5. make set-down: a reason of two words or more, recorded; it counts after the task-start only"
( cd "$C" && SET_DOWN_WHY="waiting" python3 "$SETDOWN" 385 >/dev/null 2>&1 ); [ $? -ne 0 ] && ok "a one-word reason is refused" || no "one-word reason"
printf '{"feature": "385-x", "why": "an old one", "utc": "2026-10-18T22:00:00Z"}\n' > "$G/set-downs.jsonl"
[ "$(stop)" = 2 ] && ok "a set-down before the task-start does not count" || no "old set-down"
( cd "$C" && SET_DOWN_WHY="awaiting the GM on the cohort" python3 "$SETDOWN" 385 ) | grep -q "385-x set down" && ok "make set-down records it" || no "set-down records"
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
( cd "$C" && SET_DOWN_WHY="the GM sees it first" python3 "$SETDOWN" 385 >/dev/null 2>"$T/err" ); rc=$?
[ "$rc" = 2 ] && grep -q "make arbiter-ask SUBJECT=set-down-T26" "$T/err" && grep -q "more room" "$T/err" && ok "refused, naming the arbiter ask" || no "unruled set-down" "rc=$rc $(cat "$T/err")"
( cd "$C" && SET_DOWN_OK="the usage cap wind-down" SET_DOWN_WHY="the cap is reached" python3 "$SETDOWN" 385 >/dev/null 2>&1 ) && ok "the escape lets it through" || no "escape"
printf '{"trigger": "ask:set-down-T26", "ruling": "continue", "utc": "2026-10-21T19:20:00Z"}\n' > "$C/specs/385-x/arbiter.jsonl"
( cd "$C" && SET_DOWN_WHY="the GM sees it first" python3 "$SETDOWN" 385 >/dev/null 2>&1 ); [ $? = 2 ] && ok "a ruling from before the trigger answers nothing" || no "old ruling"
printf '{"trigger": "ask:set-down-T26", "ruling": "continue", "utc": "2026-10-21T19:40:00Z"}\n' >> "$C/specs/385-x/arbiter.jsonl"
( cd "$C" && SET_DOWN_WHY="the arbiter ruled it" python3 "$SETDOWN" 385 >/dev/null 2>&1 ) && ok "ruled since: set down" || no "ruled set-down"
printf -- '- [x] T26 the wood shed\n' > "$C/specs/385-x/tasks.md"; rm -f "$C/specs/385-x/arbiter.jsonl"
( cd "$C" && SET_DOWN_WHY="nothing owed now" python3 "$SETDOWN" 385 >/dev/null 2>&1 ) && ok "a ticked task's part B holds nothing" || no "ticked owed"

echo "set-down-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
