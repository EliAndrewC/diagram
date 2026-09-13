#!/usr/bin/env bash
# test-plan-gate.sh - the companion suite for plan-gate.sh (constitution XVIII: a guard without one turns
# the gate red). It drives the push refusal against a fixture repository rather than grepping it: a grep
# proves a branch EXISTS, not that it fires. The module's own cases are tests/tooling/test_plan_gate.py.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE="$HERE/plan-gate.sh"
FIX="$(mktemp -d)"
# ISOLATE THE CENSUS (feature 169): a recording guard's fixtures never land in the live guard log.
GUARD_LOG_DIR="$FIX/guard-log"; export GUARD_LOG_DIR
trap 'rm -rf "$FIX"' EXIT

pass=0; fail=0
ok() { if [ "$1" = "$2" ]; then pass=$((pass+1)); else fail=$((fail+1)); printf '  FAIL %s: got %s want %s\n' "$3" "$1" "$2"; fi; }
g() { git -C "$FIX/repo" -c user.name=t -c user.email=t@example.com "$@"; }
run() { ( cd "$FIX/repo" && env -u PLAN_REVIEW_OK "$@" "$GATE" "$BASE..HEAD" >/dev/null 2>&1 ); echo $?; }
run_with() { ( cd "$FIX/repo" && PLAN_REVIEW_OK="$1" "$GATE" "$BASE..HEAD" >/dev/null 2>&1 ); echo $?; }

mkdir -p "$FIX/repo/.claude/skills/diagram/dev" && g init -q
echo base > "$FIX/repo/README"; g add -A; g commit -q -m base; BASE=$(g rev-parse HEAD)
D="$FIX/repo/specs/243-x"; mkdir -p "$D"
commit() { g add -A; g commit -q -m "$1"; }
review() { printf '{"plan_sha256": "%s", "decisions": [], "verdict": "%s"}\n' "$(sha256sum "$D/plan.md" | cut -d' ' -f1)" "$1" > "$D/plan-review.json"; }

# 1. a delta that touches no feature is quiet
ok "$(run)" 0 "no feature touched"

# 2. a feature with no ticked task - a plan being drafted - passes (spec D3)
printf -- '- [ ] T01 plan review\n- [ ] T02 build\n' > "$D/tasks.md"; commit draft
ok "$(run)" 0 "no ticked task passes"

# 3. a ticked task with no plan.md refuses (D5) - and a HAND tick counts (D4)
printf -- '- [x] T01 plan review\n- [ ] T02 build\n' > "$D/tasks.md"; commit hand-tick
ok "$(run)" 1 "ticked with no plan refuses"

# 4. a plan with no review refuses, and the refusal is recorded under its rule
printf '# plan\n' > "$D/plan.md"; commit plan
ok "$(run)" 1 "ticked with no review refuses"
grep -lq '"rule": "plan-review-missing"' "$GUARD_LOG_DIR"/*.json 2>/dev/null; ok $? 0 "the refusal is recorded"

# 5. a current CLEAR review passes
review CLEAR; commit clear
ok "$(run)" 0 "a current CLEAR review passes"

# 6. a plan edited after its review refuses (FR-004)
printf '# plan\n\n**P9 - a later narrowing.**\n' > "$D/plan.md"; commit edit
ok "$(run)" 1 "a stale review refuses"

# 7. a current BLOCKED review refuses (FR-005)
review BLOCKED; commit blocked
ok "$(run)" 1 "a BLOCKED review refuses"

# 8. the escape must SAY WHY, and a reason discharges it and is recorded in the repository's bypass log
ok "$(run_with x)" 1 "a bare token is refused"
ok "$(run_with 'a superseded plan nobody will implement')" 0 "a reason discharges it"
ls "$FIX/repo/.claude/skills/diagram/dev/bypass-log/"*.json >/dev/null 2>&1; ok $? 0 "the reason lands in dev/bypass-log/"
grep -lq '"rule": "plan-review-ok"' "$GUARD_LOG_DIR"/*.json 2>/dev/null; ok $? 0 "the escape is recorded"

printf 'test-plan-gate: %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
