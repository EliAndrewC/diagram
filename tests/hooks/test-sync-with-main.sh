#!/usr/bin/env bash
# Tests for sync-with-main.sh - the route decision, the mirror refresh, and the gated/direct pushes
# (feature 130; constitution XVIII: the route decision is a guard, so it ships with its test).
# Run: tests/hooks/test-sync-with-main.sh   (exit 0 = all green). Runs under `make hooks-test`, which
# derives this companion's name from the script's (test-<script>).
#
# The fixture stands in for the whole topology: a bare "github" repository, a MAIN checkout that is
# its mirror, and a session CLONE under main/.clones/. CLONE_MAIN, CLONE_GITHUB, CI_ROUTE and
# CI_MERGE are the script's test seams - the real route decision calls `make ci-status ROUTE=1`,
# which needs the whole skill and is tested in tests/ci/; here the seam supplies the answer.
set -uo pipefail
# the suite's own runs start clean: a landing worktree's make land (451 T88's land-alone) exports SYNC_BACKUP=off and
# L7R_LAND_ALONE=1, which every scratch run here would otherwise inherit (cases 10-11 then saw no backup)
unset SYNC_BACKUP L7R_LAND_ALONE
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC="$HERE/../../scripts/sync-with-main.sh"
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
# THE TOPOLOGY IS BUILT ONCE AND COPIED PER CASE (feature 449 T106, measured 2026-11-11): building it - the scripts tree copied
# into a seed, committed, pushed and cloned twice - cost 0.25 s a case against 0.03 s for a `cp -a` of the same four repositories,
# and the first `stamp --write` in a fresh clone computed the id of every scripts/ file (by codeid.py until 449 T247; by its blob id since). So template_build makes it once,
# before the parts, with the clone's id cache warmed (the semantic-id-cache a real clone holds after its first stamp, keyed by
# blob, so a copied entry is exactly what a cold run computes) and the stamps that warming wrote removed; topology copies it
# and re-points the two origins at the copy's own github.git (the template's path would make every sync-in re-point and say so).
# Each case still gets its own copy - nothing is shared between cases but the read-only template.
template_build() { # $1 = dir; builds $1/{github.git,seed,main,main/.clones/c}
  local d=$1; rm -rf "$d"; mkdir -p "$d"
  git init -q --bare -b main "$d/github.git"
  git init -q -b main "$d/seed"; ( cd "$d/seed" && mkdir -p scripts pool/x && echo base > f && echo '.clones/' > .gitignore && echo 'def a(): return 1' > pool/x/a.py && cp -r "$HERE/../../scripts/." scripts/ && printf '#!/usr/bin/env bash\nexec "%s" "$@"\n' "$(cd "$HERE/../.." && pwd)/scripts/gates/l7r-gate.sh" > scripts/gates/l7r-gate.sh && git add -A && git commit -qm base && git push -q "$d/github.git" HEAD:main )
  git clone -q "$d/github.git" "$d/main"
  git -C "$d/main" config receive.denyCurrentBranch updateInstead
  mkdir -p "$d/main/.clones/.session-clones"
  git clone -q "$d/github.git" "$d/main/.clones/c"
  stamp_hooks "$d"
  # T109: the push's self-tests passed once here, as a real clone's are after its first push, so each copy keeps them (they are kept
  # against this tree's scripts/ and gate binary, which every case shares); each self-test is pinned by its own crate's tests
  ( cd "$d/main/.clones/c" && scripts/gates/l7r-gate.sh push-checks "$PWD" >/dev/null 2>&1 ) || true
  rm -f "$d/main/.clones/c/.git/gate-green-"* "$d/main/.clones/c/.git/tool-usage.jsonl"
}
topology() { # $1 = name; copies the template to $T/$1/{github.git,seed,main,main/.clones/c}
  local d=$T/$1; rm -rf "$d"
  cp -a "$TEMPLATE" "$d"
  git -C "$d/main" remote set-url origin "$d/github.git"
  git -C "$d/main/.clones/c" remote set-url origin "$d/github.git"
  echo "$d"
}
syncmain() { # $1 = topology dir, then args
  local d=$1; shift
  ( cd "$d/main/.clones/c" && CLONE_MAIN="$d/main" CLONE_GITHUB="$d/github.git" GITHUB_TOKEN=unused "$SYNC" "$@" 2>&1 )
}
stamp_hooks() { ( cd "$1/main/.clones/c" && scripts/gates/l7r-gate.sh stamp --write hooks >/dev/null && scripts/gates/l7r-gate.sh stamp --write diagram >/dev/null ); }

# GUARD_EDIT_OK: feature 321 - new cases for the backup step at the stop; nothing existing loosened. (Feature 375 amendment 4: the
# helpers they share are defined here, before the cases, so a case finds them whichever part runs it.)
yes_() { PASS=$((PASS+1)); }
no_() { echo "FAIL  $1"; FAIL=$((FAIL+1)); }
rref() { git -C "$1/github.git" rev-parse -q --verify "refs/heads/$2"; }
# T106: a case that holds the mirror lock in the background waits until it IS held, not a fixed 0.3 s (10 s at most)
lock_held() { local i; for i in $(seq 1 1000); do flock -n "$1" true 2>/dev/null || return 0; sleep 0.01; done; }
# feature 405 T32 (D4): only the task being worked holds a landing - the clone's active task (`make task-start`)
# feature 451 T254: a started task holds a push only by its files the delta carries - so a start here also files the task's Edit of
# each file of HEAD's commit on the feature's event log, half a second after it, as the writer would have
start() {
  local c="$1/main/.clones/c" task="${2:-T01}" t top
  printf '{"feature": "140-x", "task": "%s"}\n' "$task" > "$c/.git/active-task"
  t=$(date -u -d "@$(git -C "$c" log -1 --format=%ct)" +%Y-%m-%dT%H:%M:%S).500Z; top=$(cd "$c" && pwd -P)
  mkdir -p "$c/.git/l7r-events"
  git -C "$c" diff-tree --no-commit-id --name-only -r HEAD | while read -r f; do
    printf '{"ev":"PostToolUse","cat":"edit","task":"%s","t":"%s","path":"%s/%s"}\n' "$task" "$t" "$top" "$f"
  done >> "$c/.git/l7r-events/140-x.jsonl"
}
in_progress() { # $1 = topology dir: a feature with an open task being worked plus an unrelated file, so a stop is refused
  ( cd "$1/main/.clones/c" && mkdir -p specs/140-x && printf -- '- [ ] T01 open\n' > specs/140-x/tasks.md \
    && printf -- '**Status**: APPROVED by `spec-fidelity` - round 1 verdict FAITHFUL\n' > specs/140-x/spec.md \
    && echo "${2:-docs}" > note.md && git add -A && git commit -qm "feature plus docs ${2:-}" )
  start "$1"
}

case_01() {  # 1 s measured 2026-10-11
echo "1. sync-in refreshes the mirror from GitHub main, then the clone"
D=$(topology a)
( cd "$D/seed" && echo more > g && git add -A && git commit -qm upstream && git push -q "$D/github.git" HEAD:main )
OUT=$(syncmain "$D" sync-in); check "sync-in from a clean clone" 0 $?
[ "$(git -C "$D/main" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  mirror did not fast-forward to GitHub main"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main/.clones/c" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  clone did not merge GitHub main"; FAIL=$((FAIL+1)); }
expect_out "synced with GitHub main"
}

case_02() {  # 1 s measured 2026-10-11
echo "2. sync-in --mirror-only advances the mirror and leaves the clone alone (a dirty clone's turn)"
D=$(topology b)
( cd "$D/seed" && echo more > g && git add -A && git commit -qm upstream && git push -q "$D/github.git" HEAD:main )
before=$(git -C "$D/main/.clones/c" rev-parse HEAD)
OUT=$(syncmain "$D" sync-in --mirror-only); check "sync-in --mirror-only" 0 $?
[ "$(git -C "$D/main" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  mirror not advanced"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main/.clones/c" rev-parse HEAD)" = "$before" ] && PASS=$((PASS+1)) || { echo "FAIL  clone was touched"; FAIL=$((FAIL+1)); }
}

case_03() {  # 1 s measured 2026-10-11
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
}

case_04() {  # 1 s measured 2026-10-11
echo "3. IT FIRES: a hand commit in the mirror stops sync-in with the fast-forward message"
D=$(topology c)
( cd "$D/main" && echo rogue > rogue && git add -A && git commit -qm "committed in main by hand" )
( cd "$D/seed" && echo more > g && git add -A && git commit -qm upstream && git push -q "$D/github.git" HEAD:main )
OUT=$(syncmain "$D" sync-in); check "mirror cannot fast-forward -> refused" 1 $?
expect_out "cannot fast-forward"
}

case_05() {  # 4 s measured 2026-10-11
echo "4. DIRECT route: a docs-only delta pushes straight to GitHub main, no build, mirror follows"
D=$(topology d)
( cd "$D/main/.clones/c" && echo docs > note.md && git add -A && git commit -qm docs )
# GUARD_EDIT_OK: feature 375 amendment 9, D55 - a clean push ends the landing: review-gate.sh's glyph-landing mark is removed
echo '{"feature": "", "at": 1}' > "$D/main/.clones/c/.git/glyph-landing"
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "direct push" 0 $?
[ ! -f "$D/main/.clones/c/.git/glyph-landing" ] && PASS=$((PASS+1)) || { echo "FAIL  a clean push left the glyph-landing mark"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/github.git" rev-parse main)" = "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  GitHub main did not receive the direct push"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  mirror did not follow"; FAIL=$((FAIL+1)); }
expect_out "route DIRECT"
}

case_06() {  # 7 s measured 2026-10-11
echo "5. GATED route, refused: nothing lands, the work stays in the clone"
D=$(topology e)
( cd "$D/main/.clones/c" && echo 'def a(): return 2' > pool/x/a.py && git add -A && git commit -qm engine ); stamp_hooks "$D"
gh_before=$(git -C "$D/github.git" rev-parse main)
OUT=$(CI_ROUTE=GATED CI_MERGE="false" syncmain "$D" push); check "gated route refused by ci-merge -> push fails" 1 $?
[ "$(git -C "$D/github.git" rev-parse main)" = "$gh_before" ] && PASS=$((PASS+1)) || { echo "FAIL  something landed on GitHub main"; FAIL=$((FAIL+1)); }
expect_out "nothing landed"
}

case_07() {  # 7 s measured 2026-10-11
echo "6. GATED route, the conditions hold: the clone pushes; mirror follows"
D=$(topology f)
( cd "$D/main/.clones/c" && echo 'def a(): return 3' > pool/x/a.py && git add -A && git commit -qm engine ); stamp_hooks "$D"
OUT=$(CI_ROUTE=GATED CI_MERGE="true" syncmain "$D" push); check "gated route lands when its conditions hold" 0 $?
[ "$(git -C "$D/github.git" rev-parse main)" = "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  clone and GitHub main differ after the gated landing"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  mirror did not follow the gated landing"; FAIL=$((FAIL+1)); }
}

case_08() {
echo "7. The route is named on the way out, and a refused gated push keeps the work in the clone"
D=$(topology g)
( cd "$D/main/.clones/c" && echo 'def a(): return 4' > pool/x/a.py && git add -A && git commit -qm engine ); stamp_hooks "$D"; start "$D" T02
OUT=$(CI_ROUTE=GATED CI_MERGE="false" syncmain "$D" push); check "a refused gated push fails" 1 $?
expect_out "route GATED"
[ "$(git -C "$D/github.git" rev-parse main)" != "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  a refused gated push landed"; FAIL=$((FAIL+1)); }
}

case_09() {
echo "7b. An unknown route word is not a free push"
D=$(topology gl)
( cd "$D/main/.clones/c" && printf 'ci-status:\n\t@echo GATED-LOCAL\nwork-budget-review:\n\t@true\n' > Makefile && echo 'def a(): return 5' > pool/x/a.py && git add -A && git commit -qm engine ); stamp_hooks "$D"; start "$D" T02
OUT=$(syncmain "$D" push); check "an unknown route refuses the push" 1 $?
expect_out "could not decide the route"
}

case_10() {  # 8 s measured 2026-10-11
echo "7c. THE SEAMS ARE IGNORED IN A REAL-SHAPED TREE (feature 132): CI_ROUTE=DIRECT cannot skip the gated route"
D=$(topology gs)
( cd "$D/main/.clones/c" && printf 'ci-status:\n\t@false\nwork-budget-review:\n\t@true\n' > Makefile && echo 'def a(): return 6' > pool/x/a.py && git add -A && git commit -qm engine ); stamp_hooks "$D"
OUT=$(CI_ROUTE=DIRECT CI_MERGE="true" syncmain "$D" push); check "a real-shaped tree with CI_ROUTE=DIRECT does not push" 1 $?
expect_out "could not decide the route"
[ "$(git -C "$D/github.git" rev-parse main)" != "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  the seam bypassed the gated route"; FAIL=$((FAIL+1)); }
}

case_11() {  # 6 s measured 2026-11-07 (66 s on 2026-10-11 before the first split; case_11d split off on 2026-11-07)
echo "7d. A FEATURE IN PROGRESS LANDS NOTHING (feature 133): open tasks refuse both routes; the spec directory alone is the one exception"
D=$(topology fp)
( cd "$D/main/.clones/c" && mkdir -p specs/140-x && printf -- '- [ ] T01 open\n' > specs/140-x/tasks.md && printf -- '**Status**: APPROVED by `spec-fidelity` - round 1 verdict FAITHFUL\n' > specs/140-x/spec.md && echo docs > note.md && git add -A && git commit -qm "feature plus docs" )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "STAYS QUIET: open tasks nobody has started hold nothing (405 T32) -> lands" 0 $?
( cd "$D/main/.clones/c" && echo docs-b > note.md && printf -- '- [ ] T01 open\n- [ ] T02 filed\n' > specs/140-x/tasks.md && git add -A && git commit -qm "the task's work" ); start "$D"
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: the task being worked + an unrelated file -> refused on the DIRECT route" 1 $?
expect_out "IN PROGRESS"
expect_out "note.md"
[ "$(git -C "$D/github.git" rev-parse main)" != "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  a feature in progress landed"; FAIL=$((FAIL+1)); }
}

case_11d() {  # split from case_11 (feature 444 T36, measured 2026-11-07: its nine pushes in a row, 19.2 s, were the suite's long pole)
echo "7d (cont). the spec directory alone, then the pointer, the plan gate and the GATED route"
D=$(topology fq)
( cd "$D/main/.clones/c" && mkdir -p specs/140-x && printf -- '- [ ] T01 open\n' > specs/140-x/tasks.md && printf -- '**Status**: APPROVED by `spec-fidelity` - round 1 verdict FAITHFUL\n' > specs/140-x/spec.md && git add -A && git commit -qm "the claim" ); start "$D"
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "the spec directory ALONE (the number claim) is allowed" 0 $?
expect_out "the claim), allowed"
( cd "$D/main/.clones/c" && echo docs > note.md && git add -A && git commit -qm docs )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "a later docs push from the same clone: the delta no longer touches the spec dir -> the pointer decides" 0 $?
( cd "$D/main/.clones/c" && mkdir -p .specify && echo '{"feature_directory": "specs/140-x"}' > .specify/feature.json && echo more > note.md && git add -A && git commit -qm docs2 )
# feature 451 T254's plan review, round 2: this clone's own started task holds its push whatever the push carries (405 T32 D4 kept)
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: the pointer names a feature with open tasks -> refused even for docs" 1 $?
( cd "$D/main/.clones/c" && printf -- '- [x] T01 done\n' > specs/140-x/tasks.md && printf '# report\n' > specs/140-x/report.md && git add -A && git commit -qm done )
# GUARD_EDIT_OK: feature 243 - a ticked feature now also owes its plan review at the push, so this finished
# feature proves the plan gate is WIRED into the push (refused without the record) before it lands with one.
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: ticked tasks with no plan review -> refused (feature 243)" 1 $?
expect_out "PLAN GATE"
( cd "$D/main/.clones/c" && printf '# plan\n' > specs/140-x/plan.md \
  && printf '{"plan_sha256": "%s", "decisions": [], "verdict": "CLEAR"}\n' "$(sha256sum specs/140-x/plan.md | cut -d' ' -f1)" > specs/140-x/plan-review.json \
  && git add -A && git commit -qm "the plan, reviewed" )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "STAYS QUIET: every task ticked and the plan reviewed -> the docs land" 0 $?
( cd "$D/main/.clones/c" && echo 'def a(): return 9' > pool/x/a.py && printf -- '- [x] T01 done\n- [ ] T02 the GM accepts\n' > specs/140-x/tasks.md && printf '# report\n' > specs/140-x/report.md && git add -A && git commit -qm engine ); stamp_hooks "$D"; start "$D" T02
OUT=$(CI_ROUTE=GATED CI_MERGE="echo SKIP-VERIFIED > $D/main/.clones/c/.git/ci-verdict" syncmain "$D" push); check "IT FIRES on the GATED route too, before ci-merge is even consulted" 1 $?
expect_out "IN PROGRESS"
}

case_11b() {  # split from case_11 (feature 383 amendment 3, plan D27): its 17 pushes in a row were the suite's long pole
# feature 330 (FR-002): ONE state rule with `make speckit-todo` - a feature its status line closes is not in progress,
# though a box is unticked; the same open box under a status that does not close it is still refused
D=$(topology fr)
( cd "$D/main/.clones/c" && mkdir -p specs/140-x && printf -- '- [x] T01 done\n- [ ] T02 the report\n' > specs/140-x/tasks.md && printf '# report\n' > specs/140-x/report.md \
  && printf -- '# Feature Specification: x\n\n**Status**: Done (2026-10-08): landed in abc1234; only the report was left unticked\n\n## Review history\n- spec-fidelity round 1: FAITHFUL\n' > specs/140-x/spec.md \
  && printf '# plan\n' > specs/140-x/plan.md \
  && printf '{"plan_sha256": "%s", "decisions": [], "verdict": "CLEAR"}\n' "$(sha256sum specs/140-x/plan.md | cut -d' ' -f1)" > specs/140-x/plan-review.json \
  && echo docs > note.md && git add -A && git commit -qm "closed by its status line" ); start "$D" T02
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "STAYS QUIET: an open box under a closing status line (Done) -> lands" 0 $?
( cd "$D/main/.clones/c" && printf -- '# Feature Specification: x\n\n**Status**: Implemented, mostly\n' > specs/140-x/spec.md && echo more > note.md && git add -A && git commit -qm "not closed" )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: the same open box under a status that closes nothing -> refused" 1 $?
expect_out "IN PROGRESS"
# plan review round 4: the closing-status exemption must not change how boxes are READ - an indented open task, or a
# ticked task whose indented research box is open, is still in progress under a status that closes nothing
( cd "$D/main/.clones/c" && printf -- '## Phase 1\n  - [ ] T01 indented and open\n  - [ ] T02 indented and open\n' > specs/140-x/tasks.md && echo m3 > note.md && git add -A && git commit -qm indented ); start "$D" T01
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: indented open tasks -> refused" 1 $?
( cd "$D/main/.clones/c" && printf -- '- [x] T01 done\n      - [ ] research pass\n' > specs/140-x/tasks.md && printf '# report\n' > specs/140-x/report.md && echo m4 > note.md && git add -A && git commit -qm research-box )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: a ticked task with an open indented research box -> refused" 1 $?
}

case_11c() {  # split from case_11 (plan D27); its first commit writes every file the checks read, so a fresh topology serves
D=$(topology ft)
# feature 405 T32 (D4; the GM 2026-10-20, no Lands open line): only the task being worked holds a landing - a box nobody has
# started holds nothing, marked or not; the active task holds, a [lands-open] mark on it changing nothing; the GM-review box never
( cd "$D/main/.clones/c" && mkdir -p specs/140-x && printf -- '- [x] T01 done\n- [ ] T99 later batches [lands-open]\n- [ ] T98 not started\n' > specs/140-x/tasks.md && printf '# report\n' > specs/140-x/report.md \
  && printf -- '# Feature Specification: x\n\n**Status**: In progress - batch 2 next\n\n**Owed at**: now\n\n## Review history\n- spec-fidelity round 1: FAITHFUL\n' > specs/140-x/spec.md \
  && printf '# plan\n' > specs/140-x/plan.md \
  && printf '{"plan_sha256": "%s", "decisions": [], "verdict": "CLEAR"}\n' "$(sha256sum specs/140-x/plan.md | cut -d' ' -f1)" > specs/140-x/plan-review.json \
  && echo m5 > note.md && git add -A && git commit -qm unstarted )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "STAYS QUIET: only boxes nobody has started open -> lands" 0 $?
( cd "$D/main/.clones/c" && printf -- '- [ ] T01 open\n- [ ] T99 later batches [lands-open]\n' > specs/140-x/tasks.md && echo m6 > note.md && git add -A && git commit -qm "the task being worked" ); start "$D" T01
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: the active task open -> refused" 1 $?
expect_out "holds: T01 open"
expect_out "make land F=140 T=T01"
case "$OUT" in *"conflict-markers:"*) no_ "the holding rule ran after l7r-gate push-checks (405 T34: cheap questions first)" ;; *) yes_ ;; esac
OUT=$(L7R_LAND_TICKS="T01" CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "STAYS QUIET: make land names the task it ticks -> lands" 0 $?
# feature 451 T101: a landing of another task than the active one is held, unless make land ruled it ready beside it (started, its
# plan section CLEAR, its files its own) and said so in L7R_LAND_READY - the push asks the hold again, so it reads that ruling
( cd "$D/main/.clones/c" && echo m6b > note.md && echo "another task's report line" >> specs/140-x/report.md && git add -A && git commit -qm "another task's landing" )
OUT=$(L7R_LAND_TICKS="T99" CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: a landing of another task than the active one -> refused" 1 $?
expect_out "holds: T01 open"
# 451 T432: the ruling exempts the landed feature's hold alone, the one make land names to the push in SPECIFY_FEATURE
OUT=$(L7R_LAND_TICKS="T99" L7R_LAND_READY="T99" SPECIFY_FEATURE="141-z" CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: a landing ruled ready for another feature exempts none of this one's hold (451 T432) -> refused" 1 $?
OUT=$(L7R_LAND_TICKS="T99" L7R_LAND_READY="T99" SPECIFY_FEATURE="140-x" CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "STAYS QUIET: make land ruled its task ready beside the active one (451 T101) -> lands" 0 $?
( cd "$D/main/.clones/c" && printf -- '- [x] T01 done\n- [ ] T02 being worked [lands-open]\n' > specs/140-x/tasks.md && echo m7 > note.md && git add -A && git commit -qm "a mark on the active task" ); start "$D" T02
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: a [lands-open] mark is text - the active task still holds" 1 $?
( cd "$D/main/.clones/c" && printf -- '- [x] T01 done\n- [x] T02 done\n- [ ] GM review (make gm-reviewed F=140) [lands-open]\n' > specs/140-x/tasks.md && echo m8 > note.md && git add -A && git commit -qm "the GM's box" )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "STAYS QUIET: the GM-review box never holds -> lands" 0 $?
}

case_12() {  # 1 s measured 2026-10-11
echo "8. origins are re-pointed at GitHub once, and said so"
D=$(topology h)
git -C "$D/main/.clones/c" remote set-url origin "$D/main"
OUT=$(syncmain "$D" sync-in); check "sync-in with a stale origin" 0 $?
expect_out "origin of"
[ "$(git -C "$D/main/.clones/c" remote get-url origin)" = "$D/github.git" ] && PASS=$((PASS+1)) || { echo "FAIL  origin not re-pointed"; FAIL=$((FAIL+1)); }
}

case_13() {  # 1 s measured 2026-10-11
echo "8b. the MIRROR's origin is the GM's: never re-pointed, and the mirror still refreshes by URL (2026-10-03)"
D=$(topology h2)
git -C "$D/main" remote set-url origin "ssh://git@example.invalid/gm-own-remote.git"
( cd "$D/seed" && echo more > g && git add -A && git commit -qm upstream && git push -q "$D/github.git" HEAD:main )
OUT=$(syncmain "$D" sync-in); check "sync-in with the GM's SSH origin on the mirror" 0 $?
[ "$(git -C "$D/main" remote get-url origin)" = "ssh://git@example.invalid/gm-own-remote.git" ] && PASS=$((PASS+1)) || { echo "FAIL  the mirror's origin was re-pointed"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  mirror did not fast-forward by URL"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main" rev-parse origin/main)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  the mirror's origin/main was not refreshed"; FAIL=$((FAIL+1)); }
}

case_14() {  # 1 s measured 2026-10-11
echo "9. the build's push line is a compare-and-swap: main moved between fetch and push -> rejected, nothing lands (R3, T036)"
D=$(topology i)
git clone -q "$D/github.git" "$D/build"; git clone -q "$D/github.git" "$D/other"
( cd "$D/other" && echo 2 > g && git add g && git commit -qm "landed in between" && git push -q origin HEAD:main )
( cd "$D/build" && echo 3 > h && git add h && git commit -qm "the merge result" )
OUT=$(cd "$D/build" && { git push origin HEAD:main 2>&1 || echo "main moved; re-run (the push was not a fast-forward - nothing landed)"; }); check "non-fast-forward push refused" 0 $?
expect_out "main moved; re-run"
[ "$(git -C "$D/github.git" log -1 --format=%s main)" = "landed in between" ] && PASS=$((PASS+1)) || { echo "FAIL  something landed over the in-between commit"; FAIL=$((FAIL+1)); }
}

case_15() {  # 9 s measured 2026-10-11
echo "10. the work budget's review at the push: its refusal (an accepted stage grown) or a failure to run stops it; a held budget pushes"
# (the Python call counts' review, `make perf-review`, left the push with feature 449 T223: no rule bore it, so it passed reading nothing;
# W2 and W3 below run the real push path on a Makefile without it, so a call to it would refuse there)
D=$(topology j)
( cd "$D/main/.clones/c" && echo docs > note.md && git add -A && git commit -qm docs )
gh_before=$(git -C "$D/github.git" rev-parse main)
# feature 443 T04 (FR-006): the work budget's ratchet - an accepted stage grown past its figure stops the push
OUT=$(CI_ROUTE=DIRECT CI_WORK_BUDGET_REVIEW="echo 'work-budget-review: REFUSED - web: 2,000 counted operations at 40 households, over its accepted 1,500'; false" syncmain "$D" push); check "IT FIRES: a work-budget-review refusal stops the push" 1 $?
expect_out "make work-budget-review refused (or failed to run)"
expect_out "over its accepted 1,500"
[ "$(git -C "$D/github.git" rev-parse main)" = "$gh_before" ] && PASS=$((PASS+1)) || { echo "FAIL  the push landed though the work budget refused"; FAIL=$((FAIL+1)); }
OUT=$(CI_ROUTE=DIRECT CI_WORK_BUDGET_REVIEW="echo 'work-budget-review: every accepted stage within its figures'" syncmain "$D" push); check "STAYS QUIET: a budget held push" 0 $?
expect_out "every accepted stage within its figures"

# GUARD_EDIT_OK: feature 449 T218 - THE ROLL CACHE IS NO LONGER SEEDED FROM A SIBLING. Feature 167 (GM 2026-08-30) copied a
# sibling's whole `.gencache` into a clone with none, to spare it re-rolling the Python hamlets; their roll store
# (`.gencache/rolls`, 6.0 GB in one clone) has not been written since the Python engine was deleted on 2026-11-07, so the copy
# only duplicated a dead store into every new clone. The vectors pin that sync-in copies nothing and touches a clone's own cache.
echo "== a sibling's roll cache is NOT copied into a clone (449 T218) =="
D=$(topology seed218)
SIB="$D/main/.clones/sib"; git clone -q "$D/github.git" "$SIB"
mkdir -p "$SIB/.gencache/rolls/abc"
echo '{"key":"k","subject":"s","deps":{"functions":[],"files":[]}}' > "$SIB/.gencache/rolls/abc/meta.json"

OUT=$(syncmain "$D" sync-in); check "sync-in succeeds" 0 $?
[ -e "$D/main/.clones/c/.gencache" ] \
  && { echo "FAIL  a sibling's cache was copied into the clone - the dead roll store is seeded again"; FAIL=$((FAIL+1)); } \
  || { echo "  ok    a clone with no cache is left without one"; PASS=$((PASS+1)); }
case "$OUT" in *"seeded the roll cache"*) echo "FAIL  sync-in still says it seeded the roll cache"; FAIL=$((FAIL+1)) ;; *) PASS=$((PASS+1)) ;; esac

# ...and a clone's own cache is left as it is
mkdir -p "$D/main/.clones/c/.gencache"; echo 'MINE' > "$D/main/.clones/c/.gencache/mine.txt"
OUT=$(syncmain "$D" sync-in)
[ "$(cat "$D/main/.clones/c/.gencache/mine.txt" 2>/dev/null)" = MINE ] && [ ! -e "$D/main/.clones/c/.gencache/rolls" ] \
  && { echo "  ok    a clone's own cache is left alone, nothing added"; PASS=$((PASS+1)); } \
  || { echo "FAIL  sync-in changed a clone's own cache"; FAIL=$((FAIL+1)); }
}

case_16() {  # 2 s measured 2026-10-11
echo "11. a clone whose history shares no commit with main's is refused, never merged (feature 301 FR-019)"
D=$(topology unrelated301)
git init -q -b main "$D/rewritten"
( cd "$D/rewritten" && mkdir -p scripts && echo base > f && echo '.clones/' > .gitignore && cp -r "$HERE/../../scripts/." scripts/ && printf '#!/usr/bin/env bash\nexec "%s" "$@"\n' "$(cd "$HERE/../.." && pwd)/scripts/gates/l7r-gate.sh" > scripts/gates/l7r-gate.sh && git add -A \
  && git -c user.email=t@t -c user.name=t commit -qm "the rewritten history" && git push -q -f "$D/github.git" HEAD:main )
before=$(git -C "$D/main/.clones/c" rev-parse HEAD)
OUT=$(syncmain "$D" sync-in); check "sync-in on an unrelated history" 1 $?
expect_out "shares no commit with main"
[ "$(git -C "$D/main/.clones/c" rev-parse HEAD)" = "$before" ] && PASS=$((PASS+1)) || { echo "FAIL  the clone merged the unrelated history"; FAIL=$((FAIL+1)); }
}

case_17() {  # 12 s measured 2026-10-11
echo "12. the prompt hook's path: render-sync detached, one runner at a time, a bounded lock wait (2026-10-02)"
# GUARD_EDIT_OK: new test cases for the hook's --background-render path; nothing existing loosened
D=$(topology bg)
mkdir -p "$D/main"
MARK="$D/rendered"
# THE FAKE RENDER WAITS FOR A RELEASE, NOT A CLOCK (feature 444 T36, measured 2026-11-07: its 6 s sleep and the 15 s polls behind
# it were most of the suite's 89 s): it blocks until $D/release exists, 20 s at most, so a sync-in that waited for it would take 20 s
# and find the mark written; one that did not finds no mark, and the release then lets the render finish at once
REL="$D/release"
printf 'render-sync:\n\t@for i in $$(seq 1 400); do [ -f %s ] && break; sleep 0.05; done; git -C %s rev-parse --short HEAD >> %s\n' "$REL" "$D/main" "$MARK" > "$D/main/Makefile"
( cd "$D/seed" && echo more > g && git add -A && git commit -qm upstream && git push -q "$D/github.git" HEAD:main )
start=$(date +%s)
OUT=$(syncmain "$D" sync-in --background-render); check "sync-in --background-render" 0 $?
# the render is held until the release: no mark means sync-in returned without it, however loaded the box (a clock's bound - 2 s,
# then 5 s against a 6 s render - failed under memory pressure on 2026-10-17 though sync-in did not wait)
[ ! -f "$MARK" ] && PASS=$((PASS+1)) || { echo "FAIL  sync-in waited for the render"; FAIL=$((FAIL+1)); }
expect_out "render-sync started in the background"
[ "$(git -C "$D/main/.clones/c" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  clone did not merge"; FAIL=$((FAIL+1)); }
# a second start while the first runs exits at once and does not render twice
( cd "$D/main/.clones/c" && CLONE_MAIN="$D/main" CLONE_GITHUB="$D/github.git" GITHUB_TOKEN=unused "$SYNC" render-sync-runner >/dev/null 2>&1 ); check "a second runner exits at once" 0 $?
: > "$REL"
for _ in $(seq 1 300); do grep -q '^ok' "$D/main/.clones/.render-sync.status" 2>/dev/null && break; sleep 0.05; done
[ "$(wc -l < "$MARK" 2>/dev/null)" = 1 ] && PASS=$((PASS+1)) || { echo "FAIL  expected one background render, got: $(cat "$MARK" 2>/dev/null)"; FAIL=$((FAIL+1)); }
grep -q '^ok .* at '"$(git -C "$D/main" rev-parse --short HEAD)" "$D/main/.clones/.render-sync.status" && PASS=$((PASS+1)) || { echo "FAIL  status: $(cat "$D/main/.clones/.render-sync.status" 2>/dev/null)"; FAIL=$((FAIL+1)); }
# an earlier failure is reported on the next sync
echo "FAILED 2026-10-02 exit 2 at abc1234" > "$D/main/.clones/.render-sync.status"
OUT=$(syncmain "$D" sync-in --background-render); check "sync-in after a failed render" 0 $?
expect_out "last background render-sync FAILED"
for _ in $(seq 1 300); do grep -q '^ok' "$D/main/.clones/.render-sync.status" 2>/dev/null && break; sleep 0.05; done
# a busy lock: the mirror is skipped this turn, the clone still merges, and the call returns inside the wait
( cd "$D/seed" && echo again > h && git add -A && git commit -qm upstream2 && git push -q "$D/github.git" HEAD:main )
flock "$D/main/.clones/.sync.lock" sleep 6 & HOLDER=$!
lock_held "$D/main/.clones/.sync.lock"
mirror_before=$(git -C "$D/main" rev-parse HEAD)
start=$(date +%s)
OUT=$(cd "$D/main/.clones/c" && SYNC_LOCK_WAIT=1 CLONE_MAIN="$D/main" CLONE_GITHUB="$D/github.git" GITHUB_TOKEN=unused "$SYNC" sync-in --background-render 2>&1); check "sync-in with the lock held" 0 $?
[ $(( $(date +%s) - start )) -lt 5 ] && PASS=$((PASS+1)) || { echo "FAIL  sync-in did not give up on the lock"; FAIL=$((FAIL+1)); }
expect_out "mirror lock stayed busy"
[ "$(git -C "$D/main" rev-parse HEAD)" = "$mirror_before" ] && PASS=$((PASS+1)) || { echo "FAIL  the mirror moved without the lock"; FAIL=$((FAIL+1)); }
[ "$(git -C "$D/main/.clones/c" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  the clone did not merge while the mirror was busy"; FAIL=$((FAIL+1)); }
# GUARD_EDIT_OK: feature 449 T205 - the holder's `sleep` goes with it - killed alone, `flock` left its child holding the lock, and the case below
# waited out the rest of the 6 s for it (4.9 s of this case's 7.4 s, measured 2026-11-19)
pkill -P "$HOLDER" 2>/dev/null; kill "$HOLDER" 2>/dev/null; wait "$HOLDER" 2>/dev/null
# a hand commit in the mirror still stops the hook's path, as it stops the synchronous one
( cd "$D/main" && echo rogue > rogue && git add -A && git commit -qm "committed in main by hand" )
OUT=$(syncmain "$D" sync-in --background-render); check "a mirror commit -> refused on the hook's path" 1 $?
expect_out "cannot fast-forward"

}

case_18() {  # 4 s measured 2026-10-11
echo "11b. SYNC_BACKUP=off (land-tooling's worktree) backs nothing up, even on a refused stop"
D=$(topology bkoff)
in_progress "$D"
OUT=$(CI_ROUTE=DIRECT SYNC_BACKUP=off syncmain "$D" done); check "a refused done keeps its exit code with the backup off" 1 $?
[ -z "$(git -C "$D/github.git" for-each-ref --format='%(refname)' refs/heads/backup/)" ] && yes_ || no_ "a backup branch was pushed with SYNC_BACKUP=off"
}

case_19() {  # 10 s measured 2026-10-11
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
}

case_20() {  # 4 s measured 2026-10-11
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
}

case_21() {  # 10 s measured 2026-10-11
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
# feature 405 T35 (D7): a landing returns once its work is on main; main's renders refresh behind it (T12's push waited 2.5 min)
D=$(topology bw)
# the fake render held until a release, as in case 17 (a 30 s sleep before, its 15 s poll outwaited every run)
printf 'render-sync:\n\t@for i in $$(seq 1 400); do [ -f %s ] && break; sleep 0.05; done; git -C %s rev-parse --short HEAD >> %s\n' "$D/release" "$D/main" "$D/rendered" > "$D/main/Makefile"
( cd "$D/main/.clones/c" && echo docs > note.md && git add -A && git commit -qm docs )
start_s=$(date +%s)
OUT=$(CI_ROUTE=DIRECT syncmain "$D" done); check "done with main's render in the background" 0 $?
# the property is that done RETURNS BEFORE THE RENDER: the render held until the release, so no mark is the proof, however long
# the push took (a 6 s render and a 5 s bound failed under load three times on 2026-10-24; a 30 s render then cost every run)
[ ! -f "$D/rendered" ] && yes_ || no_ "done waited for the render"
expect_out "render-sync started in the background"
[ "$(rref "$D" main)" = "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && yes_ || no_ "the work did not land"
: > "$D/release"
for _ in $(seq 1 300); do grep -q '^ok' "$D/main/.clones/.render-sync.status" 2>/dev/null && break; sleep 0.05; done
}

case_22() {  # 11 s measured 2026-10-11
echo "14. landing deletes the clone's backup; the sweep deletes exactly the backups main contains (SC-006)"
D=$(topology bl)
( cd "$D/main/.clones/c" && echo docs > note.md && git add -A && git commit -qm docs )
OUT=$(CI_ROUTE=DIRECT CI_WORK_BUDGET_REVIEW=false syncmain "$D" done); check "a refused stop (work budget review) backs up" 1 $?
[ -n "$(rref "$D" backup/c)" ] && yes_ || no_ "no backup after the refused stop"
( cd "$D/seed" && git push -q "$D/github.git" HEAD:refs/heads/backup/old && echo ahead > ahead && git add -A && git commit -qm ahead && git push -q "$D/github.git" HEAD:refs/heads/backup/ahead )
OUT=$(CI_ROUTE=DIRECT syncmain "$D" done); check "the stop that lands" 0 $?
expect_out "deleted backup/c on GitHub"
[ -z "$(rref "$D" backup/c)" ] && yes_ || no_ "the landed clone's backup is still there"
[ -z "$(rref "$D" backup/old)" ] && yes_ || no_ "the sweep kept a backup main contains"
[ -n "$(rref "$D" backup/ahead)" ] && yes_ || no_ "the sweep deleted a backup ahead of main"
( cd "$D/main/.clones/c" && echo more > note.md && git add -A && git commit -qm more && git push -q origin HEAD:refs/heads/backup/c )
OUT=$(CI_ROUTE=DIRECT CI_WORK_BUDGET_REVIEW=false syncmain "$D" done); check "a stop with the backup already at HEAD" 1 $?
case "$OUT" in *"backed up HEAD"*) no_ "pushed a backup that was already at HEAD" ;; *) yes_ ;; esac
}

case_23() {  # 2 s measured 2026-10-11
echo "15. a clone with work in flight syncs in a move of the project to the root (feature 329, FR-008, FR-009)"
# GUARD_EDIT_OK: feature 329 - a NEW case. The old path is built by concatenation so the old-layout check (retired by feature 383; it read
# this file) did not count it; the global git config is switched off so the case proves the SCRIPT passes
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
}

case_24() {  # 9 s measured 2026-10-11
echo "16. an open feature with no **Affects** tag, or an unknown one, is refused at the push, a specs/-only DIRECT one included (the GM, 2026-10-10)"
D=$(topology ow)
( cd "$D/main/.clones/c" && mkdir -p specs/400-x .specify && cp "$HERE/../../.specify/affects.json" .specify/ \
  && printf -- '# Feature Specification: x\n\n**Status**: Filed - deferred work\n\n**Approved**: the GM, 2026-10-10, "file the x feature"\n' > specs/400-x/spec.md && git add -A && git commit -qm "filed, no tag" )
# (the approval line, feature 377: spec-lint's check 6 asks it of every feature from 377 on; this case is about tags)
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: a filed spec with no tag -> refused" 1 $?
expect_out "**Affects**: hamlet, magistracy"
( cd "$D/main/.clones/c" && printf -- '\n**Affects**: towns\n' >> specs/400-x/spec.md && git add -A && git commit -qm "a typo" )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: an unknown tag -> refused" 1 $?
expect_out "unknown: towns"
# GUARD_EDIT_OK: fixing a fixture the tier placeholders (380-382) made wrong - a town-only open feature is now refused
# outside the town placeholder, so the known-tags case is owed now; nothing loosened.
( cd "$D/main/.clones/c" && sed -i 's/^\*\*Affects\*\*: towns$/**Affects**: hamlet, town/' specs/400-x/spec.md && git add -A && git commit -qm "tagged" )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "STAYS QUIET: the same spec with known tags -> lands" 0 $?
}

case_25() {  # 8 s measured 2026-10-11
echo "17. a check's pass with no row in the review ledger is refused at the push, with the row to add (feature 371)"
D=$(topology lo)
( cd "$D/main/.clones/c" && mkdir -p dev && printf '# ledger\n\n## Review checks, measured (feature 294 on)\n\n| date | check | subject | verdict | finding | class | author missed? | acted on | wall | tokens |\n|---|---|---|---|---|---|---|---|---|---|\n' > dev/review-ledger.md \
  && echo docs > note.md && git add -A && git commit -qm "a ledger" )
printf '%s\n' '{"date": "2026-10-10", "check": "glyph-check", "subject": "copse", "agent": "a1", "wall": "80 s", "tokens": "244k in (199k cached) / 7.8k out"}' > "$D/main/.clones/c/.git/check-passes.jsonl"
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "IT FIRES: a logged pass with no row -> refused" 1 $?
expect_out "| 2026-10-10 | glyph-check | copse | ? |"
OUT=$(LEDGER_ROWS_OK="a fixture's escape with its reason" CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "the escape with a reason lands" 0 $?
( cd "$D/main/.clones/c" && printf '| 2026-10-10 | glyph-check | copse | PASS | caught nothing | nothing | - | nothing | 80 s | 244k in (199k cached) / 7.8k out |\n' >> dev/review-ledger.md && echo more > note.md && git add -A && git commit -qm "the row" )
OUT=$(CI_ROUTE=DIRECT CI_MERGE="false" syncmain "$D" push); check "STAYS QUIET: the pass with its row lands" 0 $?
}

case_26() {  # 4 s measured 2026-10-11
echo "W. a push from a WORKTREE (land-tooling's route): its .git is a file, and the stamp once failed the step after the push"
D=$(topology wt)
git -C "$D/main/.clones/c" worktree add -q --detach "$D/main/.clones/c-tooling" 2>/dev/null
( cd "$D/main/.clones/c-tooling" && echo tooling > tool.md && git add -A && git commit -qm "tooling alone" )
OUT=$( cd "$D/main/.clones/c-tooling" && CI_ROUTE=DIRECT CI_MERGE="false" CLONE_MAIN="$D/main" CLONE_GITHUB="$D/github.git" GITHUB_TOKEN=unused "$SYNC" push 2>&1 ); check "a worktree's push exits 0 once landed" 0 $?
[ -f "$(git -C "$D/main/.clones/c-tooling" rev-parse --absolute-git-dir)/sync-with-main.stamp" ] && PASS=$((PASS+1)) || { echo "FAIL  no stamp in the worktree's git dir: $OUT"; FAIL=$((FAIL+1)); }
}

case_27() {  # 6 s
echo "W2. THE LANDING COHORT (feature 386): an engine tree with no cohort record is refused on the GATED route, before gated-check; COHORT_OK lands it"
D=$(topology lc)
# a real-shaped tree (a Makefile: the seams are off), whose route is GATED and whose gated-check would pass
( cd "$D/main/.clones/c" && printf 'ci-status:\n\t@echo GATED\nwork-budget-review:\n\t@true\ngated-check:\n\t@true\ncohort-landing:\n\t@true\n' > Makefile \
  && echo 'def a(): return 7' > pool/x/a.py && mkdir -p dev && printf '{"port": {"state": "integrated"}}\n' > dev/switches.json \
  && git add -A && git commit -qm engine ); stamp_hooks "$D"
# (the port switch at integrated: feature 444 FR-023's rust-only, the shipped state while any stage is Python, lands an engine
# delta on the Rust stage gate alone - its case is W3 below)
OUT=$(syncmain "$D" push); check "IT FIRES: no landing cohort -> the gated push is refused" 1 $?
expect_out "make cohort-landing"
[ "$(git -C "$D/github.git" rev-parse main)" != "$(git -C "$D/main/.clones/c" rev-parse HEAD)" ] && PASS=$((PASS+1)) || { echo "FAIL  a gated push with no landing cohort landed"; FAIL=$((FAIL+1)); }
OUT=$(COHORT_OK="a fixture with nothing rolled" syncmain "$D" push); check "COHORT_OK with a reason lands it" 0 $?
}

case_27b() {  # 6 s
echo "W3. THE PORT SWITCH (feature 444 FR-023): at rust-only an engine tree with no landing cohort lands on the Rust stage gate alone"
D=$(topology lr)
( cd "$D/main/.clones/c" && printf 'ci-status:\n\t@echo GATED\nwork-budget-review:\n\t@true\ngated-check:\n\t@true\ncohort-landing:\n\t@true\n' > Makefile \
  && echo 'def a(): return 7' > pool/x/a.py && mkdir -p dev && printf '{"port": {"state": "rust-only"}}\n' > dev/switches.json \
  && git add -A && git commit -qm engine ); stamp_hooks "$D"
OUT=$(syncmain "$D" push); check "STAYS QUIET: rust-only, no landing cohort -> the gated push lands" 0 $?
}

case_28() {  # 3 s
echo "X. sync-in with the mirror lock held: no lock taken when the mirror is at the tip; the bounded wait when main moved (feature 442)"
D=$(topology bh)
mkdir -p "$D/main/.clones"; flock "$D/main/.clones/.sync.lock" sleep 20 & holder=$!; lock_held "$D/main/.clones/.sync.lock"
start=$(date +%s); OUT=$(SYNC_LOCK_WAIT=15 syncmain "$D" sync-in); rc=$?; took=$(( $(date +%s) - start ))
check "sync-in, the mirror at the tip, the lock held" 0 $rc
[ "$took" -lt 5 ] && PASS=$((PASS+1)) || { echo "FAIL  sync-in waited ${took}s for a lock it did not need (the mirror at the tip)"; FAIL=$((FAIL+1)); }
case "$OUT" in *"mirror lock stayed busy"*) echo "FAIL  sync-in asked for the lock with the mirror at the tip"; FAIL=$((FAIL+1)) ;; *) PASS=$((PASS+1)) ;; esac
( cd "$D/seed" && echo more > g && git add -A && git commit -qm upstream && git push -q "$D/github.git" HEAD:main )
start=$(date +%s); OUT=$(SYNC_LOCK_WAIT=1 syncmain "$D" sync-in); rc=$?; took=$(( $(date +%s) - start ))
pkill -P "$holder" 2>/dev/null; kill "$holder" 2>/dev/null; wait "$holder" 2>/dev/null  # T205: and its `sleep 20`, which outlived the case
check "sync-in, main moved, the lock held" 0 $rc
[ "$took" -lt 10 ] && PASS=$((PASS+1)) || { echo "FAIL  sync-in waited ${took}s behind a held lock (bounded at 1 s)"; FAIL=$((FAIL+1)); }
expect_out "mirror lock stayed busy"
[ "$(git -C "$D/main/.clones/c" rev-parse HEAD)" = "$(git -C "$D/github.git" rev-parse main)" ] && PASS=$((PASS+1)) || { echo "FAIL  the clone did not merge GitHub main past a busy mirror"; FAIL=$((FAIL+1)); }
}

case_29() {  # 1 s
echo "Y. render-sync runs the Rust only: every map, then the pool index and the record site, a failing map stopping neither (449 T222)"
# the REAL Makefile's render-sync, in a throwaway repository whose gate is a stub: it writes each command it was handed, one a line,
# and fails `pool map --all` when MAP_FAILS is set (as the driver does when one map's engine refuses it, having drawn the others).
# Red on the recipe before T222: render-maps (since removed) was a prerequisite, so a failed map stopped make before the record site was looked at.
local R=$T/render-sync; mkdir -p "$R/scripts/gates" "$R/dev"; cp "$HERE/../../Makefile" "$R/Makefile"; echo '{}' > "$R/dev/switches.json"
cat > "$R/scripts/gates/l7r-gate.sh" <<'STUB'
#!/usr/bin/env bash
case "${1:-} ${2:-}" in "log "*|"switches "*) exit 0 ;; esac
echo "$*" >> "$(git rev-parse --show-toplevel)/.calls"
case "$*" in
  "pool map --all") echo "CACHED       pool/x/a"; [ -z "${MAP_FAILS:-}" ] || { echo "make map: pool/x/b: its engine refused it (exit 1)" >&2; exit 1; } ;;
  "pool index") echo "pool index: pool/index.html written (2 maps)" ;;
  "record site-stale"*) echo fresh ;;
esac
STUB
chmod +x "$R/scripts/gates/l7r-gate.sh"; git -C "$R" init -q
local want; want=$(printf 'pool map --all\npool index\nrecord site-stale --root %s' "$R")
OUT=$(cd "$R" && MAP_FAILS=1 make --no-print-directory render-sync 2>&1); local rc=$?
[ "$rc" -ne 0 ] && yes_ || no_ "a failed map: render-sync exited 0, so the runner's status would say ok"
[ "$(cat "$R/.calls" 2>/dev/null)" = "$want" ] && yes_ || no_ "a failed map: the index and the site were not brought up to date after it - the stub was handed: $(cat "$R/.calls" 2>/dev/null | paste -sd '|')"
expect_out "pool/x/b: its engine refused it"
expect_out "render-sync: FAILED"
rm -f "$R/.calls"
OUT=$(cd "$R" && make --no-print-directory render-sync 2>&1); check "every map drawn: render-sync exits 0" 0 $?
[ "$(cat "$R/.calls" 2>/dev/null)" = "$want" ] && yes_ || no_ "render-sync did not run the driver, the index and the site, in that order: $(cat "$R/.calls" 2>/dev/null | paste -sd '|')"
expect_out "render-sync: the record's site fresh (research/site/index.html)"
# the main-tree guard: a tree holding .clones/ is main, refused without the GM's override, which sync-with-main.sh sets
rm -f "$R/.calls"; mkdir -p "$R/.clones"
OUT=$(cd "$R" && make --no-print-directory render-sync 2>&1); local rc2=$?
[ "$rc2" -ne 0 ] && [ ! -e "$R/.calls" ] && yes_ || no_ "render-sync ran in a main tree without DIAGRAM_ALLOW_MAIN=1 (rc=$rc2)"
OUT=$(cd "$R" && DIAGRAM_ALLOW_MAIN=1 make --no-print-directory render-sync 2>&1); check "main with DIAGRAM_ALLOW_MAIN=1: render-sync runs" 0 $?
# the tree rendered is the one it runs in: render_cache's ARGS are taken where they name it (a clone's sync script not yet merged past
# T222 still passes them), and refused naming that where they name another tree or anything else
OUT=$(cd "$R" && DIAGRAM_ALLOW_MAIN=1 make --no-print-directory render-sync ARGS="--skill-dir $R --main-repo $R/." 2>&1); check "render-sync ARGS naming its own tree runs" 0 $?
OUT=$(cd "$R" && DIAGRAM_ALLOW_MAIN=1 make --no-print-directory render-sync ARGS="--skill-dir $R --main-repo /elsewhere" 2>&1); check "render-sync ARGS naming another tree refused" 2 $?
expect_out "renders the tree it runs in"
OUT=$(cd "$R" && DIAGRAM_ALLOW_MAIN=1 make --no-print-directory render-sync ARGS="wip/x.svg" 2>&1); check "render-sync ARGS of anything else refused" 2 $?
expect_out "which it does not take"
}

case_30() {  # 1 s
echo "Z. a render-sync that fails is FAILED in the runner's status, never ok (449 T222)"
# found by T222: the runner calls `render_sync || rc=$?`, and bash ignores `set -e` inside a `||` context, so the function went on past a
# failed `make render-sync` to the dirty check and returned its 0 - the status read ok over a failed render, and the next sync-in
# warned of nothing
D=$(topology rf)
printf 'render-sync:\n\t@echo "make map: pool/x/b: its engine refused it (exit 1)" >&2; exit 1\n' > "$D/main/Makefile"
OUT=$(cd "$D/main/.clones/c" && CLONE_MAIN="$D/main" CLONE_GITHUB="$D/github.git" GITHUB_TOKEN=unused "$SYNC" render-sync 2>&1); local rc=$?
[ "$rc" -ne 0 ] && yes_ || no_ "render-sync exited 0 over a failed make render-sync"
( cd "$D/main/.clones/c" && CLONE_MAIN="$D/main" CLONE_GITHUB="$D/github.git" GITHUB_TOKEN=unused "$SYNC" render-sync-runner >/dev/null 2>&1 )
grep -q '^FAILED .* exit [1-9]' "$D/main/.clones/.render-sync.status" 2>/dev/null && yes_ || no_ "the runner's status after a failed render: $(cat "$D/main/.clones/.render-sync.status" 2>/dev/null)"
}

case_31() {  # 2 s
echo "Z2. sync-in defines the plan-review.json merge driver, and a pick of another task's verdict merges clean (451 T256)"
# red first (2026-11-25): with no driver, git's text merge left the record unmerged with 3 conflict hunks on the same pick
D=$(topology mr)
OUT=$(syncmain "$D" sync-in); check "sync-in" 0 $?
expect_out "set the plan-review.json merge driver"
OUT=$(syncmain "$D" sync-in)
case "$OUT" in *"merge driver"*) no_ "the driver set again on a second sync-in" ;; *) yes_ ;; esac
local c=$D/main/.clones/c
add() { # $1 = task: its verdict, its block and its row, as record_task's CLEAR path writes them
  jq --indent 1 --arg t "$1" '.tasks[$t]={"section_sha256":"s","reviewed":"2026-11-26","verdict":"CLEAR"} | .blocks["### "+$t]={"sha256":"b","verdict":"CLEAR","reviewed":"2026-11-26"} | .block_reviews += [{"reviewed":"2026-11-26","blocks":["### "+$t],"verdict":"CLEAR"}]' \
    "$c/specs/451-x/plan-review.json" > "$c/j" && mv "$c/j" "$c/specs/451-x/plan-review.json"
}
mkdir -p "$c/specs/451-x" && printf '{\n "feature": "451-x",\n "blocks": {},\n "block_reviews": [],\n "tasks": {}\n}\n' > "$c/specs/451-x/plan-review.json"
echo 'specs/*/plan-review.json merge=plan-review' > "$c/.gitattributes"
git -C "$c" add -A && git -C "$c" commit -qm record
git -C "$c" checkout -qb other && add T02 && git -C "$c" commit -qam T02 && git -C "$c" checkout -q main
add T01 && git -C "$c" commit -qam T01
OUT=$(cd "$c" && git cherry-pick other 2>&1); check "the pick merges clean" 0 $?
[ "$(jq -r '.tasks|keys|join(",")' "$c/specs/451-x/plan-review.json")" = "T01,T02" ] && yes_ || no_ "both tasks' verdicts kept: $(cat "$c/specs/451-x/plan-review.json")"
[ "$(jq '.block_reviews|length' "$c/specs/451-x/plan-review.json")" = 2 ] && yes_ || no_ "both rows kept"
}

case_32() {  # 2 s
echo "Z3. the push refuses an unfinished carry-over with the command that finishes it (451 T292)"
# red first (2026-11-26): without the check a merge standing with nothing left to stage (MERGE_HEAD, a clean status) was pushed,
# its merge never concluded; a stopped cherry-pick met only "uncommitted changes - commit first", which names no command
D=$(topology uf)
local c=$D/main/.clones/c
git -C "$c" checkout -qb side && echo side > "$c/s" && git -C "$c" add -A && git -C "$c" commit -qm side && git -C "$c" checkout -q main
echo ours > "$c/o" && git -C "$c" add -A && git -C "$c" commit -qm ours
git -C "$c" merge -q -s ours --no-commit side
[ -f "$c/.git/MERGE_HEAD" ] && [ -z "$(git -C "$c" status --porcelain)" ] && yes_ || no_ "the fixture: a merge standing, the status clean"
OUT=$(syncmain "$D" push); check "a merge in progress is refused" 1 $?
expect_out "unfinished: a merge is in progress in"
expect_out "-c core.editor=true merge --continue"
git -C "$c" -c core.editor=true merge --continue >/dev/null 2>&1
# T270's state: a cherry-pick stopped on a conflict, the code staged
git -C "$c" checkout -qb builder HEAD~1 2>/dev/null && echo theirs > "$c/f" && echo code > "$c/code" && git -C "$c" add -A && git -C "$c" commit -qm builder && git -C "$c" checkout -q main
echo mine > "$c/f" && git -C "$c" commit -qam mine
git -C "$c" cherry-pick builder >/dev/null 2>&1
OUT=$(syncmain "$D" push); check "a stopped cherry-pick is refused" 1 $?
expect_out "unfinished: a cherry-pick is in progress in"
expect_out "resolve 1 unmerged path(s) (f)"
expect_out "-c core.editor=true cherry-pick --continue"
case "$OUT" in *"uncommitted changes - commit first"*) no_ "the refusal with the command comes first" ;; *) yes_ ;; esac
}

# GUARD_EDIT_OK: feature 375 amendment 4 (FR-022) - THE CASES RUN IN PARALLEL PARTS. This suite is held to the whole scripts
# tree (feature 172: its push path reaches scripts at run time), so every script change re-runs it, and at 202-230 s it was
# the long pole of a parallel hooks-test (specs/375-enforced-wave-process/research.md R3). Each case builds its own fixture
# (checked when the cases became functions: no case reads a variable another sets), so they are dealt into SYNC_PARTS parts,
# longest first onto the lightest part (the times are the measured ones beside each case; a new case without one counts
# 10 s), each part a subshell with its own $T, HOME and guard log. Every check still runs and is counted; a part that ends
# before a case reports fails the suite and names the case. SYNC_PARTS=1 runs them one after another, as before.
CASES=(case_01 case_02 case_03 case_04 case_05 case_06 case_07 case_08 case_09 case_10 case_11 case_11b case_11c case_11d case_12 case_13 case_14 case_15 case_16 case_17 case_18 case_19 case_20 case_21 case_22 case_23 case_24 case_25 case_26 case_27 case_27b case_28 case_29 case_30 case_31 case_32)
declare -A WEIGHT=([case_01]=1 [case_02]=1 [case_03]=1 [case_04]=1 [case_05]=1 [case_06]=1 [case_07]=1 [case_08]=1 [case_09]=1 [case_10]=1 [case_11]=1 [case_11b]=1 [case_11c]=2 [case_11d]=3 [case_12]=1 [case_13]=1 [case_14]=1 [case_15]=2 [case_16]=1 [case_17]=2 [case_18]=1 [case_19]=1 [case_20]=1 [case_21]=2 [case_22]=1 [case_23]=1 [case_24]=1 [case_25]=1 [case_26]=1 [case_27]=1 [case_27b]=1 [case_28]=1 [case_29]=1 [case_30]=1 [case_31]=2 [case_32]=2)  # seconds, each case alone less the suite's start and template (about 0.85 s), measured 2026-11-19 (feature 449 T205; case_17 6.6 s before its lock holder was killed whole)
# SYNC_CASES="case_11 case_17" runs only those cases - to time one case where it lives (feature 383 amendment 3, plan D27); the
# runner itself is tests/hooks/parts.sh since amendment 4 (plan D28), shared by every split suite
[ -n "${SYNC_CASES:-}" ] && PARTS_CASES=$SYNC_CASES
SYNC_PARTS=${SYNC_PARTS:-8}  # 8, not 4: with the measured weights and case_11 split, 36.2 -> 17.9 s (6 parts: 24.3 s), 2026-10-17 at load 8
# the template every topology copies (T106), in the suite's own $T: each part reassigns T, so the path is fixed here, before them
TEMPLATE=$T/.template; template_build "$TEMPLATE"
# shellcheck source=/dev/null
source "$HERE/parts.sh"
run_parts "$SYNC_PARTS"

echo "-----"
if [ "$FAIL" -eq 0 ]; then echo "all sync-with-main tests passed ($PASS checks)"; exit 0; else echo "SOME TESTS FAILED ($FAIL)"; exit 1; fi
