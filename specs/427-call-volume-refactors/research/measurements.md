# Measurements: what the roll costs, and how it was taken

**Load this file when:** you need the baseline numbers, or need to re-measure before or after a change.

All measured 2026-10-26 on commit fd707b608 (engine unchanged at dd3793e29), Intel Core Ultra 7 155H, 22 cores, CPython
3.14.4, shapely 2.1.2, numpy 2.5.1.

## Wall time per stage (the baseline)

`make perf LABEL=adhoc SCALING=1`, committed as `dev/perf-log/20261026T114000Z-adhoc-diagram-performance.json`. The reference
hamlet (Inashiro's spec) at seeds 4, 25, 39, 47; the household count varied. CPU seconds equal wall seconds (single-threaded,
CPU-bound; load was 7-10 on 22 cores, so no contention). Median seconds:

| stage | 10 hh | 15 hh | 20 hh | 40 hh |
|---|---|---|---|---|
| homesteads | 0.86 | 1.55 | 2.16 | 4.74 |
| lane_wells | 0.00 | 0.00 | 0.35 | 4.58 |
| web | 0.35 | 0.52 | 0.73 | 3.20 |
| field | 0.48 | 0.95 | 1.04 | 1.98 |
| hinterland | 0.64 | 1.04 | 0.85 | 1.70 |
| windbreak | 0.28 | 0.45 | 0.52 | 0.89 |
| appurtenances | 0.12 | 0.12 | 0.19 | 0.34 |
| notice | 0.10 | 0.11 | 0.12 | 0.25 |
| **total** | **3.3** | **5.2** | **6.8** | **14.7** |

Medians over four seeds, except at 40 households, where they are over three. **At 40 households seed 4 was refused**
(`WebRefused: ... joins_short ... (lane skeleton spine)`) after spending 20.3 s in the web: a correctness failure as well
as a cost, and 40 households is not reliably supported today.

**Per-seed spread matters more than the medians for some stages.** For example, lane_wells per seed: at 20 households
0 / 1.11 / 0.71 / 0 s (seeds 4 / 25 / 39 / 47); at 40, 10.04 / 4.58 / 0.59 s (seeds 25 / 39 / 47). Never subtract a stage
median from a total median to predict a saving (see `hotspots-recompute.md`, wells).

## Call counts per stage (the hotspot data)

`make perf-profile SEED=39 STAGE=<stage> HOUSEHOLDS=<20|40>` for all 23 stages (46 profiles). The raw `.prof` files went to
`dev/perf-raw/` in the session clone (gitignored, not kept). The derived survey is `fanout-2026-10-26.txt` beside this
file, produced by the script in `../tooling-perf-fanout.md`. Python-level calls (every Python and builtin call cProfile sees):

| stage | calls @20 | calls @40 | growth exponent |
|---|---|---|---|
| lane_wells | 4,786,172 | 22,622,782 | 2.2 |
| web | 5,318,952 | 11,052,045 | 1.1 |
| homesteads | 4,542,315 | 10,711,263 | 1.2 |
| hinterland | 3,325,993 | 5,965,598 | 0.8 |
| field | 2,486,936 | 4,607,882 | 0.9 |
| windbreak | 1,794,703 | 3,925,050 | 1.1 |
| appurtenances | 704,594 | 1,932,917 | 1.5 |
| notice | 567,939 | 954,670 | 0.7 |
| everything else | ~0.6M | ~1.0M | |
| **total** | **24.1M** | **62.8M** | **1.4** |

**The time is the call count.** Measured stage seconds divided by Python calls is a steady 0.2-0.45 µs per call across
stages. Shapely is about 1M of the 62.8M; at 40 households lane_wells and windbreak make no shapely calls at all. The hot
path is the project's own pure-Python geometry (`settlement/_geom/primitives.py`: `seg_dist`, `seg_closest`, `point_in_poly`)
and the `min`/`max`/`hypot` calls around it. Shapely appears mostly as a coordinate container (`_coords`, `__iter__`).

## Caveats

- cProfile adds about 225% (research R2 of `l7r/diagram/tools/perf_profile.py`), mostly per Python call, so profiled
  seconds overstate Python's share against GEOS. **Call counts are exact and deterministic per seed**; timings drift with
  load. Use counts to find and verify a multiplier, and an A/B against HEAD for the time.
- One seed (39) for the survey. A chain whose count depends on the seed's geometry (for example lane_wells, zero below
  about 20 households on some seeds) needs a second seed before you size it.
- The survey's chain walk follows the caller edge with the most calls. When a builtin (`min`, `sorted`) sits between two
  frames, it ties a lambda or generator expression to the function that defines it. That is right for nearly every chain
  in the file, but check a surprising chain in the code before you rely on it.

## To re-measure

- Wall time: `make perf LABEL=427-start SCALING=1` before the first change, `-end` after (the feature's bookends).
- Calls: the `make perf-fanout` target this feature adds (`../tooling-perf-fanout.md`); until it exists, the profile loop above.
