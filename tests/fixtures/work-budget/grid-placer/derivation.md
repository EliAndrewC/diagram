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

## The count, factor by factor

| factor | value | its reason |
|---|---|---|
| items | n discs | the contract |
| lookups, over the whole run (S2) | at most 9 n, plus the blocked sites once | each site is looked up once, and a site looked up is one of three: blocked (at most the blocked sites, once), placed (n), or refused by a center's flag - each refused site charged to the first center that flagged it, which flags at most 8 (8 n). So the lookups over the run are at most n + 8 n, plus the blocked sites |
| work per lookup (S1) | 1 | the site's own flag: every center sits on the lattice, so the conflict set is fixed (8 sites) and is marked when the disc is placed, never searched |
| marks per disc placed | at most 8 | the conflict set (fewer at the edge) |
| setup, once | 1 per site (A / (d/2)^2 = 4 A / d^2 flags laid and shuffled), plus the sites each blocked rectangle covers, summed over the rectangles | before the loop, never per candidate; overlapping rectangles flag a site more than once, so the term is the sum over the rectangles, not capped at the site count |
| slack | 1 | none needed: every factor is a stated bound |

So placing n discs takes at most 9 n lookups and 8 n marks - 17 n basic operations - plus the blocked sites' lookups and the setup,
both once. It is linear in n: no factor depends on the number placed (S1, S2), no pass over the placed discs runs inside the loop
(S3), and nothing is placed and then moved (S4).
