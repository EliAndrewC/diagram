# The spike - one predicate asked as an array in its hottest caller

Two spikes: the first converted only the seat test; the second, FR-002 as written, both of the caller's uses of the predicate.

## Spike 1 - the seat test alone

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

## Spike 1's reading

The array form made the corridor test 2.3 times slower. Each call asks the seats of a few cells - about ten - and numpy's
cost to build and dispatch an array is more than ten scalar distances. An array form pays only where one call asks many
candidates at once; this caller, like the rest the profile shows, asks a few per call, thousands of times. Vectorizing it
needs the caller restructured to ask many corridors (or many candidates) in one call - a change to the search, not to the
predicate. The time moved +2%, inside the -4% floor: no time saving was measured, and the spike is set down.

Spike 1 converted only the seat test (line 408); the cell test (line 406, 24,326 calls, 0.029 s - about 40% of the predicate's
time under `corridor_bars`) stayed scalar, so it was a partial FR-002 - spike 2 below is the whole of it.

## Spike 2 - both uses of the predicate (commit fd712b35f, reverted - FR-005)

The cells' centers asked in one `seg_dists` call, then the seats of every cell in reach in one call; the equality test (400
random corridors) passed.

`make perf-ab A=HEAD~1` (the quick form, one run a version), measured 2026-10-27:

```
 households, seed   A wall    +-  B wall    +-  wall    A cpu    +-   B cpu    +-   cpu      A calls     B calls  calls
         (40, 25)     7.17  0.00    7.37  0.00   +3%     7.17  0.00    7.37  0.00   +3%    7,562,255   7,499,637    -1%
best of each version's runs, alternated A B / B A; +- its worst less its best - read a change against it, never as a pass
floor (one engine against itself, taken 2026-10-27T20:32:13Z): wall -4%, CPU -4% - a change inside it is not a change
took 38 s
```

`make perf-profile SEED=25 STAGE=homesteads HOUSEHOLDS=40`, measured 2026-10-27:

```
corridor_bars spike 2: 4,199 calls, self 0.073 s, cumulative 0.348 s (stage 5.04 s under cProfile; before: 0.135 s of 4.47 s)
```

`make phase-calls` on spike 2's commit (in a detached worktree), measured 2026-10-27: homesteads 7,722,160 -> 7,718,806, the
roll 26,369,851 -> 26,362,008 (-0.03%). Spike 1's count (homesteads -1.2%), taken in the clone on its commit, does not agree
with this; the difference between the two counts was not explained (the call count also varies about 0.03% between processes,
feature 436's A/A).

## Reading of both

- Spike 1 made the corridor test 2.3 times slower, spike 2 2.6 times; the roll moved +2% and +3%, inside the -4% floor. No
  time saving was measured, and both are set down.
- TWO CAUSES, NOT SEPARATED: each call asks a few cells and about ten seats, and numpy's cost to build and dispatch an array
  is more than that many scalar distances; and both spikes lose the original's early exit (the scalar loop returned at the
  first seat inside the gap, the arrays measure every seat in reach first). Which holds more of the slowdown was not
  measured; spike 2, which converts more scalar calls into arrays, is the slower.
- What it says for the layer: an array form pays only where one call asks many candidates; this caller, like the others the
  profile shows, asks a few per call thousands of times. Vectorizing it means restructuring the search so one call asks many
  corridors or many seats - a change to the caller, not to the predicate.
