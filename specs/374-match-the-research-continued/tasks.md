# Tasks: the rows feature 372 left open (feature 374)

**Input**: plan.md. Only the CURRENT batch's waves are task boxes (328's FR-006 form); the rest of the work list stays data
in 328's ranking and this spec.

## Occasions

- glyph-redrawn: engawa on hayakawa-magistracy - wave 112: the veranda turned round the east block's south-east corner (two or three faces, rolled), 9-12 px
- glyph-redrawn: engawa on ochiba-magistracy - wave 112: the garden-face veranda at 12 px (Ubame's the same glyph)
- layout-revised: hayakawa-magistracy - wave 113: the kitchen at 24 x 18 ft joined to the house as an ell, the covered way gone
- layout-revised: ubame-magistracy - wave 113: the kitchen at 24 x 18 ft joined to the house as an ell, the covered way gone
- layout-revised: county-magistracy-example - wave 113: the draft's kitchen abuts the house as an ell, no corridor
- glyph-redrawn: kitchen on ochiba-magistracy - wave 113: the kitchen at 24 x 18 ft
- placement-changed: notice board on kuwabata - wave 120: the board's seat a rolled knob; a bridge end offered only where a way reaches a bridge, so Kuwabata's roll now takes the center
- placement-changed: woodland commons on inashiro - wave 120: the fuel wood seated by 0077's two tiers, kept off low ground by the water below the houses
- layout-revised: hoshigaoka-shrine - wave 123: the villagers' hall at the building's east end, the dwelling west of it; the approach, arches, basin and sanctuary 22 ft east with it
- layout-revised: hayakawa-magistracy - waves 123-126: one shrine (the river kami in the Fire Dragon's hall); the servants' range on the street front, the rear yard; the forecourt inside the gate; the stable as 0108 draws it
- layout-revised: ochiba-magistracy - waves 124-126: the servants' range on the street front, the service gate through it; the rear yard; the stable as 0108 draws it
- layout-revised: ubame-magistracy - waves 124-126: the servants' common room at the gate range's west end; the barracks 24 ft deep; the stable as 0108 draws it
- layout-revised: county-magistracy-example - waves 124-126: the servants' row on the street front, storehouses and rear yard behind the house; the long-house and barracks 24 ft deep; the tax archive, cell and hearing court re-seated; the stable as 0108 draws it
- glyph-redrawn: stables on hayakawa-magistracy - wave 126: three one-ken stalls, the earth passage before them, the grooms' room (the glyph every sheet now draws; its first use)
- layout-revised: county-magistracy-example - waves 127-130: the granary and the main gate rolled (a 50 x 27 ft kura, a one-bay gate and a 40 ft gatehouse), the servants' row of four dwellings, the barracks, guest house and storehouses re-sized; the vegetable garden at the soup-greens plot with the service yard named; the shrine in its corner beside its tree, the guest house flowing below
- layout-revised: hayakawa-magistracy - wave 130: the shrine in the inner court's north-east corner beside its tree, the stippled grove gone, the torii before its south door
- layout-revised: ochiba-magistracy - waves 130-131: the shrine hall at 30 x 26 ft in the inner court's north-east corner beside its tree, the workshop below the tree, the gardens round the shrine gone
- layout-revised: ubame-magistracy - waves 130-131: the shrine in the inner court's north-east corner beside its tree, the grove and its crowns gone, the wood kami in the one hall
- layout-revised: hoshigaoka-shrine - wave 131: the sanctuary three bays wide, as its width knob rolls
- layout-revised: county-magistracy-example - waves 132-135: the one-bay gate's 8 ft frontage (a 7 ft passage), the gate posts 2 ft square, every building and flush privy a foot and a half clear of the wall's face (the barracks 23 ft deep, the guest house 40 x 42, the hearing court shifted), each well's gear and roof
- layout-revised: ochiba-magistracy - waves 132-135: the main gate's 8.5 ft frontage (a 7.5 ft passage), its posts 2 ft square, each well's gear and roof
- layout-revised: hayakawa-magistracy - waves 133-135: the gate posts 2 ft square, the tally office a foot clear of the divider, each well's gear
- layout-revised: ubame-magistracy - waves 133 and 135: the gate posts 2 ft square, each well's gear
- glyph-redrawn: well on ubame-magistracy - wave 135: a well's lifting gear over its curb, a sweep or a pulley frame (0196), its first use on a sheet
- glyph-redrawn: well on county-magistracy-example - wave 135: the gear and a roof over the drafts' wells (0196)

## Phase 1 - wave 112: the veranda at 0102's widths, its faces rolled

- Sheets redrawn (FR-002, under 328's hand-drawn-maps rule): **Hayakawa**, **Ochiba**, **Ubame**, their notes; `docs/buildings.md`;
  `pack_audit` `veranda_depths`; the glyph-check verdict keyed by element and map (FR-007).

- [x] T01 wave 112's row (FR-001, FR-002, FR-007)
      research: rendering
      verify: DONE. wave 112: verandas at 0102's 3-6 ft, the faces a rolled knob (Hayakawa two or three faces); pack_audit veranda_depths red then green; glyph-check verdicts keyed by element and map; impl-drift IN-STEP; glyph checks engawa PASS on Hayakawa and Ochiba; m:wave112-verandas

## Phase 2 - wave 113: the kitchen at 0091's size, an ell

- Sheets redrawn: **Hayakawa**, **Ochiba**, **Ubame**, their notes; `docs/buildings.md`; the kitchen band in `buildings/types.json`.

- [x] T02 wave 113's rows (FR-001, FR-002)
      research: rendering
      verify: DONE. wave 113: kitchens 24 x 18 ft (0091's measured wing, a GUESS recorded there), ells with no corridor on three sheets and the draft; kitchen band w 18-24 by h 14-18; hearth not a door; impl-drift IN-STEP; record and pop-up checks answered; glyph-check kitchen PASS; building reviews PASS (county r2, Ubame r3, Hayakawa r3); m:wave113-kitchens

## Phase 3 - wave 114: the residence's rooms as the record counts them

- Procedure and claim (FR-001): `docs/buildings.md`; Hayakawa's notes (its "~18-25 tatami rooms").

- [x] T03 wave 114's row (FR-001)
      research: rendering
      verify: DONE. wave 114: the residence zones stand for about six rooms (0091); Hayakawa's notes state its ~145-tsubo house as drawn; impl-drift IN-STEP; m:wave114-rooms

## Phase 4 - 375's carried measurements (FR-006)

- [x] T04 SC-004: key `sc003-375-first-three-tasks` over T01-T03, from `make feature-report F=374`
      research: rendering
      verify: DONE. 375 SC-003 met over T01-T03: 0 red gates from a preflight cause, 0 pages re-checked mid-check, 0 plan BLOCKs; m:sc003-375-first-three-tasks

- [x] T05 SC-005: key `sc004-375-dispatches-per-row` over T01-T03, from `make feature-report F=374`
      research: rendering
      verify: DONE. 375 SC-004: 15 dispatches per closed row (4 rows, 60 dispatches) against 372's ~10; m:sc004-375-dispatches-per-row
## Phase 5 - batch 2: the claims labeled as the record has them

- [x] T06 wave 115: the procedures' four relabels (FR-001)
      research: rendering
      verify: DONE. wave 115: the four procedure relabels and the two re-check answers recorded IN-STEP by impl-drift (b5-docs, b7-owed, b8-owed, b9-owed); 0090's GUESS sentence quote-checked and record-formatted; the pop-ups it moved checked (nakamon, court divider, inner and outer court, office hall, residence)

- [x] T07 wave 116: the hamlet's ways and hinterland labeled and claimed (FR-001)
      research: rendering
      verify: DONE. wave 116: the hamlet's ways and hinterland claims labeled and claimed (b5-ways1, b5-ways2, b6/b8/b9 re-checks); claims needing a code change filed as DRIFTED rows (found-wave118)

- [x] T08 wave 117: the settlement, waterfields, labels and interactive claims labeled and claimed (FR-001)
      research: rendering
      verify: DONE. wave 117: the settlement, waterfields and labels claims labeled and claimed (b5-rest, b6-owed, b11/b12/b13); drifts filed in found-wave118; ranking rebuilt

- [x] T09 wave 118: the CANNOT-TELL re-checks (FR-001)
      research: rendering
      verify: DONE. wave 118: the CANNOT-TELL claims re-checked with their context (b7-ct1, b7-ct2, b8-ct1, b8-ct2): 0 CANNOT-TELL left; WITH= and PAGES= added to claims-bundle; the polder/dike-pond roll a known gap and an open DRIFTED row (plan review CLEAR)

## Phase 6 - batch 3: the hamlet's code brought to the research

- [x] T10 wave 119: the hamlet's lanes - a door path's working room through a grove band, and the needle-loop speck (the `_unkinked` and `settle_shapes` returning-leg rows moved to E4, not this batch) (FR-001, FR-004)
      research: rendering
      verify: DONE. the door path's claim IN-STEP under impl-drift (re-checked 2026-10-12 after the merge's 0036 edit); its E0 row marked wave 119; gate green 2026-10-12 on the merged tree

- [x] T11 wave 120: the hamlet's ground - no wood below the houses only beside water, the board at a bridgehead (the feeder brook's width waits on its ladder question, not this batch) (FR-001, FR-004)
      research: rendering
      verify: DONE. the wood and bridgehead-board claims IN-STEP under impl-drift; the glyph-checks of the wood on Inashiro and the board on Kuwabata PASS; both E0 rows marked wave 120; gate green 2026-10-12

- [x] T12 wave 121: claims the rows name - the kura's west annex re-checked; the belt's holes, the clump window and the south band worded to the code and re-checked (FR-001)
      research: rendering
      verify: DONE. the kura west annex, belt holes, clump window and south band claims re-checked IN-STEP (claims-owed reports none); kura row marked wave 121; gate green 2026-10-12

## Phase 7 - batch 4: the held rows answered, the country shrine's roof and the magistracies' service buildings

- [x] T13 wave 122: the two held rows answered - the door band closed on the GM's ruling; 0219's drawing page reworded to the share as a countryside rate, `fixture_quota` re-checked (FR-001, FR-004)
      research: rendering
      verify: DONE. DONE. wave 122: the door band closed on the GM's ruling (overrides.json); 0219's drawing page reworded to the share as a countryside rate, quote-check, record-format and translation-check answered (0219's round 3 accepted by the round arbiter); fixture_quota re-checked IN-STEP; both rows marked wave 122

- [x] T14 wave 123: Hoshigaoka's one roof with the hall at the arch end; Hayakawa's two shrines cited to 0218 (FR-001)
      research: rendering
      verify: DONE. DONE. wave 123: Hoshigaoka's hall at the east end of its one roof (hall_at_an_end, red first); Hayakawa one shrine, the river kami in its hall (one_compound_shrine, red first), the torii 8 ft before its door (0220); building reviews and the arbiter's close (ask:batch4-review-close); rows marked wave 123

- [x] T15 wave 124: servants on the street front, never a rear rowhouse; the second rank for stores only (FR-001)
      research: rendering
      verify: DONE. DONE. wave 124: servants on the street front, never a rear rowhouse, the second rank for stores; by kind (R4-1): menservants in the range, grooms in the stable's room (0108), maids under the main roof (a GUESS on 0115's Aizu house); impl-drift IN-STEP; pop-ups checked; rows marked wave 124

- [x] T16 wave 125: the barracks and the county staff rowhouse at most 24 ft deep; the forecourt inside Hayakawa's gate (FR-001)
      research: rendering
      verify: DONE. DONE. wave 125: the barracks and the staff long-house at most 24 ft deep, divided into dwellings a door each (0097); the forecourt inside Hayakawa's gate; impl-drift IN-STEP; building reviews verified; rows marked wave 125

- [x] T17 wave 126: the stable as 0108 draws it - one-ken stalls, the earth passage and the grooms' room - on every magistracy sheet (FR-001)
      research: rendering
      verify: DONE. DONE. wave 126: the stable as 0108 draws it on every magistracy sheet (stall_width, red first); glyph-check stables PASS twice; impl-drift IN-STEP; rows marked wave 126

- [x] T18 batch 4's review findings fixed once and verified: the servants by kind, the county postern open, the storehouse doors, the barracks divided, the hand sheets' findings, the size bands (plan R4-1 to R4-7) (FR-001)
      research: rendering
      verify: DONE. DONE. batch 4's review findings (R4-1 to R4-7): every finding fixed and recorded (measurements b4-*) or accepted or filed (found.jsonl); postern_approach red first; claims re-checked; the round arbiter closed the reviews (ask:batch4-review-close: accept)

## Phase 8 - batch 5: the county draft's filed rows, its stores and gate as knobs, the shrine beside its tree

- [x] T19 wave 127: the county draft's small rows - the practice ground comment, the inner entrance at the kitchen end (0107), the middle gate's width, the servants' row form marked (FR-001)
      research: rendering
      verify: DONE. wave 127 done: the practice ground comment, the inner entrance at the kitchen end (in the inner rooms since batch 5's review), the middle gate's 6 ft agreed, the servants' row form marked (m:batch5-open-rows)

- [x] T20 wave 128: the county granary (0098's form rolled, its size in the band) and gate (0093's form rolled, the gatehouse of its own) (FR-001)
      research: rendering
      verify: DONE. wave 128 done: the granary rolled earth-walled kura (50 x 27 ft, no posts - the plan's takakura prediction was wrong, the roll governs), the main gate one-bay (8 ft) with its 40 ft gatehouse, the takakura glyph for the other form; reviews passed

- [x] T21 wave 129: the county vegetable garden's form (0109's knob rolled, the room deciding) (FR-001)
      research: rendering
      verify: DONE. wave 129 done: the soup-greens plot at ~1,076 sq ft, its site rolled among the sites the sun and the room leave (west), the service yard named; garden_sun OK

- [x] T22 wave 130: every compound shrine in a corner beside its tree (0218), on the county draft and the three magistracy sheets (FR-001)
      research: rendering
      verify: DONE. wave 130 done: every compound shrine in a corner beside its tree - county placer (tree_ft, _shrine_tree), Hayakawa, Ochiba, Ubame; pack_audit shrine_tree red first; building-review, glyph-check and size-audit passed or accepted by the round arbiter

- [x] T23 wave 131: the shrine hall's ceiling (Ochiba), the second kami as a rolled knob (Ubame), the sanctuary's width rolled (Hoshigaoka) (FR-001)
      research: rendering
      verify: DONE. wave 131 done: Ochiba's hall 30 x 26 ft, Ubame's wood kami in the one hall, Hoshigaoka's sanctuary three bays (its roll recorded); reviews passed or accepted

- [x] T24 wave 132: the one-bay gate's ~6-8.5 ft its frontage, the passage less the posts (0093), the county draft and the hand sheets (FR-001)
      research: rendering
      verify: DONE. county 8 ft frontage / 7 ft passage and Ochiba 8.5 / 7.5 ft drawn and audited (gate_widths, passage_blockers OK); claims IN-STEP; building-reviews PASS (county, Ochiba round 3 accepted by the arbiter); record checks on 0093 answered

- [x] T25 wave 133: the main gate's posts ~2 ft square on the three magistracy sheets (FR-001)
      research: rendering
      verify: DONE. main gate posts 2 ft square on the three hand sheets and every gate on the drafts; claim relabeled CONVENTION and IN-STEP; building-reviews PASS; the lesser hand-sheet posts filed as a row

- [x] T26 wave 134: a structure a foot or two clear of the wall's face (0092), structures_on_walls, the sheets and the emitter (FR-001)
      research: rendering
      verify: DONE. every wall-hugging structure 1.5 ft off the face (structures_on_walls with the clearance), the hatch reach 3 ft with a test red at the old reach; county claims IN-STEP; building-reviews PASS

- [x] T27 wave 135: a well's lifting gear a rolled knob (0196), its glyph on every sheet's wells (FR-001)
      research: rendering
      verify: DONE. every well draws its rolled gear and roof (well_gear check, proven red first), indoor wells a beam pulley (W135-2), the roof an outline on posts; glyph-checks PASS on county and Ubame round 2; 0196 record checks and the well pop-up answered; claims IN-STEP

- [x] T28 wave 136: a farmstead's own grave, a knob (0236), drawn at the plot's scale on the hamlets that roll it (FR-001)
      research: rendering
      verify: DONE. household grave drawn on Kuwabata (5 graves), glyph-check PASS, gate green, claims none owed, household-grave pop-up through form/research/depiction

- [x] T29 wave 137: the standing rack forms by their period (0016) - a search for a premodern date; drawn if dated, recorded undrawn if not (FR-001)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. two search passes (archive first, Japanese and Chinese) found no premodern date for Niigata's living-tree posts or Ehime's year-round racks; recorded undrawn on 0016's drawing page with an absence note; source-reader 2 READ, quote-check round 3 clean, translation-check FAITHFUL 2; no new source and no number reaches a map, so the registry's existing write-ups stand for applicability

- [x] T30 wave 138: the lane along the water, the fifth lane shape (0031), where water runs along the cluster (FR-001)
      research: rendering
      verify: DONE. lane_skeleton_by_water rolls the waterside lane among five where a brook runs along a flank; web tests cover water_along_side and oriented_skeleton; gate green

- [x] T31 wave 139: the chessboard of ponds rolled beside the mosaic (0019, Qu Dajun 1678) (FR-001)
      research: rendering
      verify: DONE. POND_LAYOUTS rolls mosaic two in three, grid one in three (measured on the chessboard rolls, measurements.json w139-chessboard-rolls); pop-ups for both layouts checked; gate green

## Batch 8 - the attested field forms rolled, the web lane's room and its gap off the crop

- [x] T32 wave 140: a dike-pond hamlet with no grow-out pond in a household's reach keeps no sty (0025) (FR-001)
      research: rendering
      verify: DONE. the floor-of-one refusal dropped per 0025; refused seeds 3, 6, 7 green; seat_faults records why none drawn; tests pass; impl-drift IN-STEP; gate green

- [ ] T33 wave 141: the polder and the dike-pond rolled beside the valley fan once their rolls are green (0019, 0020) (FR-001) [lands-open]
      research: rendering

- [x] T34 wave 142: the web lane's no-build room, 9 ft from its middle (0246) (FR-001)
      research: rendering
      verify: DONE. WEB_CLEARANCE 9 ft half-width (0246's 18 ft room); cohort 15/16 as at HEAD, then 16/16 with wave 143; pool hamlets byte-identical; impl-drift IN-STEP; gate green

- [x] T35 wave 143: the web lane off the crop by its half-tread, off the toe and marsh by its own gap (0081) (FR-001)
      research: rendering
      verify: DONE. the crop at half the widest tread (3 ft, Gapped), the toe and marsh at 8 ft (UNRESEARCHED), every kept lattice step asked of the crop (crosses_the_crop, tested); cohort 16/16 (Audit-10 reached); impl-drift rounds 1-4 IN-STEP; gate green

## Batch 9 - the rolled wood on its sheet

- [x] T37 wave 145: a hamlet's rolled wood drawn on its sheet (0077) (FR-001)
      research: rendering
      verify: DONE. every open seat inside the frame stands on the houses' side on all 7 off-sheet rolls (m:w145-offsheet-why); D11's convention recorded on 0077's drawing page with its grounds note; quote-check, record-format, the woodland-commons depiction (arbiter round 3, its EDIT applied) answered; 6 claims IN-STEP; page-check green; bookends band 0

## Batch 10 - a grove farm's way in kept open

- [x] T38 wave 146: a grove farm's way in kept clear of its own fixtures; door paths and street joins close no sliver (0036) (FR-001)
      research: rendering
      verify: DONE. grove farms' fixtures keep off the way in and the door's room; door paths and street joins close no sliver; seed-pinned soak tests red at HEAD (2 failed), green now (polder 12, dike-pond 4); polder 4 waived by the arbiter and pinned; cohort 16/16, valley 20/20, dike-pond 12/12 (m:w146-rolls); 60 claims IN-STEP; gate green

## Batch 11 - the floodplain meadow

- [x] T39 wave 147: the grass ground's form from the land; the floodplain meadow on a river-flat map (0078) (FR-001)
      research: rendering
      verify: DONE. a flood-ground map's margins drawn as floodplain meadow (pasture, no pine) from the land (grass_ground), recorded as meta.grass_ground; Kuwabata's meadow glyph-check PASS; the pop-up through form, research and depiction; 29 claims checked, the paddy-plot gap left DRIFTED (rows 775, 911 open by the plan review); gate green; bookends band 0

## Standing - the ranking's remaining rows

- [ ] T99 Batches 2 on: the ranking's remaining open rows, wave by wave in ranking order, each batch's tasks added here as it starts (plan, "Lands open") [lands-open]
      research: rendering

- [ ] GM review (make gm-reviewed F=374) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
