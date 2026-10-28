# Derivation - pond_bank (feature 444)

## Contract

- Reads: the tail pond (radii rx and ry, the manifest's `pond`: 134 at 20, 190 at 40, 268 at 80 for rx and 85 at 20, 121 at 40, 170 at 80 for ry, the sink's own figures) and its reed fringe (`SINK_FRINGE`, 44 ft), the knob `pond_bank` (rolled bare or planted, 0061), the fan's outline in the field's index (square cells of 38.6 ft), the brook, and what stands - roofs, wellheads, yards' and beds' sun ground, crowns and lanes - in a standing grid of 24 ft cells (two crown reaches) the stages before it keep as they place.
- Writes: on a planted bank, mulberry and cudrania in turn round the ring, one seat every `POND_BANK_PITCH_FT` (30 ft, a GUESS), the ring a crown's radius (`POND_BANK_CROWN_FT`, 6 ft, a GUESS) beyond the reeds, each seat jittered within the bank's play (`POND_BANK_FT`, 18 ft, less two crown radii: 6 ft, across the ring), each crown in `tree_crowns`, the trees in `meta.pond_bank_trees`; on a bare bank, nothing.
- Keeps: footprints never overlap (the overlap matrix, `overlap/`: two structures may not share ground); no crown on a roof or a wellhead, or on a yard's or bed's sun ground; no trunk on a tread, the crop or the water (0061, 0071); no two crowns overlap (CONVENTION), which the pitch keeps by itself: seats 30 ft apart, jittered at most 6 ft across the ring, stand at least 24 ft apart, twice a crown's width, and the ring divided evenly leaves the closing gap no shorter than the pitch. The cohort's checks: each crown against the overlap matrix (`tree_crowns`) - carried by the seat's tests.
- Bounds (measured 2026-10-28, the reference manifests, `phases/items.md`): the seat ring the pond's radii plus 50 ft, its perimeter divided evenly at no less than the pitch: floor(perimeter / 30), 33 at 20, 43 at 40, 56 at 80 (the radii x1.41 a doubling, the sink's figures). Of what stands: the smallest side of any footprint 10.3 ft (a byre or a bed, measured at 10; 10.9 ft at 20), a wellhead 16 ft across, the smallest crown 12.8 ft; the most lane segments in one 24 ft cell 8 (at a junction, measured at 20); the brook 7 ft wide, the most brook segments in one 38.6 ft cell 12; the most outline segments in one 38.6 ft cell 11.

## The algorithm

    roll the bank's form; if bare, record it and return
    for each seat round the ring, at the pitch: jitter it within the play; look once at the 4 standing grid cells its crown reaches
        (the trunk is the crown's center, so the same look serves both), testing every footprint and lane in them; test the
        trunk against the outline segments in its 38.6 ft cell, and the brook's segments in its cell and in any neighbor within the brook's half-width, and the pond exactly; seat it if free
    record the trees and their kinds

## Indexes

- standing grid: cells of 24 ft (two crown reaches); densest 19 footprints a cell, from a smallest side of 10.3 ft - non-overlapping footprints touching a cell lie in a square of 24 + 2 x 10.3 ft, each holding at least a 10.3 ft square of it: ((24 + 2 x 10.3) / 10.3)^2 = 18.75, rounded up - and 8 lane segments a cell (measured at a junction, the ceiling)
- outline index: cells of 38.6 ft (the field's); densest 11 outline segments a cell, measured - a cell's side of 38.6 ft against the outline's 0.1 ft sliver; the ceiling
- brook cells: cells of 38.6 ft (the field's grid); densest 12 brook segments a cell, measured - a cell's side of 38.6 ft against the brook's shortest segment, 2.9 ft; the ceiling

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 33 at 20, 43 at 40, 56 at 80 | the ring's seats (the Bounds) | a planted bank at 80 households |
| the standing grid's look (cells examined) | per item | 4 | the crown's reach, 12 ft, in 24 ft cells meets at most 4; the trunk is its center, so one look serves both | always 4 |
| the footprints | per item | 76 | at most 19 a cell (the Indexes) x 4 cells | the densest cells |
| the lanes | per item | 8 | the trunk is a point, tested against the treads in its own 24 ft cell: at most 8 lane segments, junctions included (the Indexes), each lane filed in every cell its tread touches | a trunk at a junction |
| the crop (outline index cells examined) | per item | 12 | the trunk's cell examined and at most 11 outline segments - the field's index files each outline segment in every cell it crosses, so a cell with none is wholly inside or outside, and the trunk's side of the segments it holds says which | the 11-segment ceiling |
| the brook (brook cells examined) | per item | 52 | the brook is 7 ft wide, so a trunk within 3.5 ft of a cell's edge is tested against the next cells too: at most 4 cells, each examined and its at most 12 brook segments tested | a seat at a cell's corner beside the brook |
| the pond | per item | 1 | one exact distance from the ellipse | always 1 |
| the jitter | per item | 1 | one draw within the play | always 1 |
| the kind | per item | 1 | the next of mulberry and cudrania | always 1 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the roll | once | 1 | the bank's form | always 1 |

So: seats x (4 + 76 + 8 + 12 + 52 + 1 + 1 + 1) x 1 + the roll.

## Totals

- at 20: 33 x (4 + 76 + 8 + 12 + 52 + 1 + 1 + 1) x 1 + 1 = 5116
- at 40: 43 x (4 + 76 + 8 + 12 + 52 + 1 + 1 + 1) x 1 + 1 = 6666
- at 80: 56 x (4 + 76 + 8 + 12 + 52 + 1 + 1 + 1) x 1 + 1 = 8681

## Cheaper algorithms considered

- sweep: used - the ring is walked once, seat by seat, at its pitch
- grid or spatial index: used - the standing grid of 24 ft cells and the field's outline cells, so a seat meets a bounded number
- priority queue: not used - no seat is ranked; each is taken or left on its own test
- incremental update: used - the standing grid is kept by the stages before as they place, so this stage builds none; and the pitch keeps the crowns apart, so no seat is tested against another
- memoizing what a scan does not change: used - one look at the 4 standing cells serves both the crown and the trunk; the brook is read in the field's cells as the field filed it (by its centerline), not re-filed by its half-width - re-filing it would be a pass over all its segments for one stage's seats, so the trunk's neighboring cells are tested instead
