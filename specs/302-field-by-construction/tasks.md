# Tasks - feature 302, the comb field built by construction

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md).
Order: Phase 0 measures and decides; Phase 1 (T10 onward) runs only on GO, its tasks refined by the plan's amendment.

## Occasions

- placement-changed: paddy - Phase 1 only: the comb field's plots are laid as a partition of the planted region instead of carved and repaired (waterfields/); the fabric's rules are the ones already judged, but how every plot's shape is reached changes, so the paddy fabric owes its glyph check on Inashiro

## Phase 0 - the measurement (no engine change)

- [x] T01 The `302-start` bookend on unmodified code, and the baseline harness (`harness.py` capture + `timed_fit`)
      research: rendering
      verify: DONE. 302-start: total 15.3 s, median 3.9 s, worst 4.4 s (dev/perf-log/20261001T201403Z-302-start-diagram-performance.json); harness baseline research R1, all six inputs
- [ ] T02 [US1] `prototype.py`: the planted region per trial size (plan D2) and the size search on it (D8's form)
      research: rendering
- [ ] T03 [US1] `prototype.py`: the partition (D3) and the rules at construction (D4), the dry hem and beans after it (D5)
      research: rendering
- [ ] T04 [US1] `harness.py`: the prototype timed beside the current fit, the validity checks of SC-003, the verdict of SC-001 (D6); SC-004's stubs named and priced
      research: rendering
- [ ] T05 [US1] [US3] The verdict and the 10/20 trend recorded in `research.md`; on NO-GO the feature stops here and the GM is told
      research: rendering

## Phase 1 - the engine (only on GO; refined by the plan's amendment)

- [ ] T10 [US2] The partition module in `waterfields/`, red-green from the prototype, with its unit tests
      research: rendering
- [ ] T11 [US2] `carve_comb` / `finish_comb` / `fit_field` on the region and the partition; the seam repair and `planted_area` retired for comb fields, their tests moved or retired with each rule carried (FR-006, FR-007, FR-011)
      research: rendering
- [ ] T12 [US2] Inashiro regenerated and gated; then the pool (`make maps`); every map green (SC-006)
      research: rendering
- [ ] T13 [US2] Research pointers that name the retired machinery re-aimed; the glyph-check the Occasions owe
      research: rendering
- [ ] T14 [US2] [US3] The `302-end` bookend, the harness against the base (SC-005), `make done` green (SC-008)
      research: rendering
