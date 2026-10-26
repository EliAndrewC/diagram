# T09's measurements: the water family (US4)

**Load this file when:** you check what T09 removed, or re-measure it.

Seed 39 at 40 households, observed 2026-10-26 (method: `make perf-fanout STAGES=field HOT=20000`; the start is
`dev/perf-log/20261026T222703Z-fanout-427-T09-start.txt`, every stage; the end `dev/perf-log/*-fanout-427-T09d.txt`).

| chain | what changed | before | after |
|---|---|---|---|
| R7, the field settle: `Fabric.add` -> `verdict` -> `ring_violations` -> `collector_crossings` -> a generator -> `_seg_dist` | each collector's box and its segments' boxes built once a context (`RingContext.drain_index`); a point measured only against the segments whose box holds it, stopping at the first within reach | the generator 67,212, `_seg_dist` 63,478 | under 20,000 (gone) |
| `brook_rules.crosses_mid_run` -> `_proper_cross` -> `side` | every joiner leg against every water leg in loops, the side tests inline | `side` 111,914, `_proper_cross` 55,692, the generator 55,716 | gone |
| `partition.keep_rows` -> shapely `length` | every piece's length in one call | 15,496 lengths, 62,650 wrapper calls | gone |
| R6's remainder: `_outside_command` -> `drain_f` -> `_f_at_u` -> `to_uf` | the collector and the canal in the frame once a band (`f_at_u_of`) | 83,038 | gone |
| `settle.ring_of`, `RingContext.near_supply` (shapely's Python wrappers) | the coordinates read and the ring's line built in one call each | ~50,000 wrapper calls | under 20,000 |
| `_crop_edge`, `_nearest_segment`, `brook_rules._dist_to_course`, `ring_rules._seg_dist` | the clamps and maxima written as conditionals | 275k `abs`, 380k `max`, 330k `min` (the stage's) | the `abs` and the clamps' calls gone |

The field stage: 4,070,240 -> 2,925,335 calls at 40 households, 2,382,393 -> 1,742,483 at 20. Every pool manifest unchanged
against HEAD after every step (`make maps-moved`).

A defect the survey caught that the tests and the pool did not: `shapely.linestrings` refuses an empty ring where
`LineString([])` was an empty line meeting nothing - seed 39 asks `near_supply` of one; guarded, and a test holds it.
