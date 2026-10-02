# Research: homesteads at scale

Every figure here is a one-shot observation unless it names a harness. The probe is a scratch script (the session's scratchpad,
`scale.py`): it lifts `HOUSEHOLD_BAND` by assignment, plans the reference spec (`perf_snapshot.REFERENCE` without its
`households`) at the asked size, and times each of `driver.STAGES` as `perf_snapshot.measure` does.

## R1. How each stage grows with the household count (observed 2026-10-01, method: the scratch probe, base `6ce5b533e` + 302)

| households | seed 4 | seed 25 | seed 39 | seed 47 |
|---|---|---|---|---|
| 10, stage total (homesteads) | 2.10 (0.48) | 1.81 (0.42) | 1.62 (0.40) | 1.82 (0.40) |
| 20 | 4.12 (1.48) | 8.32 (5.04) | 3.37 (0.99) | 3.29 (0.85) |
| 40 | 14.74 (7.07) | 13.17 (7.74) | 15.99 (9.79) | **61.23 (55.58)** |
| 80 | `FieldRefused` | `FieldRefused` | - | - |

(Observed 2026-10-01, method: the scratch probe, as the table.) The field, web, hinterland and windbreak grow about in proportion (field 0.3 -> 1.1-2.7 s, web 0.2 -> 1.3-2.1 s). The homesteads
stage grows 17-24x for 4x the households on three seeds and 139x on seed 47.

## R2. Where the homesteads stage goes at 40 households (observed 2026-10-01)

**Seed 25, cProfile** (observed 2026-10-01, method: cProfile around `stage_homesteads` in the probe; it roughly doubled the stage, 7.7 -> 17.6 s, so shares are relative only): 3,774 `try_place` calls for 40
houses; `seat_the_rest` (the exhaustive pass) 72% of the stage; `_house_candidates` 9,080 calls, 36%; `AccessTree.targets` 30,043
calls; `seg_dist` 1.82 million calls; `heapq.nsmallest` 15,606 calls, 1.0 s.

**Seed 47, the wall-clock sampler** (observed 2026-10-01; method: feature 297's R10 method: a thread reading the main thread's stack every millisecond,
`sys.setswitchinterval(1e-4)`; 46,084 samples over the 57.3 s stage). The seat search's own counters: 1,509 placer calls, 1,315
seats offered by the exhaustive pass of which 23 were seated, 7 lattice rounds. So seed 47 makes FEWER placer calls than seed 25 and
pays ~38 ms each against ~4 ms - the cost per call grows, not only the count.

| inclusive share (observed 2026-10-01, method: the sampler above) | what |
|---|---|
| 70.7% | `try_place` (the placer) |
| 58.6% | `seat_the_rest` (the exhaustive pass) |
| 33.2% | `_house_candidates` (the corridor candidates behind each seat) |
| 28.9% | `seat_reaches_tree` |
| 17.7% | `_bundle_geom` (the four layouts) |
| **16.7%** | **`reserve_commons_byres` -> `_commons_pocket_clear`** (the shared sheds' pockets, laid before any house) |
| 16.7% | `_parts_fit` |
| 14.1% | `prime_site` -> `FreeGround.lines_edge_points` (11.4% SELF in `_samples`, the numpy sampling of every corridor line) |
| 6.5% | `AccessTree.targets` |
| 4.7% | `wood_share.corridor_bars` |

The segment distances by caller (observed 2026-10-01, method: the sampler's leaf frames with their parents): `edge_dist` inside `_commons_pocket_clear`'s
scan of every paddy outline ~9% (`seg_dist` 3.9 + `seg_closest` 3.5 + the generators); `targets`' `seg_closest` 1.4%;
`corridor_bars` ~2.8%; `surface_water_dist` from `needs_pocket` ~1.7%.

## R3. The scans behind those shares (read 2026-10-01)

- (Shares observed 2026-10-01, method: R2's sampler.) **`AccessTree.targets`** (`settlement/rolling/access.py`): for each door it lists EVERY corridor's nearest point and every point
  laid along every corridor (`_along`, one each `TARGET_STEP_PX`), then `heapq.nsmallest(TARGETS_TRIED)` by distance. It is
  remembered per door only until a corridor is added - which happens with every house seated - so the whole tree is scanned
  again for every door of every seat. The tree grows with the houses: quadratic.
- **`_commons_pocket_clear`** (`settlement/shrines_wells/byres.py`): each candidate pocket of a grid over the seat band is asked
  `point_in_poly or edge_dist < bh` against EVERY paddy outline in `field_polys`, and the surviving candidates are re-asked after
  each pocket is laid. Candidates x paddies, both growing with the households. On seed 47 it runs once per margin the seating
  tries (`_seat_households` ran three times).
- **`corridor_bars`** already reads only the seat cells the strip reaches; **`_standing_clear`** already asks the `placed_reach`
  index. Neither is a whole-map scan; they are left alone.
- **`surface_water_dist`** (`settlement/land/wet.py`) measures every stream, moat and pond rim per house; ~1.7%, not superlinear
  in the houses (the water does not grow with them). Left alone.

## R4. The seat region and the exhaustive pass (read 2026-10-01; feature 297's R2, R6 and R15)

- (Figures from 297, observed 2026-10-01, method: its R15 toggle.) `seat_the_rest` (`hamletgen/homesteads/capacity.py`) builds its seat list ONCE and asks the seat region of the whole list ONCE
  (`region.offer(seats)`) before seating any of it; while it seats, only `_near_a_house` drops a seat. So the region is current
  for the lattice rounds and stale through the exhaustive pass, which on seed 47 offered 1,315 seats and seated 23.
- `SeatRegion.sync` already paints new corridors and the wood seats as houses land. It does NOT paint the seated homesteads,
  deliberately: the placer shifts a seat off the one neighbor it overlaps, so a seat lapping one neighbor is still a seat.
- 297's R15 painted every seated homestead's box into the raster: at hamlet size (the pool and cohort seeds 1-24) placer calls fell
  4,712 -> 4,054 but the stage rose 51.31 -> 56.01 s summed (9% slower), because the raster was repainted and its table rebuilt after
  every house. Withdrawn at hamlet size; never measured at 40 households.
- 297's R2/R6: of 734 offers on Inashiro, 348 corridor searches found no candidate at all - a property of the house's box, its yard,
  the tree and the standing ground, asked after all four layouts were built. The line-of-sight reach region (a cell with a clear
  straight strip to a tree point) was priced in 297 as the lever that would refuse those seats before the layouts, and not built
  ("costly to rasterize").

## R5. The field at 80 households (observed 2026-10-01)

`FieldRefused: no fan at any of 5 aspects is legal ... and lands 104.0 acres within 15%` on seeds 4 and 25. A single fan cannot land
the acreage; a village needs several fields or several fans. Out of scope (spec Edge Cases); the bookend stops at 40.
