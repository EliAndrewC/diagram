# Firing census - 152 live checks against 5 live maps and 105 frozen fixtures

`FIRES` 40 | `FIRES-HAND-ONLY` 53 | `NEVER-FIRES` 59 - 797 verdicts observed, NO suite journal (run `make firing-census SUITE=...`)

`FIRES` = the current implementation makes it fail. `FIRES-HAND-ONLY` = only a hand-era artifact
does, which FR-003 treats as never-fires. Every non-`FIRES` row takes the FR-006 placer read
before anything is deleted - the census produces a candidate, not a ruling (feature 158).

| check | verdict | evidence |
|---|---|---|
| `aqueduct_taps_water_lands_dry` | **NEVER-FIRES** | - |
| `bamboo_stands_clear_of_paddies` | **NEVER-FIRES** | - |
| `bridges_span_their_water` | **NEVER-FIRES** | - |
| `capital_has_kosatsuba` | **NEVER-FIRES** | - |
| `capital_has_no_headman` | **NEVER-FIRES** | - |
| `channel_gates_at_water_junctions` | **NEVER-FIRES** | - |
| `channels_join_water_not_cross` | **NEVER-FIRES** | - |
| `city_has_kosatsuba` | **NEVER-FIRES** | - |
| `city_has_no_headman` | **NEVER-FIRES** | - |
| `city_streets_reach_their_neighbors` | **NEVER-FIRES** | - |
| `cluster_abuts_fields` | **NEVER-FIRES** | - |
| `commons_clear_of_paddies` | **NEVER-FIRES** | - |
| `crop_not_held_open_by_one_feature` | **NEVER-FIRES** | - |
| `every_feature_classified_for_matrix` | **NEVER-FIRES** | - |
| `every_feature_classified_for_overlap` | **NEVER-FIRES** | - |
| `every_solid_feature_classified_for_labels` | **NEVER-FIRES** | - |
| `farmhouse_aspect_in_range` | **NEVER-FIRES** | - |
| `farmhouse_sizes_vary` | **NEVER-FIRES** | - |
| `field_ditches_terminate` | **NEVER-FIRES** | - |
| `footbridges_reach_useful_ground` | **NEVER-FIRES** | - |
| `gardens_clear_of_channels` | **NEVER-FIRES** | - |
| `households_consistent` | **NEVER-FIRES** | - |
| `houses_face_south` | **NEVER-FIRES** | - |
| `inwall_drains_gated_at_cutoff` | **NEVER-FIRES** | - |
| `kosatsuba_faces_the_road` | **NEVER-FIRES** | - |
| `lanes_clear_of_dry_plots` | **NEVER-FIRES** | - |
| `matrix_debts_still_owed` | **NEVER-FIRES** | - |
| `no_structure_on_stream` | **NEVER-FIRES** | - |
| `no_structure_on_torii` | **NEVER-FIRES** | - |
| `religious_clear_of_ring_and_towers` | **NEVER-FIRES** | - |
| `remote_shrine_has_own_well` | **NEVER-FIRES** | - |
| `scalebar_matches_declared_scale` | **NEVER-FIRES** | - |
| `scatter_respects_swept_clearings` | **NEVER-FIRES** | - |
| `scrub_clear_of_urban_fabric` | **NEVER-FIRES** | - |
| `shrine_halls_clear_of_lanes` | **NEVER-FIRES** | - |
| `sluice_gates_on_water` | **NEVER-FIRES** | - |
| `stream_end_anchored` | **NEVER-FIRES** | - |
| `stream_source_anchored` | **NEVER-FIRES** | - |
| `structures_clear_of_trees` | **NEVER-FIRES** | - |
| `tanning_yards_on_water` | **NEVER-FIRES** | - |
| `title_clear_of_features` | **NEVER-FIRES** | - |
| `title_has_placard` | **NEVER-FIRES** | - |
| `torii_clear_of_halls_towers_ring` | **NEVER-FIRES** | - |
| `torii_clear_of_walls` | **NEVER-FIRES** | - |
| `town_has_kosatsuba` | **NEVER-FIRES** | - |
| `town_has_no_headman` | **NEVER-FIRES** | - |
| `towpath_hugs_the_bank` | **NEVER-FIRES** | - |
| `village_has_no_headman` | **NEVER-FIRES** | - |
| `village_windbreak_present` | **NEVER-FIRES** | - |
| `waivers_are_documented` | **NEVER-FIRES** | - |
| `waivers_are_live` | **NEVER-FIRES** | - |
| `waterside_works_follow_the_bank` | **NEVER-FIRES** | - |
| `waterward_strips_run_off_the_frame` | **NEVER-FIRES** | - |
| `waterways_merge_at_crossings` | **NEVER-FIRES** | - |
| `ways_clear_of_castle_moat` | **NEVER-FIRES** | - |
| `ways_cross_water_on_a_deck` | **NEVER-FIRES** | - |
| `ways_not_inside_road_beds` | **NEVER-FIRES** | - |
| `wells_among_dwellings` | **NEVER-FIRES** | - |
| `wells_clear_of_trees` | **NEVER-FIRES** | - |
| `all_ink_is_ruled_on` | **FIRES** | `scripted-fixture` all_ink_is_ruled_on_fires_on_an_unruled_element.json |
| `bund_beans_on_bunds` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json |
| `byre_form_declared` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` byre_form_declared_fires_when_a_map_draws_byres_and_names_no_form.json; `scripted-fixture` comb_floor_ends_at_the_collector_fires_on_the_se_needle_mizuguchi.json (+30 more) |
| `byres_meet_their_target` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` byre_form_declared_fires_when_a_map_draws_byres_and_names_no_form.json; `scripted-fixture` comb_floor_ends_at_the_collector_fires_on_the_se_needle_mizuguchi.json (+30 more) |
| `caption_stands_beside_its_referent` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` byre_form_declared_fires_when_a_map_draws_byres_and_names_no_form.json; `scripted-fixture` caption_stands_beside_its_referent_fires_on_the_board_past_the_end_of_its_label.json (+39 more) |
| `captions_clear_the_ways_they_stand_on` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` captions_clear_the_ways_they_stand_on_fires_when_a_caption_notches_its_lane.json; `scripted-fixture` cluster_shape_matches_the_drawing_fires_when_the_map_records_no_shape_at_all.json (+17 more) |
| `cluster_shape_matches_the_drawing` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` byre_form_declared_fires_when_a_map_draws_byres_and_names_no_form.json; `scripted-fixture` cluster_shape_matches_the_drawing_fires_on_a_declared_shape_the_cluster_does_not_have.json (+33 more) |
| `comb_floor_ends_at_the_collector` | **FIRES** | `scripted-fixture` comb_floor_ends_at_the_collector_fires_on_the_se_needle_mizuguchi.json; `scripted-fixture` comb_supply_commands_both_flanks_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` settlement_records_cluster_seeding_fires_on_the_untraced_knob_kashikawa.json; `scripted-fixture` woodland_commons_within_the_frame_fires_on_offframe_coppice_sawada.json |
| `comb_supply_commands_both_flanks` | **FIRES** | `scripted-fixture` comb_supply_commands_both_flanks_fires_on_the_pre_fix_inashiro.json |
| `copse_stands_clear_of_the_belt` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` byre_form_declared_fires_when_a_map_draws_byres_and_names_no_form.json; `scripted-fixture` cluster_shape_matches_the_drawing_fires_on_a_declared_shape_the_cluster_does_not_have.json (+34 more) |
| `drainage_discharges_downhill` | **FIRES** | `hand-fixture` drain_flows_downhill_fires_when_outfall_is_uphill.json; `hand-fixture` drainage_discharges_downhill_fires_when_the_brook_runs_uphill.json; `scripted-fixture` drainage_discharges_downhill_fires_on_cohort_seed_2s_uphill_brook.json |
| `drainage_junction_smooth` | **FIRES** | `hand-fixture` drain_flows_downhill_fires_when_outfall_is_uphill.json; `hand-fixture` drainage_discharges_downhill_fires_when_the_brook_runs_uphill.json; `hand-fixture` drainage_junction_smooth_fires_on_a_hard_corner.json; `scripted-fixture` drainage_discharges_downhill_fires_on_cohort_seed_2s_uphill_brook.json |
| `dry_plot_furrows_vary` | **FIRES** | `hand-fixture` dry_plot_furrows_vary_fires_when_two_neighbours_share_an_angle.json; `hand-fixture` ways_clear_of_paddies_and_marsh_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json (+36 more) |
| `farmhouses_reach_a_way` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` byre_form_declared_fires_when_a_map_draws_byres_and_names_no_form.json; `scripted-fixture` comb_floor_ends_at_the_collector_fires_on_the_se_needle_mizuguchi.json (+28 more) |
| `farmhouses_shed_separately` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` comb_floor_ends_at_the_collector_fires_on_the_se_needle_mizuguchi.json; `scripted-fixture` comb_supply_commands_both_flanks_fires_on_the_pre_fix_inashiro.json (+12 more) |
| `features_do_not_overlap` | **FIRES** | `hand-fixture` houses_clear_of_lanes_fires_when_a_house_sits_on_the_tread.json; `scripted-fixture` drainage_discharges_downhill_fires_on_cohort_seed_2s_uphill_brook.json |
| `field_ponds_sunk_into_one_plot` | **FIRES** | `hand-fixture` ways_clear_of_paddies_and_marsh_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` comb_floor_ends_at_the_collector_fires_on_the_se_needle_mizuguchi.json (+5 more) |
| `flooded_plots_read_as_basins` | **FIRES** | `scripted-fixture` flooded_plots_read_as_basins_fires_on_the_seam_needles_sawada.json |
| `kosatsuba_by_the_road` | **FIRES** | `hand-fixture` village_and_hamlet_have_kosatsuba_3.json; `scripted-fixture` drainage_discharges_downhill_fires_on_cohort_seed_2s_uphill_brook.json; `scripted-fixture` farmhouses_reach_a_way_fires_on_sawada_before_the_lane_web.json; `scripted-fixture` flooded_plots_read_as_basins_fires_on_the_seam_needles_sawada.json (+4 more) |
| `labels_align_with_their_referent` | **FIRES** | `scripted-fixture` labels_align_with_their_referent_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` lanes_bend_like_paths_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` lanes_form_one_network_fires_on_the_pre_fix_inashiro.json |
| `lane_ends_front_different_houses` | **FIRES** | `scripted-fixture` farmhouses_reach_a_way_fires_on_kashikawa_before_the_lane_web.json; `scripted-fixture` farmhouses_reach_a_way_fires_on_mizuguchi_before_the_lane_web.json; `scripted-fixture` lane_ends_front_different_houses_fires_on_kashikawa_crows_foot.json; `scripted-fixture` lane_ends_front_different_houses_fires_on_mizuguchi_crows_foot.json |
| `lanes_bend_like_paths` | **FIRES** | `scripted-fixture` lanes_bend_like_paths_fires_on_the_pre_fix_inashiro.json |
| `lanes_do_not_break_mid_run` | **FIRES** | `scripted-fixture` byre_form_declared_fires_when_a_map_draws_byres_and_names_no_form.json; `scripted-fixture` farmhouses_reach_a_way_fires_on_sawada_before_the_lane_web.json; `scripted-fixture` lanes_do_not_break_mid_run_fires_on_sawadas_broken_spine.json |
| `lanes_form_one_network` | **FIRES** | `scripted-fixture` byre_form_declared_fires_when_a_map_draws_byres_and_names_no_form.json; `scripted-fixture` cluster_shape_matches_the_drawing_fires_on_a_declared_shape_the_cluster_does_not_have.json; `scripted-fixture` cluster_shape_matches_the_drawing_fires_when_the_map_records_no_shape_at_all.json; `scripted-fixture` drainage_discharges_downhill_fires_on_cohort_seed_2s_uphill_brook.json (+11 more) |
| `lanes_reach_something` | **FIRES** | `scripted-fixture` drainage_discharges_downhill_fires_on_cohort_seed_2s_uphill_brook.json; `scripted-fixture` paddy_plot_seams_shared_fires_on_the_pre_fix_kashikawa.json; `scripted-fixture` paddy_plots_are_workable_basins_fires_on_the_fan_toe_sunburst_kashikawa.json |
| `long_ditches_have_a_footbridge` | **FIRES** | `scripted-fixture` byre_form_declared_fires_when_a_map_draws_byres_and_names_no_form.json; `scripted-fixture` captions_clear_the_ways_they_stand_on_fires_when_a_caption_notches_its_lane.json; `scripted-fixture` cluster_shape_matches_the_drawing_fires_on_a_declared_shape_the_cluster_does_not_have.json; `scripted-fixture` cluster_shape_matches_the_drawing_fires_when_the_map_records_no_shape_at_all.json (+13 more) |
| `paddy_basins_are_worth_their_bund` | **FIRES** | `scripted-fixture` paddy_basins_are_worth_their_bund_fires_on_the_pre_floor_mizuguchi.json; `scripted-fixture` paddy_basins_are_worth_their_bund_fires_on_the_pre_floor_sawada.json |
| `paddy_bunds_clear_the_collector` | **FIRES** | `scripted-fixture` paddy_bunds_clear_the_supply_channels_fires_on_edge_crossing_sawada.json |
| `paddy_bunds_clear_the_supply_channels` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` paddy_bunds_clear_the_supply_channels_fires_on_edge_crossing_sawada.json; `scripted-fixture` paddy_bunds_clear_the_supply_channels_fires_on_the_pre_fix_inashiro.json |
| `paddy_bunds_do_not_stagger` | **FIRES** | `scripted-fixture` byre_form_declared_fires_when_a_map_draws_byres_and_names_no_form.json; `scripted-fixture` cluster_shape_matches_the_drawing_fires_when_the_map_records_no_shape_at_all.json; `scripted-fixture` farmhouses_reach_a_way_fires_on_inashiro_before_the_lane_web.json; `scripted-fixture` farmhouses_reach_a_way_fires_on_kashikawa_before_the_lane_web.json (+14 more) |
| `paddy_plot_rings_overcount_stays_marginal` | **FIRES** | `scripted-fixture` drainage_discharges_downhill_fires_on_cohort_seed_2s_uphill_brook.json |
| `paddy_plot_seams_shared` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` comb_floor_ends_at_the_collector_fires_on_the_se_needle_mizuguchi.json; `scripted-fixture` comb_supply_commands_both_flanks_fires_on_the_pre_fix_inashiro.json (+14 more) |
| `paddy_plots_are_workable_basins` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` comb_floor_ends_at_the_collector_fires_on_the_se_needle_mizuguchi.json; `scripted-fixture` comb_supply_commands_both_flanks_fires_on_the_pre_fix_inashiro.json (+18 more) |
| `settlement_records_cluster_seeding` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` comb_floor_ends_at_the_collector_fires_on_the_se_needle_mizuguchi.json; `scripted-fixture` comb_supply_commands_both_flanks_fires_on_the_pre_fix_inashiro.json (+3 more) |
| `tree_crowns_not_subsumed` | **FIRES** | `hand-fixture` ways_clear_of_paddies_and_marsh_fires_on_the_pre_fix_inashiro.json; `hand-fixture` wells_off_the_wet_toe_fires_on_akagaharas_well_in_the_reeds.json; `scripted-fixture` all_ink_is_ruled_on_fires_on_an_unruled_element.json; `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json (+43 more) |
| `village_groves_visibly_stocked` | **FIRES** | `scripted-fixture` captions_clear_the_ways_they_stand_on_fires_when_a_caption_notches_its_lane.json |
| `village_windbreak_is_continuous` | **FIRES** | `scripted-fixture` farmhouses_reach_a_way_fires_on_kashikawa_before_the_lane_web.json; `scripted-fixture` farmhouses_shed_separately_fires_on_the_pre_rule_mizuguchi.json; `scripted-fixture` lane_ends_front_different_houses_fires_on_kashikawa_crows_foot.json; `scripted-fixture` village_windbreak_is_continuous_fires_on_a_gapped_belt.json |
| `woodland_commons_on_dry_ground` | **FIRES** | `scripted-fixture` comb_floor_ends_at_the_collector_fires_on_the_se_needle_mizuguchi.json; `scripted-fixture` paddy_bunds_clear_the_supply_channels_fires_on_edge_crossing_sawada.json; `scripted-fixture` woodland_commons_on_dry_ground_fires_on_the_marsh_seated_parcel_inashiro.json; `scripted-fixture` woodland_commons_on_dry_ground_fires_on_the_marsh_seated_parcel_sawada.json |
| `woodland_commons_visibly_stocked` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` comb_floor_ends_at_the_collector_fires_on_the_se_needle_mizuguchi.json; `scripted-fixture` comb_supply_commands_both_flanks_fires_on_the_pre_fix_inashiro.json (+10 more) |
| `woodland_commons_within_the_frame` | **FIRES** | `scripted-fixture` bund_beans_on_bunds_fires_on_the_pre_fix_inashiro.json; `scripted-fixture` bund_beans_on_bunds_fires_on_water_buried_beads_inashiro.json; `scripted-fixture` comb_floor_ends_at_the_collector_fires_on_the_se_needle_mizuguchi.json; `scripted-fixture` comb_supply_commands_both_flanks_fires_on_the_pre_fix_inashiro.json (+4 more) |
| `canopy_clear_of_watercourses` | **FIRES-HAND-ONLY** | `hand-fixture` canopy_clear_of_watercourses_fires_on_a_clump_in_the_stream.json |
| `channels_flow_downhill` | **FIRES-HAND-ONLY** | `hand-fixture` channels_flow_downhill_fires_when_channel_runs_uphill.json |
| `channels_join_not_cross_at_fork` | **FIRES-HAND-ONLY** | `hand-fixture` channels_join_not_cross_at_fork_fires_on_a_delivery_at_the_division.json |
| `channels_join_streams_at_confluence` | **FIRES-HAND-ONLY** | `hand-fixture` channels_flow_downhill_fires_when_channel_runs_uphill.json; `hand-fixture` channels_join_streams_at_confluence_fires_when_the_intake_starts_short.json; `hand-fixture` channels_join_streams_at_confluence_fires_when_the_mouth_dies_short.json |
| `delivery_ditches_taper` | **FIRES-HAND-ONLY** | `hand-fixture` delivery_ditches_taper_fires_on_a_blunt_ditch.json |
| `drain_flows_downhill` | **FIRES-HAND-ONLY** | `hand-fixture` drain_flows_downhill_fires_when_outfall_is_uphill.json |
| `drain_runs_cross_slope` | **FIRES-HAND-ONLY** | `hand-fixture` drain_flows_downhill_fires_when_outfall_is_uphill.json; `hand-fixture` drain_runs_cross_slope_fires_when_it_runs_downhill.json; `hand-fixture` drainage_discharges_downhill_fires_when_the_brook_runs_uphill.json |
| `dry_plots_clear_of_paddies` | **FIRES-HAND-ONLY** | `hand-fixture` dry_plots_clear_of_paddies_fires_on_a_hem_plot_in_the_rice.json |
| `field_ditch_tips_land_on_the_trunk` | **FIRES-HAND-ONLY** | `hand-fixture` field_ditch_tips_land_on_the_trunk_fires_on_a_tip_past_the_canal.json; `hand-fixture` polder_channels_clear_of_dike_fires_on_a_canal_in_the_dike.json; `hand-fixture` polder_floor_is_ring_interior_fires_on_an_envelope_floor.json; `hand-fixture` water_channels_cross_the_polder_ring_enokida.json |
| `field_ditches_reach_source_and_sink` | **FIRES-HAND-ONLY** | `hand-fixture` channels_join_not_cross_at_fork_fires_on_a_delivery_at_the_division.json; `hand-fixture` delivery_ditches_taper_fires_on_a_blunt_ditch.json; `hand-fixture` drain_runs_cross_slope_fires_when_it_runs_downhill.json; `hand-fixture` field_ditch_tips_land_on_the_trunk_fires_on_a_tip_past_the_canal.json (+7 more) |
| `fields_clear_of_road` | **FIRES-HAND-ONLY** | `hand-fixture` fields_clear_of_road_fires.json; `hand-fixture` ways_clear_of_paddies_and_marsh_fires_on_the_pre_fix_inashiro.json |
| `fields_show_water_source` | **FIRES-HAND-ONLY** | `hand-fixture` dry_plots_clear_of_paddies_fires_on_a_hem_plot_in_the_rice.json; `hand-fixture` field_ditch_tips_land_on_the_trunk_fires_on_a_tip_past_the_canal.json; `hand-fixture` fields_clear_of_road_fires.json; `hand-fixture` fields_show_water_source_branches.json (+8 more) |
| `funerary_clear_of_fields` | **FIRES-HAND-ONLY** | `hand-fixture` funerary_clear_of_fields_fires_when_a_cremation_ground_sits_on_a_field.json |
| `groves_clear_of_lanes` | **FIRES-HAND-ONLY** | `hand-fixture` groves_clear_of_lanes_fires_when_a_copse_sits_on_a_lane.json; `hand-fixture` groves_clear_of_lanes_fires_when_a_per_house_grove_sits_on_a_road.json |
| `hamlet_has_kosatsuba` | **FIRES-HAND-ONLY** | `hand-fixture` dikepond_and_polder_wander_gaps_fire_on_prefix_kuwabata.json; `hand-fixture` field_ditch_tips_land_on_the_trunk_fires_on_a_tip_past_the_canal.json; `hand-fixture` hamlet_has_no_headman_fires_when_a_hamlet_has_one.json; `hand-fixture` marsh_on_low_ground_exempts_the_waterside_fringe.json (+16 more) |
| `hamlet_has_no_headman` | **FIRES-HAND-ONLY** | `hand-fixture` hamlet_has_no_headman_fires_when_a_hamlet_has_one.json |
| `houses_clear_of_lanes` | **FIRES-HAND-ONLY** | `hand-fixture` houses_clear_of_lanes_fires_when_a_house_sits_on_the_tread.json |
| `irrigation_channels_hairline` | **FIRES-HAND-ONLY** | `hand-fixture` irrigation_channels_hairline_fires_on_a_fat_ditch.json; `hand-fixture` irrigation_channels_hairline_still_fires_on_a_fat_drain_culvert.json |
| `label_hugs_its_referent` | **FIRES-HAND-ONLY** | `hand-fixture` label_hugs_its_referent_fires_on_a_caption_adrift_in_empty_ground.json |
| `labels_within_image` | **FIRES-HAND-ONLY** | `hand-fixture` labels_within_image_fires_when_a_label_runs_off_the_edge.json; `hand-fixture` labels_within_image_uses_the_cropped_view.json |
| `map_frame_hugs_its_content` | **FIRES-HAND-ONLY** | `hand-fixture` labels_within_image_uses_the_cropped_view.json |
| `margins_form_continuous_ring` | **FIRES-HAND-ONLY** | `hand-fixture` canopy_clear_of_watercourses_fires_on_a_clump_in_the_stream.json; `hand-fixture` channels_flow_downhill_fires_when_channel_runs_uphill.json; `hand-fixture` channels_join_not_cross_at_fork_fires_on_a_delivery_at_the_division.json; `hand-fixture` channels_join_streams_at_confluence_fires_when_the_intake_starts_short.json (+45 more) |
| `marsh_on_low_ground` | **FIRES-HAND-ONLY** | `hand-fixture` marsh_on_low_ground_exempts_the_waterside_fringe.json |
| `no_caption_holds_the_frame_open` | **FIRES-HAND-ONLY** | `hand-fixture` village_windbreak_scales_with_cluster_fires_on_moritono_sparse_belt.json |
| `no_farmhouse_stands_on_a_lane` | **FIRES-HAND-ONLY** | `hand-fixture` houses_clear_of_lanes_fires_when_a_house_sits_on_the_tread.json |
| `no_label_overlaps` | **FIRES-HAND-ONLY** | `hand-fixture` no_label_overlaps_fires_when_glyphs_cross.json |
| `no_structure_on_paddy` | **FIRES-HAND-ONLY** | `hand-fixture` funerary_clear_of_fields_fires_when_a_cremation_ground_sits_on_a_field.json; `hand-fixture` no_structure_on_paddy_fires_when_a_farmhouse_sinks_a_corner_into_the_crop.json |
| `paddy_fan_has_floor` | **FIRES-HAND-ONLY** | `hand-fixture` field_ditch_tips_land_on_the_trunk_fires_on_a_tip_past_the_canal.json; `hand-fixture` polder_dike_gapped_at_sluices.json; `hand-fixture` polder_dike_is_earthwork_fires_on_a_ruled_uniform_dike.json; `hand-fixture` watercourse_ends_reach_water_fires_on_a_dangling_main_canal.json (+1 more) |
| `polder_channels_clear_of_dike` | **FIRES-HAND-ONLY** | `hand-fixture` polder_channels_clear_of_dike.json; `hand-fixture` polder_channels_clear_of_dike_fires_on_a_canal_in_the_dike.json; `hand-fixture` polder_floor_is_ring_interior.json |
| `polder_dike_gapped_at_sluices` | **FIRES-HAND-ONLY** | `hand-fixture` dikepond_and_polder_wander_gaps_fire_on_prefix_kuwabata.json; `hand-fixture` polder_channels_clear_of_dike_fires_on_a_canal_in_the_dike.json; `hand-fixture` polder_dike_gapped_at_sluices.json; `hand-fixture` polder_floor_is_ring_interior.json (+2 more) |
| `polder_dike_is_earthwork` | **FIRES-HAND-ONLY** | `hand-fixture` polder_dike_is_earthwork.json; `hand-fixture` polder_dike_is_earthwork_fires_on_a_ruled_uniform_dike.json; `hand-fixture` polder_field_must_fill_its_bbox.json |
| `polder_edges_wander` | **FIRES-HAND-ONLY** | `hand-fixture` dikepond_and_polder_wander_gaps_fire_on_prefix_kuwabata.json; `hand-fixture` polder_channels_clear_of_dike.json; `hand-fixture` polder_channels_clear_of_dike_fires_on_a_canal_in_the_dike.json; `hand-fixture` polder_dike_gapped_at_sluices.json (+7 more) |
| `polder_fills_its_bbox` | **FIRES-HAND-ONLY** | `hand-fixture` polder_field_must_fill_its_bbox.json |
| `polder_floor_is_ring_interior` | **FIRES-HAND-ONLY** | `hand-fixture` dikepond_and_polder_wander_gaps_fire_on_prefix_kuwabata.json; `hand-fixture` polder_floor_is_ring_interior.json; `hand-fixture` polder_floor_is_ring_interior_fires_on_an_envelope_floor.json; `hand-fixture` polder_wander_and_sluice_gaps_fire_on_prefix_enokida.json (+1 more) |
| `pond_clear_of_field` | **FIRES-HAND-ONLY** | `hand-fixture` pond_clear_of_field_fires_when_the_pond_sits_on_the_paddies.json |
| `pond_clear_of_paddies` | **FIRES-HAND-ONLY** | `hand-fixture` fields_show_water_source_branches.json; `hand-fixture` pond_clear_of_field_fires_when_the_pond_sits_on_the_paddies.json; `hand-fixture` pond_clear_of_paddies_fires_when_the_pond_laps_the_crop.json |
| `pond_connected_to_field` | **FIRES-HAND-ONLY** | `hand-fixture` fields_show_water_source_branches.json; `hand-fixture` pond_clear_of_paddies_fires_when_the_pond_laps_the_crop.json; `hand-fixture` pond_connected_to_field_fires_when_a_drainage_pond_drain_stops_short.json; `hand-fixture` pond_fed_from_edge_fires_when_the_feeder_starts_mid_map.json |
| `pond_fed_from_edge` | **FIRES-HAND-ONLY** | `hand-fixture` pond_fed_from_edge_fires_when_the_feeder_starts_mid_map.json |
| `pond_fill_covers_channel_mouths` | **FIRES-HAND-ONLY** | `hand-fixture` dikepond_and_polder_wander_gaps_fire_on_prefix_kuwabata.json; `hand-fixture` polder_wander_and_sluice_gaps_fire_on_prefix_enokida.json; `hand-fixture` pond_fed_from_edge_fires_when_the_feeder_starts_mid_map.json; `hand-fixture` structures_clear_of_dike_fires_on_a_house_on_the_dike.json |
| `roads_clear_of_marsh` | **FIRES-HAND-ONLY** | `hand-fixture` roads_clear_of_marsh_fires_when_the_road_runs_through_a_reed_fringe.json; `hand-fixture` village_windbreak_scales_with_cluster_fires_on_moritono_sparse_belt.json; `hand-fixture` ways_clear_of_paddies_and_marsh_fires_on_the_pre_fix_inashiro.json |
| `settlement_declares_a_land_fall` | **FIRES-HAND-ONLY** | `hand-fixture` channels_join_not_cross_at_fork_fires_on_a_delivery_at_the_division.json; `hand-fixture` delivery_ditches_taper_fires_on_a_blunt_ditch.json; `hand-fixture` drainage_junction_smooth_fires_on_a_hard_corner.json; `hand-fixture` dry_plots_clear_of_paddies_fires_on_a_hem_plot_in_the_rice.json (+17 more) |
| `settlement_dwellings_watered` | **FIRES-HAND-ONLY** | `hand-fixture` hamlet_has_no_headman_fires_when_a_hamlet_has_one.json; `hand-fixture` houses_clear_of_lanes_fires_when_a_house_sits_on_the_tread.json; `hand-fixture` no_structure_on_paddy_fires_when_a_farmhouse_sinks_a_corner_into_the_crop.json; `hand-fixture` structures_clear_of_dike.json |
| `settlement_has_wells` | **FIRES-HAND-ONLY** | `hand-fixture` hamlet_has_no_headman_fires_when_a_hamlet_has_one.json; `hand-fixture` houses_clear_of_lanes_fires_when_a_house_sits_on_the_tread.json; `hand-fixture` no_structure_on_paddy_fires_when_a_farmhouse_sinks_a_corner_into_the_crop.json; `hand-fixture` structures_clear_of_dike.json |
| `streams_avoid_fields` | **FIRES-HAND-ONLY** | `hand-fixture` streams_avoid_fields_fires.json; `hand-fixture` streams_avoid_fields_still_fires_when_a_drain_brook_reenters_the_field.json |
| `structures_clear_of_dike` | **FIRES-HAND-ONLY** | `hand-fixture` polder_channels_clear_of_dike_fires_on_a_canal_in_the_dike.json; `hand-fixture` structures_clear_of_dike.json; `hand-fixture` structures_clear_of_dike_fires_on_a_house_on_the_dike.json |
| `village_has_kosatsuba` | **FIRES-HAND-ONLY** | `hand-fixture` canopy_clear_of_watercourses_fires_on_a_clump_in_the_stream.json; `hand-fixture` channels_flow_downhill_fires_when_channel_runs_uphill.json; `hand-fixture` channels_join_not_cross_at_fork_fires_on_a_delivery_at_the_division.json; `hand-fixture` channels_join_streams_at_confluence_fires_when_the_intake_starts_short.json (+31 more) |
| `village_windbreak_embraces_cluster` | **FIRES-HAND-ONLY** | `hand-fixture` village_windbreak_scales_with_cluster_fires_on_moritono_sparse_belt.json |
| `village_windbreak_scales_with_cluster` | **FIRES-HAND-ONLY** | `hand-fixture` village_windbreak_scales_with_cluster_fires_on_moritono_sparse_belt.json |
| `water_channels_join_not_cross` | **FIRES-HAND-ONLY** | `hand-fixture` water_channels_cross_the_polder_ring_enokida.json; `hand-fixture` water_channels_join_not_cross_fires_on_a_stub_through_the_trunk.json |
| `water_channels_obtuse_turns` | **FIRES-HAND-ONLY** | `hand-fixture` streams_avoid_fields_still_fires_when_a_drain_brook_reenters_the_field.json |
| `watercourse_ends_reach_water` | **FIRES-HAND-ONLY** | `hand-fixture` channels_join_not_cross_at_fork_fires_on_a_delivery_at_the_division.json; `hand-fixture` drain_flows_downhill_fires_when_outfall_is_uphill.json; `hand-fixture` drain_runs_cross_slope_fires_when_it_runs_downhill.json; `hand-fixture` drainage_discharges_downhill_fires_when_the_brook_runs_uphill.json (+7 more) |
| `watercourses_wider_than_ditches` | **FIRES-HAND-ONLY** | `hand-fixture` watercourses_wider_than_ditches_fires_when_a_creek_reads_like_a_ditch.json |
| `wells_off_the_wet_toe` | **FIRES-HAND-ONLY** | `hand-fixture` wells_off_the_wet_toe_fires_on_akagaharas_well_in_the_reeds.json |
