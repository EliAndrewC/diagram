#!/usr/bin/env bash
# Tests for review-gate.sh (constitution XVI, and the settlement-review mandate).
# Run: scripts/test-review-gate.sh   (exit 0 = all green)
#
# TWO DIRECTIONS (constitution XVIII). Section 2 carries the cases that must NOT block, and they
# matter more here than anywhere else in the repo: a shipping gate that fires on correct work stops a
# push at the END of a feature, when the session most wants it over with, which is exactly when a
# bypass gets reached for without much thought.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE="$HERE/review-gate.sh"
PASS=0; FAIL=0
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT

# The map fixture lives in its own folder, like every real map since feature 161.
POOL=".claude/skills/diagram/pool/hamlets/m"

# A repo whose `main` already holds $2 (the pre-existing state), then a `work` branch to change on.
mkrepo() {
  rm -rf "$T/$1"; mkdir -p "$T/$1/$POOL" "$T/$1/specs/900-x"; cd "$T/$1" || return 1
  git init -q .; git config user.email t@t; git config user.name t
  echo base > seed.txt
  [ "${2:-}" = withmap ] && { echo '{"v":1}' > "$POOL/m.json"; echo "notes" > "$POOL/m.notes.md"; }
  git add -A; git commit -qm base; git branch -q -M main; git checkout -q -b work
}

check() { # label repo expected
  local rc; ( cd "$T/$2" && "$GATE" main..HEAD >/dev/null 2>&1 ); rc=$?
  if { [ "$3" = ok ] && [ "$rc" -eq 0 ]; } || { [ "$3" = blocked ] && [ "$rc" -ne 0 ]; }; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else echo "  FAIL    $1 (expected $3, rc=$rc)"; FAIL=$((FAIL+1)); fi
}

echo "1. IT FIRES on work that skipped a mandated review"
# GUARD_EDIT_OK: feature 165 - these three fixtures now ship the spec ALONGSIDE another file, which is
# what shipping a spec means. Before the GM ruling they committed the spec ALONE, and that shape is
# now the NUMBER CLAIM and is exempt - so as written they would have been testing the exemption while
# claiming to test the requirement. The property they exist for is unchanged and still proved: a spec
# that travels with any other change carries a verdict or the push stops.
mkrepo a; echo "# spec" > specs/900-x/spec.md; echo work >> seed.txt; git add -A; git commit -qm s
check "a spec with no fidelity verdict" a blocked

mkrepo b withmap; echo '{"v":2}' > "$POOL/m.json"; git add -A; git commit -qm reroll
check "a re-rolled map with no review logged" b blocked

# The two shapes the bare `grep FAITHFUL` used to let through (feature 156, 2026-08-29). The first is
# the dangerous one: a spec a reviewer REJECTED shipped as if it had passed.
mkrepo b2; printf '# spec\n\n## Review history\n- **Round 1 (2026-08-29): NOT FAITHFUL.** FR-003 carved out a case.\n' > specs/900-x/spec.md
echo work >> seed.txt; git add -A; git commit -qm s
check "a spec whose only verdict is NOT FAITHFUL" b2 blocked

mkrepo b3; printf '# spec\n\nThe word FAITHFUL must never be written here by the author.\n' > specs/900-x/spec.md
echo work >> seed.txt; git add -A; git commit -qm s
check "a spec that merely MENTIONS the word in prose" b3 blocked

echo
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
prerepo() {  # a repo whose main already holds specs/900-x/spec.md with the given body
  rm -rf "$T/$1"; mkdir -p "$T/$1/specs/900-x"; cd "$T/$1" || return 1
  git init -q .; git config user.email t@t; git config user.name t
  echo base > seed.txt; printf '%s' "$2" > specs/900-x/spec.md
  git add -A; git commit -qm base; git branch -q -M main; git checkout -q -b work
}
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

mkrepo d withmap; echo '{"v":2}' > "$POOL/m.json"; echo "reviewed 2026-08-24" >> "$POOL/m.notes.md"
git add -A; git commit -qm reroll
check "a re-rolled map WITH its notes updated" d ok

mkrepo e; echo hi > seed2.txt; git add -A; git commit -qm doc
check "a change touching neither" e ok

mkrepo f withmap
# a map with no notes file at all predates the convention and must not be held to it
rm "$POOL/m.notes.md"; git add -A; git commit -qm drop-notes
git checkout -q main; git checkout -q work
echo '{"v":3}' > "$POOL/m.json"; git add -A; git commit -qm reroll
check "a map that has no notes file" f ok

mkrepo g; echo "# spec" > specs/900-x/spec.md; git add -A; git commit -qm s
if ( cd "$T/g" && REVIEW_GATE_OK="superseded before implementation" "$GATE" main..HEAD >/dev/null 2>&1 ); then
  echo "  ok      the documented escape"; PASS=$((PASS+1))
else echo "  FAIL    the escape did not work"; FAIL=$((FAIL+1)); fi

echo
echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
