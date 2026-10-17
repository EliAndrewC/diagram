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

t0=${EPOCHREALTIME/,/.}
# GUARD_EDIT_OK: feature 383 amendment 4 - beside other suites a split suite runs in at most PARTS_MAX parts (make hooks-test sets it from the cores and the suites running; two when run without it): eight
# suites of eight parts each hit the containers' shared 10 GB memory cap (2026-10-17). A suite run alone keeps its own count.
export PARTS_MAX=${PARTS_MAX:-2}
# GUARD_EDIT_OK: feature 383 amendment 3 (plan D27), adding an operation - under the C-library recorder when make hooks-test built
# it, so a green suite's reads are kept (tests/hooks/hooktrace.py): a fixture's copy of scripts/ counts as the file it copies,
# the fixture's cp does not
if [ -n "${HOOKS_SHIM:-}" ] && [ -n "${HOOKS_ROOT:-}" ]; then
  rm -f "$WORK/$GUARD.reads"
  env LD_PRELOAD="$HOOKS_SHIM${LD_PRELOAD:+ $LD_PRELOAD}" UV_USE_IO_URING=0 L7R_TEST_DEP_LOG="$WORK/$GUARD.reads" L7R_TEST_DEP_ROOT="$HOOKS_ROOT" \
    L7R_TEST_DEP_FILE="$GUARD" L7R_TEST_DEP_SKIP="cp" L7R_TEST_DEP_MAP=scripts "$HERE/$SUITE" > "$WORK/$GUARD.log" 2>&1; rc=$?
else
  "$HERE/$SUITE" > "$WORK/$GUARD.log" 2>&1; rc=$?
fi
# feature 383 amendment 3 (plan D27): each suite's seconds beside it, so hooks-test can say which suites ran and what each cost
awk -v a="$t0" -v b="${EPOCHREALTIME/,/.}" 'BEGIN { printf "%.1f", b - a }' > "$WORK/$GUARD.s"
if [ "$rc" -eq 0 ]; then
  mkdir -p "$GITDIR/hooks-test" && printf '%s' "$SHA" > "$GITDIR/hooks-test/$GUARD"
  [ -n "${HOOKS_SHIM:-}" ] && python3 "$HERE/hooktrace.py" stamp "$GITDIR" "$GUARD" "$WORK/$GUARD.reads" "$HOOKS_ROOT" >/dev/null 2>&1
  printf 'ok' > "$WORK/$GUARD.rc"
else
  printf 'FAIL' > "$WORK/$GUARD.rc"
fi
exit 0   # never fail the fan-out; the collector reads the .rc files and reports every failure together
