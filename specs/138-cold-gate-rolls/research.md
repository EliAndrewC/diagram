# Research: why a polder roll cost 100 s, and what the fix measured

Feature 138. Every number is a stopwatch on the dev container (22 threads), 2026-08-28.

## R1 - the baseline profile (unmodified code, `1433d457` + the unwired index module)

Per stage, solo (a background sweep ran beside the second column, so it is ~1.5x inflated):

| stage | seed-19 polder (16 hh) | reference comb (15 hh) |
|---|---|---|
| `stage_web` (the lane web) | **57.2 s** | 14.2 s |
| `stage_track` (the connector) | **21.7 s** | 4.6 s |
| `stage_notice` | 10.9 s | 4.1 s |
| `stage_homesteads` | 8.6 s | 1.6 s |
| `stage_hinterland` | 8.5 s | 7.6 s |
| `stage_field` | < 1 s | 4.3 s |
| total | **110.4 s** | 37.2 s |

`cProfile` of `stage_web`: `_route` x 71 -> `clear_runs` x **165,611** (one per lattice CELL: a degenerate
two-point polyline whose truth value is "this cell center is clear") -> `fouled` x 872k -> `near` x 7.5M ->
`seg_dist` x **36M**, `max` x 106M, `min` x 83M; `_serve_stragglers` 150 of 208 profiled seconds. Of
`stage_track`: `path_violations` x 108 -> a pairwise crossing count of **170M `hypot`** (a connector across
a polder's parallel ditches has hundreds of crossings). Not NP-hard: O(cells x polygons x edges) and
O(crossings^2), brute force, with no index. The `GEN_TIME_BUDGETS` comment blaming `fit_field`'s
bisection was wrong for the polder (under a second there) and right for comb hamlets (16-22 s of
`build_comb` x 7 on cohort seeds 41 and 7) - corrected in place.

The other gate specs, baseline solo (from the manifest oracle run): polder12 122 s, polder8 162 s,
reference 49 s, cohort41 41 s, retry4 20 s, cloud7 31 s, lane5 48 s, clamped23 49 s (that run shared the
box with a test profile; the first column above is the clean figure). Live pool in a detached worktree at
HEAD: inashiro 54 s, kashikawa 100 s, mizuguchi 44 s, sawada 120 s.

## R2 - the fix, round by round (every map byte-identical after each)

| round | change | polder 19 |
|---|---|---|
| 1 | `FabricIndex` (grid over margin-inflated bounds; same predicate, superset of candidates) in `clear_runs`; `_route` derives its lattice from ONE index; `path_violations` counts crossing pairs by a sweep | 110 -> 38.8 s (web 57 -> 10 s; track off the top) |
| 2 | the index memoized on its inputs' identity (4,969 rebuilds on identical lists were 26 s profiled); polygons spanning > 256 cells tested by bounds instead of filed (25M dict inserts); the sweep bucketed by cells of the deck length (an x-sweep degenerates on parallel ditches); `fixture_clear_of_water` on a cached watercourse grid (17,407 probes x 720 segments = 12.5M `seg_dist`) | 38.8 -> 31.5 s (contended) |

Byte identity: nine gate specs (`identity.py` against the baseline manifests) IDENTICAL after each round;
the four live pool hamlets regenerated with the cache bypassed - md5 equal to the worktree's unwired
regeneration and to the committed manifests. Pool timings wired: inashiro 21 s, kashikawa 34 s,
mizuguchi 15 s, sawada 32 s.

## R3 - what remains, and why it is left

After round 2 the polder's top stages are `stage_homesteads` (~11 s: the bundle fit's `_rect_hits`, whose
cost is `point_in_poly` on large polygons - 59k calls; a grid was tried there before and measured noise,
the comment says so), `stage_hinterland` (~8 s: scatter samples against the commons outline, already on
the `PointGrid`/`boxed_grid` indexes), `stage_web` (~4 s). On comb hamlets `stage_field` (16-22 s) is
`fit_field`'s seven `build_comb` rounds - a different convergence draws a different map, so the solver
is outside this feature's byte-identity bar. `sysmon`-style tricks do not apply; these are genuine
geometry, spread thin.

Declined: coarser sampling in `clear_runs` (moves verdicts); a persistent index across stages (the fabric
changes between stages; the memo already serves the within-stage reuse).
