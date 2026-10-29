# Derivation - homesteads, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan's seat - the cluster's anchor on the field's dry margin, its axis and shape - and the belt's band; the households and the plan's family and byre forms; the field's outline, the brook, the ditches and the pond in the water index.
- Writes: each household's homestead on its own ground - the house, its threshing yard, its kitchen beds, its fixtures (the privy, the manure heap, the coop, the persimmon), its storehouse or shed and its byre where it keeps one, a retirement house where the household has one, and its way in to its door - and the access corridors from each door to where a lane will reach it; every part filed in the registry.
- Keeps: a household of a clustered settlement on a square of ground about 104 ft a side, spread once seated over about 162 ft a side with its stand of wood (0285: "Once seated ... a household is spread over about 162 ft a side, some 735 tsubo, which also holds its stand of wood"); a compact cluster, not a hollow arc (0032); the threshing yard and the kitchen beds keep 39 ft clear to their south of any house and 50 ft east, west and south of any tree (0038), rows of homesteads about 92 ft apart for it (0038: "Rows are set 92 ft apart, and a house (28 ft deep), its yard (about 26 ft) and 39 ft of sun come to about 93 ft"); a bed to the southeast, southwest, east or west of its house (0038); the storehouse on the side the settlement's form gives it (0040); every rule asked of a seat before the house is drawn (S4).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the houses 10 and 20, a mean nearest neighbor 170 and 164 ft (the 162 ft seated square); lots of 162 ft taken in ring order round the cluster's centroid clear of the field, the water and the pond at 10 of 12 and 20 of 23 lots tried (p 0.83 and 0.87, 0.85 taken); each house's ground record 11.5 and 11.45 keys, of them the parts drawn: the house, the yard, 2 beds, 4 fixtures, a byre at 4 of 10 and 7 of 20, a storehouse or shed at 1 of 10 and 3 of 20 (0.35 and 0.15 a household at 20), the rest of its keys the layout's turn, boxes and notes; retirement houses 5 and 11 (0.55 a household); access corridors 22 and 51 (2.55 a household at 20), 2 points each; the way in 4 points; the typical densities (`items.md`, rubric S8): water segments 3.7 and the field's outline segments 1.8 a crossed 64 ft cell.

## The algorithm

    the lots: squares of 162 ft on a lattice set on the anchor and the axis, generated in ring order out from the anchor (each 1),
        the cluster's shape a stretch of the ring's metric; each lot's box asked of the water index's cells it overlaps (each
        cell 1, each segment in a crossed cell 1) and of the belt's band (1); the first clear lots taken, one a household
    within its lot, the homestead laid from the form's own layout: the house at the lot's north side turned to the plan's bearing,
        its yard south of it, 39 ft of the lot clear to the yard's south before the next row's house (the 162 ft pitch keeps
        28 + 26 + 39 = 93 ft inside the lot, so no neighbor's house can shade it: the sun rule holds by construction), the beds on the
        house's flanks, the fixtures behind it, the storehouse on the form's side, a byre, a shed and a retirement house where rolled:
        each part's box from the layout (1), turned (1), written (1) and filed in the registry's cells its box overlaps (1.5)
    each household's kind, wealth, bearing jitter and quarter turn rolled (4); its way in, 4 points written (4) and its 3 legs filed
        in the registry (1.5 each); its access corridors, 2 points written and the leg filed (3.5 each)

## Indexes

- water index: cells of 64 ft, each segment filed in every cell it crosses, a box asked of the cells it overlaps; a lot's 162 ft box overlapping (1 + 162/64)^2 = 12.5 cells, segments only in the cells the field's edge or a water crosses, the mean 3.7 water and 1.8 outline segments a crossed cell (`items.md`, rubric S8), from a smallest side of 64 ft
- registry: cells of 64 ft, every part filed in every cell its box overlaps, a part's box (a 46 by 28 ft house to a 5 ft coop) overlapping about 1.5 cells on average, from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the houses, one a household | the households |
| the lot's search (water index cells examined) | per item | 18 | 1 / 0.85 = 1.18 lots tried a house (S8, 1/p), one clear and 0.18 refused: the clear lot's 12.5 cells read, its ring step (1) and the band (1), and the field's outline in the cells it crosses - the lots on the field's margin, about the third of them facing it, about 3 crossed cells at the mean 1.8 (1.8) - so 16.3; a refused lot stops at its first crossed cell, about half its cells and the segments there (9), 0.18 x 9 = 1.6; 17.9, rounded to 18 | a cluster pressed against the field and the brook |
| the parts (registry cells written) | per item | 41 | the house, the yard, 2 beds and 4 fixtures (8), a byre (0.35), a storehouse or shed (0.15) and a retirement house (0.55): 9.05 parts, each its box, turned, written and filed in about 1.5 cells (4.5) | always the layout's parts |
| the rolls, the way in and the corridors (registry cells written) | per item | 22 | the kind, the wealth, the jitter and the quarter turn (4); the way in's 4 points written (4) and its 3 legs filed in about 1.5 cells each (4.5); 2.55 corridors, each 2 points written and its leg filed (3.5): 8.9; 21.4, rounded to 22 | always |
| slack | per item | 1.05 | on the lot's search alone (the 18): the clear lots' share measured at 0.83 and 0.87 around the 0.85 taken, moving the lots tried a house by about 2.5%, rounded to 5% | not applicable |

So: houses x (18 x 1.05 + 41 + 22).

- pruning: the lots are taken in ring order from the anchor and the search stops at the household's count, so it touches 1.18 lots a house, never the ground's whole lattice.

## Totals

- at 20: 20 x (18 x 1.05 + 41 + 22) = 1638
- at 40: 40 x (18 x 1.05 + 41 + 22) = 3276
- at 80: 80 x (18 x 1.05 + 41 + 22) = 6552

## Growth

Linear, an exponent of 1.0: each house costs the same at every size, its lot asked only of its own cells.

## Earlier findings

- verdict-1, finding 1: fixed - the slack 1.05, from the clear lots' measured 0.83 to 0.87; the lot's search per house one clear lot and 0.18 refused, 18
- verdict-1, finding 2: fixed - the view dropped; the lot asks the water index and the belt's band, both in the Reads
- verdict-1, finding 3: fixed - a clear lot on the field's margin reads the outline's segments in the cells it crosses, the third of the lots facing the field (1.8)
- verdict-1, finding 4: fixed - the Bounds' 11.45 are the ground record's keys; the parts drawn are 9.05, the storehouse among them as the 0.15 storehouse or shed
- verdict-1, finding 5: fixed - the way in's legs and the corridors filed in the registry (22)

## Cheaper algorithms considered

- sweep: not used - the lots are taken in ring order, the first clear ones kept
- grid or spatial index: used - the water index for each lot's box, the registry for filing the parts
- priority queue: not used - ring order is generated in distance order directly, the lattice's own geometry
- incremental update: used - the lots are disjoint on the lattice, so a seated house never re-tests a neighbor's ground
- memoizing what a scan does not change: used - the layout's part boxes are the form's own, turned once a house
