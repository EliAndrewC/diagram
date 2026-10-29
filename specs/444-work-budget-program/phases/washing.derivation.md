# Derivation - washing (feature 444)

## Contract

- Reads: the households and their houses; the waters that pass them - the brook, the drawn channels, the field ditches and the pond's edge - and the farm channels (`farm_channels`); the registry of what stands, every way, crossing and building among it.
- Writes: the washing places (`washing_places`), each a footing 4 by 6 ft (`WASHING_FT`); `meta.washing_form`, `meta.washing_places` and `meta.washing_no_seat`.
- Keeps: the form rolled from the seed, the one-at-each-house form only where a farm channel runs to the houses (0065); on the shared form each household washes at its nearest water within 120 ft (`PASS_REACH_FT`, a GUESS), the households of one bank of one water in their order along it, one footing for every 4 (`HOUSEHOLDS_PER_WASHING`, a GUESS from 0065), at the bank point nearest their middle household, on their side, the first of 9 shifts along the bank (0, 8, -8 to 32, -32 ft, `BANK_SHIFTS_FT`) the registry admits, a group with no seat counted; on the other form a step at the end of each farm's channel, slid at most 16 ft (the first five shifts); set last of the ground's features, each seat asked of every way, bridge and building standing (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): households 10 and 20; the waters' segments 428 and 574 (x1.34: 574 at 20, 770 at 40, 1,032 at 80) and their length 12,344 and 19,311 ft (x1.56: 19,311 at 20, 30,126 at 40, 46,996 at 80); at most 46 and 48 water segments in a house's 3 by 3 cells of 120 ft (x1.04: 48 at 20, 50 at 40, 52 at 80); washing places 1 and 3, at most one a household on either form; at most 21 and 29 standing things in one 64 ft cell within 3 cells (192 ft) of a house - the 120 ft reach and the 32 ft shift inside it - each thing counted once a cell it touches, a way's segment as one (x1.38: 29 at 20, 40 at 40, 55 at 80), measured on the finished map, so every thing standing when washing runs, last of the ground's features, is in it; 1 ft a pixel at the hamlet scale. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell; each held flat past 20, a mean over occupied cells not rising with the households as the densest cell does. The footings (FR-014, measured 2026-10-28): the washing places the reference rolls draw, 1 and 3 at 10 and 20, on the shared form (`meta.washing_form` shared on the reference), grown at that rate, x3 a doubling, and capped at one for every 4 households of a bank plus a bank's remainder: 3, 9 and 23.

## The algorithm

    index the waters' segments in 120 ft cells, once
    the form: rolled; the each-house form only where farm channels run to the houses
    shared form:
        each household: its nearest water segment within 120 ft, from its 3 by 3 cells; its water, its bank side and its
            place along the water (the projection on its segment)
        the households grouped by water and bank and sorted along it (one sort of the households)
        each group, one footing for every 4: the bank point nearest the middle household (its projection), the 9 shifts along
            the bank (each an offset along the found segment's direction from the projection, a GUESS for "moved along the bank"
            within 32 ft), all inside one strip about 70 by 6 ft: its at most 6 cells gathered once, each thing in them
            projected as the one interval of shifts it blocks (a convex thing against a box sliding along a line), marked in a
            9-slot array; the first open shift in the contract's order drawn, or the group counted with no seat
    each-house form: each farm's channel end, then the first five shifts, each against the registry as above

## Indexes

- water index: cells of 120 ft (the reach, so a household's waters within it lie in its 3 by 3 cells); densest 48 water segments in a 3 by 3 block at 20, at its measured rate (48 at 20, 50 at 40, 52 at 80), from a smallest side of 120 ft
- registry: cells of 64 ft; densest 29 standing things a cell at 20, at its measured rate (29 at 20, 40 at 40, 55 at 80), from a smallest side of 64 ft against the footing's box, 6 ft, so a seat lies in at most 2 by 2 cells

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the households, each seated on its water | 80 households |
| the nearest water (water index cells examined, a household) | per item | 22 | its 3 by 3 cells of 120 ft (9), the about 3 a water crosses each with the mean 4 segments (12), and its projection (1) | the typical household |
| slack | per item | 2 | what varies around the typical case (S8): the spread around the mean footings and their shifts | a crowded bank |
| the order | over the run | 100 at 20, 240 at 40, 560 at 80 | the households sorted along their waters, log2 of the households rounded up each | 80 households |
| the footing seats (registry cells examined, a footing) | over the run | 48 a footing | the footings drawn, measured (3 at 20, 9 at 40, 23 at 80); each its strip, 70 by 6 ft at a random angle, in about 2.6 cells read with the mean 3.3 things and the cell (12), each thing projected and marked (2 x 2.6 x 3.3, 18), the 9 slots set and walked (18) | the typical bank |
| the drawing (registry cells written) | over the run | 3 x 3 at 20, 9 x 3 at 40, 23 x 3 at 80 | each footing recorded (1) and filed in its about 1.2 cells (2) | the typical bank |
| the water index (cells written) | once | 780 at 20, 1,090 at 40, 1,530 at 80 | each segment walked through the cells it crosses at a random angle: its length x (4/pi) over 120 ft, plus 1 a segment | 80 households |
| the form | once | 1 | the roll | always 1 |

So: (households x 22 + the order + the footings x (48 + 3)) x 2, plus the water index and the form.

## Totals

- at 20: (20 x 22 + 100 + 3 x 48 + 3 x 3) x 2 + 780 + 1 = 2167
- at 40: (40 x 22 + 240 + 9 x 48 + 9 x 3) x 2 + 1090 + 1 = 4249
- at 80: (80 x 22 + 560 + 23 x 48 + 23 x 3) x 2 + 1530 + 1 = 8517

## Growth

From 20 to 80 households the stage grows at an exponent within 1.15: the households' nearest waters and their order grow with the households, the footings with the banks the cluster meets.


## Earlier findings

- verdict-3, finding 1: fixed - the footings at the measured count drawn on the shared form (the reference's), grown at its rate and capped by the banks; the strip and the water index at their mean cells; the registry at the mean 3.3 (flat, measured falling); the each-house form not rolled on the reference; the Growth section restated
- verdict-1, finding 1: fixed - the water index walks each segment through the cells it crosses, the waters' length at its diagonal over 120 ft plus 3 a segment, from the measured length; no longest-segment figure
- verdict-1, finding 2: fixed - a shift is an offset along the found segment's direction, 1, labeled a GUESS for "moved along the bank"
- verdict-1, finding 3: fixed - the registry's density is measured on the finished map within 192 ft of a house (the reach and the shift), counting each thing once a cell, and grown at its measured rate
- verdict-1, finding 4: fixed - the water segments near a house grow at their measured rate
- verdict-2, finding 1: fixed - the growth past 1.15 is stated: the per-footing neighbor factor is the measured registry density, rising at its measured rate, with no geometric ceiling; the Growth section says so
- verdict-2, finding 2: fixed - the 9 shifts are one sweep of the footing's strip, its at most 6 cells read once and each thing projected as one interval in a 9-slot array
- verdict-2, finding 3: fixed - the footing row's figure is per footing, and the totals multiply it by the households

- FR-014 re-score: each factor at the typical case (rubric S8): one footing for every 4 households of a bank, not one a household; the mean densities of `items.md`; slack 2 (ask:444-budget-standard; the accept was ask:444-T03-washing-round-3)

## Cheaper algorithms considered

- sweep: used - the households of a bank are taken in their order along it, one sort; and the 9 shifts of a footing are one interval sweep of its strip
- grid or spatial index: used - the water index for each household's nearest water, the registry for each footing's strip
- priority queue: not used - the shifts are taken in their fixed order, not ranked
- incremental update: used - each footing is filed as it is drawn, for the next group's seats
- memoizing what a scan does not change: used - each household's water and its place along it, found once, and each footing's strip read once for all 9 shifts
