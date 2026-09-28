# Tasks - feature 284, the fourth hotspot pass

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (A1-A8, B1-B5, C). Research: [`research.md`](research.md).
Order: the exact pieces first, each proved on its equality test; the pool regenerated and compared byte for byte against
`5f15c65bd` with all of them landed; then the moving pieces under 276's FR-006 condition; then the five named stages and
the after-profile; then the measurement and the record.

## Setup

- [ ] T01 The base: `measure.py before` in `/tmp/base284` (low load, the new buckets), the `284-start` bookend there, and the committed pool confirmed to regenerate byte-identically in the base worktree
      research: rendering

## The exact pieces (US2, US4, US5)

- [ ] T02 [US2] One link index per route in `hamletgen/ways/route.py` and `ways/clearance.py`, with the recorded-request equality test (A1)
      research: rendering
- [ ] T03 [P] [US4] The page from the structured blades and marks and one parse of the rest in `settlement/finish.py`, `interactive/page.py` and `interactive/raster.py`, with the synthetic-page equality test (A2)
      research: rendering
- [ ] T04 [P] [US5] The board's lazy caption test in `settlement/structures/fixtures/siting.py`, with its equality test (A3)
      research: rendering
- [ ] T05 [P] [US5] The bamboo search outward in `hamletgen/hinterland/bamboo.py`, with its equality test (A4)
      research: rendering
- [ ] T06 [P] [US5] The whole-ring scans through indexes in `ways/fabric.py`, `ways/geom.py` and `settlement/fields/comb.py`, with their equality tests (A5)
      research: rendering
- [ ] T07 [P] [US5] The grove draw's crown grid in `homestead_parts/groves.py` and `shrines_wells/woods.py`, with its equality test (A6)
      research: rendering
- [ ] T08 [P] [US5] The toll's bitmap in `hamletgen/ways/route.py`, with the toll equality test extended (A7)
      research: rendering
- [ ] T08b [P] [US5] The yards' mats in arrays in `settlement/homestead_parts/yards.py`, with the recorded-yard equality test (A8)
      research: rendering
- [ ] T09 [US1] The pool - hamlets and magistracy pages - regenerated with A1-A8 landed and B not yet: byte-identical against `A_BASE`, the clone's HEAD before the first A commit, regenerated first in a detached worktree (SC-011, the exact half)
      research: rendering

## The moving pieces (US1, US2, US3, US5)

- [ ] T10 [US2] A* in `hamletgen/ways/route.py`, with the cost, clearance and length-bound test over recorded requests (B1)
      research: rendering
- [ ] T11 [US2] The coarser lattice: cells 12, 14, 16, 18 in turn over the pool, the scenarios and the cohort, unreached houses counted per map and seed (re-roll-hidden strandings included), stopping at the first that strands; the largest before it taken and the counts recorded in research R4 (B2)
      research: rendering
- [ ] T12 [US3] The field search without its blind probe in `hamletgen/water/fit.py`, with the stubbed saturating and growing fan tests (B3)
      research: rendering
- [ ] T13 [US3] The carve's rows as arrays - the vertices, their supply-bank pushes and the plot tests - in `waterfields/sector_rows.py` and `waterfields/carve.py`, timed fastest of three against the scalar rows; kept or withdrawn with the measurement in research R5 (B4)
      research: rendering
- [ ] T14 [US5] The board's coarser candidate lattice in `place_kosatsuba` and `stage_notice`'s re-seat lattice, timed fastest of three; kept or withdrawn with the measurement (B5)
      research: rendering
- [ ] T14b [US5] Only if A4 misses SC-006's floor: the bamboo's coarser sampling as a moving change (B6)
      research: rendering

## The other slow stages (FR-011)

- [ ] T15 [US5] The grove fill, the seam closing, the commons and the blade flush re-profiled; each lever of the allowed kind taken, with its test; and the after-profile read under the same rule
      research: rendering
- [ ] T16 [US1] The pool regenerated under 276's FR-006 condition: `make done` green, the rescue-rounds scenario and toys, forms and kinds, field acreage within tolerance, each moved map's houses, paddies and ways before and after recorded in research R6, `make cohort N=24` against the base's (SC-011)
      research: rendering

## Polish

- [ ] T17 `measure.py after` back to back (fastest of three, loads recorded); SC-001 to SC-009 checked on the buckets; `make perf LABEL=284-end` and `make perf-report AGAINST=284-start`
      research: rendering
- [ ] T18 `dev/performance.md`: the fourth pass's section, and only what FR-011 could not take, each with its measurement (FR-012, SC-010)
      research: rendering
