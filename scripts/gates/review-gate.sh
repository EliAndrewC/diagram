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
  if ! "$RG_HERE/l7r-gate.sh" escape reason-ok <<<"$REVIEW_GATE_OK" >/dev/null; then
    guard_log review-gate blocked "$REVIEW_GATE_OK" REVIEW_GATE_OK-no-reason
    printf 'review-gate: REVIEW_GATE_OK needs a REASON, not just a value - two words and eight characters.\n' >&2
    printf 'It ships with the push and is what a later audit reads, so say what makes this case exempt.\n' >&2
    exit 1
  fi
  guard_log review-gate escaped "$REVIEW_GATE_OK" review-gate-ok
  # GUARD_EDIT_OK: feature 449 T232 - AN ESCAPE SKIPS THE REFUSAL, NEVER THE RECORD: it exited here, before the reviews set aside at
  # rust-only were recorded, so an escaped push dropped them for good once it landed. The gate now runs on and only its refusal is
  # skipped, below.
  escaped=1
fi
escaped="${escaped:-}"
bypassed() { printf 'review-gate: BYPASSED - %s\n' "$REVIEW_GATE_OK"; exit 0; }

changed=$(git diff --name-only "$RANGE" 2>/dev/null || true)
rules=""   # GUARD_EDIT_OK: feature 248 - the map half's refusals, each named for the firing log
[ -z "$changed" ] && { [ -n "$escaped" ] && bypassed; exit 0; }
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
  # A TRIAL RUNNING (feature 438; docs/spec-kit-and-reviews.md, "The trial form"): a brief with `**Form**: trial` is measured first and
  # reviewed ONCE, when its evidence is fixed - feature 437's spec took three rounds because it was reviewed while its evidence changed
  # beside it. So a trial not yet Done pushes its evidence with no verdict, while the push changes no engine code on net (a spike is
  # committed, measured and reverted); Done, or a push that changes l7r/, owes the verdict as any spec does.
  if grep -qE '^\*\*Form\*\*:?[[:space:]]*trial\b' "$spec" && ! grep -qiE '^\*\*Status\*\*:?[[:space:]]*Done\b' "$spec" \
     && git diff --quiet "$RANGE" -- l7r/ 2>/dev/null; then continue; fi
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
  # ONE READING OF THE VERDICT (feature 442): the FAITHFUL line and the arbiter's standing ruling, asked of `l7r-gate arbiter spec-verdict`,
  # the function the merge's feature-complete check (`rust/gate/crates/ci/src/ci/features.rs`) asks too - two readings drifted twice (features 387, 440)
  if ! "$RG_HERE/l7r-gate.sh" arbiter spec-verdict "$(dirname "$spec")" 2>/dev/null; then
    printf '\n\033[1mREVIEW GATE: %s has no fidelity verdict.\033[0m\n' "$spec"
    printf 'Constitution XVI: a specification is reviewed against the GM'"'"'S OWN WORDS before\n'
    printf 'implementation, by someone other than its author. Run the `spec-fidelity` subagent in\n'
    printf 'Mode 2, give it the GM request VERBATIM (not the plan - a spec checked against its own\n'
    printf 'plan is tested for self-consistency, which a wrong spec passes), and record the verdict\n'
    printf 'in a "## Review history" section.\n'
    if grep -qE '^\*\*Form\*\*:?[[:space:]]*trial\b' "$spec"; then
      printf 'A TRIAL (feature 438) pushes with no verdict only while it is not Done AND the push changes nothing under l7r/ on\n'
      printf 'net: revert a measured spike before pushing, or take the one review now (spec-fidelity, MODE 2, on the brief).\n'
    fi
    fail="$fail $spec"
  fi
done

# --- 2. every OWED review unit ships on its reviewer's VERDICT RECORD (feature 294) -------------------------
# GUARD_EDIT_OK: feature 294 - THE OCCASIONS REPLACE THE MOVED MANIFEST (GM 2026-10-01: the review checks run only when
# what they judge is new or changed; research R1 sorts every check). A push ships when every unit `l7r-gate reviews owed` owes
# - `<check>:<subject>`, detected from the delta or declared in the feature's `## Occasions` - has a PASS or NEEDS-WORK
# record at the engine key being pushed (feature 240's record, per unit since this feature). A map that moved and owes
# nothing ships. The notes-file touch that stood in for a review on a never-reviewed map (2026-07-27) and the
# rendering-only waiver (feature 248) went with the manifest trigger. And a delta that touches drawing or placement code
# is refused until a declaration answers it: whether a change is substantial is the feature's call to DECLARE, never to
# leave silent (the GM's tannery example). GUARD_EDIT_OK: feature 449 T238 round 2 - only a line of an active feature's
# `## Occasions` whose own task is the started one (`make task-start`; `- none: T238 - <why>`, `- <kind>: <subject> - T238:
# <why>`, or a trailing `(... T238)`), or a commit `Occasion:` line owing a review someone can run, answers it: any section
# did before - one whose lines had all landed, another task's or feature's - and passed undeclared placement code.
undeclared="$("$RG_HERE/l7r-gate.sh" reviews owed --root "$ROOT" --check-declared 2>/dev/null)"
if [ -n "$undeclared" ]; then
  printf '\n\033[1mREVIEW GATE: the delta does not declare its occasions.\033[0m\n'
  printf '%s\n' "$undeclared"
  fail="$fail occasions"; rules="$rules occasions-undeclared"
fi
# GUARD_EDIT_OK: feature 449 T231 - A DRAWING NOT CURRENT IS REDRAWN BEFORE THE ASK. A live hamlet's elements are its Rust drawing's
# census (T230), unknown while the generation cache does not serve that drawing as current, and a generated compound's are its `.svg`
# as last drawn: so a map edited and not redrawn owed nothing, and at integrated an edited hamlet shipped without the glyph-check its new
# element owes. `reviews owed --undrawn` names each such map (`<kind>\t<folder>`; nothing, one walk and a cache read, when nothing is
# stale) and each is drawn by `make map MAP=` before anything is asked. A draw that fails, or leaves the map still not current, refuses:
# what the reviews owe is not known. GUARD_EDIT_OK: feature 449 T232 - AT RUST-ONLY A HAMLET IS REDRAWN TOO (T231 skipped it: its units
# were set aside below, so the draw bought nothing - but an edited hamlet not redrawn owed no unit at all, so nothing was set aside and
# the push left nothing for the throw back to owe; measured in a scratch mirror 2026-11-19). The draw is the Rust driver's, a tenth of a
# second; what it owes is set aside and recorded below. A draw that fails, or leaves it not current, refuses nothing at rust-only (444
# FR-023): the hamlet is recorded with its elements at the base, and the throw back owes what it draws new since.
# (This replaces feature 375's redraw of what each owed unit sat on, after the ask: a stale render is a drawing not current, redrawn
# here; a hand sheet's legend is its own `.svg`, its spec, which no redraw changes.)
# A PUSH THAT TOUCHES NO ENGINE PATH REDRAWS NOTHING (449 T231): a fresh tree - land-tooling's worktree, a new clone - has drawn
# nothing, so every map reads not current, and a redraw there cost an engine's cold build and every compound drawn (every hamlet too at
# integrated) on a push that changes no drawing. The engine paths are the route's one list (`delta engine-paths`, `tree/delta.rs`
# `is_engine`), which holds every file a drawing is drawn from; what only the page reads (feature 188) changes no legend. A map left
# not current reads as a problem line, never as a legend, so nothing stale is owed or missed.
port=""
undrawn=""
if [ -n "$(printf '%s\n' "$changed" | "$RG_HERE/l7r-gate.sh" delta engine-paths 2>/dev/null)" ]; then
  undrawn="$("$RG_HERE/l7r-gate.sh" reviews owed --root "$ROOT" --undrawn 2>/dev/null)"
fi
unknown=()   # GUARD_EDIT_OK: feature 449 T232 - the hamlets whose units are not known at rust-only, recorded with the set-aside units
if [ -n "$undrawn" ]; then
  port="$(cd "$ROOT" && "$RG_HERE/l7r-gate.sh" cohort port 2>/dev/null || echo integrated)"
  redrawn=""
  while IFS=$'\t' read -r kind at; do
    [ -n "$at" ] || continue
    if drew="$(cd "$ROOT" && make -s map MAP="$at" </dev/null 2>&1)"; then
      redrawn="$redrawn $at"
    elif [ "$kind" = hamlet ] && [ "$port" = "rust-only" ]; then
      printf 'review-gate: %s did not draw (%s) - at rust-only that refuses nothing (444 FR-023); it is recorded, and the throw back owes what it draws new
' "$at" "$(printf '%s\n' "$drew" | tail -n 1)"
      unknown+=(--unknown "$at")
    else
      printf '\n\033[1mREVIEW GATE: %s is not drawn as it stands, and its redraw failed - the reviews it owes are not known.\033[0m\n' "$at"
      printf '%s\n' "$drew" | tail -n 8
      printf 'Fix what the draw names, then `make map MAP=%s` until it says REGENERATED or CACHED, and push again.\n' "$at"
      fail="$fail $at"; rules="$rules map-redraw-failed"
    fi
  done <<<"$undrawn"
  if [ -n "$redrawn" ]; then
    while IFS=$'\t' read -r kind at; do
      case " $redrawn " in *" $at "*) ;; *) continue ;; esac
      if [ "$kind" = hamlet ] && [ "$port" = "rust-only" ]; then
        printf 'review-gate: %s is still not current after its redraw - at rust-only that refuses nothing (444 FR-023); it is recorded\n' "$at"
        unknown+=(--unknown "$at"); continue
      fi
      printf '\n\033[1mREVIEW GATE: %s is still not current after `make map MAP=%s` drew it.\033[0m\n' "$at" "$at"
      printf 'The generation cache does not serve the drawing it just made, so the reviews it owes are not known. Run\n'
      printf '`make map MAP=%s` and read its REGENERATED line; drawn under another DIAGRAM_SKIP_RENDER than this push, draw it\n' "$at"
      printf 'under this one; else the cache'"'"'s currency check and its draw disagree (rust/gate/crates/pool/src/cache.rs).\n'
      fail="$fail $at"; rules="$rules map-redraw-not-current"
    done < <("$RG_HERE/l7r-gate.sh" reviews owed --root "$ROOT" --undrawn 2>/dev/null)
  fi
fi
# GUARD_EDIT_OK: feature 449 T238 round 2 (the plan review's D9) - A DECLARED ELEMENT ITS MAP DOES NOT DRAW IS REFUSED HERE, after the
# redraw: a glyph line naming an element the map's current drawing does not hold (`farmhous on m`) became a unit on no map that nobody
# can run. `--check-declared` above runs before the redraw and cannot tell a stale drawing from a wrong name; here each map's legend is
# its current drawing, and a map still not current is left as it was (the element may be new to it). And (D9c) a delta whose
# placement code only commit `Occasion:` lines naming such elements answered is refused here as undeclared: the line owes no unit,
# so the code would ship unreviewed. The redraw above builds the engine from this tree's sources (`make map`, measured 2026-11-20).
misdrawn="$("$RG_HERE/l7r-gate.sh" reviews owed --root "$ROOT" --check-drawn 2>/dev/null)"
if [ -n "$misdrawn" ]; then
  printf '\n\033[1mREVIEW GATE: a declaration names an element its map does not draw.\033[0m\n'
  printf '%s\n' "$misdrawn"
  fail="$fail occasions-drawn"; rules="$rules occasions-undrawn"
fi
owed_units="$("$RG_HERE/l7r-gate.sh" reviews owed --root "$ROOT" --landing 2>/dev/null || true)"
# AT RUST-ONLY A HAMLET'S MAP REVIEWS WAIT FOR THE THROW BACK (feature 444 FR-023; the GM 2026-11-07: "You should immediately stop
# running all of the python map generating code as well"): no hamlet map is rolled through the Python stages while the port switch
# stands at rust-only (`make map` rolled Inashiro and Kashikawa through them in a landing's cheap refusals), so a review of one is not
# refused; it is owed again when the switch is thrown back to integrated. Every other unit is asked as before.
# GUARD_EDIT_OK: feature 449 T221 - `make map` runs the Rust hamlet driver now (a tenth of a second, no Python); T231 - a hamlet not
# current is redrawn above at integrated, and at rust-only is not, its units set aside here
# GUARD_EDIT_OK: feature 449 T232 - the port asked once wherever a unit or an unknown hamlet may be set aside or a deferred one cleared
[ -n "$port" ] || port="$(cd "$ROOT" && "$RG_HERE/l7r-gate.sh" cohort port 2>/dev/null || echo integrated)"
# GUARD_EDIT_OK: feature 449 T232 - WHAT IS SET ASIDE IS RECORDED, AND THE RECORD SHIPS WITH THE PUSH: the gate runs before the push,
# and the push lands HEAD, so the record is committed here (as `make land` commits its escape records, feature 408)
record_commit() {
  [ -n "$(git status --porcelain -- dev/deferred-reviews.jsonl 2>/dev/null)" ] || return 0
  git add -- dev/deferred-reviews.jsonl && git commit -q -m "$1" -- dev/deferred-reviews.jsonl \
    && printf 'review-gate: dev/deferred-reviews.jsonl committed - %s\n' "$1"
}
# GUARD_EDIT_OK: feature 449 T233 - AT RUST-ONLY EVERY PUSH RECORDS THE HAMLETS THE PORT MOVED (444 FR-019: "its moved pool hamlets
# owing their settlement-reviews"): a hamlet already in the pool owes no settlement-review the delta detects, so a Rust stage that moved
# one set nothing aside and the throw back owed nothing (measured 2026-11-19 in scratch: "review-gate: clean"); `--moved` keeps a row
# open for each live hamlet, written once (one pool walk when nothing is new)
if [ "$port" = "rust-only" ]; then
  kept=""; aside=()
  for unit in $owed_units; do
    # GUARD_EDIT_OK: feature 449 T220 - a hamlet is what the one pool walk classifies as one (its spec), not a folder name's tier
    if [ "$("$RG_HERE/l7r-gate.sh" pool find "${unit##*--}" 2>/dev/null | cut -f1)" = hamlet ]; then
      printf 'review-gate: %s waits for the port switch thrown back to integrated (FR-023), recorded in dev/deferred-reviews.jsonl\n' "$unit"
      aside+=("$unit")
    else
      kept="$kept $unit"
    fi
  done
  owed_units="${kept# }"
  # GUARD_EDIT_OK: feature 449 T232 - the units set aside and the hamlets not known, recorded until the throw back owes them
  if ! "$RG_HERE/l7r-gate.sh" reviews deferred set-aside --root "$ROOT" --utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --moved "${unknown[@]}" "${aside[@]}"; then
    printf '\n\033[1mREVIEW GATE: the reviews set aside at rust-only could not be recorded.\033[0m\n'
    printf 'Without the record they are owed by nothing once this push lands (449 T232): fix what the line above names and push again.\n'
    fail="$fail deferred-record"; rules="$rules deferred-not-recorded"
  fi
  record_commit "the review gate's set-aside hamlet reviews (444 FR-023, 449 T232)" || { fail="$fail deferred-record"; rules="$rules deferred-not-recorded"; }
fi
if [ -n "$owed_units" ]; then
  tree_key="$( cd "$ROOT" 2>/dev/null && make -s engine-key REF=worktree 2>/dev/null | tr -d '[:space:]' )"
fi
passed=()   # GUARD_EDIT_OK: feature 449 T232 - the units whose review stands, so a deferred one is recorded reviewed on main
for unit in $owed_units; do
  verdict_rec="$(git rev-parse --git-dir 2>/dev/null)/review-verdicts/$unit.json"
  if [ ! -f "$verdict_rec" ]; then
    printf '\n\033[1mREVIEW GATE: %s is owed and has no verdict record.\033[0m\n' "$unit"
    printf 'Its occasion: %s\n' "$("$RG_HERE/l7r-gate.sh" reviews owed --root "$ROOT" --landing --units 2>/dev/null | awk -F'\t' -v u="$unit" '$1 == u {print $5}')"
    printf 'Dispatch it (`make verify` writes its prompt) once the gate is green; it records the verdict as its last act.\n'
    fail="$fail $unit"; rules="$rules unit-no-review"
    continue
  fi
  read -r verdict rec_key rec_content < <("$RG_HERE/l7r-gate.sh" json-field "$verdict_rec" verdict engine_key content_key 2>/dev/null || echo "- - -")
  # GUARD_EDIT_OK: feature 374 batch 4, the round arbiter's tooling fix - A VERDICT STALES ON ITS OWN SHEET: one value in one
  # generated program moved the whole-engine key and staled ten verdicts across sheets it never touched. A verdict whose sheet
  # (drawing and notes) hashes as it did when the review read it still answers for that sheet.
  now_content="$("$RG_HERE/l7r-gate.sh" reviews prereq content-key --clone "$ROOT" --map "$unit" 2>/dev/null)"
  if [ "$verdict" = "NOT-REVIEWABLE" ]; then
    printf '\n\033[1mREVIEW GATE: %s was last returned NOT-REVIEWABLE.\033[0m\n' "$unit"
    printf 'Its reviewer stopped at the first stage - a prerequisite was missing, so no judgment was made.\n'
    printf 'Fix what that verdict names (%s) and dispatch the review again.\n' "$verdict_rec"
    fail="$fail $unit"; rules="$rules map-not-reviewable"
  elif [ -n "${tree_key:-}" ] && [ "$rec_key" = "$tree_key" ] && { [ "$verdict" = "PASS" ] || [ "$verdict" = "NEEDS-WORK" ]; }; then
    passed+=("$unit")   # the reviewer's record, at this content
  elif [ "$rec_content" != "-" ] && "$RG_HERE/l7r-gate.sh" reviews prereq answered --clone "$ROOT" --unit "$unit" --key "" 2>/dev/null; then
    # GUARD_EDIT_OK: feature 451 T199 - the content-key compare is the prereq reader's `carried`, one copy of the rule: the sheet is
    # what the reviewer read, or moved only by an edit a clean change-scoped round judged (`make review-fixed`, a nitpick fixed)
    passed+=("$unit")   # the engine moved, but this unit's sheet is what the reviewer read
  elif [ -n "$now_content" ] && ( cd "$ROOT" && "$RG_HERE/l7r-gate.sh" arbiter unit-ruled "$unit" "$now_content" ) 2>/dev/null; then
    passed+=("$unit")   # GUARD_EDIT_OK: feature 374 batch 5 - the round arbiter ACCEPTED this unit on the sheet as it reads now: its ruling
        # stands for the verdict, as a spec review's does (an accepted sheet's last verdict was NEEDS-WORK at an older key)
  else
    printf '\n\033[1mREVIEW GATE: %s has a %s verdict at engine key %s, but the tree being pushed is %s.\033[0m\n' "$unit" "$verdict" "${rec_key:0:12}" "${tree_key:0:12}"
    printf 'The content moved again after that review: dispatch it again (`make verify`), within the two-round cap.\n'
    fail="$fail $unit"; rules="$rules map-stale-verdict"
  fi
done

# GUARD_EDIT_OK: feature 449 T232 - A SET-ASIDE UNIT'S REVIEW IS RECORDED ON MAIN: the verdict files are each clone's own, so the record
# says it was reviewed, in the push, and no other clone owes it again; `reviews deferred reviewed` writes only the record's open units.
# Only on a push that ships: a review cleared on a refused one would stand for a hamlet edited again before it lands
if [ -z "$fail" ] && [ "$port" != "rust-only" ] && [ "${#passed[@]}" -gt 0 ] && [ -f "$ROOT/dev/deferred-reviews.jsonl" ]; then
  "$RG_HERE/l7r-gate.sh" reviews deferred reviewed --root "$ROOT" --utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${passed[@]}" || true
  record_commit "the review gate's reviewed set-aside hamlet reviews (444 FR-023, 449 T232)" || true
fi

# GUARD_EDIT_OK: feature 449 T232 - the escape's one effect: no refusal (and no landing mark), once everything is recorded
[ -n "$escaped" ] && bypassed

# GUARD_EDIT_OK: feature 375 amendment 9, D55 - THE PUSH ASKS EVERY OWED UNIT (--landing above), the glyph units' hour aside; a
# glyph unit with no answer marks the work LANDING, so the dispatch this refusal asks for is due and passes the pair guard
# without GLYPH_DUE_OK - a clean push clears the mark (sync-with-main.sh)
case " $fail " in *" glyph-check--"*) "$RG_HERE/l7r-gate.sh" reviews owed --root "$ROOT" --landing-mark on >/dev/null 2>&1 ;; esac
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
