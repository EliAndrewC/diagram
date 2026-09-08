# Feature 216 - the floor as doctrine

**Status**: DRAFT - `spec-fidelity` round 1 pending (constitution XVI).
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
- **FR-002 The four cuts.** (a) Woodland-shrink: the parcel band and floor are asserted on a map that already
  exists - the pool's reference through `_pool.rolled_map` on a Settlement carrying its manifest - or, if
  `open_ground_patches` cannot run on a loaded manifest, on a stub site; the ladder's own decisions stay
  pinned in `tests/hamletgen/test_hinterland.py`. (b) Clamped: the pond-to-off-map fallback is a unit test of
  the sink stage's decision with `pond_setback` and `pond_clear_of_crop` patched and `stage_sink` recorded -
  the three lines only it reached. (c) Polder 19: its two tests (the grid, dike and reservoir; the keep-outs)
  read Polder 12; the roster's polder is one. (d) The three seatings share ONE partial roll: the stages before
  the homestead pass run once in a child (inside `roll_scope`, so the census counts it), the state is copied
  three times and each seating runs with its patch - the cloud alone, the lane frontage alone, the one-household
  stop; if the cloud's assertions do not hold on the linear spec the other two need, a second partial roll for
  the nucleated form, stated in R2. The nine engine lines the three FULL rolls alone reached (`ways/route.py`,
  `ways/touch.py`, `ways/web.py`, `homesteads/wells.py`, `hinterland/stages.py`) become direct unit tests.
- **FR-003 The doctrine, in the guidelines.** Constitution Principle VI gains the clause, in the GM's words:
  the `make done` tests minimize the number of map rolls and roll only what is strictly necessary to reach 100%
  coverage; a test that rolls more than that belongs in the CI tier (the AWS check), which is not a kind of test
  run today and is where such a test goes if one is ever made (a MINOR amendment, 2.22.0). The root `CLAUDE.md`
  roster bullet, `tests/CLAUDE.md`'s tree table (a row for the CI tier: not run today; the place for a test that
  rolls more than the floor) and `dev/loop.md`'s packing section carry the rule and its date.
- **FR-004 The roster, the census, the record.** `tests/rolls.py` at 4 rows (the perturbed reference, Polder 12,
  seed 43, the seatings' partial roll; 5 if the cloud needs its own); a warm gate's census reads as many rolls
  as rows; `make done` green; R2 the census line and the gate's time; the audit re-run after landing and its
  output recorded.
- **FR-005 What proves less, stated.** (a) the woodland band is asserted on the pool's map or a stub, not on
  a site rolled for it; (b) the clamp's fallback is asserted as a decision, no longer that the brook it promised
  was actually cut on a real map; (c) the polder grid at fall 90 is no longer rolled - its form, its keep-outs
  and its web are no longer asserted on a real map; (d) the three seatings are asserted on a shared partial
  state, and the stages after the homestead pass (lanes, track, hinterland) no longer run on the seated
  variants - their nine lines hold as unit tests. Each raised with the GM at landing.

## Success criteria

- **SC-001** A warm full gate's census reads 4 rolls of 4 specs (5 of 5 if the cloud needs its own), no duplicates.
- **SC-002** `make done` green at 100% on both floors; no assertion removed except the four FR-005 states.
- **SC-003** `make roll-audit` prints the table for the landed baseline, and the constitution carries the clause.

## Decisions Recorded

- **D1 - the rule is a constitution clause, not only a CLAUDE.md line.** The GM: *"our project guidelines should
  explicitly make it clear"*; Principle VI is where the gate's obligations live, and a new obligation is a MINOR
  amendment by the versioning policy.
- **D2 - a partial roll is a roll.** The stages-before-seating run sits inside `roll_scope` (the AST rule of
  feature 210 demands it), so the census counts it as one roll with its own roster row; that is the honest
  count, and it is why the three seatings become one.
- **D3 - the audit is a tool, not a script beside a spec.** A tool owes 100% coverage and a place in the command
  map; that cost is what makes it a command the next tier can run rather than a file someone must find.
