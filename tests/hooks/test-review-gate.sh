#!/usr/bin/env bash
# Tests for review-gate.sh (constitution XVI, and the settlement-review mandate).
# Run: tests/hooks/test-review-gate.sh   (exit 0 = all green)
#
# TWO DIRECTIONS (constitution XVIII). Section 2 carries the cases that must NOT block, and they
# matter more here than anywhere else in the repo: a shipping gate that fires on correct work stops a
# push at the END of a feature, when the session most wants it over with, which is exactly when a
# bypass gets reached for without much thought.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE="$HERE/../../scripts/gates/review-gate.sh"
PASS=0; FAIL=0
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
# GUARD_EDIT_OK: feature 169 - review-gate.sh records since 168, and this suite was the one that got
# missed, because it is not a `*-hooks.sh` file and the isolation was added to nine suites by hand.
# Measured cost: 24 of the live census's 113 entries were this file's `specs/900-x` fixtures, in the
# census that is the input to every future tuning decision. Hangs off $T so the trap above cleans it.
export GUARD_LOG_DIR="$T/guard-log"

# The map fixture lives in its own folder, like every real map since feature 161.
POOL="pool/hamlets/m"

# A repo whose `main` already holds $2 (the pre-existing state), then a `work` branch to change on.
mkrepo() {
  rm -rf "$T/$1"; mkdir -p "$T/$1/$POOL" "$T/$1/specs/900-x" "$T/$1"; cd "$T/$1" || return 1
  git init -q .; git config user.email t@t; git config user.name t
  echo base > seed.txt
  # GUARD_EDIT_OK: feature 248 - the gate reads the pushed tree's ENGINE KEY (a stub target, never the engine) and
  # asks review_owed.py, which needs an origin/main to diff against; both are fixture state, like the map itself
  printf 'engine-key:\n\t@printf k\n' > Makefile
  # GUARD_EDIT_OK: feature 294 - the map carries its ink census, the record the occasions are read from
  [ "${2:-}" = withmap ] && { echo '{"v":1,"ink_classes":{"farmhouse":1}}' > "$POOL/m.json"; echo "notes" > "$POOL/m.notes.md"; }
  git add -A; git commit -qm base; git branch -q -M main; git checkout -q -b work
  git update-ref refs/remotes/origin/main main
}

check() { # label repo expected
  local rc; ( cd "$T/$2" && "$GATE" main..HEAD >/dev/null 2>&1 ); rc=$?
  if { [ "$3" = ok ] && [ "$rc" -eq 0 ]; } || { [ "$3" = blocked ] && [ "$rc" -ne 0 ]; }; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else echo "  FAIL    $1 (expected $3, rc=$rc)"; FAIL=$((FAIL+1)); fi
}

ruling() { printf '{"trigger": "round:spec-fidelity|900-x#1@6", "kind": "round", "ruling": "%s", "why": "w", "utc": "t", "spec_sha": "%s"}\n' "$1" "${2:-$SHA}" > specs/900-x/arbiter.jsonl; }
prerepo() {  # a repo whose main already holds specs/900-x/spec.md with the given body
  rm -rf "$T/$1"; mkdir -p "$T/$1/specs/900-x"; cd "$T/$1" || return 1
  git init -q .; git config user.email t@t; git config user.name t
  echo base > seed.txt; printf '%s' "$2" > specs/900-x/spec.md
  git add -A; git commit -qm base; git branch -q -M main; git checkout -q -b work
}

NEW='{"v":2,"ink_classes":{"farmhouse":1,"well":1}}'  # a constant the cases share, defined before them (383 amendment 4)
case_1() {
echo "1. IT FIRES on work that skipped a mandated review"
# GUARD_EDIT_OK: feature 165 - these three fixtures now ship the spec ALONGSIDE another file, which is
# what shipping a spec means. Before the GM ruling they committed the spec ALONE, and that shape is
# now the NUMBER CLAIM and is exempt - so as written they would have been testing the exemption while
# claiming to test the requirement. The property they exist for is unchanged and still proved: a spec
# that travels with any other change carries a verdict or the push stops.
mkrepo a; echo "# spec" > specs/900-x/spec.md; echo work >> seed.txt; git add -A; git commit -qm s
check "a spec with no fidelity verdict" a blocked

# GUARD_EDIT_OK: feature 294 - the occasion is an element new to the map, not a moved manifest
mkrepo b withmap; echo "$NEW" > "$POOL/m.json"; git add -A; git commit -qm reroll
check "a map gaining an element with no review recorded" b blocked
# GUARD_EDIT_OK: feature 375 amendment 9, D55 - the push asks every owed unit (--landing), the glyph units' hour aside, and a glyph
# unit with no answer marks the work LANDING, so the dispatch the refusal asks for is due and passes the pair guard
if [ -f "$T/b/.git/glyph-landing" ]; then echo "  ok      ...and marks the work landing, so its glyph dispatch is due (375 amendment 9)"; PASS=$((PASS+1))
else echo "  FAIL    the refused push did not mark the work landing"; FAIL=$((FAIL+1)); fi

# GUARD_EDIT_OK: feature 375 follow-up (2026-10-10) - a render older than main's reads as a new element; the gate redraws
# what an owed unit sits on (the stub `map` puts main's census back, as a real redraw did for 374's corridor) and asks again
mkrepo b1 withmap; git checkout -q main; echo "# gen" > "$POOL/m.gen.py"
printf 'map:\n\t@printf %%s %s > %s\n' "'{\"v\":1,\"ink_classes\":{\"farmhouse\":1}}'" "$POOL/m.json" >> Makefile
git add -A; git commit -qm gen; git update-ref refs/remotes/origin/main main; git checkout -q -b stale
echo work >> seed.txt; git add -A; git commit -qm work; echo "$NEW" > "$POOL/m.json"
check "a stale render that its redraw clears owes nothing" b1 ok

# The two shapes the bare `grep FAITHFUL` used to let through (feature 156, 2026-08-29). The first is
# the dangerous one: a spec a reviewer REJECTED shipped as if it had passed.
mkrepo b2; printf '# spec\n\n## Review history\n- **Round 1 (2026-08-29): NOT FAITHFUL.** FR-003 carved out a case.\n' > specs/900-x/spec.md
echo work >> seed.txt; git add -A; git commit -qm s
check "a spec whose only verdict is NOT FAITHFUL" b2 blocked

mkrepo b3; printf '# spec\n\nThe word FAITHFUL must never be written here by the author.\n' > specs/900-x/spec.md
echo work >> seed.txt; git add -A; git commit -qm s
check "a spec that merely MENTIONS the word in prose" b3 blocked

# GUARD_EDIT_OK: feature 379 amendment 2 - the round arbiter's accept on the spec's review stands in for FAITHFUL
# the ruling carries the spec's hash (hm_arbiter.spec_body_sha): it stands only while the spec reads as it was ruled on
SHA=$(printf '# spec' | sha256sum | cut -d' ' -f1)   # the title and the sections; the header block is not hashed
mkrepo b4; printf '# spec\n\n**Status**: In progress\n\n## Review history\n- round 5: CHANGES REQUIRED\n' > specs/900-x/spec.md; ruling accept
echo work >> seed.txt; git add -A; git commit -qm s
check "a spec the round arbiter accepted past the cap ships" b4 ok
printf '# spec\n\n**Status**: Done 2026-10-10 - landed\n\n## Review history\n- round 5: CHANGES REQUIRED\n' > specs/900-x/spec.md; git add -A; git commit -qm done
check "...and still ships once its Status line says Done (a header line is no amendment)" b4 ok
printf '# spec\n\n**Status**: Done 2026-10-10 - landed: spec FAITHFUL, plan CLEAR, every task ticked; the gate green\n  and the report written\n\n## Review history\n- round 5: CHANGES REQUIRED\n' > specs/900-x/spec.md; git add -A; git commit -qm wrapped
check "...or a Status line wrapped onto two lines (plan review round 4)" b4 ok
mkrepo b5; printf '# spec\n\n## Review history\n- round 5: CHANGES REQUIRED\n' > specs/900-x/spec.md; ruling continue
echo work >> seed.txt; git add -A; git commit -qm s
check "...but a continue ruling is no verdict" b5 blocked
mkrepo b6; printf '# spec\n\n**Status**: In progress\n\n## Review history\n- round 5: CHANGES REQUIRED\n' > specs/900-x/spec.md; ruling process-fault
echo work >> seed.txt; git add -A; git commit -qm s
check "...a process-fault ruling stands in too" b6 ok
printf '# spec, amended\n\n## Review history\n- round 5: CHANGES REQUIRED\n- the ruling\n' > specs/900-x/spec.md; git add -A; git commit -qm amend
check "...but not for the spec once it is amended, whichever clone pushes it" b6 blocked

# feature 330: a FILED spec (status Filed, no tasks.md) is deferred work, not an implementation - it ships with other
# files and no verdict; the same spec given a tasks.md is being implemented and owes its verdict again
mkrepo f1; printf '# Feature Specification: x\n\n**Status**: Filed - from the backlog, 2026-10-08\n' > specs/900-x/spec.md
echo work >> seed.txt; git add -A; git commit -qm filed
check "a FILED spec with no tasks, alongside other work: no verdict owed" f1 ok
mkrepo f2; printf '# Feature Specification: x\n\n**Status**: Filed - from the backlog, 2026-10-08\n' > specs/900-x/spec.md
printf -- '- [ ] T01 build it\n' > specs/900-x/tasks.md; echo work >> seed.txt; git add -A; git commit -qm filed-with-tasks
check "...the same spec given tasks: the verdict is owed" f2 blocked
# the GM 2026-10-10: withdrawing a filed spec (no tasks.md) owes no verdict; a planned one withdrawn still does
mkrepo f3; printf '# Feature Specification: x\n\n**Status**: Withdrawn (the GM, 2026-10-10) - nothing to review. Was: Filed\n' > specs/900-x/spec.md
echo work >> seed.txt; git add -A; git commit -qm withdrawn
check "a WITHDRAWN spec with no tasks: no verdict owed" f3 ok
mkrepo f4; printf '# Feature Specification: x\n\n**Status**: Superseded by 901\n' > specs/900-x/spec.md
printf -- '- [ ] T01 build it\n' > specs/900-x/tasks.md; echo work >> seed.txt; git add -A; git commit -qm superseded-with-tasks
check "...a superseded spec that HAD tasks: the verdict is owed" f4 blocked

echo
}

case_1b() {
echo "1b. THE NUMBER CLAIM passes, and only the number claim (feature 165, the GM ruling)"
# CLAUDE.md requires the number to be claimed by pushing the new specs/NNN-slug/ the moment spec.md
# exists, because several sessions allocate numbers at once - and this gate refused exactly that push
# for lacking a verdict a one-minute-old spec cannot carry. Measured cost on 2026-08-30: one session
# lost 161 to a peer mid-review, renumbered to 162, then lost 163 the same way; the second renumber
# swept 67 files, 51 of them wrongly.
mkrepo n1; mkdir -p specs/901-new; printf '# a spec written one minute ago\n' > specs/901-new/spec.md
printf 'the GM said so\n' > specs/901-new/request.md; git add -A; git commit -qm claim
check "one new spec directory, no verdict: the claim passes" n1 ok

mkrepo n2; mkdir -p specs/901-new; printf '# spec\n' > specs/901-new/spec.md
echo work >> seed.txt; git add -A; git commit -qm claim-plus
check "...plus one file elsewhere: refused" n2 blocked

mkrepo n3; mkdir -p specs/901-new specs/902-other
printf '# spec\n' > specs/901-new/spec.md; printf '# spec\n' > specs/902-other/spec.md
git add -A; git commit -qm two-claims
check "...two new spec directories at once: refused" n3 blocked

# THE SPEC HAS TO PRE-EXIST IN MAIN for these two, and `mkrepo` cannot do that - it commits base
# before the spec is written, so a spec added on `work` is an ADDITION over main..HEAD, which IS the
# claim shape. The first draft of these two fixtures made exactly that mistake and passed for the
# wrong reason. Built by hand instead, with the spec in the BASE commit.
prerepo n4 '# spec

## Review history
Round 1 - FAITHFUL
'
printf '# spec\n\nthe verdict is gone\n' > specs/900-x/spec.md; git add -A; git commit -qm strip
check "...a MODIFIED existing spec losing its verdict: refused" n4 blocked

prerepo n5 '# a spec claimed earlier, still unreviewed
'
printf 'tasks\n' > specs/900-x/tasks.md; git add -A; git commit -qm implement
check "...and a LATER push into that directory still owes the verdict" n5 blocked

echo
}

case_2() {
echo "2. IT STAYS QUIET on work that did the reviews"
mkrepo c; printf '# spec\n\n## Review history\nRound 1 - FAITHFUL\n' > specs/900-x/spec.md
git add -A; git commit -qm s
check "a spec carrying a FAITHFUL verdict" c ok

# The house's real shapes, taken verbatim from specs 127, 142 and 132 - a tightened check that fired
# on any of these would stop a push at the end of a feature, which section 2 exists to prevent.
mkrepo c2; printf '# spec\n\n**Status**: APPROVED by `spec-fidelity` (round 3, verdict FAITHFUL) - ready to implement\n' > specs/900-x/spec.md
git add -A; git commit -qm s
check "the Status-line form" c2 ok

mkrepo c3; printf '# spec\n\n- **2026-08-28, spec-fidelity round 2**: **FAITHFUL** - every clause carried.\n' > specs/900-x/spec.md
git add -A; git commit -qm s
check "the dated round-history form" c3 ok

# A spec that was rejected and then passed keeps both lines; the pass must still count.
mkrepo c4; printf '# spec\n\n- **Round 1: NOT FAITHFUL.** FR-010 was an enumeration.\n- **Round 3 (2026-08-25): FAITHFUL.** Nothing missing, nothing added.\n' > specs/900-x/spec.md
git add -A; git commit -qm s
check "a rejection followed by a pass" c4 ok

mkrepo d withmap; echo '{"v":2,"ink_classes":{"farmhouse":1}}' > "$POOL/m.json"; echo "reviewed 2026-08-24" >> "$POOL/m.notes.md"
git add -A; git commit -qm reroll
check "a re-rolled map with nothing new drawn owes no review (feature 294, SC-001 at push)" d ok

mkrepo e; echo hi > seed2.txt; git add -A; git commit -qm doc
check "a change touching neither" e ok

mkrepo f withmap
# a map with no notes file at all predates the convention and must not be held to it
rm "$POOL/m.notes.md"; git add -A; git commit -qm drop-notes
git checkout -q main; git checkout -q work
echo '{"v":3,"ink_classes":{"farmhouse":1}}' > "$POOL/m.json"; git add -A; git commit -qm reroll
check "a map that has no notes file" f ok

# GUARD_EDIT_OK: feature 240 FR-002 - a notes file touched is not a review that happened: a map whose latest
# verdict record is NOT-REVIEWABLE is refused even with its notes updated, and a PASS lets it through.
mkrepo nr withmap; echo "$NEW" > "$POOL/m.json"; echo "reviewed 2026-09-13" >> "$POOL/m.notes.md"
git add -A; git commit -qm reroll-with-notes; mkdir -p .git/review-verdicts
echo '{"map":"glyph-check--well--m","engine_key":"k","verdict":"NOT-REVIEWABLE","findings":[]}' > .git/review-verdicts/glyph-check--well--m.json
check "an owed unit whose last verdict is NOT-REVIEWABLE, notes updated or not" nr blocked
echo '{"map":"glyph-check--well--m","engine_key":"k","verdict":"PASS","findings":[]}' > "$T/nr/.git/review-verdicts/glyph-check--well--m.json"
check "...and the same map once a review returned PASS" nr ok

# GUARD_EDIT_OK: feature 248 FR-006 (GM 2026-09-14) - THE REVIEWER'S RECORD IS THE ONE RECORD. Three passes and three
# refusals: a PASS/NEEDS-WORK record at the pushed tree's key ships with NO notes touch; the rendering-only waiver ships
# a map with no record and no notes touch; a map with no record at all still ships on the notes touch; a record at a
# STALE key refuses whether or not the notes are touched (D5); a NOT-REVIEWABLE record refuses (above); no record and
# no notes touch refuses (case b above).
echo
}

case_3() {
echo "3. A MAP SHIPS ON ITS REVIEWER'S RECORD (feature 248)"
V=.git/review-verdicts/glyph-check--well--m.json
mkrepo r1 withmap; echo "$NEW" > "$POOL/m.json"; git add -A; git commit -qm reroll; mkdir -p .git/review-verdicts
echo '{"map":"glyph-check--well--m","engine_key":"k","verdict":"PASS","findings":[]}' > "$V"
check "a PASS record at this engine key, no notes touch" r1 ok
echo '{"map":"glyph-check--well--m","engine_key":"k","verdict":"NEEDS-WORK","findings":[{"id":"F1"}]}' > "$T/r1/$V"
check "...a NEEDS-WORK record at this key too (the findings are fixed under the same key)" r1 ok
echo '{"map":"glyph-check--well--m","engine_key":"stale","verdict":"PASS","findings":[]}' > "$T/r1/$V"
check "a PASS record at ANOTHER key, no notes touch: refused" r1 blocked
# GUARD_EDIT_OK: feature 374 batch 4, the round arbiter's tooling fix - a verdict stales on ITS sheet, not on the engine's key:
# a record at another engine key whose content key matches the sheet now ships; the sheet's notes changed, it is refused again
CK="$(cd "$T/r1" && python3 "$HERE/../../scripts/reviews/review_prereq.py" content-key --clone "$T/r1" --map glyph-check--well--m)"
echo "{\"map\":\"glyph-check--well--m\",\"engine_key\":\"stale\",\"content_key\":\"$CK\",\"verdict\":\"PASS\",\"findings\":[]}" > "$T/r1/$V"
check "a PASS record at another engine key whose sheet is unchanged ships" r1 ok
( cd "$T/r1" && echo "a later line" >> "$POOL/m.notes.md" && git add -A && git commit -qm notes )
check "...and once the sheet's notes change, it is refused" r1 blocked
# GUARD_EDIT_OK: feature 374 batch 5 - the round arbiter's ACCEPT on a unit stands for its verdict while the sheet reads as ruled
CK2="$(cd "$T/r1" && python3 "$HERE/../../scripts/reviews/review_prereq.py" content-key --clone "$T/r1" --map glyph-check--well--m)"
( cd "$T/r1" && mkdir -p .specify specs/902-a && echo '{"feature_directory":"specs/902-a"}' > .specify/feature.json \
  && echo "{\"trigger\":\"round:glyph-check|glyph-check--well--m@3\",\"unit\":\"glyph-check--well--m\",\"ruling\":\"accept\",\"why\":\"fixed\",\"content_key\":\"$CK2\"}" > specs/902-a/arbiter.jsonl \
  && git add -A && git commit -qm ruled )
echo '{"map":"glyph-check--well--m","engine_key":"stale","verdict":"NEEDS-WORK","findings":[{"id":"E1"}]}' > "$T/r1/$V"
check "a NEEDS-WORK record at another key ships on the arbiter's accept of the sheet as it reads" r1 ok
( cd "$T/r1" && echo "another line" >> "$POOL/m.notes.md" && git add -A && git commit -qm notes2 )
check "...and once the sheet changes after the ruling, it is refused" r1 blocked
mkrepo r2 withmap; echo "$NEW" > "$POOL/m.json"; echo "reviewed 2026-09-14" >> "$POOL/m.notes.md"; git add -A; git commit -qm reroll
mkdir -p .git/review-verdicts; echo '{"map":"glyph-check--well--m","engine_key":"stale","verdict":"PASS","findings":[]}' > "$V"
check "...and a stale-key record with the notes touched is refused too (D5: no substitute on a map with a record)" r2 blocked
# GUARD_EDIT_OK: feature 294 D2 - the rendering waiver is gone; drawing or placement code that moved must DECLARE its occasions
mkrepo r3 withmap; mkdir -p .specify specs/901-r l7r
echo 'X = 1' > l7r/placer.py
printf -- '- [x] T01 the placer\n      research: rendering\n' > specs/901-r/tasks.md
echo '{"feature_directory":"specs/901-r"}' > .specify/feature.json; git add -A; git commit -qm placer
check "placement code moved with no Occasions section in the active feature: refused" r3 blocked
printf -- '## Occasions\n\n- none: a refactor, every element placed under rules already judged\n\n- [x] T01 the placer\n      research: rendering\n' > "$T/r3/specs/901-r/tasks.md"
( cd "$T/r3" && git add -A && git commit -qm declared )
check "...and shipped once the feature declares its occasions" r3 ok
printf -- '## Occasions\n\n- placement-changed: farmhouse\n\n- [x] T01 the placer\n      research: rendering\n' > "$T/r3/specs/901-r/tasks.md"
( cd "$T/r3" && git add -A && git commit -qm re-placed )
check "...but a declared re-placement owes its glyph check (the GM's tannery)" r3 blocked

mkrepo g; echo "# spec" > specs/900-x/spec.md; git add -A; git commit -qm s
if ( cd "$T/g" && REVIEW_GATE_OK="superseded before implementation" "$GATE" main..HEAD >/dev/null 2>&1 ); then
  echo "  ok      the documented escape"; PASS=$((PASS+1))
else echo "  FAIL    the escape did not work"; FAIL=$((FAIL+1)); fi

# GUARD_EDIT_OK: 2026-09-26 - ANOTHER SESSION'S PUSH IS NOT THIS CLONE'S CHANGE. The default range was two-dot, a tree
# diff, and the gate runs before the pull: a map another session pushed after this clone synced read as ours.
mkrepo mv withmap; echo tool > tool.sh; git add -A; git commit -qm tooling
git checkout -q main; echo '{"v":2}' > "$POOL/m.json"; git commit -qam "another session's map"; git update-ref refs/remotes/origin/main main; git checkout -q work
if ( cd "$T/mv" && "$GATE" >/dev/null 2>&1 ); then
  echo "  ok      main moved on a map after this clone synced: the default range does not charge it here"; PASS=$((PASS+1))
else echo "  FAIL    another session's map change was charged to this clone"; FAIL=$((FAIL+1)); fi

}

# GUARD_EDIT_OK: feature 383 amendment 4 (plan D28) - the sections as cases, run in parallel parts (tests/hooks/parts.sh)
CASES=(case_1 case_1b case_2 case_3)
declare -A WEIGHT=()
# shellcheck source=/dev/null
source "$HERE/parts.sh"
run_parts ${REVIEWGATE_PARTS:-4}

echo
echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
