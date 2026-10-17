#!/bin/bash
# land-tooling.sh FILE... - land a clone's TOOLING on main by itself, mid-feature (feature 379 amendment 1, the GM 2026-10-10).
# GUARD_EDIT_OK: feature 379 amendment 1 - a new landing route for tooling alone; the open-task refusal is not touched.
#
# THE FAILURE IT CLOSES. A feature with open tasks lands nothing but its spec (feature 133), so a guard fix a session made
# mid-feature waited in its clone until the whole feature closed - hours - while hooks run from the mirror: every other
# session hit the same misfire, and fixes were copied by hand between clones (2026-10-10: the backlog's "accept" deadlock,
# 374's modal-research mapping ported into the research clone).
#
# HOW (plan D8, D9). Never a flag on the open-task refusal - "there is no flag" (GM 2026-08-25). Instead a NEW commit on top
# of the latest main holding only FILES' changes since the clone's merge base with main, built in a detached worktree at
# .clones/<clone>-tooling and landed by sync-with-main.sh run from there, so every push check runs unchanged. The clone's
# own history is untouched; its next merge of main meets identical hunks. FILES is required: a file lands whole, and
# mid-feature a doc or Makefile edit may describe work that has not landed.
#
# Test seams (tests/hooks/test-land-tooling.sh): LAND_TOOLING_CHECKS, LAND_TOOLING_TEST (how one landed test file runs) and
# LAND_TOOLING_PUSH replace the checks, the landed tests' runner and the push.
set -uo pipefail

die() { printf 'land-tooling: %s\n' "$*" >&2; exit "${2:-1}"; }
# FR-005: the proposal's scripts/, tests/ and agent instruction files, plus the wiring a scripts/ fix needs to take effect.
# GUARD_EDIT_OK: fixing a route that refused correct work - the review ledger too: the push checks every logged check pass
# against the LEDGER it lands, and the pass log is the clone's, so a session that had run checks could never land tooling
# without its rows (368, 2026-10-11: 168 passes owed against main's ledger). The ledger is append-only and merges by union.
tooling() { case "$1" in scripts/*|tests/*|.claude/agents/*|.claude/skills/*|.claude/workflows/*|CLAUDE.md|*/CLAUDE.md|Makefile|.claude/settings.json|docs/make-targets.html|dev/review-ledger.md) return 0 ;; *) return 1 ;; esac; }

ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || die "not inside a git checkout"
[ "$(basename "$(dirname "$ROOT")")" = ".clones" ] || die "$ROOT is not a session clone under .clones/"
# GUARD_EDIT_OK: feature 383 amendment 2, FR-017 (the GM 2026-10-13: "figure out where the rest of the 100 or so seconds goes")
# - EACH STEP IS TIMED: its seconds go to the log and, one JSON line per landing, to <git dir>/land-tooling-steps.jsonl, so
# where a landing's time went is read, never guessed. Nothing is printed to the terminal.
log="$ROOT/.git/land-tooling.log"
: > "$log"
steps_t=${EPOCHREALTIME/,/.}; steps_json=""
step() { # <name>: the time since the last step, under that name
  local now=${EPOCHREALTIME/,/.}
  local s; s=$(awk -v a="$steps_t" -v b="$now" 'BEGIN { printf "%.2f", b - a }')
  printf 'land-tooling: step %s %s s\n' "$1" "$s" >> "$log"
  steps_json="$steps_json${steps_json:+, }\"$1\": $s"; steps_t=$now
}
steps_done() { # <outcome>
  printf '{"at": "%s", "outcome": "%s", "load": "%s", "steps": {%s}}\n' "$(date -u +%FT%TZ)" "$1" "$(cut -d' ' -f1 /proc/loadavg 2>/dev/null)" "$steps_json" >> "$ROOT/.git/land-tooling-steps.jsonl"
}
git -C "$ROOT" fetch -q origin 2>/dev/null || true
base=$(git -C "$ROOT" merge-base HEAD origin/main) || die "no merge base with origin/main"

if [ "$#" -eq 0 ]; then
  eligible=$(git -C "$ROOT" diff --name-only "$base" HEAD | while read -r f; do tooling "$f" && printf '%s ' "$f"; done)
  [ -n "$eligible" ] || die "this clone's commits change no tooling path - nothing to land" 2
  printf 'land-tooling: name the files to land - each lands WHOLE, so leave out any that describe work not yet landed.\n' >&2
  printf 'The tooling this clone changed:\n  make land-tooling FILES="%s"\n' "${eligible% }" >&2
  exit 2
fi
# GUARD_EDIT_OK: feature 383, the GM 2026-10-13 ("those are on disk, so it definitely can see them, right?") - THE LEDGER COMES
# WITH ITS PASSES, unasked: a session that named only its scripts had the push refuse its own review passes against main's
# ledger, and then escaped it with LEDGER_ROWS_OK. When the clone's commits change the ledger, it lands beside FILES.
if ! printf '%s\n' "$@" | grep -qx 'dev/review-ledger.md' && ! git -C "$ROOT" diff --quiet "$base" HEAD -- dev/review-ledger.md 2>/dev/null; then
  set -- "$@" dev/review-ledger.md
  printf 'land-tooling: dev/review-ledger.md lands too - the push answers this clone'"'"'s check passes from it\n' >&2
fi
for f in "$@"; do
  tooling "$f" || die "$f is not tooling (scripts/, tests/, .claude/agents/, .claude/skills/, .claude/workflows/, a CLAUDE.md, the Makefile, .claude/settings.json, docs/make-targets.html) - it lands with its feature"
done
git -C "$ROOT" diff --quiet HEAD -- "$@" || die "uncommitted changes in FILES - commit them first; only committed work lands"
patch=$(mktemp)
git -C "$ROOT" diff --binary "$base" HEAD -- "$@" > "$patch"
[ -s "$patch" ] || { rm -f "$patch"; die "FILES carry no change since main - nothing to land"; }

WT="$(dirname "$ROOT")/$(basename "$ROOT")-tooling"
[ -e "$WT" ] && die "$WT exists (a run that did not finish?) - remove it: git -C $ROOT worktree remove --force $WT"
step prepare
git -C "$ROOT" worktree add -q --detach "$WT" origin/main || die "cannot add the worktree at $WT"
step worktree
cleanup() { git -C "$ROOT" worktree remove --force "$WT" 2>/dev/null; rm -f "$patch"; }
trap cleanup EXIT

git -C "$WT" apply --index "$patch" 2>&1 | sed 's/^/  /' >&2
[ "${PIPESTATUS[0]}" -eq 0 ] || die "FILES do not apply cleanly onto the latest main - merge main into the clone (sync-in), then run this again"
case " $* " in *" Makefile "*) ( cd "$WT" && make -s docs >/dev/null 2>&1 ) && git -C "$WT" add docs/make-targets.html 2>/dev/null ;; esac
subjects=$(git -C "$ROOT" log --format='- %s' "$base"..HEAD -- "$@" | head -20)
msg=$(printf 'Tooling from %s, landed alone mid-feature (make land-tooling, feature 379)\n\n%s\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n' "$(basename "$ROOT")" "$subjects")
git -C "$WT" commit -q -m "$msg" || die "nothing to commit in the worktree"
step patch
# every test it lands runs here: one needing work not yet landed fails in the worktree, never on main (FR-005)
# GUARD_EDIT_OK: feature 383 amendment 2, plan D21 + D22 (the GM 2026-10-13: "see what can be done there") - TWO CHECKS, EACH
# TIMED, SIDE BY SIDE, EACH TEST ONCE. The guard suites and the tooling tests share no write (the pass store is the tooling
# run's, the suites' stamps theirs), so they run at the same time; and hooks-test leaves tests/tooling/ to the tooling run,
# which reuses the clone's passes - 57 files ran twice before, once without reuse (research R7). Both must pass; each one's
# output and seconds land in the landing's log. LAND_TOOLING_CHECKS, the suite's seam, stands for both;
# LAND_TOOLING_GUARDS and LAND_TOOLING_TOOLING for one each.
guards=${LAND_TOOLING_GUARDS:-${LAND_TOOLING_CHECKS:-make hooks-test HOOKS_PYTEST_SKIP=tests/tooling/}}
tooling_tests=${LAND_TOOLING_TOOLING:-${LAND_TOOLING_CHECKS:-make test-file FILE=tests/tooling}}
run_test=${LAND_TOOLING_TEST:-make test-file FILE=}
for f in "$@"; do case "$f" in tests/tooling/*|tests/hooks/*) ;; tests/*test_*.py) [ -f "$WT/$f" ] && tooling_tests="$tooling_tests && $run_test\"$f\"" ;; esac; done
# GUARD_EDIT_OK: feature 374 batch 4 - THE CHECKS RUN WITHOUT THE CALLER'S ESCAPES: a LEDGER_ROWS_OK meant for the push reached
# the hook suites, where it waived the very refusals they test, and ten sync-with-main cases failed (twice, 2026-10-12). The
# push below keeps them.
unset_escapes=$(env | sed -n 's/^\([A-Z][A-Z_]*_OK\)=.*/-u \1/p' | tr '\n' ' ')
# GUARD_EDIT_OK: feature 383 amendment 1 (the GM 2026-10-13: "skip suites the clone already passed") - the tooling tests reuse
# each test file's pass the clone recorded on identical inputs (tests/tooling/_test_deps.py); the guard suites already do
check() { # <step name> <command>: run in the worktree without the escapes, to <log>.<name>, its exit and seconds beside it
  local t0=${EPOCHREALTIME/,/.} rc
  # shellcheck disable=SC2086 # one word per `-u NAME`
  ( cd "$WT" && env $unset_escapes L7R_TEST_DEPS=reuse bash -c "$2" ) > "$log.$1" 2>&1; rc=$?
  awk -v a="$t0" -v b="${EPOCHREALTIME/,/.}" 'BEGIN { printf "%.2f", b - a }' > "$log.$1.s"
  echo "$rc" > "$log.$1.rc"
}
check guard-suites "$guards" & check tooling-tests "$tooling_tests" & wait
failed=""
for j in guard-suites tooling-tests; do
  s=$(cat "$log.$j.s"); rc=$(cat "$log.$j.rc")
  { printf -- '--- %s: exit %s\n' "$j" "$rc"; cat "$log.$j"; printf 'land-tooling: step %s %s s\n' "$j" "$s"; } >> "$log"
  steps_json="$steps_json${steps_json:+, }\"$j\": $s"
  [ "$rc" = 0 ] || failed="$failed $j"
  rm -f "$log.$j" "$log.$j.s" "$log.$j.rc"
done
step checks
if [ -n "$failed" ]; then
  steps_done "checks-failed:${failed# }"
  tail -25 "$log" >&2
  die "the checks failed in the worktree (${failed# }; full log: $log) - fix in the clone, commit, run this again"
fi
push=${LAND_TOOLING_PUSH:-scripts/sync-with-main.sh done}
# SYNC_BACKUP=off: the worktree is not a clone - its work is the clone's own commits, backed up at the clone's own stop. Backed
# up under the fixed name backup/<clone>-tooling, a refused landing left a tip no later landing contained, and every one
# after it warned "HEAD is NOT backed up" (2026-10-11)
( cd "$WT" && SYNC_BACKUP=off bash -c "$push" ) >> "$log" 2>&1
rc=$?
step push; steps_done "push-exit-$rc"
# a refusal's reason is above the push's last lines: six lines showed the backup notice and hid the ledger's refusal
if [ "$rc" -eq 0 ] || [ "$rc" -eq 3 ]; then tail -6 "$log"; else tail -25 "$log" >&2; fi
[ "$rc" -eq 0 ] || [ "$rc" -eq 3 ] || die "the push failed (exit $rc; log: $log) - nothing landed"
printf 'land-tooling: landed %s on main. The clone keeps its own commits; its next sync-in merges them cleanly.\n' "$*"
