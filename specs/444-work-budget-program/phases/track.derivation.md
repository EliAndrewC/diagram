# Derivation - track (feature 444)

## Contract

- Reads: the way out's gate, set by the homesteads on the cluster's edge toward the way out (`way_out_gate`); the field's outline and its fall (the ideal bearing: away from the field, leaning downslope); the site's free-ground raster (the wet ground, the crop, the ponds and the water, as the homesteads built it) and the parts index (the steadings), both standing from the homesteads; the field's outline index; the canvas.
- Writes: the connector, one lane from the gate to past the canvas edge (`lanes`, `connector`), its no-build corridor registered (`Settlement.lane`), and `way_out_track`.
- Keeps: the bearing tried outward from the ideal, alternating sides at growing angles, 41 bearings (`connector_track`), the first clean of wet ground, the steadings and every crop, pond and water taken (0081); where none is clean, the least-bad dry bearing clear of every steading, else the dry exit's flood (`connector_dry_exit`); a leg that meets the field goes round it on the outline's shorter arc, each vertex stepped the margin clear on its normal (`route_around`, 0081, the GM 2026-08-12); square at the water as laid (0035, 0084); drawn past the canvas edge; asked once the last house stands (0246, feature 320); every rule asked of a bearing before the track is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the canvas 1,521 by 1,726 ft and 2,274 by 2,486 ft, its diagonal 2,300 and 3,369 ft (x1.47: 3,369 at 20, 4,953 at 40, 7,281 at 80); a ray at most the canvas diagonal and the 64 ft drawn past the edge; the raster's cells, 32 ft, 5,521 at 20, 11,926 at 40, 25,759 at 80 (x2.16); at most 20 site-boundary segments in a 32 ft cell; at most 7 placed parts in a 64 ft cell; at most 12 outline segments in a 64 ft cell; the field's outline 67 and 78 points (x1.16: 78 at 20, 90 at 40, 105 at 80); the connector one leg at 10 and 20 (2,072 and 3,333 ft); 1 ft a pixel at the hamlet scale.

## The algorithm

    the ideal bearing from the field's fall and the gate (1)
    for each of the 41 bearings, in the contract's order, until one is clean: walk the ray from the gate past the canvas edge
        through the raster's 32 ft cells (a blocked cell refuses it; an undecided cell's segments tested) and the parts index's
        64 ft cells (the steadings), keeping the least-bad dry one (a comparison a ray)
    none clean and none dry: the dry exit's flood over the raster from the gate to the canvas edge
    the chosen ray's crossings with the field's outline, from the outline index's cells along it; each entering and leaving
        pair spliced with the outline's shorter arc, each vertex stepped the margin clear (1) and its new leg tested against
        the outline index's cells it crosses
    draw the lane: recorded, its corridor filed in the parts index's cells along it

## Indexes

- raster: cells of 32 ft (the homesteads'); densest 20 boundary segments a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 32 ft
- parts index: cells of 64 ft (the homesteads'); densest 7 placed parts a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft
- outline index: cells of 64 ft (the field's); densest 12 outline segments a cell (the field's measured ceiling), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the connector, one leg | always 1 |
| the ideal bearing | per item | 1 | the field's fall against the gate | always 1 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the bearings (raster and parts index cells examined) | over the run | 159,408 at 20, 231,158 at 40, 336,897 at 80 | 41 bearings, each a ray of at most 155 at 20, 225 at 40, 328 at 80 raster cells - the diagonal and 64 ft past it at root 2 over 32 ft, plus 3 - each read with its at most 20 segments (21), and 79 at 20, 114 at 40, 166 at 80 parts index cells over 64 ft, each with its at most 7 parts (8), and its comparison (1) | every bearing refused, every cell undecided |
| the dry exit's flood (raster cells examined) | over the run | 49,689 at 20, 107,334 at 40, 231,831 at 80 | each raster cell popped once and its 8 neighbors read, on a breadth-first queue (the steps are equal) | no bearing dry |
| the crossings (outline index cells examined) | over the run | 1,027 at 20, 1,482 at 40, 2,158 at 80 | the chosen ray's 79 at 20, 114 at 40, 166 at 80 cells of 64 ft, each with its at most 12 outline segments (13) | the longest ray |
| the splice (outline index cells examined) | over the run | 4,134 at 20, 4,770 at 40, 5,565 at 80 | at most every outline vertex spliced once: stepped (1) and its new leg, under 64 ft between two outline points, in at most 2 by 2 cells with their 12 segments (52) | the ray across the whole field |
| the corridor (parts index cells written) | over the run | 79 at 20, 114 at 40, 166 at 80 | the lane filed in the cells along it, at most the ray's | the longest ray |

So: 1 x 1 x 1, plus the bearings, the flood, the crossings, the splice and the corridor.

## Totals

- at 20: 1 x 1 x 1 + 159408 + 49689 + 1027 + 4134 + 79 = 214338
- at 40: 1 x 1 x 1 + 231158 + 107334 + 1482 + 4770 + 114 = 344859
- at 80: 1 x 1 x 1 + 336897 + 231831 + 2158 + 5565 + 166 = 576618

## Cheaper algorithms considered

- sweep: not used - the bearings are tried in the contract's order and the first clean one wins; a sweep of angles over the obstacles would order them the same and save no factor at 41 rays
- grid or spatial index: used - the homesteads' raster and parts index and the field's outline index, read, not built
- priority queue: not used - the dry exit's steps are equal, so a breadth-first queue stands in for one
- incremental update: not used - one lane is drawn, once
- memoizing what a scan does not change: used - the raster and the indexes built by earlier stages are read, not rebuilt
