#!/usr/bin/env bash
# test-engine-freeze-hooks.sh - prove engine-freeze-hooks.sh refuses an engine edit while a map review this session
# launched is unfinished (the 2026-09-27 feature 261 shape), stalled or not, and passes it once the review is done,
# stopped and acked, or when the edit, the agent or the tree is not the guard's business (feature 429).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
HOOK="$REPO/scripts/hooks/engine-freeze-hooks.sh"
PASS=0; FAIL=0
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
export GUARD_LOG_DIR="$T/guard-log"

# A diagram-shaped clone: delta.py (the engine list) copied from this repository, an engine module, a doc, a test.
C=$T/clone
git init -q "$C"
mkdir -p "$C/l7r/diagram/ci" "$C/l7r/diagram/settlement" "$C/docs" "$C/tests" "$C/pool/hamlets/sawada"
cp "$REPO/l7r/diagram/ci/delta.py" "$C/l7r/diagram/ci/delta.py"
SESSION=$T/proj/sess; SUB=$SESSION/subagents; mkdir -p "$SUB"

agent() { # agent <id> <type> <last record json> [finished]
  printf '{"agentType":"%s"%s}' "$2" "${4:+,\"finished\":true}" > "$SUB/agent-$1.meta.json"
  printf '{"type":"user","message":{"content":"go"}}\n%s\n' "$3" > "$SUB/agent-$1.jsonl"
}
MIDTOOL='{"type":"assistant","message":{"stop_reason":"tool_use","content":[{"type":"tool_use"}]}}'
RESULT='{"type":"user","message":{"content":[{"type":"tool_result"}]}}'
DONE='{"type":"assistant","message":{"stop_reason":"end_turn","content":[{"type":"text","text":"PASS"}]}}'

edit() { # edit <path> [tool]
  OUT=$(printf '{"session_id":"t","cwd":"%s","transcript_path":"%s.jsonl","tool_name":"%s","tool_input":{"file_path":"%s","old_string":"a","new_string":"b"}}' \
        "$C" "$SESSION" "${2:-Edit}" "$1" | "$HOOK" pretool 2>&1); RC=$?
}
check() { if [ "$2" = "$3" ]; then printf 'ok    %s (rc=%s)\n' "$1" "$3"; PASS=$((PASS+1));
          else printf 'FAIL  %s (expected rc=%s, got rc=%s)\n      out: %s\n' "$1" "$2" "$3" "$OUT"; FAIL=$((FAIL+1)); fi; }
says() { case "$OUT" in *"$2"*) printf 'ok    %s\n' "$1"; PASS=$((PASS+1));; *) printf 'FAIL  %s - text lacks: %s\n      out: %s\n' "$1" "$2" "$OUT"; FAIL=$((FAIL+1));; esac; }

ENG=$C/l7r/diagram/settlement/lanes.py
edit "$ENG";                                  check "no review running: an engine edit passes" 0 "$RC"

agent a1 glyph-check "$MIDTOOL"
edit "$ENG";                                  check "a glyph-check mid tool call refuses an engine edit" 2 "$RC"
says "the refusal names the running review" "a1 glyph-check live"
says "the refusal names the route" "once every review has returned"
edit "$ENG" Write;                            check "Write is refused too" 2 "$RC"
edit "$C/pool/hamlets/sawada/sawada.gen.py";  check "a pool gen is engine: refused" 2 "$RC"
edit "$C/pool/hamlets/sawada/sawada.json";    check "a pool manifest is engine: refused" 2 "$RC"
edit "$C/docs/usage.md";                      check "a doc edit passes" 0 "$RC"
edit "$C/tests/test_lanes.py";                check "a test edit passes" 0 "$RC"
edit "$C/l7r/diagram/ci/state.py";            check "ci/ is not engine: passes" 0 "$RC"
edit "/tmp/scratch/lanes.py";                 check "a draft outside any tree passes" 0 "$RC"

agent a1 glyph-check "$DONE"
edit "$ENG";                                  check "the review ended its turn: the edit passes" 0 "$RC"
agent a1 glyph-check "$MIDTOOL" finished
edit "$ENG";                                  check "meta says finished: the edit passes" 0 "$RC"

agent a2 settlement-review "$RESULT"
edit "$ENG";                                  check "a review awaiting its next turn refuses" 2 "$RC"
touch -d '20 minutes ago' "$SUB/agent-a2.jsonl"
edit "$ENG";                                  check "a STALLED review still refuses" 2 "$RC"
says "a stalled review is named with the ack command" "agent-stall-hooks.sh ack $SUB a2"
mkdir -p "$SESSION/stall-ack"; touch "$SESSION/stall-ack/a2"
edit "$ENG";                                  check "stopped and acked: the edit passes" 0 "$RC"

agent a3 source-reader "$MIDTOOL"
edit "$ENG";                                  check "a non-review agent does not freeze the engine" 0 "$RC"
agent a4 fix-check "$MIDTOOL"; touch -d '3 days ago' "$SUB/agent-a4.jsonl"
edit "$ENG";                                  check "a leftover review days old does not count" 0 "$RC"
[ -n "$(ls "$GUARD_LOG_DIR" 2>/dev/null)" ] && { echo "ok    firings are recorded"; PASS=$((PASS+1)); } || { echo "FAIL  no guard-log entry"; FAIL=$((FAIL+1)); }

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
