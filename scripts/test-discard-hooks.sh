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

# GUARD_EDIT_OK: feature 165 - A MERGE OWN CONFLICT-RESOLUTION VERB IS NOT A DISCARD (the GM ruling,
# 2026-08-30, on measured evidence: one of this guard five recorded firings was a `git checkout
# --ours` mid-merge). These vectors build a REAL conflict in a second throwaway repo, because the
# whole rule turns on `MERGE_HEAD` existing, and a fixture that fakes that proves nothing.
MRG=$(mktemp -d)
git -C "$MRG" init -q -b main
git -C "$MRG" config user.email t@t; git -C "$MRG" config user.name t
printf 'base\n' > "$MRG/f.txt"; printf 'base\n' > "$MRG/mine.txt"
git -C "$MRG" add -A; git -C "$MRG" commit -qm base
git -C "$MRG" checkout -q -b side; printf 'theirs\n' > "$MRG/f.txt"; git -C "$MRG" commit -qam side
git -C "$MRG" checkout -q main; printf 'ours\n' > "$MRG/f.txt"; git -C "$MRG" commit -qam main
printf 'my own uncommitted edit\n' >> "$MRG/mine.txt"

mrun() {  # the same shape as run(), against the merge fixture
  printf '{"tool_input":{"command":%s}}' "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1")" \
    | (cd "$MRG" && "$HOOK" pretool >/dev/null 2>&1)
  RC=$?
}
mblock() { mrun "$1"; if [ "$RC" -eq 2 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: expected BLOCK, got rc=$RC for: $1"; fi; }
mallow() { mrun "$1"; if [ "$RC" -eq 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: expected ALLOW, got rc=$RC for: $1"; fi; }

# OUTSIDE a merge the flags mean something else and are refused exactly as before
mblock 'git checkout --ours -- mine.txt'
git -C "$MRG" merge side >/dev/null 2>&1 || true
[ -f "$MRG/.git/MERGE_HEAD" ] || { echo "FAIL: the merge fixture did not conflict"; fail=$((fail+1)); }
# ...and INSIDE one, picking a side is resolution, not a discard
mallow 'git checkout --ours -- f.txt'
mallow 'git checkout --theirs -- f.txt'
mallow 'git restore --ours f.txt'
mallow 'git checkout --ours .'
# ...while a plain discard of the session own work is refused, merge or no merge
mblock 'git checkout -- mine.txt'
rm -rf "$MRG"

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
