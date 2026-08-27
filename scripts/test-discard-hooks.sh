#!/usr/bin/env bash
# test-discard-hooks.sh - prove discard-hooks.sh blocks a checkout/restore that would discard
# uncommitted work, and lets every harmless spelling through. Runs in a throwaway git repo so it
# can make a file genuinely dirty.
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/discard-hooks.sh"
pass=0 fail=0

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
git -C "$TMP" init -q
git -C "$TMP" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
printf 'a\n' > "$TMP/dirty.py"; printf 'b\n' > "$TMP/clean.py"; mkdir -p "$TMP/sub"; printf 'c\n' > "$TMP/sub/deep.py"
git -C "$TMP" add . && git -C "$TMP" -c user.email=t@t -c user.name=t commit -q -m files
printf 'changed\n' >> "$TMP/dirty.py"; printf 'changed\n' >> "$TMP/sub/deep.py"

run() {  # run <command-string> -> sets RC; the hook sees $TMP as its cwd
  printf '{"tool_input":{"command":%s}}' "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1")" \
    | (cd "$TMP" && "$HOOK" pretool >/dev/null 2>&1)
  RC=$?
}
expect_block() { run "$1"; if [ "$RC" -eq 2 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: expected BLOCK, got rc=$RC for: $1"; fi; }
expect_allow() { run "$1"; if [ "$RC" -eq 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: expected ALLOW, got rc=$RC for: $1"; fi; }

# --- blocked: every spelling that discards a MODIFIED file
expect_block 'git checkout -- dirty.py'
expect_block 'git checkout dirty.py'
expect_block 'git checkout HEAD -- dirty.py'
expect_block 'git restore dirty.py'
expect_block 'git restore --worktree dirty.py'
expect_block 'git checkout -- .'
expect_block 'git restore .'
expect_block "git -C $TMP checkout -- sub/deep.py"
expect_block 'echo measuring; git checkout -- dirty.py 2>/dev/null; echo "(checkout would discard my diff - NOT run)"'
expect_block 'git checkout -- clean.py dirty.py'

# --- allowed: nothing is lost
expect_allow 'git checkout -- clean.py'
expect_allow 'git restore clean.py'
expect_allow 'git checkout main'
expect_allow 'git checkout -b feature-x'
expect_allow 'git restore --staged dirty.py'
expect_allow 'git status --short'
expect_allow 'git diff -- dirty.py'
expect_allow 'grep -n "git checkout -- ways.py" docs/iteration-loop.md'
expect_allow 'git checkout -- dirty.py   # DISCARD_OK reverting the experiment on purpose'

# --- allowed: wrong mode, or no command at all
printf '{"tool_input":{"command":"git checkout -- dirty.py"}}' | (cd "$TMP" && "$HOOK" posttool >/dev/null 2>&1)
[ $? -eq 0 ] && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: posttool mode should be a no-op"; }
printf '{}' | "$HOOK" pretool >/dev/null 2>&1
[ $? -eq 0 ] && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: empty input should be a no-op"; }

echo "test-discard-hooks: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
