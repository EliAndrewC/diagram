# Research - 220 the field fitted once

## R1 - the profile before (2026-09-09, seed 4, `make perf-profile STAGE=field`)

`stage_field` 5.40 s real (10.85 s under cProfile). `fit_field` -> `_fit_at_aspect` -> **`build_comb`
x4** at 2.68 s profiled each - the search carves the whole comb at every guess. Inside a build:

| function | calls | profiled s | share of a build |
|---|---|---|---|
| `close_seams` | 4 | 7.22 | 67% |
| `_unjog` | 4 | 2.87 | |
| `_trade` | 155 | 2.79 | |
| `_absorb` | 364 | 1.78 | |
| `_carve` | 4 | 2.81 | 26% |
| `_carve_sector` / `_sector_body_rows` | 24 / 20 | 2.47 / 2.28 | |
| `supply_bank_clearance` | 86,259 | 1.68 (1.07 self) | |
| `in_supply` -> `_quad_in_supply` | 2,557 | 1.35 | |
| shapely: `Polygon.__new__` 34,881, `buffer` 38,574, `bounds` 267,604, `intersection` 23,884, `is_valid` 27,757 | | 4.8 of the 7.2 in the seams | |

`net_acres` reads the plot polygons only; `tail_dangles` the plots' extent; `net_bends_acutely` the
channels - none reads what the finish adds.

The commons scatter's own per-glyph work bounded feature 218's hinterland; here the bound is the
search paying the finish three times over.

## R2 - step 1: the search carves, the winner is finished once (2026-09-09)

**The first cut overshot, and the reason is worth keeping.** Scored on the bare carve's acreage, the
search landed the reference hamlet at 21.9 acres against a 19.5 target (the old fit: 18.88): 684 plots
where there had been 574, 29 dry plots for 24, and `stage_homesteads` went from 0.9 s to 4.0 s seating
fifteen houses against a larger field - the roll got SLOWER, 9.9 s to 11.4 s, with the field at 2.44 s.
The seam pass does not conserve the carved area; it PLANTS every scrap of bare ground inside the command
area, and that is 11-21% of the fan. The "conserves ground" premise in the approved assessment was wrong
about the total (it is right that a trade hands the same polygon across a wall).

**The prediction.** A carve knows what the finish will plant: the carved plots plus the bare ground
inside the command area (`field - plots - water - outside`, the three geometries `close_seams` itself
computes first). Measured on the reference fan at six sizes, before any search change (`carve_comb`,
the estimate, `finish_comb`, wall seconds):

| k | carved acres | predicted | finished | finished / carved | prediction error | carve s | estimate s | finish s |
|---|---|---|---|---|---|---|---|---|
| 0.8 | 9.67 | 11.70 | 11.70 | 1.210 | +0.04% | 0.17 | 0.065 | 0.48 |
| 0.9 | 12.35 | 14.52 | 14.52 | 1.175 | +0.05% | 0.22 | 0.069 | 0.87 |
| 1.0 | 14.47 | 16.13 | 16.12 | 1.114 | +0.03% | 0.19 | 0.054 | 0.74 |
| 1.1 | 15.84 | 18.72 | 18.72 | 1.182 | +0.03% | 0.22 | 0.059 | 1.14 |
| 1.2 | 18.74 | 21.09 | 21.09 | 1.125 | +0.02% | 0.26 | 0.067 | 0.97 |
| 1.3 | 21.20 | 24.29 | 24.28 | 1.145 | +0.03% | 0.29 | 0.079 | 0.94 |

The finish costs three to five carves; the prediction a quarter of a carve; and it is within 0.05% of
the finish everywhere. So `_fit_at_aspect` scores `CombCarve.planted_area()` and `fit_field` finishes
the best carve once.

**The result on seed 4** (`make map PROFILE=1`, real seconds):

| | before | step 1 |
|---|---|---|
| `stage_field` | 5.25 | **2.43** |
| `stage_homesteads` | 0.90 | 0.90 |
| roll total | 9.9 | **7.2** |

Against the GM's yardstick (field under 3 s, the roll around 7.5 s): both met.

**The map moved by a hair.** The reference regenerated with the same 574 plots and `roll_acres`
18.87774 -> 18.87782: the search's power-law step reads the acreage numbers, and a prediction 0.03% off
the finished figure moves the chosen multiplier in its fourth decimal, so every coordinate shifts by a
fraction of a pixel. A moved manifest all the same, so the pool sweep and the review pass of FR-005 run
over it (R2b below).
