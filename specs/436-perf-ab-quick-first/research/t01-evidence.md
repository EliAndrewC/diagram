# T01 evidence - make perf-ab, quick first

Measured 2026-10-27 on the clone, the host shared with other sessions.

## The quick form: `make perf-ab A=d2ce4e79c` (the engine before feature 435 against HEAD; seed 25, 40 households, 6 runs)

Took 2.05 min, measured 2026-10-27 (the shell's clock around the run), against 8.2 min for the full sweep (feature 435).

```
 households, seed   A wall    +-  B wall    +-  wall    A cpu    +-   B cpu    +-   cpu      A calls     B calls  calls
         (40, 25)     6.85  0.29    6.82  0.23   -0%     6.83  0.31    6.82  0.23   -0%    6,549,158   7,564,885   +16%
best of each version's runs, alternated A B / B A; +- its worst less its best - read a change against it, never as a pass
floor: none on record for seed 25 at 40 households, 6 runs - take it once: make perf-ab AA=1 SEEDS=25 HOUSEHOLDS=40 N=6
```

## The noise floor: `make perf-ab AA=1 A=HEAD` (HEAD against itself, the same form)

```
 households, seed   A wall    +-  B wall    +-  wall    A cpu    +-   B cpu    +-   cpu      A calls     B calls  calls
         (40, 25)     6.86  0.37    6.96  0.31   +1%     6.86  0.36    6.96  0.31   +1%    7,564,885   7,564,885    +0%
best of each version's runs, alternated A B / B A; +- its worst less its best - read a change against it, never as a pass
floor recorded for seed 25 at 40 households, 6 runs
```

## The quick form again, with its floor printed

```
 households, seed   A wall    +-  B wall    +-  wall    A cpu    +-   B cpu    +-   cpu      A calls     B calls  calls
         (40, 25)     7.30  0.98    7.28  0.98   -0%     7.30  0.98    7.28  0.98   -0%    6,549,158   7,564,885   +16%
best of each version's runs, alternated A B / B A; +- its worst less its best - read a change against it, never as a pass
floor (one engine against itself, taken 2026-10-27T19:43:35Z): wall +1%, CPU +1% - a change inside it is not a change
```

## A subset with its quick run on record: `make perf-ab A=d2ce4e79c SEEDS=25,39` - runs

```
 households, seed   A wall    +-  B wall    +-  wall    A cpu    +-   B cpu    +-   cpu      A calls     B calls  calls
         (40, 25)     7.19  0.15    6.75  0.46   -6%     7.19  0.14    6.74  0.47   -6%    6,549,158   7,564,885   +16%
         (40, 39)     6.29  0.50    6.33  0.08   +1%     6.29  0.50    6.33  0.08   +1%    5,693,497   6,690,769   +18%
best of each version's runs, alternated A B / B A; +- its worst less its best - read a change against it, never as a pass
exit 0
```

## A subset with no quick run of its engines: `make perf-ab A=233534b97 SEEDS=25,39` - refused before any roll, in 6.3 s

```
perf-ab: refused - a subset comparison before a quick one: no quick comparison of these two engines is on record in this clone.
  Run the quick form first, iterate on it, then come back:  make perf-ab A=233534b97 B=HEAD SEEDS=25 HOUSEHOLDS=40
  A case that genuinely needs the wider run first: PERF_AB_QUICK_OK="<reason>" (recorded). This refuses a skipped step, never a timing.
make: *** [Makefile:46: perf-ab] Error 2
exit 2
```

## Reading

- The quick form answers in about a quarter of the full sweep's time, on the case the current work is aimed at.
- The engine before feature 435 against HEAD, seed 25 at 40 households: wall and CPU both -0% (spreads 0.23-0.98 s), calls
  +16% - feature 435's finding, at a quarter of the cost; the floor of that form is +1%.
- CPU time tracks wall time within 0.01 s on every row: the roll is one thread, so CPU time removes waiting (other
  processes holding the core) but not the speed of the core it lands on - on this host's mixed cores it narrows the spread
  less than hoped. The spread of a run (0.98 s in the second quick run) is still the reading's limit.
