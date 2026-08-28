# Research: feature 145 - the hamlet coverage floor, and the sixteen-second roll

All `research: rendering` - nothing here is about how a place was built. Every number is a stopwatch
or a cProfile on this container (22 cores, several sessions sharing it); the bookends are the record.

## R1 - "What are we doing billions of computations on exactly?" (the GM's question)

Profiled on the reference hamlet (Inashiro, seed 4) and the cohort's two slowest seeds, 2026-08-28,
BEFORE any change (`dev/perf-log/20260828T1634*-profile-adhoc-*`, bookend `144-start` = 128.2 s over
seeds 4/25/39/47 = 17.6 / 51.0 / 19.9 / 39.7 s):

| stage | seed | what the time was | calls |
|---|---|---|---|
| `hinterland` | 4 | the scrub and marsh scatters asking the outline "am I inside, how far is the edge" per throw, walking EVERY edge each time | 1.3M `point_in_poly`, 156k `edge_dist`, ~5M `seg_dist`; 13.4 of 20.6 profiled s |
| `web` | 25 | `FabricIndex.fouled` - the grid narrowed WHICH polygons a lookup tested, but each polygon was still walked edge by edge, and the field envelope / crop rings / marsh are `big` (tested on every lookup) | 1.19M `fouled`, 30.8M `seg_dist`; 35.6 of the roll's 51 s |
| `field` | 47 | `fit_field`'s bisection: nine carves per aspect, five aspects, most of them at aspects where the fan SATURATES (16-17 acres against 19.5 whatever k) | 42 `build_comb` at ~0.6 s each; 26.2 s |
| `field` | 4 | four carves where the first predicts the answer | 3.5 s |

Not billions - tens of millions of segment operations per roll, in Python, on questions whose answer
depends only on the few edges near the point. The shape is the one `dev/performance.md` already
names: a per-candidate scan of geometry that does not change during the scan.

## R2 - the fixes, and what each bought

1. **`RingIndex`** (`settlement/_geom/indexes.py`): a ring's edges filed in a `PointGrid`, `inside`
   counting crossings only against the edges whose y-span can meet the ray, `edge_within(limit)`
   returning the true distance under the limit or None. Exact - the test compares 9,000 random
   points against `point_in_poly`/`edge_dist`. Used by `commons`, `marsh` (the outline and the soft
   marsh polygons), `boxed_rings`/`boxed_ring_hit` (the scatters' keep-out grids, whose crop-margin
   test was the last whole-ring scan), and `FabricIndex` (every obstacle polygon). Hinterland on seed
   4: 20.6 -> 7.0 profiled s; web on seed 25: 62.4 -> 8.9 profiled s.
2. **`_predict_k`** (`hamletgen/water.py`): a power-law step through the last two (k, acres) points
   instead of halving the bracket - the fan scales in two dimensions so acres ~ k^2 - with the
   bracket kept and the prediction clamped into it. Seed 4: 4 carves -> 2.
3. **The saturation probe** (`_fit_at_aspect(probe=True)`): when k = 1 falls short, the second carve
   is the largest fan the bracket allows; if that too is short by more than the tolerance the aspect
   cannot reach the target and the search moves on after two carves. `fit_field` re-runs the best
   aspect in full when no aspect landed the target, so the map the household ratchet judges is as
   refined as before. Seed 47: 39 carves -> 8; the stage 63 -> 12 profiled s.
4. A collapsed bracket (< 0.03 of k, under a plot row) ends an aspect.

Bookends: `144-start` 128.2 s -> `144-mid` (after 1-2) 65.6 s -> `145-mid` (after 3) **48.0 s**,
seeds 4/25/39/47 = 9.9 / 13.8 / 11.9 / 12.4 s (-62.6% total; worst seed 51.0 -> 13.8 s). The
reference roll alone (`GATE_NO_CACHE=1 make reference`, gate included, process start included):
17.6 -> 12.2 s wall; its remaining stages are the web (~1.5 s), the field (~1.5 s), hinterland
(~3 s), homesteads, the notice board, and ~2 s of gate.

## R2b - what the moved maps exposed (constitution XIV: fixed here, not filed)

The first FULL run after the solver change found four checks firing on three maps that were green
before the move. Each was diagnosed to a PLACER defect the old field geometry had happened to hide:

| map | check | cause | fix |
|---|---|---|---|
| Sawada | `roads_clear_of_marsh` | the connector grazed the toe band's corner by 4.5 px off-page: `connector_track` grew the wet band by scaling about its CENTROID, which barely moves the corners of a 2,900 px contour strip | `_inflated` now offsets along the ring's normals (`ring_offset`, feature 140) |
| Kashikawa | `wells_clear_of_trees` | the windbreak's clump keep-out for a well was vr + 0.90 x clump, but a drawn crown runs to ~1.03 x clump (14.4 on a 14 clump, 25.4 px from a well of vr 12.4) | vr + 1.05 x clump + 1 |
| Kashikawa | `lanes_bend_like_paths` | a straggler footpath kept a 7 px lattice step: `_unjog` replaces a zigzag only by its full chord, and the chord brushed a garden | a knee at the step's midpoint is tried when the chord is blocked |
| Cohort-41 | `ways_cross_water_on_a_deck` | the footpath's standing place at the door was tested with `_clear_link(q, q, ...)`, which returns True for any span under 1 px - never tested at all; it stood 1.3 px off the drain brook. Its network junction had no water test either | the standing place is judged as a POINT by the router's own index (14 px off water); a junction within 14 px of water is skipped |

After the fixes all three roll clean; cohort seeds 42 and 43, pinned failing since 2026-08-27, also
come up clean and their pins are removed (gate/hamletgen/test_driver.py).

## R3 - the floor's definition (the GM's ruling, and what it means in practice)

Three definitions were priced (the GM was told the second and third; the ruling was module level):

| definition | automatic? | what it catches | what it misses |
|---|---|---|---|
| a hand list of hamlet packages | no - "something we just remember to maintain" | - | every shared module in `settlement/` |
| **module level, derived from what the scripted rolls execute** (chosen) | yes - the roll cache's dependency records | an untested function in any module a hamlet roll touches, including a city-only branch inside it | nothing at module granularity |
| line level: every line a hamlet roll executes must be reached by a NON-rolling test | yes | untested hamlet code precisely | it is a different, much larger program; measured against a suite that includes the rolls it is a tautology |

The set is derived from a FIXED list of subjects (the reference, the gate's three polders, cohort
seeds 41-44) so it is the same on every machine; `rollcache.report_deps` reads the record or rolls
once. First derivation: **99 modules** - `check_village` (45), `settlement` (~30 of 70), `hamletgen`
(10), `waterfields` (7), `interactive` (2), `sitegen`, `_invocation`. `waterfields` and
`interactive` were not in the measured `source` list at all before this feature.

## R4 - the numbers at the end

(filled in at T22)
