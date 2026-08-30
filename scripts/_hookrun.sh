#!/usr/bin/env bash
# _hookrun.sh - run ONE guard suite, for the parallel `hooks-test` (feature 172).
#
# Usage: _hookrun.sh <work-dir> <gitdir> <guard> <suite> <sha>
#
# WHY THIS EXISTS: `hooks-test` ran its 21 suites one after another - 94 s, against 17 s for the
# entire 2,286-test Python suite, which pytest runs in parallel. When a shared helper changes, the
# derived dependency set is still 19-20 suites (`_guardlog.sh` calls `_hookmatch.py`), so the
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

if "$HERE/$SUITE" > "$WORK/$GUARD.log" 2>&1; then
  mkdir -p "$GITDIR/hooks-test" && printf '%s' "$SHA" > "$GITDIR/hooks-test/$GUARD"
  printf 'ok' > "$WORK/$GUARD.rc"
else
  printf 'FAIL' > "$WORK/$GUARD.rc"
fi
exit 0   # never fail the fan-out; the collector reads the .rc files and reports every failure together
