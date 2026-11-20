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
  # asks `l7r-gate reviews owed` (449 T89), which needs an origin/main to diff against; both are fixture state, like the map itself
  printf 'engine-key:\n\t@printf k\n' > Makefile
  # GUARD_EDIT_OK: feature 294 - the map carries its ink census, the record the occasions are read from
  # GUARD_EDIT_OK: feature 449 T220 - the spec makes the folder a hamlet to the one pool walk; a manifest alone is no map in the live pool
  [ "${2:-}" = withmap ] && { echo '{}' > "$POOL/m.spec.json"; echo '{"v":1,"ink_classes":{"farmhouse":1}}' > "$POOL/m.json"; echo "notes" > "$POOL/m.notes.md"; }
  # GUARD_EDIT_OK: feature 444 FR-023 - the cases below are the integrated port's; case_4 throws the switch to rust-only
  mkdir -p dev; echo '{"port": {"state": "integrated"}}' > dev/switches.json
  # GUARD_EDIT_OK: feature 449 T230 - the map drawn as the base holds it, so a case that owes nothing reads a current drawing
  [ "${2:-}" = withmap ] && drawn '{"v":1,"ink_classes":{"farmhouse":1}}'
  git add -A; git commit -qm base; git branch -q -M main; git checkout -q -b work
  git update-ref refs/remotes/origin/main main
}

# GUARD_EDIT_OK: feature 449 T230 - a live hamlet's elements are its Rust drawing's ink census (`m.driver.json`), read only where the
# generation cache serves that drawing as current: `drawn '<census>'` writes it, a stand-in engine the fixture's stub launcher names,
# and the cache entry (its engine id the stand-in's hash, its spec's stat and digest), as test-pair-hooks.sh's `cached` does; the
# base's census, with no mirror beside the fixture, is its tracked `m.json`
drawn() {
  mkdir -p scripts/gates; printf 'stand-in hamlet engine\n' > .git/stand-in-hamlet
  printf '#!/bin/sh\n[ "$1" = hamlet ] && { echo "%s/.git/stand-in-hamlet"; exit 0; }\nexit 1\n' "$PWD" > scripts/gates/l7r-gate.sh
  chmod +x scripts/gates/l7r-gate.sh; printf 'scripts/\n.gencache/\n*.driver.json\n' >> .git/info/exclude
  printf '%s' "$1" > "$POOL/m.driver.json"
  # GUARD_EDIT_OK: feature 449 T231 - the cache entry is written by a script the fixture keeps, so a stub `map` target (b1) redraws
  # the hamlet as the Rust driver would: its census written and its entry made current again
  cat > .git/draw.py <<'PY'
import hashlib, json, os, sys
root = sys.argv[1]
eng = "sha256:" + hashlib.sha256(open(os.path.join(root, ".git/stand-in-hamlet"), "rb").read()).hexdigest()
spec = os.path.join(root, "pool/hamlets/m/m.spec.json")
st = os.stat(spec)
meta = {"engine": "hamlet", "engine_id": eng, "skip_render": os.environ.get("DIAGRAM_SKIP_RENDER") == "1",
        "spec": {"path": "pool/hamlets/m/m.spec.json", "hashed": str(4102444800 * 10**9),
                 "stat": [str(st.st_size), str(st.st_mtime_ns), str(st.st_ctime_ns), str(st.st_ino)],
                 "digest": hashlib.sha256(open(spec, "rb").read()).hexdigest()},
        "artifacts": [], "key": "k", "reads": 0}
entry = os.path.join(root, ".gencache/rust/entries/hamlets/m")
os.makedirs(entry, exist_ok=True)
open(os.path.join(root, ".gencache/rust/reads.tsv"), "w").write("# l7r pool read table 1\n")
open(os.path.join(entry, "meta.json"), "w").write(json.dumps(meta))
PY
  python3 .git/draw.py "$PWD"
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

# GUARD_EDIT_OK: feature 449 T231 - a hamlet edited on a branch and not redrawn, its main holding a stub `map` target with this recipe
b1() {  # repo, the stub map target's recipe
  mkrepo "$1" withmap; git checkout -q main
  printf 'map:\n\t@%s\n' "$2" >> Makefile
  git add -A; git commit -qm gen; git update-ref refs/remotes/origin/main main; git checkout -q -b stale
  echo '{"seed": 2}' > "$POOL/m.spec.json"; git add -A; git commit -qm "the hamlet edited, not redrawn" -m "Occasion: none: reseeded, no rule changed"
}
said() { ( cd "$T/$1" && "$GATE" main..HEAD 2>&1 ); }
has() {  # label, repo, condition (run in the repo; a here-string, never a pipe into `grep -q`, which pipefail fails on its SIGPIPE)
  if ( cd "$T/$2" && eval "$3" ); then echo "  ok      $1"; PASS=$((PASS+1)); else echo "  FAIL    $1"; FAIL=$((FAIL+1)); fi
}
REDRAW='cp .git/next-census pool/hamlets/m/m.driver.json && python3 .git/draw.py "$$PWD" && touch .git/redrawn'
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
mkrepo b withmap; echo "$NEW" > "$POOL/m.json"; drawn "$NEW"; git add -A; git commit -qm reroll
check "a map gaining an element with no review recorded" b blocked
# GUARD_EDIT_OK: feature 375 amendment 9, D55 - the push asks every owed unit (--landing), the glyph units' hour aside, and a glyph
# unit with no answer marks the work LANDING, so the dispatch the refusal asks for is due and passes the pair guard
if [ -f "$T/b/.git/glyph-landing" ]; then echo "  ok      ...and marks the work landing, so its glyph dispatch is due (375 amendment 9)"; PASS=$((PASS+1))
else echo "  FAIL    the refused push did not mark the work landing"; FAIL=$((FAIL+1)); fi

# GUARD_EDIT_OK: feature 375 follow-up (2026-10-10) - a render older than main's read as a new element, so the gate redraws first
# GUARD_EDIT_OK: feature 449 T231 - and RED FIRST: this case edited the tracked m.json, which no reader has read since T230 (a live
# hamlet's elements are its Rust drawing's), so it passed without testing anything. Now the hamlet's SPEC is edited and not redrawn:
# its drawing is not current, `reviews owed` cannot know its elements, and the gate must redraw it (`make map MAP=`, the stub below
# writing the census the redraw draws and making the cache entry current) before it asks what is owed
b1 b1 "$REDRAW"; printf '%s' "$NEW" > .git/next-census
check "a hamlet edited and not redrawn, at integrated: refused" b1 blocked
has "...because the gate redrew it" b1 '[ -f .git/redrawn ]'
has "...and the glyph-check its redraw owes has no verdict" b1 'grep -q "glyph-check--well--m is owed and has no verdict record" <<<"$(said b1)"'
mkdir -p "$T/b1/.git/review-verdicts"; echo '{"map":"glyph-check--well--m","engine_key":"k","verdict":"PASS","findings":[]}' > "$T/b1/.git/review-verdicts/glyph-check--well--m.json"
check "...and ships once that glyph-check returned PASS" b1 ok
b1 b1s "$REDRAW"; printf '%s' '{"v":1,"ink_classes":{"farmhouse":1}}' > .git/next-census
check "a hamlet whose redraw draws nothing new owes nothing" b1s ok
has "...redrawn all the same" b1s '[ -f .git/redrawn ]'
b1 b1f 'echo "the hamlet engine panicked: no seat for the well" >&2; exit 1'
check "a redraw that fails: refused" b1f blocked
has "...naming what the draw said and the fix" b1f 'o="$(said b1f)"; grep -q "the hamlet engine panicked" <<<"$o" && grep -q "make map MAP=pool/hamlets/m" <<<"$o"'
b1 b1n 'touch .git/redrawn'
check "a redraw that leaves the drawing not current: refused" b1n blocked
has "...naming the map" b1n 'grep -q "pool/hamlets/m is still not current" <<<"$(said b1n)"'
mkrepo b1c withmap; printf 'map:\n\t@touch .git/redrawn\n' >> Makefile; echo work >> seed.txt; git add -A; git commit -qm work
check "a current drawing is not redrawn" b1c ok
has "...the map target never run" b1c '[ ! -f .git/redrawn ]'
# GUARD_EDIT_OK: feature 449 T231 - A FRESH TREE (land-tooling's worktree, a new clone) draws nothing, so every map reads not current;
# a push whose delta touches no engine path (`l7r-gate delta engine-paths`, the route's one list) changes no drawing, so it redraws none
mkrepo b1t withmap; printf 'map:\n\t@touch .git/redrawn\n' >> Makefile; git add -A; git commit -qm gen; git update-ref refs/remotes/origin/main HEAD
rm -rf .gencache; echo tooling >> seed.txt; git add -A; git commit -qm tooling
check "a fresh tree's push that touches no engine path ships" b1t ok
has "...nothing redrawn" b1t '[ ! -f .git/redrawn ]'

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

# feature 438: a TRIAL (**Form**: trial) pushes its evidence with no verdict while it is not Done and changes no engine code on net
TRIAL='# Trial: x\n\n**Form**: trial\n\n**Status**: Running\n'
mkrepo t1; printf "$TRIAL" > specs/900-x/spec.md; echo evidence > specs/900-x/notes.md; git add -A; git commit -qm trial
check "a running trial with no verdict, its evidence pushed: no verdict owed yet" t1 ok
mkrepo t2; printf "$TRIAL" > specs/900-x/spec.md; mkdir -p l7r; echo spike > l7r/x.py; git add -A; git commit -qm spike; git rm -q l7r/x.py; git commit -qm revert
check "...a spike committed and reverted in the same push: still none" t2 ok
mkrepo t3; printf "$TRIAL" > specs/900-x/spec.md; mkdir -p l7r; echo spike > l7r/x.py; git add -A; git commit -qm spike
check "...a push that changes the engine on net: the verdict is owed" t3 blocked
mkrepo t4; printf '# Trial: x\n\n**Form**: trial\n\n**Status**: Done - set down\n' > specs/900-x/spec.md; echo work >> seed.txt; git add -A; git commit -qm done
check "...a trial Done: the verdict is owed" t4 blocked

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
mkrepo nr withmap; echo "$NEW" > "$POOL/m.json"; drawn "$NEW"; echo "reviewed 2026-09-13" >> "$POOL/m.notes.md"
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
mkrepo r1 withmap; echo "$NEW" > "$POOL/m.json"; drawn "$NEW"; git add -A; git commit -qm reroll; mkdir -p .git/review-verdicts
echo '{"map":"glyph-check--well--m","engine_key":"k","verdict":"PASS","findings":[]}' > "$V"
check "a PASS record at this engine key, no notes touch" r1 ok
echo '{"map":"glyph-check--well--m","engine_key":"k","verdict":"NEEDS-WORK","findings":[{"id":"F1"}]}' > "$T/r1/$V"
check "...a NEEDS-WORK record at this key too (the findings are fixed under the same key)" r1 ok
echo '{"map":"glyph-check--well--m","engine_key":"stale","verdict":"PASS","findings":[]}' > "$T/r1/$V"
check "a PASS record at ANOTHER key, no notes touch: refused" r1 blocked
# GUARD_EDIT_OK: feature 374 batch 4, the round arbiter's tooling fix - a verdict stales on ITS sheet, not on the engine's key:
# a record at another engine key whose content key matches the sheet now ships; the sheet's notes changed, it is refused again
CK="$(cd "$T/r1" && "$HERE/../../scripts/gates/l7r-gate.sh" reviews prereq content-key --clone "$T/r1" --map glyph-check--well--m)"
echo "{\"map\":\"glyph-check--well--m\",\"engine_key\":\"stale\",\"content_key\":\"$CK\",\"verdict\":\"PASS\",\"findings\":[]}" > "$T/r1/$V"
check "a PASS record at another engine key whose sheet is unchanged ships" r1 ok
( cd "$T/r1" && echo "a later line" >> "$POOL/m.notes.md" && git add -A && git commit -qm notes )
check "...and once the sheet's notes change, it is refused" r1 blocked
# GUARD_EDIT_OK: feature 374 batch 5 - the round arbiter's ACCEPT on a unit stands for its verdict while the sheet reads as ruled
CK2="$(cd "$T/r1" && "$HERE/../../scripts/gates/l7r-gate.sh" reviews prereq content-key --clone "$T/r1" --map glyph-check--well--m)"
( cd "$T/r1" && mkdir -p .specify specs/902-a && echo '{"feature_directory":"specs/902-a"}' > .specify/feature.json \
  && echo "{\"trigger\":\"round:glyph-check|glyph-check--well--m@3\",\"unit\":\"glyph-check--well--m\",\"ruling\":\"accept\",\"why\":\"fixed\",\"content_key\":\"$CK2\"}" > specs/902-a/arbiter.jsonl \
  && git add -A && git commit -qm ruled )
echo '{"map":"glyph-check--well--m","engine_key":"stale","verdict":"NEEDS-WORK","findings":[{"id":"E1"}]}' > "$T/r1/$V"
check "a NEEDS-WORK record at another key ships on the arbiter's accept of the sheet as it reads" r1 ok
( cd "$T/r1" && echo "another line" >> "$POOL/m.notes.md" && git add -A && git commit -qm notes2 )
check "...and once the sheet changes after the ruling, it is refused" r1 blocked
mkrepo r2 withmap; echo "$NEW" > "$POOL/m.json"; drawn "$NEW"; echo "reviewed 2026-09-14" >> "$POOL/m.notes.md"; git add -A; git commit -qm reroll
mkdir -p .git/review-verdicts; echo '{"map":"glyph-check--well--m","engine_key":"stale","verdict":"PASS","findings":[]}' > "$V"
check "...and a stale-key record with the notes touched is refused too (D5: no substitute on a map with a record)" r2 blocked
# GUARD_EDIT_OK: feature 294 D2 - the rendering waiver is gone; drawing or placement code that moved must DECLARE its occasions
mkrepo r3 withmap; mkdir -p .specify specs/901-r l7r
echo 'X = 1' > l7r/placer.py
printf -- '- [x] T01 the placer\n      research: rendering\n' > specs/901-r/tasks.md
echo '{"feature_directory":"specs/901-r"}' > .specify/feature.json; git add -A; git commit -qm placer
check "placement code moved with no Occasions section in the active feature: refused" r3 blocked
# GUARD_EDIT_OK: feature 449 T238 round 2 - a section answers the delta only by a line naming the started task (`make task-start`)
printf -- '## Occasions\n\n- none: T01 - a refactor, every element placed under rules already judged\n\n- [x] T01 the placer\n      research: rendering\n' > "$T/r3/specs/901-r/tasks.md"
( cd "$T/r3" && printf '{"feature": "901-r", "task": "T01"}\n' > .git/active-task && git add -A && git commit -qm declared )
check "...and shipped once the feature declares its occasions" r3 ok
printf -- '## Occasions\n\n- placement-changed: farmhouse\n\n- [x] T01 the placer\n      research: rendering\n' > "$T/r3/specs/901-r/tasks.md"
( cd "$T/r3" && git add -A && git commit -qm re-placed )
check "...but a declared re-placement owes its glyph check (the GM's tannery)" r3 blocked
# GUARD_EDIT_OK: feature 449 T238 - RED FIRST: a Rust stage's placement change (`rust/phases/src/` outside the driver, the compound's
# layout) owed nothing and refused nothing, where the deleted Python's placement code was refused until the feature declared
mkrepo r7 withmap; mkdir -p rust/phases/src; printf 'const GAP_FT: f64 = 7.0;\n' > rust/phases/src/seat.rs; git add -A; git commit -qm stage
git update-ref refs/remotes/origin/main HEAD; printf 'const GAP_FT: f64 = 8.0;\n' > rust/phases/src/seat.rs; git add -A; git commit -qm "the seat's gap"
check "a Rust stage's placement change with no Occasions: refused" r7 blocked
has "...naming the stage" r7 'grep -q "drawing or placement code moved (rust/phases/src/seat.rs)" <<<"$(said r7)"'
( cd "$T/r7" && git commit -q --allow-empty -m "declared" -m "Occasion: none: the gap a guess moved, no element re-placed" )
check "...and shipped once an occasion is declared" r7 ok
mkrepo r8 withmap; mkdir -p rust/phases/src; printf 'const GAP_FT: f64 = 7.0;\n' > rust/phases/src/seat.rs; git add -A; git commit -qm stage
git update-ref refs/remotes/origin/main HEAD; printf '// the seat\nconst GAP_FT: f64 = 7.0;\n' > rust/phases/src/seat.rs; git add -A; git commit -qm "a comment"
check "...a comment on a Rust stage owes no declaration" r8 ok
# GUARD_EDIT_OK: feature 449 T238 - RED FIRST: a declaration naming no element became the unit `glyph-check--`, on no map, which no
# check can be dispatched for; it is refused with its form, with no code touched
mkrepo r9 withmap; mkdir -p .specify specs/901-r
printf -- '## Occasions\n\n- placement-changed: - on m\n\n- [ ] T01 the placer\n      research: rendering\n' > specs/901-r/tasks.md
echo '{"feature_directory":"specs/901-r"}' > .specify/feature.json; git add -A; git commit -qm declared
check "a declaration naming no element: refused" r9 blocked
has "...with its form, never as an owed unit glyph-check--" r9 'o="$(said r9)"; grep -q "names no element - write it \`- placement-changed: <element>\`" <<<"$o" && ! grep -q "glyph-check-- is owed" <<<"$o"'
printf -- '## Occasions\n\n- placement-changed: farmhouse on m\n\n- [ ] T01 the placer\n      research: rendering\n' > "$T/r9/specs/901-r/tasks.md"
( cd "$T/r9" && git add -A && git commit -qm fixed && mkdir -p .git/review-verdicts \
  && echo '{"map":"glyph-check--farmhouse--m","engine_key":"k","verdict":"PASS","findings":[]}' > .git/review-verdicts/glyph-check--farmhouse--m.json )
check "...and shipped once it names the element and its review passed" r9 ok
# GUARD_EDIT_OK: feature 449 T238 round 2 - RED FIRST: any `## Occasions` section silenced the refusal - one whose every line had landed,
# another task's (T236's commit replayed undeclared, 444's and 451's sections in place); only a line naming the started task answers
mkrepo r10 withmap; mkdir -p .specify specs/901-r specs/902-o rust/phases/src; printf 'const GAP_FT: f64 = 7.0;\n' > rust/phases/src/seat.rs
printf -- '- [ ] T05 other work\n\n## Occasions\n\n- none: tooling only - no map feature, glyph or placement rule\n' > specs/902-o/tasks.md
printf -- '- [x] T01 the old placer\n- [ ] T02 the seat\n      research: rendering\n\n## Occasions\n\n- none: T01 - a refactor\n' > specs/901-r/tasks.md
echo '{"feature_directory":"specs/901-r"}' > .specify/feature.json; git add -A; git commit -qm sections; git update-ref refs/remotes/origin/main HEAD
printf 'const GAP_FT: f64 = 8.0;\n' > rust/phases/src/seat.rs; sed -i 's/^- \[ \] T05/- [x] T05/' specs/902-o/tasks.md
printf '{"feature": "901-r", "task": "T02"}\n' > .git/active-task; git add -A; git commit -qm "the seat's gap"
check "placement code under sections naming only other tasks, their lines landed: refused" r10 blocked
has "...naming the started task a line must name" r10 'grep -q "the started task, specs/901-r T02 (\`make task-start\`), is named by no line" <<<"$(said r10)"'
printf -- '- none: T02 - the gap a guess moved, no element re-placed\n' >> "$T/r10/specs/901-r/tasks.md"
( cd "$T/r10" && git add -A && git commit -qm declared )
check "...and shipped once a line names the started task" r10 ok
# GUARD_EDIT_OK: feature 449 T238 round 2 - RED FIRST: a declaration naming no pool map (`farmhouse on mm`) became a unit on no map; a
# map's name is checked with no redraw, and refused with its form, naming the pool's closest maps
mkrepo r11 withmap; mkdir -p .specify specs/901-r
printf -- '## Occasions\n\n- placement-changed: farmhouse on mm\n\n- [ ] T01 the placer\n      research: rendering\n' > specs/901-r/tasks.md
echo '{"feature_directory":"specs/901-r"}' > .specify/feature.json; git add -A; git commit -qm declared
check "a declaration naming no pool map: refused" r11 blocked
has "...with its form and the pool's closest map, owing no unit" r11 'o="$(said r11)"; grep -q "names \`mm\`, no pool map or sheet - the closest: m" <<<"$o" && ! grep -q "glyph-check--farmhouse is owed" <<<"$o"'
# GUARD_EDIT_OK: feature 449 T238 round 2 (the plan review's D9) - RED FIRST: a declared element the map's current drawing does not hold
# (`farmhous on m`) became a unit on no map nobody can run; after the redraw the legend is known, and the line is refused with its form
mkrepo r12 withmap; mkdir -p .specify specs/901-r
printf -- '## Occasions\n\n- glyph-redrawn: farmhous on m - T01\n\n- [ ] T01 the placer\n      research: rendering\n' > specs/901-r/tasks.md
echo '{"feature_directory":"specs/901-r"}' > .specify/feature.json; git add -A; git commit -qm declared
check "a declared element the map's drawing does not hold: refused" r12 blocked
has "...with its form and the map's closest drawn kind, owing no unit" r12 'o="$(said r12)"; grep -q "names \`farmhous\`, which m.s drawing does not hold - its closest drawn kinds: farmhouse" <<<"$o" && ! grep -q "glyph-check--farmhous is owed" <<<"$o"'
# GUARD_EDIT_OK: feature 449 T238 round 2 (the plan review's D9c) - RED FIRST: a commit `Occasion:` line naming an element its map does
# not draw answered the delta's placement code and, owing no unit after D9, shipped it unreviewed; once drawn it answers nothing
mkrepo r13 withmap; mkdir -p rust/phases/src; printf 'const GAP_FT: f64 = 7.0;\n' > rust/phases/src/seat.rs; git add -A; git commit -qm stage
git update-ref refs/remotes/origin/main HEAD; printf 'const GAP_FT: f64 = 8.0;\n' > rust/phases/src/seat.rs; git add -A
git commit -qm "the seat's gap" -m "Occasion: placement-changed: farmhous on m - the gap"
check "placement code answered only by a commit line naming an element the map does not draw: refused" r13 blocked
has "...as undeclared, after the redraw" r13 'grep -q "commit lines name only elements their maps. current drawings do not hold" <<<"$(said r13)"'
( cd "$T/r13" && git commit -q --allow-empty -m "declared" -m "Occasion: none: the gap a guess moved, no element re-placed" )
check "...and shipped once a commit line answers it" r13 ok

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

case_4() {
echo "4. AT RUST-ONLY A HAMLET'S MAP REVIEW WAITS FOR THE THROW BACK (feature 444 FR-023)"
V=.git/review-verdicts/glyph-check--well--m.json
mkrepo r4 withmap; echo "$NEW" > "$POOL/m.json"; drawn "$NEW"; git add -A; git commit -qm reroll; mkdir -p .git/review-verdicts
echo '{"map":"glyph-check--well--m","engine_key":"stale","verdict":"PASS","findings":[]}' > "$V"
check "a stale record on a hamlet's map, the switch at integrated: refused" r4 blocked
( cd "$T/r4" && echo '{"port": {"state": "rust-only"}}' > dev/switches.json && git add -A && git commit -qm rust-only )
check "...at rust-only it waits for the throw back and ships, no map redrawn" r4 ok
# GUARD_EDIT_OK: feature 449 T232 - at rust-only a hamlet IS redrawn for the gate (T231 had it not: then an edited hamlet owed no unit
# to set aside, and nothing was kept for the throw back); a redraw that leaves it not current refuses nothing, and is recorded
b1 r5 'touch .git/redrawn'; echo '{"port": {"state": "rust-only"}}' > dev/switches.json; git add -A; git commit -qm rust-only
check "a hamlet edited and not redrawn, at rust-only: ships" r5 ok
has "...redrawn, and recorded as not known" r5 '[ -f .git/redrawn ] && grep -q "\"hamlet\":\"pool/hamlets/m\"" dev/deferred-reviews.jsonl'
}

# GUARD_EDIT_OK: feature 449 T232 - A REVIEW SET ASIDE AT RUST-ONLY IS NOT LOST BEFORE THE THROW BACK. What a delta owes is read
# against the landing's base, and a hamlet's base census is main's drawing of it: once the push lands, the delta no longer holds the
# element, so at the throw back the review it owed was owed by nothing (measured 2026-11-19 in a scratch mirror: an edited hamlet
# pushed at rust-only, the mirror's render-sync, the switch thrown - "review-gate: clean"). `landed` puts the work on main as the
# push does and moves origin/main to it; `thrown` throws the switch to integrated in a new commit.
landed() { git checkout -q main && git merge -q --ff-only "$1" && git update-ref refs/remotes/origin/main main && git checkout -q "$1"; }
thrown() { echo '{"port": {"state": "integrated"}}' > dev/switches.json; git add -A; git commit -qm thrown; }
case_5() {
echo "5. A HAMLET REVIEW SET ASIDE AT RUST-ONLY IS OWED AT THE THROW BACK (449 T232)"
V=.git/review-verdicts/glyph-check--well--m.json
mkrepo d1 withmap; git checkout -q main; echo '{"port": {"state": "rust-only"}}' > dev/switches.json; git add -A; git commit -qm rust-only
git update-ref refs/remotes/origin/main main; git checkout -q -B work main
echo "$NEW" > "$POOL/m.json"; drawn "$NEW"; git add -A; git commit -qm "the hamlet gains a well"
check "a hamlet's new element at rust-only: set aside, ships" d1 ok
has "...its unit recorded, committed" d1 'grep -q "glyph-check--well--m" dev/deferred-reviews.jsonl && git diff --quiet HEAD -- dev/deferred-reviews.jsonl'
( cd "$T/d1" && landed work && thrown )
check "...landed, then the switch thrown back: owed" d1 blocked
has "...named as set aside at rust-only" d1 'grep -q "glyph-check--well--m is owed and has no verdict record" <<<"$(said d1)"'
mkdir -p "$T/d1/.git/review-verdicts"; echo '{"map":"glyph-check--well--m","engine_key":"k","verdict":"PASS","findings":[]}' > "$T/d1/$V"
# GUARD_EDIT_OK: feature 449 T233 - the hamlet the port drew at rust-only owes its settlement-review at the throw back too (case_6)
SR=.git/review-verdicts/settlement-review--m.json
echo '{"map":"settlement-review--m","engine_key":"k","verdict":"PASS","findings":[]}' > "$T/d1/$SR"
( cd "$T/d1" && echo "# spec" > specs/900-x/spec.md && git add -A && git commit -qm "a spec with no verdict" )
check "...its review found on a push refused for another reason: refused" d1 blocked
has "...and its review not recorded, so it stays owed" d1 '! grep -q "\"reviewed\"" dev/deferred-reviews.jsonl'
( cd "$T/d1" && git rm -q specs/900-x/spec.md && git commit -qm "the spec withdrawn" )
check "...and ships once its glyph-check returned PASS" d1 ok
has "...its review recorded" d1 'grep -q "\"reviewed\":\"glyph-check--well--m\"" dev/deferred-reviews.jsonl'

rm -f "$T/d1/$V" "$T/d1/$SR"; ( cd "$T/d1" && landed work )
check "...its review recorded on main: another clone with no verdict file owes it no more" d1 ok
# the gate redraws a hamlet at rust-only too: a hamlet edited and not redrawn owed nothing it could set aside, so nothing was kept
b1 d2 "$REDRAW"; printf '%s' "$NEW" > .git/next-census; echo '{"port": {"state": "rust-only"}}' > dev/switches.json; git add -A; git commit -qm rust-only
check "a hamlet edited and not redrawn, at rust-only: ships" d2 ok
has "...redrawn, its new element's unit recorded" d2 '[ -f .git/redrawn ] && grep -q "glyph-check--well--m" dev/deferred-reviews.jsonl'
( cd "$T/d2" && landed stale && thrown )
check "...landed, then thrown back: owed" d2 blocked
# the escape skips the refusal, never the record: an escaped push at rust-only still records what it sets aside
mkrepo d4 withmap; git checkout -q main; echo '{"port": {"state": "rust-only"}}' > dev/switches.json; git add -A; git commit -qm rust-only
git update-ref refs/remotes/origin/main main; git checkout -q -B work main
echo "$NEW" > "$POOL/m.json"; drawn "$NEW"; echo "# spec" > specs/900-x/spec.md; git add -A; git commit -qm "a well, and a spec with no verdict"
if ( cd "$T/d4" && REVIEW_GATE_OK="superseded before implementation" "$GATE" main..HEAD >/dev/null 2>&1 ); then
  echo "  ok      an escaped push at rust-only ships"; PASS=$((PASS+1))
else echo "  FAIL    the escape did not work"; FAIL=$((FAIL+1)); fi
has "...and still records the unit it set aside, committed" d4 'grep -q "glyph-check--well--m" dev/deferred-reviews.jsonl && git diff --quiet HEAD -- dev/deferred-reviews.jsonl'
( cd "$T/d4" && git rm -q specs/900-x/spec.md && git commit -qm "the spec withdrawn" && landed work && thrown )
check "...landed, then thrown back: owed" d4 blocked
# a redraw that fails at rust-only refuses nothing (444 FR-023), and the hamlet is recorded with its elements before, so the
# throw back owes what it draws new since
b1 d3 'echo "the hamlet engine panicked" >&2; exit 1'; echo '{"port": {"state": "rust-only"}}' > dev/switches.json; git add -A; git commit -qm rust-only
check "a hamlet whose redraw fails at rust-only: ships" d3 ok
has "...recorded with its elements before" d3 'grep -q "\"hamlet\":\"pool/hamlets/m\"" dev/deferred-reviews.jsonl && grep -q "farmhouse" dev/deferred-reviews.jsonl'
( cd "$T/d3" && landed stale && printf '%s' "$NEW" > pool/hamlets/m/m.json && printf '%s' "$NEW" > pool/hamlets/m/m.driver.json \
  && python3 .git/draw.py "$PWD" && git add -A && git commit -qm "main's drawing catches up" && landed stale && thrown )
check "...drawn with a new element since, landed, thrown back: owed" d3 blocked
has "...the element new since the set-aside" d3 'grep -q "glyph-check--well--m is owed" <<<"$(said d3)"'
}

# GUARD_EDIT_OK: feature 449 T233 - THE SETTLEMENT-REVIEW FEATURE 444 FR-019 OWES EVERY POOL HAMLET THE PORT MOVED: a hamlet already in
# the pool owes none the delta detects (only a map new to the pool does), so a Rust stage that moved one at rust-only set nothing aside
# and the throw back owed nothing (measured 2026-11-19 in scratch on the old gate: "review-gate: clean" at the throw back). Red first:
# the old gate shipped this case's thrown push.
case_6() {
echo "6. A POOL HAMLET THE PORT MOVED OWES ITS SETTLEMENT-REVIEW AT THE THROW BACK (444 FR-019, 449 T233)"
mkrepo s1 withmap; git checkout -q main; echo '{"port": {"state": "rust-only"}}' > dev/switches.json; git add -A; git commit -qm rust-only
git update-ref refs/remotes/origin/main main; git checkout -q -B work main
mkdir -p rust/phases/src; echo '// the port moves the hamlet' > rust/phases/src/stage.rs
drawn '{"v":2,"ink_classes":{"farmhouse":3}}'; echo '{"v":2,"ink_classes":{"farmhouse":3}}' > "$POOL/m.json"
git add -A; git commit -qm "a Rust stage moves the hamlet" -m "Occasion: none: the port's own roll"
check "a hamlet the port moved, at rust-only: ships" s1 ok
has "...its settlement-review recorded, committed" s1 'grep -q "\"unit\":\"settlement-review--m\"" dev/deferred-reviews.jsonl && git diff --quiet HEAD -- dev/deferred-reviews.jsonl'
has "...once: a second push records nothing more" s1 'said s1 >/dev/null; [ "$(grep -c "settlement-review--m" dev/deferred-reviews.jsonl)" = 1 ]'
( cd "$T/s1" && landed work && thrown )
check "...landed, then the switch thrown back: owed" s1 blocked
has "...named as set aside at rust-only" s1 'grep -q "settlement-review--m is owed and has no verdict record" <<<"$(said s1)"'
mkdir -p "$T/s1/.git/review-verdicts"; echo '{"map":"settlement-review--m","engine_key":"k","verdict":"PASS","findings":[]}' > "$T/s1/.git/review-verdicts/settlement-review--m.json"
check "...and ships once its settlement-review returned PASS" s1 ok
has "...its review recorded" s1 'grep -q "\"reviewed\":\"settlement-review--m\"" dev/deferred-reviews.jsonl'
# a row is keyed by its hamlet's name: renamed at rust-only (its spec moved with its folder, git's rename detection), the row is
# carried to the new name by the gate, so the throw back owes it there (before T233 the rename dropped it)
mkrepo s2 withmap; git checkout -q main; echo '{"port": {"state": "rust-only"}}' > dev/switches.json
echo '{"unit":"settlement-review--m","check":"settlement-review","subject":"m","on":"m","occasion":"o","utc":"2026-11-19T00:00:00Z","commit":"x"}' > dev/deferred-reviews.jsonl
git add -A; git commit -qm "rust-only, a row open"; git update-ref refs/remotes/origin/main main; git checkout -q -B work main
git mv pool/hamlets/m pool/hamlets/m2; for f in spec.json json notes.md; do git mv "pool/hamlets/m2/m.$f" "pool/hamlets/m2/m2.$f"; done
git commit -qm "the hamlet renamed" -m "Occasion: none: a rename"
check "a hamlet renamed at rust-only: ships" s2 ok
has "...its row carried to the new name, committed" s2 'grep -q "\"unit\":\"settlement-review--m2\"" dev/deferred-reviews.jsonl && git diff --quiet HEAD -- dev/deferred-reviews.jsonl'
( cd "$T/s2" && landed work && thrown )
check "...landed, then thrown back: owed under the new name" s2 blocked
has "...named" s2 'grep -q "settlement-review--m2 is owed and has no verdict record" <<<"$(said s2)"'
}

# GUARD_EDIT_OK: feature 383 amendment 4 (plan D28) - the sections as cases, run in parallel parts (tests/hooks/parts.sh)
CASES=(case_1 case_1b case_2 case_3 case_4 case_5 case_6)
declare -A WEIGHT=()
# shellcheck source=/dev/null
source "$HERE/parts.sh"
run_parts ${REVIEWGATE_PARTS:-4}

echo
echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
