# Tasks: seat before settle (feature 314)

**Input**: plan.md (D1-D5), research.md (R1-R4)

## Occasions

- none: every placement rule is unchanged - the grown seats and their routed paths are found in another order and breadth (a seat refused on its own ground before its layout, a path refused where it is searched), and the seats and paths found pass the same placer and lane law; the persimmon's sun and the well pocket's water answer exactly as before

## Tasks

- [x] T01 the `314-start` scaling bookend on the unmodified engine (base worktree)
      research: rendering
      verify: DONE. dev/perf-log/20261002T202943Z-314-start-base314.json, taken in /tmp/base314 (the spec's commit, engine unmodified): 15 hh median 4.3 s, worst 5.2 s
- [x] T02 the seat's own questions before its layout, with unit tests (D1, FR-001; US1)
      research: rendering
      verify: DONE. growth.seat_refused + next_house asked in settled_seat at every position; tests/hamletgen/homesteads/test_growth.py; research R1/R4 (round 1 alone 67.4 -> 59.9 s at 40 hh, r1 logs)
- [x] T03 the routed path refused where it is searched, the map's grid tried and withdrawn, with unit tests (D3; US2 round 2)
      research: rendering
      verify: DONE. route.py: own parts shut, first step by the household's tests, last leg by standing_ground, heuristic once a cell; the map's grid withdrawn (research R2-R4); tests/settlement/test_route_308.py
- [x] T04 the persimmon's sun ground once per rake and the indexed surface water, with tests against the predicates they replace (D4; US2 round 3)
      research: rendering
      verify: DONE. tree_shade.sun_ground/crown_in_ground, lot.water_index + wet.surface_water_within, each tested against the predicate it replaces (test_tree_shade, test_core)
- [x] T05 the rounds alternated against the base at 15 and 40 households, recorded (SC-001, SC-003, SC-004; research R3, R5)
      research: rendering
      verify: DONE. research R4: rounds 1-4 alternated against the base, 15 hh 21.3 -> 17.5 s (-18%), 40 hh 49.1 -> 30.1 s (-39%), every seed one margin; R5 the house-and-yard check priced and withdrawn
- [x] T06 the next costs named and attacked until the stopping rule holds (D5; US2 scenario 2)
      research: rendering
      verify: DONE. research R9 names every remaining cost of the 15-household stage with what an efficient process would do; R6 and R8 kept, R7 explained, R10 tried and withdrawn; the remaining lever (lanes planned before the houses) changes the GM's growth and is put to the GM
- [x] T07 the pool and the cohort against the base (FR-005, SC-002)
      research: rendering
      verify: DONE. research R11: cohort 28/30 on base and clone, the same two failures (seeds 5, 903; fixed on main by feature 310); make done green on the merged engine, every pool map regenerated and passing
- [x] T08 `make done`, the `314-end` bookend and `perf-report` (SC-005), `dev/performance.md`
      research: rendering
      verify: DONE. make done green on the merged engine; 314-start/314-end back to back, band 1 (reference -8.5%), explanation recorded and confirmed consistent by perf-audit (research R16); dev/performance.md
