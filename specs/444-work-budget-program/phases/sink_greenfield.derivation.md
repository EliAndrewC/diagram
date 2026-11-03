# Derivation - sink, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan's sink form (where the field's runoff ends: on the reference spec a pond); the field's outline, its area, and its drain - the one ditch carrying its runoff off the field; the brook; the plan's drainage bearing; the resting basins and the dikes a run may not cross (0060's run onward never through the rice; a dike crossed only at a gap, 0019).
- Writes: the pond where the drain ends, an ellipse (its center and two radii), with its outlet on the drain, and its wet shore and reeds as one layer record; the ditch from the drain's outfall to the pond (0060: the drain "runs on as a ditch ... to the pond at the field's foot"); the pond and the ditch filed in the overlap registry every later stage asks.
- Keeps: one outlet (0061: "the maps draw one outlet and one main ditch leaving it"); its area in proportion to the paddy it serves, and smaller where a stream tops it up (0061: "A pond that a stream keeps topping up is drawn smaller"); outside the field and clear of the brook; reeds and the wet tint kept off its embankment (0061), a drawing of its record, not a search.
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the pond 189 by 121 ft and 268 by 171 ft across (x1.41 in each radius a doubling, its area a share of the field's: 17,978 sq ft of 571,276 at 10, 35,957 of 1,210,473 at 20, about 3%: 378 by 241 ft at 40, 535 by 341 ft at 80); outside the field on both (none of 16 sampled shore points inside its outline); the drain one ditch, 6 and 10 points; the typical densities (`items.md`, rubric S8): water segments 3.7 and the field's outline segments 1.8 a crossed 64 ft cell. Measured 2026-11-03 on the reference rolls at 20, 40 and 80 households (seeds 4, 25, 39, 47, the field's output): the outline 68, 96 and 135 points, 4,278, 6,050 and 8,557 ft round, about 63 ft a segment; the brook 324, 449 and 632 stations, 20 ft apart, and on every roll falling the whole way along the fall (each station no higher than the one before, 0054's water only downhill); the field 1,132,560, 2,265,120 and 4,530,240 sq ft inside its outline.

## The algorithm

    the sink's form read from the plan (1); on a pond:
    the pond's area: the field's area read (1) times the share (1); its two radii from the area and the plan's aspect (2)
    the drain's last point and its heading read (2)
    the field's outline read once (1 a point), its segments lying below the outfall across the fall kept - the only ones a
        pond below the outfall can meet
    the pond's seat beyond the drain's last point along its heading, by its own half-length (1), tested:
        the brook's stations whose place along the fall lies within the pond's box found by bisection at each end of that
            range (log2 of the stations, twice) - the brook falls the whole way, so its stations stand in order along the fall -
            and each station's segment in the range tested against the pond grown by its margin (1 each)
        the kept outline segments facing the box tested against the pond (1 each)
        the drain's last segment tested (1)
        refused, the seat steps one half-length on along the drainage bearing and is tested again
    written: the pond, its outlet where the drain meets its shore, the layer record (3)
    the ditch from the outfall to the pond's center: three points, bowed off the chord (3); its legs tested against the
        brook's segments along it, inside the range the seat's bisections found (1 each); run downhill (1); its turn at the
        outfall (1)
    the reeds: a ring at the shore, 44 ft out (0061's reeds; the width a GUESS), written at 24 points (24)
    filed in the overlap registry: the ditch's two legs, each a ribbon of 4 corners and its box of 4 (8 each); the pond's rim
        read at 24 points for its box (24), the box binned in the registry's 64 ft cells (1 each)

## Indexes

- the overlap registry: cells of 64 ft, the pond's box binned in the cells it covers; densest case from a smallest side of 64 ft, the pond's 171 ft side at 20

No grid of the brook: its stations stand in order along the fall (it falls the whole way, the Bounds), so a range of the fall is found by bisection, log2 of the stations (324, 449 and 632: 9, 9 and 10 halvings), with nothing built.

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the pond, once a map | always 1 |
| the form, the area and the drain | per item | 7 | the form read (1), the field's area and the share (2), the two radii (2), the drain's last point and heading (2) | always 7 |
| the outline read once | per item | 68 at 20, 96 at 40, 135 at 80 | its points, one read each (the Bounds' 68, 96, 135); the segments below the outfall kept as they are read | always |
| slack | per item | 2 | on the seat's test alone: a seat refused on the brook steps on once more | a brook close under the field's toe |
| the seat's test | per item | 33 at 20, 37 at 40, 47 at 80 | the brook's range found by two bisections, 2 x 9, 9, 10 = 18, 18, 20; the brook's segments in the range, the box's depth along the fall over the 20 ft stations, 171/20, 241/20, 341/20 to the nearest = 9, 12, 17, each tested (1); the kept outline segments facing the box, its long side over the outline's 63 ft segments, 268/63, 378/63, 535/63 rounded up = 5, 6, 9, each tested (1); the drain's last segment (1): 18 + 9 + 5 + 1 = 33, 18 + 12 + 6 + 1 = 37, 20 + 17 + 9 + 1 = 47 | a brook close under the toe |
| the writes | per item | 3 | the pond, its outlet and its layer | always |
| the ditch to the pond (missed work) | per item | 12 at 20, 14 at 40, 18 at 80 | its 3 points written (3); its run the pond's own half-length from the outfall to the center (134, 189 and 268 ft), inside the range of the brook the seat's bisections found (no search of its own), the brook's segments along it, 134/20, 189/20, 268/20 to the nearest = 7, 9, 13, each tested (1); downhill (1); the turn at the outfall (1): 3 + 7 + 1 + 1 = 12, 3 + 9 + 1 + 1 = 14, 3 + 13 + 1 + 1 = 18 | a brook beside the toe |
| the reeds' ring (missed work) | per item | 24 | the ring written at the 24 points the pond's rim is drawn at (0061: reeds at the shore) | always 24 |
| the overlap registry (cells written; missed work) | per item | 59 at 20, 73 at 40, 99 at 80 | the ditch's 2 legs filed as ribbons, 4 corners and a box of 4 each (16); the pond's rim read at 24 points for its box (24); that box binned in the registry's 64 ft cells, (1 + 268/64)(1 + 171/64) = 19 at 20, 33 at 40, 59 at 80 | always |

So: 1 x (7 + the outline + the seat's test x 2 + the writes + the ditch + the reeds + the registry).

## Totals

- at 20: 1 x (7 + 68 + 33 x 2 + 3 + 12 + 24 + 59) = 239
- at 40: 1 x (7 + 96 + 37 x 2 + 3 + 14 + 24 + 73) = 291
- at 80: 1 x (7 + 135 + 47 x 2 + 3 + 18 + 24 + 99) = 380

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.34 (239 to 380): one pond, the outline's points and its box's cells growing with the field's breadth, beside the reeds' fixed 24.

## Work the first derivation missed

Feature 444 FR-022 rule 2 (amendment 7, the GM 2026-11-03): each item is work the contract owes that the first count left out.

- the ditch from the drain's outfall to the pond - the contract's run onward (0060: the drain "runs on as a ditch ... to the pond at the field's foot"); the first count placed the pond and its outlet but drew no run to it
- the reeds' ring at the shore - the contract's "its wet shore and reeds as one layer record" (0061); the first count wrote the record and priced none of its points
- the field's outline read for its stretch below the outfall, and the brook found by its order along the fall - the first count read both from a water index the field filed, which does not outlive the field's stage: no index of the field's is handed to the stages after it, so the sink reads what it needs itself
- the stage's records filed in the overlap registry - every later stage asks the registry before it places (the overlap matrix: a house, a lane or a tree kept off the water), so the pond and its ditch are filed there as they are written; the first count filed the pond only in the water index

Outside the reference roll, and so in no figure above: the off-map branch (the plan's sink rolled off-map, or a pond with no seat inside the set-back - 0060's "about one hamlet map in three"), which joins the passing brook where it is in reach or runs the drain off the map; the reference spec pins its sink a pond. It is held to rubric S1-S9 by its design - its candidates the bearings round the fall and the collector's heading at the junction distances the canvas allows, nearest first, the first that keeps every rule taken (S9); each candidate asked of the water index's cells it crosses (S1) - and to every rule by the Rust stage gate's fresh block, which rolls it.

## Earlier findings

- verdict-2, finding 1: fixed - the stream-topped pond's smaller share is the share read once in the 7 row (0060's drainage pond at about 3/100 of its paddy, below 0061's watering pond); the outline cells are taken along the box's long side, the larger count
- verdict-1, finding 1: fixed - each cell under the box read alone, segments charged only in the cells the outline and the drain cross (5, 7, 9 outline cells at 1.8; the drain's 2 cells at 3.7): 36, 53 and 83
- verdict-1, finding 2: fixed - the row recomputed from its cells, no 6.5 product left

## Cheaper algorithms considered

- sweep: not used - one seat is tested
- grid or spatial index: the brook's own order along the fall in place of a grid (bisection, no index built); the registry's 64 ft cells for the filing
- priority queue: not used - the seats are taken in order along the drain, the first clear kept
- incremental update: not used - one pond is placed
- memoizing what a scan does not change: used - the outline is read once and its low segments kept for every seat tested
