# FR-009: where each retired rule now lives

One row per check. A check is not deleted until this file gives it a destination and the destination has
been PROVEN - either a new test seen RED against the unfixed placer, or an existing test shown by mutation
to already carry the rule.

## The method, and why it is mutation rather than reading

Two questions have to be answered per check, and only one of them can be answered by reading:

1. **Which placer guarantees this rule?** Read the check, read the placer. No shortcut.
2. **Is the rule ALREADY carried by a test?** This looks answerable by reading and is not. A test that
   *mentions* the subject may assert nothing about the rule; a test that never names it may guard it
   exactly. `specs/166-retire-the-check-battery/covered_by.py` answers it by MUTATION: break the placer's
   guarantee, run the suite with the battery's own tests excluded, and see whether anything goes red.

The battery's own tests are excluded deliberately - they are what is being retired, so a rule only they
catch is precisely a rule with no home yet.

**This changed the shape of the work.** The plan assumed 101 migrations each needing a new test. The first
probes show existing placer suites already carry some of them, and those drop against a named test instead.

## Retired, with a new test written and proven

| check | destination | proof |
|---|---|---|
| `bamboo_stands_clear_of_paddies` | `tests/hamletgen/test_hinterland.py::test_bamboo_blocked_refuses_ground_inside_the_crop` + `_keeps_its_pad_off_the_crop_edge` | crop arm cut from `bamboo_blocked` -> both RED |
| `gardens_clear_of_channels` | `tests/settlement/test_homestead_parts.py::test_a_garden_is_refused_on_a_no_build_corridor` + `test_a_watercourse_registers_the_corridor_the_garden_consults` | corridor arm cut from `_garden_fits` (line-targeted, enclosing `def` asserted) -> RED |
| `title_has_placard` | `tests/settlement/test_label_placement.py::test_the_title_records_a_placard` | placard key renamed -> RED |
| `scalebar_matches_declared_scale` | `..::test_the_scalebar_reports_the_declared_scale` (3 rungs of the ladder) | `bar_ft` offset by one -> RED |
| `title_clear_of_features` | `..::test_the_blank_spot_scan_refuses_a_box_that_covers_an_obstacle` + `_returns_nothing_when_the_window_is_full` | `_box_clear`'s rect arm short-circuited -> RED |

| `labels_within_image` / `no_label_overlaps` (the REACH half) | `tests/settlement/test_label_placement.py::test_a_tilted_labels_reach_is_its_rotated_quad_not_its_unrotated_box` | `label_aabb` made to return the unrotated box -> RED |

*Note on that last row:* it carries the REACH the two rules depend on, not the rules entire. Containment
against the frame and pairwise non-overlap still need their own destinations; what is proven here is that a
tilted caption's reach is its rotated quad, which is the quantity both rules measure and the one
`dev/gate.md` records being got wrong ("a tilted caption as a ROTATED QUAD" vs "an axis-aligned bounding
box" - measuring the wrong one made every seat look illegal and the fallback took a worse one).

| `no_structure_on_paddy` | `tests/settlement/test_field_keepout.py` (point, gap and rect arms) | `_field_blocks_point` and `_field_blocks_rect` each short-circuited -> RED |
| `dry_plots_clear_of_paddies` | same module - one segment emits both, and one keep-out guarantees both | same mutations -> RED |

| `no_structure_on_stream` | `tests/settlement/test_way_and_water_corridors.py` (registration + refusal) | river's `corridors.append` removed -> RED; `_near_corridor` short-circuited -> RED |
| `houses_clear_of_lanes` | same module | lane's `corridors.append` removed -> RED |
| `no_farmhouse_stands_on_a_lane` | same module (the `width/2 + 11` setback, which is what clears building CORNERS) | same mutations -> RED |

| `irrigation_channels_hairline` | `tests/settlement/test_water_width_ladder.py` | channel default width raised off the floor -> RED |
| `watercourses_wider_than_ditches` | same module (the ladder's ORDER, which is the part that is not a legibility deviation) | same mutation -> RED |

| `settlement_declares_a_land_fall` | `tests/gate/test_generator_contracts.py` | a map declaring neither a fall nor per-field falls fails the assertion |
| `households_consistent` | same module | seated count against the spec's ask |
| `farmhouse_sizes_vary` | same module (effective footprint, so BOTH size encodings count) | - |
| `settlement_records_cluster_seeding` | same module | the shape record removed from `homesteads.py` -> RED |
| `byre_form_declared` | same module | allowed forms read off the engine, not guessed |

| `polder_fills_its_bbox` | `tests/waterfields/test_polder_geometry.py` (4 seeds) | - |
| `polder_floor_is_ring_interior` | same module | - |
| `polder_edges_wander` | same module | `lwander` made to return (0, 0) -> RED |
| `polder_dike_gapped_at_sluices` | same module | - |

| `village_windbreak_present` | `tests/hamletgen/test_hinterland.py` (belt suite) | `belt_polygon` made to return [] -> RED |
| `village_windbreak_embraces_cluster` | same suite (the belt's centre projects along +wind) | same mutation -> RED |
| `village_windbreak_scales_with_cluster` | same suite (a 12-house cluster gets more belt than a 3-house one) | same mutation -> RED |
| `village_windbreak_is_continuous` | same suite (the belt spans a ragged fringe rather than one lobe) | same mutation -> RED |

| `tree_crowns_not_subsumed` | `tests/settlement/test_canopy_seating.py` | `_crown_seat_clear` made to allow everything -> RED |
| `structures_clear_of_trees` | same module (`_crown_covers` over a recorded roof) | - |
| `wells_clear_of_trees` | same module (`_crown_covers` over a wellhead) | - |

| `settlement_has_wells` | `tests/hamletgen/test_wells.py` (floor, ceiling, and the 2-20 households-per-well band) | `well_target` divisor changed -> RED |

| `wells_off_the_wet_toe` | `tests/settlement/test_well_ground.py` (water, pond, dry plot, and the DRAWN-head margin) | the pond arm of `_well_ground_clear` removed -> RED |

| `pond_clear_of_field` | `tests/settlement/test_well_ground.py` (pond section) | `self.ellipses.append` removed from `pond()` -> RED |
| `pond_clear_of_paddies` | same module - one registry, so one guarantee serves both | same mutation -> RED |

| `farmhouses_reach_a_way` | `tests/hamletgen/test_unreached_houses.py` (11 unit tests) PLUS `tests/gate/test_reach_predicate_matches_the_check.py` (equivalence on 5 live maps and their perturbed copies) | done at T02 - the check's body LIFTED, with the equivalence test that dies with the check |

| `lanes_clear_of_dry_plots` | `tests/hamletgen/test_lane_clipping.py` (`clip_to_clear`, whose obstacle list is envelope + crops + fabric + wet toe together) | clipping disabled -> RED |

| `delivery_ditches_taper` | `tests/waterfields/test_comb_topology.py` (4 seeds) | `_canal_ft` made to return one weight -> RED |
| `water_channels_obtuse_turns` | same module | - |
| `field_ditches_terminate` | same module (the builder's half: there IS a run to land) | - |

## Already carried by an existing test - dropped against it, not rewritten

| check | carried by | proof |
|---|---|---|
| `hamlet_has_kosatsuba` | `tests/settlement/test_structures.py` (the `place_kosatsuba` suite) | board never placed -> RED |
| `caption seating (lane clearance)` | `tests/settlement/test_structures.py` | `pick_caption_seat` renamed out from under its callers -> RED |

| `village_has_kosatsuba` / `town_has_kosatsuba` / `city_has_kosatsuba` | `tests/settlement/test_structures.py` (the `place_kosatsuba` suite) | board never placed -> RED (proved earlier in this feature) |

*Why one entry for three:* `place_kosatsuba` is tier-agnostic - the GM's 2026-07-24 ruling is that EVERY
settlement tier carries the board, and the placer auto-sites it from the same manifest route fields at every
scale. The three check names are one guarantee wearing three scale labels, so one proof serves them. What
differs by tier is the COUNT (a city draws the set: the principal board plus one per main gate), and that is
`city_kosatsuba_per_gate`, a separate rule still owed.

| `ways_cross_water_on_a_deck` | `tests/settlement/test_bridge_sources.py` | the one-deck dedup removed from `bridge()` -> RED; undrawn conduits offered -> RED |

| `sluice_gates_on_water` | `tests/settlement/test_sluice_gates.py` | the gate's `sluice_gates` append removed -> RED |
| `channel_gates_at_water_junctions` (recording half) | same module | same mutation -> RED; the span mutation -> RED |

| `map_frame_hugs_its_content` | `tests/settlement/test_crop_framing.py` | `crop_to_content` made a no-op -> RED |
| `crop_not_held_open_by_one_feature` | same module (a trailing lane must not widen the frame) | same mutation -> RED |
| `no_caption_holds_the_frame_open` | same module - one frame rule, three checks | same mutation -> RED |

| `torii_clear_of_walls` | `tests/settlement/test_torii_seating.py` | `torii_seat_on_wall` made to never refuse -> RED; the true-scale box mutated to the legacy 19 -> RED |

| `commons_clear_of_paddies` | `tests/settlement/test_hinterland_cover.py` (the scrub BANDS; the interior fill is excluded, with the reason recorded in the test) | `hinterland` made a no-op -> RED |
| `marsh_on_low_ground` | same module (the toe sits below the field, oriented by `down_deg`) | same mutation -> RED |
| `scrub_clear_of_urban_fabric` | same module (cover is not a crop anchor, so it bleeds off the frame) | same mutation -> RED |

| `drain_runs_cross_slope` | `tests/waterfields/test_comb_flow.py` (6 falls, plus rotation and a non-vacuous drain) | the drain made to ignore the fall -> RED |

| `paddy_fan_has_floor` | `tests/gate/test_paddy_fabric.py` (a rolled comb fan) | the ditched-paddy floor set emptied -> RED |
| `comb_floor_ends_at_the_collector` | same module; the engine's own `floor_overhang` | `floor_overhang` made to report a long overhang -> RED |
| `comb_supply_commands_both_flanks` | same module (cross-slope extent vs delivery reach, per flank) | asserted with a non-vacuity floor on both flank extents |
| `paddy_plots_are_workable_basins` | same module; the engine's own `pointed_ring` at 15 deg | `pointed_ring` made to call every ring a needle -> RED |
| `flooded_plots_read_as_basins` | same module (the PICTURE record matched to its ring) | same mutation -> RED; the match count is asserted so it cannot judge nothing |
| `paddy_basins_are_worth_their_bund` | same module; the ratio to the fan's OWN design cell | `_GATE_MIN_AREA` raised past every basin -> RED |
| `paddy_plot_rings_overcount_stays_marginal` | same module (ring-area sum vs shapely union) | the 4% ceiling is ~1.6x the worst live map |
| `paddy_bunds_do_not_stagger` | same module; the engine's own `jog_vertices` | `close_seams` made to stop straightening its own steps -> RED |

| `channels_flow_downhill` | `tests/gate/test_water_flow.py` (a rolled map, judged against the DECLARED fall) | the map's fall turned 90 deg and flipped 180 deg -> RED both ways |
| `drain_flows_downhill` | same module (the outfall's projection on the fall vs the head's) | same mutations -> RED |
| `drainage_discharges_downhill` | same module (the sink pond / brook must lie down-fall of the outfall) | same mutations -> RED |
| `streams_avoid_fields` | same module (stream vertices inside a field outline) | asserted with both populations non-empty first |
| `stream_source_anchored` | same module (an off-map end is off the canvas; a pond end is on the pond) | the count of DECLARED ends is asserted, so it cannot judge nothing |
| `stream_end_anchored` | same module (same assertion, the far end) | same |
| `fields_show_water_source` | same module (every paddy named by a channel or a field ditch) | asserted with the paddy population non-empty first |

| `field_ditches_reach_source_and_sink` | `tests/gate/test_water_junctions.py` (the KUWABATA roll - the one live map that lays laterals) | the laterals shifted 40 px off their trunks -> RED |
| `field_ditch_tips_land_on_the_trunk` | same test (both ends of every lateral) | same mutation -> RED. `polder.py` snaps both ends with `_onto(lat_xy[0], feeder_xy)` / `_onto(lat_xy[-1], drain_xy)` - the guarantee was always in the placer |
| `channels_join_water_not_cross` | same module (a joiner crossing open water away from its own mouth) | asserted with both populations non-empty; a mouth ENDING on the bed is the confluence, not a crossing |
| `water_channels_join_not_cross` | same test | same |
| `channels_join_not_cross_at_fork` | same test | same |
| `channels_join_streams_at_confluence` | same module (a channel DECLARING a stream must reach its bed) | the count of declaring channels is asserted first |
| `waterways_merge_at_crossings` | same module (the recorded paint stack: the topmost sheen sits above every bed) | asserted on the recorded `bedz`/`sheenz`, because the dark seam is a compositing fact, not a position |
| `pond_connected_to_field` | same module (the course the DECLARED `pond_role` requires must reach the water) | the required course population is asserted before the reach is |
| `pond_fill_covers_channel_mouths` | same module (the fill's `bedz` above every joining mouth's) | the joining-mouth count is asserted first |
| `field_ponds_sunk_into_one_plot` | same module (no bund or hem ring crosses the pond ellipse) | the field-pond population is asserted first |
| `pond_fed_from_edge` | **DROP - no scripted executor.** Measured across every live map: not one pond is fed by a stream (Inashiro and Mizuguchi declare `pond_role=drainage` and are fed by the collector; the other three record no role). The rule is about a SOURCE pond fed by a brook from off-map, which only a hand-authored map produces. Its grounding - a pond's water comes from the edge, not from nowhere - is recorded here and in `settlements/water.md` | - |

| `lanes_form_one_network` | `tests/gate/test_lane_network.py` (union-find over the rolled lanes at the web's own 4 px join) | the lane web never laid -> RED; `lanes_share_tread` made to deny every join -> RED |
| `lanes_bend_like_paths` | same module (a turn past 140 deg doubles back; two real turns inside 40 ft is a kink) | same mutations -> RED |
| `lanes_reach_something` | same module (every non-connector end within 60 px of a way, a house or a field) | same mutations -> RED |
| `lanes_do_not_break_mid_run` | same module (a long jump whose midpoint lands inside something solid) | the solid population is asserted first, so a break has something to be explained by |
| `lane_ends_front_different_houses` | same module (no house discharges more than two lane ends) | the fronted-end count is asserted, so it cannot judge nothing |
| `groves_clear_of_lanes` | same module (the TRUNK position, never the crown's reach - GM 2026-08-29: a woodland path is a path under trees) | the flat `(x, y, r)` packing is named at the point of use, because reading the third value is the mistake the rule warns against |
| `fields_clear_of_road` | **DROP - no scripted executor.** `roadways` is derived from `M["road"]`, which is empty on every live map; no scripted generator lays an Imperial road. The grounding - a way's tread may not run under a drawn plot - is recorded here and in `settlements/ways.md` | - |
| `roads_clear_of_marsh` | **DROP - same reason**, same `roadways` source. A road is routed around standing water rather than through it; recorded, not deleted | - |

| `woodland_commons_visibly_stocked` | `tests/gate/test_settlement_cover.py` (crowns recorded, at least five) | `stage_woodland` made to seat nothing -> RED |
| `woodland_commons_on_dry_ground` | same module (a 5x5 sample grid against the drawn marshes) | same mutation -> RED; the marsh population is asserted first |
| `woodland_commons_within_the_frame` | same module (70% of the parcel's box inside the recorded view) | same mutation -> RED |
| `village_groves_visibly_stocked` | same module (1.5 clumps per 100k sq px) | `stage_windbreak` made to plant nothing -> RED |
| `copse_stands_clear_of_the_belt` | same module (no copse clump inside a belt clump's canopy radius) | same mutation -> RED |
| `canopy_clear_of_watercourses` | same module (clump centers against every channel and stream) | same mutation -> RED |
| `cluster_abuts_fields` | `tests/gate/test_cluster_and_homes.py` (nearest house within 60 px; the far side allowed a cluster-span) | measured on the reference roll: nearest 33 px, farthest 242 |
| `cluster_shape_matches_the_drawing` | same module (the DRAWN aspect inside the rolled shape's band, or an explicit unhonored note) | a knob that never binds looks exactly like one that always does - the motivating case is in the docstring |
| `byres_meet_their_target` | same module (seated >= declared target) | `stage_appurtenances` made to seat nothing -> RED |
| `farmhouses_shed_separately` | same module (the 8 ft eave gap, wall to wall) | the engine's own `FARMHOUSE_EAVE_GAP_FT`, which survives the battery |
| `farmhouse_aspect_in_range` | same module (2.7:1; live worst 2.37, so ~11% of margin) | a live guard on a real regression, not a re-measurement of a guarantee |
| `wells_among_dwellings` | same module (95 px to a dwelling's EDGE, never its center) | `place_wells` made to dig nothing -> RED |
| `settlement_dwellings_watered` | same module (760 ft to a well or open water, via the engine's `surface_water_dist`) | same mutation -> RED |

## Battery-internal - they go WITH the battery, and owe no destination

These four do not state a rule about a map. They state that the battery's OWN classification tables are
complete: that every feature type is classified for the overlap matrix, for the label groups, for the
matrix policy, and that no matrix debt is outstanding. They are the battery auditing itself.

| check | why no destination is owed |
|---|---|
| `every_feature_classified_for_overlap` | asserts `_OVERLAP_STRUCTS` covers every drawn feature - a `check_village` table |
| `every_feature_classified_for_matrix` | asserts the `_MATRIX_*` policy covers every pairing - a `check_village` table |
| `every_solid_feature_classified_for_labels` | asserts `_LABEL_GROUP` covers every glyph a caption can bury - a `check_village` table |
| `matrix_debts_still_owed` | asserts the matrix's own debt register is empty - a `check_village` register |

**Measured, not assumed.** Grepping every consumer of `_OVERLAP_STRUCTS`, `_LABEL_GROUP`, `OVERLAP_CLASS`
and `_MATRIX_*` outside `check_village/` returns four hits, and **three are comments** (`castle_civic.py`,
`city/waterfront.py`, `homestead_parts.py` each merely NAME a table while explaining why some feature is
exempt). The one live consumer is a TEST: `tests/settlement/test_homestead_parts.py:337`, which reads
`check_village._OVERLAP_STRUCTS` to assert the engine classifies every key in it - itself a
battery-completeness assertion that happens to live in a settlement test.

So when the battery goes, the tables go, and a rule about the tables has nothing left to be about. What
Phase 4 owes here is not a replacement but a DELETION: that one test goes with them, and this row is the
record of why, so a later reader does not mistake it for an oversight.

## Still owed

The remaining checks, by group, are in `destinations.json`. The split that governs the work:

- **~101 migrate-only** (`FIRES-HAND-ONLY`): the placer guarantees the rule today. Each needs its
  destination proven - by probe if an existing test carries it, by a new test if not.
- **~36 placer bugs** (`FIRES`): a scripted artifact still trips the check, so the placer does NOT
  guarantee it. Each is a repair, not a migration.
- **4 keeps** documented in feature 163's `placer-reads.md`.
