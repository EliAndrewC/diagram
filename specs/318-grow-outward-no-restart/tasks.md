# Tasks: grow outward, never restart (feature 318)

**Input**: plan.md (D1-D14)

## Occasions

- placement-changed: farmhouse - a nucleated cluster grows at its edge with no radius or field-reach wall, nearer the field all else being equal, neighbors a lane's threading gap apart, and no seating is thrown away (plan D1-D4, D9)
- placement-changed: village lane - the ways are laid in the gaps between homesteads once every house stands (plan D9-D13)

## Tasks

- [x] T01 the baseline: the 318-start bookend and the cohort on main (FR-009, FR-010)
      research: rendering
      verify: DONE. 318-start bookend dev/perf-log/20261003T171426Z-318-start-main318.json; cohort and spread on main measured in research.md R1-R3
- [x] T02 no take-back: the ladder only past a margin that seats no house, the rescue, the withheld re-seat, the early stop, the 12:1 refusal and the passage re-lay removed; the no-take-back test and the constructed refusal (D1, D5, FR-001, FR-004, FR-005, FR-006, SC-001, SC-003)
      research: rendering
      verify: DONE. ladder only past a margin seating no house; rescue, withheld re-seat, early stop, 12:1 refusal, passage re-lay removed; test_a_short_margin_is_refused_and_no_house_it_seated_is_taken_back, test_a_constructed_site_too_small_for_everyone_is_refused_naming_the_shortfall, gate test_no_rolled_hamlet_took_a_seated_house_back green
- [x] T03 the field reach removed with every use; the windows on the canvas (D3, FR-003, SC-002)
      research: rendering
      verify: DONE. FIELD_REACH_FT and within_field_reach deleted with every use; windows on the canvas; test_no_distance_from_the_field_refuses_a_seat green; ways/law.py's own reach untouched
- [x] T04 the growth keeps widening, the seat nearest the field first; the order test (D2, D4, FR-002, FR-003a, SC-002a)
      research: rendering
      verify: DONE. one level of 16 directions x 1.0/1.5/2.0 nearest the field first, widening past the table; test_of_a_levels_seats_the_nearest_the_field_is_tried_first green; spread in research.md R1. SUPERSEDED by T08 (Amendments 2 and 3): main's levels, the field a tie-break within a ring
- [x] T05 the built share reported (D6, FR-007)
      research: rendering
      verify: DONE. meta.built_share recorded on every nucleated map; test_the_built_share_is_the_homesteads_over_their_outline green
- [x] T06 the record: 0029, 0032 and 0081's drawing pages, and their record checks (D7, FR-008, SC-004)
      research: rendering
      verify: DONE. 0029, 0032, 0081 drawing pages edited; record checks answered clean (make record-owed: none owed)
- [x] T07 `make done`, the cohort and the pool against main, the bookends with the spread, the occasions' reviews and the claims (FR-009, FR-010, SC-005, SC-006)
      research: rendering
      verify: DONE. make done green (cc146e2cd, 55 s incremental after full runs); cohort 30/30 against main's 30/30 (make cohort N=24); pool hamlets byte-identical through the perf fixes; 318-end bookend +11.9% band 3, perf-audit consistent and justified (20261003T203450Z / T203500Z); glyph-check farmhouse and village lane PASS round 5 on a3ada499; claims-owed none
- [x] T08 the tie-break: main's levels, rings of `TIE_RING_FT`, the field nearer within a ring; the order tests (D4, FR-003a, SC-002a)
      research: rendering
      verify: DONE. DONE. GROW_LEVELS restored, TIE_RING_FT 20 ft rings, grow_key (ring, field distance, distance); test_growth ring tie-break + tie_reordered green; tie_reordered 19-123 a map; impl-drift IN-STEP (the tie-break a GUESS naming the GM's ruling)
- [x] T09 the threading gap, pairwise for a tight seat; the gap test (D9, FR-011, SC-007)
      research: rendering
      verify: DONE. DONE. grow_gap = MIN_WEB_GAP + TIGHT_GAP_PX (20 ft), keeps_every_gap pairwise exempt for a tight seat's neighbor; test_growth gap tests green; claims IN-STEP
- [x] T10 lane ground and its one predicate; no per-seat search; the no-search test (D10, D11, FR-012, FR-013, SC-008)
      research: rendering
      verify: DONE. DONE. SeatRegion lane raster + LaneGround + opens(), the one predicate in fit/place/passage; no per-seat search (seat_reaches_tree only on a roll with no seat region, recorded as 0081's deviation); test_seat_region_297 + test_passage_317 green
- [x] T11 the gap pass and the pinch; their unit tests on constructed sites (D12, D13, FR-014, SC-009)
      research: rendering
      verify: DONE. DONE. gap_ways.lay_the_ways (flood, way_out, trace, mark_laid, pinch), every household's way owed and kept by the web; tests/settlement/test_gap_ways.py 12 green, 100% coverage; chord test vectorized and list reads, byte-identical
- [x] T12 the record: 0081 and 0029's drawing pages, the claims, their checks (D14, FR-008, SC-004)
      research: rendering
      verify: DONE. DONE. 0081/0029/0032 drawing pages; every record check answered (make record-owed UNANSWERED=1: 0); claims checked in five rounds; 5 pre-existing figure drifts and 0029/0081 wording points filed in claims-followup.md, 0029-followup.md, 0081-followup.md
- [ ] T13 `make done`, the cohort and the pool against main, the bookends (FR-010, FR-015, SC-005, SC-009, SC-010), the occasions' reviews
      research: rendering
- [ ] T14 re-checks scoped to the blocks a claim rests on: numbered blocks, rests and pages per row, page snapshots, the triage, the backfill; their tests (D15, FR-016, SC-011)
      research: rendering
- [ ] T15 the 0081 follow-ups through the scoped re-check: the four figures recorded as deviations and the two wording points, then `make claims-triage` and `impl-drift` on what it sends on (D14, D15, FR-008, FR-016)
      research: rendering
