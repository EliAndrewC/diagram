#!/usr/bin/env bash
# test-builder-pool-hooks.sh - prove builder-pool-hooks still bites (feature 451 T285): a worktree made by hand under the clones
# directory, and the removal of a pool tree or its build cache, are refused with the pool's command; the tooling's own commands, a
# scratch worktree and a mention pass. Red when the guard is deleted: every expect_block then exits 0.
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/builder-pool-hooks.sh"
pass=0 fail=0
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
export GUARD_LOG_DIR="$W/log" CLONE_MAIN="$W/m" HOME="$W/h"
C="$W/m/.clones"
mkdir -p "$C/c/.git" "$C/d/.git" "$W/h"
# the clone's pool: one tree, adopted under its own name
printf '{"trees": [{"tree": "%s", "feature": "", "tasks": [], "since": ""}]}\n' "$C/c-t269" > "$C/c/.git/builder-pool.json"
# another clone's registry holds its lane's tree (461 T13's reserved holder `lane`)
printf '{"trees": [{"tree": "%s", "feature": "", "tasks": ["lane"], "since": ""}]}\n' "$C/d-land" > "$C/d/.git/builder-pool.json"

run() {  # run <command-string> -> sets RC and OUT
  OUT=$(printf '{"cwd":%s,"tool_input":{"command":%s}}' "$(jq -nc '$ARGS.positional[0]' --args -- "$C/c")" "$(jq -nc '$ARGS.positional[0]' --args -- "$1")" \
    | "$HOOK" pretool 2>&1)
  RC=$?
}
expect_block() {  # <command> <words the refusal holds>
  run "$1"
  if [ "$RC" -eq 2 ] && grep -qF -- "$2" <<< "$OUT"; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: expected BLOCK naming '$2', got rc=$RC for: $1"; fi
}
expect_allow() {
  run "$1"
  if [ "$RC" -eq 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: expected ALLOW, got rc=$RC for: $1"; fi
}

# --- blocked: a builder's tree made by hand (2026-11-26's form), under any name, the landing tree's included
expect_block "git -C $C/c worktree add --detach $C/c-t286 HEAD" 'make builder-tree T=<task>'
expect_block "git worktree add -q --detach $C/c-land HEAD" 'make builder-tree T=<task>'
expect_block "cd $C/c && git worktree add ../c-b7" 'make builder-tree T=<task>'
# --- blocked: a pool tree, or its build cache, removed or moved by hand
expect_block "git -C $C/c worktree remove --force $C/c-t269" 'make builder-tree-drop TREE=<path> REASON='
expect_block "git -C $C/c worktree move $C/c-t269 $C/c-b1" 'make builder-tree-release T=<task>'
expect_block 'rm -rf ~/.cache/l7r-cargo-target/c-t269' 'make builder-tree-drop TREE=<path> REASON='
expect_block "git -C $C/c worktree remove --force $C/c-t269 && rm -rf $W/h/.cache/l7r-cargo-target/c-t269" 'make builder-tree-drop'
expect_block "git worktree add $C/c-x  # BUILDER_TREE_OK" 'with no reason'
# --- blocked: the lane's tree and its warm cache (461 T45), which the builders' reading of the pool leaves out
expect_block "git -C $C/d worktree remove --force $C/d-land" 'make builder-tree-drop TREE=<path> REASON='
expect_block 'rm -rf ~/.cache/l7r-cargo-target/d-land' 'make builder-tree-drop TREE=<path> REASON='

# --- allowed: the pool's and the landing's own commands (their git calls are inside the tools), scratch, a tree and a cache no
# registry names (c-land: no lane adopted it), a mention
expect_allow 'make builder-tree T=T285 F=451'
expect_allow 'make land F=451 T=T285 NOTE="verified"'
expect_allow 'make builder-tree-drop TREE=/x REASON="the pool shrinks"'
expect_allow 'git worktree add --detach /tmp/t285-scratch/wt HEAD'
expect_allow "git -C $C/c worktree remove --force $C/c-land"
expect_allow 'rm -rf ~/.cache/l7r-cargo-target/c-land'
expect_allow "git log --grep 'git worktree add $C/c-x'"
expect_allow "git worktree add $C/c-x  # BUILDER_TREE_OK: a fixture for a suite"
printf '{}' | "$HOOK" pretool >/dev/null 2>&1
[ $? -eq 0 ] && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: empty input should be a no-op"; }

echo "test-builder-pool-hooks: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
