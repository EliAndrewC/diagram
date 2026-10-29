# Derivation - woodland (feature 444)

## Contract

- Reads: the coppice parcels the hinterland scanned (`open_ground_patches`: each a seat on ground nothing else wanted, its keep-outs tested at its reach, clear of every clump of the grove, `woodland_clear_of_grove`); the registry, into which each wood is filed; the `woodland` knob (on the sheet, or off it with its bearing, `meta.woodland_offsheet`).
- Writes: each worked wood (`commons`, role `woodland`): an irregular ring inside its parcel's reach, never a rectangle (T36), its line bent to the ground (a GUESS), stocked with coppice crowns; or, where the woods lie off the sheet, only their bearing and count in `meta.woodland_offsheet`, once.
- Keeps: coppice on the scanned parcels, each stocked as a worked wood (0077); the worked coppice only, never the strip woods or coppice gone to brush (0077); drawn on parcels the scrub already kept out of, so no crown is tested against the scrub; every rule asked of the parcel at the scan, before this stage draws it (S4); no crown outside its ring.
- Bounds (measured 2026-10-28 on the pool's scripted hamlets that draw a wood on the sheet - Inashiro at 15 households, one parcel; Kashikawa at 20, three - the reference roll draws its 4 parcels off the sheet): at most 4 parcels (the knob's count, the same at 10 and 20); each a ring of 12 points, at most 49,338 sq ft, its bounding box at most 247.2 by 258.8 ft (measured), so in at most 5 by 6 cells of 64 ft; its crowns at one a 64 sq ft (545 in 34,941 and 771 in 49,338 sq ft, an 8 ft grid), at most 771 a parcel; the parcels' size set by the ground the scan finds, not by the households, so the stage is flat in the households.

## The algorithm

    for each scanned parcel on the sheet: its ring's 12 points bent to the ground and written (2 a point)
        its crowns by a scanline sweep of the 8 ft grid: each grid row crossed with the ring's 12 edges once, so the sites inside
            a row's span are made and no site outside it is; each site kept (1), its jitter drawn (1), written (1); a site within
            a jitter of the ring's edge retested against the 12 edges so its crown stays inside
        the wood recorded and filed in the registry's cells its ring covers
    woods off the sheet: their bearing and count recorded once (the reference's case), nothing drawn

## Indexes

- registry: cells of 64 ft (the hinterland's), each wood filed in the at most 5 by 6 cells its ring covers; densest one wood a cell, from a smallest side of 64 ft (the parcels were scanned apart, clear of each other)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 4 | the parcels, at most 4 on the sheet | every parcel on the sheet |
| the ring | per item | 24 | its 12 points, each bent to the ground (1) and written (1) | always 24 |
| the crowns | per item | 4245 | the sweep: 34 grid rows (258.8 / 8 + 1), each crossed with the 12 edges (408); at most 771 sites inside, each kept, jittered and written (2313); the sites within a jitter of the edge, at most the ring's bounding perimeter over 8 ft, 127, each retested against the 12 edges (1524) | the largest parcel |
| the filing (registry cells written) | per item | 31 | recorded (1), its at most 5 by 6 cells (30) | the largest parcel |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the bearing | once | 4 | the woods off the sheet: their bearing, its degrees, their count and the record, once | the woods off the sheet |

So: 4 x (24 + 4245 + 31) x 1, plus the bearing, the same at every size.

## Totals

- at 20: 4 x (24 + 4245 + 31) x 1 + 4 = 17204
- at 40: 4 x (24 + 4245 + 31) x 1 + 4 = 17204
- at 80: 4 x (24 + 4245 + 31) x 1 + 4 = 17204

## Earlier findings

- verdict-1, finding 1: fixed - the bearing is recorded once, for the woods off the sheet, a once row of 4; a wood on the sheet writes none
- verdict-1, finding 2: fixed - the crowns by a scanline sweep of the grid rows against the ring's 12 edges; only the sites inside are made, and the edge sites retested
- verdict-1, finding 3: fixed - the ring's bend to the ground is counted, 1 a point
- verdict-1, finding 4: fixed - the ring's bounding box measured, at most 247.2 by 258.8 ft, so 5 by 6 cells and 34 grid rows

## Cheaper algorithms considered

- sweep: used - the crowns' grid is swept row by row against the ring's edges
- grid or spatial index: used - the crowns on a grid; each wood filed in the registry's cells
- priority queue: not used - nothing is ranked
- incremental update: used - each wood is filed as it is drawn
- memoizing what a scan does not change: used - the parcels' keep-outs were tested at the hinterland's scan and are not tested again
