#!/usr/bin/env bash
# hookrun.sh - run ONE guard suite, for the parallel `hooks-test` (feature 172).
#
# Usage: hookrun.sh <work-dir> <gitdir> <guard> <suite> <sha>
#
# WHY THIS EXISTS: `hooks-test` ran its 21 suites one after another - 94 s, against 17 s for the
# entire 2,286-test Python suite, which pytest runs in parallel. When a shared helper changes, the
# derived dependency set is still 19-20 suites (`guardlog.sh` calls `hookmatch.py`), so the
# dependency refinement cannot help the common case and concurrency is the only thing that does.
#
# WHY A SEPARATE SCRIPT rather than a subshell in the Makefile: each job needs its own log file and
# its own exit-code file, and a recipe line that already carries three levels of quoting is where
# that goes wrong silently. It also makes the unit testable on its own.
#
# The stamp is written HERE, by the job, and only on success - so a suite that goes green in a run
# where another fails is still recorded green, exactly as the serial version did.
set -uo pipefail
WORK=${1:?work dir}; GITDIR=${2:?gitdir}; GUARD=${3:?guard}; SUITE=${4:?suite}; SHA=${5:?sha}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# A SUITE GETS AN EMPTY STDIN (feature 449 T054): a case that runs the guard binary with no input of its own inherited this shell's, which in a tool's shell is a socket that never closes, and the binary reads to its end (hung 10 minutes, 2026-11-08).
t0=${EPOCHREALTIME/,/.}
# GUARD_EDIT_OK: 405 batch 8 - A SUITE RUNS WITH NO SESSION'S ESCAPE SET: `PLAN_REVIEW_OK=... make land` carried the escape through
# `make done` into every suite, and sync-with-main's "it fires" cases came back escaped (rc 0 where 1 was asserted). Each
# `*_OK` variable the session set is cleared here; a case that tests an escape sets its own.
while IFS="=" read -r name _; do case "$name" in *_OK) unset "$name" 2>/dev/null ;; esac; done < <(env)
# GUARD_EDIT_OK: feature 383 amendment 4 - beside other suites a split suite runs in at most PARTS_MAX parts (make hooks-test sets it from the cores and the suites running; two when run without it): eight
# suites of eight parts each hit the containers' shared 10 GB memory cap (2026-10-17). A suite run alone keeps its own count.
export PARTS_MAX=${PARTS_MAX:-2}
# THE LEAK PIN (feature 449 T101): each suite runs with its own TMPDIR, and anything it leaves there fails it, by name - the checks
# and tests that never removed their scratch directories left about 329,000 of them, roughly 126 GB, in the GM's /tmp (2026-11-11).
# It sits under the temp directory itself, so a guard that knows a fixture by its /tmp/ path still does. A SIGKILL cannot be
# caught, so a killed suite's own traps never run: this runner removes the directory whole after the suite, on every path out of it,
# an INT or a TERM exiting through it after stopping the suite; and a runner stopped by SIGKILL, whose trap never ran, leaves its
# directory to the next run, which removes every l7r-hooks-suite-*-p<pid>.* whose pid is gone and which has not changed in three hours
# (the GM 2026-11-11: "don't touch dirs younger than a few hours (a running gate may own them)" - a killed runner's suite can still be
# running in it); directories of the form before T101 are left to the GM's laptop session.
for d in "${TMPDIR:-/tmp}"/l7r-hooks-suite-*-p[0-9]*.*; do
  p=${d##*-p}; p=${p%%.*}
  case $p in '' | *[!0-9]*) continue ;; esac
  [ -d "$d" ] && [ ! -e "/proc/$p" ] && [ -n "$(find "$d" -maxdepth 0 -mmin +180)" ] && rm -rf "$d"
done
SUITE_TMP=$(mktemp -d "${TMPDIR:-/tmp}/l7r-hooks-suite-$GUARD-p$$.XXXXXX")
trap 'rm -rf "$SUITE_TMP"' EXIT
trap 'pkill -P $$ 2>/dev/null; exit 130' INT
trap 'pkill -P $$ 2>/dev/null; exit 143' TERM
# GUARD_EDIT_OK: feature 383 amendment 3 (plan D27), adding an operation - under the C-library recorder when make hooks-test built
# it, so a green suite's reads are kept (`l7r-guard trace`): a fixture's copy of scripts/ counts as the file it copies,
# the fixture's cp does not
if [ -n "${HOOKS_SHIM:-}" ] && [ -n "${HOOKS_ROOT:-}" ]; then
  rm -f "$WORK/$GUARD.reads"
  env TMPDIR="$SUITE_TMP" LD_PRELOAD="$HOOKS_SHIM${LD_PRELOAD:+ $LD_PRELOAD}" UV_USE_IO_URING=0 L7R_TEST_DEP_LOG="$WORK/$GUARD.reads" L7R_TEST_DEP_ROOT="$HOOKS_ROOT" \
    L7R_TEST_DEP_FILE="$GUARD" L7R_TEST_DEP_SKIP="cp" L7R_TEST_DEP_MAP=scripts "$HERE/$SUITE" < /dev/null > "$WORK/$GUARD.log" 2>&1; rc=$?
else
  TMPDIR="$SUITE_TMP" "$HERE/$SUITE" < /dev/null > "$WORK/$GUARD.log" 2>&1; rc=$?
fi
# l7r-test-scratch is what a whole Rust test process shares (`beside_binary`), which nothing in it outlives to remove: it goes with
# SUITE_TMP on this runner's exit, as it goes with `make rust-test`'s own run directory
left=$(ls -A "$SUITE_TMP" 2>/dev/null | grep -vx 'l7r-test-scratch' | tr '\n' ' ')
if [ -n "$left" ]; then
  printf '\nLEAK: the suite left %s in its TMPDIR, which it must remove\n  fix: make each mktemp with a trap that removes it on EXIT (`d=$(mktemp -d); trap '"'"'rm -rf "$d"'"'"' EXIT`), or remove it before the case returns; a Rust test holds an l7r_guard::shared::tempdir::TempDir\n' "$left" >> "$WORK/$GUARD.log"
  rc=1
fi
# feature 383 amendment 3 (plan D27): each suite's seconds beside it, so hooks-test can say which suites ran and what each cost
awk -v a="$t0" -v b="${EPOCHREALTIME/,/.}" 'BEGIN { printf "%.1f", b - a }' > "$WORK/$GUARD.s"
# feature 449 T125: kept beside the suite's stamp, pass or fail, so the next run starts the longest suites first
mkdir -p "$GITDIR/hooks-test" && cp "$WORK/$GUARD.s" "$GITDIR/hooks-test/$GUARD.s"
if [ "$rc" -eq 0 ]; then
  mkdir -p "$GITDIR/hooks-test" && printf '%s' "$SHA" > "$GITDIR/hooks-test/$GUARD"
  [ -n "${HOOKS_SHIM:-}" ] && "$HERE/../../scripts/hooks/l7r-guard.sh" trace stamp "$GITDIR" "$GUARD" "$WORK/$GUARD.reads" "$HOOKS_ROOT" >/dev/null 2>&1
  printf 'ok' > "$WORK/$GUARD.rc"
else
  printf 'FAIL' > "$WORK/$GUARD.rc"
fi
exit 0   # never fail the fan-out; the collector reads the .rc files and reports every failure together
