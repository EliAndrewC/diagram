# Derivation - washing, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan's washing form (`washing_form`) and how the farms take their water (`farm_water`); the seated lots' lattice and the houses; the brook, the ditches and the farm channels in the water index; the registry of what stands.
- Writes: the settlement's washing places at the water's edge - on the shared form a footing of steps down the bank, one for every few households, filed in the registry; on the form at each house, a step where each farm's channel ends.
- Keeps: a shared washing place on the bank of a stream, ditch or farm channel within about 120 ft of the houses it serves, at the bank point nearest the middle of those households and on their side of the water; moved along the bank up to about 32 ft either way where a lane, a bridge or a building takes that spot; a group with no spot left keeps none; one for every few households (0065, each a GUESS); the form at each house only where the farms take their water by channel (0065); the footing about 4 ft wide (0065, a GUESS).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the shared form, the farms watered by well, on both, so the form at each house is not drawn on them; washing places 1 and 3, each a 4 by 6 ft footing; the households a place serves, "every few", a knob taken at 7 (20 households over the 3 places at 20, a GUESS); the typical densities (`items.md`, rubric S8): water segments 3.7 a crossed 64 ft cell, things of every kind 5.5 a 64 ft cell within 3 cells of a house.

## The algorithm

    the form and the farms' water read (2); on the shared form: the seated lots cut into ceil(households / 7) groups by halving
        the longer side at its median (each lot once a level)
    for each group: its lots read and their mean taken (8); the water index's cells within 120 ft of the mean read, 5 by 5 of
        64 ft (each cell 1, each segment in a crossed cell 1), the nearest bank point on the group's side taken (2); none within
        120 ft: the group keeps none; else the footing's box asked of the registry's cells it overlaps (each cell 1, each thing
        1), and taken by a lane, a bridge or a building, stepped along the bank 4 ft at a time up to 32 ft either way; written (1)
        and filed (1 a cell)

## Indexes

- water index: cells of 64 ft, each segment filed in every cell it crosses; the 120 ft reach round a group's mean 5 by 5 cells, the mean 3.7 segments a crossed cell (`items.md`, rubric S8), from a smallest side of 64 ft
- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a 4 by 6 ft footing overlapping (1 + 4/64)(1 + 6/64) = 1.16 cells at the mean 5.5 things a cell near the houses, from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 3 at 20, 6 at 40, 12 at 80 | the groups, ceil(households / 7) | the households over seven |
| the group | per item | 8 | its about 7 lots read and their mean (8) | always 8 |
| the water's reach (water index cells examined) | per item | 40 | the 25 cells within 120 ft read (25) and the segments in the about 4 of them a water crosses near the houses at the mean 3.7 (15) | a cluster among ditches |
| the bank point and the footing (registry cells examined) | per item | 12 | the nearest bank point (2); the footing's box in 1.16 cells at the mean 5.5 things and the cell (7.5); written (1) and filed (1.2): 11.7, rounded up | always one seat at the typical case |
| slack | per item | 2 | on the footing's seat alone, the steps along the bank where a lane, a bridge or a building takes the first spot, up to 16 of them, their share unmeasured on the reference rolls, at most 2 (S7) | a bank lined with lanes and bridges |
| the cuts and the form | over the run | 22 at 20, 82 at 40, 242 at 80 | the form and the farms' water read (2), and each lot once a level of the halving, log2 of the groups rounded up (1, 2, 3): 20, 80 and 240 | the shared form on every roll |

So: groups x (8 + 40 + 12 x 2), plus the cuts and the form.

## Totals

- at 20: 3 x (8 + 40 + 12 x 2) + 22 = 238
- at 40: 6 x (8 + 40 + 12 x 2) + 82 = 514
- at 80: 12 x (8 + 40 + 12 x 2) + 242 = 1106

## Growth

From 20 to 80 households the stage grows at an exponent of about 1.11: a group seven households, the cuts n log k.

- pruning: each group asks only the water within 120 ft of its own mean, never every bank of the map

## Cheaper algorithms considered

- sweep: used - the bank stepped along from the nearest point, the first free spot kept
- grid or spatial index: used - the water index for the reach, the registry for the footing
- priority queue: not used - the nearest bank point is a minimum over the few segments within reach
- incremental update: not used - each footing is seated once
- memoizing what a scan does not change: not used - each group reads its own cells once
