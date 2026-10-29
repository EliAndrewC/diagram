# Derivation - track (feature 444)

## Contract

- Reads: the way out's gate, set by the homesteads on the cluster's edge toward the way out (`way_out_gate`); the field's outline and its fall (the ideal bearing: away from the field, leaning downslope); the site's free-ground raster (the wet ground, the crop, the ponds and the water, as the homesteads built it) and the parts index (the steadings), both standing from the homesteads; the field's outline index; the canvas.
- Writes: the connector, one lane from the gate to past the canvas edge (`lanes`, `connector`), its no-build corridor registered (`Settlement.lane`), and `way_out_track`.
- Keeps: the bearing tried outward from the ideal, alternating sides at growing angles, 41 bearings (`connector_track`), the first clean of wet ground, the steadings and every crop, pond and water taken (0081); where none is clean, the least-bad dry bearing clear of every steading, else the dry exit's flood (`connector_dry_exit`); a leg that meets the field goes round it on the outline's shorter arc, each vertex stepped the margin clear on its normal (`route_around`, 0081, the GM 2026-08-12); square at the water as laid (0035, 0084); drawn past the canvas edge; asked once the last house stands (0246, feature 320); every rule asked of a bearing before the track is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the canvas 1,521 by 1,726 ft and 2,274 by 2,486 ft, its diagonal 2,300 and 3,369 ft (x1.47: 3,369 at 20, 4,953 at 40, 7,281 at 80); a ray at most the canvas diagonal and the 64 ft drawn past the edge; the raster's cells, 32 ft, 5,521 at 20, 11,926 at 40, 25,759 at 80 (x2.16); at most 20 site-boundary segments in a 32 ft cell; at most 7 placed parts in a 64 ft cell; at most 12 outline segments in a 64 ft cell; the field's outline 67 and 78 points (x1.16: 78 at 20, 90 at 40, 105 at 80), its longest edge 222 and 183 ft (222 taken) and its perimeter 3,146 and 4,874 ft (x1.55: 4,874 at 20, 7,555 at 40, 11,710 at 80); the splice's margin 17 ft (`SPUR_SETBACK`, off the field's envelope); the lane's corridor 20 ft wide (`CONNECTOR_WIDTH` 6 ft and `LANE_CLEARANCE` 7 ft a side), under a 64 ft cell, so at most 2 cells across; the connector one leg at 10 and 20 (2,072 and 3,333 ft); 1 ft a pixel at the hamlet scale.

## The algorithm

    the ideal bearing from the field's fall and the gate (1)
    for each of the 41 bearings, in the contract's order, until one is clean: walk the ray from the gate past the canvas edge
        through the raster's 32 ft cells (a blocked cell refuses it; an undecided cell's segments tested) and the parts index's
        64 ft cells (the steadings), keeping the least-bad dry one (a comparison a ray)
    none clean and none dry: the dry exit's flood over the raster from the gate to the canvas edge, which yields a dry exit
        cell; the track is then the straight leg from the gate through that cell and on past the edge, the chosen ray
    the chosen ray's crossings with the field's outline, from the outline index's cells along it; each entering and leaving
        pair spliced with the outline's shorter arc, each vertex stepped the 17 ft margin clear (1) and its new leg tested against
        the outline index, the raster and the parts index in the cells it crosses (the arc must keep off wet ground and the
        steadings, as the ray did)
    square the lane at each water it crosses (`square_run`): each leg's raster cells, their segments tested for a water crossing
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
| slack | per item | 2 | what varies around the typical case (S8): a bearing or two more before a clean one, a splice where a ray meets the field | a ray across the field |
| the bearings (raster and parts index cells examined) | over the run | 1,092 at 20, 1,512 at 40, 2,133 at 80 | the first bearings from the ideal, 3 at the typical (the reference rolls' connector is one straight leg at 10 and 20, so the ideal or a near bearing is clean), each a ray of 155 at 20, 225 at 40, 328 at 80 raster cells read (1), the about 20 boundary segments a ray crosses at the mean 2.5 a crossed cell (50), and 79 at 20, 114 at 40, 166 at 80 parts index cells, each read with the parts a ray meets, typically none beside the cell (2), and its comparison (1) | the typical exit |
| the crossings (outline index cells examined) | over the run | 237 at 20, 342 at 40, 498 at 80 | the chosen ray's 79 at 20, 114 at 40, 166 at 80 cells of 64 ft, each with the mean 2 outline segments a crossed cell, and the cell (3) | the typical exit |
| the corridor (parts index cells written) | over the run | 158 at 20, 228 at 40, 332 at 80 | the one straight leg filed in at most 2 cells across each cell along it | the typical exit |
| the squaring (raster cells examined) | over the run | 205 at 20, 275 at 40, 378 at 80 | the leg's raster cells (1), and its about 20 water and boundary crossings at the mean 2.5 segments (50) | the typical exit |

So: 1 x 1 x 2, plus the bearings, the crossings, the corridor and the squaring. The dry exit's flood and the splice round the field run only where no near bearing is clean, inside the slack.

## Totals

- at 20: 1 x 1 x 2 + 1092 + 237 + 158 + 205 = 1694
- at 40: 1 x 1 x 2 + 1512 + 342 + 228 + 275 = 2359
- at 80: 1 x 1 x 2 + 2133 + 498 + 332 + 378 = 3343

## Earlier findings

- verdict-1, finding 1: fixed - the splice's leg is an outline edge, at most 222 ft (measured), with the 17 ft margin (`SPUR_SETBACK`) at each end, 256 ft, its cells counted from that
- verdict-1, finding 2: fixed - the corridor is the lane as spliced, the ray plus the shorter arc and its margins, 20 ft wide in at most 2 cells across
- verdict-1, finding 3: fixed - the plus 3 is stated: a grid walk crosses one cell more than the grid lines it crosses each way
- verdict-1, finding 4: fixed - each spliced leg is tested against the raster and the parts index as well as the outline index, counted in the splice
- verdict-1, finding 5: fixed - squaring at the water is this stage's (`square_run` on the connector as laid), its own row
- verdict-2, finding 1: fixed - the legs are the spliced vertices plus one a pair plus 1, the pairs at most half the vertices (a straight ray crosses each edge once), the arcs at most the perimeter in all, and the margin 17 ft at each end of each leg
- verdict-2, finding 2: fixed - the dry exit's flood yields a dry exit cell, and the track is the straight leg through it, the chosen ray
- FR-014 re-score: each factor at the typical case (rubric S8): the reference rolls' connector is one straight leg, so the first bearings near the ideal are clean and neither the dry exit's flood nor a splice round the field runs; the mean densities of `items.md`; slack 2 (ask:444-budget-standard; the accept was ask:444-T04-track-round-3)

## Cheaper algorithms considered

- sweep: not used - the bearings are tried in the contract's order and the first clean one wins; a sweep of angles over the obstacles would order them the same and save no factor at 41 rays
- grid or spatial index: used - the homesteads' raster and parts index and the field's outline index, read, not built
- priority queue: not used - the dry exit's steps are equal, so a breadth-first queue stands in for one
- incremental update: not used - one lane is drawn, once
- memoizing what a scan does not change: used - the raster and the indexes built by earlier stages are read, not rebuilt
