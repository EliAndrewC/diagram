#!/usr/bin/env bash
# review-gate.sh - the two independent reviews this project mandates, checked at SHIPPING time.
#
# Both are constitutional and both were unenforced (audit 2026-08-24). Both have already been skipped
# in practice, which is why they are checked by a script rather than trusted to a habit.
#
#   1. A SPEC-KIT SPEC IS REVIEWED BEFORE IMPLEMENTATION (constitution XVI). The reviewer catches
#      what the author cannot: on feature 127 it found two carve-outs in consecutive rounds, one of
#      which the author had flagged as a judgment call without being able to see why it was wrong.
#      Nothing compelled that review to happen.
#
#   2. A MODE B SETTLEMENT MAP IS REVIEWED BEFORE IT SHIPS (CLAUDE.md, Principle I's rationale). On
#      2026-07-27 three provincial-city maps went out unreviewed and nothing warned.
#
# HOW IT DECIDES, and it is deliberately coarse. This checks that the RECORD exists, not that the
# review was good - a script cannot judge that. A spec must carry a FAITHFUL verdict; a changed pool
# manifest must have its `.notes.md` touched in the same push. Coarse is the right setting: the
# expensive failure here is forgetting entirely, not reviewing badly.
#
# ESCAPE: REVIEW_GATE_OK with a reason, because there are real cases - a spec superseded before
# implementation, a manifest changed by a mechanical sweep. Using it puts the reason in the push.
set -uo pipefail

RANGE="${1:-origin/main..HEAD}"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT" || exit 0

# GUARD_EDIT_OK: feature 168 - this gate records what it does, escape included (GM 2026-08-30). It
# refuses two different things - a spec with no fidelity verdict, and a re-rolled map with no review
# logged - so the rule slug says which. Nothing it refuses changes.
RG_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$RG_HERE/_guardlog.sh"
# GUARD_EDIT_OK: feature 170 - this escape already RECORDED; now it must also say something. An
# environment variable's VALUE is its reason, and `REVIEW_GATE_OK=1` explains nothing to the person
# auditing later, which is the whole point (GM 2026-08-30).
if [ -n "${REVIEW_GATE_OK:-}" ]; then
  if ! python3 "$RG_HERE/_hookmatch.py" reason-ok <<<"$REVIEW_GATE_OK" >/dev/null; then
    guard_log review-gate blocked "$REVIEW_GATE_OK" REVIEW_GATE_OK-no-reason
    printf 'review-gate: REVIEW_GATE_OK needs a REASON, not just a value - two words and eight characters.\n' >&2
    printf 'It ships with the push and is what a later audit reads, so say what makes this case exempt.\n' >&2
    exit 1
  fi
  guard_log review-gate escaped "$REVIEW_GATE_OK" review-gate-ok
  printf 'review-gate: BYPASSED - %s\n' "$REVIEW_GATE_OK"
  exit 0
fi

changed=$(git diff --name-only "$RANGE" 2>/dev/null || true)
[ -z "$changed" ] && exit 0
fail=""

# THE NUMBER CLAIM IS NOT AN IMPLEMENTATION (feature 165, the GM's ruling 2026-08-30).
#
# GUARD_EDIT_OK. Two rules in this repository contradicted each other, and the contradiction had a
# price. `CLAUDE.md` requires a feature number to be claimed by pushing the new `specs/NNN-slug/`
# THE MOMENT `spec.md` is written - *"the locked pull+push makes the claim atomic"* - because several
# sessions allocate numbers at once. This gate refused that push, every time, for lacking a fidelity
# verdict that a spec written one minute ago cannot possibly carry. Measured on 2026-08-30: one
# session lost the number 161 to a peer while its spec was in review, renumbered to 162, then lost
# 163 the same way; the second renumber swept 67 files, 51 of them wrongly.
#
# So a delta that is EXACTLY one new spec directory - every path under it, every one of them an
# ADDITION, and nothing anywhere else - passes check 1. The reviewed-before-implementation property
# is untouched by construction: no implementation can be present in a delta that contains nothing but
# a new spec directory, and the moment one other file joins it the verdict is required again. A
# MODIFIED existing spec is judged exactly as before, so a spec cannot be smuggled past by editing it
# after the claim.
claim_only=""
spec_dirs=$(printf '%s\n' "$changed" | sed -n 's|^\(specs/[^/]*\)/.*|\1|p' | sort -u)
if [ -n "$spec_dirs" ] && [ "$(printf '%s\n' "$spec_dirs" | wc -l)" -eq 1 ] \
   && ! printf '%s\n' "$changed" | grep -qv '^specs/' \
   && ! git diff --name-status "$RANGE" -- "$spec_dirs" 2>/dev/null | awk '{print $1}' | grep -qv '^A$' \
   && git diff --name-status "$RANGE" -- "$spec_dirs/spec.md" 2>/dev/null | grep -q '^A'; then
  # THE SPEC ITSELF MUST BE ONE OF THE NEW FILES. "every changed file is an addition" is not enough:
  # adding only `tasks.md` to a spec directory that already exists in main satisfies that too, and
  # that is the IMPLEMENTATION push, which owes the verdict. The suite caught this shape.
  claim_only=1
  printf 'review-gate: NUMBER CLAIM - %s alone, every file new. The fidelity verdict is owed before\n' "$spec_dirs"
  printf '             implementation, not before the number is reserved (feature 165, GM 2026-08-30).\n'
fi

# --- 1. every spec.md being shipped carries a fidelity verdict --------------------------------
# WHICH SPECS ARE JUDGED. Not only the ones whose `spec.md` changed: ANY delta touching a feature
# directory brings that feature's spec under the check. Without that, the claim exemption below opens
# a hole one step removed from itself - claim the number with an unreviewed spec, then push the
# implementation, whose delta touches `tasks.md` and the code but not `spec.md`, and check 1 never
# looks at the spec again. Judging the directory closes it: every later push for that feature carries
# the verdict requirement with it. (Feature 165; the exemption is the GM's ruling, the hole is this
# session's own finding while implementing it.)
touched_specs=$(printf '%s\n' "$changed" | sed -n 's|^\(specs/[^/]*\)/.*|\1/spec.md|p' | sort -u)
for spec in $([ -z "$claim_only" ] && printf '%s\n' "$touched_specs" || true); do
  [ -f "$spec" ] || continue
  # A VERDICT, not a MENTION (feature 156, 2026-08-29). The check used to be a bare `grep FAITHFUL`,
  # which two shapes satisfied without a review having passed: a spec whose only occurrence is "NOT
  # FAITHFUL" - i.e. one a reviewer REJECTED - and a spec whose prose merely discusses the word. So
  # the occurrence must survive dropping every negated line AND must sit on a line that names the
  # review it reports (a Status line, a round, a verdict, the agent). Still deliberately coarse: this
  # proves the RECORD exists, never that the review was good. Measured against all 56 specs in the
  # repository when it was written - 71 of 71 unchanged, and it is the guard's own "match INVOCATIONS
  # not mentions" rule finally applied to itself.
  if ! grep -E 'FAITHFUL' "$spec" | grep -viE 'NOT[[:space:]]+\**FAITHFUL' | grep -qiE 'status|verdict|round|spec-fidelity'; then
    printf '\n\033[1mREVIEW GATE: %s has no fidelity verdict.\033[0m\n' "$spec"
    printf 'Constitution XVI: a specification is reviewed against the GM'"'"'S OWN WORDS before\n'
    printf 'implementation, by someone other than its author. Run the `spec-fidelity` subagent in\n'
    printf 'Mode 2, give it the GM request VERBATIM (not the plan - a spec checked against its own\n'
    printf 'plan is tested for self-consistency, which a wrong spec passes), and record the verdict\n'
    printf 'in a "## Review history" section.\n'
    fail="$fail $spec"
  fi
done

# --- 2. a re-rolled pool map has a review logged beside it ------------------------------------
# BOTH TREES (feature 161). This is a PATTERN, not a walk: when the hand-authored maps moved to
# legacy-hand-authored-pool/ a pattern anchored on `pool/` simply stopped matching them, with
# nothing turning red - the guard would have quietly stopped covering the frozen tree.
for man in $(printf '%s\n' "$changed" | grep -E '^\.claude/skills/diagram/(pool|legacy-hand-authored-pool)/.*\.json$' || true); do
  notes="${man%.json}.notes.md"
  [ -f "$notes" ] || continue          # a map with no notes file predates the convention
  if ! printf '%s\n' "$changed" | grep -qxF "$notes"; then
    printf '\n\033[1mREVIEW GATE: %s changed, but %s did not.\033[0m\n' "$(basename "$man")" "$(basename "$notes")"
    printf 'A Mode B map gets an independent `settlement-review` before it ships - the author is not\n'
    printf 'a reliable reviewer of their own visual output. Log the pass in the notes file'"'"'s Review\n'
    printf 'section. On 2026-07-27 three city maps shipped unreviewed and nothing warned.\n'
    fail="$fail $(basename "$man")"
  fi
done

if [ -n "$fail" ]; then
  printf '\n\033[1mreview-gate FAILED:%s\033[0m\n' "$fail"
  printf 'If a case is genuinely exempt - a superseded spec, a mechanical sweep across every map -\n'
  printf 'set REVIEW_GATE_OK="<reason>" so the reason ships with the push.\n\n'
  # GUARD_EDIT_OK: feature 168 - the rule names WHICH half refused: an unreviewed spec, an unreviewed
  # map, or both.
  case "$fail" in
    *spec.md*json*|*json*spec.md*) guard_log review-gate blocked "$fail" spec-and-map ;;
    *spec.md*)                     guard_log review-gate blocked "$fail" spec-no-verdict ;;
    *)                             guard_log review-gate blocked "$fail" map-no-review ;;
  esac
  exit 1
fi
printf 'review-gate: clean\n'
