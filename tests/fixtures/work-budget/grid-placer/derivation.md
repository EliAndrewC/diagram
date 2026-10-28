# Derivation - a lattice placer with incremental refusal (a work-budget fixture, feature 443 FR-009)

This fixture is a textbook placer, so that the `work-budget` agent can be shown not to refuse sound arithmetic. The placer it
describes is `placer.py.txt` beside this file.

## Contract

- Reads: a rectangle of ground (width and height in feet), the number of discs to place, the disc spacing `d` (no two centers
  closer than `d`), and the blocked rectangles already on the ground.
- Writes: the disc centers, each on the lattice of spacing `d / 2`, each at least `d` from every other and outside every blocked
  rectangle.
- Keeps: no two discs closer than `d`; every disc on open ground.
- Bounds: `n` is at most the ground's capacity, about `A / d^2` for its area `A`.

## The algorithm

    the candidate sites: the lattice of spacing d / 2 over the rectangle, one refused flag per site
    once: each blocked rectangle flags the sites it covers
    for each site, in a fixed seeded order, until n discs are placed:
        look up its flag; if refused, skip it                              (one lookup)
        place the disc on it
        flag the sites closer than d: on the d / 2 lattice these are the 8 offsets (i, j) with i^2 + j^2 < 4, (i, j) not (0, 0)

## Indexes

- the lattice: cells of 5 ft (d / 2, at the fixture test's d = 10 ft); densest 1 site a cell, from a smallest side of 5 ft - a cell is one site

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | n discs, the contract (the fixture's sizes are its n) | n up to the capacity A / d^2 |
| lookups: the lattice cells examined (S2) | over the run | at most 9 n, plus the blocked sites | each site is looked up once, and a site looked up is one of three: blocked (at most the blocked sites, once), placed (n), or refused by a center's flag - each refused site charged to the first center that flagged it, which flags at most 8 (8 n). So the lookups over the run are at most n + 8 n, plus the blocked sites | every center isolated, so no two conflict sets overlap; any n from 1 to the capacity |
| work per lookup (S1) | per item | 1 | the site's own flag: every center sits on the lattice, so the conflict set is fixed (8 sites) and is marked when the disc is placed, never searched | always 1 |
| marks per disc placed | per item | at most 8 | the conflict set (fewer at the edge) | a disc away from the edge, all 8 marked |
| setup | once | 4 flags a disc at capacity (A = n d^2): 4 A / d^2 = 4 n, laid and shuffled, plus the sites each blocked rectangle covers, summed over the rectangles (none in this count) | before the loop, never per candidate; overlapping rectangles flag a site more than once, so the term is the sum over the rectangles, not capped at the site count | the rectangles' total area over (d / 2)^2 |
| slack | per item | 1 | none needed: every factor is a stated bound | not applicable: no factor is estimated |

So placing n discs takes at most 9 n lookups and 8 n marks - 17 n basic operations - plus the blocked sites' lookups and the setup,
both once. It is linear in n: no factor depends on the number placed (S1, S2), no pass over the placed discs runs inside the loop
(S3), and nothing is placed and then moved (S4).

## Totals

- at 20: 20 x (9 x 1 + 8) x 1 + 4 x 20 = 420
- at 40: 40 x (9 x 1 + 8) x 1 + 4 x 40 = 840
- at 80: 80 x (9 x 1 + 8) x 1 + 4 x 80 = 1680

## Cheaper algorithms considered

- sweep: not used - the candidates are tried once each in a seeded order; a sweep orders them but lowers no factor
- grid or spatial index: used - the d / 2 lattice is the index, one flag per site
- priority queue: not used - no candidate is ranked; each is taken or refused on its own flag
- incremental update: used - placing a disc flags its 8 conflict sites, so no candidate searches its neighbors
- memoizing what a scan does not change: used - the blocked rectangles are flagged once, before the loop
