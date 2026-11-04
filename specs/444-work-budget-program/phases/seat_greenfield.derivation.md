# Derivation - seat, greenfield (feature 444 FR-015; revised under FR-022 rule 2, 2026-11-04)

## Contract

- Reads: the field's outline; the plan's fall, wind, settlement form, the cluster's shape and the households; the dry plots standing (none: the dry hem is laid after the seat, behind it - 0006, feature 444 T28); the brook's course; the wet toe below the fields and a tail pond's reed fringe; the pond and the drain's run off it; every watercourse on the map - the field's ditches, the farm channels as drawn and the brook - for the ways' routing and for the seat's way out. It derives the wet toe below the fields from the field's outline, grows the way out's wet walls by the lane's width, and sets the cost every later way pays to cross the brook on the brook's course.
- Writes: where the settlement sits - the cluster's band on a margin of the field, its center, its long and short axes, its anchor and whether its back is off the wind - with the ranked margins after it, the ladder the house seating falls back down when the chosen margin cannot seat every household; the brook's fords, the only places a way may cross it, and the cost every later way pays to cross; the list of watercourses every later way is routed against; the side of the field the houses stand on. Drawn nowhere. The ladder's rungs are asked their own way out by the house seating when it falls back to one, not here.
- Keeps: a village's cluster sits on the higher, drier ground beside its paddy (0031: "On the higher, drier ground beside its paddy, as old settlements stood on the natural levee"), its back to the wind (0072: a clustered village shelters behind one belt at its windward edge), so the belt's band is kept on the canvas before any house is seated; the band stands on open ground, off the field, its back clear of the dry crop (the hem laid after it keeps off the settlement's ground, so none stands behind a margin when it is asked); never on the wet toe below the fields (0058: "seat and anchor off the marsh below the fields"); never centered in a pond's reed fringe (the GM's ruling of 2026-08-28), an end in it scored down; the brook across the band scored down, never refused (0035: "a site the brook does not cross is still preferred when two are otherwise level"); the seat has a dry way out of the frame (0081: lanes keep to dry ground); a way crosses the brook only at a ford, opened on a straight reach (0035).
- Bounds (measured 2026-11-04, `make stage-sizes STAGE=seat` on the reference rolls, with the wet toe below the fields as the roll derives it, seeds 4, 25, 39, 47, the mean over the seeds that reach the seat): the field's outline 68, 96 and 135 points at 20, 40 and 80 households, of whose margins 37, 53 and 74 face within 90 degrees of the wind; no dry plot (the hem is laid after the seat); the brook 324, 450 and 632 stations, 20 ft apart; the wet toe 71, 90 and 118 points; the reed fringe 52, 54 and 54 points; the watercourses 487, 642 and 856 segments; the canvas 6,400, 8,900 and 12,550 ft square. On the reference rolls' finished seats (`make stage-sizes STAGE=waterward DUMP=`, the seat as the next stage is handed it): the band's half-depth 152 to 300 ft and half-length 389 to 918 ft, the band's half-depth 169, 232 and 300 ft at 20, 40 and 80 (the mean; "a band depth" below is this half-depth throughout, the band two of them deep); re-measured 2026-11-04 on the reference rolls with the hem after the seat (`make stage-sizes STAGE=hem DUMP=`, the seat as the next stage is handed it): the ranked margins that pass every refusal 29, 42 and 59 at 20, 40 and 80 (the mean); the straight runs a head tries until one keeps clear, 1, 9 and 1 on three seeds and none of the sixteen on the fourth (seed 47, at every size), 6.75 on the mean, its way out a walk of 128, 176 and 248 of the 20 ft cells toward the nearest edge (32, 44 and 62 on the mean), each walked cell's new neighbors about 3 (the walk aimed at the edge, its cells remembered); the field's breadth across the fall 1,263, 1,786 and 2,526 ft (the mean); the brook's course 6,854, 9,524 and 13,371 ft; the way out's wet walls 111, 130 and 154 points.

## The algorithm

    the plan read: the form, the shape, the fall, the wind, the households (5); the band's two half-extents from the households (2)
    the wet toe derived: the field's points read for the crop's low edge and projected across the fall, sorted once; a station every
      30 ft across the field's breadth and 90 ft past each side, each taking the points within 90 ft of it by bisection
    the way out's wet walls - the toe and the reeds - grown by the lane's width, each point along its normals
    the crossing cost set on the brook's course: a sample every 5 ft filed in cells a hair wider than the crossing's half-length,
      and each filed cell's 3 x 3 neighborhood
    the indexes, once: the outline's, the toe's and the reeds' edges filed by horizontal strip; the dry plots' cells, empty at the seat; the brook read once in its order along the fall; the walls of the way out (the toe,
      the reeds, the outline and the pond's ring) and every watercourse segment filed in cells
    the margins: each outline edge's midpoint, outward normal and its turn against the wind (2 a point); a margin facing within 90
      degrees of the wind is a candidate, its back the normal, or turned to the wind off a flank
    for each candidate, the refusals, cheapest first:
      the band's center inside the frame; the belt's band, a rectangle, clipped to the canvas for the share of it off (10)
      the wet toe at the anchor and the center (2 tests, a strip each)
      the band on open ground: 9 sample points tested against the outline (a strip read and its edges each)
      the reeds: the center refused in them, 9 points for the share of the band in them (10 tests)
      the back's clear ground: the share of the back's area - its depth the belt's and the cluster's, its width the band's depth -
        under the dry plots, from the cells it covers and each plot in them clipped to it
    for each candidate that passes, the score:
      the nearest dry-plot edge (the hem): none stands, the cells empty, the search ends at once
      the brook on the band: 15 points each asked the brook's nearest segment within 30 ft, the segments found by bisection on
        the brook's order along the fall
      the score itself: the wind, the upslope end, the reeds' share, the hem, the back, the belt's room, and the brook as the
        tie-break between margins otherwise level (7)
    the passing margins ranked by score, the first met winning a tie
    the head's dry way out: straight runs off the canvas tried every 22.5 degrees, each run asked the cells it crosses of the walls
      and the water, until one is clear; where none is, the walk of the 20 ft cells toward the nearest canvas edge, each cell asked
      of the walls and the water as it is reached, until one off the canvas, every cell it reached remembered with its answer; the next margin taken where the head has no way out, its walk reading what the walks before it found - a cell tested is never tested again, and reaching a cell already joined to an edge, or already walled in, ends the walk
    the fords: the brook walked station by station, a ford opened on each straight reach at its spacing (2 a station, a write a ford)
    the crossing cost set once; the watercourses gathered for the ways (1 a segment)
    written: the seat's frame for each passing margin (8 each), the off-wind flag, the skeleton and the field's face (3)

## The knobs the count reads

Each a GUESS: no page gives a sampling or a spacing, and each is a value of ours the rolls can move.

- the band's sample points: 9 on its open-ground test - its near edge, middle and far edge at its middle and both thirds along its length; the reeds' share on the same 9 and the center; the brook's 15 - the same three depths at five places along it, closer than the reeds' because the brook is a line a third-point grid can miss
- the back's depth: 2.6 band depths (half-depths) behind the margin - the band's own two and its belt's far edge, 146 ft behind the band's fringe, about 0.6 of a half-depth at 40 (146 / 232); its width one half-depth, centered on the margin's midpoint - the strip behind the band's middle, which the belt cannot bend away from (its ends wrap round the crop where it stands): 439 by 169 ft at 20, 603 by 232 at 40, 780 by 300 at 80
- the brook's reach on the band: a point within 30 ft of the brook counts as on the water
- the ford's spacing: 160 ft along the brook (0035 gives "a crossing place", no spacing)
- the way out's grid: 20 ft, the narrowest dry neck a track takes
- the straight runs: every 22.5 degrees, 16 in all; each run stepped at 128 ft, the way out's index cell - wider than the farthest a wall's margin reaches, so the 3 x 3 cells round a step hold every edge that can block it
- the wet toe's pad: 90 ft (0057: the toe's edge 90 ft above the local lowest field, the band as wide as the fields plus 90 ft each side); its stations across the slope every third of the pad, 30 ft, so the three stations it is smoothed over span one pad - a GUESS, the page gives "short steps" and no figure
- the crossing cost's band: the crossing's half-length, 30 ft either side of the brook (a CONVENTION: a 60 ft crossing place, so a deck near square lands on both banks); its samples every 5 ft along the brook (a GUESS: a way's ask measures points, and 5 ft keeps a sample within a foot of the band's edge); its cells 31 ft, one foot wider than the half-length, so the 3 x 3 cells round a point hold every sample within the band

## Indexes

- the outline, the toe and the reeds: cells of 64 ft, each a horizontal strip, every edge filed in the strips it spans (measured 2026-11-04 on the seat's input, `make stage-sizes STAGE=seat DUMP=`: 102, 143 and 201 filings for the outline at 20, 40 and 80, 204, 280 and 388 for the toe, 66, 71 and 78 for the reeds); a point test reads its strip and the edges in it, the typical strip about 6 of the outline's edges and 4 of the toe's or the reeds'; densest case from a smallest side of 64 ft, a strip holding 33 of the outline's edges at 40 where its lobes run along the strip
- the dry plots: cells of 64 ft, empty at the seat (the hem is laid after it); the back's rectangle - 2.6 band depths by one, 439 by 169 ft at 20, 603 by 232 at 40, 780 by 300 at 80 - covers (439 / 64 + 1) x (169 / 64 + 1) = 29, 48 and 75 cells, each read and found empty; densest case from a smallest side of 64 ft, 6 plots in one cell where a hem stood
- the way out: cells of 64 ft, the walls (the outline, the toe, the reeds and the pond's 16-point ring: 208, 256 and 324 edges, about 2 cells each) and every watercourse segment (1,095, 1,504 and 2,022 filings) filed in the cells they cross; a straight run off the canvas crosses half the canvas in 25, 35 and 49 steps of 128 ft, each step reading the 3 x 3 cells round it (9; about a third of them read again by the next step's window, priced as read), holding about 0.1 items a cell (about 2,000 filings over about 19,300 cells at 40); densest case from a smallest side of 64 ft, a cell where the brook and a ditch meet

No grid of the brook: its stations stand in order along the fall (measured 2026-11-03 on the reference rolls: each station no higher than the one before), so a range along the fall is found by bisection, 9, 9 and 10 halvings at 324, 450 and 632 stations, and the segments in it within 30 ft of the point, about 3, are asked.

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 37 at 20, 53 at 40, 74 at 80 | the margins facing within 90 degrees of the wind, each a candidate seat | every edge on the windward half |
| the frame and the belt's room | per item | 10 | the center's two bounds and the belt's rectangle clipped to the canvas, its 4 corners and 4 edges | always 10 |
| the outline, the toe and the reeds' cells | per item | 21 | the strips read: the toe's 2 tests, open ground's 9 points, the reeds' 10 (the knobs) | always 21 |
| the wet toe | per item | 8 | the anchor and the center, 4 edges each in their strips | the toe reaching the margin |
| open ground | per item | 54 | 9 band points, 6 of the outline's edges each in their strips | the outline's lobes beside the margin, up to 33 an edge strip |
| the reeds | per item | 40 | the center and 9 band points, 4 edges each in their strips | a pond roll; a brook-sink roll has no fringe |
| the dry plots' cells | per item | 29 at 20, 48 at 40, 75 at 80 | the cells the back's rectangle covers (the Indexes), each read and found empty: no dry plot stands at the seat | a plot standing, each clipped (8) |
| margins passing every refusal | over the run | 29 at 20, 42 at 40, 59 at 80 | the chosen margin and its ladder, measured on the reference seats with the hem after the seat | every candidate passing |
| the brook on the band | over the run | 315 at 20, 315 at 40, 345 at 80, a passing margin | 15 points (the knob), each two bisections of 9, 9 or 10 steps (the stations within 30 ft either side of its place) and 3 segments | the brook across the band |
| the score | over the run | 7 a passing margin | its seven terms: the wind, the upslope end, the reeds' share, the hem (none standing), the back, the belt's room and the brook's tie-break | always 7 |
| the ranking | over the run | 145 at 20, 252 at 40, 354 at 80 | the passing margins sorted, n log n: 29 x 5, 42 x 6, 59 x 6 | every candidate passing |
| the plan read and the band's size | once | 7 | the five plan fields and the two half-extents | always 7 |
| the margins' scan | once | 136 at 20, 192 at 40, 270 at 80 | each outline point's normal and turn against the wind (2 a point) | the typical field |
| the outline's strips filed | once | 102 at 20, 143 at 40, 201 at 80 | each edge in the strips it spans, measured | the typical field |
| the toe's strips filed | once | 204 at 20, 280 at 40, 388 at 80 | each edge in the strips it spans, measured | the typical toe |
| the reeds' strips filed | once | 66 at 20, 71 at 40, 78 at 80 | each edge in the strips it spans, measured | a pond roll |
| the brook read | once | 324 at 20, 450 at 40, 632 at 80 | each station read once in its order | the typical brook |
| the way out's wet walls grown | once | 111 at 20, 130 at 40, 154 at 80 | each point of the toe and the reeds moved along its normals by the lane's width, measured | a pond roll |
| the way out's walls filed | once | 416 at 20, 512 at 40, 648 at 80 | 208, 256 and 324 edges in about 2 cells each | a pond roll |
| the way out's water filed | once | 1,095 at 20, 1,504 at 40, 2,022 at 80 | each watercourse segment in the cells it crosses, measured | the typical map |
| the way out's cells along its runs | once | 1,603 at 20, 2,248 at 40, 3,146 at 80 | 6.75 runs on the mean (measured), each half the canvas in 128 ft steps (25, 35 and 49), each step its 3 x 3 reach cells read (9) and about half an item new (0.5) - 6.75 x 25 x 9.5, 6.75 x 35 x 9.5, 6.75 x 49 x 9.5 | sixteen runs walled |
| the way out's walk | once | 1,344 at 20, 1,848 at 40, 2,604 at 80 | 32, 44 and 62 walked cells on the mean (measured: seed 47 walks, the others do not), each its about 3 new neighbors tested once, each test its 9 reach cells, an item and its 4 walls' strips (14) - 42 a walked cell | a seat walled in on the way to every edge: every 20 ft cell of the canvas tested once, its cells remembered across margins |
| the walk remembered | once | 145 at 20, 221 at 40, 312 at 80 | every cell the walk reached marked with its answer, about 5 a walked cell (its new neighbors and itself), measured | as the walk's |
| the fords | once | 691 at 20, 960 at 40, 1,348 at 80 | each station's bend tested (2 a station) and a ford written each 160 ft of the brook's course (the knob: 6,854, 9,524 and 13,371 ft over 160 - 43, 60, 84) | the typical brook |
| the watercourses gathered | once | 488 at 20, 643 at 40, 857 at 80 | each segment listed for the ways (487, 642, 856) and the crossing cost set (1) | the typical map |
| the frames written | once | 235 at 20, 339 at 40, 475 at 80 | 8 for each passing margin, and the flag, the skeleton and the face (3) | every candidate passing |
| the wet toe derived | once | 1,684 at 20, 2,328 at 40, 3,375 at 80 | the field's 68, 96 and 135 points read twice for the crop's low edge (2) and projected and sorted (3); a station every 30 ft across the breadth and 90 ft past each side (48, 66 and 90), each two bisections of 7, 7 or 8 steps, the about 10 points within 90 ft of it, and its edge and inner line (4) | a field whose points bunch under one station |
| the crossing cost set | once | 3,954 at 20, 5,496 at 40, 7,723 at 80 | a sample every 5 ft of the brook (1,371, 1,905 and 2,674) filed in 31 ft cells, about 1.3 cells a 31 ft run (287, 399 and 561), each cell's 3 x 3 neighborhood (9) | the typical brook |
| slack | per item | 1 | every factor is a count of the stage's own inputs | not applicable |

So: items x (10 + 21 + 8 + 54 + 40 + the back's cells) x slack + the passing margins x (the brook on the band + 7) + the ranking + each once term.

## Totals

- at 20: 37 x (10 + 21 + 8 + 54 + 40 + 29) x 1 + 29 x (315 + 7) + 145 + 7 + 136 + 102 + 204 + 66 + 324 + 111 + 416 + 1095 + 1603 + 1344 + 145 + 691 + 488 + 235 + 1684 + 3954 = 28082
- at 40: 53 x (10 + 21 + 8 + 54 + 40 + 48) x 1 + 42 x (315 + 7) + 252 + 7 + 192 + 143 + 280 + 71 + 450 + 130 + 512 + 1504 + 2248 + 1848 + 221 + 960 + 643 + 339 + 2328 + 5496 = 40741
- at 80: 74 x (10 + 21 + 8 + 54 + 40 + 75) x 1 + 59 x (345 + 7) + 354 + 7 + 270 + 201 + 388 + 78 + 632 + 154 + 648 + 2022 + 3146 + 2604 + 312 + 1348 + 857 + 475 + 3375 + 7723 = 60754

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.56 (28,082 to 60,754): the candidates with the outline's points
(37 to 74), the passing margins (29 to 59), the brook and its crossing cost with the brook's length, the wet toe's stations with the
field's breadth, and the way out with the canvas. The wet toe's stations and the field's points are two growing sets, but each station
takes its slice of the points by bisection, so the toe grows with the stations and the points, not their product. No other loop over a
growing set runs inside another; the way out's walk remembers every cell it has tested and every cell it has found joined to an edge
or walled in, across the margins the head falls back to, so the whole run tests each cell of the canvas at most once.

## Work the first derivation missed

Feature 444 FR-022 rule 2 (amendment 7, the GM 2026-11-03): each item is work the contract owes that the first count left out. The
first count priced one pass over the outline for its highest point; the contract the seat keeps holds all of the following.

- the candidates' refusals - the band on open ground, off the field; its back clear of the dry crop; the band and its belt on the canvas; never on the wet toe; never centered in the reeds (0031, 0072, 0058 and the GM's ruling of 2026-08-28): the first count chose the highest point and tested no seat against any of them
- the score's terms beyond height - the wind first (0072: the back to the wind), the dry hem and the back's crop, the reeds' share, the belt's room, and the brook across the band as the tie-break between margins otherwise level (0035): the first count scored height alone
- the ladder - every margin that passes, ranked, which the house seating falls back down when the chosen margin cannot seat every household: the first count wrote one seat
- the dry way out of the frame (0081): a seat walled in by the wet, the field and the water is refused, and the next margin taken
- the brook's fords and the crossing cost (0035: a way crosses the brook only at a ford, opened on a straight reach), which the seat opens before any way is routed
- the watercourses gathered for every later way, the brook gapped at its fords
- the indexes each of these reads, built once: nothing a stage before the seat files outlives it, so the seat files what it asks
- the wet toe below the fields (0058: seat and anchor off the marsh below the fields), which the seat's refusals read and the seat derives through its door; the way out's wet walls grown by the lane's width (0081); and the crossing cost every later way pays (0035), set on the brook as the fords are opened - found uncounted by the MODE AUDIT of 2026-11-04 (`phases/seat.audit-1.txt`)

## Earlier findings

- verdict-1, finding 1: fixed - its SOUND judged one pass over the outline for the highest margin, the whole of the first count; that count is kept as the margins' scan above, and the work the contract owes beyond it is priced under `## Work the first derivation missed`
- verdict-2, finding 1: fixed - each sample count is now a knob named under `## The knobs the count reads` with its reason; the back's 21 points replaced by the share of its area under crop, from the cells its rectangle covers (2.6 band depths by one, the band's depth measured) and the plots in them clipped to it; the 160 ft ford spacing and the 16 runs named as knobs; the straight runs measured on the reference seats (3, 4, 8), and the walk where none is clear priced at its measured share
- verdict-2, notes: the way out's items 0.1 a cell, as measured; the hem's worst case its ring search to two band depths, in its row
- verdict-3, finding 1: fixed - as verdict-2's: the belt's band clipped to the canvas (10, its corners and edges) in place of 15 points; every other count named as a knob or derived from the band's depth and the plot side; the runs measured

- verdict-4, finding 1: fixed - "a band depth" is the half-depth throughout, said in the Bounds; the back's 2.6 half-depths are the band's two and the belt's far edge (146 ft, about 0.6 at 40), its width one half-depth on the margin's midpoint, the strip behind the band's middle the belt cannot bend away from, each in the knob with its rectangle in feet
- verdict-4, notes: the walk's figures derived (verdict-5); the 30,000 a seat said in Growth - the ladder and the map-wide indexes
- verdict-5, finding 1: fixed - the walk's step (20 ft), its 5 new neighbors a step aimed at the edge and its 20 a test derived in its row, the 4,964 ft in the Bounds, and its bound across the ladder stated: the cells it has tested and what it found of them remembered, so the canvas is walked at most once
- verdict-5, notes: the brook's 30 ft reach named a knob; the score's seven terms counted 7; the ladder's rungs' own way out is the house seating's (the contract's Writes), not the seat's

- note (verdicts 2-5), every refusal charged to every candidate: kept - the count prices each of the 53 candidates every refusal, the cheapest first; no reference measurement says which refusal stops which candidate, so the per-item term is an upper bound, at most about 26% of the total at 40 above a candidate that stops at its first refusal (under S10's half)
- note (verdicts 2-5), the plots' density behind a clear back: kept at 2.7 a cell, the density of the cells that hold any - an upper figure; a back that passes holds under 0.30 of its area in crop, so the plots it clips are fewer than the 21 at 40 priced
- note (verdicts 4-5), the reeds' test on every roll: a pond roll's work; the reference rolls are all pond rolls (the reference spec's sink is a pond), and a brook-sink roll has no fringe, its 40 a candidate and its strips not paid
- note (verdict 5), the brook's 30 ft reach: named under `## The knobs the count reads`
- note (verdict 5), the score's terms: seven, counted 7
- note (verdict 5), each ladder rung's way out: the house seating's, when it falls back to one (the contract's Writes), not the seat's
- note (verdict 2), the hem's ring search past 9 cells: its worst case in its row, about 6 rings out to two band depths where no hem stands near
- note (verdict 3), the brook's bisection along the fall: it brackets the stations whose places along the fall lie within 30 ft of the point's, and one station either side, which holds every segment within 30 ft of the point - a segment that near has an end within 30 ft along the fall, or spans the point's place; about 3 segments asked
- note (verdicts 2-4), the way out's items: about 0.1 a cell, as measured, in its row
- note (verdict 4), the figure of about 30,000 a seat: said in Growth - a seat and its ladder of 17 at 40, and the map-wide indexes every margin asks
- verdict-6, finding 1: fixed - its SOUND stood on the pipeline with the hem before the seat; the hem now follows the seat (T28), so the dry plots' rows are gone and the inputs re-measured; its notes answered below
- verdict-7, finding 1: fixed - as verdict-6's; its notes answered below
- verdicts 6-7, notes: the belt's 146 ft is the shelter belt's near face (36 ft, a GUESS) and its 110 ft depth (0071), claimed where the seat asks the belt's room, and the 2.6 is a knob at every size; the refusals' upper bound is about 25% of the total at 40 now, 53 x 181 = 9,593 against the 4,270 counted (under S10's half); the walk measured, not a minimum (44 cells at 40 on the mean, 176 on seed 47), its worst case in cells; the brook's tie-break is asked of every passing margin, as priced; the plots' filings - none now; the straight runs read the walk's memo first (a head in ground an earlier walk reached takes its answer with no run tried); an orthogonal step's 3 new neighbors priced in the walk's row; Growth no longer counts the indexes twice
- seat.audit-1, finding 1: fixed - the wet toe's derivation counted and priced, its stations' slices by bisection where each station walked every point of the field; the crossing cost's samples and cells counted and priced; the way out's grown walls counted and priced
- seat.audit-1, notes: the cells' duplicate check counted in each box's reads, the walk's memo counted, its neighbors' tests beside the runs'; the refusals' counter named for refusals, not drops
- verdict-9, finding 1: fixed - as verdict-8's below, the runs' 128 ft step named too
- verdict-8, finding 1: fixed - the spacings of the rows the audit added named as knobs with their reasons: the toe's 90 ft pad (0057) and its 30 ft stations (a third of the pad), the crossing's 30 ft half-length (a CONVENTION), its 5 ft samples and its 31 ft cells; the runs' 128 ft step named, and the Indexes' cells along a run given as the steps' 3 x 3 windows the row prices; the fords counted on the Bounds' course length (43, 60, 84)
- verdicts 8-9, notes: the crossing cost by a grid traversal of the brook's segments - not used, see below; the back's empty cells read on every candidate - kept, the index asked as the contract's refusal asks it, about 6% at 40; the brook asked of every passing margin - the ladder's order depends on it wherever two margins tie, and which tie is known only once every margin is scored; the refusals' upper bound about 24% at 40

## Cheaper algorithms considered

- sweep: used - one pass over the outline's points for the margins; the brook walked once for its fords
- grid traversal of the brook for the crossing cost: not used - each later way's ask measures its distance to the brook's samples within the band, and filing the segments cell to cell would save the samples (about 1,500 at 40, under S10's half) at the cost of a segment distance in every ask the ways make
- grid or spatial index: used - strips for the outline, the toe and the reeds; cells for the dry plots, the hem, the way out's walls and the water; the brook's own order along the fall for its nearest segments
- priority queue: not used - every passing margin is scored, because the ladder is the whole ranking; a bound-ordered search would stop at the chosen seat and leave the ladder unranked
- incremental update: not used - one seat and its ladder
- memoizing what a scan does not change: used - every index built once for all the candidates; the way out's walk remembers its cells across the margins
- pruning: the cheapest refusals first (the frame, the toe, open ground, the reeds) before the back's cells; the hem's search stopped at the first ring past its nearest edge; the way out stopped at the first clear run, its walk aimed at the nearest edge and stopped at the first cell off the canvas
