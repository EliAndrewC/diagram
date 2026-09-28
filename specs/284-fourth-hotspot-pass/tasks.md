# Tasks - feature 284, the fourth hotspot pass

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (A1-A8, B1-B5, C). Research: [`research.md`](research.md).
Order: the exact pieces first, each proved on its equality test; the pool regenerated and compared byte for byte against
`5f15c65bd` with all of them landed; then the moving pieces under 276's FR-006 condition; then the five named stages and
the after-profile; then the measurement and the record.

## Setup

- [x] T01 The base: `measure.py before` in `/tmp/base284` (low load, the new buckets), the `284-start` bookend there, and the committed pool confirmed to regenerate byte-identically in the base worktree
      research: rendering
      verify: DONE. measure.py before in /tmp/base284 at 5f15c65bd (pool 32.168 s, load 3.1->7.8; every bucket incl. mats, crowns, seams, commons, flush); 284-start bookend 17.4 s (at f52ed6aa8, before the re-base: to be re-taken if the perf report needs the merged base); the base pool regenerates byte-identically in /tmp/base284; A_BASE worktree /tmp/abase284 at efec5d67d regenerating

## The exact pieces (US2, US4, US5)

- [x] T02 [US2] One link index per route in `hamletgen/ways/route.py` and `ways/clearance.py`, with the recorded-request equality test (A1)
      research: rendering
      verify: DONE. DONE. link_index built once per route (clearance.py, route.py); the base's recorded-request equality test passes point for point
- [x] T03 [P] [US4] The page from the structured blades and marks and one parse of the rest in `settlement/finish.py`, `interactive/page.py` and `interactive/raster.py`, with the synthetic-page equality test (A2)
      research: rendering
      verify: DONE. DONE. the page reads the blade slots' structures (blade_starts, premerged, marks_region points=); tests/settlement/test_exact_pieces_284.py::test_the_page_reads_a_blade_slot_as_it_would_have_parsed_it byte-identical through both routes; the rest's one parse not built on R7's measured ceiling (0.051/0.059 s a map)
- [x] T04 [P] [US5] The board's lazy caption test in `settlement/structures/fixtures/siting.py`, with its equality test (A3)
      research: rendering
      verify: DONE. DONE. board_choice asks the caption level lazily in ranking order; test_the_lazy_board_choice_is_the_full_choice; plus VERGE_FIRST (the verge band sampled first), tested against the whole band
- [x] T05 [P] [US5] The bamboo search outward in `hamletgen/hinterland/bamboo.py`, with its equality test (A4)
      research: rendering
      verify: DONE. DONE. nearest_fitting walks outward; test_the_bamboo_walk_outward_finds_the_scans_seat
- [x] T06 [P] [US5] The whole-ring scans through indexes in `ways/fabric.py`, `ways/geom.py` and `settlement/fields/comb.py`, with their equality tests (A5)
      research: rendering
      verify: DONE. DONE. _crosses_fabric box prefilters, ring_within (end_serves' steading clause, push_clear_of_fabric), the comb's _dry through seg_reach_index; four equality tests in test_exact_pieces_284.py
- [x] T07 [P] [US5] The grove draw's crown grid in `homestead_parts/groves.py` and `shrines_wells/woods.py`, with its equality test (A6)
      research: rendering
      verify: DONE. WITHDRAWN. the crown grid was exact but slower than main's two scans after 269 (windbreak 8-12% slower on three pool hamlets, measure.py after-main); main's own CrownIndex serves the rank (research R7)
- [x] T08 [P] [US5] The toll's bitmap in `hamletgen/ways/route.py`, with the toll equality test extended (A7)
      research: rendering
      verify: DONE. DONE. _CROSSING near-cell set, in_brook_band returns early; the toll's lookups 590,253 -> 8,397 on Kashikawa, 374,679 -> 0 on Sawada
- [x] T08b [P] [US5] The yards' mats in arrays in `settlement/homestead_parts/yards.py`, with the recorded-yard equality test (A8)
      research: rendering
      verify: DONE. DONE. floor_grid / mat_spots / best_lattice in arrays, the _boxes_within prefilter; test_mats_arrays_284.py equal to the recorded 1,207 mats of 66 yards; numpy bound on first use
- [x] T09 [US1] The pool - hamlets and magistracy pages - regenerated with A1-A8 landed and B not yet: byte-identical against `A_BASE`, the clone's HEAD before the first A commit, regenerated first in a detached worktree (SC-011, the exact half)
      research: rendering
      verify: DONE. DONE. the pool byte-identical against A_BASE with A1-A8 landed (the pool diff, 2026-09-28)

## The moving pieces (US1, US2, US3, US5)

- [x] T10 [US2] A* in `hamletgen/ways/route.py`, with the cost, clearance and length-bound test over recorded requests (B1)
      research: rendering
      verify: DONE. WITHDRAWN. A* built and tested (cost, bound, clearance); measured alone on the merged engine it was 5.0 s under the cost-order search's mean against an 8.9 s spread (astarcmp/results-alone.json, research R6); the search is Dijkstra again, the base's route equality test restored
- [x] T11 [US2] The coarser lattice: cells 12, 14, 16, 18 in turn over the pool, the scenarios and the cohort, unreached houses counted per map and seed (re-roll-hidden strandings included), stopping at the first that strands; the largest before it taken and the counts recorded in research R4 (B2)
      research: rendering
      verify: DONE. WITHDRAWN. cells 12-18 over the pool, the toys and cohort 1-24 (b2/results.json, research R4): 12 px strands cohort 08 and Sawada, no coarser cell faster; ROUTE_CELL stays 10
- [x] T12 [US3] The field search without its blind probe in `hamletgen/water/fit.py`, with the stubbed saturating and growing fan tests (B3)
      research: rendering
      verify: DONE. WITHDRAWN. the probe on measured saturation was 5% faster in all against a 1% spread, but the moved pool maps failed five gate rules (research R6); the base's search restored with the reason at the point of change
- [x] T13 [US3] The carve's rows as arrays - the vertices, their supply-bank pushes and the plot tests - in `waterfields/sector_rows.py` and `waterfields/carve.py`, timed fastest of three against the scalar rows; kept or withdrawn with the measurement in research R5 (B4)
      research: rendering
      verify: DONE. WITHDRAWN. the edge walk in arrays 3.6x slower than scalar over Sawada's 3,310 recorded calls, the same verdicts (b4/results.json, research R5)
- [x] T14 [US5] The board's coarser candidate lattice in `place_kosatsuba` and `stage_notice`'s re-seat lattice, timed fastest of three; kept or withdrawn with the measurement (B5)
      research: rendering
      verify: DONE. WITHDRAWN. the 24 px lattice broke test_an_entrance_board_stands_on_the_approach_and_not_on_a_straggler_at_its_join; the spacing stays 12 (BOARD_ALONG_STEP_PX), and VERGE_FIRST took its place, exact
- [x] T14b [US5] Only if A4 misses SC-006's floor: the bamboo's coarser sampling as a moving change (B6)
      research: rendering
      verify: DONE. DONE. SC-006 missed on Mizuguchi (1.23x) after A4, so BAMBOO_SEAT_STEP_FT = 16; the bamboo bucket 4.37x and 13.1x; the thicket seats 18.1 and 24.5 ft from main's on the two maps that have one (research R6)

## The other slow stages (FR-011)

- [x] T15 [US5] The grove fill, the seam closing, the commons and the blade flush re-profiled; each lever of the allowed kind taken, with its test; and the after-profile read under the same rule
      research: rendering
      verify: DONE. DONE. re-profiled (t15/, grove/, parse/ harnesses; research R7): no lever of the allowed kind makes the seam closing, commons, flush or grove fill significantly faster - each priced; a stranding re-roll resumes at the seats (FR-014, byte-identical on six maps, re-verified after the merge)
- [x] T16 [US1] The pool regenerated under 276's FR-006 condition: `make done` green, the rescue-rounds scenario and toys, forms and kinds, field acreage within tolerance, each moved map's houses, paddies and ways before and after recorded in research R6, `make cohort N=24` against the base's (SC-011)
      research: rendering
      verify: DONE. DONE. make done green on the merged engine; the pool is main's but for the thicket (research R6); the cohort over pool + 24 seeds seats all 442 households with every connector and no failing roll (combined/, astarcmp/); the connector defect found and fixed

## Polish

- [x] T17 `measure.py after` back to back (fastest of three, loads recorded); SC-001 to SC-009 checked on the buckets; `make perf LABEL=284-end` and `make perf-report AGAINST=284-start`
      research: rendering
      verify: DONE. DONE. measure.py after-main: 35.148 s -> 26.716 s (1.32x) against main as merged, 1.20x against the base; make perf LABEL=284-end band 0, -18.0% against 284-start
- [x] T18 `dev/performance.md`: the fourth pass's section, and only what FR-011 could not take, each with its measurement (FR-012, SC-010)
      research: rendering
      verify: DONE. DONE. dev/performance.md's fourth-pass section with the residue table; the five placer fragilities to future-work/farming-communities.md
