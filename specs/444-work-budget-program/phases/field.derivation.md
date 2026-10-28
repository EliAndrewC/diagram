# Derivation - field (feature 444)

## Contract

- Reads: the plan - the field's frame and fan, the intake at the high head (`head_sluice`), the archetype (the reference: a valley comb), the plot size rolled from `PLOT_SIZES` (0005: a basin about 48 ft across its canal, 26 to 36 ft) through `plot_texture`, which resolves it into the comb's levers and draws nothing; the field record's `cell`, 1,488 sq ft, is each plot's area - at its narrowest, 26 ft wide (0005), a plot is at most 57.2 ft long, its diagonal at most 62.9 ft.
- Writes: the comb (`draw_comb_field`: the dry hem, the flooded paddies, the bunds and the channels), the field ditches - the head race and its branches and the drain (the `field_ditches` records, roles main, branch and drain) - and their drawn channels (`drawn_channels`, 13 records of 231 points at 20), the field's outline, the brook from off the map past the fan, the intake and its weir, the field pond; and each ditch stretch outside the crop reserved as a 30 px (30 ft at the reference's 1 ft a px, `meta.ftpx`) no-build corridor, written into the corridor index.
- Keeps: the comb grown round the water, fed at the high head (0053); the brook fed past the intake (0059); every plot inside the fan's outline (a plot on the outline is clipped to it and kept - none is refused) and off every ditch, and so off the brook, which runs outside the outline: the brook is tested against the outline, in place of every plot against it. The cohort's checks: each footprint against the overlap matrix (`overlap/`).
- Bounds (measured 2026-10-28, `phases/items.md`; the dry hem's record, `fields[0].drain_hem`, 36 and 61 polygons of 265 and 409 points at 10 and 20, x1.54 a doubling: 409 at 20, 631 at 40, 974 at 80; the reference manifests at 10 and 20 households, each record read by its `poly` list; past 20 at each figure's measured rate a doubling): the comb's plots 376 and 853 (853 at 20, 1,807 at 40, 3,715 at 80); the outline, a closed ring, its perimeter 3,146 and 4,874 ft (x1.55: 4,874 at 20, 7,555 at 40, 11,710 at 80) and its points, so its segments, 67 and 78 (x1.16: 78 at 20, 90 at 40, 105 at 80); at most 10 outline segments in one 64 ft cell at any size measured (10 at 10, where a 0.1 ft sliver crowds them; 4 at 20; measured 2026-10-28 by walking each segment through 64 ft cells) - the ceiling taken at every size, a sliver's crowding not following the mean segment; the ditches 9 and 12 (12 at 20, 16 at 40, 21 at 80), their segments 79 and 120 (x1.52: 120 at 20, 182 at 40, 277 at 80), their length 3,430 and 5,885 ft (x1.72: 5,885 at 20, 10,122 at 40, 17,410 at 80), of it outside the outline 914 and 1,225 ft (x1.34: 1,225 at 20, 1,642 at 40, 2,200 at 80); the brook, an open line, 5,404 and 7,362 ft (x1.36: 7,362 at 20, 10,012 at 40, 13,617 at 80), 212 and 237 points, so 211 and 236 segments (236 at 20, 264 at 40, 296 at 80); the drawn channels 149 and 231 points (x1.55); the weir a framed record of 4 points, the field pond an ellipse of 4 values, the intake one value.

## The algorithm

    lay the head race, the ditches, the brook, the outline, the pond, the intake and the weir, each written once
    index the outline in square cells of 64 ft - at least a plot's diagonal (62.9 ft at its narrowest) - each segment filed in every cell it crosses
    walk each ditch's segments through the outline's cells, testing the outline segments filed there: the stretches outside the
        crop found; reserve each, 30 ft wide, written into the corridor index's 64 ft cells
    walk the outline's points once, filing each to the strip whose ditches it falls between
    for each strip between two neighboring ditches, walking down the fall, for each plot tried:
        cut it: one new cross line met against the current segment of each of the strip's two ditches (the last plot's line kept)
        select: past either ditch's crossing (2 comparisons), or holding its strip's next filed vertex (1)? - then it is on the outline: look at the
            at most 4 cells it touches and clip it against the outline segments filed there; keep it
        classify it by its fall below the head; record its polygon and its bunds
    walk the brook's segments through the outline's cells, testing the outline segments filed there

## Indexes

- outline index: cells of 64 ft (at least a plot's diagonal); densest 10 outline segments a 64 ft cell, the ceiling measured at any size, from a smallest side of 64 ft against a sliver
- corridor index: cells of 64 ft; written, not searched here - a corridor 30 ft wide, from a smallest side of 30 ft, spans at most 2 cells across at any orientation (30 ft on the diagonal is 42 ft, under 64)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 853 at 20, 1,807 at 40, 3,715 at 80 | the comb's plots - every plot tried is recorded | 80 households |
| the cut (S1) | per item | 2 | one new cross line x the current segment of each of two ditches | always 2; a pointer's step counted below |
| the selection | per item | 3 | the cut against each of the strip's two ditches' crossings, and against the strip's next filed vertex | always 3 |
| the class | per item | 1 | one comparison of the plot's fall against the head's | always 1 |
| the record | per item | 8 | the plot's 4 corners and 4 bund edges | always 8 |
| slack | per item | 1 | every factor is a bound at its worst case | not applicable |
| the outline's plots (outline index cells examined) | over the run | 12,496 at 20, 18,040 at 40, 26,400 at 80 | 44 each: the at most 4 cells a plot touches at any orientation, examined, and at most 10 outline segments filed in each, tested; the plots on the outline by the crossing rule across a lattice of the plots the contract allows at their most elongated, 26 by 57.2 ft (1,488 sq ft at 0005's narrowest 26 ft): L x sqrt(1/26^2 + 1/57.2^2), 206 at 20, 320 at 40, 495 at 80, plus one a segment (each segment can begin in a plot of its own): 284 at 20, 410 at 40, 600 at 80 | 80 households |
| the clipped records | over the run | 646 at 20, 910 at 40, 1,305 at 80 | a plot on the outline is recorded clipped, holding the outline's crossing points and any outline vertex inside it: each crossing - one each time the outline enters a plot, so as many as the outline's plots, 284 at 20, 410 at 40, 600 at 80 (on a closed ring, entries and crossings are the same number) - recorded in the 2 plots it divides, each vertex once | every crossing a corner of two plots |
| the outline's vertices | over the run | 156 at 20, 180 at 40, 210 at 80 | 2 each: the vertex's side of each of the two ditches it falls between - the ring's order keeps each strip's vertices in order, so the selection's next filed vertex needs no sort | every point |
| the pointers' steps | over the run | 240 at 20, 364 at 40, 554 at 80 | one more test each time a strip's pointer steps: once a ditch segment for each of the 2 strips an inner ditch borders | every segment a bend |
| the ditches (outline index cells examined) | over the run | 2,761 at 20, 4,466 at 40, 7,282 at 80 | 11 a segment-cell entry - the cell examined, at most 10 outline segments tested - the ditches' entries by the crossing rule, their length at its diagonal over 64 ft plus one a segment: 251 at 20, 406 at 40, 662 at 80 | 80 households |
| the corridors (corridor index cells written) | over the run | 296 at 20, 438 at 40, 652 at 80 | the ditches' length outside the crop at its diagonal over 64 ft, plus one a ditch segment (where a stretch lies is not assumed), x 2 cells across | 80 households |
| the brook (outline index cells examined) | over the run | 4,389 at 20, 5,346 at 40, 6,567 at 80 | 11 a segment-cell entry, as the ditches; its entries by the crossing rule: 399 at 20, 486 at 40, 597 at 80 | 80 households |
| the outline index (cells written) | once | 186 at 20, 257 at 40, 364 at 80 | the crossing rule on the closed outline: its perimeter at its diagonal over 64 ft plus one a segment | 80 households |
| the writes | once | 1,096 at 20, 1,551 at 40, 2,238 at 80 | each line written by its points: the dry hem's points (409 at 20, 631 at 40, 974 at 80), the ditches' points (their segments plus one a record: 132 at 20, 198 at 40, 298 at 80), the drawn channels' points (231 at 20, 358 at 40, 555 at 80), the brook's points (237 at 20, 265 at 40, 297 at 80), the outline's points, the weir's 4 points, the field pond's 4 values and the intake's 1 | 80 households |

So: plots x (2 + 3 + 1 + 8) x 1, plus the run's terms, the index and the writes once.

## Totals

- at 20: 853 x (2 + 3 + 1 + 8) x 1 + 12496 + 646 + 156 + 240 + 2761 + 296 + 4389 + 186 + 1096 = 34208
- at 40: 1807 x (2 + 3 + 1 + 8) x 1 + 18040 + 910 + 180 + 364 + 4466 + 438 + 5346 + 257 + 1551 = 56850
- at 80: 3715 x (2 + 3 + 1 + 8) x 1 + 26400 + 1305 + 210 + 554 + 7282 + 652 + 6567 + 364 + 2238 = 97582

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
- verdict-5, finding 1: fixed - the corridor index has 64 ft cells, the 30 px width converted (30 ft at 1 ft a px), and its cells written counted from both
- verdict-5, finding 2: fixed - with 64 ft cells, at least a plot's diagonal (62.9 ft at its narrowest; verdict-8 finding 5), a plot touches at most 2 x 2 cells at any orientation
- verdict-5, finding 3: fixed - every outline vertex is walked once and filed to the strip it falls in
- verdict-5, finding 4: disputed - the crossing rule's +1 a segment stands: each outline segment can begin in a plot of its own (the row states it)
- verdict-5, finding 5: fixed - the brook is counted by its own segment-cell entries against the outline segments in those cells
- verdict-5, finding 6: fixed - the brook has 236 segments (237 points, an open line)
- verdict-6, finding 1: fixed - the brook's term is its own cells entered, each tested against the outline's segments there
- verdict-7, finding 1: fixed - 64 ft cells, so 4 at any orientation (verdict-8 finding 5); and a writes row for the ditches and their drawn channels, the brook, the outline, the pond, the intake and the weir (verdict-8 finding 1)
- verdict-7, finding 2: fixed - no end-segment assumption: every ditch segment is walked through the outline's cells
- verdict-7, finding 3: fixed - outline tests are counted by segment-cell entries, at most 10 outline segments in a 64 ft cell, the ceiling measured at any size (verdict-8 finding 4)
- verdict-7, finding 4: fixed - segments counted as points less one on an open line, as points on the closed outline
- verdict-7, finding 5: fixed - no rule on corridors keeping apart: the corridor index's writes are counted, not its density
- verdict-8, finding 1: fixed - the head race and its branches are the `field_ditches` records (roles main, branch, drain) and their drawn channels are counted in the writes; the pond, intake and weir by their own sizes (4 values, 1 value, the weir's points)
- verdict-8, finding 2: fixed - the selection is 3 a plot: its two ditches' crossings and its strip's next filed vertex
- verdict-8, finding 3: fixed - the corridors add one a ditch segment, not one a stretch end, so where a stretch lies is not assumed
- verdict-8, finding 4: fixed - the outline's density is the ceiling measured at any size in 64 ft cells, 10 a cell, not the 4 measured at 20
- verdict-8, finding 5: fixed - the cell is sized from the plot's area (the record's 1,488 sq ft) at its narrowest width (0005's 26 ft): 57.2 ft long, a 62.8 ft diagonal, so 64 ft cells - no maximum length read into "about 48 ft"
- verdict-9, finding 1: fixed - the clipped records are a run row: the outline's crossing points, each in the 2 plots it divides, and its vertices
- verdict-9, finding 2: fixed - the pointers' row says why it is 2 a ditch segment: an inner ditch borders 2 strips
- verdict-9, finding 3: fixed - the lattice is the plots the contract allows at their most elongated, 26 by 57.2 ft
- verdict-9, finding 4: fixed - every line in the writes row is counted by its points
- verdict-10, finding 1: fixed - the clipped records count a crossing each time the outline enters a plot, as many as the outline's plots
- verdict-10, finding 2: fixed - the dry hem's points are in the writes, measured from its record
- verdict-10, finding 3: fixed - filing a vertex is 2 side tests, and the ring's order keeps each strip's vertices in order

## Cheaper algorithms considered

- sweep: used - each strip's plots are cut in order down the fall, each sharing the last plot's line
- grid or spatial index: used - the outline in 64 ft cells, each segment filed where it crosses, so a plot or a segment meets only what is filed in its cells
- priority queue: not used - no plot is ranked against another
- incremental update: used - each ditch's pointer advances as the strip is walked; a plot keeps the last plot's line; the outline's vertices are filed to their strips once
- memoizing what a scan does not change: used - the outline's index, the ditches' crossings and the vertices' strips are found once, before any strip is cut
