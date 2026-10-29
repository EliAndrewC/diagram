# Derivation - web, greenfield (feature 444 FR-015)

## Contract

- Reads: the seated lots' lattice - each household's 104 ft square inside its 162 ft lot, its house at the square's north side and its door on the yard - and the households; the track out's start on a lot corner; the plan's lane form (`lane_web`: side lanes or back lanes) and the share reached across a neighbor's land.
- Writes: the lane network inside the cluster - each household's own way from its dooryard, and the lanes they join, laid in the gaps between the lots - and, on the back-lane form, the back lanes and their cross lanes; each lane a record of its points, filed in the ways index.
- Keeps: the farmhouses placed first and the lanes drawn among them after, each lane following the houses (0246); the lanes laid in the gaps between homesteads, along the middle of the gaps, each household's way laid from its dooryard to the track out or an earlier way, joined at a T (0246); a lane's middle at least 7 ft clear of a garden fence (0246); a share of the households, rolled from none up to a quarter, reached across a neighbor's land with no lane of their own (0246); every other farmhouse served by a lane of its own, within 100 ft of a way (0246); a lane that serves nothing not drawn (0246); the back-lane form one of two, rolled (0246); nothing built on a lane (0246).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households, the lots grown as the homesteads lay them, and on past the households on the same ground for 40 and 80): the lots' gaps 58 ft wide (162 - 104), each household's square 29 ft off its lot's edge, so a lane in a gap's middle stands 29 ft off every square, its fence among them; the lattice's corners touching a seated lot 41, 71 and 121 at 20, 40 and 80; the gaps the households' ways climb, marked once, 21, 44 and 87 (1.05 to 1.1 a household, 1.1 taken); the breadth-first pass's ring R 4, 6 and 8 and the lots' span 9 by 6, 12 by 9 and 16 by 12; the house at its square's north side with its door on the yard, 57 ft below the lot's north edge (29 + 28) and 81 ft from its side edges, so the way runs from the door to the nearer side edge, 81 ft, and along it to the north corner, 57 ft; the lane form a knob of two forms taken at even odds; the share reached across a neighbor rolled from none to a quarter, a mean of an eighth; a leg of L ft along the lattice's axes crossing about L / 64 + 1 cells of the 64 ft ways index; a 162 ft gap at the lattice's bearing to the index, 3.5.

## The algorithm

    the gaps' graph: the lattice's corners, a gap between two corners open where a seated lot borders it - its edge lies inside
        that lot's box, which was clear of every water and the field when the lot was seated, so an open gap needs no test
    a breadth-first pass from the track's start corner over the open gaps: each corner popped (1), its 4 bordering lots looked
        up on the lattice once (4), its 4 gaps' state read from them
    each household's way: from its door across its dooryard to its lot's nearer side edge, 81 ft, round its own beds and fixtures
        by the layout's own path, and along the edge to the lot's north corner, 57 ft; 3 points written and its 2 legs filed in
        the cells they cross (2.6 and 2.1)
    each household's corner climbed up the pass's tree until a gap already marked (1 a gap, each gap marked once; 1 the stop)
    the marked gaps joined into lanes at their junctions (1 each), written, and filed in the ways index (3.5 cells each)
    the share reached across a neighbor rolled once and each household rolled against it (1); a household so reached lays no way
    on the back-lane form (half the rolls): the gap row at half the pass's ring R from the anchor's row, the cluster's middle
        depth from the field's edge, taken once (1), marked along the lots' span, and cross lanes every 300 ft, about every second
        lot, from it to the field's edge row, R / 2 gaps each; their gaps joined, written and filed as above
    the rules hold by construction: every lane runs in a gap's middle, 29 ft off every square and its fence, over clear ground;
        every way starts at its own door, so every farmhouse but the ones reached across a neighbor has a way within 100 ft and
        no lane serves nothing - the tree holds only the gaps a household's way climbs

## Indexes

- ways index: cells of 64 ft, each leg filed in every cell it crosses; a 162 ft gap crossing about 3.5 cells and a dooryard leg about 1.5, written here, from a smallest side of 64 ft
- the lots' lattice: cells of 162 ft, the seated lots by their lattice index, a corner's 4 bordering lots looked up directly, from a smallest side of 162 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the households | the households |
| the way from the door (ways index cells written) | per item | 6.3 | its 3 points written (3) and its 2 legs filed, 81 ft and 57 ft along the lattice's axes, L / 64 + 1 cells each (2.27 and 1.89): 7.2, at the seven in eight households that lay a way (S8) | always |
| the climb | per item | 2 | the gaps marked, 1.1 a household, once each (1.1), and the stop at seven in eight households (0.9) | always about 2 |
| the lanes (ways index cells written) | per item | 6.1 | 1.1 gaps a household, each joined (1), written (1) and filed in 3.5 cells (3.5): 5.5 x 1.1 | a cluster of many short rows |
| the share reached across | per item | 1 | each household rolled against the share | always 1 |
| slack | per item | 1 | every factor a measured count on the lattice, no search | not applicable |
| the pass (the lots' lattice cells examined) | over the run | 205 at 20, 355 at 40, 605 at 80 | each corner popped (1) and its 4 bordering lots read once (4): 41, 71 and 121 corners | a ragged cluster, more corners on its edge |
| the back lanes | over the run | 51 at 20, 84 at 40, 133 at 80 | on half the rolls (S9): the row taken (1), and its gaps along the span (9, 12, 16) and its cross lanes every second lot of R / 2 gaps (4.5 x 2, 6 x 3, 8 x 4): 18, 30 and 48 gaps, each joined, written and filed (5.5), counted whole though some lie on the tree already: 100, 166 and 265, half each, rounded up | the back-lane form on every roll |

So: households x (6.3 + 2 + 6.1 + 1) x 1, plus the pass and the back lanes.

- pruning: the pass visits only the lattice's corners that touch a seated lot, 41 to 121, and each household climbs only to the first marked gap; nothing visits the map's ground beyond the lots

## Totals

- at 20: 20 x (6.3 + 2 + 6.1 + 1) x 1 + 205 + 51 = 564
- at 40: 40 x (6.3 + 2 + 6.1 + 1) x 1 + 355 + 84 = 1055
- at 80: 80 x (6.3 + 2 + 6.1 + 1) x 1 + 605 + 133 = 1970

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.9: every factor a household's on the lattice, the corners a household falling as the cluster fills.

## Earlier findings

- verdict-1, finding 1: fixed - the way's legs from the layout, 81 ft to the side edge and 57 ft to the north corner, 2.27 and 1.89 cells
- verdict-1, finding 2: fixed - the back lanes' gaps from the lattice's measured span and ring, 18, 30 and 48
- verdict-1, finding 3: fixed - the way and the climb's stop at seven in eight households
- verdict-1, finding 4: fixed - a corner's 4 bordering lots read once, 5 a corner, the corners measured
- verdict-1, finding 5: fixed - the back lane's row at half the pass's ring from the anchor's row, one operation

## Cheaper algorithms considered

- sweep: not used - the gaps are walked by the breadth-first pass once
- grid or spatial index: used - the lots' own lattice for the gaps, the ways index written
- priority queue: not used - a breadth-first queue, each corner once, the tree's gaps in about distance order
- incremental update: used - each household climbs only to the tree already marked
- memoizing what a scan does not change: used - a gap's clearance is its bordering lot's, tested when the lot was seated, never again
