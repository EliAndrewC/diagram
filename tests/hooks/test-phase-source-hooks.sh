#!/bin/bash
# Tests for phase-source-hooks.sh - a stage being rebuilt is never read from its old code while its task runs (feature 444).
# Run: tests/hooks/test-phase-source-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 444 - a NEW guard's companion suite.
#
# Every case drives the REAL hook with a REAL payload against a real git checkout holding a hold.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# PHASE_SOURCE_HOOK lets the proof-of-firing run this suite against a mutated copy of the guard and watch it go red.
HOOK="${PHASE_SOURCE_HOOK:-$HERE/../../scripts/hooks/phase-source-hooks.sh}"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
R="$T/repo"
git init -q "$R"
mkdir -p "$R/specs/444-x" "$R/l7r/diagram/hamletgen/water" "$R/l7r/diagram/settlement"
printf -- '- [ ] T16 phase: field - rebuilt\n      phase: field\n' > "$R/specs/444-x/tasks.md"
echo "def stage_field(): pass" > "$R/l7r/diagram/hamletgen/water/fields.py"
echo "x = 1" > "$R/l7r/diagram/settlement/other.py"
hold() { # hold [allow json] - the state make task-start writes
  printf '{"feature":"444-x","task":"T16","phase":"field","files":["l7r/diagram/hamletgen/water/fields.py"],"allow":[%s]}\n' "${1:-}" > "$R/.git/phase-sources.json"
}
export PHASE_SOURCE_GLOB="$R/.git/phase-sources.json"
call() { # call <tool> <json tool_input> [cwd] -> rc in $T/rc
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t-ps","tool_name":sys.argv[1],"tool_use_id":"now","cwd":sys.argv[3],"tool_input":json.loads(sys.argv[2])}))' "$1" "$2" "${3:-$R}" \
    | "$HOOK" pretool 2>"$T/err"; echo $? > "$T/rc"
}
rc() { cat "$T/rc"; }

hold
echo "1. a read of the stage's old code is refused, with the derivation to write from"
call Read "{\"file_path\":\"$R/l7r/diagram/hamletgen/water/fields.py\"}"
[ "$(rc)" -eq 2 ] && ok "the Read tool on a held file" || no "allowed" "(rc=$(rc))"
grep -q 'field_greenfield.derivation.md' "$T/err" && ok "...the message names the derivation" || no "no derivation in the message"
grep -q 'make phase-read FILE=' "$T/err" && ok "...and the way to open one file" || no "no escape route in the message"
call Bash '{"command":"sed -n 1,80p l7r/diagram/hamletgen/water/fields.py"}'
[ "$(rc)" -eq 2 ] && ok "sed on a held file, relative to the checkout" || no "allowed" "(rc=$(rc))"
call Bash '{"command":"grep -n def l7r/diagram/hamletgen/water/"}'
[ "$(rc)" -eq 2 ] && ok "a grep over the held file's directory" || no "allowed" "(rc=$(rc))"
call Bash '{"command":"git show HEAD:l7r/diagram/hamletgen/water/fields.py"}'
[ "$(rc)" -eq 2 ] && ok "git show of a held file" || no "allowed" "(rc=$(rc))"
call Grep "{\"pattern\":\"def\",\"path\":\"$R/l7r/diagram/hamletgen/water\"}"
[ "$(rc)" -eq 2 ] && ok "the Grep tool on the held file's directory" || no "allowed" "(rc=$(rc))"
call Read '{"file_path":"water/fields.py"}' "$R/l7r/diagram/hamletgen"
[ "$(rc)" -eq 2 ] && ok "a Read relative to a cwd inside the checkout" || no "allowed" "(rc=$(rc))"

echo "2. what is not a read of the held code passes"
call Read "{\"file_path\":\"$R/l7r/diagram/settlement/other.py\"}"
[ "$(rc)" -eq 0 ] && ok "another module" || no "refused" "(rc=$(rc))"
call Bash '{"command":"git rm l7r/diagram/hamletgen/water/fields.py"}'
[ "$(rc)" -eq 0 ] && ok "git rm names it with no read verb (a mention)" || no "refused" "(rc=$(rc))"
call Bash '{"command":"grep -rn stage_field l7r/"}'
[ "$(rc)" -eq 0 ] && ok "a grep over the whole engine (a search for a name)" || no "refused" "(rc=$(rc))"
call Read '{"file_path":"/tmp/l7r-check/work-budget-field/code/fields.py"}'
[ "$(rc)" -eq 0 ] && ok "a review bundle's copy outside the checkout" || no "refused" "(rc=$(rc))"
call Bash '{"command":"sed -n 1,80p l7r/diagram/hamletgen/water/fields.py  # PHASE_SOURCE_OK: replacing the thin stage function"}'
[ "$(rc)" -eq 0 ] && ok "the escape with a reason" || no "refused" "(rc=$(rc))"

echo "3. an allowance, a ticked task, and no hold at all"
hold '{"file":"l7r/diagram/hamletgen/water/fields.py","until":"2999-01-01T00:00:00Z","why":"replacing the stage function"}'
call Read "{\"file_path\":\"$R/l7r/diagram/hamletgen/water/fields.py\"}"
[ "$(rc)" -eq 0 ] && ok "make phase-read's allowance lets the Read through" || no "refused" "(rc=$(rc))"
hold '{"file":"l7r/diagram/hamletgen/water/fields.py","until":"2000-01-01T00:00:00Z","why":"long expired"}'
call Read "{\"file_path\":\"$R/l7r/diagram/hamletgen/water/fields.py\"}"
[ "$(rc)" -eq 2 ] && ok "an expired allowance holds again" || no "allowed" "(rc=$(rc))"
sed -i 's/^- \[ \] T16/- [x] T16/' "$R/specs/444-x/tasks.md"
call Read "{\"file_path\":\"$R/l7r/diagram/hamletgen/water/fields.py\"}"
[ "$(rc)" -eq 0 ] && ok "a ticked task holds nothing" || no "refused" "(rc=$(rc))"
rm -f "$R/.git/phase-sources.json"
call Bash '{"command":"cat l7r/diagram/hamletgen/water/fields.py"}'
[ "$(rc)" -eq 0 ] && ok "no hold, no refusal" || no "refused" "(rc=$(rc))"

echo
echo "test-phase-source-hooks: passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
