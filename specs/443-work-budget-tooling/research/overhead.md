# What the counters cost (T01, SC-001)

Load this file when: you change a counting site, or ask what the counters add to a roll.

Measured 2026-10-28 on the clone (the host shared with other sessions), the engine before the counters at 29253d4c3 and with
them at b42efb3dc.

## Python calls - unmoved (SC-001)

`make perf-fanout SEED=25 HOT=20000` before (`dev/perf-log/20261028T045040Z-fanout-443-loops.txt`) and after, the Python
functions' calls read from each run's raw profiles (cProfile entries with a file, not `~`):

| households | before | after | change |
|---|---|---|---|
| 20 | 7,092,838 | 7,093,049 | +0.003% |
| 40 | 10,592,082 | 10,591,580 | -0.005% |

Both inside SC-001's one call in a thousand. The push's own count (`sys.monitoring` PY_START, `make perf-ab`'s calls column) is
7,564,885 in both engines at 40 households.

**C builtins rose** - `len()` at a counting site is a call cProfile counts: 19,604,250 to 19,807,023 at 40 households (+1.0%),
12,124,871 to 12,236,913 at 20 (+0.9%). They are not Python calls and the push's guard does not count them; a counting site
that needs a size takes one `len()`.

## Time - inside the floor

`make perf-ab A=29253d4c3` (quick form, seed 25 at 40 households, alternated): wall 7.06 s to 7.14 s (+1%), CPU the same,
against the quick form's floor of -4% (`make perf-ab AA=1`, 2026-10-27). The counters' cost is not distinguishable from noise.

## Inert under `-O`

`PYTHONOPTIMIZE=1 make map GEN=pool/hamlets/inashiro/inashiro.gen.py`: REGENERATED in 7.4 s, "this map's manifest is unchanged
against HEAD" - HEAD's manifest was rolled before the counters existed. T02's `make counters-inert` makes this a gate step.

## Counts checked by hand

`tests/test_work_counts.py` asserts each site's exact count on hand-built inputs (one point test, a 3-point batch, a 2-by-3
distance matrix, a square's four edges, the registry's candidates, placements, drops and moves).
