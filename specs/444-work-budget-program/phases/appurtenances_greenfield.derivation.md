# Derivation - appurtenances, greenfield (feature 444 FR-015)

## Contract

- Reads: each household's homestead as laid on its lot (its yard, its beds, its byre and its storehouse or shed, each a box in the lot's layout), the layout inside the lot's middle 104 ft square with the house, 46 by 28 ft, at that square's north side and centered across it, and the rest of the 162 ft lot its wood's ground, planted later (0285: a household's ground about 104 ft a side, spread over about 162 ft with its stand of wood; the house's place the homesteads' layout); the seated lots' lattice; the plan's well form (`well_siting`: by the lane or among the houses); the registry of what stands.
- Writes: each homestead's yard, beds, byre and storehouse or shed as the map's own records, each with its ring of corners; on the cluster form, the communal wells among the houses, each a curb on its apron, filed in the registry, so the lanes laid after are laid off it. On the lane form the wells are seated once the lanes stand, by `lane_wells`.
- Keeps: a well stands among the houses it serves, never out in the fields, a dwelling within about 95 ft, the cluster form's well among five to ten houses, off every lane, a dwelling's wall within 80 ft (0196); a hamlet draws one or two wells, one more where one would be the nearest for more than ten households or a household stands beyond the reach (0196: "one more well is seated by the same form"); every household within about 760 ft of a well or open water (0196); an apron about 4 ft wider than its curb all round (0196); no well inside a household's farmstead (0196).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the records 12 and 23 beds, 10 and 20 yards, 4 and 7 byres, 1 and 3 sheds (2.65 a household at 20), each a ring of 4 corners; the wells 2 and 2, both of the lane form; the well form a knob of two forms (0196), taken at even odds where the record gives no share; the wells one to ten households, 2, 4 and 8 at 20, 40 and 80; the seated lots (grown breadth-first from the anchor, as the homesteads lay them, and grown on past the households on the same ground for 40 and 80) cut into that many groups by halving the longer side at the median, each group holding a corner four seated lots share in 29 of 30 groups over the eight cuts, its farthest lot within 760 ft of that corner in 28 of 30 (the worst 834 ft); a well's curb 16 ft across, its apron 24 ft.

## The algorithm

    for each homestead: its yard, beds, byre and storehouse or shed copied from its layout into their own records, each its
        record and its 4 corners written (5)
    the well form read (1); on the cluster form: the seated lots cut into ceil(households / 10) groups by halving the longer
        side at its median (each lot once a level, a median found in a linear pass); for each group: its lots read (10) and
        their mean (2); each lot's lower corner asked whether the 3 lots sharing it are seated, from the lattice (3 a lot); the
        shared corner nearest the mean taken (10); its farthest lot's distance checked against the reach (10); written (1) and
        filed in the registry (1 a cell)
    a group with no shared corner, or a lot beyond the reach, is cut once more and seated as two (one more well, 0196)
    the seat holds the rules by construction: its 24 ft apron reaches 12 ft into each of the four seated lots meeting there,
        each lot's 104 ft square standing 29 ft off its edges, so the apron lies outside every farmstead; each of the four lots'
        boxes was clear of every water and the field when it was seated, and nothing else stands on its wood's ground yet, so
        the apron is clear of the registry; the two lots south of the corner keep their houses at their squares' north side,
        the nearest house corner 58 ft along and 29 ft across from it, about 65 ft, inside the 80 ft and the 95 ft

## Indexes

- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a well's 24 ft apron overlapping (1 + 24/64)^2 = 1.9 cells, written and never asked, the seat clear by construction, from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the homesteads, one a household | the households |
| the records | per item | 13.25 | 2.65 records a homestead (1.15 beds, 1 yard, 0.35 byre, 0.15 shed), each its record and 4 corners written (5) | always the layout's records |
| slack | per item | 1 | the records are a count of the layout's parts | not applicable |
| the cuts | over the run | 10 at 20, 40 at 40, 120 at 80 | at the cluster form's share, one half (S9): each seated lot once a level of the halving, log2 of the wells' count levels (1, 2, 3): 20, 80 and 240, half each | the cluster form on every roll |
| the cluster wells (registry cells written) | over the run | 72 at 20, 143 at 40, 286 at 80 | at the cluster form's share, one half (S9): each well its group's 10 lots read and their mean (12), the 3 lattice lookups a lot (30), the corner nearest the mean (10), the reach (10), written and filed in 1.9 cells (2.9): 64.9; one more well at the measured 3 of 30 groups, 0.1 x 65 = 6.5: 71.4 a well; 2, 4 and 8 wells (143, 286, 571), half each, rounded up | the cluster form on every roll |

So: homesteads x (13.25 x 1), plus the cuts and the cluster wells.

- pruning: a well's seat is read from its own group's lots on the lattice, never searched for among all the households

## Totals

- at 20: 20 x (13.25 x 1) + 10 + 72 = 347
- at 40: 40 x (13.25 x 1) + 40 + 143 = 713
- at 80: 80 x (13.25 x 1) + 120 + 286 = 1466

## Growth

From 20 to 80 households the stage grows at an exponent of about 1.04: the records a homestead and the wells ten households each, the cuts n log k.

## Earlier findings

- verdict-1, finding 1: fixed - the well's seat is a corner four seated lots share, clear of every farmstead, every water and the field by construction, so no candidate is refused and none tested
- verdict-1, finding 2: fixed - the 95 ft, the 80 ft and outside-a-farmstead each hold by the lots' geometry, stated in the algorithm
- verdict-1, finding 3: fixed - the wells' households are compact groups cut from the lattice, the reach measured in 28 of 30 and the rest given one more well
- verdict-1, finding 4: fixed - the well's apron filed in the registry, so the lanes laid after keep off it
- verdict-2, finding 1: fixed - the house's place in its lot is in the Reads (the north side of the 104 ft square, centered across it), and the seat is a corner four seated lots share, the apron's 12 ft reach into each of them clear
- verdict-2, finding 2: fixed - the wells ceil(households / 10), 2, 4 and 8, each group about ten households
- verdict-2, finding 3: fixed - the reach checked once a group, at its farthest lot, not once a household; a group beyond it gets one more well
- verdict-2, finding 4: fixed - the house's nearest corner about 65 ft from the seat (58 along, 29 across)
- verdict-2, finding 5: fixed - the corner nearest the mean is 10 distances over the group's lots
- verdict-2, finding 6: fixed - a group is cut by halving its longer side at the median, not a tile's side

## Cheaper algorithms considered

- sweep: not used - each record is copied once
- grid or spatial index: used - the lots' own lattice for the shared corners; the registry is written, never asked
- priority queue: not used - the groups are cut by medians, a linear pass a level
- incremental update: not used - each well is seated once
- memoizing what a scan does not change: used - the records are the layout's boxes, already turned, copied rather than laid again
