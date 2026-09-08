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

(filled in as the conversions land)

## R3 - after the change

(the stage profile after, the from-scratch roll after)

## R4 - the gate's time

(a green `make done` after the change, beside the last recorded one before it)
