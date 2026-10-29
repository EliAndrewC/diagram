# Derivation - appurtenances (feature 444)

## Contract

- Reads: the placed homesteads and each household's laid parts (feature 287: each lot's byre stall, its fixtures by kind and quota, its retirement house and the shared sheds' pockets, laid with the house); the rolled `well_siting`; the parts index of what stands, the track's segments filed in it; the households' count; the open water (the brook, the channels, the ditches and the ponds' edges), whose segments the reach counts.
- Writes: the byres and shared sheds (`byres`, `farm_sheds`), the farmstead fixtures but the night-soil pit (`farm_fixtures`, the early call), the retirement houses (`retirement_houses`), and on the cluster form the communal wells (`wells`), each with its form.
- Keeps: nothing sought for a part the lot laid - each is drawn where it stands, so none falls short (feature 287); a well off every homestead and every way, its verge included, and within 80 ft of a dwelling's wall (`WELL_SEAT_FT`, 0196); among five houses within the widening reach (190, 300, 520 ft, then 760 ft, `seat_cluster`, 0196); each well seated for the worst-served household, the seat ranked by that household's walk to it; every household within 760 ft of a well or open water (`WATER_REACH_FT`, `reach_wells`); no well nearest more than 10 households where a seat avoids it (`WELL_SERVES_MAX`); each seat asked before its well is drawn (S4). The walk is measured as the reach is, a straight distance (0196's 760 ft).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the parts drawn - byres 4 and 7, shared sheds 1 and 3, fixtures but the sties 31 and 63, retirement houses 5 and 11 - 41 and 84 (x2.05: 84 at 20, 173 at 40, 354 at 80); a homestead's extent at most 184 ft; at most 7 placed parts and 1 track segment in one 64 ft cell; a well drawn 12.4 ft in radius (its diameter 25 ft); a way's verge 7 ft off its line (`ACCESS_HALF_FT`), so a site's clearance, 12.4 + 7 = 19.4 ft, is under 32 ft and lies in at most 2 by 2 cells of 64 ft; a part's longest side at most 63 ft (the threshing yard, measured at 10 and 20), under 64 ft; the wells, at most two by count (`well_target`) and one more for every ten households past it (`WELL_SERVES_MAX`), the larger of 2 and the households over 10 rounded up (2 at 20, 4 at 40, 8 at 80); the houses' density at most 2.9e-5 a sq ft (10 in 477 by 721 ft at 10, 20 in 750 by 1,085 ft at 20; the greater taken), so at most density x pi x r squared houses within r of a point and density x 9 x r squared in 3 by 3 cells of r ft, never more than the households; the cluster's extent 477 by 721 ft and 750 by 1,085 ft (x1.57 and x1.5: 750 by 1,085 ft at 20, 1,178 by 1,628 ft at 40, 1,849 by 2,442 ft at 80); the waters' segments 574 at 20 (x1.34: 770 at 40, 1,032 at 80, measured for washing); a site at most 148 ft from its house's center (half the diagonal of the 184 ft envelope grown by 12.4 ft, the house within it), so the houses with a site within 760 ft of a point lie within 908 ft of it, at most density x pi x 908 squared; 1 ft a pixel at the hamlet scale.

## The algorithm

    draw each laid part: its record written and filed in the parts index's cells (nothing is sought)
    on the cluster form:
        the sites: along each homestead's envelope grown by a well's radius (a well off the homestead has its center 12.4 ft
            outside it), one a well's diameter (25 ft) apart - one site a well's width apart misses no seat by more than its
            radius; each site, once over the run (the houses and parts stand through the stage): its clearance against the
            parts and the track in its cells, and its fifth-nearest house from the house index (its 3 by 3 cells of 760 ft),
            which names its rung - the narrowest of 190, 300, 520 and 760 ft that holds five houses
        each household's distance to open water, once, from a water index of 760 ft cells (its 3 by 3 cells' segments),
            seeding the max-heap's keys (n pushes, heapified)
        the worst-served household: the top of a max-heap of each household's distance to its nearest well, lazily invalidated
        while a well is owed (the count, then the reach, then the ten):
            the worst-served household's sites within 760 ft: the sites filed in the 760 ft cells, its 3 by 3 cells scanned and
                each site's distance tested (1), the ones within 760 ft pushed on a heap keyed by (rung, walk):
                the widening reach is the key's first part, so a site is popped once a well; for each, its walk and the households
                it would serve (the households in its 3 by 3 cells of 760 ft, each against its kept distance) under the ten, the
                seat serving fewest past ten kept as the fallback (one comparison)
            draw the first admitted, or the fallback where none is (the ten gives way only where no seat avoids it); re-key the
                households in its 3 by 3 cells of 760 ft; while the heap's top is beyond 760 ft a household is dry (one comparison)

## Indexes

- parts index: cells of 64 ft; densest 7 placed parts and 1 track segment a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft
- house index: cells of 760 ft, the widest rung, so every rung's houses lie in a point's 3 by 3 cells; densest the houses' density x the cell's area, from a smallest side of 760 ft, never more than the households
- site index: cells of 760 ft, the house index's own, each site filed once; densest the sites of the houses within the cell grown by 148 ft, from a smallest side of 760 ft
- water index: cells of 760 ft, each water segment filed in the cells it crosses; densest every segment, from a smallest side of 760 ft (a household's open water within 760 ft lies in its 3 by 3 cells)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 84 at 20, 173 at 40, 354 at 80 | each part the lots laid, drawn | 80 households |
| the drawing (parts index cells written) | per item | 5 | the record written (1) and filed in at most 4 cells of 64 ft, a part's side under 64 ft (4) | always 5 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the sites (parts and house index cells examined) | over the run | 44,200 at 20, 115,600 at 40, 340,000 at 80 | 34 sites a house (680 at 20, 1,360 at 40, 2,720 at 80): the envelope grown by the well's radius as a square, 4 x (184 + 2 x 12.4) = 835 ft, over the well's 25 ft, rounded up; each once - its 4 cells of 64 ft with 7 parts and 1 track segment each (36), its 9 cells of 760 ft (9) and their houses (20 at 20, 40 at 40, 80 at 80) for the fifth-nearest | the cluster form, every site examined |
| the well search (house index cells examined) | over the run | 70,720 at 20, 402,560 at 40, 2,397,952 at 80 | 2 at 20, 4 at 40, 8 at 80 wells, each at most its pool, the sites within 760 ft of the worst-served household - those of the houses within 908 ft, 20 at 20, 40 at 40, 76 at 80 houses x 34, 680 at 20, 1,360 at 40, 2,584 at 80 - each popped once by its (rung, walk) key: its walk (1), the rung read (1), its 9 cells (9) and their households under the ten (20 at 20, 40 at 40, 80 at 80), the fallback's comparison (1), and the heap's push and pop, 2 x log2 of the pool rounded up | every site examined for every well, every rung reached |
| the worst-served query (site index cells examined) | over the run | 1,378 at 20, 5,476 at 40, 21,832 at 80 | each well, the worst-served household's 9 cells of 760 ft (9) and the sites in them, each its distance tested (1): the sites of the houses within the 3 by 3 block grown by 148 ft, 20 at 20, 40 at 40, 80 at 80 houses x 34 | every well owed |
| the service (households re-keyed) | over the run | 458 at 20, 2,116 at 40, 9,672 at 80 | each well, its 9 cells of 760 ft (9) and the households in them, at most every household, each re-keyed with a push, 1 + 2 x log2 of the households rounded up | every well owed |
| the dry households (heap top compared) | over the run | 2 at 20, 4 at 40, 8 at 80 | one comparison a well: the max-heap's top against 760 ft; a household a well brings within reach lies in its 3 by 3 cells, which the service re-keys | every well owed |
| the site index (site index cells written) | once | 680 at 20, 1,360 at 40, 2,720 at 80 | each site filed once | 80 households |
| the open water (water index cells examined) | once | 11,660 at 20, 31,160 at 40, 83,280 at 80 | each household's 9 cells of 760 ft (9) and their segments, at most every segment (574 at 20, 770 at 40, 1,032 at 80), its distance to the nearest | 80 households |
| the heap's seed | once | 20 at 20, 40 at 40, 80 at 80 | the households' keys, heapified, one each | 80 households |
| the wells drawn (registry cells written) | over the run | 10 at 20, 20 at 40, 40 at 80 | each well recorded (1) and filed in at most 4 cells (4) | every well owed |
| the house index (cells written) | once | 20 at 20, 40 at 40, 80 at 80 | each house filed once | 80 households |

So: the parts x 5 x 1, plus the sites, the worst-served query, the well search, the service, the dry households, the site index, the open water, the heap's seed, the wells drawn and the house index.

## Totals

- at 20: 84 x 5 x 1 + 44200 + 1378 + 70720 + 458 + 2 + 680 + 11660 + 20 + 10 + 20 = 129568
- at 40: 173 x 5 x 1 + 115600 + 5476 + 402560 + 2116 + 4 + 1360 + 31160 + 40 + 20 + 40 = 559241
- at 80: 354 x 5 x 1 + 340000 + 21832 + 2397952 + 9672 + 8 + 2720 + 83280 + 80 + 40 + 80 = 2857434

## Growth

From 20 to 80 households the stage grows at an exponent of about 2, for a bounded n: the 760 ft reach's 3 by 3 cells hold every household until the density bound passes the household count (151 houses, so past 150 households), so in the program's 20 to 80 every site under the ten reads every household, while the wells grow one for every ten households; past 150 households each well's search is constant and the stage grows with the wells, linear. No term grows as the wells times the households past 150: the dry households are one comparison a well.

## Earlier findings

- verdict-1, finding 1: fixed - the sites are one a well's diameter along each homestead's envelope, from the seat rule (off the homestead, within 80 ft of its wall), not 8 a house
- verdict-1, finding 2: fixed - the track's segments are filed in the parts index (1 a cell, measured) and counted in each site's clearance; the engine's verdict is that clearance
- verdict-1, finding 3: fixed - the walk is the straight distance, as the reach is measured (0196's 760 ft)
- verdict-1, finding 4: fixed - the worst-served household's 3 by 3 query is its own row
- verdict-1, finding 5: fixed - the worst-served household is a max-heap's top, lazily invalidated; a well re-keys only the households in its cells, and the dry households, bounded by the cluster's cover, are their own row
- verdict-1, finding 6: fixed - the houses examined are every house in the 3 by 3 cells (density x 9 x r squared, capped by the households), not the five; the fifth-nearest is found once a site
- verdict-1, finding 7: fixed - the service row counts households re-keyed
- verdict-1, finding 5 (its remainder): fixed - the wells x households pass is gone; the dry households are one comparison a well
- verdict-1, finding 6 (its remainder): fixed - every rung reached is counted: a site is popped once a well under the (rung, walk) key
- verdict-2, finding 1: fixed - the sites' heap is keyed by (rung, walk), the rung read from the site's memoized fifth-nearest, so a site is popped once a well across the four rungs
- verdict-2, finding 2: fixed - the fallback, the seat serving fewest past ten, kept at one comparison a site and drawn where none is admitted
- verdict-2, finding 3: fixed - the dry households' row is one comparison a well, the heap's top against 760 ft
- verdict-2, finding 4: fixed - the service charges the 9 cells once and each household its push, 9 + n x (1 + 2 x log2 n)
- verdict-2, finding 5: fixed - the dry row's wells are the contract's, at most two and four at 20 and 40
- verdict-2, finding 6: fixed - 34 sites a house, on the envelope grown by the well's radius
- verdict-2, finding 7: fixed - a part's longest side (63 ft) and the verge (7 ft) are in the Bounds, and the clearance lies in 2 by 2 cells

- verdict-3, finding 1: fixed - the pool is the sites within 760 ft of the household, those of the houses within 908 ft (a site at most 148 ft from its house's center), found from a site index of 760 ft cells, each scanned site's distance tested
- verdict-3, finding 2: fixed - the heap's seed, each household's distance to open water, and the wells drawn are rows of their own; the heap's push and pop is stated as 2 x log2 of the pool
- verdict-3, finding 3: disputed - memoizing each site's households within 760 ft breaks even at 20 and 40 by the verdict's own figures, and the ten's nearest has no distance limit, so a site's memo would miss a dry household beyond it; the 9-cell scan stays

## Cheaper algorithms considered

- sweep: not used - the wells are seated one at a time, each for the worst-served household as it stands
- grid or spatial index: used - the parts index for a site's clearance and the house index for its neighborhood
- priority queue: used - the worst-served household (a max-heap) and the sites nearest it
- incremental update: used - each well re-keys only the households in its cells
- memoizing what a scan does not change: used - a site's clearance and fifth-nearest house, once over the run, as the houses and parts stand through the stage
