# Derivation - seat, greenfield (feature 444 FR-015; revised under FR-022 rule 2, 2026-11-04)

## Contract

- Reads: the field's outline; the plan's fall, wind, settlement form, the cluster's shape and the households; the dry plots; the brook's course; the wet toe below the fields and a tail pond's reed fringe; the pond and the drain's run off it; every watercourse on the map - the field's ditches, the farm channels as drawn and the brook - for the ways' routing and for the seat's way out.
- Writes: where the settlement sits - the cluster's band on a margin of the field, its center, its long and short axes, its anchor and whether its back is off the wind - with the ranked margins after it, the ladder the house seating falls back down when the chosen margin cannot seat every household; the brook's fords, the only places a way may cross it, and the cost every later way pays to cross; the list of watercourses every later way is routed against; the side of the field the houses stand on. Drawn nowhere. The ladder's rungs are asked their own way out by the house seating when it falls back to one, not here.
- Keeps: a village's cluster sits on the higher, drier ground beside its paddy (0031: "On the higher, drier ground beside its paddy, as old settlements stood on the natural levee"), its back to the wind (0072: a clustered village shelters behind one belt at its windward edge), so the belt's band is kept on the canvas before any house is seated; the band stands on open ground, off the field, its back clear of the dry crop; never on the wet toe below the fields (0058: "seat and anchor off the marsh below the fields"); never centered in a pond's reed fringe (the GM's ruling of 2026-08-28), an end in it scored down; the brook across the band scored down, never refused (0035: "a site the brook does not cross is still preferred when two are otherwise level"); the seat has a dry way out of the frame (0081: lanes keep to dry ground); a way crosses the brook only at a ford, opened on a straight reach (0035).
- Bounds (measured 2026-11-04, `make stage-sizes STAGE=seat` on the reference rolls, with the wet toe below the fields as the roll derives it, seeds 4, 25, 39, 47, the mean over the seeds that reach the seat): the field's outline 68, 96 and 135 points at 20, 40 and 80 households, of whose margins 37, 53 and 74 face within 90 degrees of the wind; the dry plots 95, 152 and 251, at 380, 609 and 1,003 points; the brook 324, 450 and 632 stations, 20 ft apart; the wet toe 71, 90 and 118 points; the reed fringe 52, 54 and 54 points; the watercourses 487, 642 and 856 segments; the canvas 6,400, 8,900 and 12,550 ft square. On the reference rolls' finished seats (`make stage-sizes STAGE=waterward DUMP=`, the seat as the next stage is handed it): the band's half-depth 152 to 300 ft and half-length 389 to 918 ft, and the ranked margins that pass every refusal 13, 17 and 36 (the chosen one and its ladder, the mean); the band's half-depth 169, 232 and 300 ft at 20, 40 and 80 (the mean; "a band depth" below is this half-depth throughout, the band two of them deep); the dry plots' sides about 72 ft, each plot's box over about 6.3 cells of 64 ft, 2.7 plots in a cell that holds any; from each reference seat, the straight runs off the canvas tried until one keeps clear of the walls and the water, 3, 4 and 8 on the mean, and on one seat of the eleven (seed 47 at 80, 4,964 ft from the nearest canvas edge) none of the sixteen, its way out found only by a walk of the 20 ft cells (measured 2026-11-04 on the dumped seats: the walls, the water lines and the runs replayed on each).

## The algorithm

    the plan read: the form, the shape, the fall, the wind, the households (5); the band's two half-extents from the households (2)
    the indexes, once: the outline's, the toe's and the reeds' edges filed by horizontal strip; each dry plot's points read and the
      plot filed in the cells its box covers; the brook read once in its order along the fall; the walls of the way out (the toe,
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
      the nearest dry-plot edge within two band depths, from the cells round the margin (the hem)
      the brook on the band: 15 points each asked the brook's nearest segment within 30 ft, the segments found by bisection on
        the brook's order along the fall
      the score itself: the wind, the upslope end, the reeds' share, the hem, the back, the belt's room, and the brook as the
        tie-break between margins otherwise level (7)
    the passing margins ranked by score, the first met winning a tie
    the head's dry way out: straight runs off the canvas tried every 22.5 degrees, each run asked the cells it crosses of the walls
      and the water, until one is clear; where none is, the walk of the 20 ft cells toward the nearest canvas edge, each cell asked
      of the walls and the water as it is reached, until one off the canvas; the next margin taken where the head has no way out, its walk reading what the walks before it found - a cell tested is never tested again, and reaching a cell already joined to an edge, or already walled in, ends the walk
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
- the straight runs: every 22.5 degrees, 16 in all

## Indexes

- the outline, the toe and the reeds: cells of 64 ft, each a horizontal strip, every edge filed in the strips it spans (measured 2026-11-04 on the seat's input, `make stage-sizes STAGE=seat DUMP=`: 102, 143 and 201 filings for the outline at 20, 40 and 80, 204, 280 and 388 for the toe, 66, 71 and 78 for the reeds); a point test reads its strip and the edges in it, the typical strip about 6 of the outline's edges and 4 of the toe's or the reeds'; densest case from a smallest side of 64 ft, a strip holding 33 of the outline's edges at 40 where its lobes run along the strip
- the dry plots: cells of 64 ft, each plot filed in the cells its box covers (605, 948 and 1,570 filings, about 6.3 a plot, its sides about 72 ft); the back's rectangle - 2.6 band depths by one, 439 by 169 ft at 20, 603 by 232 at 40, 780 by 300 at 80 - covers (439 / 64 + 1) x (169 / 64 + 1) = 29, 48 and 75 cells, holding 29 x 2.7 / 6.3 = 12, 21 and 32 distinct plots, each clipped to it (8); the hem reads the 9 cells round a margin, ring by ring, and stops at the first ring past the nearest edge (out to two band depths, about 6 rings at 40, where no hem stands near); densest case from a smallest side of 64 ft, 6 plots in one cell
- the way out: cells of 64 ft, the walls (the outline, the toe, the reeds and the pond's 16-point ring: 208, 256 and 324 edges, about 2 cells each) and every watercourse segment (1,095, 1,504 and 2,022 filings) filed in the cells they cross; a straight run off the canvas crosses half the canvas, 50, 70 and 98 cells, holding about 0.1 items a cell (about 2,000 filings over about 19,300 cells at 40); densest case from a smallest side of 64 ft, a cell where the brook and a ditch meet

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
| the dry plots' cells | per item | 29 at 20, 48 at 40, 75 at 80 | the cells the back's rectangle covers (the Indexes) | always these |
| the back's clear ground | per item | 96 at 20, 168 at 40, 256 at 80 | 12, 21 and 32 plots in those cells, each clipped to the rectangle (8) | a margin backing onto the dry hem, 6 plots a cell |
| margins passing every refusal | over the run | 13 at 20, 17 at 40, 36 at 80 | the chosen margin and its ladder, measured on the reference seats | every candidate passing |
| the dry plots' cells round each passing margin | over the run | 9 a passing margin | the hem's first ring | about 6 rings out to two band depths where no hem stands near |
| the hem | over the run | 97 a passing margin | 9 cells of 2.7 plots of 4 edges, each an edge's distance | the hem within two band depths |
| the brook on the band | over the run | 180 at 20, 180 at 40, 195 at 80, a passing margin | 15 points (the knob), each 9, 9 or 10 bisection steps and 3 segments | the brook across the band |
| the score | over the run | 7 a passing margin | its seven terms: the wind, the upslope end, the reeds' share, the hem, the back, the belt's room and the brook's tie-break | always 7 |
| the ranking | over the run | 52 at 20, 85 at 40, 216 at 80 | the passing margins sorted, n log n: 13 x 4, 17 x 5, 36 x 6 | every candidate passing |
| the plan read and the band's size | once | 7 | the five plan fields and the two half-extents | always 7 |
| the margins' scan | once | 136 at 20, 192 at 40, 270 at 80 | each outline point's normal and turn against the wind (2 a point) | the typical field |
| the outline's strips filed | once | 102 at 20, 143 at 40, 201 at 80 | each edge in the strips it spans, measured | the typical field |
| the toe's strips filed | once | 204 at 20, 280 at 40, 388 at 80 | each edge in the strips it spans, measured | the typical toe |
| the reeds' strips filed | once | 66 at 20, 71 at 40, 78 at 80 | each edge in the strips it spans, measured | a pond roll |
| the dry plots read | once | 380 at 20, 609 at 40, 1,003 at 80 | each plot's points | the typical hem |
| the dry plots' cells filed | once | 605 at 20, 948 at 40, 1,570 at 80 | each plot in the cells its box covers, measured | the typical hem |
| the brook read | once | 324 at 20, 450 at 40, 632 at 80 | each station read once in its order | the typical brook |
| the way out's walls filed | once | 416 at 20, 512 at 40, 648 at 80 | 208, 256 and 324 edges in about 2 cells each | a pond roll |
| the way out's water filed | once | 1,095 at 20, 1,504 at 40, 2,022 at 80 | each watercourse segment in the cells it crosses, measured | the typical map |
| the way out's cells | once | 150 at 20, 280 at 40, 784 at 80 | the straight runs tried, measured (3, 4 and 8 on the mean), each 50, 70 or 98 cells | sixteen runs walled |
| the way out's items | once | 15 at 20, 28 at 40, 78 at 80 | about 0.1 a cell along those runs | as above |
| the way out's walk | once | 0 at 20, 0 at 40, 6,200 at 80 | where no run is clear, the walk of the 20 ft cells toward the nearest edge - one seat in four at 80 (seed 47, 4,964 ft from its nearest edge): 248 steps of 20 ft, each step testing its new neighbors, 5 of the 8 a cell on a walk aimed at the edge, each test the 9 reach cells round it read, the 4 wall and water edges in them asked and the 4 walls' strips (about 20), so 248 x 5 x 20 = 24,800, a quarter of it on the mean | a seat walled in on the way to every edge: every 20 ft cell of the canvas tested once, about 394,000 at 80, the walk's cells remembered across margins so no cell is tested twice |
| the fords | once | 689 at 20, 956 at 40, 1,343 at 80 | each station's bend tested (2 a station) and a ford written each 160 ft of brook (the knob: 41, 56, 79) | the typical brook |
| the watercourses gathered | once | 488 at 20, 643 at 40, 857 at 80 | each segment listed for the ways (487, 642, 856) and the crossing cost set (1) | the typical map |
| the frames written | once | 107 at 20, 139 at 40, 291 at 80 | 8 for each passing margin, and the flag, the skeleton and the face (3) | every candidate passing |
| slack | per item | 1 | every factor is a count of the stage's own inputs | not applicable |

So: items x (10 + 21 + 8 + 54 + 40 + the back's cells + the back's plots) x slack + the passing margins x (9 + 97 + the brook on the band + 7) + the ranking + each once term.

## Totals

- at 20: 37 x (10 + 21 + 8 + 54 + 40 + 29 + 96) x 1 + 13 x (9 + 97 + 180 + 7) + 52 + 7 + 136 + 102 + 204 + 66 + 380 + 605 + 324 + 416 + 1095 + 150 + 15 + 0 + 689 + 488 + 107 = 18191
- at 40: 53 x (10 + 21 + 8 + 54 + 40 + 48 + 168) x 1 + 17 x (9 + 97 + 180 + 7) + 85 + 7 + 192 + 143 + 280 + 71 + 609 + 948 + 450 + 512 + 1504 + 280 + 28 + 0 + 956 + 643 + 139 = 30325
- at 80: 74 x (10 + 21 + 8 + 54 + 40 + 75 + 256) x 1 + 36 x (9 + 97 + 195 + 7) + 216 + 7 + 270 + 201 + 388 + 78 + 1003 + 1570 + 632 + 648 + 2022 + 784 + 78 + 6200 + 1343 + 857 + 291 = 62012

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.89 (18,191 to 62,012): the candidates with the outline's points
(37 to 74), the back's cells and plots with the band's depth squared (x2.6), the plots and the brook with the field and the canvas,
the passing margins x2.8, and the way out with the canvas (the walk where a seat needs it). The stage is a seat and its ladder, not one seat: about 1,800 operations a passing margin at 40 (its refusals and its score, the 53 candidates' refusals shared over the 17 it ranks) and the map-wide indexes (about 6,000 at 40) every margin asks. No loop over a growing set runs inside another: each candidate's tests
read cells and strips, never the whole of a ring; the way out's walk remembers every cell it has tested and every cell it has found joined to an edge or walled in, across the margins the head falls back to, so the whole run tests each cell of the canvas at most once.

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

## Cheaper algorithms considered

- sweep: used - one pass over the outline's points for the margins; the brook walked once for its fords
- grid or spatial index: used - strips for the outline, the toe and the reeds; cells for the dry plots, the hem, the way out's walls and the water; the brook's own order along the fall for its nearest segments
- priority queue: not used - every passing margin is scored, because the ladder is the whole ranking; a bound-ordered search would stop at the chosen seat and leave the ladder unranked
- incremental update: not used - one seat and its ladder
- memoizing what a scan does not change: used - every index built once for all the candidates; the way out's walk remembers its cells across the margins
- pruning: the cheapest refusals first (the frame, the toe, open ground, the reeds) before the back's cells; the hem's search stopped at the first ring past its nearest edge; the way out stopped at the first clear run, its walk aimed at the nearest edge and stopped at the first cell off the canvas
