# Derivation - track, greenfield (feature 444 FR-015)

## Contract

- Reads: the seated lots' lattice and the households' parts in the registry; the plan's bearing of the road out and the seat's anchor on the field's margin; the field's outline; the water index; the view.
- Writes: the track out - from its start on the cluster's edge to the map's edge, a 6 ft connector - and its gate point; the spur from the cluster to the field's head; both filed in the ways index, and any water they cross handed to `crossings`.
- Keeps: no way is sought while houses are seated; once the last house stands, the track out's start is set on the cluster's edge (0246); a track passing outside the cluster keeps 7 ft off every part of a homestead (0246); the spur to the fields belongs to no household and keeps the 7 ft gap from every garden (0246).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the track out one leg, 2,072 and 3,333 ft long, crossing no water on either, past 20 with the view's side (x1.47 a doubling: 4,900 and 7,200 ft); its start a lot's outer corner; the lots seated within the breadth-first pass's ring R of the anchor, its lattice span 7 by 3 and 9 by 6 lots at 10 and 20, so R about 5 at 20, past 20 with the square root of the lots (7 at 40, 10 at 80); every homestead's square 29 ft inside its lot's edge (the homesteads' layout), so a way leaving from a lot's outer corner stands 29 ft off every part; the spur one leg from the anchor's lot to the outline's highest point, about 160 ft; the typical densities (`items.md`, rubric S8): water segments 3.7 a crossed 64 ft cell, things of every kind 5.5 a 64 ft cell within 3 cells of a house.

## The algorithm

    the track's start: the lattice's lines across the bearing walked from the outermost the breadth-first pass reached, ring R,
        inward, each line's R + 1 cells looked up on the lattice until a seated lot is found (1 a cell) - a line's cells are an
        upper bound on the projection of any lot further in, so the first seated lot on the outermost occupied line is the
        largest; on a ragged edge the next line is walked too (about 2 lines); its outer corner
    the track's leg to the view's edge along the bearing: the water index's cells it crosses read in order (each 1, each segment
        in a crossed cell 1), any crossing handed on (1); it leaves from the outermost lot's outer corner along the bearing, so no
        other lot lies ahead of it and every homestead part stands at least 29 ft off it: the 7 ft holds by construction
    the spur: from the anchor's lot corner to the outline's highest point, known from the seat (2); its about 3 cells read as above;
        it leaves from a lot's corner too, 29 ft off every garden, so the 7 ft holds by construction
    written: the track's 2 points, the gate, the spur's 2 points (5); both filed in the ways index's cells they cross (1 a cell)

## Indexes

- water index: cells of 64 ft, each segment filed in every cell it crosses; a leg read cell by cell along its line, (length / 64) x 1.27 cells for a line at a random bearing, the mean 3.7 segments a crossed cell, from a smallest side of 64 ft
- the lots' lattice: cells of 162 ft, the seated lots by their lattice index, a line's cells looked up directly, from a smallest side of 162 ft
- ways index: cells of 64 ft, each leg filed in every cell it crosses, written here, from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the track out and its spur, once a map | always 1 |
| the start (the lots' lattice cells examined) | per item | 12 at 20, 16 at 40, 22 at 80 | about 2 lines of R + 1 cells from the outermost ring, R about 5, 7 and 10 (the lattice's span measured, past 20 with the square root of the lots) | a ragged edge facing the bearing |
| the track's leg (water index cells examined) | per item | 66 at 20, 97 at 40, 143 at 80 | its cells, 3,333 / 64 x 1.27 = 66 at 20 (97, 143 with the view's side), each read; no water crossed on either reference roll, so no segment read | a track across the brook |
| the spur (water index cells examined) | per item | 5 | its 2 ends and its about 3 cells | always about 5 |
| the writes (ways index cells written) | per item | 74 at 20, 105 at 40, 151 at 80 | the track's 2 points, the gate and the spur's 2 points written (5), and the two legs filed in the cells they cross (66 + 3, 97 + 3, 143 + 3) | always |
| slack | per item | 1 | every factor is a length or a count of the reference rolls' output | not applicable |

So: 1 x (the start + the track's leg + 5 + the writes) x 1.

- pruning: the start is found by walking the lattice's lines across the bearing from the outermost inward, each line an upper bound on every lot further in, so it stops at the first occupied line and never reads the households

## Totals

- at 20: 1 x (12 + 66 + 5 + 74) x 1 = 157
- at 40: 1 x (16 + 97 + 5 + 105) x 1 = 223
- at 80: 1 x (22 + 143 + 5 + 151) x 1 = 321

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.52: the track's leg with the view's side, the start with the lattice's span.

## Earlier findings

- verdict-1, finding 1: fixed - the start found by walking the lattice's lines across the bearing from the outermost inward, about 2 lines of R + 1 cells
- verdict-1, finding 2: fixed - the 7 ft holds by construction: the track and the spur leave from a lot's corner, 29 ft off every homestead square; the registry row dropped
- verdict-1, finding 3: fixed - the writes count the 5 points, the gate among them
- verdict-1, finding 4: fixed - the spur filed in its about 3 cells
- verdict-1, finding 5: fixed - the spur's 7 ft from every garden holds by construction, as the track's

## Cheaper algorithms considered

- sweep: used - the track's leg read cell by cell along its line
- grid or spatial index: used - the water index along the legs, the lots' lattice for the start
- priority queue: not used - the lattice's lines are walked in order from the outermost, each a bound on the next
- incremental update: not used - one track
- memoizing what a scan does not change: used - the spur's end is the seat's highest outline point, read rather than found again
