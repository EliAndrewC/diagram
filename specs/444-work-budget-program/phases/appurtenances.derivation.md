# Derivation - appurtenances (feature 444)

## Contract

- Reads: the placed homesteads and each household's laid parts (feature 287: each lot's byre stall, its fixtures by kind and quota, its retirement house and the shared sheds' pockets, laid with the house); the rolled `well_siting`; the parts index of what stands, the track's segments filed in it; the households' count.
- Writes: the byres and shared sheds (`byres`, `farm_sheds`), the farmstead fixtures but the night-soil pit (`farm_fixtures`, the early call), the retirement houses (`retirement_houses`), and on the cluster form the communal wells (`wells`), each with its form.
- Keeps: nothing sought for a part the lot laid - each is drawn where it stands, so none falls short (feature 287); a well off every homestead and every way, its verge included, and within 80 ft of a dwelling's wall (`WELL_SEAT_FT`, 0196); among five houses within the widening reach (190, 300, 520 ft, then 760 ft, `seat_cluster`, 0196); each well seated for the worst-served household, the seat ranked by that household's walk to it; every household within 760 ft of a well or open water (`WATER_REACH_FT`, `reach_wells`); no well nearest more than 10 households where a seat avoids it (`WELL_SERVES_MAX`); each seat asked before its well is drawn (S4). The walk is measured as the reach is, a straight distance (0196's 760 ft).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the parts drawn - byres 4 and 7, shared sheds 1 and 3, fixtures but the sties 31 and 63, retirement houses 5 and 11 - 41 and 84 (x2.05: 84 at 20, 173 at 40, 354 at 80); a homestead's extent at most 184 ft; at most 7 placed parts and 1 track segment in one 64 ft cell; a well drawn 12.4 ft in radius (its diameter 25 ft); the wells, at most two by count (`well_target`) and one more for every ten households past it (`WELL_SERVES_MAX`), the larger of 2 and the households over 10 rounded up (2 at 20, 4 at 40, 8 at 80); the houses' density at most 2.9e-5 a sq ft (10 in 477 by 721 ft at 10, 20 in 750 by 1,085 ft at 20; the greater taken), so at most density x pi x r squared houses within r of a point and density x 9 x r squared in 3 by 3 cells of r ft, never more than the households; the cluster's extent 477 by 721 ft and 750 by 1,085 ft (x1.57 and x1.5: 750 by 1,085 ft at 20, 1,178 by 1,628 ft at 40, 1,849 by 2,442 ft at 80); 1 ft a pixel at the hamlet scale.

## The algorithm

    draw each laid part: its record written and filed in the parts index's cells (nothing is sought)
    on the cluster form:
        the sites: along each homestead's envelope, one a well's diameter (25 ft) apart - a well off every homestead and
            nearest its wall stands at the envelope's edge, and one site a well's width apart misses no seat by more than its
            radius; each site, once over the run (the houses and parts stand through the stage): its clearance against the
            parts and the track in its cells, and its fifth-nearest house from the house index (its 3 by 3 cells of 760 ft),
            so a rung's five-house test is one comparison
        the worst-served household: the top of a max-heap of each household's distance to its nearest well, lazily invalidated
        while a well is owed (the count, then the reach, then the ten):
            the worst-served household's houses within 760 ft, from its 3 by 3 cells; their sites, nearest that household first
                (a heap); for each, the rung's five-house comparison, its walk, and the households it would serve (the
                households in its 3 by 3 cells of 760 ft, each against its kept distance) under the ten
            draw the first admitted; re-key the households in its 3 by 3 cells of 760 ft; test each dry household (beyond 760 ft
                of every well) against it

## Indexes

- parts index: cells of 64 ft; densest 7 placed parts and 1 track segment a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft
- house index: cells of 760 ft, the widest rung, so every rung's houses lie in a point's 3 by 3 cells; densest the houses' density x the cell's area, from a smallest side of 760 ft, never more than the households

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 84 at 20, 173 at 40, 354 at 80 | each part the lots laid, drawn | 80 households |
| the drawing (parts index cells written) | per item | 5 | the record written (1) and filed in at most 4 cells of 64 ft, a part's side under 64 ft (4) | always 5 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the sites (parts and house index cells examined) | over the run | 39,000 at 20, 102,000 at 40, 300,000 at 80 | 30 sites a house (600 at 20, 1,200 at 40, 2,400 at 80): an envelope's edge of 4 x 184 ft over the well's 25 ft; each once - its 4 cells of 64 ft with 7 parts and 1 track segment each (36), its 9 cells of 760 ft (9) and their houses (20 at 20, 40 at 40, 80 at 80) for the fifth-nearest | the cluster form, every site examined |
| the well search (house index cells examined) | over the run | 61,200 at 20, 350,400 at 40, 1,437,360 at 80 | 2 at 20, 4 at 40, 8 at 80 wells, each at most 30,600 at 20, 87,600 at 40, 179,670 at 80: the sites of the houses within 760 ft of the worst-served household (20 at 20, 40 at 40, 53 at 80 houses x 30), each the rung comparison (1), its walk (1), its 9 cells (9) and their households under the ten (20 at 20, 40 at 40, 80 at 80), and the heap's push and pop | every site examined for every well |
| the worst-served query (house index cells examined) | over the run | 58 at 20, 196 at 40, 712 at 80 | each well, the worst-served household's 9 cells of 760 ft and their houses | every well owed |
| the service (households re-keyed) | over the run | 638 at 20, 2,548 at 40, 10,680 at 80 | each well, the households in its 9 cells of 760 ft, each re-keyed with a push, 2 x log2 of the households rounded up, plus the cell | every well owed |
| the dry households (households tested) | over the run | 80 at 20, 240 at 40, 640 at 80 | a household beyond 760 ft of every well is tested against each well drawn while any is dry: the two by count and the reach's, at most the cover of the cluster's extent by squares of 760 x root 2 ft (2 at 20, 4 at 40, 6 at 80), each well testing at most every household | every household dry until the reach is met |
| the house index (cells written) | once | 20 at 20, 40 at 40, 80 at 80 | each house filed once | 80 households |

So: the parts x 5 x 1, plus the sites, the well search, the worst-served query, the service, the dry households and the house index.

## Totals

- at 20: 84 x 5 x 1 + 39000 + 61200 + 58 + 638 + 80 + 20 = 101416
- at 40: 173 x 5 x 1 + 102000 + 350400 + 196 + 2548 + 240 + 40 = 456289
- at 80: 354 x 5 x 1 + 300000 + 1437360 + 712 + 10680 + 640 + 80 = 1751242

## Growth

From 20 to 80 households the stage grows at an exponent of about 2, for a bounded n: the 760 ft reach's 3 by 3 cells hold every household until the density bound passes the household count (151 houses, so past 150 households), so in the program's 20 to 80 every site under the ten reads every household, while the wells grow one for every ten households; past 150 households each well's search is constant and the stage grows with the wells, linear. The dry households' term (the cover of the cluster times the households) is under 0.1 percent of the total at 80.

## Earlier findings

- verdict-1, finding 1: fixed - the sites are one a well's diameter along each homestead's envelope, from the seat rule (off the homestead, within 80 ft of its wall), not 8 a house
- verdict-1, finding 2: fixed - the track's segments are filed in the parts index (1 a cell, measured) and counted in each site's clearance; the engine's verdict is that clearance
- verdict-1, finding 3: fixed - the walk is the straight distance, as the reach is measured (0196's 760 ft)
- verdict-1, finding 4: fixed - the worst-served household's 3 by 3 query is its own row
- verdict-1, finding 5: fixed - the worst-served household is a max-heap's top, lazily invalidated; a well re-keys only the households in its cells, and the dry households, bounded by the cluster's cover, are their own row
- verdict-1, finding 6: fixed - the houses examined are every house in the 3 by 3 cells (density x 9 x r squared, capped by the households), not the five; the fifth-nearest is found once a site
- verdict-1, finding 7: fixed - the service row counts households re-keyed

## Cheaper algorithms considered

- sweep: not used - the wells are seated one at a time, each for the worst-served household as it stands
- grid or spatial index: used - the parts index for a site's clearance and the house index for its neighborhood
- priority queue: used - the worst-served household (a max-heap) and the sites nearest it
- incremental update: used - each well re-keys only the households in its cells
- memoizing what a scan does not change: used - a site's clearance and fifth-nearest house, once over the run, as the houses and parts stand through the stage
