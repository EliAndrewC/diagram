# Derivation - field (feature 444)

## Contract

- Reads: the plan - the field's frame and fan, the intake at the high head (`head_sluice`), the archetype (the reference: a valley comb), the plot size rolled from `PLOT_SIZES` (0005: a basin about 48 ft across its canal, 26 to 36 ft) through `plot_texture`, which resolves it into the comb's levers (plots across a reach, the row step) and draws nothing.
- Writes: the comb (`draw_comb_field`: the dry hem, the flooded paddies, the bunds and the channels), the field ditches (5 points each), the head race and drawn channels, the field's outline, the brook from off the map past the fan (9 points), the intake and its weir, the field pond; and each ditch stretch outside the crop reserved as a 30 px no-build corridor.
- Keeps: the comb grown round the water, fed at the high head (0053); the brook fed past the intake (0059); every plot inside the fan's outline and off every ditch - and so off the brook, which runs outside the outline: the brook is tested against the outline once, in place of every plot against the brook. The cohort's checks (`cohort_audit` runs the gate's rules on the finished map, through `generate`): each footprint against the overlap matrix (`overlap/`) - nothing stands before this stage but the brook, so a plot is tested against the fan's outline and the brook alone.
- Bounds: the comb's plots, 376 at 10 households and 853 at 20 (the field record's `plots`, cells of 1,488 sq ft), measured 2026-10-28 (`phases/items.md`) - about 48 a household at the measured slope between them (the 1.3 gross acres a household of 0017 over a 1,488 sq ft cell would give 38; the comb tiles the fan's whole outline, its hem included): 1,810 at 40 and 3,720 at 80 by that line. The outline 67 points at 10 and 78 at 20 (its perimeter 3,146 ft and 4,874 ft; at 20 households no plot-sized cell holds more than 4 of its segments, measured the same day by walking each segment through the cells), the ditches 9 and 12, 5 points each: each grows as the fan's side, the square root of the households.

## The algorithm

    lay the head race from the intake along the high head, and the ditches down the fall from it
    index the fan's outline in a grid of square cells of a plot's area (1,488 sq ft, about 38.6 ft a side), once
    for each strip between two neighboring ditches, walking down the fall:
        cut the next plot: two cross lines at the row step, each met against the CURRENT segment of each of the strip's
            two ditches - a pointer that advances down the ditch as the strip is walked
        a plot on the strip's end, where the strip meets the fan's outline: its corners against the outline in its cells
        classify it (dry hem, flooded) by its fall below the head; record its polygon and its bunds
    lay each ditch's segments against the outline in their cells, reserving the stretches outside the crop
    lay the brook's segments against the outline in their cells

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | the comb's plots: 853 at 20, 1,810 at 40, 3,720 at 80 | the contract's Bounds | 80 households |
| the cut (S1) | per item | 4 | two cross lines x two ditches x the one current segment of each - the pointer has already advanced past every segment above the cut | a cut at a ditch's bend: its extra test is in the bends' row |
| the class | per item | 1 | one comparison of the plot's fall against the head's | always 1 |
| the record | per item | 8 | the plot's 4 corners and its 4 bund edges, written once | always 8 |
| the outline's plots | over the run | 16 x the plots on the outline | each such plot's 4 corners against at most 4 outline segments in its cell (the worst cell at 20 households, measured); the plots on the outline at most its perimeter over the narrowest plot, 26 ft (0005): 188 at 20, 265 at 40, 375 at 80, the perimeter growing as the fan's side | the narrowest plots, the worst cell |
| the bends | over the run | 4 x 3 x 2 x the ditches | a ditch has 4 segments, so a strip's pointer on each of its 2 ditches steps at most 3 times, each step one more cross-line test of 4 | 12 ditches at 20, 17 at 40, 24 at 80 |
| the ditches | over the run | 20 x the ditches | each of a ditch's 4 segments against at most 4 outline segments in its cells, then 4 reserves, one per stretch | as the bends |
| the brook | over the run | 32 | its 8 segments against at most 4 outline segments each - in place of every plot against the brook (the Keeps line) | the same at every size: the brook is 9 points |
| slack | per item | 1 | every factor is a bound at its worst case; the bends are counted in their own row | not applicable |

So: plots x (4 + 1 + 8) x 1 = 13 a plot, plus the run's terms (at 20: 3,008 + 288 + 240 + 32): about 14,700 at 20, 28,600 at 40
and 55,400 at 80 households - linear in the plots, so in the households.

## Cheaper algorithms considered

- sweep: used - each strip's plots are cut in order down the fall, so no cut searches the strip
- grid or spatial index: used - the fan's outline in plot-sized cells, so a corner meets at most 4 outline segments
- priority queue: not used - no plot is ranked against another
- incremental update: used - each ditch's current-segment pointer advances as the strip is walked; nothing above the cut is met again
- memoizing what a scan does not change: used - the outline's index is built once, before any strip is cut
