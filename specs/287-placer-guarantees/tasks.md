# Tasks - feature 287, every finished-map rule guaranteed by its placer

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (M1-M9, P0-P9, D1-D12). The rules: [`plan-rules.md`](plan-rules.md) and
`design/*.json` (a rule is `area:id`). Each owner task lands its rules' guarantees with a unit test of the placer on
constructed inputs including the violating case (FR-004), and retires the tests its design rows name (FR-007).

## P0 - Measurements owed

- [x] T01 [US1] P0: the polder's two failures read from the record (research R5); seed 31's yard over a paddy; the belt cases D8 leaves; the field pond's knob (D9); the seats D2 refuses (households unseated today over cohort 1-48, the probes and the pool); the board terminal counted once the strict caption predicate exists (labels L4, D12)
      research: rendering
      verify: DONE. DONE (research R5): the polder's two failures closed on record, W48 an excuse to remove; every map of pool and cohort 1-48 seats all households today, eight by re-rolling; the field pond is rolled (D9 applies); the belt leftovers, D2's refusals and the board terminal are counted where their mechanisms land (P5, P3, P6)

## P1 - The shared mechanisms, no placer changed yet

- [x] T02 [US1] M1: `waterfields/ring_rules.py` - every paddy-ring rule as one predicate, each tested against the test body it replaces
      research: rendering
      verify: DONE. DONE: waterfields/ring_rules.py (needle, too_small, overcount, staircase, self_crossing, arrowhead, narrow/working_width, dart, under_island, crosses_pond_rim, supply_intrusions, collector_crossings; ring_violations); tests/waterfields/test_ring_rules.py 14 tests, 100% of the module; the gate tests call the predicates; width and dart thresholds labeled GUESS pending T13's research pass
- [x] T03 [US1] M1: `hamletgen/ways/law.py` - every lane rule as one predicate (the 30 ft ford constant, `_deck_corners_clear` for decks), each tested against its old test body
      research: rendering
      verify: DONE. DONE: hamletgen/ways/law.py (19 ways rules + W01 via unreached_houses; LAW, violations(M)), tests/hamletgen/ways/test_law.py 28 tests, 100%; four test files call it; placer/test disagreements listed for P4 (bends one segment vs whole run, the weaker service set, the connector hairpin constant); pool findings for P4: Kuwabata hairpin and lateral-ditch planks, Mizuguchi needle join
- [x] T04 [US1] M1: the one-predicate fixes where placer and test disagree (wells' spacing, the eave gap on a turned house, the pond's rim, the flooded tint's ring, the woodland's dry sample, the drip lines, the same-bank test)
      research: rendering
      verify: DONE. DONE: well_gap_to_dwellings, ring_meets_ellipse, the raw-ring needle for the tint, crosses_a_stream, eave_gap - each read by placer and test, unit-tested where they disagreed
- [x] T05 [US2] M2: `brook.py:finished_course` and `round_the_brooks` moved after `stage_sink`, the pool regenerated and every moved map recorded
      research: rendering
      verify: DONE. DONE: finished_course and round_the_brooks at the end of stage_sink; the ways route the first-drawn course; the pool regenerated (research R6): Inashiro, Kashikawa, Mizuguchi re-seat, all seat every household in one roll; two Mizuguchi rules fail until P4/P6 guarantee them
- [x] T06 [US2] M6: the view decided once at the end of `stage_hinterland`; `stage_frame` takes it
      research: rendering
      verify: DONE. DONE: the view decided once after the belt is planted (content_view, frame_for, plan.view; stage_frame takes it, records view_drift); the pool's five views and belts identical to before; no drift
- [x] T07 [US1] M7: the recorded marsh outline is the drawn marsh; every marsh test reads it
      research: rendering
      verify: DONE. DONE: drawn_ground records the marsh the reeds are drawn on; marsh_ground the one reading (18 readers swept); the pool's toe marshes shrank to their drawn ground
- [x] T08 [US1] M9: `sweep/harness.py` - the pool and cohort 1-48, plain and with 284's A* and field-search probes, every M1 predicate, failures and re-rolls counted; its first run recorded as the baseline
      research: rendering
      verify: DONE. DONE: sweep/harness.py (law.violations, ring_violations per ring, 102 census tests called per manifest; 16 not yet runnable, listed); baseline.json at cc39f599a - 0 of 53 clean either pass; 8 maps re-roll; the belt-depth test raises StopIteration on cohort 20 (a test defect to fix with its predicate)

## P2 - Water

- [x] T09 [US1] `hamletgen/water/brook.py` - water:W01, water:W02, water:W03, water:W04, water:W06, water:W07, water:W08, water:W09
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T10 [US1] `settlement/rolling/fit.py` - water:W05, water:W54, water:W55, water:W56
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T11 [US1] `hamletgen/sink.py` - water:W10, water:W11, water:W12, water:W49
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T12 [US1] `waterfields/comb.py` - water:W13, water:W14, water:W15, water:W31, water:W36
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes; water W36 is the winter-crop knob (R7, research/fields/165)
- [x] T13 [US1] `waterfields/seams/close.py` - water:W16, water:W17, water:W18, water:W20, water:W21, water:W22, water:W23, water:W24, water:W26, water:W27
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes; water W26/W27 recorded, not enforced (R7, a guess held open)
- [x] T14 [US1] `waterfields/polder.py` - water:W19, water:W44, water:W48
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T15 [US1] `waterfields/seams/pockets.py` - water:W25
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T16 [US1] `settlement/fields/features.py` - water:W28, water:W29
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T17 [US1] `settlement/fields/comb.py` - water:W30, water:W33, water:W37, water:W38
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T18 [US1] `hamletgen/water/fit.py` - water:W32, water:W39, water:W59
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes; water W39 a recorded drop on the hamlet path (R7)
- [x] T19 [US1] `waterfields/carve.py` - water:W34
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T20 [US1] `waterfields/furrows.py` - water:W35
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T21 [US1] `settlement/land/dikes.py` - water:W40, water:W41
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T22 [US1] `hamletgen/water/polder.py` - water:W42, water:W45, water:W46, water:W47
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T23 [US1] `hamletgen/frame.py` - water:W43
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T24 [US1] `hamletgen/pondstock.py` - water:W50, water:W51
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T25 [US1] `settlement/finish.py` - water:W52
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T26 [US1] `overlap/matrix.py` - water:W53
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T27 [US1] `settlement/water_ways/lanes.py` - water:W57
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T28 [US1] `hamletgen/hinterland/frame.py` - water:W58
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes

## P3 - Homesteads (M5, and M3's seat half)

- [x] T29 [US1] M5: the household quota table keyed on seat order and the guaranteed parts inside the envelope
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T30 [US1] M3 (seat half): the exit strip and each house's access corridor reserved at seating; the cohort 1-48 and the pool measured with it alone (households seated, seats refused, `unreached_houses`)
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T31 [US1] `settlement/shrines_wells/byres.py` - homes:H01
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T32 [US1] `none - the producer was removed; census ` - homes:H02
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T33 [US1] `settlement/rolling/fit.py` - homes:H03, homes:H44
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T34 [US1] `hamletgen/homesteads/stages.py` - homes:H04, homes:H05, homes:H14, homes:H28, homes:H16
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T35 [US1] `settlement/houses.py` - homes:H08, homes:H17, homes:H45, homes:H06
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T36 [US1] `settlement/rolling/place.py` - homes:H18
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T37 [US1] `settlement/homestead_parts/yards.py` - homes:H07, homes:H21, homes:H22, homes:H23, homes:H24, homes:H25
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T38 [US1] `settlement/homestead_parts (_yard_dims, ` - homes:H19
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T39 [US1] `yards.py` - homes:H20
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T40 [US1] `hamletgen/homesteads/wells.py` - homes:H09, homes:H10, homes:H11, homes:H12
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T41 [US1] `settlement/farm_fixtures.py` - homes:H13
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T42 [US1] `hamletgen/homesteads/fixtures.py` - homes:H32, homes:H33, homes:H34, homes:H35
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T43 [US1] `hamletgen/cluster.py` - homes:H30
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T44 [US1] `hamletgen/plan.py` - homes:H31
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T45 [US1] `hamletgen/water/fit.py` - homes:H15
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T46 [US1] `hamletgen/burial.py` - homes:H36
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T47 [US1] `hamletgen/ways/serve.py` - homes:H37
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T48 [US1] `hamletgen/ways/sweeps.py` - homes:H38, homes:H39, homes:H40
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T49 [US1] `hamletgen/ways/web.py` - homes:H41
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T50 [US1] `serve.py` - homes:H42
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T51 [US1] `settlement/homestead_parts/stands.py` - homes:H43
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T52 [US1] `settlement/_geom/primitives.py` - homes:H26, homes:H27
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T53 [US1] `compound.py` - homes:H29a, homes:H29b
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T54 [US1] `labels/placer.py` - homes:H29c
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes

## P4 - Ways (M3's web half, M4)

- [x] T55 [US2] M4: `settle_the_web` as the web's last pass, the crossing-squaring moved into it; its rounds, seconds and lanes cut per pool map measured
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T56 [US1] `settlement/rolling/fit.py` - ways:W01
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T57 [US1] `settlement/city/bridges.py` - ways:W02, ways:W13, ways:W14, ways:W15
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T58 [US1] `hamletgen/ways/bund.py` - ways:W03
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T59 [US1] `hamletgen/ways/settle.py` - ways:W04, ways:W05
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T60 [US1] `hamletgen/ways/sweeps.py` - ways:W06
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T61 [US1] `settle.py` - ways:W07, ways:W08, ways:W09, ways:W10, ways:W12, ways:W16, ways:W17, ways:W18, ways:W19, ways:W20, ways:W21
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T62 [US1] `hamletgen/ways/checks.py` - ways:W11
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T63 [US1] `joints.py` - ways:W22
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T64 [US1] `hamletgen/ways/track.py` - ways:W23, ways:W25
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T65 [US1] `hamletgen/ways/clearance.py` - ways:W24
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T66 [US1] M3 (web half) and the re-roll removed: `generate`'s re-roll loop and its machinery deleted with the tests of it (FR-002, FR-007)
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes

## P5 - Woods and cover

- [x] T67 [US1] `settlement/homestead_parts/stands.py` - woods:W01, woods:W02, woods:W03, woods:W05, woods:W06, woods:W15, woods:W16, woods:W17, woods:W18, woods:W20, woods:W22, woods:W23
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T68 [US1] `hamletgen/hinterland/parcels.py` - woods:W04, woods:W12, woods:W14, woods:W26
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes; woods W26's bounded-by half held for the GM (R7)
- [x] T69 [US1] `settlement/land/wet.py` - woods:W07, woods:W08, woods:W09
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T70 [US1] `hamletgen/hinterland/stages.py` - woods:W10, woods:W25
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T71 [US1] `settlement/land/cover.py` - woods:W11, woods:W13
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T72 [US1] `hamletgen/hinterland/belt.py` - woods:W19
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T73 [US1] `stands.py` - woods:W21
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T74 [US1] `hamletgen/hinterland/bamboo.py` - woods:W24
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes

## P6 - Labels, boards and the generated Mode A sheets

- [x] T75 [US1] `settlement/structures/fixtures/siting.py` - labels:L1, labels:L2, labels:L3, labels:L4, labels:L11, labels:L12
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T76 [US1] `labels/obstacles.py` - labels:L5, labels:L6
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T77 [US1] `settlement/structures/captions.py` - labels:L7
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T78 [US1] `labels/placer.py` - labels:L8, labels:L10
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T79 [US1] `settlement/finish.py` - labels:L9, labels:L14, labels:L17, labels:L18
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T80 [US1] `labels/hand_sheet.py` - labels:L13
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T81 [US1] `compound.py` - labels:L15
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes
- [x] T82 [US1] `settlement/fields/comb.py` - labels:L16
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes

## P7 - One registry

- [x] T83 [US1] M8: the indexed registry every footprint is recorded through, refusing by the overlap matrix; every placer offers only what it admits; the matrix rule guaranteed (water:W53)
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes

## P8 - Excuses and retirements closed

- [x] T84 [US3] FR-006: `ACREAGE_SHORT`, the seed-43 strict xfail, the polder soak carve-out and R3's test-side excuses removed; each seed asserts its rule
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes; R8 and the T84/T85 commit
- [x] T85 [US3] FR-007: every test the refactor made unnecessary retired with the cost it saved; every kept map-reading test named with the correctness it guards (SC-005)
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes; R8: 84+ tests retired with their cost, every kept map-reading test with its reason

## P9 - Acceptance

- [x] T86 [US1] SC-003: the sweep - no predicate fails and no roll re-rolls, plain and under the probes
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes; R11
- [x] T87 [US1] SC-004: the pool regenerated with every moved map's before and after in the research; `make cohort N=24` with zero failing seeds; `make done` green
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes; R6 and the pool regenerated at the green gate
- [x] T88 [US1] SC-001, FR-008: the closing census by `census_select.py` and the same judgment - every placement rule guaranteed, its mechanism named
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes; R12 (162 guaranteed, 13 recorded decisions of 175)
- [ ] T89 [US3] SC-005, SC-006: `make durations` and `make audit` against research R4; `make perf LABEL=287-end` and `make perf-report AGAINST=287-start`
      research: rendering
- [x] T90 [US1] The record: `dev/performance.md` / `dev/gate.md` on the guarantees and what the gate now tests; future-work entries the feature closed marked closed
      research: rendering
      verify: DONE. verified at ade061bc7: research R12 names each rule's placer and unit test (the violating case included); make done green; cohort 1-60 60/60; the R11 sweep clean plain and under the 284 probes; dev/gate.md, dev/performance.md, future-work closed entries
