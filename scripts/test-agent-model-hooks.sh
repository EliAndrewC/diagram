#!/bin/bash
# Tests for agent-model-hooks.sh - an ad-hoc agent dispatch names its model, or is refused (feature 252).
# Run: scripts/test-agent-model-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 252 - a NEW guard's companion suite.
#
# Every case drives the REAL hook with a REAL payload against a fixture repository, because a grep proves
# a call site exists and not that it fires.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# GUARD_EDIT_OK: feature 252 - AGENT_MODEL_HOOK lets the proof-of-firing run this suite against a MUTATED copy
# of the guard (its refusal removed) and watch it go red, without touching the real file.
HOOK="${AGENT_MODEL_HOOK:-$HERE/agent-model-hooks.sh}"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT

FIX="$T/clone"; mkdir -p "$FIX/.claude/agents"; git -C "$FIX" init -q 2>/dev/null
printf -- '---\nname: quote-check\nmodel: opus\neffort: medium\n---\nbody\n' > "$FIX/.claude/agents/quote-check.md"

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
dispatch() { # dispatch <json tool_input> -> rc in $T/rc, stderr in $T/err, stdout returned
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t-agent-model","cwd":sys.argv[2],"tool_name":"Agent","tool_input":json.loads(sys.argv[1])}))' "$1" "$FIX" \
    | ( cd "$FIX" && "$HOOK" pretool 2>"$T/err" ); echo $? > "$T/rc"
}
rc() { cat "$T/rc"; }
logged() { grep -rlq "$1" "$GUARD_LOG_ROOT" 2>/dev/null; }

echo "1. what is refused"
dispatch '{"subagent_type":"general-purpose","prompt":"read three pages","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "a general-purpose dispatch with no model is refused" || no "it was allowed" "(rc=$(rc))"
grep -q 'sonnet' "$T/err" && grep -q 'opus' "$T/err" && ok "...the message names both models" || no "the message does not name both models"
grep -qi 'session' "$T/err" && ok "...says the agent would run on the SESSION's model" || no "the message does not say whose model it would run on"
grep -qi 're-send' "$T/err" && ok "...and says to re-send the same dispatch" || no "the message does not say what to do"
grep -q 'to read, fetch, translate or extract' "$T/err" && grep -q 'for anything that judges' "$T/err" && ok "...in the rule's own words" || no "the rule is not reiterated"
logged no-model && ok "...recorded blocked/no-model" || no "no-model not recorded"
dispatch '{"prompt":"no type at all","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "an omitted subagent_type is the general-purpose agent, and is refused" || no "an omitted type was allowed" "(rc=$(rc))"
dispatch '{"subagent_type":"Explore","prompt":"find the callers","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "a built-in type with no agent file (Explore) is refused" || no "Explore was allowed" "(rc=$(rc))"
dispatch '{"subagent_type":"general-purpose","model":"","prompt":"an empty model is no model","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "an EMPTY model is no model" || no "an empty model was allowed" "(rc=$(rc))"

echo "2. what passes"
dispatch '{"subagent_type":"general-purpose","model":"sonnet","prompt":"read three pages","description":"x"}'
[ "$(rc)" -eq 0 ] && [ ! -s "$T/err" ] && ok "the same dispatch WITH a model passes, silently" || no "a named model was refused" "(rc=$(rc))"
logged model-named && ok "...recorded permitted/model-named" || no "model-named not recorded"
dispatch '{"subagent_type":"general-purpose","model":"fable","prompt":"a deliberate choice","description":"x"}'
[ "$(rc)" -eq 0 ] && ok "ANY named model passes - the choice is the caller's" || no "a named model was second-guessed" "(rc=$(rc))"
dispatch '{"subagent_type":"quote-check","prompt":"check hamlets","description":"x"}'
[ "$(rc)" -eq 0 ] && ok "a type with an agent file passes with no model - its file pins its tier" || no "a pinned type was refused" "(rc=$(rc))"
logged pinned-type && ok "...recorded permitted/pinned-type" || no "pinned-type not recorded"
dispatch '{"subagent_type":"fork","prompt":"continue this","description":"x"}'
[ "$(rc)" -eq 0 ] && ok "a fork passes: a model on it is ignored by the harness" || no "a fork was refused" "(rc=$(rc))"
logged fork-inherits && ok "...and is RECORDED permitted/fork-inherits, so the spend shows in the audit" || no "fork-inherits not recorded"
out=$(printf '{"session_id":"t-agent-model","tool_name":"Bash","tool_input":{"command":"make done"}}' | ( cd "$FIX" && "$HOOK" pretool 2>/dev/null )); r=$?
[ "$r" -eq 0 ] && [ -z "$out" ] && ok "a Bash call is ignored" || no "a Bash call was not ignored" "(rc=$r)"
out=$(printf 'not json' | ( cd "$FIX" && "$HOOK" pretool 2>/dev/null )); r=$?
[ "$r" -eq 0 ] && ok "a payload that is not JSON never blocks" || no "a broken payload blocked" "(rc=$r)"

echo "3. the rule is stated once, and the docs say the same"
ROOT="$(dirname "$HERE")"
grep -q 'to read, fetch, translate or extract' "$ROOT/CLAUDE.md" && grep -q 'for anything that judges' "$ROOT/CLAUDE.md" && ok "root CLAUDE.md carries the same two clauses the message reads from agent-model-rule.txt" || no "CLAUDE.md and the message's rule have drifted apart"
"$HOOK" bogus >/dev/null 2>&1; [ $? -eq 1 ] && ok "an unknown mode is an error, not a pass" || no "an unknown mode passed"

echo
echo "test-agent-model-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
