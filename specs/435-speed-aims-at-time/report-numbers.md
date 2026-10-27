# Feature 435 - the new numbers

For the GM, to decide what performance work comes next (FR-008, SC-006). Measured 2026-10-27 on the clone, the host shared
with other sessions (load average about 3). Engine before this feature: d2ce4e79c (the 435-start bookend). After it:
34ee43bee.

## In one paragraph

The reverts put back the calls that bought no time, and time did not move: the roll's calls at 40 households are up 44% by
the profiler's count (+16-18% by the snapshot's, which skips builtins), and its time is unchanged within what this host can
resolve. An A/A run - one engine timed against itself - swings up to 9% on a single seed and size, so a best-of-3 comparison
here separates effects only above about 5-9%. The two cheap fixes built (the wells, the notice board) removed real work
(lane wells -24% calls, notice -9%) worth about 0.1 s of a 6-7 s roll, below that floor. The third (the homestead bundle
built once) was measured and set down: its layouts are already kept per seat offered, and keying them on the household is
feature 297's withdrawn change.

## Calls by stage, seed 39, 40 households (`make phase-calls`, cProfile's count, builtins included)

| stage | before 435 (T57) | after the reverts (T02) | after the fixes (now) | now vs before |
|---|---|---|---|---|
| homesteads | 5,205,329 | 7,722,633 | 7,722,160 | +48% |
| web | 3,278,818 | 4,933,316 | 4,933,316 | +50% |
| field | 2,869,011 | 3,694,962 | 3,694,962 | +29% |
| hinterland | 2,543,420 | 4,357,785 | 4,357,785 | +71% |
| lane_wells | 1,267,184 | 2,009,602 | 1,520,149 | +20% |
| windbreak | 1,119,945 | 1,561,346 | 1,561,346 | +39% |
| notice | 779,962 | 953,393 | 845,220 | +8% |
| appurtenances | 494,974 | 892,154 | 710,091 | +43% |
| woodland | 205,647 | 299,659 | 299,659 | +46% |
| seat | 205,378 | 237,697 | 238,162 | +16% |
| crossings | 125,028 | 160,948 | 160,948 | +29% |
| labels | 107,013 | 107,013 | 107,013 | +0% |
| sink | 77,396 | 90,824 | 90,824 | +17% |
| washing | 30,524 | 59,404 | 59,404 | +95% |
| sties | 27,684 | 28,150 | 28,150 | +2% |
| frame | 18,062 | 31,097 | 31,097 | +72% |
| **the roll** | **18,364,796** | **27,149,548** | **26,369,851** | **+44%** |

The reverts (T02) added 8.8M calls - builtins written back as builtins and helpers called again, the work they always did. The
fixes (T06, T08) took 0.78M back. `labels` and `sties` were untouched by either.

## Time: the engine before this feature against after it (`make perf-ab`, alternated, best of 3, each arm's spread)

```
 households, seed   A best spread   B best spread    time      A calls     B calls   calls
          (10, 4)     1.87   0.10     1.80   0.14     -4%    2,511,504   3,554,860    +42%
         (10, 25)     1.48   0.09     1.42   0.10     -4%    1,590,284   1,917,530    +21%
         (10, 39)     1.35   0.07     1.38   0.02     +2%    1,420,851   1,667,233    +17%
         (10, 47)     1.25   0.04     1.24   0.04     -1%    1,334,193   1,653,109    +24%
          (15, 4)     2.57   0.20     2.43   0.20     -5%    3,209,092   3,866,908    +20%
         (15, 25)     2.09   0.12     1.94   0.08     -7%    2,072,942   2,505,791    +21%
         (15, 39)     1.91   0.10     1.87   0.09     -2%    1,895,089   2,323,563    +23%
         (15, 47)     2.07   0.10     2.04   0.08     -1%    2,085,368   2,491,716    +19%
          (20, 4)     3.22   0.14     3.25   0.06     +1%    3,691,234   4,491,507    +22%
         (20, 25)     3.67   0.10     3.67   0.08     +0%    3,866,749   4,955,586    +28%
         (20, 39)     2.83   0.10     2.87   0.06     +1%    2,848,073   3,349,002    +18%
         (20, 47)     2.87   0.07     2.91   0.08     +1%    2,971,164   3,640,404    +23%
          (40, 4)  refused         refused
         (40, 25)     6.59   0.19     6.57   0.02     -0%    6,581,482   7,613,894    +16%
         (40, 39)     5.83   0.11     5.54   0.32     -5%    5,724,470   6,735,669    +18%
         (40, 47)     6.75   0.10     6.82   0.07     +1%    7,027,876   8,239,850    +17%
time: best of each arm's runs; spread: its worst less its best - read the change against the spread, never as a pass
```

The calls column is the snapshot's counter (Python functions, not builtins). Time moved -7% to +2%, inside the A/A floor below.

## The floor: the same engine against itself (`make perf-ab A=HEAD B=<HEAD's hash>`)

```
 households, seed   A best spread   B best spread    time      A calls     B calls   calls
          (10, 4)     1.94   0.01     1.76   0.18     -9%    3,554,860   3,554,860     +0%
         (10, 25)     1.50   0.03     1.42   0.09     -5%    1,917,530   1,917,530     +0%
         (10, 39)     1.37   0.02     1.37   0.02     +0%    1,667,233   1,667,233     +0%
         (10, 47)     1.27   0.00     1.26   0.01     -1%    1,653,109   1,653,109     +0%
          (15, 4)     2.42   0.24     2.61   0.01     +8%    3,866,908   3,866,908     +0%
         (15, 25)     1.95   0.17     2.08   0.03     +7%    2,505,791   2,505,791     +0%
         (15, 39)     1.83   0.11     1.82   0.11     -1%    2,324,086   2,323,563     -0%
         (15, 47)     2.10   0.01     2.00   0.09     -5%    2,491,716   2,491,716     +0%
          (20, 4)     3.30   0.02     3.20   0.10     -3%    4,491,507   4,491,507     +0%
         (20, 25)     3.75   0.01     3.58   0.16     -5%    4,955,586   4,955,586     +0%
         (20, 39)     2.87   0.02     2.87   0.03     +0%    3,349,002   3,349,002     +0%
         (20, 47)     2.92   0.02     2.92   0.02     +0%    3,640,404   3,640,404     +0%
          (40, 4)  refused         refused
         (40, 25)     6.21   0.43     6.59   0.02     +6%    7,613,894   7,613,894     +0%
         (40, 39)     5.68   0.23     5.85   0.03     +3%    6,735,669   6,735,669     +0%
         (40, 47)     6.88   0.08     6.86   0.03     -0%    8,239,850   8,239,850     +0%
time: best of each arm's runs; spread: its worst less its best - read the change against the spread, never as a pass
```

Identical code, identical calls, -9% to +8% apart. This is the resolution of a best-of-3 A/B on this host today: an effect
smaller than about 5-9% on one seed and size cannot be told from the conditions of the run. It also reads back on T08's A/B
(3-7% at every size for a change worth well under 1%): that was this floor, not the change.

## The bookends (`make perf LABEL=435-start` / `-end`, the 10-household reference rows)

`make perf-gate` reads the end against the start in CPU seconds: -9.7% in all (seeds 4, 25, 39, 47: -10.7%, -9.1%, -10.0%,
-8.7%), measured 2026-10-27 (make perf-gate). CPU time moves less with load than wall time, but this is one pair of runs four
hours apart, not alternated, so it is read as a direction beside the A/B above, not as a gain.

## What was done

- **The checklist and its tools** (T01): `docs/performance-checklist.md`; a "Performance work?" line on every task and
  `make task-add PERF=1`; `make perf-ab`; the perf-audit agent's occasion; the guidance in the constitution and the dev docs.
- **The reverts** (T02, `t02-evidence.md`): every call-cutting change of 427 T07, T08, T09, T12 and 417 T54, T63, T64, T65,
  split into a moves-work and a removes-work arm per commit and timed in a 14-arm rotation. Every arm's time sat inside the
  spread. The eight moves-work arms (inlined helpers, builtins written out) were REVERTED. Kept: `removes-T54` (its work grows
  4.2% -> 13.2% from 20 to 40 households) and `removes-T07`, `-T08`, `-T09`, `-T63` (the round arbiter, ask:435-removes-arms:
  each removes a scan of unchanging geometry repeated per candidate, which grows with the settlement). No pool map moved.
- **The cheap fixes** (T03):
  - wells (T06, `research/t06-evidence.md`): the verge, wood-floor and belt tests asked of the seat lattice as arrays and kept
    for the stage; lane wells 2.01M -> 1.52M calls, appurtenances 0.89M -> 0.71M.
  - notice board (T08, `research/t08-evidence.md`): `_fits`' clearance from what stands asked first as a screen and not again;
    notice 0.95M -> 0.85M calls.
  - the bundle built once (T57 item 3): set down by the round arbiter (ask:435-bundle-once) - about 0.3 s of the roll it might
    have bought, against undoing feature 297's measured decision. `_bundle_geom`'s docstring, which overstated the cache and
    led T57 to rank it cheap, now says the layouts are per seat offered (2,369 for 40 households).
- Found on the way and fixed: `lay_fixtures`' docstring (stale since feature 328), `_fits`' margins claim, the notice board's
  combined seat claim split into its three decisions, 0190's 6 ft spelled once, and `perf-ab` now timing a leg from its
  stages to the hundredth (the snapshot rounds a leg to the tenth). Three record notes are filed as T05, T07 and T09.

## What the numbers suggest next (the GM's to decide)

1. **Time measurement first.** At ±9% between identical runs, no change worth under ~5% can be confirmed here. Options: more
   runs per arm (`make perf-ab N=7` or more, at the cost of wall time), CPU time beside wall time (the snapshot already records
   `cpu_stages`), or pinning both arms to one core. Each is cheap to try; without one, the time evidence for small fixes is
   only a direction.
2. **Where the time is.** Homesteads (31.6% of the 40-household roll's time at the 435-start bookend, seed 25), field (17.3%), hinterland (14.8%) and web (12.4%) hold most of it, and each is many
   Python calls on one value at a time (T57 section 3). T57's item 10 - the geometry layer moved into arrays - is the only
   candidate with a large expected effect, and it is the open decision from before this feature.
3. **The bundle**, if it is wanted later: lay the fixtures only for the side and seat chosen rather than for every envelope
   probe, or give the seating more room (SEATING_GROUND_FT first) so per-seat rerolls are not needed and a per-household
   template key could return (the round arbiter's two candidates).
