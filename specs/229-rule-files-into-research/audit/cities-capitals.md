# Audit: the city tier - `settlements/cities.md`, `settlements/cities/*.md`, `settlements/capitals.md` against `research/cities/*.html`

Independent Opus reader, 2026-09-12. Section granularity. Class E here means SETTING-CANON.

**Dominant finding**: every file is written against a validator that no longer exists. 325 distinct named checks across the eight files; none executable (the ~11 grep hits are prose mentions in engine comments). Per file: cities.md 115, fabric.md 54, government.md 44, defenses.md 35, hinterland.md 31, river-cities.md 18, capitals.md 16, sizing.md 12.

## cities.md (30.7 KB, the tier index; NO research counterpart)

| Section | Class | Engine / anchor |
|---|---|---|
| Header + load table (2.3 K) | C | - |
| ASK THESE THREE BEFORE DRAWING (1.4 K) | D (B) | GM 2026-08-11: the capital's bearing is a GM fact; `capital_dir` NOT FOUND in `l7r/` |
| A CITY IS RINGED BY ITS FARMLAND (2.2 K) | D (B) | GM 2026-08-11 verbatim; 4 fields / 3 flanks floor NOT FOUND; `farmland_ring` `city/canals.py:108` |
| What a provincial city is (3.1 K) | E | `citybudget.py:37` `CASTE_FAMILY_FRAC` |
| Framing - crop tight to the walls (1.3 K) | B | `city/crop.py` |
| What the gate demands of a city (12.9 K) | F | ~115 deleted checks |
| A field may DRAIN INTO the moat + the north shelf (1.9 K) | D | GM 2026-08-11; the earlier note blamed the current and was wrong |
| Half-built field UNRECORDED / hem per field (0.9 K) | D | |
| The belt loop lives in the ENGINE (3.8 K) | D (B) | GM 2026-08-12; `canals.py:108`, `:62` `_ring_upslope`; perf trap recorded |
| Next on the farmland work (1.7 K) | C | `comb_field` still copied in four gens |

Shares: F ~42%, D ~33%, C ~13%, E ~10%, B ~4%, A 0%.

## cities/sizing.md (22.3 KB, NO research counterpart)

Grounding: partly `research/cities/fabric.html#a-county-seats-street-share-open-reserve-and-civic-share`; the budget model, density calibration and tolerances only in `specs/009-city-area-budget/research.md` (pre-HTML, no footnotes). `citybudget.py:109` points back at `sizing.md`.

| Section | Class | Engine |
|---|---|---|
| Size the wall to HOLD the city; every open is CLAIMED; dead-ground detector (32 px grid, 20 px clearance, 4,000 px²) (2.5 K) | B (F) | detector NOT FOUND; `animal_ground` `lodging.py:162` |
| Tango's quarters (0.5 K) | C | |
| `city_capacity` + four verdicts + `--capacity-map` (3.8 K) | F | `RHO_CANONICAL`, `suggested_wall_scale` NOT FOUND |
| THE DECLARED POPULATION IS EXACT (2.3 K) | D | GM 2026-07-26; `fill_exactly` in gens only |
| Quarters and per-quarter density [0.30,2.30]/1000 px², `DEAD_ZONE_MAX` 150, `CIVIC_OPEN_TOL` 70%, `RESERVE_CAP_FRAC` 20% (5.5 K) | B (F, D) | `s.quarter` `water_ways/wards.py:155`; every constant NOT FOUND |
| Budget-first wall sizing feature 009 (2.4 K) | B | `citybudget.py:407` `derive_wall`, `:423` `plan_city` |
| Six grounding bullets (4.6 K) | A/B | `C_PACKED=690` `:50`, `C_SPACED=2480` `:51`, `CIRC_FRAC=0.07` `:133`, `AGRI_FRAC=0.15` `:145`, `TEMPLE_PRECINCTS` `:115` |

Shares: B ~47%, A(partial) ~21%, F ~17%, D ~10%, C ~5%.

## cities/defenses.md (31.1 KB) vs defenses.html (8.3 KB, 3 sections)

| Section | Class | Engine / anchor |
|---|---|---|
| Wall is a CLOSED ring, >=2 gates (0.7 K) | B | `city/walls.py:485` |
| PLANNED sally/postern gate knob (2.2 K) | D | NOT FOUND |
| MOAT rings the wall, feeder ±25% (1.1 K) | B | `city/moat.py`; width `px(66)`; feeder rule NOT FOUND |
| Gate guard house + inspection + tower (1.9 K) | B (E) | `walls.py:227-260` |
| Wall TOWERED, three defense tiers (4.4 K) | B | `_knobs.py:446` `WALL_DEFENSE`, `:542`, `:532` `KIDO_TOWER_KEEPCLEAR=62`; `walls.py:383-420` |
| RING ROAD inside the wall inset 34, corridor `width/2+17` (3.5 K) | B | `walls.py:59`; junction rules NOT FOUND |
| Gate structures TO SCALE (1.5 K) | A | `#gate-structures-real-footprints`; `walls.py:89,219,252,304` |
| Gate OPENING to scale; 228 ft bug; NO check argued (2.5 K) | D | throat 30 ft `walls.py:509-515` |
| Gate furniture AT THE THROAT (2.2 K) | A | `#gate-furniture-at-the-throat-barbican-and-tax-barrier-practice` |
| Gate's own tower AT its gate (1.3 K) | B (D) | `walls.py:278-305` |
| Wall towers - tunable tier (4.4 K) | A + B | `#wall-towers-the-mamian-system-and-bowshot-ranges`; rectangular-vs-round doctrine on no page |
| NEIGHBORHOOD WALL JOINS THE CITY WALL (3.6 K) | D | GM 2026-07-27; `s.ward` snapping `water_ways/wards.py` |
| Gate furniture never overlaps (0.7 K) | B | |

Shares: B ~44%, D ~27%, A ~26%, C ~3%. **Disagreements**: the md states as fact what the page marks GUESS/unsourced - opposite-flank guard/inspection ("a GUESS - no readable page supports it"), the 52x30 gate-tower footprint, Shen Kuo 矢石相及 and Pingyao 50-60 m; setback ~110-135 ft vs the page's ~20-100 ft unsourced; mamian 62x40 vs ~65x40.

## cities/fabric.md (38.8 KB) vs fabric.html (11.2 KB, 3 sections)

| Section | Class | Engine / anchor |
|---|---|---|
| Walled merchant compounds rolled 30/40/30 (2.0 K) | D (B, C) | GM 2026-07-23 gate is a granted privilege; `_knobs.py:424` |
| Imperial road N-S + label outside a gate (0.6 K) | B | NOT FOUND |
| Commercial ribbon >=1 per 130 px; 1 storefront per 25-30 residents; LAST (2.0 K) | B | NOT FOUND |
| >=1 burakumin neighborhood inside the walls (0.3 K) | B/E | NOT FOUND |
| Streets form a crossing GRID (7.3 K) | B (C) | `step >= 0.8 x footprint`, near-miss/stub/aligned rules, `skip`-identity gotcha; NOT FOUND |
| Shops front, poor housing fills interiors (6.7 K) | B (E) | 85 px frontage band, spread >=1.3x, alley ~1 per 30 px, one lane per block, gate spur exemption; `laborer_large` `structures/urban.py:28`; thresholds NOT FOUND |
| `s.bound` fills the wall's shape (0.4 K) | C | |
| Civic amenities port up (4.5 K) | B + D | kura >=5, flophouse in+out of every gate, caravan cluster within ~340 px, theater >=185; flophouse-count decision is D; `lodging.py` |
| Fire defense >=2 towers dispersed, LAST (0.9 K) | B | `boards.py:26`; dispersal NOT FOUND |
| Contiguous terraces row-packing >=55% touching, <=2 px gap, idobata every 2 rows (0.9 K) | B | `packing.py:47` `rowpack` |
| Estate wall on dry private ground (1.7 K) | D | GM 2026-07-19; `compounds.py:208` |
| Doors face OUTWARD; rows <=2 deep; `DOOR_CLEAR_FT = 7` (1.7 K) | D | GM 2026-07-18; `servants.py:49` |
| Fire towers: the fire-defense of a dense ENCLOSED wooden core (6.3 K) | B (research content, misfiled) | hinomi-yagura, hansho, Meireki, jin'ya confirming case (GM 2026-07-24), Song wanghuolou, machi-bikeshi anachronism; `hinomi` nowhere in research/; no citations |
| Why we DON'T depict firebreaks (1.3 K) | D | both depictions priced and declined |
| Commoner housing CONTIGUOUS (1.4 K) | A | `#urban-commoners-built-in-continuous-street-walls` |

Shares: B ~76%, D ~17%, C ~3%, A ~3.5%. **Disagreements**: row-packing rests on the frontage tax; `fabric.html` says ja.wikipedia 京町家 disputes it; the page records an 18 ft median gap departure the md's 3-6 ft doctrine omits.

## cities/government.md (34.1 KB) vs government.html (19.2 KB, 3 sections)

| Section | Class | Engine / anchor |
|---|---|---|
| Provincial government in the interior; six ministries; Rites in the temple neighborhood; torii roll; small shrines >=3; samurai ~65% of cohort; yamen >=3x a ministry; ~14 px (8.5 K) | B | `castle_civic.py:278` `ministry`, `city/civic.py:17`, `_knobs.py:393`, `shrines.py:71`; distances NOT FOUND |
| Servant ranges in the samurai ward (4.3 K) | A (D, B) | `#servant-housing-in-the-samurai-ward---servants-are-drawn-as-walls-not-as-houses`; `servants.py:92` |
| Martial hall + rolled dojos (2.1 K) | A/B | `castle_civic.py:330` `DOJO_PER_SAMURAI = 200`, `:353`, `:491` |
| A small city GATES its ward, does not WALL every quarter (5.9 K) | B (D) | `_geom/walls.py:53` `WARD_BARRED_KINDS`, `:56`; `water_ways/wards.py:65` |
| The kido squares to the LANE (1.9 K) | D | GM 2026-07-26; `water_ways/kido.py` |
| The guard box on the VERGE (1.8 K) | D | GM 2026-07-26 + three failed approaches |
| Keep-clear reads the kido's TRUE parts (0.6 K) | B | `kido.py:198` |
| `s.kido_reservation` ordering (0.9 K) | C | `kido.py:103` |
| Historical grounding: martial training (7.4 K) | D (A) | GM 2026-08-08 "I don't know where the 1 per resident samurai number came from"; the ROLL wins; `#martial-training-is-an-urban-institution`; `castle_civic.py:417-438` |

Shares: B ~44%, D ~32%, A ~19%, C ~5%.

## cities/hinterland.md (18.7 KB) vs hinterland.html (4.4 KB, one section)

| Section | Class | Engine / anchor |
|---|---|---|
| Cramped lots push samurai to estates OUTSIDE, 1-3 shown, >=200 px, vary >=1.5x (1.9 K) | B (A) | `#gentry-estates-are-dispersed-not-clustered-at-the-wall`; counts NOT FOUND |
| Farmland close, farmhouse-worked; comb params `plot_across=26`, `row_step=(13,19)`, 55,000 px² floor; 7 farmhouses per 1000 px; `dry_polys` vs `block_polys` (5.9 K) | B | `settlement/core.py:198`; densities NOT FOUND |
| Gate market outside EVERY main-road gate; floor 3 -> 6 (GM 2026-07-24); guan-xiang 10-40 (1.8 K) | B (D) | NOT FOUND |
| Extensive farmland outside (0.3 K) | B | NOT FOUND |
| No farms inside by default; `agricultural_district`; 16 per 1000 px; chiral comb; RNG trap (2.8 K) | B (C) | `citybudget.py:145` `AGRI_FRAC`; densities NOT FOUND |
| Estates: the belt is a SLICE (0.7 K) | D | GM 2026-07-19 |
| Freed ground goes to the agricultural district (0.7 K) | D | GM density canon |
| Samurai estates DISPERSED (2.0 K) | A (D) | same anchor |
| In-wall VEGETABLE tracts ~55 ft / <=0.15 acre (1.8 K) | B | NOT FOUND |

Shares: B ~77%, A ~11%, D ~7%, C ~4%.

## cities/river-cities.md (10.3 KB, one 9.5 KB bullet) vs river-cities.html (10.2 KB, 2 sections)

Sub-items: one mouth on the river not two (GM 2026-07-23; Suzhou) - D; sluggish far-side circulation ACCEPTED ("do not fix it") - D; junction angles follow the current (GM 2026-07-24, overturning an earlier call; outlet 22 deg downstream, inlet 10 deg near-square - bedload) - D + B (`city/moat.py:27-28`); engine vocabulary - B (`water.py:79`, `moat.py:20,134`, `canals.py:20`, `waterfront.py:151,165`); the checks - F; gateposts tangent-aware, estates face the capital, funerary off fields - B (`walls.py:219`; `capital_dir` NOT FOUND); clan's TWO patron fortunes - E; render/layout ORDER - C (general doctrine in a variant file); Nagahara DONE - C.

Shares: D ~37%, B ~21%, C ~18%, F ~15%, E ~5%, A 0%. **The page titles itself "the research behind the river, moat-junction and wharf rules" and contains zero junction-angle content.**

## capitals.md (40.2 KB) vs capitals.html (130 KB, 35 sections)

| Section | Class | Engine / anchor |
|---|---|---|
| Header + STATUS block (3.4 K) | C (F) | named capital checks NOT FOUND |
| What a domain capital is (1.8 K) | E | `citybudget.py:163` `CAPITAL_POP=12_360`, `:169`, `:177` |
| Rectangles not circles (1.0 K) | A | `#wall-geometry-rectangles-and-terrain-loops...` |
| Scale and the wall, `ftpx=3` (1.2 K) | B | `citybudget.py:285` |
| The castle + WHY blank + the ward experiment (4.3 K) | D | `castle_civic.py:39`, `:63` cites by name |
| Inventory INSIDE vs OUTSIDE (2.5 K) | B | `imperial_granary_seat` `:339` |
| Two castle seats (1.1 K) | A/B | `citybudget.py:231` `CASTLE_SEATS`, `:363` |
| The government ward (0.9 K) | A | `#the-ministries-sit-outside-the-castle-flanking-the-approach-avenue` |
| Compounds with no provincial equivalent (2.3 K) | B (E) | `castle_civic.py:417` `hanko`; cited by `compounds.py:65` |
| Ward structure a MESH (2.5 K) | A | `#neither-tradition-walls-its-wards...`; `ward_style` NOT FOUND |
| Placements that change (0.9 K) | A/B | `citybudget.py:213` `C_TERRACE=660` |
| Rules that INVERT (1.2 K) | B (A) | `CAPITAL_RANK_BANDS` |
| Counts that multiply (0.9 K) | B | none encoded |
| Martial training unchanged (0.6 K) | A | |
| Moat complete RING with sluiced leats (0.7 K) | A | `#the-moat-ring-and-the-river-flank-moat-are-both-real...` |
| Water: an AQUEDUCT, NO ARCADES (1.9 K) | A | `#the-aqueduct-is-open-outside-the-wall...`; `waterfront.py:90,95` |
| Wharf and tax-rice warehouses (3.5 K) | A | four anchors |
| Settled defaults (0.6 K) | D (F) | clan identity = labels only (GM 2026-08-08); "encloses all 12,360" CONTRADICTED |
| Shiro Daika clan, roads, gates (3.1 K) | E | |
| Shiro Daika's lineage compounds (2.8 K) | E (D) | kurogi correction GM 2026-08-08: size tracks households housed; `lineages` NOT FOUND |
| Open, still to settle (1.4 K) | C (F) | `SAMURAI_INWALL_FRAC` settled at `citybudget.py:188` = 0.85 |
| Per-household ground costs "proposed" (1.6 K) | B, encoded | `C_YASHIKI=4150` `:201`, `C_TERRACE=660` `:213` |

Shares: A ~30%, B ~24%, E ~19%, D ~16%, C ~12%.

**What capitals.html holds that capitals.md does not** (roughly half the page, much of it operative): funerary ground setback (>=150 ft past the moat's outer face; pollution binary; Edo moved for stench); the four trades scaling classes (6 bathhouses, one cremation ground sized up, one pauper mound, kilns consolidating, dye works a street); how much lives OUTSIDE the walls (GM ruled 2026-08-10 ~2.8%; 57% and 30% declined with why); the dimensional audit (17 families at 3 ft/px); how a josui ran (intake angle, 21 cm per 100 m, open-topped, no kakehi, josui-ido draw-basins); street widths (ote-suji 45 ft = 1.5 x 30 ft highway, GM 2026-08-28); sluice duty cycle (one closed-board glyph); moat scumming, sluice frame / quay kura / boat-length jetty, temple approaches, six equal ministry compounds, the aqueduct-vs-moat-spill artifact, the out-wall samurai budget line.

## D items (city tier), in full

1. cities.md ASK THESE THREE (GM 2026-08-11): the capital's bearing is not derivable; joins water-flow and clan as intake facts in `meta`.
2. cities.md A CITY IS RINGED BY ITS FARMLAND (GM 2026-08-11 verbatim: "keep adding rice paddies and farmhouses until there are no more places to put them. Farmland ringing a city is the DEFAULT"); floor 4+ fields / 3+ flanks.
3. cities.md drain-to-moat (GM 2026-08-11): a field upstream of the draw may DISCHARGE into the moat; the first diagnosis (the current) was wrong; the north shelf unfarmed for depth.
4. cities.md the belt loop (GM 2026-08-12): `s.farmland_ring`; byte-identity migration proof; four divergence hooks; snapshot cropland boxes once (11 s -> ten minutes otherwise).
5. sizing.md DECLARED POPULATION IS EXACT (GM 2026-07-26: "we must ALWAYS meet that number EXACTLY"); 7% band gone; grow the wall, never trim the figure; Minami 486 vs 520.
6. defenses.md sally/postern knob deferred with framing (wengcheng sortie point; karamete-mon / umon / shuimen).
7. defenses.md gate opening 228 ft units bug; NO check argued ("the number it would assert is the number the code already computes").
8. defenses.md ward fence joins the wall (GM 2026-07-27 Minami); join-not-cross FAMILY; the linecap arithmetic; placement side snaps.
9. fabric.md merchant estates rolled 30/40/30 (GM 2026-07-23: a granted privilege).
10. fabric.md estate wall on dry private ground (GM 2026-07-19).
11. fabric.md doors face outward, rows <=2 deep (GM 2026-07-18); `DOOR_CLEAR_FT = 7`.
12. fabric.md flophouse count (GM 2026-07-24): unknowable; symmetric 1 in + 1 out per gate a generous stylization; declined: busiest gate only; animal-yard cart-inn.
13. fabric.md why no firebreaks: drawn plaza reads as a plaza; label-only adds a word; build a real feature if needed.
14. government.md kido squares to the LANE (GM 2026-07-26; 38 and 44 deg off on Tango/Nagahara under the fence reading).
15. government.md guard box on the verge (GM 2026-07-26) + three dead ends (curving ring road; tower keep-out widened and dropped; far flank on the rampart).
16. government.md attested vs extrapolated martial training (GM 2026-08-08); the ROLL wins; countryside not counted (GM 2026-07-25); two disclosed departures.
17. hinterland.md estate belt is a SLICE (GM 2026-07-19): >=2, cut by the frame.
18. hinterland.md freed ground -> agricultural district (GM density canon).
19. river-cities.md sluggish circulation ACCEPTED (~800 ft apart, tiny head; period-accurate stagnation).
20. river-cities.md junction angles follow the current (GM 2026-07-24, overturning): outlet 22 deg, inlet 10 deg - bedload.
21. capitals.md WHY the castle is BLANK (GM 2026-08-08: "I'd rather nothing be shown than the WRONG thing be shown"); general doctrine for every implied-interior compound; `castle_civic.py:63` cites it.
22. capitals.md internal-ward experiment: two renders, both nested rectangles; "rectangles inside rectangles read as ABSTRACTION"; `baileys=False` stays; ishigaki doubling survived; caveat: judged inside a blank city.
23. capitals.md clan identity changes LABELS ONLY (GM 2026-08-08).
24. capitals.md size tracks HOUSEHOLDS HOUSED not rank (GM 2026-08-08, kurogi).
25. (on capitals.html already) the extramural ruling (GM 2026-08-10).

## B items nothing encodes, grouped

a. Density and capacity model (sizing.md): `RHO_CANONICAL = 0.00149`, four capacity verdicts, `suggested_wall_scale`, cell classification, `[0.30, 2.30]/1000 px²`, `DEAD_ZONE_MAX = 150`, `CIVIC_OPEN_TOL = 70%`, `RESERVE_CAP_FRAC = 20%`, dead-ground detector, `population_tol = 0.0`, `fill_exactly`/`top_up`. (Budget half survives in `citybudget.py`.)
b. Lane and street geometry (fabric, defenses): near-miss 2-30 px, stub 3-50 px, aligned-lanes-meet 37 deg / 80 px, streets-meet-through-lanes T rule, `city_larger_streets_lined` 140/58 px, `businesses_front_streets` 85 px, alleys ~1 dwelling per 30 px, `no_isolated_dwelling_cluster` 95 px / >30, ring-road clearance, `step >= 0.8 x footprint`, `frontage(skip=)` identity gotcha.
c. Placement distances and counts: gate market >=6 / 520 px; flophouse 520 px; caravan cluster 340 px / <=4 dwellings within 75 px; theater >=185; estates >=200 px, 1-3, >=1.5x; fire towers ~230 px, district centroid; wells 1 per 10-20 hh, none in the samurai quarter; ministries within 480 px of the yamen, 85 px of a street, 14 px apart; yamen >=3x; gate furniture <=70 px; moat feeder ±25%.
d. Farmland densities and comb params: 7 farmhouses per 1000 px outside, 16 inside; 55,000 px² floor; `plot_across=26`, `row_step=(13,19)`, canal spans 60-260, `field_fall` 90-190; `(47, 88)` dry hem; vegetable beds ~55 ft / <=0.15 acre; 4 fields / 3 flanks.
e. Commercial intensity: >=1 per 130 px; ~1 storefront per 25-30 residents; wealth 8/12/80; spread >=1.3x; `laborer_large` 6-20%; rows >=55% touching, <=2 px gap.
f. Capital knobs declared not built: `ward_style`, `lineages` / `ruling_lineage`, `capital_dir`, the 021 housing program, counts-that-multiply (fire towers ~10-15, wells ~160-240, estates ~4-8, kura ~20).
g. Deferred designs: sally/postern knob; district-scale hinterland map; `comb_field` into the engine; the capital's belt-loop re-tuning.

## Inbound references (code -> rule file, by heading)

`citybudget.py:109` -> sizing.md (no page); `citybudget.py:157` -> capitals.md + capitals.html; `castle_civic.py:63` -> capitals.md "WHY blank" (NO page equivalent); `castle_civic.py:429` -> government.md martial training (page has it); `castle_civic.py:438` -> capitals.md hanko (page has it); `structures/urban.py:61` -> government.md servants (page has it); `structures/compounds.py:65` -> capitals.md "Compounds with no provincial equivalent" (partial, scattered); `city/waterfront.py:95` -> capitals.md aqueduct (page has it, same title); `city/moat.py:42` -> settlements.md "junction angles" (two hops; page lacks it). Docs: `CLAUDE.md:93`, `SKILL.md:89`, `settlements.md:21-22,44-48`, `research/README.md:11-16`, `future-work/CLAUDE.md:12`, `future-work/cities.md:51`, `settlement-review.md:49`, `wip/shiro-daika.notes.md:441,489`, `minami.notes.md:149`, `nagahara.gen.py:1024`, `tests/tier_city/settlement/test_core.py:57`; `wip/shiro_daika/*.py` cite capitals.md five times.

## Disagreements

1. capitals.md "the wall encloses all 12,360 inhabitants" vs the 2026-08-10 ruling (~2.8% extramural) on capitals.html and `citybudget.py` (`suburb` share, `:344`).
2. capitals.md lists `SAMURAI_INWALL_FRAC` as open; `citybudget.py:188` ships 0.85.
3. capitals.md's proposed-rows table omits `C_PACKED_CAPITAL = 950` (`:65`) and `CIRC_FRAC_CAPITAL = 0.15` (`:140`); calls `C_YASHIKI`/`C_TERRACE` proposed.
4. capitals.md STATUS lists capital checks as shipped and gated; none exists.
5. defenses.md states as attested three things defenses.html marks GUESS/unsourced.
6. fabric.md's frontage-tax rationale disputed on fabric.html.
7. sizing.md cites Chang in Skinner for civic 5-15%; fabric.html has civic share unsourced; mamian 62x40 vs ~65x40.
8. river-cities.html advertises junction-angle research it does not contain.

## Verdicts

cities.md: 42% dead checks written as a contract; the rest four GM rulings, caste canon and the framing formula - the farmland-ring ruling would be lost outright. sizing.md: half describes a deleted tool; the density half exists only here and in a pre-HTML spec artifact - highest silent-loss risk. defenses.md: best balanced; the md runs ahead of its evidence. fabric.md: 76% pure operative rule, almost none encoded; a 6.3 KB fire-tower research narrative in no research page. government.md: the healthiest pair; the kido pair with its dead ends is md-only. hinterland.md: 89% has no why anywhere. river-cities.md: the junction hydrology and the accepted stagnation are the valuable content and the page lacks them; carries the tier's render order. capitals.md: the inverse - the page is richer; the md uniquely holds the castle doctrine and the ward experiment, and is the most stale file in the tier.

Overall: the why is mostly safe; what would be lost is ~25 dated GM rulings and accepted limitations, the ~150-item threshold layer, and the unscripted tiers' only statement of what to build. The what CAN live on the page beside the why - capitals.html already does it and it is the strongest writing in the tier - except rendering/procedural material, setting canon, and GM rulings about the drawing (which the extramural entry shows the record can hold when the declined options are recorded). What has no why at all: the sizing model's density half; the fire-tower narrative; the threshold layer in fabric and hinterland; the junction hydrology.
