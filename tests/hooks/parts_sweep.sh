#!/usr/bin/env bash
# parts_sweep.sh [suite...] - run each split guard suite at 1, 2, 3 and 8 parts and report any count whose summary differs.
#
# WHY (the round arbiter's tooling fix on hour:383-tooling-caches-and-hourly-step-back@3, feature 383 amendment 4): a suite dealt
# into parallel parts can hide a case that leans on state another case left - pair's case_02 failed only when the measured
# weights dealt case_04 before it into the same part - and the session found it by hand-written loops over each suite's own
# parts variable, twice in one hour. This is that loop, kept: run by hand (`make parts-sweep`) after a suite's cases change,
# never by the gate, which stays one deterministic run.
#
# A suite is named by its file; the variable that sets its parts is read from the file (`<NAME>_PARTS:-`). Each count's
# summary line is compared with the one-part run; a difference, or a nonzero exit, is printed and fails the sweep.
# PARTS_SWEEP_COUNTS overrides "1 2 3 8".
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COUNTS=${PARTS_SWEEP_COUNTS:-"1 2 3 8"}
if [ "$#" -eq 0 ]; then
  # every suite that deals its cases into parts: it sources parts.sh, or carries its own SUITE_PARTS runner
  set -- $(grep -lE 'source "\$HERE/parts.sh"|SUITE_PARTS=\$\{SUITE_PARTS' "$HERE"/test-*.sh | xargs -n1 basename)
fi
bad=0
for suite in "$@"; do
  f="$HERE/$suite"
  var=$(grep -oE '\$\{([A-Z]+_PARTS):-' "$f" | head -1 | sed -E 's/\$\{([A-Z]+_PARTS):-/\1/')
  [ -n "$var" ] || { echo "$suite: no <NAME>_PARTS variable - skipped"; continue; }
  first=""; this=0  # GUARD_EDIT_OK: feature 383 amendment 4 - the arbiter's tooling fix, per-suite verdict
  for n in $COUNTS; do
    out=$(env PARTS_MAX= "$var=$n" bash "$f" 2>&1); rc=$?
    line=$(printf '%s\n' "$out" | grep -E '[0-9]+ (passed|checks)|passed [0-9]+' | tail -1)
    if [ -z "$first" ]; then first="$line"; fi
    if [ "$rc" -ne 0 ] || [ "$line" != "$first" ]; then
      echo "$suite at $var=$n: exit $rc, '$line' (one part: '$first')"
      printf '%s\n' "$out" | grep -E 'FAIL' | head -5 | sed 's/^/    /'
      bad=1; this=1
    fi
  done
  [ "$this" -eq 0 ] && echo "$suite: the same at $COUNTS parts ($first)"
done
exit "$bad"
