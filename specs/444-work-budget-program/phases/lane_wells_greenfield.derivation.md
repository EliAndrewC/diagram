# Derivation - lane_wells, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan's well form (`well_siting`); the lanes as laid, in the ways index; the households in the order their lots were seated; the houses' walls; the registry of what stands.
- Writes: on the lane form, the communal wells on the lanes' verges, each a curb on its apron within reach of the houses it serves, filed in the registry.
- Keeps: on the lane form the wellhead stands on a lane's verge, its curb within about 8 ft of the tread, a dwelling's wall within 80 ft (0196); a well never inside a farmstead, on a yard, a bed or another lane (0196: "Where every verge is a yard, a bed or another lane ... the well takes the other form"); a hamlet draws one or two wells, one more where one would be the nearest for more than ten households, every household within about 760 ft of a well or open water (0196); each seat asked before the well is drawn (S4).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the wells 2 and 2, of the lane form on both; the well form a knob of two forms (0196), taken at even odds where the record gives no share; the wells one to ten households, 2, 4 and 8 at 20, 40 and 80; the verge seats 8 ft apart, 19 ft off a lane's line (half the 14 ft tread, 7, and the apron's half-width, 12, so the curb's edge stands within 8 ft of the tread), within 80 ft of a house's wall: 510 and 1,147, their 24 ft apron clear of what stands at 225 and 423 (p 0.44 and 0.37); walking out from the foot of the leg nearest each block's mean, the seats tried until one is clear and within 80 ft of a block house's wall, 1 for the one block at 10 and 1 and 37 for the two at 20 (a mean of 13 a well, the verges by one block's houses lined with yards and beds), and the lane-crossed cells among the 3 by 3 round each block's mean 7, 4 and 5 (5.3); the typical densities (`items.md`, rubric S8): ways' legs 1.94 a crossed 64 ft cell, things of every kind 5.5 a 64 ft cell within 3 cells of a house.

## The algorithm

    the well form read (1); on the lane form: the households in the order their lots were seated, ten to a well; for each well,
        its ten houses read (10) and their mean taken (2); the nearest lane leg to the mean from the ways index - the mean's cell
        and its ring read (9 cells, each leg in a crossed cell 1) - and the leg's foot point (2); the verge seats walked out
        from the foot both ways at 8 ft steps; the ten houses ranked once by their distance to the foot (10 log 10, 33); each
        seat its apron's box asked of the registry's cells it overlaps (each cell 1, each thing 1) and the ranked houses' walls
        until one lies within 80 ft (about 1.5), until a seat is clear; written (1) and filed (1 a cell)
    each household's distance to its block's well checked against the reach (1)

## Indexes

- ways index: cells of 64 ft, each leg filed in every cell it crosses; the mean 1.94 legs a crossed cell (`items.md`, rubric S8), a point's cell and ring 3 by 3 cells, from a smallest side of 64 ft
- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a 24 ft apron overlapping (1 + 24/64)^2 = 1.9 cells at the mean 5.5 things a cell near the houses (`items.md`, rubric S8), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 2 at 20, 4 at 40, 8 at 80 | the wells, one to ten households | the households over ten |
| the block and the leg (ways index cells examined) | per item | 76 | the ten houses read (10), their mean (2), the mean's 9 cells read (9) and the legs in the 5.3 crossed among them, measured, at 1.94 (10.3), the foot point (2), and the ten ranked by their distance to it (10 + 33): 76.3, rounded to 76 | the typical cluster |
| the verge seats (registry cells examined) | per item | 14 | each seat its apron in 1.9 cells at the mean 5.5 things and the cell (12.4) and the ranked houses' walls until one lies within 80 ft (1.5): 13.9, rounded to 14 | a lane lined with yards and beds |
| the seats tried | per item | 13 | measured walking out from each block's foot on the reference rolls: 1, 1 and 37, a mean of 13 a well - higher than 1 / 0.37 = 2.7, because a block's own verges are its yards and beds | a lane lined with yards and beds |
| the writes | per item | 3 | the well written (1) and filed in its 1.9 cells (2) | always 3 |
| slack | per item | 1 | the seats tried is the measured mean over the three blocks, its spread inside it | not applicable |
| the reach (households read) | over the run | 20 at 20, 40 at 40, 80 at 80 | each household's distance to its block's well (1) | the households |

So: at the lane form's share of the rolls, one half (S9): (wells x (76 + 14 x 13 x 1 + 3) + the reach) / 2.

## Totals

- at 20: (2 x (76 + 14 x 13 x 1 + 3) + 20) / 2 = 271
- at 40: (4 x (76 + 14 x 13 x 1 + 3) + 40) / 2 = 542
- at 80: (8 x (76 + 14 x 13 x 1 + 3) + 80) / 2 = 1084

## Growth

Linear, an exponent of 1.0: a well ten households, each its own block's seat.

- pruning: a well's lane leg is read from its own block's mean through the ways index, and its seats walked from the leg's foot until one is clear, never every verge of the network

## Earlier findings

- verdict-1, finding 1: fixed - the lane-crossed cells among the 3 by 3 measured, 7, 4 and 5 (5.3), at 1.94 (10.3)
- verdict-1, finding 2: fixed - the ten houses ranked once by their distance to the foot, each seat stopping at the first wall within 80 ft (1.5)
- verdict-1, finding 3: fixed - the seats tried the measured mean over the blocks, 13, slack 1

## Cheaper algorithms considered

- sweep: used - the verge walked out from the leg's foot at 8 ft steps, the first clear seat kept
- grid or spatial index: used - the ways index for the nearest leg, the registry for each apron
- priority queue: not used - the block's ten houses are the seating order's, read in order
- incremental update: not used - each well is seated once
- memoizing what a scan does not change: used - the ten houses are read and ranked once a well, each seat asking them in that order
