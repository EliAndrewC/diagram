# Derivation - pond_bank (feature 444)

## Contract

- Reads: the tail pond (radii rx and ry, the manifest's `pond`) and its reed fringe (`SINK_FRINGE`, 44 ft), the knob `pond_bank` (rolled bare or planted, 0061), the fan's outline (indexed by the field stage), the brook, and the settlement's standing index of what stands - roofs, wellheads, yards' and beds' sun ground, treads, crowns - kept by the stages before it.
- Writes: on a planted bank, mulberry and cudrania in turn round the ring, one seat every `POND_BANK_PITCH_FT` (30 ft, a GUESS), the ring a crown's radius (`POND_BANK_CROWN_FT`, 6 ft, a GUESS) beyond the reeds, each seat jittered within the bank's play (`POND_BANK_FT`, 18 ft, less two crown radii: 6 ft, across the ring), each crown recorded in `tree_crowns` and the trees in `meta.pond_bank_trees`; on a bare bank, nothing.
- Keeps: no crown on a roof or a wellhead, or on a yard's or bed's sun ground; no trunk on a tread, the crop or the water (0061, 0071); no two crowns overlap (CONVENTION) - which the pitch keeps by itself: seats 30 ft apart, jittered at most 6 ft across the ring, stand at least 24 ft apart, twice a crown's 12 ft width, and the ring divided evenly leaves the closing gap no shorter than the pitch. The cohort's checks: each crown against the overlap matrix (`tree_crowns`) - carried by the seat's tests.
- Bounds (measured 2026-10-28 from the reference manifests at 10 and 20 households, `phases/items.md`): the seat ring 27 seats at 10 and 34 at 20 (the pond's radii plus 50 ft, over the pitch), growing with the pond: 34 at 20, 44 at 40, 57 at 80. Within reach of any seat (its crown and a crown's width of pad, 12 ft): no roof, sun ground, wellhead, lane or crown at 10 or 20; the crop no nearer than 26 ft; the brook within 3 ft at 10 (62 ft at 20) - so a seat's queries find at most the brook's 2 nearest segments.

## The algorithm

    roll the bank's form; if bare, record it and return
    for each seat round the ring, at the pitch: jitter it within the bank's play; query its crown and its trunk in the
        standing index (each query a crown's reach, at most 4 cells); test the trunk against the outline in its cell and the
        pond exactly, and the brook's segments in its cells; seat it if it stands free
    record the trees and their kinds

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 34 at 20, 44 at 40, 57 at 80 | the ring's seats (the Bounds) | a planted bank at 80 households |
| the standing queries (cells examined) | per item | 8 | the crown's and the trunk's queries, each at most 4 cells of the standing index; nothing found within reach at 10 or 20 (the Bounds) | always 8 |
| the crop | per item | 5 | the trunk against at most 4 outline segments in its cell, the cell examined once | always 5 |
| the pond | per item | 1 | one exact distance from the ellipse | always 1 |
| the brook (cells examined) | per item | 6 | its at most 4 cells near the trunk and its 2 nearest segments | a seat beside the brook, as at 10 |
| the jitter | per item | 1 | one draw within the play | always 1 |
| the kind | per item | 1 | the next of mulberry and cudrania | always 1 |
| slack | per item | 1 | every factor is a bound at its worst case | not applicable |
| the roll | once | 1 | the bank's form, rolled once | always 1 |

So: seats x (8 + 5 + 1 + 6 + 1 + 1) x 1 + the roll - growing as the pond's ring.

## Totals

- at 20: 34 x (8 + 5 + 1 + 6 + 1 + 1) x 1 + 1 = 749
- at 40: 44 x (8 + 5 + 1 + 6 + 1 + 1) x 1 + 1 = 969
- at 80: 57 x (8 + 5 + 1 + 6 + 1 + 1) x 1 + 1 = 1255

## Cheaper algorithms considered

- sweep: used - the ring is walked once, seat by seat, at its pitch
- grid or spatial index: used - the standing index the earlier stages keep, and the field's outline index, so a seat meets a bounded number of cells
- priority queue: not used - no seat is ranked; each is taken or left on its own test
- incremental update: used - the standing index is kept by the stages before, so this stage builds none; and the pitch keeps the crowns apart, so no seat is tested against another
- memoizing what a scan does not change: used - the pond's ellipse and the ring are computed once, before the walk
