I ruled every number in `t38_N12-settlement-other.txt` from the record and the code. None needed a search pass: every number that says something about the world was already ruled in the record, or sits in code that no generator reaches. So I searched neither the archive nor the web, and added nothing to the sources ledger. I edited nothing.

## What the record says

- **`research/questions/0029-farmhouses-minka.drawing.html`**: "A house's length varies by roughly 0.85 to 1.35 of the base and its depth by only 0.90 to 1.10". That covers the 0.2 depth spread at `houses.py:465`, but that line never runs (see below).
- **`0005-rice-paddies-and-their-plots-suiden.drawing.html`**:
  - "On a hamlet map, drawn at a foot to the pixel, the usual basin is about 48 ft across its canal and 26 to 36 ft along it, about 1,500 sq ft (0.03 acre), the size the hamlet maps keep." This is `plot_texture`'s medium grain.
  - "On a valley hamlet's map the paddies are drawn larger, about 2.8 se (0.07 acre)." The page's hidden comment adds "about 70 x 37 ft on a 1 ft/px hamlet". This is the large_block grain.
  - "The maps allow a household about nine plots of 0.02 to 0.25 acre. Both are this project's own figures, a GUESS". This covers small_irregular.
- **`0031-clustered-and-scattered-villages-shuson-sanson.drawing.html`**:
  - "the crescent and the split village are this project's extension of them, a GUESS"
  - "Our maps give a village's lanes one of five shapes of our own choosing."
- **`0087-road-bridges-over-rivers-and-canals-hashi.drawing.html`**: "A deck must lie within about 24 ft and 8 degrees of its crossing." This bounds `seat_deck`'s skew of up to 7 degrees. The page has no 12% growth step and no 14-step count.
- **`0130-market-days-and-the-market-ground-ichi.drawing.html`**: "No stalls are drawn. No page we read says what a stall was built of, or whether anything of it stood between market days, so the map shows only the ground, a GUESS that nothing stood."
- **Earlier passes:**
  - T29 pass P7 ruled `skeleton_layout`'s headman and gateway positions record-silent, and `winding` NOT-ABOUT-THE-WORLD.
  - T29 pass P1 ruled the board's traffic floor NOT-ABOUT-THE-WORLD.
  - T38 pass N9 established that `road`, `moat`, `ring_road` and the widths that go with them are set only by tests.

## Code that no generator reaches (its numbers ruled NONE)

- **Functions nothing calls:**
  - `cluster_anchor`, `market`, `ancestral_hall` and `water_mouth` (searched by name under `l7r/`).
  - `water_field` and `fallow_field`, which are the only callers of `organic_bbox`/`organic_poly` and, through `paddy.py:444`, of `channel()` and `winding`.
  - `mill` is also unreached, as far as I could tell.
  - Nothing passes `inwall_drain_moat_bias`, so `inwall_drain_outfall` never runs.
- **Ways and waters no generator writes** (N9, plus my own greps): `road`, `roads`, `town_streets`, `alleys`, `ring_road`, `moat`, `wall`, `wards`, `river`, `castles`, `canals`, `aqueducts`.
- **Width fallbacks that never fire**, because every live record carries its own `w`: streams, channels, lanes, and comb field ditches (`comb.py:804`). The only ditch records without a `w` are written at `paddy.py:453`, by the dead `water_field`.
- **`plot_texture`:**
  - Every map in the pool is `"ftpx": 1.0`, and `HamletPlan.ftpx` defaults to 1.0. So the ftpx >= 2 table never runs.
  - `PLOT_SIZES` never rolls `strip`, and the pool fixes only `medium`, `small_irregular` and `large_block`.
- **`_try_place_bundle`, lines 465 to 469:** both branches run only when `_lot` is None. Every production `try_place` is `"plain"` with no role, and seating stops at the declared household count, so a lot always exists. That leaves the 0.2 (which 0029 would cite) and the 30/80 split dead.

| file::unit | line | value | ruling | what the number does |
|---|---|---|---|---|
| _geom/curves.py::fillet_polyline | 20 | 6 | NONE | samples per fillet ("curve plumbing - NONE") |
| _geom/curves.py::fillet_polyline | 62 | 0.35 | NONE | fillet cap per leg (the claim: "fillet cap and threshold - NONE") |
| _geom/curves.py::smooth_closed | 78, 79 | 6 | NONE | Catmull-Rom to Bezier constant |
| _geom/curves.py::smooth_points | 91, 92 | 6 | NONE | the same constant |
| _geom/curves.py::organic_bbox | 114 | 0.18 | NONE | outline jitter (no caller) |
| _geom/curves.py::organic_bbox | 116 | 0.35 | NONE | first-sample damping (no caller) |
| _geom/curves.py::organic_poly | 131 | 150 | NONE | densify step (no caller) |
| _geom/curves.py::winding | 138 | 15 | NONE | default amplitude; only dead `channel()` calls it (channel's own 15 is GUESS, T36 P2b) |
| _geom/indexes.py::__init__ | 254, 770, 831 | 128 | NONE | spatial-index cell |
| _geom/indexes.py::__init__ | 303 | 32 | NONE | point-grid cell |
| _geom/indexes.py::__init__ | 433 | 64 | NONE | ring-index cell |
| _geom/indexes.py::inside_many | 478 | 0.05 | NONE | boundary tolerance |
| _geom/indexes.py::_trees_for | 681 | 0.02, 0.05 | NONE | arc chord-error margin |
| _geom/indexes.py::_trees_for | 692 | 0.05 | NONE | the same margin |
| _geom/labels.py::aligned_tilt | 89 | 0.05 | NONE | angle tolerance |
| _geom/labels.py::label_quad | 140 | 7 | NONE | tuple index |
| _geom/overlap.py::poly_gap | 124 | 1e18 | NONE | sentinel |
| _geom/primitives.py::ring_offset | 224 | 0.25 | NONE | divide-by-zero guard on the miter |
| _geom/primitives.py::ring_offset | 226 | 1.5 | NONE | miter clamp (geometry) |
| _geom/primitives.py::keepout_ring | 282 | 1.5 | NONE | tolerance widened on retry |
| _geom/primitives.py::facing_chains | 336 | 1.5 | NONE | tolerance widened on retry |
| _geom/walls.py::torii_halfbox | 45 | 16 | GUESS (torii_glyph_dims claim, T36 P7) | torii span, live via `registry.py:135`; T29 P7's 2.5 to 5.87 m brackets 16 ft |
| _geom/walls.py::wall_runs | 67, 71 | 5.5 | NONE | rampart and wall-cap stroke half-width (no wall written) |
| _geom/walls.py::wall_runs | 69 | 2.5 | NONE | ward-fence stroke half-width (no wards written) |
| _geom/water_index.py::__init__ | 28 | 128 | NONE | index cell |
| _geom/ways.py::lane_runs | 57 | 30 | NONE | road_width fallback (N9: never set) |
| _geom/ways.py::lane_runs | 59 | 26 | NONE | roads `w` fallback (no producer) |
| _geom/ways.py::lane_runs | 61 | 18 | NONE | town-street fallback (no producer) |
| _geom/ways.py::lane_runs | 63 | 6 | NONE | alley fallback (no producer) |
| _geom/ways.py::lane_runs | 65 | 20 | NONE | ring-road fallback (no producer) |
| _geom/ways.py::way_beds | 88 | 8 | NONE | lane `w` fallback (lanes carry `w`) |
| _knobs.py::_toward | 219 | 0.45 | NONE | leg cap ("geometry - NONE") |
| _knobs.py::skeleton_layout | 477 | 0.12 | SEARCHED-SILENT (T29 P7; the unit's claim: T36 P7) | headman near a spine's head |
| _knobs.py::skeleton_layout | 479 | 0.4 | SEARCHED-SILENT (T29 P7) | T crossbar and headman, 0.4 up |
| _knobs.py::skeleton_layout | 483 | 0.2 | SEARCHED-SILENT (T29 P7) | Y fork and headman, 0.2 down |
| _knobs.py::skeleton_layout | 484 | 0.7 | GUESS 0031.drawing ("five shapes of our own choosing") | spread of the Y's arms |
| _knobs.py::skeleton_layout | 488 | 0.22, 0.4 | SEARCHED-SILENT (T29 P7) | headman's quadrant at the cross |
| _knobs.py::bridge_carried_ways | 594 | 30 | NONE | road fallback (claim: "with fallback widths - NONE") |
| _knobs.py::bridge_carried_ways | 596 | 26 | NONE | roads fallback |
| _knobs.py::bridge_carried_ways | 598 | 8 | NONE | ring-road fallback |
| _knobs.py::bridge_carried_ways | 602 | 6 | NONE | lane fallback (lanes carry `w`) |
| _knobs.py::bridge_crossed_waters | 612 | 9 | NONE | stream fallback (streams carry `w`) |
| _knobs.py::bridge_crossed_waters | 615, 617 | 4.2 | NONE | channel and field-ditch fallback (both carry `w`) |
| _knobs.py::bridge_crossed_waters | 619 | 12 | NONE | canal fallback (no producer) |
| _knobs.py::bridge_crossed_waters | 621 | 22 | NONE | moat fallback |
| _knobs.py::bridge_crossed_waters | 627 | 40 | NONE | river fallback (no producer) |
| _knobs.py::bridge_crossed_waters | 630 | 26 | NONE | castle-moat fallback |
| _knobs.py::bridge_crossed_waters | 632 | 8 | NONE | aqueduct fallback |
| _knobs.py::crop_boxes | 763 | 5 | NONE | tuple index |
| castle_civic.py::place_caption | 35 | 9 | CONVENTION | caption font size |
| city/bridges.py::seat_deck | 124, 133 | 0.12 | NOT-ABOUT-THE-WORLD | growth step of the deck search (0087 has no 12%) |
| city/bridges.py::seat_deck | 130 | 6 | NOT-ABOUT-THE-WORLD | a skew step, bounded by 0087's "8 degrees" |
| city/bridges.py::deck_glyph | 347 | 0.7 | CONVENTION (claim) | log at 7/10 of the deck |
| city/bridges.py::deck_glyph | 349 | 0.3 | CONVENTION | crown highlight |
| city/bridges.py::deck_glyph | 352 | 7 | CONVENTION | log-end ticks |
| city/bridges.py::deck_glyph | 356 | 0.8 | CONVENTION | tick length |
| city/bridges.py::deck_glyph | 360 | 7, 8 | CONVENTION | plank seams |
| city/bridges.py::deck_glyph | 365 | 2.4 | CONVENTION | rail offset |
| city/bridges.py::deck_glyph | 366 | 0.2 | CONVENTION | rail offset |
| city/bridges.py::channel_footbridges | 582 | 41 | NONE | taper sample count |
| city/bridges.py::_widen_for_confluence | 728 | 0.02 | NONE | divide-by-zero guard |
| city/moat.py::sluice_gate | 53 | 10.8 | CONVENTION | glyph normalizer (span is 0179's 20 ft) |
| city/moat.py::sluice_gate | 55 | 4.6, 9.2 | CONVENTION (claim) | board inside the span |
| city/moat.py::sluice_gate | 56, 57 | 5.4 | CONVENTION | posts at the span's ends |
| city/moat.py::sluice_gate | 63 | 4.4 | CONVENTION | crossbeam |
| city/moat.py::sluice_gate | 71 | 13 | CONVENTION | label offset |
| city/moat.py::sluice_gate | 72 | 4.2, 5.4 | CONVENTION | label reference box |
| city/moat.py::inwall_drain_outfall | 108 | 20 | NONE | ring-road fallback (unit dead) |
| city/moat.py::inwall_drain_outfall | 120 | 24 | NONE | bisection count |
| city/moat.py::inwall_drain_outfall | 138 | 2.5 | NONE | undrawn conduit width (unit dead) |
| core.py::__init__ | 63 | 1820, 1180 | CONVENTION | default sheet size |
| core.py::__init__ | 63 | 23 | NONE | default seed |
| farm_fixtures.py::farm_fixture | 179 | 0.2, 0.22, 0.4 | CONVENTION (claim: "fixture glyphs") | privy jar |
| farm_fixtures.py::farm_fixture | 184 | 0.3 | CONVENTION | ridge |
| farm_fixtures.py::farm_fixture | 185 | 3.2 | CONVENTION | log-end count |
| farm_fixtures.py::farm_fixture | 187 | 0.3, 0.4 | CONVENTION | log ends |
| farm_fixtures.py::farm_fixture | 191 | 1.1 | CONVENTION | manure-pit mouth |
| farm_fixtures.py::farm_fixture | 195 | 0.17 | CONVENTION | slats |
| farm_fixtures.py::farm_fixture | 196 | 0.22, 0.8, 0.9 | CONVENTION | slats |
| farm_fixtures.py::farm_fixture | 199 | 0.24 | CONVENTION | cauldron |
| farm_fixtures.py::farm_fixture | 202 | 0.25 | CONVENTION | coop niches |
| farm_fixtures.py::farm_fixture | 203 | 0.8 | CONVENTION | niche lines |
| farm_fixtures.py::farm_fixture | 211 | 0.05, 0.12, 0.28, 0.3, 0.36, 0.62 | CONVENTION | grave stones |
| farm_fixtures.py::farm_fixture | 212 | 0.18, 1.1 | CONVENTION | stone rects |
| farm_fixtures.py::farm_fixture | 215 | 0.35 | CONVENTION | shrine ridge |
| farm_fixtures.py::farm_fixture | 216 | 2.6 | CONVENTION | small torii offset |
| farm_fixtures.py::farm_fixture | 217 | 1.5 | CONVENTION | lintel overhang |
| farm_fixtures.py::farm_fixture | 222 | 0.2, 1.8 | CONVENTION | tie beam |
| farm_fixtures.py::farm_fixture | 223, 224 | 0.4, 0.6, 3.2 | CONVENTION | torii posts |
| farm_fixtures.py::persimmon | 251 | 107 | NONE | salt |
| farm_fixtures.py::persimmon | 253 | 107.5, 13, 7 | NONE | salt and hash offsets |
| farm_fixtures.py::persimmon | 253 | 45, 34 | CONVENTION (claim: "fruit dots") | dot angles |
| farm_fixtures.py::persimmon | 254 | 107.9, 11, 5 | NONE | salt and hash offsets |
| farm_fixtures.py::persimmon | 254 | 0.44, 0.24, 0.92, 0.16 | CONVENTION | dot radii |
| farm_fixtures.py::persimmon | 255 | 0.14 | CONVENTION | dot size |
| farm_fixtures.py::sty_parts | 289 | 0.8 | CONVENTION (claim: "sty glyph") | ridge inset |
| farm_fixtures.py::pond_fixture_fits | 307 | 6 | NOT-ABOUT-THE-WORLD | stand-in size for a record with no `w` (as T29 C) |
| finish.py::caption_record_box | 41, 44 | 0.55 | CONVENTION | glyph advance |
| finish.py::caption_record_box | 43 | 0.25, 0.8 | CONVENTION | text box |
| finish.py::caption_record_box | 46 | 0.275 | CONVENTION | box center |
| finish.py::caption_record_box | 47 | 1.05, 1.15 | CONVENTION | line pitch |
| finish.py::_record_label | 182 | 0.55 | CONVENTION | advance |
| finish.py::_record_label | 188 | 0.25, 0.8 | CONVENTION | box |
| finish.py::label | 217 | 12 | CONVENTION | font size |
| finish.py::label | 275 | 1.15 | CONVENTION | pitch |
| finish.py::label | 276 | 0.55 | CONVENTION | advance |
| finish.py::label | 278 | 0.275 | CONVENTION | center |
| finish.py::_caption_lines | 315 | 1.15 | CONVENTION | pitch |
| finish.py::_caption_lines | 319 | 0.55 | CONVENTION | advance |
| finish.py::_caption_lines | 321 | 1.05 | CONVENTION | box height |
| finish.py::_caption_lines | 322 | 0.275 | CONVENTION | center |
| finish.py::_text_width | 362 | 0.62 | CONVENTION | advance |
| finish.py::finish | 437 | 2600 | CONVENTION | PNG width |
| finish.py::_record_scatter_frame | 620, 625 | 1e9 | NONE | sentinel |
| finish.py::render_png | 692 | 2600 | CONVENTION | PNG width |
| hard_ground.py::_hard_ground | 47 | 1.5 | NONE | field-ditch `w` fallback (comb ditches carry `w`) |
| houses.py::house | 82 | 0.3 | CONVENTION (claim: "farmhouse glyph") | ridge line |
| houses.py::house | 84 | 0.4, 0.42 | CONVENTION | door mark |
| houses.py::house | 86 | 0.04, 0.16, 0.2 | CONVENTION | ruin mark |
| houses.py::_fits | 271 | 88 | CONVENTION | top sheet margin |
| houses.py::_fits | 274 | 55, 26 | CONVENTION | side and bottom sheet margins |
| houses.py::_hjit | 362 | 12.9898, 4.1414, 43758.5, 7.373 | NONE | hash constants |
| houses.py::_house_rot | 377 | 11 | NONE | salt |
| houses.py::_quad | 396 | 0.19 | NONE | salt step |
| houses.py::_try_place_bundle | 465 | 0.2 | NONE | depth spread 0.90 to 1.10; the branch is dead (0029 would cite it) |
| houses.py::_try_place_bundle | 468 | 53, 29 | NONE | hash multipliers |
| houses.py::_try_place_bundle | 469 | 30, 80 | NONE | 0.9 / 1.0 / 1.12 tier split; the branch is dead |
| houses.py::cluster_seeds | 537 | 0.55, 1.4 | NOT-ABOUT-THE-WORLD | elongated seed cloud; 0031 attests the levee string but gives no ratio, and the placer sets the drawn width |
| houses.py::cluster_seeds | 547 | 0.22 | GUESS 0031.drawing ("this project's extension... a GUESS") | crescent spread |
| houses.py::cluster_seeds | 548 | 0.95 | GUESS 0031.drawing | crescent depth |
| houses.py::cluster_seeds | 552 | 0.42, 0.62, 0.82 | GUESS 0031.drawing | split sub-clusters |
| houses.py::cluster_anchor | 556 | 0.6, 0.34 | NONE | lateral and depth fractions (no caller) |
| houses.py::cluster_anchor | 589 | 22 | NONE | clearance (no caller) |
| houses.py::cluster_anchor | 597, 599, 605 | 0.3 | NONE | lateral offsets (no caller) |
| houses.py::cluster_anchor | 603 | 0.45 | NONE | valley-mouth offset (no caller) |
| houses.py::plot_texture | 640, 641 | 0.66 | NONE | basin aspect at ftpx >= 2 (unreached) |
| houses.py::plot_texture | 643 | 1.9 | NONE | strip aspect (unreached) |
| houses.py::plot_texture | 648 | 34, 20, 40 | GUESS 0005.drawing ("this project's own figures, a GUESS") | small_irregular basin |
| houses.py::plot_texture | 649 | 48, 26, 36 | CITED 0005.drawing ("about 48 ft across its canal and 26 to 36 ft along it") | medium basin |
| houses.py::plot_texture | 650 | 70, 30, 44 | CITED 0005.drawing ("about 2.8 se (0.07 acre)"; note "about 70 x 37 ft") | large_block basin |
| houses.py::plot_texture | 651 | 32, 46, 66 | NONE | hamlet strip (never rolled or fixed) |
| structures/captions.py::_draw_placement | 216 | 0.08, 0.6 | CONVENTION | leader stroke |
| structures/captions.py::label_obstacles | 266 | 6 | NONE | tuple index |
| structures/captions.py::label_obstacles | 273 | 26 | NONE | road fallback |
| structures/captions.py::label_obstacles | 276 | 9 | NONE | stream fallback |
| structures/captions.py::_defense_lines | 288 | 4.5 | NONE | wall half-width (no wall) |
| structures/captions.py::_defense_lines | 291 | 22 | NONE | moat fallback |
| structures/captions.py::_draw_field_name_label | 310 | 15 | CONVENTION | font size |
| structures/fixtures/_helpers.py::outermost_join | 182 | 5 | NOT-ABOUT-THE-WORLD | sample step |
| structures/fixtures/_helpers.py::kosatsuba_anchor | 304 | 5 | NOT-ABOUT-THE-WORLD | sample step |
| structures/fixtures/_helpers.py::departure_routes | 324 | 7 | NOT-ABOUT-THE-WORLD | graph join tolerance |
| structures/fixtures/_helpers.py::__init__ | 437 | 32 | NONE | grid cell |
| structures/fixtures/siting.py::_route_seats | 336 | 26 | CONVENTION | top sheet margin |
| structures/fixtures/siting.py::_board_for | 467 | 0.6 | NOT-ABOUT-THE-WORLD (T29 P1; the claim records it on 0190.drawing as a kept departure) | traffic floor |
| structures/ground.py::_finish_road_label | 29 | 26 | NONE | road fallback |
| structures/ground.py::_finish_road_label | 30 | 12 | CONVENTION | font size |
| title.py::placard_height | 28 | 30 | CONVENTION | title font |
| title.py::placard_height | 34 | 1.2, 46 | CONVENTION | placard height |
| title.py::placard_size | 40 | 30 | CONVENTION | font |
| title.py::placard_size | 47 | 1.2 | CONVENTION | line height |
| title.py::title | 51 | 30 | CONVENTION | font |
| title.py::title | 89 | 8 | NOT-ABOUT-THE-WORLD | spot-search step |
| title.py::title | 102 | 16, 30 | CONVENTION | corner insets |
| title.py::title | 127 | 3.5, 7 | CONVENTION | inner frame |
| title.py::title | 131 | 12 | CONVENTION | scale-bar offset |
| title.py::title | 139 | 33, 5 | CONVENTION | scale-bar box |
| title.py::title | 146, 147 | 5 | CONVENTION | bar ticks |
| title.py::title | 152 | 12, 17 | CONVENTION | bar text |
| title.py::title | 154 | 31 | CONVENTION | ftpx text |
| title.py::_title_band | 168 | 32 | CONVENTION | band height |
| title.py::_title_band | 175 | 16 | CONVENTION | band inset |
| title.py::_title_band | 176, 177 | 30 | CONVENTION | side inset |
| title.py::_title_band | 187 | 8 | NOT-ABOUT-THE-WORLD | scan step |
| title.py::_title_band | 191 | 16, 30 | CONVENTION | fallback seat |
| title.py::_title_obstacles | 284 | 8 | NONE | well-radius fallback (wells carry `vr`) |
| title.py::_title_obstacles | 287 | 14, 8 | NONE | board-size fallback |
| title.py::_blank_label_spot | 319 | 22 | CONVENTION | sheet margin |
| title.py::_blank_label_spot | 319 | 24 | NOT-ABOUT-THE-WORLD | scan step |
| town_ways.py::ancestral_hall | 32 | 5 | NONE | inner eave (no caller; claim CONVENTION) |
| town_ways.py::ancestral_hall | 34 | 18, 9 | NONE | porch block (no caller; claim CONVENTION) |
| town_ways.py::water_mouth | 52 | 6 | NONE | hexagon (no caller; claim CONVENTION) |
| town_ways.py::water_mouth | 54 | 0.42 | NONE | inner ring (no caller) |
| town_ways.py::market | 75 | 22, 6 | NONE | stall pitch and offset (no caller; 0130 draws no stalls) |
| water_ways/_helpers.py::_pull_back | 88 | 8 | NOT-ABOUT-THE-WORLD | pull-back step |
| water_ways/clipping.py::_clip_to_pond | 35 | 24 | NONE | bisection count |
| water_ways/clipping.py::_clip_to_pond | 49 | 1.35 | NOT-ABOUT-THE-WORLD | "just outside the rim" tolerance |
| water_ways/clipping.py::_clip_to_moat | 69 | 22 | NONE | moat fallback |
| water_ways/clipping.py::_clip_to_river | 114 | 40 | NONE | river fallback |
| water_ways/clipping.py::_clip_to_stream | 171 | 1e9 | NONE | sentinel |
| water_ways/clipping.py::_clip_to_stream | 171 | 4.5 | NONE | initial value, overwritten |
| water_ways/clipping.py::_clip_to_stream | 174 | 9 | NONE | stream fallback |
| water_ways/clipping.py::field_channel | 251 | 0.2 | NONE | taper tolerance |
| water_ways/focal.py::mill | 43 | 8 | NONE | spokes (mill not reached; claim CONVENTION) |
| water_ways/lanes.py::_lane_ink_at | 140 | 2.5 | CONVENTION | worn-earth halo stroke |
| water_ways/lanes.py::trim_lane_stubs | 346 | 0.01 | NONE | divide-by-zero guard |
| water_ways/water.py::stream | 146 | 0.35 | CONVENTION (claim: "bed and sheen") | sheen stroke |

## Leads not followed

- **Two claims misquote their pages:**
  - `market`'s claim cites 0130.drawing for "a row of 14 x 12 ft stalls, one per 34 ft". The page says "No stalls are drawn."
  - `seat_deck`'s claim cites 0087.drawing for "14 steps of 12%" and "at most 7 deg". The page gives only "within about 24 ft and 8 degrees".
- **Code no generator reaches** that the session may want to retire: `cluster_anchor`, `water_field`, `fallow_field`, `organic_bbox`, `organic_poly`, `winding`, `channel`, `market`, `ancestral_hall`, `water_mouth`, `inwall_drain_outfall`, `plot_texture`'s ftpx >= 2 table, and `_try_place_bundle`'s non-lot branches.
- **large_block grain:** 70 x 37 ft is about 0.059 acre, a little under the page's "0.07 acre".
- **Unsearched:** how long a levee-string village runs against how wide it is. I ruled the seed cloud's 0.55/1.4 not about the world, so no search ran.