# Audit: `settlements/homesteads.md` (138 lines, 65.9 KB) against `research/homesteads.html`

Independent Opus reader, 2026-09-12. Classes: A restated on the page; B rule-only (engine site given where
encoded); C hand-procedure; D decision record the page lacks; E unscripted tier; F stale.

## Unit table

| # | unit (line) | class | justification | engine (B) / anchor (A) |
|---|---|---|---|---|
| 1 | Title + "Part of the Mode B settlement docs" (1-3) | C | navigation | - |
| 2 | "Load this file when" (5) | C | addressed to a session | - |
| 3 | "Research:" pointer (7) | C | pointer | - |
| 4a | The headman is a FARMSTEAD - routing + `headman_has_kura` (11) | D | GM 2026-07-21 ruling (shoya needs fireproof storage); page has no headman entry | `houses.py:715-721` encodes + carries the why |
| 4b | retrofit knock-on, re-seed `SEED+1..+4` (11) | C | hand-retrofit procedure | - |
| 5 | Village variation knobs (feature 005) intro - Kikuta/Hoshigaoka twinning (12-14) | E | village tier | - |
| 6 | The roll engine `_knobs.py` (16) | B | resolution order, SHA-256 sub-seed | `_knobs.py:76` `register_knob`, `:348` |
| 7 | The Family-A catalog - 7 knobs with typing rules (18-25) | B | 背山面水 / 条里 / 草市 grounding NOT on the page | `_knobs.py:263-283` |
| 8a | Generator surface for the shipped knobs (26) | B | API surface | `rolling/seeds.py:17,37`; `hamletgen/homesteads/stages.py:265` |
| 8b | Sizing caveat for dispersed - twice the margin room per farm (26) | B | prose only | NOT FOUND |
| 8c | crescent pond labels itself "geomantic pond" + what it is (26) | D | GM 2026-07-21: the one exception to don't-label-the-obvious | `fields/features.py:290` (partial) |
| 9 | Knob resolvers + roll-from-seed entrypoint (28-31) | B | | `houses.py:820,876,926,959` |
| 10 | `s.roll_village(...)`, ~1/3 of seeds pass (33) | E/B | village roll; stale measurement | `rolling/roll.py:75,176` |
| 11 | Completed focal catalog (34) | B | glyph methods | `water_ways/focal.py`; `town_ways.py` |
| 12 | The twin-detector (36) | F + D | `check_village/` empty; `twin_axes` etc 0 hits; the 4-of-8 calibration and the GM's read are D | GONE |
| 13 | Houses - pitched-roof glyph, south-facing (38-41) | B | drawing convention | `houses.py:43-75` |
| 14 | A fireproof kura on ~30% of plain farms (42) | B + D | D: the 2026-08-17 position-seeded correction (re-pack re-rolls it; 0.2993 over 200k; pool 343/1208 = 28.4%) and the declined household-index key | `houses.py:721` `_hjit(x,y,3.0) < 0.30` |
| 15 | Houses never overlap (43) | B | | overlap matrix |
| 16 | Draft animals live in the farmhouse (45) | A (+E) | page carries magariya/doma and "no European barn" | `#may-a-byre-stand-beside-a-wellhead` |
| 17 | DRAFT-ANIMAL BYRES fraction~0.2, ~16 m² (46) | B | share and 31x21 ft footprint not on page | `byres.py:164`; `homesteads/stages.py:381` calls 0.22/gap 60 |
| 18 | TWO FORMS ROLLED PER SETTLEMENT (`byre_form`) (47) | B + D | D: "Do not restore the old prose claim that a byre always abuts its farmhouse" | `_knobs.py:298`; `byres.py:181`; `taxonomy.py:292-296`; seed test `tests/gate/test_generator_contracts.py:94` |
| 19 | Field-adjacency TUNABLE by form - 165 px (48) | B | | `hamletgen/cluster.py:193`, `homesteads/seats.py:24`, `consts.py:672` |
| 20 | Field OUTLINE must BE the planting (49) | F + D | check 0 hits; D: Akagahara 181 px phantom tail, Hoshigaoka/Kikuta 210 px tails kept on purpose, the general lesson | GONE |
| 21 | HARVEST-PROCESSING layer (50) | A + B + F | A: per-farmstead/universal/sunny side; B: farmstead drawing DEFERRED; F: "smaller than its farmhouse" retired AND contradicted | `rolling/farmsteads.py:17`; `#how-big-was-the-work-yard...` |
| 22 | Nucleated cluster is a COMPACT FABRIC + calibration + honest limit (51-54) | E + D | village scale >=12 houses; D: 0.20 / 0.28-0.31 / 0.40 calibration, 0.25 floor, 0.31 ceiling accepted | comments only `houses.py:807`, `rolling/roll.py:257` |
| 23 | Threshing yards PER-FARMSTEAD and UNIVERSAL (56-59) | A | | `#how-big-was-the-work-yard-and-how-did-the-sizes-spread` |
| 24 | Size and how sizes SPREAD - 18 tsubo, sigma 0.40, floor 8 (60-75) | A | | same; `homestead_parts/yards.py:94-120` |
| 25 | Shape near-square, SIZE rolled (76-82) | B | | `yards.py` `YARD_ASPECT = 1.45` |
| 26 | A SIDE feature - east, then SE/SW, windward LAST (83) | B | the preference ladder; no page entry | `rolling/bundle.py`, `rolling/fit.py` |
| 27 | Clear EASTERN sky `gardens_unshaded_from_east` (84) | B + D | D: GM 2026-07 "move it a bit south"; two implementation subtleties | `rolling/farmsteads.py:52,105`; `stands.py:183` |
| 28 | Three appurtenances, three sides (85) | B | check name stale, rule live | `homestead_parts/gardens.py:48-49` |
| 29 | Off the water too (86) | B + D | found on Ueda; fix-in-the-solver | `rolling/fit.py:138` |
| 30 | Why a side and not the front (87) | A | | `#the-gardens-sun-and-how-far-the-windbreak-shades` |
| 31 | Relative size (88) | B | | bundle caps |
| 32 | Size held to a HISTORICAL AREA band 10-140 m², 1 tsubo = 3.31 m², 1 se = 30 tsubo (89) | B + D | page has NO garden-size entry; D: the 2026-09-07 wording correction | `rolling/bundle.py:67,101-102` |
| 33 | Shape - irregular hand-worked quad (90) | B | | `gardens.py:99` |
| 34 | FRAGMENTED into two beds, three arrangements (91) | B | | `rolling/bundle.py:20-49,130` |
| 35 | Storehouses/sheds a MINORITY (~30%) (92-93) | B (part A) | kura 0.24 overlaps page; 30% choice md-only | `houses.py:721` |
| 36 | NUCLEATED vs DISPERSED - Knapp, North vs South China, ~30-60 households, 200-500 villages/100 km² (94) | B (unmigrated research) | "Knapp" nowhere in research/; no Sources line | `_knobs.py:219` `settlement_form`; numbers NOT FOUND |
| 37 | The consequence for groves (95) | B | | `rolling/farmsteads.py:221` |
| 38 | DISPERSED unchanged + windward belt deferred TODO (96) | E + F | TODO stale (belt built) | - |
| 39 | Headman = LARGER plain farmhouse + `"big"` glyph wing defect (97) | B + D | D: the unreserved storeroom wing trap | `rolling/place.py:16-19` |
| 40 | Cluster HUGS the paddy `_slide_nuc(keep_field=True)` (98) | B | | `settlement/houses.py` |
| 41 | Lanes lace the cluster, spur bridges it (99) | B + C | C: "For a HAND-AUTHORED gen the older order still applies" | `hamletgen/ways/` |
| 42 | EVERY house reached by a way, FORM a KNOB (100) | A | | `#is-every-farmhouse-reached-by-a-lane-and-in-what-form`; `_knobs.py:265` |
| 43 | Name-informed siting: read the village NAME (101) | D | GM 2026-07, general rule, Ueda example, cue glossary; NOT on page, NOT in engine | NOT FOUND |
| 44 | Homestead groves header + check list (102) | B (names F) | four of seven check names 0 hits | `homestead_parts/groves.py` |
| 45 | What it is - species mix, L-belt (103) | A | | `#homestead-groves-yashikirin---the-real-scale-and-prevalence` |
| 46 | why pointer (104) | C | | - |
| 47 | Prevalence near-universal (105) | A + B | B: `grove_prevalence` default 1.0, minimal-clump fallback | `groves.py:47` |
| 48 | Intramural farms carry NO groves (106) | E + B | city tier | `rolling/farmsteads.py:223-227` |
| 49 | Why the WINDWARD side N/W (107) | B | winter-monsoon rationale; page makes side a knob, record S+W (disagreement) | `hamletgen/water.py:43` |
| 50 | Per-map geography overrides `meta(windward=)` (108) | B | | `hamletgen/cluster.py:59` |
| 51 | Size-adaptive, merging, never drops a house (109) | B | four-step fallback ladder | `rolling/farmsteads.py:186-221` |
| 52 | The homestead SOLVER (110) | B | | `houses.py:242` |
| 53 | NOR DOES A NEIGHBOR'S FARMHOUSE - 39 ft (111) | A + B | | `#the-threshing-yards-sun-and-how-far-a-farmhouse-shades`; `consts.py:249` `SUN_CORRIDOR_FT` |
| 54 | THE LEGACY POOL IS DELIBERATELY EXEMPT, and the exemption cannot rot (112) | D | GM 2026-08-13, per-map counts, `meta.generated_by` gating, declined exemption list | mechanism exists; ruling only here |
| 55 | A grove never shades a yard (113) | A | | same anchor |
| 56 | Farmer wealth + homestead variation (114-117) | B | tiers 30/50/20% at 0.9/1.0/1.12; aspect 2.7:1 NOT FOUND in l7r (seed test only) | `houses.py:708,752` |
| 57 | Farmhouses face SOUTH (118) | B | seed test | `tests/gate/test_generator_contracts.py` |
| 58 | WALL AT LEAST 6 FT OFF THE PADDY (119) | A + B | | `houses.py:22` `HOUSE_PADDY_GAP_FT`, `:88` |
| 59 | Farmstead fixtures (121-138) | A (+B) | | `#the-farmsteads-fixtures...`; `fixtures.py:46` `FIXTURE_BANDS` |

Share by bytes: B ~63%, A ~16%, E ~7%, F ~6%, D ~3-4%, C ~1%.

## D items

1. **Name-informed siting** (L101, GM 2026-07, general rule). Read the place name before seeding: Ueda (上田) puts the dwellings DOWNSLOPE of the paddies; cue glossary (shimo-, kawa-, yama-, saka, hara, tani, sawa, hama, guchi); "the map should be able to be READ back into the name." Only other trace: a comment in `legacy-hand-authored-pool/villages/ueda/ueda.gen.py`.
2. **Legacy pool exempt from the yard-sun rule** (L112, GM 2026-08-13): Ueda 45/85 yards shaded, Hoshigaoka 31/70, Kikuta 27/55, Ubame 21/36, Hoshizora 19/44, hamlets 3-10; cities 0-1. Re-packing by hand judged the wrong trade; gated on `meta.generated_by`; declined: an exemption list somebody prunes.
3. **Headman is a FARMSTEAD with a kura** (L11, GM 2026-07-21, Hikari no Sato).
4. **Crescent pond labels itself "geomantic pond"** (L26, GM 2026-07-21): geomantic not religious; 背山面水; the half shape leaves room to grow; runoff basin, fire water, washing water; flat bank as forecourt.
5. **"Do not restore the old prose claim that a byre always abuts its farmhouse"** (L47) - the registry said so for months while the placer did otherwise.
6. **The phantom tail** (L49): Akagahara 181 px; Hoshigaoka/Kikuta ~210 px kept on purpose; lesson: pin a derived outline to what is drawn.
7. **Cluster-compactness honest limit** (L54): 0.20 / 0.28-0.31 / 0.40; floor 0.25; 0.31 ceiling accepted.
8. **Twin-detector 4-of-8 calibration and the GM's read** (L36): why `settlement_form` was added as the biggest structural axis.
9. **Kura roll position-seeded** (L42, 2026-08-17): re-pack took Kashikawa 25% -> 15%; declined: household index.
10. **Garden's eastern-sky nudge** (L84, GM 2026-07 "move it a bit south"): clear every east arm in one 1-D move; test real footprints.
11. **2026-09-07 garden-size wording correction** (L89): nothing inflated in the scripted era (everything-to-scale ruling 2026-07-21).
12. **The `"big"` glyph's unreserved wing** (L97): nucleated headman uses `"plain"`.

## B items the engine does not encode

1. Farmhouse aspect ~1.3-2.5:1, fires above ~2.7:1 (L116) - seed test only; minka-bays reasoning prose-only.
2. Dispersed sizing caveat - TWICE the margin room per farm; declare fewer households rather than compress (L26).
3. Settlement-form research (L94): Knapp; North China 1,000+ household villages vs South China ~30-60; 200-500 villages/100 km²; dispersed as Sichuan-type. Uncited; no Sources line.
4. Byre footprint rationale ~31x21 ft = ~16 m², 6-8 m² per ox (L46); must not read as a multi-stall barn.
5. Garden band 10-140 m² with tsubo/se conversions; generator measured ~35-115 m² centered ~55 (L89); page has no garden-size entry.
Also prose-only: the typing-rule rationales for `cluster_position` / `cluster_shape` / `lane_skeleton` / `water_source_position`.

## Inbound references

Real ones: `settlements.md:15,38`; `research/README.md:18`; `research/homesteads.html:15` (visible link), `:225` (comment); `farm_fixtures.py:8,31` (page has equivalents); `shrines_wells/byres.py:224,255` (borrow-or-hire rule - page's byre entry is about wells, not sharing); `dev/pool.md:97` (sun rule - page has it); `future-work/farming-communities.md:1324,1655` (byre share - prose only); `kashikawa.notes.md:267,567`; `.claude/agents/settlement-review.md:49`; `inashiro.notes.md:1129` (BROKEN today: text says html, target says md). False positives: `wip/*.html`, `dev/placement-stages/*.html` (rendered pages with a stale `research/homesteads.md` string), `scripts/fixtures/main-tree-refusals-2026-09.json`.

## Disagreements

1. L50 lists "smaller than its farmhouse" as live; L56 and the page and `yards.py` say the opposite.
2. L107 derives N/W as THE rule; the page says the record gives S/W (Tonami sugi south to west) and the side is a map default knob.
3. L103 puts bamboo in the N/W arms; the page labels that a GUESS, ja.wikipedia puts Tonami's bamboo south.
4. Byre fraction 0.2 in the md; the shipped stage calls 0.22 / gap 60.
5. Kura ~30% has no supporting research entry (page: Sugiura 0.24).
6. Fourteen check names no longer exist anywhere.

## Verdict

Delete it and almost nothing operative is lost for the hamlet tier. Lost: the twelve D items (name-informed siting above all), five prose-only B rules (one of them un-migrated uncited research), the village-tier knob catalog and compactness calibration, the twin-detector's calibration reasoning. Smallest restructuring: D items into `research/homesteads.html` as Decision paragraphs (name-informed siting needs a new question; shading exemption under the threshing-yard sun entry; crescent pond under a geomancy heading or water); the five prose-only rules into the code they govern with the Knapp material through the research pass; the village content parked with the village tier; F units deleted; four inbound links re-pointed; the Inashiro dead link fixed.
