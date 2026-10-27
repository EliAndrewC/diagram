# Hunk classification: 427 T07, T08, T09, T12 and 417 T54 (engine files only)

Classes: **R** = REMOVES-WORK, **M** = MOVES-WORK, **N** = NEITHER (docstring, comment, import, rename or behavior change),
**R+M** / **R+N** = a mixed hunk, split in the "why" column. Hunk numbers follow `git show <c> -- 'l7r/**'` order.
"Reverted" means the MOVES lines are undone in the matching patch.

## 73713d668 - 427 T07 (25 hunks: R 15, M 2, mixed 2, N 6)

| # | file | function | class | why |
|---|---|---|---|---|
| 1 | hamletgen/homesteads/boundary.py | FreeGround.state_grid, points_taken (new) | R | `point_taken` for the whole grid asked as numpy arrays in one call, instead of 82k scalar calls |
| 2 | hamletgen/homesteads/boundary.py | FreeGround (line sampler) | N | the state-array build moved into `state_grid` so both callers share it; same work |
| 3 | hamletgen/homesteads/capacity.py | field_distances | R | returns the shapely distance array directly; no per-point dict built or read back |
| 4 | hamletgen/homesteads/capacity.py | free_seats | R | grid, taken mask, house test and sort (`np.lexsort` instead of a key tuple per point) all on arrays |
| 5 | hamletgen/homesteads/growth.py | footprint | R (unsure) | 4n `max` calls and n sets of arithmetic become one `min`/`max` per axis over lists (a loop moved into C). Kept |
| 6 | homestead_parts/fixture_seats.py | lay_fixtures | R | `px(PRIVY_SUN_MAX_FT)` worked out once, not once per seat offered (T12 later replaced this code; the patch puts the hoist back) |
| 7 | homestead_parts/fixture_seats.py | _persimmon | R | `px(...)` of the step, dooryard and shade margin worked out once, not per seat tried |
| 8 | homestead_parts/wood_share.py | WoodShares (lane-vs-seats test) | M | `seg_dist` written inline and compared squared; `any(generator)` turned into a loop. Same projections. **Reverted** |
| 9 | homestead_parts/yards.py | mat_cells (`fits` closure removed) | R | the per-spot scalar `fits` gives way to the batched `fits_all` |
| 10 | homestead_parts/yards.py | mat_cells / fits_all | R | every spot's corners tested in one `floor_points` call (shapely-vectorized) |
| 11 | homestead_parts/yards.py | mat_cells | R | the exact lattice filtered by one batched `fits_all` call |
| 12 | homestead_parts/yards.py | _filled_lattice (signature, docstring) | N | parameter rename `fits` to `fits_all` |
| 13 | homestead_parts/yards.py | _filled_lattice | R | one batched call per gap lattice |
| 14 | homestead_parts/yards.py | floor_grid / floor_points | R | the grid test generalized to any point arrays so the batch above can use it |
| 15 | homestead_parts/yards.py | floor_points | R | takes arrays directly (part of 14) |
| 16 | homestead_parts/yards.py | floor_points (band loop) | N | the same exact-test loop over the band, indexed flat |
| 17 | homestead_parts/yards.py | _lay_by_hand (signature, docstring) | N | rename |
| 18 | homestead_parts/yards.py | _lay_by_hand | R | all four tries' floor tests for the whole lattice in one batched call |
| 19 | rolling/access.py | imports | N | `Sequence` import |
| 20 | rolling/access.py | fixtures_clear, fixture_gaps, point_clear (new) | R | the box list is built once (`fixture_gaps`) and `point_clear` is a specialized point-to-box test that never enters `seg_box_within`/`_seg_box_gap` (4 `segments_cross` + 12 `seg_dist` in the band). Kept |
| 21 | rolling/access.py | parts_clear, part_gaps | R+N | R: the boxes listed once (`part_gaps`). N: shed and byre now kept at `wall` (3 ft tread-to-wall) rather than `gap`, a rule change (0081) |
| 22 | rolling/gap_ways.py | imports | N | imports |
| 23 | rolling/gap_ways.py | way_out | M | `ok()`'s own memo lookup written inline at the call site; `best.get(k, inf)` turned into `in` plus a subscript. **Reverted** |
| 24 | rolling/gap_ways.py | trace, SegFeet (new) | R+M | R: `SegFeet` finds the nearest foot over all legs as one numpy pass (was a `seg_closest` per leg per cell). M: `u, v = (int(x) for x in pred[u][v])` written as two subscripts to drop the generator. **M part reverted** |
| 25 | rolling/gap_ways.py | _way_for.open_here | R | house, parts and fixture boxes listed once per household rather than rebuilt for every cell; `point_clear` (see 20) |

## 0a6ce7d7d - 427 T08 (27 hunks: R 12, M 8, mixed 4, N 3)

| # | file | function | class | why |
|---|---|---|---|---|
| 1 | hinterland/belt.py | past_the_lanes | R | lane samples as arrays; each column's test is one numpy mask (was `abs` per sample per column) |
| 2 | hinterland/belt.py | far_envelope | R | each sample's disc reach computed over arrays |
| 3 | hinterland/belt.py | belt_polygon.fouled | R | all vertices tested at once: `inside_many` plus one `shapely.distance` per crop ring |
| 4 | hinterland/stages.py | stage_windbreak | R | nearest house per clump as one numpy pass |
| 5 | homesteads/bamboo.py | parts_hit | R+M | R: the strip's four bounds worked out once, not per ring. M: `min`/`max` over lists turned into a hand-written Python loop. **M part reverted** |
| 6 | _geom/indexes.py | RingIndex.__init__ / slots | R | slot for the shapes cache |
| 7 | _geom/indexes.py | RingIndex.inside_many | R | polygon and buffers built and prepared once per index, not per call; crossings counted for all asked points as arrays |
| 8 | _geom/primitives.py | convex_hull | M | nested `cross()` written inline. **Reverted** (417 T65's `n` counter kept) |
| 9 | homestead_parts/bamboo_keepout.py | stand_spares_seats | M | `any(abs...)` turned into a loop with conditionals. **Reverted** |
| 10 | homestead_parts/belt_law.py | BeltReading.__init__ | M | `self.uv()` and `self.bin()` written inline over the crowns. **Reverted** |
| 11 | homestead_parts/belt_law.py | BeltReading.__init__ (ways) | M | `uv` inline. **Reverted** |
| 12 | homestead_parts/belt_law.py | _parted | R+M | R: `_near(b)` memoized per bin. M: `bin` inline. **M part reverted, memo kept** |
| 13 | homestead_parts/fixture_seats.py | lay_fixtures | N | the FixtureUnlaid message names the kind (a behavior and message fix) |
| 14 | homestead_parts/grove_blocks.py | imports | N | import |
| 15 | homestead_parts/grove_blocks.py | GroveBlocks.inside_many (new) | R | a column's points asked of the ring in one vectorized call, sharing the memo |
| 16 | homestead_parts/grove_blocks.py | Seats.too_near | M | `any(generator)` turned into a loop. **Reverted** |
| 17 | homestead_parts/grove_fill.py | close_belt_gaps | R | the 33-point column asked through `inside_many` |
| 18 | homestead_parts/grove_fill.py | ink_and_record_grove | R | `canopy_frozen`: keep-outs and persimmons read once per grove, not per clump |
| 19 | homestead_parts/groves.py | under_a_crown (new) | M | two `any(generator)` turned into loops inside a new helper. **Reverted (helper removed)** |
| 20 | homestead_parts/groves.py | GrovesMixin (`_trees`) | R | reads `self._persimmons()`, which is frozen once per grove |
| 21 | homestead_parts/groves.py | GrovesMixin (open_share lambda) | M | calls `under_a_crown` in place of the two generators. **Reverted** |
| 22 | homestead_parts/keepouts.py | imports | N | imports |
| 23 | homestead_parts/keepouts.py | _canopy_keepouts / _canopy_all | R+N | R: the structure scan done once while frozen, then a box filter. N: wells prefiltered by drawn extent, not by center (a bug fix) |
| 24 | homestead_parts/keepouts.py | _canopy_all | R | the box test moved out to the prefilter (part of 23) |
| 25 | homestead_parts/keepouts.py | _canopy_all, canopy_frozen, _persimmons | R | the freeze scope and the persimmon list read once |
| 26 | homestead_parts/keepouts.py | _crown_covers | R+M | R: `(r + pad) ** 2` worked out once, not per rect. M: `abs`/`max` turned into conditionals; `any(generator)` over circles turned into a loop. **M part reverted, `reach2` kept** |
| 27 | shrines_wells/woods.py | (crown-clear test) | M | `all(generator)` plus `max` turned into a loop with conditionals. **Reverted** |

## 7307453e2 - 427 T09 (16 hunks: R 7, M 6, mixed 1, N 2)

| # | file | function | class | why |
|---|---|---|---|---|
| 1 | water/brook_course.py | _crop_edge | M | `abs`/`max` turned into comparisons. **Reverted** |
| 2 | water/brook_rules.py | _proper_cross (removed), _dist_to_course | M | the predicate deleted (inlined into hunk 3); the clamp and `min` turned into conditionals. **Reverted** |
| 3 | water/brook_rules.py | crosses_mid_run | M | `any(_proper_cross(...))` and its nested `side()` written as loops (the joiner leg's dx, dy are now worked out once per leg, which saves very little). **Reverted** |
| 4 | waterfields/banks.py | drain_bank_clearance | M | clamp written as conditionals. **Reverted** |
| 5 | waterfields/banks.py | _nearest_segment | M | same. **Reverted** (417 T65's squared running gap kept) |
| 6 | waterfields/frame.py | imports | N | import |
| 7 | waterfields/frame.py | _f_at_u / f_at_u_of | R | the polyline is converted to the frame once per caller, not at each of about 1,170 stations |
| 8 | waterfields/partition.py | keep_rows | R | every length in one vectorized `shapely.length` call, each read once (it was read twice) |
| 9 | waterfields/ring_rules.py | _seg_dist, _near_polyline, drain_index | R+M | R: segment box screen, stop at the first hit, collectors indexed once. M: `_seg_dist`'s clamp as conditionals; `_near_polyline` as a loop instead of `any`. **M part reverted (screen and early stop kept, now `any(...)`)** |
| 10 | waterfields/ring_rules.py | collector_crossings | R | uses the per-context index; segments outside the box are skipped |
| 11 | waterfields/ring_rules.py | RingContext.drain_index | R | the index is built once per context |
| 12 | waterfields/ring_rules.py | RingContext.near_supply | M (unsure) | `LineString(...).intersects` changed to `shapely.intersects(shapely.linestrings(...))`. The C work is the same, with fewer Python wrapper calls. **Reverted** (the empty-ring guard goes too, because `LineString([])` is empty and intersects nothing) |
| 13 | waterfields/ring_rules.py | ring_violations | R | passes the context's index |
| 14 | waterfields/seams/pockets.py | imports | N | import |
| 15 | waterfields/seams/pockets.py | _outside_command | R | the collector and canal are converted to the frame once, not at every station |
| 16 | waterfields/settle.py | ring_of | R | `shapely.get_coordinates` (C) replaces iterating the CoordinateSequence, which takes a Python step per coordinate |

## 1a6a84a02 - 427 T12 (3 hunks: M 3)

| # | file | function | class | why |
|---|---|---|---|---|
| 1 | homestead_parts/fixture_seats.py | clears | M | `abs` turned into conditionals. **Reverted** |
| 2 | homestead_parts/fixture_seats.py | lay_fixtures | M | the privy's generator filter calling `within_reach_of` is folded into `_first`. **Reverted** (with T07's hoist of `reach` and `house`) |
| 3 | homestead_parts/fixture_seats.py | _first | M | `within_reach_of` and `abs` written inline (plus 26c9f32a2's default line). **Reverted** to T07's `_first` |

## 7eefc6280 - 417 T54 (6 hunks: R 2, M 1, mixed 1, N 2)

| # | file | function | class | why |
|---|---|---|---|---|
| 1 | ways/fabric.py | house_hit | R | box screen: houses whose reach disc misses the run's box are skipped before `rot_rect` and the wall `seg_dist`s |
| 2 | ways/last_resort.py | lane_breaches | N | docstring (Research line) |
| 3 | ways/law.py (now law/meet.py) | free_end | M | `box_gap` written inline as four axis comparisons in front of `box_gap` itself (box_gap is the same cheap arithmetic); `all(generator)` turned into a loop. **Reverted** |
| 4 | ways/settle/ends.py | settle_network | N | docstring (Research line) |
| 5 | ways/tree.py | rejoined | R | water legs and their boxes listed once per run; legs whose box misses are skipped before `segments_cross` |
| 6 | rolling/access.py | _seg_box_gap | R+M | R: a Liang-Barsky clip replaces in-box plus 4 `segments_cross`; each end's gap to the box is a clamp (2) instead of 8 `seg_dist` to the edges. M: the 4 corner-to-segment distances are `seg_dist` written inline. **M part reverted** (`min(sqrt(best_end2), min(seg_dist(corner...)))`) |

## Notes for the patches

- `revert-427.patch` also edits `tests/settlement/test_fixture_seats.py`. T12's test calls `_first(..., house, reach)`, so it
  now passes the privy's filter as a generator the way `lay_fixtures` does. Drop that hunk if the patch must touch only `l7r/**`.
- Removed with the reverts: T12's `Research:` line in `_first`'s docstring (the privy-reach claim). `within_reach_of` keeps
  its own claim, but the claims index (`dev/claims-index.json`) will see a changed or removed fingerprint.
- Same values: each reverted M line computes the same expression, except in three places where HEAD compares squared
  distances and the restored code uses `hypot`/`seg_dist`: wood_share 8, and `_seg_box_gap`'s corners in the T54 patch. HEAD
  went the other way from the original code in each. Those values agree to about 1e-14 (a standalone check of the corner
  part: 17% of random cases differ, by at most 2.8e-14). A verdict can flip only when a gap lies within that of its
  threshold. Clamps (`max(0, min(1, t))` against conditionals) and `abs` against sign tests differ only in the sign of zero,
  which no comparison or product here can see.
