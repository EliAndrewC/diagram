#!/usr/bin/env bash
# Tests for checks-hooks.sh with the two guards that read its state - decide, then freeze (feature 375, FR-003(b)(c)).
# Run: tests/hooks/test-checks-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 375 - a NEW hook's companion suite.
#
# The whole round through the REAL hooks, in a throwaway clone: a quote-check dispatched on 0105 (check-bundle-hooks.sh records
# it), launched (checks-hooks.sh launched pairs the agent id), an Edit to 0105 refused while it runs (record-edit-hooks.sh), the
# same check refused again while it runs, the return (checks-hooks.sh returned keeps its EDIT block), the proposed edit
# admitted and another refused, `make apply-edits` admitted only for the round's reply.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
H="$HERE/../../scripts/hooks"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT
PASS=0; FAIL=0
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

C="$T/clone"
git init -q "$C"
mkdir -p "$C/.specify" "$C/research/questions" "$T/b"
printf '{"feature_directory": "specs/999-x"}\n' > "$C/.specify/feature.json"
PAGE="$C/research/questions/0105-baths-furo.drawing.html"
printf '<p>about 10 by 8 ft</p>\n' > "$PAGE"
printf 'owed-checks: quote-check\nunit: quote-check:0105.drawing#bath abc\n' > "$T/b/MANIFEST.md"
REPLY="$T/reply.txt"
printf 'quote-check: 0105 - 1\n\nEDIT research/questions/0105-baths-furo.drawing.html\n<<<\nabout 10 by 8 ft\n===\nabout 10 by 8 feet\n>>>\n' > "$REPLY"

agent() { # agent <tool_use_id> -> the PreToolUse payload of a quote-check on the bundle
  python3 -c 'import json,sys; print(json.dumps({"cwd":sys.argv[1],"tool_name":"Agent","tool_use_id":sys.argv[2],"tool_input":{"subagent_type":"quote-check","prompt":"Read "+sys.argv[3]}}))' "$C" "$1" "$T/b/MANIFEST.md"
}
edit() { # edit <old> <new> -> rc of record-edit-hooks.sh pretool
  python3 -c 'import json,sys; print(json.dumps({"cwd":sys.argv[1],"tool_name":"Edit","tool_input":{"file_path":sys.argv[2],"old_string":sys.argv[3],"new_string":sys.argv[4]}}))' "$C" "$PAGE" "$1" "$2" \
    | "$H/record-edit-hooks.sh" pretool >/dev/null 2>"$T/err"
}
bash_call() { python3 -c 'import json,sys; print(json.dumps({"cwd":sys.argv[1],"tool_name":"Bash","tool_input":{"command":sys.argv[2]}}))' "$C" "$1" \
    | "$H/record-edit-hooks.sh" pretool-bash >/dev/null 2>"$T/err"; }

echo "checks-hooks:"
agent t1 | "$H/check-bundle-hooks.sh" pretool >/dev/null 2>"$T/err"; rc=$?
[ "$rc" = 0 ] && ok "the first quote-check on 0105 is dispatched" || no "first dispatch" "rc=$rc $(cat "$T/err")"
python3 -c 'import json,sys; print(json.dumps({"cwd":sys.argv[1],"tool_name":"Agent","tool_use_id":"t1","tool_input":{},"tool_response":{"status":"async_launched","agentId":"ag1"}}))' "$C" | "$H/checks-hooks.sh" launched; rc=$?
[ "$rc" = 0 ] && ok "its launch is recorded, exit 0" || no "launched" "rc=$rc"
edit "about 10 by 8 ft" "about 10 by 8 feet"; rc=$?
[ "$rc" = 2 ] && grep -q "frozen while its checks run" "$T/err" && ok "IT FIRES: an Edit to 0105 while its check runs is refused" || no "the frozen edit went through" "rc=$rc"
agent t2 | "$H/check-bundle-hooks.sh" pretool >/dev/null 2>"$T/err"; rc=$?
[ "$rc" = 2 ] && grep -q "already in q:0105's round" "$T/err" && ok "IT FIRES: the same check re-dispatched while it runs is refused" || no "re-dispatch allowed" "rc=$rc"
bash_call "make apply-edits FROM=$REPLY"; rc=$?
[ "$rc" = 2 ] && ok "IT FIRES: make apply-edits while the check runs is refused" || no "apply-edits allowed while running" "rc=$rc"
python3 -c 'import json,sys; print(json.dumps({"cwd":sys.argv[1],"agent_id":"ag1","agent_type":"quote-check","last_assistant_message":open(sys.argv[2]).read()}))' "$C" "$REPLY" | "$H/checks-hooks.sh" returned
edit "about 10 by 8 ft" "about 10 by 8 feet"; rc=$?
[ "$rc" = 0 ] && ok "STAYS QUIET: the returned check's own edit goes in" || no "the proposed edit was refused" "rc=$rc $(cat "$T/err")"
edit "about 10 by 8 ft" "about 12 by 9 ft"; rc=$?
[ "$rc" = 2 ] && grep -q "none of the 1 edit(s) they proposed" "$T/err" && ok "IT FIRES: another replacement at the proposed place is refused" || no "a different edit went through" "rc=$rc"
bash_call "make apply-edits FROM=$REPLY"; rc=$?
[ "$rc" = 0 ] && ok "STAYS QUIET: make apply-edits on the round's own reply" || no "apply-edits refused" "rc=$rc $(cat "$T/err")"
# the command the freeze names, for a check that went silent, closes it (the advisor's note: a refusal must name a command that runs)
agent t5 | "$H/check-bundle-hooks.sh" pretool >/dev/null 2>&1
python3 -c 'import json,sys; print(json.dumps({"cwd":sys.argv[1],"tool_name":"Agent","tool_use_id":"t5","tool_input":{},"tool_response":{"status":"async_launched","agentId":"ag5"}}))' "$C" | "$H/checks-hooks.sh" launched
edit "about 10 by 8 feet" "about 10 by 8 ft"; rc=$?
[ "$rc" = 2 ] && ok "a new round freezes the page again" || no "not frozen" "rc=$rc"
out="$( cd "$C" && python3 "$H/lib/hm_checks.py" close q:0105 "the agent died silently" )"  # what `make check-closed` runs
edit "about 10 by 8 feet" "about 10 by 8 ft"; rc=$?
[ "$rc" = 2 ] && printf '%s' "$out" | grep -q "0 silent dispatch(es)" && ok "make check-closed leaves a LIVE check alone (only a silent one closes)" || no "check-closed closed a live check" "rc=$rc $out"
# a check the session STOPPED itself (TaskStop) never returns: AGENT= closes it though it is not silent (374, arbiter hour 4)
out="$( cd "$C" && python3 "$H/lib/hm_checks.py" close q:0105 "the session stopped it" ag9 )"
printf '%s' "$out" | grep -q "0 silent dispatch(es)" && ok "AGENT= closes only the agent it names" || no "AGENT= closed another agent's check" "$out"
out="$( cd "$C" && python3 "$H/lib/hm_checks.py" close q:0105 "the session stopped it" ag5 )"
again="$( cd "$C" && python3 "$H/lib/hm_checks.py" close q:0105 "nothing left running now" )"
printf '%s' "$out" | grep -q "1 silent dispatch(es)" && ! printf '%s' "$again" | grep -q "still running" && ok "make check-closed AGENT= closes the check the session stopped: nothing is left running on its page" || no "the stopped check still counts as running" "$out / $again"
bash_call "make quick"; rc=$?
[ "$rc" = 0 ] && ok "STAYS QUIET: an unrelated command" || no "make quick refused" "rc=$rc"
"$H/checks-hooks.sh" bogus >/dev/null 2>&1; rc=$?
[ "$rc" = 64 ] && ok "an unknown mode is a usage error" || no "usage" "rc=$rc"
grep -rq "frozen-while-checked" "$GUARD_LOG_ROOT" && ok "the refusal is recorded in the firing log" || no "not logged"

# FR-003(a) DECIDE FIRST: a task whose plan section has no verdict yet holds its checks
mkdir -p "$C/specs/999-x"
printf -- '- [ ] T01 the bath\n' > "$C/specs/999-x/tasks.md"
printf '# plan\n\n## T01 the bath\n\n- 10 x 8 ft\n' > "$C/specs/999-x/plan.md"
printf 'owed-checks: record-format\nunit: record-format:0200 abc\n' > "$T/b/MANIFEST.md"
python3 -c 'import json,sys; print(json.dumps({"cwd":sys.argv[1],"tool_name":"Agent","tool_use_id":"t9","tool_input":{"subagent_type":"record-format","prompt":"Read "+sys.argv[2]}}))' "$C" "$T/b/MANIFEST.md" \
  | "$H/check-bundle-hooks.sh" pretool >/dev/null 2>"$T/err"; rc=$?
[ "$rc" = 2 ] && grep -q "decide first" "$T/err" && grep -q "make decide F=999 T=T01" "$T/err" && ok "IT FIRES: a check before its task's decisions are ruled on, with the command" || no "decide-first did not fire" "rc=$rc $(cat "$T/err")"
grep -q "record-format on $T/b/MANIFEST.md: " "$T/err" && ok "the decide-first refusal names its check and bundle (feature 385 T22: four identical lines read as three checks)" || no "the refusal names no check" "$(cat "$T/err")"
python3 -c 'import json,sys; print(json.dumps({"cwd":sys.argv[1],"tool_name":"Agent","tool_use_id":"t10","tool_input":{"subagent_type":"record-format","prompt":"Read "+sys.argv[2]+" DECIDE_OK=\"the GM asked for this check\""}}))' "$C" "$T/b/MANIFEST.md" \
  | "$H/check-bundle-hooks.sh" pretool >/dev/null 2>"$T/err"; rc=$?
[ "$rc" = 0 ] && ok "STAYS QUIET: DECIDE_OK with a reason" || no "the escape did not pass" "rc=$rc $(cat "$T/err")"
# feature 430 T07 (D7; research R2): the claims TRIAGE runs beside the plan review - decide-first holds impl-drift, not the triage
python3 -c 'import json,sys; print(json.dumps({"cwd":sys.argv[1],"tool_name":"Agent","tool_use_id":"t11","tool_input":{"subagent_type":"impl-drift","prompt":"Read "+sys.argv[2]}}))' "$C" "$T/b/MANIFEST.md" \
  | "$H/check-bundle-hooks.sh" pretool >/dev/null 2>"$T/err"; rc=$?
[ "$rc" = 2 ] && grep -q "decide first" "$T/err" && ok "IT FIRES: impl-drift waits for the task's decisions" || no "impl-drift was let through undecided" "rc=$rc $(cat "$T/err")"
python3 -c 'import json,sys; print(json.dumps({"cwd":sys.argv[1],"tool_name":"Agent","tool_use_id":"t12","tool_input":{"subagent_type":"claims-triage","prompt":"Read "+sys.argv[2]}}))' "$C" "$T/b/MANIFEST.md" \
  | "$H/check-bundle-hooks.sh" pretool >/dev/null 2>"$T/err"; rc=$?
[ "$rc" = 0 ] && ok "STAYS QUIET: a claims triage beside the plan review (feature 430 T07)" || no "the claims triage was held by decide-first" "rc=$rc $(cat "$T/err")"

echo
echo "checks-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" = 0 ]
