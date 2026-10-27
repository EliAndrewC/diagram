# T06 evidence - the wells' seat tests asked as arrays

Measured 2026-10-27 on the clone, the host shared with other sessions (load not controlled).

## Calls (`make phase-calls`, seed 39, 40 households, nucleated)

| stage | before (9441ca253) | after (2ccbb7ff9) | change |
|---|---|---|---|
| lane_wells | 2,009,602 | 1,520,139 | -24% |
| appurtenances | 892,154 | 710,211 | -20% |
| the roll | 27,149,548 | 26,478,205 | -2.5% |

## Time (`make perf-ab A=9441ca253 B=2ccbb7ff9 N=3`: alternated, best of 3, each arm's spread)

The snapshot's leg totals are rounded to 0.1 s, coarser than this change; `perf-ab` now sums the stages, timed to 0.01 s
(changed in this task), so later comparisons resolve it. This run read the 0.1 s totals:

```
 households, seed   A best spread   B best spread    time      A calls     B calls   calls
          (10, 4)     1.80   0.10     1.80   0.10     +0%    3,565,522   3,559,058     -0%
         (10, 25)     1.40   0.10     1.40   0.10     +0%    1,995,657   1,924,209     -4%
         (10, 39)     1.30   0.10     1.30   0.10     +0%    1,697,302   1,674,747     -1%
         (10, 47)     1.20   0.10     1.20   0.00     +0%    1,663,132   1,659,138     -0%
          (15, 4)     2.60   0.00     2.50   0.10     -4%    3,908,819   3,873,380     -1%
         (15, 25)     2.10   0.00     2.00   0.10     -5%    2,540,080   2,516,218     -1%
         (15, 39)     1.80   0.10     1.80   0.10     +0%    2,355,319   2,333,617     -1%
         (15, 47)     2.00   0.10     2.00   0.10     +0%    2,504,906   2,499,391     -0%
          (20, 4)     3.10   0.20     3.10   0.10     +0%    4,531,356   4,501,706     -1%
         (20, 25)     3.60   0.10     3.60   0.10     +0%    5,070,784   4,969,815     -2%
         (20, 39)     2.80   0.10     2.70   0.10     -4%    3,477,420   3,361,154     -3%
         (20, 47)     2.90   0.00     2.90   0.00     +0%    3,661,984   3,652,754     -0%
          (40, 4)  refused         refused
         (40, 25)     6.60   0.10     6.40   0.10     -3%    8,083,073   7,640,526     -5%
         (40, 39)     5.80   0.10     5.60   0.20     -3%    7,049,862   6,761,842     -4%
         (40, 47)     6.60   0.20     6.70   0.10     +2%    8,320,973   8,252,284     -1%
time: best of each arm's runs; spread: its worst less its best - read the change against the spread, never as a pass
```

## Reading

At 40 households the roll is 3% faster on seeds 25 and 39 (6.6 -> 6.4 s, 5.8 -> 5.6 s, spreads 0.1-0.2 s) and 2% slower on
47 (inside its spread); at 10 to 20 households nothing separates from the spread. That is what the plan expected: about 0.1 s
of an ~8 s roll (checklist item 3's GUESS). Time and calls agree in direction; the gain is small and real only where the
wells' lattice is largest, which is where the work grows (checklist item 4).

No pool map is expected to move: each array test is its one-seat test's arithmetic (`tests/hamletgen/homesteads/
test_well_seats_387.py`, `test_well_siting_154.py`, `tests/settlement/test_geom.py` hold them equal on random cases); the
landing's `make maps-moved` and cohort say.
