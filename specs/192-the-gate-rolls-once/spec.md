# 192 - The gate rolls once

**Status**: draft, round 2
**Request**: [request.md](request.md)
**Diagnosis**: `specs/191-refusals-that-tell-the-truth/research.md` R7

## Why

On a cold roll cache the gate's floor phase rolls seven maps, four of which the suite has ALREADY
rolled moments earlier under the same subject. That phase measured **401.6 s** on an instrumented
run - about half the gate's wall clock - against ~1 s warm.

`rollcache.obtain()` bypasses SERVING under `L7R_TESTS_FULL=1` (which the gate always sets, via
`Makefile:1130`), because a served roll executes nothing the coverage floors could see. Correct. But
the non-shared bypass returns at line 173 - `return produce(), "BYPASS"` - before ever reaching the
`gencache.record(...)` tail, so those rolls leave no dependency record. `hamlet_floor` derives the
hamlet path from exactly those records, finds none, and (by its own documented design, *"Never
bypassed"*) rolls its subjects itself.

**What the fix actually removes, counted rather than asserted** (corrected at review round 1, which
found the first draft's "the same eight maps TWICE" wrong for four of the eight):

| floor subject | who else rolls it as `report:` | after this feature |
|---|---|---|
| Inashiro seed 4 | the `_reference` phase, which is NOT bypassed and writes the record before pytest starts | already not re-rolled today |
| cohort seeds 41-44 | `tests/gate/hamletgen/test_driver.py:44` via `rollcache.report(spec)`, under FULL | **FIXED - 4 rolls removed** |
| Polder 12, Polder 19 | nobody. The suite rolls these as `hamlet:{spec!r}` - a different subject and a different code path (`plan_site+build+finish` vs `hg.generate` with the gate and re-roll loop) | still a FIRST roll in the floor - accepted, D4 |
| Polder seed 8 | nothing in the tree rolls it in any form | **REMOVED from the subject list** - FR-007 |

So the floor rolls **seven** subjects cold. FR-001 removes **four** (the duplicated cohort seeds) and
FR-007 removes **one** (seed 8, which reaches no module the others do not). **Two remain** - Polder 12
and Polder 19 - and those are FIRST rolls rather than duplicates, so no amount of bypass-recording can
remove them: nothing else in the tree produces their `report:` records. On R7's own arithmetic
(~57 s per roll) roughly **115 s of floor rolling remains**.

## Requirements

- **FR-001** A roll bypassed **because `L7R_TESTS_FULL=1`** records its dependencies and stores its
  entry. **`GATE_NO_CACHE=1` is explicitly NOT included**: it is the documented "regenerate
  everything, leave nothing behind" escape (`gencache.py:568`), the GM did not ask to change it, and
  `bypassed()` is true for both - so the two must be told apart rather than treated as one.
- **FR-002** Nothing about SERVING under FULL changes: the bypass still PRODUCES on every call, so
  every line the coverage floors judge is still executed. What changes is only what is left behind.
- **FR-003** The entry is written as `payload.pickle` + `meta.json` TOGETHER, exactly as the MISS
  path does, preserving the pair invariant `_place` exists to hold (D1).
- **FR-004** Recording is confined to `report:` subjects, which is what the floor consumes. The
  residual this leaves is stated in the table above rather than discovered from a slower-than-promised
  run.
- **FR-005** `report_deps` needs NO change - it already reads `meta.json`, which FR-003 now writes.
- **FR-007** `hamlet_floor.subjects()` drops `Polder seed=8`. **AUTHORIZED AND MEASURED, in that
  order.** The GM ruled *"I defer to you on whether that Polder seed eight earns its place or not
  because I am not familiar with that code. If you take a look and find that it does not seem to be
  doing anything, then we should remove it."* Measured from the recorded `report:` deps of all eight
  subjects: seed 8 reaches **83 modules, of which 0 are reached by no other subject**. Its entire
  contribution to the floor's module set - the floor's ONLY output - is already made by the other
  seven, while it costs a full roll (~57 s) on every cold cache. Disclosed limit on the finding: it
  is the only polder subject with `down_deg=None`, so it does exercise a distinct CONFIGURATION; at
  module granularity, which is what the GM chose for this floor, that configuration reaches nothing
  new. If the floor ever becomes line-level this decision must be revisited.
- **FR-006** The `done` ratchet baseline is re-pinned to **400 s** - the figure in the GM's own
  authorization - with the reason resting on 191 R7. A materially different measurement goes back to
  the GM rather than being pinned by this session.

## Decisions Recorded

- **D1 - a `deps.json` side-file was DESIGNED AND REJECTED. Recorded because it is a dead end worth
  not re-walking.** The first draft had the bypass write deps to their own file, on the reasoning
  that writing `meta.json` alone - the payload withheld - would let a later run serve stale bytes:
  meta rewritten with the current key while `payload.pickle` still held bytes from an older key, so
  the serve path (which validates the key on meta and then unpickles the payload with no key of its
  own) would hand back the old bytes as the new. **That hazard is real** - `_place` lands meta last
  precisely so the pair is only ever valid together. But it is a hazard of a HOBBLED implementation:
  the bypass has the payload in hand, so letting it fall through to `obtain()`'s existing
  record-and-store tail writes the pair together, keeps the invariant exactly as it is today, needs
  no new file and no new read path, and is about three lines. The side-file was solving a problem
  created by an unnecessary constraint.
- **D2 - a FULL-run payload is byte-identical to a MISS-run payload, so caching it is safe.**
  Verified at review: `L7R_TESTS_FULL` is read in exactly two places in the tree - `rollcache.py:51`
  and `tests/_scope.py:25` - and `_scope` selects WHICH tests and specs run, never engine behavior
  inside a roll. This is what makes FR-003 legitimate rather than a shortcut; without it, storing a
  payload produced under FULL would be storing bytes from a different program.
- **D3 - overhead was MEASURED before the design was chosen.** One Inashiro roll: 23.75 s plain,
  23.60 s under `gencache.record` (0.99x - within noise; 803 dep entries). Disclosed limit: that was
  measured outside a coverage-traced pytest process, which is where FR-001 puts the recording. The
  mechanism is sound (`gencache.record` uses `sys.monitoring.PROFILER_ID`, coverage does not share
  it), but the number under coverage is unverified and SC-001's instrumented run is what confirms it.
- **D4 - Polder 12 and 19 are ACCEPTED as a residual, not fixed.** Removing them would mean either
  changing what the suite rolls (a `report:` roll where it now does a `hamlet:` one, which costs the
  suite the difference) or dropping them from the subject list - and unlike seed 8 they are NOT free
  to drop: the seed-8 measurement that justifies FR-007 was specifically that it adds no module the
  others do not, and no such finding exists for these two. Dropping them would change what the floor
  MEASURES on no evidence, which is the opposite of what FR-007 does.

## Out of scope

- The ratchet's population mixing (a median over warm and cold runs describes neither) and the
  run-log behavior where a run that FAILS the ratchet is still logged `green` and so feeds the
  median that failed it. Both recorded in 191 R7; deliberate per the Makefile's own comment.
- (`Polder seed=8` was out of scope in round 2 and is now FR-007 - the GM ruled on it between
  rounds. Its removal takes the floor's cold-cache rolls from seven to six, on top of the four
  removed by FR-001.)

## Success Criteria

- **SC-001** On an instrumented cold-cache `make done`, the post-pytest gap falls from ~400 s to
  **roughly 115 s** - five of seven rolls removed (four by FR-001, one by FR-007), not "to seconds".
  The number is stated so the run either meets it or contradicts it.
- **SC-002** No roll is SERVED under `L7R_TESTS_FULL=1`. Asserted - this is the property FR-002
  protects and the whole reason the bypass exists.
- **SC-003** `GATE_NO_CACHE=1` still leaves nothing behind. The existing assertion
  (`tests/pipeline/test_rollcache.py:113-131`) covers BOTH bypasses today and must be SPLIT rather
  than deleted: FULL now stores, `GATE_NO_CACHE` still does not.
- **SC-004** `make done` green, 100% coverage held.
- **SC-005** Measured fact to set expectations, not a target: a 400 s baseline yields a 520 s
  ceiling, and the current median is **543 s**. The re-pin therefore clears the deadlock only once
  one further run lands under ~520 s and pulls the median down. If that does not happen, the block is
  not resolved and goes back to the GM rather than being re-pinned again.

## Review history

- **Round 1 (`spec-fidelity`): CHANGES REQUIRED.** Five items, all accepted: (1) the "eight maps
  twice" claim was wrong for four of eight - Inashiro's record is written by the un-bypassed
  `_reference` phase, and the three polders are never rolled as `report:` by anything but the floor,
  seed 8 by nothing at all; the count is seven rolled, four removed, ~170 s residual. (2) FR-004/D3
  had to state that residual rather than leave it to be discovered. (3) D1 justified a new file
  against a hobbled alternative - the fall-through to the existing store tail is simpler and keeps
  the invariant, so it is adopted and the side-file recorded as a dead end. (4) FR-001 did not
  distinguish the two bypasses, and would have silently changed `GATE_NO_CACHE`'s documented
  behavior. (5) FR-006 said "the measured warm cost", which authorizes pinning whatever this session
  next measures - the exact shape of the re-pin made and reverted this morning; it now names the
  GM's own 400 s. The reviewer independently confirmed the mechanism (bypass skips `record`,
  `report_deps` never bypassed, the gate sets FULL), the stale-payload hazard, and the ratchet
  arithmetic; it could not reproduce R7's 401.6 s gap or D3's overhead numbers, which is stated.
- **Round 2 (`spec-fidelity`): FAITHFUL.** *"Implement it."* The reviewer walked `obtain()` and
  confirmed the fall-through preserves the pair invariant (payload first, meta last, both through
  `_place`), that `bypassed()` does not collapse the two variables so FR-001's split is
  implementable, and that FR-002 does not overstate. It also WIDENED D2's check unprompted: besides
  `L7R_TESTS_FULL`, no engine module reads `L7R_TESTS_EXHAUSTIVE` or `L7R_COV_FLOORS` either, so a
  payload produced inside the gate's pytest process is byte-identical to one from `make quick` on
  every environment axis - the new serve capability rests on measurement, not assertion.
- **Round 3**: pending - FR-007 was added after round 2, on the GM's ruling.
