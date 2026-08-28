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

## R3b - the floor's first measurement, and what it is made of (T12)

`floor-first.txt` is the table. 932 uncovered lines on the 99 hamlet-path modules, mapped to the
functions holding them. Two kinds, and the spec treats them differently (FR-002):

**Hamlet code no roll or test reached (~200 lines)** - covered in this feature by tests where a unit
can reach the branch (the geometry predicates, the solver's probe and re-run, the registry cache, the
sibling guard, the SVG merger, the waive printout), and otherwise by the cohort the FULL run rolls
(seed-dependent placer branches: `_thread_the_fabric`, `_smooth_web`, `_strip_blocked`, the well and
byre fits, the carve's sector edge cases). The residue after the next FULL run is listed at T12.

**Code only another tier reaches, inside a module the hamlet path executes (~700 lines)** - the case
the spec sends to the GM, not to tests and not to deletion. By function:

| module | lines | what it is |
|---|---|---|
| `check_village/common_02_overlap_policy.py` | 223 | `check_fire_features` (143), `_theater_one_stage` (75), `_ward_interior` (48), `check_ring_road_clear`, `check_theater_stage` - town/city fire towers, theaters, wards, the ring road |
| `check_village/segments_11a_taxfree_terraces_and_dikeponds.py` | 56 | `dikepond_is_ponds_in_a_block` (94 lines of it) - the mulberry dike-pond form, which no scripted map draws yet |
| `check_village/segments_01*, 02*, 03a/b, 10*` (city, capital, wards) | ~150 | the city/capital branches of segments the hamlet gate still enters and leaves at their scale guard |
| `check_village/common_03_capacity.py` | 32 | `_fronts_route`, `city_capacity` |
| `waterfields/polder.py` | 100 | `build_terraces` (85), `build_ribbon` (66) - the contour-terrace and ribbon-valley field engines; `FIELD_ARCHETYPES` deliberately holds two of the five (`consts.py`), so hamletgen never calls them; the two pool maps that did are frozen legacy |
| `settlement/water_ways.py` | 44 | `market`, `ancestral_hall`, `water_mouth`, `alley` - town features |
| `settlement/structures/fixtures.py` | 32 | `drum_tower` (30) - a city fixture; the kosatsuba branches are hamlet's and get tests |
| `settlement/city/bridges.py` | 18 | `bridges`, `channel_footbridges` - the city's spans; the hamlet path enters the module for the footbridge helper |
| `settlement/finish.py` | 22 | `finish`'s city crop / legend branch (lines 419-468) |
| `settlement/core.py` | 8 | `crop_city` |
| `settlement/_knobs.py` | 7 | `machi_mouths`, `moat_swept_tap` |
| `settlement/shrines_wells/woods.py` | 14 | `forest` (13) - the town-scale canvas-filling wood |

Three ways to make the floor honest about these, for the GM to choose between (none taken here):

1. **Write the tests** - contradicts the GM's own reason for the exemption ("they might be deleted entirely"), ~700 lines of city/town test-writing.
2. **Move the other-tier code out of the shared modules** into modules the hamlet path never executes (a `city/` segment file, a `polder_hill.py`, `water_ways_town.py`) - mechanical, no behavior change, and it makes the module-level floor mean exactly what the GM said; the cost is a file move per function and the frozen-registry re-derivation for the check segments.
3. **A recorded, per-function exemption list** read by the floor - the "something we just remember to maintain" the GM asked to avoid; listed only for completeness.

The session's recommendation is 2: it is the module-level ruling applied to the code rather than to
the floor, and it leaves nothing for a future session to remember.

## R4 - the numbers at the end

**The rolls** (`make perf`, seeds 4/25/39/47, this container): `144-start` 126.7 s -> `145-end`
**49.2 s** (-61.2%; per seed -30.7 / -72.9 / -50.5 / -65.2%; worst seed 51.0 -> 13.8 s; band 0,
nothing owed). The reference alone rolls in ~12 s wall including its gate - the session's own 8 s
target was NOT met (reported, per SC-001): what remains is the hinterland's scatter volume (~3 s),
the field's two carves (~1.5 s), the web (~1.5 s), homesteads, the notice board, and ~2 s of gate.

**The unit tests** (`make durations`, quick set, 2,116 tests): pytest **10.9 s** wall on 8 workers.
The settlement-geometry tests that led the profile on 2026-08-28 morning are gone from its top:
the slowest ten are now tooling fixtures (2.96 s, `make` in a fixture) and comb builds (~2 s); the
fabric-index brute-force comparison is 0.79 s. Nothing over the quick cutoff was left deliberately.

**The floor**: 99 modules derived; the FULL run judges them (and now rolls eight cohort seeds in
process so the seed-dependent placer branches count). The residue and the other-tier decision are
in R3b and at T12.
