# Derivation - hinterland, greenfield (feature 444 FR-015)

## Contract

- Reads: the seated lots' lattice (each household's 104 ft square inside its 162 ft lot, its house at the square's north side, its yard below it) and the households' layouts; the field's outline and the pond; the water and the ways in their indexes; the seat's belt band and the plan's wind; the plan's grass-ground form; the view.
- Writes: the ground past the houses and fields - the rough grazing over the dry margins, drawn as one repeated block with no outline; the scrub's scattered pines over that band; the reed marshes at the pond's fringe and the field's toe; each homestead's stand of wood, crown by crown; the village shelter belt on the windward side, its polygon and its crowns; the late farmstead fixtures - each household's night-soil pit - and the fixtures' and persimmons' own records; every crown and pine filed in the registry.
- Keeps: the commons a repeated block of grass and brush, no solid fill and no outline, stopping where its ground ends and leaving bare the lanes and their verges, the fields' margins and the houses' swept ground; the pines drawn one by one, a few scraggly ones; the scrub one continuous band round the settlement; nothing on the flooded rice fields (0078); every yard and kitchen bed keeps 50 ft east, west and south clear of any crown or bamboo, from its north edge down (0038); a household's wood at least 6,000 sq ft on its seated ground (0285); the shelter belt on the village's windward side, its depth running off the sheet (0072, 0241); a pond's reeds on wet ground at its shore, off its embankment (0061); a household's night-soil pit by its field or its way (0047).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the scrub's frame 1,601 by 2,192 and 2,354 by 2,952 ft (3.51M and 6.95M sq ft), its pines 252 and 591, one try a 77 ft cell (5,929 sq ft, the pines' spacing a GUESS knob) over it - 592 and 1,172 cells, kept at 0.43 and 0.50 - and past 20 with the view's area (x2.16 a doubling: 2,532 and 5,469 cells); the marshes 2, a pond fringe and a toe, 82 and 414 and 82 and 485 ring points (567 at 20, x1.1 a doubling: 624 and 687), their edge about 13,400 ft at 20; the homestead wood 9,931 and 8,137 sq ft a household drawn, its crowns about 8 a household (the 717 crowns at 20 less the copse's 462 and the belt's 93 near-face vertices and its crowns, about 160); the belt's near face 44 and 93 vertices, 1.04 crowns a vertex, past 20 with the cluster's side (x1.41: 131 and 185); the fixtures' records 38 and 78 (3.9 a household), the persimmons 9 and 17 (0.85 a household); the night-soil pit by the field at 0.746 of households, by the way at the rest; the lots' squares 29 ft inside their lots, each house at its square's north side, 28 ft deep, its yard 26 ft below it, so the yard ends 83 ft below the lot's north edge (29 + 28 + 26), its beds on the house's flanks beside it, ending above that; the lattice's span 9 by 6, 12 by 9 and 16 by 12 lots; the water's segments 574 at 20 (`items.md`), the brook's 236 growing x1.12 a doubling and the ditches' and channels' 338 x1.54, the track 3,333 ft long, the field's side x1.41 and the marshes x1.1; the typical densities (`items.md`, rubric S8): things of every kind 5.5 a 64 ft cell within 3 cells of a house.

## The algorithm

    the grazing: one record over the view, the repeated block clipped by nothing - every feature drawn above it covers it, and
        each feature that leaves bare ground (a lane and its verge, a field's margin, a house's swept ground) draws its own bare
        halo with it, so no sample of the ground is painted or tested (2)
    the blocked mask, once, on the 77 ft try lattice over the scrub's frame - the field's outline by one scanline pass (each row's
        crossings, kept for the pits, each inside cell marked), the marshes' rings the same, each water segment and the track's leg
        marking the cells it crosses, the belt's polygon by scanline, all marked into the one mask as they are drawn; a lot read
        straight from the lots' lattice, never rastered
    the scrub: each try cell taken once (1), its mask read (1) and its lots' lattice cell (1), its jittered point rolled (1); kept
        at the band's density, its slot (1), written (1) and filed in the registry (1.4)
    the marshes: each ring's points laid along the pond's shore and the field's toe and written (2 a point); their edge filed in
        the water index (each segment its cells)
    each homestead's wood: its crowns on a jittered grid in its lot's north strip, between the lot's north edge and its square
        (162 by 29 ft, north of its own house and so of its own yard and beds), and in its south strip (162 by 29 ft, which lies
        50 ft and more south of its own yard - the yard ends 83 ft below the lot's north edge, the strip starts at 133 - and north
        of the next lot's yard): every crown keeps the sun by the lattice's geometry, so none is tested; each written (1) and filed
        (1.4), its slot taken (1); the north strip's west 22 ft left free for the household's bamboo stand, laid by `bamboo`
    the belt: its near face along the windward lots' outer edges, found by walking the lattice's line facing the wind (as the
        track's start, about 2 lines of R + 1 cells), set 21 ft past the lots' edges so 50 ft past every square and its yard and
        beds; its polygon's vertices written (1 each); its crowns on a jittered grid inside it, each its slot, written and filed
        (3.4)
    the fixtures' and persimmons' records copied from each layout, each its record and its box written (2)
    each household's night-soil pit: by the field (0.746) at its lattice column's margin point, read from the field's kept
        scanline crossing for that column (2), a column's second household's pit one pit-width along the margin from its first;
        its box asked of the registry's cells it overlaps (each cell 1, each thing 1); taken, stepped one pit-width along the margin
        and asked again, at most twice; written and filed (2.2); by the way (the rest) at its lot's lane corner, clear by the lot's
        margin (3.4)

## Indexes

- the try lattice: cells of 77 ft over the scrub's frame, one blocked mask, read one a try, from a smallest side of 77 ft
- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a pine's or a crown's box overlapping about 1.4 cells, a pit's 1.2 at the field's margin at the mean 3.3 things an occupied cell (`items.md`, rubric S8), from a smallest side of 64 ft
- water index: cells of 64 ft, each segment filed in every cell it crosses; the marshes' edge, about 13,400 ft at 20, crossing about (13,400 / 64) x 1.27 = 266 cells, from a smallest side of 64 ft
- the lots' lattice: cells of 162 ft, the seated lots by their lattice index, looked up directly, from a smallest side of 162 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the households, their woods, records and pits | the households |
| the wood (registry cells written) | per item | 27 | about 8 crowns a household, each its slot (1), written (1) and filed in 1.4 cells (1.4): 3.4 x 8 | a household with more wood |
| the records | per item | 9.5 | 3.9 fixtures and 0.85 persimmons a household, each its record and its box written (2) | always |
| the pit (registry cells examined) | per item | 11.8 | by the field at 0.746: its column's margin point (2), its box in 1.2 cells at the margin's mean 3.3 things and the cell (5.2), asked at most twice more where taken, at slack 2 on the ask (10.4), written and filed (2.2): 14.6 x 0.746 = 10.9; by the way at 0.254: 3.4 x 0.254 = 0.9 | a column of many households on a crowded margin |
| slack | per item | 1 | the households' factors are counts of their layouts and lots | not applicable |
| the grazing | once | 2 | one record over the view, its kind from the plan's grass-ground form | always 2 |
| the rasters (the try lattice cells written) | once | 2105 at 20, 2656 at 40, 3432 at 80 | the field's outline (22 rows' crossings and its 204 inside cells, about 300, x1.41 a doubling), the marshes' rings (567 segments marking about 1.2 cells each and their inside, about 900, x1.1), the water's segments (the brook's 236 and the rest's 338 at about 1.3 cells each, about 750, x1.12 and x1.54), the track (55 cells, x1.47) and the belt (about 100, x1.41), each into the one mask | the typical valley |
| the scrub (the try lattice cells examined) | over the run | 6680 at 20, 14432 at 40, 31173 at 80 | each try cell, 1,172, 2,532 and 5,469 (the view's area x2.16 a doubling): taken (1), its mask (1), its lots' cell (1), rolled (1), and at the 0.5 kept its slot, written and filed (3.4 x 0.5 = 1.7): 5.7 a try | the typical valley |
| the marshes (water index cells written) | over the run | 1400 at 20, 1530 at 40, 1700 at 80 | each ring point laid and written (2), 567, 624 and 687 points, and the edge's 266, 293 and 322 cells filed | the typical valley |
| the belt (the lots' lattice cells examined) | over the run | 434 at 20, 611 at 40, 862 at 80 | its near face's line walk (about 2 lines of R + 1, 12, 16 and 22), its 93, 131 and 185 vertices written (1), and its crowns at 1.04 a vertex, each its slot, written and filed (3.4 x 1.04 = 3.54): 4.54 a vertex | the typical valley |

So: households x (27 + 9.5 + 11.8) x 1, plus the grazing, the rasters, the scrub, the marshes and the belt.

- pruning: the scrub visits each try cell once and reads one mask cell for it - the band is the output, one try a 77 ft cell - never the features themselves; the grazing paints and tests nothing, each feature's bare halo a style it is drawn with, no operation of any stage

## Totals

- at 20: 20 x (27 + 9.5 + 11.8) x 1 + 2 + 2105 + 6680 + 1400 + 434 = 11587
- at 40: 40 x (27 + 9.5 + 11.8) x 1 + 2 + 2656 + 14432 + 1530 + 611 = 21163
- at 80: 80 x (27 + 9.5 + 11.8) x 1 + 2 + 3432 + 31173 + 1700 + 862 = 41033

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.96: the scrub with the view's area, the rest with the households or the cluster's side.

## Earlier findings

- verdict-1, finding 1: fixed - the four rasters marked into one mask as they are drawn, a try reading one mask cell and one lattice cell: 5.7 a try with the kept pine's slot
- verdict-1, finding 2: fixed - a taken pit steps one pit-width along the margin and asks again, at most twice, at slack 2 on its ask; a column's second household one pit-width on
- verdict-1, finding 3: fixed - the yard's end at 83 ft and the beds beside the house are in the Bounds
- verdict-1, finding 4: fixed - the records written as their record and their box, 2 each
- verdict-1, finding 5: fixed - the belt's arithmetic one rate at every size, 4.54 a vertex: 434, 611 and 862
- verdict-1, finding 6: fixed - the belt's crowns and the kept pines charged a slot as the wood's are
- verdict-1, finding 7: fixed - the pit asks the margin's mean 3.3 things, not the houses' 5.5
- verdict-1, finding 8: fixed - the rasters' growth from each part's own measure
- verdict-1, finding 9: fixed - the bare halo a style each feature is drawn with, no operation of any stage

## Cheaper algorithms considered

- sweep: used - each raster drawn by one scanline pass
- grid or spatial index: used - the try lattice's rasters, the lots' lattice, the registry and the water index
- priority queue: not used - nothing is ranked
- incremental update: not used - each pine, crown and record is written once, nothing moved
- memoizing what a scan does not change: used - the field, the marshes, the water, the track and the belt marked once into one mask on the try lattice, each try reading one cell of it
