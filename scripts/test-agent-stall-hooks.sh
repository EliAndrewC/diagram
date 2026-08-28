#!/usr/bin/env bash
# test-agent-stall-hooks.sh - prove agent-stall-hooks.sh reports a stalled subagent and stays quiet otherwise.
# (GUARD_EDIT_OK: the companion of a NEW guard, feature 138)
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/agent-stall-hooks.sh"
pass=0 fail=0
ok() { pass=$((pass+1)); }
bad() { fail=$((fail+1)); echo "FAIL: $1"; }
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
D="$TMP/sess/subagents"; mkdir -p "$D"
rec() { printf '{"type":"%s","message":{"role":"%s","content":"x"}}\n' "$1" "$1"; }
# 1. stalled: last record `user`, mtime 10 min old
{ rec assistant; rec user; } > "$D/agent-stall1.jsonl"; touch -d '-600 seconds' "$D/agent-stall1.jsonl"
# 2. finished: last record `assistant`, mtime 10 min old
{ rec user; rec assistant; } > "$D/agent-done1.jsonl"; touch -d '-600 seconds' "$D/agent-done1.jsonl"
# 3. alive: last record `user` but fresh
{ rec assistant; rec user; } > "$D/agent-live1.jsonl"
# 4. ancient: last record `user`, 3 days old - ignored
{ rec assistant; rec user; } > "$D/agent-old1.jsonl"; touch -d '-3 days' "$D/agent-old1.jsonl"
out=$("$HOOK" check "$D")
grep -q "STALLED stall1" <<<"$out" && ok || bad "the stalled agent is reported"
grep -q "done1" <<<"$out" && bad "a finished agent is not reported" || ok
grep -q "live1" <<<"$out" && bad "a fresh agent is not reported" || ok
grep -q "old1" <<<"$out" && bad "an ancient transcript is ignored" || ok
grep -q "TaskStop" <<<"$out" && ok || bad "the report says what to do"
# 5. prompt mode reads transcript_path from the hook JSON and derives the subagents dir
out=$(printf '{"transcript_path":"%s/sess.jsonl","session_id":"sess"}' "$TMP" | "$HOOK" prompt)
grep -q "STALLED stall1" <<<"$out" && ok || bad "prompt mode finds the session's subagents dir"
# 6. prompt mode is silent with no stalls
rm "$D/agent-stall1.jsonl"; out=$(printf '{"transcript_path":"%s/sess.jsonl"}' "$TMP" | "$HOOK" prompt)
[ -z "$out" ] && ok || bad "prompt mode is silent when nothing is stalled"
# 7. prompt mode with no transcript_path exits 0 silently
out=$(printf '{}' | "$HOOK" prompt); rc=$?; [ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "no transcript_path: silent, rc 0"
# 8. the stale threshold is honored
{ rec assistant; rec user; } > "$D/agent-stall2.jsonl"; touch -d '-100 seconds' "$D/agent-stall2.jsonl"
out=$("$HOOK" check "$D"); grep -q stall2 <<<"$out" && bad "100 s is under the 300 s threshold" || ok
out=$(AGENT_STALE_S=60 "$HOOK" check "$D"); grep -q stall2 <<<"$out" && ok || bad "AGENT_STALE_S lowers the threshold"
# 9. watch mode reports once, then goes quiet (two ticks)
out=$(AGENT_STALE_S=60 AGENT_TICK_S=0.2 timeout 1 "$HOOK" watch "$D"); n=$(grep -c "STALLED stall2" <<<"$out")
[ "$n" -eq 1 ] && ok || bad "watch reports a stall exactly once (got $n)"
# 10. an acknowledged stall is never reported again
"$HOOK" ack "$D" stall2; out=$(AGENT_STALE_S=60 "$HOOK" check "$D"); grep -q stall2 <<<"$out" && bad "an acked stall is silent" || ok
echo "agent-stall-hooks: $pass passed, $fail failed"; [ $fail -eq 0 ]
