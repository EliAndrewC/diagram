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

## R3 - Rounds 1-3 on the map's grid, alternated (observed 2026-10-02, method: `abab.sh`, `r3-15-*.log`, `r3-40-*.log`)

With R2's fixes and the map's grid still in place: 15 households 19.5 s base against 18.8 s; 40 households 48.4 s against
51.0 s - nine seeds faster (seed 2 5.66 -> 2.60 s, seed 10 6.50 -> 3.95 s), and seed 6 three margins (5.94 -> 19.52 s). Without
seed 6, 42.5 -> 31.5 s.

## R4 - The door's grid again (observed 2026-10-02, method: `refusals.py` with the grid switched by environment on four seeds at 40 households; then `abab.sh` against the base, `r4-15-*.log`, `r4-40-*.log`)

Seed 6 on the map's grid: 202 of 545 searches found no path at all - the narrow ways between homesteads held no grid point of
the map's 12 px grid, where a grid laid from the door runs straight out through the gap the door faces. The door's grid with
R2's fixes, against the map's, on the same four seeds: seed 6 2.21 s against 16.44 s, seed 13 3.03 against 2.85, seed 2 2.03
against 2.32, seed 10 3.11 against 3.76 - every seed on one margin. So the sharing was not what paid; the tests asked where the
path is searched were. The map's grid is withdrawn (plan D3).

The first step's test was cheapened at the same time: asked with the whole leg test, it ran the ways' ground test on up to 24
first steps a search, half a route's cost at 15 households (profile, seed 5); the refusals it exists for are the household's
own (R2), so it asks `house_clear`, `fixtures_clear` and `parts_clear` alone.

Rounds 1-4 (the pre-check, the route, the persimmon's sun ground, the indexed water) alternated against the base:

| households | seeds | base | clone | change | margins |
|---|---|---|---|---|---|
| 15 | 1-16 | 21.3 s | 17.5 s | -18% | one on every seed, both legs |
| 40 | 1, 2, 4, 6, 8, 9, 10, 12, 13, 39 | 49.1 s | 30.1 s | -39% | one on every seed, both legs |

At 40 households every seed is faster or level (seed 8 2.64 -> 2.63 s). At 15, thirteen of sixteen are faster; seeds 4 (1.09
-> 1.31 s), 9 (1.12 -> 1.18 s) and 11 (1.38 -> 1.43 s) are slower, by less than a single run's spread on this host.

## R5 - The placed homesteads asked of the house and its yard before the layout, priced and withdrawn (observed 2026-10-02, method: `abab.sh`, round 4 as the base leg and the clone with the check as the new, `r5-15-*.log`, `r5-40-*.log`)

The plan review asked for FR-002's cheap test of the placed homesteads to be priced, not argued away. Every garden side's box
holds the box round the house and its threshing yard (both the same for every side, feature 297 R6), so the house box's tests
asked of that box - the canvas, a reserved corridor, two placed homesteads, the refused-ground grid - refuse every layout when
they refuse it, and it is computed without laying anything out (`_core_box`, the yard's rolled size and the seat's rake; a test
held it equal to the laid boxes' bbox at four seats, two sizes, every side). Asked at every position the settle would lay the
household out at, in place of the house box:

| households | round 4 | with the check | change |
|---|---|---|---|
| 15 (seeds 1-16) | 19.4 s | 20.2 s | +4% |
| 40 (ten seeds) | 34.5 s | 38.2 s | +11% |

By round 4 the seats refused for no garden side fitting were 34-52 a seed at 40 households (the base's 70-744): the seats that
reach the placer are mostly good ones, so there was little left to catch. And the larger box refused positions the settle
would have moved past onto clear ground: seed 4 popped 1,721 seats against 290, seed 9 753 against 300. Withdrawn; the house
box alone stays (plan D1).
