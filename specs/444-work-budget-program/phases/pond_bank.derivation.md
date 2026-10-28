# Derivation - pond_bank (feature 444)

## Contract

- Reads: the tail pond and its reed fringe, the knob `pond_bank` (rolled bare or planted, 0061), and what stands: the roofs, wellheads, yards' and beds' sun ground, the treads, the crop and the water.
- Writes: on a planted bank, mulberry and cudrania in turn round the ring, one seat every `POND_BANK_PITCH_FT` (30 ft, a GUESS) a crown's radius (6 ft, a GUESS) beyond the reeds, each crown recorded in `tree_crowns` and the trees in `meta.pond_bank_trees`; on a bare bank, nothing.
- Keeps: no crown on a roof or a wellhead, or on a yard's or bed's sun ground; no trunk on a tread, the crop or the water (0061, 0071); no two crowns overlap (CONVENTION). The cohort's checks: each crown against the overlap matrix (`tree_crowns` read by every structure test) - the seat's index tests carry it.
- Bounds: the ring's length grows with the pond, as the square root of the households (the pond about 95 by 60 ft at 10, 134 by 85 ft at 20, measured 2026-10-28, `phases/items.md`): about 17 seats at 10, 24 at 20, 34 at 40 and 48 at 80.

## The algorithm

    roll the bank's form; if bare, record it and return
    index what a crown or a trunk must clear (the roofs, wellheads, sun ground, treads, crop, water) once
    for each seat round the ring, at the pitch: jitter it within the bank's play; test its crown and trunk through the index and against the last tree seated; seat it if it stands free
    record the trees and their kinds

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | the seats: 24 at 20, 34 at 40, 48 at 80 | the ring's length over the 30 ft pitch (the contract's Bounds) | a planted bank at 80 households |
| candidates per seat (S2) | per item | 1 | each seat on the ring is tried once, at its pitch; a seat that does not stand free is left empty, never moved | always 1 |
| the tests, per seat (S1) | per item | 22 | the crown against at most 4 roofs or wellheads and 4 sun grounds in its cells, the trunk against at most 4 each of tread, crop and water, and the last tree once | a seat beside a farmstead's yard |
| the jitter and the kind | per item | 2 | one jitter within the bank's play, one turn of the kind | 2 at every seat |
| slack | per item | 1 | the tests are bounds at the worst cell, not estimates | not applicable |
| the index | once | the standing things near the pond | built once, before the ring | as many as stand within a crown of the ring |

So: seats x (1 x 22 + 2) x 1 = 24 a seat: about 580 at 20, 820 at 40 and 1,150 at 80 households, plus the index once - growing as
the square root of the households.

## Cheaper algorithms considered

- sweep: used - the ring is walked once, seat by seat, at its pitch
- grid or spatial index: used - what a crown or a trunk must clear is indexed once, so a seat meets a bounded number
- priority queue: not used - no seat is ranked; each is taken or left on its own test
- incremental update: used - each seat tests only the last tree seated, the one a crown at the pitch can reach
- memoizing what a scan does not change: used - the index is built once, before the ring is walked
