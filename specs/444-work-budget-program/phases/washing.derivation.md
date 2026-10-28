# Derivation - washing (feature 444)

## Contract

- Reads: the households and their houses; the waters that pass them - the brook, the drawn channels, the field ditches and the pond's edge - and the farm channels (`farm_channels`); the registry of what stands, every way, crossing and building among it.
- Writes: the washing places (`washing_places`), each a footing 4 by 6 ft (`WASHING_FT`); `meta.washing_form`, `meta.washing_places` and `meta.washing_no_seat`.
- Keeps: the form rolled from the seed, the one-at-each-house form only where a farm channel runs to the houses (0065); on the shared form each household washes at its nearest water within 120 ft (`PASS_REACH_FT`, a GUESS), the households of one bank of one water in their order along it, one footing for every 4 (`HOUSEHOLDS_PER_WASHING`, a GUESS from 0065), at the bank point nearest their middle household, on their side, the first of 9 shifts along the bank (0, 8, -8 to 32, -32 ft, `BANK_SHIFTS_FT`) the registry admits, a group with no seat counted; on the other form a step at the end of each farm's channel, slid at most 16 ft (the first five shifts); set last of the ground's features, each seat asked of every way, bridge and building standing (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): households 10 and 20; the waters' segments 428 and 574 (x1.34: 574 at 20, 770 at 40, 1,031 at 80); at most 46 and 48 water segments in a house's 3 by 3 cells of 120 ft (48 taken); washing places 1 and 3, at most one a household on either form; at most 29 standing things in one 64 ft cell about the houses (measured for the sties, 21 and 29); 1 ft a pixel at the hamlet scale.

## The algorithm

    index the waters' segments in 120 ft cells, once
    the form: rolled; the each-house form only where farm channels run to the houses
    shared form:
        each household: its nearest water segment within 120 ft, from its 3 by 3 cells; its water, its bank side and its
            place along the water (the projection on its segment)
        the households grouped by water and bank and sorted along it (one sort of the households)
        each group, one footing for every 4: the bank point nearest the middle household (its projection), then the 9 shifts
            along the bank in order, each the footing's box against the registry's things in its cells; the first admitted
            drawn, or the group counted with no seat
    each-house form: each farm's channel end, then the first five shifts, each against the registry as above

## Indexes

- water index: cells of 120 ft (the reach, so a household's waters within it lie in its 3 by 3 cells); densest 48 water segments in a 3 by 3 block (measured at 10 and 20, 46 and 48, the ceiling taken), from a smallest side of 120 ft
- registry: cells of 64 ft; densest 29 standing things a cell (measured at 10 and 20 about the houses, the ceiling taken), from a smallest side of 64 ft against the footing's box, 6 ft, so a seat lies in at most 2 by 2 cells

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the households, each seated on its water | 80 households |
| the nearest water (water index cells examined) | per item | 58 | its 3 by 3 cells of 120 ft (9), their at most 48 segments (48), and its projection on the nearest (1) | the densest block |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the order | over the run | 100 at 20, 240 at 40, 560 at 80 | the households sorted along their waters, log2 of the households rounded up each | 80 households |
| the footing seats (registry cells examined) | over the run | 1089 a footing | at most one footing a household (20 at 20, 40 at 40, 80 at 80), on either form; each at most 9 shifts, each the box's 2 by 2 cells with their at most 29 things (4 x 30) and its bank side (1), 121 | every shift refused but the last |
| the drawing (registry cells written) | over the run | 100 at 20, 200 at 40, 400 at 80 | each footing recorded (1) and filed in at most 4 cells (4) | a footing a household |
| the water index (cells written) | once | 1,722 at 20, 2,310 at 40, 3,093 at 80 | each segment filed in at most 3 cells of 120 ft (the longest, 222 ft, crosses at most 3) | 80 households |
| the form | once | 1 | the roll | always 1 |

So: households x 58 x 1, plus the order, the footings x 1089, the drawing, the water index and the form.

## Totals

- at 20: 20 x 58 x 1 + 100 + 20 x 1089 + 100 + 1722 + 1 = 24863
- at 40: 40 x 58 x 1 + 240 + 40 x 1089 + 200 + 2310 + 1 = 48631
- at 80: 80 x 58 x 1 + 560 + 80 x 1089 + 400 + 3093 + 1 = 95814

## Cheaper algorithms considered

- sweep: used - the households of a bank are taken in their order along it, one sort
- grid or spatial index: used - the water index for each household's nearest water, the registry for each seat
- priority queue: not used - the shifts are taken in their fixed order, not ranked
- incremental update: used - each footing is filed as it is drawn, for the next group's seats
- memoizing what a scan does not change: used - each household's water and its place along it, found once
