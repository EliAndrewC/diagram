# Derivation - lane_wells (feature 444)

## Contract

- Reads: the wells drawn so far and `well_target` (the count owed, at most two); the rolled `well_siting` and which form was tried before the lanes; the lanes as laid (their lines and verges); the placed homesteads; the registry of what stands; the households' count.
- Writes: the communal wells still owed, each with its form (`lane`, `cluster` or `fallback`); the wells the reach and the ten add (`meta.wells_for_reach`, `meta.wells_for_ten`); `meta.well_fallback`, `meta.dry_households`.
- Keeps: the lane-side form on a lane's verge, clear of the tread, a dwelling's wall within 80 ft (`WELL_SEAT_FT`, 0196); then the cluster form, among five houses within the widening reach (190, 300, 520 ft, then 760 ft), off every lane and verge (0196); then the recorded fallback, among three houses, then two, at the 95 ft check (`THREE_THEN_TWO`: 190, 300 and 520 ft for three, 520 ft for two), marked `fallback` (a DEVIATION, 0196); each seated for the worst-served household, ranked by its walk, the straight distance as the reach is measured; every household within 760 ft of a well or open water (`WATER_REACH_FT`); no well nearest more than 10 households where a seat avoids it (`WELL_SERVES_MAX`); each seat asked before its well is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the lanes' length 2,569 and 5,568 ft (x2.17: 5,568 at 20, 12,083 at 40, 26,220 at 80), their density at most 7.47e-3 ft a sq ft (2,569 ft in 477 by 721 ft at 10; the greater taken); a homestead's extent at most 184 ft; a well drawn 12.4 ft in radius (its diameter 25 ft) and a verge 7 ft off a lane's line (`ACCESS_HALF_FT`), so a site's clearance, 19.4 ft, lies in at most 2 by 2 cells of 64 ft; at most 21 and 29 standing things in one 64 ft cell within 192 ft of a house, on the finished map (x1.38: 29 at 20, 40 at 40, 55 at 80); the wells, the larger of 2 and the households over 10 rounded up (2 at 20, 4 at 40, 8 at 80); the houses' density at most 2.9e-5 a sq ft, so at most density x pi x r squared houses within r of a point and density x 9 x r squared in 3 by 3 cells of r ft, never more than the households; 1 ft a pixel at the hamlet scale. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell; each held flat past 20, a mean over occupied cells not rising with the households as the densest cell does.

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
| slack | per item | 2 | what varies around the typical case (S8): a well whose nearest sites fail, the fallback reached | a crowded cluster |
| the well search (house index, ways index and registry cells examined) | over the run | 1,256 at 20, 2,552 at 40, 5,264 at 80 | 2 at 20, 4 at 40, 8 at 80 wells on the lane-side form, each 628 at 20, 638 at 40, 658 at 80: the worst-served household's nearest lane point from the ways' 3 by 3 cells of 64 ft with the mean 2 legs a cell (18), then its sites nearest first until one is admitted, 10 at the typical (S8: the nearest admitted within a few pops), each its clearance's 2 by 2 cells with the mean 4 things and the cell (20), its nearest wall within 80 ft from the houses about it (20), the households it would serve - about the 10 a well serves, from its 9 cells of 760 ft - (19), its walk (1), and the wells this stage has drawn (half the wells, rounded up) | the typical cluster |
| the service (households re-keyed) | over the run | 238 at 20, 556 at 40, 1,272 at 80 | each well, its 9 cells (9) and the about 10 households it takes, each re-keyed with a push and the stale entry's pop, 1 + 2 x log2 of the households rounded up | the typical cluster |
| the worst-served query (heap top read) | over the run | 2 at 20, 4 at 40, 8 at 80 | each well, the max-heap's top, 1 | every well owed |
| the house index (cells written) | once | 20 at 20, 40 at 40, 80 at 80 | each house filed once in its 760 ft cell | 80 households |

So: the items x 5 x 2, plus the well search, the service, the worst-served query, the house index.

## Totals

- at 20: 2 x 5 x 2 + 1256 + 238 + 2 + 20 = 1536
- at 40: 4 x 5 x 2 + 2552 + 556 + 4 + 40 = 3192
- at 80: 8 x 5 x 2 + 5264 + 1272 + 8 + 80 = 6704

## Growth

From 20 to 80 households the stage grows faster than the households, for a bounded n: the 760 ft reach's 3 by 3 cells hold every household until the density bound passes the household count (151 houses, so past 150 households), so in the program's 20 to 80 every site's neighborhood reads every household, while the wells grow one for every ten; past 150 each well's search is constant and the stage grows with the sites and the wells, linear.

## Earlier findings

- verdict-1, finding 1: fixed - each well's pool heap is built bottom-up, 2 an element, and popped at log2 of the pool
- verdict-1, finding 2: fixed - the 34 cluster sites a house carry their arithmetic, 835 ft over 25 ft
- verdict-1, finding 3: fixed - the nearest wall within 80 ft is the 4 walls of each of the five nearest houses, 20 a site, in the sites row
- verdict-1, finding 4: fixed - the worst-served query is the heap's top, 1 a well
- verdict-1, finding 5: fixed - each well's scan of its 3 by 3 cells' sites against the disc is a row of its own
- verdict-1, finding 6: fixed - the cluster sites in the pool are those of the houses within 908 ft (a site up to 148 ft from its house's center)
- verdict-2, finding 1: fixed - each popped site is tested against the wells this stage drew before it, one distance each, its own row (S4)
- verdict-2, finding 2: fixed - the service row states what its 2 pays for, the push and the stale entry's pop, and the heap's size under lazy invalidation
- verdict-2, finding 3: fixed - a lane site reads only its 2 by 2 cells of 760 ft and the houses within 210 ft, for the wall within 80 ft
- FR-014 re-score: each factor at the typical case (rubric S8): a well's sites are asked nearest the worst-served household first and the nearest is admitted within a few pops, so no site index is built and no pool scanned; each popped site at the mean densities of `items.md`; slack 2 (ask:444-budget-standard; the accept was ask:444-T03-lane_wells-round-3)

## Cheaper algorithms considered

- sweep: not used - the wells are seated one at a time, each for the worst-served household as it stands
- grid or spatial index: used - the registry for a site's clearance, the house index and the site index for its neighborhood
- priority queue: used - the worst-served household (a max-heap) and each well's pool by (form, rung, walk), built bottom-up once the pool is known
- incremental update: used - each well re-keys only the households in its cells
- memoizing what a scan does not change: used - a site's clearance and its five nearest houses, once over the run
