# Derivation - woodland (feature 444)

## Contract

- Reads: the coppice parcels the hinterland scanned (`open_ground_patches`: each a seat on ground nothing else wanted, clear of every clump of the grove, `woodland_clear_of_grove`); the registry and its keep-outs, the standing crowns among them; the hinterland's marsh raster on its 25 ft bare samples and its 64 ft marsh index; the pond; the `woodland` knob (on the sheet, or off it with its bearing, `meta.woodland_offsheet`).
- Writes: each worked wood (`commons`, role `woodland`): an irregular ring inside its parcel's reach, never a rectangle (T36), its line bent to the ground (a GUESS), stocked with coppice crowns; or, where the woods lie off the sheet, only their bearing and count in `meta.woodland_offsheet`, once.
- Keeps: coppice on the scanned parcels, each stocked as a worked wood (0077); the worked coppice only (0077); its crowns on a regular square lattice at the stocking spacing, 8 ft (`COMMONS_SPACING_FT`, 0080: 1,700 stems a hectare), a crown 4 to 4.5 ft in radius (`COMMONS_CROWN_R_FT`, a GUESS), deterministic, no draw made (`woodland_room`): each lattice seat inside the ring, on dry ground (off every marsh), clear of every keep-out the commons' crowns are thrown against at the largest crown's radius, off the pond, and under no crown already standing; every rule asked of a seat before its crown is drawn (S4).
- Bounds (measured 2026-10-28 on the pool's scripted hamlets that draw a wood on the sheet - Inashiro at 15 households, one parcel; Kashikawa at 20, three - the reference roll draws its 4 parcels off the sheet): at most 4 parcels (the knob's count, the same at 10 and 20); each a ring of 12 points, at most 49,338 sq ft, its bounding box at most 247.2 by 258.8 ft and its perimeter at most 806.8 ft (measured), so in at most 5 by 6 cells of 64 ft; its lattice seats inside the ring at any alignment at most its area over 64 sq ft, plus its perimeter over 8 ft, plus 1: 873; a wood's own seats 8 ft apart, more than any crown's 4.5 ft radius, so none of its own crowns stands over another of its seats; at most 21 and 29 things in a 64 ft cell (x1.38: 29 at 20, 40 at 40, 55 at 80, the hinterland's rate); a thing at most 63 ft across, so it spans at most (63 + 9) / 8 + 1 = 10 lattice rows; at most 13 marsh segments in a 64 ft cell (the hinterland's measured); the parcels' size set by the ground the scan finds, not by the households.

## The algorithm

    for each scanned parcel on the sheet: its ring's 12 points bent to the ground and written (2 a point)
        the registry's things in the parcel's 5 by 6 cells gathered once (the registry does not change while a parcel is
            stocked: the wood is filed after its crowns): the keep-outs and the standing crowns; each reaching the ring dilated by
            the crown's 4.5 ft kept, and cut from the lattice rows it spans
        its lattice by an active-edge sweep: the 12 edges sorted by their start row, each crossed only with the rows it spans
        each seat inside a row's span, less its cuts: dry - its 25 ft marsh sample read from the hinterland's raster, and in a
            crossed cell its at most 13 marsh segments; off the pond (1); admitted: its crown written and filed (1)
        the wood recorded and filed in the registry's cells its ring covers
    woods off the sheet: their bearing and count recorded once, nothing drawn

## Indexes

- registry: cells of 64 ft; densest 29 things a cell at 20, at its measured rate (29 at 20, 40 at 40, 55 at 80), from a smallest side of 64 ft; a parcel's things gathered from its 5 by 6 cells once
- marsh raster and index: the hinterland's, cells of 25 ft and of 64 ft, read here; densest 13 segments a crossed 64 ft cell (the hinterland's measured), from a smallest side of 25 ft for the raster

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 4 | the parcels, at most 4 on the sheet | every parcel on the sheet |
| the ring | per item | 24 | its 12 points, each bent to the ground (1) and written (1) | always 24 |
| the sweep | per item | 161 | the 12 edges sorted (48, 12 x log2 of 12 rounded up), and each crossed with only the rows it spans, at most the perimeter over 8 ft plus one a edge (113) | the longest ring |
| the seats (marsh raster and index cells examined) | per item | 14841 | at most 873 seats, each inside its row's span (1), dry - its marsh sample and a crossed cell's 13 segments (14) - off the pond (1), and its crown written and filed (1) | the largest parcel, every seat admitted |
| the gather (registry cells examined) | per item | 900 at 20, 1,230 at 40, 1,680 at 80 | the parcel's 5 by 6 cells, each with its things and the cell | the densest cells |
| the cuts (lattice rows cut) | per item | 8,700 at 20, 12,000 at 40, 16,500 at 80 | each gathered thing kept and cut from the at most 10 rows it spans, at most every thing of the 30 cells | every thing reaching the ring |
| the filing (registry cells written) | per item | 31 | recorded (1), its at most 5 by 6 cells (30) | the largest parcel |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |

So: 4 x (24 + 161 + 14841 + the gather + the cuts + 31) x 1. The woods off the sheet record their bearing and count once and draw nothing, the cheaper of the two exclusive cases.

## Totals

- at 20: 4 x (24 + 161 + 14841 + 900 + 8700 + 31) x 1 = 98628
- at 40: 4 x (24 + 161 + 14841 + 1230 + 12000 + 31) x 1 = 113148
- at 80: 4 x (24 + 161 + 14841 + 1680 + 16500 + 31) x 1 = 132948

## Earlier findings

- verdict-1, finding 1: fixed - the bearing is recorded once, and only for the woods off the sheet, the exclusive case
- verdict-1, finding 2: fixed - the crowns by a scanline sweep of the lattice rows against the ring's edges
- verdict-1, finding 3: fixed - the ring's bend to the ground is counted, 1 a point
- verdict-1, finding 4: fixed - the ring's bounding box measured, 5 by 6 cells
- verdict-2, finding 1: fixed - no jitter: the crowns are a deterministic lattice (`woodland_room`)
- verdict-2, finding 2: fixed - the sweep's rows are floor(258.8 / 8) + 1 = 33, now crossed only where each edge spans
- verdict-2, finding 3: fixed - the on-sheet and off-sheet cases are exclusive; the total is the on-sheet one
- verdict-2, finding 4: fixed - the ring's perimeter measured, at most 806.8 ft; no figure rests on convexity
- verdict-3, finding 1: fixed - no crown index: a wood's own crowns, 8 ft apart, never stand over its seats, and the crowns standing before it are gathered once with the keep-outs
- verdict-3, finding 2: fixed - the marsh's 13 segments a cell are the marsh's own, measured in the hinterland
- verdict-3, finding 3: fixed - the marsh's inside and outside are the hinterland's raster's, read; no classification is built here
- verdict-3, finding 4: fixed - the keep-outs gathered once a parcel and cut from the rows they span, in place of 120 a seat
- verdict-3, finding 5: fixed - the active-edge sweep, each edge crossed only with its rows
- verdict-3, finding 6: fixed - the seats are a lattice-point ceiling, area over 64 plus perimeter over 8 plus 1, every seat tested counted
- verdict-3, finding 7: fixed - the registry's things grow at their measured rate; the marsh is the hinterland's, read

## Cheaper algorithms considered

- sweep: used - the crowns' lattice swept by an active-edge list against the ring's edges
- grid or spatial index: used - the registry's cells gathered once a parcel; the hinterland's marsh raster and index read
- priority queue: not used - nothing is ranked
- incremental update: not used - a wood's own crowns cannot block its seats, so nothing is filed for the next seat
- memoizing what a scan does not change: used - the parcel's keep-outs and standing crowns gathered once and cut from the rows; the marsh read from the hinterland's raster
