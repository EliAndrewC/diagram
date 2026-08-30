#!/usr/bin/env bash
# test-pair-hooks.sh - prove the gate/review pairing refuses each half alone, allows the pair, takes the
# override, and does NOT fire on a mention of the commands it guards.
# (GUARD_EDIT_OK: the companion of a NEW guard, feature 151, GM 2026-08-29)
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/pair-hooks.sh"
WATCH="$(cd "$(dirname "$0")" && pwd)/agent-stall-hooks.sh"
pass=0 fail=0
ok() { pass=$((pass+1)); }
bad() { fail=$((fail+1)); echo "FAIL: $1"; }
check() { if eval "$2"; then ok; else bad "$1"; fi; }

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
CLONE="$TMP/clone"; SKILL="$CLONE/.claude/skills/diagram"
mkdir -p "$SKILL/dev/bypass-log" "$CLONE/scripts" "$TMP/proj/sid-1/subagents"
(cd "$CLONE" && git init -q)
: > "$TMP/proj/sid-1.jsonl"
KEY=deadbeefcafe0000
printf 'engine-key:\n\t@printf "%%s" %s\n' "$KEY" > "$SKILL/Makefile"   # the fixture's own key: the test never runs the engine
cp "$WATCH" "$CLONE/scripts/agent-stall-hooks.sh"                        # the guard asks IT whether an agent is pending
DIR="$TMP/proj/sid-1/subagents"

stdin_for() { printf '{"tool_name":"%s","tool_input":%s,"transcript_path":"%s","session_id":"sid-1","cwd":"%s"}' "$1" "$2" "$TMP/proj/sid-1.jsonl" "$CLONE"; }
run_pretool() { ( cd "$CLONE" && printf '%s' "$1" | "$HOOK" pretool 2>&1 ); }
rc_pretool() { ( cd "$CLONE" && printf '%s' "$1" | "$HOOK" pretool >/dev/null 2>&1 ); echo $?; }

GATE=$(stdin_for Bash '{"command":"make done"}')
REVIEW=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"review the map"}')

# --- 1. neither half runs alone: the gate is CORRECTED into the pair, the review is refused --------
# GUARD_EDIT_OK: feature 164 - the gate branch no longer spends a round trip telling the session to
# type `make verify`; it rewrites the command into it (GM 2026-08-30). The RULE is unchanged - the
# two still run together - but what used to not happen at all now happens correctly. 13 firings of
# the old refusal, 7 escaped with PAIR_OK in the very next call.
GATE_FULL=$(stdin_for Bash '{"command":"make done FULL=1"}')
check "the gate alone is REWRITTEN into the paired command" 'run_pretool "$GATE" | python3 -c "
import json,sys
try: sys.exit(0 if json.load(sys.stdin)[\"hookSpecificOutput\"][\"updatedInput\"][\"command\"] == \"make verify\" else 1)
except Exception: sys.exit(1)"'
check "...and the correction says to dispatch the review in the same turn" 'run_pretool "$GATE" | grep -q "SAME TURN"'
check "...and still names the override for a one-sided case" 'run_pretool "$GATE" | grep -q "PAIR_OK"'
check "a shape that cannot convert is still REFUSED" '[ "$(rc_pretool "$GATE_FULL")" -eq 2 ]'
check "...naming the paired command" 'run_pretool "$GATE_FULL" | grep -q "make verify"'
check "a settlement-review alone is refused" '[ "$(rc_pretool "$REVIEW")" -eq 2 ]'

# --- 2. a MENTION is not an invocation ------------------------------------------------------------
# THE SHAPE THAT BLOCKED THIS FEATURE'S OWN TIME AUDIT, four times in one day: a guard that greps the
# whole command string fires on a script that merely TALKS about the target - an analysis heredoc, a
# grep over the docs, this very test file. A guard nobody can work beside gets worked around.
MENTION=$(stdin_for Bash '{"command":"python3 - <<PY\nprint(\"count the make done runs in the log\")\nPY"}')
QUOTED=$(stdin_for Bash '{"command":"grep -n \"make done\" docs/iteration-loop.md"}')
OTHER=$(stdin_for Bash '{"command":"make quick"}')
check "a heredoc that TALKS about the gate passes" '[ "$(rc_pretool "$MENTION")" -eq 0 ]'
check "a quoted mention passes" '[ "$(rc_pretool "$QUOTED")" -eq 0 ]'
check "another target passes" '[ "$(rc_pretool "$OTHER")" -eq 0 ]'

# ...AND THE SAME RULE ON THE AGENT SIDE, which the guard's own author got wrong (2026-08-29). The
# branch greped the whole tool_input for "settlement-review", so a `spec-fidelity` dispatch that merely
# QUOTED the referent was blocked - a spec review, which owes no gate at all and cannot have one,
# because there is no map. The subagent TYPE is the invocation; the prompt is prose.
SPECREV=$(stdin_for Agent '{"subagent_type":"spec-fidelity","prompt":"the referent is the settlement-review pass of 2026-08-29; judge the spec"}')
READER=$(stdin_for Agent '{"subagent_type":"source-reader","prompt":"read what a settlement-review cited"}')
check "a spec-fidelity dispatch that MENTIONS a settlement-review passes" '[ "$(rc_pretool "$SPECREV")" -eq 0 ]'
check "a source-reader that mentions one passes" '[ "$(rc_pretool "$READER")" -eq 0 ]'
check "...while a real settlement-review is still refused" '[ "$(rc_pretool "$REVIEW")" -eq 2 ]'

# --- 3. the pair: a pending review lets the gate through ------------------------------------------
TU='{"type":"assistant","message":{"role":"assistant","stop_reason":"tool_use","content":[{"type":"tool_use","name":"Read","input":{}}]}}'
TR='{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"..."}]}}'
# the launch record names the agent; the tool_result must stay LAST, because that is exactly what
# `agent-stall-hooks.sh pending` reads to mean "this agent is still awaiting its next turn"
printf '{"prompt":"settlement-review of the map"}\n%s\n%s\n' "$TU" "$TR" > "$DIR/agent-rev.jsonl"
check "with a review PENDING the gate runs" '[ "$(rc_pretool "$GATE")" -eq 0 ]'
check "...and the gate records its key" 'grep -q "gate_key" "$CLONE/.git/pairing-state.json"'

# --- 4. with a gate recorded, the review dispatch is allowed --------------------------------------
rm -f "$DIR/agent-rev.jsonl"
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
check "with a green record the review runs" '[ "$(rc_pretool "$REVIEW")" -eq 0 ]'

# --- 5. the override runs the command and leaves its reason ---------------------------------------
rm -f "$CLONE/.git/pairing-state.json" "$CLONE/.git/verification-state.json"
OVER=$(stdin_for Bash '{"command":"PAIR_OK=\"docs only, no map ink\" make done"}')
check "the override runs the gate alone" '[ "$(rc_pretool "$OVER")" -eq 0 ]'
check "...and logs its reason for the audit" 'grep -rql "docs only, no map ink" "$SKILL/dev/bypass-log"'

# --- 6. stop: a half-open pairing is refused ONCE --------------------------------------------------
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
rm -f "$CLONE/.git/pairing-state.json"
STOP=$(printf '{"transcript_path":"%s","session_id":"sid-1","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$CLONE")
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); FIRST=$?
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); SECOND=$?
check "stop refuses a half-open pairing" '[ "$FIRST" -eq 2 ]'
check "...and never twice for the same content" '[ "$SECOND" -eq 0 ]'

# --- 7. the documented remedy CLEARS the stop hook -------------------------------------------------
# The stop message says "record why it is not owed: PAIR_OK=... on your next gate run". Before
# 2026-08-29 doing exactly that logged a bypass and changed nothing stop reads, so the hook fired
# again and repeated the remedy the session had just used. An escape that cannot clear its own guard
# is the shape this project's guard rules single out.
rm -f "$CLONE/.git/pairing-state.json"
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
WAIVE=$(stdin_for Bash '{"command":"PAIR_OK=\"the review read these exact maps and nothing moved\" make done"}')
check "the waived gate runs" '[ "$(rc_pretool "$WAIVE")" -eq 0 ]'
check "...and records the waiver against this content" 'grep -q "waived_key" "$CLONE/.git/pairing-state.json"'
STOP2=$(printf '{"transcript_path":"%s","session_id":"sid-2","cwd":"%s"}' "$TMP/proj/sid-2.jsonl" "$CLONE")
( cd "$CLONE" && printf '%s' "$STOP2" | "$HOOK" stop >/dev/null 2>&1 ); WAIVED=$?
check "...so stop does not fire on content the gate waived" '[ "$WAIVED" -eq 0 ]'
# and the waiver is per-CONTENT: a waiver recorded against OTHER content does not cover this one, so
# an engine edit after a waived gate is guarded again rather than riding the old waiver
printf '{"waived_key":"deadbeefdeadbeef"}' > "$CLONE/.git/pairing-state.json"
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
( cd "$CLONE" && printf '%s' "$STOP2" | "$HOOK" stop >/dev/null 2>&1 ); OTHER=$?
check "...but a waiver for OTHER content does not cover this one" '[ "$OTHER" -eq 2 ]'

printf '\ntest-pair-hooks: %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
