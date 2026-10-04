# Tasks: no ways placed before the homesteads (feature 320)

**Input**: plan.md (D1-D6)

## Occasions

- placement-changed: village lane - no way is reserved before the houses; the track out is laid first once they stand, then each household's way in the gaps, joined to it (plan D1-D3)
- glyph-redrawn: marsh - a short ripple (60-90 ft) added to the waved outline so no stretch runs straight past what a visible edge may (the GM, 2026-10-04: "Fix marsh ends first")

## Tasks

- [x] T01 the baseline: the 320-start bookend on main (FR-005)
      research: rendering
      verify: DONE. 320-start bookend taken on main 264a24ca5 (dev/perf-log 20261004T043603Z)
- [x] T02 the seating with nothing reserved: no exit strip, no field's corridor, the region's reach from the anchor; the no-reservation test and the constructed open/closed test (D1, FR-001, FR-002, SC-001, SC-002)
      research: rendering
      verify: DONE. nothing reserved at seating (SC-001 test in test_household_ways_320.py), the region's reach from the anchor clipped to the window; SC-002 constructed test
- [x] T03 the track out first, then the households' ways joined to it; the reservations split (D2, FR-003)
      research: rendering
      verify: DONE. superseded by amendment 2 / T09: the track out chosen once, then the ways laid to it
- [x] T04 the strip's branches deleted with their tests; the field path left to the web (D3, D4, FR-003, FR-004)
      research: rendering
      verify: DONE. strip branches and the field's corridor deleted with their tests; the field way drawn by the settle (reach.settle_field), routed from six starts per ford
- [x] T05 the reference spec and the bookend seeds reach every household; the cohort against main; `make done` (FR-004, SC-003)
      research: rendering
      verify: DONE. cohort 36/36 (cohort320e.log), every pool hamlet rolls, Inashiro and Kuwabata every household a way of its own; make done green
- [x] T06 the bookends and the perf records their band owes; put to the GM were the reservations faster (FR-005, SC-004)
      research: rendering
      verify: DONE. 320-end bookend band 1 (main -9.8%, every leg faster in total); explanation confirmed consistent by perf-audit (dev/perf-log 20261004T144425Z); the reservations not faster (audit: 0.6% with the entrance set aside)
- [x] T07 the record and the claims: 0081's drawing page, the changed units' claims, their checks; the occasions' reviews (D5, FR-006, SC-005)
      research: rendering
      verify: DONE. 0081 and 0074 record checks answered; claims-owed none; claims-followup.md filed; glyph checks marsh PASS, village lane PASS (round 4)
- [x] T08 the marsh ends (Amendment 1): the short ripple in the shaped outline and its guarantee test (D6, FR-007, SC-006)
      research: rendering
      verify: DONE. WAVE_SHORT_FT ripple; test_no_stretch_of_a_shaped_outline_runs_straight... passes; marsh glyph PASS
- [x] T09 one decision for the track out (Amendment 2): chosen once the last house stands against the homesteads as seated, recorded, the ways laid to it, drawn as chosen (D2, FR-008, SC-007)
      research: rendering
      verify: DONE. choose_track_out once when the last house stands, recorded way_out_track, drawn as chosen (SC-007 test); Inashiro no hairpin; glyph village lane PASS
