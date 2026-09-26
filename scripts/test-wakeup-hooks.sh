#!/usr/bin/env bash
# Tests for wakeup-hooks.sh - a timed wakeup cannot outlive its purpose (feature 263).
# Run: scripts/test-wakeup-hooks.sh   (exit 0 = all green)
#
# Every case drives the REAL hook with a REAL payload shape - the Stop payload's `session_crons` entries are the
# `{id, schedule, recurring, prompt}` measured in specs/263-stale-wakeup-guard/research.md R1, a loop's wakeup
# prompt is `/loop <input>` (R3) - and a fixture transcript in the harness's JSONL form, because the transcript is
# what tells a wakeup from a reminder and a live loop from a stopped one.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/wakeup-hooks.sh"
T=$(mktemp -d)
GUARD_LOG_DIR="$T/log"; export GUARD_LOG_DIR
HOOK_ERR="$T/err"
trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

WAKE_PROMPT="Continue feature 262: integrate the prose fixes."
REMINDER_PROMPT="Remind the GM to look at the Ochiba page."
LOOP_PROMPT="/loop check the deploy"

transcript() { # transcript <file> <events...> -> a JSONL transcript; events: loopcmd | loopskill | stop | wake:<prompt> | reminder
  python3 - "$@" <<'PY'
import json, sys
path, events = sys.argv[1], sys.argv[2:]
rows = [{"type": "user", "message": {"role": "user", "content": "please build the thing"}}]
def tool(name, inp):
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "name": name, "input": inp}]}}
for e in events:
    if e == "loopcmd":  # the measured shape of a /loop firing (research.md R3)
        rows.append({"type": "user", "message": {"role": "user", "content": "<command-message>loop</command-message>\n<command-name>/loop</command-name>\n<command-args>check the deploy</command-args>"}})
    elif e == "loopskill":
        rows.append(tool("Skill", {"skill": "loop", "args": "check the deploy"}))
    elif e == "stop":
        rows.append(tool("ScheduleWakeup", {"stop": True}))
    elif e.startswith("wake:"):
        rows.append(tool("ScheduleWakeup", {"delaySeconds": 1500, "reason": "r", "prompt": e[5:]}))
    elif e == "reminder":
        rows.append(tool("CronCreate", {"cron": "17 9 24 12 *", "prompt": "Remind the GM to look at the Ochiba page.", "recurring": False}))
open(path, "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
}

wake_call() { # wake_call <transcript> <reason> <prompt> [stop] -> the pretool hook's exit code
  python3 -c 'import json,sys; ti={"delaySeconds":1500,"reason":sys.argv[2],"prompt":sys.argv[3]}
if len(sys.argv)>4: ti={"stop":True}
print(json.dumps({"session_id":"s1","tool_name":"ScheduleWakeup","transcript_path":sys.argv[1],"tool_input":ti}))' "$@" \
    | "$HOOK" pretool 2>"$HOOK_ERR"
}

stop_call() { # stop_call <session> <transcript> <cron-json-list> -> the stop hook's exit code
  python3 -c 'import json,sys; print(json.dumps({"session_id":sys.argv[1],"hook_event_name":"Stop","transcript_path":sys.argv[2],"background_tasks":[],"session_crons":json.loads(sys.argv[3])}))' "$@" \
    | "$HOOK" stop 2>"$HOOK_ERR"
}
cron() { python3 -c 'import json,sys; print(json.dumps({"id":sys.argv[1],"schedule":"51 20 * * *","recurring":False,"prompt":sys.argv[2]}))' "$1" "$2"; }

transcript "$T/plain.jsonl" "wake:$WAKE_PROMPT" reminder
transcript "$T/live.jsonl" loopcmd "wake:$LOOP_PROMPT"
transcript "$T/liveskill.jsonl" loopskill "wake:$LOOP_PROMPT"
transcript "$T/stopped.jsonl" loopcmd "wake:$LOOP_PROMPT" stop "wake:$WAKE_PROMPT"
transcript "$T/none.jsonl"

echo "1. layer 1 - a ScheduleWakeup outside a live /loop is refused before it exists"
wake_call "$T/plain.jsonl" "fallback while the agent runs" "$WAKE_PROMPT"; rc=$?
[ "$rc" -eq 2 ] && ok "refused outside /loop" || no "not refused outside /loop" "(rc=$rc)"
grep -q "wakes this session by itself" "$HOOK_ERR" && ok "...saying background work wakes the session by itself" || no "the refusal does not say why it is unneeded"
grep -q "CronCreate" "$HOOK_ERR" && ok "...and naming CronCreate for a reminder the GM asked for" || no "the refusal does not name the reminder route"
wake_call "$T/plain.jsonl" 'WAKEUP_OK="a deliberate format measurement"' "$WAKE_PROMPT"; rc=$?
[ "$rc" -eq 2 ] && ok "there is no escape: a WAKEUP_OK token changes nothing" || no "a WAKEUP_OK token let a fallback through" "(rc=$rc)"
wake_call "$T/live.jsonl" "pacing the loop" "$LOOP_PROMPT"; rc=$?
[ "$rc" -eq 0 ] && ok "a live loop's own wakeup passes (/loop command)" || no "a live loop's wakeup was refused" "(rc=$rc)"
wake_call "$T/liveskill.jsonl" "pacing the loop" "$LOOP_PROMPT"; rc=$?
[ "$rc" -eq 0 ] && ok "...and when the loop was started through the loop skill" || no "the skill-started loop was refused" "(rc=$rc)"
wake_call "$T/live.jsonl" "fallback inside the loop" "$WAKE_PROMPT"; rc=$?
[ "$rc" -eq 2 ] && grep -q "OWN prompt" "$HOOK_ERR" && ok "a fallback timer inside a live loop is refused" || no "a non-loop prompt rode on a live loop" "(rc=$rc)"
wake_call "$T/stopped.jsonl" "pacing" "$LOOP_PROMPT"; rc=$?
[ "$rc" -eq 2 ] && ok "a loop that was stopped is not live" || no "a stopped loop still counted as live" "(rc=$rc)"
wake_call "$T/plain.jsonl" "x" "x" stop; rc=$?
[ "$rc" -eq 0 ] && ok "stop:true (ending a loop) always passes" || no "stop:true refused" "(rc=$rc)"
printf '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | "$HOOK" pretool 2>/dev/null; rc=$?
[ "$rc" -eq 0 ] && ok "any other tool is ignored" || no "another tool was refused" "(rc=$rc)"
printf 'not json' | "$HOOK" pretool 2>/dev/null; rc=$?
[ "$rc" -eq 2 ] && ok "an unreadable payload is refused - closed on the call (plan review)" || no "a garbage payload let a wakeup through" "(rc=$rc)"
wake_call "$T/missing.jsonl" "fallback" "$WAKE_PROMPT"; rc=$?
[ "$rc" -eq 2 ] && ok "a missing transcript is refused - no live loop can be shown" || no "a missing transcript let a wakeup through" "(rc=$rc)"
printf 'this line is not json\n' > "$T/broken.jsonl"
wake_call "$T/broken.jsonl" "fallback" "$WAKE_PROMPT"; rc=$?
[ "$rc" -eq 2 ] && ok "an unparsable transcript is refused" || no "an unparsable transcript let a wakeup through" "(rc=$rc)"
wake_call "$T/missing.jsonl" "x" "x" stop; rc=$?
[ "$rc" -eq 0 ] && ok "...but stop:true still passes without a transcript (ending a loop is always allowed)" || no "stop:true refused without a transcript" "(rc=$rc)"

echo "2. layer 2 - a turn cannot end with a stale wakeup pending"
stop_call s2 "$T/plain.jsonl" "[$(cron 43582eac "$WAKE_PROMPT")]"; rc=$?
[ "$rc" -eq 2 ] && ok "a pending wakeup outside /loop blocks the turn end" || no "the stale wakeup did not block" "(rc=$rc)"
grep -q "CronDelete 43582eac" "$HOOK_ERR" && ok "...naming the exact CronDelete" || no "the block does not name CronDelete <id>"
stop_call s2 "$T/plain.jsonl" "[$(cron 43582eac "$WAKE_PROMPT")]"; rc=$?
[ "$rc" -eq 2 ] && ok "...and at EVERY turn end while it stays pending - no once-only valve" || no "the second turn end let it through" "(rc=$rc)"
stop_call s3 "$T/plain.jsonl" "[$(cron 106428e0 "$REMINDER_PROMPT")]"; rc=$?
[ "$rc" -eq 0 ] && ok "a CronCreate reminder never blocks" || no "a reminder the GM asked for was blocked" "(rc=$rc)"
stop_call s4 "$T/plain.jsonl" "[$(cron 106428e0 "$REMINDER_PROMPT"),$(cron e1f0ebb6 "$WAKE_PROMPT")]"; rc=$?
[ "$rc" -eq 2 ] && grep -q "CronDelete e1f0ebb6" "$HOOK_ERR" && ! grep -q "106428e0" "$HOOK_ERR" && ok "with both pending, only the wakeup is named" || no "the mixed case named the wrong cron" "(rc=$rc)"
stop_call s5 "$T/live.jsonl" "[$(cron 0ec9c84c "$LOOP_PROMPT")]"; rc=$?
[ "$rc" -eq 0 ] && ok "a live loop's own wakeup never blocks" || no "a live loop's wakeup was blocked" "(rc=$rc)"
stop_call s6 "$T/stopped.jsonl" "[$(cron 43582eac "$WAKE_PROMPT")]"; rc=$?
[ "$rc" -eq 2 ] && ok "a fallback set after the loop stopped blocks" || no "a post-loop fallback survived" "(rc=$rc)"
stop_call s7 "$T/none.jsonl" "[]"; rc=$?
[ "$rc" -eq 0 ] && ok "nothing pending, nothing to say" || no "an empty turn end blocked" "(rc=$rc)"
stop_call s8 "$T/missing.jsonl" "[$(cron 43582eac "$WAKE_PROMPT")]"; rc=$?
[ "$rc" -eq 0 ] && ok "an unreadable transcript does not block on a guess" || no "blocked without a transcript" "(rc=$rc)"

echo "3. every firing is recorded"
grep -rqs '"blocked"' "$GUARD_LOG_DIR" && ok "blocks reach the guard log" || no "no blocked entry in the guard log"

echo
echo "  test-wakeup-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
