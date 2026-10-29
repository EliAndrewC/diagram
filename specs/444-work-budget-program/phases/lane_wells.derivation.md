# Derivation - lane_wells (feature 444)

## Contract

- Reads: the wells drawn so far and `well_target` (the count owed, at most two); the rolled `well_siting` and which form was tried before the lanes; the lanes as laid (their lines and verges); the placed homesteads; the registry of what stands; the households' count.
- Writes: the communal wells still owed, each with its form (`lane`, `cluster` or `fallback`); the wells the reach and the ten add (`meta.wells_for_reach`, `meta.wells_for_ten`); `meta.well_fallback`, `meta.dry_households`.
- Keeps: the lane-side form on a lane's verge, clear of the tread, a dwelling's wall within 80 ft (`WELL_SEAT_FT`, 0196); then the cluster form, among five houses within the widening reach (190, 300, 520 ft, then 760 ft), off every lane and verge (0196); then the recorded fallback, among three houses, then two, at the 95 ft check (`THREE_THEN_TWO`: 190, 300 and 520 ft for three, 520 ft for two), marked `fallback` (a DEVIATION, 0196); each seated for the worst-served household, ranked by its walk, the straight distance as the reach is measured; every household within 760 ft of a well or open water (`WATER_REACH_FT`); no well nearest more than 10 households where a seat avoids it (`WELL_SERVES_MAX`); each seat asked before its well is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the lanes' length 2,569 and 5,568 ft (x2.17: 5,568 at 20, 12,083 at 40, 26,220 at 80), their density at most 7.47e-3 ft a sq ft (2,569 ft in 477 by 721 ft at 10; the greater taken); a homestead's extent at most 184 ft; a well drawn 12.4 ft in radius (its diameter 25 ft) and a verge 7 ft off a lane's line (`ACCESS_HALF_FT`), so a site's clearance, 19.4 ft, lies in at most 2 by 2 cells of 64 ft; at most 21 and 29 standing things in one 64 ft cell within 192 ft of a house, on the finished map (x1.38: 29 at 20, 40 at 40, 55 at 80); the wells, the larger of 2 and the households over 10 rounded up (2 at 20, 4 at 40, 8 at 80); the houses' density at most 2.9e-5 a sq ft, so at most density x pi x r squared houses within r of a point and density x 9 x r squared in 3 by 3 cells of r ft, never more than the households; 1 ft a pixel at the hamlet scale.

## The algorithm

    the sites, each once over the run (the lanes, houses and parts stand through the stage):
        lane sites: along each lane, on each verge, one a well's diameter (25 ft) apart
        cluster sites: along each homestead's envelope grown by a well's radius, one a well's diameter apart (34 a house)
        each: its clearance against the registry's things in its cells (for a cluster site, the lanes and verges among them),
            and its five nearest houses from the house index (its 3 by 3 cells of 760 ft), which name its rungs - the
            narrowest reach holding five (the cluster form), three, or two (the fallback) - and its nearest wall (80 ft)
    the worst-served household: the top of a max-heap of each household's distance to its nearest well, lazily invalidated
    while a well is owed (the count, then the reach, then the ten):
        the worst-served household's sites within 760 ft, from its 3 by 3 cells, on a heap keyed by (form, rung, walk): the
            forms' order and the widening reach are the key, so a site is popped once a well
        each popped: its walk and the households it would serve (its 3 by 3 cells' households, each against its kept distance)
            under the ten, the seat serving fewest past ten kept as the last resort (one comparison)
        draw the first admitted, or that seat; re-key the households in its 3 by 3 cells; the heap's top against 760 ft says
            whether a household is dry (one comparison)

## Indexes

- registry: cells of 64 ft; densest 29 standing things a cell at 20, at its measured rate (29 at 20, 40 at 40, 55 at 80), from a smallest side of 64 ft
- house index: cells of 760 ft, the widest rung, so every rung's houses lie in a point's 3 by 3 cells; densest the houses' density x the cell's area, from a smallest side of 760 ft, never more than the households
- site index: cells of 760 ft, the house index's own, the sites filed in them, so the worst-served household's sites lie in its 3 by 3 cells; densest the lanes' density x 2 x the area over 25 ft plus the envelope sites of the houses in it, from a smallest side of 760 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 2 at 20, 4 at 40, 8 at 80 | the wells drawn here, at most all that are owed | 80 households |
| the drawing (registry cells written) | per item | 5 | the record written (1) and filed in at most 4 cells of 64 ft (4) | always 5 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the sites (registry and house index cells examined) | over the run | 190,294 at 20, 542,191 at 40, 1,604,394 at 80 | the lane sites, 2 x the lanes' length over 25 ft (446 at 20, 967 at 40, 2,098 at 80), and 34 cluster sites a house - the 184 ft square grown by the 12.4 ft radius each side, 4 x 208.8 = 835 ft, over 25 ft, 33.4 rounded up - (680 at 20, 1,360 at 40, 2,720 at 80); each once: its 2 by 2 cells of 64 ft with their things and the cell (120 at 20, 164 at 40, 224 at 80), its 9 cells of 760 ft (9) and their houses (20 at 20, 40 at 40, 80 at 80) for the five nearest, and the 4 walls of each of those five houses for the nearest wall within 80 ft (20) | every site examined |
| the well search (house index cells examined) | over the run | 101,340 at 20, 614,328 at 40, 3,111,312 at 80 | 2 at 20, 4 at 40, 8 at 80 wells, each at most its pool, the sites within 760 ft of the worst-served household (1,126 at 20, 2,327 at 40, 3,669 at 80: the lane sites, 2 x the lanes' density x pi x 760 squared over 25 ft, capped by the lane sites, 446 at 20, 967 at 40, 1,085 at 80, and 34 a house of the houses within 908 ft, a site lying up to 148 ft from its house's center, 20 at 20, 40 at 40, 76 at 80), each popped once - its walk (1), its rung read (1), its 9 cells (9) and their households under the ten (20 at 20, 40 at 40, 80 at 80), the last resort's comparison (1), the heap built bottom-up once the pool is known (2 an element) and its pop, log2 of the pool rounded up | every site examined for every well, every form and rung reached |
| the worst-served query (heap top read) | over the run | 2 at 20, 4 at 40, 8 at 80 | each well, the max-heap's top, 1 | every well owed |
| the pool's scan (site index cells examined) | over the run | 2,270 at 20, 9,344 at 40, 38,616 at 80 | each well, the worst-served household's 9 cells of 760 ft (9) and every site in them, each tested against the 760 ft disc (1); at these sizes the cells hold every site (1,126 at 20, 2,327 at 40, 4,818 at 80) | every well owed |
| the service (households re-keyed) | over the run | 458 at 20, 2,116 at 40, 9,672 at 80 | each well, its 9 cells (9) and the households in them, at most every household, each re-keyed with a push, 1 + 2 x log2 of the households rounded up | every well owed |
| the dry households (heap top compared) | over the run | 2 at 20, 4 at 40, 8 at 80 | one comparison a well, the max-heap's top against 760 ft | every well owed |
| the site index (site index cells written) | once | 1,126 at 20, 2,327 at 40, 4,818 at 80 | each site filed once in its 760 ft cell | 80 households |
| the house index (cells written) | once | 20 at 20, 40 at 40, 80 at 80 | each house filed once | 80 households |

So: the wells x 5 x 1, plus the sites, the pool's scan, the well search, the worst-served query, the service, the dry households, the house index and the site index.

## Totals

- at 20: 2 x 5 x 1 + 190294 + 2270 + 101340 + 2 + 458 + 2 + 20 + 1126 = 295522
- at 40: 4 x 5 x 1 + 542191 + 9344 + 614328 + 4 + 2116 + 4 + 40 + 2327 = 1170374
- at 80: 8 x 5 x 1 + 1604394 + 38616 + 3111312 + 8 + 9672 + 8 + 80 + 4818 = 4768948

## Growth

From 20 to 80 households the stage grows faster than the households, for a bounded n: the 760 ft reach's 3 by 3 cells hold every household until the density bound passes the household count (151 houses, so past 150 households), so in the program's 20 to 80 every site's neighborhood reads every household, while the wells grow one for every ten; past 150 each well's search is constant and the stage grows with the sites and the wells, linear.

## Earlier findings

- verdict-1, finding 1: fixed - each well's pool heap is built bottom-up, 2 an element, and popped at log2 of the pool
- verdict-1, finding 2: fixed - the 34 cluster sites a house carry their arithmetic, 835 ft over 25 ft
- verdict-1, finding 3: fixed - the nearest wall within 80 ft is the 4 walls of each of the five nearest houses, 20 a site, in the sites row
- verdict-1, finding 4: fixed - the worst-served query is the heap's top, 1 a well
- verdict-1, finding 5: fixed - each well's scan of its 3 by 3 cells' sites against the disc is a row of its own
- verdict-1, finding 6: fixed - the cluster sites in the pool are those of the houses within 908 ft (a site up to 148 ft from its house's center)

## Cheaper algorithms considered

- sweep: not used - the wells are seated one at a time, each for the worst-served household as it stands
- grid or spatial index: used - the registry for a site's clearance, the house index and the site index for its neighborhood
- priority queue: used - the worst-served household (a max-heap) and each well's pool by (form, rung, walk), built bottom-up once the pool is known
- incremental update: used - each well re-keys only the households in its cells
- memoizing what a scan does not change: used - a site's clearance and its five nearest houses, once over the run
