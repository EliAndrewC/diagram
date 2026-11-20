#!/usr/bin/env bash
# Tests for context-cap-hooks (feature 451 T12, FR-006, plan D8 and D9): a builder's tool call past CONTEXT_CAP_TOKENS (300,000) is
# refused naming its handoff file and the next step, but for that file's Write; a builder under the cap, the main session and a
# defined agent pass; CONTEXT_OK="<reason>" in a Bash command escapes, recorded.
# Run: tests/hooks/test-context-cap-hooks.sh   (exit 0 = all green)
#
# Every case drives the REAL guard (through the shim, `l7r-guard --only context-cap-hooks PreToolUse`) with the REAL payloads pinned in
# rust/guard/src/guards/context_cap_hooks/payloads.json (captured from Claude Code 2.1.325), their cwd and transcript path moved to a
# fixture clone and session; the handoff's Write runs through the WHOLE chain too, since it is the cap's one exit.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
HOOK="$HERE/context-cap-hooks.sh"
PINNED="$REPO/rust/guard/src/guards/context_cap_hooks/payloads.json"
PASS=0; FAIL=0
T=$(mktemp -d); export GUARD_LOG_DIR="$T/guard-log"
unset L7R_EVENTS_DIR L7R_FEATURE_DIRECTORY SPECIFY_FEATURE
trap 'rm -rf "$T"' EXIT

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

AID=af3dc58915037d8d6
C="$T/clone"; S="$T/proj/sess.jsonl"; OWN="$T/proj/sess/subagents/agent-$AID.jsonl"
mkdir -p "$C/.git" "$C/.claude/agents" "$(dirname "$OWN")"
printf -- '---\n' > "$C/.claude/agents/review-x.md"
H="$C/.git/l7r-handoffs/$AID.md"

context() {  # context <tokens>: the builder's last model call
  printf '{"type":"assistant","message":{"id":"m","usage":{"input_tokens":2,"cache_read_input_tokens":%s,"cache_creation_input_tokens":0}}}\n' "$(($1 - 2))" > "$OWN"
}
payload() {  # payload <builder|main|defined> <tool> <tool_input json>
  jq -c --arg w "$1" --arg tool "$2" --argjson ti "$3" --arg cwd "$C" --arg tp "$S" \
    '.[$w] | .cwd = $cwd | .transcript_path = $tp | .tool_name = $tool | .tool_input = $ti' "$PINNED"
}
run() {  # run <who> <tool> <tool_input json>: OUT and RC
  OUT=$(payload "$1" "$2" "$3" | "$HOOK" pretool 2>&1); RC=$?
}
bash_in() { jq -nc --arg c "$1" '{command: $c}'; }

echo "1. a builder past the cap is refused, every tool, naming its handoff and the next step"
context 310000
run builder Bash "$(bash_in 'make quick')"
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q '310000 tokens, past the cap of 300000' && ok "a Bash call past the cap is refused" || no "the call passed" "(rc=$RC: $OUT)"
printf '%s' "$OUT" | grep -qF "$H" && printf '%s' "$OUT" | grep -q 'Stop, and reply with that path' && ok "...naming the handoff file and the next step" || no "the refusal names no handoff" "($OUT)"
ls "$GUARD_LOG_DIR" 2>/dev/null | grep -q . && grep -lq 'past-cap' "$GUARD_LOG_DIR"/* && ok "...and the firing is logged" || no "no guard-log record"
run builder Edit "$(jq -nc --arg f "$C/x.rs" '{file_path: $f, old_string: "a", new_string: "b"}')"
[ "$RC" -eq 2 ] && ok "an Edit past the cap is refused" || no "the Edit passed" "(rc=$RC)"

echo "2. its handoff's Write passes, alone and through the whole chain; another file does not"
WRITE=$(jq -nc --arg f "$H" '{file_path: $f, content: "done: T12 red; left: the green"}')
run builder Write "$WRITE"
[ "$RC" -eq 0 ] && ok "the handoff's Write passes" || no "the handoff's Write refused" "(rc=$RC: $OUT)"
grep -lq '"handoff"' "$GUARD_LOG_DIR"/* && ok "...recorded" || no "the handoff's pass left no record"
OUT=$(payload builder Write "$WRITE" | "$REPO/scripts/hooks/l7r-guard.sh" PreToolUse 2>&1); RC=$?
[ "$RC" -eq 0 ] && ok "the handoff's Write passes every guard of the chain" || no "a guard of the chain refused the handoff" "(rc=$RC: $OUT)"
OUT=$(payload builder Write "$(jq -nc --arg f "$C/.git/l7r-handoffs/T12-$AID.md" '{file_path: $f, content: "done; left"}')" | "$REPO/scripts/hooks/l7r-guard.sh" PreToolUse 2>&1); RC=$?
[ "$RC" -eq 0 ] && ok "...and so does the task-named handoff a real builder is given (T<n>-<agent id>.md)" || no "a guard of the chain refused the task-named handoff" "(rc=$RC: $OUT)"
OUT=$(payload builder Write "$(jq -nc --arg f "$C/notes.md" '{file_path: $f, content: "x"}')" | "$REPO/scripts/hooks/l7r-guard.sh" PreToolUse 2>&1); RC=$?
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q 'past the cap' && ok "...while the chain refuses any other Write (the guard is registered)" || no "the chain let another Write through" "(rc=$RC: $OUT)"
run builder Write "$(jq -nc --arg f "$C/.git/l7r-handoffs/a0000000000000000.md" '{file_path: $f, content: "x"}')"
[ "$RC" -eq 2 ] && ok "another agent's handoff is refused" || no "another agent's handoff passed" "(rc=$RC)"

echo "3. a builder under the cap passes"
context 250000
run builder Bash "$(bash_in 'make quick')"
[ "$RC" -eq 0 ] && ok "a builder at 250k passes" || no "a builder under the cap refused" "(rc=$RC: $OUT)"

echo "4. the main session, and a defined agent past the cap, pass"
context 900000
run main Bash "$(bash_in 'make quick')"
[ "$RC" -eq 0 ] && ok "the main session passes" || no "the main session refused" "(rc=$RC: $OUT)"
OUT=$(payload builder Bash "$(bash_in 'make quick')" | jq -c '.agent_type = "review-x"' | "$HOOK" pretool 2>&1); RC=$?
[ "$RC" -eq 0 ] && ok "a defined agent past the cap passes" || no "a defined agent refused" "(rc=$RC: $OUT)"

echo "5. the escape"
before=$(ls "$GUARD_LOG_DIR" | wc -l)
run builder Bash "$(bash_in 'CONTEXT_OK="the landing needs it" make land')"
[ "$RC" -eq 0 ] && ok "CONTEXT_OK with a reason passes" || no "the escape was refused" "(rc=$RC: $OUT)"
[ "$(ls "$GUARD_LOG_DIR" | wc -l)" -gt "$before" ] && grep -lq 'the landing needs it' "$GUARD_LOG_DIR"/* && ok "...and is recorded" || no "the escape left no record"
run builder Bash "$(bash_in 'make quick CONTEXT_OK')"
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q 'CONTEXT_OK with no reason' && ok "a bare CONTEXT_OK is refused" || no "a bare escape passed" "(rc=$RC)"

echo
echo "context-cap-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
