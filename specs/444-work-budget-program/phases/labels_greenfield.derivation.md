# Derivation - labels, greenfield (feature 444 FR-015)

## Contract

- Reads: the captions owed on a hamlet sheet and each one's proved seat - on a hamlet the notice board's, proved by `notice`.
- Writes: each caption - its words, its box, its angle, its lines, and a leader where it is not at the preferred offset.
- Keeps: captions spent on the few things the ink cannot carry, never stating what the drawing shows; caption text drawn above all other ink (0241); a board's caption at its preferred offset or a ring within reach (0190).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): one caption on both, the board's, at every size.

## The algorithm

    for each owed caption: its proved seat read (1); its words, box, angle and lines written (4); a leader written where the seat
        is off the preferred offset (1)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the board's caption | always 1 |
| the caption | per item | 6 | the seat read, the four fields written, the leader | always 6 |
| slack | per item | 1 | nothing varies | not applicable |

So: 1 x 6 x 1.

## Totals

- at 20: 1 x 6 x 1 = 6
- at 40: 1 x 6 x 1 = 6
- at 80: 1 x 6 x 1 = 6

## Growth

Flat, an exponent of 0: one caption.

## Cheaper algorithms considered

- sweep: not used - one caption
- grid or spatial index: not used - its seat is proved by `notice`
- priority queue: not used - nothing is ranked
- incremental update: not used - one caption
- memoizing what a scan does not change: used - the proved seat read, never searched again
