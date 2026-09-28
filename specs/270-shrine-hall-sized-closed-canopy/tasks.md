# Tasks - feature 270, crowns may overlap; the shrine hall sized from the research

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D5).

- [x] T01 `trees_overlap` drops the crown-on-crown test (D1; FR-001); its test rewritten red first: a partly
      overlapping pair passes, a concentric pair is a duplicated tree, a canopy over a building or a caption still fires; docstring and `buildings.md`'s tree rule
      research: rendering
      verify: DONE. DONE. trees_overlap reports only a duplicated tree (trunks within a third of the smaller crown's radius, a guess, research R2) and every canopy-over-X as before; test_crowns_may_overlap_but_a_tree_is_not_drawn_on_another red first, then green; docstring, comment, registry fix line, buildings.md
- [x] T02 The Hoshigaoka sheet and village map redrawn from the layout (D2-D4; FR-002, FR-003): the building 66 by
      32 ft, the arches, forecourt, basin, clearing to the new face, the grove closed; the map's svg/png and
      manifest; the notes label every dimension; pack audit and `matches_map` green
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. DONE. sheet and map from one layout: the hall-and-dwelling 66 x 32 ft (28 x 32 hall at center, 16 ft kitchen, 22 ft dwelling), 138 overlapping crowns (87% of the ground they may cover), arches one pitch off the new face, the map glyph 33 x 16 px with its records and the ragged grove outline; pack audit all green, matches_map OK. Boxes: research pass = record question 120 (bands) and 124 as feature 268 checked them - no new source; source-reader, recorded and cited, quote-check and source-applicability confirmed there (268 T01/T02)
- [x] T03 `buildings.md` and `buildings/programs.md` (and the hall item's why in `types.json`): the sizing rule
      (D5; FR-004) and the one-roof building's dimensions from question 120
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. DONE. buildings.md: a sheet's building sized from the research, never from a map glyph as a measurement, the map edited to the sheet; programs.md size anchors say so; make building-programs CHECK=1 current. Boxes as T02 (question 120 as checked in 268)
- [x] T04 size-audit and building-review on the sheet, settlement-review on the map's shrine region, in the
      background; ledger rows; findings applied; escalation-check on anything for the GM (FR-005)
      research: rendering
      verify: DONE. DONE. size-audit (26/28 ok; the kitchen end and the sacred tree applied), building-review (3 errors applied), settlement-review x2 (round 1 no errors, recorded NOT-REVIEWABLE on a gate flake; round 2 PASS); ledger rows; escalation-check on every relay
- [x] T05 `make done`; `scripts/sync-with-main.sh done`
      research: rendering
      verify: DONE. DONE. make done green 2026-09-27 (163 s) after one browser-timing flake in test_synthetic's raster-mode wash (passes alone 20/20, green on re-run; not on this feature's path)
