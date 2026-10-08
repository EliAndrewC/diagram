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
mkdir -p "$D/main/.clones/c/pool/hamlets/x"
printf 'pool-index:\n\t@echo built >> pool/index.html\npool-index-if-stale:\n\t@if [ ! -f pool/index.html ] || [ -n "$$(find pool legacy-hand-authored-pool -newer pool/index.html \\( -name "*.json" -o -name "*.png" -o -name "*.notes.md" \\) -print -quit 2>/dev/null)" ]; then $(MAKE) --no-print-directory pool-index; fi\n' > "$D/main/.clones/c/Makefile"
IDX="$D/main/.clones/c/pool/index.html"
OUT=$(syncmain "$D" sync-in --mirror-only); check "mirror-only sync-in with no index" 0 $?
[ "$(cat "$IDX" 2>/dev/null)" = "built" ] && PASS=$((PASS+1)) || { echo "FAIL  missing index was not built on the dirty-clone branch"; FAIL=$((FAIL+1)); }
OUT=$(syncmain "$D" sync-in); check "sync-in with a fresh index" 0 $?
[ "$(cat "$IDX")" = "built" ] && PASS=$((PASS+1)) || { echo "FAIL  fresh index was rebuilt (efficiency check did not hold)"; FAIL=$((FAIL+1)); }
touch -d '-10 seconds' "$IDX"; echo '{}' > "$D/main/.clones/c/pool/hamlets/x/x.json"
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
( cd "$D/main/.clones/c" && printf 'ci-status:\n\t@false\nperf-review:\n\t@true\n' > Makefile && echo 'def a(): return 6' > .claude/skills/x/a.py && git add -A && git commit -qm engine ); stamp_hooks "$D"
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
# GUARD_EDIT_OK: feature 243 - a ticked feature now also owes its plan review at the push, so this finished
# feature proves the plan gate is WIRED into the push (refused without the record) before it lands with one.
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: ticked tasks with no plan review -> refused (feature 243)" 1 $?
expect_out "PLAN GATE"
( cd "$D/main/.clones/c" && printf '# plan\n' > specs/140-x/plan.md \
  && printf '{"plan_sha256": "%s", "decisions": [], "verdict": "CLEAR"}\n' "$(sha256sum specs/140-x/plan.md | cut -d' ' -f1)" > specs/140-x/plan-review.json \
  && git add -A && git commit -qm "the plan, reviewed" )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "STAYS QUIET: every task ticked and the plan reviewed -> the docs land" 0 $?
( cd "$D/main/.clones/c" && echo 'def a(): return 9' > .claude/skills/x/a.py && printf -- '- [x] T01 done\n- [ ] T02 the GM accepts\n' > specs/140-x/tasks.md && git add -A && git commit -qm engine ); stamp_hooks "$D"
OUT=$(CI_ROUTE=GATED CI_MERGE="echo SKIP-VERIFIED > $D/main/.clones/c/.git/ci-verdict" syncmain "$D" push); check "IT FIRES on the GATED route too, before ci-merge is even consulted" 1 $?
expect_out "IN PROGRESS"

echo "8. origins are re-pointed at GitHub once, and said so"
D=$(topology h)
git -C "$D/main/.clones/c" remote set-url origin "$D/main"
OUT=$(syncmain "$D" sync-in); check "sync-in with a stale origin" 0 $?
expect_out "origin of"
[ "$(git -C "$D/main/.clones/c" remote get-url origin)" = "$D/github.git" ] && PASS=$((PASS+1)) || { echo "FAIL  origin not re-pointed"; FAIL=$((FAIL+1)); }

echo "8b. the MIRROR's origin is the GM's: never re-pointed, and the mirror still refreshes by URL (2026-10-03)"
D=$(topology h2)
git -C "$D/main" remote set-url origin "ssh://git@example.invalid/gm-own-remote.git"
( cd "$D/seed" && echo more > g && git add -A && git commit -qm upstream && git push -q "$D/github.git" HEAD:main )
OUT=$(syncmain "$D" sync-in); check "sync-in with the GM's SSH origin on the mirror" 0 $?
[ "$(git -C "$D/main" remote get-url origin)" = "ssh://git@example.invalid/gm-own-remote.git" ] && PASS=$((PASS+1)) || { echo "FAIL  the mirror's origin was re-pointed"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  mirror did not fast-forward by URL"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main" rev-parse origin/main)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  the mirror's origin/main was not refreshed"; FAIL=$((FAIL+1)); }

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
mkdir -p "$SIB/.gencache/rolls/abc"
echo '{"key":"k","subject":"s","deps":{"functions":[],"files":[]}}' > "$SIB/.gencache/rolls/abc/meta.json"

OUT=$(syncmain "$D" sync-in); check "sync-in succeeds" 0 $?
[ -d "$D/main/.clones/c/.gencache/rolls/abc" ] \
  && { echo "  ok    a clone with no cache is seeded from the sibling"; PASS=$((PASS+1)); } \
  || { echo "FAIL  the clone was not seeded"; FAIL=$((FAIL+1)); }
expect_out "seeded the roll cache"

# ...and it must NOT overwrite a cache the clone already has - that one is keyed to work in progress
echo 'MINE' > "$D/main/.clones/c/.gencache/mine.txt"
OUT=$(syncmain "$D" sync-in)
[ -f "$D/main/.clones/c/.gencache/mine.txt" ] \
  && { echo "  ok    an existing cache is left alone"; PASS=$((PASS+1)); } \
  || { echo "FAIL  the seeding clobbered an existing cache"; FAIL=$((FAIL+1)); }

# ...and a sibling at a DIFFERENT commit is not taken: the clone starts cold instead
D2=$(topology seed167b)
SIB2="$D2/main/.clones/sib"; git clone -q "$D2/github.git" "$SIB2"
mkdir -p "$SIB2/.gencache/rolls/xyz"
( cd "$SIB2" && echo drift > drift.txt && git add -A && git -c user.email=t@t -c user.name=t commit -qm drift )
OUT=$(syncmain "$D2" sync-in)
[ -d "$D2/main/.clones/c/.gencache" ] \
  && { echo "FAIL  seeded from a sibling at a different commit"; FAIL=$((FAIL+1)); } \
  || { echo "  ok    a sibling at another commit is refused - the clone starts cold"; PASS=$((PASS+1)); }

echo "11. a clone whose history shares no commit with main's is refused, never merged (feature 301 FR-019)"
D=$(topology unrelated301)
git init -q -b main "$D/rewritten"
( cd "$D/rewritten" && mkdir -p scripts && echo base > f && echo '.clones/' > .gitignore && cp "$HERE"/*.sh "$HERE"/*.py scripts/ && git add -A \
  && git -c user.email=t@t -c user.name=t commit -qm "the rewritten history" && git push -q -f "$D/github.git" HEAD:main )
before=$(git -C "$D/main/.clones/c" rev-parse HEAD)
OUT=$(syncmain "$D" sync-in); check "sync-in on an unrelated history" 1 $?
expect_out "shares no commit with main"
[ "$(git -C "$D/main/.clones/c" rev-parse HEAD)" = "$before" ] && PASS=$((PASS+1)) || { echo "FAIL  the clone merged the unrelated history"; FAIL=$((FAIL+1)); }

echo "12. the prompt hook's path: render-sync detached, one runner at a time, a bounded lock wait (2026-10-02)"
# GUARD_EDIT_OK: new test cases for the hook's --background-render path; nothing existing loosened
D=$(topology bg)
mkdir -p "$D/main"
MARK="$D/rendered"
printf 'render-sync:\n\t@sleep 2; git -C %s rev-parse --short HEAD >> %s\n' "$D/main" "$MARK" > "$D/main/Makefile"
( cd "$D/seed" && echo more > g && git add -A && git commit -qm upstream && git push -q "$D/github.git" HEAD:main )
start=$(date +%s)
OUT=$(syncmain "$D" sync-in --background-render); check "sync-in --background-render" 0 $?
[ $(( $(date +%s) - start )) -lt 2 ] && [ ! -f "$MARK" ] && PASS=$((PASS+1)) || { echo "FAIL  sync-in waited for the render"; FAIL=$((FAIL+1)); }
expect_out "render-sync started in the background"
[ "$(git -C "$D/main/.clones/c" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  clone did not merge"; FAIL=$((FAIL+1)); }
# a second start while the first runs exits at once and does not render twice
( cd "$D/main/.clones/c" && CLONE_MAIN="$D/main" CLONE_GITHUB="$D/github.git" GITHUB_TOKEN=unused "$SYNC" render-sync-runner >/dev/null 2>&1 ); check "a second runner exits at once" 0 $?
for _ in $(seq 1 30); do grep -q '^ok' "$D/main/.clones/.render-sync.status" 2>/dev/null && break; sleep 0.5; done
[ "$(wc -l < "$MARK" 2>/dev/null)" = 1 ] && PASS=$((PASS+1)) || { echo "FAIL  expected one background render, got: $(cat "$MARK" 2>/dev/null)"; FAIL=$((FAIL+1)); }
grep -q '^ok .* at '"$(git -C "$D/main" rev-parse --short HEAD)" "$D/main/.clones/.render-sync.status" && PASS=$((PASS+1)) || { echo "FAIL  status: $(cat "$D/main/.clones/.render-sync.status" 2>/dev/null)"; FAIL=$((FAIL+1)); }
# an earlier failure is reported on the next sync
echo "FAILED 2026-10-02 exit 2 at abc1234" > "$D/main/.clones/.render-sync.status"
OUT=$(syncmain "$D" sync-in --background-render); check "sync-in after a failed render" 0 $?
expect_out "last background render-sync FAILED"
for _ in $(seq 1 30); do grep -q '^ok' "$D/main/.clones/.render-sync.status" 2>/dev/null && break; sleep 0.5; done
# a busy lock: the mirror is skipped this turn, the clone still merges, and the call returns inside the wait
( cd "$D/seed" && echo again > h && git add -A && git commit -qm upstream2 && git push -q "$D/github.git" HEAD:main )
flock "$D/main/.clones/.sync.lock" sleep 6 & HOLDER=$!
sleep 0.3
mirror_before=$(git -C "$D/main" rev-parse HEAD)
start=$(date +%s)
OUT=$(cd "$D/main/.clones/c" && SYNC_LOCK_WAIT=1 CLONE_MAIN="$D/main" CLONE_GITHUB="$D/github.git" GITHUB_TOKEN=unused "$SYNC" sync-in --background-render 2>&1); check "sync-in with the lock held" 0 $?
[ $(( $(date +%s) - start )) -lt 5 ] && PASS=$((PASS+1)) || { echo "FAIL  sync-in did not give up on the lock"; FAIL=$((FAIL+1)); }
expect_out "mirror lock stayed busy"
[ "$(git -C "$D/main" rev-parse HEAD)" = "$mirror_before" ] && PASS=$((PASS+1)) || { echo "FAIL  the mirror moved without the lock"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main/.clones/c" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  the clone did not merge while the mirror was busy"; FAIL=$((FAIL+1)); }
kill "$HOLDER" 2>/dev/null; wait "$HOLDER" 2>/dev/null
# a hand commit in the mirror still stops the hook's path, as it stops the synchronous one
( cd "$D/main" && echo rogue > rogue && git add -A && git commit -qm "committed in main by hand" )
OUT=$(syncmain "$D" sync-in --background-render); check "a mirror commit -> refused on the hook's path" 1 $?
expect_out "cannot fast-forward"

# GUARD_EDIT_OK: feature 321 - new cases for the backup step at the stop; nothing existing loosened.
yes_() { PASS=$((PASS+1)); }
no_() { echo "FAIL  $1"; FAIL=$((FAIL+1)); }
rref() { git -C "$1/github.git" rev-parse -q --verify "refs/heads/$2"; }
in_progress() { # $1 = topology dir: a feature with an open task plus an unrelated file, so a stop is refused
  ( cd "$1/main/.clones/c" && mkdir -p specs/140-x && printf -- '- [ ] T01 open\n' > specs/140-x/tasks.md \
    && printf -- '**Status**: APPROVED by `spec-fidelity` - round 1 verdict FAITHFUL\n' > specs/140-x/spec.md \
    && echo "${2:-docs}" > note.md && git add -A && git commit -qm "feature plus docs ${2:-}" )
}

echo "11. a REFUSED stop backs the clone's HEAD up to backup/<clone-name>, and nothing else (feature 321, SC-001, SC-002)"
D=$(topology bk)
git -C "$D/github.git" config core.logAllRefUpdates always
in_progress "$D"
OUT=$(CI_ROUTE=DIRECT syncmain "$D" done); check "a refused done keeps its exit code" 1 $?
expect_out "IN PROGRESS"; expect_out "backed up HEAD"
[ "$(rref "$D" backup/c)" = "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && yes_ || no_ "backup/c is not the clone's HEAD"
[ "$(git -C "$D/main/.clones/c" for-each-ref --format='%(refname)' refs/heads)" = "refs/heads/main" ] && yes_ || no_ "the clone has a local branch beside main"
[ "$(git -C "$D/github.git" for-each-ref --format='%(refname)' | tr '\n' ' ')" = "refs/heads/backup/c refs/heads/main " ] && yes_ || no_ "the remote carries refs beyond main and backup/c: $(git -C "$D/github.git" for-each-ref --format='%(refname)')"
OUT=$(CI_ROUTE=DIRECT syncmain "$D" done); check "a second refused done, nothing new" 1 $?
case "$OUT" in *"backed up HEAD"*) no_ "a second stop with nothing new pushed again" ;; *) yes_ ;; esac
[ "$(git -C "$D/github.git" reflog show refs/heads/backup/c | wc -l)" = 1 ] && yes_ || no_ "the backup ref moved more than once"
bk_before=$(rref "$D" backup/c)
( cd "$D/seed" && echo more > g && git add -A && git commit -qm upstream && git push -q "$D/github.git" HEAD:main )
( cd "$D/main/.clones/c" && echo again > note2.md && git add -A && git commit -qm "more work" )
OUT=$(syncmain "$D" sync-in); check "sync-in after more work" 0 $?
[ "$(rref "$D" backup/c)" = "$bk_before" ] && yes_ || no_ "sync-in moved the backup"
OUT=$(syncmain "$D" push); check "push (the stop without the render) is refused too" 1 $?
[ "$(rref "$D" backup/c)" = "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && yes_ || no_ "push did not back up the new HEAD"

echo "12. a DIVERGED backup is never forced; the message says HEAD is NOT backed up and prints the GM's merge (SC-003)"
D=$(topology bd)
( cd "$D/seed" && echo old > lost && git add -A && git commit -qm "a dead clone's work" && git push -q "$D/github.git" HEAD:refs/heads/backup/c )
old=$(rref "$D" backup/c)
in_progress "$D"
OUT=$(CI_ROUTE=DIRECT syncmain "$D" done); check "a refused done with a diverged backup" 1 $?
expect_out "IN PROGRESS"; expect_out "HEAD is NOT backed up"; expect_out "merges that backup's commits into this clone's HEAD, so they land on main"
[ "$(rref "$D" backup/c)" = "$old" ] && yes_ || no_ "the diverged backup was overwritten"
FIX=$(printf '%s\n' "$OUT" | grep '^  git -C .* fetch origin refs/heads/backup/c && ' || true)
[ -n "$FIX" ] && yes_ || no_ "no resolving command printed"
case "$FIX" in *--force*|*" +"*|*--delete*|*" :refs"*) no_ "the command forces or deletes: $FIX" ;; *merge*push\ origin\ HEAD:refs/heads/backup/c) yes_ ;; *) no_ "the command is not fetch, merge, push: $FIX" ;; esac
head=$(git -C "$D/main/.clones/c" rev-parse HEAD)
( export CLONE_GITHUB=; eval "$FIX" ) >/dev/null 2>&1 && yes_ || no_ "the printed command failed"
new=$(rref "$D" backup/c)
git -C "$D/github.git" merge-base --is-ancestor "$old" "$new" && git -C "$D/github.git" merge-base --is-ancestor "$head" "$new" && yes_ || no_ "the resolved backup does not hold both the old tip and HEAD"

echo "13. a remote that refuses or cannot be reached changes nothing about the stop (SC-004)"
D=$(topology bu)
printf '#!/bin/sh\nwhile read o n r; do case "$r" in refs/heads/backup/*) echo "backups refused here"; exit 1 ;; esac; done\n' > "$D/github.git/hooks/pre-receive"; chmod +x "$D/github.git/hooks/pre-receive"
in_progress "$D"
OUT=$(CI_ROUTE=DIRECT syncmain "$D" done); check "a refused done whose backup push is rejected" 1 $?
expect_out "IN PROGRESS"; expect_out "backup NOT pushed to backup/c: "; expect_out "backups refused here"
[ "$(printf '%s\n' "$OUT" | grep -c 'backup NOT')" = 1 ] && yes_ || no_ "the failure is not one line"
mv "$D/github.git" "$D/github.gone"
OUT=$(CI_ROUTE=DIRECT syncmain "$D" done); check "an unreachable remote: the stop fails as it would anyway" 1 $?
mv "$D/github.gone" "$D/github.git"
expect_out "backup NOT checked - cannot reach origin"
[ "$(printf '%s\n' "$OUT" | grep -c 'backup NOT')" = 1 ] && yes_ || no_ "the failure is not one line"
D=$(topology bv)
( cd "$D/main/.clones/c" && echo docs > note.md && git add -A && git commit -qm docs && git push -q origin HEAD:refs/heads/backup/c )
printf '#!/bin/sh\nwhile read o n r; do case "$r" in refs/heads/backup/*) echo "backups refused here"; exit 1 ;; esac; done\n' > "$D/github.git/hooks/pre-receive"; chmod +x "$D/github.git/hooks/pre-receive"
OUT=$(CI_ROUTE=DIRECT syncmain "$D" done); check "a landing whose backup delete is rejected still lands" 0 $?
expect_out "backup/c NOT deleted"
[ "$(rref "$D" main)" = "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && yes_ || no_ "the work did not land"

echo "14. landing deletes the clone's backup; the sweep deletes exactly the backups main contains (SC-006)"
D=$(topology bl)
( cd "$D/main/.clones/c" && echo docs > note.md && git add -A && git commit -qm docs )
OUT=$(CI_ROUTE=DIRECT CI_PERF_REVIEW=false syncmain "$D" done); check "a refused stop (perf review) backs up" 1 $?
[ -n "$(rref "$D" backup/c)" ] && yes_ || no_ "no backup after the refused stop"
( cd "$D/seed" && git push -q "$D/github.git" HEAD:refs/heads/backup/old && echo ahead > ahead && git add -A && git commit -qm ahead && git push -q "$D/github.git" HEAD:refs/heads/backup/ahead )
OUT=$(CI_ROUTE=DIRECT syncmain "$D" done); check "the stop that lands" 0 $?
expect_out "deleted backup/c on GitHub"
[ -z "$(rref "$D" backup/c)" ] && yes_ || no_ "the landed clone's backup is still there"
[ -z "$(rref "$D" backup/old)" ] && yes_ || no_ "the sweep kept a backup main contains"
[ -n "$(rref "$D" backup/ahead)" ] && yes_ || no_ "the sweep deleted a backup ahead of main"
( cd "$D/main/.clones/c" && echo more > note.md && git add -A && git commit -qm more && git push -q origin HEAD:refs/heads/backup/c )
OUT=$(CI_ROUTE=DIRECT CI_PERF_REVIEW=false syncmain "$D" done); check "a stop with the backup already at HEAD" 1 $?
case "$OUT" in *"backed up HEAD"*) no_ "pushed a backup that was already at HEAD" ;; *) yes_ ;; esac

echo "15. a clone with work in flight syncs in a move of the project to the root (feature 329, FR-008, FR-009)"
# GUARD_EDIT_OK: feature 329 - a NEW case. The old path is built by concatenation so the old-layout check (which reads
# this file) does not count it; the global git config is switched off so the case proves the SCRIPT passes
# merge.directoryRenames, not the container's ~/.gitconfig.
OLDP=".claude/skills/""diagram"
D=$(topology mv)
( cd "$D/seed" && mkdir -p "$OLDP/dev" "$OLDP/l7r" && printf 'a\nb\nc\n' > "$OLDP/dev/x.md" && echo 'X = 1' > "$OLDP/l7r/a.py" \
  && echo '.gencache/' >> .gitignore && git add -A && git commit -qm old-layout && git push -q "$D/github.git" HEAD:main )
OUT=$(GIT_CONFIG_GLOBAL=/dev/null syncmain "$D" sync-in); check "the clone takes the old layout" 0 $?
( cd "$D/main/.clones/c" && printf 'a\nB\nc\n' > "$OLDP/dev/x.md" && echo new > "$OLDP/dev/new.md" && mkdir -p "$OLDP/.gencache" \
  && echo warm > "$OLDP/.gencache/k" && git add -A && git commit -qm in-flight )
( cd "$D/seed" && git mv "$OLDP/dev" dev && git mv "$OLDP/l7r" l7r && git commit -qm move && git push -q "$D/github.git" HEAD:main )
OUT=$(GIT_CONFIG_GLOBAL=/dev/null syncmain "$D" sync-in); check "sync-in merges the move into the clone with work in flight" 0 $?
C="$D/main/.clones/c"
grep -qx B "$C/dev/x.md" 2>/dev/null && yes_ || no_ "the clone's edit did not land on the moved file"
[ "$(cat "$C/dev/new.md" 2>/dev/null)" = new ] && yes_ || no_ "a file the clone added under the old directory did not follow the rename"
[ "$(cat "$C/.gencache/k" 2>/dev/null)" = warm ] && yes_ || no_ "the clone's ignored cache was not carried to the root"
[ ! -e "$C/$OLDP" ] && yes_ || no_ "the old directory was left behind"
[ -z "$(git -C "$C" status --porcelain)" ] && yes_ || no_ "the merge left the clone dirty: $(git -C "$C" status --porcelain | head -3)"

echo "-----"
if [ "$FAIL" -eq 0 ]; then echo "all sync-with-main tests passed ($PASS checks)"; exit 0; else echo "SOME TESTS FAILED ($FAIL)"; exit 1; fi
