#!/usr/bin/env bash
# Tests for sync-with-main.sh - the route decision, the mirror refresh, and the gated/direct pushes
# (feature 130; constitution XVIII: the route decision is a guard, so it ships with its test).
# Run: scripts/test-sync-with-main.sh   (exit 0 = all green). Runs under `make hooks-test`, which
# derives this companion's name from the script's (test-<script>).
#
# The fixture stands in for the whole topology: a bare "github" repository, a MAIN checkout that is
# its mirror, and a session CLONE under main/.clones/. CLONE_MAIN, CLONE_GITHUB, CI_ROUTE and
# CI_MERGE are the script's test seams - the real route decision calls `make ci-status ROUTE=1`,
# which needs the whole skill and is tested in tests/ci/; here the seam supplies the answer.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC="$HERE/sync-with-main.sh"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
# GUARD_EDIT_OK: feature 170 - sync-with-main.sh RECORDS now (its GATE_STAMP_OK escape was the third
# silent permit), so this suite writes into a throwaway log rather than the live census. Caught by the
# derived isolation check the moment the guard started recording, which is the point of deriving it.
export GUARD_LOG_DIR="$T/guard-log"
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t HOME=$T

check() { # label expected-rc actual-rc
  if [ "$2" = "$3" ]; then printf 'ok    %s (rc=%s)\n' "$1" "$3"; else printf 'FAIL  %s (expected rc=%s, got rc=%s)\n      out: %s\n' "$1" "$2" "$3" "${OUT:-}"; FAIL=$((FAIL+1)); return; fi
  PASS=$((PASS+1))
}
expect_out() { case "$OUT" in *"$1"*) : ;; *) echo "FAIL  output lacks '$1': $OUT"; FAIL=$((FAIL+1)) ;; esac; }

# ---- fixture ------------------------------------------------------------------------------------
topology() { # $1 = name; builds $T/$1/{github.git,main,main/.clones/c}
  local d=$T/$1; rm -rf "$d"; mkdir -p "$d"
  git init -q --bare -b main "$d/github.git"
  git init -q -b main "$d/seed"; ( cd "$d/seed" && mkdir -p scripts .claude/skills/x && echo base > f && echo '.clones/' > .gitignore && echo 'def a(): return 1' > .claude/skills/x/a.py && cp "$HERE"/*.sh "$HERE"/*.py scripts/ && git add -A && git commit -qm base && git push -q "$d/github.git" HEAD:main )
  git clone -q "$d/github.git" "$d/main"
  git -C "$d/main" config receive.denyCurrentBranch updateInstead
  mkdir -p "$d/main/.clones/.session-clones"
  git clone -q "$d/github.git" "$d/main/.clones/c"
  echo "$d"
}
syncmain() { # $1 = topology dir, then args
  local d=$1; shift
  ( cd "$d/main/.clones/c" && CLONE_MAIN="$d/main" CLONE_GITHUB="$d/github.git" GITHUB_TOKEN=unused "$SYNC" "$@" 2>&1 )
}
stamp_hooks() { ( cd "$1/main/.clones/c" && python3 scripts/gate-stamp.py --write hooks >/dev/null ); }

echo "1. sync-in refreshes the mirror from GitHub main, then the clone"
D=$(topology a)
( cd "$D/seed" && echo more > g && git add -A && git commit -qm upstream && git push -q "$D/github.git" HEAD:main )
OUT=$(syncmain "$D" sync-in); check "sync-in from a clean clone" 0 $?
[ "$(git -C "$D/main" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  mirror did not fast-forward to GitHub main"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main/.clones/c" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  clone did not merge GitHub main"; FAIL=$((FAIL+1)); }
expect_out "synced with GitHub main"

echo "2. sync-in --mirror-only advances the mirror and leaves the clone alone (a dirty clone's turn)"
D=$(topology b)
( cd "$D/seed" && echo more > g && git add -A && git commit -qm upstream && git push -q "$D/github.git" HEAD:main )
before=$(git -C "$D/main/.clones/c" rev-parse HEAD)
OUT=$(syncmain "$D" sync-in --mirror-only); check "sync-in --mirror-only" 0 $?
[ "$(git -C "$D/main" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  mirror not advanced"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main/.clones/c" rev-parse HEAD)" = "$before" ] && PASS=$((PASS+1)) || { echo "FAIL  clone was touched"; FAIL=$((FAIL+1)); }

echo "2b. sync-in refreshes the CLONE's pool index on both branches, only when it is stale"
D=$(topology b2)
mkdir -p "$D/main/.clones/c/.claude/skills/diagram/pool/hamlets/x"
printf 'pool-index:\n\t@echo built >> pool/index.html\npool-index-if-stale:\n\t@if [ ! -f pool/index.html ] || [ -n "$$(find pool legacy-hand-authored-pool -newer pool/index.html \\( -name "*.json" -o -name "*.png" -o -name "*.notes.md" \\) -print -quit 2>/dev/null)" ]; then $(MAKE) --no-print-directory pool-index; fi\n' > "$D/main/.clones/c/.claude/skills/diagram/Makefile"
IDX="$D/main/.clones/c/.claude/skills/diagram/pool/index.html"
OUT=$(syncmain "$D" sync-in --mirror-only); check "mirror-only sync-in with no index" 0 $?
[ "$(cat "$IDX" 2>/dev/null)" = "built" ] && PASS=$((PASS+1)) || { echo "FAIL  missing index was not built on the dirty-clone branch"; FAIL=$((FAIL+1)); }
OUT=$(syncmain "$D" sync-in); check "sync-in with a fresh index" 0 $?
[ "$(cat "$IDX")" = "built" ] && PASS=$((PASS+1)) || { echo "FAIL  fresh index was rebuilt (efficiency check did not hold)"; FAIL=$((FAIL+1)); }
touch -d '-10 seconds' "$IDX"; echo '{}' > "$D/main/.clones/c/.claude/skills/diagram/pool/hamlets/x/x.json"
OUT=$(syncmain "$D" sync-in); check "sync-in after a manifest changed" 0 $?
[ "$(cat "$IDX")" = "$(printf 'built\nbuilt')" ] && PASS=$((PASS+1)) || { echo "FAIL  stale index was not rebuilt: $(cat "$IDX")"; FAIL=$((FAIL+1)); }

echo "3. IT FIRES: a hand commit in the mirror stops sync-in with the fast-forward message"
D=$(topology c)
( cd "$D/main" && echo rogue > rogue && git add -A && git commit -qm "committed in main by hand" )
( cd "$D/seed" && echo more > g && git add -A && git commit -qm upstream && git push -q "$D/github.git" HEAD:main )
OUT=$(syncmain "$D" sync-in); check "mirror cannot fast-forward -> refused" 1 $?
expect_out "cannot fast-forward"

echo "4. DIRECT route: a docs-only delta pushes straight to GitHub main, no build, mirror follows"
D=$(topology d)
( cd "$D/main/.clones/c" && echo docs > note.md && git add -A && git commit -qm docs )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "direct push" 0 $?
[ "$(git -C "$D/github.git" rev-parse main)" = "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  GitHub main did not receive the direct push"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  mirror did not follow"; FAIL=$((FAIL+1)); }
expect_out "route DIRECT"

echo "5. GATED route, refused: nothing lands, the work stays in the clone"
D=$(topology e)
( cd "$D/main/.clones/c" && echo 'def a(): return 2' > .claude/skills/x/a.py && git add -A && git commit -qm engine ); stamp_hooks "$D"
gh_before=$(git -C "$D/github.git" rev-parse main)
OUT=$(CI_ROUTE=GATED CI_MERGE="false" syncmain "$D" push); check "gated route refused by ci-merge -> push fails" 1 $?
[ "$(git -C "$D/github.git" rev-parse main)" = "$gh_before" ] && PASS=$((PASS+1)) || { echo "FAIL  something landed on GitHub main"; FAIL=$((FAIL+1)); }
expect_out "nothing landed"

echo "6. GATED route, dispatched: the build lands the merge on GitHub main; the clone fast-forwards; mirror follows"
D=$(topology f)
( cd "$D/main/.clones/c" && echo 'def a(): return 3' > .claude/skills/x/a.py && git add -A && git commit -qm engine ); stamp_hooks "$D"
# the "build": merges main into the mailbox commit and pushes the result to GitHub main
BUILD="git -C $D/main/.clones/c push -q $D/github.git HEAD:main && echo DISPATCHED > $D/main/.clones/c/.git/ci-verdict"
OUT=$(CI_ROUTE=GATED CI_MERGE="$BUILD" syncmain "$D" push); check "gated route dispatched" 0 $?
[ "$(git -C "$D/github.git" rev-parse main)" = "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  clone and GitHub main differ after the gated push"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  mirror did not follow the gated landing"; FAIL=$((FAIL+1)); }

echo "7. GATED route, SKIP-VERIFIED: the clone pushes directly (a build already verified this tree)"
D=$(topology g)
( cd "$D/main/.clones/c" && echo 'def a(): return 4' > .claude/skills/x/a.py && git add -A && git commit -qm engine ); stamp_hooks "$D"
OUT=$(CI_ROUTE=GATED CI_MERGE="echo SKIP-VERIFIED > $D/main/.clones/c/.git/ci-verdict" syncmain "$D" push); check "skip-verified pushes directly" 0 $?
[ "$(git -C "$D/github.git" rev-parse main)" = "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  skip-verified did not land"; FAIL=$((FAIL+1)); }

echo "7b. GATED-LOCAL route (remote off, feature 132): SKIP-VERIFIED pushes directly; a refusal keeps the work in the clone"
D=$(topology gl)
( cd "$D/main/.clones/c" && echo 'def a(): return 5' > .claude/skills/x/a.py && git add -A && git commit -qm engine ); stamp_hooks "$D"
OUT=$(CI_ROUTE=GATED-LOCAL CI_MERGE="false" syncmain "$D" push); check "gated-local refused by ci-merge -> push fails" 1 $?
expect_out "route GATED (local - remote off)"
[ "$(git -C "$D/github.git" rev-parse main)" != "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  a refused gated-local push landed"; FAIL=$((FAIL+1)); }
OUT=$(CI_ROUTE=GATED-LOCAL CI_MERGE="echo SKIP-VERIFIED > $D/main/.clones/c/.git/ci-verdict" syncmain "$D" push); check "gated-local skip-verified pushes directly" 0 $?
[ "$(git -C "$D/github.git" rev-parse main)" = "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  gated-local skip-verified did not land"; FAIL=$((FAIL+1)); }

echo "7c. THE SEAMS ARE IGNORED IN A REAL-SHAPED TREE (feature 132): CI_ROUTE=DIRECT cannot skip the gated route"
D=$(topology gs)
( cd "$D/main/.clones/c" && mkdir -p .claude/skills/diagram && printf 'ci-status:\n\t@false\nperf-review:\n\t@true\n' > .claude/skills/diagram/Makefile && echo 'def a(): return 6' > .claude/skills/x/a.py && git add -A && git commit -qm engine ); stamp_hooks "$D"
OUT=$(CI_ROUTE=DIRECT CI_MERGE="true" syncmain "$D" push); check "a real-shaped tree with CI_ROUTE=DIRECT does not push" 1 $?
expect_out "could not decide the route"
[ "$(git -C "$D/github.git" rev-parse main)" != "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  the seam bypassed the gated route"; FAIL=$((FAIL+1)); }

echo "7d. A FEATURE IN PROGRESS LANDS NOTHING (feature 133): open tasks refuse both routes; the spec directory alone is the one exception"
D=$(topology fp)
( cd "$D/main/.clones/c" && mkdir -p specs/140-x && printf -- '- [ ] T01 open\n' > specs/140-x/tasks.md && printf -- '**Status**: APPROVED by `spec-fidelity` - round 1 verdict FAITHFUL\n' > specs/140-x/spec.md && echo docs > note.md && git add -A && git commit -qm "feature plus docs" )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: open tasks + an unrelated file -> refused on the DIRECT route" 1 $?
expect_out "IN PROGRESS"
expect_out "note.md"
[ "$(git -C "$D/github.git" rev-parse main)" != "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  a feature in progress landed"; FAIL=$((FAIL+1)); }
D=$(topology fq)
( cd "$D/main/.clones/c" && mkdir -p specs/140-x && printf -- '- [ ] T01 open\n' > specs/140-x/tasks.md && printf -- '**Status**: APPROVED by `spec-fidelity` - round 1 verdict FAITHFUL\n' > specs/140-x/spec.md && git add -A && git commit -qm "the claim" )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "the spec directory ALONE (the number claim) is allowed" 0 $?
expect_out "the claim), allowed"
( cd "$D/main/.clones/c" && echo docs > note.md && git add -A && git commit -qm docs )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "a later docs push from the same clone: the delta no longer touches the spec dir -> the pointer decides" 0 $?
( cd "$D/main/.clones/c" && mkdir -p .specify && echo '{"feature_directory": "specs/140-x"}' > .specify/feature.json && echo more > note.md && git add -A && git commit -qm docs2 )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: the pointer names a feature with open tasks -> refused even for docs" 1 $?
( cd "$D/main/.clones/c" && printf -- '- [x] T01 done\n' > specs/140-x/tasks.md && git add -A && git commit -qm done )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "STAYS QUIET: every task ticked -> the docs land" 0 $?
( cd "$D/main/.clones/c" && echo 'def a(): return 9' > .claude/skills/x/a.py && printf -- '- [x] T01 done\n- [ ] T02 the GM accepts\n' > specs/140-x/tasks.md && git add -A && git commit -qm engine ); stamp_hooks "$D"
OUT=$(CI_ROUTE=GATED CI_MERGE="echo SKIP-VERIFIED > $D/main/.clones/c/.git/ci-verdict" syncmain "$D" push); check "IT FIRES on the GATED route too, before ci-merge is even consulted" 1 $?
expect_out "IN PROGRESS"

echo "8. origins are re-pointed at GitHub once, and said so"
D=$(topology h)
git -C "$D/main/.clones/c" remote set-url origin "$D/main"
OUT=$(syncmain "$D" sync-in); check "sync-in with a stale origin" 0 $?
expect_out "origin of"
[ "$(git -C "$D/main/.clones/c" remote get-url origin)" = "$D/github.git" ] && PASS=$((PASS+1)) || { echo "FAIL  origin not re-pointed"; FAIL=$((FAIL+1)); }

echo "9. the build's push line is a compare-and-swap: main moved between fetch and push -> rejected, nothing lands (R3, T036)"
D=$(topology i)
git clone -q "$D/github.git" "$D/build"; git clone -q "$D/github.git" "$D/other"
( cd "$D/other" && echo 2 > g && git add g && git commit -qm "landed in between" && git push -q origin HEAD:main )
( cd "$D/build" && echo 3 > h && git add h && git commit -qm "the merge result" )
OUT=$(cd "$D/build" && { git push origin HEAD:main 2>&1 || echo "main moved; re-run (the push was not a fast-forward - nothing landed)"; }); check "non-fast-forward push refused" 0 $?
expect_out "main moved; re-run"
[ "$(git -C "$D/github.git" log -1 --format=%s main)" = "landed in between" ] && PASS=$((PASS+1)) || { echo "FAIL  something landed over the in-between commit"; FAIL=$((FAIL+1)); }

echo "10. the performance bands are enforced at the push (feature 129): a refused review stops it, a passing one does not"
D=$(topology j)
( cd "$D/main/.clones/c" && echo docs > note.md && git add -A && git commit -qm docs )
gh_before=$(git -C "$D/github.git" rev-parse main)
OUT=$(CI_ROUTE=DIRECT CI_PERF_REVIEW="echo 'perf-review: [local] band 3 - MISSING: the GM sign-off'; false" syncmain "$D" push); check "IT FIRES: a refused perf-review stops the push" 1 $?
expect_out "performance bands owe a record"
[ "$(git -C "$D/github.git" rev-parse main)" = "$gh_before" ] && PASS=$((PASS+1)) || { echo "FAIL  the push landed despite the refused review"; FAIL=$((FAIL+1)); }
OUT=$(CI_ROUTE=DIRECT CI_PERF_REVIEW="echo 'perf-review: nothing owed'" syncmain "$D" push); check "STAYS QUIET: a passing perf-review pushes" 0 $?

# GUARD_EDIT_OK: feature 167 - A NEW CLONE BORROWS A SIBLING ROLL CACHE (GM 2026-08-30). Measured:
# a clone that has never rolled pays 30 s for the reference settlement and 122 s for the map-rolling
# gate tests; seeded from a sibling at the same commit those become 5 s and 28 s. The seeding may
# never make a clone WRONG, so the vectors below pin what it must not do as firmly as what it does.
echo "== the roll cache is seeded from a sibling at the same commit =="
D=$(topology seed167)
SIB="$D/main/.clones/sib"; git clone -q "$D/github.git" "$SIB"
mkdir -p "$SIB/.claude/skills/diagram/.gencache/rolls/abc"
echo '{"key":"k","subject":"s","deps":{"functions":[],"files":[]}}' > "$SIB/.claude/skills/diagram/.gencache/rolls/abc/meta.json"

OUT=$(syncmain "$D" sync-in); check "sync-in succeeds" 0 $?
[ -d "$D/main/.clones/c/.claude/skills/diagram/.gencache/rolls/abc" ] \
  && { echo "  ok    a clone with no cache is seeded from the sibling"; PASS=$((PASS+1)); } \
  || { echo "FAIL  the clone was not seeded"; FAIL=$((FAIL+1)); }
expect_out "seeded the roll cache"

# ...and it must NOT overwrite a cache the clone already has - that one is keyed to work in progress
echo 'MINE' > "$D/main/.clones/c/.claude/skills/diagram/.gencache/mine.txt"
OUT=$(syncmain "$D" sync-in)
[ -f "$D/main/.clones/c/.claude/skills/diagram/.gencache/mine.txt" ] \
  && { echo "  ok    an existing cache is left alone"; PASS=$((PASS+1)); } \
  || { echo "FAIL  the seeding clobbered an existing cache"; FAIL=$((FAIL+1)); }

# ...and a sibling at a DIFFERENT commit is not taken: the clone starts cold instead
D2=$(topology seed167b)
SIB2="$D2/main/.clones/sib"; git clone -q "$D2/github.git" "$SIB2"
mkdir -p "$SIB2/.claude/skills/diagram/.gencache/rolls/xyz"
( cd "$SIB2" && echo drift > drift.txt && git add -A && git -c user.email=t@t -c user.name=t commit -qm drift )
OUT=$(syncmain "$D2" sync-in)
[ -d "$D2/main/.clones/c/.claude/skills/diagram/.gencache" ] \
  && { echo "FAIL  seeded from a sibling at a different commit"; FAIL=$((FAIL+1)); } \
  || { echo "  ok    a sibling at another commit is refused - the clone starts cold"; PASS=$((PASS+1)); }

echo "-----"
if [ "$FAIL" -eq 0 ]; then echo "all sync-with-main tests passed ($PASS checks)"; exit 0; else echo "SOME TESTS FAILED ($FAIL)"; exit 1; fi
