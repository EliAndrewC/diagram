# Tasks - feature 297, placement by construction

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (A, B1-B4, C, D1-D4, E1-E3, F). Research: [`research.md`](research.md).
Order: the region and its tests; the small levers; the region's three uses, each measured on Inashiro and the moved pool
gated as it lands; the lane law in four steps; then the measurement and the record. Maps may move anywhere the rules allow
(the GM, 2026-09-30); every lever is held to the gate on the regenerated pool.

## Setup

- [ ] T01 The base: `measure.py before` and `regen-before` in `/tmp/base297` (done at spec time), and the `297-start` bookend there
      research: rendering

## The region (A)

- [ ] T02 [US2] [US3] `settlement/_geom/region.py`: the conservative `Region` (painters, `taken_many`, the lazy summed-area `box_clear`), with its tests against shapely and brute force (A)
      research: rendering

## The small levers (C, E1-E3)

- [ ] T03 [US2] A seat judged once before its layouts: the seat-level pretest in `settlement/rolling/place.py` (`seat_reaches_tree` in `access.py`), and the bundle template keyed per household (C)
      research: rendering
- [ ] T04 [P] [US2] The threshing-yard mats as a computed, centered lattice in `settlement/homestead_parts/yards.py` (E1)
      research: rendering
- [ ] T05 [P] [US5] The page's hit regions, explanations and blob computed while the picture and id map render, in `interactive/page.py` (E2)
      research: rendering
- [ ] T06 [P] [US5] The drain-bank hem's box prefilter in `waterfields/banks.py` (E3)
      research: rendering

## The region's uses (B1-B4)

- [ ] T07 [US2] The seat region: built at the seating, painted as houses are seated, the buildable and reachable rasters, every round offering only where a side's envelope is clear and the door ground is reachable (B1)
      research: rendering
- [ ] T08 [US3] The marsh as array throws read against one region (B2)
      research: rendering
- [ ] T09 [US3] The village grove's crowns tested against one region as arrays (B3)
      research: rendering
- [ ] T10 [US3] The woodland search's squares admitted by the region's box query, one region per half (B4)
      research: rendering
- [ ] T11 The moved pool regenerated and gated with T03-T10 in (`make done`), every failure fixed; Inashiro measured; each moved map's houses, paddies and ways before and after recorded in research (SC-009)
      research: rendering

## The lane law as laid (D)

- [ ] T12 [US4] `hamletgen/ways/keeper.py`: the per-lane and joint verdicts kept on every write (the writers routed through it), tested against `law.LAW` on the pool and cohort webs (D1)
      research: rendering
- [ ] T13 [US4] The access tree's lanes laid at the start of `stage_web` (D2)
      research: rendering
- [ ] T14 [US4] Every rule's repair applied at the write by the keeper's hook; a lane no repair can make lawful not laid (D3)
      research: rendering
- [ ] T15 [US4] The settle's rounds, `unsettled` and the last resort retired; the stage's end reads the keeper and refuses a break by name (D4)
      research: rendering
- [ ] T16 The moved pool regenerated and gated with T12-T15 in, every failure fixed; `make cohort N=24` against the base; each moved map's houses, paddies and ways before and after recorded in research (SC-009)
      research: rendering

## Measurement and record (F)

- [ ] T17 `measure.py after` and `regen-after`, the page marks for SC-006, every SC judged in the spec (an amendment for any withdrawn lever)
      research: rendering
- [ ] T18 `dev/performance.md`: the section FR-008 owes (every stage over half a second and the page write) and the doctrine of the region
      research: rendering
- [ ] T19 The `297-end` bookend and `make perf-report AGAINST=297-start` with whatever its band owes; settlement-reviews of the moved pool maps; the gate; land
      research: rendering
