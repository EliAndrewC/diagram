# Derivation - appurtenances, greenfield (feature 444 FR-015)

## Contract

- Reads: each household's homestead as laid on its lot (its yard, its beds, its byre and its storehouse or shed, each a box in the lot's layout), the layout inside the lot's middle 104 ft square and the rest of the 162 ft lot its wood's ground, planted later (0285: a household's ground about 104 ft a side, spread over about 162 ft with its stand of wood); the lots' lattice; the plan's well form (`well_siting`: by the lane or among the houses); the registry of what stands.
- Writes: each homestead's yard, beds, byre and storehouse or shed as the map's own records, each with its ring of corners; on the cluster form, the communal wells among the houses, each a curb on its apron, filed in the registry, so the lanes laid after are laid off it. On the lane form the wells are seated once the lanes stand, by `lane_wells`.
- Keeps: a well stands among the houses it serves, never out in the fields, a dwelling within about 95 ft, the cluster form's well among five to ten houses, off every lane, a dwelling's wall within 80 ft (0196); a hamlet draws one or two wells, one more where one would be the nearest for more than ten households (0196: "one more well is seated by the same form"); every household within about 760 ft of a well or open water (0196); an apron about 4 ft wider than its curb all round (0196); no well inside a household's farmstead (0196).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the records 12 and 23 beds, 10 and 20 yards, 4 and 7 byres, 1 and 3 sheds (2.65 a household at 20), each a ring of 4 corners; the wells 2 and 2, both of the lane form on both rolls; the well form a knob of two forms (0196), taken at even odds where the record gives no share; the seated lots (grown breadth-first from the anchor, as the homesteads lay them) fall in 4 and 4 tiles of 5 by 5 lots at 10 and 20, and on the same ground in 5 and 10 at 40 and 80, the most households in one tile 3, 6, 11 and 19, 2 and 3 tiles holding more than 10 at 40 and 80 - so 4, 7 and 13 wells at 20, 40 and 80 (measured 2026-10-29, the walk grown past the households on both reference rolls); a well's curb 16 ft across, its apron 24 ft; the hamlet about 820 ft across, inside one well's 760 ft reach from its middle; the typical densities (`items.md`, rubric S8): things of every kind 5.5 a 64 ft cell within 3 cells of a house.

## The algorithm

    for each homestead: its yard, beds, byre and storehouse or shed copied from its layout into their own records, each its
        record and its 4 corners written (5)
    the well form read (1); on the cluster form: each seated lot's tile of 5 by 5 lots taken from its lattice index (2); a tile
        of more than ten households split in two along its long side; for each tile (or half), its lots read (about 5) and
        the north corner of the lot nearest their mean taken (2), the well written (1) and filed (1 a cell); each household's
        distance to its tile's well checked against the reach (1)
    the seat holds every rule by construction, so no candidate is refused and none is tested: a lot's corner stands 29 ft
        off the 104 ft squares of the four lots that meet there, so a 24 ft apron (12 ft from its middle) lies outside every
        farmstead; the lot's box was clear of every water and the field when it was seated, so its corner is too; the lot's own
        house stands at its square's north side, about 29 ft from its north corner, inside the 80 ft and the 95 ft; the farthest
        lot of a 5 by 5 tile lies within 2.5 lots on each axis of its middle corner, 2.5 x 1.41 x 162 = 573 ft, inside the
        760 ft reach; the lanes are laid after, off the well's filed apron

## Indexes

- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a well's 24 ft apron overlapping (1 + 24/64)^2 = 1.9 cells, at the mean 5.5 things a cell near the houses (`items.md`, rubric S8), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the homesteads, one a household | the households |
| the records | per item | 13.25 | 2.65 records a homestead (1.15 beds, 1 yard, 0.35 byre, 0.15 shed), each its record and 4 corners written (5) | always the layout's records |
| slack | per item | 1 | the records are a count of the layout's parts | not applicable |
| the cluster wells (registry cells written) | over the run | 54 at 20, 102 at 40, 198 at 80 | at the cluster form's share of the rolls, one half (S9): each household's tile (2) and reach (1), 3 a household; each well its tile's about 5 lots read (5), its corner (2), written (1) and filed in 1.9 cells (1.9), 10, rounded up to 12 with the split's sort where a tile holds more than ten; 4, 7 and 13 wells: 60 + 48 = 108, 120 + 84 = 204, 240 + 156 = 396, and half of each | the cluster form on every roll |

So: homesteads x (13.25 x 1), plus the cluster wells.

## Totals

- at 20: 20 x (13.25 x 1) + 54 = 319
- at 40: 40 x (13.25 x 1) + 102 = 632
- at 80: 80 x (13.25 x 1) + 198 = 1258

## Growth

Linear, an exponent of 1.0: the records a homestead and the wells ten households each.

- pruning: a well's seat is read from its own tile's lots on the lattice, never searched for among all the households

## Earlier findings

- verdict-1, finding 1: fixed - the well's seat is a lot's north corner on the lattice, clear of every farmstead, every water and the field, and within 80 ft of its lot's house by construction, so no candidate is refused and none tested
- verdict-1, finding 2: fixed - the 95 ft, the 80 ft and outside-a-farmstead each hold by the lot's geometry, stated in the algorithm
- verdict-1, finding 3: fixed - the wells' households are 5 by 5 tiles of the lattice, not blocks of the seating order: the farthest lot within 573 ft of its well, measured 2 and 3 tiles over ten at 40 and 80, each split
- verdict-1, finding 4: fixed - the well's apron filed in the registry, so the lanes laid after keep off it

## Cheaper algorithms considered

- sweep: not used - each record is copied once
- grid or spatial index: used - the lots' own lattice gives each household's tile; the registry is written, never asked, the seat clear by construction
- priority queue: not used - the wells' houses are their tiles'
- incremental update: not used - each well is seated once
- memoizing what a scan does not change: used - the records are the layout's boxes, already turned, copied rather than laid again
