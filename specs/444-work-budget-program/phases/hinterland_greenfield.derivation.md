# Derivation - hinterland, greenfield (feature 444 FR-015)

## Contract

- Reads: the seated lots' lattice (each household's 104 ft square inside its 162 ft lot, its house at the square's north side, its yard below it) and the households' layouts; the field's outline and the pond; the water and the ways in their indexes; the seat's belt band and the plan's wind; the plan's grass-ground form; the view.
- Writes: the ground past the houses and fields - the rough grazing over the dry margins, drawn as one repeated block with no outline; the scrub's scattered pines over that band; the reed marshes at the pond's fringe and the field's toe; each homestead's stand of wood, crown by crown; the village shelter belt on the windward side, its polygon and its crowns; the late farmstead fixtures - each household's night-soil pit - and the fixtures' and persimmons' own records; every crown and pine filed in the registry.
- Keeps: the commons a repeated block of grass and brush, no solid fill and no outline, stopping where its ground ends and leaving bare the lanes and their verges, the fields' margins and the houses' swept ground; the pines drawn one by one, a few scraggly ones; the scrub one continuous band round the settlement; nothing on the flooded rice fields (0078); every yard and kitchen bed keeps 50 ft east, west and south clear of any crown or bamboo, from its north edge down (0038); a household's wood at least 6,000 sq ft on its seated ground (0285); the shelter belt on the village's windward side, its depth running off the sheet (0072, 0241); a pond's reeds on wet ground at its shore, off its embankment (0061); a household's night-soil pit by its field or its way (0047).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the scrub's frame 1,601 by 2,192 and 2,354 by 2,952 ft (3.51M and 6.95M sq ft), its pines 252 and 591, one try a 77 ft cell (5,929 sq ft, the pines' spacing a GUESS knob) over it - 592 and 1,172 cells, kept at 0.43 and 0.50 - and past 20 with the view's area (x2.16 a doubling: 2,532 and 5,469 cells); the marshes 2, a pond fringe and a toe, 82 and 414 and 82 and 485 ring points (567 at 20, x1.1 a doubling: 624 and 687), their edge about 13,400 ft at 20; the homestead wood 9,931 and 8,137 sq ft a household drawn, its crowns about 8 a household (the 717 crowns at 20 less the copse's 462 and the belt's 93 near-face vertices and its crowns, about 160); the belt's near face 44 and 93 vertices, 1.04 crowns a vertex, past 20 with the cluster's side (x1.41: 131 and 185); the fixtures' records 38 and 78 (3.9 a household), the persimmons 9 and 17 (0.85 a household); the night-soil pit by the field at 0.746 of households, by the way at the rest; the lots' squares 29 ft inside their lots, the lattice's span 9 by 6, 12 by 9 and 16 by 12 lots; the water's segments 574 at 20 (`items.md`), the track 3,333 ft long; the typical densities (`items.md`, rubric S8): things of every kind 5.5 a 64 ft cell within 3 cells of a house.

## The algorithm

    the grazing: one record over the view, the repeated block clipped by nothing - every feature drawn above it covers it, and
        each feature that leaves bare ground (a lane and its verge, a field's margin, a house's swept ground) draws its own bare
        halo with it, so no sample of the ground is painted or tested (2)
    the rasters, once, on the 77 ft try lattice over the scrub's frame: the field's outline by one scanline pass (each row's
        crossings, each inside cell marked); the marshes' rings the same; each water segment and the track's leg marking the cells
        it crosses; the belt's polygon by scanline; a lot read straight from the lots' lattice, never rastered
    the scrub: each try cell taken once (1), its jittered point rolled (1), asked of the rasters - field, marsh, water and ways,
        belt - (4) and of the lots' lattice (1); kept at the band's density, written (1) and filed in the registry (1.4)
    the marshes: each ring's points laid along the pond's shore and the field's toe and written (2 a point); their edge filed in
        the water index (each segment its cells)
    each homestead's wood: its crowns on a jittered grid in its lot's north strip, between the lot's north edge and its square
        (162 by 29 ft, north of its own house and so of its own yard and beds), and in its south strip (162 by 29 ft, which lies
        50 ft and more south of its own yard - the yard ends 83 ft below the lot's north edge, the strip starts at 133 - and north
        of the next lot's yard): every crown keeps the sun by the lattice's geometry, so none is tested; each written (1) and filed
        (1.4), its slot taken (1); the north strip's west 22 ft left free for the household's bamboo stand, laid by `bamboo`
    the belt: its near face along the windward lots' outer edges, found by walking the lattice's line facing the wind (as the
        track's start, about 2 lines of R + 1 cells), set 21 ft past the lots' edges so 50 ft past every square and its yard and
        beds; its polygon's vertices written (1 each); its crowns on a jittered grid inside it, each written and filed (2.4)
    the fixtures' and persimmons' records copied from each layout, each its record and its box written (5)
    each household's night-soil pit: by the field (0.746) at its lattice column's margin point, read from the field raster's
        crossing for that column (2), its box asked of the registry's cells it overlaps (each cell 1, each thing 1), written and
        filed (2.2); by the way (the rest) at its lot's lane corner, clear by the lot's margin (3.4)

## Indexes

- the try lattice: cells of 77 ft over the scrub's frame, the rasters' marks, read one a try, from a smallest side of 77 ft
- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a pine's or a crown's box overlapping about 1.4 cells, a pit's 1.2 at the mean 5.5 things a cell near the houses (`items.md`, rubric S8), from a smallest side of 64 ft
- water index: cells of 64 ft, each segment filed in every cell it crosses; the marshes' edge, about 13,400 ft at 20, crossing about (13,400 / 64) x 1.27 = 266 cells, from a smallest side of 64 ft
- the lots' lattice: cells of 162 ft, the seated lots by their lattice index, looked up directly, from a smallest side of 162 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the households, their woods, records and pits | the households |
| the wood (registry cells written) | per item | 27 | about 8 crowns a household, each its slot (1), written (1) and filed in 1.4 cells (1.4): 3.4 x 8 | a household with more wood |
| the records | per item | 23.8 | 3.9 fixtures and 0.85 persimmons a household, each its record and box written (5) | always |
| the pit (registry cells examined) | per item | 9.8 | by the field at 0.746: its column's margin point (2), its box in 1.2 cells at the mean 5.5 things and the cell (7.8), written and filed (2.2): 12 x 0.746 = 9.0; by the way at 0.254: 3.4 x 0.254 = 0.9 | always |
| slack | per item | 1 | the households' factors are counts of their layouts and lots | not applicable |
| the grazing | once | 2 | one record over the view, its kind from the plan's grass-ground form | always 2 |
| the rasters (the try lattice cells written) | once | 2100 at 20, 2600 at 40, 3200 at 80 | the field's outline (22 rows' crossings and its 204 inside cells, about 300), the marshes' rings (567 segments marking about 1.2 cells each and their inside, about 900), the water's 574 segments (about 1.3 cells each, about 750), the track (55 cells), the belt (about 100); past 20 with the field's side and the water's length, about x1.25 a doubling | the typical valley |
| the scrub (the try lattice cells examined) | over the run | 9610 at 20, 20762 at 40, 44846 at 80 | each try cell, 1,172, 2,532 and 5,469 (the view's area x2.16 a doubling): taken (1), rolled (1), the four rasters and the lattice (5), and at the 0.5 kept written and filed (2.4 x 0.5 = 1.2): 8.2 a try | the typical valley |
| the marshes (water index cells written) | over the run | 1400 at 20, 1530 at 40, 1700 at 80 | each ring point laid and written (2), 567, 624 and 687 points, and the edge's 266, 293 and 322 cells filed | the typical valley |
| the belt (the lots' lattice cells examined) | over the run | 344 at 20, 487 at 40, 673 at 80 | its near face's line walk (about 2 lines of R + 1, 12, 16 and 22), its 93, 131 and 185 vertices written (1), and its crowns at 1.04 a vertex written and filed (2.4 x 1.04 = 2.5): 12 + 93 x 3.5, 16 + 131 x 3.6, 22 + 185 x 3.5 | the typical valley |

So: households x (27 + 23.8 + 9.8) x 1, plus the grazing, the rasters, the scrub, the marshes and the belt.

- pruning: the scrub visits each try cell once because each is a place a pine may stand - the band is the output, one try a 77 ft cell - and asks rasters drawn once, never the features themselves; the grazing paints and tests nothing

## Totals

- at 20: 20 x (27 + 23.8 + 9.8) x 1 + 2 + 2100 + 9610 + 1400 + 344 = 14668
- at 40: 40 x (27 + 23.8 + 9.8) x 1 + 2 + 2600 + 20762 + 1530 + 487 = 27805
- at 80: 80 x (27 + 23.8 + 9.8) x 1 + 2 + 3200 + 44846 + 1700 + 673 = 55269

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.96: the scrub with the view's area, the rest with the households or the cluster's side.

## Cheaper algorithms considered

- sweep: used - each raster drawn by one scanline pass
- grid or spatial index: used - the try lattice's rasters, the lots' lattice, the registry and the water index
- priority queue: not used - nothing is ranked
- incremental update: not used - each pine, crown and record is written once, nothing moved
- memoizing what a scan does not change: used - the field, the marshes, the water, the track and the belt rastered once onto the try lattice, each try reading them rather than the features
