I ruled every number in the file. None was left UNRESEARCHED as a question about the world, so I ran no web pass. The one world number that looked open (the well pocket's margin in `farm_water.py`) is already covered by a GUESS claim in `bundle.py`. Nothing was edited and nothing was added to the ledger.

## Sources

**research/questions/0029-farmhouses-minka.drawing.html** (preserved houses as a basis for drawing; a modern description of premodern houses). These words back the 46 x 28 ft house and its 1.35 / 1.10 ceilings:
- "Our maps draw a farmhouse 46 by 28 ft, the size of the better-off farmers' houses preserved today."
- "A house's length varies by roughly 0.85 to 1.35 of the base and its depth by only 0.90 to 1.10, so the proportions stay inside about 1.3 to 2.5 long to deep"

**research/questions/0033-row-villages-resson.drawing.html** (Edo-period planned colonies on the Musashino plateau: Santome, Nobidome 1661). These words back the 240 ft frame width:
- "A frame is about 220 to 260 ft wide, and the row never spaces its farms wider than Santome's 40-ken lots, about 240 ft, the widest frontage the record gives (accurate)."

**research/questions/0196-communal-wells-ido.drawing.html** (Karihama, Ehime). These words back the count of 5 in the cluster form:
- "in the cluster form it stands in the open ground among five to ten houses, off every lane - the five to ten houses that each dug well served at Karihama"
- "A cluster well is seated among five houses, off every lane; how far round a seat the five may stand is this project's choice, widened before the count of five gives way, and only a hamlet with fewer than five househ[olds]…" (the page text is cut off at this point in my extract)

**research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html**. The (1.9, 4.2) default is a GUESS: the page names the crescent but gives no ratio.
- "The lump and the line along a levee or a road are the attested forms; the crescent and the split village are this project's extension of them, a GUESS."
- The 1.9–4.2 band itself comes from measuring the project's hand-drawn maps (the `CLUSTER_DRAWN_ASPECT` docstring in `l7r/diagram/hamletgen/consts.py`), not from a source.

**Searched-silent claims recorded in the code, not on a page.** These come from this month's T29/T36 search passes, so I did not repeat them:
- `bamboo.py::_strip_blocked`: "what a strip or fixture keeps off - GUESS: searched, the record silent (feature 417 T29 pass C, 2026-10-25); the pads, … 6 ft off wells and sheds and paddy or marsh, 3 ft off dry plots, off water and crowns". This covers the 6 ft ring pad and the 0.6 ft crown margin.
- `settlement/rolling/bundle.py:211`: "dispersed well pocket - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P3, 2026-10-25); the wellhead plus a 3 ft margin, `2 * _well_vr() + px(6.0)`". `farm_water.py:156` repeats this expression.
- `stages.py::_seat_rank_rounds`: "rank jitter … GUESS: no source gives the figures, (feature 417 T29 pass E2 …) seats nudged up to a tenth of a pitch along the band"; "the rescue band widened 22% and 16% a round"; "four rank rounds then three rescue rounds".

**Evidence for the well-pocket margin: none.** In the archive, "井台" (well platform) and "井栏" (well curb) found the Wenhui interview with Ruan Yisan (32270-ruan-yisan-wenhui-wells.html). It says "井台边通常会分别设置清水沟和污水沟" ("separate clean-water and waste-water ditches are usually set beside the well platform", translation). It gives no distance, so it does not bear on the 3 ft margin. 0196 has "a paved apron about 4 ft wider than its curb all round", but that is measured from the curb, while the code's 3 ft is measured past the well-house roof square. They are different measures, so the page neither gives nor contradicts the 3 ft.

## Reading

**SILENT** on the only world question the file raises: how much clear ground a channel keeps round a farm's well-house. The record (bundle.py:211, T36 pass P3), the archived Wenhui text and 0196 all give no figure for a margin round a well-house. Every other world number either quotes 0029, 0033 or 0196 directly, or already carries a code claim from a search run this month.

## Rulings

| file::unit | line | value | ruling | what the number does |
|---|---|---|---|---|
| bamboo.py::household_bamboo | 125 | 1e9 | NONE | sentinel box: the whole map |
| bamboo.py::household_bamboo | 136 | 95 | NONE | jitter salt (prevalence roll) |
| bamboo.py::household_bamboo | 147 | 96 | NONE | jitter salt (strip candidates) |
| bamboo.py::household_bamboo_wanted | 379 | 95 | NONE | same salt, the count |
| bamboo.py::__init__ (Footing) | 433 | 6 | SEARCHED-SILENT (bamboo.py::_strip_blocked claim, T29 pass C; no page) | 6 ft pad off paddy/marsh rings |
| bamboo.py::__init__ (StripNear) | 491 | 0.6 | SEARCHED-SILENT (same T29 pass C claim, "off … crowns") | crown box padded 0.6 ft |
| bamboo.py::count | 520 | 6 | NOT-ABOUT-THE-WORLD | prefilter reach, the widest pad |
| bamboo.py::_strip_blocked | 551 | 30 | CONVENTION | strip kept 30 px off the sheet edge |
| bamboo.py::_strip_blocked | 602 | 0.6 | SEARCHED-SILENT (T29 pass C claim) | strip 0.6 ft clear of a crown |
| boundary.py::__init__ | 189 | 128 | NONE | spatial-index cell |
| boundary.py::_vertex_grid | 239 | 32 | NONE | spatial-index cell |
| capacity.py::free_seats | 84 | 6 | CONVENTION | seat grid inset 6 px from the sheet edge |
| farm_water.py::_obstacles | 156 | 6 | SEARCHED-SILENT (settlement/rolling/bundle.py:211, T36 pass P3; this pass also silent) | well pocket = well-house + 3 ft a side, walled from channels |
| fixtures.py::_draw_laid | 365 | 102.7 | NONE | jitter salt (manure pit share) |
| growth.py::household_reach | 185 | 28, 46 | CITED 0029-farmhouses-minka.drawing.html | base house 46 x 28 ft |
| growth.py::next_house | 210 | 28, 46 | CITED 0029-farmhouses-minka.drawing.html | base house 46 x 28 ft |
| growth.py::grow_jitter | 306 | 8 | NOT-ABOUT-THE-WORLD | reference direction count for jitter scaling |
| growth.py::grow_level | 318 | 16 | NOT-ABOUT-THE-WORLD | search directions past the table (already GUESS T29 B) |
| household_ways.py::seated_parts | 81 | 8 | NONE | octagon standing in for a circle |
| persimmon_reseat.py::give_way | 109 | 0.2 | NONE | float tolerance, crown under the disc |
| persimmon_reseat.py::give_way | 130 | 0.2 | NONE | float tolerance, matching an SVG circle |
| region.py::smallest_sides | 217 | 28, 46 | CITED 0029-farmhouses-minka.drawing.html | base house times the smallest factors |
| retirement.py::retirement_glyph | 130 | 0.28 | CONVENTION | ridge-line length in the glyph |
| retirement.py::retirement_glyph | 131 | 1.6 | CONVENTION | door mark offset in the glyph |
| row_rules.py::continuous | 50 | 1.5 | NOT-ABOUT-THE-WORLD | join tolerance between street pieces |
| row_rules.py::row_rules | 97 | 240 | CITED 0033-row-villages-resson.drawing.html | fallback frame width, how far a farm may stand off its street |
| row_rules.py::row_rules | 122 | 240 | CITED 0033-row-villages-resson.drawing.html | fallback frame width ("behind another" test) |
| row_rules.py::row_rules | 124 | 240 | CITED 0033-row-villages-resson.drawing.html | fallback frame depth (half-frame test) |
| rows.py::_normal_away | 100, 101 | 5 | NOT-ABOUT-THE-WORLD | probe step to orient the normal |
| rows.py::street_line | 121, 127, 146 | 8 | NOT-ABOUT-THE-WORLD | street sampled every 8 ft |
| rows.py::holding_clear | 264 | 0.25 | CONVENTION | holding drawn only if a quarter of it is on the sheet |
| rows.py::draw_holdings | 365 | 1e5 | NONE | sentinel band length, clipped |
| rows.py::best_row_line | 505 | 16 | NOT-ABOUT-THE-WORLD | candidate lines sampled |
| rows.py::seat_rows | 583 | 30 | CONVENTION | holdings clipped 30 px inside the sheet |
| seat_geometry.py::water_push | 30 | 8 | NOT-ABOUT-THE-WORLD | water segment sampled every 8 ft |
| seats.py::front_row | 32 | 46 | NONE (dead default: the one caller, stages.py:719, passes `standoff=None`; the live standoff is CITED 0029) | unused default standoff |
| seats.py::_front_row_from_chains | 120, 121, 122 | 64 | NOT-ABOUT-THE-WORLD | cap on front-row candidates |
| seats.py::lane_frontage | 138 | 86 | NONE (no caller in the engine, only tests) | step between frontage seats |
| stages.py::stage_homesteads | 263 | 45 | NONE | meta count threshold for a quarter turn |
| stages.py::_seat_households_as | 491 | 1.1, 1.35, 28, 46 | CITED 0029-farmhouses-minka.drawing.html | largest house rolled |
| stages.py::_seat_households_as | 496 | 2654435761, 0xFFFFFFFF | NONE | seed hash multiplier and mask |
| stages.py::_seat_households_as | 563 | 1.5 | NOT-ABOUT-THE-WORLD | length of the way-out test line |
| stages.py::_seat_households_as | 633 | 1.9, 4.2 | GUESS 0031-clustered-and-scattered-villages-shuson-sanson.drawing.html | fallback crescent aspect band |
| stages.py::_seat_rank_rounds | 849 | 7 | NOT-ABOUT-THE-WORLD (code claim: 4 rank + 3 rescue rounds, GUESS T29 E) | number of seating rounds |
| stages.py::_seat_rank_rounds | 853 | 0.16, 0.22 | NOT-ABOUT-THE-WORLD (code claim: GUESS T29 E2) | rescue band widening per round |
| stages.py::_seat_rank_rounds | 905 | 6, 30 | NOT-ABOUT-THE-WORLD | rescue cloud candidate count |
| stages.py::_seat_rank_rounds | 916 | 0.2 | SEARCHED-SILENT (code claim, T29 pass E2: "a tenth of a pitch") | seat nudged up to 0.1 pitch either way |
| stages.py::_seat_rank_rounds | 916 | 13 | NONE | jitter salt |
| stages.py::_seat_rank_rounds | 949 | 14 | NONE | jitter salt (rank depth) |
| wells.py::mark_form | 98 | 0.06 | NONE | float tolerance, matching the well record |
| wells.py::own_well_clear | 177 | 26, 55, 88 | CONVENTION | wellhead kept off the sheet edges |
| wells.py::shared_row_wells | 243 | 240 | CITED 0033-row-villages-resson.drawing.html | fallback frame width |
| wells.py::place_wells | 379 | 11 | NOT-ABOUT-THE-WORLD | lattice step, lane-side seats |
| wells.py::seat_wells | 395 | 22 | NOT-ABOUT-THE-WORLD | default lattice step |
| wells.py::seat_wells | 419, 457 | 0.01 | NONE | divide-by-zero guard |
| wells.py::seat_wells | 498 | 120 | NOT-ABOUT-THE-WORLD | sweep box pad |
| wells.py::seat_cluster | 676 | 0.01 | NONE | divide-by-zero guard |
| wells.py::seat_cluster | 679 | 5 | CITED 0196-communal-wells-ido.drawing.html | a cluster well among five houses |
| wells.py::seat_cluster | 680 | 5 | CITED 0196-communal-wells-ido.drawing.html | fewer than five households: three, then two |
| wells.py::reach_wells | 774 | 11 | NOT-ABOUT-THE-WORLD | lattice step |
| wells.py::lane_and_fallback_wells | 824 | 11 | NOT-ABOUT-THE-WORLD | lattice step |

## Leads not followed

- The two dead numbers (`seats.py` standoff 46 and `lane_frontage` step 86) can be deleted rather than researched.
- The 1.9–4.2 crescent band rests on the frozen hand-drawn maps, not a source. If the GM wants a sourced ratio, it would have to come from a survey of village plans, which no page holds.