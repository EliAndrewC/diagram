#!/bin/bash
# Tests for workflow-hooks.sh - a Workflow call is held to the guards its agents would meet as Agent calls (feature 383
# amendment 7, FR-045, plan D48; SC-031).
# Run: tests/hooks/test-workflow-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 383 amendment 7 - a NEW guard's companion suite.
#
# Every case drives the REAL hook with a REAL Workflow payload against a fixture repository. The Agent hooks a check-wave unit is
# put through are a fixture settings file's (WORKFLOW_SETTINGS): a stub that records each payload it sees and refuses a prompt
# saying REFUSE-ME, and the REAL agent-prefix guard - so a unit a real guard of its type refuses is shown refused with that
# guard's own message.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="${WORKFLOW_HOOK:-$HERE/../../scripts/hooks/workflow-hooks.sh}"
PREFIX="$HERE/../../scripts/hooks/agent-prefix-hooks.sh"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT
FIX="$T/clone"; mkdir -p "$FIX/.claude/agents" "$FIX/.claude/workflows"; git -C "$FIX" init -q 2>/dev/null
for a in quote-check source-reader escalation-check; do printf -- '---\nname: %s\nmodel: opus\n---\nbody\n' "$a" > "$FIX/.claude/agents/$a.md"; done
cp "$HERE/../../.claude/workflows/check-wave.js" "$FIX/.claude/workflows/"
SEEN="$T/seen.jsonl"
cat > "$T/stub.sh" <<EOF
#!/bin/bash
p="\$(cat)"; printf '%s\n' "\$p" >> "$SEEN"
printf '%s' "\$p" | grep -q 'REFUSE-ME' && { echo "BLOCKED by the stub guard: its own words" >&2; exit 2; }
[ "\${L7R_WAVE_UNIT:-}" = 1 ] || { echo "the unit came without L7R_WAVE_UNIT" >&2; exit 2; }
exit 0
EOF
chmod +x "$T/stub.sh"
python3 -c 'import json,sys; print(json.dumps({"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"exit 2"}]},{"matcher":"Agent","hooks":[{"type":"command","command":sys.argv[1]},{"type":"command","command":sys.argv[2]+" pretool"}]}]}}))' "$T/stub.sh" "$PREFIX" > "$T/settings.json"
export WORKFLOW_SETTINGS="$T/settings.json"

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
wf() { # wf <json tool_input> -> rc in $T/rc, stderr in $T/err
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t-wf","cwd":sys.argv[2],"tool_name":"Workflow","tool_use_id":"toolu_wf1","tool_input":json.loads(sys.argv[1])}))' "$1" "$FIX" \
    | ( cd "$FIX" && "$HOOK" pretool 2>"$T/err" >"$T/out" ); echo $? > "$T/rc"
}
script() { python3 -c 'import json,sys; print(json.dumps({"script":sys.argv[1]}))' "$1"; }
rc() { cat "$T/rc"; }
logged() { grep -rlq "$1" "$GUARD_LOG_ROOT" 2>/dev/null; }

echo "1. a script's agent() calls"
wf "$(script "export const meta = {name: 'x', description: 'y'}
const r = await agent('summarize the file', {label: 'a'})")"
[ "$(rc)" -eq 2 ] && grep -q 'no agentType' "$T/err" && grep -q '35k' "$T/err" && ok "an untyped agent() is refused, naming the ~35k first write" || no "an untyped agent() went" "(rc=$(rc)) $(head -3 "$T/err")"
logged untyped && ok "...recorded" || no "not recorded"
wf "$(script "// GP_OK: a deliberate general stage
const r = await agent('summarize the file', {label: 'a', model: 'sonnet'})")"
[ "$(rc)" -eq 0 ] && ok "GP_OK with a reason, and a model, passes" || no "the escape was refused" "(rc=$(rc)) $(head -3 "$T/err")"
logged escape && ok "...and is recorded as an escape" || no "the escape is not recorded"
wf "$(script "// GP_OK: a deliberate general stage
const r = await agent('summarize the file', {label: 'a'})")"
[ "$(rc)" -eq 2 ] && grep -q 'names no model' "$T/err" && ok "...but an untyped stage still names its model, as an ad-hoc Agent call must" || no "a model-less GP stage went" "(rc=$(rc))"
wf "$(script "// GP_OK
const r = await agent('summarize the file', {label: 'a', model: 'sonnet'})")"
[ "$(rc)" -eq 2 ] && ok "a bare GP_OK with no reason does not pass" || no "a bare GP_OK passed" "(rc=$(rc))"
wf "$(script "const r = await agent('check 0105', {agentType: 'quote-check', schema: S})")"
[ "$(rc)" -eq 2 ] && grep -q 'name: "check-wave"' "$T/err" && ok "a defined check in a script of its own is refused with the check-wave call" || no "a guarded type ran outside check-wave" "(rc=$(rc)) $(head -3 "$T/err")"
wf "$(script "const t = pick(); const r = await agent('check 0105', {agentType: t})")"
[ "$(rc)" -eq 2 ] && grep -q 'name it literally' "$T/err" && ok "an agentType computed at run time is refused the same way" || no "a computed type went" "(rc=$(rc))"
wf "$(script "const r = await workflow('check-wave', {agentType: 'quote-check', units: built})")"
[ "$(rc)" -eq 2 ] && grep -q 'by name from the Workflow tool' "$T/err" && ok "check-wave called from inside a script (args built at run time) is refused" || no "a nested check-wave went" "(rc=$(rc))"
wf "$(script "const r = await agent('find the callers', {agentType: 'Explore', model: 'sonnet'})")"
[ "$(rc)" -eq 0 ] && ok "a built-in type with its model passes (no project guard covers it)" || no "Explore was refused" "(rc=$(rc)) $(head -3 "$T/err")"
printf "const r = await agent('x', {label: 'a'})\n" > "$T/saved.js"
wf "{\"scriptPath\": \"$T/saved.js\"}"
[ "$(rc)" -eq 2 ] && ok "a scriptPath is read and judged as the inline script is" || no "a scriptPath went unjudged" "(rc=$(rc))"

echo "2. check-wave: every unit through the Agent hooks"
: > "$SEEN"
wf '{"name":"check-wave","args":{"agentType":"quote-check","units":[{"label":"0105","prompt":"Read /tmp/a/MANIFEST.md"},{"label":"0106","prompt":"Read /tmp/b/MANIFEST.md","then":[{"agentType":"source-reader","prompt":"Verify /tmp/b/MANIFEST.md"}]}]}}'
[ "$(rc)" -eq 0 ] && ok "a wave of clean units passes" || no "a clean wave was refused" "(rc=$(rc)) $(head -5 "$T/err")"
grep -q 'make wave-report' "$T/out" && ok "...and the session is told the command that measures it (FR-046)" || no "the measurement is not named" "$(cat "$T/out")"
n=$(wc -l < "$SEEN")
[ "$n" -eq 3 ] && ok "each unit AND its declared verify step met the Agent hooks (3 payloads)" || no "the hooks saw $n payloads, not 3"
python3 - "$SEEN" <<'PY' && ok "...as the Agent payload a hand launch sends: its type, prompt, a wave:<run>:<n> id" || no "the payloads are not Agent payloads"
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
assert all(r["tool_name"] == "Agent" and r["tool_use_id"].startswith("wave:") for r in rows)
assert [r["tool_input"]["subagent_type"] for r in rows] == ["quote-check", "quote-check", "source-reader"]
assert rows[2]["tool_use_id"].endswith(":1.0") and rows[2]["tool_input"]["prompt"] == "Verify /tmp/b/MANIFEST.md"
PY
wf '{"name":"check-wave","args":{"agentType":"quote-check","units":[{"label":"0105","prompt":"Read /tmp/a/MANIFEST.md"},{"label":"0107","prompt":"REFUSE-ME /tmp/c/MANIFEST.md"}]}}'
[ "$(rc)" -eq 2 ] && grep -q 'unit 0107' "$T/err" && grep -q 'BLOCKED by the stub guard: its own words' "$T/err" && ok "a unit a guard refuses refuses the whole run, with the unit's label and the guard's own message" || no "a refused unit went" "(rc=$(rc)) $(head -5 "$T/err")"
wf '{"name":"check-wave","args":{"agentType":"quote-check","units":[{"label":"0105","prompt":"Read /tmp/a/MANIFEST.md","then":[{"agentType":"source-reader","prompt":"REFUSE-ME verify"}]}]}}'
[ "$(rc)" -eq 2 ] && grep -q '0105 / source-reader' "$T/err" && ok "a declared verify step a guard refuses refuses the run too" || no "a refused verify step went" "(rc=$(rc))"
SHARED=$(python3 -c 'print("\n".join(f"Context line {i}: what every check of this kind needs to know about the record." for i in range(130)))')
python3 - "$SHARED" > "$T/args.json" <<'PY'
import json, sys
print(json.dumps({"name": "check-wave", "args": {"agentType": "quote-check", "units": [
    {"label": "u1", "prompt": "Judge 0105.\n" + sys.argv[1]}, {"label": "u2", "prompt": "Judge 0106.\n" + sys.argv[1]}]}}))
PY
wf "$(cat "$T/args.json")"
[ "$(rc)" -eq 2 ] && grep -q 'unit u2' "$T/err" && grep -q '.claude/agents' "$T/err" && ok "the REAL repeated-block guard refuses a unit, in its own words" || no "the real guard did not fire on a unit" "(rc=$(rc)) $(head -5 "$T/err")"
wf '{"name":"check-wave","args":{"agentType":"escalation-check","units":[{"label":"a","prompt":"x"}]}}'
[ "$(rc)" -eq 2 ] && grep -q 'not an authorized wave job' "$T/err" && ok "a type outside the authorized wave jobs is refused" || no "an unauthorized job went" "(rc=$(rc))"
wf '{"name":"check-wave","args":{"agentType":"quote-check","units":[{"label":"a","prompt":"x","then":[{"agentType":"spec-fidelity","prompt":"y"}]}]}}'
[ "$(rc)" -eq 2 ] && ok "...and so is a verify step of one" || no "an unauthorized verify step went" "(rc=$(rc))"
wf '{"name":"check-wave","args":"{\"agentType\": \"quote-check\"}"}'
[ "$(rc)" -eq 2 ] && grep -q 'JSON string' "$T/err" && ok "args passed as a JSON string is refused, naming the fix" || no "a string args went" "(rc=$(rc))"
wf "{\"scriptPath\": \"$FIX/.claude/workflows/check-wave.js\", \"args\": {\"agentType\": \"quote-check\", \"units\": [{\"label\": \"z\", \"prompt\": \"REFUSE-ME\"}]}}"
[ "$(rc)" -eq 2 ] && ok "check-wave by its scriptPath is judged as check-wave (its units guarded)" || no "check-wave by path went unguarded" "(rc=$(rc))"

echo "3. what it leaves alone"
printf '{"tool_name":"Agent","cwd":"%s","tool_input":{"prompt":"x"}}' "$FIX" | ( cd "$FIX" && "$HOOK" pretool 2>"$T/err" ); r=$?
[ "$r" -eq 0 ] && ok "a non-Workflow payload passes" || no "a non-Workflow payload was refused" "(rc=$r)"

echo "-----"
if [ "$FAIL" -eq 0 ]; then echo "all workflow-hook tests passed ($PASS)"; exit 0; fi
echo "SOME TESTS FAILED ($FAIL of $((PASS+FAIL)))"; exit 1
