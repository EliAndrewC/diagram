# Research - 218 efficient overlap checks

## R1 - where the time went before the change (2026-09-08)

A from-scratch roll of the reference hamlet (Inashiro, seed 4, `make hamlet ... --out <scratch>`,
every output written), on the container (22 vCPU, the placement single-threaded):

| step | seconds |
|---|---|
| placement roll, every stage | 23.7 |
| render: PNG, the HTML with its raster, SVG | ~10 |
| make, the reference-check cache hit, imports | ~2 |
| **wall clock** | **36.2** |

A second roll with `--no-render` (SVG, JSON and the raster-less HTML still written) took 26.2 s, so
the PNG and the raster-backed HTML are the ten seconds.

The stage profile of that roll (`make hamlet PROFILE=1`), the three that matter:

| stage | seconds | share |
|---|---|---|
| `stage_hinterland` | 8.09 | 34.1% |
| `stage_windbreak` | 7.27 | 30.7% |
| `stage_field` | 5.40 | 22.8% |
| everything else | 2.9 | 12.4% |

`make perf-profile SEED=4 STAGE=<stage>` (cProfile, about +225% on the stage it wraps) then said which
functions:

**Windbreak** - 23.9 s profiled. `village_grove` is called twice (the belt, then the copse) and
`_hard_blocked` 37,490 times - once per candidate clump position, including the re-seat probes. Each
call ran `edge_dist` over `self.field_polys` and `self.dry_polys` - 25 polygons on this map (the
paddy outline and 24 dry plots) - which is 936,709 `edge_dist` calls and **7.19 million `seg_dist`
calls**, 18.5 of the 23.9 profiled seconds (77%). `_lane_blocked` 74,980 calls, 6.6 s cumulative,
walking every corridor segment per call. The grove kept 150 clumps (145 in the belt, 5 in the copse).
The trees never test against each other: a dense belt's clumps overlap by design. The scan was
against geometry that does not change during the fill, and `field_polys` is an `Indexed` registry
with a spatial index the farmhouse placer already uses - the grove walked it linearly.

**Hinterland** - 25.8 s profiled. `marsh` 19.3 s of `hinterland`'s 24.6; inside it `_sparse` ran
27,383 times and `_on_watercourse` 141,142 times, 18.8 s cumulative. On 20,964 of those calls
`_watercourse_segs` was REBUILT - the stream, two channels and the 13 drawn laterals re-split into
taper pieces (`taper_pieces` 230,604 calls, 8.0 s) - and every segment then scanned (6.7 million
`seg_dist` calls), because `_sparse` bypasses the pre-boxed grid `wat_b` whenever the mark carries a
mound pad, which the tint and the tuft both do. The same function builds one grid per pad for the
dike crests (`mnd_g`); the watercourse test did not get the same treatment when feature 145 indexed
the rest of the scatter. After the marsh, `commons` and `open_ground_patches` (`_ok` -> `_clear_gap`,
every crop polygon per candidate square) are the visible rows.

**Field** - 10.8 s profiled, 7.2 of them in `close_seams` and 2.8 in `_carve`, about 540,000 shapely
calls. No redundant scan: the cost is the seam-closing algorithm itself. Out of scope (the GM), and
the next candidate.

Raw profiles: `dev/perf-raw/20260908T1223*-seed4-{windbreak,hinterland,field}.prof` (gitignored,
archived to the perf-logs repository); the derived tables in `dev/perf-log/20260908T1223*-profile-adhoc-*.txt`
of the `diagram-research` clone that took them.

## R2 - the census of per-candidate scans in the two stages

Every per-candidate scan of static geometry found in the two stages, with its cumulative time on the
seed-4 cProfile of its stage BEFORE conversion and its disposition against the 0.10 s bar (spec
FR-002, D5). Profiled seconds; the profiler adds about +225%, so divide by ~3 for wall clock.

| where | what it scanned per candidate | profiled s | disposition |
|---|---|---|---|
| `village_grove` `_hard_blocked` | every edge of every crop and dry-plot ring, every watercourse segment, every dike ring | 18.50 | CONVERTED - `GroveBlocks.hard` |
| `village_grove` `_lane_blocked` | every corridor segment | 6.60 | CONVERTED - `GroveBlocks.lane` |
| `village_grove` `_local_blocked` | every occupancy circle, every sun-corridor rectangle | 2.20 | CONVERTED - `GroveBlocks.local` (circles and rects in grids) |
| `village_grove` `_reseat` and the gap fill | every clump already seated (proximity) | 1.46 | CONVERTED - `Seats`, filed as they land |
| `village_grove` grid walk | the outline, by `point_in_poly` | 1.03 | CONVERTED - `RingIndex.inside` |
| `marsh` `_sparse` -> `_on_watercourse` with `near=None` | REBUILT `_watercourse_segs` (taper split included) and scanned every segment | 18.84 | CONVERTED - a grid per pad, then folded into the marsh's `KeepoutGrid` (slot 3) |
| `marsh` `_sparse` halo | every urban-halo rect and wellhead circle | ~0.10 | CONVERTED - into the `KeepoutGrid` |
| `commons` `_sparse` halo | every urban-halo rect (1.76 M rectangle tests) and wellhead circle | 0.22 | CONVERTED - into the `KeepoutGrid` |
| `commons` / `marsh` `_sparse`, ten indexed families | one `near` call and one wrapper per family per point - 1.33 M `near` calls | 2.70 | CONVERTED - `KeepoutGrid`: one cell read per point |
| `open_ground_patches` `_ok` -> `_clear_gap` | every edge of every crop ring per candidate square | 0.61 | CONVERTED - `_crop_refuses` from a `RingIndex`, crops boxed per rung |
| `_strip_blocked` (bamboo, fixtures) | every edge of every paddy and marsh ring per corner; `_on_watercourse` with no `near` (210 rebuilds); every dry plot | 0.39 | CONVERTED - `Footing`, built once per pass |
| `_trunk_blocked` (fixtures) | the same, per persimmon trunk | 0.15 | CONVERTED - `Footing` |
| `_on_crescent_pond` (was the tail of `_on_watercourse`) | a registry lookup per point | 0.16 | CONVERTED - the registry read once per scatter |
| `open_ground_patches` `_ok` | every house/well/pond circle, every keep rect, every lane and stream (`_near_line`), every marsh ring (`_wet`) per candidate | < 0.10 each | LEFT, listed: 2,565 candidates against 15 houses; below the bar |
| `_strip_blocked` | `s.placed` (grows during the pass), the wells/board/byres/sheds, the lanes, the tree crowns | < 0.10 each | LEFT, listed: dynamic or a dozen items; below the bar |
| `woods.py` `_fringe` / `forest` | every crop polygon per tree | 0.01 (the whole stage) | LEFT, listed: `stage_woodland` is 0.01 s |

**The commons scrub scatter, reported either way (FR-002).** Its keep-out tests were already indexed
family by family (feature 145); what this feature changed is the ten grids into one and the halo into
it. After that the scatter's cost is its own work per glyph: on seed 4 it throws 134,877 points,
ACCEPTS about 100,000 of them (the other quarter fall on a keep-out or thin out in the feather), and
for each accepted tuft draws six more random numbers and three `<line>` elements. The outline test,
the cell read and the feather are about 40% of the scatter's remaining time; the glyphs' random
draws and SVG text the rest. There is no per-candidate scan left in it. Two levers would cut it
further, both changing what the map draws, both recorded for the GM (spec D6): fewer marks per acre
(the densities are research-set), or a vectorized scatter (numpy for the throws and the tests, the
SVG assembled in bulk) - the latter could plausibly take the stage under half a second.

**Out of scope, recorded:** `stage_field` 5.4 s (the seam-closing algorithm, R1), `stage_track`
1.0 s, `stage_homesteads` 0.9 s - now the three largest stages. The doctrine (constitution X clause
15) applies to each when it is next worked.

## R3 - after the change

The stage profile of the reference hamlet's seed 4 after each conversion (`make map PROFILE=1`, real
seconds, the map byte-identical at every row - `git status` clean on `pool/` after `make map`, and
after the tier sweep `make maps` over all five hamlets):

| stage | before | windbreak indexed | marsh water grid | halo, footing, parcels | one grid per scatter |
|---|---|---|---|---|---|
| `stage_windbreak` | 7.27 | **0.51** | 0.50 | 0.50 | **0.50** |
| `stage_hinterland` | 8.09 | 8.41 | 2.60 | 2.42 | **1.27** |
| roll total | 23.7 | 17.5 | 11.4 | 11.3 | **10.2** |

Windbreak: 7.27 s to 0.50 s, under the GM's one-second target (SC-002). Hinterland: 8.09 s to 1.27 s
- an 84% cut, past the 50% floor, but ABOVE the one-second target by about a quarter of a second,
reported as the shortfall SC-002 requires; the reason and the levers are in R2.

A from-scratch roll of the reference hamlet with every output written (SVG, PNG, HTML), the reference
check served from a warm roll cache, `time make hamlet ... --out <scratch>`:

| | before | after |
|---|---|---|
| wall clock | 36.2 s | **22.7 s** |
| of which placement | 23.7 s | 10.2 s |

The render (PNG and the raster-backed HTML, about 10 s) is untouched and is now half the roll.

## R4 - the gate's time, and the bookends

The GM asked how long `make done` takes when this is finished, with their own caveat that the gate
rolls only 3 maps and might not move much. The green gate that verified this feature:

| run | wall | test phase | tests | what it did |
|---|---|---|---|---|
| feature 216's landing gate (the last recorded before this), 2026-09-08 | 143 s | 123 s | 3,471 | warm roll cache, hooks-test skipped, incremental |
| this feature's gate, 2026-09-08 13:22 UTC | 215 s | 131 s | 3,487 | FULL (no baseline after the merge of main), every roll cold (the engine changed, so the five pool hamlets and the reference re-rolled), all 21 guard suites re-run (main's merge touched them), and another session's `make done` running beside it on the same box |

So the number the GM asked for is 215 s, and it is not a like-for-like comparison: the test phase
itself was 131 s against 123 s with six cold rolls where 216's run had none, which is the rolls
halving (below) paying for the cache miss. The gate's cost is set by what it runs around the rolls -
the guard suites, the coverage merge, the browser test - so, as the GM expected, the roll speed-up
is most of a roll and a small share of a gate. `scripts/_gatecost.py done` (the median of recorded
green runs) is the standing figure to ask.

The bookends (`make perf`, the reference spec across seeds 4/25/39/47, local, `perf-report`):

| seed | 218-start | 218-end | change |
|---|---|---|---|
| 4 | 24.1 s | 10.2 s | -57.7% |
| 25 | 25.9 s | 14.0 s | -45.9% |
| 39 | 21.1 s | 9.8 s | -53.6% |
| 47 | 26.2 s | 14.2 s | -45.8% |
| **total** | **97.3 s** | **48.2 s** | **-50.5%** |

Band 0: nothing owed. Seeds 25 and 47 fall less than seed 4 because their field stage (out of scope)
is a larger share of their roll.
