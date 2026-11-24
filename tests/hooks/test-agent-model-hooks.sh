#!/bin/bash
# Tests for the agent-model guard (rust/guard, replayed through its link) - an ad-hoc agent dispatch states its model, or is refused (feature 252):
# sonnet or haiku named for reading work, the session's model - no `model`, a SESSION_MODEL line in the prompt - for judging or building (451 T216),
# and that line only on a type measured to inherit it (451 T217).
# Run: tests/hooks/test-agent-model-hooks.sh   (exit 0 = all green)
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
  jq -nc '{"session_id":"t-agent-model","cwd":$ARGS.positional[1],"tool_name":"Agent","tool_input":($ARGS.positional[0]|fromjson)}' --args -- "$1" "$FIX" \
    | ( cd "$FIX" && "$HOOK" pretool 2>"$T/err" ); echo $? > "$T/rc"
}
rc() { cat "$T/rc"; }
logged() { grep -rlq "$1" "$GUARD_LOG_ROOT" 2>/dev/null; }

echo "1. what is refused"
dispatch '{"subagent_type":"general-purpose","prompt":"read three pages","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "a general-purpose dispatch with no model is refused" || no "it was allowed" "(rc=$(rc))"
grep -q 'model: "sonnet"' "$T/err" && grep -q '^ *SESSION_MODEL: <' "$T/err" && ok "...the message names both compliant forms: sonnet named, or the prompt's SESSION_MODEL line" || no "the message does not name both forms"
grep -q "session's model" "$T/err" && ok "...says the marked dispatch runs on the session's model" || no "the message does not say whose model it would run on"
grep -qi 're-send' "$T/err" && ok "...and says to re-send the same dispatch" || no "the message does not say what to do"
grep -q 'to read, fetch, translate or extract' "$T/err" && grep -q 'for anything that judges or builds' "$T/err" && ok "...in the rule's own words" || no "the rule is not reiterated"
logged no-model && ok "...recorded blocked/no-model" || no "no-model not recorded"
dispatch '{"prompt":"no type at all","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "an omitted subagent_type is the general-purpose agent, and is refused" || no "an omitted type was allowed" "(rc=$(rc))"
dispatch '{"subagent_type":"Explore","prompt":"find the callers","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "a built-in type with no agent file (Explore) is refused" || no "Explore was allowed" "(rc=$(rc))"
dispatch '{"subagent_type":"general-purpose","model":"","prompt":"an empty model is no model","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "an EMPTY model is no model" || no "an empty model was allowed" "(rc=$(rc))"
dispatch '{"subagent_type":"general-purpose","model":"fable","prompt":"review this plan","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "a named fable is refused: a named model does not follow the GM's switch (451 T216)" || no "a named fable was allowed" "(rc=$(rc))"
grep -q 'names `fable`' "$T/err" && grep -qi 'omit' "$T/err" && grep -q '^ *SESSION_MODEL: <' "$T/err" && ok "...the message names the model, says to omit it and gives the line to add" || no "the message does not name the compliant dispatch"
logged judging-model-named && ok "...recorded blocked/judging-model-named" || no "judging-model-named not recorded"
dispatch '{"subagent_type":"Explore","model":"opus","prompt":"SESSION_MODEL: judges the plan section\nreview it","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "a named opus is refused, its SESSION_MODEL line or not" || no "a named opus was allowed" "(rc=$(rc))"
dispatch '{"subagent_type":"general-purpose","prompt":"451 T216: review it\nSESSION_MODEL: judges\n","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "a SESSION_MODEL line with a one-word reason is no decision" || no "a bare marker passed" "(rc=$(rc))"
dispatch '{"subagent_type":"general-purpose","prompt":"the guard reads a SESSION_MODEL: line of the prompt, as the docs say","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "a MENTION of the marker inside a line is not the line" || no "a mention passed" "(rc=$(rc))"

dispatch '{"subagent_type":"Explore","prompt":"451 T217: judge it\nSESSION_MODEL: judges the plan section\n","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "a MARKED Explore is refused: it runs its own definition's model, not the session's (451 T217)" || no "a marked Explore passed" "(rc=$(rc))"
grep -q 'model: "sonnet"' "$T/err" && grep -q 'dispatch `general-purpose`' "$T/err" && ok "...the message names the two routes: sonnet to read, general-purpose to judge or build" || no "the message does not name the two routes"
grep -q 'only `general-purpose`, `Plan` and `claude` inherit' "$T/err" && ok "...and the types that do inherit" || no "the message does not name the inheriting types"
grep -qi 're-send the same' "$T/err" && no "the message tells an Explore to re-send the same dispatch with the line" || ok "...and does not offer the line on the same type"
logged type-not-inheriting && ok "...recorded blocked/type-not-inheriting" || no "type-not-inheriting not recorded"
dispatch '{"subagent_type":"web-fetch","prompt":"SESSION_MODEL: judges the page read\nread it","description":"x"}'
[ "$(rc)" -eq 2 ] && ok "a marked type nobody probed (web-fetch) is refused: the list is what was measured" || no "a marked web-fetch passed" "(rc=$(rc))"
dispatch '{"subagent_type":"Explore","prompt":"find the callers","description":"x"}'
grep -q 'SESSION_MODEL: <' "$T/err" && grep -q 'dispatch `general-purpose`' "$T/err" && ok "an unmarked Explore is offered the line only on general-purpose" || no "an unmarked Explore is offered a line that would be refused"

echo "2. what passes"
for kind in Plan claude; do
  dispatch '{"subagent_type":"'$kind'","prompt":"451 T217: judge it\nSESSION_MODEL: judges the plan section\n","description":"x"}'
  [ "$(rc)" -eq 0 ] && ok "a marked $kind passes: measured to inherit the session's model (451 T217)" || no "a marked $kind was refused" "(rc=$(rc))"
done
dispatch '{"subagent_type":"Explore","model":"sonnet","prompt":"find the callers","description":"x"}'
[ "$(rc)" -eq 0 ] && ok "an Explore naming sonnet passes: the named model is what it runs" || no "Explore on sonnet was refused" "(rc=$(rc))"
dispatch '{"subagent_type":"general-purpose","model":"sonnet","prompt":"read three pages","description":"x"}'
[ "$(rc)" -eq 0 ] && [ ! -s "$T/err" ] && ok "the same dispatch WITH a model passes, silently" || no "a named model was refused" "(rc=$(rc))"
logged model-named && ok "...recorded permitted/model-named" || no "model-named not recorded"
dispatch '{"subagent_type":"general-purpose","model":"haiku","prompt":"describe this page","description":"x"}'
[ "$(rc)" -eq 0 ] && ok "haiku passes too - a reading model" || no "haiku was refused" "(rc=$(rc))"
dispatch '{"subagent_type":"general-purpose","prompt":"451 T216: build the guard\nSESSION_MODEL: builds the T216 guard\nRead first: ...","description":"451 T216: build it"}'
[ "$(rc)" -eq 0 ] && [ ! -s "$T/err" ] && ok "no model and a SESSION_MODEL line with its reason passes, silently - the session's model (451 T216)" || no "a marked dispatch was refused" "(rc=$(rc)) $(head -3 "$T/err")"
logged session-model && logged 'builds the T216 guard' && ok "...recorded permitted/session-model with its reason" || no "session-model not recorded"
dispatch '{"subagent_type":"general-purpose","model":"sonnet","prompt":"SESSION_MODEL: judges the plan section\nread it","description":"x"}'
[ "$(rc)" -eq 0 ] && ok "a named sonnet beside the line passes: the named reading model is what runs" || no "sonnet beside the line was refused" "(rc=$(rc))"
dispatch '{"subagent_type":"quote-check","model":"opus","prompt":"check hamlets","description":"x"}'
[ "$(rc)" -eq 0 ] && ok "a type with an agent file is out of scope whatever model it names" || no "a pinned type naming a model was refused" "(rc=$(rc))"
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
ROOT="$(cd "$HERE/../.." && pwd)"
grep -q 'to read, fetch, translate or extract' "$ROOT/CLAUDE.md" && grep -q 'for anything that judges or builds' "$ROOT/CLAUDE.md" && grep -q 'SESSION_MODEL: <' "$ROOT/CLAUDE.md" && ok "root CLAUDE.md carries the same two clauses, and the line, the message reads from agent_model_rule.txt" || no "CLAUDE.md and the message's rule have drifted apart"
"$HOOK" bogus >/dev/null 2>&1; [ $? -eq 1 ] && ok "an unknown mode is an error, not a pass" || no "an unknown mode passed"

echo
echo "test-agent-model-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
