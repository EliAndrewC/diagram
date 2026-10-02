# Tasks - feature 302, the comb field built by construction

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md).
Order: Phase 0 measures and decides; Phase 1 (T10 onward) runs only on GO, its tasks refined by the plan's amendment.

## Occasions

- placement-changed: paddy - Phase 1 only: the comb field's plots are laid as a partition of the planted region instead of carved and repaired (waterfields/); the fabric's rules are the ones already judged, but how every plot's shape is reached changes, so the paddy fabric owes its glyph check on Inashiro

## Phase 0 - the measurement (no engine change)

- [x] T01 The `302-start` bookend on unmodified code, and the baseline harness (`harness.py` capture + `timed_fit`)
      research: rendering
      verify: DONE. 302-start: total 15.3 s, median 3.9 s, worst 4.4 s (dev/perf-log/20261001T201403Z-302-start-diagram-performance.json); harness baseline research R1, all six inputs
- [x] T02 [US1] `prototype.py`: the planted region per trial size (plan D2) and the size search on it (D8's form)
      research: rendering
      verify: DONE. prototype.py Trial: the skeleton as carve_comb lays it, region = envelope - _water - _outside_command; _search_aspect scores (fan_legal on the region's outline, acreage error)
- [x] T03 [US1] `prototype.py`: the partition (D3) and the rules at construction (D4), the dry hem and beans after it (D5)
      research: rendering
      verify: DONE. prototype.py Sectors/cut (partition), settle (snap, split, merge, scraps left bare), tint, _comb_dry_and_beans, fan_admissible
- [x] T04 [US1] `harness.py`: the prototype timed beside the current fit, the validity checks of SC-003, the verdict of SC-001 (D6); SC-004's stubs named and priced
      research: rendering
      verify: DONE. harness.py: capture, interleaved three runs, validity (band, bare, unshared, ring_violations), the verdict; nothing stubbed
- [x] T05 [US1] [US3] The verdict and the 10/20 trend recorded in `research.md`; on NO-GO the feature stops here and the GM is told
      research: rendering
      verify: DONE. research R2: GO, 6.558 -> 2.414 s (2.72x), spread 0.05 s; 10 hh 3.00x, 20 hh 2.48x; phase0-verdict.json

## Phase 1 - the engine (only on GO; refined by the plan's amendment)

- [x] T10 [US2] The partition, settle and tint modules in `waterfields/`, red-green from the prototype, with their unit tests - settle's assert that no cell it returns has a `ring_violations` finding (the plan review's round-3 note: what the deleted weld tests held)
      research: rendering
      verify: DONE. DONE. waterfields/partition.py, settle.py (settle_cells), tint.py; test_partition/test_settle/test_tint, each module 100% from its own tests; settle asserts no returned cell has a ring_violations finding
- [x] T11 [US2] `carve_comb` / `finish_comb` / `fit_field` on the region and the partition; the seam repair and `planted_area` retired for comb fields, their tests moved or retired with each rule carried (FR-006, FR-007, FR-011)
      research: rendering
      verify: DONE. DONE. carve_comb lays the skeleton + region, finish_comb partitions/settles/tints; fit scores region.area; carve plot cutting, sector_rows.py, close_seams and seams/plots.py deleted, PlotGeoms and planted_area gone; tests moved (tint) or retired, the rules held by test_settle/test_partition (tiling, shared bunds) and ring_rules' own
- [x] T12 [US2] Inashiro regenerated and gated; then the pool (`make maps`); every map green (SC-006)
      research: rendering
      verify: DONE. DONE. make done green on 1249742be+ (6676 passed, FULL, every pool map rolled under test-full; coverage 100%); Inashiro's two gate failures (toe-marsh straight run, B7 corridor tread) fixed in c774680b4
- [x] T13 [US2] Research pointers that name the retired machinery re-aimed; the glyph-check the Occasions owe
      research: rendering
      verify: DONE. DONE. research fragments' code pointers re-aimed at partition/settle/tint (c774680b4); glyph checks: paddy on inashiro PASS round 2 (round 1's F1-F4 fixed, R5), alder PASS, woodland commons PASS x2, grave island PASS x2, homestead bamboo PASS round 2 (its round-1 errors fixed)
- [x] T13b [US2] [US3] The 10- and 20-household fields compared cell by cell with the carve's (plot count, cell-size distribution, the longest cells) in the harness before the push - the plan review's round-3 note: the glyph check on Inashiro cannot see the narrow-sector and edge-strip cases R2 found there; a finding is fixed in the lattice
      research: rendering
      verify: DONE. DONE. research R4: first cut 19/26 cells over 3 design cells at 10/20 hh (carve 3/5); four lattice causes measured and fixed (CROSS, _rows_kept, keep_rows, recut); after: 10 hh 0 over 2 cells (carve 13), 20 hh 2 (19), largest and longest below the carve's at both
- [x] T14 [US2] [US3] The `302-end` bookend, the harness against the base (SC-005), `make done` green (SC-008)
      research: rendering
      verify: DONE. DONE. 302-end vs 302-start 15.3 -> 12.7 s (-17.0%, band 0, owes nothing); fit_field 5.72 -> 3.05 s vs main (R4); make done green on the final engine
