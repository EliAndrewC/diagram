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
# Test seams (tests/hooks/test-land-tooling.sh): LAND_TOOLING_CHECKS, LAND_TOOLING_LEDGER, LAND_TOOLING_LINT, LAND_TOOLING_TEST (how one landed test file runs) and
# LAND_TOOLING_PUSH replace the checks, the landed tests' runner and the push.
set -uo pipefail

die() { LT_OUTCOME="failed: ${1:0:160}"; printf 'land-tooling: %s\n' "$*" >&2; exit "${2:-1}"; }
# GUARD_EDIT_OK: feature 385 T79 (plan D98; the round arbiter on hour:385-approach-checklist@25) - EACH RUN LEAVES ITS RECORD, from
# the exit trap so a run that dies early leaves one too: `make tick` refuses a NOTE saying "landed" while the task's last run failed
# or a file it named still differs from main (T72 was ticked "landed" at 00:49 over a failed landing).
LT_OUTCOME="died"; LT_FILES="$*"
lt_record() {
  local gd task
  gd=$(git -C "${ROOT:-.}" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || return 0
  task=$(tail -1 "$gd/task-starts.jsonl" 2>/dev/null | python3 -c 'import json,sys; r=json.loads(sys.stdin.read() or "{}"); print(r.get("feature","") + " " + r.get("task",""))' 2>/dev/null)
  python3 -c 'import json,sys,datetime; f,t=sys.argv[2].split(" ",1) if " " in sys.argv[2] else ("",""); print(json.dumps({"feature": f, "task": t, "files": sys.argv[3].split(), "outcome": sys.argv[4], "log": sys.argv[5], "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}))' \
    "$gd" "$task" "$LT_FILES" "$LT_OUTCOME" "$gd/land-tooling.log" >> "$gd/land-tooling.jsonl" 2>/dev/null || :
}
trap lt_record EXIT
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
# GUARD_EDIT_OK: feature 385 T91 (plan D112; the round arbiter on hour:385-approach-checklist@27) - THE LINT FIRST, IN THE CLONE: T85
# was landed three times, two of them lint slips seen minutes later in a backgrounded landing's log. The same ruff the worktree
# applies, on the .py files given, before the fetch, the merge and the worktree - so every caller learns it in seconds.
first_pys=""; for f in "$@"; do case "$f" in *.py) [ -f "$ROOT/$f" ] && first_pys="$first_pys $f" ;; esac; done
if [ -n "$first_pys" ] && [ -z "${LAND_TOOLING_LINT:-}" ] && ( cd "$ROOT" && python3 -m ruff --version ) >/dev/null 2>&1; then
  # main's lint config, as the worktree's lint reads it (a clone's own may lag): `--config` from origin/main's pyproject.toml
  # (in the clone's root: ruff resolves a config's exclude paths against the config file's own directory)
  # (and as a ruff.toml: its `[tool.ruff...]` sections, the prefix dropped - `--config` reads a ruff.toml's form)
  cfg="$ROOT/.land-tooling-lint-$$.toml"
  git -C "$ROOT" show origin/main:pyproject.toml 2>/dev/null | python3 -c 'import re,sys
keep=False
for line in sys.stdin:
    m=re.match(r"\s*\[(tool\.ruff(?:\.[^\]]+)?)\]\s*$", line)
    if re.match(r"\s*\[", line): keep=bool(m)
    if keep: print(("[" + m.group(1)[len("tool.ruff."):] + "]") if m and m.group(1) != "tool.ruff" else ("" if m else line.rstrip("\n")))' > "$cfg" || : > "$cfg"
  cfgarg=""; [ -s "$cfg" ] && cfgarg="--config $cfg"
  # shellcheck disable=SC2086 # one word per file
  if ! lint_out=$( cd "$ROOT" && python3 -m ruff check $cfgarg --force-exclude $first_pys 2>&1 && python3 -m ruff format --check $cfgarg --force-exclude $first_pys 2>&1 ); then
    rm -f "$cfg"
    printf '%s\n' "$lint_out" | head -12 >&2
    die "the checks failed in the clone (lint, before anything else ran) on$first_pys - python3 -m ruff format$first_pys, fix what ruff names, commit, and land again (feature 385 T91)"
  fi
  rm -f "$cfg"
fi
base=$(git -C "$ROOT" merge-base HEAD origin/main) || die "no merge base with origin/main"

if [ "$#" -eq 0 ]; then
  eligible=$(git -C "$ROOT" diff --name-only "$base" HEAD | while read -r f; do tooling "$f" && printf '%s ' "$f"; done)
  [ -n "$eligible" ] || die "this clone's commits change no tooling path - nothing to land" 2
  printf 'land-tooling: name the files to land - each lands WHOLE, so leave out any that describe work not yet landed.\n' >&2
  printf 'The tooling this clone changed:\n  make land-tooling FILES="%s"\n' "${eligible% }" >&2
  exit 2
fi
# GUARD_EDIT_OK: feature 385 T72 (plan D92) - A PLAN REVIEW'S ROW IS WRITTEN HERE: its agent recorded the verdict with `make
# plan-verdict`, so where it was recorded is known; 81 such rows were written by hand on 2026-10-18 and two landings refused for one.
# Any other owed pass still refuses below, as before.
( cd "$ROOT" && eval "${LAND_TOOLING_PLAN_ROWS:-python3 scripts/reviews/ledger_owed.py --write-plan-reviews --ledger dev/review-ledger.md}" ) >&2 || :
if git -C "$ROOT" rev-parse -q --verify HEAD >/dev/null && [ -n "$(git -C "$ROOT" status --porcelain -- dev/review-ledger.md 2>/dev/null)" ]; then  # T72: a fresh repo has no HEAD to diff
  git -C "$ROOT" commit -q -m "the plan reviews' ledger rows, written at landing (feature 385 T72)" -- dev/review-ledger.md || die "the plan reviews' ledger rows could not be committed"
fi
# GUARD_EDIT_OK: feature 383, the GM 2026-10-13 ("those are on disk, so it definitely can see them, right?") - THE LEDGER COMES
# WITH ITS PASSES, unasked: a session that named only its scripts had the push refuse its own review passes against main's
# ledger, and then escaped it with LEDGER_ROWS_OK. When the clone's commits change the ledger, it lands beside FILES.
if ! printf '%s\n' "$@" | grep -qx 'dev/review-ledger.md' && ! git -C "$ROOT" diff --quiet "$base" HEAD -- dev/review-ledger.md 2>/dev/null; then
  set -- "$@" dev/review-ledger.md
  printf 'land-tooling: dev/review-ledger.md lands too - the push answers this clone'"'"'s check passes from it\n' >&2
fi
# GUARD_EDIT_OK: feature 385 T46 (the round arbiter's fix on hour:385-approach-checklist@17) - A LANDED MAKEFILE BRINGS ITS PAGE: the
# worktree regenerates main's make-targets page, but the clone's own copy stayed stale, and the clone's next push refused it. So a
# Makefile in FILES lands only with the clone's page current, and that page lands beside it.
if printf '%s\n' "$@" | grep -qx 'Makefile'; then
  ( cd "$ROOT" && eval "${LAND_TOOLING_DOCS_CHECK:-python3 scripts/make-docs.py . --check}" ) >/dev/null 2>&1 \
    || die "docs/make-targets.html is stale against the clone's Makefile - run \`make docs\`, commit the page, and land again"
  if ! printf '%s\n' "$@" | grep -qx 'docs/make-targets.html' && ! git -C "$ROOT" diff --quiet "$base" HEAD -- docs/make-targets.html 2>/dev/null; then
    set -- "$@" docs/make-targets.html
    printf 'land-tooling: docs/make-targets.html lands too - the page generated from the Makefile\n' >&2
  python3 "$(dirname "${BASH_SOURCE[0]}")/hooks/lib/usage_log.py" record --tool land-tooling-docs --kind step --outcome changed 2>/dev/null || true  # feature 406 T03 (D162)
  fi
fi
for f in "$@"; do
  tooling "$f" || die "$f is not tooling (scripts/, tests/, .claude/agents/, .claude/skills/, .claude/workflows/, a CLAUDE.md, the Makefile, .claude/settings.json, docs/make-targets.html) - it lands with its feature"
done
git -C "$ROOT" diff --quiet HEAD -- "$@" || die "uncommitted changes in FILES - commit them first; only committed work lands"
# GUARD_EDIT_OK: feature 385 T53 (the round arbiter's fix on hour:385-approach-checklist@19) - OWED LEDGER ROWS ARE REFUSED FIRST: the
# push refused them only after about 35 s of checks, three times in one hour. Asked of the ledger as committed - what lands - and
# waived by LEDGER_ROWS_OK, as the push's own check is
if [ -z "${LEDGER_ROWS_OK:-}" ]; then
  committed=$(mktemp)
  git -C "$ROOT" show HEAD:dev/review-ledger.md > "$committed" 2>/dev/null || :
  if ! ( cd "$ROOT" && eval "${LAND_TOOLING_LEDGER:-python3 scripts/reviews/ledger_owed.py --refuse --ledger}" "$committed" ) >&2; then
    rm -f "$committed"
    die "check passes owe ledger rows (above) - write them (make ledger-owed WRITE=\"<where you recorded what you did>\"), commit, and land again"
  fi
  rm -f "$committed"
fi
patch=$(mktemp)
git -C "$ROOT" diff --binary "$base" HEAD -- "$@" > "$patch"
[ -s "$patch" ] || { rm -f "$patch"; die "FILES carry no change since main - nothing to land"; }

WT="$(dirname "$ROOT")/$(basename "$ROOT")-tooling"
[ -e "$WT" ] && die "$WT exists (a run that did not finish?) - remove it: git -C $ROOT worktree remove --force $WT"
step prepare
git -C "$ROOT" worktree add -q --detach "$WT" origin/main || die "cannot add the worktree at $WT"
step worktree
cleanup() { git -C "$ROOT" worktree remove --force "$WT" 2>/dev/null; rm -f "$patch"; }
LT_FILES="$*"
trap 'cleanup; lt_record' EXIT

# GUARD_EDIT_OK: feature 385 T24 (plan D46) - A STALE BASE IS MERGED, NOT REFUSED: measured 2026-10-18, three of three tooling
# landings were refused here because the ledger and the make-targets page moved on main, and each landed unchanged after a
# `sync-in`. So on a failed apply the clone merges origin/main (a merge commit, never a rebase), the patch is taken again from
# the new merge base, and it is applied once more; only a merge that conflicts, or a second failed apply, refuses.
if ! git -C "$WT" apply --index "$patch" 2>/dev/null; then
  # GUARD_EDIT_OK: feature 385 T30 - never merged under a running gate (the round arbiter on red-gate@2026-10-18T12:36:36Z)
  if [ -f "$ROOT/scripts/gates/gate_lock.py" ] && python3 "$ROOT/scripts/gates/gate_lock.py" held "$(git -C "$ROOT" rev-parse --absolute-git-dir)"; then
    die "FILES do not apply onto the latest main, and a gate is running in this clone - nothing is merged under it; run this again when it ends"
  fi
  if ! git -C "$ROOT" merge -q --no-edit origin/main >/dev/null 2>&1; then
    # GUARD_EDIT_OK: feature 385 T122 (D144; the round arbiter's change-route on hour:385-approach-checklist@35) - a conflict with
    # this clone's OWN earlier landing (a file new here, landed, then edited again) is named with its one-line fix, never resolved
    own=""
    for f in $(git -C "$ROOT" diff --name-only --diff-filter=U); do
      case "$(git -C "$ROOT" log -1 --format=%s origin/main -- "$f")" in "Tooling from $(basename "$ROOT"),"*) own="$own $f" ;; esac
    done
    git -C "$ROOT" merge --abort 2>/dev/null
    [ -z "$own" ] || die "FILES do not apply cleanly onto the latest main:$own conflict only with this clone's own earlier landing (main's last commit to them is it; for a file that was not new, git log origin/main --$own first, so no other session's change is lost) - run scripts/sync-with-main.sh sync-in, then git checkout --ours$own && git add$own && git commit --no-edit, then land again"
    die "FILES do not apply cleanly onto the latest main, and merging main into the clone conflicts - run scripts/sync-with-main.sh sync-in, resolve the conflict, commit, then run this again"
  fi
  printf 'land-tooling: main had moved under FILES - merged origin/main into the clone and took the patch again\n' >&2
  python3 "$(dirname "${BASH_SOURCE[0]}")/hooks/lib/usage_log.py" record --tool land-tooling-merge --kind step --outcome changed 2>/dev/null || true  # feature 406 T03 (D162)
  base=$(git -C "$ROOT" merge-base HEAD origin/main) || die "no merge base with origin/main"
  git -C "$ROOT" diff --binary "$base" HEAD -- "$@" > "$patch"
  [ -s "$patch" ] || die "FILES carry no change since main - nothing to land (main already has them)"
  git -C "$WT" reset -q --hard
  git -C "$WT" apply --index "$patch" 2>&1 | sed 's/^/  /' >&2
  [ "${PIPESTATUS[0]}" -eq 0 ] || die "FILES do not apply cleanly onto the latest main even after merging it - run scripts/sync-with-main.sh sync-in, then run this again"
fi
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
# GUARD_EDIT_OK: feature 385 T52 - THE PYTHON THAT LANDS IS LINTED FIRST: T49's test landed with its imports unsorted (and a merge's
# duplicate import after it), T51's fixture with the wrong blank lines - each caught by the next session's `make done`, on main.
# `ruff check` and `ruff format --check` on the landed .py files, in the worktree, beside the other two checks
pys=""; for f in "$@"; do case "$f" in *.py) pys="$pys $f" ;; esac; done
# --force-exclude (feature 385 T55): ruff lints a file it is NAMED even where pyproject.toml excludes it, and the gate leaves
# scripts/ and tests/hooks/ out on purpose - so without it a script's fix was refused for rules the gate never applies there
lint=${LAND_TOOLING_LINT:-${pys:+ruff check --force-exclude$pys && ruff format --check --force-exclude$pys}}
lint=${lint:-true}
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
# LINT FIRST, ALONE (feature 385 T67, plan D86): it takes 0.05 s, and T65's landing waited 122 s on the tests before its lint said
# one test file would be reformatted. A lint failure stops here, the other two never started; a clean lint runs them in parallel.
check lint "$lint"
ran=lint
if [ "$(cat "$log.lint.rc")" = 0 ]; then
  check guard-suites "$guards" & check tooling-tests "$tooling_tests" & wait
  ran="guard-suites tooling-tests lint"
fi
failed=""
for j in $ran; do
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
  case " $failed " in *" lint "*) printf 'land-tooling: lint failed on%s - `ruff format%s` for the format, the rule ruff names for the rest\n' "$pys" "$pys" >&2 ;; esac
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
LT_OUTCOME="landed"
printf 'land-tooling: landed %s on main. The clone keeps its own commits; its next sync-in merges them cleanly.\n' "$*"
