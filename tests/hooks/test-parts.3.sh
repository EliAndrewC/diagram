#!/usr/bin/env bash
# test-parts.3.sh - the third shard of parts.sh's suite (feature 451 T281): THE RENDERED GUARD MESSAGES, A TREE AT A TIME. The real
# `make hooks-test` and `make guard-messages` recipes run in a fixture repository of stub guards with a linked worktree beside its
# main one, as two builders' trees sit beside each other in a clone. The store of rendered messages lay in the git COMMON directory,
# so (a) one tree's run replaced another's renderings - `make guard-messages` then said nothing was owed for the wording that tree's
# own red hooks-test had just named - and (b) a tree's check went red on the wordings of a guard only the other tree holds (both seen
# 2026-11-26, both reproduced here on the code before the fix). The suites' stamps STAY shared (a fresh worktree reran 5 suites of 46
# where it had rerun all: 83 s against 151 s, 2026-10-12), so two more cases hold the fix to them: a fresh tree still skips every suite
# and ends with its store filled, and a tree skipping on another tree's stamp reads the rendering at THAT key, never its own stale one.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
pass=0 fail=0
check() { if eval "$2"; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL: $1"; fi; }
D=$(mktemp -d)
trap 'rm -rf "$D"' EXIT
A="$D/a"; B="$D/b"
GATES="review-gate entry-gate claims-gate cohort-gate plan-gate closing-checks l7r-gate"
OTHERS="sync-with-main land-tooling state-sync"
mkdir -p "$A/scripts/hooks" "$A/scripts/gates" "$A/tests/hooks" "$A/dev"
git -C "$A" init -q -b main
stub() { printf '#!/bin/sh\nexit 0\n' > "$1"; chmod +x "$1"; }
for g in $GATES; do stub "$A/scripts/gates/$g.sh"; done
for g in $OTHERS; do stub "$A/scripts/$g.sh"; done
stub "$A/tests/hooks/parts.sh"; stub "$A/scripts/hooks/fx-hooks.sh"
# the guard's binary is the real one, asked in the FIXTURE's tree (a suite's key is its own files' there); the gate's launcher does nothing
BIN=$(L7R_GUARD_PRINT_FRESH=1 "$ROOT/scripts/hooks/l7r-guard.sh" < /dev/null)
printf '#!/bin/sh\n[ -z "$L7R_GUARD_PRINT_FRESH" ] || exec "%s/scripts/hooks/l7r-guard.sh"\nL7R_GUARD_TREE=$(cd "$(dirname "$0")/../.." && pwd) exec "%s" "$@"\n' "$ROOT" "$BIN" > "$A/scripts/hooks/l7r-guard.sh"
chmod +x "$A/scripts/hooks/l7r-guard.sh"
cp "$HERE/hookrun.sh" "$A/tests/hooks/"
# a stub guard's suite: it counts its run in its tree and renders one refusal, the wording its own
suite() { # <tree> <guard, as its messages name it> <wording>
  cat > "$1/tests/hooks/test-$2.sh" <<EOF
#!/bin/sh
echo ran >> "\$(dirname "\$0")/../../runs-$2"
mkdir -p "\$L7R_MESSAGE_CORPUS"
printf '{"guard":"$2","event":"PreToolUse","kind":"refuse","text":"$3"}\n' >> "\$L7R_MESSAGE_CORPUS/messages.jsonl"
EOF
  chmod +x "$1/tests/hooks/test-$2.sh"
}
for g in $GATES $OTHERS l7r-guard parts; do suite "$A" "$g" "the wording of $g"; done
suite "$A" fx-hooks "the old wording of fx"
printf 'runs-*\n' > "$A/.gitignore"
printf 'key\tverdict\tchars\tguard\tkind\tby\tover\thead\n' > "$A/dev/guard-messages.tsv"
# the user-level self-test is not this fixture's: stamped as run, at the key the recipe computes
uk=$(cat "$HOME/.claude/hooks/test-missing-program-hook.sh" "$HOME/.claude/hooks/missing-program-hook.sh" 2>/dev/null | sha256sum | cut -c1-16)
mkdir -p "$A/.git/hooks-test" && printf '%s' "$uk" > "$A/.git/hooks-test/missing-program-hook"
# the recipes, as a session's shell runs them: none of the outer run's make state, and never every suite forced
mk() { ( cd "$1" && env -u MAKEFLAGS -u MAKELEVEL -u MFLAGS -u HOOKS_ALL make --no-print-directory -f "$ROOT/Makefile" "${@:2}" 2>&1 ); }
runs() { wc -l < "$1/runs-$2" 2>/dev/null || echo 0; }
owed() { printf '%s\n' "$1" | grep -c "NOT REVIEWED: $2 "; }

# the main tree's first run renders every suite; each wording is then recorded reviewed (the list-growing messages' worst cases too)
out=$(mk "$A" hooks-test)
check "the fixture's first run is red on its unreviewed wordings alone" 'case $out in *"hooks-test FAILED: guard-messages"*) true ;; *) false ;; esac'
for k in $(printf '%s\n' "$out" | sed -n 's/^GUARD MESSAGE .*, key \([0-9a-f]\{16\}\),.*/\1/p'); do
  mk "$A" guard-messages KEY="$k" VERDICT=PASS BY=fixture > /dev/null
done
git -C "$A" add -A; git -C "$A" -c user.name=t -c user.email=t@t commit -qm base
out=$(mk "$A" hooks-test)
check "reviewed, the main tree's run is green and skips every suite" 'case $out in *"0 guard suites green, 14 unchanged"*) true ;; *) echo "$out"; false ;; esac'
count=$(mk "$A" guard-messages | sed -n 's/^guard-messages: \([0-9]*\) wordings, each reviewed.*/\1/p')
check "its store holds every wording" '[ "${count:-0}" -ge 13 ]'

# A FRESH TREE STILL SKIPS EVERY SUITE (the shared stamps, commit d7456c4c8d), and its store is filled all the same
git -C "$A" worktree add -q --detach "$B" HEAD
out=$(mk "$B" hooks-test)
check "a fresh worktree of the same content runs no suite" 'case $out in *"0 guard suites green, 14 unchanged"*) true ;; *) echo "$out"; false ;; esac'
check "... none at all" '[ -z "$(ls "$B" | grep "^runs-")" ]'
check "... and its own store holds every wording" '[ "$(mk "$B" guard-messages | sed -n "s/^guard-messages: \([0-9]*\) wordings, each reviewed.*/\1/p")" = "$count" ]'

# EFFECT (a): B changes a wording and its run names it; A, the old wording, runs; B's wording is still owed
suite "$B" fx-hooks "a NEW wording of fx, written in the linked tree"
out=$(mk "$B" hooks-test)
check "the changed wording fails its tree's run" '[ "$(owed "$out" fx-hooks)" = 1 ]'
out=$(mk "$A" hooks-test)
check "the other tree, at the old wording, reruns the suite and is green" '[ "$(runs "$A" fx-hooks)" = 2 ] && case $out in *"hooks area stamped"*) true ;; *) echo "$out"; false ;; esac'
out=$(mk "$B" guard-messages)
check "(a) another tree's run leaves this tree's unreviewed wording owed" '[ "$(owed "$out" fx-hooks)" = 1 ]'

# EFFECT (b): B gains a guard A does not hold; A's check never reads it. With it, in ONE run of A: a rendering left in A's store by
# a guard A does not hold (the main tree's store is where every tree's lay before T281) goes, and A, brought to B's wording, SKIPS
# the suite on B's stamp and reads the rendering at that stamp's key - its own last rendering is the old wording's.
stub "$B/scripts/hooks/only-b-hooks.sh"; suite "$B" only-b-hooks "the wording of a guard only the linked tree holds"
out=$(mk "$B" hooks-test)
check "the tree holding the new guard owes its wording" '[ "$(owed "$out" only-b-hooks)" = 1 ] && [ "$(owed "$out" fx-hooks)" = 1 ]'
out=$(mk "$A" guard-messages)
check "(b) a tree is not judged on a guard only another tree holds" '[ "$(owed "$out" only-b-hooks)" = 0 ]'
cp "$B/tests/hooks/test-fx-hooks.sh" "$A/tests/hooks/test-fx-hooks.sh"
mkdir -p "$A/.git/hooks-test/messages"
printf '{"guard":"gone-hooks","event":"PreToolUse","kind":"refuse","text":"the wording of a guard this tree does not hold"}\n' > "$A/.git/hooks-test/messages/gone-hooks.sh.jsonl"
before=$(runs "$A" fx-hooks)
out=$(mk "$A" hooks-test)
check "a suite another tree stamped at this tree's content is skipped" '[ "$(runs "$A" fx-hooks)" = "$before" ]'
check "... and its rendering at that stamp's key is the one judged, not the tree's stale one" '[ "$(owed "$out" fx-hooks)" = 1 ]'
check "(b) the run is not judged on another tree's guard" '[ "$(owed "$out" only-b-hooks)" = 0 ]'
check "a rendering of a guard the tree does not hold is not judged, and goes" '[ "$(owed "$out" gone-hooks)" = 0 ] && [ ! -e "$A/.git/hooks-test/messages/gone-hooks.sh.jsonl" ]'

# feature 451 T414: A RED SUITE'S LOG OUTLIVES THE RUN, in the COMMON git directory (a linked tree's failure under the main tree's .git),
# named by the run's FAIL line and handed to the event line's writer; the run's green suites keep none. The gate's launcher here records
# what it is asked, so the Phase call's spans are read as they left the recipe.
printf '#!/bin/sh\nprintf "%%s\\n" "$*" >> "%s/gate-calls"\nexit 0\n' "$D" > "$B/scripts/gates/l7r-gate.sh"
printf '#!/bin/sh\necho "case 7: the state-sync case FAILED"\nexit 1\n' > "$B/tests/hooks/test-fx-hooks.sh"
out=$(mk "$B" hooks-test)
kept=$(printf '%s\n' "$out" | sed 's/\x1b\[[0-9;]*m//g' | sed -n 's/^HOOK TESTS FAILED: fx-hooks\.sh (whole log kept: \(.*\))$/\1/p')
check "the FAIL line names the kept log, in the common git directory" 'case $kept in "$A/.git/l7r-hooks-failed/"*-fx-hooks.sh-p*.log) true ;; *) echo "$out"; false ;; esac'
check "the kept log holds the suite's whole log" '[ -f "$kept" ] && grep -q "case 7: the state-sync case FAILED" "$kept"'
check "only the red suite's log is kept" '[ "$(ls "$A/.git/l7r-hooks-failed" | wc -l)" -eq 1 ]'
check "the event line's span carries the kept log" 'grep -qx "suite:[0-9.]*:[0-9.]*:1:fx-hooks.sh:l7r-hooks-failed/${kept##*/}" <<<"$(grep "event-log phase" "$D/gate-calls" | tr " " "\n")"'

echo "parts.3: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
