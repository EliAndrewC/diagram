# Tasks - feature 278, the second hotspot pass

Spec: [`spec.md`](spec.md) (FAITHFUL, round 3). Plan: [`plan.md`](plan.md) (A1-A9, B1-B2, C, D). Research: [`research.md`](research.md).
Order: the exact pieces first, each proved on its equality test and the map it touches most; then the two moving
pieces; then the tooling; then the sweep, the measurement and the records.

## Setup

- [ ] T01 The base harness from the detached worktree of `ac01ffe2d` (`harness-before.json`, `measurements.json` before-keys) and the `278-start` bookend
      research: rendering

## US2 - the ways are routed without evaluating ground the search never reaches (P1)

- [ ] T02 [US2] The router's lazy lattice in `hamletgen/ways/route.py` and the recorded-request equality fixture (A1)
      research: rendering
- [ ] T03 [US2] The doorstep index once per house in `hamletgen/ways/serve.py`, with its spy test (A2)
      research: rendering

## US3 - the placers stop re-deriving what does not change (P1)

- [ ] T04 [P] [US3] The footbridge segment index in `settlement/city/bridges.py`, with its equality test (A3)
      research: rendering
- [ ] T05 [P] [US3] The wells re-sort in `hamletgen/homesteads/wells.py`, with its count (A4)
      research: rendering
- [ ] T06 [P] [US3] The field: the hem pass's plot index in `waterfields/carve.py`, `_at_f`'s projected threads in `waterfields/frame.py`, with their equality tests (A5)
      research: rendering
- [ ] T07 [P] [US3] The notice board: `off_every_bed`'s segment grid, `_hard_clear`'s box index, `quad_hits_poly`'s prefilter, with their equality tests (A6)
      research: rendering
- [ ] T08 [P] [US3] The windbreak's one grid in `settlement/homestead_parts/grove_blocks.py`, with its equality test (A7)
      research: rendering
- [ ] T09 [P] [US3] The page's bucket index in `interactive/page.py`, with its equality test (A8)
      research: rendering
- [ ] T10 [US3] The exact pieces across the pool: every manifest they touch byte-identical against the base (SC-013's first clause)
      research: rendering

## US4 - Sawada is rolled once, and a discarded roll is not finished (P1)

- [ ] T11 [US4] Only the kept attempt is finished in `hamletgen/driver.py`, with the stubbed re-roll test (A9)
      research: rendering
- [ ] T12 [US4] The envelope refusal in `hamletgen/homesteads/boundary.py`, with its test; Sawada regenerated - built once, 19 households; its research entry before and after (B1)
      research: rendering

## US5 - the commons scatter runs as array operations (P2)

- [ ] T13 [US5] The vectorized commons in `settlement/land/cover.py`, with the compliance and density tests (B2)
      research: rendering
- [ ] T14 [US5] Every pool map regenerated and read; each moved map's research entry (houses, paddies, ways before and after)
      research: rendering

## US6 - the tooling stops paying for work nobody asked for (P2)

- [ ] T15 [P] [US6] `make map` rolls the reference once (C, FR-012)
      research: rendering
- [ ] T16 [P] [US6] The placement page's class hash and the sync-in re-plate, with the planted missing-class test (C, FR-013)
      research: rendering
- [ ] T17 [P] [US6] The `md_tokens` equality test's line oracle, with the planted token test (C, FR-014)
      research: rendering

## Polish - the sweep and the records

- [ ] T18 `make done` green; SC-013 in full (the rescue-rounds scenario and the toys, no new or larger shortfall, forms and kinds)
      research: rendering
- [ ] T19 `make cohort N=24` against the base's 21/24
      research: rendering
- [ ] T20 The after-harness back to back (`measure.py`), SC-001 to SC-012; `make perf LABEL=278-end`, `make perf-report AGAINST=278-start`
      research: rendering
- [ ] T21 `dev/performance.md`: the after-profile's residue with its levers priced (FR-015)
      research: rendering
