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
# FR-005: the proposal's scripts/, tests/ and agent instruction files, plus the wiring a scripts/ fix needs to take effect
tooling() { case "$1" in scripts/*|tests/*|.claude/agents/*|.claude/skills/*|CLAUDE.md|*/CLAUDE.md|Makefile|.claude/settings.json|docs/make-targets.html) return 0 ;; *) return 1 ;; esac; }

ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || die "not inside a git checkout"
[ "$(basename "$(dirname "$ROOT")")" = ".clones" ] || die "$ROOT is not a session clone under .clones/"
git -C "$ROOT" fetch -q origin 2>/dev/null || true
base=$(git -C "$ROOT" merge-base HEAD origin/main) || die "no merge base with origin/main"

if [ "$#" -eq 0 ]; then
  eligible=$(git -C "$ROOT" diff --name-only "$base" HEAD | while read -r f; do tooling "$f" && printf '%s ' "$f"; done)
  [ -n "$eligible" ] || die "this clone's commits change no tooling path - nothing to land" 2
  printf 'land-tooling: name the files to land - each lands WHOLE, so leave out any that describe work not yet landed.\n' >&2
  printf 'The tooling this clone changed:\n  make land-tooling FILES="%s"\n' "${eligible% }" >&2
  exit 2
fi
for f in "$@"; do
  tooling "$f" || die "$f is not tooling (scripts/, tests/, .claude/agents/, .claude/skills/, a CLAUDE.md, the Makefile, .claude/settings.json, docs/make-targets.html) - it lands with its feature"
done
git -C "$ROOT" diff --quiet HEAD -- "$@" || die "uncommitted changes in FILES - commit them first; only committed work lands"
patch=$(mktemp)
git -C "$ROOT" diff --binary "$base" HEAD -- "$@" > "$patch"
[ -s "$patch" ] || { rm -f "$patch"; die "FILES carry no change since main - nothing to land"; }

WT="$(dirname "$ROOT")/$(basename "$ROOT")-tooling"
[ -e "$WT" ] && die "$WT exists (a run that did not finish?) - remove it: git -C $ROOT worktree remove --force $WT"
git -C "$ROOT" worktree add -q --detach "$WT" origin/main || die "cannot add the worktree at $WT"
cleanup() { git -C "$ROOT" worktree remove --force "$WT" 2>/dev/null; rm -f "$patch"; }
trap cleanup EXIT

git -C "$WT" apply --index "$patch" 2>&1 | sed 's/^/  /' >&2
[ "${PIPESTATUS[0]}" -eq 0 ] || die "FILES do not apply cleanly onto the latest main - merge main into the clone (sync-in), then run this again"
case " $* " in *" Makefile "*) ( cd "$WT" && make -s docs >/dev/null 2>&1 ) && git -C "$WT" add docs/make-targets.html 2>/dev/null ;; esac
subjects=$(git -C "$ROOT" log --format='- %s' "$base"..HEAD -- "$@" | head -20)
msg=$(printf 'Tooling from %s, landed alone mid-feature (make land-tooling, feature 379)\n\n%s\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n' "$(basename "$ROOT")" "$subjects")
git -C "$WT" commit -q -m "$msg" || die "nothing to commit in the worktree"

log="$ROOT/.git/land-tooling.log"
# every test it lands runs here: one needing work not yet landed fails in the worktree, never on main (FR-005)
checks=${LAND_TOOLING_CHECKS:-make hooks-test && make test-file FILE=tests/tooling}
run_test=${LAND_TOOLING_TEST:-make test-file FILE=}
for f in "$@"; do case "$f" in tests/tooling/*|tests/hooks/*) ;; tests/*test_*.py) [ -f "$WT/$f" ] && checks="$checks && $run_test\"$f\"" ;; esac; done
if ! ( cd "$WT" && bash -c "$checks" ) > "$log" 2>&1; then
  tail -25 "$log" >&2
  die "the checks failed in the worktree (full log: $log) - fix in the clone, commit, run this again"
fi
push=${LAND_TOOLING_PUSH:-scripts/sync-with-main.sh done}
( cd "$WT" && bash -c "$push" ) >> "$log" 2>&1
rc=$?
tail -6 "$log"
[ "$rc" -eq 0 ] || [ "$rc" -eq 3 ] || die "the push failed (exit $rc; log: $log) - nothing landed"
printf 'land-tooling: landed %s on main. The clone keeps its own commits; its next sync-in merges them cleanly.\n' "$*"
