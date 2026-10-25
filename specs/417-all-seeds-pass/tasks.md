# Tasks - feature 417, all seeds pass

## Occasions

- none yet: each engine task names its map delta's occasions in its Approach (`make verify`)

## Tasks

- [x] T01 The baseline: 1,000 fresh seeds at main by form and cause, and `make fresh-tally` (D1, D2; FR-001)
      research: rendering
      verify: DONE. landed: make fresh-tally (2 tests, red without); R3: 125 of 1,000 fresh seeds fail at main 14214b115 (12.5%) - nucleated 11%, dispersed 4%, linear 28%; WebRefused 49, lane_knots 31, SiteRefused 13, row_rules 11
- [x] T02 The hold made: `make task-start` refuses a task of a feature ON HOLD until an open feature closes; `HOLD_OK` only for a non-engine task (D4; FR-010)
      research: rendering
      verify: DONE. landed: make task-start refuses a held feature's task, naming the feature it waits on; an engine task (an engine path or module named, research: physical, or nothing named outside the engine) has no escape; HOLD_OK starts a non-engine one. 405, 372 and 384 are held by 417 (a wrapped status line read whole); 7 tests, red without the refusal and without the paragraph read; live: 405 T106 refused
- [x] T03 The inventory: every repair pass, audit-only rule, rule coded twice, mid-map check and refusal where room is the remedy, each with where it is and the point it breaks; each breaking entry filed here as an engine task; the principle's text drafted for the GM (D3, D6; FR-002, FR-003)
      research: rendering
      verify: DONE. R2: three inventories kept verbatim in inventory/, a sample of each checked against the code, the three cross-package searches run by the session (inventory/cross.md) and reconciled; twelve groups filed as T04-T15; R4: the principle's draft text for the GM
- [x] T04 (R2 G7) One stream-crossing rule: `cohort_audit.parts_across_brook`'s own segment test replaced by `_geom/water_index.crosses_a_stream`, the placers' predicate (FR-006; no map moves)
      research: rendering
      verify: DONE. landed: landed: cohort_audit.parts_across_brook asks crosses_a_stream, the placers' predicate; its own segment test deleted (D12); 27 audit tests, the new one pins the predicate asked
- [x] T05 (R2 G1) One lane rule, one predicate: each rule `ways/` codes two to seven times made one named predicate or constant, at the lane law's value where the copies differ, in `l7r/diagram/hamletgen/ways/` (FR-005, FR-006)
      research: rendering
      verify: DONE. landed: landed: the 40 ft tail past a meeting (six copies), the 25 ft join (three), the knot margin, the 100 ft serve, route.py's bend literals and the 6 ft field reach each read one constant (D13-D16); a test checks each copy is assigned from its constant (red on a bare 40.0); Inashiro regenerated unchanged against HEAD; claims round 27 recorded, four findings on unchanged code carried as T19, T23-T25 (arbiter ask 417-T05-claims)
- [ ] T16 (R2 G1, second part) The lane rules whose copies DIFFER made one at the rule's recorded value, in `l7r/diagram/hamletgen/ways/` - the doubled tail (the sweep's 25 deg against the law's 15, the page's 20; 405 T101's known gap, held), the shadow (four bodies), the hook (five), the reach to a farmhouse (three), the network tolerance (25 ft against 4 ft), the foul, the dangling end, the street end, the link width (FR-006). Set down 2026-10-25 under D11 for the doubled tail: no page records the value its two roles should share; each other rule waits on its own recorded value
      research: rendering
- [ ] T06 (R2 G2) The web laid by the law: an ordinary lane admitted whole by the lane law before it is drawn; the passes after the lay and the settle's repair steps deleted, in `l7r/diagram/hamletgen/ways/` (FR-004, FR-006)
      research: rendering
- [ ] T07 (R2 G3) The ways' drops and refusals: ordinary lanes dropped, `WebRefused`, `NoDryExit`, spurs given up, angle rules waived, wood seats released, in `l7r/diagram/hamletgen/ways/` (FR-007)
      research: rendering
- [ ] T08 (R2 G4) Seating room: `SiteRefused` on a short margin, the dry-spell give-up, the rank rounds' drop, pinched passages, in `l7r/diagram/hamletgen/homesteads/` (FR-007)
      research: rendering
- [ ] T09 (R2 G5) The row village's rules into the row placer: `row_rules`, `water_rules`, `bamboo_mismatch` asked of candidates; wells' dry-household check out of the run, in `l7r/diagram/hamletgen/homesteads/` (FR-005, FR-006)
      research: rendering
- [ ] T10 (R2 G6) The grove rules into the grove placers: the five audit-only grove rules asked before placing, `fixtures_on_groves` and `gardens_east_shaded` one predicate each; the belt, copse and persimmon repairs deleted, in `l7r/diagram/settlement/homestead_parts/` (FR-004, FR-005, FR-006)
      research: rendering
- [ ] T11 (R2 G8) The brook, sink, field and polder placed by their rules: courses not repaired then judged, the field not judged as a finished net, the polder's relaxed wander, in `l7r/diagram/hamletgen/water/` and `l7r/diagram/hamletgen/sink.py` (FR-004, FR-006, FR-007)
      research: rendering
- [ ] T12 (R2 G9) The paddy cells cut by their rules: cells not cut then merged or left bare, rings not split and welded after, twins and stubs not drawn, the needle one predicate, in `l7r/diagram/waterfields/` (FR-004, FR-005)
      research: rendering
- [ ] T13 (R2 G10) The hinterland and land placed by their rules: dike trees not thinned after, holes not filled to a share in the run, the belt's ladder, parcels, marsh and wet lanes, in `l7r/diagram/hamletgen/hinterland/` and `l7r/diagram/settlement/land/` (FR-004, FR-006, FR-007)
      research: rendering
- [ ] T14 (R2 G11) The overlap registry: the per-stage resync and the record-time refusal as backstop only, the hand mirrors made one, in `l7r/diagram/overlap/` (FR-006)
      research: rendering
- [ ] T15 (R2 G12) The rest: labels' repair and least-cost seat, beads dropped twice, bridges' reseat and refusal, byres' relaxed tiers, wells and pond-stock rules asked twice, the cluster's belt and dry-exit copies, in `l7r/diagram/` (FR-004, FR-005, FR-006, FR-007)
      research: rendering
- [ ] T17 (R2 G6, first part) A fixture in a grove band, one predicate: `homesteads/fixtures._flexible_clear` and `rolling/fit._fixtures_in_bands` ask `grove_rules.fixture_on_band`, in `l7r/diagram/` (D17; FR-006; no map moves)
      research: rendering
- [ ] T18 (R2 G11, first part) The overlap matrix's dead mirrors deleted: `forest_reveal_x`, `FOREST_REVEAL_FT`, `CANOPY_STRUCT_KEYS` (27 keys against the engine's 34), in `l7r/diagram/overlap/matrix.py` (D18; FR-006; no map moves)
      research: rendering
- [ ] T19 (T05's claims round, DRIFTED; arbiter ask 417-T05-claims) The track out stops in open country: `fabric._pull_back_to_service` leaves an inner end alone when nothing is within `_LANE_JOIN_FT`, and refuses a snap that would cross the fabric, against 0081's "It never stops in open country" (`evidence/impl-T05.txt`), in `l7r/diagram/hamletgen/ways/fabric.py` (FR-004; a behavior change - waits for the GM's fixing pass, D11)
      research: rendering
- [ ] T23 (T05's claims round, MISLABELED; arbiter ask 417-T05-claims) Four labels corrected: `bund.cut_stub_ends#a stub that reaches the bund kept` to GUESS 0014 (6 ft); `sweeps._bridge_collinear_breaks#bridge width` and `sweeps._join_orphan_ways#link width` to CONVENTION 0081; `sweeps._sweep_doubled_remnants#doubled lane dropped` to cite 0081 (`evidence/impl-T05.txt`), in `l7r/diagram/hamletgen/ways/` (label-only)
      research: rendering
- [ ] T24 (T05's claims round; arbiter ask 417-T05-claims) A doubled lane is dropped whole where 0081 cuts it where it comes alongside and lets it meet the other as a T: `sweeps._sweep_doubled_remnants`, in `l7r/diagram/hamletgen/ways/sweeps.py` (FR-004; a behavior change - waits for the GM's fixing pass, D11)
      research: rendering
- [ ] T25 (T05's claims round, outside the change; arbiter ask 417-T05-claims) `water_ways/_helpers.BUND_REACH_FT` is a second 6.0 of `consts_ways.FIELD_REACH_FT` (read by `bund.cut_stub_ends` and `geom.end_serves`); `cut_stub_ends` tests its tail with `<=` where the other two read `<` against "under 40 ft"; comments in `sweeps` still give `_LANE_JOIN_FT` as 30 where the claims say 25, in `l7r/diagram/hamletgen/ways/` (FR-006)
      research: rendering
- [ ] T20 The fresh block runs inside `make land` before the push and any fresh failure refuses, once a fresh block of 500 passes whole (FR-009, SC-005; after the last engine task)
      research: rendering
- [ ] T21 Every archetype form's seeds recorded per seed and diffed against HEAD; a newly red unrolled-form seed with no filed row or waiver refuses (FR-011, SC-006; feature 394)
      research: rendering
- [ ] T22 Close: 1,000 fresh seeds, T106's seat turn re-applied (User Story 2), the code-size delta (SC-004), the feature report
      research: rendering
- [ ] GM review (make gm-reviewed F=417)
