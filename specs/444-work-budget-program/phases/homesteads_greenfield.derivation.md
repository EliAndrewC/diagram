# Derivation - homesteads, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan's seat - the cluster's anchor on the field's dry margin, its axis and shape - and the belt's band; the households and the plan's family and byre forms; the field's outline, the brook, the ditches and the pond in the water index.
- Writes: each household's homestead on its own ground - the house, its threshing yard, its kitchen beds, its fixtures (the privy, the manure heap, the coop, the persimmon), its storehouse or shed and its byre where it keeps one, a retirement house where the household has one, and its way in to its door - and the access corridors from each door to where a lane will reach it; every part filed in the registry.
- Keeps: a household of a clustered settlement on a square of ground about 104 ft a side, spread once seated over about 162 ft a side with its stand of wood (0285: "Once seated ... a household is spread over about 162 ft a side, some 735 tsubo, which also holds its stand of wood"); a compact cluster, not a hollow arc (0032); the threshing yard and the kitchen beds keep 39 ft clear to their south of any house and 50 ft east, west and south of any tree (0038), rows of homesteads about 92 ft apart for it (0038: "Rows are set 92 ft apart, and a house (28 ft deep), its yard (about 26 ft) and 39 ft of sun come to about 93 ft"); a bed to the southeast, southwest, east or west of its house (0038); the storehouse on the side the settlement's form gives it (0040); every rule asked of a seat before the house is drawn (S4).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the houses 10 and 20, a mean nearest neighbor 170 and 164 ft (the 162 ft seated square); lots of 162 ft grown breadth-first from the anchor (the field's highest margin point, set off it by half a lot), never through a lot the field's outline crosses, clear of the water and the pond at 10 of 17 and 20 of 29 lots tried (p 0.59 and 0.69, 0.69 taken at 20), the refused ones crossed by the outline 3 and 3 and by a water 4 and 6, none by the pond (0.15 and 0.30 a house at 20), no lot seated inside the field on either; the anchor's own lot crossed by the brook at the intake on both rolls - refused but grown through, never by the outline (were the outline to cross it, the walk starts from the next lot off the field against the fall); each house's ground record 11.5 and 11.45 keys, of them the parts drawn: the house, the yard, 2 beds, 4 fixtures, a byre at 4 of 10 and 7 of 20, a storehouse or shed at 1 of 10 and 3 of 20 (0.35 and 0.15 a household at 20), the rest of its keys the layout's turn, boxes and notes; retirement houses 5 and 11 (0.55 a household); access corridors 22 and 51 (2.55 a household at 20), 2 points each; the way in 4 points; the typical densities (`items.md`, rubric S8): water segments 3.7 and the field's outline segments 1.8 a crossed 64 ft cell.

## The algorithm

    the lots: squares of 162 ft on a lattice set on the anchor and the axis, grown breadth-first from the anchor's lot: a lot
        popped (1) and its 4 neighbors pushed once each (4), the cluster's shape a stretch of the lattice's metric; each lot's box
        asked of the water index's cells it overlaps (each cell 1, each segment in a crossed cell 1) and of the belt's band (1);
        a lot the field's outline crosses is refused and not grown through, so the outline walls the field's inside off - a lot
        inside the field is never reached and needs no inside test - and its test stops at the first cell holding an outline
        segment; a lot a water crosses is refused but grown through, and only after all its cells are read, so that no outline
        segment in a cell not yet read is missed; the first clear lots taken, one a household
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
| the lot's search (water index cells examined) | per item | 33 | 1 / 0.69 = 1.45 lots tried a house at 20 (S8, 1/p), one clear, 0.15 refused by the outline and 0.30 by a water (measured): the clear lot's 12.5 cells read, its pop and 4 pushes (5) and the band (1), the field's outline in the cells it crosses - the third of the lots facing the field, about 3 crossed cells at the mean 1.8 (1.8) - and the water in its border cells, the third of the lots near a ditch or the brook, about 2 crossed cells at the mean 3.7 (2.5): 22.8; a lot the outline crosses stops at its first outline cell, about half its cells and the segments there (9), with its pop (1): 0.15 x 10 = 1.5; a lot a water crosses reads all 12.5 cells, the water's segments in its about 3 crossed cells at the mean 3.7 (11), its pop and pushes (5): 28.5, 0.30 x 28.5 = 8.6; 32.9, rounded to 33 | a cluster pressed against the field and the brook |
| the parts (registry cells written) | per item | 43 | the house, the yard, 2 beds and 4 fixtures (8), a byre (0.35), a storehouse or shed (0.15) and a retirement house (0.55): 9.05 parts, each its box, turned, written and filed in the cells its box overlaps, about 1.67 on average - the house (1 + 46/64)(1 + 28/64) = 2.5, the 5 ft coop 1.2 (4.67): 42.3, rounded up to 43 | always the layout's parts |
| the rolls, the way in and the corridors (registry cells written) | per item | 22 | the kind, the wealth, the jitter and the quarter turn (4); the way in's 4 points written (4) and its 3 legs filed in about 1.5 cells each (4.5); 2.55 corridors, each 2 points written and its leg filed (3.5): 8.9; 21.4, rounded to 22 | always |
| slack | per item | 1.15 | on the lot's search alone (the 33): the same count at 10, from its 0.3 outline and 0.4 water refusals a house, is 22.8 + 3 + 11.4 = 37.2, 13% above the 33 taken | not applicable |

So: houses x (33 x 1.15 + 43 + 22).

- pruning: the lots are grown breadth-first from the anchor and the search stops at the household's count, so it touches 1.45 lots a house, never the ground's whole lattice.

## Totals

- at 20: 20 x (33 x 1.15 + 43 + 22) = 2059
- at 40: 40 x (33 x 1.15 + 43 + 22) = 4118
- at 80: 80 x (33 x 1.15 + 43 + 22) = 8236

## Growth

Linear, an exponent of 1.0: each house costs the same at every size, its lot asked only of its own cells.

## Earlier findings

- verdict-1, finding 1: fixed - the slack 1.05, from the clear lots' measured 0.83 to 0.87; the lot's search per house one clear lot and 0.18 refused, 18
- verdict-1, finding 2: fixed - the view dropped; the lot asks the water index and the belt's band, both in the Reads
- verdict-1, finding 3: fixed - a clear lot on the field's margin reads the outline's segments in the cells it crosses, the third of the lots facing the field (1.8)
- verdict-1, finding 4: fixed - the Bounds' 11.45 are the ground record's keys; the parts drawn are 9.05, the storehouse among them as the 0.15 storehouse or shed
- verdict-1, finding 5: fixed - the way in's legs and the corridors filed in the registry (22)

- verdict-2, finding 1: fixed - the lots grown breadth-first from the anchor, never through a lot the outline crosses, so a lot inside the field is never reached (0 on either reference roll); p re-measured from the anchor, 0.59 and 0.69
- verdict-2, finding 2: fixed - a part's registry overlap 1.67 cells (43)
- verdict-2, finding 3: fixed - a clear lot's border cells read the water near a ditch or the brook, the third of the lots at 2 crossed cells (2.5)
- verdict-2, finding 4: fixed - the slack from the measured spread of the lots tried, 1.7 at 10 and 1.45 at 20: 1.15

- verdict-3, finding 1: fixed - a lot a water crosses reads all its cells before it is grown through (28.5), a lot the outline crosses stops at its first outline cell (10), each at its measured share of the refusals, 0.15 and 0.30 a house

## Cheaper algorithms considered

- sweep: not used - the lots are taken in ring order, the first clear ones kept
- grid or spatial index: used - the water index for each lot's box, the registry for filing the parts
- priority queue: not used - a breadth-first queue over the lattice gives the lots in about distance order, each pushed once
- incremental update: used - the lots are disjoint on the lattice, so a seated house never re-tests a neighbor's ground; the outline's wall is found by the lots' own tests, never a separate inside test
- memoizing what a scan does not change: used - the layout's part boxes are the form's own, turned once a house
