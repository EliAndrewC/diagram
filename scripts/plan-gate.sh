#!/usr/bin/env bash
# plan-gate.sh - a feature whose tasks are ticked does not land without its plan reviewed (feature 243).
#
# WHY. Constitution XVI puts an independent check in front of every exception, and review-gate.sh holds it
# for a SPEC. A plan is written after that verdict and nothing read it, so feature 239's plan narrowed its
# accepted spec - framed as an open question, not as a narrowing - and the narrowing reached ticked tasks
# and main unchecked (specs/243-plan-decisions-reviewed-before-tasks/research.md R1).
#
# WHY AT THE PUSH AS WELL AS AT `make tick`. A box can be ticked by a hand edit of tasks.md, and nothing
# refuses that (spec D4). So every feature the delta touches - the set review-gate.sh check 1 judges - that
# has a ticked task must carry a plan-review.json matching its plan.md with a CLEAR verdict, read at HEAD
# because HEAD is what lands. A feature with no ticked task, a plan still being drafted, passes (D3).
#
# It is deliberately coarse, like review-gate.sh: it checks that the review was RECORDED and current,
# never that it was good. The judgment is `spec-fidelity`'s, in its PLAN REVIEW mode.
#
# ESCAPE: PLAN_REVIEW_OK with a reason, recorded to the guard log and dev/bypass-log/.
set -uo pipefail

RANGE="${1:-origin/main..HEAD}"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT" || exit 0

PG_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$PG_HERE/_guardlog.sh"

if [ -n "${PLAN_REVIEW_OK:-}" ]; then
  if ! python3 "$PG_HERE/_hm_escape.py" reason-ok <<<"$PLAN_REVIEW_OK" >/dev/null; then
    guard_log plan-gate blocked "$PLAN_REVIEW_OK" PLAN_REVIEW_OK-no-reason
    printf 'plan-gate: PLAN_REVIEW_OK needs a REASON, not just a value - two words and eight characters.\n' >&2
    printf 'It ships with the push and is what a later audit reads: say why these plans need no review.\n' >&2
    exit 1
  fi
  guard_log plan-gate escaped "$PLAN_REVIEW_OK" plan-review-ok
  python3 -c 'import pathlib, sys; sys.path.insert(0, sys.argv[1]); import _plan_gate; _plan_gate.bypass_record(pathlib.Path(sys.argv[2]), "push", sys.argv[3])' \
    "$PG_HERE" "$ROOT" "$PLAN_REVIEW_OK" || true
  printf 'plan-gate: BYPASSED - %s\n' "$PLAN_REVIEW_OK"
  printf '  recorded in dev/bypass-log/ - `make audit` lists it\n'
  exit 0
fi

OWED="$(python3 "$PG_HERE/_plan_gate.py" push "$RANGE")"
[ -z "$OWED" ] && exit 0

while IFS=$'\t' read -r feature rule _; do
  guard_log plan-gate blocked "$feature" "$rule"
done <<<"$OWED"
printf '\n\033[1mPLAN GATE: a feature with ticked tasks has no current CLEAR plan review.\033[0m\n' >&2
printf '%s\n' "$OWED" | awk -F'\t' '{ printf "  %s (%s)\n    %s\n", $1, $2, $3 }' >&2
printf '\nThe reviewer reads the whole plan against request.md and spec.md, lists its decisions and rules on\n' >&2
printf 'each one that narrows what was asked. If a case is genuinely exempt, set\n' >&2
printf 'PLAN_REVIEW_OK="<reason>" so the reason ships with the push.\n\n' >&2
exit 1
