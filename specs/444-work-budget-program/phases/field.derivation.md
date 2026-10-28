# Derivation - field (feature 444)

## Contract

- Reads: the plan - the field's frame and fan, the intake at the high head (`head_sluice`), the archetype (the reference: a valley comb), the plot size rolled from `PLOT_SIZES` (0005: a basin about 48 ft across its canal, 26 to 36 ft) through `plot_texture`, which resolves it into the comb's levers and draws nothing.
- Writes: the comb (`draw_comb_field`: the dry hem, the flooded paddies, the bunds and the channels), the field ditches, the head race and drawn channels, the field's outline, the brook from off the map past the fan, the intake and its weir, the field pond; and each ditch stretch outside the crop reserved as a 30 px (30 ft at the reference's 1 ft a px, `meta.ftpx`) no-build corridor, written into the corridor index's cells.
- Keeps: the comb grown round the water, fed at the high head (0053); the brook fed past the intake (0059); every plot inside the fan's outline (a plot on the outline is clipped to it and kept, as the hem - none is refused) and off every ditch, and so off the brook, which runs outside the outline: the brook is tested against the outline, in place of every plot against the brook. The cohort's checks: each footprint against the overlap matrix (`overlap/`) - nothing stands before this stage but the brook.
- Bounds (measured 2026-10-28, `phases/items.md`, the reference roll's manifest at 10 and 20 households, each record read by its `poly` list; each size past 20 extended at its measured rate a doubling): the comb's plots 376 and 853 (47.7 a household: 853 at 20, 1,807 at 40, 3,715 at 80); the outline's perimeter 3,146 and 4,874 ft (x1.55: 4,874 at 20, 7,555 at 40, 11,710 at 80) and its points 67 and 78 (x1.16: 78 at 20, 90 at 40, 105 at 80); the most outline segments in one plot-sized cell, 11 at 10 (a 0.1 ft sliver) and 4 at 20 - the ceiling taken is 11 at every size; the ditches 9 and 12 (x1.33: 12 at 20, 16 at 40, 21 at 80), their segments 79 and 120 (x1.52: 120 at 20, 182 at 40, 277 at 80), the longest 222 ft; the brook 5,404 and 7,362 ft (x1.36: 7,362 at 20, 10,012 at 40, 13,617 at 80), 212 and 237 points (x1.12: 237 at 20, 265 at 40, 297 at 80), the most brook segments in one plot-sized cell 12 - the ceiling taken.

## The algorithm

    lay the head race and the ditches; index the fan's outline in square cells of a plot's area (1,488 sq ft, 38.6 ft a side), once
    find each ditch's two crossings of the outline, on its end segments, through the outline's cells; reserve each stretch
        outside the crop, written into the corridor index's cells
    for each strip between two neighboring ditches, walking down the fall, for each plot tried:
        cut it: one new cross line met against the CURRENT segment of each of the strip's two ditches (the plot's top line is
            the last plot's bottom line; each ditch's pointer advances down it)
        select: is the cut beyond either ditch's crossing? - one comparison a ditch; if so, the plot is on the outline:
            clip its 4 corners against the outline segments in each corner's cell, and keep it
        classify it by its fall below the head; record its polygon and its bunds
    walk the outline's points once, filing each to the strip whose crossings it falls between
    walk the brook's segments through the outline's cells, testing the outline segments in each

## Indexes

- outline index: cells of 38.6 ft (a plot's area); densest 11 outline segments a cell, measured at 10 and 20 households - a cell's side of 38.6 ft against the outline's shortest segment, a 0.1 ft sliver at 10; the ceiling taken at every size
- corridor index: cells of 38.6 ft (the outline index's grid); densest 3 corridors a cell, from a smallest side of 30 ft (a corridor's width, 30 px (30 ft)): corridors keep apart, so at most (38.6 + 30) / 30, rounded up

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 853 at 20, 1,807 at 40, 3,715 at 80 | the comb's plots - every plot tried is recorded (the Keeps line) | 80 households |
| the cut (S1) | per item | 2 | one new cross line x the one current segment of each of two ditches | always 2; a pointer's step counted below |
| the selection | per item | 2 | the cut against each of the strip's two ditches' crossings | always 2 |
| the class | per item | 1 | one comparison of the plot's fall against the head's | always 1 |
| the record | per item | 8 | the plot's 4 corners and 4 bund edges | always 8 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the outline's plots (outline index cells examined) | over the run | 21,024 at 20, 30,312 at 40, 44,496 at 80 | 72 each: a plot, up to 48 by 36 ft, touches at most 3 x 2 cells of 38.6 ft, each examined and its at most 11 outline segments tested; the plots on the outline the perimeter at its diagonal across a 26 by 48 ft lattice, L x sqrt(1/26^2 + 1/48^2): 292 at 20, 421 at 40, 618 at 80 | the 11-segment cell, every cell |
| the outline's vertices between crossings | over the run | 78 at 20, 90 at 40, 105 at 80 | each outline point walked once, filed to the strip whose crossings it falls between, so a plot holding a vertex is taken as an outline plot | every point |
| the pointers' steps | over the run | 240 at 20, 364 at 40, 554 at 80 | one more test each time a strip's pointer steps, once per segment of each of its 2 ditches | every segment a bend |
| the ditches' crossings (outline index cells examined) | over the run | 2,880 at 20, 3,840 at 40, 5,040 at 80 | 240 a ditch: 2 end segments, each through at most 10 cells (222 ft at its diagonal over 38.6 ft, plus one), each examined and its at most 11 outline segments tested | the longest end segments |
| the corridors (corridor index cells written) | over the run | 480 at 20, 640 at 40, 840 at 80 | 40 a ditch: 2 stretches, each at most an end segment long and 30 ft wide - 10 cells along by 2 across | the longest end segments |
| the brook (outline index cells examined) | over the run | 3,591 at 20, 5,036 at 40, 7,216 at 80 | its 236 segments walked through the outline index's cells: each cell it enters examined once, and at most 12 brook segments tested against the outline segments there - the outline index's cells x 12 plus the brook's cells | 80 households |
| the outline index (cells written) | once | 257 at 20, 367 at 40, 535 at 80 | the crossing rule on the perimeter: at its diagonal over 38.6 ft plus one a segment | 80 households |

So: plots x (2 + 2 + 1 + 8) x 1, plus the run's terms and the index once.

## Totals

- at 20: 853 x (2 + 2 + 1 + 8) x 1 + 21024 + 78 + 240 + 2880 + 480 + 3591 + 257 = 39639
- at 40: 1807 x (2 + 2 + 1 + 8) x 1 + 30312 + 90 + 364 + 3840 + 640 + 5036 + 367 = 64140
- at 80: 3715 x (2 + 2 + 1 + 8) x 1 + 44496 + 105 + 554 + 5040 + 840 + 7216 + 535 = 107081

## Cheaper algorithms considered

- sweep: used - each strip's plots are cut in order down the fall, each sharing the last plot's line
- grid or spatial index: used - the fan's outline in plot-sized cells, so a corner or a segment meets a bounded number
- priority queue: not used - no plot is ranked against another
- incremental update: used - each ditch's pointer advances as the strip is walked; a plot keeps the last plot's line; the outline plots are selected by the ditches' crossings, found once
- memoizing what a scan does not change: used - the outline's index and the ditches' crossings are built once, before any strip is cut
