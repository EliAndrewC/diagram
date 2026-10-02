# Tasks: grow the cluster (feature 308)

**Input**: plan.md (D1-D4), research.md (R1-R7)

## Occasions

- placement-changed: village lane - a house's path may now be routed round what stands, several legs (plan D3), where it was straight or round the gable
- placement-changed: farmhouse - a nucleated cluster is grown from its first house at each homestead's minimum distance (plan D1, D2), where a front row, ranks and an exhaustive pass seated it

## Tasks

- [ ] T01 the prototype rounds and the GO verdict (US1, FR-001, FR-002): research R1-R7
      research: rendering
- [ ] T02 the `308-start` scaling bookend on the unmodified engine
      research: rendering
- [ ] T03 the route module `settlement/rolling/route.py` with unit tests on plain inputs; `AccessTree.routed`; the hook in `_house_candidates` (D3, FR-005)
      research: rendering
- [ ] T04 the growth module `hamletgen/homesteads/growth.py` with unit tests; `_seat_households` calls it for the nucleated form in place of the front row, ranks and exhaustive pass (D1, D2, FR-003, FR-004, FR-007)
      research: rendering
- [ ] T05 Inashiro, then the pool and cohort seeds 1-24 plus the pinned six against the base's baseline (FR-006, FR-008, SC-004)
      research: rendering
- [ ] T06 the 40-household legs on the engine, base and clone back to back (SC-002, SC-003)
      research: rendering
- [ ] T07 `make done`, the `308-end` bookend and `perf-report` (SC-005, FR-009), `dev/performance.md`
      research: rendering
- [ ] T08 the occasion's glyph-check, and the items for the GM through escalation-check
      research: rendering
