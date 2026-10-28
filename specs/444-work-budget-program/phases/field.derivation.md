# Derivation - field (feature 444)

## Contract

- Reads: the plan - the field's frame and fan, the intake at the high head (`head_sluice`), the archetype (the reference: a valley comb), the plot size rolled from `PLOT_SIZES` (0005: a basin about 48 ft across its canal, 26 to 36 ft) through `plot_texture`, which resolves it into the comb's levers (plots across a reach, the row step) and draws nothing.
- Writes: the comb (`draw_comb_field`: the dry hem, the flooded paddies, the bunds and the channels), the field ditches, the head race and drawn channels, the field's outline, the brook from off the map past the fan, the intake and its weir, the field pond; and each ditch stretch outside the crop reserved as a 30 px no-build corridor.
- Keeps: the comb grown round the water, fed at the high head (0053); the brook fed past the intake (0059); every plot inside the fan's outline and off every ditch - and so off the brook, which runs outside the outline: the brook is tested against the outline, in place of every plot against the brook. The cohort's checks (`cohort_audit` runs the gate's rules on the finished map, through `generate`): each footprint against the overlap matrix (`overlap/`) - nothing stands before this stage but the brook.
- Bounds (measured 2026-10-28, `phases/items.md`, from the reference roll's manifest at 10 and 20 households, read by each record's `poly` list): the comb's plots 376 at 10 and 853 at 20 (cells of 1,488 sq ft), about 47.7 a household at the measured slope, so 1,807 at 40 and 3,715 at 80; the outline's perimeter 3,146 ft and 4,874 ft (x1.55 a doubling), its points 67 and 78 - the points growing slower than the perimeter, so its segments lengthen and a plot-sized cell holds no more than the 4 measured at 20; the ditches 9 and 12 (x1.33 a doubling), their segments 79 and 120 in all (x1.52), the longest 222 and 183 ft; the brook 5,404 ft and 7,362 ft (x1.36), 212 and 237 points. Each size past 20 is extended at its measured rate a doubling.

## The algorithm

    lay the head race from the intake along the high head, and the ditches down the fall from it
    index the fan's outline in a grid of square cells of a plot's area (1,488 sq ft, 38.6 ft a side), once
    for each strip between two neighboring ditches, walking down the fall:
        cut the next plot: one new cross line at the row step, met against the CURRENT segment of each of the strip's two
            ditches (the plot's top line is the last plot's bottom line, kept; each ditch's pointer advances down it)
        a plot on the outline: its 4 corners against the outline segments in its cell
        classify it by its fall below the head; record its polygon and its bunds
    for each ditch: find where it leaves the crop at its head and its tail, on its end segments, through the outline's cells;
        reserve each stretch outside the crop
    walk the brook's segments through the outline's cells, testing the outline segments in each

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 853 at 20, 1,807 at 40, 3,715 at 80 | the comb's plots (the Bounds) | 80 households |
| the cut (S1) | per item | 2 | one new cross line x the one current segment of each of two ditches | always 2; a pointer's step is counted below |
| the class | per item | 1 | one comparison of the plot's fall against the head's | always 1 |
| the record | per item | 8 | the plot's 4 corners and 4 bund edges, written once | always 8 |
| slack | per item | 1 | every factor is a bound at its worst case | not applicable |
| the outline's plots | over the run | 3,008 at 20, 4,656 at 40, 7,216 at 80 | 16 each: 4 corners x at most 4 outline segments in a cell, for the plots on the outline - at most the perimeter over the narrowest plot, 26 ft (0005): 188 at 20, 291 at 40, 451 at 80 | the narrowest plots |
| the pointers' steps | over the run | 240 at 20, 364 at 40, 554 at 80 | a strip's pointer on each of its 2 ditches steps once per segment of that ditch, each step one more test: 2 x the ditches' segments (120 at 20, 182 at 40, 277 at 80) | every segment a bend |
| the ditches' crossings (cells examined) | over the run | 1,080 at 20, 1,440 at 40, 1,890 at 80 | 90 a ditch: its 2 end segments, each through at most 9 cells (the longest segment, 222 ft, at its diagonal over 38.6 ft) with at most 4 outline segments tested in each - 2 x 9 x 5 | the longest end segments |
| the corridors | over the run | 24 at 20, 32 at 40, 42 at 80 | one reserve for each of a ditch's 2 stretches outside the crop | as the ditches |
| the brook (cells examined) | over the run | 1,350 at 20, 1,835 at 40, 2,495 at 80 | its length at its diagonal over 38.6 ft (270 at 20, 367 at 40, 499 at 80 cells), each cell examined and at most 4 outline segments tested: 5 a cell | 80 households |
| the outline's index (cells written) | once | 179 at 20, 277 at 40, 430 at 80 | the perimeter at its diagonal over 38.6 ft, each cell written once | 80 households |

So: plots x (2 + 1 + 8) x 1, plus the run's terms and the index once - linear in the plots, the run's terms growing more slowly.

## Totals

- at 20: 853 x (2 + 1 + 8) x 1 + 3008 + 240 + 1080 + 24 + 1350 + 179 = 15264
- at 40: 1807 x (2 + 1 + 8) x 1 + 4656 + 364 + 1440 + 32 + 1835 + 277 = 28481
- at 80: 3715 x (2 + 1 + 8) x 1 + 7216 + 554 + 1890 + 42 + 2495 + 430 = 53492

## Cheaper algorithms considered

- sweep: used - each strip's plots are cut in order down the fall, each sharing the last plot's line
- grid or spatial index: used - the fan's outline in plot-sized cells, so a corner or a segment meets at most 4 outline segments
- priority queue: not used - no plot is ranked against another
- incremental update: used - each ditch's current-segment pointer advances as the strip is walked, and a plot keeps the last plot's line
- memoizing what a scan does not change: used - the outline's index is built once, before any strip is cut
