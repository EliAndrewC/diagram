# Derivation - lane_wells (feature 444)

## Contract

- Reads: the wells drawn so far and `well_target` (the count owed, at most two); the rolled `well_siting` and which form was tried before the lanes; the lanes as laid (their lines and verges); the placed homesteads; the registry of what stands; the households' count.
- Writes: the communal wells still owed, each with its form (`lane`, `cluster` or `fallback`); the wells the reach and the ten add (`meta.wells_for_reach`, `meta.wells_for_ten`); `meta.well_fallback`, `meta.dry_households`.
- Keeps: the lane-side form on a lane's verge, clear of the tread, a dwelling's wall within 80 ft (`WELL_SEAT_FT`, 0196); then the cluster form, among five houses within the widening reach (190, 300, 520 ft, then 760 ft), off every lane and verge (0196); then the recorded fallback, among three houses, then two, at the 95 ft check (`THREE_THEN_TWO`: 190, 300 and 520 ft for three, 520 ft for two), marked `fallback` (a DEVIATION, 0196); each seated for the worst-served household, ranked by its walk, the straight distance as the reach is measured; every household within 760 ft of a well or open water (`WATER_REACH_FT`); no well nearest more than 10 households where a seat avoids it (`WELL_SERVES_MAX`); each seat asked before its well is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the lanes' length 2,569 and 5,568 ft (x2.17: 5,568 at 20, 12,083 at 40, 26,220 at 80), their density at most 7.47e-3 ft a sq ft (2,569 ft in 477 by 721 ft at 10; the greater taken); a homestead's extent at most 184 ft; a well drawn 12.4 ft in radius (its diameter 25 ft) and a verge 7 ft off a lane's line (`ACCESS_HALF_FT`), so a site's clearance, 19.4 ft, lies in at most 2 by 2 cells of 64 ft; at most 21 and 29 standing things in one 64 ft cell within 192 ft of a house, on the finished map (x1.38: 29 at 20, 40 at 40, 55 at 80); the wells, the larger of 2 and the households over 10 rounded up (2 at 20, 4 at 40, 8 at 80); the houses' density at most 2.9e-5 a sq ft, so at most density x pi x r squared houses within r of a point and density x 9 x r squared in 3 by 3 cells of r ft, never more than the households; 1 ft a pixel at the hamlet scale. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell; each held flat past 20, a mean over occupied cells not rising with the households as the densest cell does. The admission share (FR-014; the round arbiter's ruling ask:444-T09-rescore-batch; measured 2026-10-28 on the reference manifests at 10 and 20): of the lane-verge sites 25 ft apart, 0.39 and 0.24 are clear for a well's 19.4 ft box with a dwelling's wall within 80 ft (0.24 taken), so a well past the first is admitted at the 1 / 0.24 = 4.17th site popped; the first well, owed where more than 10 households share it, is admitted nowhere under the ten - every site serves them all - so it costs its whole pool, and the seat serving fewest past ten is drawn.

## The algorithm

    while a well is owed (the count, then the reach, then the ten), on the lane-side form:
        the worst-served household: the top of a max-heap of each household's distance to its nearest well
        its nearest lane point, from the ways' 3 by 3 cells of 64 ft; the lane sites along that lane's verges, one a well's diameter apart, walked outward nearest first
        each site: clear of the registry's things in its 2 by 2 cells (S4), a dwelling's wall within 80 ft, the households it would
            serve under the ten from its 9 cells of 760 ft, its walk, and the wells this stage drew; the first admitted is the well
        draw it; re-key the households it takes

## Indexes

- house index: cells of 760 ft, the widest reach, so the households a well would serve lie in its 3 by 3 cells; densest the about 10 a well serves at the typical (`WELL_SERVES_MAX`), from a smallest side of 760 ft
- registry: cells of 64 ft; densest the mean 4 things a cell near the houses (`items.md`'s typical densities), from a smallest side of 64 ft against a well's 19.4 ft clearance, in at most 2 by 2 cells
- ways index: cells of 64 ft, the laid ways' legs; densest the mean 2 legs a crossed cell (`items.md`), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 2 at 20, 4 at 40, 8 at 80 | the wells drawn here, at most all that are owed: the larger of 2 and the households over 10 rounded up | 80 households |
| the drawing (registry cells written) | per item | 5 | the record written (1) and filed in at most 4 cells of 64 ft (4) | always 5 |
| slack | per item | 1 | what varies around the typical case (S8): the spread around the mean pops, inside the first well's whole pool | not applicable |
| the first well (house index, ways index and registry cells examined) | over the run | 43,262 at 20, 113,139 at 40, 170,502 at 80 | its pool, the lane sites within 760 ft of the worst-served household, 2 x the lanes' density x pi x 760 squared over 25 ft, capped by the lane sites (446 at 20, 967 at 40, 1,086 at 80), every site popped (the ten admits none), each 97 at 20, 117 at 40, 157 at 80: its clearance in the 2.6 cells a 38.8 ft box covers with the mean 5.5 things within 3 cells of a house and the cell (2.6 x 6.5, 17), a dwelling's wall within 80 ft (`WELL_SEAT_FT`) from the cells its 160 ft box covers, (1 + 160/64) squared = 12.25, with the mean 3 parts and the cell (49), the households it would serve read from its 9 cells of 760 ft, every household below about 150 (9 + n), its walk (1), no wells drawn yet (0); and the fallback's comparison, 1 a site (ask:444-T09-rescore-batch-2) | the typical cluster |
| the later wells (house index, ways index and registry cells examined) | over the run | 436 at 20, 1,570 at 40, 4,889 at 80 | the wells past the first (1 at 20, 3 at 40, 7 at 80), each the worst-served household's nearest lane point from the ways' 3 by 3 cells with the mean 2 legs and the cell (27) and 4.17 sites popped (1 / p), each at the first well's per-site cost plus the wells drawn (half, rounded up): 98 at 20, 119 at 40, 161 at 80 | the typical cluster |
| the service (households re-keyed) | over the run | 348 at 20, 946 at 40, 2,322 at 80 | the first well re-keys every household (the contract admits it past the ten, and every site serves them all), its 9 cells (9) and n households; each later well its 9 cells and the about 10 households it takes; each re-keyed with a push and the stale entry's pop, 1 + 2 x log2 of the households rounded up | the typical cluster |
| the worst-served query (heap top read) | over the run | 2 at 20, 4 at 40, 8 at 80 | each well, the max-heap's top, 1 | every well owed |
| the house index (cells written) | once | 20 at 20, 40 at 40, 80 at 80 | each house filed once in its 760 ft cell | 80 households |

So: the items x 5 x 1, plus the first well, the later wells, the service, the worst-served query and the house index.

## Totals

- at 20: 2 x 5 x 1 + 43262 + 436 + 348 + 2 + 20 = 44078
- at 40: 4 x 5 x 1 + 113139 + 1570 + 946 + 4 + 40 = 115719
- at 80: 8 x 5 x 1 + 170502 + 4889 + 2322 + 8 + 80 = 177841

## Growth

From 20 to 80 households the stage grows at an exponent of about 1.01, within 1.15: the first well's pool is capped by the lane sites within 760 ft of the worst-served household, and the households a site reads grow with n while the wells grow one for every ten.


## Earlier findings

- verdict-4, finding 1: fixed - the wall test from the cells the 80 ft reach's 160 ft box covers, 12.25 x 4 = 49 a site; the first well re-keys every household (9 + n x 11 at 20); no wells drawn at the first well; the clearance at the near-house 5.5, 17 (ask:444-T09-rescore-batch-2)
- verdict-3, finding 1: fixed - the households a site would serve read 9 + n from its 760 ft cells; the first well costs its whole pool (the ten admits none); the later wells 1/p pops, p = 0.24 measured on the reference geometry; the wall test and the find at their 3 by 3 cells; the five-nearest key dropped (the forms' order is the search's, no rung key)
- verdict-1, finding 1: fixed - each well's pool heap is built bottom-up, 2 an element, and popped at log2 of the pool
- verdict-1, finding 2: fixed - the 34 cluster sites a house carry their arithmetic, 835 ft over 25 ft
- verdict-1, finding 3: fixed - the nearest wall within 80 ft is the 4 walls of each of the five nearest houses, 20 a site, in the sites row
- verdict-1, finding 4: fixed - the worst-served query is the heap's top, 1 a well
- verdict-1, finding 5: fixed - each well's scan of its 3 by 3 cells' sites against the disc is a row of its own
- verdict-1, finding 6: fixed - the cluster sites in the pool are those of the houses within 908 ft (a site up to 148 ft from its house's center)
- verdict-2, finding 1: fixed - each popped site is tested against the wells this stage drew before it, one distance each, its own row (S4)
- verdict-2, finding 2: fixed - the service row states what its 2 pays for, the push and the stale entry's pop, and the heap's size under lazy invalidation
- verdict-2, finding 3: fixed - a lane site reads only its 2 by 2 cells of 760 ft and the houses within 210 ft, for the wall within 80 ft
- FR-014 re-score: each factor at the typical case (rubric S8): a well's sites are asked nearest the worst-served household first and the nearest is admitted within a few pops, so no site index is built and no pool scanned; each popped site at the mean densities of `items.md`; slack 2 (ask:444-budget-standard; the accept was ask:444-T03-lane_wells-round-3); since corrected by ask:444-T09-rescore-batch: the first well scans its whole pool, slack 1

- reason above the reference: a well is one thing placed, and the first well, owed where more than 10 households share it, is admitted nowhere under the ten, so it searches its whole pool of lane sites; about 25,000 a well at 40

## Cheaper algorithms considered

- sweep: not used - the wells are seated one at a time, each for the worst-served household as it stands
- grid or spatial index: used - the registry for a site's clearance and the house index for its neighborhood; no site index is built (the lane sites are walked from the worst-served household)
- priority queue: used - the worst-served household is a max-heap's top; a household's sites are walked nearest first
- incremental update: used - each well re-keys only the households in its cells
- memoizing what a scan does not change: not used - the sites are popped nearest first and only the few the search reaches are tested, so nothing is memoized over the run
