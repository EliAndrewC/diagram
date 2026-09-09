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

## R2b - step 1 on the pool

`make maps` clean (the reference, the five tripwire seeds, then Kashikawa, Kuwabata, Mizuguchi, Sawada).
Four hamlets moved and are under `settlement-review` (FR-005); Kuwabata, the polder, is byte-identical:

| map | paddy plots | roll acres | else |
|---|---|---|---|
| Inashiro | 574 -> 574 | 18.8777 -> 18.8778 | sub-pixel |
| Kashikawa | 802 -> 801 | 26.930 -> 26.924 | dry plots 29 -> 27, lanes 13 -> 14, cluster aspect 3.08 -> 3.17 |
| Mizuguchi | 498 -> 481 | 15.82 -> 15.49 | cluster aspect 3.44 -> 2.40 - the house cloud re-seated |
| Sawada | 778 -> 770 | 24.55 -> 24.62 | dry plots 22 -> 26, lanes 16 -> 13 |

The search's path through its guesses is what moves: each guess's predicted acreage sits a few
hundredths of a percent off the finished figure the old search read, the power-law step reads those
numbers, and on three maps the winning multiplier landed a plot row away.

## R3 - step 2: the stroke index (2026-09-09)

`StrokeIndex` (`waterfields/banks.py`): the stroke's segments in a 64 px cell grid; a query walks the
segments in the cells within the caller's reach, in index order, with `supply_bank_clearance`'s own
arithmetic (`_nearest_segment`, one body for both walks). The first cut fell back to the full walk
whenever the nearest of those was beyond the reach - and that was a THIRD of all calls (27,000 of
78,000), because the callers' bbox gate admits every point inside a stroke's box, most of them far
from its line. Measured: no gain, 2.48 s against 2.43 s. The two hot callers (`_clear_supply`,
`_quad_in_supply`) only ever act on a gap under the reach, so for them a beyond-reach point is
answered `BEYOND` (gap 1e9) without the walk - the same verdict, proven by `test_strokes.py` on random
strokes and points; the hem's `_bank` reads the nearest half-width wherever the point stands and keeps
the exact fallback. Then: **`stage_field` 2.43 s -> 2.09 s**, the roll 7.2 s -> 6.9 s, every pool map
byte-identical to step 1. Against the GM's yardstick (near 2.4 s after step 2): met.

## R4 - step 3: one geometry per plot, neighbors by tree (2026-09-09)

`waterfields/seams/geoms.py`: `PlotGeoms` builds `Polygon(ring).buffer(0)` once per ring OBJECT (the
passes reassign a ring, never mutate one in place) and answers "which plots touch this box" from an
`STRtree` over the same vertex-extent boxes the old gate compared, so the candidate set is identical;
`_trade`'s three scans over every plot and `_absorb`'s scan over every basin read it. `_unjog` fell from
0.78 s to 0.22 s profiled.

**A dead end, measured.** `GeomTree`'s first form rebuilt its tree after every merge the pocket pass
made - 101 rebuilds of a 600-basin tree per roll, 0.68 s profiled, MORE than the scan it replaced. It
now keeps a `changed` set and reads a replaced basin's current envelope directly; the tree is built once
per round. `stage_field` **2.09 s -> 1.71 s**, `close_seams` 1.8 s -> 0.95 s profiled, the roll 6.5 s,
every map byte-identical to step 1.

**After the three steps** (seed 4, real seconds):

| | before | step 1 | step 2 | step 3 |
|---|---|---|---|---|
| `stage_field` | 5.25 | 2.43 | 2.09 | **1.71** |
| roll total | 9.9 | 7.2 | 6.9 | **6.5** |

**What is left in the field** (3.7 s profiled, ~1.7 s real): the four carves are 2.1 s profiled - the
sector-row carve itself (`_sector_body_rows`, `edge`, `_bnd`, the per-quad supply test at a 3 px step) -
and the one finish 1.0 s, of which the seam passes are 0.95. The GM's assessment named the carve as what
"under a second would need"; its share is now 58% of the stage and it is the next lever (spec D3).

## R4b - a defect the review found, fixed in the work (Principle XIV)

The `settlement-review` of Inashiro (step 1's delta) found two recorded plot rings that cross
themselves - #29 at (1433.7, 1312) and #303 at (1897.7, 1553.3), a 2 px needle each, one of them
byte-identical across the delta and so pre-existing. Ink-invisible under the bund stroke; not a simple
polygon for any shape metric. Cause: `close_seams` repairs bow-ties at its START (so a crossing ring's
ground returns to the pocket pool), but the trades and welds that follow judge a `buffer(0)` COPY of the
ring they record, and the manifest rounds every vertex to 0.1 px - a ring valid unrounded can revisit a
vertex exactly once rounded. Fix: the repair is lifted to `_repair_crossing_rings` and runs again at the
END of the pass on the ring as the manifest will round it; consumes no randomness, so the plot count
and the RNG are untouched. On the reference: 574 rings, the two repaired, none invalid, `roll_acres`
18.8778 -> 18.8766. Guard: `tests/gate/test_paddy_fabric.py::test_every_recorded_plot_ring_is_a_simple_polygon`
on the cached roll - it fails on the code before the fix. The review's second note, the stale acreage in
`inashiro.notes.md`'s comparison table (18.4 for a drawn 18.9), is corrected in place.
