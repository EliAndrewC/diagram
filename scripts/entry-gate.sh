#!/usr/bin/env bash
# entry-gate.sh - a modal whose research section moved underneath it does not land unexamined.
#
# WHY IT REFUSES AT ALL (feature 234, GM 2026-09-12). What a modal says about a feature IS the docstring
# of its `Kind` class, written FROM a research section the class names in its `Entry:` tag - and nothing
# noticed when that section's content moved. The GM, told to update the pigsty write-up: *"if I hadn't
# said that ... then would you have done it?"* It would not have been.
#
# WHY IT REFUSES RATHER THAN REPORTS. An earlier draft of this feature made the obligation doctrine with
# no mechanism, on the measurement that the key fires on nearly every research-only commit. The GM struck
# that: *"I don't believe that we should have any such thing as an unenforced doctrine. If it is
# unenforced, then it is not a doctrine. something should either not be considered doctrinal or it should
# be enforced."* Narrowing the key was priced first and is dead - firing only on what a READER SEES takes
# 39 of 39 research-only commits to 38 of 39 (specs/234-entry-owed-when-the-record-moves/research.md R5).
# There is no mechanical key that separates "this section now says something different" from "this
# section was maintained", because that is a judgment about meaning.
#
# SO THE SESSION SUPPLIES THE JUDGMENT, IN WRITING. This is the shape the repository already uses for
# every rule whose compliant action only a session can give - `guard-write`, `guard-file`,
# `FILE_SIZE_OK`, `PAIR_OK`: refuse, take a reason, record it. Discharge a named pair by rewriting the
# modal's prose, or by ENTRY_DRIFT_OK with a reason - ONE reason may cover a whole maintenance sweep,
# because the obligation is per pair whose section's FINDING moved, not per pair named.
#
# It is deliberately coarse, like review-gate.sh: it checks that the pair was ANSWERED, never that the
# answer was good. A script cannot judge prose; `entry-drift` can, and the refusal says to dispatch it.
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT" || exit 0

EG_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$EG_HERE/_guardlog.sh"

if [ -n "${ENTRY_DRIFT_OK:-}" ]; then
  if ! python3 "$EG_HERE/_hm_escape.py" reason-ok <<<"$ENTRY_DRIFT_OK" >/dev/null; then
    guard_log entry-gate blocked "$ENTRY_DRIFT_OK" ENTRY_DRIFT_OK-no-reason
    printf 'entry-gate: ENTRY_DRIFT_OK needs a REASON, not just a value - two words and eight characters.\n' >&2
    printf 'It ships with the push and is what a later audit reads: say what the sections moved and why\n' >&2
    printf 'no modal written from them now says the wrong thing.\n' >&2
    exit 1
  fi
  guard_log entry-gate escaped "$ENTRY_DRIFT_OK" entry-drift-ok
  printf 'entry-gate: BYPASSED - %s\n' "$ENTRY_DRIFT_OK"
  exit 0
fi

NAMED="$(python3 "$EG_HERE/_entry_owed.py" --root "$ROOT" 2>/dev/null || true)"
[ -z "$NAMED" ] && exit 0

guard_log entry-gate blocked "$(printf '%s' "$NAMED" | head -c 400)" entry-owed
printf '\n\033[1mENTRY GATE: a research section moved and the modal written from it did not.\033[0m\n' >&2
printf '%s\n' "$NAMED" | sed 's/^/  /' >&2
printf '\nWhat a modal says IS the class docstring, written FROM the section its `Entry:` names. Dispatch the\n' >&2
printf '`entry-drift` agent at each pair above - it reads the explanation prose against the section as it\n' >&2
printf 'now stands and returns IN-STEP, DRIFTED or CANNOT-TELL - then rewrite the prose it calls DRIFTED.\n' >&2
printf '\nIf the sections moved without any FINDING moving - a footnote relocated, a session note turned into\n' >&2
printf 'a comment, a citation re-pointed, a passage translated - that is one line, not one dispatch per\n' >&2
printf 'class: ENTRY_DRIFT_OK="<what moved, and why no modal is now wrong>" and the reason ships with the\n' >&2
printf 'push for `make audit` to list.\n\n' >&2
exit 1
