# Feature 220 - the field fitted once

**Status**: DRAFT 2026-09-09; `spec-fidelity` round 1 required three changes, applied: the pool regeneration and the review apply after ANY step that moves a map, and FR-003 lost its "or records why not" escape (FR-005); the neighbor search REQUIRES the spatial tree the GM named, a bounds prefilter only in front of it (FR-003); the whole-roll figure the GM predicted is on the yardstick and in SC-001 (FR-004). The reviewer's aside (yardstick vs success criterion) settled: SC-001 states the GM's numbers as the yardstick and the measured result is reported against them - a miss is reported, not hidden, and the GM decides.
**Request**: [`request.md`](request.md) - the session's assessment the GM approved, and their approval.
**Research**: [`research.md`](research.md) - the profile before, each step's measurement, the gate's
time. **Predecessors**: 218 (the index pattern, `KeepoutGrid`, constitution X clause 15, and the GM's
relaxation of byte-identity), 145 (`RingIndex`, the prefilter family), 141/166 (a rule about a map is
a test of the placer).

## Summary

`stage_field` is 5.4 s of the reference hamlet's 10.2 s roll, and its cost is not one overlap check
but four full comb builds: `fit_field` searches a size multiplier for the target acreage and builds
the whole comb - carve, seam closing, dry plots - at every guess, then keeps one. Seam closing is two
thirds of a build and was added after the search's docstring promised a build "well under a second".
This feature does the three things the GM approved, in order, each measured before the next: the
search carves bare and the winner alone is finished (the map may shift slightly - the GM's standing
relaxation); the two per-candidate walks over the supply strokes are indexed, exactly; the seam
passes stop rebuilding a shapely polygon per plot per look. The map-changing step is judged by the
gate's placement tests and a `settlement-review` pass over the pool, not by a manifest diff.

## Functional requirements

- **FR-001 The search carves bare; the winner is finished once.** `build_comb` is split into the
  CARVE (skeleton, threads, march, drain, brook, clip, canal pieces, the carve, the envelope, the toe
  and hem) and the FINISH (seam closing, the acreage, the dry plots and beans) with one body:
  `build_comb` = carve then finish, so every other caller is unchanged. `fit_field`'s search
  (`_fit_at_aspect`) measures each guess on the CARVED plots (`net_acres`, `tail_dangles`,
  `net_bends_acutely` read nothing the finish adds), keeps the best carved state, and finishes it
  exactly once - the same random state the inline finish would have consumed, so a search that picks
  the same multiplier produces the same map. The docstring's "costs well under a second" is replaced
  by what is measured. The acreage the search sees is pre-seam; research R2 records how far it sits
  from the finished acreage on the pool's hamlets and whether any map's winner changed.
- **FR-002 The supply-stroke tests are indexed, exactly.** `supply_bank_clearance` (86,000 calls per
  roll, every segment of a stroke per call) is answered from a per-stroke segment index for its three
  callers - `_clear_supply`, `_quad_in_supply` and the hem's `_bank` - with the same verdict: the
  nearest segment within the caller's own reach (half-width + bank margin + slack) decided by the
  same arithmetic, and a point no segment governs within that reach reported as clear exactly as the
  full walk would have reported it. The `_quad_in_supply` edge walk keeps its 3 px step and its bbox
  gate. Verdict-equivalence is proven by a unit test against the linear walk on a synthetic stroke;
  the maps do not move for this step.
- **FR-003 The seam passes build one geometry per plot.** `_trade`, `_absorb`, `_unjog` and the
  pocket passes (`waterfields/seams/`) stop constructing `Polygon(plot["poly"]).buffer(0)` on every
  look: a plot's shapely geometry is built once per pass and invalidated when the plot's ring changes;
  a neighbor search over all plots (shared-boundary length, bounds overlap) goes through a SPATIAL
  TREE (`shapely.STRtree`) rather than a scan - the GM's words, *"finding neighbors through a spatial
  tree instead of a scan"*; a bounds prefilter may sit in front of the tree, never in place of it.
  Verdicts identical where the pass is a pure predicate; where a pass mutates plots, the same sequence
  of mutations, so the finished plots equal the step-2 plots (research R4 measures it on the reference
  hamlet and the pool). Where they differ, the map has moved and FR-005 governs.
- **FR-004 Each step is measured before the next.** The stage profile of seed 4 after each step
  (`make map PROFILE=1` and `make perf-profile STAGE=field`) in research R2-R4, the ROLL TOTAL
  beside the stage each time; the bookends `220-start` (taken on unmodified code) and `220-end`; a
  from-scratch rendered roll after; the green gate's time beside its predecessor (R5). A step that
  buys less than expected is reported as such; the expected outcome the GM approved - the field from
  about 5.4 s to under 3 s AND the whole roll from 10.2 s to around 7.5 s after step 1, the field near
  2.4 s after step 2 - is the yardstick, not a promise: the measured numbers are reported against it.
- **FR-005 Verification of ANY step that moves a map.** After every step - FR-001, which is expected
  to move maps, and FR-002/FR-003, which are not, but are checked the same way - every pool hamlet is
  regenerated (`make maps`); the gate's placement tests and seed tests are the rules check (a plot that
  overlaps water or a bund that crosses a channel fails the gate, as it always has - the GM's *"so long
  as nothing ends up overlapping, which isn't supposed to overlap"*); and a `settlement-review` pass
  runs over every hamlet whose manifest moved at any step, dispatched beside the gate (`make verify`),
  its findings fixed under Principle XIV before the feature lands. A map that did not move at any step
  is the exhibit the GM already accepted and needs no review; the manifest comparison SCOPES the
  review, it never judges the map.
- **FR-006 Tests, under the floor.** The carve/finish split is tested (a finished carve equals a
  `build_comb`; `fit_field` finishes exactly once - a counting monkeypatch); the stroke index's
  equivalence test; the seam passes' existing tests (`tests/waterfields/test_seams.py`,
  `tests/gate/test_paddy_fabric.py`) stay green; 100% over everything added.

## Success criteria

- **SC-001** `stage_field` and the roll total on seed 4 reported after each step against the GM's
  yardstick (field under 3 s and the roll around 7.5 s after step 1; the field near 2.4 s after step
  2); the bookends recorded; band 0 or the records a band owes.
- **SC-002** `make done` green at 100%; every map that moved at any step reviewed and its findings
  fixed; no map moved for step 2.
- **SC-003** The search finishes one comb per roll, proven by test.

## Decisions Recorded

- **D1 - the search measures the carve, not the finish.** The finish conserves ground (the trades and
  absorptions hand the same polygon across a wall; pockets are planted from bare floor inside the
  envelope), so the pre-seam acreage is within the search's 6% tolerance of the finished one on every
  map measured (R2 records the numbers). Where a map's winner changes, the map changes - accepted
  under the GM's standing relaxation, verified per FR-005.
- **D2 - the three steps in the GM's order, each measured, all three implemented.** The GM approved
  *"one feature with those three steps in that order, each measured on the reference hamlet before the
  next"*; a step the measurement shows buying less than expected is still implemented and its result
  recorded - the measurement orders the work and reports it, it does not retire a step.
- **D3 - the carve itself stays.** Under a second would also need the sector-row carve reworked
  (research R1: 26% of a build); the GM's approved assessment named it as possible, not planned. It
  is recorded in R4 as the next lever with its measured share.
