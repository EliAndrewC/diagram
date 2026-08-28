# Tasks: The Cold Gate - Faster Rolls, and a Cache Warmed While Idle (feature 138)

Verification: `make quick` while iterating; the byte-identity sweep (`scratch baseline vs after`) after every
router change; ONE `make done` per batch; `make maps`; the perf bookends.

## Phase 0 - baseline (FR-001)
- [ ] T01 per-stage timings of the seed-19 polder and the reference; the manifest of every gate roll spec and every live pool map on unmodified code (the byte-identity oracle); `make perf LABEL=138-start`
- [ ] T02 the cold gate's baseline wall clock on this code (every cached roll re-made): the 5 m 42 s figure re-measured after main's merge

## Phase 1 - the router (FR-002, FR-004)
- [ ] T10 `FabricIndex` in `hamletgen/ways.py` (or a sibling module): per-polygon bounds once, a cell grid over a box, `candidates(q)` returning the obstacle / tight / line entries whose inflated bounds cover q's cell; a property test that on random fabric the index's candidates are a superset of the bbox scan's, and that `fouled` agrees on every sample
- [ ] T11 `clear_runs` builds the index once per call and tests each sample against its cell; `_route` builds ONE index for the routing box and derives the free lattice from it (no per-cell `clear_runs`)
- [ ] T12 byte identity: the seed-19 polder's manifest equals the baseline's; then every gate roll and live pool map (T01's oracle); stage timings recorded

## Phase 2 - the connector (FR-003, FR-004)
- [ ] T20 `path_violations`: the pairwise crossing count becomes a sorted sweep; a test with a hand-made hit list proves the count identical to the pairwise form on random inputs
- [ ] T21 byte identity again, all maps

## Phase 3 - the numbers (FR-005, FR-006)
- [ ] T30 the cold gate re-measured (every cached roll re-made); `make perf LABEL=138-end`; `make perf-report AGAINST=138-start`; any slower seed diagnosed in writing
- [ ] T31 the idle run warms the interactive gate: after a sync that moved the rolls' keys, `make idle-tests` (run by hand for the measurement, as the hook would) leaves the next `make done` reporting every roll served; anything the gate reads that the idle run did not fill is added to it
- [ ] T32 `GEN_TIME_BUDGETS` and `dev/performance.md`: the measured cause and the fixed figures; the "bisection" explanation corrected (FR-008); the polder budgets re-derived from the new solo times

## Phase 4 - close
- [ ] T40 `make done` green, `make maps` green, the stop-work ritual (gated route; feature complete when every box above is ticked - FR-010)
