# Feature 435 T02 - the earlier call-cutting changes, timed

Measured 2026-10-27: a rotation of 14 detached worktrees - HEAD and one per arm (each arm a revert patch against HEAD) - each
taking `make perf LABEL=rot-<arm>-<n> SCALING=1` in turn, three rounds (round 1 counting calls, rounds 2-3 timing only,
`L7R_PERF_NO_COUNTS`), the host's load 1.1-1.9 through rounds 2-3. Below: per arm, the sum over seeds 25, 39, 47 of each leg's
best time, the sum of the legs' spreads (worst less best), and the revert's change against HEAD; then the revert's extra calls
by size. THE CALLS COLUMN is the snapshot's counter, which counts Python-level calls and not builtins: so `moves-T64` and
`moves-T65`, which only replaced builtins, read +0.0% here; by the fanout's cProfile count their landings took the roll 21.5M
-> 18.5M and 18.5M -> 17.9M. HEAD's round-1 run at 20 households overlapped the T01 landing's post-push cohort (its 3.6 s spread).

```
arm          | 20 hh: best sum spread vs head | 40 hh: best sum spread vs head | calls@40 vs head
head         |            9.00   3.60   +0.0% |           18.60   1.80   +0.0% |            +0.0%
moves-T07    |            8.80   0.40   -2.2% |           18.30   0.50   -1.6% |            +2.6%
moves-T08    |            8.90   0.30   -1.1% |           18.40   0.30   -1.1% |            +2.9%
moves-T09    |            9.00   0.10   +0.0% |           18.10   0.50   -2.7% |            +2.9%
moves-T12    |            9.00   0.10   +0.0% |           18.30   0.30   -1.6% |            +1.8%
moves-T54    |            8.90   0.20   -1.1% |           18.50   0.20   -0.5% |            +1.3%
moves-T63    |            9.20   0.00   +2.2% |           18.60   0.20   +0.0% |            +8.8%
moves-T64    |            8.90   0.10   -1.1% |           18.40   0.30   -1.1% |            +0.0%
moves-T65    |            8.90   0.10   -1.1% |           18.50   0.20   -0.5% |            +0.0%
removes-T07  |            9.00   0.10   +0.0% |           18.60   0.40   +0.0% |           +10.6%
removes-T08  |            8.90   0.00   -1.1% |           18.50   0.20   -0.5% |            +3.8%
removes-T09  |            9.20   0.00   +2.2% |           18.70   0.10   +0.5% |            +2.7%
removes-T54  |            9.20   0.00   +2.2% |           18.70   0.20   +0.5% |            +5.0%
removes-T63  |            9.00   0.10   +0.0% |           18.50   0.30   -0.5% |            +0.4%

the revert's extra calls over HEAD, all seeds summed (the snapshot's counter):
arm               @10      @20      @40
moves-T07       +1.3%    +2.0%    +2.0%
moves-T08       +2.9%    +2.6%    +1.6%
moves-T09       +5.7%    +4.8%    +2.4%
moves-T12       +1.4%    +2.0%    +1.5%
moves-T54       +0.2%    +0.5%    +1.6%
moves-T63      +18.5%   +12.8%   +20.7%
moves-T64       +0.0%    +0.0%    +0.0%
moves-T65       +0.0%    +0.0%    +0.0%
removes-T07     +7.9%    +9.2%    +8.3%
removes-T08     +2.2%    +3.2%    +2.7%
removes-T09     +1.7%    +2.9%    +2.0%
removes-T54     +4.2%    +4.2%   +13.2%
removes-T63     +0.4%    +0.3%    +0.2%
```

The reading (FR-004: kept where the revert costs time or the work's growth with size argues for it, reverted otherwise):

- **Every arm's time is inside the spread** (the spec's edge case: neither a gain nor a loss): within about +-2.7% of HEAD at 20 and 40 households, inside the runs' spread;
  several reverts ran faster.
- **The eight moves-work arms** (427 T07, T08, T09, T12; 417 T54, T63, T64, T65): their extra calls are flat or shrinking with
  size - REVERTED.
- **`removes-T54`** (417 T54's box screens in `house_hit` and `rejoined`): its revert's extra calls grow 4.2% -> 13.2% from 20 to
  40 households, the curve the screens bend - KEPT on the size ground.
- **`removes-T07`, `removes-T08`, `removes-T09`, `removes-T63`**: KEPT by the round arbiter's ruling on ask:435-removes-arms -
  the time clause decides nothing (every arm inside the spread, which the spec's edge case reads as neither gain nor loss, and
  reverting on it would gate a revert on a timing, against FR-006); the growth clause keeps them on the shape of the work each
  revert would bring back, a scan of unchanging geometry repeated per candidate (constitution X clause 15):
  - `removes-T07`: per seat, the per-point `point_taken` loop, the mat floor's `fits` per spot, and each household's way-out
    test rebuilding its box lists per cell - grows with households and grid points;
  - `removes-T08`: per clump and per point, generators over every house (`past_the_lanes`, `far_envelope`, `fouled`, `_trees`)
    and `inside_many` rebuilding its shapes per call - grows with households and the grove's clumps;
  - `removes-T09`: per point, `collector_crossings` scanning every collector segment and `_f_at_u` converting the polyline
    per call - grows with the collector's segments;
  - `removes-T63`: per seat, `admits` collecting every conflict where one answers - grows with what stands near a seat.
- **427 T07 hunk 6** (the privy's hoisted reach): the reverted arm calls px once per call, so hunk 6 has no arm and is not
  timed, and it is kept as removes-work, a loop-invariant hoist whose revert cannot be written against HEAD (the round
  arbiter's ruling on ask:435-T07-privy-reach, case (b)).

The hunk-by-hunk classification: `t02-hunks.md`.
