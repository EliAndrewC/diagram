I ruled all 75 numbers in the two files. None needed a web pass, and I put nothing on the sources-consulted ledger. The one world question with no claim behind it (`woods.py::_draw_stand`, the 0.42 jitter in where trees stand) is answered by passages the record already holds in 0080. Everything else is cited to a page, covered by a search recorded this month, or not a fact about the world. Nothing was edited.

## Sources (all already in the record)

**/diagram/research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.originals.html** and its `.html` page. The Qimin Yaoshu (6th century, China) is premodern evidence. The Edo planting study is a 1941 study describing Edo practice.
- On the oak wood: 「宜於山阜之曲，三遍熟耕，漫散橡子，即再勞之。……一定不移。」 — (translation) "It suits the bend of a hill. Plow it thoroughly three times, scatter the acorns broadcast, and harrow again ... once set, it is not moved."
- On planted timber: 「楸既無子，可於大樹四面掘坑取栽移之。亦方兩步一根，兩畝一行。一行百二十樹，五行合六百樹。」 — (translation) "Since the qiu bears no seed, dig pits round a big tree and move the suckers. Again one to every two paces square, a row to every two mu; 120 trees to a row, five rows make 600 trees."
- Edo planting, from the 1941 study: 「江戸時代に於ける植付密度は全般的に見て一坪一本植を普通とした」 — (translation) "Planting density in the Edo period was, broadly, one tree to the tsubo as the norm." Also: 「「三尺」・「六尺」・「九尺」或は「二間」…等を單位として一定の間隔に植付けられたこともあつた」 — (translation) "At times they were planted at a fixed interval, in units of 3 shaku, 6 shaku, 9 shaku or 2 ken ..."
- The drawing page: "each crown is drawn between 0.75 and 1.4 times that" and "across stands and clumps the map's recorded crowns are the seed, padded by two emergent radii".

**/diagram/research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html**: "Either conifer-led - darker, taller crowns set in rows along the windward side ... or a mixed broadleaf wood, an irregular wood of rounded crowns like the woods around it, the form of the Chinese village grove".

**Other record pages quoted in the table:**
- **0038 drawing:** "How much clear ground does a yard keep to its south? 39 ft".
- **0196 drawing:**
  - "A communal well sits on a paved apron about 4 ft wider than its curb all round"
  - "the apron's width is a GUESS"
  - "A well is drawn as a marker larger than life"
  - "round a premodern shaft about 1 m (~3 ft) across a 4 ft curb leaves a frame about 4 in wide a side"
- **0220 drawing:** "The arches stand 12 ft apart, the innermost 12 ft off the hall's face".
- **0068 (.html):** "This record's widths for a village brook and a town river, about 2 m (~7 ft) and 20 m (~66 ft), are GUESSES".
- **0081 drawing:** "a footpath is drawn 3 ft wide, the cluster's spine and its spur to the fields 5 ft, and the track out to the wider world 6 ft".
- **0039 drawing:** "keep it between 10 and 140 sq m (~108-1,507 sq ft)". It says nothing on how much gardens vary between households.
- **0029 drawing:**
  - "Our maps draw a farmhouse 46 by 28 ft" (quoted from pass-N3; I did not re-read it)
  - "How far is a house turned from its lane's own line? By up to about 12 degrees, most by much less, so a village reads as set out by eye rather than surveyed"

**Searches recorded this month:** T36 passes P3 and P6 put SEARCHED-SILENT claims in the code (bundle.py, woods.py). The passes themselves are in `/diagram/.clones/diagram-backlog/specs/417-all-seeds-pass/evidence/t29/` (pass-P3-village-rolling.md, pass-P6-shrines-wells.md).

## Reading

**ATTESTED ONLY FOR a broadcast-sown or coppice wood** (woods.py:85-86, the 0.42 jitter). The Qimin Yaoshu (6th century) sows its oak wood broadcast and never moves it, so that wood stands irregularly. Planted timber stood on a fixed interval: the Qimin Yaoshu's catalpa and qiu two paces square in counted rows, and Edo plantings one to the tsubo or at 3 or 6 shaku. 0072 drawing gives the same split: a conifer belt in rows, a broadleaf wood irregular. No source gives a figure for how irregular, so the 42% itself stays the project's own number. Jitter is right for a coppice or a mixed broadleaf wood. It would be wrong for a planted conifer stand, if one were drawn through `_draw_stand`.

Nothing in the engine fills `_pending_stands` (only `tests/settlement/test_shrines_wells.py:511` does), so `_draw_stand` and `_stand_fringe` look unreachable at present. That covers woods.py:85-88 and 177-184.

**Flags from the record:**
- Four rulings are CONTRADICTED by a page. Each is a departure the code already records: fit.py:905, held until T33; torii.py:107, marked DEVIATION; and the well's r = 8 in three places, held until T33.
- wells.py:92's water at 0.47 of the curb is below the page's 3 ft shaft in a 4 ft curb (about 0.75). The marker is not drawn to scale, so I ruled it CONVENTION.

## Rulings

Paths: `l7r/diagram/settlement/rolling/` for the first group, then `l7r/diagram/settlement/shrines_wells/`.

| file::unit | line | value | ruling | what the number does |
|---|---|---|---|---|
| access.py::__init__ | 92 | 128 | NONE | spatial-index cell |
| access.py::__init__ | 103 | 128 | NONE | spatial-index cell |
| bearing.py::wrap_square_deg | 72 | 45 | NONE | a square's quarter-turn fold (geometry) |
| bearing.py::__init__ | 109 | 64 | NONE | spatial-index cell |
| bearing.py::nearest | 115 | 64 | NOT-ABOUT-THE-WORLD | first search radius, doubled up to the reach |
| bearing.py::house_rot | 154 | 11, 14 | NONE | jitter salts (triangular spread) |
| bundle.py::_garden_beds | 53 | 8 | NONE | jitter salt |
| bundle.py::_garden_beds | 53 | 0.26 | SEARCHED-SILENT (bundle.py::_garden_beds "bed split share" claim, T36 pass P3) | about 1 in 4 households split the garden |
| bundle.py::_garden_beds | 58 | 9 | NONE | jitter salt |
| bundle.py::_garden_beds | 58 | 0.55 | SEARCHED-SILENT ("bed split forms" claim, T36 P3) | each flanking bed 0.55 of the garden's width |
| bundle.py::_garden_beds | 59 | 0.55 | SEARCHED-SILENT (same claim) | the same flanking-bed width |
| bundle.py::_bundle_layout | 267 | 0.25 | CITED 0039-kitchen-gardens-beside-farmhouses-yashikibatake.drawing.html (the 108-1,507 sq ft band; the up-to-1.25x spread is not on the page) | garden width jittered up to 1.25x |
| bundle.py::_bundle_layout | 268 | 0.25 | CITED 0039 drawing (same) | garden depth jittered up to 1.25x |
| bundle.py::_lay_fixtures | 374 | 5 | CITED 0029-farmhouses-minka.drawing.html via houses.py::_house_rot ("up to about 12 degrees, most by much less"; the page gives no 5, and the rule is for hamlet lanes) | +-5 degree rake where no hamlet bearing is set |
| farmsteads.py::_farm_rolls_bamboo | 65 | 95 | NONE | jitter salt (bamboo prevalence) |
| farmsteads.py::_east_trees | 156 | 1.5 | NONE | tolerance for matching the garden's own grove arms |
| fit.py::stream_segment_index | 38 | 9 | GUESS 0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.html (the page guesses ~7 ft; 9 is off it; the fallback never fires) | stream width when a record has no w |
| fit.py::_envelope_blocked | 271 | 6 | CONVENTION | envelope kept 6 px off the sheet edge |
| fit.py::_bundle_side_fits | 812 | 6 | CONVENTION | the same sheet-edge margin |
| fit.py::_yard_sun_conflict | 905 | 11 | CONTRADICTED 0038-sunlight-and-shade-on-the-farm.drawing.html ("39 ft"; a 22 ft strip, a recorded departure until T33) | center of the 22 px sun strip south of a yard |
| lot.py::house_aspect_bound | 106 | 28, 46 | CITED 0029-farmhouses-minka.drawing.html ("46 by 28 ft") | base house in the length/depth bound |
| lot.py::held_part_records | 234 | 8 | CONTRADICTED 0196-communal-wells-ido.drawing.html (apron "about 4 ft wider than its curb", itself a GUESS; recorded departure until T33) | the held well's clearance radius r |
| place.py::_bundle_refused | 85 | 6 | CONVENTION | sheet-edge margin |
| place.py::_slide | 110 | 1.5 | NONE | stop tolerance (arrived at the target) |
| place.py::_place_bundle_dispersed | 156 | 7, 15, 92 | NOT-ABOUT-THE-WORLD | spiral ring step 7 px, out to 91 px (one ring for an exact row seat) |
| place.py::_place_bundle_dispersed | 157 | 12 | NOT-ABOUT-THE-WORLD | 12 directions per ring |
| place.py::_place_bundle_dispersed | 158 | 6 | NOT-ABOUT-THE-WORLD | pi/6 step between those directions |
| place.py::_place_bundle_nucleated | 295 | 12 | NONE | jitter salt (which hand the garden goes on) |
| place.py::_house_box_refused | 314 | 6 | CONVENTION | sheet-edge margin |
| byres.py::courtyard_annex_span | 62 | 0.55 | NOT-ABOUT-THE-WORLD | a step just past the byre's half-depth in the span bound |
| byres.py::paddy_index | 143 | 128 | NONE | spatial-index cell |
| byres.py::_yard_shed_seat | 310 | 0.3 | NOT-ABOUT-THE-WORLD (the wall is from 0048 via the claim) | back-wall candidate seats at +-0.3 of the house width |
| byres.py::_yard_shed_seat | 311 | 0.25 | NOT-ABOUT-THE-WORLD | flank candidate seat 0.25 of the depth toward the back |
| byres.py::_yard_shed_seat | 312 | 131 | NONE | jitter salt (first wall turned) |
| byres.py::_yard_shed_seat | 312 | 5 | NONE | count of the first ring's seats (rotation modulus) |
| byres.py::_byre_clear_of_all_but | 372 | 0.05 | NONE | float tolerance (its own house) |
| byres.py::_draw_byre | 395 | 0.02, 0.4 | CONVENTION | stall-mouth band in the glyph |
| byres.py::_draw_byre | 396 | 0.3, 0.7 | CONVENTION | the two posts' places in the glyph |
| byres.py::_draw_byre | 398 | 0.02, 0.42 | CONVENTION | post stroke ends |
| byres.py::_draw_byre | 399 | 0.08 | CONVENTION | ridge line offset |
| byres.py::draft_byres | 563 | 0.75 | NOT-ABOUT-THE-WORLD | spread tier for the shared-shed choice (borrowing itself NOT ATTESTED, P6/0048) |
| byres.py::draft_byres | 564 | 0.25 | NOT-ABOUT-THE-WORLD | the next widening tiers (0.5, 0.25, 0) |
| byres.py::draft_byres | 589 | 30 | NOT-ABOUT-THE-WORLD | 30-degree step of the spiral search |
| shrines.py::shrine | 29 | 8 | CONVENTION | vermilion band in the hall glyph |
| torii.py::torii_even | 107 | 0.06, 0.8 | CONTRADICTED 0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html ("12 ft apart, the innermost 12 ft off the hall's face"; recorded DEVIATION) | arches spread from 6% to 86% of the ascent |
| wells.py::well | 92 | 0.47 | CONVENTION (marker larger than life, 0196 drawing; at true size the page's 3 ft shaft in a 4 ft curb is about 0.75) | dark water's radius within the curb glyph |
| wells.py::well_at | 106 | 8 | CONTRADICTED 0196 drawing (as lot.py:234) | default clearance radius r (2r+14 box) |
| wells.py::place_wells | 162 | 8 | CONTRADICTED 0196 drawing (as lot.py:234) | default clearance radius r |
| woods.py::trees_off_the_treads | 39 | 6 | CITED 0081-village-lanes.drawing.html ("the track out to the wider world 6 ft"; only a fallback when a lane has no w) | lane width when a record has no w |
| woods.py::_draw_stand | 85 | 0.42 | ATTESTED ONLY FOR a broadcast-sown or coppice wood (0080 originals, Qimin Yaoshu 漫散橡子; 0072 drawing "an irregular wood"); planted timber stood on a fixed interval (方兩步一樹; Edo 一坪一本植); the 42% is on no page | crown x jitter, 0.42 of the spacing |
| woods.py::_draw_stand | 86 | 0.42 | as line 85 | crown y jitter |
| woods.py::_draw_stand | 87 | 0.18 | SEARCHED-SILENT (woods.py::_draw_stand "emergent share" claim, T36 P6) | share of emergent crowns |
| woods.py::_draw_stand | 88 | 0.34 | SEARCHED-SILENT ("conifer share" claim, T36 P6) | share of conifers |
| woods.py::_crowns_near | 130 | 1.4 | CITED 0080 drawing ("padded by two emergent radii"; crowns "0.75 and 1.4 times") | reach padded by the largest crown |
| woods.py::_stand_fringe | 177 | 0.3 | SEARCHED-SILENT ("fringe crown size and conifer share" claim, T36 P6) | fringe conifer share |
| woods.py::_stand_fringe | 183 | 31 | NONE | jitter salt (thicket mask) |
| woods.py::_stand_fringe | 183 | 0.12, 0.42, 5 | SEARCHED-SILENT ("thickets, not a sprinkle" claim, T36 P6) | thicket mask about 5 crowns across: 58% seeded, the rest at 0.12 |
| woods.py::_stand_fringe | 184 | 1.4 | SEARCHED-SILENT ("fringe band and thinning" claim, T36 P6) | thinning exponent away from the wood's edge |

## Leads not followed
- `_pending_stands` is filled only by a test, so `_draw_stand` and `_stand_fringe` may be dead code. Worth confirming before T33/T34 spend effort on their numbers.
- If a planted conifer belt ever goes through `_draw_stand`, the Edo fixed-interval planting would argue against random jitter there. 0072's conifer rows already draw that form apart.
- `wells.py::well` water at 0.47 against the page's about 0.75 (3 ft shaft, 4 ft curb): a glyph choice, but the page gives a proportion if the GM wants one.