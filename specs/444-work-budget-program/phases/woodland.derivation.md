# Derivation - woodland (feature 444)

## Contract

- Reads: the coppice parcels the hinterland scanned (`open_ground_patches`: each a seat on ground nothing else wanted, clear of every clump of the grove, `woodland_clear_of_grove`); the registry and its keep-outs; the drawn marsh; the pond; the crowns already standing; the `woodland` knob (on the sheet, or off it with its bearing, `meta.woodland_offsheet`).
- Writes: each worked wood (`commons`, role `woodland`): an irregular ring inside its parcel's reach, never a rectangle (T36), its line bent to the ground (a GUESS), stocked with coppice crowns; or, where the woods lie off the sheet, only their bearing and count in `meta.woodland_offsheet`, once.
- Keeps: coppice on the scanned parcels, each stocked as a worked wood (0077); the worked coppice only (0077); its crowns on a regular square lattice at the stocking spacing, 8 ft (`COMMONS_SPACING_FT`, 0080: 1,700 stems a hectare), a crown 4 to 4.5 ft in radius (`COMMONS_CROWN_R_FT`, a GUESS), deterministic, no draw made (`woodland_room`): each lattice seat inside the ring, on dry ground (off every marsh), clear of every keep-out the commons' crowns are thrown against at the largest crown's radius, off the pond, and under no crown already standing; every rule asked of a seat before its crown is drawn (S4).
- Bounds (measured 2026-10-28 on the pool's scripted hamlets that draw a wood on the sheet - Inashiro at 15 households, one parcel; Kashikawa at 20, three - the reference roll draws its 4 parcels off the sheet): at most 4 parcels (the knob's count, the same at 10 and 20); each a ring of 12 points, at most 49,338 sq ft, its bounding box at most 247.2 by 258.8 ft and its perimeter at most 806.8 ft (measured), so in at most 5 by 6 cells of 64 ft and on at most floor(258.8 / 8) + 1 = 33 lattice rows; its crowns at most its area over 64 sq ft, 771 (545 in 34,941 and 771 in 49,338 sq ft); the marsh's rings at most 485 points, about 5,300 ft of edge, at 20 (the stage after the woods does not grow it); at most 29 things in a 64 ft cell; the parcels' size set by the ground the scan finds, not by the households, so the stage is flat in the households.

## The algorithm

    the marsh's rings indexed once in 64 ft cells, each cell inside, outside or crossed with its segments
    for each scanned parcel on the sheet: its ring's 12 points bent to the ground and written (2 a point)
        its lattice by a scanline sweep: each of its rows crossed with the ring's 12 edges once, so only the seats inside are made
        each seat: inside (1, the sweep's span); clear of the keep-outs in its 2 by 2 cells of 64 ft at the crown's 4.5 ft;
            dry - its marsh index cell's state, and a crossed cell's at most 12 segments; off the pond (1); under no standing
            crown - the crowns in its 3 by 3 cells of an 8 ft crown index; admitted: its crown written and filed in the crown index
        the wood recorded and filed in the registry's cells its ring covers
    woods off the sheet: their bearing and count recorded once, nothing drawn

## Indexes

- registry: cells of 64 ft; densest 29 things a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft against a seat's 9 ft crown, in at most 2 by 2 cells
- marsh index: cells of 64 ft, each inside, outside or crossed; densest 12 segments a crossed cell (the field's outline's measured ceiling, the marsh's rings no denser), from a smallest side of 64 ft
- crown index: cells of 8 ft (the lattice's spacing); densest 1 crown a cell (no crown under another), from a smallest side of 8 ft, so a seat's standing neighbors lie in its 3 by 3 cells

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 4 | the parcels, at most 4 on the sheet | every parcel on the sheet |
| the ring | per item | 24 | its 12 points, each bent to the ground (1) and written (1) | always 24 |
| the crowns (registry, marsh index and crown index cells examined) | per item | 119130 | the sweep's 33 rows, each crossed with the 12 edges (396); at most 771 seats inside, each 153: inside (1), the keep-outs' 2 by 2 cells with their 29 things and the cell (120), dry - its marsh cell and a crossed cell's 12 segments (13) - off the pond (1), the standing crowns' 3 by 3 cells of 8 ft with their at most 1 each (18); and each crown written and filed (1) | the largest parcel, every seat admitted |
| the filing (registry cells written) | per item | 31 | recorded (1), its at most 5 by 6 cells (30) | the largest parcel |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the marsh index (cells written) | once | 1573 | the marsh's rings walked through the 64 ft cells: their edge at root 2 over 64 ft, plus 3 a segment | a marsh at its largest |

So: 4 x (24 + 119130 + 31) x 1, plus the marsh index, the same at every size. The woods off the sheet record their bearing and count once (4) and draw nothing, the cheaper of the two exclusive cases.

## Totals

- at 20: 4 x (24 + 119130 + 31) x 1 + 1573 = 478313
- at 40: 4 x (24 + 119130 + 31) x 1 + 1573 = 478313
- at 80: 4 x (24 + 119130 + 31) x 1 + 1573 = 478313

## Earlier findings

- verdict-1, finding 1: fixed - the bearing is recorded once, and only for the woods off the sheet, the exclusive case
- verdict-1, finding 2: fixed - the crowns by a scanline sweep of the lattice rows against the ring's 12 edges
- verdict-1, finding 3: fixed - the ring's bend to the ground is counted, 1 a point
- verdict-1, finding 4: fixed - the ring's bounding box measured, 5 by 6 cells
- verdict-2, finding 1: fixed - no jitter: the crowns are a deterministic lattice (`woodland_room`), each seat tested by the contract's own rules, so no edge band is retested
- verdict-2, finding 2: fixed - the sweep's rows are floor(258.8 / 8) + 1 = 33
- verdict-2, finding 3: fixed - the on-sheet and off-sheet cases are exclusive; the total is the on-sheet one
- verdict-2, finding 4: fixed - the ring's perimeter measured, at most 806.8 ft; no figure rests on convexity

## Cheaper algorithms considered

- sweep: used - the crowns' lattice is swept row by row against the ring's edges
- grid or spatial index: used - the registry for the keep-outs, the marsh index for dry ground, the crown index for the standing crowns
- priority queue: not used - nothing is ranked
- incremental update: used - each crown is filed in the crown index as it is drawn, for the next seat's test
- memoizing what a scan does not change: used - the marsh's rings are indexed once for every seat
