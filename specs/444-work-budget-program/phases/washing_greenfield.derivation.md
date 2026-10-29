# Derivation - washing, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan's washing form (`washing_form`) and how the farms take their water (`farm_water`); the seated lots' lattice and the houses; the brook, the ditches and the farm channels in the water index; the registry of what stands.
- Writes: the settlement's washing places at the water's edge - on the shared form a footing of steps down the bank, one for every few households, filed in the registry; on the form at each house, a step where each farm's channel ends.
- Keeps: a shared washing place on the bank of a stream, ditch or farm channel within about 120 ft of the houses it serves, at the bank point nearest the middle of those households and on their side of the water; moved along the bank up to about 32 ft either way where a lane, a bridge or a building takes that spot; a group with no spot left keeps none; one for every few households (0065, each a GUESS); the form at each house only where the farms take their water by channel (0065); the footing about 4 ft wide (0065, a GUESS).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the shared form, the farms watered by well, on both, so the form at each house is not drawn on them; the households within 120 ft of a water 2 of 10 and 3 of 20 (0.15 a household at 20), at 113, 114 and 114, 108, 68 ft; washing places 1 and 3, each a 4 by 6 ft footing - at 20 one for each near household, which stand apart; the footing clear at its nearest bank point for all five, no step along the bank taken; the households a place serves, "every few", a knob taken at 7 (a GUESS), binding only where near households stand together; a 120 ft disk overlapping (pi x 120^2 + 4 x 120 x 64 + 64^2) / 64^2 = 19.5 cells of 64 ft on average, measured at 19.3 a household at both sizes, its cells holding 8.0 and 7.8 water segments a household at 10 and 20 (each cell's segments, the near and the far households alike); a 256 ft coarse count read first would find water in 8 of 10 and 12 of 20 households' reaches and save about 4 reads a household, against about 1,260 to build it at 20 (574 segments, each filed in about 1.2 coarse cells and counted); the typical densities (`items.md`, rubric S8): water segments 3.7 a crossed 64 ft cell, things of every kind 5.5 a 64 ft cell within 3 cells of a house.

## The algorithm

    the form and the farms' water read (2); on the shared form, for each household: the water index's cells round its house read
        ring by ring, nearest first (each cell 1, each segment in a crossed cell 1), stopping at the first ring whose nearest point
        lies past the best bank distance found or past 120 ft - for a house with no water in reach, every cell of the 120 ft disk
    the households with a bank in reach grouped along their banks, up to every few (7) at one place; for each group: the bank
        point nearest its middle on its side taken (2); the footing's box asked of the registry's cells it overlaps (each cell 1,
        each thing 1), and taken by a lane, a bridge or a building, stepped along the bank 4 ft at a time up to 32 ft either way;
        written (1) and filed (1 a cell); a group with no spot left keeps none

## Indexes

- water index: cells of 64 ft, each segment filed in every cell it crosses; the 120 ft disk round a house 19.5 cells on average, the mean 3.7 segments a crossed cell (`items.md`, rubric S8), from a smallest side of 64 ft
- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a 4 by 6 ft footing overlapping (1 + 4/64)(1 + 6/64) = 1.16 cells at the mean 5.5 things a cell near the houses, from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the households, each asked for a bank in reach | the households |
| the water's reach (water index cells examined) | per item | 28 | each household's reach, measured: its 19.3 cells read (19.3) and the 7.8 segments those cells hold tested for their distance (7.8), and the nearest against 120 ft (1): 28.1 | a cluster among ditches |
| the place (registry cells examined) | per item | 1.8 | at the near households' share, 0.15, one place each as measured: the bank point (2), the footing's box in 1.16 cells at the mean 5.5 things and the cell (7.5), written (1) and filed (1.2), no step taken (all five clear at their nearest point): 11.7, rounded to 12, x 0.15 | a bank lined with lanes and bridges |
| slack | per item | 1 | the steps along the bank measured at none on all five places | not applicable |
| the form | once | 2 | the form and the farms' water read | always 2 |

So: households x (28 + 1.8) x 1, plus the form.

- pruning: each household asks only the cells within 120 ft of its own house, nearest first, never every bank of the map

## Totals

- at 20: 20 x (28 + 1.8) x 1 + 2 = 598
- at 40: 40 x (28 + 1.8) x 1 + 2 = 1194
- at 80: 80 x (28 + 1.8) x 1 + 2 = 2386

## Growth

Linear, an exponent of 1.0: each household asks its own 120 ft reach.


## Earlier findings

- verdict-1, finding 1: fixed - the households with water in reach measured, 0.15 a household at 20, and the crossed cells of a near reach about 3 at 3.7
- verdict-1, finding 2: fixed - the cuts dropped; each household asks its own reach, the near ones grouped along their banks
- verdict-1, finding 3: fixed - the steps along the bank measured at none on all five places, slack 1
- verdict-1, finding 4: fixed - the cells read nearest first, stopping at the first ring whose nearest point lies past the best
- verdict-1, finding 5: fixed - the 120 ft disk's mean 19.5 cells, not the 25 of its bounding square

- verdict-2, finding 1: fixed - the segments in each household's reach measured, 7.8 a household at 20, the far households' cells included
- verdict-2, finding 2: fixed - the far households charged their cells' segments, the same measurement
- verdict-2, finding 3: disputed - a coarse 256 ft count would cost about 1,260 to build at 20 against the about 80 reads it saves; its line in the cheaper algorithms says so
- verdict-2, finding 4: fixed - the group's pruning line, left from the earlier version, dropped

## Cheaper algorithms considered

- sweep: used - the bank stepped along from the nearest point, the first free spot kept
- grid or spatial index: used - the water index for the reach, the registry for the footing; a coarse 256 ft count read first is not used - building it, about 1,260 at 20, costs more than the about 80 reads it saves
- priority queue: used - the cells read ring by ring nearest first, stopping once the best bank distance beats the next ring's nearest point
- incremental update: not used - each footing is seated once
- memoizing what a scan does not change: not used - each household reads its own cells once
