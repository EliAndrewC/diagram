# Tasks - feature 387, scale the placement loops

Every task changes how a verdict is computed, not what is drawn or where: nothing physical is decided, so each is
`research: rendering`. Each change is held to the old form's answers by an equivalence test (plan, Summary; FR-007).

## Occasions

- none: amendment 1 moves maps but changes no rule - the merges keep `verdict` and may now find a split part as a partner; the
  wells keep every 0196/0072 rule and are found by a cheaper search - so no element is re-placed by substantially different rules
- none (as landed before amendment 1): no glyph, caption or placement rule changes - each site keeps the old verdicts, proved call by call by its equivalence
  test; a map that moves anyway is judged by the cohort and the gate (FR-007), and its move named in the report

## Tasks

- [x] T01 The way tree judged on what a candidate adds (plan T01, D1; FR-001): `ways/tree_base.py` holds the base tree per content state; `admits` asks only the candidate's host, lane, chain and the ends it changes; equivalence test red without the base
      research: rendering
      verify: DONE. tree_base: the base tree kept and extended; tree lays per candidate 7.9/13.7/21.4 -> 1.9/1.8/1.4, fronting pairs -> 0; equivalence: test_tree_base and the soak (admits old vs new, every call, 5 rolls); make done green
- [x] T02 The web's field way best-first and the knots' local counts by the edited lanes (plan T02, D2a, D2b; FR-002): `field_runs` stops once no nearer point is left; `settle_knots.judge` re-asks `doorstep_ends`, `doubled_tails`, `shadows` and `needle_loops` only where the edit can change them (`way_outs` stays whole); equivalence tests
      research: rendering
      verify: DONE. field_runs best-first by distance band, nearest first (run_on_target 2596/4084/8552 -> 512/504/568); knots' doorstep/doubled/shadows/needle counts by their edits, way_outs whole; equivalence: test_corridors, test_web_counts, the soak; make done green
- [x] T03 The cell merges measure each live neighbor once (plan T03, D3; FR-003): owners deduplicated before `shared_length`; the split-part defect recorded and measured; equivalence test
      research: rendering
      verify: DONE. each live neighbor measured once, a pair's measure kept while neither cell changes (15.7 -> 7.6 a merge at 40 hh); the split-part defect measured by the soak (42 of 502 at 40-4, 20/160 at 40-39, 10/126 at 40-25, 0 at 15-4) and reported; equivalence: test_settle_neighbors_387 and the soak; make done green
- [x] T04 The sun keep-outs keyed on the registries' versions (plan T04, D4; FR-005): yards and gardens `Indexed`, `Indexed.touch()` at the in-place bed shift, the version key checked against the content key under the suite, the sun-box grid; equivalence test
      research: rendering
      verify: DONE. the plots' sun boxes keyed on the registries' versions, Indexed.touch at the bed shift, the content key checked under the suite, a grid of the boxes (plot_box per ask 23/47/88 -> 0); equivalence: test_sun_keepouts_387 and the soak; make done green
- [x] T05 The bamboo strip check asks an index (plan T05, D5; FR-006): the per-pass grid in `household_bamboo`, `_strip_blocked(near=...)` at both callers (the strips and the field pit), seated strips added as seated; equivalence test
      research: rendering
      verify: DONE. StripNear at both callers, the straight scan only in the test oracle (items per candidate 212/431/629 -> 31/36/40); equivalence: test_strip_near_387 and the soak; make done green
- [x] T06 Measure, sweep and record (plan T06; FR-009, FR-010, SC-001 - SC-004): the counts at 10/20/40 after into `measurements.json`; the soak equivalence run (`make soak`); `make cohort`, `make maps`, `make done`; the end bookend; `dev/performance.md`'s section
      research: rendering
      verify: DONE. counts after (m:counts-after: tree lays/candidate 1.9/1.8/1.4, fronting pairs 0, run_on_target 512/504/568, merges 3.2/3.1/7.6 a merge, plot_box 0, strip items 31/36/40); soak equivalence 5 rolls green; cohort 16/16; make maps byte-identical; make done green; end bookend and the pre-feature engine back to back: the five stages 13.5 -> 12.2 s at 40 hh (-10%), flat at 10-20 (m:five-stages-ab); dev/performance.md section
- [x] T07 Land (SC-003, SC-005): `make cohort-landing`, the gated push, the feature report; the landing report carries FR-004's withdrawal (measurement, 297 R9), FR-002's and FR-003's restated premises with what was measured, and FR-003's split-part defect with its frequency
      research: rendering
      verify: DONE. landing cohort on this engine: 54/54 (dev/cohort-log/20261018T121355Z, fresh 6 of 48); report.md written with the GM's section (SC-005); the gated push follows
- [x] T08 (amendment 1) The merges find every live neighbor (plan T08, D8; FR-011): the neighbor index kept current as split parts are added; the split-part count 0 in the soak; every kept basin passes `verdict`; unit test red before
      research: rendering
      verify: DONE. Fabric.late keeps the cells added after the index and neighbors asks them by box; unit test red without it; soak: split parts missed 0 on 15-4, 40-4, 40-25, 40-39, 40-47 (was 42/502, 20/160, 10/126); Sawada's paddy cells moved, pool gate clean; cohort 16/16
- [x] T09 (amendment 1) The well seating scales (plan T09, D9; FR-012): each candidate seat's nearest houses, wall gap, pair look-ahead and verge answered from what is near it or once a pass; tests against the old forms where the answer is kept
      research: rendering
      verify: DONE. well_seats.SeatSweep (one distance array a call, the wall gap of the near houses), PairAhead (vectorized look ahead, the old pair_keeps_ten the test's oracle), the crop box once a well landed, the verge legs indexed, numpy loaded at seat time; tests against the old forms (test_well_seats_387, 300-seed sweep); lane_wells 15.1 -> 2.2 s, appurtenances 2.9 -> 0.3 s at 40 hh (m:wells-ab); claims IN-STEP or relabeled, the belt drift carried to 384; make done green
- [x] T12 (amendment 1) The guidelines and checklists say speed may always change maps (plan T12; FR-013): the constitution (Principle X clause 15, v2.31.0), root CLAUDE.md, the engine's dev loop, dev/performance.md, docs/efficiency-tooling.md, the spec and plan templates, the speckit-specify checklist
      research: rendering
      verify: DONE. the GM's 2026-10-18 permission in the constitution (Principle X clause 15, v2.31.0), root CLAUDE.md, l7r/diagram/CLAUDE.md, dev/performance.md, docs/efficiency-tooling.md, the spec and plan templates and the speckit-specify checklist - a permission, not a ban; spec FAITHFUL round 3
- [x] T10 (amendment 1) Measure, sweep and record (plan T10; SC-006 - SC-008): the counts and the two well stages' time before/after, the soak, `make cohort`, `make maps` (moved maps committed), `make done`, `dev/performance.md`
      research: rendering
      verify: DONE. counts (m:counts-wells-*: lane_wells one-at-a-time distances 10.0M -> 1.1M, wall measures 886,600 -> 27,492 at 40 hh); soak green, split parts missed 0; cohort 16/16; make maps clean, Sawada moved and committed; end bookend and main's engine back to back (m:wells-ab: 40-hh roll 30.7 -> 15.1 s); dev/performance.md; make done green
- [ ] T11 (amendment 1) Land: the claims of the touched code re-judged, the landing cohort, the gated push, the report
      research: rendering
      verify:
- [ ] GM review (make gm-reviewed F=387) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
