# Feature 216 - the floor as doctrine

**Status**: DRAFT - `spec-fidelity` round 1 required three changes, applied: the conditional second partial roll
deleted (a fifth roll can never be strictly necessary for a spec with no unique line); FR-005 d states the loss
the collapse causes; the amendment is 2.23.0 and corrects the footer. Round 2 required two changes, applied: seed 43 - the one gate roll carrying no coverage line - leaves the
gate roster for the CI tier's tree under the very clause this feature writes (FR-002 e, FR-005 e); the woodland
band's site is stated as the stub the probe settled on (FR-002 a, FR-005 a). Round 3 pending (constitution XVI).
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - the four cuts' sites, the
feasibility probes, the count after.
**Predecessors**: 215 (the floor itself: 9 rolls of 9; its R1 audit and the four cuts it priced and left), 214,
213 (the roll census and the roster).

## Summary

The GM, on the two things 215 recorded and did not take: the audit script becomes `make roll-audit` (*"I imagine
that we will do this again ... for villages or towns ... or whatever other types of maps that we make"*); the
four further rolls go (*"Not only should we do that here, we should always do that for the make done tests"*);
and the rule is written into the guidelines: the gate's tests minimize map rolls and roll only what 100% coverage
strictly needs - a test that rolls more belongs in the CI tier, which does not exist today but is where such a
test goes if one is ever made.

## Functional requirements

- **FR-001 `make roll-audit`.** A tool (`l7r/diagram/tools/roll_audit.py`, under the 100% floor like every
  tool) reads the current gate baseline's coverage contexts and prints, per rolling context - any context that
  executed at least `--min-lines` engine lines (default 2,000; a tier's rolls are larger, and the threshold is
  the knob) - the engine lines NO other context of the suite reaches, with the files they sit in; 215's R1
  method, for any tier. `make roll-audit` runs it; `make audit` names it. Unit-tested on a synthetic coverage
  database with contexts; the target documented in the command map.
- **FR-002 The four cuts, and the fifth the clause forces.** (a) Woodland-shrink: the parcel band and floor
  are asserted on the hinterland unit tests' stub site (the pool's loaded manifest cannot run
  `open_ground_patches` - R1's probe; the ladder's own decisions stay pinned in
  `tests/hamletgen/test_hinterland.py`). (b) Clamped: the pond-to-off-map fallback is a unit test of
  the sink stage's decision with `pond_setback` and `pond_clear_of_crop` patched and `stage_sink` recorded -
  the three lines only it reached. (c) Polder 19: its two tests (the grid, dike and reservoir; the keep-outs)
  read Polder 12; the roster's polder is one. (d) The three seatings share ONE partial roll: the stages before
  the homestead pass run once in a child (inside `roll_scope`, so the census counts it), the state is copied
  three times and each seating runs with its patch followed by the track stage (the frontage offers seats along
  the connector the track draws) - the cloud alone, the lane frontage alone, the one-household stop. ONE roll:
  the probe of 2026-09-08 showed all three assertions hold on the linear state; had the cloud's not, it would
  have become a unit test of the cloud pass's decision or been dropped and recorded in FR-005 - never a second
  roll, since a spec with no unique line can never be strictly necessary for the floor. The ten engine lines the
  three FULL rolls alone reached (`ways/route.py`, `ways/touch.py`, `ways/web.py`, `homesteads/wells.py`,
  `hinterland/stages.py`; R1) become direct unit tests, the gate's floor naming any the count missed.
  (e) Seed 43: its eight unique lines became unit tests in feature 215 and its only remaining reason is the
  strict xfail over the open kink defect - a roll that carries no coverage line, which is exactly what the
  clause of FR-003 assigns to the CI tier. So it leaves the gate roster: the xfail moves to `tests/ci/`, the
  CI tier's tree, which no target runs today (`tests/CLAUDE.md` names it as the place), and the defect stays
  recorded in the research (feature 166 R2b) and in that test.
- **FR-003 The doctrine, in the guidelines.** Constitution Principle VI gains the clause, in the GM's words:
  the `make done` tests minimize the number of map rolls and roll only what is strictly necessary to reach 100%
  coverage; a test that rolls more than that belongs in the CI tier (the AWS check), which is not a kind of test
  run today and is where such a test goes if one is ever made (a MINOR amendment, 2.23.0 - the log already
  records 2.22.0 for feature 211 while the footer still says 2.21.0; the amendment sets both). The root `CLAUDE.md`
  roster bullet, `tests/CLAUDE.md`'s tree table (a row for the CI tier: not run today; the place for a test that
  rolls more than the floor) and `dev/loop.md`'s packing section carry the rule and its date.
- **FR-004 The roster, the census, the record.** `tests/rolls.py` at 3 rows (the perturbed reference, Polder 12,
  the seatings' partial roll), every row carrying a coverage line nothing else reaches, as the clause requires;
  a warm gate's census reads 3 rolls of 3 specs; `make done` green; R2 the census line and the gate's time; the audit re-run after landing and its
  output recorded.
- **FR-005 What proves less, stated.** (a) the woodland band and floor are no longer asserted on any rolled
  site - they hold on a stub site's parcels; (b) the clamp's fallback is asserted as a decision, no longer that the brook it promised
  was actually cut on a real map; (c) the polder grid at fall 90 is no longer rolled - its form, its keep-outs
  and its web are no longer asserted on a real map; (d) the three seatings are asserted on a shared partial
  state, and the stages after the homestead pass (lanes, track, hinterland) no longer run on the seated
  variants - their lines hold as unit tests; the cloud's seating is asserted on the shared LINEAR state rather
  than on a rolled nucleated hamlet (its roster row existed for the cloud seating a default-form hamlet, seed
  7); and the three seatings are no longer three distinct maps (OneHouse's own map, whose placard width made it
  differ from LaneOnly's, ceases to exist); (e) seed 43's kink is no longer observed by any gate run - the
  strict xfail lives in the CI tier's tree, which nothing runs today, so the gate will not go red the day the
  router stops making the kink. Each raised with the GM at landing.

## Success criteria

- **SC-001** A warm full gate's census reads 3 rolls of 3 specs, no duplicates, every row with a coverage reason.
- **SC-002** `make done` green at 100% on both floors; no assertion removed except the four FR-005 states.
- **SC-003** `make roll-audit` prints the table for the landed baseline, and the constitution carries the clause.

## Decisions Recorded

- **D1 - the rule is a constitution clause, not only a CLAUDE.md line.** The GM: *"our project guidelines should
  explicitly make it clear"*; Principle VI is where the gate's obligations live, and a new obligation is a MINOR
  amendment by the versioning policy.
- **D2 - a partial roll is a roll.** The stages-before-seating run sits inside `roll_scope` (the AST rule of
  feature 210 demands it), so the census counts it as one roll with its own roster row - the three seatings'
  runs in the same child are its attempts, not rolls of their own; that is the honest count, and it is why the
  three seatings become one.
- **D3 - the audit is a tool, not a script beside a spec.** A tool owes 100% coverage and a place in the command
  map; that cost is what makes it a command the next tier can run rather than a file someone must find.
