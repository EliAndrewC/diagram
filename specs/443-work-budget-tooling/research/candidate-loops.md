# The candidate loops of every stage - the walk (feature 443 T01, plan D2)

Load this file when: you add a `candidate@<function>` counter, or rebuild a phase and need the loops it owns.

## Status

**The walk's first pass, 2026-10-28: a static call-graph scan, unfiltered.** It is a candidate SET, not the verified list. The
filtered list - each loop with one phrase saying what it tries, and the loops excluded with why (loops that measure or sum
placed things) - is written per stage family by the task that instruments it (T09 water and fields, T10 the homesteads
family, T11 the ways, T12 ground cover, frame, notice and labels), each hand-reading what the scan could not follow.

**Known gaps of the scan, owed a hand-read** (the advisor's and the scan's own caveats, 2026-10-28):

- the `getattr(s, "_seat_region" | "_free_ground" | "_access" | "_site_corridors")` dispatch in `hamletgen/homesteads/region.py`,
  `capacity.py`, `growth.py` and `hamletgen/ways/gateway.py` - the homestead seat funnel trial 439 measured;
- `hamletgen/homesteads/stages.py`, only partly detected;
- **misses of the walk found by the cross-check**: `make perf-fanout SEED=25 HOT=20000` (2026-10-28,
  `dev/perf-log/20261028T045040Z-fanout-443-loops.txt`) names anchors the scan does not list - `settlement/rolling/gap_ways.py:265
  way_out`, `:309 trace`, `hamletgen/ways/law/meet.py:272 near_misses`, `:350 web_lines` - each a miss of the walk, to be read
  and listed by its family's task.

## The search

- The stage list: `grep -n "STAGES" -A40 l7r/diagram/hamletgen/driver.py` (23 stages).
- The scan: `candidate_scan.py.txt` beside this file (run with `python3 -I` from `l7r/diagram/`; a copy of the scratch script,
  kept as text so the gate does not lint it). It builds a call graph with `ast` over `hamletgen`, `settlement`, `waterfields`,
  `sitegen`, `overlap` and `labels` (not `tools/`), follows each stage's reachable functions, and lists every loop,
  comprehension or `min`/`max`/`sorted`/`next` whose subtree calls a test name (`admits`, `conflicts`, `forbidding`, `*fit*`,
  `fouled`, `*clear*`, `blocked`, `taken`, `open_seat`, `is_free`, `within_reach`, `hit`, `inside`, `near`, `refused`, `offer`,
  and every predicate defined in `settlement/_geom/` and `overlap/`).
- The cross-check: the `make perf-fanout` anchors above.

## The scan's output (verbatim, 2026-10-28)

## Method and caveats
- **Stage list:** `driver.py:96` `STAGES`, 23 entries. `grep -n "STAGES" -A40 hamletgen/driver.py`.
- **Stage definitions:** `grep -rn "def stage_\(water_frame\|field\|seat\|waterward\|track\|web\|washing\)\b"`, plus the `driver.py` imports. They live in:
  - `water/skeleton.py:27`, `water/comb.py:21`, `water/polder.py:611`
  - `ways/track.py:60` (seat) and `:204` (track), `ways/web/stage.py:38`
  - `washing.py:222`
- **Call graph:** built with `python3 -I` and `ast` over `hamletgen`, `settlement`, `waterfields`, `sitegen`, `overlap` and `labels`, excluding `tools/`. An edge is a resolved name, a module attribute, `self.method`, or a method name.
- **Reachable-set sizes:** the strict graph (calls resolved through imports, `self`, or a unique method name) reaches 4 to 515 functions per stage. The looser name-matched graph over-reaches to 1784 functions in total.
- **Candidate test:**
  - A loop, comprehension, generator, or `min`/`max`/`sorted`/`next` counts if its subtree calls a test name.
  - Test names are `admits`, `conflicts`, `forbidding`, `*fit*`, `fouled`, `*clear*`, `blocked`, `taken`, `open_seat`, `is_free`, `within_reach`, `hit`, `inside`, `near`, `refused`, `offer`, plus every geometry predicate defined in `_geom/` and `overlap/`.
  - `*` after a loop kind means it only calls a helper that itself tests.
- **Precision:** the scan cannot tell a trial from a measurement. Many `seg_dist`-only entries in `ways/` measure or sum placed things (joints, knots, tree faults, tidy) and are probably not candidates. I did not read each one.

Searches run:
- `grep -n "^def \|^class \|^    def [a-z]" settlement/_geom/*.py overlap/registry.py` to list the geometry and registry predicates.
- `grep -rn "getattr(s\b\|getattr(self\|importlib\|__import__" <the six trees>` to find calls the scan could not follow.
- `grep -n "for \|while \|min(\|max(\|sorted(\|next(" hamletgen/frame.py`.

Stage codes: A water_frame, B field, C sink, D seat, E waterward, F homesteads, G track, H appurtenances, I pond_stock, J burial, K web, L lane_wells, M pond_bank, N hinterland, O woodland, P windbreak, Q bamboo, R crossings, S sties, T washing, U frame, V notice, W labels. Uppercase means strictly reached. Lowercase means reached only by method-name matching.

Loop kinds: F `for`, W `while`, lc/sc/dc list, set, dict comprehension, ge generator, plus `min`/`max`/`sorted`/`next`.

## Per-stage results (stage-owned loops)
- **A water_frame:** none. It only calls `Settlement.pin_knob` and `meta`.
- **J burial:** none. It records a knob and `household_graves`, and the graves are laid by the homestead fixtures (F/H).
- **D seat** (`ways/track.py:60`), stage-owned:
  - `cluster.py:58 nearest_within` - nearest cluster seat - `seg_dist`/`near`.
  - `cluster.py:80,82,86 back_fouled` - back-of-site trial - `point_in_poly`.
  - `cluster.py:256-338 seat_cluster` - where the cluster seats, sampled over positions - `back_fouled`, `point_in_poly`, `nearest_within`.
  - Also reaches `ways/dry_exit.py:87-110 _blocked_cells`, `185,187 _pull` and `199-200 clear_of_bands` (D/F/G).
- **B field:**
  - `water/comb.py:104,106 stage_field` - `point_in_poly`.
  - `water/fit.py:87,117 fit_field` - field fit at an aspect - `_fit_at_aspect`.
  - `water/fit.py:132 _finish_first_admissible` - F/ge/sorted - `_admissible`/`fan_admissible`.
  - `water/brook.py:363,366 bend_at`, `453-456 clear_of_field`, `471 settle_course`, `521`, `557-575 feed_brook` (brook course trials, tested with `crosses_mid_run`/`brook_violations`), `637,642 around_the_field` (`clear`), `726 draw_intake` (W, `admits`).
  - `water/brook_course.py:256,260 join_vertices`, `water/brook_rules.py:160,259,280`.
  - `water/polder.py:77 walk_pond_uphill` (`reservoir_clear_of_crop`), `107-113 dike_gaps_at_channels`, `335,337 stage_polder`, `407 fit_polder`, `476 _polder_candidate`.
  - Engine, mostly strict B:
    - `settlement/fields/comb.py` - `744,745 _comb_record_field` (`within_reach`), `400,443` (`refused`), `854-939 _comb_source_channel`.
    - `settlement/fields/features.py:335,338,361 _paddy_features`, `445-449 _pond_fit`.
    - `settlement/fields/paddy.py:260 resting_plots` (`admits`), `281`.
    - `settlement/fields/grain.py:120 top_up` (`refused`).
    - `settlement/fields/landuse.py:475-483`.
    - `settlement/land/dikes.py:148-171`, `263 perimeter_dike`.
    - `settlement/_geom/primitives.py:303-331 keepout_ring`.
    - `sitegen/geom.py:104,107 crosses_poly`.
- **C sink:**
  - `sink.py:166 pond_clear_of_crop`.
  - `sink.py:188-200 pond_setback`.
  - `sink.py:270 route_refusals` (`crosses_poly`).
  - `sink.py:376 _through_the_crop` (`point_in_poly`).
  - `sink.py:433,435 brook_join*`.
  - `sink.py:547 pond_seat` (`crosses_mid_run`).
  - `sink.py:691,716 lay_sink`.
  - Shares `brook_course.py:256` and `brook_rules.py:160` with B, and `land/dikes.py:148,171`.
- **E waterward** (`water/polder.py:611`):
  - `pondstock.py:131-134 reserve_sty_seat` - pond-bank sty seat - `pond_fixture_fits`.
  - Reaches `settlement/_geom/indexes.py` `_parity_region` and `KeepoutGrid._trees_for`.
  - Reaches `land/wet.py:325 bank_rings` and the `overlap/` registry.
- **F homesteads** (largest; mixes strict and weak reach):
  - `homesteads/region.py:171 SeatRegion.offer` - site offered - `box_clear_many`.
  - `homesteads/capacity.py:130 seat_the_rest` (`offer`).
  - `homesteads/growth.py:395 grow_the_margin` (`offer`).
  - `homesteads/stages.py:721,722 _seat_households_as` (`_ground_push`), `857,922 _seat_rank_rounds` (`offer`).
  - `homesteads/boundary.py:212-237 SiteCorridors._in_outline/hit_points/hit_center`, `486 FreeGround.rect_refused` (`point_taken`).
  - `homesteads/rows.py:493 clear_frames` (`door_clear`), `538 best_row_line`, `623,636 seat_rows` (`holding_clear`).
  - `homesteads/seat_geometry.py:31 water_push`.
  - `homesteads/well_seats.py:109`.
  - `homesteads/wells.py` - `478,495,542,591 seat_wells`, `787,799 on_a_verge`.
  - `clearance.py:217 FabricIndex.fouled`, `236 fouled_brute.near`.
  - `ways/tree.py` (the bundle's access tree) - `290,315 admits`, `880 others_clear`, `892 own_clear`.
  - `settlement/rolling/place.py` - `110 _slide`, `167 _place_bundle_dispersed`, `248-258 _place_bundle_nucleated`, `87-94 _bundle_refused`, `67 _seat_refused`, `333 _house_box_refused`. Test is `_bundle_fits` or `_parts_fit` / `_envelope_blocked` / `rect_refused`.
  - `settlement/rolling/fit.py` - `_rect_hits` (159-169), `_rect_on_water` (230-239), `_parts_fit` (398-424), `_bundle_common_fits` (760), `_bundle_side_fits` (826,828), `_house_too_near_a_neighbor` (557, `eave_gap`), `_envelope_blocked`, `_site_blocks_rect`, `_field_blocks_*`, plus the sun-conflict loops (`houses_meeting`).
  - `settlement/rolling/farmsteads.py:174,177,212-240 _garden_beds_clear/_relax_gardens_south`.
  - `settlement/rolling/access.py` - `709-717 _house_candidates` (`clear`), `569 admitted` (`fixtures_clear`/`parts_clear`), `296,355`.
  - `settlement/rolling/gap_ways.py` - `532 _way_for`, `544`, `576 _first_admitted`.
  - `settlement/rolling/route.py:87-102 search` (`is_open`), `127-130 taut` (`leg_ok`).
  - `settlement/rolling/lot.py:282 bundle_admitted` (`admits`).
  - `settlement/rolling/passage.py:176,219`.
  - `settlement/homestead_parts/fixture_seats.py` - `411,430 lay_fixtures` (`clears`, `within_reach_of`), `836,837 _persimmon`.
  - `settlement/homestead_parts/yards.py` - `149,160 mat_cells`, `184,192 _filled_lattice` (`fits_all`), `407-451`.
  - `settlement/houses.py:141,144 _in_blocked`, `159 _near_corridor`, `235-261 _on_a_tread`/`_tread_skipped`, `326,337 _clear_of_placed`.
  - `homesteads/fixtures.py:427-433 _draw_pending` (`_flexible_clear`, `admits`).
  - `settlement/shrines_wells/wellground.py:186-195`.
  - `settlement/hard_ground.py:88 _hard_clear`.
- **G track** (`ways/track.py:204`):
  - `ways/track.py:387,401 connector_track` (`fabric_hits_boxed`, `violations`), `569 on_course`.
  - `ways/route.py:127,133 lattice_search` (`is_free`), `285,292 _route` (`_clear_link`), `330 _unjog`, `408,410 _ease_corner` (`_clear_touch`).
  - `ways/clearance.py:72 link_survives`, `231-257 route_around`, `328 clear_runs`, `372,377 clip_to_clear` (all `fouled`).
  - `ways/thread.py:53-221`, `ways/fabric.py:360-514` (`house_hit`, `_crosses_fabric`).
  - `ways/checks.py:276-293 PathChecker.violations`, `ways/gateway.py:54,71`, `ways/dry_exit.py`.
  - `sitegen/geom.py:71,72 pull_clear`.
  - `overlap/reserved.py:200` (`release_seats_along`) and `overlap/registry.py:322 forbidding`.
- **H appurtenances:**
  - `homesteads/retirement.py:179,182` - `_byre_clear_of_all_but`, `admits`.
  - `settlement/shrines_wells/byres.py` - `278,279 _courtyard_byre_seat`, `321 _yard_shed_seat`, `541-607 draft_byres` (`_fits`).
  - `homesteads/farm_water.py` - `89-90`, `111`, `120-122`, `206-222 farm_channel`, `239`, `249` (`crosses_other_water`, `segments_cross`).
  - `homesteads/fixtures.py:427-433`, `wells.py:255-294 shared_row_wells` (`own_well_clear`), `homesteads/boundary.py` (`SiteCorridors`).
  - `settlement/homestead_parts/fixture_seats.py:411-445`, `836`.
  - `settlement/rolling/` (`access.py`, `fit.py`) as in F.
  - Also strict-reached: `ways/clearance.py` and `ways/route.py`.
- **I pond_stock:**
  - `pondstock.py:216,231,232 stage_pond_stock` - `pond_fixture_fits`.
  - `pondstock.py:257 seat_faults` - `pond_fixture_fits`.
- **K web** (largest ways set; probably includes measurement loops, see caveat):
  - `ways/web/skeleton.py:157,271 _lay_skeleton` (`admitted_runs`, `clip_to_clear`).
  - `ways/web/stage.py:215`, `341-362 _reachable_runs`.
  - `ways/lay.py:66,68`, `102 _held` (`admits_lane`).
  - `ways/serve.py` - `244-297 _lay_web_lane`, `394-397 door_off_fixtures`, `409-410 pulled` (`clear`), `426 to_first_arrival`, `694-721 door_path` (`clear`, `segments_cross`).
  - `ways/street.py:223,227 thread`, `251 join_to`, `311`.
  - `ways/bund.py` - `90,94`, `178-189 RunOnBlocks.clear`, `241,248 run_lanes_on_to_the_bund`, `317-349 a_way_onto_the_bund` (`admits_lane`, `clear`).
  - `ways/knots.py:731,734 settle_knots` (`clear`).
  - `ways/tree.py:660,661 cut_alongside` (`admit`), `694 settle_defer` (`admits`).
  - `ways/last_resort.py:82-130` (`conflicts`, `fouled_segment`).
  - `ways/tails.py`, `ways/tidy.py`, `ways/joints.py`, `ways/geom.py`, `ways/corridors.py:139-156`, `391 field_router` (`forbidding`).
  - `settlement/water_ways/lanes.py:110 admitted_runs` (`admits_lane`), `275-336 trim_lane_stubs`.
  - `settlement/water_ways/_helpers.py:111`.
  - `settlement/land/wet.py:522-531 trim_off_marsh`.
  - `cluster.py:460,461 _arm_hit`, `476 _arm_crossing_accidental`.
- **L lane_wells:**
  - `homesteads/wells.py` - `478,495,542,591 seat_wells`, `787,799 on_a_verge`, `847 dry_households`, `870,878 reach_wells`.
  - `homesteads/well_seats.py:109 SeatSweep.walls`.
  - `settlement/shrines_wells/wellground.py:186-195 _well_ground_clear`.
  - `settlement/land/wet.py:685-687 surface_water_dist`.
  - Also `homesteads/boundary.py:212-237`.
- **M pond_bank:**
  - `pondbank.py:101,103,105 seat_free` - `point_in_poly`/`seg_dist`.
  - `pondbank.py:152 stage_pond_bank` - `seat_free`.
- **N hinterland:**
  - `hinterland/bamboo.py:131 nearest_fitting`, `287-310 bamboo_seats` (`_fits`, `_blocked`).
  - `hinterland/belt.py:392,401 belt_polygon` (`fouled`, `inside_many`).
  - `hinterland/paddy_grass.py:78 seat_paddy_grass` (`clear_of_plot`, `open_seat`).
  - `hinterland/parcels/bounds.py:63-133`, `parcels/patches.py:134 fit_square_parcel`, `482-485`, `577-739 open_ground_patches` (`_ok`).
  - `homesteads/bamboo.py:133,150,407,420`, `572-613 _strip_blocked`.
  - `settlement/shrines_wells/seats.py:74,76 open_seat` (`_fits`).
  - `settlement/shrines_wells/woods.py:84,86`, `152`, `179-229`.
  - `settlement/homestead_parts/groves.py:176,185 belt_walk`, `377-404 _belt_ranks`.
  - `settlement/homestead_parts/grove_fill.py:337-438`.
  - `settlement/homestead_parts/stands.py:353-421 village_grove`.
  - `settlement/homestead_parts/grove_blocks.py:102`, `242`, `277,284`.
  - `settlement/land/cover.py:367-373 woodland_room`, `492-565 commons`, `696-731 _stock_woodland`.
  - `settlement/homestead_parts/belt_law.py:387-415` and `groves.py:651,682`.
  - `hinterland/frame.py:302,304 clear_pocket_spot`, `387,388 title_pocket` (`_box_clear`, `pocket_clear_of_features`).
- **O woodland:**
  - `settlement/land/cover.py:367-373 woodland_room`, `696 _stock_woodland`.
  - `settlement/homestead_parts/belt_law.py`.
- **P windbreak:**
  - `hinterland/belt.py` as in N, and `hinterland/frame.py:302-388`.
  - `settlement/homestead_parts/groves.py`, `grove_fill.py`, `grove_blocks.py:242,277`.
- **Q bamboo:**
  - `hinterland/stages.py:193 stage_bamboo` - `bamboo_stand*`.
  - `settlement/homestead_parts/stands.py:179,181 bamboo_stand` - `point_in_poly`.
  - `settlement/_geom/indexes.py:878-884 BambooObstacles.blocked`.
  - `hinterland/bamboo.py:287` and `homesteads/bamboo.py:572-613`.
- **R crossings:**
  - `settlement/city/bridges.py` - `124-133 seat_deck` (`_deck_corners_clear`), `306 deck_admitted` (`conflicts`), `433 bridges`, `564-656 channel_footbridges` (`admits`, `_deck_clears_its_water`), `792-796 _plank_reaches_useful_ground`, `828-832`.
- **S sties:**
  - `homesteads/sties.py:110 sty_seat` (W, `admits`), `147 stage_sties`.
  - `settlement/homestead_parts/fixture_seats.py:470 against_a_part` (`clears`).
- **T washing:**
  - `washing.py:98 nearest_on`.
  - `washing.py:138-151 shared_places` (`admits`), `187,193 each_house_places` (`admits`).
- **U frame:**
  - `hinterland/frame.py:302,304,387,388`.
  - `settlement/title.py:112 title`, `183,191 _title_band`, `350,352 _blank_label_spot` (all `_box_clear`).
  - `settlement/_knobs.py:764,765 crop_boxes`.
  - `hamletgen/frame.py` has none: its loops are min/max over strip extents, not trials.
- **V notice:**
  - `settlement/structures/fixtures/siting.py:312-326 _route_seats` (`_clear_of_placed`, `_fits`, `admits`, `fixture_clear_of_water`), `275,279 _board_seats`, `87 under_canopy`.
  - `structures/fixtures/board_seat.py:90-93 WayFacing._near`.
  - `structures/fixtures/_helpers.py:79-235` (`dwellings_joining`, `outermost_join`, `kosatsuba_handover`, ...).
  - `settlement/title.py` and `hinterland/frame.py` as in U.
  - `labels/` as in W.
- **W labels:**
  - `labels/placer.py:244,268 _area_cands`/`_extended_cands` (`inside`, sorted).
  - `labels/placer.py:473 place` (`blocked`).
  - `labels/placer.py:540 _strict_seat`, `591 _score`, `615-623 nudge`.
  - `labels/obstacles.py:176-205 score`, `226 nearer_than`, `257-282 blocked`.
  - `labels/geom.py:106-118`, `132`, `labels/layout.py:41`.
  - `settlement/finish.py:338,345 _caption_lines` (`rects_overlap`).

## Shared registry and index loops (reached by most stages)
- `overlap/registry.py:283-295 Standing.conflicts` - `pair_forbidden`; `:322 forbidding`; `:430 forbidden_segment`. `admits` itself has no loop in its own body.
- `overlap/reserved.py:146-167 Reservations.conflicts`, `:210-213 box_covers`.
- `settlement/_geom/indexes.py` - `518 RingIndex.edge_within`, `587 KeepoutGrid.hit`, `832-843 BoxObstacles.clear`, `318 CrownIndex.clear`, `420 _parity_region`.
- `settlement/_geom/water_index.py:50-51,79-81`.
- `settlement/_geom/primitives.py` - `272`, `303-331`, `487-489`.
- `sitegen/geom.py:71,72,104,107`.
- `waterfields/ring_rules.py:322-330,530` and `waterfields/seams/close.py:222,229` (`ring_violations`), reached only through name matching (b,f,h,l,r,V,W).

## Modules not fully walked
- **All stages:** calls on `s` that I could not resolve to one method (`add`, `get`, `at`, `find`, ...) were excluded. `getattr(s, "_access" | "_free_ground" | "_seat_region" | "_site_corridors")` in `homesteads/region.py`, `capacity.py`, `growth.py` and `ways/gateway.py` was not followed. `pondstock.py:136,234` use `getattr(s, "dikepond_inset")`.
- **A:** nothing beyond `Settlement.pin_knob` and `meta`.
- **B/C:** `water/brook*.py` and `water/polder.py` bodies are listed from the scan, not read.
- **D:** `ways/track.py:60 stage_seat` itself, and `cluster.py` helpers beyond those listed.
- **E:** `water/polder.py:611 stage_waterward` had no tested loop in its own body. Its delegates are under `settlement/land/`.
- **F/H:** `homesteads/stages.py` has 999 lines. Only the `offer`, `_ground_push` and `_seat_rank_rounds` loops were detected, and `ways/tree.py` was only partly scanned. `settlement/rolling/*` is reached by a mix of strict and name-matched edges.
- **K:** `ways/` has about 350 scanned loops. Many `seg_dist`-only entries are measurement loops (`joints`, `knots`, `tree_faults`, `tidy`) and should be filtered by hand.
- **N-P:** `hinterland/parcels/*`, `settlement/homestead_parts/groves.py` and `grove_fill.py` are listed from the scan only.
- **R:** `settlement/city/*` is reached only through `bridges.py`. The rest of `city/` (for example `moat.py`) shows up only via name matching (b).
- **U/W:** `labels/*` and `settlement/finish.py` were scanned, not read.
- **Not in scope but reached:** `settlement/rolling/*`, `settlement/city/*`, `settlement/land/*`, `waterfields/*` are included only where the name-matched graph reached them.
## T09 - the water and fields stages, filtered by hand (2026-10-28)

Stages: water_frame, field, sink, waterward, pond_stock, pond_bank. Each loop of the scan for these stages read; the counted
ones carry `if __debug__: OPS["candidate@<key>"] += <n>` at the line named.

**Counted (a site, shape or route tried):**

| where | key | what each iteration tries |
|---|---|---|
| `hamletgen/water/fit.py` `_fit_at_aspect` | `_fit_at_aspect` | one carve of the fan at a size `k` |
| `hamletgen/water/fit.py` `_finish_first_admissible` | `_finish_first_admissible` | one admissible carve finished and judged |
| `hamletgen/water/brook.py` `bend_at` | `bend_at` | one bend offset on a stretch |
| `hamletgen/water/brook.py` `clear_of_field` | `clear_of_field` | one nudge of a course vertex off the field |
| `hamletgen/water/brook.py` `settle_course` | `settle_course` | one settling pass over a candidate course |
| `hamletgen/water/brook.py` `feed_brook` (both swing loops) | `feed_brook` | one approach bearing of the brook |
| `hamletgen/water/brook.py` `around_the_field` | `around_the_field` | one edge of the route search relaxed |
| `hamletgen/water/brook.py` `draw_intake` | `draw_intake` | one weir-bar offset |
| `hamletgen/water/polder.py` `walk_pond_uphill` | `walk_pond_uphill` | one reservoir seat up the fall |
| `hamletgen/water/polder.py` `fit_polder` (both rounds) | `fit_polder` | one block size gridded; one winner cleaned |
| `hamletgen/water/polder.py` `_polder_candidate` | `_polder_candidate` | one wander of the polder |
| `settlement/fields/comb.py` `_refused` (the hem's predicate; also `grain.top_up`'s) | `_refused` | one dry plot offered |
| `settlement/fields/comb.py` `bead_drowned` (passed to `bead_runs` by reference) | `bead_drowned` | one bean bead's seat |
| `settlement/fields/comb_record.py` `_comb_source_channel` | `_comb_source_channel` | one pull of the intake into the field |
| `settlement/fields/features.py` `_paddy_features` (pond, grave) | `_paddy_features` | one low plot for the pond; one plot for the grave |
| `settlement/fields/features.py` `_pond_fit` | `_pond_fit` | one pond size in its plot |
| `settlement/fields/paddy.py` `rest_basin` | `rest_basin` | one tuft sample in a rest basin |
| `settlement/land/dikes.py` `perimeter_dike` | `perimeter_dike` | one scatter sample on the dike |
| `hamletgen/sink.py` `pond_setback`, `pond_seat`, `lay_sink` (two), `confluence_keeps_the_brook` | the function | one setback, sway, back-off, route swing, confluence |
| `settlement/farm_fixtures.py` `pond_fixture_fits` (pond_stock's and waterward's seats) | `pond_fixture_fits` | one sty seat on a pond bank |
| `hamletgen/pondbank.py` `stage_pond_bank` | `stage_pond_bank` | one bank tree seat |
| `waterfields/carve.py` `_bund_beans`' `buried` | `_bund_beans` | one bead seat against the other plots |
| `waterfields/seams/close.py` `_split_steps` (a `min` with a key over the cuts) | `_split_steps` (`len(cuts)`) | one cut of a stepped ring |

**Counted at the registry, no counter of their own** (the only test is `admits`/`conflicts`): `settlement/fields/paddy.py`
`resting_plots`, `hamletgen/water/brook.py` `draw_intake`'s record.

**Excluded, with why:**

- measuring or reserving placed things, not trying a site: `hamletgen/water/comb.py` `stage_field`'s ditch corridors,
  `polder.py` `stage_polder`'s and `dike_gaps_at_channels`, `brook.py` `outside_stretches`, `settlement/fields/comb.py`'s hem
  ring detection (`_comb_record_field`) and its stream-reach tests, `landuse.py`'s channel cuts, `dikes.py`' breach tests,
  `sink.py`'s lead scan, `brook_join` sampling and `route_refusals`;
- a test the counted loops call, not a loop of trials: `brook_rules.py` (160, 259, 280), `sink.py` `pond_clear_of_crop`,
  `pondbank.py` `seat_free`, `pondstock.py` `seat_faults`;
- construction of the carved field (no site tried): `brook_course.py` `join_vertices`, `waterfields` partition, pockets,
  clipping, settle;
- nearest-point and ordering keys (a `min`/`sorted` over a measure, no test): the `key=` hits of the reference grep in these
  stages' modules.

**The water_frame stage** has no candidate loop: the walk finds only `pin_knob` and `meta`. **waterward**'s one trial is the
sty seat it reserves (`pond_fixture_fits`, above).

**Misses of T01's shared sites found here:** waterfields keeps its own geometry - `frame._seg_d`, `frame._pip`,
`ring_rules._seg_dist`, `trunks._seg_dist` - which T01's `_geom` counters did not reach; counted now (`dist@`, `pt_test@`).
Other module-local helpers (`brook_rules._proper_cross`, `_dist_to_course`) remain uncounted: these stages' counts are a lower
bound until their rebuild (D2).

**T09's cross-check** (`make perf-fanout SEED=25 HOT=20000 LABEL=443-T09`, 2026-10-28, `dev/perf-log/`): the field stage's
anchors are the walk's or construction excluded above (`crosses_mid_run`, `crosses_poly` are tests; `grid_lines`, `_water`,
`settle`, `_comb_clip_and_cap`, `bund_junctions` build the carve; `_pond_fit` and `_bund_beans` are counted). The sink's
anchors are the registry's `conflicts` (counted there) and `cluster.back_fouled`, which no line of `hamletgen/sink.py` calls
(grep, 2026-10-28) - a cluster predicate T10 counts by function wherever it is reached. No anchor is a miss of the walk.
Python calls after T09 (the run's raw profiles, Python functions only): 10,594,880 at 40 households against 10,591,580 after
T01 (+0.031%), 7,093,577 at 20 against 7,093,049 (+0.007%) - inside SC-001's one in a thousand.

## T10 - the homesteads family, filtered by hand (2026-10-28)

Stages: seat, homesteads, appurtenances, burial, lane_wells, sties, washing. Every seat a house or bundle is tried at ends in one
of two fit tests, so those carry the per-candidate count for the whole seating; the loops above them count their own rounds.

**Counted:**

| where | key | what each count is |
|---|---|---|
| `settlement/houses.py` `_fits` | `_fits` | one house footprint tried (every `try_place`, front-row and cluster seat) |
| `settlement/rolling/fit.py` `_bundle_fits` | `_bundle_fits` | one homestead bundle tried at a seat and side |
| `hamletgen/homesteads/region.py` `SeatRegion.offer` | `SeatRegion.offer` (`len(pts)`) | the seats the region screens at once (vectorized) |
| `hamletgen/homesteads/capacity.py` `offer_seats` | `offer_seats` | one seat offered to the placer |
| `hamletgen/homesteads/rank_rounds.py` `_seat_rank_rounds` | `_seat_rank_rounds` | one widening round of the ranks |
| `settlement/rolling/place.py` `_slide`, `_place_bundle_dispersed`, `_place_bundle_nucleated` | the function | one slide step; one offset; one side of a nucleated seat |
| `settlement/rolling/gap_ways.py` `_way_for`, `_first_admitted` | the function | one exit; one run |
| `settlement/rolling/access.py` `fixtures_clear`, `_house_candidates` (both target loops) | the function | one door or leg asked against the fixtures; one target |
| `settlement/rolling/route.py` `search`, `taut` | the function | one lattice neighbor; one pull of the line taut |
| `settlement/rolling/farmsteads.py` `_relax_gardens_south` | `candidate@` and **`moved@`** | one shift tried; **a placed garden moved after placing (S4)** |
| `settlement/homestead_parts/fixture_seats.py` `clears`, `in_dooryard`, `against_a_part` | the function | one clearance asked (a seat asks `clears` up to twice); one persimmon seat; one wall seat |
| `hamletgen/homesteads/fixtures.py` `_flexible_clear` | `_flexible_clear` | one deferred fixture's seat (the manure pit's) |
| `settlement/homestead_parts/yards.py` `_lay_by_hand`, `_filled_lattice` | the function | one mat try; one lattice gap |
| `hamletgen/homesteads/rows.py` `clear_frames`, `best_row_line`, `seat_rows` | the function | one frame; one street angle; one row seat |
| `hamletgen/homesteads/wells.py` `shared_row_wells`, `seat_wells` | the function | one side of a street well; one pool seat ranked and tried |
| `hamletgen/cluster.py` `seat_cluster`, `back_fouled` | the function | one margin; one back-ground test (also reached from the sink's fanout row) |
| `hamletgen/ways/tree.py` `AccessTree.lay` | `AccessTree.lay` | one chain tried for a new lane of the access tree |
| `hamletgen/homesteads/retirement.py` `retirement_houses` | `retirement_houses` | one retirement-house seat |
| `settlement/shrines_wells/byres.py` `_courtyard_byre_seat`, `_yard_shed_seat`, `_borrowers` | the function | one courtyard side; one shed seat; one borrowed byre drawn from the pool |

**Counted at the registry, no counter of their own:** `rolling/lot.py` `bundle_admitted`, `hamletgen/washing.py`'s shared and
per-house places (footing then `admits`), `retirement.py`'s record, `ways/tree.py` `settle_defer`.

**Excluded, with why** - tests the counted loops call (`houses.py` `_in_blocked`, `_near_corridor`, `_on_a_tread`,
`_clear_of_placed`; `hard_ground._hard_clear`; `wellground._well_ground_clear`; `boundary.SiteCorridors` and
`FreeGround.rect_refused`; `access.parts_clear`, paired with `fixtures_clear`; `passage.walk_clear`, `is_open`; `tree.others_clear`,
`own_clear`; `wells.ok`, `many`), measurements (`seat_geometry.water_push`, `well_seats.walls`, `wells._belt_all`, `_in_belt`,
`dry_households`, `cluster.nearest_within`), and `farmsteads._garden_beds_clear`, the test `_relax_gardens_south` asks.

**The getattr dispatch** (`s._seat_region`, `s._free_ground`, `s._access`, `s._site_corridors`) resolves to `SeatRegion`,
`FreeGround`, `AccessTree` and `SiteCorridors`: their trials are counted above (`offer`, `_house_candidates`, `lay`) and the rest
are tests. **burial** places nothing and has no candidate loop. **sties**' trials are `against_a_part`'s; **washing**'s are the
registry's.

**Split at the 1,000-line bar:** `homesteads/stages.py` went to 1,002 lines with its round counter; `_seat_rank_rounds` moved to
`rank_rounds.py` (stages imports it back, so `stages._seat_rank_rounds`, which a test patches, still names it).

**T10's cross-check** (`make perf-fanout SEED=25 HOT=20000 LABEL=443-T10`, 2026-10-28): three anchors were **misses of the walk**,
counted now - `settlement/rolling/gap_ways.py` `way_out` (each cell asked whether a household's way may cross it, in its search out
of the homestead), `trace` (each join onto the laid ways tried) and `settlement/homestead_parts/wood_share.py` `WoodShares.share`
(each wood seat of a homestead's lattice tried). The rest are counted (`taut`, `_lay_by_hand`, `grow_the_margin` through
`offer`), raster builds (`_geom/region.cells`), or the ways' law and settle (`meet.near_misses`, `web_lines`,
`ways/geom.push_clear_of_fabric`, `settle/shapes.fouled_segment`), which T11 walks. Python calls after T10 (the run's raw
profiles): 10,591,824 at 40 households against 10,594,880 after T09 (-0.03%).

**A measurement for T10's claims round** (2026-10-28, a one-off test calling `Settlement._bundle_envelope` at the canvas center
with `_house_max` and `shed=True`, as `_seat_rank_rounds` does, on the reference spec's four seeds, ft/px 1.0): the envelope is
244.1 x 196.4 ft (seed 4), 312.1 x 236.4 (25), 236.1 x 185.5 (39), 304.1 x 225.5 (47) - so a north-south step between ranks is
the depth plus 39 ft, 224.5-275.4 ft, not the 92 ft (house, yard and sun) the claim "the step between ranks" says. The envelope
is the union of the four garden sides' bundles, not one house and yard.

**Where the rank-step finding is resolved:** the DRIFTED row of `rank_rounds.py::_seat_rank_rounds#the step between ranks` in the
claims index, which `make claims-report` lists and feature 405 resolves (the round arbiter's ask:443-T10-rank-step-carry). Its two
routes: bring the step to house + yard + sun (about 93 ft), or keep the wider step and rewrite the claim as a departure from 0038
§17 with its figure - decided on whether 0038's 92 ft is a fixed row spacing or a minimum for sun. With it, re-read the stale
"about 111 ft" comment above `_rank_step` and the claim "a lane's room between ranks" (impl-drift's notes outside the change).

## T11 - the ways, filtered by hand (2026-10-28)

Stages: track, web, crossings. The ways try routes and points through a few predicates, so the predicates carry most counts.

**Counted:**

| where | key | what each count is |
|---|---|---|
| `hamletgen/clearance.py` `FabricIndex.fouled` | `index_query@`, `index_examined@FabricIndex.fouled` | one point asked of the fabric index, and the entries it examines (every lattice cell, sample and link point of the ways) |
| `hamletgen/ways/route.py` `lattice_search`, `_ease_corner` | the function | one lattice neighbor stepped to; one eased corner |
| `hamletgen/ways/clearance.py` `_clear_link`, `_clear_touch`, `route_around` | the function | one link or touch tried; one route round a polygon |
| `hamletgen/ways/track.py` `connector_track` | `connector_track` | one bearing of the connector |
| `sitegen/geom.py` `pull_clear` | `pull_clear` | one pull of a point clear |
| `hamletgen/ways/settle/shapes.py` `fouled_segment`; `ways/fabric.py` `house_hit`, `_crosses_fabric`; `ways/law/ends.py` `over_a_fixture` | the function | one run asked against houses, yards and fixtures |
| `hamletgen/ways/lay.py` `_held` | `_held` | one re-aim or cut of a draft lane, asked again |
| `hamletgen/ways/serve.py` `door_off_fixtures`, `door_path` | the function | one door offset; one door path sought |
| `hamletgen/ways/bund.py` `RunOnBlocks.clear`, `a_way_onto_the_bund` | the function | one bund leg; one end tried onto the bund |
| `hamletgen/ways/knots.py` `trial_count` | `trial_count` | one fence gap tried |
| `settlement/city/bridges.py` `_deck_corners_clear`, `undeckable_at` | the function | one deck size or skew; one run asked whether a deck can carry it |
| `hamletgen/ways/law/meet.py` `free_end` (`seg_test@`, the other ways it is asked against), `box_gap` (`dist@`); `ways/tails.py` `tail_doubled` (`seg_test@`) | the function | the web law's all-pairs end tests (feature 427's hot chains) |

**Counted at the registry, no counter of their own:** `settlement/water_ways/lanes.py` `admits_lane` and `admitted_runs` (each
segment asked `admits`), `ways/last_resort.py`'s refusals, `bridges.deck_admitted`.

**Excluded, with why:** construction and assembly - `ways/web/skeleton.py`, `web/stage.py`'s line loop, `tree.lanes_of`,
`fabric.project`, `ways/street.py`'s threading of a placed line, `route._unjog` and `in_band`'s link pulls (their tests are
`_clear_link`, counted), `clearance.clip_to_clear` and `clear_runs` (samples through `fouled`, counted); measurement -
`track.on_course`, `serve.to_first_arrival`, `street.near`, `web/stage.near`; and `law_water.crossing_points`, an indexed pair
test (its grid's `near` counted).

**Uncounted work, a lower bound:** `law/meet.web_lines` and `web_faces` build and polygonize the treads in shapely, work in C the
counters do not see (S5); the web law's checks over the laid web (`near_misses`, `fronting_ends`, `doubled_tails`) are counted
through `free_end` and `tail_doubled`, not as candidates - they judge placed lanes, the S4 question 444's rebuild of the web asks.

**T11's cross-check** (`make perf-fanout SEED=25 HOT=20000 LABEL=443-T11`, 2026-10-28): the web's anchors are counted
(`undeckable_at`, `doubled_tails` via `tail_doubled`, `lattice_search`, `over_a_fixture`, `fronting_ends` via `free_end`) or
excluded above (`lanes_of`, `project`, `crossing_points`); the homesteads stage's `near_misses` and `web_lines` (T10's) are the
law's, counted through `free_end` and uncounted shapely respectively. No anchor is a miss. Python calls (the run's raw profiles):
10,576,254 at 40 households against 10,591,824 after T10 (-0.15%), 7,085,089 at 20 against 7,093,022 (-0.11%).

## T12 - ground cover, the frame, the notice board and the labels, filtered by hand (2026-10-28)

Stages: hinterland, woodland, windbreak, bamboo, frame, notice, labels.

**Counted** (each the function's key): the woods' and groves' crown tests `settlement/shrines_wells/woods.py` `_crown_seat_clear`,
`_fringe_blocked` and `homestead_parts/keepouts.py` `_crown_covers` (every crown seat a stand, belt, grove or woodland tries); the
bamboo strips `hamletgen/homesteads/bamboo.py` `strip_refused` and `hinterland/bamboo.py`'s `_fits` (`bamboo_seats._fits`); the
parcels `hinterland/parcels/patches.py` `_ok` (`open_ground_patches._ok`) and `fit_square_parcel`'s shrinks; the paddy grass
`hinterland/paddy_grass.py` `clear_of_plot`; the belt `hinterland/belt.py` (`belt_polygon`, one span and setback tried); the
grove gaps `homestead_parts/grove_fill.py` `reseat_clump` and `close_belt_gaps` (a miss of the walk, added from the cross-check);
the groves' top-up `homestead_parts/groves.py` (`GroveMixin.seat`); the woodland's stocking `land/cover.py` `_stock_woodland`; the
title's and title pocket's box tests `settlement/title.py` `_box_clear`, `hinterland/frame.py` `pocket_clear_of_features`; the notice
board's route seats `settlement/structures/fixtures/siting.py` `_route_seats` (each verge and band seat); the label placer
`labels/obstacles.py` `Obstacles.blocked` and `labels/placer.py` `_strict_seat`. The notice board's house-fit is `_fits` (T10's).

**Excluded, with why:** drawing and scatter - the stand and fringe fills (`woods._draw_stand`, `_stand_fringe`), the commons'
scatter (`cover._sparse`, `_in_soft`), `stands.bamboo_stand`'s mark grid, `dikes`' mottle; construction - the belt walk and
ranks (`groves.belt_walk`, `_belt_ranks`, their tests `_crown_covers` counted), `belt_law`'s index, `grove_blocks`' indexes,
`ink_and_record_grove`, `village_grove`'s layout (its seats through `_crown_covers`), `convex_hull`; measurement - `bamboo.across_a_lane`,
`in_belt`, `_strip_blocked` (inside `strip_refused`, counted). **woodland** places nothing of its own (the commons' stocking is the
hinterland's).

**T12's cross-check** (`make perf-fanout SEED=25 HOT=20000 LABEL=443-T12`, 2026-10-28): one miss, `grove_fill.close_belt_gaps`'
gap-seat loop, counted now; the rest are counted (`household_bamboo` through `strip_refused`, `open_ground_patches`, the notice
board's `blocked`) or construction above. Python calls (the run's raw profiles): 10,576,265 at 40 households against 10,576,254
after T11 (+0.0001%).
