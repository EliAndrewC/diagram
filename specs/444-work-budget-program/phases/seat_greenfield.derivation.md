# Derivation - seat, greenfield (feature 444 FR-015; revised under FR-022 rule 2, 2026-11-04)

## Contract

- Reads: the field's outline; the plan's fall, wind, settlement form, the cluster's shape and the households; the dry plots; the brook's course; the wet toe below the fields and a tail pond's reed fringe; the pond and the drain's run off it; every watercourse on the map - the field's ditches, the farm channels as drawn and the brook - for the ways' routing and for the seat's way out.
- Writes: where the settlement sits - the cluster's band on a margin of the field, its center, its long and short axes, its anchor and whether its back is off the wind - with the ranked margins after it, the ladder the house seating falls back down when the chosen margin cannot seat every household; the brook's fords, the only places a way may cross it, and the cost every later way pays to cross; the list of watercourses every later way is routed against; the side of the field the houses stand on. Drawn nowhere.
- Keeps: a village's cluster sits on the higher, drier ground beside its paddy (0031: "On the higher, drier ground beside its paddy, as old settlements stood on the natural levee"), its back to the wind (0072: a clustered village shelters behind one belt at its windward edge), so the belt's band is kept on the canvas before any house is seated; the band stands on open ground, off the field, its back clear of the dry crop; never on the wet toe below the fields (0058: "seat and anchor off the marsh below the fields"); never centered in a pond's reed fringe (the GM's ruling of 2026-08-28), an end in it scored down; the brook across the band scored down, never refused (0035: "a site the brook does not cross is still preferred when two are otherwise level"); the seat has a dry way out of the frame (0081: lanes keep to dry ground); a way crosses the brook only at a ford, opened on a straight reach (0035).
- Bounds (measured 2026-11-04, `make stage-sizes STAGE=seat` on the reference rolls, with the wet toe below the fields as the roll derives it, seeds 4, 25, 39, 47, the mean over the seeds that reach the seat): the field's outline 68, 96 and 135 points at 20, 40 and 80 households, of whose margins 37, 53 and 74 face within 90 degrees of the wind; the dry plots 95, 152 and 251, at 380, 609 and 1,003 points; the brook 324, 450 and 632 stations, 20 ft apart; the wet toe 71, 90 and 118 points; the reed fringe 52, 54 and 54 points; the watercourses 487, 642 and 856 segments; the canvas 6,400, 8,900 and 12,550 ft square. On the reference rolls' finished seats (`make stage-sizes STAGE=waterward DUMP=`, the seat as the next stage is handed it): the band's half-depth 152 to 300 ft and half-length 389 to 918 ft, and the ranked margins that pass every refusal 13, 17 and 36 (the chosen one and its ladder, the mean).

## The algorithm

    the plan read: the form, the shape, the fall, the wind, the households (5); the band's two half-extents from the households (2)
    the indexes, once: the outline's edges filed by horizontal strip (2 an edge); the toe's and the reeds' edges the same (2 an edge);
      each dry plot's points read and the plot filed in the cells it covers (a point read each, 1.5 cells a plot); the brook read
      once in its order along the fall (1 a station); the walls of the way out (the toe, the reeds, the outline and the pond's ring)
      and every watercourse segment filed in cells (1.5 cells each)
    the margins: each outline edge's midpoint, outward normal and its turn against the wind (2 a point); a margin facing within 90
      degrees of the wind is a candidate, its back the normal, or turned to the wind off a flank
    for each candidate, the refusals, cheapest first:
      the band's center inside the frame, the belt's 15 sample points on the canvas (17)
      the wet toe at the anchor and the center (2 tests, a strip each)
      the band on open ground: 9 sample points tested against the outline (a strip read and its crossing edges each)
      the reeds: the center refused in them, 9 points for the share of the band in them (10 tests)
      the back's clear ground: 21 points behind the margin tested against the dry plots in their cells
    for each candidate that passes, the score:
      the nearest dry-plot edge within two band depths, from the cells round the margin (the hem)
      the brook on the band: 15 points each asked the brook's nearest segment within 30 ft, the segments found by bisection on
        the brook's order along the fall
      the score itself: the wind, the upslope end, the reeds' share, the hem, the back, the brook, the belt's room (6)
    the passing margins ranked by score, the first met winning a tie
    the head's dry way out: straight runs off the canvas tried every 22.5 degrees, each run asked the cells it crosses of the walls
      and the watercourses, until one is clear; the ranked list's next margin taken where the head has none
    the fords: the brook walked station by station, a ford opened on each straight reach at its spacing (2 a station, a write a ford)
    the crossing cost set once; the watercourses gathered for the ways (1 a segment)
    written: the seat's frame for each passing margin (8 each), the off-wind flag, the skeleton and the field's face (3)

## Indexes

- the outline, the toe and the reeds: cells of 64 ft, each a horizontal strip, every edge filed in the strips it spans (measured 2026-11-04 on the seat's input, `make stage-sizes STAGE=seat DUMP=`: 102, 143 and 201 filings for the outline at 20, 40 and 80, 204, 280 and 388 for the toe, 66, 71 and 78 for the reeds); a point test reads its strip and the edges in it, the typical strip about 6 of the outline's edges and 4 of the toe's or the reeds'; densest case from a smallest side of 64 ft, a strip holding 33 of the outline's edges at 40 where its lobes run along the strip
- the dry plots: cells of 64 ft, each plot filed in the cells its box covers (605, 948 and 1,570 filings, about 6.3 a plot, its sides about 72 ft); a point behind a margin reads its one cell and the plots in it, about 2.7 plots of 4 edges; the hem reads the 9 cells round a margin, ring by ring, and stops at the first ring past the nearest edge; densest case from a smallest side of 64 ft, 6 plots in one cell
- the way out: cells of 64 ft, the walls (the outline, the toe, the reeds and the pond's 16-point ring: 208, 256 and 324 edges, about 2 cells each) and every watercourse segment (1,095, 1,504 and 2,022 filings) filed in the cells they cross; a straight run off the canvas crosses half the canvas, 50, 70 and 98 cells, about one item a cell; densest case from a smallest side of 64 ft, a cell where the brook and a ditch meet

No grid of the brook: its stations stand in order along the fall (measured 2026-11-03 on the reference rolls: each station no higher than the one before), so a point's nearby segments are found by bisection, 9, 9 and 10 halvings at 324, 450 and 632 stations, with about 3 segments within 30 ft.

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 37 at 20, 53 at 40, 74 at 80 | the margins facing within 90 degrees of the wind, each a candidate seat | every edge on the windward half |
| the frame and the belt's room | per item | 17 | the center's two bounds and the belt's 15 sample points on the canvas | always 17 |
| the outline, the toe and the reeds' cells | per item | 21 | the strips read: the toe's 2 tests, open ground's 9, the reeds' 10 | always 21 |
| the wet toe | per item | 8 | the anchor and the center, 4 edges each in their strips | the toe reaching the margin |
| open ground | per item | 54 | 9 band points, 6 of the outline's edges each in their strips | the outline's lobes beside the margin, up to 33 an edge strip |
| the reeds | per item | 40 | the center and 9 band points, 4 edges each in their strips | a pond roll; a brook-sink roll has no fringe |
| the dry plots' cells | per item | 21 | the cell under each of the 21 points behind the margin | always 21 |
| the back's clear ground | per item | 227 | 21 points, each 2.7 plots of 4 edges in its cell | a margin backing onto the dry hem, 6 plots a cell |
| margins passing every refusal | over the run | 13 at 20, 17 at 40, 36 at 80 | the chosen margin and its ladder, measured on the reference seats | every candidate passing |
| the dry plots' cells round each passing margin | over the run | 9 a passing margin | the hem's 9 cells | always 9 |
| the hem | over the run | 97 a passing margin | 9 cells of 2.7 plots of 4 edges, each an edge's distance | the hem within two band depths |
| the brook on the band | over the run | 180 at 20, 180 at 40, 195 at 80, a passing margin | 15 points, each 9, 9 or 10 bisection steps and 3 segments | the brook across the band |
| the score | over the run | 6 a passing margin | its six terms | always 6 |
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
| the way out's cells | once | 100 at 20, 140 at 40, 196 at 80 | 2 straight runs tried, each 50, 70 or 98 cells | the first run walled; a seat walled in on every bearing asks the canvas's flood fill, outside the reference rolls |
| the way out's items | once | 100 at 20, 140 at 40, 196 at 80 | about one wall or watercourse a cell along the 2 runs | as above |
| the fords | once | 689 at 20, 956 at 40, 1,343 at 80 | each station's bend tested (2 a station) and a ford written each 160 ft of brook (41, 56, 79) | the typical brook |
| the watercourses gathered | once | 488 at 20, 643 at 40, 857 at 80 | each segment listed for the ways (487, 642, 856) and the crossing cost set (1) | the typical map |
| the frames written | once | 107 at 20, 139 at 40, 291 at 80 | 8 for each passing margin, and the flag, the skeleton and the face (3) | every candidate passing |
| slack | per item | 1 | every factor is a count of the stage's own inputs | not applicable |

So: items x (17 + 21 + 8 + 54 + 40 + 21 + 227) x slack + the passing margins x (9 + 97 + the brook on the band + 6) + the ranking + each once term.

## Totals

- at 20: 37 x (17 + 21 + 8 + 54 + 40 + 21 + 227) x 1 + 13 x (9 + 97 + 180 + 6) + 52 + 7 + 136 + 102 + 204 + 66 + 380 + 605 + 324 + 416 + 1095 + 100 + 100 + 689 + 488 + 107 = 23023
- at 40: 53 x (17 + 21 + 8 + 54 + 40 + 21 + 227) x 1 + 17 x (9 + 97 + 180 + 6) + 85 + 7 + 192 + 143 + 280 + 71 + 609 + 948 + 450 + 512 + 1504 + 140 + 140 + 956 + 643 + 139 = 32347
- at 80: 74 x (17 + 21 + 8 + 54 + 40 + 21 + 227) x 1 + 36 x (9 + 97 + 195 + 6) + 216 + 7 + 270 + 201 + 388 + 78 + 1003 + 1570 + 632 + 648 + 2022 + 196 + 196 + 1343 + 857 + 291 = 49682

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.55 (23,023 to 49,682): the candidates with the outline's points (x1.41 over the
two doublings, 37 to 74), the plots and the brook with the field and the canvas (x2.6 and x2.0), the passing margins x2.8. No loop
over a growing set runs inside another: each candidate's tests read cells and strips, never the whole of a ring.

## Work the first derivation missed

Feature 444 FR-022 rule 2 (amendment 7, the GM 2026-11-03): each item is work the contract owes that the first count left out. The
first count priced one pass over the outline for its highest point; the contract the seat keeps holds all of the following.

- the candidates' refusals - the band on open ground, off the field; its back clear of the dry crop; the band and its belt on the canvas; never on the wet toe; never centered in the reeds (0031, 0072, 0058 and the GM's ruling of 2026-08-28): the first count chose the highest point and tested no seat against any of them
- the score's terms beyond height - the wind first (0072: the back to the wind), the dry hem and the back's crop, the reeds' share, the brook across the band (0035), the belt's room: the first count scored height alone
- the ladder - every margin that passes, ranked, which the house seating falls back down when the chosen margin cannot seat every household: the first count wrote one seat
- the dry way out of the frame (0081): a seat walled in by the wet, the field and the water is refused, and the next margin taken
- the brook's fords and the crossing cost (0035: a way crosses the brook only at a ford, opened on a straight reach), which the seat opens before any way is routed
- the watercourses gathered for every later way, the brook gapped at its fords
- the indexes each of these reads, built once: nothing a stage before the seat files outlives it, so the seat files what it asks

## Earlier findings

- verdict-1, finding 1: fixed - its SOUND judged one pass over the outline for the highest margin, the whole of the first count; that count is kept as the margins' scan above, and the work the contract owes beyond it is priced under `## Work the first derivation missed`

## Cheaper algorithms considered

- sweep: used - one pass over the outline's points for the margins; the brook walked once for its fords
- grid or spatial index: used - strips for the outline, the toe and the reeds; cells for the dry plots, the hem, the way out's walls and the water; the brook's own order along the fall for its nearest segments
- priority queue: not used - every passing margin is scored, because the ladder is the whole ranking; a bound-ordered search would stop at the chosen seat and leave the ladder unranked
- incremental update: not used - one seat and its ladder
- memoizing what a scan does not change: used - every index built once for all the candidates
- pruning: the cheapest refusals first (the frame, the toe, open ground, the reeds) before the back's 21 points; the hem's search stopped at the first ring past its nearest edge; the way out stopped at the first clear run
