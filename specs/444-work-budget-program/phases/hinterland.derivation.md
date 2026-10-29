# Derivation - hinterland (feature 444)

## Contract

- Reads: everything placed before it - the fields and their crops, the cluster and its homesteads, the ways, the waters, the pond and the dry plots; the wind and the fall; the plan's canvas; the registry; the knobs (`bamboo`, `woodland`, the belt's form).
- Writes: the planted trees thinned out of the sun ground (`thin_planted_trees`); the shelter belt's polygon and its planted clumps (`belt_polygon`, `plant_the_belt`); the scatter's frame; the reed marsh at the toe and the scrub's pines (`hinterland`); the coppice parcels scanned (`open_ground_patches`); the late farmstead fixtures (the night-soil pits, `farmstead_fixtures`); the farms' bamboo strips and the thicket's seat (`seat_strips`, `bamboo_seats`); the decided view (`frame_for`, `plan.view`); the rough grazing over the bare ground (`fill_the_holes`, `commons` role grazing).
- Keeps: ground cover fills what is left and reserves nothing (0078); the marsh on the downhill toe band (0057); scrub past the fields, brush and pine stopping at every wood's line and at the marsh (0077, 0078); one pine throw a 6,000 sq ft, at least two a block (0078); no scrub on the ponds' open water (0073); the coppice on the nearest open high ground, clear of the crops by 80 ft and 180 ft on their sunny side (0038), apart from each other, none in a row, its square shrunk down a ladder before it is dropped (GUESS), none on marsh (0077); the belt along the cluster's windward fringe, 36 ft behind it and 100 ft deep (0072), its crowns filtered off every structure; the thicket within 220 ft of its target behind the back row (0075); the bare share of the view at most 0.35 (`BARE_SHARE_CAP`, feature 287 W11); the view decided once, after the belt (feature 287 M6); every seat asked before it is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the crowns 389 and 717 (x1.84: 717 at 20, 1,320 at 40, 2,428 at 80); the hard features about 902 and 1,632 (x1.81: 1,632 at 20, 2,954 at 40, 5,347 at 80); the view 1,521 by 1,726 ft and 2,274 by 2,486 ft (x1.47 a side: 2,274 by 2,486 ft at 20, 3,343 by 3,655 ft at 40, 4,914 by 5,372 ft at 80); the cluster's length 721 and 1,085 ft (x1.5); the marsh's rings, the longest 414 and 485 points (x1.1: 485 at 20, 534 at 40, 587 at 80), their edge 9,935 and 13,382 ft (x1.35: 13,382 at 20, 18,066 at 40, 24,389 at 80), at most 13 and 10 segments in a 64 ft cell (13 taken), all the rings' points 496 and 567 (x1.1); the covering things a sample-painting reads - the crowns, the scrub, the built parts and the way and water segments - 1,046 and 1,990 (x1.9), painting 5,224 and 9,718 cells of 25 ft edge cells included, at most 5 a thing on average (4.99 and 4.88); the field's box 857 by 1,103 ft and 1,448 by 1,668 ft (x1.6 a side: 1,448 by 1,668 ft at 20, 2,317 by 2,669 ft at 40, 3,707 by 4,271 ft at 80); the ways' length 4,703 and 8,917 ft (x1.9) and their legs at most 8 a household; the waters' segments 428 and 574 (x1.34) and their length 12,344 and 19,311 ft (x1.56); the belt's clumps 81 and 76; at most 7 homestead parts in a 64 ft cell (the homesteads' parts index, measured 6 and 7, held by the houses' density); at most 21 and 29 things of every kind in a 64 ft cell (x1.38: 29 at 20, 40 at 40, 55 at 80); at most 26 water segments a 64 ft cell; the houses' density at most 2.9e-5 a sq ft (3 houses in 3 by 3 cells of 90 ft); a homestead at most 184 ft; 1 ft a pixel at the hamlet scale.

## The algorithm

    thin the planted strings: each tree against the sun keep-outs in its cells
    the belt's near face: the fringe sampled across the wind every 30 ft, each sample's nearest fringe house; the band 36 ft behind
        it and 100 ft deep
    the scatter's frame from the hard features' boxes
    the marsh: the toe band's ring laid; the scrub: one pine throw a 6,000 sq ft of the view and its pad, each against the keep-outs
        in its cells and the water
    the coppice: the scan's keep-outs rasterized once on its 90 ft lattice over the view; each open seat asked low by the water;
        the open seats ranked by nearness; at most 4 parcels taken, each its square down the shrink ladder, its 5 by 5 wet samples
        in the marsh's ring, apart from the placed and out of their row
    the late fixtures: each household's night-soil pit at its field or its road, against its cells
    the bamboo: each farm's strip against its homestead's sides; the thicket's reach rasterized once at its 14 ft sample pitch, and
        its 16 ft lattice's seats each read from the raster
    plant the belt: each clump's crowns filtered against the structures in its cells
    decide the view from the hard features' boxes
    fill the holes: the bare samples every 25 ft over the view, grouped into blocks by one breadth-first pass, the largest clothed
        first until the bare share is at most 0.35

## Indexes

- registry: cells of 64 ft; densest 29 things a cell at 20, at its measured rate (29 at 20, 40 at 40, 55 at 80), from a smallest side of 64 ft against a probe under 64 ft, in at most 2 by 2 cells
- parts index: cells of 64 ft (the homesteads'); densest 7 homestead parts a cell (measured at 10 and 20, 6 and 7, the ceiling taken, held by the houses' density), from a smallest side of 64 ft against a probe under 64 ft, in at most 2 by 2 cells
- water index: cells of 64 ft; densest 26 water segments a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft
- house index: cells of 90 ft (the windbreak's), so a sample's fringe houses lie in its 3 by 3 cells; densest 3 houses, from a smallest side of 90 ft
- open region: cells of 90 ft, the coppice scan's own lattice; densest 1 a cell (a cell holds open or taken), from a smallest side of 90 ft
- thicket raster: cells of 14 ft, the thicket's sample pitch, with a summed-area table; densest 1 a cell (blocked or free), from a smallest side of 14 ft
- bare samples: cells of 25 ft (`BARE_STEP`, the gate's own grid), each holding its covered state (the things painted onto it once) and its marsh state; densest 1 a cell, from a smallest side of 25 ft
- marsh index: cells of 64 ft, each inside, outside or crossed; densest 13 segments a crossed cell (the marsh's own, measured at 10 and 20, 13 and 10, the ceiling taken), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the hinterland, once | always 1 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the planted trees (parts index cells examined) | over the run | 22,944 at 20, 42,240 at 40, 77,696 at 80 | each planted tree, at most the crowns, tested against the sun keep-outs - the yards' and beds' sun ground, parts of the homesteads - in its 2 by 2 cells of the homesteads' 64 ft parts index with their at most 7 parts and the cell (32) | 80 households |
| the belt's near face (house index cells examined) | over the run | 796 at 20, 1,228 at 40, 1,980 at 80 | the fringe sampled across the wind every 30 ft (`BELT_PROFILE_STEP_FT`) over the cluster's length and its 100 ft frame each side (44 at 20, 62 at 40, 90 at 80 samples), each its nearest fringe house from its 3 by 3 cells of the 90 ft house index and their 3 houses (12) and its near and far points written (2); the at most 9 samples in the frame past the cluster's ends, which may find no house in their cells, each scanning every house (9 x the households) | 80 households |
| the scatter's frame | over the run | 1,636 at 20, 2,958 at 40, 5,351 at 80 | each hard feature's box read once (1), and the frame's 4 sides | 80 households |
| the marsh | over the run | 970 at 20, 1,068 at 40, 1,174 at 80 | the toe band's ring, at most 485 points at 20 (x1.1), each laid and written (2) | 80 households |
| the scrub (registry and water index cells examined) | over the run | 307,572 at 20, 735,048 at 40, 1,823,212 at 80 | one pine throw a 6,000 sq ft of the scatter's frame - the view, `SCATTER_PAD` (40 ft) past each side and the title band's 193 ft on one - (1,083 at 20, 2,241 at 40, 4,699 at 80 throws), each against the keep-outs in its 2 by 2 cells of 64 ft with their things and the cell (120 at 20, 164 at 40, 224 at 80), the water in its 2 by 2 cells with their 26 segments and the cell (108), and the marsh - a pine stops at it - in its 2 by 2 cells of the marsh index, each its state and a crossed cell's 13 segments (56) | 80 households |
| the open region (open region cells written) | over the run | 7,821 at 20, 13,035 at 40, 22,854 at 80 | the coppice scan's keep-outs rasterized once on its 90 ft lattice: the field's box grown by its 180 ft set-back each side, (its side + 360) / 90 + 1 cells each way (528 at 20, 1,085 at 40, 2,491 at 80); each lane leg its length over 90 ft by 3 cells and 6 cells of ends, from the ways' length and legs (1,260 at 20, 2,487 at 40, 4,914 at 80); each water segment the same, from the waters' length and segments (4,089 at 20, 5,625 at 40, 7,755 at 80); the marsh by one scanline pass over the lattice and its edge's crossings, its edge over 90 ft, 2 a crossing (1,081 at 20, 2,040 at 40, 3,958 at 80); the keep rects 4 a house; and each lattice seat's state written once (783 at 20, 1,638 at 40, 3,416 at 80 seats) | 80 households |
| the open seats (water index cells examined) | over the run | 85,347 at 20, 178,542 at 40, 372,344 at 80 | each lattice seat the region leaves open, at most every seat, asked low by the water: its 2 by 2 cells of 64 ft with their 26 water segments and the cell (108), and the marsh read from the region's own raster (1) | 80 households |
| the ranking | over the run | 7,830 at 20, 18,018 at 40, 40,992 at 80 | the open seats sorted by nearness, log2 of the seats rounded up each | 80 households |
| the marsh index (marsh index cells written) | over the run | 1,751 at 20, 2,002 at 40, 2,300 at 80 | the marsh's rings walked through the 64 ft cells once: their edge (13,382 at 20, 18,066 at 40, 24,389 at 80 ft) at root 2 over 64 ft, plus 3 a segment (485 at 20, 534 at 40, 587 at 80 segments) | 80 households |
| the marsh raster (bare samples cells written) | over the run | 10,364 at 20, 21,426 at 40, 44,720 at 80 | the marsh's state at each bare sample, 25 ft over the view (9,292 at 20, 19,980 at 40, 42,768 at 80), by one scanline pass, each sample once, and the edge's crossings, its edge over 25 ft, 2 a crossing | 80 households |
| the parcels (open region and bare samples cells read) | over the run | 86,913 at 20, 181,818 at 40, 379,176 at 80 | the ranked seats tried until 4 are taken, at most every seat; each its square down the shrink ladder's 4 rungs, each rung one region read and its 5 by 5 wet samples each one marsh raster read (26), its exclusion against the at most 4 placed (4) and its row test (3) | 80 households |
| the late fixtures (registry cells examined) | over the run | 4,800 at 20, 13,120 at 40, 35,840 at 80 | each household's night-soil pit, its field seat and its road seat, each against its 2 by 2 cells of 64 ft with their things and the cell | 80 households |
| the bamboo strips (parts index cells examined) | over the run | 16,896 at 20, 33,792 at 40, 67,584 at 80 | the farms that roll a strip, 6 of 10 and 11 of 20 households (`meta.household_bamboo_wanted`), at most 0.55 a household, each at most 48 seats - 4 sides of its homestead, 184 ft over the 16 ft step - each against its homestead's parts and the belt in its 2 by 2 cells of the homesteads' 64 ft parts index with their at most 7 parts and the cell (32) | 80 households |
| the thicket (thicket raster cells written and read) | over the run | 26,432 at 20, 34,968 at 40, 46,608 at 80 | the thicket's reach, 220 ft (`THICKET_REACH_FT`), rasterized once at the 14 ft sample pitch, pi x 220 squared over 196, 776 cells, each decided against its 64 ft cell's things and the cell, and summed (a summed-area table, 1 a cell); then the 16 ft lattice's 594 seats in the reach, each its 84 by 58 ft stand's box read from the table (4) | 80 households |
| the belt (parts index cells examined) | over the run | 2,640 at 20, 3,696 at 40, 5,346 at 80 | the belt's crowns, 84 on 81 clumps and 76 on 76, 1.04 a clump, the clumps carried at the near face's rate (x1.41: 76, 107, 155, so 80 at 20, 112 at 40, 162 at 80 crowns), each filtered against the structures - the houses, yards, gardens, byres, sheds, wells, all homestead parts - in its 2 by 2 cells of the homesteads' 64 ft parts index with their at most 7 parts and the cell, and written (33) | 80 households |
| the view | over the run | 1,636 at 20, 2,958 at 40, 5,351 at 80 | each hard feature's box read once for the content's frame (1), and its 4 sides | 80 households |
| the holes (bare samples cells written and read) | over the run | 112,162 at 20, 238,685 at 40, 506,368 at 80 | the covering things painted once onto the 25 ft samples - the crowns, the scrub, the built parts and the way and water segments, 1,046 and 1,990 at 10 and 20 (x1.9: 1,990 at 20, 3,781 at 40, 7,184 at 80), each at most 5 cells of 25 ft, edge cells included (4.99 and 4.88 measured, the ceiling taken) (9,950 at 20, 18,905 at 40, 35,920 at 80), and the large polygons by one scanline pass, 2 a sample - then each sample one read (1); grouped into connected blocks by one breadth-first pass (5 a sample); the blocks counting-sorted by size (2 a sample: a size is a whole number at most the samples); each sample clothed once (1) | 80 households |

So: 1 x 1, plus each step's row.

## Totals

- at 20: 1 x 1 + 22944 + 796 + 1636 + 970 + 307572 + 7821 + 85347 + 7830 + 1751 + 10364 + 86913 + 4800 + 16896 + 26432 + 2640 + 1636 + 112162 = 698511
- at 40: 1 x 1 + 42240 + 1228 + 2958 + 1068 + 735048 + 13035 + 178542 + 18018 + 2002 + 21426 + 181818 + 13120 + 33792 + 34968 + 3696 + 2958 + 238685 = 1524603
- at 80: 1 x 1 + 77696 + 1980 + 5351 + 1174 + 1823212 + 22854 + 372344 + 40992 + 2300 + 44720 + 379176 + 35840 + 67584 + 46608 + 5346 + 5351 + 506368 = 3438897

## Growth

From 20 to 80 households the stage grows at an exponent of about 1.15, past 1.15, for a stated reason: ground cover fills the view, and the view's area grows x2.16 a doubling (the hamlet spreads as it grows, measured 2,625,246 and 5,653,164 sq ft at 10 and 20), so the scrub's throws, the bare samples and the coppice's lattice grow with the view, not the households; and the rows that test a probe against the registry carry its things a cell at their measured rate (21 and 29 at 10 and 20), with no geometric ceiling - crowns, parts and way segments differ in size - and no finer index lowering the densest cell's count below what a probe of its size meets. The holes, the largest row by the view, read a painted raster instead, so the density no longer reaches them. The audit at 40 and 80 measures both.


## Earlier findings

- verdict-1, finding 1: fixed - the parcels' trials are bounded by the ranked seats, at most every lattice seat, each its 4 rungs, the row its own
- verdict-1, finding 2: fixed - the open region's cells are derived from each keep-out: the field's grown box, the lanes' and the waters' segments, the marsh's scanline pass and the keep rects
- verdict-1, finding 3: fixed - the planted trees read the registry's things at their measured rate, 29, 40 and 55
- verdict-1, finding 4: fixed - the scrub's pad is `SCATTER_PAD`, 40 ft, and the title band's 193 ft on one side, the frame `scatter_frame` names
- verdict-1, finding 5: fixed - the growth past 1.15 is stated: the view's area and the registry's density, both measured
- verdict-1, finding 6: fixed - the open seats read the marsh from the region's own raster, 1 a seat
- verdict-1, finding 7: fixed - the parcels' wet samples read a marsh raster built once at the bare samples' 25 ft
- verdict-1, finding 8: fixed - the thicket's seats read a summed-area table, 4 a seat
- verdict-1, finding 9: fixed - the belt's clumps carried at the near face's own rate, x1.41: 76, 107, 155
- verdict-1, finding 10: fixed - the strips' 0.55 a household is `meta.household_bamboo_wanted`, 6 of 10 and 11 of 20 households
- verdict-1, finding 11: fixed - the belt's crowns are at most 2 a clump (84 and 76 crowns on 81 and 76 clumps), each filtered
- verdict-2, finding 1: fixed - the open region's inputs are in the Bounds - the field's box, the ways' length and legs, the waters' length and segments, the marsh's edge - each at its measured rate; the field's box counted by its cells each way
- verdict-2, finding 2: fixed - the marsh's edge and its 13 segments a cell are its own, measured
- verdict-2, finding 3: fixed - the holes paint the covering things onto the 25 ft samples once and read each sample once; the density no longer reaches them
- verdict-2, finding 4: fixed - the holes' blocks are counting-sorted, 2 a sample
- verdict-2, finding 5: fixed - the marsh raster is one scanline pass with its edge's crossings, not 13 a sample
- verdict-2, finding 6: fixed - the belt's crowns are 1.04 a clump, the measured
- verdict-2, finding 7: fixed - the near face's samples past the cluster's ends scan every house, their own term
- verdict-2, finding 8: fixed - the marsh index's figure recomputed from the measured edge
- the arbiter's continue (ask:444-T05-hinterland-round-3): fixed - the holes' painted cells derived: the covering things, measured 1,046 and 1,990 (x1.9), at most 5 cells of 25 ft each (4.99 and 4.88 measured)
- verdict-3, finding 1: fixed - the scrub's pine stops at the marsh through the marsh index, 4 cells each its state and a crossed cell's 13 segments (56 a throw), so the index is read
- verdict-3, finding 2: fixed - the rows that ask of one kind - the sun keep-outs, a homestead's sides, the structures - read the homesteads' parts index, 7 parts a cell, flat with the houses' density; only the rows that ask of every kind read the registry's growing count
- verdict-3, finding 3: fixed - the painted things' counts and cells are in the Bounds, the 5 an average a thing, the total count x mean
- verdict-3, finding 4: fixed - the marsh's rings' points in all, 496 and 567, are in the Bounds

## Cheaper algorithms considered

- sweep: used - the bare samples are grouped by one breadth-first pass; the belt's near face is a sweep across the wind
- grid or spatial index: used - the registry, the homesteads' parts index for the rows that ask of homestead parts alone, the water index and the house index; the coppice's open region, the thicket's raster and the bare samples each a grid built once
- priority queue: not used - the coppice's open seats are sorted once by nearness; the blocks once by size
- incremental update: used - each placed thing is filed as it is drawn, for the steps after
- memoizing what a scan does not change: used - the coppice scan's keep-outs, the thicket's reach, the marsh and the holes' covering things are each rasterized once and read per seat and per sample
