I ruled all 104 numbers from the record and the code. None needed a search pass: no number that speaks about the world was left unresearched, so no archive or web search ran and nothing was added to the sources ledger. The research pages read were 0042, 0044, 0046 and 0047 (`.drawing.html`, plus 0044's findings page), in `/diagram/research/questions/`. There is no `t36` evidence directory under `specs/417-all-seeds-pass/evidence/`, so "SEARCHED-SILENT (T36 pass P1)" below refers to what the unit's own `Research:` claim says, dated 2026-10-25.

**What the record says**
- `0047-farm-privies-and-their-night-soil-benjo.drawing.html` describes the maps' own rule, not a period source: "the maps seat every farmhouse facing south, turned a little, so 112.5 to 202.5 degrees is the house's own southeast to south. That sector is the sunny side the maps seat a privy in". The page gives the two ends of the sector. It does not give the code's 7.5-degree step.
- `0042-manure-heaps-and-compost-kyuhi.drawing.html`: "The heap's distance from its privy varies by a few feet from one farm to the next. ... The place is a GUESS: no page we read says where in the yard the heap stood." It says "a few feet" but gives no number; the 9 ft spread is ours.
- `0044-baths-on-the-farm-furo.drawing.html`: "A bath room stands by the main door, at the far end of the stable wing, or joined to the floored rooms." It names the walls, not where along the wall the room stands.
- `0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html`: "in front of the house or behind it ... Its crown's edge stands within about 30 ft of the house". The page never says "front corners", although `_persimmon`'s claim quotes it as saying so (a mis-citation the session may want to correct).

**Fallbacks no generator reaches** (so ruled NONE):
- `road`, `moat` and `ring_road` start as None in `core.py` and are written only by tests. No production code sets `road_width`, `moat_width` or `ring_road_width`.
- Every stream (`water.py:133`), channel (`water.py:211`, `sink.py:130`, `moat.py:138`, comb), lane (`lanes.py:76`) and village-grove `r` (`grove_fill.py:539`) record carries its own width or radius.
- The windbreak's one caller always passes `wind_unit(plan.windward)` (`stages.py:367`).
- One thing to tidy, though it decides nothing today: the fallbacks disagree with each other. A stream defaults to 9 in `grove_fill`/`wood_share` and 6 in `keepouts`, while the generator draws 7 ft (0068). A channel defaults to 2.5 in some files and 6 in `keepouts`.

| file::unit | line | value | ruling | what the number does |
|---|---|---|---|---|
| belt_law::__init__ | 140 | 1e9, 2e9 | NONE | sentinel frame when no view is recorded |
| belt_law::reading_of | 338 | 14 | NONE | belt clump radius fallback; `r` is always recorded |
| belt_law::_offers | 354 | 8 | NOT-ABOUT-THE-WORLD | step between offered seats along the wind |
| belt_law::_offers | 365 | 0.25, 0.75 | NOT-ABOUT-THE-WORLD | where across a stretch seats are offered |
| belt_law::_close | 399 | 6 | NOT-ABOUT-THE-WORLD | offers kept 6 in from a gap's two ends |
| fixture_seats::fixture_ft | 205 | 104.3 | NONE | roll salt for the bath's length |
| fixture_seats::against_a_wall | 256 | 1.5 | NONE | slack in the "stands against a wall" test |
| fixture_seats::lay_fixtures | 415 | 0.25 | NONE | salt offset for the bath-wall roll |
| fixture_seats::bath_room_seats | 549 | 0.25 | GUESS 0044-baths-on-the-farm-furo.html | candidate seats at the stable-end wall's quarters; the page gives only the wall |
| fixture_seats::bath_room_seats | 550 | 0.25 | GUESS 0044-baths-on-the-farm-furo.html | the same, on the floored-rooms end wall |
| fixture_seats::_sun_sector | 648 | 64 | NONE | cache size |
| fixture_seats::_sun_sector | 658 | 1125, 2026 | CITED 0047-…benjo.drawing.html | the 112.5 to 202.5 degree sunny sector ("112.5 to 202.5 degrees is the house's own southeast to south") |
| fixture_seats::_sun_sector | 658 | 75 | NOT-ABOUT-THE-WORLD | 7.5-degree step of the bearing search |
| fixture_seats::_seats | 696 | 0.4 | SEARCHED-SILENT (T36 pass P1, the unit's claim) | sideways place of the front privy (0.40 of the house's half-width) |
| fixture_seats::_seats | 722 | 102.4 | NONE | salt |
| fixture_seats::_seats | 722 | 9 | GUESS 0042-…kyuhi.drawing.html | heap's distance from the privy varies over a 9 ft spread ("varies by a few feet") |
| fixture_seats::_seats | 737 | 105.9 | NONE | salt |
| fixture_seats::_seats | 739 | 105.5 | NONE | salt |
| fixture_seats::_persimmon | 800 | 0.75 | NOT-ABOUT-THE-WORLD | diagonal candidate seats on the ring, then stepped out (0046 gives front or behind only) |
| fixture_seats::_persimmon | 801 | 0.75 | NOT-ABOUT-THE-WORLD | the same, behind the house |
| gardens::_draw_garden | 35 | 8 | CONVENTION | plant dots kept 4 in from the bed glyph's ends |
| gardens::_attach_garden | 60 | 5, 71 | NONE | quad jitter salts |
| grove_blocks::regions | 145 | 40 | NONE | raster window pad |
| grove_blocks::__init__ | 215 | 16 | NONE | spatial-index cell floor |
| grove_fill::grove_blocks | 91 | 14, 19 | CONVENTION | torii glyph half-extent ("glyph spans x +/-19") |
| grove_fill::grove_blocks | 135 | 0.45 | NONE | floor under `crown_reach` (the drawn crown's reach); the tread rule itself is GUESS in `_corridor_buffers` |
| grove_fill::grove_blocks | 166 | 9 | NONE | stream width fallback, never reached |
| grove_fill::grove_blocks | 167 | 2.5 | NONE | channel width fallback, never reached |
| grove_fill::grove_blocks | 169 | 22 | NONE | moat width fallback; no production moat |
| grove_fill::reseat_clump | 332 | 0.6, 1.4, 1.8 | NOT-ABOUT-THE-WORLD | re-seat search radii ladder |
| grove_fill::reseat_clump | 333 | 45 | NOT-ABOUT-THE-WORLD | re-seat search bearing step |
| grove_fill::reseat_clump | 337 | 0.9 | CONVENTION | "any ink on the page" frame test |
| grove_fill::close_belt_gaps | 380 | 6 | NOT-ABOUT-THE-WORLD | gap-fill round cap |
| grove_fill::close_belt_gaps | 426 | 0.22, 0.34, 0.66, 0.78 | NOT-ABOUT-THE-WORLD | fractions along a gap tried |
| grove_fill::close_belt_gaps | 429 | 33 | NOT-ABOUT-THE-WORLD | depth samples across the band |
| grove_fill::close_belt_gaps | 430 | 32 | NOT-ABOUT-THE-WORLD | the same, as intervals |
| grove_fill::close_belt_gaps | 435 | 0.9 | CONVENTION | "any ink on the page" frame test |
| groves::over_a_conifer | 269 | 0.2 | NONE | ink rounding slack |
| groves::bamboo_mark | 297 | 5 | CONVENTION | culm mark height (glyph; 0075 drawing: marks a convention) |
| groves::bamboo_mark | 298 | 1.6 | CONVENTION | mark lean |
| groves::bamboo_mark | 299 | 1.2 | CONVENTION | culm offset in the glyph |
| groves::bamboo_mark | 301 | 0.6, 0.8, 0.9, 1.2 | CONVENTION | second culm's lean and length, stroke width |
| groves::bamboo_mark | 302 | 0.4, 0.8, 1.2, 1.6, 2.2, 2.4, 2.6 | CONVENTION | leaf-fork strokes and width |
| groves::_belt_ranks | 380 | 64 | NONE | index cell |
| groves::_belt_ranks | 397 | 95 | NONE | salt |
| groves::_belt_ranks | 398 | 96 | NONE | salt |
| groves::_belt_ranks | 399 | 97 | NONE | salt |
| groves::_draw_grove | 494 | 5 | NONE | seed multiplier |
| groves::_draw_grove | 537 | 0.6 | NOT-ABOUT-THE-WORLD | scatter of decorative crowns about even steps along a band; no source could speak to it |
| groves::_draw_grove | 565 | 9 | NONE | prefilter pad, floor under the true crown reach |
| groves::_draw_grove | 634 | 0.2 | NONE | ink rounding slack |
| groves::_draw_grove | 706 | 93, 94 | NONE | salts |
| keepouts::_corridor_buffers | 42 | 6 | NONE | lane width fallback; lanes always record `w` |
| keepouts::_corridor_buffers | 48 | 20 | NONE | ring-road width fallback; no production ring road |
| keepouts::_corridor_buffers | 50 | 30 | NONE | road width fallback; no production road |
| keepouts::_watercourse_segs | 66 | 6 | NONE | stream width fallback, never reached |
| keepouts::_watercourse_segs | 67 | 6 | NONE | channel width fallback, never reached |
| keepouts::_watercourse_segs | 72 | 0.2 | NONE | uniform-vs-taper tolerance |
| keepouts::_urban_keepouts | 414 | 40 | NONE | prefilter pad for wells |
| stands::trunk_on_tread | 53 | 6 | NONE | lane width fallback, never reached |
| stands::reserved_seat_keepouts | 143 | 0.9 | NONE | mirrors the copse's own displacement test (the 0.90 is SEARCHED-SILENT at wood_share:197) |
| stands::bamboo_stand | 174 | 0.6 | CONVENTION | jitter of the glyph grid (0075 drawing) |
| stands::bamboo_stand | 174 | 91, 92 | NONE | salts |
| stands::bamboo_stand | 177 | 0.86 | CONVENTION | staggered row step of the glyph grid |
| stands::village_grove | 348 | 21 | NONE | salt |
| stands::village_grove | 407 | 0.25, 0.75 | NOT-ABOUT-THE-WORLD | refill grid offsets |
| stands::village_grove | 414 | 23 | NONE | salt |
| stands::village_grove | 415 | 24 | NONE | salt |
| stands::village_grove | 486 | 0.7071 | NONE | northwest wind fallback; the caller always passes the wind |
| stocking::grove_stocked | 15 | 100000 | NONE | the unit of the stocking floor (per 100,000 sq px); the 1.5 floor is the recorded GUESS |
| stocking::crown_cover | 103 | 12 | NONE | buffer arc segments |
| wood_share::ground_blocks | 164 | 9 | NONE | stream width fallback, never reached |
| wood_share::ground_blocks | 165 | 2.5 | NONE | channel width fallback, never reached |
| wood_share::ground_blocks | 167 | 22 | NONE | moat width fallback; no production moat |
| wood_share::open_water_discs | 197 | 0.9 | SEARCHED-SILENT (T36 pass P1, the unit's claim) | copse keeps 0.90 of a clump off ponds and sacred ground |
| wood_share::open_water_discs | 199 | 14, 19 | CONVENTION | torii glyph half-extent |
| wood_share::__init__ | 272 | 0.45 | NONE | floor under `crown_reach`, as at grove_fill:135 |
| wood_share::__init__ | 276 | 64 | NONE | index cell |
| wood_share::__init__ | 277 | 64 | NONE | index cell |
| wood_share::__init__ | 435 | 64 | NONE | index cell |
| wood_share::seat_barred | 308 | 6 | CONVENTION | seats kept 6 px off the sheet's edge |
| yards::_mat_hash | 51 | 12.9898, 37.719, 43758.5, 78.233 | NONE | hash constants |
| yards::floor_grid | 218 | 0.02 | NONE | buffer arc error margin |
| yards::_draw_threshing_yard | 500 | 53 | NONE | salt |
| yards::_draw_threshing_yard | 501 | 0.25 | CONVENTION | mat glyphs kept a quarter foot off the rack (mats are a convention) |
| yards::_draw_threshing_yard | 503 | 61, 997 | NONE | salt and multiplier |
| yards::_draw_threshing_yard | 514 | 0.55 | CONVENTION | rack post dot radius |
| yards::_yard_area_ft2 | 588 | 23, 29, 31, 37, 43, 47 | NONE | salts |
| yards::_attach_yard | 641 | 0.1 | CONVENTION | outline jitter, recorded "swept outline - CONVENTION: jitter 0.10" |
| yards::_attach_yard | 641 | 41 | NONE | salt |

**Leads not followed**
- Where along an end wall a farm bath room stood (bath_room_seats 549/550): the floor plans behind 0044 might show it, but nothing points that way yet.