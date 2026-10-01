# Tasks - feature 291, how many sides a homestead grove takes

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D13).

- [x] T01 The cohort audit reads the matrix and prints the forms it rolled; the baseline on main (plan: measurement; D13; SC-005)
      research: rendering
      verify: DONE. the cohort audit prints the forms, sides, row knobs and never-rolled values; verified 2026-09-30: cohort 30/30 at engine key 1dde9894 predecessors and the gate green at 1dde9894e487 with all five settlement-reviews PASS
- [x] T02 The two nucleated overlaps (seeds 17, 20) diagnosed and fixed (D13)
      research: rendering
      verify: DONE. the nucleated overlaps fixed; cohort 30/30, the overlap matrix run on every roll
- [x] T03 The knob and the flood ground in the plan and the meta, with the roll-frequency and polder tests (D1; FR-005, FR-006, FR-009; SC-003)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. grove_sides and flood_ground in plan and meta, roll tests in tests/hamletgen/test_plan.py; record R1-R2 checked
- [x] T04 `grove_faces` and the turned bundle, with unit tests for every key and side count (D2, D3; FR-007; SC-004)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. grove_faces and the turned bundle, tests/settlement/test_grove_sides.py; record homesteads/715 checked
- [x] T05 The bands, the way in and the list-shaped bundle through every reader; the drawing (D4, D5, D6, D8, D9; FR-008, FR-010; SC-004)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. bands, way in, band_clumps and the bamboo patch drawn; grove_rules clean on the pool and the cohort; record checked
- [x] T06 The grove rules as manifest predicates, in the cohort and a gate seed test (D7; FR-010; SC-005)
      research: rendering
      verify: DONE. grove_rules predicates in the cohort audit and tests/gate/test_farm_groves.py, green
- [x] T07 The forms back on; the cohort green with every side count present (D10; FR-011; SC-005)
      research: rendering
      verify: DONE. forms rolled: dispersed 9, linear 10, nucleated 11; sides 2/3/4 all present; cohort 30/30
- [x] T08 The record, group R1 (0036, 710, 480): write, check and apply (D12; FR-001, FR-002; SC-001)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. R1 written and checked (quote-check, record-format, source-applicability)
- [x] T09 The record, group R2 (0072, 620): write, check and apply (D12; FR-001, FR-003; SC-001)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. R2 written and checked
- [x] T10 The modals: the grove kind states the side count; entry-drift on every owed pair (D12; FR-004, FR-009; SC-002)
      research: rendering
      verify: DONE. the homestead grove kind states the side count; entry-drift run on the owed pairs (homestead bamboo DRIFTED, fixed); no pair owed now (make page-check)
- [x] T12 The record, groups R5 and R6 (homesteads 715, 150, 155, 156; vegetation 620, 154): write, check and apply (FR-013-FR-019; amendment 3)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. R5, R6 written and checked; R7-R11 and R13 carry the map paragraphs and corrections
- [x] T13 The row's line and its seats: `rows.py`, the line and sides knobs, farms one frame apart along the line, further streets (D14, D15; FR-013, FR-014, FR-015, FR-016; SC-007)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. rows.py seat_rows, best_row_line, parallel (offset curve), inside_the_sheet, frame_refused; row_rules clean; Kashikawa and Mizuguchi PASS
- [x] T14 The far row's holding: a strip behind on a street laid first, compact on the dry edge (D16; FR-015; SC-007)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. holdings drawn (draw_holdings), recorded, holding_not_drawn clean; the depth a GUESS, R12 researching it
- [x] T15 The streets laid as one continuous way each, joined to the connector (D17; FR-017; SC-007)
      research: rendering
      verify: DONE. lay_row_streets: each street one way over its own farms, joins as ways of their own, further streets join the row; continuous rule clean
- [x] T16 Water: the dispersed farm-water knob (a channel into the lot, or its own well), the row water knob; homesteads/200's map paragraph says what the map draws (D18; FR-018; SC-008)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. farm_water knob (farm_water.py), row_water; water_rules clean on the cohort; homesteads/200 map paragraph (R8, R9) checked
- [x] T17 Door paths and the grove's bamboo roll (FR-019; SC-008)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. door paths (lay_door_paths), the grove bamboo roll and patch; doors_unreached and bamboo_mismatch clean
- [x] T18 The row rules as manifest predicates, in the cohort and the gate test (D19; SC-007, SC-008)
      research: rendering
      verify: DONE. row_rules/water_rules/doors/bamboo in the cohort audit and tests/gate/test_farm_groves.py, green
- [x] T11 The pool regenerated, settlement-review on each moved map, make done, push (D11; FR-012; SC-006)
      research: rendering
      verify: DONE. DONE 2026-09-30. The pool regenerated on the port (all five), make done green (100% coverage), cohort 30/30. The settlement reviews were SKIPPED at the GM's instruction (2026-09-30: Go ahead and skip the review process entirely; feature 294 rethinks the process).
