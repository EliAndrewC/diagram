# T14/T15 - the measurement ledger, for the GM's case-by-case discussion

**This ledger decides nothing.** Every row carries the measurement and the fact that points at one
of the GM's two readings; the ruling is the GM's, check by check. Built by joining
`make check-census` (which stage last changes each input) with `make firing-census` (what can still
make it fail) - see `build_ledger.py`.

147 live checks. The discriminator is the one the GM set in feature 141: **can any stage
after the placer change what this check reads?**

| reading | n | what it means |
|---|---|---|
| **placer bug** | 11 | nothing after the placer can move its inputs, so a failure means the placer produced it wrong. Disposition: a unit test of the placer, not a per-map audit. |
| **fold into a trial-and-error placer** | 116 | a later stage can undo the placer, so no unit test of the placer can carry the guarantee. Disposition: an accept condition inside the loop - `farmhouses_reach_a_way` is the worked precedent. |
| **neither** | 20 | the measurement supports neither reading; recorded as an observation. |

## placer bug (11)

| check | still made to fail by | the measurement |
|---|---|---|
| `bridges_span_their_water` | `test` | every input settles at the stage that placed it (polder19: placed crossings, last changed crossings; reference: placed crossings, last changed crossings) - nothing after the placer can move it |
| `caption_stands_beside_its_referent` | `scripted-fixture`, `test` | every input settles at the stage that placed it (polder19: placed labels, last changed labels; reference: placed labels, last changed labels) - nothing after the placer can move it |
| `channel_gates_at_water_junctions` | `test` | every input settles at the stage that placed it (polder19: placed crossings, last changed crossings; reference: placed field, last changed sink) - nothing after the placer can move it |
| `footbridges_reach_useful_ground` | `test` | every input settles at the stage that placed it (polder19: placed crossings, last changed crossings; reference: placed crossings, last changed crossings) - nothing after the placer can move it |
| `label_hugs_its_referent` | `hand-fixture`, `test` | every input settles at the stage that placed it (polder19: placed labels, last changed labels; reference: placed labels, last changed labels) - nothing after the placer can move it |
| `labels_align_with_their_referent` | `scripted-fixture`, `test` | every input settles at the stage that placed it (polder19: placed labels, last changed labels; reference: placed labels, last changed labels) - nothing after the placer can move it |
| `labels_within_image` | `hand-fixture`, `test` | every input settles at the stage that placed it (polder19: placed labels, last changed labels; reference: placed labels, last changed labels) - nothing after the placer can move it |
| `long_ditches_have_a_footbridge` | `scripted-fixture`, `test` | every input settles at the stage that placed it (polder19: placed crossings, last changed crossings; reference: placed crossings, last changed crossings) - nothing after the placer can move it |
| `no_caption_holds_the_frame_open` | `hand-fixture`, `test` | every input settles at the stage that placed it (polder19: placed labels, last changed labels; reference: placed labels, last changed labels) - nothing after the placer can move it |
| `no_label_overlaps` | `hand-fixture`, `test` | every input settles at the stage that placed it (polder19: placed labels, last changed labels; reference: placed labels, last changed labels) - nothing after the placer can move it |
| `wells_among_dwellings` | `test` | every input settles at the stage that placed it (polder19: placed appurtenances, last changed appurtenances; reference: placed appurtenances, last changed appurtenances) - nothing after the placer can move it |

## fold into a trial-and-error placer (116)

| check | still made to fail by | the measurement |
|---|---|---|
| `all_ink_is_ruled_on` | `scripted-fixture`, `test` | check-census reads its inputs as absent on both scripted maps, but the firing census has it FIRING (FIRES) - the inputs are empty because a correct map has nothing to report, which is what PASSING looks like |
| `aqueduct_taps_water_lands_dry` | `test` | an input changes after its placer (polder19: placed crossings, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `bamboo_stands_clear_of_paddies` | `test` | an input changes after its placer (polder19: placed bamboo, last changed finish; reference: placed bamboo, last changed finish) - the placer cannot guarantee the finished state |
| `bund_beans_on_bunds` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed sink, last changed finish) - the placer cannot guarantee the finished state |
| `byre_form_declared` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed notice; reference: placed appurtenances, last changed notice) - the placer cannot guarantee the finished state |
| `byres_meet_their_target` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed notice; reference: placed appurtenances, last changed notice) - the placer cannot guarantee the finished state |
| `canopy_clear_of_watercourses` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `captions_clear_the_ways_they_stand_on` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed labels, last changed finish; reference: placed labels, last changed finish) - the placer cannot guarantee the finished state |
| `channels_flow_downhill` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `channels_join_not_cross_at_fork` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `channels_join_streams_at_confluence` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `channels_join_water_not_cross` | `test` | an input changes after its placer (polder19: placed field, last changed field; reference: placed field, last changed sink) - the placer cannot guarantee the finished state |
| `city_streets_reach_their_neighbors` | `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `cluster_shape_matches_the_drawing` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed homesteads, last changed notice; reference: placed homesteads, last changed notice) - the placer cannot guarantee the finished state |
| `comb_floor_ends_at_the_collector` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed notice; reference: placed field, last changed notice) - the placer cannot guarantee the finished state |
| `comb_supply_commands_both_flanks` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `commons_clear_of_paddies` | `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `copse_stands_clear_of_the_belt` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed notice; reference: placed windbreak, last changed notice) - the placer cannot guarantee the finished state |
| `delivery_ditches_taper` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `drain_flows_downhill` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `drain_runs_cross_slope` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `drainage_discharges_downhill` | `hand-fixture`, `scripted-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `drainage_junction_smooth` | `hand-fixture`, `scripted-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `dry_plot_furrows_vary` | `hand-fixture`, `scripted-fixture`, `test` | an input changes after its placer (polder19: placed water_frame, last changed notice; reference: placed field, last changed notice) - the placer cannot guarantee the finished state |
| `dry_plots_clear_of_paddies` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `farmhouses_reach_a_way` | `scripted-fixture`, `test` | a generator ALREADY branches on this verdict: l7r/diagram/hamletgen/driver.py - it is an accept condition today, not an audit |
| `farmhouses_shed_separately` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed homesteads, last changed notice; reference: placed homesteads, last changed notice) - the placer cannot guarantee the finished state |
| `field_ditch_tips_land_on_the_trunk` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `field_ditches_reach_source_and_sink` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `field_ditches_terminate` | `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `field_ponds_sunk_into_one_plot` | `hand-fixture`, `scripted-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `fields_clear_of_road` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `fields_show_water_source` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `flooded_plots_read_as_basins` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed notice; reference: placed field, last changed notice) - the placer cannot guarantee the finished state |
| `funerary_clear_of_fields` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `gardens_clear_of_channels` | `test` | an input changes after its placer (polder19: placed homesteads, last changed finish; reference: placed homesteads, last changed finish) - the placer cannot guarantee the finished state |
| `groves_clear_of_lanes` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `hamlet_has_kosatsuba` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed notice, last changed finish; reference: placed notice, last changed finish) - the placer cannot guarantee the finished state |
| `houses_clear_of_lanes` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `inwall_drains_gated_at_cutoff` | `test` | an input changes after its placer (polder19: placed crossings, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `irrigation_channels_hairline` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed field; reference: placed field, last changed sink) - the placer cannot guarantee the finished state |
| `kosatsuba_by_the_road` | `hand-fixture`, `scripted-fixture`, `test` | an input changes after its placer (polder19: placed notice, last changed finish; reference: placed notice, last changed finish) - the placer cannot guarantee the finished state |
| `kosatsuba_faces_the_road` | `test` | an input changes after its placer (polder19: placed notice, last changed finish; reference: placed notice, last changed finish) - the placer cannot guarantee the finished state |
| `lane_ends_front_different_houses` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `lanes_bend_like_paths` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `lanes_clear_of_dry_plots` | `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `lanes_do_not_break_mid_run` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `lanes_form_one_network` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `lanes_reach_something` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `margins_form_continuous_ring` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `marsh_on_low_ground` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed sink, last changed finish) - the placer cannot guarantee the finished state |
| `no_farmhouse_stands_on_a_lane` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `no_structure_on_paddy` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `no_structure_on_stream` | `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `no_structure_on_torii` | `test` | an input changes after its placer (polder19: placed water_frame, last changed notice; reference: placed water_frame, last changed notice) - the placer cannot guarantee the finished state |
| `paddy_basins_are_worth_their_bund` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed water_frame, last changed notice; reference: placed water_frame, last changed notice) - the placer cannot guarantee the finished state |
| `paddy_bunds_clear_the_collector` | `scripted-fixture` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `paddy_bunds_clear_the_supply_channels` | `scripted-fixture`, `test` | a generator ALREADY branches on this verdict: l7r/diagram/hamletgen/driver.py - it is an accept condition today, not an audit |
| `paddy_bunds_do_not_stagger` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed water_frame, last changed notice; reference: placed water_frame, last changed notice) - the placer cannot guarantee the finished state |
| `paddy_fan_has_floor` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `paddy_plot_rings_overcount_stays_marginal` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed water_frame, last changed notice; reference: placed water_frame, last changed notice) - the placer cannot guarantee the finished state |
| `paddy_plot_seams_shared` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `paddy_plots_are_workable_basins` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed water_frame, last changed notice; reference: placed water_frame, last changed notice) - the placer cannot guarantee the finished state |
| `polder_channels_clear_of_dike` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `polder_dike_gapped_at_sluices` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `polder_dike_is_earthwork` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `polder_edges_wander` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `polder_floor_is_ring_interior` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `pond_clear_of_field` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `pond_clear_of_paddies` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `pond_connected_to_field` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `pond_fed_from_edge` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `pond_fill_covers_channel_mouths` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed sink, last changed finish) - the placer cannot guarantee the finished state |
| `religious_clear_of_ring_and_towers` | `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `remote_shrine_has_own_well` | `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `roads_clear_of_marsh` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `scalebar_matches_declared_scale` | `test` | an input changes after its placer (polder19: placed labels, last changed finish; reference: placed labels, last changed finish) - the placer cannot guarantee the finished state |
| `scatter_respects_swept_clearings` | `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `scrub_clear_of_urban_fabric` | `test` | an input changes after its placer (polder19: placed hinterland, last changed hinterland; reference: placed hinterland, last changed woodland) - the placer cannot guarantee the finished state |
| `settlement_declares_a_land_fall` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `settlement_dwellings_watered` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `settlement_has_wells` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `settlement_records_cluster_seeding` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed water_frame, last changed notice; reference: placed water_frame, last changed notice) - the placer cannot guarantee the finished state |
| `shrine_halls_clear_of_lanes` | `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `sluice_gates_on_water` | `test` | an input changes after its placer (polder19: placed crossings, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `stream_end_anchored` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `stream_source_anchored` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `streams_avoid_fields` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `structures_clear_of_dike` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `structures_clear_of_trees` | `test` | an input changes after its placer (polder19: placed hinterland, last changed finish; reference: placed hinterland, last changed finish) - the placer cannot guarantee the finished state |
| `tanning_yards_on_water` | `test` | an input changes after its placer (polder19: placed crossings, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `title_clear_of_features` | `test` | an input changes after its placer (polder19: placed labels, last changed finish; reference: placed labels, last changed finish) - the placer cannot guarantee the finished state |
| `title_has_placard` | `test` | an input changes after its placer (polder19: placed labels, last changed finish; reference: placed labels, last changed finish) - the placer cannot guarantee the finished state |
| `torii_clear_of_halls_towers_ring` | `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `towpath_hugs_the_bank` | `test` | an input changes after its placer (polder19: placed crossings, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `tree_crowns_not_subsumed` | `hand-fixture`, `scripted-fixture`, `test` | an input changes after its placer (polder19: placed hinterland, last changed windbreak; reference: placed hinterland, last changed windbreak) - the placer cannot guarantee the finished state |
| `village_groves_visibly_stocked` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed notice; reference: placed windbreak, last changed notice) - the placer cannot guarantee the finished state |
| `village_windbreak_embraces_cluster` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed windbreak; reference: placed windbreak, last changed frame) - the placer cannot guarantee the finished state |
| `village_windbreak_is_continuous` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed notice; reference: placed windbreak, last changed notice) - the placer cannot guarantee the finished state |
| `village_windbreak_present` | `test` | an input changes after its placer (polder19: placed windbreak, last changed windbreak; reference: placed windbreak, last changed frame) - the placer cannot guarantee the finished state |
| `village_windbreak_scales_with_cluster` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed windbreak, last changed windbreak; reference: placed windbreak, last changed frame) - the placer cannot guarantee the finished state |
| `water_channels_join_not_cross` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `water_channels_obtuse_turns` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `watercourse_ends_reach_water` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `watercourses_wider_than_ditches` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `waterside_works_follow_the_bank` | `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `waterward_strips_run_off_the_frame` | `nothing` | an input changes after its placer (polder19: placed field, last changed hinterland; reference: placed sink, last changed hinterland) - the placer cannot guarantee the finished state |
| `waterways_merge_at_crossings` | `test` | an input changes after its placer (polder19: placed field, last changed finish; reference: placed field, last changed finish) - the placer cannot guarantee the finished state |
| `ways_clear_of_castle_moat` | `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `ways_cross_water_on_a_deck` | `test` | an input changes after its placer (polder19: placed crossings, last changed finish; reference: placed crossings, last changed finish) - the placer cannot guarantee the finished state |
| `ways_not_inside_road_beds` | `test` | an input changes after its placer (polder19: placed track, last changed finish; reference: placed track, last changed finish) - the placer cannot guarantee the finished state |
| `wells_clear_of_trees` | `test` | an input changes after its placer (polder19: placed windbreak, last changed finish; reference: placed windbreak, last changed finish) - the placer cannot guarantee the finished state |
| `wells_off_the_wet_toe` | `hand-fixture`, `test` | an input changes after its placer (polder19: placed appurtenances, last changed finish; reference: placed appurtenances, last changed finish) - the placer cannot guarantee the finished state |
| `woodland_commons_on_dry_ground` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed hinterland, last changed notice; reference: placed hinterland, last changed notice) - the placer cannot guarantee the finished state |
| `woodland_commons_visibly_stocked` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed hinterland, last changed notice; reference: placed hinterland, last changed notice) - the placer cannot guarantee the finished state |
| `woodland_commons_within_the_frame` | `scripted-fixture`, `test` | an input changes after its placer (polder19: placed hinterland, last changed notice; reference: placed hinterland, last changed notice) - the placer cannot guarantee the finished state |

## neither (20)

| check | still made to fail by | the measurement |
|---|---|---|
| `city_has_kosatsuba` | `test` | no scripted map runs it - a tier this engine cannot yet produce. Not a deletion candidate under the GM's 2026-08-30 ruling; a class for the discussion |
| `cluster_abuts_fields` | `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `crop_not_held_open_by_one_feature` | `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `every_feature_classified_for_matrix` | `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `every_feature_classified_for_overlap` | `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `every_solid_feature_classified_for_labels` | `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `farmhouse_aspect_in_range` | `nothing` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `farmhouse_sizes_vary` | `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `features_do_not_overlap` | `hand-fixture`, `scripted-fixture`, `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `hamlet_has_no_headman` | `hand-fixture`, `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `households_consistent` | `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `houses_face_south` | `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `map_frame_hugs_its_content` | `hand-fixture`, `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `matrix_debts_still_owed` | `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `polder_fills_its_bbox` | `hand-fixture`, `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `torii_clear_of_walls` | `test` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `town_has_kosatsuba` | `test` | no scripted map runs it - a tier this engine cannot yet produce. Not a deletion candidate under the GM's 2026-08-30 ruling; a class for the discussion |
| `village_has_kosatsuba` | `hand-fixture`, `test` | no scripted map runs it - a tier this engine cannot yet produce. Not a deletion candidate under the GM's 2026-08-30 ruling; a class for the discussion |
| `waivers_are_documented` | `nothing` | reads no manifest key the census can see (derived entirely) - judge by hand |
| `waivers_are_live` | `nothing` | reads no manifest key the census can see (derived entirely) - judge by hand |
