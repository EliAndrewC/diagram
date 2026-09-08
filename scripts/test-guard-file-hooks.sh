#!/usr/bin/env bash
# Tests for guard-file-hooks.sh (feature 127, layer 3).
# Run: scripts/test-guard-file-hooks.sh   (exit 0 = all green)
#
# TWO DIRECTIONS (FR-015 + FR-016). Section 2 carries the case the fidelity review put here: an edit
# to a review-subagent definition must NOT be intercepted. It was in the first draft of the spec and
# was removed as unrequested - editing an agent cannot start an expensive run, so a prompt there
# guards nothing and obstructs this project's own procedure for improving review subagents.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/guard-file-hooks.sh"
# GUARD_EDIT_OK: feature 164 - this guard RECORDS its firings now (feature 162's log), so the suite
# must write its fixtures to a throwaway directory. Without it the suite pollutes `make audit`, whose
# whole purpose is to price a guard from real firings: 24 fixture entries appeared there the first
# time these conversions ran their suites.
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
trap 'rm -rf "$GUARD_LOG_ROOT"' EXIT

ROOT="$(cd "$HERE/.." && pwd)"
PASS=0; FAIL=0

ev() { python3 -c 'import json,sys; print(json.dumps({"session_id":"g","tool_name":sys.argv[3],"tool_input":{"file_path":sys.argv[1],"new_string":sys.argv[2]}}))' "$1" "$2" "${3:-Edit}"; }
run() { ev "$1" "${2:-x}" "${3:-Edit}" | "$HOOK" pretool >/dev/null 2>/tmp/gf.err; echo $?; }

check() { local rc; rc=$(run "$2" "${3:-x}" "${4:-Edit}")
  if { [ "$1" = ok ] && [ "$rc" -eq 0 ]; } || { [ "$1" = blocked ] && [ "$rc" -ne 0 ]; }; then
    echo "  ok      $1: $(basename "$2")"; PASS=$((PASS+1))
  else echo "  FAIL    expected $1 for $2 (rc=$rc)"; FAIL=$((FAIL+1)); fi; }

echo "1. IT FIRES on the files that ARE guards (FR-015)"
check blocked "$ROOT/.claude/skills/diagram/Makefile"
check blocked "$ROOT/scripts/gate-hooks.sh"
check blocked "$ROOT/scripts/make-only-hooks.sh"
check blocked "$ROOT/scripts/guard-file-hooks.sh"
check blocked "$ROOT/.claude/settings.json"
check blocked "$ROOT/.claude/settings.json" "x" "Write"
check blocked "$ROOT/.claude/skills/diagram/dev/switches.json"
check blocked "$ROOT/.claude/skills/diagram/dev/switches.json" "x" "Write"

echo
echo "2. IT STAYS QUIET on everything else (FR-016)"
check ok "$ROOT/.claude/agents/frontend-review.md"
check ok "$ROOT/.claude/agents/spec-fidelity.md"
check ok "$ROOT/scripts/test-gate-hooks.sh"
check ok "$ROOT/scripts/test-make-only-hooks.sh"
check ok "$ROOT/.claude/skills/diagram/l7r/diagram/hamletgen/ways.py"
check ok "$ROOT/.claude/skills/diagram/tests/test_invocation.py"
check ok "$ROOT/CLAUDE.md"
check ok "$ROOT/specs/127-gated-make-commands/spec.md"

echo
echo "3. THE ESCAPE WORKS, and puts the intent in the diff"
check ok "$ROOT/.claude/skills/diagram/Makefile" "GUARD_EDIT_OK - adding a target for a new operation"
check ok "$ROOT/scripts/gate-hooks.sh" "GUARD_EDIT_OK - it was firing on correct work"

echo
echo "4. THE REFUSAL TELLS YOU WHAT TO DO"
rc=$(run "$ROOT/.claude/skills/diagram/Makefile")
if [ "$rc" -ne 0 ] && grep -q "GUARD_EDIT_OK" /tmp/gf.err && grep -q "fires on correct work" /tmp/gf.err; then
  echo "  ok      names the escape and distinguishes legitimate edits"; PASS=$((PASS+1))
else echo "  FAIL    refusal did not carry the escape or the categories"; FAIL=$((FAIL+1)); fi

# GUARD_EDIT_OK: feature 212 - a recipe comment that would RUN is refused on any Makefile, by any
# route, marker or no marker (the GM's relayed ruling after feature 207's 914-level recursion).
echo
echo "5. A RECIPE COMMENT THAT WOULD RUN IS REFUSED (feature 212)"
TAB=$(printf '\t')
hazard() { # label, expected, new_string (Edit) - against the skill Makefile
  local rc; rc=$(run "$ROOT/.claude/skills/diagram/Makefile" "$3" Edit)
  if { [ "$2" = ok ] && [ "$rc" -eq 0 ]; } || { [ "$2" = blocked ] && [ "$rc" -ne 0 ]; }; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else echo "  FAIL    $1 (expected $2, rc=$rc)"; sed 's/^/          /' /tmp/gf.err | head -3; FAIL=$((FAIL+1)); fi
}
hazard "the 207 shape: a backtick in a : \"...\" comment, WITH the marker" blocked "${TAB}: \"GUARD_EDIT_OK: feature 207 - \`make test-full\` is the gate's test phase\" ; \\"
hazard "an @-prefixed comment with a backtick" blocked "${TAB}@: \"see \`make help\`\""
hazard "a \$\$( substitution in the comment" blocked "${TAB}: \"GUARD_EDIT_OK: the key is \$\$(git rev-parse HEAD) here\""
hazard "the same comment without backticks passes" ok "${TAB}: \"GUARD_EDIT_OK: feature 207 - make test-full is the gate's test phase\" ; \\"
hazard "an escaped backtick passes" ok "${TAB}: \"GUARD_EDIT_OK: the target is \\\`make done\\\`\""
hazard "the Makefile's own escaped \\\$\$(MAKE) mention passes" ok "${TAB}: \"GUARD_EDIT_OK: make runs \\\$\$(MAKE) sub-invocations even under -n\" ; \\"
hazard "a single-quoted comment cannot substitute" ok "${TAB}: 'GUARD_EDIT_OK: \`make done\` in single quotes is inert'"
hazard "a backtick in a make COMMENT line (#) is not a recipe" ok "# GUARD_EDIT_OK: \`make done\` is fine in a hash comment"
hazard "a backtick in a recipe COMMAND is the session's business" ok "${TAB}@echo \"GUARD_EDIT_OK: \$\$(date) runs on purpose\""
RC=$(ev "$ROOT/other/Makefile" "${TAB}: \"a \`backtick\` comment\"" Write | "$HOOK" pretool >/dev/null 2>&1; echo $?)
[ "$RC" -ne 0 ] && { echo "  ok      any Makefile, by Write too"; PASS=$((PASS+1)); } || { echo "  FAIL    a Write to another Makefile was not checked"; FAIL=$((FAIL+1)); }
run "$ROOT/.claude/skills/diagram/Makefile" "${TAB}: \"\`x\`\"" Edit >/dev/null
grep -q "There is no escape token" /tmp/gf.err && { echo "  ok      the refusal says there is no escape and how to write it"; PASS=$((PASS+1)); } || { echo "  FAIL    the refusal is unhelpful"; FAIL=$((FAIL+1)); }

echo
echo
echo "6. THE ROSTER OF ROLLED HAMLETS IS A GUARD (feature 217), with its own Read-time context"
ROSTER="$ROOT/.claude/skills/diagram/tests/rolls.py"
check blocked "$ROSTER"
check blocked "$ROSTER" "x" "Write"
check ok "$ROSTER" "GUARD_EDIT_OK: adding a roll row after make roll-audit showed its lines"
check ok "$ROOT/.claude/skills/diagram/tests/test_rolls.py"   # the roster's TEST is ordinary source
ctx=$(ev "$ROSTER" "" "Read" | "$HOOK" pretool 2>/dev/null)
if printf '%s' "$ctx" | grep -q "roll-audit" && printf '%s' "$ctx" | grep -q "constitution VI" && printf '%s' "$ctx" | grep -q "tests/soak/"; then
  echo "  ok      the Read of the roster names the doctrine, make roll-audit and the three exits"; PASS=$((PASS+1))
else echo "  FAIL    the roster's Read-time context is missing the doctrine or the command: $ctx"; FAIL=$((FAIL+1)); fi
ctx=$(ev "$ROOT/.claude/skills/diagram/Makefile" "" "Read" | "$HOOK" pretool 2>/dev/null)
if printf '%s' "$ctx" | grep -q "GUARD file" && ! printf '%s' "$ctx" | grep -q "roll-audit"; then
  echo "  ok      another guard's Read keeps the generic context"; PASS=$((PASS+1))
else echo "  FAIL    the generic Read context changed: $ctx"; FAIL=$((FAIL+1)); fi

echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
