# Research: seat before settle (feature 314)

Every figure here was observed 2026-10-02, method: `refusals.py` (each grown seat followed to its outcome, the time of each phase
summed by outcome) or `abab.sh` (base and clone alternated per seed, one process a seed), on the reference spec, under the load
of the other sessions on this host (the same load on both legs; single runs vary by up to 2x, so only alternated legs are
compared).

## R1 - The GM's case, 15 households on seeds 1-16, where the time goes (observed 2026-10-02, method: `refusals.py 15 1,...,16` on the base, `r1-base-15.log`)

| what the seat came to | seats | time | share |
|---|---|---|---|
| refused on the ground (house box, field reach, water) | 471 | 0.9 s (settle) + 0.02 s | 4% |
| refused: no garden side fit among the standing homesteads | 753 | 1.2 s + 0.4 s | 7% |
| fit, refused by the parts (no lawful corridor, the lane law) | 574 | 1.0 s + 3.8 s | 22% |
| seated | 240 | 0.4 s + 5.4 s | 26% |
| outside the seat-by-seat loop (the first house's free ground, the boundary, the exit strip, the field's corridor, the stage's own bookkeeping) | - | 8.8 s | 40% |

The homesteads stage took 21.9 s summed, 1.37 s a map. At 15 households the ground-refused seats the pre-check (US1) drops are
4% of the stage, against 11% at 40; the largest single share is the work outside the seat loop.

## R2 - Round 2: the route searched on the map's grid (observed 2026-10-02, method: `abab.sh`, `r2-15-*.log`, `r2-40-*.log`; then `routecount.py` on seed 13 at 40 households)

The route's heuristic was computed at every push and pop of a cell (a third of the search, by profile); it is now computed once
a cell, which changes no route. To share what a grid point's standing ground answers between searches, the grid was made the
map's (multiples of the step) rather than each door's. Alternated against the base: 15 households 20.5 s both legs; 40 households
46.4 s base against 102.1 s - seeds 2, 8, 13, 39 and 4 needed three and four margins where they had needed one.

Why, measured on seed 13: 1,189 route searches, 1,072 of them found a path of cells and 1,016 of those were then refused when
pulled taut, because a leg crossed the household's own beds or fixtures (`parts_clear`, `fixtures_clear`). The search kept off
the house's own box only; laid from the door, its first steps had run straight out of the yard, and on the map's grid they ran
along the house front into the beds. Fixed three ways, each the taut pull's own test asked earlier: the search keeps off the
household's own parts by the gaps their leg tests keep; its first step from the door (up to two cells) is judged by the leg test;
a goal whose last leg onto the tree the standing ground refuses is no goal. Seed 13: 82 searches, 38 routes, one margin, 3.1 s
(the base 4.7 s).

A start at the grid point nearest the door, or the first step widened to two cells, alone changed nothing (the same 7,690 seats
popped) - recorded so neither is taken for the cause again.

## R3 - Rounds 1-3 against the base, alternated (observed 2026-10-02, method: `abab.sh`, `r3-15-*.log`, `r3-40-*.log`)

Pending.
