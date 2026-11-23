#!/usr/bin/env bash
# Tests for builder-stop-hooks (feature 451 T84): a builder the session dispatched for a started task (its brief `451 T84: ...`) stops
# only once the gate says its plan section is decided - `l7r-gate plan decided <root> <feature> <task>`, a stand-in gate script here -
# else its SubagentStop is answered `decision: block` naming `make decide` and the review to dispatch; the main session, a defined
# agent and `STOP_OK="<reason>"` in its final message pass.
# Run: tests/hooks/test-builder-stop-hooks.sh   (exit 0 = all green)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/builder-stop-hooks.sh"
PASS=0; FAIL=0
T=$(mktemp -d); export GUARD_LOG_DIR="$T/guard-log"
trap 'rm -rf "$T"' EXIT
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

C="$T/clone"; S="$T/p/sess.jsonl"; OWN="$T/p/sess/subagents/agent-a1.jsonl"
mkdir -p "$C/.git" "$C/.claude/agents" "$C/specs/451-x" "$C/scripts/gates" "$(dirname "$OWN")"
printf 'agent\n' > "$C/.claude/agents/spec-fidelity.md"
printf -- '- [ ] T84 the stop\n' > "$C/specs/451-x/tasks.md"
printf '{"feature": "451-x", "task": "T84"}\n' > "$C/.git/task-starts.jsonl"
: > "$S"; : > "$OWN"
printf '{"agentType":"general-purpose","description":"451 T84: the stop","spawnDepth":1}\n' > "${OWN%.jsonl}.meta.json"
gate() {  # gate <exit> <text>: the stand-in gate's answer, its text kept in a file so its backticks are never run
  printf '%s\n' "$2" > "$C/gate-said"
  printf 'cat "%s"\nexit %s\n' "$C/gate-said" "$1" > "$C/scripts/gates/l7r-gate.sh"
}
stop() {  # stop <agent_type> <final message> [main]: OUT and RC
  local p; p=$(jq -nc --arg c "$C" --arg s "$S" --arg t "$1" --arg m "$2" \
    '{hook_event_name: "SubagentStop", agent_id: "a1", agent_type: $t, cwd: $c, transcript_path: $s, last_assistant_message: $m}')
  [ "${3:-}" = main ] && p=$(jq -c 'del(.agent_id)' <<<"$p")
  OUT=$(printf '%s' "$p" | "$HOOK" SubagentStop 2>&1); RC=$?
}

echo "== a builder whose section is not decided is held"
# the gate's why as l7r-gate plan decided words it (rust/gate/crates/plan/src/plan/task.rs), so the block renders as sessions read it
gate 1 '451-x T84: its plan section carries no current CLEAR verdict - run `make decide F=451 T=T84` and dispatch the MODE 4 review it prints yourself, then fix what it finds'
stop general-purpose "done"
if grep -q '"decision"' <<<"$OUT" && grep -q 'block' <<<"$OUT" && grep -q 'make decide F=451 T=T84' <<<"$OUT"; then ok "held, told the decide and the review"; else no "held" "rc=$RC $OUT"; fi
# 451 T177 (message-check): the why carries the decide and the review, so the block says them once
[ "$(grep -o 'make decide' <<<"$OUT" | wc -l)" = 1 ] && ok "...said once" || no "...said once" "$OUT"
grep -q '"blocked"' "$GUARD_LOG_DIR"/* 2>/dev/null && ok "the hold recorded" || no "the hold recorded"

echo "== the stops that pass"
stop general-purpose "done" main
[ -z "$OUT" ] && [ "$RC" = 0 ] && ok "the main session" || no "the main session" "rc=$RC $OUT"
stop spec-fidelity "done"
[ -z "$OUT" ] && [ "$RC" = 0 ] && ok "a defined agent" || no "a defined agent" "rc=$RC $OUT"
stop general-purpose 'handoff written. STOP_OK="the context cap is near"'
[ -z "$OUT" ] && [ "$RC" = 0 ] && ok "STOP_OK with a reason" || no "STOP_OK" "rc=$RC $OUT"
gate 0 ""
stop general-purpose "done"
[ -z "$OUT" ] && [ "$RC" = 0 ] && ok "a decided section" || no "a decided section" "rc=$RC $OUT"

echo; echo "builder-stop-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" = 0 ]
