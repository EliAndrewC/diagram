# Tasks: grow outward, never restart (feature 318)

**Input**: plan.md (D1-D8)

## Occasions

- placement-changed: farmhouse - a nucleated cluster grows at its edge with no radius or field-reach wall, the seat nearest the field first, and no seating is thrown away (plan D1-D4)
- placement-changed: village lane - the lanes follow the houses the new growth seats (plan D2, D4)

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
      verify: DONE. one level of 16 directions x 1.0/1.5/2.0 nearest the field first, widening past the table; test_of_a_levels_seats_the_nearest_the_field_is_tried_first green; spread in research.md R1
- [x] T05 the built share reported (D6, FR-007)
      research: rendering
      verify: DONE. meta.built_share recorded on every nucleated map; test_the_built_share_is_the_homesteads_over_their_outline green
- [x] T06 the record: 0029, 0032 and 0081's drawing pages, and their record checks (D7, FR-008, SC-004)
      research: rendering
      verify: DONE. 0029, 0032, 0081 drawing pages edited; record checks answered clean (make record-owed: none owed)
- [ ] T07 `make done`, the cohort and the pool against main, the bookends with the spread, the occasions' reviews and the claims (FR-009, FR-010, SC-005, SC-006)
      research: rendering
      verify:
