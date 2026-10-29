# Derivation - woodland (feature 444)

## Contract

- Reads: the coppice parcels the hinterland scanned (`open_ground_patches`: each a seat on ground nothing else wanted, its keep-outs tested at its reach, clear of every clump of the grove, `woodland_clear_of_grove`); the registry, into which each wood is filed; the `woodland` knob (on the sheet, or off it with its bearing, `meta.woodland_offsheet`).
- Writes: each worked wood (`commons`, role `woodland`): an irregular ring inside its parcel's reach, never a rectangle (T36), stocked with coppice crowns; or, where the woods lie off the sheet, only their bearing and count in `meta.woodland_offsheet`.
- Keeps: coppice on the scanned parcels, each stocked as a worked wood (0077); the worked coppice only, never the strip woods or coppice gone to brush (0077); the ring's line bent to the ground (a GUESS); drawn on parcels the scrub already kept out of, so no crown is tested against the scrub; every rule asked of the parcel at the scan, before this stage draws it (S4).
- Bounds (measured 2026-10-28 on the pool's scripted hamlets that draw a wood on the sheet - Inashiro at 15 households, one parcel; Kashikawa at 20, three - the reference roll draws its 4 parcels off the sheet): at most 4 parcels (the knob's count, the same at 10 and 20); each a ring of 12 points, at most 49,338 sq ft, in a 222 ft square at most, so in at most 5 by 5 cells of 64 ft; its crowns at one a 64 sq ft (545 in 34,941 and 771 in 49,338 sq ft, an 8 ft pitch), at most 771 a parcel; the parcels' size set by the ground the scan finds, not by the households, so the stage is flat in the households.

## The algorithm

    for each scanned parcel on the sheet: its ring written (12 points); its crowns laid on the 8 ft jittered grid inside it, each
        tested inside the ring (12 edges), its jitter drawn (1) and written (1); the wood recorded and filed in the registry's
        cells its ring covers
    woods off the sheet: their bearing and count recorded (the reference's case), nothing drawn

## Indexes

- registry: cells of 64 ft (the hinterland's), each wood filed in the at most 5 by 5 cells its ring covers; densest one wood a cell, from a smallest side of 64 ft (the parcels were scanned apart, clear of each other)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 4 | the parcels, at most 4 on the sheet | every parcel on the sheet |
| the ring | per item | 12 | its 12 points written | always 12 |
| the crowns | per item | 10794 | at most 771 crowns, each tested inside the ring's 12 edges (12), its jitter drawn (1), written (1) | the largest parcel |
| the filing (registry cells written) | per item | 30 | recorded (1), its at most 5 by 5 cells (25), and its bearing record (4) | the largest parcel |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |

So: 4 x (12 + 10794 + 30) x 1, the same at every size.

## Totals

- at 20: 4 x (12 + 10794 + 30) x 1 = 43344
- at 40: 4 x (12 + 10794 + 30) x 1 = 43344
- at 80: 4 x (12 + 10794 + 30) x 1 = 43344

## Cheaper algorithms considered

- sweep: not used - each parcel's crowns are a grid inside it, laid once
- grid or spatial index: used - the crowns on a grid; each wood filed in the registry's cells
- priority queue: not used - nothing is ranked
- incremental update: used - each wood is filed as it is drawn
- memoizing what a scan does not change: used - the parcels' keep-outs were tested at the hinterland's scan and are not tested again
