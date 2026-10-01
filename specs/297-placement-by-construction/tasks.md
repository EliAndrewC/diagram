# Tasks - feature 297, placement by construction

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (A, B1-B4, C, D1-D4, E1-E3, F). Research: [`research.md`](research.md).
Order: the region and its tests; the small levers; the region's three uses, each measured on Inashiro and the moved pool
gated as it lands; the lane law in four steps; then the measurement and the record. Maps may move anywhere the rules allow
(the GM, 2026-09-30); every lever is held to the gate on the regenerated pool.

## Setup

- [x] T01 The base: `measure.py before` and `regen-before` in `/tmp/base297` (done at spec time), and the `297-start` bookend there
      research: rendering
      verify: DONE. measure.py before + regen-before in /tmp/base297 (c5a631f9b); 297-start bookend 16.1 s after REFERENCE took Inashiro's pins (research R8); base cohort 30/30

## The region (A)

- [x] T02 [US2] [US3] `settlement/_geom/region.py`: the conservative `Region` (painters, `taken_many`, the lazy summed-area `box_clear`), with its tests against shapely and brute force (A)
      research: rendering
      verify: DONE. settlement/_geom/region.py; tests/settlement/test_region.py 3 passed (no painted point read clear at cells 2/3/8, box query = brute sum, off-window taken)

## The small levers (C, E1-E3)

- [ ] T03 [US2] A seat judged once: the field's reach and the water before any layout, the corridor once per seat (`seat_reaches_tree` in `access.py`); the bundle template keyed per household built and withdrawn (C, R9, R10)
      research: rendering
- [ ] T04 [P] [US2] The threshing-yard mats as a computed, centered lattice in `settlement/homestead_parts/yards.py` (E1)
      research: rendering
- [x] T05 [P] [US5] The page's hit regions, explanations and blob computed while the picture and id map render, in `interactive/page.py` (E2)
      research: rendering
      verify: DONE. page.py: the picture submitted from the wrapped strings before the hit regions/hit layer, the id map after them, the explanations/card computed while both render; Inashiro regenerates with its 12 MB page and picture; tests/interactive 1202 passed
- [x] T06 [P] [US5] The drain-bank hem's box prefilter in `waterfields/banks.py` (E3)
      research: rendering
      verify: DONE. banks.py: hem_to_bank asks drain_bank_clearance_many (one numpy pass over vertices x drain segments); test_banks_297.py: per-vertex verdict equals the scalar predicate over 40 random rings/drains incl. zero-length segments

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
- [ ] T13 [US4] The access tree's lanes laid at the start of `stage_web` (D2) - built and measured; withdrawn (R10, R14)
      research: rendering
- [ ] T14 [US4] Every rule's repair applied at the write (each pass boundary); a lane no repair can make lawful not laid (D3) - built and measured; withdrawn (R14)
      research: rendering
- [ ] T15 [US4] The settle's rounds, `unsettled` and the last resort retired; the stage's end refuses a break by name (D4) - built and measured; withdrawn (R14); the measured fix (`settle_dangling`) and the targeted rounds (R12, withdrawn) in its place
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
