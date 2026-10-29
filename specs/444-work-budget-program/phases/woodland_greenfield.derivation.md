# Derivation - woodland, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan's woodland bearing (the high side, past the commons) and its count of worked woods; the view, cut from the solid features plus a narrow margin.
- Writes: on a sheet whose woods lie off it, their bearing and their count, once, into the plan (`woodland_offsheet`); on a sheet that counts a wood as solid, each worked wood an irregular ring stocked with coppice crowns.
- Keeps: the ground ordered away from the houses as village, back grove, commons, then whatever lies past the map, the commons on the high side further out than the grove (0078); the frame the box round the solid features - houses, fields, water, groves - plus about 30 ft on a hamlet sheet, the wild ground cut off at the edge and never widening it (0241: "If a map ever wants a wild feature to widen its frame, the honest change is to count that feature as solid").
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the woods off the sheet on both, bearing N, 4 parcels; the woods lie past the commons, which lies past the grove, so on a hamlet sheet framed 30 ft past its solid features no worked wood falls inside the view unless a wood is counted solid, which no hamlet's plan does.

## The algorithm

    the woodland's bearing and count read from the plan (2); the sheet's frame rule read (1): no wood counted solid, so the woods
        lie off the sheet - their bearing and count written once (2)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the woods' record, once a map | always 1 |
| the reads and the writes | per item | 5 | the bearing and the count read (2), the frame rule read (1), the record's two fields written (2) | always 5 |
| slack | per item | 1 | nothing varies | not applicable |

So: 1 x 5 x 1.

## Totals

- at 20: 1 x 5 x 1 = 5
- at 40: 1 x 5 x 1 = 5
- at 80: 1 x 5 x 1 = 5

## Growth

Flat, an exponent of 0: the woods lie off every hamlet sheet.

## Cheaper algorithms considered

- sweep: not used - nothing is laid on the sheet
- grid or spatial index: not used - nothing is tested
- priority queue: not used - nothing is ranked
- incremental update: not used - one record
- memoizing what a scan does not change: not used - there is no scan
