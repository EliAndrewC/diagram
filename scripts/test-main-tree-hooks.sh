#!/usr/bin/env bash
# test-main-tree-hooks.sh - prove main-tree-hooks.sh refuses a WRITE in the mirror root and nothing else.
# (GUARD_EDIT_OK: the companion of a NEW guard, feature 169 - constitution XVIII.)
#
# TWO DIRECTIONS, and the second matters more. This guard's whole risk is firing on correct work: a
# session reads main constantly (`git -C /diagram log`), and every clone lives UNDER the mirror root,
# so a pattern one character too greedy would refuse all editing everywhere. Section 2 is that half.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/main-tree-hooks.sh"
PASS=0; FAIL=0
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
export GUARD_LOG_DIR="$T/guard-log"

# A fake mirror with a clone under it, so the guard's own derivation (toplevel, minus /.clones/<name>)
# is exercised rather than stubbed.
MAIN=$T/diagram
git init -q "$MAIN"; git -C "$MAIN" config user.email t@t; git -C "$MAIN" config user.name t
echo a > "$MAIN/f"; git -C "$MAIN" add f; git -C "$MAIN" commit -qm a
mkdir -p "$MAIN/.clones"; git clone -q "$MAIN" "$MAIN/.clones/worker"

run() { # run <cwd> <command> -> RC, and OUT for the message
  # GUARD_EDIT_OK: feature 170 - the payload carries `cwd`, which is what FR-005 reads. The fixture
  # always passed a cwd implicitly (by `cd`), and the guard could not see it - which is exactly how a
  # suite can be green while the guard misses the shape it was built for.
  OUT=$(cd "$1" && printf '{"session_id":"t","cwd":"%s","tool_name":"Bash","tool_input":{"command":%s}}' \
        "$1" "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$2")" | "$HOOK" pretool 2>&1); RC=$?
}
check() { if [ "$2" = "$3" ]; then printf 'ok    %s (rc=%s)\n' "$1" "$3"; PASS=$((PASS+1));
          else printf 'FAIL  %s (expected rc=%s, got rc=%s)\n      out: %s\n' "$1" "$2" "$3" "$OUT"; FAIL=$((FAIL+1)); fi; }

echo "--- 1. a write in the mirror root is refused ---"
# THE TWO REAL INCIDENTS OF 2026-08-30, in the shape they actually took.
run "$MAIN/.clones/worker" "cd $MAIN && git add -A && git commit -m 'work'"
check "the 166 incident: cd into the mirror, then add and commit" 2 "$RC"
run "$MAIN/.clones/worker" "cd $MAIN; echo x > specs/163/request.md"
check "the 163 incident: cd into the mirror, then a redirect into a file" 2 "$RC"
run "$MAIN/.clones/worker" "cd $MAIN && sed -i 's/a/b/' f"
check "cd into the mirror, then sed -i" 2 "$RC"
run "$MAIN/.clones/worker" "cd $MAIN && make done"
check "cd into the mirror, then make" 2 "$RC"
case "$OUT" in *"git -C"*) printf 'ok    the refusal names the git -C rule\n'; PASS=$((PASS+1));;
  *) printf 'FAIL  the refusal does not give the route\n'; FAIL=$((FAIL+1));; esac

echo "--- 2. everything legitimate is untouched (the half that decides whether this guard survives) ---"
run "$MAIN/.clones/worker" "cd $MAIN && git log --oneline -5"
check "a READ in the mirror after a cd -> allowed" 0 "$RC"
run "$MAIN/.clones/worker" "cd $MAIN && git status --short"
check "git status in the mirror -> allowed" 0 "$RC"
run "$MAIN/.clones/worker" "git -C $MAIN log --oneline -1"
check "git -C read, no cd at all -> allowed" 0 "$RC"
run "$MAIN/.clones/worker" "cd $MAIN/.clones/worker && git commit -am work"
check "a commit in a CLONE under the mirror -> allowed" 0 "$RC"
run "$MAIN/.clones/worker" "( cd $MAIN/.clones/worker && make quick )"
check "the documented subshell form in a clone -> allowed" 0 "$RC"
# GUARD_EDIT_OK: feature 177 - THE CASE THAT FAILED BEFORE THE FIX. The guard's own refusal says
# "( cd <your clone> && ... ) in a subshell for anything you want to DO", and from main's tree that
# form was refused: the LEAVES scan's command positions were `^ ; & | &&` with no `(`, so the cd never
# counted as leaving. The case above passes even on the broken guard, because its cwd is already the
# clone - which is exactly how the suite stayed green while the guard refused correct work.
run "$MAIN" "( cd $MAIN/.clones/worker && git commit -am work )"
check "STANDING IN MAIN, the documented subshell form into a clone -> allowed" 0 "$RC"
run "$MAIN" "( cd $MAIN/.clones/worker && echo x > f )"
check "standing in main, subshell into a clone, then a redirect -> allowed" 0 "$RC"
# ...and the half that proves the fix did not widen what is PERMITTED (FR-017). Before it, neither of
# these was caught either: the ENTRY scan had no `(` any more than the LEAVES scan did, so teaching
# only one about subshells would have turned a false refusal into a false allow.
run "$MAIN/.clones/worker" "( cd $MAIN && git add -A && git commit -m 'work' )"
check "the subshell form into the MIRROR -> still refused" 2 "$RC"
run "$MAIN/.clones/worker" "( cd $MAIN && echo x > f )"
check "subshell into the mirror, then a redirect -> still refused" 2 "$RC"
run "$MAIN/.clones/worker" "git commit -am work"
check "an ordinary commit with no cd -> allowed" 0 "$RC"

echo "--- 3. a MENTION is not an invocation (this feature's own rule, applied to itself) ---"
run "$MAIN/.clones/worker" "git commit -m 'never cd $MAIN && git commit - name the tree instead'"
check "the pattern quoted inside a commit message -> allowed" 0 "$RC"
run "$MAIN/.clones/worker" "$(printf 'python3 - <<PY\ntext = "cd %s && git commit"\nPY' "$MAIN")"
check "the pattern inside a heredoc body -> allowed" 0 "$RC"

echo "--- 4. the escape, which is itself matched as an invocation ---"
run "$MAIN/.clones/worker" "cd $MAIN && git commit -am x  # MAIN_TREE_OK: render-sync, by hand, GM asked"
check "a real escape -> allowed" 0 "$RC"
run "$MAIN/.clones/worker" "grep -rn MAIN_TREE_OK scripts/ && cd $MAIN && git commit -am x"
check "the escape token merely GREPPED for -> still refused" 2 "$RC"

echo "--- 4b. THE SHAPE THAT ACTUALLY HAPPENED: standing in the mirror, no cd in the command (170 FR-005) ---"
# Feature 169 shipped claiming to prevent the reported incident and did not: a bare `cd` into a path
# inside the project persists into the NEXT Bash call (measured), so the real incident is a cd in one
# command and the write in another. Every case below returned 0 before FR-005.
run "$MAIN" "git add -A && git commit -m work"
check "a commit while STANDING IN the mirror -> refused" 2 "$RC"
run "$MAIN" "echo x > notes.md"
check "a redirect while standing in the mirror -> refused" 2 "$RC"
run "$MAIN" "git log --oneline -5"
check "a READ while standing in the mirror -> allowed" 0 "$RC"
run "$MAIN" "git status --short"
check "git status while standing in the mirror -> allowed" 0 "$RC"
run "$MAIN/.clones/worker" "git add -A && git commit -m work"
check "the same write from a CLONE under the mirror -> allowed" 0 "$RC"
run "$MAIN" "git commit -am x  # MAIN_TREE_OK: render-sync by hand"
check "standing in the mirror, escaped WITH a reason -> allowed" 0 "$RC"
run "$MAIN" "git commit -am x  # MAIN_TREE_OK"
check "standing in the mirror, escape with NO reason -> refused" 2 "$RC"

echo "--- 4c. LEAVING main before writing is correct work (feature 172 - it refused ME) ---"
# GUARD_EDIT_OK: feature 172 - the guard fired on its own author within the hour of shipping. The
# session's cwd was the mirror (a previous command had ended there), the command opened
# `cd <clone> && ...`, and every write after that cd lands in the clone. Judging by the payload's cwd
# alone cannot see that, and a guard that refuses correct work is the expensive failure.
run "$MAIN" "cd $MAIN/.clones/worker && git commit -am work"
check "standing in main, but cd INTO A CLONE first -> allowed" 0 "$RC"
run "$MAIN" "cd /tmp && echo x > f"
check "standing in main, cd right out of the tree -> allowed" 0 "$RC"
run "$MAIN" "cd $MAIN/specs && echo x > f"
check "standing in main, cd DEEPER into main -> still refused" 2 "$RC"

echo "--- 4d. a redirect to /dev/null is not a write (feature 172 - the third false positive) ---"
# GUARD_EDIT_OK: feature 172 - the write test matches `>`, so every `2>/dev/null` in an ordinary READ
# looked like a write and the guard refused a plain grep of mine while I stood in main. Third false
# positive this session from a pattern matching a CHARACTER rather than a thing: `->` in printed
# prose, `make -n`, and this.
run "$MAIN" "grep -h X /tmp/f 2>/dev/null"
check "a read with 2>/dev/null while standing in main -> allowed" 0 "$RC"
run "$MAIN" "git log --oneline 2>&1 | head -3"
check "a read with 2>&1 -> allowed" 0 "$RC"
run "$MAIN" "git log > /tmp/out"
check "a REAL redirect is still a write -> refused" 2 "$RC"

echo "--- 5. it records, with a rule slug (feature 168) ---"
rules=$(python3 -c "
import json,glob,os,collections
rows=[json.load(open(f)) for f in glob.glob(os.path.join('$GUARD_LOG_DIR','*.json'))]
print(dict(collections.Counter((r['event'], r.get('rule')) for r in rows)))" 2>/dev/null)
case "$rules" in
  *"'blocked', 'write-in-mirror'"*) printf 'ok    the block records as write-in-mirror\n'; PASS=$((PASS+1));;
  *) printf 'FAIL  the block did not record its rule: %s\n' "$rules"; FAIL=$((FAIL+1));; esac
case "$rules" in
  *"'escaped', 'main-tree-ok'"*) printf 'ok    the escape records as main-tree-ok\n'; PASS=$((PASS+1));;
  *) printf 'FAIL  the escape did not record its rule: %s\n' "$rules"; FAIL=$((FAIL+1));; esac

echo "-----"
printf 'test-main-tree-hooks: passed %s, failed %s\n' "$PASS" "$FAIL"
[ "$FAIL" = 0 ] || exit 1
