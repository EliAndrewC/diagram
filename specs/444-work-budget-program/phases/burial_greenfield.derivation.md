# Derivation - burial, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan's settlement size (a hamlet or a village); the homesteads' lots and their corners; the field's basins; the registry of what stands.
- Writes: where the hamlet's dead lie, into the plan (`hamlet_burial`: the village's ground, drawn nowhere); on the rolls that keep them, a small grave at a corner of some farmsteads' plots (`household_graves`), and a single grave standing in a field.
- Keeps: a hamlet draws no burial ground, its dead lying in the village's (0236: "A hamlet draws no burial ground: its dead lie in the village's"); on about half of hamlet maps some farmsteads keep a small grave of their own at a corner of their plot, and on some paddy maps a single grave stands in a field (0236); each grave asked of what stands before it is drawn (S4).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): `hamlet_burial` the village's ground and `household_graves` false on both; the household graves' roll even odds (0236: "about half"); the share of farmsteads keeping one where they are kept, and the share of paddy maps with a field grave, given by no page ("some"), each a knob taken at a quarter, a GUESS; a grave about 6 ft across; the typical densities (`items.md`, rubric S8): things of every kind 5.5 a 64 ft cell within 3 cells of a house.

## The algorithm

    the settlement's size read and the village's ground written to the plan (2)
    the household graves rolled (1); kept: each farmstead rolled for a grave (1), a kept one at its lot's back corner, its box
        asked of the registry's cells it overlaps (each cell 1, each thing 1), written (1) and filed (1 a cell)
    the field grave rolled (1); kept: a basin's middle taken (1), its box asked as above, written and filed

## Indexes

- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a 6 ft grave's box overlapping (1 + 6/64)^2 = 1.2 cells, at the mean 5.5 things a cell near the houses (`items.md`, rubric S8), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the hamlet's burial, once a map | always 1 |
| the size and the plan's field | per item | 2 | the size read, the village's ground written | always 2 |
| the two rolls | per item | 2 | the household graves' roll and the field grave's | always 2 |
| slack | per item | 1 | every branch is charged at its share, its tests at the mean | not applicable |
| the household graves (registry cells examined) | over the run | 35 at 20, 70 at 40, 140 at 80 | on a keeping roll each farmstead rolled (1) and a quarter of them a grave - its box in 1.2 cells at the mean 5.5 things and the cell (7.8), written (1) and filed (1.2): 10, so 2.5 - 3.5 a farmstead (70, 140, 280); at the keeping rolls' share, one half (S9): 35, 70 and 140 | the graves kept on every roll |
| the field grave (registry cells examined) | over the run | 3 at 20, 3 at 40, 3 at 80 | at a quarter of the rolls (S9): a basin's middle (1), its box in 1.2 cells at the mean 5.5 and the cell (7.8), written and filed (2.2): 11, a quarter rounded up | a field grave on every roll |

So: 1 x (2 + 2) x 1, plus the household graves and the field grave.

## Totals

- at 20: 1 x (2 + 2) x 1 + 35 + 3 = 42
- at 40: 1 x (2 + 2) x 1 + 70 + 3 = 77
- at 80: 1 x (2 + 2) x 1 + 140 + 3 = 147

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.9: the household graves with the farmsteads.

## Cheaper algorithms considered

- sweep: not used - each farmstead is rolled once
- grid or spatial index: used - the registry's cells under each grave's box
- priority queue: not used - nothing is ranked
- incremental update: not used - each grave is seated once
- memoizing what a scan does not change: not used - there is no scan
