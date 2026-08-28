#!/usr/bin/env bash
# test-agent-watch-hooks.sh - prove agent-watch-hooks.sh tells a finished agent from a hung one and acts on it.
# (GUARD_EDIT_OK: the companion of a NEW guard, GM 2026-08-28)
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/agent-watch-hooks.sh"
pass=0 fail=0
ok() { pass=$((pass+1)); }
bad() { fail=$((fail+1)); echo "FAIL: $1"; }
check() { if eval "$2"; then ok; else bad "$1"; fi; }
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
SESS="$TMP/proj/sid-1"; DIR="$SESS/subagents"; mkdir -p "$DIR"; : > "$TMP/proj/sid-1.jsonl"
rec() { printf '%s\n' "$2" >> "$DIR/agent-$1.jsonl"; }
TU='{"type":"assistant","message":{"role":"assistant","stop_reason":"tool_use","content":[{"type":"tool_use","name":"WebFetch","input":{"url":"https://example.org/paper"}}]}}'
TR='{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"..."}]}}'
END='{"type":"assistant","message":{"role":"assistant","stop_reason":"end_turn","content":[{"type":"text","text":"done"}]}}'
rec fin "$TU"; rec fin "$TR"; rec fin "$END"          # a finished agent
rec pend "$TU"; rec pend "$TR"                          # pending, fresh
rec hung "$TU"; rec hung "$TR"; touch -d '-3 hours' "$DIR/agent-hung.jsonl"   # pending, 3 h idle
STDIN=$(printf '{"transcript_path":"%s","session_id":"sid-1","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$TMP")

# --- 1. the scanner
SCAN=$("$HOOK" scan "$DIR" 20)
check "finished agent read from end_turn" 'echo "$SCAN" | grep -q "^fin finished"'
check "fresh pending agent is pending" 'echo "$SCAN" | grep -q "^pend pending"'
check "3 h idle agent is stale" 'echo "$SCAN" | grep -q "^hung stale"'
check "last tool is reported" 'echo "$SCAN" | grep "^hung" | grep -q "WebFetch(https://example.org/paper)"'

# --- 2. stop: refused once per pending agent, with the watchdog command; never for a finished one; then passes
OUT=$(printf '%s' "$STDIN" | "$HOOK" stop 2>&1); RC=$?
check "stop refused while agents pend (rc 2)" '[ "$RC" -eq 2 ]'
check "stop names both pending agents" 'echo "$OUT" | grep -q "agent pend" && echo "$OUT" | grep -q "agent hung"'
check "stop does not name the finished agent" '! echo "$OUT" | grep -q "agent fin -"'
check "stop hands over the watchdog command" 'echo "$OUT" | grep -q "agent-watch-hooks.sh watchdog all"'
OUT2=$(printf '%s' "$STDIN" | "$HOOK" stop 2>&1); RC2=$?
check "stop refuses only once per agent" '[ "$RC2" -eq 0 ] && [ -z "$OUT2" ]'
rec new "$TU"
OUT3=$(printf '%s' "$STDIN" | "$HOOK" stop 2>&1); RC3=$?
check "a NEW pending agent is refused once more" '[ "$RC3" -eq 2 ] && echo "$OUT3" | grep -q "agent new" && ! echo "$OUT3" | grep -q "agent pend"'
check "stop with no subagents directory passes" '[ "$(printf "{\"transcript_path\":\"/nope/x.jsonl\",\"session_id\":\"s\"}" | "$HOOK" stop 2>&1; echo rc=$?)" = "rc=0" ]'

# --- 3. prompt: warns on the stale one only
OUT=$(printf '%s' "$STDIN" | "$HOOK" prompt 2>&1); RC=$?
check "prompt exits 0" '[ "$RC" -eq 0 ]'
check "prompt flags the hung agent" 'echo "$OUT" | grep -q "agent hung is PROBABLY HUNG"'
check "prompt is quiet about pending and finished" '! echo "$OUT" | grep -q "pend\|fin "'

# --- 4. watchdog: exits 0 when the watched agent finishes, 3 when it stalls, 4 at the cap (fast tick)
D2="$TMP/w"; mkdir -p "$D2"
printf '%s\n%s\n' "$TU" "$TR" > "$D2/agent-a.jsonl"
( sleep 0.5; printf '%s\n' "$END" >> "$D2/agent-a.jsonl" ) &
OUT=$("$HOOK" watchdog a 20 --dir "$D2" --tick 0.1); RC=$?
check "watchdog exits 0 on finish" '[ "$RC" -eq 0 ] && echo "$OUT" | grep -q finished'
printf '%s\n%s\n' "$TU" "$TR" > "$D2/agent-b.jsonl"; touch -d '-10 minutes' "$D2/agent-b.jsonl"
OUT=$("$HOOK" watchdog b 5 --dir "$D2" --tick 0.1); RC=$?
check "watchdog exits 3 on a stall past the limit" '[ "$RC" -eq 3 ] && echo "$OUT" | grep -q "STALLED"'
OUT=$("$HOOK" watchdog all 5 --dir "$D2" --tick 0.1); RC=$?
check "watchdog all reports the stalled one" '[ "$RC" -eq 3 ] && echo "$OUT" | grep -q "agent b STALLED"'
rm "$D2/agent-b.jsonl"; printf '%s\n%s\n' "$TU" "$TR" > "$D2/agent-c.jsonl"
OUT=$("$HOOK" watchdog c 20 --dir "$D2" --tick 0.1 --cap 0); RC=$?
check "watchdog gives up at the cap (rc 4)" '[ "$RC" -eq 4 ]'

echo "agent-watch-hooks: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
