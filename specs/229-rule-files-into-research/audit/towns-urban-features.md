# Audit: `settlements/towns.md` (37.8 KB) against `research/towns.html` (9.5 KB); `settlements/urban-features.md` (88.6 KB) against `research/urban-features.html` (106 KB)

Independent Opus reader, 2026-09-12. Both tiers unscripted; the class E here means SETTING-CANON.

## towns.md

Units (line: class; engine / anchor):
- 1-9 header: C.
- 11a Hoshizora exhibit description: C. 11b town comb grain `plot_across=58`, `row_step=(52,72)`: B; gens only (hoshizora/ubame/hirameki `.gen.py`), no town default in `l7r/`. 11c town farmsteads run the nucleated to-scale bundle + GM 2026-07 house-first reversal: B/D; wiring in the gens. 11d windbreak COMPOSITION rule (>=12 clumps within 150 px): B; `hinterland/belt.py:113-116`; `rolling/roll.py:349`. 11e canopy-fraction metric calibrated and REJECTED (4-18% vs 29-45%): D.
- 12-25 the belt's BEARING is not a rule (face-to-wind ratio Ubame 1.46 vs Hoshizora 1.02, Hirameki 0.90-1.13, Moritono 1.25, Ueda 1.33; principal-axis error Ubame 31 deg vs approved 33-49): D; "do not add a bearing check".
- 25 in-field flourishes OFF at town+city: B; NOT FOUND.
- 26 Hirameki exhibit (five water topologies, cascade, toe_block): C+B.
- 27a tier ~1,200 / ~238 households: E; `interactive/assets/place.json:24`, `place.py:89`. 27b caste counts 24 merchant / 29 laborer / 13 servant / 12 burakumin / 4 samurai / 156 farmer: E; NOT FOUND. 27c three modeling conventions (servants inside compounds; shops ungated; samurai barracked): D. 27d wealth-varied housing (`merchant_large` 4-5 of 24, `laborer_large` 2-3 of 29, hand-set after the packs): B; counts NOT FOUND. 27e banding shops -> merchant homes -> >=35 px -> laborers (Hoshizora 106-116 vs 156): B; NOT FOUND. 27f homes share storefront orientation, mod 180, 15-74 px depth: B; `frontage()` rotates (`houses.py:449`); window NOT FOUND.
- 29-31 unifying principle: A; `towns.html#chinese-towns-were-planned---the-gate-to-yamen-axis`.
- 33 urban core, awning 5 ft, sign floored 6x5 px, 92 px setback: B+C; awning/sign encoded `structures/urban.py:86-95`; setback NOT FOUND.
- 34 streets history: A. 35 road spine off both edges: B; `structures/ground.py:31`.
- 36 theater stage within ~260 px of the hall, ground opens toward it, `rot` table, inside the wall: B; glyph `urban_fixtures.py:13`; thresholds NOT FOUND; partial why on `research/cities/capitals.html`.
- 37 granary implied by the manor; `meta(granary=True)`: B+D; `civic_grounds/civic.py:99`.
- 38 market-day flophouse: A+B; `lodging.py:49`; `towns.html#the-market-day-flophouse---who-actually-stays-over`.
- 39 caravan inn + stables 150 px, open ground, fronts the route: B; `lodging.py:91,123`; thresholds NOT FOUND; no why anywhere.
- 40-51 THE MANOR IS A GLYPH, AND IT IS ALWAYS A BOX (GM 2026-07-27): D.
- 52 manor at the edge, gate faces what it fronts, tilt reshuffles -> pick a seed: B+D; `structures/compounds.py:24`.
- 54-56 `s.wall` irregular >=5 sections, CoV >= 0.25, clearance ~46: B; `castle_civic.py:824` draws; rule NOT FOUND; `towns.html#a-ramparts-cost-scales-with-its-length`.
- 57 open arc anchored to a steep hill: B; `shrines.py:24`. 58 chrysanthemum field flush inside the wall: B+E; `castle_civic.py:867`.
- 59a whole urban core inside the wall: A+E. 59b gate market ~4-8, floor >=3 within ~420 px, shops ungated: B; NOT FOUND; `towns.html#the-gate-market-exists-for-traffic-not-taxes`.
- 61 fire-watch tower walled yes / open no, commoner quarter, placed LAST; the 2026-07 widening reverted 2026-07-24: B+D+F; glyph `structures/fixtures/boards.py:26`; the "Fire towers" grounding it cites exists in NO file.
- 62 `s.bscale ~ 0.82`, Hirameki `Settlement(2600, 1820)`: F (both wrong: bscale retired; canvas is (2600, 2000)).
- 63 streets carve blocks 26/20 px, `main=True`, `face_streets="fill"`: B+C; `water_ways/lanes.py:214`; `packing.py:156`.
- 64 no street to nowhere ~130 px, "fronts" not "near", a fence breaks frontage; the Tango red herring: B+D; NOT FOUND; `towns.html#a-street-is-access-infrastructure...`.
- 66 wall hugs the town 280/140 px, two slacks, pull the face in: B; NOT FOUND.
- 67 the town-scale check roster (~30 names): F - every name dead.
- 68 farmers, fields and the economy of the wall: A+B.

Share: B ~44%, C ~19%, F ~14%, D ~12%, A ~6%, E ~5%. Measured: 34 of 50 backticked identifiers resolve nowhere in `l7r/` or `tests/`.

### towns.md D items
1. THE MANOR IS A GLYPH, AND IT IS ALWAYS A BOX (GM 2026-07-27): walls + gate + empty court, a simplification not a scale reduction; three consequences (Mode B footprint need not match the Mode A sheet; outside-the-walls Mode A features need not appear; the glyph contains everything the sheet shows); `settlement-review` must not report a difference; reported on Ubame and withdrawn.
2. The windbreak bearing measured before believed (2026-07-27): two metrics refuted a review; the wind chooses the SIDE not the bearing; do not add a bearing check.
3. Canopy-fraction shelter metric calibrated and rejected; the form-aware adjacency metric replaced it (approved maps nestle at 37-131 px).
4. House-first town farmstead path reversed (GM 2026-07): center-tested fields, a 44 px house sank a corner into crop.
5. Fire-watch tower reverted to walled-only (2026-07-24): an open town has field gaps for natural breaks.
6. Three depiction conventions for the town census (servants ~5 stand alone; shops counted separately; samurai 5-10 houses, platoon barracked in the manor).
7. Manor tilt fixed by picking a seed.
8. `streets_have_buildings` threshold was a red herring (Tango: frontage counted ACROSS a ward fence).

### towns.md B items nothing encodes (a future town generator's inventory)
Census: 24/29/13/12/4 + ~156 farmers; farmer plurality; `merchant_large` 4-5 of 24, `laborer_large` 2-3 of 29; laborers <= farmhouses. Zoning: banding (shops front, merchants behind, >=35 px radial gap, then laborers; 106-116 vs 156 px); storefront orientation mod 180 with 15-74 px depth; 92 px housing setback; burakumin quarter its own pack. Wall: >=5 sections, CoV >= 0.25, ~46 px clearance; 280/140 px hug with terrain and gate-forecourt exemptions. Streets: 26 main / 20 cross px; gate-to-yamen axis through the gate; ~130 px street-earns-buildings as "fronts"; fence breaks frontage. Institutions: theater within ~260 px of a hall, ground opening toward it, `rot` table; inn + stables within ~150 px, open ground (fails >4 dwellings within ~75 px), inn fronting the route within ~115 px parallel; gate market 4-8 with floor 3 within ~420 px; fire tower in the commoner quarter, last; manor gate faces the dwelling centroid or the road, fallback south. Field grain `plot_across=58`, `row_step=(52,72)` at 1 ft/px; flourish gate-off.

### towns.md inbound and disagreements
Inbound: `settlements.md:20,43,55,60,61,131`; `research/towns.html:15`; `research/README.md:20`; `future-work/CLAUDE.md:11`; `.claude/agents/settlement-review.md:49,182`; **`tests/interactive/test_place.py:135`** quotes towns.md as the authority for ~238 households, ~156 farming (load-bearing for a live test). Disagreements: L62 `bscale` retired, canvas wrong; L61/L67 "Fire towers" grounding exists nowhere; L67 roster dead.

### towns.md verdict
The ONLY statement of the town tier's composition. towns.html is small because it is purely the why for five questions; most town institutions are grounded on `urban-features.html` and (theater) `research/cities/capitals.html`. What has no why at all: fire-tower scoping, caravan-inn thresholds, theater 260 px, gate-market 420 px, 35 px banding, 130/280/140 px thresholds, the `bscale`/canvas paragraph.

## urban-features.md

Units (line: class; engine / anchor):
- 11 merchant kura `s.merchant_storehouses(count=6)`, >=3, at the back: B; `civic_grounds/civic.py:152`.
- 12a kosatsuba two boards distinct: A; `#the-notice-board-kosatsuba---siting-is-a-traffic-decision`. 12b auto-site every tier (GM 2026-07-27 "fix both of them"; Hoshizora 3 vs peak 30, Hirameki 10 vs 29; auto 19 and 29): D; `structures/fixtures/siting.py:90`. 12c city set principal + one per gate ~800 ft: B; NOT FOUND. 12d marker floor `KOSATSUBA_MARKER_MIN_PX` 11, 12:5 aspect: B; `_knobs.py:454`.
- 13 THE CAPTION IS PART OF THE SEAT (GM 2026-07-27; Ubame 8 vs 23; `clear_label_seat`; "on the traffic" belongs to settlement-review): D.
- 14 the board is ROADSIDE 6 ft `KOSATSUBA_VERGE_FT` (GM 2026-08-26); towns/cities 60 ft: B+D; `_helpers.py:31`; `siting.py:113`.
- 15-31 THE BOARD IS THE LAST THING PLACED, AND IT CLEARS NOTHING (GM 2026-08-29, feature 154): D; `hamletgen/frame.py:59`, `driver.py:128`.
- 32-40 A BOARD UNDER A CANOPY IS FINE (GM 2026-08-29; caption z=20,000,005): D.
- 41-47 `kosatsuba_on_a_main_way` RETIRED as a check: D/F.
- 48 board FACES the road, 30 deg (GM 2026-07-27; worst legit 18 deg): B+D; `siting.py`.
- 49 board on a MAIN way ~60 ft band; punishment ground deliberately not covered (GM 2026-08-02): B+D; `tests/tier_town/settlement/test_structures.py:22`.
- 50-52 justice works: punishment inside, execution outside; tier sizes 60x60 / 100x60 / 150-250x50-80: A+B; `_knobs.py:476` `execution_ground_ft`; `civic_grounds/justice.py:76`; `#the-justice-works---why-a-county-seat-executes-and-why-the-ground-is-outside`.
- 53 boundary stone, `BOUNDARY_STONE_CLEAR_FT` 60 and why not 120: B+D; `_knobs.py:493`.
- 54 stone nearer the edge than the ground (GM 2026-07-27; centroid failed on Ubame 86 of 118): B+D; NOT FOUND.
- 55 placement order, `_CROP_HARD`/`_CROP_CITY`: C. 56 `tools/site_justice.py`: C. 57 practical traps: C.
- 58 farm belt wells 500 ft, 150 ft edge: B; `shrines_wells/wells.py:66` `farm_wells(reach_ft=500.0, edge_ft=150.0)` with docstring.
- 59 NO WELL IN THE PADDY WATER (GM 2026-07-27; cost Tango): B+D; `_geom/extents.py` `paddy_wet_rings`; `tests/hamletgen/test_wells.py`.
- 60 public wells ~290 px coverage, 26 hh per well, [0.35,0.85] size band: B; glyph `wells.py:30`; the numbers NOT FOUND; `#communal-wells-and-the-samurai-exception`.
- 61 rural wells 1 per ~20-25 hh, `near=85`, ~380 px: B; `homesteads/wells.py:20` (hamlet 1 per ~6); 20-25 and 380 NOT FOUND.
- 62 OUR well is the DOMESTIC one: A; `#wells-in-crop-fields-two-different-objects-and-only-one-of-them-is-ours`.
- 63 well among the dwellings ~95 px: B; `wells_among_dwellings` live. 64 set-apart shrine's own well >150 px: B; `wells.py:283`.
- 65 wells research + liberty: villages 1 per 8-26 hh, hamlets 2-20: B+D; hamlet band `homesteads/wells.py:23-27`; village band NOT FOUND; `#wells---the-research-and-the-deliberate-liberty`.
- 66 bell-and-drum tower ~36 ft city / ~30 ft town: A+B; `urban_fixtures.py:65` `px(36)`; `#the-bell-and-drum-tower---one-per-walled-seat`.
- 67 TRADE WORKS (8.1 KB): A+B; glyphs `trades.py:77-303`; bathhouse formula encoded `trades.py:210-218`; `city_*` scoping and fire gaps NOT FOUND.
- 68 KILN WORKS six glyph defects recorded (three review passes 2026-07-27): D; `trades.py:303`.
- 73 TANNING YARDS header, eleven check names, 120 ft correction: B+F; `trades.py:701`; 120 ft NOT FOUND.
- 75 FIELD DRAIN the caste's most attested water: A. 76 `rot` is the bank's bearing (GM 2026-08-08): A+D.
- 79 placement rules (a)-(g): B; NOT FOUND (only (d) argued on the page). 80-82 (b),(e),(f) with tolerances (15 deg; pool 2.1/3.8/7.2 vs 22.9): B+D; NOT FOUND.
- 84 burakumin-dwelling exemption from the 120 ft standoff (zero viable sites at Hoshizora): A+D. 85 a long walk to work is not a defect (GM 2026-07-24): D. 86 outcast side 90 deg NOT a distance; two maps waive (Tango, Ubame): A+D. 87 per-map siting: C+D.
- 90-97 stable yards: A+B+D; `lodging.py:123,155`, `_yardctx.py:83-94`; `#stable-yards---beaten-earth-hitching-rails-and-watering-by-relay`.
- 98-100, 102 pointer bullets: A.
- 101 burakumin seam 60 ft `BURAKUMIN_SEAM_FT`, cities exempt, reserve the collar first: B+D+F; the constant exists ONLY in this file.
- 104-120 CHARCOAL YARDS + four-rung separation ladder: A+B; `trades.py:458`; `#charcoal-yards-...`.
- 122-128 REFINING FORGES 60 ft, smoke vs filth: A+B; `trades.py:533`; `#refining-forges-...`.
- 130-135 CLAN BORDERS line not mound: A+B+D; `trades.py:633`; `#drawing-a-clan-border`.
- 138-168 Circulation inside a dense quarter (footpaths; census Tango 6+8, Minami 9+7, Nagahara 3+10, Hirameki 2, towns zero; two failed implementations): B+D; `structures/packing.py:156` `pack(..., footpaths=N)`.
- 170-186 The refining forge should read as a yard, not an appliance: D.

Share: A ~28%, B ~34%, D ~15%, F ~14%, C ~7%, E ~2%. Measured: 69 of 126 backticked identifiers resolve nowhere.

### urban-features.md D items
1. Auto-site every board (GM 2026-07-27). 2. Caption is part of the seat (GM 2026-07-27). 3. Board last, clears nothing (GM 2026-08-29): `village_grove` keep-out retired; frame guard tests `meta.view`. 4. Board under a canopy fine (GM 2026-08-29). 5. `kosatsuba_on_a_main_way` retired (2026-08-29). 6. Long walk to work not a defect (GM 2026-07-24). 7. Outcast side directional not metric; Tango (Emperor SE) and Ubame (land falls SW) waive (GM 2026-07-27). 8. Burakumin dwellings exempt from the 120 ft standoff. 9. Kiln works six glyph defects. 10. No animals on maps (GM 2026-07-25). 11. Dung-heap clearance two rounds, 24 px map-wide (GM 2026-07-25). 12. Wells/troughs/rails collide by design (glyph-level rule, no feet). 13. Burakumin seam measured center-to-center shipped eight farmhouses inside (GM audit 2026-07-27). 14. Forge reads as an appliance; levers are count, contrast, spacing. 15. Footpath census and two failed implementations.

### urban-features.md B items nothing encodes
City wells (26 per well, ~290 px, [0.35,0.85], no public wells in the samurai quarter); rural wells (1 per 20-25, `near=85`, ~380 px; village 1 per 8-26); tanning yard seven clauses (20 ft on-water reach, dry, outside walls, below every intake, no crop overlap, 15 deg squareness, 90 deg outcast side, 120 ft standoff + exemption); justice works (~60 ft traffic band, execution ground 120 ft from road / 400 ft from gate, outcast-side and past-the-stone ordering, nearer the edge than the ground); fire/nuisance ladder 6 farrier / 30 charcoal / 60 forge + kiln / 120 crematory + tannery (only 400 ft and 60 ft exist as constants); trade-works scoping and the `meta(river_port|charcoal_district|iron_district|imperial_road)` opt-ins, dye works 40 px on-water, farrier 250 ft stables pairing, kiln body gap and cottage bookkeeping; stable yards 24 px heap-to-rail, 40 ft trough-to-well, 2-3 troughs, 85 px berth, dig-your-own-well fallback; burakumin seam 60 ft, city exemption, collar first; city kosatsuba gates+1 and ~800 ft corridor.

### urban-features.md inbound and disagreements
Inbound: `settlements.md:23,43`; `research/urban-features.html:15,91`; `research/README.md:21`; `research/cities/capitals.html:107`; `.claude/agents/settlement-review.md:49`; `trades.py:309,464,537` (KILN / CHARCOAL / FORGE headings - the page has equivalents; the argument is now in three places); `overlap/taxonomy.py:556`.
Disagreements: **the drum tower contradicts itself on the page** (`research/urban-features.html:151`: 36/30 finding then "70 ft city / ~60 ft town" as the decision - the pre-correction figures; engine `px(36)`; `urban_fixtures.py:74` docstring says "county tier ~60-80 ft square"); `BURAKUMIN_SEAM_FT` in no `.py`; `pool/regressions/` cited seven times; L66/67/73 point to a "Historical grounding below" that moved; L14 "until re-rolled at unlock" stale twice; `tanning_yard_on_water` vs `tanning_yards_on_water`.

### urban-features.md verdict
The most duplicated (a quarter restates the page; three arguments restated a third time in `trades.py` docstrings) and still holds fifteen rulings and dead ends found nowhere else plus the operative layer for tanning yard, justice works, trade-works scoping and city wells. The what separates cleanly from the why here; what has no why: 26 per well, [0.35,0.85], ~290 px, `near=85` / ~380 px, 60 ft seam, ~800 ft gate corridor, 40 ft trough, 24 px heap, tannery clauses other than (d).
