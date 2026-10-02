# Tasks: grow the cluster (feature 308)

**Input**: plan.md (D1-D4), research.md (R1-R7)

## Occasions

- placement-changed: village lane - a house's path may now be routed round what stands, several legs (plan D3), where it was straight or round the gable
- placement-changed: farmhouse - a nucleated cluster is grown from its first house at each homestead's minimum distance (plan D1, D2), where a front row, ranks and an exhaustive pass seated it

## Tasks

- [x] T01 the prototype rounds and the GO verdict (US1, FR-001, FR-002): research R1-R7
      research: rendering
      verify: DONE. DONE. research R1-R10: rounds 1-3 stalled on straight paths, round 5 (routed paths, widening levels) GO at 10/15/20/40 households (R6-R8), every household seated
- [x] T02 the `308-start` scaling bookend on the unmodified engine
      research: rendering
      verify: DONE. DONE. 308-start dev/perf-log/20261002T121458Z-308-start-diagram-performance.json on 30059fdde; cohort base 30/30 (/tmp/base308)
- [x] T03 the route module `settlement/rolling/route.py` with unit tests on plain inputs; `AccessTree.routed`; the hook in `_house_candidates` (D3, FR-005)
      research: rendering
      verify: DONE. DONE. settlement/rolling/route.py (search, taut, routed_corridors), AccessTree.routed, access.ROUTE_LATER; tests/settlement/test_route_308.py; make done green
- [x] T04 the growth module `hamletgen/homesteads/growth.py` with unit tests; `_seat_households` calls it for the nucleated form in place of the front row, ranks and exhaustive pass (D1, D2, FR-003, FR-004, FR-007)
      research: rendering
      verify: DONE. DONE. hamletgen/homesteads/growth.py (footprint, seat_toward, settled_seat, household_reach, keeps_its_distance, grow_the_margin, grows); stages calls it for the nucleated form; tests/hamletgen/homesteads/test_growth.py; R9/R10 separation 0 of 271 within the gap
- [x] T05 Inashiro, then the pool and cohort seeds 1-24 plus the pinned six against the base's baseline (FR-006, FR-008, SC-004)
      research: rendering
      verify: DONE. DONE. make maps SCOPE=all clean; cohort 28/30 on the final engine, the two failures (seeds 5, 903) identical on main's merge base 1cc8ba3c4 - the persimmon push's, owned by the Diagram (Inashiro) session; no regression of 308's
- [x] T06 the 40-household legs on the engine, base and clone back to back (SC-002, SC-003)
      research: rendering
      verify: DONE. DONE. R10 back to back: 40 households 101.4 -> 84.8 s, 15 households 17.5 -> 15.6 s; SC-002 missed on eight seeds, SC-003 on offers (5.8-62 a house kept), no seed past two margins - raised with the GM
- [x] T07 `make done`, the `308-end` bookend and `perf-report` (SC-005, FR-009), `dev/performance.md`
      research: rendering
      verify: DONE. DONE. make done green; 308-end vs 308-start band 0 (total -44.2%; 10/20/40 households -43/-34/-44%); dev/performance.md
- [x] T08 the occasion's glyph-check, and the items for the GM through escalation-check
      research: rendering
      verify: DONE. DONE. glyph-checks PASS: farmhouse (2 rounds), village lane (2 rounds), homestead bamboo on kuwabata; escalation-check on the GM items
