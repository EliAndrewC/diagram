# Derivation - crossings (feature 444)

## Contract

- Reads: every way as laid (the connector, the web's lanes, the households' ways; `lanes`); every watercourse (the brook, the drawn channels, the field ditches; on a polder its perimeter dike and toe collector); the registry of what stands; the field's form (a comb or a polder).
- Writes: a deck (`bridges`) at every crossing of a way and water, square to the water; plank footbridges along the long field ditches, one every 300 ft on a comb and 320 ft on a polder (a GUESS, `channel_footbridges`); a sluice gate at every cut of a polder's perimeter dike (`dike_gates`, 0019); the polder's crossing caps on the settlement-side toe collector (a GUESS).
- Keeps: every crossing decked, square (0084; the `roads_bridge_water` check); set after every way and every watercourse, so no crossing is left unbridged; each plank asked against what stands before it is laid (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the ways' length 4,703 and 8,917 ft (x1.9: 8,917 at 20, 16,943 at 40, 32,191 at 80) and their segments 24 and 144, 2.4 and 7.2 a household - at most 8 a household taken (160 at 20, 320 at 40, 640 at 80): a household's way is at most 3 legs (the homesteads' budget) and the web's lanes are pulled taut between the plots they serve, so the segments grow with the households, not with today's output (x6 a doubling from 10 to 20 is the reference map's shape at 20, not a rate); the waters' segments 428 and 574 (x1.34: 574 at 20, 770 at 40, 1,031 at 80) and length 12,344 and 19,311 ft (x1.56: 19,311 at 20, 30,126 at 40, 46,996 at 80); at most 26 and 18 water segments in one 64 ft cell (26 taken); the field ditches' length 3,430 and 5,885 ft (x1.72: 5,885 at 20, 10,123 at 40, 17,411 at 80) in 9 and 12 ditches (x1.33: 12 at 20, 16 at 40, 22 at 80); the bridges 6 and 9 (x1.5: 9 at 20, 14 at 40, 21 at 80); at most 21 and 29 standing things in one 64 ft cell about the houses (29 taken, a measured Bound the audit at 40 and 80 confirms); a deck 10 by 4 ft and a plank no wider than a ditch, each under 64 ft, so in at most 2 by 2 cells; the perimeter dike is the field's outline, not among the waters' segments (the brook, the channels and the ditches); at most 12 outline segments in one 64 ft cell (the field's, the polder's dike its outline); 1 ft a pixel at the hamlet scale.

## The algorithm

    index the waters' segments in 64 ft cells, once
    walk each way through the water index's cells: each water segment in a cell tested against the way's leg, and on a polder the
        outline index's dike segments in the same cell; each crossing
        decked, square to the water, recorded and filed, and a deck on a ditch also filed on that ditch by its distance along it
        (a sorted insert); each cut of the dike its sluice gate, recorded and filed; a crossing of the toe collector is a deck
    along each field ditch, a spot every 300 ft (320 on a polder), floor of its length over 300 plus 1: its plank, unless a
        deck stands within the spacing (a binary search of the ditch's decks by distance along it), tested
        against the registry's things in its cells (S4); laid, recorded and filed

## Indexes

- water index: cells of 64 ft; densest 26 water segments a cell (measured at 10 and 20, 26 and 18, the ceiling taken), from a smallest side of 64 ft
- outline index: cells of 64 ft (the field's); densest 12 outline segments a cell, from a smallest side of 64 ft
- registry: cells of 64 ft; densest 29 standing things a cell (measured at 10 and 20, 21 and 29, the ceiling taken), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 9 at 20, 14 at 40, 21 at 80 | the decks, one a crossing, the toe collector's caps among them | 80 households |
| the deck (registry cells written) | per item | 5 | recorded (1) and filed in at most 4 cells, a deck 10 by 4 ft (4) | always 5 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the water index (cells written) | once | 2,149 at 20, 2,976 at 40, 4,132 at 80 | each water segment walked through the cells it crosses: the waters' length at root 2 over 64 ft, plus 3 a segment (a grid walk crosses one cell more than the grid lines it crosses each way) | 80 households |
| the ways' walk (water index cells examined) | over the run | 18,306 at 20, 36,045 at 40, 71,064 at 80 | the ways' cells, their length at root 2 over 64 ft plus 3 a segment (678 at 20, 1,335 at 40, 2,632 at 80), each read with its at most 26 water segments tested against the leg (27) | every way through the densest water |
| the dike's cuts (outline index cells examined) | over the run | 8,136 at 20, 16,020 at 40, 31,584 at 80 | on a polder, in the ways' walk's same cell visit, its at most 12 dike segments tested (12) | a polder |
| the sluice gates (registry cells written) | over the run | 800 at 20, 1,600 at 40, 3,200 at 80 | at most one cut a way's leg (160 at 20, 320 at 40, 640 at 80), each gate recorded (1) and filed in at most 4 cells (4) | a polder, every leg cutting the dike |
| the ditch decks (sorted inserts) | over the run | 45 at 20, 70 at 40, 126 at 80 | each deck on a ditch filed by its distance along it, 1 and log2 of the decks rounded up | every deck on a ditch |
| the plank spots (registry cells examined) | over the run | 4,032 at 20, 6,300 at 40, 10,287 at 80 | the spots, floor of each ditch's length over 300 ft plus 1, summed at most the ditches' length over 300 ft plus the ditches, rounded up (32 at 20, 50 at 40, 81 at 80); each its point along the ditch (1), the decks within the spacing by a binary search of its ditch's decks (1 and log2 of the decks rounded up), and its plank's box's at most 2 by 2 cells with their 29 things and the cell (120) | every spot planked |
| the planks laid (registry cells written) | over the run | 160 at 20, 250 at 40, 405 at 80 | each plank recorded (1) and filed in at most 4 cells (4) | every spot planked |

So: the decks x 5 x 1, plus the water index, the ways' walk, the dike's cuts, the sluice gates, the ditch decks, the plank spots and the planks laid.

## Totals

- at 20: 9 x 5 x 1 + 2149 + 18306 + 8136 + 800 + 45 + 4032 + 160 = 33673
- at 40: 14 x 5 x 1 + 2976 + 36045 + 16020 + 1600 + 70 + 6300 + 250 = 63331
- at 80: 21 x 5 x 1 + 4132 + 71064 + 31584 + 3200 + 126 + 10287 + 405 = 120903

## Earlier findings

- verdict-1, finding 1: fixed - the decks within a plank's spacing are found by a binary search of its ditch's decks by distance along it, each deck on a ditch filed so as it is laid; no registry reach
- verdict-1, finding 2: fixed - the sluice gates are a row, at most one cut a way's leg, each recorded and filed; a toe collector's cap is a deck, among the items
- verdict-1, finding 3: fixed - a deck is 10 by 4 ft and a plank no wider than its ditch, each under 64 ft, in the Bounds
- verdict-1, finding 4: fixed - the dike's segments are read in the ways' walk's own cell visit, and the dike is the field's outline, not among the waters
- verdict-1, finding 5: fixed - the plank spots take the registry's density flat at 29, a measured Bound the audit confirms
- verdict-1, finding 6: fixed - the spots are the floor of each ditch's length over 300 ft plus 1, as the figure counts them

## Cheaper algorithms considered

- sweep: not used - the ways and the waters are walked through a shared grid, which finds every crossing once without a sort
- grid or spatial index: used - the water index, the field's outline index and the registry
- priority queue: not used - nothing is ranked; every crossing is decked
- incremental update: used - each deck and plank is filed as it is laid, so a plank sees the decks standing
- memoizing what a scan does not change: used - the water index is built once for every way
