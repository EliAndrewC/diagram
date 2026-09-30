# Research - feature 287, the placer guarantees

## R1 - The census: which finished-map rules does a placer not guarantee? (2026-09-29)

**Method** (observed 2026-09-29, method: every test under `tests/` whose body reads a rolled or pool map, or that lives in
`tests/gate/`, `tests/full/`, `tests/soak/` or a `tests/hamletgen/test_pool_*.py` file - 195 tests, listed in `census-raw.txt` -
read by five Opus readers, each test with its fixtures and the engine code that places what it checks, and classified;
the rows are `census.json`). Of the 195: 72 are mechanics (tooling, the page, the pipeline, the driver's loop), 3 pin one
map's values, 2 already test a placer on constructed inputs, and 118 assert a placement rule on a finished map. Of those
118, the placer that makes the feature already makes a violation impossible for 31; for 53 it guards some cases and not
others; for 34 nothing in the placer prevents a violation. Those 87 are this feature's scope, grouped below by the
placer the census names as the owner (the last placer whose decision can break the rule).

| owner | test | the rule | now | sketch (observed 2026-09-29, method: the census readers, `census.json`) |
|---|---|---|---|---|
| `hamletgen/water/brook.py` | `test_no_brook_folds_back_on_itself` | No vertex of the brook's drawn course turns it by more than 100 degrees. | partial | In feed_brook, refuse an approach bearing (the 15-swing loop) whose entry into the sluice plus the first skirt leg turns more than the limit, and move on to the next swing. Or run unfold over the whole assembled course while holding the tap vertex. GM 2026-08-26 / FR-017. |
| `hamletgen/water/brook.py` | `test_no_brook_runs_ruled_along_the_frame` | No stretch of brook within 80 ft of the view's edge runs level along that edge (within 4 ft) for more than 150 ft. | no | The frame is decided later (stage_frame, crop_to_content with brook_beside_the_field as extra), so hold the course to the same box the reservation predicts. Break at the first station the box binds, not only after half the stations. Bend or turn any exit leg that runs parallel to, and within 80 ft of, a box edge. Or assert it in stage_frame and widen the crop. GM 2026-08-26 (Sawada: 'makes it look like a mistake'). |
| `hamletgen/water/brook.py` | `test_no_brook_runs_ruled_for_most_of_its_course_on_the_page` | No straight run of the brook (every vertex within 3.1 ft of the chord) covers more than 40% of its in-view length (when that length is 300 ft or more). | no | Measure the straightest run of the course inside the predicted frame box before returning. Where it exceeds 40%, add bends (exit_bend on the offending legs, or more lateral wander where the crop floor does not bind) until it does not. Settlement-review of Sawada (round 0ae309f0); GM 2026-08-26 on ruled courses. |
| `hamletgen/water/brook.py` | `test_no_brook_segment_lies_on_a_screen_axis_but_the_tap_run` | No brook segment of 10 ft or longer (other than the two tap-run segments) lies within 1.6 degrees of a screen axis. | partial | Apply _off_the_axes AFTER unfold and iterate the pair until both hold. Include the approach's last leg into the sluice while holding the sluice point (nudge the leg's start). GM 2026-08-26. |
| `hamletgen/water/brook.py` | `test_no_stream_runs_through_a_field` | No stream's interior vertex may lie inside a field outline. | partial | The approach is tested on its chord BEFORE the +-16 px wobble and _off_the_axes nudges are applied; the tap run (BROOK_TAP_RUN) is deliberately not floored ('crop at the fan's head yields'); unfold() and round_the_brooks move points after the floor. Re-test the final course against the envelope and refuse/re-route. |
| `hamletgen/water/brook.py` | `test_every_stream_end_is_anchored_to_what_it_declares` | A stream end declared off-map must lie off the canvas; one declared to a pond must lie on it. | no | The brook's frm=offmap start is a fixed `run` = 420 px from the sluice on a bearing up to 70 deg off upslope, while the sluice is placed 0.36*min(W,H) from the center (fit.py:head_sluice); nothing checks the start is past the canvas edge. Derive the run from the distance to the canvas edge along the bearing (as stage_sink already does for the off-map drain). |
| `hamletgen/water/brook.py` | `test_no_watercourse_crosses_another_mid_run` | No channel or field ditch may cross a stream except at its own end (a confluence). | partial | No placer asks the crossing question: ditches that run outside the envelope (delivery tails, the collector's ends) and stage_sink's off-map drain run are never tested against the brook. Add a stream-crossing refusal to stage_sink's route search and to brook_skirt's profile (the ditch stretches outside the crop). |
| `waterfields/seams/close.py` | `test_no_bund_is_drawn_down_the_middle_of_a_supply_channel` | No paddy bund edge may stand inside a supply canal's or delivery ditch's drawn stroke (halfw + BANK_MARGIN). | partial | Close the unguarded producers in close_seams: _shed_necks (grows a basin by tail.buffer(0.05) with no water test), _absorb (union + simplify(0.05)), _repair_crossing_rings (buffer(0) part) - run the carve's _quad_in_supply on every ring a seam-pass step rewrites and refuse/revert the step. Also _water buffers a segment at its HEAD width only; a widening stroke (w_tail > w) is under-covered - buffer at max(w_i, w_i+1). GM rule 2026-08-15 (bunds abut the water's edge). |
| `waterfields/seams/close.py` | `test_no_bund_is_drawn_across_the_collector` | No plot-ring edge may run across the drain collector (both ends within half the stroke of its centerline). | partial | Make the terminal invariant terminal: hem_to_bank exempts vertices where `lean < 0.2` (drain running with the fall) and `past` (beyond the drain's ends), and it runs BEFORE close_seams, whose welds/trades/necks can re-shape rings. Re-run the drain-bank clearance on rings close_seams rewrites (refuse the step) or move hem_to_bank's check to the end of close_seams. GM 2026-08-08 (hem bunds run with the ditch). |
| `waterfields/seams/close.py` | `test_no_basin_tapers_to_a_point` | No paddy basin ring (as recorded) may have an interior angle under 15 deg. | partial | The toe pass judges only dedup_ring(r, 1.0); a carved ring that no seam step touches is never judged on the RAW ring the gate reads (a sub-pixel edge can hide a raw apex). Add a terminal sweep at the end of close_seams (after _repair_crossing_rings) that sends any plot pointed on either reading to _absorb as a scrap. GM realism ruling 2026-08-17. |
| `waterfields/seams/close.py` | `test_a_flooded_plot_reads_as_a_basin_and_not_as_a_pond` | No plot painted with the flooded tint may be a needle (raw ring under 15 deg). | partial | The re-judge reads the DEDUPED ring while the gate now reads the raw ring; add pointed_ring(raw, 25) to `_wrong` (the carve's own comment says both rings are needed). |
| `waterfields/seams/close.py` | `test_no_basin_is_too_small_to_be_worth_its_own_bund` | No basin may be smaller than _GATE_MIN_AREA (0.20) of the fan's design cell. | partial | _shed_necks shrinks the giving basin (body = largest part after the tail) with no area test, and _repair_crossing_rings keeps the largest part of a buffer(0) with no area test. Add the _GATE_MIN_AREA floor to both (refuse the trade / send the remainder to _absorb). GM 2026-08-17 ('a few very small triangles'). |
| `waterfields/seams/close.py` | `test_no_shipped_hamlet_has_a_basin_tapering_to_a_point` | No basin ring on any shipped hamlet (every field with plot rings, polders included) may taper under 15 deg. | partial | Two holes: (1) carved comb rings untouched by the seam pass are judged only on the deduped ring (toe pass); (2) polder parcels (build_polder/_polder_parcels, clean_polder_parcels, hem_to_bank) have no apex guard at all. Add the raw+dedup apex refusal as a terminal pass in both engines. |
| `hamletgen/homesteads/stages.py` | `test_the_cluster_abuts_the_ground_it_works` | A nucleated cluster must never stand with its nearest house more than 700 px from a field, nor any house more than 700 px + two cluster spans away. | partial | Assert field adjacency on the PLACED position: refuse (or re-rank) any homestead seat whose distance to the field outline exceeds the band's depth, in every round including the lattice ranks; the record gives a 6 ft minimum and a ~700 ft tolerance (research/homesteads.html, 'How close does a farmhouse stand to the paddy?'). |
| `hamletgen/homesteads/stages.py` | `test_a_rolled_cohort_passes_the_whole_gate` | A rolled hamlet must never seat under 85% of its declared households, never land its paddy acreage more than 15% off target, and never strand a farmhouse (baseline_verdict on farmhouses_reach_a_way). | no | Seating: after the seven rounds, re-roll (the driver already re-rolls for reach) or widen the rescue until placed >= ceil(0.85*households) and refuse to return short. Acreage: fit_field keeps the closest carve even when no aspect lands within tolerance (fit.py:89-98) - have plan_site grow the canvas/envelope when every aspect saturates. Reach: generate stops after four re-rolls and keeps the least-bad (driver.py:452-485); the owner is the web (ways/serve.py) which should refuse to leave a seated house unserved. |
| `hamletgen/homesteads/stages.py` | `test_every_declared_household_is_seated` | A hamlet must never seat fewer than 85% of its declared households. | no | stage_homesteads runs a front row, four lattice rounds and three rescue rounds (stages.py:452-557) and then records whatever it got (plan.placed = s.farmsteads(), 641); the docstring says the shortfall is recorded rather than re-rolled. Guarantee it by continuing the rescue (wider band, more guesses) until the quota is met, or by having generate() re-roll a short roll the way it re-rolls a stranding one and refuse to ship under the floor. Research: research/settlements.html 'Is every household in a hamlet actually drawn?'. |
| `hamletgen/homesteads/stages.py` | `test_the_polder_seats_its_households_and_lands_its_acreage` | A polder must never seat under 85% of households or land acreage over 15% off target. | no | As the cohort row: seat to the quota or re-roll; fit_polder grows the block rather than keeping the closest miss. |
| `hamletgen/homesteads/stages.py` | `test_the_cluster_seeds_cloud_still_seats_a_hamlet_when_the_rows_offer_nothing` | With the front row and lane frontage silent, the cluster_seeds cloud must never seat zero households, and it records the rolled shape as honored or unhonored. | no | The rescue offers cluster_seeds candidates for three rounds and stops; if every candidate is refused it seats none. Guarantee by widening the band until at least the quota (or one) seats, or raising so the driver re-rolls. The shape record is unconditional (stages.py:617-621) - mechanics. |
| `hamletgen/ways/web.py` | `test_the_ways_cross_the_brook_only_at_fords_and_never_over_and_back` | No lane record is an empty husk, no lane's end runs on alongside another way, no lane crosses the brook an even number of times (2+), and no crossing stands more than 45 ft from a ford. | partial | Refuse the even-crossing fallback in _join_orphan_ways (leave the orphan to the straggler pass or the re-roll). Make the doubled-tail sweep ask every neighbor regardless of width and run it after the last lane rewrite. Give meet_end_to_end and every late rewrite a water/ford test (the stream_segs list). Check all four as an invariant at the end of stage_web. FR-011; settlement-reviews of Kashikawa and Mizuguchi. |
| `hamletgen/ways/web.py` | `test_no_lane_end_is_served_only_by_the_way_it_left` | No internal lane end reaches nothing (way, house, bund or steading) except the way its own far end stands on. | no | Have _trim_to_service ask end_serves with the test's segment set (the other lanes minus those within _TOUCH_GAP of the lane's own far end), and trim or drop by it. Run it after the last end-moving pass (meet_end_to_end, a_way_onto_the_bund). Keep a lane that is some house's only way by carrying it on to the house rather than exempting it. Settlement-review of Mizuguchi (round 176042d3). |
| `hamletgen/ways/web.py` | `test_every_lane_belongs_to_one_network` | The lanes must never fall into more than one network (every lane end within 4 px of the rest). | no | Make one-network a postcondition of stage_web: after the last pass, compute _components at the ink tolerance and either route a link (as _join_orphan_ways does) or drop the orphan piece (re-rolling if it strands a house), and give every later lane writer (stage_crossings.square_crossings) a keep-connected check like commit_lane's. |
| `hamletgen/ways/web.py` | `test_a_lane_does_not_break_mid_run` | A lane segment longer than 60 px must never run through a house, farm shed or byre. | partial | Give every lane writer one footprint test (commit_lane currently guards only connectivity), and run it on stage_crossings' square_crossings output too. |
| `hamletgen/ways/web.py` | `test_every_shipped_hamlets_lanes_are_one_network_at_the_ink_tolerance` | No shipped hamlet's lanes may form more than one network at the 4 ft ink tolerance (_TOUCH_GAP). | no | Same as the one-network rule: a stage_web postcondition at _TOUCH_GAP (not _LANE_JOIN_FT), with a link-or-drop repair and a keep-connected check on every later lane writer. |
| `hamletgen/water/polder.py` | `test_no_channel_is_cut_through_the_dike_except_at_its_gaps` | No watercourse may cross the dike crest except within 60 px of a recorded gap (sluice or outfall). | partial | Only net['channels'] crossing the INNER ring are gapped: M['channels'] (the reservoir inlet hairline, stage_sink's drain_run) and any course running along the crest without crossing the inner ring get no gap. Compute gaps from every recorded course against the crest band after the water is final, or make later channel routers treat the dike band as a keep-out except at its gaps. |
| `hamletgen/water/polder.py` | `test_the_waterward_reed_strip_runs_off_the_frame` | A waterward reed strip must reach the map's view edge on its flank, never stop inside the frame. | no | The strip's outer edge is the dike's extreme minus WATERWARD_DEPTH (280 px, consts.py), a constant measured to outlast every crop seen so far; the view is decided later by the crop, which ignores the strip. Either clamp the crop so it never extends past a waterward strip's outer edge, or extend the strip to the final view after cropping. GM 2026-08-28 / feature 150 T55. |
| `hamletgen/water/polder.py` | `test_a_polder_reservoir_backs_off_until_its_rim_clears_the_crop` | A polder's header reservoir rim must never lie on the crop, and the reservoir must never sit downhill of the field's highest point. | partial | Raise instead of returning an uncleared pond (or fall back to a different anchor), test the rim as a polygon against the envelope rather than 16 points, and assert the fall projection before accepting. Rule: the source sits above what it waters (research/archetypes polder siting). |
| `hamletgen/water/polder.py` | `test_a_polder_hamlet_draws_its_grid_dike_and_reservoir` | A polder must never miss its perimeter dike, a gate at every dike cut (>=2), its reservoir outside the crop, every household seated, or land acreage over 12% off target. | partial | fit_polder: grow the canvas/block when the tolerance is not met instead of keeping the closest; seating as in the household rows. |
| `hamletgen/ways/serve.py` | `test_a_farmhouse_discharges_one_lane_end_not_three` | No farmhouse may be the terminus of more than two free lane ends (within 80 px). | no | Count free lane ends per house as the web is laid (_lay_web_lane / _serve_stragglers / the sweeps that end a lane at a dooryard) and, when a third end would terminate at the same house, T it into an existing lane there or drop it; grounding is the 0611 ruling (consts.py: 'two lane ends within 60 ft pointing within 25 degrees are a fork serving one steading'). |
| `hamletgen/ways/serve.py` | `test_the_clean_cohort_seeds_bend_like_paths` | A non-connector lane must never turn past 140 degrees, nor make two 50-degree turns within 40 ft of path. | partial | Align _bends_badly with the rule's run-sum predicate, and make the folded fallback a repair (chord or knee the fold) or a refusal that leaves the house to the reach re-roll, never an emitted kink. Rule: research/homesteads.html 'How does a village lane bend?'. |
| `hamletgen/ways/serve.py` | `test_the_polder_s_lanes_bend_like_paths` | A polder lane must never double back past 140 degrees or kink twice within 40 ft. | partial | As the cohort lane row: align the predicate and turn the folded fallback into a repair or a refusal. |
| `hamletgen/ways/serve.py` | `test_seed_43_still_kinks_round_a_house_corner` | A routed footpath must never keep a lattice-step kink round a house corner (strict xfail: seed 43 still does). | no | The router keeps a 36 px lattice step round a house corner that neither chord nor knee can take (feature 166 research R2b). Repair the path post-route by rounding the step into one bend, or refuse the path and re-route to the next junction. Geometry: specs/215-the-floor-itself/census/kink-seed-43.json. |
| `settlement/homestead_parts/stands.py` | `test_a_belt_tree_in_the_marsh_is_alder` | No windbreak clump seated inside a toe or waterside marsh is drawn as anything but alder, and the grove's recorded alder count equals the number of its on-page clumps in the marsh. | partial | Recount `alder` over the on-page clumps when set_view partitions them (core.py:_partition_grove_clumps), or record alder and alder_offpage separately. Test the rounded record points the same way. research/vegetation.html (the marsh margin: alder or willow, never pine). |
| `settlement/homestead_parts/stands.py` | `test_no_tree_is_planted_in_a_path` | No tree trunk may stand on a lane's tread (within its half-width of the centerline). | partial | Either run the lane rewrite in stage_crossings before the woods, or have square_crossings refuse/redirect a leg onto a recorded trunk (tree_crowns) - the same 'reserve before the later stage draws' rule the scatter uses. |
| `settlement/homestead_parts/stands.py` | `test_every_recorded_grove_holds_trees` | A recorded village grove must never hold fewer than 1.5 clumps per 100k sq px of its recorded w x h. | no | Record the grove's extent as the drawn clumps' extent (not the requested footprint), or refuse/re-seat a grove whose clump density falls below the floor after seating. |
| `settlement/homestead_parts/stands.py` | `test_every_pool_belt_keeps_its_depth_across_its_windward_face` | No judged 40 ft stretch of the windbreak may be shallower than 30 ft along the wind; a belt with no judged stretch must stand against the page edge. | no | belt_polygon designs a 110 ft band (BELT_NEAR_FT + BELT_DEPTH_FT, far_envelope) but village_grove thins crowns against structures and sun lanes with no depth floor, and past_the_lanes can shift columns. Guarantee by having village_grove measure depth per bin after its filter and replant behind the thinned stretch (or push that column's band back) until each bin reaches 30 ft. Research: research/vegetation/020 (a belt under ~30 ft reads as a row of blobs). |
| `hamletgen/sink.py` | `test_every_channel_runs_downhill` | Every M['channels'] course's net displacement must run down the fall by at least 20% of its length. | partial | stage_sink holds only weaker bars than the rule: brook_join needs a descent of 20 px over a reach up to 420 (0.05, not 0.2), the off-map route needs descent > 0, and when no route is clean it takes the least-bad one. Put the rule's 0.2 fraction into brook_join's and the off-map route's refusals. The head-race start snap (<= 30 px onto a stream) in _comb_source_channel is also untested against the fraction. |
| `hamletgen/sink.py` | `test_the_runoff_leaves_the_outfall_downhill` | The runoff's continuation (sink pond, drain run, or any brook near the outfall) must lie/run downhill of the outfall. | partial | The off-map loop's least-bad fallback (sink.py ~475) ships a route that failed the descent test; refuse instead (e.g. extend the search or re-seat). The test also judges ANY stream within 60 px of the outfall, including the feed brook routed past the fan by brook_skirt, which no sink logic governs - the brook's direction near the outfall should be asserted by brook_skirt. |
| `hamletgen/sink.py` | `test_no_watercourse_end_dangles_in_bare_ground` | A main or collector end must never stop on the map in bare ground (it must join water, the crop, the pond or leave the frame). | partial | Assert the postcondition where the network is built: after the water stages, check every main/drain end against the same join/crop/frame predicate and extend or clip the end (the comb builder already starts the drain 'inside the field'), refusing the field layout otherwise. |
| `hamletgen/ways/sweeps.py` | `test_every_way_out_crosses_the_brook_at_most_once` | No household's way out (through the lanes and along the connector) crosses the brook more than once. | no | Refuse the over-and-back link where it is made (the _join_orphan_ways fallback). After _link_home_bank, and again after the last lane pass, recompute departure_routes and treat a household with 2+ crossings as unreached, so the driver's re-roll or the straggler pass owns it. Settlement-review of Mizuguchi (feature 261). |
| `hamletgen/ways/sweeps.py` | `test_every_lane_end_reaches_something_worth_walking_to` | No internal lane end may stop in open ground (end_serves: another way, a house/steading, or the worked ground). | partial | Make it the final lane pass and a hard rule: when the pull-back would strand a served house and carry_to_dooryard finds no seat, route the end to the nearest way (as _join_orphan_ways does) instead of restoring the dangling original. |
| `hamletgen/ways/sweeps.py` | `test_every_shipped_hamlets_lane_ends_reach_something` | No shipped hamlet may carry an internal lane end that reaches nothing (end_serves). | partial | As for the reference roll: make the end rule the last lane pass and route rather than restore when a pull-back would strand a house. |
| `labels/placer.py` | `test_the_board_caption_names_the_board_only` | The notice board's drawn caption never lies on a farmhouse roof or within 2 ft of a lane's tread. | partial | Treat a board seat whose caption level is 0 as refused in place_kosatsuba and in the stage_notice re-seat, and let the label phase seat the caption against the index the siter probed with. Or re-site the board in the label phase when place() returns cost > 0. |
| `labels/placer.py` | `test_the_board_caption_stands_nearest_its_own_board` | The board caption never stands nearer another built footprint than its own board. | no | Add a cost term (or a hard refusal for point subjects) when another obstacle's gap to the block is at or below the block's gap to its own subject, so a caption that names a neighbor is never cost-0. The cartographic standard's proximity principle (research/presentation, 'Where does a caption sit'). |
| `labels/placer.py` | `test_no_caption_lies_across_a_way` | A caption's drawn block must never come within 2 px of a lane's tread. | no | Make a way crossing a refusal, not a cost: in place(), skip any candidate whose ObstacleIndex way-cost is non-zero (WAY_NOTCH is already the test's 2 px) and widen the ring/position set (or move to a leader seat) until a way-clear seat exists; only if none exists anywhere in reach, fail loudly rather than draw it. |
| `settlement/city/bridges.py` | `test_every_way_across_the_brook_is_bridged` | No lane crosses the brook without a deck whose own span reaches the crossing point. | partial | Make the dedupe test the same as the check: skip a new deck only when an existing deck is within the existing deck's own span (or its footprint covers the crossing), not within half the new span. Otherwise draw the deck. |
| `settlement/city/bridges.py` | `test_every_deck_is_long_enough_to_land_on_dry_ground` | A bridge deck must never be shorter than the width of the water it crosses. | partial | When seat_deck cannot seat a deck, do not draw the undersized one: re-route/square the way at that crossing (stage_crossings already squares lanes over streams and drawn channels, not field ditches) and re-solve, or refuse the crossing so the way is re-planned. |
| `settlement/city/bridges.py` | `test_every_plank_crosses_a_supply_ditch_and_never_the_collector` | A footplank must never be laid off a recorded ditch, nor over the collector/drain rather than a supply ditch. | partial | Refuse role == 'drain' (and 'feeder') in channel_footbridges for every archetype, not only through the polder's seg_caps - the test's grounding is that a plank over the drain crosses the runoff, not the ditch anyone needs. |
| `settlement/rolling/fit.py` | `test_no_farmhouse_stands_on_the_brook` | No farmhouse corner stands within the brook's half-width plus 5 ft of its course. | no | Round the brook before the homesteads are seated (at the water stage, since every way is routed after the houses anyway), so the seat test reads the final course. Or re-check the house rects against the rounded course in round_the_brooks and refuse the rounding radius locally. FR-013. |
| `settlement/rolling/fit.py` | `test_the_comb_hamlet_draws_no_forbidden_overlap` | No two features whose overlap classes forbid it may overlap (matrix_violations) on the comb reference hamlet. | partial | Have the placers consult the taxonomy they are judged by: index the classified extents once (matrix_extents) and make _fits and every scatter/linear writer refuse a seat that matrix_policy forbids against what is already drawn. |
| `settlement/rolling/fit.py` | `test_the_polder_hamlet_draws_no_forbidden_overlap` | No two features whose overlap classes forbid it may overlap on the polder (Kuwabata) hamlet. | partial | As for the comb hamlet: placers consult matrix_policy through one indexed extent set. |
| `waterfields/comb.py` | `test_the_supply_commands_both_flanks_of_the_fan` | Each flank of the fork must have supply ditch reach of at least max(80 ft, 30% of that flank's planted extent). | no | It holds by the skeleton's proportions (canal A at down-42 deg, canal B at down+58 deg, offtakes along both) but nothing measures it; BROOK_FAN_TRIM shortens one canal. Add a both-flanks predicate to the fit's legality score (beside tail_dangles / net_bends_acutely) so an aspect/size that leaves a flank uncommanded is illegal, or constrain canal lengths per flank. GM 2026-08-16. |
| `waterfields/comb.py` | `test_a_collector_discharges_at_its_lowest_point` | A drain collector's outfall may not sit more than 1 px uphill of its head. | partial | Every interior vertex, including the HEAD at lo_u, gets U(-6, 6) of fall jitter, so the outfall is only b*(hi_u - lo_u) below the head's line; a span under ~100 px lets the jitter put the head below the outfall. Clamp the head's jitter to <= b*span - 1 (or no jitter on the head), which makes it by construction. |
| `waterfields/comb.py` | `test_the_runoff_curves_out_of_the_collector` | The drain collector's recorded polyline must never turn 100 degrees or more at any vertex. | no | Build the collector so its turns are bounded: drop the last interior vertex when it falls within a few px of the outfall (the `duf` loop at comb.py:695-698 appends hi_u after an arbitrary last u, which makes the 'short hook' drain_heading's docstring describes), or clamp the jitter so every turn stays under the bar; the research grounding is the test's 'a collector turns DOWN the valley'. |
| `hamletgen/hinterland/parcels.py` | `test_no_three_woodland_parcels_stand_in_a_ruled_row` | No three woodland parcels stand in a ruled line (the third off the line through two others by less than 20% of their span). | no | Re-ask in_a_ruled_line on the final seat, after the jitter and size roll (refuse the jitter, as _ok does), and on the point the record will carry. Or make the record's x,y the seat center the rule was asked of. Settlement-reviews of 2026-08-18 and of Inashiro (feature 261). |
| `hamletgen/hinterland/parcels.py` | `test_a_woodland_commons_is_mostly_inside_the_picture` | A woodland commons parcel's box must never fall less than 70% inside the rendered view. | partial | Seat the woodland against the FINAL view, or re-test after stage_frame and drop/move a parcel that fell under the floor. |
| `hamletgen/homesteads/wells.py` | `test_every_well_stands_among_the_doors_it_serves` | A well must never stand more than 95 px (edge gap) from every dwelling. | partial | Use the gate's own measure in every rung: require an EDGE gap <= 95 px to some house (not a center distance of 105-112), and give the last-resort open_seat the same floor. |
| `hamletgen/homesteads/wells.py` | `test_every_household_can_reach_water` | No household may stand more than 760 ft from a well or open water. | partial | Make coverage a hard postcondition: if the ring probe finds no seat for a dry house, fall back to open_seat near THAT house, and if that fails refuse the house seat (feed it to the driver's avoid list, as the reach re-roll does) rather than ship it dry. |
| `hamletgen/ways/checks.py` | `test_every_lane_crosses_a_drawn_channel_square` | No lane crosses a drawn channel more than 10 degrees off square. | partial | Where the crossing segment is too short, split the segment or move the adjoining vertex so the square leg fits, instead of leaving it. Handle every crossing on a segment, not just the first. Re-square against all waters until a pass changes nothing. Research ways/030 (a plank crosses its ditch square). |
| `hamletgen/ways/checks.py` | `test_every_lane_crosses_the_brook_square` | No lane crosses the brook more than 10 degrees off square. | partial | As for the channels: split or extend a segment too short to hold the square leg, square every crossing on a segment, and iterate over streams and channels together until nothing changes. Or square at the router by forcing the path through the two ford landings (ford_crossing) that the connector already uses. Settlement-review of Kashikawa (round 03cf6a84). |
| `hamletgen/ways/joints.py` | `test_no_lane_ends_in_a_hook` | No lane's first or last leg is 12 ft or shorter and turns back 90 degrees or more. | no | Make hook removal the invariant of the lane commit (commit_lane / reink_lane refuse to write a hooked lane). Or run _one_hook as the very last lane pass, after stage_crossings' squaring too. Where unhooked cannot keep the end on its ways, cut at the vertex before and let the touch pass re-join it. GM 2026-09-26. |
| `hamletgen/ways/joints.py` | `test_no_two_lanes_meet_end_to_end_in_a_fold_and_no_lane_ends_in_a_hook` | Two lanes meeting end to end must never double back (>=140 degrees), and no lane may end in a short hook (_HOOK_FT / _HOOK_DEG). | partial | Refuse rather than repair: when neither tee nor unhooked yields a legal rewrite, drop or re-route the lane end; and run the joint/hook rule after the last lane writer (split_at_crossings creates new end-to-end joints after straighten_joints). |
| `settlement/fields/comb.py` | `test_every_bund_bead_sits_on_visible_ground` | No azemame bead may sit on water paint (inside any field ditch, channel stroke, or the pond). | partial | The drop reads M at one moment; water recorded after it is never tested: `_comb_source_channel` (a pond-fed field's bowed hairline into the paddy, w 2.5) is appended AFTER the drop in draw_comb_field, and hamletgen/sink.py:drain_run (stage_sink) later still. Run the drop at finish over the final water registry (or have every channel recorder re-filter beads), keeping bead_runs so the two-bead rule survives. |
| `settlement/fields/comb.py` | `test_village_passes_gate` | A shipped scripted map must never paint a field channel under a later paddy plot, and its typical paddy cell must never leave the 0.030-0.072 acre band (plus: the gen runs within its CPU budget). | partial | Make every field_channel on a comb map late (or have field_channel default to the late block once one exists), so no channel can precede a plot. For cell size, have fit_field/carve_comb assert the median interior cell area inside the band (research/fields.html 'Plot sizes, pond sizing and acreage from population') and adjust plot_across when a carve leaves it. |
| `settlement/land/cover.py` | `test_the_countryside_has_no_holes_in_it` | No more than 35% of the rendered view may be ground no cover, field or built footprint covers. | no | Measure the bare fraction over the predicted frame after the scrub scatter (the same 25 px grid) and lay further scrub/grazing parcels into the largest uncovered cells until it is under the bar; the grounding is the GM rule 'margins form a continuous ring'. |
| `settlement/land/cover.py` | `test_a_woodland_commons_is_visibly_stocked` | A woodland commons parcel must never record fewer than 5 crowns (or none). | no | After seating a woodland's crowns, refuse the parcel (drop it and try the next scanned patch) when fewer than the stocking floor seated; or have open_ground_patches pre-test crown seats so a parcel is only offered where the floor can be met. |
| `settlement/shrines_wells/byres.py` | `test_every_farmstead_part_stands_on_its_house_bank` | No farmstead part (garden, threshing yard, fixture, byre, shed, persimmon, bamboo stand with `of`) stands across the brook from its own house. | partial | Give draft_byres (_courtyard_byre_seat, _yard_shed_seat and its spiral) the same across_the_brook refusal and try the next seat. Move round_the_brooks before the homesteads so every bank test reads the final course. FR-013; the shared-bank rule is recorded as a GUESS in research/homesteads. |
| `settlement/shrines_wells/byres.py` | `test_the_settlement_seats_the_byres_it_asked_for` | A settlement must never seat fewer byres than its recorded byre_target. | no | Reserve the byre with the homestead: decide the keeper households (BYRE_KEEPER_SHARE, research/homesteads/300) before seating and include the byre arm/shed in the homestead envelope at seat time (the envelope-first placer already carries the kura this way), so a keeper cannot be seated without room for its beast; failing that, walk every household (not only the ranked pool) and widen COURTYARD_REACH before giving up, and raise if the target is still unmet. |
| `settlement/structures/fixtures/siting.py` | `test_an_entrance_board_stands_at_the_entrance` | An entrance-seated notice board never stands more than 160 ft from the entrance anchor, nor where some household's way out does not pass within 20 ft of it. | no | Make routes_missed == 0 and dist(anchor) <= ENTRANCE_REACH + ANCHOR_BAND hard filters on the candidate set. Where no verge passes them, open a verge on the approach inside the handover band (the connector is every departure's way). Give stage_notice's re-seat the same filters. FR-015 / SC-011; research/urban-features.html (the kosatsu at the village entrance, broadside to the way out). |
| `settlement/structures/fixtures/siting.py` | `test_the_board_caption_notches_no_crown` | The board caption never lies on a tree crown unless meta.kosatsuba_caption_level records that no seat offered a clear caption (level 1). | no | Give the canopy to the label-phase placer as an obstacle (weighted below roofs) for the board's caption, so the drawn seat is the one ranked clear. Record kosatsuba_caption_level from the DRAWN caption in _draw_board_caption rather than from the siter's probe. |
| `compound.py` | `test_every_mode_a_sheet_passes_its_checks` | No live Mode A sheet fails any registered pack_audit check for its type (structures on walls, occluded/overlapping/dark-on-dark labels, floating doors, passage blockers, scale bar, viewBox crop, tub/well/notice-board siting, coverage band, perimeter hugging, sanctuary axis, arch/well, etc.). | partial | For the generated drafts: run R.run_checks on emit_svg's output inside compound.main (or place()) and refuse/raise on a hard check, and make overflow a hard error; move siting rules (tubs, notice board within 20 ft of gate, perimeter hugging) into _place_one's candidate set. For hand sheets a placer guarantee is impossible - the test IS the guard (feature 254: 'automated checks that we run on them'). |
| `hamletgen/frame.py` | `test_a_channel_declaring_a_stream_actually_reaches_its_bed` | A channel declaring a stream end must reach within 13 px of that stream's bed. | partial | The drain run's confluence (sink.py:brook_join) is not held by round_the_brooks, so a join near a brook vertex can be left off the filleted course; hold confluences too (or re-snap the run's end after rounding). The intake snap only fires within 30 px. |
| `hamletgen/hinterland/belt.py` | `test_every_pool_hamlet_has_its_belt_on_the_regional_northwest` | A hamlet's windbreak must never stand more than 45 degrees off northwest of the cluster center, never subtend more than 200 degrees round it, and the map must seat exactly its declared households. | partial | After village_grove, measure the drawn clumps' bearing and subtense against the cluster and repair (replant the thinned windward stretch, drop a flank arm past the hook) or refuse the band and try the next ladder rung. Research: research/vegetation 'Does a shelter belt wrap the settlement?' (a hook on one or two sides). |
| `hamletgen/hinterland/frame.py` | `test_no_shipped_hamlet_breaches_its_scatter_frame` | The final view must never reach past the frame the scatter was thrown within (a strip with no scatter). | no | settlement/finish.py:601-626 only MEASURES and records scatter_frame_breach after the fact; nothing refuses or repairs. Guarantee by clamping the view to the recorded scatter frame at crop time, or by re-throwing scatter over the breached strip at finish (the frame is known then). |
| `hamletgen/hinterland/stages.py` | `test_the_ground_cover_scatter_respects_what_was_swept_before_it` | Ground cover (commons, marshes) must never be drawn over a swept clearing or any feature its class may not overlap. | partial | Refuse a clearing registered after a scatter it intersects (or re-sweep the cover under it), i.e. move every clearing-reserving placer before stage_hinterland as a checked invariant using the recorded seq ordinal. |
| `hamletgen/homesteads/seats.py` | `test_lane_frontage_seats_the_hamlet_when_the_field_row_offers_nothing` | With the field row silent, a linear hamlet must never seat zero households and its connector must offer frontage seats. | no | lane_frontage returns whatever verge the connector offers; each seat must still pass _seat_allowed and try_place. Guarantee by falling through to the lattice/rescue (which the stage already does) and by having the linear form's connector sized to offer >= households seats. |
| `hamletgen/pondstock.py` | `test_a_dike_pond_hamlet_is_ponds_in_a_diked_block_with_wet_flanks` | A dike-pond hamlet must never lack its overlay/dike-pond record, 1-3 fry ponds, pig sties, a wet strip on every declared waterward flank, every household seated, or draw a duck pen or a threshing floor (forecourts only). | partial | stage_pond_stock: when no near-half seat fits, widen to the whole bank before skipping, and guarantee at least one sty when n_sty>=1 (feature 150 A3). Households: as the seating rows. |
| `hamletgen/ways/bund.py` | `test_a_way_reaches_the_field` | On a brook map, some internal lane always comes within 60 ft of the paddy or its dry hem. | partial | Make the 'none: ...' outcome impossible. Let the branch cross water at a ford or ditch (stage_crossings decks it), as the run-on already does. Failing that, feed the stranded field into the driver's re-roll like unreached_houses. FR-012 / SC-008; research/fields/290 (the path never ends short of the bund). |
| `hamletgen/ways/smooth.py` | `test_no_lane_doubles_back_or_kinks` | A lane must never turn 140 degrees or more at a vertex, nor make two 50-degree-plus turns within 40 ft. | partial | Hold the bend rule at every lane write (commit_lane / may_write refuse a result with a fold or a kink, not only one 'worse than it was'), and square brook crossings with a leg that keeps turns under 50 degrees or re-smooth after stage_crossings. |
| `settlement/_geom/primitives.py` | `test_the_polders_keep_outs_contain_what_they_stand_for` | The dike's keep-out must contain every vertex of the drawn band within <=24 chords; the field's facing chains must never accept an outline vertex they reach, within <=12 chords. | partial | If the chord caps are a rule (the GM's 'a couple of dozen'), raise eps adaptively in keepout_ring until the count is under the cap (containment stays guaranteed by the measured push). |
| `settlement/fields/features.py` | `test_a_field_pond_is_sunk_into_one_plot` | No plot or drain-hem ring edge may cross a field pond's rim (the pond sits inside one plot). | partial | The placer and the test no longer ask the same predicate: the placer allows a ring to enter the outer 3 px band (inset 3), but the test fails any ring with one VERTEX inside the full ellipse and the next outside. Align them: either the placer refuses any ring vertex inside the full ellipse (+ rounding margin), or the test returns to seg_in_ellipse_core. |
| `settlement/homestead_parts/yards.py` | `test_every_drawn_yard_is_a_floor_of_mats_and_racks_follow_the_weather` | A drawn threshing yard must never hold under 4 or over two-thirds-of-full-cover mats, never fall short of a third where a 1 ft lattice seats more, never lack a rack on a changeable-weather map, never have a rack corner map-south of its center, and never have a rack on a settled map; a no-rice hamlet draws no threshing floor. | partial | Make the yard placer (_find_yard / _yard_fits) refuse a yard whose outline cannot seat 4 mats or a rack of RACK_MIN_FT on a changeable map, so the yard is re-sized or re-sited rather than drawn short. Research: spec 282 FR-004 (mats) and the harvest_weather knob (racks by the house). |
| `settlement/houses.py` | `test_farmhouses_vary_in_size` | A hamlet must never draw its plain farmhouses so uniform that under 20% differ from the median footprint by more than 5%. | no | Sizes are a position-seeded hash (houses.py:650-661: length factor 0.85-1.35, depth 0.90-1.10 on the nucleated path; wealth tiers on the dispersed path), so variety is statistical, not constrained. Guarantee by drawing sizes from a stratified set per settlement (e.g. a shuffled ladder of length factors) so the spread is fixed by construction. Research: the farmhouse-size spread in research/homesteads. |
| `settlement/land/dikes.py` | `test_the_polder_dike_is_a_hand_piled_earthwork` | A polder dike's widest stretch must be at least 1.4x its narrowest (never a uniform-width band). | no | Width is wlo + (whi-wlo)*clamp(0.5 + three seeded sines) + U(-3,3); with the default (14, 40) the ratio is usually well past 1.4, but nothing bounds it (phases can flatten the sum). After w_seen is built, if max/min < DIKE_IRREGULARITY, stretch the profile about its mean (deterministic, no new draw) until it holds. Research: fish-scale polder dike (archetypes.html). |
| `settlement/structures/captions.py` | `test_every_caption_records_the_feature_it_names` | A caption must never be drawn without recording the box of the feature it names (element [6]). | partial | Make the referent mandatory: label()/_record_label (settlement/finish.py) refuse a caption with ref=None unless it is explicitly an area/district caption, so the `text` path cannot emit an anchorless caption. |
| `tools/seat_label.py (make seat-label) over the one caption placer in labels/` | `test_every_caption_on_a_hand_drawn_sheet_is_at_its_standard_seat` | A caption on a hand-drawn Mode A sheet must never stand off its standard cartographic seat (unless ledgered for an unchanged sheet). | no | Captions on these sheets are hand-written SVG; the placer is only consulted after the fact (judge) and via a manual `make seat-label WRITE=1`. Guarantee by having the sheet's gen emit captions through the placer (compose, not hand-write), retiring the ledger. Rule: feature 266 cartographic standard. |
| `waterfields/furrows.py` | `test_dry_plots_share_a_row_direction_within_a_tract_and_change_it_at_the_seams` | Neighboring dry plots of one tract may not differ by more than 2x the in-tract turn; neighbors across a tract seam must differ by more than ~6 deg. | partial | Seams are forced only against the previous tract in sequence. Unguarded: the fork-triangle band (_comb_dry_and_beans' second _dry_fields call, tract0 offset) against first-band tracts it abuts, and non-consecutive tracts that end up spatially adjacent. Force a seam against every tract whose plots neighbor the new one (spatial adjacency, as the gate reads it). Research fields/180. |
| `waterfields/seams/plots.py` | `test_a_bund_does_not_build_a_flight_of_steps` | No plot ring may carry more than one bund step (jog) - no staircase walls. | no | _absorb PREFERS a weld that adds no jog but falls back to the least-jogged weld (`_jogged` branch), and _unjog REPAIRS steps but refuses a trade that would break another rule, leaving the step. Nothing refuses a ring with >1 step. Make >1 step a refusal in _absorb (treat a jog-adding weld like a needle: try _open_to / the next host) and add a terminal check after _unjog that sends a remaining staircase to the scrap path. GM 2026-08-18 on Inashiro. |

**Findings beyond the owners** (observed 2026-09-29, method: the census readers). `stage_crossings` / `square_crossings` rewrite the lanes after the web and the woods
with no re-check (group 3). Where a placer and its test measure different things - the wells' spacing (center to center
against edge to edge), the eave gap on a quarter-turned house (rotated quads against boxes), the field pond's 3 px inset,
the flooded tint's deduplicated ring - the guarantee is written against the rule, and the test and the placer read one
predicate (the engine's standing rule). The overlap matrix is read by a test only, never by a placer (group 3).

## R2 - The placer fallbacks that knowingly emit a compromise (2026-09-29)

**Method** (observed 2026-09-29, method: a grep of the engine code a live generator executes for fallback language -
least-bad, best-effort, fallback, shortfall, give up, rescue, last resort and the like - read by four Opus readers, each
distinct fallback with the code around it; the rows are `fallbacks.json`). The grep EXCLUDED, by path: `settlement/city/`,
`settlement/town_ways.py`, `settlement/structures/urban*.py`, `packing.py` and `servants.py` (the town and city tiers), and
`tools/`, `ci/`, `pipeline/` and `interactive/` (not placement) - 260 hits in 70 files. The town and city exclusion is by
CODE PATH, not module, so the city modules a hamlet calls were read as well: `settlement/city/bridges.py` (`bridges`,
`channel_footbridges`, from `hamletgen/frame.py` and `settlement/rolling/roll.py`) - its two
fallbacks are the last two rows below - and `settlement/city/moat.py` (`sluice_gate`, from the polder dike in `land/dikes.py`;
`inwall_drain_outfall`, from `fields/comb.py`), where the fallback grep finds nothing. `city/walls.py`'s helpers are reached
only by the town wards and the freestanding wall (`castle_civic.py`'s `wall`, a town feature), so they stay out (the search:
every method of `settlement/city/*.py` against callers outside the town and city modules). One row the grep brought in is town-only and recorded, not converted:
`settlement/water_ways/wards.py:_ward_ends_on_wall` (reached only by a hand-authored city generator).
Of 150 distinct fallbacks, 31 emit something that breaks a stated rule when their branch runs; the rest degrade within
their rules (a smaller feature, a drop the rule itself provides for, a search fallback that still returns a legal result),
are not placement, or are the town-only row. The breaking ones are this feature's scope (FR-005). The three censuses are joined by owning placer in
`scope-by-owner.json`, written by `scope_join.py` from `census.json`, `fallbacks.json` and `excused.json`:

| where | what the branch does | the rule it breaks | reachable | sketch (observed 2026-09-29, method: the fallback readers) |
|---|---|---|---|---|
| `hamletgen/frame.py:stage_notice:250-301,362-365` | when every in-frame verge is refused as off-way (>15 deg) or under the village canopy, the best-ranked LOOSE seat is taken anyway and turned to its nearest way - the board can stand under the belt | a board may not stand under the village's own trees ('a board in a wood is a notice nobody reads'), stated at frame.py:283-287 and applied by place_kosatsuba (settlement-review, feature 230 pass 12) | rare (a hamlet whose every in-frame lane verge lies under its belt or beside a crossing straggler) | reserve a roadside board seat before the belt/woods are grown (the woods keep out of it), or grow the frame/ranked lanes until an unshaded verge exists; failing that, a stated drop with the manifest saying so |
| `hamletgen/frame.py:stage_notice:366-369` | when no verge inside the frame takes a board at all, the engine's original seat (the one the guard just found outside the frame) is appended unchanged | labels_within_image / the board's whole footprint inside the view (frame.py:170-195, settlement-review feature 227: Sawada shipped with no board drawn) | rare (pragma no cover; no cohort map reaches it) | refuse the out-of-frame seat: extend the crop to take the board (it runs last, so nothing is displaced) or have place_kosatsuba search only inside the predicted frame |
| `hamletgen/frame.py:stage_frame:412 (settlement/finish.py:title:348-368)` | title with no blank or cover-only pocket and every corner blocked grows a north title band and sits the placard there 'over nothing, unless a feature runs off the frame there, which the check still reports'; the stage_frame comment still describes the retired corner-overlap fallback | title_clear_of_features (named at frame.py:412-413 and finish.py:360-362) | rare (every corner holds a plot AND a runner - lane, stream, belt - crosses the north edge under the placard) | slide the placard along the band to a span no runner crosses (or clip runners at the band's lower edge, since the band is outside the map); also correct the stale comment |
| `hamletgen/homesteads/wells.py:wells:276-327` | coverage rescue: a household beyond 760 ft of any water gets a ring-probed well; if no probe passes, nothing is placed and the household is left dry | settlement_dwellings_watered - every dwelling within ~760 real ft of a well, channel, pond or stream (wells.py:271-274) | rare (pragma no cover: 'the bundle-pitch fix left the courtyards open enough that no cohort map strands a household') | reserve a well seat inside each bundle's courtyard when the household is seated (the envelope-first placer), so coverage is guaranteed by construction; or refuse the seat of a household no well can reach |
| `hamletgen/homesteads/wells.py:wells:328-337` | last resort: open_seat over the house-cloud bbox with no among-the-dwellings or not-clustered test; if that finds nothing the map has no well | settlement_has_wells ('a settlement with NO well fails the gate outright', wells.py:329-330); the open_seat seat is not held to wells_among_dwellings' 95 px edge gap (wells.py:286-293) | rare (pragma no cover; only when the whole lattice found nothing) | apply the same among-the-dwellings filter to the open_seat result, and guarantee a seat by reserving one well pocket in the cluster before the houses pack it (refuse a cluster that leaves none) |
| `hamletgen/ways/track.py:connector_track:647-665 (path_violations, hamletgen/ways/checks.py:147)` | no clean bearing: the connector takes the least-bad candidate ranked (wet, steadings, crop/pond/brook) | roads_clear_of_marsh and 'a path does not pass through marshland' (GM, track.py:614-620, wet.py toe_band); houses_off_corridors / TRACK_FABRIC_GAP (track.py:622-636: a through-road across the hamlet 'stays laid across'); pond/brook avoided outright (checks.py:149-152) | rare (a cluster pocketed so every one of 41 bearings is fouled) | route the connector with the lattice router over a coarse grid (cap raised for the long span) with wet/steadings as hard walls, or refuse the cluster seat/gateway that leaves no clean exit and re-seat |
| `settlement/land/wet.py:_clip_marsh:168-183` | when shapely raises or returns no polygon, the marsh is drawn UNCLIPPED - over the dike block, the fields and the pond | the marsh is subtracted from the filled dike block, the fields and the pond (docstring wet.py:150-168, the GM's T54 complaint) | rare (degenerate outline / GEOS exception) | repair instead of reverting: buffer(0)/make_valid the inputs and retry, else drop the marsh record (a stated drop) rather than draw it over the crop |
| `settlement/land/wet.py:trim_off_marsh:454` | a two-point way whose whole length lies in wet ground is shortened to <=30 px and left with its soaked end | 'a path does not run into a reed bed: it stops on the dry side of it' (trim_off_marsh docstring wet.py:430-433; roads_clear_of_marsh) | rare (a skeleton arm or stub lying entirely inside a marsh) | drop the way entirely (return []) and let the caller treat it as an arm with nowhere to go, the drop test_lane_clipping already states |
| `hamletgen/cluster.py:seat_cluster:55,120,242-245` | when no wind-facing margin has room for its belt, the best CRAMPED margin is seated - the windbreak belt runs partly off the canvas | the windbreak stands 36-146 ft upwind of the cluster on the canvas (belt_polygon; settlement-review of Mizuguchi, feature 261, cluster.py:225-231: the belt left 'a strip ... holed where they stood in it') | rare (every wind-facing margin's band runs >20% off the canvas) | grow the canvas/frame upwind to take the belt, or shift the seat along the margin until the band fits; failing that a stated reduced-belt rule |
| `hamletgen/cluster.py:seat_cluster:82,119,244-245` | when no margin faces within 45 deg of the wind, the best OFF-WIND margin is seated (recorded as seat_offwind) | 背山面水 - the cluster's back to the windward side; 'a margin whose normal is more than 45 degrees off the wind is not a candidate at all' (WIND_BACK_MIN_DOT, seat_cluster docstring, feature 261) | rare (an envelope with no wind-facing margin clear of the drain, hem and brook) | constrain the field envelope/plan so a wind-facing flank always exists, or re-roll the plan when none does rather than seat off the wind |
| `hamletgen/ways/clearance.py:route_around:305` | Bends a way round a field outline for at most `rounds` (6) passes and returns whatever it has when the rounds run out, even if a leg still crosses the outline. | A track meeting a field goes round it (route_around docstring; lanes_clear_of_dry_plots / fields_clear_of_road gate tests, the Inashiro 2026-08-12 GM finding) | rare (an outline whose detour needs more than six splice rounds - deeply lobed fans or a leg re-entering after a splice) | Loop until no leg crosses (bounded by the ring's vertex count, since each splice consumes edges), then verify; if a crossing survives, refuse the track and hand back to connector_track's next bearing rather than returning a crossing path. |
| `hamletgen/sink.py:stage_sink:473` | When no bearing/junction-distance candidate for the off-map drain brook scores zero, it draws the LEAST-BAD route, which may lie in the envelope, cross the field, turn over 55 deg, or run uphill. | drainage_discharges_downhill, watercourses_flow_downstream, drainage_junction_smooth and streams_avoid_fields (the gate predicates this function's own comment says it scores against, sink.py ~433-470) | rare (pragma no cover: a fan that blocks every bearing at every junction distance; no cohort fan does) | Constrain first: widen the candidate set (more junction distances, longer run, route_around the envelope), then try the pond sink; if still none is clean, raise so the roll is refused rather than drawing a known-bad brook. |
| `hamletgen/water/brook.py:feed_brook:385` | When all fifteen upslope bearings clip the field envelope, the approach is drawn straight up the fall line regardless, crossing the rice. | streams_avoid_fields - a stream does not run through a flooded paddy (feed_brook docstring, brook.py ~351-356) | no (pragma no cover: 'a fan head never blocks all fifteen'; kept as the loop's terminal) | Replace the terminal with route_around(plan.envelope, approach) and a verified clear result, or raise ValueError so the fan is refused, instead of returning a route known to cross. |
| `hamletgen/ways/track.py:_thread_the_fabric:230` | When route+clip and the four-step swing ladder all fail, returns `out` (a clipped run still crossing the steadings) or, if the clip died, the original `run` straight through them. | houses_off_corridors, houses_clear_of_lanes, features_do_not_overlap; the function's own comment 'THE FALLBACK MUST NOT BE THE OFFENDING RUN' (track.py:194) | rare (run[0] inside the fabric or an obstacle next to it; the ladder's success path is pragma no cover and _route returns [] for frame-length connectors, so this terminal is what a blocked connector gets) | Return [] (a stated drop recorded in meta, as the spur's shortfall is) or move run[0] out of the fabric before routing; never return a run that _crosses_fabric. |
| `hamletgen/cluster.py:seat_cluster:246 (recorded at hamletgen/ways/track.py:stage_seat:301)` | With no wind-facing margin, the cluster seats on the best margin whose back faces off the wind and records meta.seat_offwind. | The seat turns its back to the wind (WIND_BACK_MIN_DOT, hamletgen/consts.py:669-675, feature 261); 'the gate refuses [seat_offwind] on the pool' (test_pool_wind.py:51 asserts False) | rare (a fan whose every wind-facing margin is blocked by drain/hem; test_cluster.py:62 builds one) | Refuse (raise) on a live roll so the seed is re-rolled or the spec's fall/wind is revisited, or constrain the site plan so a wind-facing margin exists; keep the offwind seat only behind an explicit spec opt-in. |
| `hamletgen/ways/track.py:connector_track:651` | When none of 41 bearings is clean of wet ground, steadings and crop, the connector returns the LEAST-BAD bearing (lexicographic wet, steadings, crop); only crop hits are repaired later by route_around. | roads_clear_of_marsh (a track through a marsh is not a road, track.py ~590-600) and houses_off_corridors / features_do_not_overlap for steading hits (track.py ~614-630) | yes for crop-only violations (repaired downstream); rare for wet or steading violations (a cluster in a pocket of the fan with the toe marsh spanning the canvas) | Accept only candidates with soaked==0 and steaded==0; if none, widen the sweep (reach, bows, a second start on the cluster edge) and then refuse the seat, instead of returning a bearing through marsh or a house. |
| `hamletgen/ways/serve.py:door-path loop (cut ranking):550-563` | when neither cut is clean, the least-bad cut by (fouls, bends) is kept, and a cut that crosses a neighbor's yard or garden (_crosses_fabric against passable) can survive, because only a steading foul is re-tested later (_hits_a_steading) | a lane may not overlap another household's fabric (the overlap matrix; stated at serve.py:550-555 'An overlap is a rule the matrix forbids outright', cohort seed 18 grazing a garden at 1.21 ft) | rare (both cuts foul, e.g. cohort seed 18) | Treat a fabric foul like a steading foul: skip the cut (continue to the next target way) rather than rank it, leaving the house unserved when no clean cut exists. |
| `hamletgen/ways/serve.py:door-path loop (_folded last resort):606-632` | a door path that bends badly on every target way is still drawn as the least-bad fold so the house is served | lanes_bend_like_paths (no turn past the bend bar; tests/gate/test_lane_network.py, tests/hamletgen/ways/test_geom.py:300) | rare (every way round is blocked, e.g. cohort seed 16's 71-then-61 degree fold) | Refuse the fold as the steading foul is refused, or repair it: route the path again with a turn-angle cost in the router so no candidate folds; else a stated drop reported by farmhouses_reach_a_way. |
| `hamletgen/ways/serve.py:door-path loop (unserved house):612-635` | when every candidate fouls a steading or none ends worth walking to, the house is left with no way and recorded in _exhausted | farmhouses_reach_a_way (every farmhouse is served by a way; named at serve.py:618-619 as the check that reports it) | rare (hemmed-in steadings; the comment at serve.py:388 records 2 unserved on cohort seeds 5 and 25) | Constrain the candidates upstream: have the homestead placer reserve a door corridor to the web before seating neighbors, so an unreachable seat is refused at seating rather than discovered here. |
| `hamletgen/ways/fabric.py:_draw_web (join refused):272-282` | a join link that would touch a farmhouse is refused and the piece it was joining is kept orphaned (the trade serve.py:619 cites) | lanes_form_one_network (the web is one connected network; stated at fabric.py:275-281) | rare (a join whose only short route runs past a house corner, e.g. sawada and kashikawa 2026-08-29) | Repair: route the join at WEB_FABRIC_GAP around the steading before refusing, and drop the orphan piece (a stated drop) only if its houses are served elsewhere. |
| `hamletgen/cluster.py:seat choice (offwind fallback):244-247` | when no field margin faces the wind within 45 degrees, the best off-wind margin is taken and meta.seat_offwind is set | the seat turns its back to the wind (WIND_BACK_MIN_DOT, hamletgen/consts.py:664-675, which says the gate refuses seat_offwind on the pool; tests/hamletgen/test_pool_wind.py) | rare (every wind-facing margin blocked by the drain or dry hem) | Refuse: raise as the no-margin case does, so the roll re-seeds or the plan re-aims the fan, instead of drawing an off-wind seat. |
| `settlement/finish.py:title (no view):376-377` | with no view set, the title goes at the top center of the canvas with no clearance test | title_clear_of_features (the placard may sit on cover, never on a building, plot, field, water, lane or label; finish.py:543, tests/settlement/test_label_placement.py) | no (both callers, hamletgen/frame.py:432 and settlement/rolling/roll.py:111, crop first) | Refuse: raise when title() is called before crop_to_content, since the docstring already requires the crop. |
| `settlement/structures/fixtures/siting.py:board_choice / place_kosatsuba:91-115,469,536-560` | when no seat above the traffic floor offers a caption at level 2, the board is still placed at the best level available (caption over a crown, or nowhere beside the board), and meta.kosatsuba_caption_level records it | the GM's ruling 2026-08-29 that a board under a canopy is acceptable only 'as long as there is a label attached to it and the label is visible' (siting.py:520-523, 538-539); labels_clear_of_other_buildings, which siting.py:469 says will report it | yes (siting.py:557-559 names Sawada's entrance as having no departure-band seat with a clear caption) | Constrain the candidates: widen the anchor/handover band or the traffic floor until some seat reaches caption level 2, and refuse the placement only when none does, recorded as a stated drop. |
| `waterfields/seams/pockets.py:_absorb (chevron fallback):490-500` | the least-bad arrowhead weld is taken with no test against the gate's chevron line, unlike the needle fallback, which is held to _GATE_MIN_APEX | a paddy basin does not read as an arrowhead: _CHEVRON_MIN_APEX / _CHEVRON_MIN_SOLIDITY, 'CAUGHT AT 40/0.90, GATED AT 35/0.85' (waterfields/banks.py:503-504) | rare (no jogging or lumpy host and a chevron host available) | Hold it to the gate line as the needle fallback is held to its line: take the chevron only if is_chevron(ring, 35, 0.85) is false, else leave the scrap bare (the recorded 'odd corner left unpaddied'). |
| `settlement/shrines_wells/byres.py:draft byre placement (shortfall):265,287-368` | when the owner pool runs out before target byres are seated, fewer are drawn; meta.byre_target records the ask | byres_meet_their_target (a shortfall is a placement failure, not a settlement without oxen; tests/gate/test_cluster_and_homes.py:134-143) | rare (crowded ground where no spiral seat clears; courtyard form seated 8 of 16 on the cohort before the arm seat) | Reserve the byre with the homestead bundle (as the yard and garden are) so the count is guaranteed at seating, or widen the spiral reach for the shared form until the target is met. |
| `hamletgen/ways/sweeps.py:_join_orphan_ways:308-314` | When no candidate link joins an orphan way without crossing the brook and coming back, the out-and-back link is kept as the last resort and drawn | A link must not cross the brook to the same bank and come back, 'two planks for nothing' (settlement-review of Mizuguchi, feature 261, stated in the comment at sweeps.py:302-304). This branch knowingly draws that form | rare (an orphan whose only routable candidates leave by one ford and return by another, e.g. Mizuguchi-type brook-in-the-cluster maps) | Constrain the router so the orphan and the network are joined along one bank, planning against the brook with no fords open when both ends are on the same bank. Where that fails, drop the link as a stated drop and let the straggler pass or the stranding re-roll handle the houses |
| `hamletgen/homesteads/stages.py:stage_homesteads:441-520 (rescue rounds 5-7, then the shortfall)` | After four lattice rounds, the rescue offers along-the-field ends and a wider random cloud. If the quota is still short after round 7, the map ships with fewer households and plan.placed records the shortfall, with no refusal or re-roll | households_consistent: occupied farmhouses must be 0.85-1.05x the declared households (stages.py:131, research/settlements.html 'Is every household in a hamlet actually drawn?', tests/gate/test_generator_contracts.py:test_every_declared_household_is_seated). Only the gate's rolled seeds hold it | rare (a short or boxed margin band. Cohort seed 25 was 19 of 20 before the rescue took the ends, and Inashiro was 13 of 15) | Size the band from the household count before seating (as roll.py sizes need = households x pitch^2) and widen or re-seat until the floor is met. Otherwise refuse the roll (re-roll it, as the stranding re-roll does) when placed < 0.85 x households |
| `hamletgen/homesteads/fixtures.py:seat_farm_fixtures:653-660 (the unseated shortfall)` | A fixture no house had room for is not drawn, and the miss is recorded in meta.farm_fixtures_unseated | The per-hamlet PREVALENCE BAND rolled from the seed (fixtures.py:18-30, research/homesteads.html 'The farmstead's fixtures'. For example, the privy is near-universal, 'a separate outbuilding was the norm'). The drawing departs from its own rolled count, which the comment admits ('a drawing that departs from its own declared count'). Recording the miss is not the rule | rare (a boxed-in homestead. The tests at test_homesteads.py:383 and :511 build it) | Constrain: reserve each rolled fixture's seat inside the homestead envelope when the house is seated (envelope-first, feature 227), so a seated house has its fixtures by construction. Otherwise refuse the house seat that leaves no room |
| `settlement/homestead_parts/stands.py:gap fill:531-590` | A windbreak gap whose columns offer no legal seat at any depth is marked _barren and left bare | village_windbreak_is_continuous: a hole funnels the wind (tests/hamletgen/test_hinterland.py:360, and the agroforestry passage quoted at stands.py:533-538). The branch ships the bare column | rare (cohort seed 45 fails village_windbreak_is_continuous, per tests/gate/hamletgen/test_driver.py:152. Seed 33 is a recorded tripwire in tools/mapcheck) | Constrain upstream: reserve the belt's band against later hard blockers before they are seated, or re-route the belt polygon around the blocker so every column has plantable ground. Where a lane crosses, draw the attested angled opening as a stated exception the check accepts |
| `settlement/city/bridges.py:seat_deck:104` | when no deck seats by growth or skew, the original undersized span comes back and the caller draws it | bridges_span_their_water (a deck spans its water; the docstring: 'an undersized deck that bridges_span_their_water then fails is better than none') | rare (a near-parallel crossing; cohort seed 47 reached it) | seat the crossing where a deck spans (move the crossing along the way, or square the way at the water as square_crossings does) and never draw an undersized deck |
| `settlement/city/bridges.py:channel_footbridges:377-386` | a ditch the gate needs crossed gets a plank at the best available spot even where the water there does not earn a board | worth_planking (a plank stands on water that earns one) | rare (cohort seeds 41 and 43 before the preference) | offer only seats whose water earns a board, and make the crossing need satisfiable (a seat on the qualifying run) rather than planking narrow water |

## R3 - The violations already on record but excused or left open (2026-09-29)

**Method** (observed 2026-09-29, method: one Opus reader over every section of `future-work/farming-communities.md` and
`future-work/cross-cutting.md`, and every test-side skip, pin or strict xfail that excuses a known violation - the
`ACREAGE_SHORT` seeds, the 85% seating floor, the seed-43 kink, the tripwire pins; the rows are `excused.json`).
Of 116 items, 61 are a placement rule a live generator can violate, or an excuse for one; the rest are out
(a feature not yet built, research or record text owed, performance, or a tier no live generator produces). Of the
61: 29 still true on today's engine, 29 unknown - most were found by checks feature 166 retired and
never re-measured, and a guarantee makes them impossible either way - and 3 fixed. The 58 not fixed are this
feature's scope (FR-006 for the test-side excuses, FR-001 for the rest):

| where | what | the rule | still open | owner | sketch (observed 2026-09-29, method: the R3 reader) |
|---|---|---|---|---|---|
| future-work/farming-communities.md: ## OPEN 2026-09-28, OWED: no way reaches a burial ground | No lane or path reaches a hamlet's own burial ground (Inashiro, Kashikawa, Kuwabata). | Rule: a path runs to the graves (research religion-and-death 140 'the graves and the paths to the graves are cleaned', 190 funeral path). hamletgen/burial.py seats the ground on every live hamlet and the web never targets it. | yes | `hamletgen/burial.py (seat) + the lane web (hamletgen/ways stage_web way-targets)` | Register a way-target at the ground's edge nearest the houses after the burial seat and before the web, so the web lays a footpath spur to it; unit-test that every seated burial ground has a way end within the footpath's reach. |
| future-work/farming-communities.md: ## OPEN 2026-09-28 (269 B26): the homesteads' woods fall short of their rolled area | Drawn homestead wood is 49-86% of the rolled area on every map; Kuwabata near/under the 6,000 sq ft floor; copse crowns across a lane from their house. | Rule: each homestead that keeps a wood keeps 6,000-28,000 sq ft of it, rolled per homestead (research/vegetation 210; HOMESTEAD_WOOD_FT2). The copse top-up runs out of seats inside COPSE_HOUSE_REACH_FT. | yes | `hamletgen homestead_parts/groves.py village_grove(area=) copse top-up` | Seat the shortfall as a second stand (behind the belt on the homestead's side) or widen the reach for a full homestead; unit-test drawn/rolled >= a stated floor per homestead. |
| future-work/farming-communities.md: ## OPEN 2026-09-28 (269 B07): a wild fan middle leaves a hamlet almost no dry field | fan_middle=wild leaves Inashiro 0.42 acre and Mizuguchi 0.41 acre of dry field (~0.03 acre/household). | Rule: the paddy and dry fields are sized from population, coarse grain about a third of the diet (research/fields 'Acreage from population'); the knob removes the hem and nothing re-places it. WHERE the band goes is research owed first. | yes | `waterfields/comb.py fan_toe_hem (the dry-band placer)` | After the research pass, place the dry band on the named ground at the acreage the sizing rule leaves; unit-test dry acreage per household against the sizing rule on both fan_middle forms. |
| future-work/farming-communities.md: ## OPEN 2026-09-28: the rest of the 269 landing's settlement-review findings - 'A lane end behind a house counts as its dooryard' | trim_lane_stubs accepts a lane end 11 ft behind a house's back wall as reaching its dooryard. | Rule: a lane end must reach something - a way or a dooryard (269 B17, trim_lane_stubs). | yes | `settlement/water_ways/lanes.py trim_lane_stubs + hamletgen/ways web` | Judge an end against the recorded yard and front face only, and have the web carry such an end round the gable. |
| same section, 'A rolled form the sheet never draws' | woodpile_form kizuma rolled on Kashikawa/Kuwabata and none drawn; bath_seat corridor rolled on Mizuguchi and baths drawn unjoined. | Rule: a rolled knob is honored by what is drawn (GM 2026-08-24, checks against what is rendered; meta.woodpile_forms_drawn / bath_seats_drawn now record the gap). | yes | `hamletgen/homesteads/fixtures.py (woodpile and bath seating)` | Offer a form only where a homestead can seat it and fall back per homestead to the next attested form; unit-test rolled form == drawn form or a recorded fallback. |
| same section, 'Eaves woodpiles standing off the wall' (Mizuguchi F2) and 'Woodpiles off the wall also on Kuwabata' | 5-7 of 10 eaves stacks 10.5-27.8 ft from any building on Mizuguchi, 7 of 15 on Kuwabata. | Rule: the eaves form stands against a wall (homesteads eaves woodpile). | yes | `hamletgen/homesteads/fixtures.py woodpile placer (feature-261 outward rungs)` | Try every wall of the steading's own buildings at the wall gap before stepping out; unit-test every eaves stack within the wall gap of a building. |
| same section, 'Coppice lots read as stamped discs' | Coppice lot stocking fills a near-round 12-sided outline edge to edge. | Rule: a lot is bounded by what research/vegetation 140 names (a path, a stream, the slope), no fixed shape. | yes | `hamletgen/hinterland/parcels.py open_ground_patches (lot outline)` | Bound the lot by the nearest path/stream/slope break and roughen the rest; unit-test the outline is not a regular polygon. |
| same section, 'The burial ground beside the title placard' | Burial glyph stood 23 ft from the title placard on its centerline, reading as its ornament. | Rule: the title pocket keeps clear of features (placement keep-clear contract, dev/placement.md). | unknown | `hamletgen title pocket (frame.py) / hamletgen/burial.py` | Make feature glyphs and their clearings keep-outs of the title pocket search; unit-test pocket vs every recorded feature bbox. |
| same section, 'A needle join' (Mizuguchi) | Orphan join lane runs back along the skeleton lane 35 ft at 16 degrees, leaving a ~250 sq ft needle. | Rule: a join meets its way as a T, not a needle (ways/web.py center_lane_ends; 2c defect 2). | yes | `hamletgen/ways/web.py join + tidy` | Square the join at the foot of the prior vertex and keep the skeleton tail as that house's way (name it in the tidy's keep). |
| same section, 'A house at the edge of the lanes' reach' (Kuwabata) | A house 96 ft from the nearest lane (inside WEB_REACH_FT 100, a guess) with a neighbor's back yard between. | Rule: every farmhouse reaches a way (unreached_houses / WEB_REACH_FT); passes by distance while the path crosses private ground. | unknown | `hamletgen/ways straggler pass` | Serve a house whose nearest way lies past a neighbor's yard, not only one past the reach. |
| same section, 'The field path's canal deck runs onto the paddy' | Carried deck's 10 ft LANDING_FT puts the paddy-side end ~7 ft onto a flooded field. | Rule: a deck lands on dry ground (bridges() LANDING_FT, roads_bridge_water). | unknown | `settlement/city/bridges.py bridges() + the field path's crossing form` | A field path over its own canal takes the channel footbridge form (rolled footbridge_form) with short abutments. |
| same section, 'A lane and the connector doubling back' (Kuwabata) | Lane 2 and the connector run back 126 ft 15-40 ft apart at 169 degrees. | Rule: ways do not double back (lanes_bend_like_paths, DOUBLE_BACK_DEG 140); fold_the_connector_hairpin refused by may_write. | unknown | `hamletgen/ways/joints.py fold_the_connector_hairpin` | Start the connector at the lane's earlier vertex, or route the moved start round the steading. |
| future-work/farming-communities.md: ## OPEN 2026-08-24: the web stops exactly one clearance short of the lane it should join | Four Inashiro lanes end 28.1-28.5 ft from the lane they should join (WEB_CLEARANCE 28). | Rule: a link Ts into the way it joins; lanes form one network. WEB_CLEARANCE still registers each lane's corridor against the one being joined. | unknown | `hamletgen/ways web (_lay_web_lane, WEB_CLEARANCE in consts.py)` | Exempt a link's terminal segment from the clearance of the way it joins; unit-test that every link end lies on a way (distance 0), not within a tolerance. |
| future-work/farming-communities.md: ## OPEN 2026-08-24: the field SPUR can be forced onto a house | On tight clusters the spur's final fallback returns its original run over a house (tripwire seed 27). | Rule: no farmhouse stands on a lane (no_farmhouse_stands_on_a_lane, houses_clear_of_lanes). | unknown | `hamletgen/ways track spur_path / _thread_the_fabric` | Rank spur targets by a fabric-clear route and drop the spur rather than draw onto a house; unit-test the fallback never returns a run crossing a footprint. |
| future-work/farming-communities.md: ## 2b. The packer must RESERVE ways | Cohort seeds 5/8/25 strand farmhouses 172-237 ft from any way; reach is repaired only by a re-roll, not guaranteed by the seat or the web. | Rule: every farmhouse reaches the connected way network (unreached_houses, WEB_REACH_FT 100); driver.py records roll_failures farmhouses_reach_a_way and keeps the least-bad re-roll. | yes | `hamletgen/homesteads/stages.py seating + hamletgen/ways straggler pass (+ driver re-roll)` | A post-pack pass that re-seats a stranded steading (or seats only on ground a footpath corridor reaches, counting final fabric); unit-test unreached_houses == [] as a placer postcondition rather than a retry. |
| same section, 'A real defect fell out of the retraction' (cluster_shape) | cluster_shape rolled but not drawn when the frontage seats every household. | Rule: a rolled knob is honored by the drawing (GM 2026-08-24). Partly addressed: stages.py now binds CLUSTER_DRAWN_ASPECT and records cluster_shape_unhonored when a roll does not take. | yes | `hamletgen/homesteads/stages.py (front_row / cluster_seeds)` | Make the frontage seat within the rolled shape's band so the shape is always drawn, and test the drawn bbox aspect against the rolled shape. |
| future-work/farming-communities.md: ## 2b-i. THE SKELETON MUST FOLLOW THE MARGIN | The lane skeleton is a straight chord across a curved seat band; far-arm houses get no lane (the unshipped fix cleared seeds 8/25). Cluster seats on field corners (111-113 deg turns) strand houses. | Rule: every farmhouse reaches a way; _margin_frame's docstring says anything parallel to the field is built on the edge. | unknown | `hamletgen stage_ways skeleton (_margin_frame) + cluster.py seat_cluster anchor scoring` | Map skeleton arms through _margin_frame; add an edge-turn term to seat_cluster refusing a corner. |
| future-work/farming-communities.md: ## 2c. The way-repair passes want ONE design | Corner holes invisible to the aim test, the same break repaired twice around a needle, 4 ft fragments, and a 0-40 ft dead band between generator and check join tolerances. | Rules: lanes do not break mid-run, no doubled way, no fragment under _WEB_MIN_FT, one join tolerance shared by placer and check. | unknown | `hamletgen/ways (_join_orphan_ways, _bridge_collinear_breaks, _serve_stragglers)` | One graph-based repair stage with one declared join tolerance that emits a repair set (straight span before detour); unit-test the finished graph has no hole, doubled pair or sub-minimum run. |
| same section, 'Also found': skeleton arm overruns its last steading | A skeleton arm overruns its last steading by 85 ft because _trim_to_service runs only on web lanes. | Rule: a lane ends at what it serves (lanes_reach_something; trim_lane_stubs). | unknown | `hamletgen stage_ways skeleton / _trim_to_service` | Run the service trim on skeleton arms too; unit-test every non-connector lane end is within reach of a house or way. |
| future-work/farming-communities.md: ## 2f. The shallow-crossing veto must be STREAM-scoped | A link way meets a stream at 17 degrees (seed 47) and its deck cannot span. | Rule: a way crosses water square enough to be decked (bridges_span_their_water / bridges_align_with_their_way). | unknown | `hamletgen/ways _join_orphan_ways (link routing) + settlement/city/bridges.py` | Bend the link locally onto a square crossing where it meets a stream (not a veto); unit-test every stream crossing angle above a floor. |
| future-work/farming-communities.md: ## OPEN 2026-08-19 (latent): the oblique-deck growth loop fails SILENTLY | When no grown or skewed deck clears the water, the original undersized span is drawn anyway. | Rule: a deck clears its water with a landing each side. bridges.py now returns seated=False after skew attempts, but its docstring says the caller still draws the undersized deck. | yes | `settlement/city/bridges.py (deck search) + the way that asked for the crossing` | On seated=False, re-route or bend the way rather than draw; unit-test no drawn deck has a corner in water. |
| future-work/farming-communities.md: ## Review residue from the shared-bund re-roll - 'A tip-angle companion to the area floor' | Basins of 0.55-0.72 cell with 27-30 deg tips read as darts. | Rule: a basin never tapers to a point (research/fields 'Minimum basin SIZE'); tests/gate/test_paddy_fabric.py now checks NEEDLE_DEG on shipped manifests, no placer guarantee of a tip floor. | unknown | `waterfields toe/seam pass` | Add a tip-angle floor to the carve/toe pass's acceptance, placer stricter than the test. |
| same section - '### STILL OPEN ... cohort seed 62's northern lobe' | A well seated in the sweep pad 65 px past the next feature holds the frame open. | Rule: no single feature holds the crop open (crop_not_held_open_by_one_feature; the frame stays tight to content). | unknown | `hamletgen/homesteads/wells.py place_wells` | Score a seat by _worst_after plus the crop extent it adds. |
| same section - 'cohort seeds 9 and 11' | Carve leaves a tapering scrap no weld resolves; paddy_plot_seams_shared fails. | Rules: plot seams shared, basins workable (research/fields 'Bunds are shared'). | unknown | `waterfields/carve.py sector opening` | Stop the carve opening a sector whose boundary collapses onto the collector. |
| same section - E. belt continuity | Inashiro belt canopy thinned to 4.8 ft / one clump over a 45 ft band after the web landed; the road gap's coincidence is unstable. | Rule: village_windbreak_is_continuous (canopy depth per column across the wind). | unknown | `hamletgen/hinterland/belt.py (belt scatter) vs the web` | The belt placer guarantees a minimum canopy depth per cross-wind column except a declared track gap; unit-test it. |
| future-work/farming-communities.md: ## OPEN 2026-08-18: paddy bunds still step sideways; tests/gate/test_paddy_fabric.py test_a_bund_does_not_build_a_flight_of_steps ('Seven of those survive across the pool, each ledgered') | Single bund steps survive on pool rings; cohort seeds 12 (4 steps) and 39 (2 steps) carry staircases. | Rule: paddy_bunds_do_not_stagger (the GM's report; more than one step on a ring fails). The test tolerates single steps and reads only shipped maps; the seam pass does not guarantee it. | yes | `waterfields seams close_seams / _seam_cuts / _unjog` | Keep the weld pitch in register with the fabric so close_seams cannot emit a second step on a ring; unit-test the pass's output on the seed-12 fixture. |
| same section - seed 31's threshing yard laps a paddy | The fit tests a reservation; the south-nudge relaxation moves the bundle so the drawn yard corner lands in a basin. | Rule: harvest yards clear of paddies; the placer tests a rect that is not the drawn one. | unknown | `settlement/rolling/farmsteads.py farmsteads() at _attach_yard` | Re-assert the final yard against the paddy outlines after the nudge and undo the nudge if it fails; unit-test drawn yard vs outlines. |
| future-work/farming-communities.md: ## OPEN 2026-08-19: the kura roll under-delivers 2.2x - FINDING 1; and ## The storehouse share is a positional roll | _hjit positional roll aliases along a front row; pool share 13.6-22% against ~30% (p=0.2993), a re-pack moves it. | Rule: ~30% of farmhouses have a kura (research/homesteads 'Which farmhouses have a storehouse?'). settlement/houses.py still keys it on _hjit(x, y). | yes | `settlement/houses.py kura roll` | Key the roll to the household number with an avalanche hash (_nth_roll in the entry); test the pool share against 0.2993. |
| same section - FINDING 2: a raked house corner bulges into a neighbor's garden | Bundle fit measures unraked rects; the drawn raked corner eats a 2.1 ft margin to a neighbor's garden. | Rule: features_do_not_overlap / gardens_clear_of_structures; rolling/fit.py admits bundle separation 'knows nothing about either house's rake'. | unknown | `settlement/rolling/fit.py bundle fit` | Add a rake-aware house-to-neighbor-garden clearance in the bundle fit; unit-test drawn quads never cross a neighbor's garden. |
| same section - THE WIDTH STEP | One continuous back lane halves its width at a node where nothing happens (a link takes the joined way's width). | Rule: a way keeps its width along a run unless its rank changes. | unknown | `hamletgen/ways link width assignment` | Assign width per connected chain; unit-test no width change at a degree-2 node. |
| future-work/farming-communities.md: ## OPEN 2026-08-19 (waterfields): the paddy area floor cannot see WIDTH | Basins 5.9 ft wide pass the area floor; 9 under 12 ft, 30 under 16 ft on Kashikawa. | Rule: a basin is wide enough to stand in and puddle (research/fields 'Minimum basin SIZE'). | unknown | `waterfields toe pass` | Add a working-width floor (area / longest side) to the toe pass, merging a scrap into its neighbor. |
| future-work/farming-communities.md: ## OPEN 2026-08-19 (small): the notice-board caption's halo notches the lane; ## gate 0617 finds caption notches on five cohort seeds; ## the five caption notches need a 2D seat search; ## ATTEMPTS 8-13 | Tilted boards' captions land on a lane tread (seeds 1, 7, 14, 33, 36); a 1D seat ladder and a board sited where no caption is sitable. | Rule: a caption's box clears the way it stands on by 2 ft (captions_clear_the_ways_they_stand_on). | unknown | `structures/fixtures kosatsuba caption seat + place_kosatsuba (now the feature-266 labels/ placer)` | Verify the labels/ placer treats lane treads as blockers for the board caption and that place_kosatsuba ranks by sitability; unit-test on a tilted board in a lane crotch. |
| future-work/farming-communities.md: ## 2026-08-20: the caption clearance on a CURVED tread | Corner sampling misses a curved tread crossing the caption box edge. | Same caption-vs-tread rule; the fix (segment-to-rectangle) is unverified on curved treads. | unknown | `Settlement.caption_lane_clearance` | Unit-test the measure on a synthetic concave tread crossing an edge between samples. |
| future-work/farming-communities.md: ## OPEN 2026-08-27: the south well stands in the commons, not a dooryard | Inashiro's south well is 100 ft from its nearest house with scrub on every side. | Rule: shared wells drop into the courtyards the layout left (the doctrine in wells.py; 井戸端 dooryards). | unknown | `hamletgen/homesteads/wells.py place_wells` | Prefer a seat inside the house cloud's hull when the worst walk is within ~30 ft of the open-ground optimum. |
| future-work/farming-communities.md: ## OPEN 2026-08-27 (feature 133 T91, WAIVED); l7r/diagram/tools/mapcheck.py TRIPWIRE_EXPECTED | Tripwire seeds 27, 33, 37, 47 failed named checks; the pin table is EMPTY since the battery was deleted, so the defects have no reader. | Rules: village_grove thins around a plot inside the band (seed 33), orphan joiner accepts short links (seed 37), lane bends and bamboo off lanes (seed 27). The waiver lapsed with the battery, not with a fix. | unknown | `hamletgen/hinterland village_grove; hamletgen/ways _touch_junctions; ways smoothing` | Re-measure the four seeds with the migrated tests; move each surviving defect into its placer's unit test. |
| future-work/farming-communities.md: ## Carve the paddy around an in-field grave island | The mound is drawn over an intact lattice; three plot rings and nine junctions lie under it. | Rule: the flat paddy tiles around the grave (registry entry); features.py now labels drawing over the lattice a map drawing convention. | yes | `settlement/fields/features.py _plot_grave_island + the toe pass` | Carve the plots around the grave where the toe pass builds them, as for the pond. |
| future-work/farming-communities.md: ## Two checks that pass VACUOUSLY - woodland | Sawada and Kashikawa roll zero woodland parcels. | Rule: a farming village held worked woodland (iriai; research/vegetation); the scan finds no legal seat on a tight sheet. | unknown | `hamletgen/hinterland/parcels.py open_ground_patches` | Guarantee at least one parcel (a smaller floor or a set-back seat) and test count >= 1 on every roll. |
| same section - windbreak counts the record, not the ink | A belt drawn 57 px short of the page with 37 recorded clumps undrawn passes. | Rule: the belt is continuous as drawn (GM 2026-08-24: check what is rendered). | unknown | `hamletgen/hinterland/belt.py trim vs the final crop` | Trim the belt record at the final crop so record == ink; test drawn clumps. |
| future-work/farming-communities.md: ## Eight tree trunks stand in a tread on Moritono | Placer constrains clump centers while crowns are drawn scattered (median 8.1 ft), so drawn trunks can stand in a tread. | Rule: a trunk may not stand in a path (groves_clear_of_lanes, GM feature 157). Moritono itself is a legacy map, but the mechanism is the live village_grove scatter. | unknown | `hamletgen village_grove crown scatter` | Test each drawn crown's trunk against the corridor at scatter time; unit-test drawn tree_crowns vs treads. |
| future-work/farming-communities.md: ## SEED 45'S WINDBREAK PIN; tests/gate/hamletgen/test_driver.py GATE_COHORT_EXPECTED comment | Seed 45's windbreak continuity failure is unverified since the pin moved out of the gate. | Rule: village_windbreak_is_continuous. | unknown | `hamletgen/hinterland/belt.py` | Roll seed 45 against the belt placer's own continuity predicate; fix the placer or carry a strict xfail. |
| future-work/farming-communities.md: ## A tree stands in a path on the reference hamlet | Three trunks 3.1-4.2 ft from Inashiro's straggler footpath centerline (bar 4.0). | Rule: groves_clear_of_lanes (trunk 4.0 ft). The straggler router's obstacle set lacks recorded crowns. | yes | `hamletgen/ways straggler router (_homestead_polys obstacle set)` | Add M['tree_crowns'] circles to the footpath's obstacles, or refuse a tread within 4 ft of a trunk. |
| future-work/farming-communities.md: ## The windbreak's far limb, where a cluster sits in two groups | On Inashiro 63 of 308 belt crowns stand over 200 ft from any farmhouse (furthest 518 ft). | Rule: the belt shelters the houses on the windward fringe (belt_polygon's own docstring). | yes | `hamletgen/hinterland/belt.py belt_polygon` | Sample cross-wind columns that contain a house and end the belt where its column is empty (two belts for a split cluster). |
| future-work/farming-communities.md: ## A garden may be seated on an in-field ditch | The bundle has no in-field channel keep-out; the stub was holding the ground a garden would otherwise take. | Rule: features_do_not_overlap (a garden never on a ditch). | yes | `homestead bundle fit + hamletgen/water/comb.py corridors` | Give the bundle rect the in-field channel keep-out the houses carry, then drop sub-stride stubs. |
| future-work/farming-communities.md: ## Two ways that meet where the material changes | Polder toe canal ends 3 ft short and 2.5 ft off the drain trunk's centerline. | Rule: a watercourse joins the one it feeds at its centerline (as feeder/lateral junctions do). | unknown | `hamletgen/water/polder.py ring corner builder` | End the toe on the drain's centerline; unit-test endpoint-on-centerline at both corners. |
| future-work/farming-communities.md: ## The weir's root lands on the head race's mouth | 17% of the weir bar lies on the head race; the Weir modal says it runs from the mouth. | Rule: the weir's root keys into the bank at the mouth's upstream lip (Weir class docstring). | yes | `hamletgen/water/brook.py weir seat` | Root the bar at the mouth's upstream lip; unit-test zero bar area inside the race band. |
| future-work/farming-communities.md: ## The toe marsh's recorded outline is not the drawn marsh | marshes[0].poly keeps the unclipped ring, so the belt cannot be kept off the marsh (68 of 179 belt crowns inside it on Sawada). | Rule: woody cover stands on dry ground above the marsh (research/vegetation; the copse test in test_pool_261). | yes | `settlement/land/wet.py marsh record + hamletgen/hinterland/belt.py` | Record drawn_poly and have every grove and parcel test against it; then give the belt the copse's keep-out. |
| future-work/farming-communities.md: ## Five finished-map rules no placer guarantees - stepped bund | A paddy bund built as a flight of steps (tests/gate/test_paddy_fabric.py). | Rule: paddy_bunds_do_not_stagger; asserted on the finished pool only. | yes | `waterfields seam pass` | Make it a seam-pass guarantee with a unit test (see the bunds item). |
| same section - woodland parcels in a ruled row | Three woodland parcels in a ruled row on Kashikawa (test_pool_261). | Rule: no three coppice lots on one line (settlement-reviews 2026-08-18, feature 261). | yes | `hamletgen/hinterland/parcels.py (seat_off_the_row)` | Apply in_a_ruled_line as a seat refusal inside open_ground_patches; unit-test the layout. |
| same section - copse clump off its house's bank | A copse clump within reach only across the brook (Inashiro). | Rule: every copse clump has a house within reach on its own side of the brook (test_pool_261). | yes | `homestead groves copse seat` | Test the bank side at seat time. |
| same section - brook legs within 1.6 degrees of a screen axis | Brook legs near-axis-aligned on Kashikawa and Sawada. | Rule: a brook wanders, no leg on a screen axis (test_pool_261). | yes | `hamletgen/water/brook.py wander` | Reject or perturb an axis-aligned leg in the wander. |
| same section - Sawada's seat off the regional northwest | Seat not facing the regional wind (test_pool_wind.py). | Rule: the seat faces away from the regional northwest wind (feature 261). | yes | `hamletgen/cluster.py seat scoring` | Make the wind term a hard constraint or bounded band in seat_cluster, with a unit test. |
| future-work/cross-cutting.md: ## The caption-over-a-building rule was cut | No check measures a caption against a building it does not name; Kuwabata's board caption 2.24 px from a built glyph. | Rule: a label must not sit on a feature it does not name (the retired labels_clear_of_other_buildings). Feature 266's single labels/ placer scores captions against every subject but its own, which may now guarantee it; the registry apparatus decision is the GM's. | unknown | `l7r/diagram/labels/ (the one caption placer)` | Confirm the labels/ placer's cost blocks every built glyph on hamlets and the generated Mode A sheets; unit-test a caption next to a foreign roof. |
| tests/gate/hamletgen/test_driver.py ACREAGE_SHORT (seeds 45, 47), test_a_rolled_cohort_passes_the_whole_gate | Seed 45 reaches 18.6 of 22.1 acres, seed 47 21.9 of 26.0; the 15% acreage assertion is skipped for them. | Rule: paddy acreage lands on the figure the household count implies (research/fields 'Acreage from population'; the 15% band in the same test). The envelope clamps the fan at every aspect for a large household count at that fall. | yes | `hamletgen/water fit_field + canvas/envelope sizing (plan_site)` | Grow the canvas/envelope (or change archetype) when the largest fan cannot reach the target, and unit-test acreage within band on a large-household, steep-fall spec. |
| tests/gate/hamletgen/test_driver.py:109 (and tests/soak/test_polder_fall_0.py:113) - placed >= round(0.85 * households) | The test accepts a hamlet seating 85% of its declared households. | A rule, not a bare excuse: research/settlements 030 states the band 0.85-1.05 occupied farmhouses per declared household and 'aims at one apiece'. But the seating stage only records a shortfall (stages.py docstring) - no placer guarantees even the 0.85 floor; it is asserted on rolled maps. | yes | `hamletgen/homesteads/stages.py stage_homesteads (front row, cloud, widening rounds)` | Make the seating stage keep widening its candidate ground until the band is met (or fail the roll loudly); unit-test placed/households >= 0.85 on a tight-ground spec. |
| tests/soak/test_seed_43_kink.py (strict xfail) and tests/gate/test_cohort_lane_rules.py | Seed 43's routed footpath keeps a 36 px lattice step round a house corner; the lane-bend rule is asserted only on the coverage rolls, with seed 43 moved to the soak tier. | Rule: lanes bend like paths - no two real turns inside 40 ft, nothing past 140 deg (lanes_bend_like_paths, _kinks). The router's chord/knee cannot take the step. | yes | `hamletgen/ways/route.py lattice step removal (_clear_touch / chord)` | Post-process routed runs so no kink survives (chord with a fabric-aware detour); unit-test the kink geometry in specs/215 census/kink-seed-43.json. |
| l7r/diagram/hamletgen/driver.py re-roll loop (tests/gate/hamletgen/test_driver.py test_a_map_that_strands_a_farmhouse_is_re_rolled_with_that_ground_forbidden) | Farmhouse reach is enforced by re-rolling with stranded ground forbidden and keeping the least-bad attempt; a map can still ship with meta.roll_failures farmhouses_reach_a_way. | Rule: every farmhouse reaches the way network (ways.unreached_houses). A retry is not a guarantee; driver.py's comment calls it 'the one thing no placer can promise in advance'. | yes | `hamletgen/driver.py + homesteads seating + ways straggler pass` | Same as the 2b item: a post-pack re-seat of the stranded steading so the finished roll always satisfies unreached_houses == []. |
| tests/hamletgen/test_pool_261.py test_the_board_caption_notches_no_crown ('or meta.kosatsuba_caption_level == 1') | A board caption may lie on a crown when the siter records that no seat offered a clear one. | Rule: the caption halo notches no crown (settlement-review, features 230/261); the level-1 fallback is excused by the GM's 2026-08-29 allowance for a board under canopy with a visible label, so the placer does not guarantee a clear caption. | yes | `structures/fixtures/siting.py place_kosatsuba + the board caption seat` | Rank board positions by a crown-clear caption seat so level 1 cannot occur, or have the GM confirm the fallback is the rule. |
| tests/soak/test_polder_fall_0.py test_a_polder_hamlet_draws_its_grid_dike_and_reservoir docstring; hamletgen.md 'down to two named failures' | The polder grid is WIP with two named gate failures in build_polder's own geometry; the test deliberately does not assert a clean gate, and no pool map is a polder grid. | The polder_grid archetype is a live hamletgen path (coverage rolls Polder 12/19); the two failures are not named in the test and the soak tier rarely runs. | unknown | `hamletgen/water/polder.py build_polder` | Name the two failures, make each a build_polder unit test, and assert the clean placement properties on the polder roll. |

## R4 - What the gate costs before the work (2026-09-29)

**Method** (observed 2026-09-29, method: `make durations` in the clone before any 287 engine change, load 1.3): 5,258 tests
passed, 12 skipped, in 57.13 s. The slowest, which FR-007 and SC-005 weigh against what they guard:
    10.10s call     tests/gate/test_bunds_and_dikes.py::test_every_beaded_bund_segment_shows_at_least_two_beads[kashikawa.gen.py]
    10.09s call     tests/gate/test_bunds_and_dikes.py::test_every_beaded_bund_segment_shows_at_least_two_beads[sawada.gen.py]
    9.85s setup    tests/gate/test_bunds_and_dikes.py::test_no_bund_is_drawn_down_the_middle_of_a_supply_channel
    5.68s call     tests/gate/test_bunds_and_dikes.py::test_every_beaded_bund_segment_shows_at_least_two_beads[mizuguchi.gen.py]
    5.32s call     tests/hamletgen/test_homesteads.py::test_the_free_ground_changes_no_seat[rescue-dispersed]
    4.77s call     tests/test_engine_ast.py::test_the_four_scans_parse_each_file_once
    4.61s call     tests/gate/test_bunds_and_dikes.py::test_every_beaded_bund_segment_shows_at_least_two_beads[kuwabata.gen.py]
    4.31s call     tests/tools/test_pack_audit_sun.py::test_the_red_fixture_fails_naming_the_wood
    3.08s call     tests/tooling/test_incremental_gate.py::test_the_fast_core_keeps_every_context_once_its_events_are_re_armed
    2.97s call     tests/settlement/test_exact_pieces_284.py::test_the_board_sampled_verge_first_is_the_board_sampled_whole
    2.95s call     tests/tools/test_registry.py::test_every_check_fires_on_its_red_fixture[garden_sun]
    2.79s call     tests/tools/test_registry.py::test_every_check_passes_the_pool_sheets_of_its_tiers[garden_sun]

## R5 - P0: the measurements owed before building (2026-09-29)

**The polder grid's "two named failures" (water W48).** The record names and closes them: `hamletgen.md` ("Where it stands:
the polder DRAWS and is down to two named failures ... BOTH OF THOSE ARE NOW FIXED" - `paddy_bunds_clear_the_collector`,
`build_polder` never calling `hem_to_bank`, and the second the same section names) (observed 2026-09-29, method: reading
`hamletgen.md`'s polder section and `tests/soak/test_polder_fall_0.py`). What survives is the soak test's docstring carve-out
("this does not assert a clean gate, which would be a lie"), stale since; W48 is therefore an excuse to remove (FR-006): the
polder roll is held to every placement rule like any other.

**The seats today (D2's stand-in count)** (observed 2026-09-29, method: `p0/harness.py`, the pool and cohort seeds 1-48, each
through `generate`; `p0/results.json`): all 53 maps seat every household, every one draws its connector, none fails; eight
re-roll to get there - cohort seeds 6, 8, 19, 33, 38 and 42 once, 23 twice, 45 three times. Those re-rolls are what M3's
corridor must make unnecessary; the count that decides D2's question is P3's, under the new placer.

**The field pond's count (D9)** (observed 2026-09-29, method: reading `settlement/fields/features.py:_paddy_features`): it is
ROLLED - `rng.random() < 0.55` per valley field with low plots, a disclosed calibrated liberty - and when the roll says yes
and no low plot takes a legible pond, nothing is drawn. So D9 applies: the roll is taken only over the fields where some low
plot can hold a pond (the fits found first, then the roll), and a rolled pond is always drawn.

**What P0 leaves to the phases that build the mechanisms.** Three of P0's counts are of what a new mechanism LEAVES, so they
are taken where the mechanism lands, before anything depends on it: the belt cases D8 leaves (with P5's belt guarantee), the
seats D2 refuses (with P3's corridor and capacity), and the board terminal (with P6's strict caption predicate). Seed 31's
yard over a paddy is not measured separately: homes H44 guarantees the yard clear of every paddy as drawn whatever it reads
today, and P9's sweep checks it.

## R6 - The maps as the work moves them (2026-09-29)

**After M2 (T05: the brook rounded once, before the homesteads)** (observed 2026-09-29, method: `make maps SCOPE=all`, each
manifest compared with the one committed before): Inashiro, Kashikawa and Mizuguchi re-seat (houses, lanes and what stands
among them move, since the seats now read the finished course); Sawada moves only its site boundary's record; Kuwabata is
unchanged. Every map seats every household in one roll. The pool's rule tests then fail two rules on Mizuguchi -
`test_an_entrance_board_stands_at_the_entrance` and `test_every_lane_crosses_the_brook_square` - both rules this feature
guarantees (labels, P6; ways, P4); the regressed state stays in the clone until they land.

**At acceptance: the pool as the green gate regenerated it** (observed 2026-09-29, method: each hamlet's committed
manifest at bf705bee3 against `git show 153bcc6e6^:<path>`, the tree before feature 287; positions compared relative to
the centroid of the field's outline, since the canvas itself grew; the scripts are in the session's scratchpad and not
kept). The comparison spans feature 280 as well, merged into this feature (R8, "Merged with feature 280"), so each
change below is attributed to the mechanism that made it.

What moved on all five, and why:

- **The canvas.** Every canvas grew about 1.9 times a side (Inashiro 2,900 px square to 5,550; Sawada 3,300 to 6,350;
  observed 2026-09-29, method: `meta.W` and `meta.H` of the manifests compared above):
  the canvas now holds the field and, on every side, the seat with its belt (`plan.py`, homes H31, plan D8). Absolute
  coordinates therefore all change; the views changed less (below).
- **Every house re-seated.** 82 of 82 farmhouses stand more than 10 ft from their old seat relative to the field. The
  seat band is chosen by the seating pass itself and a household is seated only with its parts, its access corridor and
  its wood share inside its envelope (M3, M5, plan D2); 280's 25-tsubo yards widened the ground a homestead takes to
  104 ft (R8). No house is quarter-turned any more (`house_quarter_turns` 1-4 to 0: 280, M26).
- **The ways.** Every map records its access corridors (16-24 a map, `access_corridors`, none before) and the web's
  settle (`meta.web_settle`): 2-3 rounds, 3-15 lanes changed, and 3-12 houses the lanes had not reached before the
  settle drew their corridors, 0 after. Every map seats every household and records no `roll_failures`; the
  `roll_attempt` / `roll_after` fields are gone with the re-roll (M3, T66).
- **The woods.** The copse grew on every map (41-225 clumps to 264-546) and the drawn homestead wood now stands at 93-112%
  of its rolled area, against 49-85% before (`meta.homestead_wood_ft2`): each household's share of the wood floor is
  reserved at seating and planted first (woods W25; future-work 269 B26). Bamboo stands fell (4-7 to 0-1 on four maps)
  where the thicket and the household strips give way to the reserved copse seats (280's two-crown keep-out, carried
  through `stand_spares_seats`).
- **What 280 removed.** No hamlet draws a burial ground of its own (`cemeteries` 1 to 0 on Inashiro, Kashikawa and Kuwabata; M68); fewer
  woodpiles and baths are drawn (`farm_fixtures` 42-75 to 36-58: the wood shed's quota to the larger houses, the bath a
  room joined to the house) and fewer farm sheds (3-10 to 2-3).

Per map (figures in ft; "houses" is the move of each house from its nearest old seat, relative to the field):

| hamlet | houses: median / max; cluster centroid | lanes: count, length | board: seat, from the cluster's centroid | woods: drawn / rolled sq ft; belt, copse clumps | field |
|---|---|---|---|---|---|
| Inashiro | 66 / 220; 71 | 11 to 15; 6,306 to 7,047 | entrance; 305 to 320 | 10,539 / 13,059 to 13,458 / 14,493; belt 283 to 234, copse 120 to 387 | 19.62 to 19.52 acres; 624 to 599 plot rings; dry plots 2 to 83 (the winter-crop knob narrowed to what the site can feed, water W36, R7: 12.84 acres of coarse grain against a need of 12.75); cluster shape crescent to round, declared as drawn (plan D4) |
| Kashikawa | 114 / 440; 190 | 16 to 21; 6,715 to 8,409 | entrance to center (`kosatsuba_seat_unsitable: entrance`: the knob resolves only over placements the map can site, labels L1); 485 to 241 | 8,658 / 11,523 to 15,123 / 16,142; belt 229 to 362, copse 225 to 546 | 25.22 to 24.91 acres; 786 plot rings, unchanged; cluster shape recorded unhonored (elongated) to crescent, declared as drawn; winter crop barley only (a cleared fan, R7) |
| Kuwabata (polder) | 144 / 383; 128 | 11 to 13; 5,908 to 3,628 | center, as before; 51 to 256 | 6,441 / 13,030 to 13,665 / 13,749; belt 178 to 208, copse 112 to 452 | 19.13 to 21.22 acres (the polder fit lands in its band or is refused); 29 to 35 parcels; its three woodland parcels recorded off the sheet to the north (`meta.woodland_offsheet`, plan D11); a fry village (280, M60); retirement houses 7 to 4 |
| Mizuguchi | 100 / 292; 139 | 9 to 13; 5,866 to 6,484 | entrance, as before; 371 to 309 | 10,682 / 12,534 to 16,250 / 14,537; belt 260 to 345, copse 41 to 264 | 14.64 to 14.62 acres; 444 to 432 plot rings; its field grave not drawn on this roll (`field_graves` 1 to 0); field path run on to joined |
| Sawada | 2,103 / 2,350; 2,338 | 13 to 18; 6,460 to 7,531 | entrance, as before; 768 to 618 | 9,879 / 13,422 to 13,804 / 14,731; belt 381 to 275, copse 149 to 543 | 23.47 to 25.14 acres; 1,000 to 1,051 plot rings; the cluster moved from the field's west flank (bearing 161 degrees from the field's centroid) to its north-east margin (-53 degrees), half as far from the field's center (1,618 to 809), the seat chosen by the seating pass over the margins in rank order (plan D2); cluster shape recorded unhonored (elongated) to crescent, declared as drawn |

The views (w x h px): Inashiro 1,924 x 2,030 to 2,588 x 2,010; Kashikawa 1,751 x 2,570 to 1,737 x 2,641; Kuwabata 955 x
2,281 to 1,229 x 2,454; Mizuguchi 1,796 x 1,192 to 1,984 x 1,195; Sawada 3,012 x 1,498 to 2,481 x 1,932. Every map keeps
its households (15, 20, 16, 12, 19), its archetype and its forms; the kinds it draws change only where a mechanism above
says so (FR-009).

## R7 - Decisions recorded during implementation (2026-09-29)

Each is recorded where it arose as well (the pointer at the point of change); this is the feature's list, for the
Decisions review and for what goes to the GM once the work runs.

- **water:W26 / W27 (a plot's working width, the dart) - RECORDED, not enforced; a guess held open.** The research
  entries `fields/023` and `fields/025` describe irregular hill-foot plots narrower and sharper than the old thresholds
  allowed, so a placer that refused them would draw against the record. `ring_rules.narrow` / `dart` report them and no
  placer refuses on them. Cost: a plot a reader finds implausibly thin is not prevented. Alternative priced: enforcing the
  old thresholds (contradicts the record). Chosen by the session; for the Decisions review.
- **water:W36 - needed a physical research pass** before any guarantee (the design row names the question); the pass was
  run in wave 4 (research/fields/165, all four checks applied), and the guarantee that followed is the knob recorded below.
- **labels:L6 applies at ring 0 only** (the crown obstacles are the tree ring the caption would cover; outer rings are
  scatter the placer already treats as soft). Map drawing convention.
- **labels:L14(b) treats the canvas as the view** on Mode A sheets, which have no crop. Map drawing convention.
- **Mode A area captions take a holder waiver**: a room's caption sits inside its room by definition, so the "not over
  another feature" rule excludes the caption's own holder. Map drawing convention.
- **D12, the board terminal** ("no verge takes a board with a clean caption"): kept, marked for the GM; the count over the
  pool, cohort 1-48 and the Mode A sheets is **0 of 53** maps (the labels implementer's run, 2026-09-29). Mizuguchi's
  board moves from its entrance to the center: the knob now resolves only over placements the map can site.
- **The fan envelope's fold (seed 27)**: an outline the floor trim folds is reduced to its largest valid polygon at the
  outline's making (`ring_rules.simple_outline`), keeping all the fan's ground; historically neutral (a drawing repair).
- **water:W36, the winter-crop knob narrowed to what the site can feed** (as D4 narrows the cluster shape): a form is
  offered only where its coarse-grain need fits the ground the map draws for it. Measured over cohort 1-60 and four pool
  hamlets: every wild fan (44) offers both forms; every cleared fan (20, Kashikawa and Sawada among them) offers `barley`
  only, since its dry ground is the toe strip alone (2.5-5.2 acres against a need of 8.5-17). Cost: the bare-winter form
  never appears on a cleared fan. Alternative priced: a deep reserve on cleared ground (no research places it). Chosen by
  the session; for the Decisions review.
- **Wave 5, water: what a placer does when its candidates run out (FR-005)** - every one a refusal by name, none a kept
  violation; measured 2026-09-29 over cohort 1-60 and the pool, none fires. The fan (`fit.py:fit_field`): the search is
  widened to every aspect in full, then `FieldRefused` - the canvas is not grown, because it is `plan.py`'s decision
  (HOMES') and no fan needed it (worst 6.7% of the 15% band). The sty (`pondstock.py`): `StyRefused` where no near-half bank
  seat of any grow-out pond fits, at the reservation or at the stage. The feed brook (`brook.py:feed_brook`): the routes
  round the field from every bearing on both skirts, then `BrookRefused`. The feed hairline (`fields/comb.py`): a snap
  that would leave it level is not taken; one that climbs from the sluice is refused (by construction it never does).
  The drain's pond (`sink.py:pond_seat`): a seat whose ditch crosses the brook is no seat, and past the last the field
  drains off the frame (the existing fallback); six maps moved their pond to the other side of the outfall, none lost it.
  The constructed drain route meeting the brook where the drawn brook breaks a rule: `SinkRefused`. Historically neutral
  (refusals of drawings the rules forbid); chosen by the session, for the Decisions review.
- **D12's terminal takes D10's form** (labels, wave 5): where no verge takes a board with a clean caption, the caption
  goes on a leader or in the sheet's key (`board_seat.terminal_caption`), never at the retired least-cost seat, which could
  lie across a lane; a seat whose key mark would lie on a way is refused, and where none clears the ways no board is
  posted, as when no verge fits. The GM's question stays marked (`meta.kosatsuba_d12`); the count reaching it is 0 of 53.
  Map drawing convention; for the GM with D12. (The figures in this list: observed 2026-09-29, method: `make cohort N=60` and the implementers' per-seed harnesses in the clone, as each entry says.)
- **water:W39, the paddy cell's 0.030-0.072 acre band - a RECORDED DROP on the hamlet path** (the gate doctrine: a rule
  about a map no scripted generator produces is a recorded drop with its grounding kept). The band is the village and city
  calibration (`waterfields/palette.py`: "DELIBERATELY NOT applied to hamlets/towns"; research/fields/110 gives a
  pre-modern plot as 0.02-0.25 acre), and the hamlet keeps the GM's pixel grain (`Settlement.plot_texture`, "by GM
  request"; its small cells 0.023-0.026 acre, measured over cohort 1-60 on 2026-09-29, method: the fits' own plots, which
  match the SVG measure within 0.0001 acre). No scripted generator draws a village or a city today; those tiers are the
  frozen hand-drawn pool, and the band becomes a placer guarantee in the village tier's conversion
  (`migration-plan.md`). `tests/full/test_villages.py` keeps the band as that tier's guard. Map drawing convention;
  decided by the session on the GM's standing ruling (the pixel grain).
- **woods:W26, what a coppice lot's line followed - HELD FOR THE GM.** The not-a-disc half is guaranteed by construction
  (`hinterland/parcels.py:_parcel_outline`); the bounded-by half has no attested form to build. research/vegetation/140
  labels it a GUESS after a 2026-09-27 search pass, and a second pass (2026-09-29: 割山, 山割, wariyama, 入会山 with 尾根,
  沢 or 道 and 村絵図, 平地林 with 境木 and 武蔵野; kotobank, the Gakugei Musashino lecture, the J-STAGE Wariyama
  abstract) found no page stating what a lot's line followed. The record is silent, so it is the GM's question; the
  engine draws the not-a-disc form until the GM answers.

## R8 - Tests retired and kept (2026-09-29)

**Method** (T84, T85; FR-006, FR-007, SC-005). Every finished-map test in `tests/gate/`, `tests/hamletgen/test_pool_*.py`,
`tests/full/`, `tests/soak/` and the candidates the design rows and the implementers named were read by five Opus
readers against the code: for each, the placer that decides the rule (the line that refuses, repairs or constrains) and
the unit test that drives it on constructed input INCLUDING the violating case. A test was retired only where both were
found; otherwise it was kept and its reason is below. Every figure is **observed 2026-09-29, `make durations FULL=1
MARK="rolls_map or not rolls_map"` in a detached worktree at 0e792a665** (5,871 passed, 6 failed, 256 s wall; the failures
are listed under "Found on the way"). A figure is the test's call plus setup summed over its parameters; `<0.005` is under
pytest's print floor. A pool-reading test's setup includes the pool map's roll when the cache is cold, and that roll is
SHARED by every reader of the map: Inashiro's cold obtain landed on `test_no_watercourse_crosses_another_mid_run`'s setup
(18.60 s) and is paid by whichever reader comes first, so no retirement here frees it. The soak tier is collected by no
ordinary run and costs the gate nothing.

**Totals.** 84 test functions retired from the gate and quick trees (82 finished-map tests and their helpers'
self-tests, and 2 unit tests in `tests/settlement/structures/test_fixtures.py`), plus 6 soak tests and a soak seating
variant; 10 clauses retired from kept tests; 3 whole modules deleted
(`tests/gate/test_cohort_lane_rules.py`, `tests/hamletgen/test_pool_282.py`, `tests/soak/test_seed_43_kink.py`) with the
helper only they needed (`tests/test_villages.py:_channels_under_plots`, the `woodland` fixture, the `comb` and
`kuwabata` fixtures of their modules, the seatings' lane variant). **Measured cost retired: 228.6 s** of test time per
full gate run, of which 216.45 s is one unit test (below); the finished-map tests themselves cost 10.4 s together
(the beads' 5.57 s the largest). One replacement unit test was added for two lines only the retired board tests reached
(`siting.py:371-372`): `test_fixtures.py::test_an_anchored_board_with_no_handover_keeps_to_the_seats_nearest_its_anchor`,
0.02 s (observed 2026-09-29, a direct call in the clone). (Totals observed 2026-09-29, method: `make durations FULL=1` in a detached worktree at 0e792a665.)

### Retired

| retired test | s (observed 2026-09-29, method: `make durations FULL=1` in a detached worktree) | the placer that now decides it, and its unit test on the violating case |
|---|---|---|
| gate/test_bunds_and_dikes::test_no_bund_is_drawn_down_the_middle_of_a_supply_channel | 0.10 | `seams/close.py:hold_ring_rules` via `ring_violations` "stroke"; test_ring_guarantees::test_no_bund_is_left_down_the_middle_of_a_supply_channel |
| ::test_no_bund_is_drawn_across_the_collector | 0.01 | the same, "collector"; test_ring_guarantees::test_no_bund_is_left_across_the_collector |
| ::test_every_bund_bead_sits_on_visible_ground | 0.05 | `fields/comb.py:settle_beads` at the finish; test_field_guarantees::test_finish_settles_every_bead_the_last_water_drowned... |
| ::test_every_beaded_bund_segment_shows_at_least_two_beads (5 maps) | 5.57 | `waterfields/carve.py:bead_runs`; test_core::test_bead_runs_split_at_a_drop_and_a_part_of_one_bead_goes |
| ::test_bead_segments_derivation_fires | <0.005 | the helper's self-test; goes with the test above |
| ::test_dry_plots_share_a_row_direction_within_a_tract_and_change_it_at_the_seams | 0.23 | `waterfields/hem.py:settle_tract_seams`; test_furrows::test_a_second_band_tract_turns_off_every_tract_it_abuts |
| ::test_the_tract_judge_fires_on_a_split_tract_and_a_blurred_seam | <0.005 | moved with the judge: test_furrows::test_the_tract_judge_names_a_tract_run_apart... |
| ::test_the_polder_dike_is_a_hand_piled_earthwork | 0.07 | `land/dikes.py:hand_piled_widths`; test_land::test_a_flat_dike_profile_is_stretched_until_it_reads_hand_piled |
| ::test_nothing_is_built_on_the_dike | <0.005 | the dike keep-out in the site boundary (`rolling/fit.py:_rect_blocked`); test_land::test_a_homestead_is_refused_inside_the_dike_keep_out |
| ::test_no_channel_is_cut_through_the_dike_except_at_its_gaps | 0.01 | `water/polder.py:gaps_for_courses`, `sink.py:breaches_any_dike`; test_water_287::test_the_route_refusals_name_the_dike |
| gate/test_paddy_fabric::test_every_ditched_paddy_has_a_floor_under_its_plots | 0.05 | `fields/comb.py:draw_comb_field` (the floor unconditionally); test_field_guarantees::test_every_ditched_comb_draws_its_floor_under_its_plots_and_names_its_water |
| ::test_the_floor_stops_where_the_command_area_does | <0.005 | `waterfields/comb.py:_comb_floor_and_winding`; test_trunks::test_the_floor_stops_where_the_command_area_does |
| ::test_no_basin_tapers_to_a_point | <0.005 | `hold_ring_rules` "needle"; test_ring_guarantees::test_a_needle_no_neighbor_can_take_is_left_bare |
| ::test_a_flooded_plot_reads_as_a_basin_and_not_as_a_pond | <0.005 | the same, and the raw tint re-judge; test_ring_guarantees::test_a_needle_hidden_from_the_deduplicated_ring_is_judged_raw |
| ::test_no_basin_is_too_small_to_be_worth_its_own_bund | <0.005 | "area" and the refused neck trade; test_ring_guarantees::test_a_scrap_under_the_area_floor... |
| ::test_the_rings_double_count_only_marginally | 0.05 | the seam partition; test_ring_guarantees::test_lapping_carved_plots_come_out_counted_once |
| ::test_a_bund_does_not_build_a_flight_of_steps | <0.005 | `_split_steps`; test_ring_guarantees::test_the_whole_seam_pass_hands_back_no_staircase |
| ::test_every_recorded_plot_ring_is_a_simple_polygon | 0.01 | `_repair_crossing_rings`, "crossing"; test_ring_guarantees::test_no_recorded_ring_crosses_itself |
| gate/test_water_flow::test_a_collector_discharges_at_its_lowest_point | <0.005 | `waterfields/comb.py:_comb_drain`; test_trunks::test_a_collector_never_runs_uphill_even_where_its_head_draws_the_worst_jitter |
| ::test_the_runoff_leaves_the_outfall_downhill | <0.005 | pond and drain run: `sink.py` pond seat and route refusals; test_sink::test_a_pond_sink_draws_a_ditch_ending_on_the_pond. Its brook clause judged nothing on the fixture (no brook within 60 px of Inashiro's outfall) - see "Gaps" |
| ::test_no_stream_runs_through_a_field | <0.005 | `water/brook.py:feed_brook`, "enters"; test_brook::test_a_course_through_the_field_is_moved_out... |
| ::test_every_field_shows_where_its_water_comes_from | <0.005 | `draw_comb_field` records the ditches unconditionally; test_field_guarantees (as the floor) |
| gate/test_water_junctions::test_every_lateral_lands_on_a_trunk_at_both_ends | 0.05 | `waterfields/polder.py`'s tip snap; test_polder_ring::test_every_lateral_lands_on_a_trunk_at_both_ends (a wandered build; the weakest of these) |
| ::test_a_channel_declaring_a_stream_actually_reaches_its_bed | <0.005 | the intake snap, `round_the_brooks`; test_field_guarantees::test_an_intake_declares_a_stream_only_where_its_mouth_reaches_one |
| ::test_courses_that_meet_are_composited_as_one_confluence | <0.005 | `settlement/finish.py`'s one water stack; test_finish_287::test_no_bed_is_painted_above_a_sheen_and_the_pond_fill_over_every_mouth |
| ::test_the_pond_fill_is_drawn_over_the_mouths_that_join_it | <0.005 | the same |
| ::test_the_pond_is_connected_to_the_field_it_serves | <0.005 | `sink.py`'s pond run; test_sink::test_a_pond_sink_draws_a_ditch_ending_on_the_pond |
| ::test_a_field_pond_is_sunk_into_one_plot | <0.005 | `fields/features.py:_pond_fit` (`ring_meets_ellipse`); test_fields::test_plot_pond_refuses_a_neighbor_corner_inside_the_rim... |
| gate/test_lane_network::test_every_lane_belongs_to_one_network | 0.05 | `ways/settle.py:settle_network`; test_settle::test_a_piece_off_the_network_goes_and_so_does_a_husk |
| ::test_no_lane_doubles_back_or_kinks | <0.005 | `settle_shapes` (`kink_spans`); test_settle::test_seed_43s_lattice_step_is_a_kink_the_old_bend_test_passed |
| ::test_no_two_lanes_meet_end_to_end_in_a_fold_and_no_lane_ends_in_a_hook | <0.005 | `settle_ends`, `settle_shapes`, `Lawful`; test_settle::test_a_fold_at_a_joint_becomes_a_tee..., ::test_a_hook_is_relaid_as_a_tee... |
| ::test_every_lane_end_reaches_something_worth_walking_to | 0.06 | `settle_dangling`; test_settle::test_a_lane_end_in_open_ground_is_trimmed_and_a_lane_serving_nothing_goes |
| ::test_a_farmhouse_discharges_one_lane_end_not_three | <0.005 | `settle_ends` (`DOORSTEP_MAX`); test_settle::test_a_farmhouse_discharges_two_lane_ends_not_three |
| ::test_every_shipped_hamlets_lanes_are_one_network_at_the_ink_tolerance (5) | 0.04 | as one network |
| ::test_every_shipped_hamlets_lane_ends_reach_something (5) | 0.43 | as the lane end |
| gate/test_cohort_lane_rules::test_the_clean_cohort_seeds_bend_like_paths (module) | 0.12 | as the kink |
| gate/test_crossings_and_cover::test_every_deck_is_long_enough_to_land_on_dry_ground | 0.06 | `settle.py:_crossing_fault`, `city/bridges.py` (`UndeckableCrossing`); test_settle::test_a_crossing_no_deck_seats_is_squared_and_else_cut, test_city::test_a_deck_is_never_drawn_undersized |
| ::test_every_plank_crosses_a_supply_ditch_and_never_the_collector | <0.005 | `bridges.py:channel_footbridges` (`plank_on_supply`); test_city::test_a_plank_is_laid_on_a_supply_ditch_only |
| ::test_the_runoff_curves_out_of_the_collector | <0.005 | `_comb_drain`; test_trunks::test_the_collector_draws_no_hook_into_its_outfall |
| ::test_no_watercourse_end_dangles_in_bare_ground | <0.005 | `trunks.py:anchor_trunk_ends`; test_trunks::test_every_trunk_end_is_left_where_its_water_goes |
| gate/test_cluster_and_homes::test_the_cluster_abuts_the_ground_it_works | 0.05 | `rolling/fit.py:_parts_fit` (`within_field_reach`); test_capacity::test_the_placer_refuses_a_seat_beyond_the_fields_reach |
| ::test_the_settlement_seats_the_byres_it_asked_for | <0.005 | `rolling/lot.py`, `bundle.py`, `SiteRefused`; test_lot::test_a_keepers_byre_is_a_part_of_its_bundle_and_every_one_is_drawn |
| ::test_two_farmhouses_keep_their_own_drip_lines | <0.005 | `fit.py:_house_too_near_a_neighbor`; test_fit_287::test_two_farmhouses_seven_feet_apart_on_their_drawn_quads_are_refused |
| ::test_every_threshing_yard_fronts_its_house_square | <0.005 | `yards.py:_attach_yard`; test_homestead_parts::test_the_yard_edge_facing_its_house_runs_parallel_to_the_house |
| ::test_no_farmhouse_is_drawn_as_a_shed | <0.005 | `houses.py:_try_place_bundle`, `lot.py`; test_lot::test_an_explicit_size_past_the_minka_norm_is_refused_at_the_call |
| ::test_every_well_stands_among_the_doors_it_serves | <0.005 | `homesteads/wells.py:place_wells`; test_homesteads::test_a_well_is_held_to_the_wall_gap_the_test_reads... |
| gate/test_generator_contracts::test_the_map_declares_the_fall_its_drainage_is_judged_against | 0.09 | `plan.py:plan_site` always resolves it; test_plan (an undeclared fall); a duplicate of test_water_flow's non-vacuity test |
| ::test_every_declared_household_is_seated | <0.005 | `stages.py:seat_every_household` (`SiteRefused`); test_capacity::test_a_site_no_margin_can_seat_is_refused_naming_it |
| ::test_farmhouses_vary_in_size | <0.005 | the size ladder; test_lot::test_the_size_ladder_spreads_the_footprints_and_stays_a_farmhouse |
| ::test_the_rolled_cluster_shape_leaves_a_record | <0.005 | `stages.py:declare_cluster_shape`; test_capacity::test_the_declaration_is_the_drawing_and_the_knob_narrows_to_it |
| gate/test_map_vocabulary::test_a_hamlet_has_no_headman_of_its_own | 0.05 | `rolling/place.py:PlacerMixin.headman`; test_rolling::test_a_hamlet_scale_map_can_draw_no_headman |
| gate/test_captions_and_boards::test_every_caption_records_the_feature_it_names | 0.05 | `finish.py:label` refuses no `ref`; test_label_placement::test_a_caption_that_names_no_subject_is_refused |
| ::test_every_caption_hugs_what_it_names | <0.005 | `labels/placer.py:place` (`HUG_RING`); test_placer_287::test_no_seat_stands_past_the_hug |
| ::test_every_caption_is_turned_to_match_its_subject | <0.005 | `placer.py:_point_cands`; test_placer_287::test_a_caption_is_drawn_at_its_subjects_own_angle_through_every_fallback |
| ::test_the_notice_board_stands_by_the_way | <0.005 | `siting.py:_route_seats`; test_board_seat::test_the_board_stands_by_its_way_and_faces_it |
| ::test_the_notice_board_faces_the_way | <0.005 | `siting.py:place_kosatsuba` (`nearest_way_bearing`); the same |
| gate/test_settlement_cover::test_a_woodland_commons_is_visibly_stocked | 0.05 | `land/cover.py:commons`, `parcels.py`; test_woods_287::test_a_woodland_whose_throws_miss_is_stocked_from_its_room |
| ::test_a_woodland_commons_stands_on_dry_ground | <0.005 | `parcels.py:open_ground_patches`; test_hinterland::test_the_scan_refuses_a_ring_the_wet_share_fails_and_takes_the_next_seat |
| ::test_a_woodland_commons_is_mostly_inside_the_picture | <0.005 | `parcels.py` (`parcel_inside_share`); test_hinterland_287::test_the_scan_refuses_a_ring_mostly_off_the_page_and_takes_the_next_seat |
| ::test_a_dooryard_copse_stands_clear_of_the_windbreak | 0.03 | `stands.py:village_grove`; test_woods_287::test_a_copse_over_a_belt_crown_stands_clear_of_its_canopy |
| ::test_no_canopy_stands_over_open_water | 0.07 | `stands.py`, `wood_share.py`; test_woods_287::test_no_grove_clump_stands_over_a_stream_through_its_band |
| gate/test_no_feature_overlaps::test_the_ground_cover_scatter_respects_what_was_swept_before_it | 0.01 | `cover.py:_clear_ground`; test_woods_287::test_a_clearing_swept_after_the_scrub_takes_its_blades_and_marks_out (and a subset of the matrix test's verdict) |
| ::test_no_pond_fixture_stands_on_its_ponds_sluice | 0.01 | `farm_fixtures.py:pond_fixture_fits`; test_farm_fixtures::test_a_pond_fixture_will_not_stand_on_its_sluice. SUPERSEDED by feature 280 M57 (merged 2026-09-29): no per-pond sluice is drawn, so the rule has no subject - `fields/landuse.py` records none (test_fields asserts `dikepond_sluices` absent); 280's replacement `test_no_pond_is_cut_by_a_sluice_of_its_own` stays retired with the module (below) |
| ::test_every_pond_fixture_keeps_to_the_near_half_of_its_pond | <0.005 | `pondstock.py:sty_on_near_half`; test_pondstock::test_a_sty_never_stands_on_the_far_half_of_its_pond |
| hamletgen/test_pool_261::test_every_way_across_the_brook_is_bridged (5) | 0.38 | `city/bridges.py:bridges`; test_city::test_a_crossing_is_decked_unless_a_standing_deck_covers_it |
| ::test_every_farmstead_part_stands_on_its_house_bank (5) | 0.22 | `fit.py:_parts_across_stream`, `byres.py`, `bamboo.py`, `fixtures.py`; test_rolling::test_parts_across_stream_refuses_a_garden_on_the_far_bank |
| ::test_an_entrance_board_stands_at_the_entrance (5) | 0.31 | `siting.py:_board_for` (`entrance_seat_ok`); test_board_seat::test_an_entrance_board_stands_where_every_way_out_passes_it |
| ::test_no_farmhouse_stands_on_the_brook (5) | 0.12 | `fit.py:_rect_on_stream`; test_fit_287::test_a_house_on_the_brooks_course_is_refused_at_its_turned_box |
| ::test_the_ways_cross_the_brook_only_at_fords_and_never_over_and_back (5) | 0.16 | `settle.py`; test_settle::test_a_brook_crossed_out_and_back_loses_the_far_bank_stretch, ::test_a_crossing_off_a_ford_is_cut_and_one_at_a_ford_stands |
| ::test_no_household_grain_plot_is_laid_by_its_house (4) | 0.04 | the producer removed; test_capacity::test_no_writer_of_a_household_grain_plot_is_left_in_the_engine |
| ::test_no_lane_ends_in_a_hook (5) | 0.06 | `settle_shapes`; test_settle::test_a_hook_is_relaid_as_a_tee_and_a_free_hook_loses_its_leg |
| ::test_every_lane_crosses_a_drawn_channel_square (5) | 0.10 | `settle.py:square_every_crossing`; test_settle::test_a_crossing_left_oblique_is_cut |
| ::test_the_board_caption_stands_at_the_boards_angle (4) | 0.04 | `board_seat.py:board_caption_seat`; test_placer_287::test_a_caption_is_drawn_at_its_subjects_own_angle_through_every_fallback |
| ::test_no_three_woodland_parcels_stand_in_a_ruled_row (5) | 0.05 | `parcels.py:open_ground_patches`; test_hinterland_287::test_a_jittered_seat_in_a_row_is_not_taken |
| ::test_no_copse_clump_is_based_in_the_marsh (5) | 0.13 | `stands.py` (marsh in the copse's blocks); test_woods_287::test_every_seat_is_decided_at_the_records_grain |
| ::test_a_belt_tree_in_the_marsh_is_alder (5) | 0.05 | `stands.py`, `core.py:set_view`'s recount; test_woods_287::test_the_alder_count_is_taken_again_over_the_clumps_on_the_page |
| ::test_every_lane_crosses_the_brook_square (5) | 0.06 | as the channel |
| ::test_no_lane_end_is_served_only_by_the_way_it_left (5) | 0.53 | `settle_dangling`; as the lane end |
| hamletgen/test_pool_wind::test_every_pool_belt_is_whole (5) | 0.05 | `belt_law.py:settle_the_belt`; test_belt_law::test_the_settle_deepens_the_thin_stretch_and_closes_the_hole |
| hamletgen/test_pool_282 (module: the yard test (5), the weathers' non-vacuity, the oracle (3)) | 0.78 | `homestead_parts/yards.py`; test_yard_mats_282 (four mats at every turn, the third-to-two-thirds cover, the lattice, the rack's half, the record) |
| settlement/structures/test_fixtures::test_a_board_under_a_canopy_still_takes_a_seat | 216.45 | the feature-261 level-1 seat it pinned is gone; a board every caption of which lies on ink takes plan D12's terminal, held by test_board_seat::test_with_no_clean_caption_anywhere_the_question_stands_for_the_gm (1.78 s) |
| ::test_a_board_whose_caption_cannot_fit_is_not_sitable | 1.68 | the same terminal, the same test |
| soak/test_seed_43_kink (module, strict xfail) | soak | `settle_shapes`; test_settle::test_seed_43s_lattice_step_is_a_kink_the_old_bend_test_passed. With the kink repaired the strict xfail would XPASS and fail |
| soak/test_polder_fall_0::test_a_polder_reservoir_backs_off_until_its_rim_clears_the_crop | soak | `water/polder.py:walk_pond_uphill`; test_water::test_the_reservoir_is_seated_clear_of_a_spike_and_above_the_field_however_far_it_must_go |
| ::test_a_polder_hamlet_draws_its_grid_dike_and_reservoir (with its carve-out docstring) | soak | `fit_polder` (`polder_acres_in_band` or refuse), `SiteRefused`, `dikes.py:dike_gates`; test_water::test_fit_polder_lands_inside_the_band_where_the_bisection_stalls |
| ::test_the_polder_s_lanes_bend_like_paths | soak | as the kink |
| ::test_the_polder_seats_its_households_and_lands_its_acreage (with its 85% floor) | soak | as the grid test |
| soak/test_seatings::test_lane_frontage_seats_the_hamlet_when_the_field_row_offers_nothing (and its seating variant) | soak | `SiteRefused`; test_seats::test_lane_frontage_skips_web_lanes_and_lanes_of_the_other_kind |
| hamletgen/test_pool_261::test_every_way_out_crosses_the_brook_at_most_once (5) (wave 5) | 0.22 | `ways/settle.py:settle_way_outs` (an ordinary lane's crossing cut, else the tree lane carrying it dropped whole), `lane_violators` and the last resort's tail (tree carriers too), `Lawful` asking the route (`law.adds_a_way_out_crossing`) before any tree lane is laid, `track.connector_keeps_the_law` (the connector crosses a brook at most once, so every such way out has a carrier the web may take); test_settle::test_no_way_out_crosses_the_brook_twice, ::test_a_way_out_only_tree_lanes_carry_over_and_back_loses_the_tree_lane_nearest_the_house, ::test_lawful_refuses_a_tree_lane_that_hands_a_household_a_way_out_over_the_brook_and_back, ::test_a_way_out_left_over_the_brook_after_the_last_resort_loses_its_lanes; test_track::test_a_connector_through_a_building_or_over_the_brook_twice_takes_the_dry_exit |
| gate/test_lane_network::test_the_connector_does_not_break_mid_run (wave 5) | <0.005 | `track.connector_keeps_the_law` (the connector as drawn, squared first, runs through no `law.breaks_through` box, else the dry exit) with `stage_track` walling the sweep and the dry exit by `law.solid_quads`; the later writers ask the same predicate (`web.kept_connector`, `joints.fold_the_connector_hairpin`); test_track::test_the_connector_sweep_refuses_a_bearing_with_a_house_on_it_and_takes_the_next, ::test_a_connector_through_a_building_or_over_the_brook_twice_takes_the_dry_exit, test_web::test_the_late_pass_keeps_the_connector_as_placed_where_its_pulled_back_end_would_run_through_a_building, test_joints::test_a_connector_fold_whose_new_first_leg_runs_through_a_building_is_refused. The settle's hook repair only shortens a leg of at most `_HOOK_FT` (no leg past `BREAK_SPAN_FT` is made), and its squaring is a no-op on the already-squared connector |
| gate/test_settlement_cover::test_every_recorded_grove_holds_trees (module deleted; wave 5) | <0.005 | `stands.py:stocked_box` - every grove is recorded at its band's box where its clumps stock it, else the extent they are drawn at, else their main stand's (`main_stand`), judged at the record's 0.1 px grain (`stocked_at_grain`); `village_grove` records through it and `core.py:_partition_grove_clumps` re-decides the box over the clumps the page shows; test_woods_287::test_a_grove_is_recorded_at_an_extent_its_clumps_stock, ::test_village_grove_records_a_windbreak_its_clumps_stock, ::test_the_page_partition_records_the_grove_again_at_what_the_page_shows |
| gate/test_scatter_frame::test_no_shipped_hamlet_breaches_its_scatter_frame (5) (wave 5) | 0.28 | `hinterland/frame.py:scatter_frame_for` - the decided view's scatter frame carries the title band's allowance below the view as well as above (the band goes under the map when every seat above is crossed; cohort seed 8 reached 98 px past the old pad), so the view the band grows stays inside it; the finish's unused re-throw (`_scatter_rethrows`, set by nothing) deleted; test_finish_287::test_a_scatter_frame_of_the_decided_view_holds_the_title_band_on_either_side, test_hinterland::test_after_the_view_is_decided_the_scatter_throws_within_it_and_the_placers_ask_it |
| gate/test_crossings_and_cover::test_the_countryside_has_no_holes_in_it (module deleted; wave 5) | 0.04 | `finish.py:_title_band` clothes the band it grows (`cover.py:refill_the_view`, the fill again over the final `map_window` - the view, or the neatline where the band is sheet outside the map) on a map that filled its holes; test_finish_287::test_the_title_band_is_clothed_as_the_view_was |
| hamletgen/test_pool_261::test_the_copse_stands_within_reach_of_what_it_is_named_for (5) (wave 5) | 0.15 | `stands.py:village_grove` asks every clump its reach where it is seated and again where it is re-seated (`_reseat(reach_of=...)`): a household's reserved seat its dooryard's (`seat_near`: a house within `COPSE_HOUSE_REACH_FT` on its bank, passed by `stage_windbreak` on either siting), every other clump the siting's `near` (the belt's lee on against_the_belt); test_woods_287::test_a_reserved_seat_is_asked_its_households_reach_and_bank, ::test_a_reserved_seat_moved_round_another_groves_crown_is_asked_its_reach_again. The rule as W25 restated it: a reserved seat is its household's share, standing by its house on either siting (cohort 1-60 at wave 5 start: 172-279 such crowns a map beyond 60 ft of the belt on the against_the_belt seeds) |
| ::test_every_copse_clump_stands_on_the_bank_of_a_house_within_reach (4) (wave 5) | 0.15 | the same (`BankNear`: the house within reach on the clump's own side of the brook) |
| hamletgen/test_pool_wind::test_every_pool_hamlet_has_its_belt_on_the_regional_northwest (5) (wave 5; its record clause kept as ::test_every_pool_hamlet_records_the_regional_northwest) | 0.10 | `stands.py:trim_to_the_wind` - the end trim converges on the crown nearest the wind's bearing, and where even that bears off the wind's quarter no belt is planted (never one off the wind); the non-settling path trims a one-crown belt too; test_woods_287::test_a_belt_wrapped_round_the_cluster_is_trimmed_to_a_hook_on_the_wind (the lone crown off the wind), ::test_a_belt_with_no_crown_on_the_wind_is_not_planted |
| gate/test_captions_and_boards::test_no_caption_lies_across_a_way (module deleted; wave 5) | <0.005 | a hamlet's one caption is its notice board's (the pool's five manifests draw no other), and `board_seat.py` decides it clear of every way on both paths: `board_caption_seat` (strict, the way term `caption_clears_ways` reads) and, at plan D12's terminal, `terminal_caption` - the caption on a leader or in the key (D10, no hard ink: a settlement's ways are hard) at a seat whose key mark clears every way, else the next seat; `place(least=True)`, the retired least-cost seat that could lie across a lane, is deleted. test_board_seat::test_with_no_clean_caption_anywhere_the_question_stands_for_the_gm (a verge seat whose mark would lie on the road refused), ::test_the_terminal_caption_clears_every_way_or_is_refused, test_placer_287::test_a_way_crossed_between_the_blocks_corners_is_seen |
| ::test_every_pool_belt_keeps_its_depth_across_its_windward_face (5) (wave 5) | 0.08 | `belt_law.py:BeltReading.depths` - a belt no bin of which is judged, some stretch of which stands farther than `BELT_DESIGN_DEPTH_FT` from the page's edge (`off_the_page`, the retired test's frame-held clause), has every crowned bin judged, which `settle_the_belt` deepens or ends; test_belt_law::test_a_belt_no_bin_judges_is_judged_whole_where_it_stands_off_the_page |
| gate/test_paddy_fabric::test_the_supply_commands_both_flanks_of_the_fan (module deleted; wave 5) | <0.005 | `water/fit.py:fit_field` - a fan is legal only where `flanks_commanded` holds (with `tail_dangles` and `net_bends_acutely`, one `fan_legal`), judged again on the finished net; the least-bad keep is gone: past a search widened to every aspect in full the site is refused (`FieldRefused`); test_fit_flanks::test_a_fan_whose_supply_leaves_a_flank_uncommanded_is_never_returned, ::test_a_flank_whose_supply_is_trimmed_short_is_uncommanded |
| ::test_no_shipped_polder_parcel_tapers_to_a_point (wave 5) | 0.30 | `waterfields/polder.py:unpoint_parcels` judges and writes the ring AS RECORDED (rounded to 0.1 px, as `fields/comb.py`'s `plot_rings`); test_polder_ring::test_a_parcel_blunt_unrounded_but_a_needle_as_recorded_is_re_hemmed (15.0 degrees raw, 14.9 recorded) |
| gate/test_water_flow (module deleted; wave 5): ::test_every_channel_runs_downhill | <0.005 | `fields/comb.py:runs_downhill`, the ONE channel rule every writer of `channels` decides by: the sink's routes, pond seat and confluence (`sink.py`, as before) and now the hairline feed (`_comb_source_channel`: a snap onto the stream taken only where the feed still runs downhill, a feed that climbs refused by name); test_field_guarantees::test_the_feed_runs_downhill_its_snap_refused_where_it_would_climb_and_a_climbing_feed_refused, test_sink::test_a_run_downhill_keeps_a_fifth_of_its_travel_on_the_fall |
| ::test_every_stream_end_is_anchored_to_what_it_declares | <0.005 | the feed brook declares both ends off the map (`water/comb.py`, `to: offmap`) and `brook_violations` holds the source AND the mouth off the canvas on every candidate (`ends_off_canvas`), the mouth by construction (`brook.py:exit_legs` lengthens the last leg down the fall; cohort seed 48's stopped 60 ft inside the sheet at HEAD); test_brook::test_the_mouth_leaves_the_canvas_however_far_across_the_fall_the_course_heads, ::test_the_source_is_off_the_canvas_however_wide_the_canvas. No hamlet stream declares a pond end (the drain's run to a pond is a channel) |
| ::test_the_map_declares_the_fall_every_rule_below_is_measured_against | 0.05 | non-vacuity for the two above |
| gate/test_water_junctions::test_no_watercourse_crosses_another_mid_run (module deleted; wave 5) | 18.63 | every candidate of `feed_brook`, the routes round the field included, judged on the drawn course against the net's ditches (`crosses_mid_run`), else `BrookRefused`; the sink's routes as before; the pond seat refuses a ditch over the brook (`pond_seat`; six maps of cohort 1-60 and the pool, Mizuguchi among them, drew one across it at HEAD - each now keeps its pond on the other side); each confluence judged with the brook as drawn (`confluence_keeps_the_brook`); test_brook::test_a_ditch_tail_on_the_brooks_flank_is_skirted_not_crossed, test_sink::test_the_pond_seat_steps_across_the_fall_to_where_its_ditch_crosses_no_brook, ::test_a_pond_reached_only_across_the_brook_is_no_pond_and_the_field_drains_by_a_route_that_crosses_nothing. 18.60 s of the figure is the Inashiro pool map's cold obtain, shared, so the retirement frees about 0.03 s |
| hamletgen/test_pool_261::test_no_brook_folds_back_on_itself (5) (wave 5) | 0.12 | `brook.py:feed_brook` judges EVERY candidate - the routes round the field from every bearing on both skirts, where the last used to be returned unjudged - on `drawn_course` (the tap and any confluence held, as `round_the_brooks` draws it), and refuses the site past the last (`BrookRefused`); the sink judges the confluence it adds with the brook as drawn (`sink.confluence_keeps_the_brook`), so the course is never rounded after its judgment; test_brook::test_a_last_candidate_that_breaks_a_rule_is_never_returned_the_next_bearing_is_or_the_site_is_refused, ::test_the_last_candidate_bows_a_clear_way_straight_up_the_fall, test_sink::test_the_confluence_is_the_nearest_one_the_brook_as_drawn_keeps_its_rules_with |
| ::test_no_brook_runs_ruled_along_the_frame (5) (wave 5) | 0.09 | the same (`level_runs_any_view`, a superset of every view) |
| ::test_no_brook_runs_ruled_for_most_of_its_course_on_the_page (5) (wave 5) | 0.08 | the same (`ruled_excess`, the view-independent bound) |
| ::test_no_brook_segment_lies_on_a_screen_axis_but_the_tap_run (5) (wave 5) | 0.06 | the same (`axis_segments`) |
| hamletgen/test_seed_branches_147::test_the_fit_gives_a_saturated_best_aspect_the_full_search_it_was_denied (wave 5) | cached (~11 s cold, its own record) | a test of the closest-miss branch FR-005 converts: at an unreachable target the fit now refuses (`FieldRefused`) after every aspect is searched in full; test_fit_flanks::test_a_fan_no_aspect_can_bring_into_its_acreage_band_is_refused_after_every_aspect_is_searched_in_full; the best aspect's full re-search keeps test_water::test_fit_field_probes_saturation_and_rerolls_the_best_aspect_in_full (stand-in carves) |
| gate/test_cluster_and_homes::test_the_cluster_draws_inside_the_band_of_the_shape_it_declared (module deleted; homes wave 5) | <0.005 | `homesteads/stages.py:seat_every_household` keeps no seating whose houses draw no shape's band (`in_a_shapes_band`: past elongated's 12:1): the margin is taken back as a short one is, and past the last the site is refused (`SiteRefused`); test_capacity::test_a_seating_drawn_past_every_shapes_band_is_taken_back_and_the_next_margin_seated. Cohort 1-60: widest drawn 3.43 |
| ::test_every_household_can_reach_water (homes wave 5) | <0.005 | `rolling/lot.py:watered`, asked of every candidate where the house is PLACED (`fit.py:_candidate_watered`, from `_parts_fit` and `_bundle_common_fits`): a household with no pocket of its own carried past every pocket's and water's reach by the envelope's move or a slide is refused; test_homesteads_287::test_a_household_moved_off_the_seat_it_was_sought_from_past_every_pockets_reach_is_refused |
| hamletgen/test_pool_261::test_a_way_reaches_the_field (5) (homes wave 5) | 0.21 | ways W03: `homesteads/stages.py:reserve_field_corridor` reserves the field's corridor with the exit strip (the ways' own field paths, straight or over the brook at a ford, then routed; the first on lawful ground) as legs of the access tree, so no envelope and no wood share covers it, or the margin seats no one; `ways/settle.py:settle_field` draws it first (`corridors.field_chain`, bowed round a shed on it). test_homesteads_287::test_the_field_corridor_is_reserved_with_the_exit_strip_and_no_homestead_covers_it, ::test_a_margin_with_no_lawful_field_corridor_seats_no_one, test_settle::test_the_field_corridor_the_seating_reserved_is_drawn_first_and_alone_where_nothing_else_keeps_the_law. Cohort 1-60: every margin seated found one; 0 unreached |
| ::test_the_pool_has_a_brook_to_cross | 0.08 | non-vacuity for the test above; goes with it |
| gate/test_no_feature_overlaps::test_the_comb_hamlet_draws_no_forbidden_overlap (module deleted; M8, T83) | 0.05 | the registry of what stands (`overlap/registry.py`): the manifest is a `StandingManifest` whose every list under a key the matrix tests is a `StandingList`, so every footprint the settlement records - an append, an insert, a set, a rebind, a single record, a whole-value road or pond - is recorded through one grid index (120 px cells, filed once as recorded, asked per candidate); a lane is a `Kept` record whose every rewrite of a drawn field asks first; `resync` at every stage's end and before the manifest is written re-records anything reshaped in place. On the hamlet (`Standing.strict`, `hamletgen/driver.build`) a record the matrix forbids on what stands raises `OverlapRefused` by name, and every placer the matrix could refuse asks `Settlement.admits` first: the lane law (`settle.fouled_segment` via `forbidden_segment`, so `Lawful`, the settle and `corridor_on_lawful_ground`), every lane rewrite (`reshape_lane`, `admits_lane`, `smooth.commit_lane`'s `admit`, the touch splice, the connector fold, the bund run-on), the web's lanes and skeleton arms (`_draw_web`, `admitted_runs`), the router walls (`corridors.field_router`, the dry exit), the connector (`track.connector_keeps_the_law`), the spur, the corridors from their own beds, shed, byre and pocket (`access.parts_clear`, `leaves_its_yard`, `house_gap`), the well pocket off the beds (`bundle.pocket_clear_of_beds`), the wells (`well_at`), the burial ground (`edge_seat`), the retirement house, the flexible fixtures, the footplanks and the carried decks (`bridges.deck_admitted` inside `undeckable_at`); the parts laid at seating stand held until drawn (`homesteads/holds.py`). The one predicate is `registry.element_extents` + `pair_forbidden`, which `matrix_violations` also reads. Measured: Inashiro 4 and Kuwabata 9 forbidden pairs at 289d5fe8a, 0 of 5 pool maps and 0 of cohort 1-60 after, with no record refused at record time. test_standing_287 (the registry, its containers and the seating's reservations on the violating case), test_matrix_287 (each way placer refused by a bed or a well), test_m8_placers_287, test_m8_287 |
| ::test_the_polder_hamlet_draws_no_forbidden_overlap | 0.06 | as above |
| gate/test_lane_network::test_no_tree_is_planted_in_a_path (M8, T83) | 0.06 | the copse trunk past its reach (cohort seed 31): `stands.crown_reach`'s lift is `groves.crown_lift`, the lift `_draw_grove` draws (3 * bscale / 0.82 = 3.66 px on a hamlet, taken as 3.0 before), so the planting's lane buffer (`village_grove`'s `_corridor_buffers`) and the reserved seats' `lane_gap` hold every trunk the grove draws off every tread; the yard persimmon closed in homes wave 5 (above). test_m8_placers_287::test_crown_reach_is_the_reach_the_grove_draws (200 clumps: the farthest trunk inside the reach, and past the old one); 0 trunks on a tread over cohort 1-60 and the pool after |
| hamletgen/test_hinterland_287::test_a_woods_short_of_the_floor_is_topped_up_among_the_houses (M8, T83; with the lee copse top-up and the `homestead_wood_drawn < HOMESTEAD_WOOD_FT2[0]` floor check that triggered it in `stage_windbreak`) | <0.005 | woods W25 held by construction: every household is seated only with copse seats covering the floor (`wood_share`), and the registry keeps every later placer off them (`overlap/reserved.py`: the web's lanes by the copse's lane buffer, the title's pocket, the shared sheds, the parts laid after the seating; the connector over one only as its last resort, named in `meta.wood_seats_to_the_connector`), the seats are reserved off the toe marsh and the ponds the copse refuses, and the view takes in every seat's crown (`frame_extras`). Seats lost to what was planted after the seating: 17% of cohort 1-60 before (2,961 of 20,441 on the measure here: lanes 2,866, the pocket 95), 0 of 20,095 and 0 of the pool's 1,808 after; the lowest drawn wood 9,401 sq ft a homestead against the 6,000 floor. The top-up fired on none of cohort 1-60 since the seats were planted first; `meta.homestead_wood_ft2` stays as the record of what was drawn. test_hinterland_287::test_every_households_reserved_share_is_planted_though_no_belt_stands, test_standing_287::test_a_reserved_seat_is_kept_off_by_occupiers_wells_and_lanes, test_m8_287 |

**Clauses retired from kept tests**: the seating floor and `ACREAGE_SHORT`'s skip and `GATE_COHORT_EXPECTED`'s pins in
gate/hamletgen/test_driver (FR-006); the household clause of gate/hamletgen/test_water; the channel-under-plot clause of
full/test_villages (`finish.py` lifts every plot under the water block; test_field_guarantees::test_a_plot_drawn_after_the_water_is_painted_under_every_channel);
the comb fans' half of the shipped-hamlet needle test; the pond and drain clauses of the runoff (with the test);
every clause but the band of the cluster-shape test; every lane but the connector in the break-mid-run test; the seat and
household clauses of test_pool_wind's northwest test and the judged half of its depth test; the chord caps and the facing
chains of the polder soak's keep-out test; the shape-record clause of the cloud seating; the `kosatsuba_caption_level == 1`
excuse of test_the_board_caption_notches_no_crown (FR-006: no engine code writes it since ec241c0b1). Wave 5: the acreage clause of
gate/hamletgen/test_driver (`fit_field` lands the fan within `FIELD_ACRE_BAND` on the finished net or refuses; test_fit_flanks's
three fit tests), and the sty clause of gate/hamletgen/test_water (a dike-pond hamlet with a grow-out pond seats its sty or is
refused, `StyRefused`; test_water_287::test_a_dike_pond_hamlet_whose_every_near_half_seat_is_built_on_is_refused_never_drawn_without_its_sty,
::test_no_reservation_where_the_hamlet_keeps_no_ponds_or_no_seat).

### Kept, and the correctness each guards

(a) = a property no single placer owns; (b) = a rule not yet guaranteed (what is missing is the reason).

| kept map-reading test | s | why |
|---|---|---|
| gate/test_bunds_and_dikes::test_the_waterward_reed_strip_runs_off_the_frame | <0.005 | RETIRED by the lead in wave 6 with its module (water W43 closed on every path the map's edge can take): the view is decided at the strips (`hinterland/frame.py:to_the_strips`, test_m8_287::test_the_decided_view_stops_where_each_water_facing_strip_stops), the title band is never grown on a flank a strip runs off (`finish.band_keeps_the_strips`, test_finish_287::test_the_title_band_is_not_grown_on_a_flank_a_reed_strip_runs_off), and the caption key band is sheet furniture outside the neatline, the map's own edge (`structures/captions.py:_draw_caption_key`). (Observed 2026-09-29, method: the implementers' unit tests and `make cohort N=60`.) |
| gate/test_generator_contracts::test_a_map_that_draws_byres_declares_their_form | <0.005 | (b) written by construction, but no unit test asserts `meta.byre_form` |
| gate/test_map_vocabulary::test_every_mark_on_the_map_has_been_ruled_on | <0.005 | (a) every layer's ink carries a class |
| ::test_no_stage_after_the_view_is_decided_moves_the_frame (5) | 0.33 | (a) a contract over every stage after the view is decided |
| gate/hamletgen/test_driver::test_a_rolled_cohort_passes_the_whole_gate (narrowed, wave 5) | 0.09 | (a) the roll's reach verdict, reported not refused |
| gate/hamletgen/test_water::test_a_dike_pond_hamlet_is_ponds_in_a_diked_block_with_wet_flanks (narrowed, wave 5) | 0.04 | (b) the archetype's record (the overlay count, the fry ponds, no duck pen, a wet strip per waterward face, forecourt yards): no placer unit test holds it |
| ::test_the_board_caption_names_the_board_only (4) | 0.04 | (b) plan D12's terminal |
| ::test_the_board_caption_stands_nearest_its_own_board (5) | 0.05 | (b) plan D12's terminal |
| ::test_the_board_caption_notches_no_crown (5, excuse removed) | 0.15 | (b) plan D12's terminal |
| hamletgen/test_pool_wind::test_the_pool_has_scripted_hamlets_to_judge | <0.005 | non-vacuity |
| ::test_no_pool_hamlet_declares_a_wind (5) | <0.005 | (a) the GM's ruling on the pool's content; no placer owns a spec file |
| ::test_every_pool_hamlet_records_the_regional_northwest (5; wave 5, the record clause of the retired belt test) | <0.005 | (a) the GM's ruling on the pool's content: no declared wind, the region's northwest recorded |
| full/test_villages::test_village_passes_gate (5) | 69.85 | (a) every shipped generator runs in its budget and to a manifest (this is the pool's regeneration, the gate's largest cost, which no retirement touches); (b) the paddy cell band (no placer holds it; it judges no map the pool ships today) |
| full/settlement/test_rolling::test_pinned_knob_is_byte_identical_across_regens_and_rejects_incompatible_pins | 8.75 | (a) determinism of the whole roll |
| soak/test_polder_fall_0::test_the_polder_dikes_keep_out_contains_its_drawn_band (narrowed) | soak | RETIRED by the lead 2026-09-29 with its module and `tests/rolls.py:POLDER_FALL_0`: `_geom/primitives.py:keepout_ring` asks the ring of every covered point and pushes the side it escapes on until none does, or refuses the band by name past `KEEPOUT_GROWTHS`; test_keepouts::test_a_band_the_inner_tolerance_misses_at_an_acute_corner_is_contained_all_the_same |
| soak/test_seatings::test_the_cluster_seeds_cloud_still_seats_a_hamlet_when_the_rows_offer_nothing | soak | RETIRED by the lead 2026-09-29 with its module: test_capacity::test_the_cloud_alone_seats_the_hamlet_when_the_rows_offer_nothing drives the cloud alone on a constructed site |
| ::test_the_linear_frontage_pass_stops_once_the_households_are_housed | soak | RETIRED by the lead 2026-09-29 with its module: test_capacity::test_the_linear_frontage_stops_once_the_households_are_housed_with_seats_still_on_offer offers more frontage seats than households and seats exactly the households |
| soak/test_village_determinism::test_roll_village_is_deterministic_and_seed_varies_the_combination | soak | (a) determinism; (b) the village path's house count has a cap and no floor |

Not placement rules, so outside FR-007 and kept: `tests/gate/test_pool.py`, `tests/gate/settlement/test_rolling.py` (the
village entrypoint's coverage, 3.4 s), `tests/gate/pipeline/*`, `tests/full/hamletgen/test_driver.py` (CLI and fan-out),
`tests/full/pipeline/*`, and `tests/test_villages.py`'s classification, budget, render and design-cell tests. (Observed 2026-09-29, method: `make durations FULL=1` in a detached worktree.)

### Gaps (FR-006: an excuse removed on a rule no placer guarantees yet)

- **The fan's acreage** - CLOSED in wave 5: `fit_field` returns only a fan legal and within `FIELD_ACRE_BAND` (15%) on the
  finished net; where none is, the search is widened to every aspect in full and then the site is refused (`FieldRefused`),
  never the closest miss. Measured 2026-09-29 over cohort 1-60 and the pool (64 comb fans, Kuwabata a polder): 0 refused,
  every fan legal on the first search and within 6.7% (seed 20), no map moved.
- **The board caption on a crown, on a way, off its board.** The level-1 excuse is gone; plan D12's terminal (0 of 53
  maps) is the GM's question and the three pool tests are kept for it. ON A WAY - CLOSED in wave 5: the terminal's caption
  is D10's (leader or key, never overlapping) at a seat whose key mark clears every way (`board_seat.terminal_caption`),
  in place of the least-cost seat D10 had retired everywhere else. That is still the question's option (c), a caption
  breaking the board caption's own rules (beside the board, no leader), so the GM's answer is not presumed; the crown
  and off-its-board clauses stay open with it.
- **The runoff brook downhill from the outfall** - CLOSED in wave 5: every candidate of `feed_brook`, the routes round the
  field included, is judged on the drawn course with `monotone_down` below the tap (`climbs`), so the brook passing the
  outfall runs downhill wherever it passes it; the drain's continuation is held by `runs_downhill` at every writer. (The figures in this list: observed 2026-09-29, method: `make cohort N=60` and the fit's own acreage over the pool.)

### Found on the way (for the lead)

- **The SC-003 sweep reads the census tests by name** (`sweep/harness.py:census_tests` imports each module and looks the
  function up). The retired ones will read "no such test function in its module" there; the sweep at acceptance needs
  them from the pre-retirement tree or their predicates called directly.
- **216 s**: `place_kosatsuba` on a road under one 600 px crown took 216.45 s at 0e792a665 (the strict siter proving
  every seat before plan D12's terminal); a real map whose board stands under a canopy pays the same. CLOSED in wave 5,
  indexed and exact: rebuilt as a timing probe (the retired test's scene, 1,072 seats), 305.5 s at 920c5ad9f and 4.6 s
  after (observed 2026-09-29, a direct call in the clone and in a detached worktree at 920c5ad9f, both under the same
  load). The profile's two scans: `choose_board` proved every shaded seat on its way to an open one (595 of 713 profiled
  s: every seat was shaded, each proved by the full least-cost search), now open seats first and then shaded, the same
  seat; and each strict proof scored ~140 blocks with the association's outline gap (four fifths of a proof), now
  `ObstacleIndex.blocked` refuses a block held past a nudge's reach unmeasured (a gap under the clearance less the reach,
  or an overlap deeper than it) and `_strict_seat` measures the refused ones only where one might be the least-cost seat
  the nudge starts from. With them: the way term measures a segment once (a long road was re-measured in every cell) and
  clears it by the boxes first; `nearest_points` skips its crossing tests for outlines whose boxes stand apart. Held
  exact by test_strict_index (the indexed strict search against the scan over 60 scenes; `blocked` against every nudge
  over 400 blocks) and a differential run against 920c5ad9f, identical: 1,600 placements (strict and lax, 258 of them
None) over 400 random scenes and 16 sited hamlets under small crowns (observed 2026-09-29); the fast siting test
  is test_fixtures::test_a_board_under_one_wide_canopy_is_sited_without_measuring_a_seat_it_cannot_take (0.6 s, the
  scene on a 200 px road: the only seats scored are the one terminal search's).
- **Six failures at 0e792a665** in the worktree's run: the two overlap-matrix tests (kept, above), two
  `test_notes_census` blocks (Inashiro, Kuwabata) and two test_pool_261 params on Mizuguchi's committed manifest (both
  retired here).
- **Stale mentions left in files this task does not own**: `hamletgen/ways/law.py`'s docstring (fixed in wave 5, with
  `ways/serve.py`'s `_JOIN_FT` pointer to the retired one-network test) and `hamletgen/homesteads/wells.py` name retired tests; `tests/hamletgen/test_surface.py:105` names the deleted cohort module. (Homes wave 5: the `wells.py` pointer and the stale `cohort_specs` pin fixed.)
- **Not touched, owned elsewhere now** (homes wave 5: the two `contextlib.suppress(SiteRefused)` excuses in `tests/hamletgen/test_homesteads.py` now assert the refusal): homes:H32's fixtures-unseated excuse tests in `tests/hamletgen/test_homesteads.py`
  (the performance implementer's file) and woods:W17's `tools/mapcheck.py` tripwire (not a test). (The figures in this list: observed 2026-09-29, method: the implementers' timing probes and `make durations`, as each entry says.)

### Merged with feature 280 (2026-09-29)

Feature 280 (the GM's rulings of 2026-09-29, the settlement-reviews, the modern-only forms eliminated, the dike-pond
changes) was merged into this feature. Its two edits to modules this feature deleted, and its new finished-map rules, were
judged by the method above - the placer that decides the rule and the unit test that drives it on the violating case.

- **`tests/gate/test_no_feature_overlaps.py` stays deleted.** 280 replaced the sluice-clearance test with
  `test_no_pond_is_cut_by_a_sluice_of_its_own` (M57: no per-pond sluice is drawn). The placer that decides it is
  `fields/landuse.py`, which records no `dikepond_sluices`; its unit test is 280's own `test_fields` assertion that the key
  is absent. 280's other edit there removed the sluice import. Nothing is left that no placer guarantees.
- **`tests/hamletgen/test_pool_282.py` stays deleted**, and its frozen fixture `tests/fixtures/sawada_yards_282.json` (280
  added it only for this module) is removed. 280 moved the oracle test onto the frozen fixture because its 25-tsubo yard
  median (M16) moved Sawada's yards; it added no assertion. The rule is the one retired above to `homestead_parts/yards.py`
  and test_yard_mats_282.
- **280's rules checked on the finished map, turned into placer guarantees:**
  - *A sty stands within a household's reach* (`STY_HOUSE_REACH_FT`, settlement-review of Kuwabata). One predicate,
    `pondstock.sty_in_reach`, is asked by the reservation (of the seat's center, before the houses stand) and by
    `stage_pond_stock` (of the houses as seated); with 287's at-least-one rule, a dike-pond hamlet with no sty seat in any
    household's reach is refused (`StyRefused`) instead of shipped without one (280 drew none). Tests:
    test_plan::test_a_sty_stands_within_a_household_s_reach_or_not_at_all (the violating case refused, drawn 0),
    test_water_287::test_no_reservation_where_the_hamlet_keeps_no_ponds_or_no_seat (the reservation past reach refused).
  - *The copse keeps two crowns off the bamboo* (`bamboo_rings`, rounds 3-4). The copse refuses a seat in a stand's grown
    ring; so that no household's RESERVED copse seat (woods W25, planted where reserved) is ever refused by it, every bamboo
    placer - the thicket's scan and the household strips - keeps the reserved seats outside the keep-out, by the one
    predicate `homestead_parts/bamboo_keepout.stand_spares_seats`. Tests: test_grove_blocks (the predicate against
    `grown_ring` over random rings), test_hinterland_287::test_the_thicket_gives_way_to_every_reserved_copse_seat,
    test_homesteads_287::test_a_household_bamboo_strip_gives_way_to_every_reserved_copse_seat.
  - *The bath is a room joined to the house; the wood shed stands a ken off its wall, never walked out across the
    dooryard* (M21, M22). 280 seated them in its late placer and passed a fixture with no seat to the next house; here they
    are laid in the bundle (`fixture_seats.lay_fixtures`) with a predicate each - `joined_to_house`, `shed_off_a_wall` - and
    a layout where the lot's bath room or wood shed finds no seat is refused by the fit (`FixtureUnlaid`, `unlaid`,
    `_bundle_side_fits`), so another garden side or seat is sought: no fixture recorded short, none walked into the yard.
    Tests: test_fixture_seats (the bath on each wall, slid along it, refused; the shed a ken off, refused, the predicate's
    both edges). The wood shed's quota goes to the larger houses first (`lot.larger_first`, test_homesteads), the privy and
    the bath room take the household's rolled size (`fixture_ft`, carried on the laid record as `ft` and drawn at it).
  - *No hamlet draws a burial ground of its own* (M68): 280's `stage_burial` is taken whole; 287's own-ground narrowing and
    its way target (homes H36) have no subject and went with it (`plan.way_targets` and the web's service of it stay, fed by
    nothing until a form that owes a path returns).
  - *A fry village's nursery water is at most seven tenths* (M60): guaranteed at `landuse.fry_pond_ids` (280's test_fields);
    the kept gate test (`gate/hamletgen/test_water.py`) carries 280's fry clause as the archetype's record, and loses its sty
    clause (retired above: `StyRefused`).
- **Where 280 fixed what 287 guarantees differently, 287's mechanism kept:** the doubled-tail sweep (moved to
  `ways/tails.py` by 280) writes every lane through `reshape_lane` and carries a stranded end onto the way only where the
  overlap matrix admits it (all or none; test_sweeps); the thicket's 9 x 5 sample grid is 287's `stand_samples` at
  `BAMBOO_SAMPLE_FT`, finer than a persimmon's crown and its pad on either axis; the kura's 1.67-to-one annex (M18) is one
  table, `farm_fixtures.kura_rect`, read by the drawing, the bundle, the flush's side choice and the fixtures' walls (280's
  change had reached two of the four copies); the lots' kura quota is 280's one farm in eight (M20).
- **The seat band's area grows with 280's yards** (`consts.HOMESTEAD_GROUND_FT`, 104 ft, read by `plan.band_extent`): at
  the row pitch's 100 the merged seat band held 13 of cohort seed 18's 15 households and the site was refused (287's HEAD
  seats it, measured in a detached worktree); the median yard is 3.8 ft deeper at 25 tsubo (M16), so the ground one
  homestead takes is 104. The row pitch and the web's reach stay 100 - raising them too left a farmhouse off the way
  network on seeds 11 and 43 (measured, not taken).
- **A 287 defect the bigger yards exposed, fixed at its placer** (`access.doors_of`, test_access): the far-edge door was
  set by the yard's axis-aligned box, which overstates a turned yard; with 280's 25-tsubo yards a door stood 16 ft past
  the drawn yard (cohort seed 32, a yard turned 12 degrees), an end `end_serves` reads as reaching nothing, so the reserved
  corridor could not be drawn and a farmhouse stood off the network. The bundle now records its turn (`geom["turn"]`) and
  the door stands on the drawn edge.
- **Toy tests re-seeded, not weakened:** 280's geometry (no quarter-turned tenth, M26; the larger annex; the wood shed)
  moved the toy hamlet's seed 3: the front-row tests take seed 5, the wells test seed 4, the rank-round refusal 13
  households (twelve now fit the strip); the linear-frontage test keeps its fixtures and wood shares out, as the other
  seating-count tests already did. (The figures in this section: observed 2026-09-29, method: `make cohort N=60` and `make cohort N=1 SEED=18` on the merged tree.)

## R9 - The acceptance sweep (2026-09-29)

**Method** (observed 2026-09-29, method: `make spec-harness SPEC=specs/287-placer-guarantees/sweep OUT=<json>` in the
clone at bf705bee3 with the harness as amended below, eight workers, 106 rolls in 282 s wall; the output is the session's
`sweep-287-final.json`, not kept). The 53 maps - the five pool hamlets from their generators' own `HamletSpec` and cohort
seeds 1-48 - each rolled twice: plain, and under feature 284's two withdrawn levers applied as probes (A* in the router,
`specs/284-fourth-hotspot-pass/astarcmp/astar.txt`; the field search's saturation probe, `b3cmp/b3_fit.py.txt`; neither
ships). The B3 probe's aspect search ranks by its own legality (no flank term), while today's `fit_field` still judges
the finished net with `fan_admissible`, so the probe moves the search and not the rules. Every finished manifest is
asked every predicate: the lane law (`law.LAW`, 29 rules by name), the paddy-ring rules (`ring_violations` over every
recorded plot ring: 32,902 rings plain, 31,227 under the probes), the overlap matrix (`matrix_violations`), the
windbreak as `settle_the_belt` reads it (`belt_law.reading_of`: thin stretches, holes), the roll's own seating and reach
verdict, and 101 of the census's 118 finished-map tests.

**What changed in the harness since the baseline** (`sweep/baseline.json`, taken at cc39f599a):

- **The re-roll is gone**, so the harness counts BUILDS: it wraps `driver.build` and `driver.unreached_houses` and
  counts one call of each per roll; a second is a re-roll. The Report's `attempt` and `rerolled_after` no longer exist.
- **The retired tests are pointed at what replaced them, measuring the same rules.** A census test still in the tree
  runs as it stands. A test feature 287 retired runs as its body LAST stood - the parent of the commit that removed it,
  after FR-003 made it read its placer's own predicate - and its baseline body at cc39f599a runs beside it as a twin,
  whose verdict is recorded where the two differ. Where R8 names an engine predicate that reads a finished manifest, the
  test is also read through it (`ENGINE`: 37 tests onto `law:*`, `ring:*`, `matrix:*`, `belt:thin` and the roll's
  seating). Two are counted through a restated predicate, their bodies' verdicts kept beside it (`RESTATED`): the copse's
  reach as woods W25 restated it (R8), and the runoff with the retired body's two misreadings corrected - it read a
  polder's header reservoir as the sink, and took a brook passing the outfall by its far END, which on a feed brook is
  its source. One is listed and not run: the pond fixture's sluice, superseded by 280 M57 (R8).
- **Harness defects fixed on the way**: a `pytest.fail` or `SystemExit` escaping a worker left `pool.map` waiting for a
  result that never came (the first run hung with every worker idle); a fixture taking no parameters now runs its own
  body with `_pool.rolled_map` answering this map (the captions' `labels` derives from the roll, and the old stand-in
  handed it the raw pair); `git log` is given a path from the repository's top.

The 17 census tests the sweep cannot run on a map are the baseline's 16 and the superseded one: seven roll or build
their own input (the polder soak's five, whose rules the sweep reads through `law:bends` and the roll's seating on every
map; the seatings' three; the tract seams), the pool's regeneration test, the cohort test and the dike-pond archetype
test (which roll their own), the Mode A sheets (a bundle, not a manifest), and the hand-sheet captions (a module deleted
before the baseline).

**The result.** The bar is zero failing predicates and zero re-rolls. **Zero re-rolls holds; zero failing predicates
does not.**

| | plain | under the probes |
|---|---|---|
| rolls; rolls that produced a map | 53; 53 | 53; 51 (two refused, below) |
| maps clean of every predicate | 45 | 43 |
| builds per roll; re-rolled maps | 1; 0 | 1; 0 |
| households unseated on a produced map | 0 | 0 |
| maps reaching plan D12's terminal | 0 | 0 |
| maps recording their woodland off the sheet (plan D11) | 2 (cohort 13, Kuwabata) | 4 (cohort 13, 32, Kuwabata, Sawada) |
| `law:fragments` | 6 maps, 8 lanes | 6 maps, 7 lanes |
| `law:unreached_houses` and the roll's `farmhouses_reach_a_way` | 0 | 2 maps, 1 farmhouse each |
| `test_the_notice_board_faces_the_way` | 2 maps | 0 |
| every other predicate: every other lane rule, every enforced ring rule, the matrix, the belt's depth and holes, every other census test | 0 | 0 |

(Figures in the table: observed 2026-09-29, method: the sweep above; the baseline for comparison, observed 2026-09-29,
method: the same harness at cc39f599a: 0 of 53 maps clean on either pass, 8 maps re-rolled plain with 11 extra
attempts, 8 under the probes with 9.)

**Each failure, precisely** (observed 2026-09-29, method: the sweep above, each map's `failing`, `messages` and
`roll_trace`; the committed manifests read directly for the pool's two):

1. **A short access corridor stays drawn** (`law:fragments`, homes H40; observed 2026-09-29, method: the sweep and
   `law.short_fragments` on the committed manifests). Plain: Kashikawa (lane 17, 28.8 ft), Mizuguchi
   (lane 11, 16.1 ft), cohort 13, 23 (two), 24 (two), 37. Probes: Mizuguchi, cohort 13, 14, 24, 25 (two), 45. Each is a
   lane of the tree (`role: access`) shorter than `FRAGMENT_FT` whose removal would leave no house unreached, no second
   network and no target unserved (`law.short_fragments`). `settle.settle_fragments` drops only lanes that are not tree
   lanes (`corridors.is_tree`), so the predicate and its placer disagree (FR-003) and the pool ships two of them.
2. **A farmhouse off the way network**, under the probes only: cohort seed 8 and seed 39, one farmhouse each
   (`law.unreached_houses`; the map's `meta.roll_failures` carries `farmhouses_reach_a_way[1]`). Both maps also place a
   well the baseline body judged open ground (the twin, below). The closing census (R10, ways W01) names the branch: when
   the lawful-route test refuses the reserved run, the routed run and the dooryard route alike, `draw_corridors` records
   the house in `meta.access_refused` and the map ships with it unreached.
3. **A notice board side-on to its way**, plain only: cohort seed 25, the board at (2038, 2686) standing 55 degrees off
   its nearest way; cohort seed 42, at (2792, 2532), 86 degrees off (the rule: 45). The retired test's body is the
   baseline's, unchanged; R8 retired it to `siting.py:place_kosatsuba` (`nearest_way_bearing`).
4. **Two probe rolls refused, no map produced.** Inashiro: `OverlapRefused` - a farmstead fixture laid in a homestead's
   bundle would be recorded on a field ditch at (2960, 1780), raised by the registry when `stage_homesteads` holds the laid
   parts (`holds.hold_laid_parts` -> `Standing.hold`); the bundle's fixture layout did not ask the registry first, so the
   refusal is an exception at record time, not a placer's choice. Cohort seed 18: `SiteRefused` - no margin of the 17
   tried seats all 15 households (the best seated 13), plan D2's refusal of an impossible site; D2 sends a cohort seed
   that reaches it to the GM with its count: 1 of 106 rolls, under the probes only.

**Where a retired test's baseline body and its last body disagree** (the twin; not counted, recorded): the wells' test at
cc39f599a (the box-gap measure FR-003 replaced with the placer's `well_gap_to_dwellings`) fails 5 rolls (cohort 8 plain
and probes, 15 and 20 plain, 39 probes) that the placer's own predicate passes; the belt-depth test at cc39f599a (its own
depth measure) fails 3 (cohort 9 under the probes, 19 on both), which `belt_law`'s reading passes. The restated two: the
copse-reach body fails 44 rolls on the against-the-belt seeds, which W25's restatement passes; the runoff body fails 21,
every one a misreading above, which the corrected predicate passes. (Observed 2026-09-29, method: the sweep above,
`base_messages`.)

Every census test the sweep runs judged at least one map; the polder's own (the dike, its gaps, the laterals, the sty's
half) judge Kuwabata's rolls alone, and the woodland commons tests read the maps that seat one (the four D11 maps
excepted).

## R10 - The closing census (2026-09-29)

**The selection** (observed 2026-09-29, method: `python3 specs/287-placer-guarantees/census_select.py` on the clone at
bf705bee3, diffed by name against `census-raw.txt`). It selects 90 tests where the opening census selected 195: 66 of the
opening selection remain, 130 are gone (the retirements of R8 and the modules they emptied), and 24 are new. Of the 66
that remain, 57 are mechanics, 1 is a placer unit test, and 8 are the finished-map tests R8 KEPT, each with its reason
there (the three board-caption tests for plan D12, the reed strip, the dike-pond archetype's record, the cohort's reach
report, the pool's regeneration and the Mode A sheets). Of the 24 new: 2 are finished-map tests of properties no placer
owns, kept as R8's (a) (`test_no_stage_after_the_view_is_decided_moves_the_frame`,
`test_every_pool_hamlet_records_the_regional_northwest`), 1 is a placer unit test
(`test_ring_rules::test_the_fan_context_is_the_one_the_gate_reads_off_the_manifest`), and 21 are mechanics (the tools'
own tests, the one-build contract `test_generate_builds_once_and_reports_what_it_built`, the village entrypoint, records
and budgets). No selected test asserts a placement rule that is not in the rule list below.

**The judgment** (observed 2026-09-29, method: five Opus readers, one per area, each given its design file
`design/design-<area>.json` - the 175 distinct rules R1's 118 finished-map rules, R2's 31 breaking fallbacks and R3's 58
open violations resolve to (`scope-by-owner.json`) - with R7, R8 and the plan's decisions, and asked of today's code per
rule: GUARANTEED (the placer that refuses, repairs or constrains, read, and one unit test on constructed input including
the violating case, found in the tree), a recorded DECISION (cited), or a GAP; then corrected by the acceptance sweep, R9,
where a map broke a rule a reader had read as guaranteed; the readers' rows are the session's `close-<area>.json`, not
kept). The same judgment as R1's: a finished-map check followed by a re-roll or a retry does not count; a refusal of an
impossible site by name does (plan D2, D7).

| area | rules | guaranteed | recorded decision | gap |
|---|---|---|---|---|
| water | 59 | 52 | 4 | 3 |
| homes | 47 | 38 | 7 | 2 |
| ways | 25 | 23 | 0 | 2 |
| woods | 26 | 24 | 0 | 2 |
| labels | 18 | 17 | 0 | 1 |
| **all** | **175** | **154** | **11** | **10** |

**Guaranteed** - each rule's mechanism (`path:function`) and its unit test are its row in the readers' files; the
retired tests' share of them is R8's table, row by row. By area: water's brook rules in `feed_brook` (every candidate
judged on `drawn_course`, else `BrookRefused`), the paddy rings in `seams/close.py:hold_ring_rules`, the sink's routes and
pond seat in `sink.py`, the fan in `fit.py:fit_field` (`fan_legal`, `FieldRefused`), the polder in `waterfields/polder.py`
and `hamletgen/water/polder.py`; homes' seating in `homesteads/stages.py:seat_every_household` (`SiteRefused`) and the
bundle's parts in `settlement/rolling/fit.py` and `lot.py`; ways in `ways/settle.py` (the settle's steps over
`law.py`), `track.py` and `clearance.py`, the decks and planks in `settlement/city/bridges.py`; woods in
`homestead_parts/stands.py`, `belt_law.py:settle_the_belt`, `wood_share.py`, `hinterland/parcels.py` and `land/cover.py`;
labels in `labels/placer.py`, `structures/fixtures/board_seat.py` and `siting.py`, `settlement/finish.py` and
`compound.py`.

**Recorded decisions** (11): water W26 and W27 (a plot's working width and its dart: recorded, not enforced - R7, a guess
held open, for the GM); water W36 (restated: the coarse-grain need is covered by the dry band or winter barley - R7);
water W48 (no subject beyond the polder's other rules - R5); homes H02 (no producer - R8), H13 (no per-pond sluice - 280
M57), H33 (no woodpile-form knob - 280 M21), H36 (no hamlet burial ground - 280 M68); homes H05 (the cluster-shape knob
narrowed to what the band draws - plan D4), H34 (the bath a room joined to the house, the rolled wall tried first - 280
M22), H35 (the wood shed a ken off a wall, refused where none - 280 M21). Held for the GM with the rules they touch:
**D6** (woods W11 is guaranteed under D6's bare-ground predicate, which counts every recorded footprint and tread as
covered), **D11** (a woodland off a tight sheet recorded off it with its bearing: 2 maps plain and 4 under the probes in
R9), **D12** (the board terminal: 0 of 106 rolls in R9; the crown and off-its-board clauses of labels L3, L4, L6 and L7
stand guaranteed on every other path and open with D12 at the terminal), and **W26** (with W27).

**Gaps - rules neither guaranteed nor a recorded decision** (10):

| rule | what is missing |
|---|---|
| water W39 - the paddy cell stays inside its 0.030-0.072 acre band | no placer holds it: `fit_field` holds the acreage, not the cell; R8 keeps it in `full/test_villages` as not yet guaranteed |
| water W43 - a waterward reed strip reaches the view's edge | held when the view is decided (`frame.py:to_the_strips`); `finish._title_band` grows the sheet afterwards on a water-facing north or south flank, and nothing re-asks (R8, Kept) |
| water W53 - nothing lies where the overlap matrix forbids | the registry refuses at record time, but not every placer asks it first: under the probes Inashiro's bundle laid a farmstead fixture on a field ditch and the hold raised `OverlapRefused` (R9, failure 4) - the fixture layout must ask `Settlement.admits` |
| homes H29b - a generated Mode A sheet's sitings (coverage band, perimeter hugging, the wells) | only the tubs and the notice board are placer-held, by assertion at construction (`compound_parts.py:_point_features`); nothing holds the coverage band when `place()` grows the envelope, nor the perimeter or the Mode A wells |
| homes H40 - no lane shorter than `FRAGMENT_FT` that earns nothing | `settle_fragments` skips the tree's lanes, so a short access corridor that earns nothing stays drawn: 6 maps plain and 6 under the probes in R9, Kashikawa and Mizuguchi among the pool (the reader read it guaranteed; the sweep corrects it) |
| ways W01 - every farmhouse reaches the way network | `corridors.draw_corridors`' last fallback, when the lawful-route test refuses every run, records `meta.access_refused` and ships the house unreached; R9: cohort 8 and 39 under the probes |
| ways W03 - a way reaches the field | the seating reserves a field corridor on lawful ground, but at draw time the joint, end and way-out clauses the seating never asked can refuse every run and `settle_field` leaves the field unreached (`web_settle.field_unreached`; pinned by `test_a_target_or_a_field_no_lawful_run_reaches_is_left_unreached_not_drawn_least_bad`); no map reached it in R9 |
| woods W08 - the marsh's record is the ground its reeds are drawn on | holds as the marsh is laid; a household shrine's clearing swept later culls the reeds inside it (`cover.py:_cull_cover_in`) and the record is not shrunk |
| woods W26 - a coppice lot is bounded by what bounds it, not a stamped disc | the not-a-disc half holds by construction (`_parcel_outline`); the bounded-by half and its predicate were never built, and the design's question for the GM (what a lot's line followed) has no recorded answer |
| labels L12 - the notice board faces its way | R9: cohort 25 (55 degrees off) and 42 (86 degrees off) plain; the reader read `place_kosatsuba`'s turn as a guarantee, the sweep corrects it |

**Readers' caveats on rules left guaranteed** (for the lead, not gaps): labels L11's unit test has no violating case (the
far-verge case the design named was never written); water W09 holds the weir's root at the mouth's downstream lip, where
the design said upstream; water W10 holds on the hamlet path, while the village and city comb's drain run
(`fields/comb.py`) does not ask `runs_downhill`; water W36's two R7 bullets disagree (one says it stays open in T12, the
later one records it narrowed); homes H09 (a well pocket pushed past the beds has no explicit gap check), H16 (the final
reach is reported, not refused - the gap above), H29c (a caption may sit over soft ink on a hand sheet; dark-on-dark is
handled by the ink's color), H45 (the kura share is 280's one in eight, not the design's 0.2993); woods W09 (a single wet
leg over about 1,440 px could survive the walk-back), W13 (the woodland's room is re-read at draw time after later
fixtures, unmeasured). (Observed 2026-09-29, method: the five readers above.)

**SC-001 is not met**: 10 of 175 placement rules are gaps, four of them (homes H40, ways W01, labels L12, water W53) seen
on maps in R9. Separately, plan D2 owes the GM its count: the seating refused one site (cohort seed 18, under the probes),
1 of 106 rolls. R2's fallbacks and R3's excuses are inside the
175 through `scope-by-owner.json`; the one R2 row recorded and not converted is the town-only `wards.py:_ward_ends_on_wall`
(spec, Edge Cases).

## R11 - The acceptance sweep after wave 6 (2026-09-30)

**Method** (observed 2026-09-30, method: `make spec-harness SPEC=specs/287-placer-guarantees/sweep OUT=<json>` in the
clone at 0e4bf59c5 with the harness as amended below, four workers (`SWEEP_WORKERS=4`) under the session's cohort lock,
106 rolls in 358 s wall; the output is the session's `sweep-287-r11b.json`, not kept). The same 53 maps and the same two
passes as R9 - the five pool hamlets from their generators' `HamletSpec` and cohort seeds 1-48, plain and under feature
284's two withdrawn levers as probes - each finished manifest asked the same predicates: the lane law (`law.LAW`, 29 rules
by name), the ring rules over every recorded plot ring (32,902 rings plain, 31,822 under the probes), the overlap matrix,
the windbreak as `settle_the_belt` reads it, the roll's own seating and reach verdict, and the same 101 census tests (98
retired ones run as their bodies last stood, 9 baseline twins, 37 read through an engine predicate, 2 restated, 1
superseded and listed, 17 that cannot run on a map - R9's list, unchanged).

**What changed in the harness since R9**: one adapter, no predicate. Feature 287's perf pass (b7b88b9e1) gave the
router's `lattice_search` two more arguments, the caller's verdict memos `free` and `band`, which the search reads before
it asks `is_free` / `in_band`; those two callbacks fill the same memos, so the memos are a cache and not a rule. The A*
probe (`astarcmp/astar.txt`, written before the memos existed) is wrapped to take them and ask the callbacks instead: the
same verdicts, the same A* search 284 withdrew. The first run at this HEAD, before the adapter, raised
`TypeError: lattice_search() takes 8 positional arguments but 10 were given` on 52 of the 53 probe rolls and is not
counted (observed 2026-09-30, method: the same command, 342 s wall; its plain pass agreed with the one below map for map).
The saturation probe's `_fit_at_aspect` keeps its signature and needed nothing. No predicate the harness names was renamed
or moved since R9, so no test was re-pointed.

**The result.** The bar is zero failing predicates, zero re-rolls and zero unreached houses. **Zero re-rolls and zero
unreached houses hold; zero failing predicates holds under the probes and fails on one map plain, by one retired test's
body, which the engine predicate R8 names in its place passes.**

| | plain | under the probes |
|---|---|---|
| rolls; rolls that produced a map | 53; 53 | 53; 52 (cohort seed 18 refused by plan D2, below) |
| maps clean of every predicate | 52 | 52 of 52 produced |
| builds per roll; re-rolled maps | 1; 0 | 1; 0 |
| households unseated on a produced map | 0 | 0 |
| `law:unreached_houses` and the roll's `farmhouses_reach_a_way` | 0 | 0 |
| `law:fragments` | 0 | 0 |
| `test_the_notice_board_faces_the_way` | 0 | 0 |
| maps reaching plan D12's terminal | 0 | 0 |
| maps recording their woodland off the sheet (plan D11) | 4 (cohort 4, 13, Kuwabata, Mizuguchi) | 3 (cohort 13, Kuwabata, Mizuguchi) |
| retired test `test_every_pool_belt_keeps_its_depth_across_its_windward_face` (its frame-held half, body as last stood) | 1 map (cohort 34) | 0 |
| every other predicate: every lane rule, every enforced ring rule, the matrix, the belt's depth and holes (`belt:thin`, `belt:holes`), every engine reading (37 tests), every other census test | 0 | 0 |

(Figures in the table: observed 2026-09-30, method: the sweep above, `summary` and each map's `failing`, `builds`,
`per_attempt_unreached`, `seated`, `d12` and `woodland_offsheet`. Against R9, observed 2026-09-29: 45 clean plain and 43
under the probes, 6 maps with fragments, 2 unreached farmhouses under the probes, 2 boards side-on, 2 probe rolls refused.)

**The one failure, precisely** (observed 2026-09-30, method: the sweep's `messages` for the map, then a scratch harness
rolling cohort seed 34 plain through `make spec-harness` and reading `belt_law.reading_of` beside the retired body's own
arithmetic; the scratch harness is not kept). Cohort seed 34, plain: the retired test's frame-held clause - a belt no bin
of which is judged must stand against the page, every 40 ft bin's crown nearest the edge within `BELT_DESIGN_DEPTH_FT`
(110 ft) of it - fails on one bin: the body bins crowns from the origin (`int((x*ax + y*ay) // 40)`), and its bin 1 holds a
single crown at the belt's far tip 117.8 ft from the page's edge. `BeltReading.off_the_page` - the predicate R8 names as
this clause's replacement, which `settle_the_belt` asks - bins from the belt's own start (`rd.bin(v)`, bins 0-19), where
that crown shares bin 0 with a crown 18 ft from the edge, so it returns no bin, the belt is left unjudged, and the engine
reading passes. Read strictly (`_depths(lenient=False)`), every one of the belt's 20 bins is 88-315 ft deep, none under
`MIN_BELT_DEPTH_FT` (30 ft). The two measures of one rule disagree on bin alignment alone; the map carries no thin stretch.
Not fixed (the task is a measurement); FR-003's form for this is the retired body reading its placer's own predicate.

**Cohort seed 18 under the probes: plan D2's refusal, for the GM as a count.** `SiteRefused`: no margin of the 17 tried
seats all 15 households (seated per margin: 11, 11, 12, 10, 10, 11, 11, 8, 14, 9, 13, 12, 11, 14, 11, 10, 11 - the best
14); 1 of 106 rolls, under the probes only, as in R9 (observed 2026-09-30, method: the sweep above, `roll_errors`). Not
counted as a failure. Inashiro's probe roll, refused in R9 by `OverlapRefused`, now produces a clean map, and so do cohort 8
and 39 under the probes (R9's unreached farmhouses).

**The twins and the restated two** (not counted, recorded; observed 2026-09-30, method: the sweep above,
`base_messages`): the wells' test at cc39f599a fails 5 rolls and the belt-depth test at cc39f599a fails 3, which the
placers' own predicates pass; the copse-reach body fails 44 rolls, which W25's restatement passes; the runoff body fails
21, every one R9's misreading, which the corrected predicate passes - the same counts as R9.

## R12 - The closing census after wave 6 (2026-09-30)

**The selection** (observed 2026-09-30, method: `python3 specs/287-placer-guarantees/census_select.py` on the clone at
0e4bf59c5, diffed by name against `census-raw.txt`). It selects 89 tests (R10: 90): 65 of the opening selection remain,
131 are gone, and the same 24 are new. The one fewer is `tests/gate/test_bunds_and_dikes.py::test_the_waterward_reed_strip_runs_off_the_frame`,
one of R10's eight KEPT finished-map tests, retired with its module (fdc5e1209: water W43 held at the view's decision, the
title band and the key band's neatline). Of the 65 that remain, 57 are mechanics, 1 is a placer unit test and 7 are the
finished-map tests R8 KEPT (the three board-caption tests for plan D12, the dike-pond archetype's record, the cohort's
reach report, the pool's regeneration, the Mode A sheets). No selected test asserts a placement rule outside the 175.

**The judgment** (observed 2026-09-30, method: five Opus readers, one per area, each given its design file
`design/design-<area>.json`, R7, R8, R10, the plan's decisions and the commit messages since R10, and asked of HEAD per
rule: GUARANTEED (the placer that refuses, repairs or constrains, read, and one unit test on constructed input including
the violating case, read), a recorded DECISION (cited), or a GAP; told that R10's readers had read H40 and L12 as
guaranteed and the sweep broke them; then checked against R11 - no rule a reader read as guaranteed broke on a map; the
readers' rows are the session's `close-<area>.json`, not kept). The same judgment as R1 and R10.

| area | rules | guaranteed | recorded decision | gap |
|---|---|---|---|---|
| water | 59 | 54 | 4 | 1 |
| homes | 47 | 40 | 7 | 0 |
| ways | 25 | 25 | 0 | 0 |
| woods | 26 | 25 | 0 | 1 |
| labels | 18 | 18 | 0 | 0 |
| **all** | **175** | **162** | **11** | **2** |

**R10's ten gaps** (observed 2026-09-30, method: the readers above, each naming the placer and its unit test):

| R10 gap | now | placer | unit test |
|---|---|---|---|
| water W39 | **gap** (below) | - | - |
| water W43 | guaranteed | `finish.py:band_keeps_the_strips`, asked in `_title_band`, with `frame.py:to_the_strips` | `test_finish_287::test_the_title_band_is_not_grown_on_a_flank_a_reed_strip_runs_off` |
| water W53 | guaranteed | every hamlet writer asks `Settlement.admits` first (`bundle_admitted`, `drain_admitted`, the weir's walk, `board_record`, `lanes.py:lane()`); a one-candidate writer raises `OverlapRefused` by name (`refuse_unadmitted`) | `test_w53_writers_287::test_a_stream_a_pond_and_a_sluice_the_matrix_forbids_are_refused_before_any_ink`, `test_m8_placers_287::test_the_bundle_fit_refuses_a_layout_the_registry_refuses` |
| homes H29b | guaranteed | `compound.py:place` asks the audit's coverage and hugging bands of the placed composition (`composition_sitings`) and refuses out of band (plan D7); `compound_parts.py:garden_well` a clear seat or none | `tests/test_compound.py::test_a_grown_compound_that_falls_out_of_its_band_is_refused_naming_what_grew_it`, `::test_a_program_that_requires_a_well_and_has_no_seat_for_one_is_refused`, `::test_the_garden_well_is_seated_on_clear_ground_or_not_at_all` |
| homes H40 | guaranteed | `ways/settle.py:settle_fragments` over `law.short_fragments`, tree lanes included | `tests/hamletgen/ways/test_settle.py::test_a_fragment_is_dropped_and_a_chain_takes_one_width` |
| ways W01 | guaranteed | `access.py:access_corridor` admits a seat only when `tree.admits` passes; `tree.settle_tree` draws each chain as judged; `meta.access_refused` deleted | `test_access::test_a_seat_whose_corridor_the_tree_cannot_take_lawfully_is_refused_at_seating`, `test_settle::test_a_stranded_house_is_reached_along_its_corridor_and_the_tree_is_never_cut` |
| ways W03 | guaranteed | `homesteads/stages.py:reserve_field_corridor` asks `corridor_on_lawful_ground` and `tree.admits(FIELD_ROLE)`; the field-unreached fallback deleted | `test_homesteads_287::test_a_margin_with_no_lawful_field_corridor_seats_no_one`, `test_settle::test_the_field_corridor_the_seating_reserved_is_the_field_way` |
| woods W08 | guaranteed | `land/wet.py:shrink_marshes_off`, called from `cover.py:_cull_cover_in` on every swept clearing | `test_woods_287::test_a_clearing_swept_in_the_marsh_after_it_is_laid_leaves_the_marsh_record` |
| woods W26 | **gap** (below) | - | - |
| labels L12 | guaranteed | `board_seat.py:WayFacing.turn` turns every sampled seat; `siting.py:_route_seats` refuses a corner tie more than 45 degrees off | `test_board_seat.py::test_a_board_is_turned_to_its_way_and_refused_where_it_cannot_face_it`, `::test_the_facing_predicate_turns_to_the_nearest_way_and_refuses_a_corner_tie` |

R10's caveats closed in the same wave: labels L11's violating case
(`test_board_seat.py::test_a_board_stands_no_farther_from_its_way_than_the_reach_even_where_only_the_far_ground_is_open`);
the L6 rounding tie (`board_caption_seat` passes `place(accept=)` the `stands_nearest` check on the recorded, rounded
geometry; `::test_a_yard_just_nearer_than_the_board_on_the_record_moves_the_caption`); water W09 (the bar at the mouth's
downstream lip recorded as historically accurate, research/water/253; woods W09's long wet leg walked back however long,
`tests/settlement/test_land.py`); water W10 (the village drain run asks `runs_downhill`, `outfall_run`); woods W13
(`hinterland/stages.py:stock_woodland`, `test_hinterland_287::test_a_parcel_whose_room_later_fixtures_took_is_clothed_as_grazing_not_drawn_a_thin_wood`);
water W36's two R7 bullets now agree (0bb5bdede); homes H09's pushed well pocket keeps its gap from every bed
(`pocket_clear_of_beds`).

**Recorded decisions** (11, as R10): water W26 and W27 (recorded, not enforced; a guess held open for the GM - R7), W36
(the winter-crop knob narrowed to what the site can feed - R7), W48 (no subject beyond the polder's other rules - R5);
homes H02 (no producer - R8), H05 (plan D4), H13 (280 M57), H33 (280 M21), H34 (280 M22), H35 (280 M21), H36 (280 M68).
Held for the GM with the rules they touch, as R10: D6 (woods W11), D11 (the woodland off a tight sheet: 4 maps plain, 3
under the probes in R11), D12 (0 of 106 rolls in R11).

**Gaps - rules neither guaranteed nor a recorded decision** (2):

| rule | what is missing |
|---|---|
| water W39 - the paddy cell stays inside its 0.030-0.072 acre band | wave 6 calls it a village/city rule (hamlets keep the GM's grain, research/fields/110's 0.02-0.25 acre), but that is written only in commit aa49a0bd7's message: no line of this file, the plan, research/fields or the code records it, and `tests/full/test_villages.py` still says no placer holds the cell to the band. On villages and cities no placer holds it either. Either a placer on the village/city carve, or a decision recorded here and at the point of change taking the rule off hamlets and saying what that costs |
| woods W26 - a coppice lot is bounded by what bounds it, not a stamped disc | unchanged from R10: the not-a-disc half holds by construction (`hinterland/parcels.py:_parcel_outline`); the bounded-by half (a lot's line following a lane, brook or crop line), its predicate and a violating-case test were never built. research/vegetation/140 labels "follows ridge, stream and path" a GUESS - the record is silent on what a lot's line followed, so it is the GM's question, but no decision records it as held for the GM |

**Readers' caveats on rules left guaranteed** (for the lead, not gaps; observed 2026-09-30, method: the readers above):

- ways W01 / W03, homes H16: the seating now guarantees every house and the field a lawful corridor, but `settle_the_web`'s
  last resort (reached only when its rounds do not settle) drops every lane that hands a household a way out over the
  brook and back, tree lanes included (ways W08), and a house or field that leaves unreached is reported in
  `meta.roll_failures`, not refused (`ways/settle.py`, pinned by
  `test_a_way_out_left_over_the_brook_after_the_last_resort_loses_its_lanes`). `tree.admits`' way-out check asks the new
  house's chain only to the strip's end, so nothing rules the trigger out; R11 measured 0 unreached on 105 produced maps.
- homes H09: the pushed pocket's gap from the beds holds; its gap from its own dwelling is still unasserted and the
  push loop has no bound. H41: the violating case is `test_geom::test_trim_to_service_pulls_an_end_back_to_what_it_serves`;
  tree lanes are exempt from the trim. H45: the kura share is 280 M20's one in eight, not the design's 0.2993. H29c as R10.
- water W10's residue: the legacy `Settlement.channel` (`paddy.py`, `nearring.py`) and the city's
  `moat.py:inwall_drain_outfall` record channels without asking `runs_downhill` (no hamlet path). W53: only the hamlet
  registry is strict; town and city registries still record without refusing. W44's test asserts on two builds, not a
  constructed miss.
- woods W09: `trim_off_marsh` sees only marshes recorded when it runs (the toe marsh and the waterside strip are laid
  later); W21 has no unit test putting a lane through a woodland parcel; W14's violating case is a patched share; ways W23 /
  W24: the connector's squared crossings are not asked about wet ground again, unmeasured and unseen.
- labels L3: its shaded-seat violating case is at siter level only; at D12's terminal the knob resolves without the
  sitable filter (worst case no board).
- `tasks.md` still carries open tasks for water (T12, T13, T14, T18) and woods (T68).

**SC-001 is not met**: 2 of 175 placement rules are gaps (water W39, woods W26), neither seen on a map in R11; 162 are
guaranteed and 11 are recorded decisions. SC-003's sweep (R11) meets zero re-rolls and zero unreached houses and misses
zero failing predicates by one retired test's body on one map, which the engine predicate replacing it passes. Plan D2
owes the GM its count: cohort seed 18 refused under the probes, 1 of 106 rolls.

**After R12** (2026-09-30): the census's two gaps are recorded decisions in R7 - water W39 a recorded drop on the hamlet
path (the village and city calibration; no scripted generator draws either tier yet), woods W26 held for the GM (the
record silent after two search passes). SC-001 therefore stands at 162 guaranteed and 13 recorded decisions of 175. R11's
one belt-depth reading on cohort 34 is the retired test's grouping, not the rule: the rule's one predicate
(`belt_law.BeltReading.off_the_page`, which feature 287 made the placer's and the test's) passes that map, and every
stretch of its belt reads 88-315 ft deep (observed 2026-09-30, method: the sweep implementer's scratch harness over the
R11 manifest of cohort 34).
