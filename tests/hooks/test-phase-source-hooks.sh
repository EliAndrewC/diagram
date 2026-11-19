#!/bin/bash
# Tests for the phase-source guard (rust/guard, replayed through its link) - a stage being rebuilt is never read from its old code while its task runs (feature 444).
# Run: tests/hooks/test-phase-source-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 444 - a NEW guard's companion suite.
#
# Every case drives the REAL hook with a REAL payload against a real git checkout holding a hold.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# PHASE_SOURCE_HOOK lets the proof-of-firing run this suite against a mutated copy of the guard and watch it go red.
HOOK="${PHASE_SOURCE_HOOK:-$HERE/phase-source-hooks.sh}"
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
hold() { # hold [allow json] [derivation] - the state make task-start writes
  printf '{"feature":"444-x","task":"T16","phase":"field","derivation":"%s","files":["l7r/diagram/hamletgen/water/fields.py"],"allow":[%s]}\n' "${2-specs/444-x/derivations/T16-field.md}" "${1:-}" > "$R/.git/phase-sources.json"
}
mkdir -p "$R/specs/444-x/derivations"; echo "the derivation" > "$R/specs/444-x/derivations/T16-field.md"
export PHASE_SOURCE_GLOB="$R/.git/phase-sources.json"
call() { # call <tool> <json tool_input> [cwd] -> rc in $T/rc
  jq -nc '{"session_id":"t-ps","tool_name":$ARGS.positional[0],"tool_use_id":"now","cwd":$ARGS.positional[2],"tool_input":($ARGS.positional[1]|fromjson)}' --args -- "$1" "$2" "${3:-$R}" \
    | "$HOOK" pretool 2>"$T/err"; echo $? > "$T/rc"
}
rc() { cat "$T/rc"; }

hold
echo "1. a read of the stage's old code is refused, with the derivation to write from"
call Read "{\"file_path\":\"$R/l7r/diagram/hamletgen/water/fields.py\"}"
[ "$(rc)" -eq 2 ] && ok "the Read tool on a held file" || no "allowed" "(rc=$(rc))"
grep -q 'Write it from:  specs/444-x/derivations/T16-field.md' "$T/err" && ok "...the message names the derivation the task recorded" || no "not the recorded derivation in the message"
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
call Bash '{"command":"grep -rn stage_field l7r/"}'
[ "$(rc)" -eq 2 ] && ok "a grep over a parent of the held file (T204)" || no "allowed" "(rc=$(rc))"
grep -q 'Search without them:  --exclude=fields.py' "$T/err" && ok "...the refusal names the exclusion that makes it compliant" || no "no exclusion in the message"
call Bash '{"command":"rg -n stage_field"}'
[ "$(rc)" -eq 2 ] && ok "an rg over the whole checkout" || no "allowed" "(rc=$(rc))"
call Grep "{\"pattern\":\"def\",\"path\":\"$R/l7r\",\"output_mode\":\"content\"}"
[ "$(rc)" -eq 2 ] && ok "the Grep tool over a parent of the held file" || no "allowed" "(rc=$(rc))"
call Grep "{\"pattern\":\"def\",\"path\":\"$R/l7r\",\"glob\":\"!**/water/fields.py\"}"
[ "$(rc)" -eq 0 ] && ok "...and with a glob that leaves it out, passes" || no "refused" "(rc=$(rc))"
for c in 'find l7r -name \"*.py\" | sort | xargs grep -n stage_field' 'cat $(find l7r -name \"*.py\")' 'find l7r -type f | xargs cat' 'find l7r -name \"*.py\" -exec cat {} +'; do
  call Bash "{\"command\":\"$c\"}"
  [ "$(rc)" -eq 2 ] && ok "a find feeding a reader: $c" || no "allowed: $c" "(rc=$(rc))"
done
grep -q "Search without them:  -not -path '\*/diagram/hamletgen/water/fields.py'" "$T/err" && ok "...the refusal names the find's exclusion" || no "no find exclusion in the message"
for c in 'ls -R l7r | xargs cat' 'ls l7r/diagram/hamletgen/water/* | xargs cat' 'git ls-files l7r | xargs cat' 'git ls-files | xargs grep -n stage_field' 'cat $(git ls-files l7r)' 'tree -fi l7r | xargs cat' 'cat l7r/diagram/hamletgen/water/*'; do
  call Bash "{\"command\":\"$c\"}"
  [ "$(rc)" -eq 2 ] && ok "a reader fed by a lister or a glob: $c" || no "allowed: $c" "(rc=$(rc))"
done
for c in 'git ls-files l7r | wc -l' 'ls -R l7r | sort' 'git ls-files | xargs wc -l' 'ls -R l7r --ignore=fields.py | xargs cat'; do
  call Bash "{\"command\":\"$c\"}"
  [ "$(rc)" -eq 0 ] && ok "a listing alone, or one that leaves the held file out: $c" || no "refused: $c" "(rc=$(rc))"
done
call Bash '{"command":"find l7r -not -path \"*/water/fields.py\" -type f | xargs cat"}'
[ "$(rc)" -eq 0 ] && ok "...and a find that leaves the held file out passes" || no "refused" "(rc=$(rc))"
call Bash '{"command":"find l7r -name \"*.py\" | wc -l"}'
[ "$(rc)" -eq 0 ] && ok "a find feeding only a count passes" || no "refused" "(rc=$(rc))"
hold '' ''
call Read "{\"file_path\":\"$R/l7r/diagram/hamletgen/water/fields.py\"}"
grep -q 'greenfield' "$T/err" && no "a derivation that does not exist is named" || ok "no derivation recorded: none is invented"
grep -q 'names no derivation' "$T/err" && ok "...and the message says where to look" || no "no pointer to the task block"
hold

echo "2. what is not a read of the held code passes"
call Read "{\"file_path\":\"$R/l7r/diagram/settlement/other.py\"}"
[ "$(rc)" -eq 0 ] && ok "another module" || no "refused" "(rc=$(rc))"
call Bash '{"command":"git rm l7r/diagram/hamletgen/water/fields.py"}'
[ "$(rc)" -eq 0 ] && ok "git rm names it with no read verb (a mention)" || no "refused" "(rc=$(rc))"
call Bash '{"command":"grep -rn stage_field l7r/ --exclude=fields.py"}'
[ "$(rc)" -eq 0 ] && ok "a grep over the whole engine that leaves the held file out" || no "refused" "(rc=$(rc))"
call Bash '{"command":"make phase-read FILE=l7r/diagram/hamletgen/water/fields.py WHY=\"the thin wrapper\" 2>&1 | tail -3"}'
[ "$(rc)" -eq 0 ] && ok "the make phase-read the refusal prescribes, piped into tail" || no "refused" "(rc=$(rc))"
call Bash '{"command":"git diff --stat l7r/diagram/hamletgen/water/ | tail -3"}'
[ "$(rc)" -eq 0 ] && ok "git diff --stat over the held directory prints no content" || no "refused" "(rc=$(rc))"
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
