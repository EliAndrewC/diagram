# Derivation - field (feature 444)

## Contract

- Reads: the plan - the field's frame and fan, the intake at the high head (`head_sluice`), the archetype (the reference: a valley comb), the plot size rolled from `PLOT_SIZES` (0005: a basin about 48 ft across its canal, 26 to 36 ft) through `plot_texture`, which resolves it into the comb's levers and draws nothing.
- Writes: the comb (`draw_comb_field`: the dry hem, the flooded paddies, the bunds and the channels), the field ditches, the head race and drawn channels, the field's outline, the brook from off the map past the fan, the intake and its weir, the field pond; and each ditch stretch outside the crop reserved as a 30 px (30 ft at the reference's 1 ft a px, `meta.ftpx`) no-build corridor, written into the corridor index.
- Keeps: the comb grown round the water, fed at the high head (0053); the brook fed past the intake (0059); every plot inside the fan's outline (a plot on the outline is clipped to it and kept - none is refused) and off every ditch, and so off the brook, which runs outside the outline: the brook is tested against the outline, in place of every plot against it. The cohort's checks: each footprint against the overlap matrix (`overlap/`).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households, each record read by its `poly` list; past 20 at each figure's measured rate a doubling): the comb's plots 376 and 853 (853 at 20, 1,807 at 40, 3,715 at 80); the outline, a closed ring, its perimeter 3,146 and 4,874 ft (x1.55: 4,874 at 20, 7,555 at 40, 11,710 at 80) and its points, so its segments, 67 and 78 (x1.16: 78 at 20, 90 at 40, 105 at 80); at most 4 outline segments in one 60 ft cell at 20 (11 at 10, a 0.1 ft sliver, at a size the budget is not held at; the segments lengthen with size, the points growing slower than the perimeter); the ditches 9 and 12 (12 at 20, 16 at 40, 21 at 80), their segments 79 and 120 (x1.52: 120 at 20, 182 at 40, 277 at 80), their length 3,430 and 5,885 ft (x1.72: 5,885 at 20, 10,122 at 40, 17,410 at 80), of it outside the outline 914 and 1,225 ft (x1.34: 1,225 at 20, 1,642 at 40, 2,200 at 80); the brook, an open line, 5,404 and 7,362 ft (x1.36: 7,362 at 20, 10,012 at 40, 13,617 at 80), 212 and 237 points, so 211 and 236 segments (236 at 20, 264 at 40, 296 at 80).

## The algorithm

    lay the head race, the ditches, the brook, the outline, the pond, the intake and the weir, each written once
    index the outline in square cells of 60 ft - at least a plot's diagonal (48 by 36 ft: 60 ft) - each segment filed in every cell it crosses
    walk each ditch's segments through the outline's cells, testing the outline segments filed there: the stretches outside the
        crop found; reserve each, 30 ft wide, written into the corridor index's 60 ft cells
    walk the outline's points once, filing each to the strip whose ditches it falls between
    for each strip between two neighboring ditches, walking down the fall, for each plot tried:
        cut it: one new cross line met against the current segment of each of the strip's two ditches (the last plot's line kept)
        select: past either ditch's crossing, or holding a vertex filed to its strip? - then it is on the outline: look at the
            at most 4 cells it touches and clip it against the outline segments filed there; keep it
        classify it by its fall below the head; record its polygon and its bunds
    walk the brook's segments through the outline's cells, testing the outline segments filed there

## Indexes

- outline index: cells of 60 ft (at least a plot's diagonal); densest 4 outline segments a cell (measured at 20), from a smallest side of 60 ft against the outline's segments, which lengthen with size
- corridor index: cells of 60 ft; written, not searched here - a corridor 30 ft wide, from a smallest side of 30 ft, spans at most 2 cells across at any orientation (30 ft on the diagonal is 42 ft, under 60)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 853 at 20, 1,807 at 40, 3,715 at 80 | the comb's plots - every plot tried is recorded | 80 households |
| the cut (S1) | per item | 2 | one new cross line x the current segment of each of two ditches | always 2; a pointer's step counted below |
| the selection | per item | 2 | the cut against each of the strip's two ditches' crossings (a vertex filed to the strip counted in its own row) | always 2 |
| the class | per item | 1 | one comparison of the plot's fall against the head's | always 1 |
| the record | per item | 8 | the plot's 4 corners and 4 bund edges | always 8 |
| slack | per item | 1 | every factor is a bound at its worst case | not applicable |
| the outline's plots (outline index cells examined) | over the run | 5,840 at 20, 8,420 at 40, 12,360 at 80 | 20 each: the at most 4 cells a plot touches at any orientation, examined, and at most 4 outline segments filed in each, tested; the plots on the outline by the crossing rule across a 26 by 48 ft lattice, L x sqrt(1/26^2 + 1/48^2), plus one a segment (each segment can begin in a plot of its own): 292 at 20, 421 at 40, 618 at 80 | 80 households |
| the outline's vertices | over the run | 78 at 20, 90 at 40, 105 at 80 | each walked once and filed to its strip | every point |
| the pointers' steps | over the run | 240 at 20, 364 at 40, 554 at 80 | one more test each time a strip's pointer steps, once a ditch segment | every segment a bend |
| the ditches (outline index cells examined) | over the run | 1,295 at 20, 2,105 at 40, 3,440 at 80 | 5 a segment-cell entry - the cell examined, at most 4 outline segments tested - the ditches' entries by the crossing rule, their length at its diagonal over 60 ft plus one a segment: 259 at 20, 421 at 40, 688 at 80 | 80 households |
| the corridors (corridor index cells written) | over the run | 106 at 20, 142 at 40, 188 at 80 | the stretches outside the crop at their diagonal over 60 ft, plus one at each of a ditch's 2 stretch ends, x 2 cells across | 80 households |
| the brook (outline index cells examined) | over the run | 2,050 at 20, 2,500 at 40, 3,085 at 80 | 5 a segment-cell entry, as the ditches; its entries by the crossing rule: 410 at 20, 500 at 40, 617 at 80 | 80 households |
| the outline index (cells written) | once | 193 at 20, 269 at 40, 382 at 80 | the crossing rule on the closed outline: its perimeter at its diagonal over 60 ft plus one a segment | 80 households |
| the writes | once | 437 at 20, 539 at 40, 681 at 80 | the ditches' segments, the brook's 236 segments (236 at 20, 264 at 40, 296 at 80), the outline's points, and the pond, the intake and the weir, 3 | 80 households |

So: plots x (2 + 2 + 1 + 8) x 1, plus the run's terms, the index and the writes once.

## Totals

- at 20: 853 x (2 + 2 + 1 + 8) x 1 + 5840 + 78 + 240 + 1295 + 106 + 2050 + 193 + 437 = 21328
- at 40: 1807 x (2 + 2 + 1 + 8) x 1 + 8420 + 90 + 364 + 2105 + 142 + 2500 + 269 + 539 = 37920
- at 80: 3715 x (2 + 2 + 1 + 8) x 1 + 12360 + 105 + 554 + 3440 + 188 + 3085 + 382 + 681 = 69090

## Earlier findings

- verdict-1, finding 1: fixed - no texture factor: the comb draws no furrows (`draw_comb_field`: hem, paddies, bunds, channels)
- verdict-1, finding 2: fixed - the ditches' segments measured from their `poly` lists: 79 and 120 at 10 and 20 (`phases/items.md`)
- verdict-1, finding 3: fixed - the brook is counted once, by the cells it enters
- verdict-1, finding 4: fixed - every row is a term of the Totals (the bundle checks it)
- verdict-1, finding 5: fixed - a plot on the outline is clipped against the outline in its cells (the outline's plots row)
- verdict-1, finding 6: fixed - slack 1; named work is in rows of its own
- verdict-1, finding 7: fixed - the items are the comb's own plots, 853 at 20
- verdict-1, finding 8: fixed - each figure is measured from the manifest or derived from the contract
- verdict-2, finding 1: fixed - slack 1; the pointers' steps are a run term, one a ditch segment
- verdict-2, finding 2: fixed - the items come from the measured slope, 47.7 a household
- verdict-2, finding 3: fixed - no mean segment: outline tests are counted by segment-cell entries
- verdict-3, finding 1: fixed - every index row counts the cells it examines or writes
- verdict-3, finding 2: fixed - the outline's perimeter grows x1.55 a doubling, as measured
- verdict-3, finding 3: fixed - the cut is 2 a plot: one new cross line, the last plot's line kept
- verdict-4, finding 1: fixed - the selection row (2 a plot) and the outline's vertices walked once decide which plots are on the outline
- verdict-4, finding 2: fixed - the outline's plots by the crossing rule across a 26 by 48 ft lattice, plus one a segment: 292 at 20
- verdict-4, finding 3: fixed - every plot tried is recorded: an outline plot is clipped and kept, none refused (the Keeps line)
- verdict-4, finding 4: fixed - a corridor's reserve is written into the corridor index's cells, counted by its length and width
- verdict-5, finding 1: fixed - the corridor index has 60 ft cells, the 30 px width converted (30 ft at 1 ft a px), and its cells written counted from both
- verdict-5, finding 2: fixed - with 60 ft cells, at least a plot's diagonal (60 ft for 48 by 36), a plot touches at most 2 x 2 cells at any orientation
- verdict-5, finding 3: fixed - every outline vertex is walked once and filed to the strip it falls in
- verdict-5, finding 4: disputed - the crossing rule's +1 a segment stands: each outline segment can begin in a plot of its own (the row states it)
- verdict-5, finding 5: fixed - the brook is counted by its own segment-cell entries against the outline segments in those cells
- verdict-5, finding 6: fixed - the brook has 236 segments (237 points, an open line)
- verdict-6, finding 1: fixed - the brook's term is its own cells entered, each tested against the outline's segments there
- verdict-7, finding 1: fixed - 60 ft cells, so 4 at any orientation; and a writes row for the ditches, brook, outline, pond, intake and weir
- verdict-7, finding 2: fixed - no end-segment assumption: every ditch segment is walked through the outline's cells
- verdict-7, finding 3: fixed - no densest-cell charge to every cell: outline tests are counted by segment-cell entries, at most 4 outline segments in a 60 ft cell (measured at 20; the outline's segments lengthen with size)
- verdict-7, finding 4: fixed - segments counted as points less one on an open line, as points on the closed outline
- verdict-7, finding 5: fixed - no rule on corridors keeping apart: the corridor index's writes are counted, not its density

## Cheaper algorithms considered

- sweep: used - each strip's plots are cut in order down the fall, each sharing the last plot's line
- grid or spatial index: used - the outline in 60 ft cells, each segment filed where it crosses, so a plot or a segment meets only what is filed in its cells
- priority queue: not used - no plot is ranked against another
- incremental update: used - each ditch's pointer advances as the strip is walked; a plot keeps the last plot's line; the outline's vertices are filed to their strips once
- memoizing what a scan does not change: used - the outline's index, the ditches' crossings and the vertices' strips are found once, before any strip is cut
