# The spike - one predicate asked as an array in its hottest caller

Measured 2026-10-27, seed 25 at 40 households, the host shared with other sessions.

**The change** (commit 31c884aec, reverted - FR-005): `WoodShares.corridor_bars` (`settlement/homestead_parts/wood_share.py`) asked
every reserved seat in the cells its corridor can reach as one array, `seg_dists(seats, [(a, b)])`, where each seat was a
`seg_dist` call; a test held it equal to the seat-by-seat form on 400 random corridors.

## Time: `make perf-ab A=HEAD~1` (the quick form, one run a version)

```
 households, seed   A wall    +-  B wall    +-  wall    A cpu    +-   B cpu    +-   cpu      A calls     B calls  calls
         (40, 25)     7.14  0.00    7.30  0.00   +2%     7.14  0.00    7.29  0.00   +2%    7,564,885   7,614,237    +1%
best of each version's runs, alternated A B / B A; +- its worst less its best - read a change against it, never as a pass
floor (one engine against itself, taken 2026-10-27T20:32:13Z): wall -4%, CPU -4% - a change inside it is not a change
took 38 s
```

## Calls: `make phase-calls` (seed 39, builtins included)

homesteads 7,722,160 (after feature 435) -> 7,627,674 (-1.2%); the roll 26,369,851 -> 26,276,316 (-0.4%). The snapshot's
counter (Python functions only) rose 1% (7,564,885 -> 7,614,237): numpy's own Python-level calls replace the `seg_dist` calls.

## The function itself: `make perf-profile SEED=25 STAGE=homesteads HOUSEHOLDS=40`, before and after

```
corridor_bars before: 4,199 calls, self 0.043 s, cumulative 0.135 s (stage 4.47 s under cProfile)
corridor_bars after:  4,199 calls, self 0.064 s, cumulative 0.317 s (stage 4.85 s under cProfile)
```

## Reading

The array form made the corridor test 2.3 times slower. Each call asks the seats of a few cells - about ten - and numpy's
cost to build and dispatch an array is more than ten scalar distances. An array form pays only where one call asks many
candidates at once; this caller, like the rest the profile shows, asks a few per call, thousands of times. Vectorizing it
needs the caller restructured to ask many corridors (or many candidates) in one call - a change to the search, not to the
predicate. The time moved +2%, inside the -4% floor: no time saving was measured, and the spike is set down.
