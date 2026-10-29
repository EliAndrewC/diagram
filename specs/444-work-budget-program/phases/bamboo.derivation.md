# Derivation - bamboo (feature 444)

## Contract

- Reads: the bamboo seats `stage_hinterland` scanned (each a stand's position and extent, in the farmsteads or at the settlement's edge behind its back row, per the `bamboo` knob), and the registry, into which each stand is filed.
- Writes: each bamboo stand (`bamboo_stands`): its polygon to scale (a stand-level glyph, a map drawing convention after Japan's topographic legend, 0075) and its symbolic marks inside it on a jittered grid; `meta.bamboo`.
- Keeps: drawn on the seats the hinterland scanned, after the belt, over scrub that already kept out of them; no seat is sought here (the scan was the hinterland's).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the stands 3 and 6 (x2: 6 at 20, 12 at 40, 24 at 80); a stand's polygon 4 points and its marks 7 (16 by 22 ft on the reference, each stand the same), at most 7 marks a stand; a stand under 64 ft a side, in at most 2 by 2 cells. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell; each held flat past 20, a mean over occupied cells not rising with the households as the densest cell does.

## The algorithm

    for each seat the hinterland scanned: the stand's polygon written (4 points), its marks laid on the jittered grid inside it
        (each mark's jitter drawn and its strokes written), recorded and filed in the registry's cells

## Indexes

- registry: cells of 64 ft (the hinterland's), each stand filed in its at most 2 by 2 cells; densest one stand a cell's share, from a smallest side of 64 ft against a stand of 16 by 22 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 6 at 20, 12 at 40, 24 at 80 | the stands, one a seat | 80 households |
| the polygon | per item | 4 | its 4 points written | always 4 |
| the marks | per item | 14 | at most 7 marks, each its jitter drawn (1) and its strokes written (1) | 7 marks |
| the filing (registry cells written) | per item | 3 | recorded (1) and filed in the cells a 16 by 22 ft stand covers at a typical spot on the 64 ft grid, (1 + 16/64)(1 + 22/64) = 1.68, rounded up 2 | the typical stand |
| slack | per item | 1 | what varies around the typical case (S8): the spread around the mean: a stand straddling a corner files in 4 cells, 23 against 21 | a corner stand |

So: the stands x (4 + 14 + 5) x 1.

## Totals

- at 20: 6 x (4 + 14 + 3) x 1 = 126
- at 40: 12 x (4 + 14 + 3) x 1 = 252
- at 80: 24 x (4 + 14 + 3) x 1 = 504

- FR-014 re-score: every factor is an exact count, no density or candidate taken at its worst, so the typical case is the derivation as it reads (rubric S8; ask:444-budget-standard)

## Earlier findings

- verdict-2, finding 1: fixed - the filing at the typical 1.68 cells a stand, 3 with its record (the batch's accept, ask:444-T09-rescore-batch)
- verdict-1, finding 1: fixed - carried from the verdict as it stood (its notes stand); the derivation re-scored to the typical case under FR-014

- the batch's accept (ask:444-T09-rescore-batch): the filing at its typical 1.68 cells, as verdict-2 named

## Cheaper algorithms considered

- sweep: not used - each stand is drawn on its own seat, independent of the others
- grid or spatial index: used - the registry's cells, each stand filed for the stages after
- priority queue: not used - nothing is ranked; every scanned seat is drawn
- incremental update: used - each stand is filed as it is drawn
- memoizing what a scan does not change: used - the seats are the hinterland's scan, read, never searched again
