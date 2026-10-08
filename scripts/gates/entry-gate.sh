#!/usr/bin/env bash
# entry-gate.sh - the RECORD GATE: no record check a delta owes lands unanswered (feature 311), the modal half
# of which is where it began - a modal whose research section moved underneath it does not land unexamined.
#
# GUARD_EDIT_OK: feature 311 - THE GATE NOW HOLDS EVERY RECORD CHECK (GM 2026-10-02: *"not just do the correct thing, to
# kind of enforce us doing the correct thing"*). `scripts/record/record_owed.py --unanswered` names each unit the delta owes -
# intro-check, record-format, source-reader, quote-check, source-applicability, translation-check, entry-drift - that has
# no answer record at the content being pushed (`make record-checked` writes one when a check returns). Before this,
# quote-check and record-format were doctrine with no mechanism at the push. Nothing is loosened: the entry-drift units
# are the ones `entry_owed.py` named before, less the intro and comment edits that moved no finding (spec FR-004), and
# ENTRY_DRIFT_OK still discharges exactly them. RECORD_CHECKS_OK discharges every unit, with a reason, to the bypass log.
#
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
# 28 of 30 research-only commits to 27 of 30 (specs/234-entry-owed-when-the-record-moves/research.md R5).
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
. "$EG_HERE/../hooks/lib/guardlog.sh"

# GUARD_EDIT_OK: feature 311 - one writer of a reason to dev/bypass-log/, for either escape.
record_bypass() {  # $1 the escape's name, $2 its reason
  if ! python3 "$EG_HERE/../hooks/lib/hm_escape.py" reason-ok <<<"$2" >/dev/null; then
    guard_log entry-gate blocked "$2" "$1-no-reason"
    printf 'entry-gate: %s needs a REASON, not just a value - two words and eight characters.\n' "$1" >&2
    printf 'It ships with the push and is what a later audit reads: say what moved and why no check is owed.\n' >&2
    return 1
  fi
  guard_log entry-gate escaped "$2" "$(printf '%s' "$1" | tr 'A-Z_' 'a-z-')"
  # AND to dev/bypass-log/, which is what `make audit` reads and what the spec promises a later reader
  # (SC-013). The guard log is per-host and gitignored; a reason that ships with the push has to be in
  # the repository, like every other bypass this project records.
  BL="$ROOT/dev/bypass-log/$(date -u +%Y-%m)"   # GUARD_EDIT_OK: 2026-10-02 - a month folder, as every log writer
  mkdir -p "$BL" 2>/dev/null || true
  python3 - "$BL" "$1: $2" <<'PYBL' || true
import json, os, pathlib, secrets, subprocess, sys, time
bl, why = pathlib.Path(sys.argv[1]), sys.argv[2]
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
(bl / f"{stamp}-{secrets.token_hex(3)}.json").write_text(
    json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "target": "entry-gate", "commit": head, "why": why}, indent=2) + "\n",
    encoding="utf-8",
)
PYBL
  printf 'entry-gate: BYPASSED (%s) - %s\n  recorded in dev/bypass-log/ - `make audit` lists it\n' "$1" "$2"
}

if [ -n "${RECORD_CHECKS_OK:-}" ]; then
  record_bypass RECORD_CHECKS_OK "$RECORD_CHECKS_OK" || exit 1
  exit 0
fi
SKIP=""
if [ -n "${ENTRY_DRIFT_OK:-}" ]; then
  record_bypass ENTRY_DRIFT_OK "$ENTRY_DRIFT_OK" || exit 1
  SKIP="--skip-check entry-drift"
fi

# shellcheck disable=SC2086
# GUARD_EDIT_OK: feature 311 - no bytecode: the push's own suite runs this in fixture trees whose `git status` must stay clean
OWED="$(PYTHONDONTWRITEBYTECODE=1 python3 "$EG_HERE/../record/record_owed.py" --root "$ROOT" --unanswered $SKIP 2>/dev/null || true)"
case "$OWED" in ""|"record-owed: no record check is owed"*) exit 0 ;; esac

guard_log entry-gate blocked "$(printf '%s' "$OWED" | head -c 400)" record-owed
printf '\n\033[1mRECORD GATE: the delta owes record checks that have no answer at the content being pushed.\033[0m\n' >&2
printf '%s\n' "$OWED" | sed 's/^/  /' >&2
printf '\nEach unit is owed because the words its check reads changed (`make record-owed` says why). Build the bundle the\n' >&2
printf 'line names, dispatch the check on its MANIFEST, then `make record-checked CHECK=<check> BUNDLE=<dir> RESULT="<counts>"`.\n' >&2
printf 'A modal'"'"'s entry-drift is also answered by rewriting its prose. If a section moved without any FINDING moving,\n' >&2
printf 'ENTRY_DRIFT_OK="<why no modal is now wrong>" discharges the entry-drift units; RECORD_CHECKS_OK="<why>" every unit.\n\n' >&2
exit 1
