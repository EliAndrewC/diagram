# Derivation - appurtenances (feature 444)

## Contract

- Reads: the placed homesteads and each household's laid parts (feature 287: each lot's byre stall, its fixtures by kind and quota, its retirement house and the shared sheds' pockets, laid with the house); the rolled `well_siting`; the parts index of what stands, the track's segments filed in it; the households' count; the open water (the brook, the channels, the ditches and the ponds' edges), whose segments the reach counts.
- Writes: the byres and shared sheds (`byres`, `farm_sheds`), the farmstead fixtures but the night-soil pit (`farm_fixtures`, the early call), the retirement houses (`retirement_houses`), and on the cluster form the communal wells (`wells`), each with its form.
- Keeps: nothing sought for a part the lot laid - each is drawn where it stands, so none falls short (feature 287); a well off every homestead and every way, its verge included, and within 80 ft of a dwelling's wall (`WELL_SEAT_FT`, 0196); among five houses within the widening reach (190, 300, 520 ft, then 760 ft, `seat_cluster`, 0196); each well seated for the worst-served household, the seat ranked by that household's walk to it; every household within 760 ft of a well or open water (`WATER_REACH_FT`, `reach_wells`); no well nearest more than 10 households where a seat avoids it (`WELL_SERVES_MAX`); each seat asked before its well is drawn (S4). The walk is measured as the reach is, a straight distance (0196's 760 ft).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the parts drawn - byres 4 and 7, shared sheds 1 and 3, fixtures but the sties 31 and 63, retirement houses 5 and 11 - 41 and 84 (x2.05: 84 at 20, 173 at 40, 354 at 80); a homestead's extent at most 184 ft; at most 7 placed parts and 1 track segment in one 64 ft cell; a well drawn 12.4 ft in radius (its diameter 25 ft); a way's verge 7 ft off its line (`ACCESS_HALF_FT`), so a site's clearance, 12.4 + 7 = 19.4 ft, is under 32 ft and lies in at most 2 by 2 cells of 64 ft; a part's longest side at most 63 ft (the threshing yard, measured at 10 and 20), under 64 ft; the wells, at most two by count (`well_target`) and one more for every ten households past it (`WELL_SERVES_MAX`), the larger of 2 and the households over 10 rounded up (2 at 20, 4 at 40, 8 at 80); the houses' density at most 2.9e-5 a sq ft (10 in 477 by 721 ft at 10, 20 in 750 by 1,085 ft at 20; the greater taken), so at most density x pi x r squared houses within r of a point and density x 9 x r squared in 3 by 3 cells of r ft, never more than the households; the cluster's extent 477 by 721 ft and 750 by 1,085 ft (x1.57 and x1.5: 750 by 1,085 ft at 20, 1,178 by 1,628 ft at 40, 1,849 by 2,442 ft at 80); the waters' segments 574 at 20 (x1.34: 770 at 40, 1,032 at 80, measured for washing); a site at most 148 ft from its house's center (half the diagonal of the 184 ft envelope grown by 12.4 ft, the house within it), so the houses with a site within 760 ft of a point lie within 908 ft of it, at most density x pi x 908 squared; 1 ft a pixel at the hamlet scale. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell; each held flat past 20, a mean over occupied cells not rising with the households as the densest cell does. The admission share (FR-014; the round arbiter's ruling ask:444-T09-rescore-batch; measured 2026-10-28 on the reference manifests at 10 and 20): of the envelope sites 34 a house, 0.54 and 0.49 are clear for a well's 19.4 ft box with a dwelling's wall within 80 ft (0.49 taken), so a well past the first is admitted at the 1 / 0.49 = 2.04th site popped; the first well, owed where more than 10 households share it, is admitted nowhere under the ten - every site serves them all - so it costs its whole pool, and the seat serving fewest past ten is drawn.

## The algorithm

    draw each laid part: its record written and filed in the parts index's cells (nothing is sought)
    while a well is owed (the count, then the reach, then the ten), on the cluster form:
        the heap seeded once: each household's distance to open water from the water index, heapified
        the worst-served household: the top of a max-heap of each household's distance to its nearest well
        its nearest homestead edge, from the parts' 3 by 3 cells of 64 ft; the sites along that homestead's envelope grown by a well's radius, one a well's diameter apart, walked outward nearest first
        each site: clear of the registry's things in its 2 by 2 cells (S4), a dwelling's wall within 80 ft, the households it would
            serve under the ten and the five-houses rung (190, 300, 520, then 760 ft) from its 9 cells of 760 ft, its walk, and the wells this stage drew; the first admitted is the well
        draw it; re-key the households it takes

## Indexes

- house index: cells of 760 ft, the widest reach, so the households a well would serve lie in its 3 by 3 cells; densest the about 10 a well serves at the typical (`WELL_SERVES_MAX`), from a smallest side of 760 ft
- water index: cells of 120 ft over the open water's segments, built once, so a household's nearest water lies in its 3 by 3 cells (washing's figure); densest the about 5.6 segments a crossed 120 ft cell (the 3.7 a crossed 64 ft cell scaled to the longer chord), from a smallest side of 120 ft
- registry: cells of 64 ft; the mean 5.5 things a cell within 3 cells of a house, where every site lies (`items.md`'s typical densities), from a smallest side of 64 ft against a well's 19.4 ft clearance, in at most 2 by 2 cells
- parts index: cells of 64 ft (the homesteads'); densest the mean 3 parts an occupied cell (`items.md`), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 84 at 20, 173 at 40, 354 at 80 | each part the lots laid, drawn (byres, shared sheds, fixtures but the sties, retirement houses; 41 and 84 at 10 and 20, x2.05), nothing sought | 80 households |
| the drawing (registry cells written) | per item | 5 | the record written (1) and filed in at most 4 cells of 64 ft (4) | always 5 |
| slack | per item | 1 | what varies around the typical case (S8): the spread around the mean pops, inside the first well's whole pool | not applicable |
| the first well (house index, parts index and registry cells examined) | over the run | 249 at 20, 330 at 40, 493 at 80 | searched like the later wells (ask:444-T09-rescore-batch-2): with no well drawn and more than 10 households, every site serves all n (the contract's all-n service), so the ten test's answer is known before any site is read and the seat is the walk's - the worst-served household's nearest homestead edge from the parts' 3 by 3 cells with the mean 3 parts and the cell (36) and 2.04 sites popped (1 / p, p = 0.49 measured), each 104 at 20, 144 at 40, 224 at 80: its clearance in the 2.6 cells a 38.8 ft box covers with the mean 5.5 things within 3 cells of a house and the cell (2.6 x 6.5, 17), a dwelling's wall within 80 ft from the 3 by 3 cells of 64 ft with the mean 3 parts and the cell (36), the households read from its 9 cells of 760 ft, every household below about 150 (9 + n), each placed in its reach band for the five-houses rung - the houses within 190, 300, 520 and 760 ft - and the ten (1 each, n), its walk (1), no wells drawn yet (0); and the fallback's comparison (1) | the typical cluster |
| the later wells (house index, parts index and registry cells examined) | over the run | 251 at 20, 1,002 at 40, 3,508 at 80 | the wells past the first (1 at 20, 3 at 40, 7 at 80), each the worst-served household's nearest homestead edge (36) and 2.04 sites popped (1 / p), each at the first well's per-site cost plus the wells drawn (half, rounded up) | the typical cluster |
| the service (households re-keyed) | over the run | 348 at 20, 946 at 40, 2,322 at 80 | the first well re-keys every household (every site serves them all), its 9 cells (9) and n households; each later well its 9 cells and the about 10 households it takes; each re-keyed with a push and the stale entry's pop, 1 + 2 x log2 of the households rounded up | the typical cluster |
| the worst-served query (heap top read) | over the run | 2 at 20, 4 at 40, 8 at 80 | each well, the max-heap's top, 1 | every well owed |
| the heap's seed (water index cells examined, heap built) | over the run | 580 at 20, 1,160 at 40, 2,320 at 80 | each household's distance to open water from the water index's 3 by 3 cells of 120 ft, the about 3 a water crosses each with about 5.6 segments, and its projection (27, washing's figure on the same segments), and the max-heap built bottom-up over the households (2 a household) | the typical cluster |
| the water index (cells written) | once | 780 at 20, 1,090 at 40, 1,530 at 80 | the open water's segments (574 at 20, 770 at 40, 1,032 at 80) each walked through the 120 ft cells it crosses at a random angle: its length x (4/pi) over 120 ft, plus 1 a segment (washing's figure) | 80 households |
| the house index (cells written) | once | 20 at 20, 40 at 40, 80 at 80 | each house filed once in its 760 ft cell | 80 households |
| the wells drawn (registry cells written) | over the run | 2 x 5 at 20, 4 x 5 at 40, 8 x 5 at 80 | each well recorded (1) and filed in at most 4 cells (4) | every well owed |

So: the items x 5 x 1, plus the first well, the later wells, the service, the worst-served query, the heap's seed, the water index and the wells drawn and the house index.

## Totals

- at 20: 84 x 5 x 1 + 249 + 251 + 348 + 2 + 580 + 780 + 20 + 2 x 5 = 2660
- at 40: 173 x 5 x 1 + 330 + 1002 + 946 + 4 + 1160 + 1090 + 40 + 4 x 5 = 5457
- at 80: 354 x 5 x 1 + 493 + 3508 + 2322 + 8 + 2320 + 1530 + 80 + 8 x 5 = 12071

## Growth

From 20 to 80 households the stage grows at an exponent of about 1.09, within 1.15: the parts and the households grow linearly, and each site popped reads the households in its 760 ft cells, n below about 150, a few sites a well.


## Earlier findings

- verdict-5, finding 1: fixed - the heap's seed counted, each household's distance to open water through the 120 ft water index (27) and a bottom-up heapify, with the index's build; the five-houses rung counted, each household read placed in its reach band (n a site); the first well searched like the later ones (36 + 2.04 pops), the all-n service settling the ten; no wells drawn at the first; the first well re-keys n; the clearance at the near-house 5.5, 17; the 2.9e-5 density's pool gone with the pool (ask:444-T09-rescore-batch-2)
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

- verdict-3, finding 1: fixed - the pool is the sites within 760 ft of the household, those of the houses within 908 ft (a site at most 148 ft from its house's center), found from a site index of 760 ft cells, each scanned site's distance tested; since corrected by ask:444-T09-rescore-batch-2: no site index is built, the first well searched like the later ones
- verdict-3, finding 2: fixed - the heap's seed, each household's distance to open water, and the wells drawn are rows of their own; the heap's push and pop is stated as 2 x log2 of the pool
- verdict-3, finding 3: disputed - memoizing each site's households within 760 ft breaks even at 20 and 40 by the verdict's own figures, and the ten's nearest has no distance limit, so a site's memo would miss a dry household beyond it; the 9-cell scan stays
- FR-014 re-score: each factor at the typical case (rubric S8): a well's sites are asked nearest the worst-served household first and the nearest is admitted within a few pops, so no site index is built and no pool scanned; each popped site at the mean densities of `items.md`; slack 2 (ask:444-budget-standard; the accept was ask:444-T03-appurtenances-round-4); since corrected by ask:444-T09-rescore-batch-2: slack 1, the first well searched like the later ones

## Cheaper algorithms considered

- sweep: not used - the wells are seated one at a time, each for the worst-served household as it stands
- grid or spatial index: used - the parts index for a site's clearance and the house index for its neighborhood
- priority queue: used - the worst-served household is a max-heap's top; a household's sites are walked nearest first
- incremental update: used - each well re-keys only the households in its cells
- memoizing what a scan does not change: not used - the sites are popped nearest first and only the few the search reaches are tested, so nothing is memoized over the run
