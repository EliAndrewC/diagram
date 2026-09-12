# Audit: `settlements/water.md` against `research/water.html`; `settlements/ways.md` and `settlements/presentation.md` (no research counterpart)

Independent Opus reader, 2026-09-12. Classes as in `homesteads.md`.

## Cross-cutting

1. The retired check battery is quoted throughout as if live: water.md names ~42 checks, ways.md ~12, presentation.md ~22; about half survive as re-implemented rules in `tests/gate/` and `tests/settlement/`, the rest are gone. water.md cites 3 `pool/regressions/*.json` fixtures and 4 `tests/check_village/` tests that do not exist.
2. Ten of water.md's fifteen deep links into `research/water.html` are broken (the `---` slug rule). `inashiro.notes.md:298` links to `research/water.md`.

## water.md (86 lines, ~60 units)

Share: A ~28%, B ~28% (~75% of it encoded with a comment), C ~7%, D ~25%, E ~12%; F inside ~60% of units.

Key units (class / engine or anchor):
- Villages must have a water source, kind is village-specific; ~33 px corridor - B+E; corridor `hamletgen/water.py:662`; `no_structure_on_channel` NOT FOUND.
- Source brook DIVERTED (Ikegami) - C+E; `stream_runs_off_edge` NOT FOUND.
- DRAINAGE pond below the field `pond_role` - B; live in `tests/gate/test_water_junctions.py`.
- Water flows downhill `meta(downhill)` - B; `channels_flow_downhill` live; `downhill_direction_valid` NOT FOUND.
- Watercourses MERGE like a confluence - B; `settlement/finish.py` `_water`.
- REEDS KEEP OFF THE EARTHEN MOUNDS (GM 2026-08-28) - A; `#a-reservoirs-shore-is-reeded-and-its-embankment-is-mown---the-two-are-different-ground`.
- ONE WATER BLOCK, EVERY WATERCOURSE IN IT (GM 2026-08-28) - D; mechanism `finish.py`.
- A pond JOINS its feeders at the rim, LATE block - B; `pond_fill_covers_channel_mouths` live.
- Water sources for city fans - three patterns, sluice gates, in-wall drain - E+B; `settlement/city/moat.py:154,192`.
- Streams stay between fields; every field SHOWS a source - B; live in `test_water_flow.py`.
- DRAINAGE SLOPE IS PER-FIELD - B; `drain_flows_downhill` / `drain_runs_cross_slope` live.
- Mirrored fan must stamp the DRAWN fall - D+E. Trimmed in-wall drain not a contour collector - D+E. Edge outfall at the DOWNHILL edge (Nagahara fnn2) - D. HOW THE DISCHARGE END IS IDENTIFIED - four failed shortcuts - D; `drain_tail` NOT FOUND. Pool ALL the evidence and take the LOWEST - D.
- WATER FLOW - every map declares a DRAINAGE BEARING - B; `water_flow` 11 engine sites; three checks NOT FOUND.
- WHAT THIS IS FOR: verisimilitude, NOT uniformity (GM 2026-07-25) - D (compressed at `SKILL.md:84`).
- The ONE hard rule and the anti-pattern (river parallel to a range) - D.
- MOAT JUNCTION SWEPT WITH THE CURRENT - A (`#canal-junction-angles---an-offtake-leaves-pointing-downstream`, link broken); the four measured lessons (local segment; averaged vertex tangent, ~8-9 deg bias; arc length not vertex; cap the walk ~90 px) - D+E; `moat_swept_tap` `city/knobs.py:42`.
- ONE DIRECTION MODEL, NOT THREE (GM 2026-07-25) - D: two checks gated on a knob 2 of 17 maps declared; 15 maps skipped them green.
- Moat current SNAPPED TO A CARDINAL - D: the tangent version built and rejected as measuring the wrong quantity.
- NO topographic markings, deliberately (GM 2026-07-25) - D; `settlement_declares_a_land_fall` live.
- Establish the bearing BEFORE drawing - C/D (SKILL.md:84).
- Two fields not one (fall vs flow); diverge < 90 deg, ±60 draft declined - D+B; no live check.
- Polylines UPSTREAM-FIRST, `flow="reverse"` - B. Navigable canal `flow="level"` - E+B; NOT FOUND.
- LIMIT of both angle checks (one regional bearing; a bank city breaks it; do not "fix" the map) - D.
- Moat records INLET and OUTLET `s.moat_flow` - E+B.
- KNOWN GAP - two cities declare no `down_deg`; 10-degree sweep; do not adopt the one value - D+F.
- ONE NAME per river - A (broken link). Fed CLOSED moat must DRAIN - A + E/B; `city_moat_has_outfall` NOT FOUND.
- Delivery takes off DOWNSTREAM of the head fork, 40 px - B; `comb.py:766`; live.
- Marsh where the paddy STOPS - A+B; `marsh_on_low_ground` live. Marsh UNBUILDABLE (GM 2026-07 quote) - D+B; `sacred_and_graves_off_marsh` NOT FOUND. NO WELLHEAD IN THE BOG (review 2026-08-12) - D+B: draw-order cause; measure below the crop's lowest point not the toe polygon; `toe_band()` `boundary.py:183`. DWELLINGS OFF THE WET TOE (GM 2026-07) - D: the "rectangular field = cross-slope drain" story refuted by measurement (269/340/352 px); `dwellings_above_field_drain` NOT FOUND. Why the marsh abuts the ditch on three maps not Akagahara - A part + D + F. Towns/cities NO toe marsh - A. Defensive marshland - A + E/B; `defense_marsh_girds_the_walls` NOT FOUND.
- In-field ditch geometry VALID - B; live. Irrigation topology ONE outlet - A. Head-race FORKS - A+B; live in `test_paddy_fabric.py`.
- Water-width ladder - A (broken). Stroke convention (GM 2026-07-21) - D+B; `MIN_CHANNEL_PX` `frame.py:84`. TAPER IS A SQUARE ROOT - A. Finest channel STOPS at the lateral tier - A. Bund UNBROKEN - A. COMB NET AT TRUE SIZE - A (but see disagreement 1). TAPER SUB-PERCEPTUAL - A in FULL on the page. Dry hem OFF the canal bank `CANAL_BERM_FT` 5.0 - A+B. PLANK only over water you cannot stride - A; `FOOTPLANK_MIN_FT`. SCALE enters the ladder in ONE place - A+B. DELIVERY NEVER WIDER THAN ITS CANAL - A; `DELIVERY_PARENT_FRAC` 0.8 / `SUB_PARENT_FRAC` 0.75.

### water.md D items
1. ONE WATER BLOCK (GM 2026-08-28, quoted: "water just flows"; the pond's rim absent at the intersection) - rendering convention, every map. 2. Verisimilitude NOT uniformity (GM 2026-07-25). 3. The river-parallel-to-a-range anti-pattern. 4. Moat-junction engineering record (four lessons, the ~8-9 deg bias). 5. ONE DIRECTION MODEL (two sources of truth is how drift starts). 6. Snapped to a cardinal (fine version measures the wrong quantity). 7. NO topographic markings (clutter), so declarations are mandatory. 8. Two fields not one; strict < 90; ±60 declined (pool's real 60 and 69). 9. LIMIT of both angle checks; a bank map trips it -> revisit the model. 10. KNOWN GAP two cities' `down_deg` (GM to decide 2026-07-24). 11. Marsh UNBUILDABLE (GM: "no one would ever put a graveyard - or a shrine - in a marsh"). 12. No wellhead in the bog (review 2026-08-12; cost Tango six wells unscoped). 13. Dwellings off the wet toe (GM; the false cross-slope story). 14. Why the marsh abuts the ditch - two wrong answers first, both invented without reading the gens. 15. Stroke convention (GM 2026-07-21): visibility floor is a sanctioned minimum, never a size license.

### water.md B items not encoded
`flow="level"`; `moat_declares_circulation`, `water_flow_declared`, `watercourses_flow_downstream`; `city_moat_has_outfall`; `sacred_and_graves_off_marsh` (0 refs); `dwellings_above_field_drain` (comments only); `defense_marsh_girds_the_walls` + the defensive-belt contract (~60 px, exempt from two rules, unbuildable); three moat-junction checks (`moat_swept_tap` exists, nothing grades it); `moat_is_heaviest_watercourse`, `moat_dwarfs_ditches`; `stream_runs_off_edge` + `at_ditch`; `no_structure_on_channel` / `houses_off_corridors`; `drain_tail()` and `name: <field>` wiring. All city/town except the two hamlet rules.

### water.md disagreements
1. `HEAD_RACE_FT`: md 5.0, `research/water.html:280` 5.0, engine 6.0 (`frame.py:27-35`, review 2026-08-17: `sqrt(4.5²+4.0²)`). The research page carries a wrong number.
2. The marsh-wedge "nevertheless correct" argument is marked superseded on the page; the md keeps both.
3. KNOWN GAP proposes the per-field fix the block above says was implemented.

## ways.md (24 lines)

Grounding elsewhere: the two lane-network rules ARE on `research/homesteads.html` ("Is every farmhouse reached by a lane, and in what FORM?", "How does a village lane bend?"). Lane WIDTH research is `research/SOURCES.html:28` as an absence note in the queue. Nothing in research/ covers roads, bridges, planks or the wheelbarrow.

Units: header - C; bridge carries a way over water - B+C (`city/bridges.py:156`; `roads_bridge_water` NOT FOUND); SOLVE a crossing never eyeball (GM 2026-07-27) - D (8 px / 8 deg tolerance from solved 0-1 px vs hand 17 px / 39 deg; `bridges_align_with_their_way` NOT FOUND); shuimen/ring-road mount - E; lanes OFF the dry plots (GM 2026-07-21) - B+D (3 px; the detour fought the packing); PLANK BRIDGES two kinds - B; standalone FOOTBRIDGES incl. the itabashi correction - B+D (`PLANK_ABUTMENT` `_geom/ways.py:21`; `channel_footbridges` `city/bridges.py:230`); footplank reaches USEFUL ground both banks (GM 2026-07-22) - B+D (`PLANK_VILLAGE_REACH` `_geom/ways.py:31`; live); plank never ON a farmhouse - B (`bridges_clear_of_houses` NOT FOUND); deck LANDS past its banks (GM 2026-08-09) - B physical (`LANDING_FT` `_geom/ways.py:23` with full reasoning; live); UNPAVED NARROW single track + the 2026-08-27 re-read (23 fetches) - B physical uncited (`consts.py:112` cites this file; widths `ways/track.py:323,380`, `ways/web.py:183`); CHINA the wheelbarrow and the porter - B physical uncited; WATER as the freight highway - canals a Rokugan EXCEPTION - D setting canon; JAPAN corroborating - B; Render `s.lane(...)` clearance - B+C (`WEB_CLEARANCE` 28 / `LANE_CLEARANCE`; `houses_clear_of_lanes`); connecting path RUNS OFF THE EDGE, OFF THE WET GROUND - B+A (`connector=True`; `connector_lane_runs_off_edge` NOT FOUND); Rokugan nuance corvee trunk network - D canon; Legacy `worn=False` - F; LANE WEB IS ONE NETWORK IN INK (GM 2026-08-27) - A+B (`ways/touch.py:99`; live); LANE BENDS THE WAY FEET WEAR A PATH (GM 2026-08-27) - A+B (`ways/smooth.py:112`; live).

Share: A ~15%, B ~45%, C ~10%, D ~20%, E ~5%, F ~5%.

### ways.md D items
1. SOLVE a crossing (GM 2026-07-27 Minami): why 40 px was insufficient, why it happened, the 8/8 derivation; "do not write bridge coordinates by hand." 2. dobashi -> itabashi (2026-08-19): earthen deck vs plank; deck size ruling (GM 2026-07-22). 3. Useless-plank census (GM 2026-07-22 Hikari 13 -> 11; six other maps); placer and checker read the SAME source. 4. Rokugan canal exception (GM canon: Lion lands; Crane coastal; Dragon Drowned Merchant River; Unicorn Firefly valley; boat landing on natural water; no canal by default). 5. Lane-width absence note (GM 2026-08-27 "not set arbitrarily"): 23 fetches, no numeric village-lane width in any language.

### ways.md B items not encoded
`roads_bridge_water`, `bridges_align_with_their_way` (8 px / 8 deg), `bridges_clear_of_houses`, `connector_lane_runs_off_edge`. `_TOUCH_GAP` is 1 ft in the md and 4.0 in `hamletgen/ways/geom.py:143` (engine records why).

### ways.md inbound / internal
`hamletgen/consts.py:112`; `kashikawa.notes.md:149`; `inashiro.notes.md:1393`; `wip/shiro-daika.notes.md:157`. Internal contradiction: 1px=2ft width passages vs the 1 ft/px re-read (pre-scale-ladder residue).

### ways.md verdict
Three physical researched findings live here and nowhere else: bridge landing (scour, bearing 5-15 ft), lane vehicle (wheelbarrow, porter, 23 reads, NOT FOUND number), itabashi. Plus the Rokugan canal canon. Propose `research/ways.html` with four questions: how far a bridge lands past the bank; what vehicle used a village lane; what a plank bridge is; where a village's freight goes. Thresholds stay in the engine.

## presentation.md (60 lines, ~34 units)

Grounding elsewhere: only the windbreak crop ruling (2026-07-20 CLIPS; 2026-08-26 INNER FACE) is on `research/homesteads.html` ~190-205. Nothing in research/ about labels, captions, titles, scale bars, crop; no Leopold & Wolman.

Units: no legend / no subtitle / no obvious labels / no compass (GM 2026-07-20 scale bar) - B+D (`no_label_overlaps`, `labels_within_image` live; `title_clear_of_features`, `scalebar_matches_declared_scale`, `labels_render_on_top` NOT FOUND); label-group registry - E+F (`future-work/cross-cutting.md:218` names this the WORST dead-gate assertion); `city_civic_label_on_its_own_building` - E+F; one caption per district (GM 2026-07-21) - E+D; quarter vs neighborhood - E; subtitle must add information - B+E (`religious_subtitle_not_redundant` NOT FOUND); CONTENT crop `crop_city` + history (GM 2026-07-23 aggressive crop; fans cut to 46 px slivers) - E+D (`city/crop.py:12` margin 35); `crop_to_content(margin=30)`, `vis_bbox`, 210 px bug - B (`core.py:613`; live in `test_crop_framing.py`); everything clips at the frame, bleed rule tried and removed - D (test exists); SWEPT BEND never a mitred corner (GM 2026-07-25), radius ~2.5 widths from Leopold & Wolman, cap 35% - B physical uncited (`fillet_polyline` `_geom/curves.py:18`; `round_channel_joints` `banks.py:573`); AMENDED 2026-08-26 INNER FACE sets the frame - A; windbreak does NOT set the frame (GM 2026-07-20) - A; call order for SET-APART hard features - C+B; runners ignored - B; crop advisory (`crop_relocatable_singletons` etc, 150 px) - F (0 hits); `_shrine_group` - F; valley-head pond NUDGE (Ueda ~157 px, ~9% smaller; N poke accepted; re-orienting declined - erases sibling variance) - D+F; nudged pond channels JOIN at the RIM - B; zone labels WITH the cluster - E+F; ONE FEATURE MUST NOT HOLD THE FRAME OPEN (GM 2026-07-25) - B+D (live); the discriminator is the RATIO not the gap (`gap > max(60px, 3 x extent)`; pool census 1.03-1.35x vs Tango 17.8x) - D (threshold NOT FOUND); reads `crop_boxes()` same list - B+D (17 maps byte-identical); extramural trade works framed by CAPTION, `kilns` LEFT the exclusion 2026-07-27 - E+D (`core.py:600` cites); `meta(crop_outlier_ok=True)` Tango example - F (knob NOT FOUND); empty ground wins (GM 2026-07) - B+D (`_geom/labels.py:20`); NEARNESS second term (GM 2026-07-26; Tango shipped both halves) - D (`place_caption` `castle_civic.py:635`); the ladder 5/6/9 - B (`LABEL_MIN_AIR` etc `_geom/labels.py:34-41` each with a comment); constraints; captions DEFERRED to `finish()` - B+C; road caption vs CROSS-SECTION (486x256 box, hint not distance) - D (`_best_label_spot` `castle_civic.py:528`); checks stay narrow - F (`labels_clear_of_other_buildings` gone; `label_hugs_its_referent` live; `LABEL_AIR_CAP` 3.0); Angled captions (GM 2026-08-02) - B+D superseded (`label_tilt`); LINEAR CLAMPS where a box FOLDS (GM 2026-08-08) - B+D superseded (`linear_tilt`, `frontage_rot`); A LABEL IS ALIGNED WITH THE THING IT LABELS (GM 2026-08-27) - B+D (`aligned_tilt`; live); CAPTION WRAPS (GM 2026-08-27) - B (`_caption_lines` `finish.py:195`; `LABEL_GROUND_KEYS`); HALF THE AIR OFF ITS SUBJECT (GM 2026-08-27, provisional) - B+D (`pull_caption_toward` `structures/captions.py:94`).

Share: A ~6%, B ~40%, C ~8%, D ~24%, E ~15%, F ~10%.

### presentation.md D items
1. Bleed rule tried and removed (add to `_CROP_HARD` instead). 2. City content-crop history (GM 2026-07-23 twice quoted; a label never pins the frame). 3. Outlier discriminator is the RATIO (GM 2026-07-25; pool census). 4. `crop_boxes` refactor verified byte-identical over 17 maps. 5. `kilns` left `_CROP_CITY` 2026-07-27 (both directions recorded). 6. `crop_outlier_ok` Tango example (8 px of 1402). 7. Valley-head pond nudge; re-orienting declined (sibling variance). 8. NEARNESS the second term (GM 2026-07-26). 9. Road caption cross-section; `label_xy` is a HINT. 10. A probe must measure the box the CHECK will measure (3.3x AABB overstatement). 11. 2026-08-27 alignment ruling's one session interpretation (square-rotated subject keeps a level caption; a question for the GM, not a clamp).

### presentation.md B items not encoded
Thirteen: `title_clear_of_features`, `scalebar_matches_declared_scale`, `labels_render_on_top`, `labels_clear_of_other_buildings` + registry, `city_civic_label_on_its_own_building`, `religious_subtitle_not_redundant`, `crop_hugs_content` (56 px quoted in five comments, enforced nowhere), `hard_features_within_frame`, `city_labels_placed_with_subject`, `road_label_tilts_with_the_roadway`, the crop advisory family, `crop_outlier_ok`, the `max(60px, 3 x extent)` discriminator.

### presentation.md inbound
`hamletgen/hinterland/stages.py:132`, `settlement/core.py:600`, `settlement/_geom/labels.py:20`, `homestead_parts/stands.py:339`, `settlements/vegetation.md:192`, four pool notes, `research/homesteads.html:205`. No numeric disagreement; the file asserts dead gates as live (named in `future-work/cross-cutting.md:218-219`).

### presentation.md verdict
Overwhelmingly map-drawing convention. The swept-bend radius is the one physical, uncited claim (Leopold & Wolman) and belongs on `research/water.html`. Split at the tier line: hamlet-applicable mechanism into the engine comments (already the exemplar); town/city label and crop rules kept as the specification of thirteen rules with no other statement.
