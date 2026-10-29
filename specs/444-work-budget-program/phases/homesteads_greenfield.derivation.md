# Derivation - homesteads, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan's seat - the cluster's anchor on the field's dry margin, its axis and shape - and the belt's band; the households and the plan's family and byre forms; the field's outline, the brook, the ditches and the pond in the water index.
- Writes: each household's homestead on its own ground - the house, its threshing yard, its kitchen beds, its fixtures (the privy, the manure heap, the coop, the persimmon), its storehouse or shed and its byre where it keeps one, a retirement house where the household has one, and its way in to its door - and the access corridors from each door to where a lane will reach it; every part filed in the registry.
- Keeps: a household of a clustered settlement on a square of ground about 104 ft a side, spread once seated over about 162 ft a side with its stand of wood (0285: "Once seated ... a household is spread over about 162 ft a side, some 735 tsubo, which also holds its stand of wood"); a compact cluster, not a hollow arc (0032); the threshing yard and the kitchen beds keep 39 ft clear to their south of any house and 50 ft east, west and south of any tree (0038), rows of homesteads about 92 ft apart for it (0038: "Rows are set 92 ft apart, and a house (28 ft deep), its yard (about 26 ft) and 39 ft of sun come to about 93 ft"); a bed to the southeast, southwest, east or west of its house (0038); the storehouse on the side the settlement's form gives it (0040); every rule asked of a seat before the house is drawn (S4).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the houses 10 and 20, a mean nearest neighbor 170 and 164 ft (the 162 ft seated square); lots of 162 ft taken in ring order round the cluster's centroid clear of the field, the water and the pond at 10 of 12 and 20 of 23 lots tried (p 0.83 and 0.87, 0.85 taken); each house's ground 11.5 and 11.45 parts recorded, the parts drawn: the house, the yard, 2 beds, 4 fixtures, a byre at 4 of 10 and 7 of 20, a shed at 1 of 10 and 3 of 20 (0.35 and 0.15 a household at 20); retirement houses 5 and 11 (0.55 a household); access corridors 22 and 51 (2.55 a household at 20), 2 points each; the way in 4 points; the typical densities (`items.md`, rubric S8): water segments 3.7 and the field's outline segments 1.8 a crossed 64 ft cell.

## The algorithm

    the lots: squares of 162 ft on a lattice set on the anchor and the axis, generated in ring order out from the anchor (each 1),
        the cluster's shape a stretch of the ring's metric; each lot's box asked of the water index's cells it overlaps (each
        cell 1, each segment in a crossed cell 1) and of the belt's band and the view (2); the first clear lots taken, one a household
    within its lot, the homestead laid from the form's own layout: the house at the lot's north side turned to the plan's bearing,
        its yard south of it, 39 ft of the lot clear to the yard's south before the next row's house (the 162 ft pitch keeps
        28 + 26 + 39 = 93 ft inside the lot, so no neighbor's house can shade it: the sun rule holds by construction), the beds on the
        house's flanks, the fixtures behind it, the storehouse on the form's side, a byre, a shed and a retirement house where rolled:
        each part's box from the layout (1), turned (1), written (1) and filed in the registry's cells its box overlaps (1.5)
    each household's kind, wealth, bearing jitter and quarter turn rolled (4); its way in, 4 points (4); its access corridors, 2 points each (2)

## Indexes

- water index: cells of 64 ft, each segment filed in every cell it crosses, a box asked of the cells it overlaps; a lot's 162 ft box overlapping (1 + 162/64)^2 = 12.5 cells, segments only in the cells the field's edge or a water crosses, the mean 3.7 water and 1.8 outline segments a crossed cell (`items.md`, rubric S8), from a smallest side of 64 ft
- registry: cells of 64 ft, every part filed in every cell its box overlaps, a part's box (a 46 by 28 ft house to a 5 ft coop) overlapping about 1.5 cells on average, from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the houses, one a household | the households |
| the lot's search (water index cells examined) | per item | 15 | 1 / 0.85 = 1.18 lots tried a house (S8, 1/p): a clear lot's 12.5 cells read, its ring step (1) and the band and the view (2), no segment in it (15.5); a refused lot stops at its first crossed cell, about half its cells and the segments there (9); 0.85 x 15.5 + 0.18 x 9, rounded to 15 | a cluster pressed against the field and the brook |
| the parts (registry cells written) | per item | 41 | the house, the yard, 2 beds and 4 fixtures (8), a byre (0.35), a shed (0.15) and a retirement house (0.55): 9.05 parts, each its box, turned, written and filed in about 1.5 cells (4.5) | always the layout's parts |
| the rolls, the way in and the corridors | per item | 13 | the kind, the wealth, the jitter and the quarter turn (4), the way in's 4 points (4), 2.55 corridors of 2 points (5) | always |
| slack | per item | 2 | on the lot's search alone (the 15): the spread of the clear lots' share around 0.85 between seeds and shapes | a cluster pressed against the field and the brook |

So: houses x (15 x 2 + 41 + 13).

- pruning: the lots are taken in ring order from the anchor and the search stops at the household's count, so it touches 1.18 lots a house, never the ground's whole lattice.

## Totals

- at 20: 20 x (15 x 2 + 41 + 13) = 1680
- at 40: 40 x (15 x 2 + 41 + 13) = 3360
- at 80: 80 x (15 x 2 + 41 + 13) = 6720

## Growth

Linear, an exponent of 1.0: each house costs the same at every size, its lot asked only of its own cells.

## Cheaper algorithms considered

- sweep: not used - the lots are taken in ring order, the first clear ones kept
- grid or spatial index: used - the water index for each lot's box, the registry for filing the parts
- priority queue: not used - ring order is generated in distance order directly, the lattice's own geometry
- incremental update: used - the lots are disjoint on the lattice, so a seated house never re-tests a neighbor's ground
- memoizing what a scan does not change: used - the layout's part boxes are the form's own, turned once a house
