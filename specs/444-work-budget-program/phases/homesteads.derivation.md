# Derivation - homesteads (feature 444)

## Contract

- Reads: the seat frame (`plan.seat`), the canvas, and everything the map holds before the houses - the paddy's outline, the dry hem, the marshes, the ponds, the dry plots, the no-build ground, the water courses and the registered corridors - as the site boundary; the household count; the homestead program (`household_parts`: the house, its yard, garden and beds, kura, sheds, fixtures, retirement house, persimmon).
- Writes: every declared household's homestead, its parts recorded (`record_parts`); the cluster's declared shape; the way out's gate; and each household's way, laid in the gaps once the last house stands (`gap_ways.lay_the_ways`), its legs reserved and recorded as its access corridor (`access_corridors`, one record a leg).
- Keeps: every declared household seated or the site refused (0001; `seat_every_household`); no lane before the houses, no path searched while a house is seated (0246); every two homesteads parted by a lane's threading gap, 20 ft (`grow_gap`: 7 ft off each garden fence and the 4 ft tread, 0246, and the 2 ft parting); a way's line 7 ft off each homestead (`ACCESS_HALF_FT`), so the gap leaves it a band of 20 - 2 x 7 = 6 ft; a yard's south sun clear 39 ft (`SUN_CORRIDOR_FT`, 0038) and the belt's afternoon lane 50 ft (`WEST_SUN_FT`, 0038); a yard opens onto lane ground (`SeatRegion.opens`); a way joins a laid one within 25 ft (`JOIN_FT`); a household no way reaches is reached across its nearest reached neighbor's yard (the pinch, 0246); every rule asked of a seat before its homestead is placed (S4). The cohort's checks: each part's footprint against the overlap matrix (`overlap/`), every house reached by a way.
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): houses one a household; a homestead's parts at most 11 at 10 and 13 at 20 (13 taken); a homestead's extent at most 163 and 184 ft (184 taken); a part's longest side at most 61 and 63 ft (the threshing yard; 63 taken, under 64 ft); at most 6 and 7 placed parts in one 64 ft cell (7 taken); at most 20 and 8 site-boundary segments in one 32 ft cell (20 taken); the canvas 1,521 by 1,726 ft and 2,274 by 2,486 ft (x2.16 in area: at 32 ft cells 5,521 at 20, 11,926 at 40, 25,759 at 80); the site boundary's segments 1,193 and 1,538 (x1.29: 1,538 at 20, 1,985 at 40, 2,560 at 80) and its length 32,437 and 50,182 ft (x1.55: 50,182 at 20, 77,783 at 40, 120,563 at 80).

## The algorithm

    rasterize the site boundary once over the canvas in 32 ft cells (`FreeGround`): each cell free, blocked, or undecided with
        the boundary segments that cross it
    index the placed parts in 64 ft cells, each part filed as it is placed
    the first house: the free cell nearest the seat's center
    while households are left: pop the next seat from a heap of offers (nearest the seat first, the field first within a ring);
        a standing house offers the 6 seats about it at the least distance: the envelope is a 184 ft square in the seat frame,
            and the seats lie on a brick lattice of pitch 204 ft (its side and the gap) - (+-204, 0) and (+-102, +-204) - the six
            squares that touch one without overlap, and the 12 of the second shell - (+-408, 0), (+-306, +-204), (+-204, +-408)
            and (0, +-408) - only where every first-shell seat of
            every standing house is refused; a seat is keyed by its 32 ft cell and offered once over the run (a refused seat
            stays refused: the boundary is fixed and the parts only accumulate)
        test the seat, every rule before anything is placed (S4): the raster cells under its envelope - a blocked or an
            undecided interior cell refuses it (a boundary segment inside the envelope meets it), and only an edge cell's
            segments are tested against the envelope; the envelope against the placed parts in its 64 ft cells; the sun's
            39 ft, the west lane's 50 ft and the yard's opening onto lane ground, each against the parts in its cells
        refused: the next offer; admitted: lay the program's parts inside the envelope, each recorded and filed (inside an
            envelope the boundary and the parts already cleared, no part is tested again)
    declare the cluster's shape; set the way out's gate on the cluster's edge
    lane ground, a sparse raster of 6 ft cells over each homestead's gap band (its envelope dilated by the 20 ft gap): each
        cell's free ground read from the 32 ft raster and its parts from the parts index
    one flood from the gate over lane ground (a bucket queue: the cheapest walk to every cell, dearer beside blocked ground)
    each household, nearest the way out first: its door opens onto lane ground (the seat's rule), so its way is traced back
        along the flood to the gate or to a laid way within 25 ft (each laid way marks lane ground's cells within 25 ft of
        it as it is laid, so the trace reads one cell a step), pulled taut, and its legs admitted against the parts
        index; reserved and recorded; a household none admits is pinched across its nearest reached neighbor's yard

## Indexes

- raster: cells of 32 ft (a GUESS: half the parts index's cell, so an envelope's edge is one cell deep and its interior cells are read, not tested); densest 20 boundary segments a cell (measured at 10 and 20, 20 and 8, the ceiling taken), from a smallest side of 32 ft
- parts index: cells of 64 ft (a part's longest side, 63 ft, is under it, so a part lies in at most 2 by 2 cells); densest 7 placed parts a cell (measured at 10 and 20, 6 and 7, the ceiling taken), from a smallest side of 64 ft
- lane ground: cells of 6 ft (the way's band, 20 - 2 x 7 ft: a cell no wider than the band, so every gap holds a cell's center); densest 1 a cell, from a smallest side of 6 ft - a cell holds one state and one flood value

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | one house a household | 80 households |
| the parts laid (parts index cells written) | per item | 65 | 13 parts, each recorded (1) and filed in at most 2 by 2 cells of 64 ft (4) | the most parts |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the seats offered | over the run | 360 at 20, 720 at 40, 1,440 at 80 | 18 a house: the 6 of the first shell and the 12 of the second, each offered once | the second shell reached for every house |
| the seat test (raster and parts index cells examined) | over the run | 831 a seat | the envelope, 184 ft, covers at most 7 by 7 cells of 32 ft, each read (49), and its 24 edge cells each with at most 20 segments tested (480); the envelope grown by the 20 ft gap, 224 ft, in at most 5 by 5 cells of 64 ft, each with at most 7 parts (200); the sun's 39 ft, the west lane's 50 ft and the opening's 20 ft, each a strip at most 63 ft long in at most 2 by 2 cells of 64 ft (32 each, 96), and the opening's 3 by 2 cells of 32 ft read for lane ground (6) | every seat at the densest cells |
| the heap | over the run | 6,480 at 20, 14,400 at 40, 31,680 at 80 | each offer pushed and popped, 2 x log2 of the offers rounded up | 80 households |
| the raster (cells written) | once | 5,521 at 20, 11,926 at 40, 25,759 at 80 | the canvas in 32 ft cells | 80 households |
| the boundary (raster cells written) | once | 6,832 at 20, 9,393 at 40, 13,009 at 80 | each boundary segment walked through the raster: its length at its diagonal over 32 ft, plus 3 a segment | 80 households |
| lane ground (cells written) | over the run | 480,180 at 20, 960,360 at 40, 1,920,720 at 80 | 453 cells a homestead - its gap band, the envelope grown by the 20 ft gap, (224 x 224 - 184 x 184) sq ft over 36 sq ft - each decided against the 32 ft raster (its cell read, 1, and where undecided its at most 20 segments tested, 20) and tested against the parts of the at most 2 by 2 cells of 64 ft a 6 ft cell straddles (32), 53 | every band unshared, every cell undecided |
| the flood (lane ground cells examined) | over the run | 235,560 at 20, 471,120 at 40, 942,240 at 80 | 26 a cell, on a bucket queue (Dial's): the step costs are small integers - 2 straight and 3 diagonal, times the center weight 1 to 3, at most 9 - so a push or a pop is one operation; each cell popped once (1), its 8 neighbors read (8), pushed at most once for each neighbor that improves it (8), and the buckets scanned once, at most 9 a cell (the costs' ceiling times the cells) | every band cell reached |
| the trace (lane ground cells examined) | over the run | 1,240 at 20, 2,480 at 40, 4,960 at 80 | 62 a household: the ways end where they join, so together they are at most the gaps' length, half each homestead's 4 x 184 ft perimeter (a gap is shared by two), over 6 ft cells, 62 | every gap walked |
| the taut pull (lane ground cells examined) | over the run | 2,480 at 20, 4,960 at 40, 9,920 at 80 | 124 a household: a funnel over the trace's at most 62 cells, each cell's two sides tested once (2) | every gap walked |
| the join mark (lane ground cells written) | over the run | 12,400 at 20, 24,800 at 40, 49,600 at 80 | 620 a household: each way's at most 62 cells, each step marking the band 25 ft either side of it, 2 x 25 / 6 + 1 rounded up, 10 cells | every gap walked |
| the admission (parts index cells examined) | over the run | 2,880 at 20, 5,760 at 40, 11,520 at 80 | 144 a household: its way, at most 368 ft, at its diagonal over 64 ft rounded up (9), plus 3 a leg at most 3 legs (a start and a turn at each of 2 corners a way passes, 9), each cell's at most 7 parts and the cell (8) | every way at the densest cells |
| the pinch (parts index cells examined) | over the run | 1,280 at 20, 2,560 at 40, 5,120 at 80 | at most one a household: one leg across a neighbor's yard, 184 ft at its diagonal over 64 ft plus 3, 7.07 rounded up to 8 cells, each with its at most 7 parts (8) | every household pinched |
| the cluster's shape and the gate | once | 567 at 20, 1,288 at 40, 2,889 at 80 | the hull of the envelopes' 4 corners a house, a sort of 4 x n points, 4 x n x log2 rounded up; the gate a binary search by bearing on the hull's at most 4 x n edges toward the way out, log2 rounded up | 80 households |

So: houses x 65 x 1, plus the seats offered x 831, the run's other terms and the raster once.

## Totals

- at 20: 20 x 65 x 1 + 360 x 831 + 6480 + 5521 + 6832 + 480180 + 235560 + 1240 + 2480 + 12400 + 2880 + 1280 + 567 = 1055880
- at 40: 40 x 65 x 1 + 720 x 831 + 14400 + 11926 + 9393 + 960360 + 471120 + 2480 + 4960 + 24800 + 5760 + 2560 + 1288 = 2109967
- at 80: 80 x 65 x 1 + 1440 x 831 + 31680 + 25759 + 13009 + 1920720 + 942240 + 4960 + 9920 + 49600 + 11520 + 5120 + 2889 = 4219257

## Earlier findings

- verdict-1, finding 1: fixed - the seats are the 6 of the least distance and the 12 of its second shell, from the geometry, no longer `GROW_LEVELS`
- verdict-1, finding 2: fixed - an undecided interior cell refuses the seat and only the 24 edge cells' segments are tested, at the measured 20 a cell
- verdict-1, finding 3: fixed - a part's longest side, 63 ft, is a measured Bound, and the 64 ft cell follows from it
- verdict-1, finding 4: fixed - the sun's, the west lane's and the opening's rules read their regions' cells, charged in the seat test
- verdict-1, finding 5: fixed - the ways' lane ground, flood, trace, admission and pinch are counted, each its own row
- verdict-1, finding 6: fixed - the envelope is cleared against the boundary and the parts before anything is placed; a part inside it needs no test
- verdict-1, finding 7: fixed - a seat is keyed by its 32 ft cell and offered once over the run
- verdict-1, finding 8: fixed - the ways are bounded by the gaps' length, linear in the households, not by today's segments
- verdict-1, finding 9: fixed - an access corridor record is a way's leg (19 of the 51 at 20 name a household); the legs are counted in the admission
- verdict-1, finding 10: fixed - the heap charges a push and a pop
- verdict-2, finding 1: fixed - the taut pull is a funnel over the trace's cells, its own row
- verdict-2, finding 2: fixed - the cluster's shape (a hull of the envelopes' corners) and the gate are a once row
- verdict-2, finding 3: fixed - the flood runs on a bucket queue, and a cell is pushed at most once for each improving neighbor, 8
- verdict-2, finding 4: fixed - the seat's parts query is the envelope grown by the 20 ft gap, 5 by 5 cells, 200
- verdict-2, finding 5: fixed - the opening's strip is 2 by 2 cells of 64 ft, 32
- verdict-2, finding 6: fixed - lane ground counts the dilation's corners, 453 cells a homestead
- verdict-2, finding 7: fixed - the pinch is 8 cells, 7.07 rounded up
- verdict-3, finding 1: fixed - the 25 ft join is marked on lane ground as each way is laid, its own row, so the trace reads one cell a step
- verdict-3, finding 2: fixed - the envelope is a 184 ft square and the seats are a brick lattice of pitch 204 ft, the offsets stated
- verdict-3, finding 3: fixed - the gate is a binary search by bearing on the hull's edges
- verdict-3, finding 4: fixed - a lane-ground cell is decided against the undecided raster cell's 20 segments, and tested against the 2 by 2 cells of 64 ft it straddles
- verdict-3, finding 5: fixed - the summary line reads 831
- verdict-3, finding 6: fixed - the admission is 144 a household

## Cheaper algorithms considered

- sweep: not used - the growth offers seats from the houses standing, not in a fixed order a sweep could follow
- grid or spatial index: used - the raster refuses blocked ground, the parts index bounds a seat's and a way's neighbors, and lane ground is the flood's grid
- priority queue: used - the offers on a heap, and the flood on a bucket queue (its step costs are small integers)
- incremental update: used - the parts index is filed as each part is placed; lane ground is built once, after the last house
- memoizing what a scan does not change: used - the boundary is rasterized once, and each seat is offered once over the run
