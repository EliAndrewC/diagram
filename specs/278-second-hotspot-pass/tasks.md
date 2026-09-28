# Tasks - feature 278, the second hotspot pass

Spec: [`spec.md`](spec.md) (FAITHFUL, round 3). Plan: [`plan.md`](plan.md) (A1-A9, B1-B2, C, D). Research: [`research.md`](research.md).
Order: the exact pieces first, each proved on its equality test and the map it touches most; then the two moving
pieces; then the tooling; then the sweep, the measurement and the records.

## Setup

- [x] T01 The base harness from the detached worktree of `ac01ffe2d` (`harness-before.json`, `measurements.json` before-keys) and the `278-start` bookend
      research: rendering
      verify: DONE. harness-before.json from make spec-harness in the detached worktree /tmp/base278 at ac01ffe2d; measurements.json before-keys; 278-start bookend 27.8 s (log copied into the clone)

## US2 - the ways are routed without evaluating ground the search never reaches (P1)

- [x] T02 [US2] The router's lazy lattice in `hamletgen/ways/route.py` and the recorded-request equality fixture (A1)
      research: rendering
      verify: DONE. route.py: free and band are judged on first ask; test_the_lazy_router_returns_the_whole_box_routers_paths over 14 requests recorded on ac01ffe2d (a recorder id-reuse bug was found and fixed first); ways tests 204 passed
- [x] T03 [US2] The doorstep index once per house in `hamletgen/ways/serve.py`, with its spy test (A2)
      research: rendering
      verify: DONE. test_a_stragglers_doorstep_ground_is_obtained_once_per_house: at most one doorstep index per house, more standing places tried than indexes asked

## US3 - the placers stop re-deriving what does not change (P1)

- [x] T04 [P] [US3] The footbridge segment index in `settlement/city/bridges.py`, with its equality test (A3)
      research: rendering
      verify: DONE. water_segment_index + _widen_for_confluence; test_the_footbridge_widening_from_its_segment_index_equals_the_scan over 600 random decks
- [x] T05 [P] [US3] The wells re-sort in `hamletgen/homesteads/wells.py`, with its count (A4)
      research: rendering
      verify: DONE. wells re-sorted only when a well lands, the house-distance key memoized per seat; Kuwabata and Kashikawa manifests byte-identical (research R4)
- [x] T06 [P] [US3] The field: the hem pass's plot index in `waterfields/carve.py`, `_at_f`'s projected threads in `waterfields/frame.py`, with their equality tests (A5)
      research: rendering
      verify: DONE. carve plot index grown with its hem plots, _at_f falls cached per carve; one comb built three ways gives the same plots; the non-monotone walk test
- [x] T07 [P] [US3] The notice board: `off_every_bed`'s segment grid, `_hard_clear`'s box index, `quad_hits_poly`'s prefilter, with their equality tests (A6)
      research: rendering
      verify: DONE. _hard_clear box grid, quad_hits_poly box prefilter with the full first stage, bed segment index in both probes; three equality tests
- [x] T08 [P] [US3] The windbreak's one grid in `settlement/homestead_parts/grove_blocks.py`, with its equality test (A7)
      research: rendering
      verify: DONE. the grove's static families in one tagged grid, the seats grid at its reach, the outline test memoized; test_grove_blocks green; windbreak 2.22 -> 1.43 s Kashikawa, 1.05 -> 0.69 s Inashiro (observed 2026-09-28)
- [x] T09 [P] [US3] The page's bucket index in `interactive/page.py`, with its equality test (A8)
      research: rendering
      verify: DONE. _BoxGrid per bucket for extents and skips, blocked buckets stop collecting; the merged scatter byte-identical to the whole-list walk
- [x] T10 [US3] The exact pieces across the pool: every manifest they touch byte-identical against the base (SC-013's first clause)
      research: rendering
      verify: DONE. make map of all five: Inashiro, Kashikawa, Kuwabata, Mizuguchi byte-identical (research R4)

## US4 - Sawada is rolled once, and a discarded roll is not finished (P1)

- [x] T11 [US4] Only the kept attempt is finished in `hamletgen/driver.py`, with the stubbed re-roll test (A9)
      research: rendering
      verify: DONE. only the kept attempt is finished; test_only_the_attempt_kept_is_finished (kept, rejected, with and without an output path)
- [x] T12 [US4] The envelope refusal in `hamletgen/homesteads/boundary.py`, with its test; Sawada regenerated - built once, 19 households; its research entry before and after (B1)
      research: rendering
      verify: DONE. UnreachableGround refuses a seat deeper than the reach inside the web's hard ground; its unit test; Sawada attempt 1, 19 households, research R4

## US5 - the commons scatter runs as array operations (P2)

- [x] T13 [US5] The vectorized commons in `settlement/land/cover.py`, with the compliance and density tests (B2)
      research: rendering
      verify: DONE. grass_scatter + KeepoutGrid.hit_many + RingIndex.inside_many (exact: shrunk/grown band, even-odd parity regions for invalid rings; equality tests), the compliance test (rounding-aware); commons CPU 0.70 -> 0.51 s Kashikawa
- [x] T14 [US5] Every pool map regenerated and read; each moved map's research entry (houses, paddies, ways before and after)
      research: rendering
      verify: DONE. every pool map regenerated: only ink_classes moved; blades within 1.1%, dots within 2.7%, pines within sampling noise (research R4); a parcel-index defect found by the comparison and fixed (one line index per size)

## US6 - the tooling stops paying for work nobody asked for (P2)

- [x] T15 [P] [US6] `make map` rolls the reference once (C, FR-012)
      research: rendering
      verify: DONE. the map recipe skips the reference check when GEN is the reference (regen gates what it rolls); make -n shows no _reference for the reference and one for Sawada; the double roll was check-roll + uncached re-roll for a render-less cached entry
- [x] T16 [P] [US6] The placement page's class hash and the sync-in re-plate, with the planted missing-class test (C, FR-013)
      research: rendering
      verify: DONE. render_cache.replate_if_classes_moved + the .classes stamp + make placement-stages-if-classes, run by sync_in after a merge; tests: re-plated when stale or unstamped, not when current, left alone with no page; the planted missing class still red; run in this clone it re-plated the stale page (alder) and then read current
- [x] T17 [P] [US6] The `md_tokens` equality test's line oracle, with the planted token test (C, FR-014)
      research: rendering
      verify: DONE. test_md_tokens_equal_the_whole_text_scan: line oracle over every tracked text plus whole-text edge strings with newlines; 0.64 s call (was 4.6 s); non-vacuity >100 tokens

## Polish - the sweep and the records

- [x] T18 `make done` green; SC-013 in full (the rescue-rounds scenario and the toys, no new or larger shortfall, forms and kinds)
      research: rendering
      verify: DONE. make done green 2026-09-28 (71 s, 100% coverage); SC-013: the four exact-piece manifests byte-identical, Sawada attempt 1 with 19 households, B2 moved only ink_classes; the rescue scenario, the toys and the dense layouts seat the same houses on base and clone (research R4)
- [x] T19 `make cohort N=24` against the base's 21/24
      research: rendering
      verify: DONE. make cohort N=24 on 2026-09-28: 24/24 pass the whole gate (feature 276 closed at 21/24; no seed can newly fail)
- [ ] T20 The after-harness back to back (`measure.py`), SC-001 to SC-012; `make perf LABEL=278-end`, `make perf-report AGAINST=278-start`
      research: rendering
- [ ] T21 `dev/performance.md`: the after-profile's residue with its levers priced (FR-015)
      research: rendering
