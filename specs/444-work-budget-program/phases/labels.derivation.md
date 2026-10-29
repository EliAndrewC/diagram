# Derivation - labels (feature 444)

## Contract

- Reads: the label queue (`label()` requests from the stages before), each caption's subject and, where a stage proved it, its seat: the notice board's caption seat is proved by `place_kosatsuba` (`board_caption_seat`) and rides to this phase; the finished map.
- Writes: each caption (`labels`): its words, its box, its angle, its lines, and a leader where it is not at the preferred offset.
- Keeps: labels last, against the finished sheet (CONVENTION, feature 157); one placer for every caption (feature 266, 0242); a caption whose seat its feature already proved is drawn as proved; a caption is never dropped.
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households): the queue holds 1 caption at 10 and 20 (the notice board's), constant with the households: a hamlet labels its board and nothing else (the title is the frame's).

## The algorithm

    drain the queue in its call order: each caption with a proved seat (the board's) drawn as proved - its box, its angle,
        its lines and its leader written and recorded; a caption with no seat would be seated by the one placer, but the
        hamlet's queue holds none

## Indexes

No index is read or built: the board's caption seat was proved against the finished map by the notice stage, and this stage only writes it.

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the captions, the board's alone | always 1 |
| the caption (written) | per item | 6 | its words (1), box (1), angle (1), lines (1), leader (1), recorded (1) | always 6 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |

So: 1 x 6 x 1.

## Totals

- at 20: 1 x 6 x 1 = 6
- at 40: 1 x 6 x 1 = 6
- at 80: 1 x 6 x 1 = 6

## Cheaper algorithms considered

- sweep: not used - one caption, already seated
- grid or spatial index: not used - the seat was proved by the notice stage; nothing is searched here
- priority queue: not used - the queue drains in its call order, the contract's
- incremental update: not used - one caption is written
- memoizing what a scan does not change: used - the board's proved caption seat is read, not sought again
