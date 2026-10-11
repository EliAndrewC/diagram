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

- [ ] T10 wave 119: the hamlet's lanes - a door path's working room through a grove band, and the needle-loop speck (the `_unkinked` and `settle_shapes` returning-leg rows moved to E4, not this batch) (FR-001, FR-004)
      research: rendering

- [ ] T11 wave 120: the hamlet's ground - no wood below the houses only beside water, the board at a bridgehead (the feeder brook's width waits on its ladder question, not this batch) (FR-001, FR-004)
      research: rendering

- [ ] T12 wave 121: claims the rows name - the kura's west annex re-checked; the belt's holes, the clump window and the south band worded to the code and re-checked (FR-001)
      research: rendering

## Standing - the ranking's remaining rows

- [ ] T99 Batches 2 on: the ranking's remaining open rows, wave by wave in ranking order, each batch's tasks added here as it starts (plan, "Lands open") [lands-open]
      research: rendering

- [ ] GM review (make gm-reviewed F=374) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
