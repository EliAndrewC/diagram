# Derivation - bamboo (feature 444)

## Contract

- Reads: the bamboo seats `stage_hinterland` scanned (each a stand's position and extent, in the farmsteads or at the settlement's edge behind its back row, per the `bamboo` knob), and the registry, into which each stand is filed.
- Writes: each bamboo stand (`bamboo_stands`): its polygon to scale (a stand-level glyph, a map drawing convention after Japan's topographic legend, 0075) and its symbolic marks inside it on a jittered grid; `meta.bamboo`.
- Keeps: drawn on the seats the hinterland scanned, after the belt, over scrub that already kept out of them; no seat is sought here (the scan was the hinterland's).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the stands 3 and 6 (x2: 6 at 20, 12 at 40, 24 at 80); a stand's polygon 4 points and its marks 7 (16 by 22 ft on the reference, each stand the same), at most 7 marks a stand; a stand under 64 ft a side, in at most 2 by 2 cells.

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
| the filing (registry cells written) | per item | 5 | recorded (1) and filed in at most 4 cells (4) | always 5 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |

So: the stands x (4 + 14 + 5) x 1.

## Totals

- at 20: 6 x (4 + 14 + 5) x 1 = 138
- at 40: 12 x (4 + 14 + 5) x 1 = 276
- at 80: 24 x (4 + 14 + 5) x 1 = 552

## Cheaper algorithms considered

- sweep: not used - each stand is drawn on its own seat, independent of the others
- grid or spatial index: used - the registry's cells, each stand filed for the stages after
- priority queue: not used - nothing is ranked; every scanned seat is drawn
- incremental update: used - each stand is filed as it is drawn
- memoizing what a scan does not change: used - the seats are the hinterland's scan, read, never searched again
