# Derivation - sink, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan's sink form (where the field's runoff ends: on the reference spec a pond); the field's outline, its area, and its drain - the one ditch carrying its runoff off the field; the brook; the plan's drainage bearing.
- Writes: the pond where the drain ends, an ellipse (its center and two radii), with its outlet on the drain, and its wet shore and reeds as one layer record; the pond filed in the water index.
- Keeps: one outlet (0061: "the maps draw one outlet and one main ditch leaving it"); its area in proportion to the paddy it serves, and smaller where a stream tops it up (0061: "A pond that a stream keeps topping up is drawn smaller"); outside the field and clear of the brook; reeds and the wet tint kept off its embankment (0061), a drawing of its record, not a search.
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the pond 189 by 121 ft and 268 by 171 ft across (x1.41 in each radius a doubling, its area a share of the field's: 17,978 sq ft of 571,276 at 10, 35,957 of 1,210,473 at 20, about 3%: 378 by 241 ft at 40, 535 by 341 ft at 80); outside the field on both (none of 16 sampled shore points inside its outline); the drain one ditch, 6 and 10 points; the typical densities (`items.md`, rubric S8): water segments 3.7 and the field's outline segments 1.8 a crossed 64 ft cell.

## The algorithm

    the sink's form read from the plan (1); on a pond:
    the pond's area: the field's area read (1) times the share (1); its two radii from the area and the plan's aspect (2)
    the drain's last point and its heading read (2)
    the pond's seat beyond the drain's last point along its heading, by its own half-length (1): its box's cells of the water
        index tested against the brook's and the field's outline segments in each (each segment 1, the cell 1); refused, the
        seat steps one half-length on along the drainage bearing and is tested again
    written: the pond, its outlet where the drain meets its shore, the layer record (3); filed in the water index's cells its
        box covers (1 each)

## Indexes

- water index: cells of 64 ft, the brook's, the ditches' and the field's outline segments filed by the field; the mean 3.7 water and 1.8 outline segments a crossed cell, an uncrossed cell read alone (`items.md`, rubric S8), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the pond, once a map | always 1 |
| the form, the area and the drain | per item | 7 | the form read (1), the field's area and the share (2), the two radii (2), the drain's last point and heading (2) | always 7 |
| slack | per item | 2 | on the seat's test alone: a seat refused on the brook steps on once more | a brook close under the field's toe |
| the seat's test (water index cells examined) | per item | 36 at 20, 53 at 40, 83 at 80 | the pond's box over 64 ft cells, (1 + 268/64)(1 + 171/64) = 19 at 20 (33 at 40, 59 at 80), each cell read (1); segments only where one crosses: the field's outline along the box's side facing the field, 1 + 268/64 = 5 cells at 20 (7, 9) at the mean 1.8 (9, 12, 17), and the drain's last segment in its about 2 cells at the mean 3.7 (7); the brook under no cell at the typical case (the slack's case); one seat, the drain's end lying outside the field by construction | a brook close under the toe |
| the writes (water index cells written) | per item | 22 at 20, 36 at 40, 62 at 80 | the pond, its outlet and its layer (3), and the pond filed in the cells its box covers (19, 33, 59) | always |

So: 1 x (7 + the seat's test x 2 + the writes).

## Totals

- at 20: 1 x (7 + 36 x 2 + 22) = 101
- at 40: 1 x (7 + 53 x 2 + 36) = 149
- at 80: 1 x (7 + 83 x 2 + 62) = 235

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.61: one pond, its box's cells growing with its radii, x1.41 a doubling each.

## Earlier findings

- verdict-1, finding 1: fixed - each cell under the box read alone, segments charged only in the cells the outline and the drain cross (5, 7, 9 outline cells at 1.8; the drain's 2 cells at 3.7): 36, 53 and 83
- verdict-1, finding 2: fixed - the row recomputed from its cells, no 6.5 product left

## Cheaper algorithms considered

- sweep: not used - one seat is tested
- grid or spatial index: used - the water index's cells under the pond's box
- priority queue: not used - the seats are taken in order along the drain, the first clear kept
- incremental update: not used - one pond is placed
- memoizing what a scan does not change: not used - there is no scan
