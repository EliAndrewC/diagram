# Derivation - seat (feature 444)

## Contract

- Reads: the field's drawn envelope (its outline, a closed ring of points), the field's fall and its toe, the dry hem (its polygons), the brook, the wind (the regional northwest unless declared) and the canvas (the belt's room, `BELT_ROOM_MAX_OFF`).
- Writes: nothing drawn; the seat frame - a center, an along-the-margin unit, an away-from-the-field unit and the band's half-extents - in `plan.seat`, and its `ladder`, the ranked margins the seating falls back to.
- Keeps: back to the wind, face to the field (0031, 0072); a margin whose normal is within 45 degrees of the wind faces it (tier 0), one 45 to 90 degrees off offers its back turned to the wind (tier 1); one whose belt would fall off the canvas is no candidate; the wet toe below the fields is no building ground; a site with no legal seat is refused, naming it (`SeatRefused`). The cohort's checks read the seat through what later stages place on it.
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the outline's points 67 and 78 (x1.16: 78 at 20, 90 at 40, 105 at 80); the dry hem's polygons 36 and 61 (x1.69: 61 at 20, 104 at 40, 176 at 80), each no larger than a plot (its diagonal under 64 ft, so in at most 4 cells of 64 ft); at most 7 hem polygons in one 64 ft cell, measured at 10 and 20 (6 and 7) - the ceiling taken; at most 12 brook segments in one 64 ft cell (the field's measured ceiling).

## The algorithm

    index the dry hem's polygons in 64 ft cells, once; the brook in the field's outline index's cells
    for each margin point of the drawn envelope (each outline point):
        score it: its outward normal against the wind (1), its height against the fall's upslope end (1)
        penalize it: inside a hem polygon in its cell (the cell examined, at most 7 polygons tested), the brook in its cell (the
            cell examined: the brook is in it or not), below the field's toe (1), the belt's room off the canvas (4 sides); its tier from those penalties (1)
    rank the margin points by tier and score (a sort); the first is the seat, the rest its ladder; refuse if none is legal
    write the seat frame (its center, its two units, its two half-extents)

## Indexes

- hem index: cells of 64 ft; densest 7 hem polygons a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft against a hem polygon whose diagonal is under 64 ft
- outline index: the field's, read for the brook - cells of 64 ft; densest 12 brook segments a cell, from a smallest side of 64 ft (the field's measured ceiling); only whether a cell holds the brook is read

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 78 at 20, 90 at 40, 105 at 80 | the margin points: each outline point (the Bounds) | 80 households |
| the wind | per item | 1 | the point's outward normal against the wind's bearing | always 1 |
| the upslope | per item | 1 | the point's height against the fall's upslope end | always 1 |
| the hem (hem index cells examined) | per item | 8 | the point's cell examined and at most 7 hem polygons tested | the densest cell |
| the brook (outline index cells examined) | per item | 1 | the point's cell examined: the penalty is the brook in the cell, so no segment is tested | always 1 |
| the toe | per item | 1 | the point's fall against the field's toe | always 1 |
| the belt's room | per item | 4 | the belt's extent off the point against each of the canvas's 4 sides | always 4 |
| the tier | per item | 1 | the point's tier, read from its penalties | always 1 |
| slack | per item | 1 | every factor is a bound at its worst case | not applicable |
| the ranking | over the run | 546 at 20, 630 at 40, 735 at 80 | the margin points sorted by tier and score, log2 of the points rounded up each | 80 households |
| the hem index (cells written) | once | 244 at 20, 416 at 40, 704 at 80 | each hem polygon filed in at most 4 cells (its diagonal under 64 ft) | 80 households |
| the frame | once | 10 | the center (2), the along and away units (4), the half-extents (2) and the refusal test (2), once | always 10 |

So: the margin points x (1 + 1 + 8 + 1 + 1 + 4 + 1) x 1, plus the ranking, the index and the frame.

## Totals

- at 20: 78 x (1 + 1 + 8 + 1 + 1 + 4 + 1) x 1 + 546 + 244 + 10 = 2126
- at 40: 90 x (1 + 1 + 8 + 1 + 1 + 4 + 1) x 1 + 630 + 416 + 10 = 2586
- at 80: 105 x (1 + 1 + 8 + 1 + 1 + 4 + 1) x 1 + 735 + 704 + 10 = 3234

## Earlier findings

- verdict-1, finding 1: fixed - the brook is a presence penalty, the point's cell examined (1), no segment tested
- verdict-1, finding 2: fixed - the tier is read per point from its penalties, its own per-item factor (1), out of the frame

## Cheaper algorithms considered

- sweep: not used - each margin point is scored on its own; no order of the points lowers a factor
- grid or spatial index: used - the hem in 64 ft cells and the brook in the field's cells, so a point meets a bounded number
- priority queue: not used - the ladder is the whole ranking, so a full sort, not a queue's first item
- incremental update: not used - nothing a point's score reads changes as the points are scored
- memoizing what a scan does not change: used - the hem index is built once, before the points are scored
