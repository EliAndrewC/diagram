# Derivation - appurtenances (feature 444)

## Contract

- Reads: the placed homesteads and each household's laid parts (feature 287: each lot's byre stall, its fixtures by kind and quota, its retirement house and the shared sheds' pockets, laid with the house); the rolled `well_siting`; the parts index of what stands, the track's segments filed in it; the households' count; the open water (the brook, the channels, the ditches and the ponds' edges), whose segments the reach counts.
- Writes: the byres and shared sheds (`byres`, `farm_sheds`), the farmstead fixtures but the night-soil pit (`farm_fixtures`, the early call), the retirement houses (`retirement_houses`), and on the cluster form the communal wells (`wells`), each with its form.
- Keeps: nothing sought for a part the lot laid - each is drawn where it stands, so none falls short (feature 287); a well off every homestead and every way, its verge included, and within 80 ft of a dwelling's wall (`WELL_SEAT_FT`, 0196); among five houses within the widening reach (190, 300, 520 ft, then 760 ft, `seat_cluster`, 0196); each well seated for the worst-served household, the seat ranked by that household's walk to it; every household within 760 ft of a well or open water (`WATER_REACH_FT`, `reach_wells`); no well nearest more than 10 households where a seat avoids it (`WELL_SERVES_MAX`); each seat asked before its well is drawn (S4). The walk is measured as the reach is, a straight distance (0196's 760 ft).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the parts drawn - byres 4 and 7, shared sheds 1 and 3, fixtures but the sties 31 and 63, retirement houses 5 and 11 - 41 and 84 (x2.05: 84 at 20, 173 at 40, 354 at 80); a homestead's extent at most 184 ft; at most 7 placed parts and 1 track segment in one 64 ft cell; a well drawn 12.4 ft in radius (its diameter 25 ft); a way's verge 7 ft off its line (`ACCESS_HALF_FT`), so a site's clearance, 12.4 + 7 = 19.4 ft, is under 32 ft and lies in at most 2 by 2 cells of 64 ft; a part's longest side at most 63 ft (the threshing yard, measured at 10 and 20), under 64 ft; the wells, at most two by count (`well_target`) and one more for every ten households past it (`WELL_SERVES_MAX`), the larger of 2 and the households over 10 rounded up (2 at 20, 4 at 40, 8 at 80); the houses' density at most 2.9e-5 a sq ft (10 in 477 by 721 ft at 10, 20 in 750 by 1,085 ft at 20; the greater taken), so at most density x pi x r squared houses within r of a point and density x 9 x r squared in 3 by 3 cells of r ft, never more than the households; the cluster's extent 477 by 721 ft and 750 by 1,085 ft (x1.57 and x1.5: 750 by 1,085 ft at 20, 1,178 by 1,628 ft at 40, 1,849 by 2,442 ft at 80); the waters' segments 574 at 20 (x1.34: 770 at 40, 1,032 at 80, measured for washing); a site at most 148 ft from its house's center (half the diagonal of the 184 ft envelope grown by 12.4 ft, the house within it), so the houses with a site within 760 ft of a point lie within 908 ft of it, at most density x pi x 908 squared; 1 ft a pixel at the hamlet scale. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell; each held flat past 20, a mean over occupied cells not rising with the households as the densest cell does. The admission share (FR-014; the round arbiter's ruling ask:444-T09-rescore-batch; measured 2026-10-28 on the reference manifests at 10 and 20): of the envelope sites 34 a house, 0.54 and 0.49 are clear for a well's 19.4 ft box with a dwelling's wall within 80 ft (0.49 taken), so a well past the first is admitted at the 1 / 0.49 = 2.04th site popped; the first well, owed where more than 10 households share it, is admitted nowhere under the ten - every site serves them all - so it costs its whole pool, and the seat serving fewest past ten is drawn.

## The algorithm

    draw each laid part: its record written and filed in the parts index's cells (nothing is sought)
    while a well is owed (the count, then the reach, then the ten), on the cluster form:
        the worst-served household: the top of a max-heap of each household's distance to its nearest well
        its nearest homestead edge, from the parts' 3 by 3 cells of 64 ft; the sites along that homestead's envelope grown by a well's radius, one a well's diameter apart, walked outward nearest first
        each site: clear of the registry's things in its 2 by 2 cells (S4), a dwelling's wall within 80 ft, the households it would
            serve under the ten from its 9 cells of 760 ft, its walk, and the wells this stage drew; the first admitted is the well
        draw it; re-key the households it takes

## Indexes

- house index: cells of 760 ft, the widest reach, so the households a well would serve lie in its 3 by 3 cells; densest the about 10 a well serves at the typical (`WELL_SERVES_MAX`), from a smallest side of 760 ft
- registry: cells of 64 ft; densest the mean 4 things a cell near the houses (`items.md`'s typical densities), from a smallest side of 64 ft against a well's 19.4 ft clearance, in at most 2 by 2 cells
- parts index: cells of 64 ft (the homesteads'); densest the mean 3 parts an occupied cell (`items.md`), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 84 at 20, 173 at 40, 354 at 80 | each part the lots laid, drawn (byres, shared sheds, fixtures but the sties, retirement houses; 41 and 84 at 10 and 20, x2.05), nothing sought | 80 households |
| the drawing (registry cells written) | per item | 5 | the record written (1) and filed in at most 4 cells of 64 ft (4) | always 5 |
| slack | per item | 1 | what varies around the typical case (S8): the spread around the mean pops, inside the first well's whole pool | not applicable |
| the first well (house index, parts index and registry cells examined) | over the run | 55,080 at 20, 138,720 at 40, 372,096 at 80 | its pool, the 34 envelope sites a house of the houses whose sites lie within 760 ft (within 908 ft of the household, at most 76), capped by the households (680 at 20, 1,360 at 40, 2,584 at 80), every site popped (the ten admits none), each 80 at 20, 101 at 40, 143 at 80: its clearance in the 2.6 cells a 38.8 ft box covers with the mean 4 things and the cell (13), a dwelling's wall within 80 ft from the 3 by 3 cells of 64 ft with the mean 3 parts and the cell (36), the households it would serve read from its 9 cells of 760 ft, every household below about 150 (9 + n), its walk (1), the wells drawn (half, rounded up); and the fallback's comparison, 1 a site | the typical cluster |
| the later wells (house index, parts index and registry cells examined) | over the run | 200 at 20, 727 at 40, 2,295 at 80 | the wells past the first (1 at 20, 3 at 40, 7 at 80), each the worst-served household's nearest homestead edge from the parts' 3 by 3 cells with the mean 3 parts and the cell (36) and 2.04 sites popped (1 / p), each at the first well's per-site cost | the typical cluster |
| the service (households re-keyed) | over the run | 238 at 20, 556 at 40, 1,272 at 80 | each well, its 9 cells (9) and the about 10 households it takes, each re-keyed with a push and the stale entry's pop, 1 + 2 x log2 of the households rounded up | the typical cluster |
| the worst-served query (heap top read) | over the run | 2 at 20, 4 at 40, 8 at 80 | each well, the max-heap's top, 1 | every well owed |
| the house index (cells written) | once | 20 at 20, 40 at 40, 80 at 80 | each house filed once in its 760 ft cell | 80 households |
| the wells drawn (registry cells written) | over the run | 2 x 5 at 20, 4 x 5 at 40, 8 x 5 at 80 | each well recorded (1) and filed in at most 4 cells (4) | every well owed |

So: the items x 5 x 1, plus the first well, the later wells, the service, the worst-served query and the wells drawn and the house index.

## Totals

- at 20: 84 x 5 x 1 + 55080 + 200 + 238 + 2 + 20 + 2 x 5 = 55970
- at 40: 173 x 5 x 1 + 138720 + 727 + 556 + 4 + 40 + 4 x 5 = 140932
- at 80: 354 x 5 x 1 + 372096 + 2295 + 1272 + 8 + 80 + 8 x 5 = 377561

## Growth

From 20 to 80 households the stage grows at an exponent of about 1.38, past 1.15, for a bounded n: a well's households are read from its 3 by 3 cells of 760 ft, which hold every household until the density passes the household count (about 150 households), so each site popped reads n; past 150 it reads a bounded block and the stage grows with the wells, linear.


## Earlier findings

- verdict-4, finding 1: fixed - the households a site would serve read 9 + n from its 760 ft cells; the first well costs its whole pool (the ten admits none); the later wells 1/p pops, p = 0.49 measured on the reference geometry; the wall test and the find at their 3 by 3 cells; the five-nearest key dropped (the forms' order is the search's, no rung key)
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
- FR-014 re-score: each factor at the typical case (rubric S8): a well's sites are asked nearest the worst-served household first and the nearest is admitted within a few pops, so no site index is built and no pool scanned; each popped site at the mean densities of `items.md`; slack 2 (ask:444-budget-standard; the accept was ask:444-T03-appurtenances-round-4)

## Cheaper algorithms considered

- sweep: not used - the wells are seated one at a time, each for the worst-served household as it stands
- grid or spatial index: used - the parts index for a site's clearance and the house index for its neighborhood
- priority queue: used - the worst-served household is a max-heap's top; a household's sites are walked nearest first
- incremental update: used - each well re-keys only the households in its cells
- memoizing what a scan does not change: not used - the sites are popped nearest first and only the few the search reaches are tested, so nothing is memoized over the run
