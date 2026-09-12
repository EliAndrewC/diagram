#!/usr/bin/env bash
# test-pair-hooks.sh - prove the gate/review pairing refuses each half alone, allows the pair, takes the
# override, and does NOT fire on a mention of the commands it guards.
# (GUARD_EDIT_OK: the companion of a NEW guard, feature 151, GM 2026-08-29)
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/pair-hooks.sh"
# GUARD_EDIT_OK: feature 164 - this guard RECORDS its firings now (feature 162's log), so the suite
# must write its fixtures to a throwaway directory. Without it the suite pollutes `make audit`, whose
# whole purpose is to price a guard from real firings: 24 fixture entries appeared there the first
# time these conversions ran their suites.
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
trap 'rm -rf "$GUARD_LOG_ROOT"' EXIT

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
# GUARD_EDIT_OK: feature 231 - THE TRIGGER IS SCRIPTED, so the fixture must say which world it is in. A
# review is owed only when a pool manifest moved against main (GM 2026-09-12), and the two scripts that
# decide it live beside the guard, so the fixture carries them and a moved manifest. `moved`/`unmoved`
# switch the world between cases; every case below section 1 runs in the world it names.
cp "$(dirname "$HOOK")/_review_owed.py" "$(dirname "$HOOK")/_review_snapshot.py" "$CLONE/scripts/"
MAPDIR_F="$SKILL/pool/hamlets/testmap"
moved()   { mkdir -p "$MAPDIR_F"; printf '{"meta":{"name":"testmap"}}' > "$MAPDIR_F/testmap.json"; printf '# testmap\n' > "$MAPDIR_F/testmap.notes.md"; }
unmoved() { rm -rf "$SKILL/pool"; }
moved

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
# GUARD_EDIT_OK: feature 212 - a shape `verify` cannot take is RECORDED AND PERMITTED with the
# DISPATCH NOW context, not refused (GM 2026-09-07): the census found the rewrite above fired once
# while every real refusal - eight `make maps`, three detached `make done` - was such a shape.
permitted_with() { # label, payload, text the context must carry
  local out; out=$(run_pretool "$2"); local rc=$?
  if [ "$rc" -eq 0 ] && printf '%s' "$out" | grep -q "DISPATCH NOW" && printf '%s' "$out" | grep -q -- "$3" \
     && ! printf '%s' "$out" | grep -q "updatedInput"; then ok; else bad "$1 (rc=$rc: $out)"; fi
}
rm -f "$CLONE/.git/pairing-state.json"
permitted_with "make done FULL=1 is permitted, told the review is owed, and told it serializes" "$GATE_FULL" "FOREGROUND"
check "...and records the gate key for the pairing" 'grep -q "gate_key" "$CLONE/.git/pairing-state.json"'
MAPS=$(stdin_for Bash '{"command":"make maps SCOPE=all 2>&1 | tail -60"}')
permitted_with "make maps ... | tail is permitted (foreground: the review follows the gate)" "$MAPS" "make verify"
DETACHED=$(stdin_for Bash '{"command":"setsid nohup make done > /tmp/done.log 2>&1 &"}')
permitted_with "a detached make done is permitted and told the review overlaps" "$DETACHED" "detached"
BGGATE=$(stdin_for Bash '{"command":"make maps","run_in_background":true}')
permitted_with "a run_in_background gate counts as detached" "$BGGATE" "detached"
check "...the permit names PAIR_OK for the one-sided case" 'run_pretool "$MAPS" | grep -q "PAIR_OK"'
rm -f "$CLONE/.git/pairing-state.json"
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


# --- 6. NO LAYOUT CHANGE, NO REVIEW (feature 231, GM 2026-09-12) -----------------------------------
# GUARD_EDIT_OK: feature 231 - the new branch and its three properties: the gate runs as typed, the stop
# branch stays quiet, and the waiver is RECORDED with its reason so `make audit` can count it. The
# motivating case is feature 228: one path's `d`, a byte-identical manifest, 18.7 minutes of review.
unmoved
rm -f "$CLONE/.git/pairing-state.json" "$CLONE/.git/verification-state.json"
check "with no manifest moved the gate runs as typed" '[ "$(rc_pretool "$GATE")" -eq 0 ]'
check "...and is NOT rewritten into make verify" '! run_pretool "$GATE" | grep -q "updatedInput"'
check "...and the context says no review is owed" 'run_pretool "$GATE" | grep -q "NO SETTLEMENT-REVIEW OWED"'
check "...and says why, in the words of the script" 'run_pretool "$GATE" | grep -q "no pool manifest moved"'
check "...and the context is valid JSON - a quoting slip here is silent" 'run_pretool "$GATE" | python3 -c "import json,sys; json.load(sys.stdin)"'
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); QUIET=$?
check "...and the stop branch does not fire half-open" '[ "$QUIET" -eq 0 ]'
check "...having recorded the automatic waiver" 'grep -q "waived_key" "$CLONE/.git/pairing-state.json"'
check "...with the reason it was waived for" 'grep -q "no pool manifest moved" "$CLONE/.git/pairing-state.json"'
moved
rm -f "$CLONE/.git/pairing-state.json"
check "...while a MOVED manifest owes the review again" 'run_pretool "$GATE" | grep -q "updatedInput"'
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); OWED=$?
check "...and the stop branch fires on it" '[ "$OWED" -eq 2 ]'

# --- 7. the guard reads THIS SESSION'S CLONE, not the shell's tree (feature 231) -------------------
# GUARD_EDIT_OK: feature 231 - the defect that cost feature 228 a refusal and a half-open stop: the
# session's shell stood in the MIRROR, so the guard keyed and recorded the mirror's tree. The resolver is
# feature 204's - the claim map, read from the payload's session_id - and the mirror's state stays clean.
MIRROR="$TMP/mirror"; mkdir -p "$MIRROR/.clones/.session-clones"; (cd "$MIRROR" && git init -q)
printf '%s' "$CLONE" > "$MIRROR/.clones/.session-clones/sid-1"
rm -f "$CLONE/.git/pairing-state.json" "$MIRROR/.git/pairing-state.json"
# `make done FULL=1`, because it is a shape the guard PERMITS and records - the plain gate is rewritten
# into `make verify` and records nothing, which is not what this case is about.
FROM_MIRROR=$(printf '{"tool_name":"Bash","tool_input":{"command":"make done FULL=1"},"transcript_path":"%s","session_id":"sid-1","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$MIRROR")
CLONE_MAIN="$MIRROR" bash -c 'cd "$1" && printf "%s" "$2" | "$3" pretool >/dev/null 2>&1' _ "$MIRROR" "$FROM_MIRROR" "$HOOK"
check "standing in the mirror, the gate records the pairing state of the CLONE" '[ -f "$CLONE/.git/pairing-state.json" ]'
check "...and never that of the mirror" '[ ! -f "$MIRROR/.git/pairing-state.json" ]'

# --- 8. an ESCAPED review is still a review (feature 231) ------------------------------------------
# GUARD_EDIT_OK: feature 231 - the second half of feature 228's pairing incident: the escaped dispatch
# logged a bypass and recorded nothing, so the stop branch fired half-open on a review that had run.
rm -f "$CLONE/.git/pairing-state.json"
ESCREV=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"PAIR_OK: the gate is running beside this - review the map"}')
check "a review escaped with a reason runs" '[ "$(rc_pretool "$ESCREV")" -eq 0 ]'
check "...and records itself as a review" 'grep -q "review_key" "$CLONE/.git/pairing-state.json"'
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); AFTER_ESC=$?
check "...so the stop branch does not fire half-open on it" '[ "$AFTER_ESC" -eq 0 ]'

printf '\ntest-pair-hooks: %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
