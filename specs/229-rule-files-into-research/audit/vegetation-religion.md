# Audit: `settlements/vegetation.md` (63.9 KB) against `research/vegetation.html`; `settlements/religion-and-death.md` (59.7 KB) against `research/religion-and-death.html`

Independent Opus reader, 2026-09-12. Classes as in `homesteads.md`.

## vegetation.md

Share by unit (46): A ~22%, B ~46%, C ~7%, D ~20%, E ~4%; stale check names on ~22% of units. By bytes the bullet body (L11-84) is 84% (A and B); the four prose sections L86-217 are 15% and entirely D.

Units (line: class; engine / anchor):
- 11 Pastures and large terrain: B/F; `edge_features_run_off_map` NOT FOUND.
- 12 Village windbreak - the fengshui forest: A; `#the-fengshui-forest---real-scale-and-why-ours-is-honest`.
- 13 Trees OFF the paths: B; `stands.py` `_corridor_buffers`; `groves_clear_of_lanes` live.
- 14 BELT out of the AFTERNOON sun 50 ft, 75 ft declined: D+B (GM 2026-08-25); `homesteads/stages.py:51` `WEST_SUN_FT`.
- 15 Trees out of SOUTHERN SUN of yards/gardens: B/F; rule live, name retired.
- 16 Clump ABUTS never OVERLAPS (GM 2026-07 "directly next to is OK"; 0.35x dead end): B+D; `grove_clumps_clear_of_structures`.
- 17 ORGANIC and EMBRACING: A. 18 Why communal: A. 19-22 Three parts by role: A+B (`land/cover.py`, `hinterland/belt.py`).
- 24 BELT SCALES canopy >= 0.40x roofs, 80-120 ft deep: B+D; `belt.py:146`.
- 25-46 A GAP IS ACCEPTABLE + MEASURED, KUWABATA IS NOT THE CROP CASE: D.
- 48 Neighboring FOREST counts when it shelters (150 px): B; `belt.py`.
- 49 FAR side is fuel-and-fodder COMMONS (south-China degraded hills): B+D; `commons_beyond_the_windbreak` NOT FOUND.
- 50 `commons(role="grazing")` ring, 12% bare: B; `hamletgen/frame.py`.
- 51 DRAW ORDER for margin fill: C. 52-53 scrub/reeds under road, off footprints: B; `cover.py`.
- 54 URBAN-CLEARANCE HALO 30/20/8 ft: B+E; `land/nearring.py:75`; `scrub_clear_of_urban_fabric` live.
- 55 off open WATER: A. 56 Scrub OFF the crops 6 ft: A; `cover.py:119` `_CROP_MARGIN_FT`.
- 57 WELLHEAD clean draw-point: B/F; `homesteads/wells.py`.
- 58-62 Slope by consequence; REJECTION of shaded relief: B+D.
- 63 Hinterland catena `hinterland()`: B; `cover.py:332`. 64 Interior fill: B. 65 Three commons looks: B. 66 Placement mechanics: C+B.
- 67 Scrub NEVER into a marsh: A+D (three review rounds, final grass-only form); `hinterland/stages.py:44`.
- 68 Woodland not over crops (CLEAR ~14 px + SHADE): B/F; `hinterland/parcels.py`. 69 Woodland DISTINCT from grove: B/F.
- 70 Real FOREST (Moritono, `skip_sides`): E+B; `cover.py:332`.
- 71-72 FOREST as INDIVIDUAL TREES: A; `#forest-density-and-crown-size`. 73 Edge made of TREES: B; `woods.py:109`.
- 74 NO TREE ON A ROOF OR A WELLHEAD (GM 2026-07-25): B+D; `overlap/matrix.py` `CANOPY_STRUCT_KEYS`.
- 75 PER CROWN: B. 76 Trees LAST: B. 77 Reads DRAWN crowns, `CANOPY_PAD` 0.6: B; `fixtures.py:170`.
- 78 Canvas-filling wood REVEALED 110 ft (GM 2026-07-25): B+D/F; `overlap/matrix.py` `FOREST_REVEAL_FT`.
- 79 NOT frame-setting on the axis it RUNS ALONG (Moritono 157 px): B+D; `forest_frame_span`.
- 80 NO SCRUB UNDER A VILLAGE WOOD: A; `#does-scrub-stand-under-a-village-wood-...`.
- 81 COPPICE PARCEL IRREGULAR RING: A; `parcels.py:535`.
- 82 BAMBOO IS A STAND: A+B/F; `hinterland/bamboo.py`; `consts.py:718`.
- 84 No canopy tree under another's crown: A; `cover.py:219`.
- 86-132 A shelter belt is not a RING, and its open side is not a gap: D.
- 134-169 The GM's ruling on the hook, and why no knob was built: D.
- 172-196 A belt runs off the page: D; `stands.py:422` `_column_in_belt`.
- 198-217 Why the continuity check is asymmetric on purpose: D.

### vegetation.md D items
1. **A shelter belt is not a RING** (GM 2026-08-29 ruling quoted): absent flank (historical) vs hole in a planted run (a defect; Purdue NCR-191 constriction); the 30 ft threshold relabeled a rendering convention; the unbuilt `belt_enclosure` knob (`full_ring` | `windward_flanks`, the Izumo tsuijimatsu) declined as new scope.
2. **The GM's ruling on the hook** (GM 2026-08-29): the NW hook kept and the knob NOT built - "it communicates that wind tends to blow from the northwest to the southeast"; the belt's shape is communicative; measured arcs Inashiro 102, Kashikawa 146, Kuwabata 97, Mizuguchi 136, Sawada 129 deg. The only recorded case where two supportable answers were answered with a ruling, with the reason.
3. **A belt runs off the page** (2026-08-29): continuity window widened to the belt POLYGON; the "gaps" were wholly off-page on two maps; extending the planting to the polygon ends tried, bought one clump, reverted.
4. **Why the continuity check is asymmetric** (2026-08-29): the symmetric version fails Mizuguchi at a 60 ft run where a homestead's sun corridors rightly refuse canopy; closing it costs a second generator inside the gate; the reopen condition named.
5. 75 ft west-sun lane priced and declined (GM 2026-08-25, feature 133 T10).
6. Shaded relief REJECTED: reads as a light source; slope is water + steep-only terraces + pictorial hills.
7. "Directly next to is OK" and the 0.35xclump failed number (Hikari).
8. Marsh/scrub final form after three rounds (GM 2026-08-26 "it looks like it is still overlapping!"): grass alone grades in.
9. South-China degraded commons finding: past the grove the ground is open scrub, no fill, no outline.

### vegetation.md B items not encoded
`edge_features_run_off_map`; `commons_beyond_the_windbreak` (grove -> commons toposequence and the grazing/pasture/woodland exemptions); `village_groves_clear_of_paddies`, `yards_unshaded_by_groves`, `gardens_unshaded_by_neighbors`, `village_trees_unshade_yards_and_gardens`, `groves_where_possible` (geometry live in `stands.py`/`keepouts.py`, named guarantees gone); `bamboo_declared_and_drawn`, `bamboo_stands_legible`, `bamboo_stands_clear_of_paddies`; 80-120 ft belt depth and the set-the-outline-back rule; `_BELT_MAX_GAP_FT` is really `_BELT_GAP_FT = 30.0` at `homestead_parts/_helpers.py:11` (grounding at :13-17).

### vegetation.md inbound and disagreements
Inbound: `settlements.md:17,40`; `research/README.md:22`; `research/vegetation.html:16,141` (comments); `SKILL.md:265` (page has density, not reveal/frame-span); `_helpers.py:13`, `keepouts.py:102`, `stands.py:157` (quotes "the copse, not the belt, fills the inner gaps" - page has no equivalent), `hinterland/parcels.py:339,401`; `tests/settlement/test_homestead_parts.py:165`; `future-work/farming-communities.md:72,1197`; `inashiro.notes.md:1040`; `interactive/classes/greenery.py:103` Entry tag - INERT at runtime (`_ENTRY_FILE` matches only research html; 'Village windbreak' matches no page heading; the shipped Inashiro copse class carries one question). What the md has that the page lacks: the three-role decomposition (windbreak / water_mouth / copse) with siting logic and "the village is LEAFY, not bare".
Disagreements: bamboo legibility floor md 20 ft, page 20 ft, engine `BAMBOO_LEGIBLE_FT = 14.0` (`hinterland/bamboo.py:24`, short axis); belt-scale "~1,800 sq ft per household" anchor exists only in the md (page: ~1-2 ha, upper half of HK band); coppice cycle 15-20 on the page vs "10-30 year" in the `WoodlandCommons` docstring; `tests/check_village/` and `check_village.py` cited at 57, 66, 68, 69, 78.

### vegetation.md verdict
Lost on deletion: the four prose sections (a GM ruling that overrides constitution XII's knob rule; an earned-but-unbuilt knob; two measurements that killed two repairs; an accepted limitation priced), nine embedded decision records, ten prose-only rules, and engine comments that quote it. Move the four sections wholesale as two new entries ("Does a shelter belt wrap the settlement?", "Where does the continuity check stop looking?"); embedded records into their entries or the point of change; fix the ten stale names and the 20-vs-14; fix the `greenery.py:103` tag.

## religion-and-death.md

Framing: the hamlet generator draws NO shrine, torii, graveyard, cremation ground, ossuary or mausoleum (`plan.py:109` refuses a village-sized spec for that reason; the only fixture is a farmstead kamidana/hokora at 0.03-0.08 in `homesteads/fixtures.py`). Essentially the entire file is class E for the scripted tier; the class below is the secondary class.

Units (line: class; engine / anchor):
- 11 Village/hamlet shrine footprint 275/490/600 m² (GM 2026-07-21 Hikari): E+B; `village_shrine_footprint_within_norms` NOT FOUND.
- 12 Religious building scales with the settlement: E+B; `water_ways/focal.py` `religious_matches_scale`.
- 13 A town has TWO monasteries; seven clan patron pairs: E+B; `overlap/taxonomy.py:707` `CLAN_FORTUNES`.
- 14-15 City temples count, four justifications, Fox reframing: E+A; `taxonomy.py:705` `TEMPLE_EXCEPTIONS`; `#many-modest-temples-per-walled-city-is-the-historical-norm`.
- 16 Clergy HOUSING inverts: E+A+B; `citybudget.py:313`; `#temples-as-economic-institutions-with-hereditary-householder-clergy`.
- 17 GRAVEYARD ceiling does NOT scale: E+A; `#the-graveyard-ceiling-does-not-scale-with-temple-count`.
- 18 Size - the deliberate liberty: A; `#city-temple-size-the-deliberate-l7r-liberty`.
- 19 Initiates living out (~2x; "altar boy tier"): E+D.
- 20 BLANK-COURT clergy compound (GM 2026-07-24, supersedes draw-no-monk-houses): E+D; `shrines_wells/shrines.py`.
- 21-26 Temple NEIGHBORHOOD is LAY households (GM 2026-07-20: no religious-goods shop; four trades; placement not icon): E+D.
- 27 Neighborhood SIZE ~40-80 lay houses, 1-2 per monk, pilgrimage 10:1: E+B; NOT FOUND.
- 28 Small shrines at SPECIFIC locations: E+D. 29 Festival rhythm miaohui: E+D.
- 30 RETIRED `monastery_torii_scale_with_space` (2026-07-24): F/D.
- 31 Main shrine placement, torii numerology, pitch cap, threshold (GM 2026-07-27 quote), captions, walls: E+B+A+D; `shrines.py:201-207`, `castle_civic.py:759`, `_geom/labels.py:65`; `#torii-spacing---two-regimes-and-nothing-in-between`.
- 32 Shrine HALL BESIDE a lane: B; `shrine_halls_clear_of_lanes` live.
- 33 Torii 1/3/7 numerology + full re-roll (2026-07-23): A+B+D; `_knobs.py:380` `TORII_WEIGHTS`; `#torii-are-votive-donations---the-count-records-patronage`.
- 35 DONATION ROWS designated-site special case (GM 2026-07-25: Shinden Togashi, Amaterasu, Ki Rin): D; `shrines.py:154` `torii_outlier`.
- 36 A WELL BESIDE a shrine: B+C; `wells.py:283` `shrine_well`.
- 37 Shrine + torii NESTLE in a CLEARING 0.90xclump: B; `stands.py:131`.
- 38 Every settlement above a hamlet buries its DEAD: E; `civic_grounds/funerary.py`.
- 39 Temple graveyards; CHURCHYARD rule; sizing: E+B+D; NOT FOUND.
- 40 Common ground ORGANIC, Japan-style: A; `funerary.py:32` `parish`; `#burial-ground-shape---japan-organic-china-surveyed`.
- 41 Clan mausoleum + ward-wall yield: E+B; `structures/compounds.py:106`.
- 42 Cremation ground four siting rules: E+B; all NOT FOUND. 43 Pauper ossuary: E+B; `taxonomy.py:230` draws it.
- 44 Scale schedule city 2-4 / town 1-2 / village 1: E+B; NOT FOUND. 45 Walled: inside AND outside, 1.3x: E+B; NOT FOUND.
- 46 Every solid feature first-class for overlap: F+B; registry moved to `l7r/diagram/overlap/`.
- 47 Burial grounds set back from water 75/130/140 px, 50 px paddy: E+B; `water_setback` NOT FOUND (residue `land/nearring.py:241`).
- 48 NON-parish graveyard; bunkotsu not drawn: E+B; `funerary.py:32`.
- 49 Gates, walls and funerary features TO SCALE + the anchors memo: E+D; four `*_to_scale` names NOT FOUND.
- 50 District catchment ~800-person district (GM 2026-07-23, researched): D; `BURIAL_AC_BAND` NOT FOUND; CITED by `research/archetypes.html:165`.
- 51 Swept ground around sacred + funerary: B; `core.py`, `cover.py` `_clear_ground`, `reserve_clearing`; `scatter_respects_swept_clearings` live.
- 52 Verge outline ORGANIC never the padded rectangle (GM 2026-07-23): D+B.
- 53 What the research found - swept ground, China-first: D. 54 The decision 58/30/30 px collars: B. 55 chinju no mori nuance: D.
- 56 ORDERING GOTCHA: C. 57 Village GRAVEYARD is the shrine's CHURCHYARD; two deferred slices: E+B+D.
- 58 Village SHRINE at the WATER-MOUTH (土地庙): E+D. 59 Funerary geography summary: E+D. 60 Religious building by scale (dup of 12): E+B.

Share by unit: A ~14%, B ~32%, C ~7%, D ~32%, E ~9% pure - E riding on ~80% of every unit. F: 2 whole units and ~20 dead names.

### religion-and-death.md D items
1. **District catchment** (L50, GM asked 2026-07-23; researched + source-verified): Edo Japan buried PER-SETTLEMENT (shuraku bochi / minashi bochi) while the RITUAL center was central (danka; ryobosei); Ming/Qing scattered family graves (Buck ~2% of farm area) with communal grounds only as pauper yizhong; two reasons the one-central-ground convention is MORE defensible in Rokugan (cremate-then-inter canon; a hamlet's patch 750-2,450 sq ft is below map resolution); ~800 x 25-30/1,000/yr x 30-yr reuse = 600-720 urn plots x 10-20 sq ft = **~0.15-0.30 acre**; band re-anchored [0.04,0.30] -> [0.12,0.38]. `research/archetypes.html:165` cites it; `research/religion-and-death.html` does not contain it.
2. **Swept ground** (L53-55, GM asked 2026-07-19): keidai swept forecourt; sando kept clear; graves PARTIAL ("clear AT the graves, wild BETWEEN them"); collars ~58 px shrine / ~30 px torii footing / ~30 px grave; the chinju no mori nuance - the keep-out affects ONLY loose scatter, never the grove or placement.
3. **Verge outline ORGANIC** (GM 2026-07-23 "such clearage rarely conforms to precise geometric shapes"); outward lobes rejected (a collar is a maintenance CLAIM; a lobe newly overlaps predating cover; first lobed draft flipped a check on Ueda); bays-only is a subset of the old rectangle.
4. **Gates, walls and funerary features TO SCALE** (GM 2026-07-19) with the size memo: samurai gate 9-12 ft, yamen gatehouse 18-24 ft (old +/-34 px drew 204 ft); walls 1.5-2 ft; sanmai 30-80 ft village/town to 80-160 ft city (Yoyogi ~900 tsubo); muenzuka 10-30 ft (Mimizuka ~50 ft base); retired legibility license (~40 ft glyph, 9 px floor = 54 ft; tightened 2026-07-21 to [8, 32] ft). Sources named: Edo hatamoto yashiki schedules, the Fukui sanmai survey, Shinpen Musashi Fudoki-ko, Tanigawa JJRS 1992, Chinese Deathscape.
5. **Temple NEIGHBORHOOD is LAY households** (GM 2026-07-20): amulets/charms/incense were temple-direct sales (temple accounts book "annual oil-lamp and incense income"; omamori bestowed for an offering) - NO religious-goods shop; food and drink, meibutsu, funeral trades by the GRAVEYARD (joss-paper makers), service trades and temple-artisan families; the story is in placement, never the icon.
6. **Village SHRINE at the WATER-MOUTH** (土地庙 "near the entrance, in the most strategic feng-shui location" = 水口); 30x24 px vs `shrine_hall` 120x82; no label.
7. **DONATION ROWS designated-site special case** (GM 2026-07-25): Fushimi senbon is NOT the ordinary sando; Shinden Togashi, Temple of Amaterasu, Ki Rin Shrine; `torii_outlier=True`.
8. **BLANK-COURT clergy compound** (GM 2026-07-24): the big rectangle IS the temple (interior is Mode A); clergy implied population; married adepts 2-3 homes identical to a laborer house.
9. **Torii avenue THRESHOLD** (GM 2026-07-27 "the distance from the front of the temple should be the same as the distance between each torii arch"); Tango Bishamon 139 ft, Nagahara Ebisu 120 ft, Minami 44-93 ft; strict ORDER not a score for the hall caption (scoring blind flipped Bishamon's caption onto a fire tower not yet drawn).
10. **RETIRED `monastery_torii_scale_with_space`** (2026-07-24): predated the roll table, wrongly banned 3.
11. Festival rhythm (L29) and initiates living out (L19).

### religion-and-death.md B items not encoded
Nearly every named check (~30; listed in the reader's full report) - FOUND only: `religious_matches_scale`, `torii_count_canonical`, `torii_match_roll`, `shrine_halls_clear_of_lanes`, `torii_clear_of_walls`, `torii_clear_of_halls_towers_ring`, `religious_clear_of_ring_and_towers`, `no_structure_on_torii`, `scatter_respects_swept_clearings`, `every_feature_classified_for_overlap`. Prose-only numbers: 275/490/600 m² shrine band; 40-80 lay houses, 1-2 per monk, 10:1 pilgrimage; water set-backs 75/130/140 px, 50 px paddy; burial acre bands village 0.15-0.30, town 0.25-0.75, city 0.75-2, Chinese full-body 4-6x; 1.3x exterior cemetery; 230/250 px precinct reaches; 170 px monk-house reach; ossuary [8,32] ft; ~400 px temple proximity, ~40 px tolerance for crematory rules; 58/30/30 px collars. Encoded: `CLAN_FORTUNES` (seven pairs match), `TEMPLE_EXCEPTIONS` (four justifications).

### religion-and-death.md inbound and disagreements
Inbound: `settlements.md:18,41` (page lacks District catchment and Swept ground); `research/README.md:19`; `research/religion-and-death.html:15,16,47`; **`research/archetypes.html:165`** (cites the district-catchment finding as its grounding - load-bearing for the RECORD); `overlap/taxonomy.py:696`; `settlements/cities/sizing.md:96`. No `Entry:` tag names it.
Disagreements: `check_village.py` described as live (L46); ~30 checks described as gating; four near-duplicate tier-schedule statements (L11/12/38/44/60). No numeric disagreement with the page because the two barely overlap.

### religion-and-death.md verdict
Nearly the opposite of vegetation: only ~14% restated; ~32% operative rules the engine holds nowhere; ~32% decision record. Nothing is hamlet-tier; the whole file is the prose inheritance the village/town/city generators need. Lift the eleven D items onto the page (District catchment FIRST, another page cites it); sweep the ~30 dead names; collapse the four tier-schedule duplicates; the rest is the unscripted-tier specification.
