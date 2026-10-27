# T08 evidence - the notice board's seats screened by their clearance from what stands

Measured 2026-10-27 on the clone, the host shared with other sessions (load average about 3).

## Calls (`make phase-calls`, seed 39, 40 households, nucleated)

| stage | before | after | change |
|---|---|---|---|
| notice | 953,393 (measured after T02) | 871,838 | -9% |
| the roll | 26,478,205 (after T06) | 26,396,697 | -0.3% |

## Time (`make perf-ab A=HEAD~1 B=HEAD N=3`: alternated, best of 3, each arm's spread; legs timed from their stages)

```
 households, seed   A best spread   B best spread    time      A calls     B calls   calls
          (10, 4)     1.93   0.07     1.81   0.12     -6%    3,559,058   3,557,890     -0%
         (10, 25)     1.49   0.05     1.44   0.04     -3%    1,924,209   1,919,790     -0%
         (10, 39)     1.37   0.04     1.27   0.11     -7%    1,674,747   1,669,383     -0%
         (10, 47)     1.25   0.04     1.19   0.07     -5%    1,659,138   1,656,499     -0%
          (15, 4)     2.62   0.11     2.44   0.19     -7%    3,873,380   3,871,148     -0%
         (15, 25)     2.08   0.10     1.95   0.15     -6%    2,516,218   2,509,231     -0%
         (15, 39)     1.93   0.07     1.82   0.11     -6%    2,333,094   2,326,853     -0%
         (15, 47)     2.09   0.07     1.97   0.12     -6%    2,499,391   2,495,996     -0%
          (20, 4)     3.26   0.09     3.09   0.21     -5%    4,501,706   4,496,787     -0%
         (20, 25)     3.73   0.07     3.62   0.09     -3%    4,969,815   4,960,056     -0%
         (20, 39)     2.84   0.06     2.84   0.03     +0%    3,361,154   3,354,122     -0%
         (20, 47)     2.90   0.08     2.91   0.02     +0%    3,652,754   3,645,584     -0%
          (40, 4)  refused         refused
         (40, 25)     6.54   0.12     6.18   0.39     -6%    7,640,526   7,625,364     -0%
         (40, 39)     5.85   0.07     5.51   0.35     -6%    6,761,842   6,744,459     -0%
         (40, 47)     6.85   0.07     6.55   0.33     -4%    8,252,284   8,249,800     -0%
time: best of each arm's runs; spread: its worst less its best - read the change against the spread, never as a pass
```

## Reading

The table shows B 3 to 7 percent faster at every size, ten households included, while the calls moved by under a tenth of a
percent and the whole notice stage is about 0.15 s of the 40-household roll (its profiled 0.43 s, measured 2026-10-27 (make
perf-profile SEED=25 STAGE=notice HOUSEHOLDS=40), read through cProfile's inflation). A change confined to that stage cannot
take 0.3 s off the roll, so most of this gap is the conditions of the run, not the change - B's spreads (0.33-0.39 s at 40
households) are also several times A's. Read as evidence: the change removes some work (notice -9% calls); its time is too
small to separate from this run's bias. An A/A run of one engine against itself (T04) measures that bias.
