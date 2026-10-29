# Derivation - crossings (feature 444)

## Contract

- Reads: every way as laid (the connector, the web's lanes, the households' ways; `lanes`); every watercourse (the brook, the drawn channels, the field ditches; on a polder its perimeter dike and toe collector); the registry of what stands; the field's form (a comb or a polder).
- Writes: a deck (`bridges`) at every crossing of a way and water, square to the water; plank footbridges along the long field ditches, one every 300 ft on a comb and 320 ft on a polder (a GUESS, `channel_footbridges`); a sluice gate at every cut of a polder's perimeter dike (`dike_gates`, 0019); the polder's crossing caps on the settlement-side toe collector (a GUESS).
- Keeps: every crossing decked, square (0084; the `roads_bridge_water` check); set after every way and every watercourse, so no crossing is left unbridged; each plank asked against what stands before it is laid (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the ways' length 4,703 and 8,917 ft (x1.9: 8,917 at 20, 16,943 at 40, 32,191 at 80) and their segments 24 and 144, 2.4 and 7.2 a household - at most 8 a household taken (160 at 20, 320 at 40, 640 at 80): a household's way is at most 3 legs (the homesteads' budget) and the web's lanes are pulled taut between the plots they serve, so the segments grow with the households, not with today's output (x6 a doubling from 10 to 20 is the reference map's shape at 20, not a rate); the waters' segments 428 and 574 (x1.34: 574 at 20, 770 at 40, 1,031 at 80) and length 12,344 and 19,311 ft (x1.56: 19,311 at 20, 30,126 at 40, 46,996 at 80); at most 26 and 18 water segments in one 64 ft cell (26 taken); the field ditches' length 3,430 and 5,885 ft (x1.72: 5,885 at 20, 10,123 at 40, 17,411 at 80) in 9 and 12 ditches (x1.33: 12 at 20, 16 at 40, 22 at 80); the bridges 6 and 9 (x1.5: 9 at 20, 14 at 40, 21 at 80); at most 21 and 29 standing things in one 64 ft cell about the houses (x1.38: 29 at 20, 40 at 40, 55 at 80); at most 12 outline segments in one 64 ft cell (the field's, the polder's dike its outline); 1 ft a pixel at the hamlet scale.

## The algorithm

    index the waters' segments in 64 ft cells, once
    walk each way through the water index's cells: each water segment in a cell tested against the way's leg; each crossing
        decked, square to the water, recorded and filed
    on a polder: the same walk through the field's outline index (its perimeter dike): each cut gets its sluice gate; each
        crossing of the toe collector its cap (in the water walk, the collector a water)
    along each field ditch, a spot every 300 ft (320 on a polder): its plank, unless a deck stands within the spacing, tested
        against the registry's things in its cells (S4); laid, recorded and filed

## Indexes

- water index: cells of 64 ft; densest 26 water segments a cell (measured at 10 and 20, 26 and 18, the ceiling taken), from a smallest side of 64 ft
- outline index: cells of 64 ft (the field's); densest 12 outline segments a cell, from a smallest side of 64 ft
- registry: cells of 64 ft; densest 29 standing things a cell at 20, at its measured rate (29 at 20, 40 at 40, 55 at 80), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 9 at 20, 14 at 40, 21 at 80 | the decks, one a crossing | 80 households |
| the deck (registry cells written) | per item | 5 | recorded (1) and filed in at most 4 cells (4) | always 5 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the water index (cells written) | once | 2,149 at 20, 2,976 at 40, 4,132 at 80 | each water segment walked through the cells it crosses: the waters' length at root 2 over 64 ft, plus 3 a segment (a grid walk crosses one cell more than the grid lines it crosses each way) | 80 households |
| the ways' walk (water index cells examined) | over the run | 18,306 at 20, 36,045 at 40, 71,064 at 80 | the ways' cells, their length at root 2 over 64 ft plus 3 a segment (678 at 20, 1,335 at 40, 2,632 at 80), each read with its at most 26 water segments tested against the leg (27) | every way through the densest water |
| the dike's cuts (outline index cells examined) | over the run | 8,814 at 20, 17,355 at 40, 34,216 at 80 | on a polder, the ways' same cells, each read with its at most 12 dike segments (13) | a polder |
| the plank spots (registry cells examined) | over the run | 4,128 at 20, 8,650 at 40, 18,873 at 80 | the spots, each ditch's length over 300 ft rounded up plus one a ditch, each its point along the ditch (1) (32 at 20, 50 at 40, 81 at 80); each: the decks within the spacing read from its 2 by 2 cells (8), and its box's at most 2 by 2 cells with their things and the cell (120 at 20, 164 at 40, 224 at 80) | every spot planked |
| the planks laid (registry cells written) | over the run | 160 at 20, 250 at 40, 405 at 80 | each plank recorded (1) and filed in at most 4 cells (4) | every spot planked |

So: the decks x 5 x 1, plus the water index, the ways' walk, the dike's cuts, the plank spots and the planks laid.

## Totals

- at 20: 9 x 5 x 1 + 2149 + 18306 + 8814 + 4128 + 160 = 33602
- at 40: 14 x 5 x 1 + 2976 + 36045 + 17355 + 8650 + 250 = 65346
- at 80: 21 x 5 x 1 + 4132 + 71064 + 34216 + 18873 + 405 = 128795

## Cheaper algorithms considered

- sweep: not used - the ways and the waters are walked through a shared grid, which finds every crossing once without a sort
- grid or spatial index: used - the water index, the field's outline index and the registry
- priority queue: not used - nothing is ranked; every crossing is decked
- incremental update: used - each deck and plank is filed as it is laid, so a plank sees the decks standing
- memoizing what a scan does not change: used - the water index is built once for every way
