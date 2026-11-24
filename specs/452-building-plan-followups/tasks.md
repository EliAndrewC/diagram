# Tasks - feature 452, the building-plan follow-ups

The 17 building-plan (Mode A) follow-ups moved out of feature 449 at the GM's request of 2026-11-24 (`request.md`), so 449 can
close on its port. Each of T001-T017 keeps its full text and evidence from `specs/449-rust-codebase/tasks.md` and names its 449 task; T18-T22 name their 449 found row and T23 the audit that found it. A task
about how a place was built or lived in is `research: physical` with its five boxes (a box the record already answers is ticked
with its pointer); a claim, doc or note restated to a page the record already holds is `research: rendering`.

## Occasions

- none: filed 2026-11-24, nothing drawn yet; a task that redraws a sheet adds its own occasion line, naming itself, when it lands
- none: T007 T008 T009 T010 T011 T012 T013 T014 T015 T21 T23 - doc claims, a doc procedure bullet, pop-up Guesses text and sheet notes restated to their pages and sheets; no sheet's drawing, placement or glyph changes, and no research page (spec-fidelity 2026-11-24: T012 and T013 are restatements).

## Tasks

### Research questions answered into the record (FR-001)

- [ ] T001 from 449 T386: a research pass on how a magistracy's menservants lodged - as families or as single men, and how many - so the county example's servants' row states its headcount and lodges no wider a man than the junior samurai (building-review 2026-11-23 re-review of county-magistracy-example, Q1: about 3-6 men in 912 sq ft, roughly 150-300 sq ft a man against the junior retainers' 96)
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [ ] T002 from 449 T387: a research pass on whether a hearing court (shirasu) was screened from the yard, or whether lodgings could face it, since three of the county example's junior retainers' doors open behind the court's open south side (building-review 2026-11-23 re-review of county-magistracy-example, Q2; 0099 and 0097 silent)
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [ ] T003 from 449 T389: a research pass on how long a junior officials' rowhouse or hut ran, since the county example's junior retainers' quarters are 48 x 24 ft (2:1) where the retainers'-quarters pop-up gives rowhouses about 80 to 145 ft long and 0097 'never a square or squat block' (glyph-check 2026-11-23 of retainers-quarters on county-magistracy-example, F3): a measured one under about 60 ft lowers the pop-up's floor, else 0097's drawing page labels the length a GUESS
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed

### The stables drawn to the source (FR-002)

- [ ] T004 from 449 T404: the stables' stalls have no rear doors - JAANUS umaya gives each warrior-class stall a pair of rear swing doors (shirido) for mucking out; the county's stalls back onto the south wall about 3 ft off with none drawn (county building-review 2026-11-23 N2, outside the T388 change)
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [ ] T005 from 449 T405: 0108's page takes JAANUS's tozamurai depth, then the stables follow it (found 2026-11-23 by 449 T401's search pass, keys t401-umaya and t401-umaya-b: JAANUS umaya, 'It was 2 bays in cross section with a peripheral veranda', the one depth any source gives for the warrior's stable's grooms' room, is not on research/questions/0108-stables-umaya.html, whose note quotes the passage's neighbors only): a page session adds it, then the generated stables' grooms' room (rust/mode_a/src/compound/emit.rs STABLE_DEPTHS, a GUESS 9 ft) and the hand sheets' (Ochiba's stables draw 9 ft) are re-drawn to it with room first (the county's and round trip's stables deepened, inside the stables band 10-30 ft), and the undrawn veranda ruled; visible effect: a reader who knows the form sees a grooms' room a bay and a half deep where the record gives two
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed

### Ubame's kitchen-garden bed (FR-003)

- [ ] T006 from 449 T408: Ubame's kitchen-garden bed stands 1.3 ft off Koharu's veranda and off the writing pavilion, so the household's way from its rooms to the household door runs round the pavilion, about 104 ft (building-review 2026-11-23 of ubame-magistracy, O1, outside the T375 change; the bed's seat a feature 283 knob)
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed

### Claims and docs restated to their pages (FR-004)

- [ ] T007 from 449 T374: docs/buildings.md's Side gate bullet says a cart gate is named as its own form "at a Kochi domain residence of about 1790-1800" - the Kochi paper's 車御門 is an OCR misreading of 裏御門 (449 T361 brief B, the paper's page image, 2026-11-23); restate the clause to Himeji's Kurumamon alone, as research/questions/0082-moving-goods-carts-packhorses-and-river-landings-kashi.drawing.html now does - visible effect: the procedure cites a cart gate no source has
      research: rendering
- [ ] T008 from 449 T390: docs/building-programs.md's two out-of-change rows restated to the record - the inner_garden row's why takes the pond as the office's form where 0103's section 141 rolls a pond or a dry garden from the seed, and the latrine row's why gives a privy 5 ft square as the smallest farm privy counted where 0101's section 47 says no source we read gives a privy's size (found by 449 T351's claims round)
      research: rendering
- [ ] T009 from 449 T393: the county example's junior retainers' quarters and cell re-cited to the record (449 T372's last clause, deferred from the T371 bundle: pool/magistracies is the T383 bundle's live files) - in county-magistracy-example.compound.json, the research string 'the junior retainers' quarters' cites research/questions/0331-where-an-offices-staff-lived.html (Sakai and Sayama, the seat) and research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html (its bullets 'Where does a county magistrate's office on our maps lodge its staff?' and 'How big is a dwelling of the junior retainers' quarters?') in place of 'research-pass 2026-11-23 - not yet on a page' and '(research-pass 2026-11-23: ...)'; the string 'the cell joined to the junior rowhouse's east end' cites research/questions/0096-holding-cells-agariya-and-roya.drawing.html ('Where does the county plan put its cell?', absence how-our-maps-draw-holding-cells) in place of 'research-pass 2026-11-23 found no source ...'; and county-magistracy-example.notes.md lines 104, 109, 152 and 156 likewise (observed 2026-11-23, method: grep for 'research-pass 2026-11-2' in both files); visible effect: none on a map, the county sheet's junior rowhouse and cell claims cite passes no reader can open; research: rendering
      research: rendering
- [ ] T010 from 449 T396: three claims in docs/building-programs.md and docs/buildings.md restated to the pages the T371 bundle moved (impl-drift 2026-11-23, recorded: claims fix only, no map effect; docs/build*.md are the T383 bundle's live files) - 'Magistrate's manor (county magistracy)#staff housing knob' MISLABELED: cite research/questions/0331-where-an-offices-staff-lived.html for the knob's three forms and keep 0097 for the family rowhouse, and check the Knobs 5 prose option (c), seniors in town, against 0331 (a finding contradicted if 0331 does not carry it); '#the official study's seat' DRIFTED: 0113's drawing page now records Hayakawa's mirrored row and the back-row end seat as a GUESS departing from the record (Edo's yobeya, Takayama's ima); 'Outer court (administrative / public)#office hall' DRIFTED: the same mirrored row, no longer 'only the east seat'. Effect: a reader of the docs is told 0113 records less than it does; no plan moves.
      research: rendering
- [ ] T011 from 449 T411: docs/buildings.md 'Sacred features#grave markers' claim MISLABELED (impl-drift 2026-11-23 on the T399 bundle's round 2, outside the change): it cites 0235's drawing page for 'rows of ~2x1 ft markers', where the page calls the rows a map drawing convention and gives no marker size - fix: claim, CONVENTION for the rows and GUESS for the size; visible effect: none on the map, the procedure gives a guessed size as the page's
      research: rendering
- [ ] T012 from 449 T412: a compound's modest shrine is always drawn a wooden hall (impl-drift 2026-11-23 on the T399 bundle's round 2, MISLABELED docs/buildings.md 'Sacred features#modest compound shrine'): 0218 attests a small shrine but not its material, and 0220 gives household shrines 'of stone or wood' - two attested forms, so a knob rolled per sheet (or the wooden form recorded as a DEVIATION), the claim citing 0220; visible effect: no compound shrine is ever stone; ruled 2026-11-24 (spec-fidelity, spec.md Decisions Recorded and FR-004): a claim restatement, no sheet changes - every sheet's compound shrine is the hall form, 0220's 'of stone or wood' is the small shrine's and the record gives a hall no material, so the wooden hall is labeled a GUESS in docs/buildings.md's claim and its 'Modest shrine' bullet; a knob and a redraw only if the task's source-applicability check rules that 0220's two materials apply to the drawn shrine
      research: physical
      - [ ] research pass - answered by the record: research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html and research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.html
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [ ] T013 from 449 T413: a country shrine's burial ground is drawn as rows of small markers only (impl-drift 2026-11-23 on the T399 bundle's round 2, OUTSIDE THE CHANGE on docs/buildings.md 'Sacred features', Grave markers): 0235's drawing page puts a taller memorial stone or two among the rows and six stone jizo in a row at the entrance of every village burial ground - visible effect: the burial ground reads without its jizo or memorial stones; ruled 2026-11-24 (spec-fidelity, spec.md Decisions Recorded and FR-004): the drawing PROCEDURE changes and no sheet is redrawn - no Mode A sheet or generator draws a burial ground today, so docs/buildings.md's 'Grave markers' bullet and its claim carry the memorial stones and the six jizo for every sheet that draws one
      research: physical
      - [ ] research pass - answered by the record: research/questions/0235-village-burial-grounds-bochi.drawing.html
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [ ] T014 from 449 T414: 0097's drawing page gives the county plan's junior retainers' quarters as four 12 x 24 ft dwellings in a 48 ft row, while docs/buildings.md 'Outer court#barracks' gives the county example's range as 24 x 67 ft (impl-drift 2026-11-24 on the T394 bundle, OUTSIDE THE CHANGE) - measure the county sheet's barracks and retainers' quarters, then restate whichever text the drawing contradicts; visible effect: a reader comparing the page with the map finds a different length
      research: rendering

### Notes and record brought to their drawings (FR-005)

- [ ] T015 from 449 T380: the T351 bundle's PASS sheets' notes and comments brought to their drawings (building-review 2026-11-23, nitpicks and outside findings; a fix to a sheet's svg or notes re-owes its review, so none was made in the bundle): hayakawa-magistracy - the older log entries T276, T299 and T312 still give the armory at the west end with no 'since mirrored by T367' pointer (N1), and the svg comment still gives the east door to business visitors where the day office now stands at the west end (N2); ubame-magistracy - the new log line calls the clerks' room 'the room behind the dais' where the dais runs 2 ft past the clerks'/day-office partition at svg x 546, so 'mostly the clerks' room' (N1); ochiba-roundtrip-test - notes lines 100, 102 and 116-118 superseded by T367 and unmarked (N2), the Result paragraph stale, coverage 36% and perimeter-hugging 61% where make pack-audit reads 33% and 66% and the servants now on the south wall (O1, observed 2026-11-23, method: the review's make pack-audit), and the cinnabar workshop's open form with no source or GUESS label in either sheet's notes (O2: label it a GUESS, or a research pass on where a vermilion-grinding workshop kept its stock)
      research: rendering
- [ ] T016 from 449 T406: 0093's drawing page states the gatehouse site knob 449 T398 drew (found 2026-11-23 by 449 T398: the drawing page's bullet 'Where the gatekeepers sit follows the gate's form' seats a one-bay gate's gatekeepers' house beside it only, where the generator now rolls beside or behind the gate per sheet from 0093's Kita-in guardroom, against its gate now and inside behind it on the plan of 1841): a page session restates the drawing bullet to the knob, the setback past the gate's held approach labeled a GUESS; visible effect: none on a map - a reader of the page is told one seat where the maps roll two
      research: rendering
- [ ] T017 from 449 T410: 0334's Shibata row passage (hoppou-shibata-ashigaru) names 'men of the rope office' (御綱方) with no gloss (record-format 2026-11-24 round 2 on the T394 bundle, NO EDIT; the round arbiter's ruling ask:449-T394-0334-round3, accept) - visible effect: a reader is not told what the post did; look up 御綱方 at Shibata, add a bracketed translator's gloss once a source says, re-run that edit's quote-check, translation-check and record-format; and check whether the glossary's 'banner' tooltip lands inside 'banner-bearer' in that passage
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [ ] T18 Armory audit gap: rust/mode_a/src/audit/armory.rs drawn_end (lines 89-101) counts an armory anywhere inside the office hall as its west or east end bay by the side of the hall's center it falls on, so a mid-hall or dais-band armory passes armory_site; latent, no pool sheet draws one (449 found row 173; found 2026-11-24 by the triage of the open found rows (found-triage.md, found-triage-older.md))
      research: rendering
- [ ] T19 Audit size ranks have no bath pair: rust/mode_a/src/audit/program_rules.rs lines 478-490 (HIERARCHY) lacks the bath below the residence that 0116 drawing line 11 states (No kitchen, bath or shrine hall out-sizes it); the generator holds it but no audit does; latent (449 found rows 50, 55, 60; found 2026-11-24 by the triage of the open found rows (found-triage-older.md))
      research: rendering
- [ ] T20 arch_on_approach measures to the plan's bounds: rust/mode_a/src/audit/shared/grounds.rs lines 162-169 measures the first arch to plan.bounds() while its claim says the ground's edge (0220 section 48: the shrine's ground, not the edge of its wood); part verified, whether bounds equal the shrine's ground was not read, so a misplaced arch may pass (449 found rows 53, 58, 63; found 2026-11-24 by the triage of the open found rows (found-triage-older.md))
      research: rendering
- [ ] T21 docs/building-programs.md line 142 gives the generated guest quarters as a room beside the reception, where the county example (pool/magistracies/county-magistracy-example/*.compound.json line 63) draws a detached 40 x 42 ft guest house; restate the doc (449 found row 124; found 2026-11-24 by the triage of the open found rows (found-triage-older.md))
      research: rendering
- [ ] T22 docs/building-programs.md line 130 kitchen row says the door is recorded often at the rear of the house, a frequency its cited pages do not give; cite what they say or drop the frequency (449 found row 210; found by the triage of 2026-11-24, found-triage.md)
      research: rendering
- [ ] T23 docs/buildings.md's three claims that still name a departure 'the code keeps until feature 417 T33' restated to what is drawn (the restatement audit of 2026-11-24, /home/agent/.claude/jobs/c6fd72d1/tmp/restatement-audit.md): genkan porch size (the generator draws 12 by 9 ft, layout.rs GENKAN, as 0104's drawing page says; Ochiba's 10 by 6 ft the page's GUESS), tax archive strongroom role (no page puts coin in a records storehouse; a GUESS, or the clause cut), kitchen garden at the dwelling (Hoshigaoka's bed moved to sunny ground by feature 283); visible effect: none on a map, the procedure tells a reader of departures no sheet or code holds
      research: rendering
- [ ] T24 a compound's shrine is always drawn as a hall, never as the small shrine of stone or wood that 0220 says most household shrines were (impl-drift 2026-11-24 on docs/buildings.md 'Sacred features#modest compound shrine', DRIFTED after T012's restatement; spec-fidelity's aside of the same day: a separate question from T012's material): rule whether the small-shrine form applies to an office's shrine (0218 gives an office's shrine no form; 0220's source is of households, an analog) and, if it does, roll the form per sheet from the map's seed, room first; visible effect: every compound's shrine reads as a building of 77 sq ft or more, never as a small stone or wooden shrine
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited

- [ ] T25 the county plan's junior retainers' quarters lodge 12 of the office's about fifteen staff: four dwellings in a 48 ft row at no more than three men a dwelling (record-format on 0097, rounds 8-12, OUTSIDE THE CHANGE; filed on the round arbiter's ruling of 2026-11-24, round:record-format|q:0097@1). Every figure in it is a labeled GUESS, and 0097 now says no measured row under about 60 ft was found at an office, so room first: five dwellings in a row of about 60 ft, which brings the plan inside the measured range; failing that, a restated sentence saying where the other three men lodge. The 48 ft row is not a requirement; visible effect: the county sheet's staff row reads three men short of the staff its own pop-up counts
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
