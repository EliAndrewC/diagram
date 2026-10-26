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

# GUARD_EDIT_OK: THREE DOTS, the merge base (2026-09-26). The gate runs BEFORE sync-with-main's locked pull, and a
# two-dot `git diff origin/main..HEAD` compares TREES - so every map another session pushed since this clone last
# synced read as this clone's change, and a tooling push was refused over five maps it never touched.
RANGE="${1:-origin/main...HEAD}"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT" || exit 0

# GUARD_EDIT_OK: feature 168 - this gate records what it does, escape included (GM 2026-08-30). It
# refuses two different things - a spec with no fidelity verdict, and a re-rolled map with no review
# logged - so the rule slug says which. Nothing it refuses changes.
RG_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$RG_HERE/../hooks/lib/guardlog.sh"
# GUARD_EDIT_OK: feature 170 - this escape already RECORDED; now it must also say something. An
# environment variable's VALUE is its reason, and `REVIEW_GATE_OK=1` explains nothing to the person
# auditing later, which is the whole point (GM 2026-08-30).
if [ -n "${REVIEW_GATE_OK:-}" ]; then
  if ! python3 "$RG_HERE/../hooks/lib/hm_escape.py" reason-ok <<<"$REVIEW_GATE_OK" >/dev/null; then
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
rules=""   # GUARD_EDIT_OK: feature 248 - the map half's refusals, each named for the firing log
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
  # A FILED SPEC IMPLEMENTS NOTHING (feature 330): deferred work is filed as a feature whose spec.md says
  # `**Status**: Filed` and carries the deferred text - no plan, no tasks. Constitution XVI reviews a spec BEFORE
  # IMPLEMENTATION, and a filed one has none; the moment it gains a tasks.md it is being implemented, and the
  # verdict is owed here like any other. (Code pushed without touching the spec's directory never brought it
  # under this check anyway, so the exemption opens nothing the check held.)
  if [ ! -f "$(dirname "$spec")/tasks.md" ] && grep -qE '^\*\*Status\*\*:?[[:space:]]*Filed\b' "$spec"; then continue; fi
  # GUARD_EDIT_OK: the GM 2026-10-10 withdrew filed feature 345 and this check refused the status edit. A spec WITHDRAWN
  # or SUPERSEDED with no tasks.md was never implemented, so it owes no verdict either; one that was planned keeps owing it.
  if [ ! -f "$(dirname "$spec")/tasks.md" ] && grep -qiE '^\*\*Status\*\*:?[[:space:]]*(Withdrawn|Superseded by)\b' "$spec"; then continue; fi
  # A VERDICT, not a MENTION (feature 156, 2026-08-29). The check used to be a bare `grep FAITHFUL`,
  # which two shapes satisfied without a review having passed: a spec whose only occurrence is "NOT
  # FAITHFUL" - i.e. one a reviewer REJECTED - and a spec whose prose merely discusses the word. So
  # the occurrence must survive dropping every negated line AND must sit on a line that names the
  # review it reports (a Status line, a round, a verdict, the agent). Still deliberately coarse: this
  # proves the RECORD exists, never that the review was good. Measured against all 56 specs in the
  # repository when it was written - 71 of 71 unchanged, and it is the guard's own "match INVOCATIONS
  # not mentions" rule finally applied to itself.
  # GUARD_EDIT_OK: feature 379 amendment 2 (the GM 2026-10-10: "things should go to the arbiter at the point where they were
  # previously coming to me") - past five rounds the round arbiter rules on a spec review, and its accept or process-fault
  # stands in for the FAITHFUL verdict (the ruling reaches the GM only as a kept for_gm question, feature 432); without this the ruling could not bind
  # only a ruling on the spec AS IT READS NOW (the ruling carries the spec's hash; plan review round 2): an amended spec is
  # never passed on an old ruling, whichever clone pushes it
  ruled=""
  python3 "$RG_HERE/../hooks/lib/hm_arbiter.py" spec-ruled "$(dirname "$spec")" 2>/dev/null && ruled=yes
  if [ -z "$ruled" ] && ! grep -E 'FAITHFUL' "$spec" | grep -viE 'NOT[[:space:]]+\**FAITHFUL' | grep -qiE 'status|verdict|round|spec-fidelity'; then
    printf '\n\033[1mREVIEW GATE: %s has no fidelity verdict.\033[0m\n' "$spec"
    printf 'Constitution XVI: a specification is reviewed against the GM'"'"'S OWN WORDS before\n'
    printf 'implementation, by someone other than its author. Run the `spec-fidelity` subagent in\n'
    printf 'Mode 2, give it the GM request VERBATIM (not the plan - a spec checked against its own\n'
    printf 'plan is tested for self-consistency, which a wrong spec passes), and record the verdict\n'
    printf 'in a "## Review history" section.\n'
    fail="$fail $spec"
  fi
done

# --- 2. every OWED review unit ships on its reviewer's VERDICT RECORD (feature 294) -------------------------
# GUARD_EDIT_OK: feature 294 - THE OCCASIONS REPLACE THE MOVED MANIFEST (GM 2026-10-01: the review checks run only when
# what they judge is new or changed; research R1 sorts every check). A push ships when every unit `review_owed.py` owes
# - `<check>:<subject>`, detected from the delta or declared in the feature's `## Occasions` - has a PASS or NEEDS-WORK
# record at the engine key being pushed (feature 240's record, per unit since this feature). A map that moved and owes
# nothing ships. The notes-file touch that stood in for a review on a never-reviewed map (2026-07-27) and the
# rendering-only waiver (feature 248) went with the manifest trigger. And a delta that touches drawing or placement code
# with no `## Occasions` section in any active feature is refused: whether a change is substantial is the feature's call
# to DECLARE, never to leave silent (the GM's tannery example).
undeclared="$(python3 "$RG_HERE/../reviews/review_owed.py" --root "$ROOT" --check-declared 2>/dev/null)"
if [ -n "$undeclared" ]; then
  printf '\n\033[1mREVIEW GATE: the delta does not declare its occasions.\033[0m\n'
  printf '%s\n' "$undeclared"
  fail="$fail occasions"; rules="$rules occasions-undeclared"
fi
owed_units="$(python3 "$RG_HERE/../reviews/review_owed.py" --root "$ROOT" --landing 2>/dev/null || true)"
# GUARD_EDIT_OK: feature 375 follow-up (2026-10-10) - A STALE RENDER IS NO OCCASION. A sheet's SVG is a gitignored render,
# and a clone never re-renders on a merge (GM 2026-07-22), so a render drawn before main moved read as an element "new to"
# its sheet: a spec-only push owed 374's glyph-check and size-audit on a corridor main no longer drew. Redraw what each owed
# unit sits on (`make map` answers CACHED when the render is current), then ask again.
if [ -n "$owed_units" ]; then
  for on in $(python3 "$RG_HERE/../reviews/review_owed.py" --root "$ROOT" --landing --units 2>/dev/null | awk -F'\t' '{print $4}' | sort -u); do
    g="$(find "$ROOT/pool" -path "*/$on/$on.gen.py" 2>/dev/null | head -1)"
    [ -n "$g" ] && ( cd "$ROOT" && make -s map GEN="${g#"$ROOT"/}" >/dev/null 2>&1 )
  done
  owed_units="$(python3 "$RG_HERE/../reviews/review_owed.py" --root "$ROOT" --landing 2>/dev/null || true)"
fi
if [ -n "$owed_units" ]; then
  tree_key="$( cd "$ROOT" 2>/dev/null && make -s engine-key REF=worktree 2>/dev/null | tr -d '[:space:]' )"
fi
for unit in $owed_units; do
  verdict_rec="$(git rev-parse --git-dir 2>/dev/null)/review-verdicts/$unit.json"
  if [ ! -f "$verdict_rec" ]; then
    printf '\n\033[1mREVIEW GATE: %s is owed and has no verdict record.\033[0m\n' "$unit"
    printf 'Its occasion: %s\n' "$(python3 "$RG_HERE/../reviews/review_owed.py" --root "$ROOT" --landing --units 2>/dev/null | awk -F'\t' -v u="$unit" '$1 == u {print $5}')"
    printf 'Dispatch it (`make verify` writes its prompt) once the gate is green; it records the verdict as its last act.\n'
    fail="$fail $unit"; rules="$rules unit-no-review"
    continue
  fi
  read -r verdict rec_key rec_content < <(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("verdict","") or "-", d.get("engine_key","") or "-", d.get("content_key","") or "-")' "$verdict_rec" 2>/dev/null || echo "- - -")
  # GUARD_EDIT_OK: feature 374 batch 4, the round arbiter's tooling fix - A VERDICT STALES ON ITS OWN SHEET: one value in one
  # generated program moved the whole-engine key and staled ten verdicts across sheets it never touched. A verdict whose sheet
  # (drawing and notes) hashes as it did when the review read it still answers for that sheet.
  now_content="$(python3 "$RG_HERE/../reviews/review_prereq.py" content-key --clone "$ROOT" --map "$unit" 2>/dev/null)"
  if [ "$verdict" = "NOT-REVIEWABLE" ]; then
    printf '\n\033[1mREVIEW GATE: %s was last returned NOT-REVIEWABLE.\033[0m\n' "$unit"
    printf 'Its reviewer stopped at the first stage - a prerequisite was missing, so no judgment was made.\n'
    printf 'Fix what that verdict names (%s) and dispatch the review again.\n' "$verdict_rec"
    fail="$fail $unit"; rules="$rules map-not-reviewable"
  elif [ -n "${tree_key:-}" ] && [ "$rec_key" = "$tree_key" ] && { [ "$verdict" = "PASS" ] || [ "$verdict" = "NEEDS-WORK" ]; }; then
    :   # the reviewer's record, at this content
  elif [ "$rec_content" != "-" ] && [ "$rec_content" = "$now_content" ] && { [ "$verdict" = "PASS" ] || [ "$verdict" = "NEEDS-WORK" ]; }; then
    :   # the engine moved, but this unit's sheet is what the reviewer read
  elif [ -n "$now_content" ] && ( cd "$ROOT" && python3 "$RG_HERE/../hooks/lib/hm_arbiter.py" unit-ruled "$unit" "$now_content" ) 2>/dev/null; then
    :   # GUARD_EDIT_OK: feature 374 batch 5 - the round arbiter ACCEPTED this unit on the sheet as it reads now: its ruling
        # stands for the verdict, as a spec review's does (an accepted sheet's last verdict was NEEDS-WORK at an older key)
  else
    printf '\n\033[1mREVIEW GATE: %s has a %s verdict at engine key %s, but the tree being pushed is %s.\033[0m\n' "$unit" "$verdict" "${rec_key:0:12}" "${tree_key:0:12}"
    printf 'The content moved again after that review: dispatch it again (`make verify`), within the two-round cap.\n'
    fail="$fail $unit"; rules="$rules map-stale-verdict"
  fi
done

# GUARD_EDIT_OK: feature 375 amendment 9, D55 - THE PUSH ASKS EVERY OWED UNIT (--landing above), the glyph units' hour aside; a
# glyph unit with no answer marks the work LANDING, so the dispatch this refusal asks for is due and passes the pair guard
# without GLYPH_DUE_OK - a clean push clears the mark (sync-with-main.sh)
case " $fail " in *" glyph-check--"*) python3 "$RG_HERE/../reviews/review_owed.py" --root "$ROOT" --landing-mark on >/dev/null 2>&1 ;; esac
if [ -n "$fail" ]; then
  printf '\n\033[1mreview-gate FAILED:%s\033[0m\n' "$fail"
  printf 'If a case is genuinely exempt - a superseded spec, a mechanical sweep across every map -\n'
  printf 'set REVIEW_GATE_OK="<reason>" so the reason ships with the push.\n\n'
  # GUARD_EDIT_OK: feature 168 - the rule names WHICH half refused: an unreviewed spec, an unreviewed
  # map, or both. GUARD_EDIT_OK: feature 248 - the map half names which of its three refusals fired.
  case "$fail" in
    *spec.md*)
      case "$rules" in
        *map-*|*unit-*|*occasions-*) guard_log review-gate blocked "$fail" spec-and-map ;;  # GUARD_EDIT_OK: feature 294 - the unit and occasions refusals are the map half
        *)      guard_log review-gate blocked "$fail" spec-no-verdict ;;
      esac ;;
    *)
      for rule in $(printf '%s\n' $rules | sort -u); do guard_log review-gate blocked "$fail" "$rule"; done ;;
  esac
  exit 1
fi
printf 'review-gate: clean\n'
