#!/usr/bin/env bash
# Tests for research-switch-hooks (feature 451 T244): while dev/switches.json's research axis is `deferred`, a research-pass dispatch
# and a `make page-session` are refused naming the switch; RESEARCH_OK with a reason lets one through, recorded; open is silent.
# Run: tests/hooks/test-research-switch-hooks.sh   (exit 0 = all green)
#
# Every case runs on a FIXTURE tree with its own switch file, never the live one, so the verdicts do not flip when the GM reopens.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
FIX=$(mktemp -d); mkdir -p "$FIX/.git" "$FIX/dev"
SESS=$(mktemp -d); export CLONE_SESSIONS_DIR="$SESS" CLONE_MAIN="$FIX"
HOOK_ERR=$(mktemp)
trap 'rm -rf "$GUARD_LOG_ROOT" "$FIX" "$SESS" "$HOOK_ERR"' EXIT
HOOK="$HERE/research-switch-hooks.sh"
PASS=0; FAIL=0

switch() { printf '{"research": {"state": "%s", "why": "the GM: defer all of it", "who": "E", "utc": "2026-11-25T00:00:00Z"}}\n' "$1" > "$FIX/dev/switches.json"; }
agent_ev() { jq -nc --arg t "$1" --arg p "$2" --arg c "$FIX" '{"tool_name":"Agent","cwd":$c,"tool_input":{"subagent_type":$t,"prompt":$p}}'; }
bash_ev() { jq -nc --arg x "$1" --arg c "$FIX" '{"tool_name":"Bash","cwd":$c,"tool_input":{"command":$x}}'; }

check() { # label expected payload
  local rc; printf '%s' "$3" | "$HOOK" pretool >/dev/null 2>"$HOOK_ERR"; rc=$?
  if { [ "$2" = ok ] && [ "$rc" -eq 0 ]; } || { [ "$2" = blocked ] && [ "$rc" -ne 0 ]; }; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else echo "  FAIL    $1 (expected $2, rc=$rc)"; FAIL=$((FAIL+1)); fi
}

echo "1. DEFERRED: research starts are refused"
switch deferred
check "a research-pass dispatch"        blocked "$(agent_ev research-pass "the ford's width")"
check "make page-session"               blocked "$(bash_ev 'make page-session BRIEF=/x/brief.md')"
check "page-session after a cd"         blocked "$(bash_ev 'cd /x && make page-session BRIEF=b')"

echo
echo "2. DEFERRED: everything else passes"
check "another agent type"              ok "$(agent_ev impl-drift 'q')"
check "a mention of page-session"       ok "$(bash_ev 'grep -n page-session Makefile')"
check "make research-backlog"           ok "$(bash_ev 'make research-backlog STAGE=seat')"

echo
echo "3. THE REFUSAL NAMES THE SWITCH AND THE STEPS"
printf '%s' "$(agent_ev research-pass q)" | "$HOOK" pretool >/dev/null 2>"$HOOK_ERR" || true
if grep -q 'research is DEFERRED' "$HOOK_ERR" && grep -q 'the GM: defer all of it' "$HOOK_ERR" \
   && grep -q 'make research-backlog' "$HOOK_ERR" && grep -q 'make research-open REASON=' "$HOOK_ERR" && grep -q 'RESEARCH_OK=' "$HOOK_ERR"; then
  echo "  ok      names the switch, its reason, the backlog, the reopen and the escape"; PASS=$((PASS+1))
else echo "  FAIL    the refusal is missing a part"; FAIL=$((FAIL+1)); fi

echo
echo "4. THE ESCAPE: RESEARCH_OK with a reason permits and is recorded, a bare token does not"
check "prompt with a reason"            ok "$(agent_ev research-pass $'q\nRESEARCH_OK: the GM asked for this pass')"
check "command with a reason"           ok "$(bash_ev 'RESEARCH_OK="the GM asked for it" make page-session BRIEF=b')"
check "bare in a prompt"                blocked "$(agent_ev research-pass 'q RESEARCH_OK')"
check "bare in a command"               blocked "$(bash_ev 'make page-session BRIEF=b # RESEARCH_OK')"
if grep -rqs '"escaped"' "$GUARD_LOG_ROOT" && grep -rqs 'the GM asked for this pass' "$GUARD_LOG_ROOT"; then
  echo "  ok      the escape is in the guard log with its reason"; PASS=$((PASS+1))
else echo "  FAIL    the escape was not recorded"; FAIL=$((FAIL+1)); fi

echo
echo "5. OPEN, MISSING OR MALFORMED: silent"
switch open
check "open: research-pass"             ok "$(agent_ev research-pass q)"
check "open: page-session"              ok "$(bash_ev 'make page-session BRIEF=b')"
rm -f "$FIX/dev/switches.json"
check "missing: research-pass"          ok "$(agent_ev research-pass q)"
echo 'not json' > "$FIX/dev/switches.json"
check "malformed: page-session"         ok "$(bash_ev 'make page-session BRIEF=b')"

echo
echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
