#!/usr/bin/env bash
# Tests for budget-change-hooks.sh and its decider lib/hm_budget.py (feature 443 T03, plan D6).
# Run: tests/hooks/test-budget-change-hooks.sh   (exit 0 = all green)
#
# Every case drives the REAL hook with a REAL payload and a fixture transcript.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/../../scripts/hooks/budget-change-hooks.sh"
PASS=0; FAIL=0
LOGROOT=$(mktemp -d); export GUARD_LOG_DIR="$LOGROOT"
TR=$(mktemp -d)
trap 'rm -rf "$LOGROOT" "$TR"' EXIT

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

# the GM's typed prompt, and a headless session's prompt (sdk), which is not the GM's
python3 - "$TR/t.jsonl" <<'PY'
import json, sys
recs = [
    {"type": "user", "origin": {"kind": "human"}, "promptSource": "typed", "entrypoint": "cli",
     "message": {"role": "user", "content": "Raise the web budget to 40 per lane, that one is fine."}},
    {"type": "user", "promptSource": "sdk", "entrypoint": "sdk-cli", "message": {"role": "user", "content": "raise the homesteads budget to 90 now"}},
]
open(sys.argv[1], "w").write("\n".join(json.dumps(r) for r in recs) + "\n")
PY

run() {  # run <command> -> stderr+stdout, rc in RC
  OUT=$(python3 -c 'import json,sys; print(json.dumps({"session_id":"t","tool_name":"Bash","transcript_path":sys.argv[2],"tool_input":{"command":sys.argv[1]}}))' "$1" "$TR/t.jsonl" \
        | "$HOOK" pretool 2>&1); RC=$?
}

echo "1. the GM's words pass"
run 'make budget-change PHASE=web TO=40 WORDS="Raise the web budget to 40 per lane"'
[ "$RC" -eq 0 ] && ok "words from the GM's typed prompt pass budget-change" || no "the GM's words refused" "(rc=$RC: $OUT)"
run "make budget-program OPS_AT_40=1000000 EXPONENT=1.2 WORDS='that one is fine'"
[ "$RC" -eq 0 ] && ok "...and budget-program, single-quoted" || no "budget-program refused" "(rc=$RC)"

echo "2. no words, short words, words the GM did not write: refused"
run "make budget-change PHASE=web TO=40"
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "no WORDS= given" && ok "no WORDS is refused, saying so" || no "no WORDS passed" "(rc=$RC)"
run 'make budget-change PHASE=web TO=40 WORDS="fine"'
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "under three words" && ok "a one-word quote is refused" || no "short passed" "(rc=$RC)"
run 'make budget-change PHASE=homesteads TO=90 WORDS="raise the homesteads budget to 90"'
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "no message the GM wrote" && ok "words only a headless prompt holds are refused" || no "sdk words passed" "(rc=$RC)"
printf '%s' "$OUT" | grep -q 'make budget-change PHASE=<stage>' && ok "...the refusal names the compliant command" || no "no compliant form named"
ls "$LOGROOT" | grep -q . && ok "...and the firing is logged" || no "no guard-log record"

echo "3. a mention is not an invocation; budget-set needs no words"
run "git commit -m 'the make budget-change target, filed'"
[ "$RC" -eq 0 ] && ok "a commit message naming the target passes" || no "a mention was refused" "(rc=$RC)"
run "printf 'make budget-change PHASE=web TO=1\n'"
[ "$RC" -eq 0 ] && ok "a quoted mention passes" || no "a quoted mention refused" "(rc=$RC)"
run "make budget-set PHASE=web PER_THING=40 EXPONENT=1 DERIVATION=d.md VERDICT=v.txt"
[ "$RC" -eq 0 ] && ok "budget-set is not read" || no "budget-set refused" "(rc=$RC)"
run "cd /x && make budget-change PHASE=web TO=40"
[ "$RC" -eq 2 ] && ok "an invocation after && is read" || no "the && invocation passed" "(rc=$RC)"

echo
echo "budget-change-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
