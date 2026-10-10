#!/usr/bin/env bash
# Tests for event-log-hooks.sh - every hook event becomes one line of the feature's event log (feature 375, FR-008).
# Run: tests/hooks/test-event-log-hooks.sh   (exit 0 = all green)
#
# Each case drives the REAL hook with the payload shapes measured on 2026-10-10 (specs/375-enforced-wave-process/
# measurements.json `subagent-stop-probe`: a background agent's PostToolUse carries tool_response.agentId, its
# SubagentStart and SubagentStop the same agent_id) inside a throwaway clone with a `.specify/feature.json`.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/../../scripts/hooks/event-log-hooks.sh"
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

CLONE="$T/clone"
git init -q "$CLONE"
mkdir -p "$CLONE/.specify" "$CLONE/sub/dir"
printf '{"feature_directory": "specs/999-a-feature"}\n' > "$CLONE/.specify/feature.json"
LOG="$CLONE/.git/l7r-events/999-a-feature.jsonl"

fire() { # fire <json payload> -> the hook's exit code; its stdout+stderr to $T/out
  printf '%s' "$1" | "$HOOK" >"$T/out" 2>&1
}
last() { tail -n1 "$LOG" 2>/dev/null; }
field() { last | python3 -c 'import json,sys; v=json.load(sys.stdin).get(sys.argv[1], ""); print(v)' "$1"; }

echo "event-log-hooks:"

fire '{"hook_event_name":"PreToolUse","session_id":"s1","cwd":"'"$CLONE"'/sub/dir","tool_name":"Bash","tool_use_id":"tu1","tool_input":{"command":"cd x && make quick ALL=1"}}'
rc=$?
[ "$rc" = 0 ] && [ ! -s "$T/out" ] && ok "a call is logged silently, exit 0" || no "silent exit 0" "rc=$rc out=$(cat "$T/out")"
[ "$(field ev)" = PreToolUse ] && [ "$(field cat)" = "quick test" ] && [ "$(field make)" = quick ] && [ "$(field id)" = tu1 ] \
  && ok "a make quick is a quick test, its target and tool_use_id kept" || no "quick test" "$(last)"
[ -n "$(field t)" ] && [ "$(field sid)" = s1 ] && ok "time and session on the line" || no "time and session" "$(last)"

fire '{"hook_event_name":"PreToolUse","session_id":"s1","cwd":"'"$CLONE"'","tool_name":"Bash","tool_use_id":"tu2","tool_input":{"command":"make test-file FILE=tests/x.py"}}'
[ "$(field cat)" = "test file" ] && ok "make test-file is a test file" || no "test file" "$(last)"
fire '{"hook_event_name":"PreToolUse","session_id":"s1","cwd":"'"$CLONE"'","tool_name":"Bash","tool_use_id":"tu3","tool_input":{"command":"make done 2>&1 | tee log"}}'
[ "$(field cat)" = gate ] && ok "make done is a gate" || no "gate" "$(last)"
fire '{"hook_event_name":"PreToolUse","session_id":"s1","cwd":"'"$CLONE"'","tool_name":"Bash","tool_use_id":"tu4","tool_input":{"command":"grep -n make Makefile"}}'
[ "$(field cat)" = "other tool" ] && [ -z "$(field make)" ] && ok "a mention of make is not a make run" || no "mention" "$(last)"

fire '{"hook_event_name":"PreToolUse","session_id":"s1","cwd":"'"$CLONE"'","tool_name":"Edit","tool_use_id":"tu5","tool_input":{"file_path":"/x/a.md","old_string":"A","new_string":"B"}}'
old1="$(field old)"; new1="$(field new)"
[ "$(field cat)" = edit ] && [ "$(field path)" = /x/a.md ] && [ -n "$old1" ] && [ "$old1" != "$new1" ] \
  && ok "an Edit keeps its path and both strings' digests" || no "edit digests" "$(last)"
fire '{"hook_event_name":"PreToolUse","session_id":"s1","cwd":"'"$CLONE"'","tool_name":"Edit","tool_use_id":"tu6","tool_input":{"file_path":"/x/a.md","old_string":"B","new_string":"A"}}'
[ "$(field new)" = "$old1" ] && [ "$(field old)" = "$new1" ] && ok "a reversal reads as its digests swapped (the A -> B -> A wire)" || no "reversal" "$(last)"

fire '{"hook_event_name":"PreToolUse","session_id":"s1","cwd":"'"$CLONE"'","tool_name":"Agent","tool_use_id":"tu7","tool_input":{"subagent_type":"quote-check","prompt":"read /tmp/l7r-check/0100-quote-check/MANIFEST.md"}}'
[ "$(field cat)" = "record check" ] && [ "$(field agent)" = quote-check ] && [ "$(field manifest)" = /tmp/l7r-check/0100-quote-check/MANIFEST.md ] \
  && ok "a record check keeps its type and MANIFEST" || no "record check" "$(last)"
fire '{"hook_event_name":"PostToolUse","session_id":"s1","cwd":"'"$CLONE"'","tool_name":"Agent","tool_use_id":"tu7","tool_input":{"subagent_type":"quote-check","prompt":"p"},"tool_response":{"status":"async_launched","agentId":"ag1"},"duration_ms":40}'
[ "$(field ev)" = PostToolUse ] && [ "$(field aid)" = ag1 ] && [ "$(field ms)" = 40 ] && ok "a launch pairs tool_use_id with the agent id" || no "launch pairing" "$(last)"
fire '{"hook_event_name":"SubagentStop","session_id":"s1","cwd":"'"$CLONE"'","agent_type":"quote-check","agent_id":"ag1"}'
[ "$(field ev)" = SubagentStop ] && [ "$(field aid)" = ag1 ] && [ "$(field cat)" = "record check" ] && ok "a return carries the same agent id" || no "return" "$(last)"
fire '{"hook_event_name":"PreToolUse","session_id":"s1","cwd":"'"$CLONE"'","tool_name":"Agent","tool_use_id":"tu8","tool_input":{"subagent_type":"general-purpose","model":"opus","prompt":"triage /tmp/l7r-check/claims-triage/MANIFEST.md"}}'
[ "$(field cat)" = "claims check" ] && ok "an ad-hoc claims triage is a claims check" || no "claims triage" "$(last)"
fire '{"hook_event_name":"PreToolUse","session_id":"s1","cwd":"'"$CLONE"'","tool_name":"Agent","tool_use_id":"tu9","tool_input":{"subagent_type":"glyph-check","prompt":"p"}}'
[ "$(field cat)" = "review check" ] && ok "glyph-check is a review check" || no "review check" "$(last)"
fire '{"hook_event_name":"PreToolUse","session_id":"s1","cwd":"'"$CLONE"'","tool_name":"Skill","tool_use_id":"tu10","tool_input":{"skill":"speckit-plan"}}'
[ "$(field cat)" = "spec-kit step" ] && ok "a speckit skill is a spec-kit step" || no "speckit" "$(last)"
fire '{"hook_event_name":"UserPromptSubmit","session_id":"s1","cwd":"'"$CLONE"'","prompt":"go"}'
[ "$(field ev)" = UserPromptSubmit ] && ok "a prompt is logged" || no "prompt" "$(last)"

n=$(wc -l < "$LOG")
fire 'not json at all'; rc=$?
[ "$rc" = 0 ] && [ "$(wc -l < "$LOG")" = "$n" ] && ok "a payload that does not parse exits 0 and writes nothing" || no "garbage" "rc=$rc"
fire '{"hook_event_name":"PreToolUse","session_id":"s1","cwd":"/","tool_name":"Bash","tool_input":{"command":"ls"}}'; rc=$?
[ "$rc" = 0 ] && ok "a call outside any clone exits 0" || no "outside a clone" "rc=$rc"

rm -f "$CLONE/.specify/feature.json"
fire '{"hook_event_name":"Stop","session_id":"s1","cwd":"'"$CLONE"'"}'
[ -s "$CLONE/.git/l7r-events/_unassigned.jsonl" ] && ok "no active feature: the unassigned log" || no "unassigned"

echo
echo "event-log-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" = 0 ]
