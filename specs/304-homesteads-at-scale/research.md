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

**Seed 25's `seg_dist` calls by caller** (observed 2026-10-01, method: the plan review's cProfile probe around `stage_homesteads`
at 40 households, one run): `corridor_bars` ~579,000; `surface_water_dist` 448,539; `seg_box_within` / `_seg_box_gap` (in
`_standing_clear` and `covers_box`) ~337,000; `law._min_dist` via `fronting_ends` 237,004; `chain_distance` 73,923. None is a
whole-map clearance scan without an index, so R3's reading holds on the request's own seed. `law.fronting_ends` compares every
lane end with every other way (0.70 s of an 18.8 s profiled stage) - a lane rule, outside FR-005, noted for the GM.

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

## R6. The cohort at the base (observed 2026-10-02, method: `make cohort N=24` in the detached worktree `/tmp/base304` at 505bcf0c9)

28/30 pass the whole gate (forms rolled: dispersed 9, linear 10, nucleated 11). The two failures are pre-existing, of the class
302's research R3 recorded (23/30 at its base, the failing seeds moving with the geometry):

- Audit-11 (10 households, linear): `WebRefused` - the web's last resort cannot mend lane 1 (skeleton) without dropping a tree
  lane; the web still breaks `bends`, `off_ford`.
- Audit-905 (20 households, dispersed): `UndeckableCrossing` - no deck seats where a way crosses water at (3036, 2756).

Neither is in the homesteads stage. Constitution XIV and the GM's ruling of 2026-10-01 ("We should definitely fix the
pre-existing failure"): fixed in this work (tasks T02, T03), each diagnosed here first.

## R7. The indexed scans against their oracles on real rolls (observed 2026-10-02, method: a scratch spy wrapping `ring_targets` and `beside_a_paddy` through `stage_homesteads` at 40 households, comparing every 97th answer with `scan_targets` / the scan of every outline)

Seed 47 (`detached_commons`, so the pockets are laid): 111,881 ring queries, 1,153 compared, 0 differ; 95,531 pocket tests, 984
compared, 0 differ. Seed 25 (`courtyard`, no pockets): 15,606 more ring queries, 161 compared, 0 differ. With the equivalence
tests (`tests/settlement/test_access_ring_304.py`: 74 cases, 50 of them red when either query's radius is cut to a quarter) this
is plan D8a and D8b. The timings of these spy runs are not readings: two cohorts were running beside them.

## R8. Audit-905's refusal (observed 2026-10-02, method: a background agent in its own worktree; `make hamlet ARGS="--name Audit-905 --seed 905 --households 20 --form dispersed --farm-water channel --no-render"`, then `make cohort N=24`)

(Observed 2026-10-02, method: as the heading.) The way across the water was the FIELD SPUR (`hamletgen/ways/track.py`, `stage_track`). Its tip was set on the bund
(`tip_onto_the_bund`), then `_thread_the_fabric` moved its free bow vertex 20 ft into a paddy plot and `spur_cut_at_the_fold`
kept the arm out to it - across the comb's main ditch (2.8 ft) at the field's head, onto a bund strip about 2.4 ft wide. Both
deck forms in `crossing_deck` clear the water but fail "lands dry" (the carried deck's corners in two plots, the plank's in
one). A dispersed hamlet returns early from `stage_web`, so `settle_the_web`, which cuts a crossing no deck seats, never ran,
and `bridges()` raised `UndeckableCrossing`. The fix sets the DRAWN spur's tip on the bund again after the fold cut, and records
the spur dropped where the kept arm is rice end to end; no rule changed. Seed 905 passes; the cohort 29/30 (Audit-11 alone).
Two regression tests in `tests/hamletgen/ways/test_track.py`, red with the fix off.

## R9. Audit-11's refusal (observed 2026-10-02, method: a background agent in its own worktree; `make cohort N=1 SEED=11`, then `make cohort N=24`)

(Observed 2026-10-02, method: as the heading.) The failing lane was the row village's first STREET, a tree lane no settle may cut. It is drawn from its first farm to its last
plus half a frame (`ways/street.py`, `street_span`), along a straight line fitted to the hard ground's edge (`rows.street_line`).
On seed 11 that line runs 10.8 degrees off the brook's first reach, the last farm stood 12 ft before the crossing, and the half
frame took the street over the brook 45.6 ft from the nearest ford (`off_ford`; the law allows `FORD_HALF`, 30 ft). The settle's
`square_every_crossing` then squared the shallow crossing in place into two turns of about 80 degrees 21 ft apart (`bends`),
and the last resort drops ordinary lanes only, so the web was refused. The fix (`brook_bounds`): the run past an end farm stops
`FORD_LANDING_FT` (22 ft, the figure the ways already keep between a way's turn and the brook - a map drawing convention) short
of a crossing beyond that farm, never short of the farm itself; a crossing between farms is left to the street. The road reads
the same span and crosses at a ford. Seed 11 passes; the cohort 29/30 (Audit-905 alone, before its own fix). One regression
test in `tests/hamletgen/ways/test_street.py`. Not yet judged by eye: the road's new jog at the ford (two turns 59 ft apart).

## R10. What the levers bought at 40 households, and the forms withdrawn (observed 2026-10-02, method: the scratch probe `p3.py`, `stage_homesteads` timed through itself, best of three unless said; the machine otherwise idle)

**P3's forms (plan D9), on P2 as first built, summed over the four seeds at 40 households** (homesteads seconds; placer calls):

| form | seed 4 | seed 25 | seed 39 | seed 47 | sum |
|---|---|---|---|---|---|
| P2 alone | 6.41 (916) | 7.79 (946) | 9.81 (907) | 53.01 (1,509) | **77.0** |
| A, the region re-asked after each house | 27.92 (2,035) | 18.23 (919) | 14.64 (919) | 52.87 (1,401) | 113.7 |
| A', A with each seated homestead's boxes painted | 42.19 (1,277) | 86.73 (1,026) | 14.43 (894) | 55.25 (420) | 198.6 |
| B, no seat without a clear straight corridor from the smallest layout | 5.69 (383) | 17.90 (552) | 6.86 (403) | 52.23 (769) | 82.7 |

(Observed 2026-10-02, method: as the table.) Every form seated all 40 households. At 15 and 20 households (same method) A was 0-7% faster than P2 alone, A' erratic (seed 4
at 15: 3.70 s against 1.01), B about even at 15 and 5-16% faster at 20 on three seeds. **Plan D10: none is faster at 40, so all
three are withdrawn** (FR-006, FR-007). Why, in their own numbers: re-asking the region rebuilds its reachable raster (a flood)
per seated house, and the pass then visits a different, worse order of seats (A on seed 4: 2,035 placer calls against 916);
painting the homesteads refuses seats the placer's one computed move would have rescued (297's R15 found the same at hamlet
size); B halves the placer calls but pays a layout and a corridor search for every seat it offers, the costliest question asked
first (297's R10 lesson, again), and on seed 47 the calls it saves are cheap ones.

**P2's two indexes, measured apart** (observed 2026-10-02, method: the probe, one run each, two rounds alternated, 40 households): the access tree's targets from the
ring (D5) against the scan, with the pocket index in both - seed 4 6.25/6.31 against 5.93/6.30, seed 25 7.88/7.68 against
7.54/7.65, seed 39 10.00/9.84 against 9.56/9.30, seed 47 51.31/50.82 against 49.89/48.84. **The ring is 1-4% slower on every
seed: D5 is withdrawn** and the scan restored (`access.py` records why at `targets`). The sampler showed it: the exhaustive
pass's doors stand far from the tree, the ring doubled across thousands of empty cells (`PointGrid.near` 11.7% SELF of seed 47's
stage), and a fallback to the scan once the ring outgrew the tree's own point count still left it behind. **The pocket index (D6)
stays**: `reserve_commons_byres` fell from 16.7% of seed 47's stage to 8.8-9.0% (the sampler, observed 2026-10-02), and seed 47's
stage from 55.6 s (R1) to 48.8-49.9 s; it does nothing on the three seeds whose byres are not `detached_commons`.

**So the goals are missed** (spec SC-002, SC-003; observed 2026-10-02, method: the probe and the R10 sampler): at 40 households the homesteads stage is ~6-10 s on three seeds and ~49 s on
seed 47, against 0.40-0.48 s at 10 households - ~0.15-1.2 s a household against ~0.04, where SC-002 asked at most twice. What
remains, on seed 47 (the sampler on the current engine): the exhaustive pass 64.5% of the stage, the corridor search behind each
seat (`seat_reaches_tree` -> `_house_candidates`) 33-38%, the four layouts with their fixtures 18.5%, the site raster's sampling
of every candidate corridor (`prime_site`) 15%. Those are the seat search's own questions asked of ~1,500 seats, 23 of which the
exhaustive pass seats - not a scan an index replaces. Per the spec this is recorded and raised with the GM, not pursued with
levers beyond the three accepted.
