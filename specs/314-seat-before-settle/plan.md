# Implementation Plan: seat before settle (feature 314)

**Spec**: [spec.md](spec.md) | **Research**: [research.md](research.md) | **Date**: 2026-10-02

## Summary

The homesteads stage's grown seating asks a seat's ground before it lays the household out (US1), and the further rounds (US2)
attack what the measurement names next: the routed path's search, the household layout's persimmon, the well pocket's water
test. Every round is prototyped in the clone and timed against the base alternated per seed (`abab.sh`) before it is kept;
every seat offered still passes the placer's full rules.

## Technical Context

Python 3.14 engine, `hamletgen/homesteads/growth.py` (the growth), `settlement/rolling/route.py` (the routed path),
`settlement/homestead_parts/fixture_seats.py` and `tree_shade.py` (the persimmon's sun), `settlement/rolling/lot.py` and
`settlement/land/wet.py` (the well pocket's water). Measured with `refusals.py` and `abab.sh` (spec Assumptions), profiled with
`prof.py`.

## Performance bookends (constitution VI)

| | label | notes |
|---|---|---|
| before | `314-start` | taken in the base worktree (`/tmp/base314`, the spec's commit, engine unmodified) |
| after | `314-end` | before the push; `make perf-report AGAINST=314-start` |

## Decisions

**D1 - The seat's own questions before its layout (FR-001; US1).** `growth.settled_seat` asks `seat_refused` of every position
it would lay the household out at: the field's reach, then the house's own box (the lot's rung of the size ladder, `next_house`)
against the canvas, the reserved corridors and two placed homesteads (`_house_box_refused`) and the refused-ground grid
(`FreeGround.rect_refused`) - the placer's own tests, asked as it asks them. The water is not asked: a household sought at a
seat carries a pocket wherever none is in reach, so `watered` holds there by construction. A refused position drops the seat
(the spec's Decisions row; FR-005 measures what it costs). Measured: research R3.

**D2 - The placed homesteads (FR-002).** `_house_box_refused` (in D1) asks the placed homesteads of the house's box: two of
them under it refuse every layout. A further cheap test was PRICED (research R5): the same tests asked of the box round the
house and its threshing yard, which every garden side's box holds, computed without the layout. It made the stage 4% slower at
15 households and 11% slower at 40 - few seats were left for it to catch by round 4, and its larger box dropped positions the
settle would have moved onto clear ground. Withdrawn on those numbers; no cheaper test of the placed homesteads than D1's was
found.

**D3 - The routed path refused where it is searched (US2, round 2).** Research R2, R4 and R12. Its first step from the door may
span two cells and is judged by the household's own leg tests (`house_clear`, `fixtures_clear`, `parts_clear`); a goal whose last
leg onto the tree the standing ground refuses (`standing_ground`) is no goal; a cell's heuristic is computed once. The search
keeps off its own house only, as before: kept off the household's beds and fixtures too, it found paths the web could not draw
(seed 13 at 20 households refused, seeds 4 and 39 a web stage 2-3x slower) and was withdrawn (R12). The grid stays the door's:
the map's grid lost seed 6 two margins (R4) and is withdrawn. Kept on R13's numbers - a round that does not pay is withdrawn
and recorded, as the map's grid, R5's check and R12's own parts were.

**D4 - Exact speedups of the household layout and the well pocket (US2, round 3).** Each plot's sun ground is taken once per
rake (`tree_shade.sun_ground`, asked by `crown_in_ground`; `crown_shades` reads the same two), not once per crown asked; the
surface water is a `PointGrid` kept while its lines stand (`lot.water_index`), asked by `wet.surface_water_within` - the same
distances decide. Neither changes an answer; tests compare each against the predicate it replaces. Kept within R4's rounds.

**D5 - The iteration (US2; spec acceptance scenario 2).** After each kept round the profile names the next cost; the record
(research) names each remaining cost, what an efficient process would do about it, and that the stage now does it or the
measured reason it cannot.

## Verification

- Unit tests: `tests/hamletgen/homesteads/test_growth.py` (the pre-check, `next_house`), `tests/settlement/test_route_308.py`
  (the search's start and first step, the own parts, the last leg), `tests/settlement/test_core.py` (the indexed water against
  `surface_water_dist`), `tests/settlement/test_tree_shade.py` (the sun ground against `crown_shades`).
- `abab.sh` at 15 households (seeds 1-16) and 40 (ten seeds) after each round; the pool and cohort through `make done` and
  `make cohort`; the bookends.

## Constitution Check

- VI (performance): bookends taken; every lever timed by the wall clock, base and clone alternated; withdrawn levers recorded.
- XII: no research question - the change is the search's order and breadth, every rule unchanged.
- XIII: the cohort and the pool measured against the base (FR-005).
- XVI: FR-001's seat refused on its own questions is the GM's "before the household layout"; no exception taken.
