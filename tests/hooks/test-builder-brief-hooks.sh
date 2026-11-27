#!/usr/bin/env bash
# test-builder-brief-hooks.sh - prove builder-brief-hooks still bites (feature 451 T334): a builder's dispatch - an ad-hoc agent
# whose prompt names a pool tree - is refused without the BUILDER-BRIEF line `make builder-brief` prints, with a marker whose tree the
# pool does not hold for its task, of an unknown kind or past three jobs, or a measurement that orders a source edit; each refusal
# prints the command. A check agent, the claims round, a mention and a reasoned escape pass. Red when the guard's branch is removed:
# every expect_block then exits 0.
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/builder-brief-hooks.sh"
pass=0 fail=0
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
export GUARD_LOG_DIR="$W/log" CLONE_MAIN="$W/m" HOME="$W/h"
C="$W/m/.clones"
mkdir -p "$C/c/.git" "$W/h"
T="$C/c-t271"
# the clone's pool: one tree held by 451 T334, one free, one held by a bundle (451 T299 and T282, one builder)
B="$C/c-t272"
printf '{"trees": [{"tree": "%s", "feature": "451", "tasks": ["T334"], "since": ""}, {"tree": "%s", "feature": "", "tasks": [], "since": ""}, {"tree": "%s", "feature": "451", "tasks": ["T299", "T282"], "since": ""}]}\n' "$T" "$C/c-t270" "$B" > "$C/c/.git/builder-pool.json"

run() {  # run <subagent_type> <prompt> -> sets RC and OUT
  OUT=$(jq -nc '{cwd: $ARGS.positional[0], tool_name: "Agent", tool_input: {subagent_type: $ARGS.positional[1], prompt: $ARGS.positional[2]}}' --args -- "$C/c" "$1" "$2" \
    | "$HOOK" pretool 2>&1)
  RC=$?
}
expect_block() {  # <type> <prompt> <words the refusal holds>
  run "$1" "$2"
  if [ "$RC" -eq 2 ] && grep -qF -- "$3" <<< "$OUT"; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: expected BLOCK naming '$3', got rc=$RC for: $2"; fi
}
expect_allow() {
  run "$1" "$2"
  if [ "$RC" -eq 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: expected ALLOW, got rc=$RC for: $2"; fi
}
M="BUILDER-BRIEF 451 T334"

# --- blocked: a builder with no marker (2026-11-26's form), under each ad-hoc type that can build
BRIEF="Build feature 451 task T334 in the pool worktree $T (work ONLY there). Another builder is in $C/c-t270."
expect_block '' "$BRIEF" 'make builder-brief T=T334 F=451 KIND=fix|measurement|build-half|closing-half'
expect_block general-purpose "$BRIEF" 'has no BUILDER-BRIEF line'
expect_block claude "$BRIEF" 'make builder-brief T=T334 F=451'
# --- blocked: the marker and the escape only MENTIONED, as this task's own brief did
expect_block '' "$BRIEF The block opens \`BUILDER-BRIEF <feature> <task> KIND=<kind> JOBS=<n> TREE=<path>\`; escape BUILDER_BRIEF_OK=\"<reason of two words or more>\" in the prompt." 'has no BUILDER-BRIEF line'
# --- blocked: a marker the pool does not bear out, an unknown kind, too many jobs
expect_block '' "$M KIND=fix JOBS=1 TREE=$C/c-t270"$'\n'"Work in $C/c-t270." 'is not held by 451 T334 in the pool (held by free)'
expect_block '' "BUILDER-BRIEF 451 T335 KIND=fix JOBS=1 TREE=$T"$'\n'"Work in $T." 'make builder-brief T=T335 F=451 KIND=fix'
expect_block '' "$M KIND=fix JOBS=1 TREE=/elsewhere/tree" 'not a pool tree'
expect_block '' "$M KIND=mechanism-build JOBS=1 TREE=$T" 'is no builder'"'"'s kind'
expect_block '' "$M KIND=fix JOBS=4 TREE=$T" 'a brief holds at most 3 jobs'
# --- blocked: a bundle's tree with no marker (the command named with both tasks), and a marker naming a task its hold lacks
expect_block '' "Build 451 T299 and T282 as one bundle in $B." 'make builder-brief T=T299,T282 F=451 KIND='
expect_block '' "BUILDER-BRIEF 451 T299,T300 KIND=fix JOBS=2 TREE=$B" 'is not held by 451 T299,T300 in the pool (held by 451 T299,T282)'
# --- blocked: a measurement that orders a source edit; the escape with no reason
expect_block '' "$M KIND=measurement JOBS=1 TREE=$T"$'\n'"Job 1, the measurement."$'\n'"Job 2, only if job 1 shows a safe rule: build it in the callers, red-first." 'make builder-brief T=T334 F=451 KIND=fix'
expect_block '' "$BRIEF"$'\n'"BUILDER_BRIEF_OK:" 'BUILDER_BRIEF_OK with no reason'
# --- blocked (451 T353): a builder's brief written by hand - the block's STOP POINT line, no marker - into the clone, or naming no tree
expect_block '' "Fix 451 T240 in $C/c, the session clone."$'\n'"STOP POINT (fix): red-first, then the plan section." 'make builder-brief T=<task> F=<feature> KIND='
expect_block general-purpose "Build 451 T237."$'\n'"  STOP POINT: stop at the plan review." 'a STOP POINT line and no BUILDER-BRIEF line'

# --- allowed: the block's marker, borne out by the pool, for each kind
for k in fix measurement build-half closing-half; do
  expect_allow '' "$M KIND=$k JOBS=1 TREE=$T"$'\n'"Blocks: none"$'\n'"Work in $T only. Job 1: measure the seven crates."
done
expect_allow general-purpose "the task's own text first"$'\n'"  $M KIND=fix JOBS=3 TREE=$T"$'\n'"Job 2: fix the reader."
# --- allowed: a bundle's marker naming both tasks of the tree held for it
expect_allow '' "BUILDER-BRIEF 451 T299,T282 KIND=fix JOBS=2 TREE=$B"$'\n'"Work in $B only."
# --- allowed: a check, the claims round, a dispatch naming no pool tree, a longer name, the escape with its reason
expect_allow spec-fidelity "Review the plan delta; the builder's tree is $T."
expect_allow impl-drift "$BRIEF"
expect_allow Explore "$BRIEF"
expect_allow '' "Run the claims round for feature 451 T334; the builder's tree is $T."
expect_allow '' "Read $C/c/docs/usage.md and $T-land/x and report."
expect_allow '' "Summarize docs/usage.md"
expect_allow '' "Read $C/c and report: a builder's STOP POINT is its plan review."
expect_allow impl-drift "Fix it in $C/c."$'\n'"STOP POINT (fix): red-first."
expect_allow '' "Fix it in $C/c."$'\n'"STOP POINT (fix): red-first."$'\n'"BUILDER_BRIEF_OK: a repair staged in the clone"
expect_allow '' "Read the pre-warm log under $T and report its last line."$'\n'"BUILDER_BRIEF_OK: a reader of one log"
printf '{}' | "$HOOK" pretool >/dev/null 2>&1
[ $? -eq 0 ] && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: empty input should be a no-op"; }

echo "test-builder-brief-hooks: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
