# Derivation - field (feature 444)

## Contract

- Reads: the plan - the field's frame and fan, the intake at the high head (`head_sluice`), the archetype (the reference: a valley comb), the plot size rolled from `PLOT_SIZES` (0005: a basin about 48 ft across its canal, 26 to 36 ft) through `plot_texture`, which resolves it into the comb's levers and draws nothing; the field record's `cell`, 1,488 sq ft, is each plot's area - at its narrowest, 26 ft wide (0005), a plot is at most 57.2 ft long, its diagonal at most 62.9 ft.
- Writes: the comb (`draw_comb_field`: the dry hem, the flooded paddies, the bunds and the channels), the field ditches - the head race and its branches and the drain (the `field_ditches` records, roles main, branch and drain) - and their drawn channels (`drawn_channels`, 13 records of 231 points at 20), the field's outline, the brook from off the map past the fan, the intake and its weir, the field pond; and each ditch stretch outside the crop reserved as a 30 px (30 ft at the reference's 1 ft a px, `meta.ftpx`) no-build corridor, written into the corridor index.
- Keeps: the comb grown round the water, fed at the high head (0053); the brook fed past the intake (0059); every plot inside the fan's outline (a plot on the outline is clipped to it and kept - none is refused) and off every ditch, and so off the brook, which runs outside the outline: the brook is tested against the outline, in place of every plot against it. The cohort's checks: each footprint against the overlap matrix (`overlap/`).
- Bounds (measured 2026-10-28, `phases/items.md`; the comb's strips about 272 ft wide - the crop's area, the plots x 1,488 sq ft (1,269,264 at 20), over the ditches' length inside it (5,885 less 1,225 ft) - so a strip holds a row of at most 11 plots across (272 ft over 0005's narrowest 26 ft), and at least 1; the dry hem's record, `fields[0].drain_hem`, 36 and 61 polygons of 265 and 409 points at 10 and 20, x1.54 a doubling: 409 at 20, 631 at 40, 974 at 80; the reference manifests at 10 and 20 households, each record read by its `poly` list; past 20 at each figure's measured rate a doubling, but the plots at their slope a household: 1.3 gross acres a household (0017) over a fixed cell is linear in the households, the hem their intercept): the comb's plots 376 and 853 (853 at 20, 1,807 at 40, 3,715 at 80); the outline, a closed ring, its perimeter 3,146 and 4,874 ft (x1.55: 4,874 at 20, 7,555 at 40, 11,710 at 80) and its points, so its segments, 67 and 78 (x1.16: 78 at 20, 90 at 40, 105 at 80); at most 10 outline segments in one 64 ft cell at any size measured (10 at 10, where a 0.1 ft sliver crowds them; 4 at 20; measured 2026-10-28 by walking each segment through 64 ft cells) - the ceiling taken at every size, a sliver's crowding not following the mean segment; the ditches 9 and 12 (12 at 20, 16 at 40, 21 at 80), their segments 79 and 120 (x1.52: 120 at 20, 182 at 40, 277 at 80), their length 3,430 and 5,885 ft (x1.72: 5,885 at 20, 10,122 at 40, 17,410 at 80), of it outside the outline 914 and 1,225 ft (x1.34: 1,225 at 20, 1,642 at 40, 2,200 at 80); the brook, an open line, 5,404 and 7,362 ft (x1.36: 7,362 at 20, 10,012 at 40, 13,617 at 80), 212 and 237 points, so 211 and 236 segments (236 at 20, 264 at 40, 296 at 80); the drawn channels 149 and 231 points (x1.55); the weir a framed record of 4 points, the field pond an ellipse of 4 values, the intake one value.

## The algorithm

    lay the head race, the ditches, the brook, the outline, the pond, the intake and the weir, each written once
    index the outline in square cells of 64 ft - at least a plot's diagonal (62.9 ft at its narrowest) - each segment filed in every cell it crosses
    walk each ditch's segments through the outline's cells, testing the outline segments filed there: the stretches outside the
        crop found; reserve each, 30 ft wide, written into the corridor index's 64 ft cells
    walk the outline's points once, filing each to the strip whose ditches it falls between
    for each strip between two neighboring ditches, walking down the fall, row by row, for each plot tried:
        cut the next row: one new cross line met against the current segment of each of the strip's two ditches (the last row's
            line kept), then divided along it into the row's plots, one divider a plot but the last
        select: past either ditch's crossing (2 comparisons), or holding its strip's next filed vertex (1)? - then it is on the outline
        classify it by its fall below the head
    walk the outline's ring through the cut comb, plot by plot: at each plot it enters, find where it leaves (at most 3 side
        tests against the plot's other edges; across a ditch, a binary search of the next strip's cross lines, so no cross line
        need line up with its neighbor's); each crossing clips the two plots it divides; then record every plot, clipped or not
    walk the brook's segments through the outline's cells, testing the outline segments filed there

## Indexes

- outline index: cells of 64 ft (at least a plot's diagonal); densest 10 outline segments a 64 ft cell, the ceiling measured at any size, from a smallest side of 64 ft against a sliver
- corridor index: cells of 64 ft; written, not searched here - a corridor 30 ft wide, from a smallest side of 30 ft, spans at most 2 cells across at any orientation (30 ft on the diagonal is 42 ft, under 64)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 853 at 20, 1,807 at 40, 3,715 at 80 | the comb's plots - every plot tried is recorded | 80 households |
| the cut (S1) | per item | 2 | a row of k plots across (1 to 11, the Bounds) costs its one cross line met against its two ditches' current segments, 2, and k - 1 dividers: (k + 1) / k a plot, at most 2 | a row of one plot; a pointer's step counted below |
| the selection | per item | 3 | the row against each of the strip's two ditches' crossings, and against the strip's next filed vertex - at most 3 a plot, a row's tests shared by its plots | a row of one plot |
| the class | per item | 1 | one comparison of the plot's fall against the head's | always 1 |
| the record | per item | 8 | the plot's 4 corners and 4 bund edges, written once after the ring walk (a clipped plot's extra points in the clipped records) | always 8 |
| slack | per item | 1 | every factor is a bound at its worst case: each crossing-rule row pays 3 a segment, its start cell and the 2 more it can touch at a corner | not applicable |
| the ring walk | over the run | 7,966 at 20, 11,286 at 40, 16,293 at 80 | each plot the ring enters: at most 3 side tests to find its exit; where it crosses a ditch, a binary search of the next strip's rows (log2 of the plots, rounded up: 10 at 20, 11 at 40, 12 at 80) and then of the row's plots (4, log2 of 11 rounded up), charged at every entry; the entries at their worst, the length term L x sqrt(1/26^2 + 1/57.2^2) plus 3 a segment, plus one for each strip the ring enters (the cross lines need not line up from strip to strip; it enters a strip at most where a ditch crosses it, 2 a ditch): 464 at 20, 622 at 40, 852 at 80; plus one a vertex | every entry across a ditch |
| the clipped records | over the run | 1,006 at 20, 1,334 at 40, 1,809 at 80 | each crossing recorded in the 2 plots it divides - the crossings as many as the entries, 464 at 20, 622 at 40, 852 at 80 - and each vertex once | every crossing a corner of two plots |
| the outline's vertices | over the run | 156 at 20, 180 at 40, 210 at 80 | 2 each: the vertex's side of each of the two ditches it falls between - the ring's order keeps each strip's vertices in order | every point |
| the pointers' steps | over the run | 240 at 20, 364 at 40, 554 at 80 | one more test each time a strip's pointer steps: once a ditch segment for each of the 2 strips an inner ditch borders | every segment a bend |
| the ditches (outline index cells examined) | over the run | 5,401 at 20, 8,470 at 40, 13,376 at 80 | 11 a segment-cell entry - the cell examined, at most 10 outline segments tested; the entries at their worst, their length at its diagonal over 64 ft plus 3 a segment (its start cell and up to 2 more at a corner): 491 at 20, 770 at 40, 1,216 at 80 | 80 households |
| the corridors (corridor index cells written) | over the run | 776 at 20, 1,166 at 40, 1,760 at 80 | the ditches' length outside the crop at its diagonal over 64 ft, plus 3 a ditch segment (its worst: a start cell and 2 more at a corner), x 2 cells across | 80 households |
| the brook (outline index cells examined) | over the run | 9,581 at 20, 11,154 at 40, 13,079 at 80 | 11 a segment-cell entry - the cell examined, at most 10 outline segments tested; the entries at their worst, its length at its diagonal over 64 ft plus 3 a segment: 871 at 20, 1,014 at 40, 1,189 at 80 | 80 households |
| the outline index (cells written) | once | 342 at 20, 437 at 40, 574 at 80 | the closed outline's perimeter at its diagonal over 64 ft, plus 3 a segment at its worst | 80 households |
| the writes | once | 1,096 at 20, 1,551 at 40, 2,238 at 80 | each line written by its points: the dry hem's points (409 at 20, 631 at 40, 974 at 80), the ditches' points (their segments plus one a record: 132 at 20, 198 at 40, 298 at 80), the drawn channels' points (231 at 20, 358 at 40, 555 at 80), the brook's points (237 at 20, 265 at 40, 297 at 80), the outline's points, the weir's 4 points, the field pond's 4 values and the intake's 1 | 80 households |

So: plots x (2 + 3 + 1 + 8) x 1, plus the run's terms, the index and the writes once.

## Totals

- at 20: 853 x (2 + 3 + 1 + 8) x 1 + 7966 + 1006 + 156 + 240 + 5401 + 776 + 9581 + 342 + 1096 = 38506
- at 40: 1807 x (2 + 3 + 1 + 8) x 1 + 11286 + 1334 + 180 + 364 + 8470 + 1166 + 11154 + 437 + 1551 = 61240
- at 80: 3715 x (2 + 3 + 1 + 8) x 1 + 16293 + 1809 + 210 + 554 + 13376 + 1760 + 13079 + 574 + 2238 = 101903

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
- verdict-11, finding 1: fixed - every crossing-rule row pays 3 a segment, its worst (the start cell and the 2 more a segment can touch at a corner), so slack 1 holds
- verdict-11, finding 2: fixed - the ring walk follows the cut lines as they are, a binary search of each strip's own cross lines, so none need line up
- verdict-11, finding 3: fixed - the ring is walked through the cut comb, each crossing found where it happens, in place of the clip of every outline plot against its cells
- verdict-12, finding 1: fixed - the cut is a row's: one cross line against the strip's two ditches and a divider a plot, at most 2 a plot for a row of 1 to 11 plots across
- verdict-12, finding 2: fixed - the selection is the row's, shared by its plots; the ring walk's search finds the row and then the plot in it
- verdict-12, finding 3: fixed - the entries add one for each strip the ring enters, 2 a ditch
- verdict-12, finding 4: fixed - the plots are stated linear in the households (1.3 gross acres a household over a fixed cell), the other figures at their rate a doubling

## Cheaper algorithms considered

- sweep: used - each strip's plots are cut in order down the fall, each sharing the last plot's line
- grid or spatial index: used - the outline in 64 ft cells, each segment filed where it crosses, so a plot or a segment meets only what is filed in its cells
- priority queue: not used - no plot is ranked against another
- incremental update: used - each ditch's pointer advances as the strip is walked; a plot keeps the last plot's line; the outline's vertices are filed to their strips once; the ring is walked through the comb once, each crossing found where it happens
- memoizing what a scan does not change: used - the outline's index, the ditches' crossings and the vertices' strips are found once, before any strip is cut
