# Derivation - crossings (feature 444)

## Contract

- Reads: every way as laid (the connector, the web's lanes, the households' ways; `lanes`); every watercourse (the brook, the drawn channels, the field ditches; on a polder its perimeter dike and toe collector); the registry of what stands; the field's form (a comb or a polder).
- Writes: a deck (`bridges`) at every crossing of a way and water, square to the water; plank footbridges along the long field ditches, one every 300 ft on a comb and 320 ft on a polder (a GUESS, `channel_footbridges`); a sluice gate at every cut of a polder's perimeter dike, where a channel passes through it (`dike_gates`, 0019; a water gate, 20 ft in span on the pool's water-edge hamlet, Kuwabata); the polder's crossing caps on the settlement-side toe collector (a GUESS).
- Keeps: every crossing decked, square (0084; the `roads_bridge_water` check); set after every way and every watercourse, so no crossing is left unbridged; each plank asked against what stands before it is laid (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the ways' length 4,703 and 8,917 ft (x1.9: 8,917 at 20, 16,943 at 40, 32,191 at 80) and their segments 24 and 144, 2.4 and 7.2 a household - at most 8 a household taken (160 at 20, 320 at 40, 640 at 80): a household's way is at most 3 legs (the homesteads' budget) and the web's lanes are pulled taut between the plots they serve, so the segments grow with the households, not with today's output (x6 a doubling from 10 to 20 is the reference map's shape at 20, not a rate); the waters' segments 428 and 574 (x1.34: 574 at 20, 770 at 40, 1,031 at 80) and length 12,344 and 19,311 ft (x1.56: 19,311 at 20, 30,126 at 40, 46,996 at 80); at most 26 and 18 water segments in one 64 ft cell (26 taken); the field ditches' length 3,430 and 5,885 ft (x1.72: 5,885 at 20, 10,123 at 40, 17,411 at 80) in 9 and 12 ditches (x1.33: 12 at 20, 16 at 40, 22 at 80); the bridges 6 and 9 on the comb-field reference (x1.5: 9 at 20, 14 at 40, 21 at 80); on a polder the toe collector is a drawn channel, among the waters' segments; the polder's caps a fixed count by the seat's side (`polder_crossing_caps`: three on the collector the village abuts, one on each other collector or lateral it names, none on the drain), at most 5 plus the laterals, the laterals at most the drawn channels (18 at 20, 22 at 40, 27 at 80); the drawn channels 10 and 13 (x1.3: 13 at 20, 17 at 40, 22 at 80); the dike's cuts recorded with the dike (`perimeter_dike`), where water passes it, at most a channel's inlet and outlet, 2 a channel (26 at 20, 34 at 40, 44 at 80); a sluice gate 20 ft in span; at most 21 and 29 standing things in one 64 ft cell about the houses (29 taken, a measured Bound the audit at 40 and 80 confirms); a deck 10 by 4 ft and a plank no wider than a ditch, each under 64 ft, so in at most 2 by 2 cells; the perimeter dike is the field's outline, not among the waters' segments (the brook, the channels and the ditches); at most 12 outline segments in one 64 ft cell (the field's, the polder's dike its outline); 1 ft a pixel at the hamlet scale.

## The algorithm

    index the waters' segments in 64 ft cells, once
    walk each way through the water index's cells: each water segment in a cell tested against the way's leg; each crossing
        decked, square to the water, recorded and filed, and a deck on a ditch also filed on that ditch by its distance along it
        (appended, and marking the at most 3 plank spots within the spacing of it); a crossing is accepted only in the cell its
        point falls in, so a water segment filed in several cells is decked once; a crossing of the toe collector is a deck
    on a polder: each cut the dike records (its point only, as `dike_gates` reads it), its sluice gate snapped onto a
        watercourse within 20 ft (the 2 by 2 water index cells the radius reaches, their segments read), recorded and filed; the caps, a fixed count by the seat's side, each seated on its collector
        against the registry and filed
    along each field ditch, a spot every 300 ft (320 on a polder), floor of its length over 300 plus 1: its plank, unless a
        deck stands within the spacing (its flag, marked as the decks were laid), tested
        against the registry's things in its cells (S4); laid, recorded and filed

## Indexes

- water index: cells of 64 ft; densest 26 water segments a cell (measured at 10 and 20, 26 and 18, the ceiling taken), from a smallest side of 64 ft
- registry: cells of 64 ft; densest 29 standing things a cell (measured at 10 and 20, 21 and 29, the ceiling taken), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 9 at 20, 14 at 40, 21 at 80 | the decks, one a crossing of a way and a water: the comb's measured. A polder's other waters are the same channels and ditches a comb has; its toe collector's crossings are the caps, which `polder_crossing_caps` places by the seat's side, their own row, so no crossing of the collector is decked twice | 80 households |
| the deck (registry cells written) | per item | 5 | recorded (1) and filed in at most 4 cells, a deck 10 by 4 ft (4) | always 5 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the water index (cells written) | once | 2,149 at 20, 2,976 at 40, 4,132 at 80 | each water segment walked through the cells it crosses: the waters' length at root 2 over 64 ft, plus 3 a segment (a grid walk crosses one cell more than the grid lines it crosses each way) | 80 households |
| the ways' walk (water index cells examined) | over the run | 18,306 at 20, 36,045 at 40, 71,064 at 80 | the ways' cells, their length at root 2 over 64 ft plus 3 a segment (678 at 20, 1,335 at 40, 2,632 at 80), each read with its at most 26 water segments tested against the leg (27) | every way through the densest water |
| the sluice gates (water index and registry cells) | over the run | 2,938 at 20, 3,842 at 40, 4,972 at 80 | the dike's recorded cuts (26 at 20, 34 at 40, 44 at 80), each snapped onto a watercourse within 20 ft (a radius, which reaches into at most 2 by 2 cells of 64 ft about the cut, each read with its at most 26 segments, 4 x 27, 108), recorded (1) and filed in at most 4 cells, a gate 20 ft in span (4) | a polder |
| the caps (registry cells examined) | over the run | 2,268 at 20, 2,772 at 40, 3,402 at 80 | the polder's caps (18 at 20, 22 at 40, 27 at 80), each its seat on its collector (1), its plank's - a cap is a plank, no wider than its collector, under 64 ft - 2 by 2 cells with their 29 things and the cell (120), recorded and filed (5) | a polder |
| the ditch decks (spots marked) | over the run | 36 at 20, 56 at 40, 84 at 80 | each deck appended to its ditch (1) and the at most 3 spots within the spacing of it marked (3) | every deck on a ditch |
| the plank spots (registry cells examined) | over the run | 3,904 at 20, 6,100 at 40, 9,882 at 80 | the spots, floor of each ditch's length over 300 ft plus 1, summed at most the ditches' length over 300 ft plus the ditches, rounded up (32 at 20, 50 at 40, 81 at 80); each its point along the ditch (1), its flag (1), and its plank's box's at most 2 by 2 cells with their 29 things and the cell (120) | every spot planked |
| the planks laid (registry cells written) | over the run | 160 at 20, 250 at 40, 405 at 80 | each plank recorded (1) and filed in at most 4 cells (4) | every spot planked |

So: the decks x 5 x 1, plus the water index, the ways' walk, the sluice gates, the caps, the ditch decks, the plank spots and the planks laid.

## Totals

- at 20: 9 x 5 x 1 + 2149 + 18306 + 2938 + 2268 + 36 + 3904 + 160 = 29806
- at 40: 14 x 5 x 1 + 2976 + 36045 + 3842 + 2772 + 56 + 6100 + 250 = 52111
- at 80: 21 x 5 x 1 + 4132 + 71064 + 4972 + 3402 + 84 + 9882 + 405 = 94046

## Earlier findings

- verdict-1, finding 1: fixed - the decks within a plank's spacing are read from a flag each deck marks on its ditch's spots as it is laid; no registry reach
- verdict-1, finding 2: fixed - the sluice gates are a row, each recorded and filed; the toe collector's caps are their own row (verdict-2, finding 4)
- verdict-1, finding 3: fixed - a deck is 10 by 4 ft and a plank no wider than its ditch, each under 64 ft, in the Bounds
- verdict-1, finding 4: fixed - no way's leg is tested against the dike: the dike's cuts are its own record, and the dike is the field's outline, not among the waters
- verdict-1, finding 5: fixed - the plank spots take the registry's density flat at 29, a measured Bound the audit confirms
- verdict-1, finding 6: fixed - the spots are the floor of each ditch's length over 300 ft plus 1, as the figure counts them
- verdict-2, finding 1: fixed - a cut of the dike is recorded with the dike where water passes it (a sluice is a water gate, 20 ft in span on Kuwabata), at most a channel's inlet and outlet, 2 a channel; no way's leg cuts the dike
- verdict-2, finding 2: fixed - the gate's 20 ft span is in the Bounds, under 64 ft
- verdict-2, finding 3: fixed - each deck is appended to its ditch and marks the at most 3 spots within the spacing; each spot reads one flag; no sorted insert
- verdict-2, finding 4: fixed - the toe collector is a drawn channel, among the waters; its caps are the fixed count `polder_crossing_caps` sets by the seat's side, their own row
- verdict-2, finding 5: fixed - a crossing is accepted only in the cell its point falls in, so a water segment in several cells is decked once (S4)
- the arbiter's continue (ask:444-T04-crossings-round-3), a: fixed - the dike's-cuts row and the ways' dike test are struck
- the arbiter's continue, b: fixed - the gates are read from the dike's recorded cuts, each snapped from one water index cell; no walk of the dike
- the arbiter's continue, c: fixed - the caps are `polder_crossing_caps`' fixed count, at most 5 plus the laterals
- the arbiter's continue, d: fixed - `dike_gates` draws a gate at every cut the dike records, snapped onto a watercourse within 20 ft or at the cut, so every recorded cut is counted, on a course or not
- the arbiter's continue, e: fixed - the verdict-1 finding 1 line reads the flags
- verdict-3, finding 1: fixed - the snap's 20 ft radius reads the 2 by 2 cells it reaches, 108, 113 a gate
- verdict-3, finding 2: fixed - the decks are the comb's measured on a polder too: its other waters are a comb's, and its toe collector's crossings are the caps' own row
- verdict-3, finding 3: fixed - a cap is a plank, no wider than its collector, under 64 ft; the stale verdict-1 finding 2 line reads the caps' own row
- verdict-3, finding 4: disputed - the dike's cut record holds the cut's point only (`dike_gates` snaps it onto a watercourse within 20 ft, else draws it at the cut), so the gate's snap search stays

## Cheaper algorithms considered

- sweep: not used - the ways and the waters are walked through a shared grid, which finds every crossing once without a sort
- grid or spatial index: used - the water index and the registry
- priority queue: not used - nothing is ranked; every crossing is decked
- incremental update: used - each deck and plank is filed as it is laid, and each deck marks its ditch's spots, so a plank reads one flag
- memoizing what a scan does not change: used - the water index is built once for every way
