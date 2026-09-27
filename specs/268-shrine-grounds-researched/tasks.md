# Tasks - feature 268, a village shrine's grounds, researched

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md) (R1-R4 the
pass, D1-D7 its decisions; D8-D9 in the plan). Every prose or code task: American spellings, hyphens only.

## Phase 1 - the record (FR-001 to FR-003)

- [x] T01 `research/religion-and-death/`: three new questions after entry 120 - "Was a village shrine
      walled or fenced?" (R1), "How large was a village shrine's precinct, and how much of it was built
      on?" (R2), "What else stood in a village shrine's precinct?" (R4) - and entry 090 rewritten to R3
      and the GM's ruling of 2026-09-27; entry 120's fence and precinct-size sentences and every other
      stale mention (`grep` the page directory for the fence, 30 ft, the precinct guess) brought to the
      finding; each new source registered with its write-ups; `make record`, `make citations`,
      `make glossary`
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      measure: `make quote-verbatim PAGE=religion-and-death` before quote-check; `make record-prepass PAGE=religion-and-death` before record-format
      verify: DONE. DONE. religion-and-death 122, 124, 126, 128 (128 split from 120 by the size cap), 090 rewritten, 120 and 100 brought to it; 27 registry entries; 7+6 glossary terms; make record/citations/glossary current; record tests 1128 green. Boxes: research pass = the four reader reports; source-reader 81 claims READ, 2 CONTRADICTED applied (Bishamon temple, Kanzaki registers); quote-check two passes, every finding applied, one NOT-ON-PAGE (Hakusan 09jin11, a malformed byte; read with curl); source-applicability 26 keys, 14 write-ups given their limits
- [x] T02 The record's checks, in the background, from bundles (`make check-bundle`): `source-reader`,
      `quote-check`, `record-format`, `source-applicability` on the new and changed entries and keys;
      then `entry-drift` on every pair `scripts/_entry_owed.py` names (the torii and country-shrine
      kinds in `household.py`, the grove in `grounds.py`); every verdict folded in
      research: rendering
      verify: DONE. DONE. source-reader x3, quote-check x3 + re-check x2, record-format x2, source-applicability x2 + 1, entry-drift on 4 modals (2 DRIFTED, applied); all findings applied in one pass; the entry-owed and check-bundle tools extended to the Mode A compound kinds, which they had never scanned

## Phase 2 - the program (FR-004 to FR-006)

- [x] T03 `buildings/programs.md` and `l7r/diagram/buildings/types.json`: no precinct enclosure; the
      precinct band from R2; the grove and sacred tree (site items) and the basin as items; the knobs
      (guardian figures, lanterns, strength stones and a sanctuary fence on wealth, none at average; a
      farmers' stage and a sumo ring, absent by default, prevalence stated); `buildings.md`'s arch (D5),
      grove and precinct vocabulary; `make building-programs CHECK=1`
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. DONE. programs.md composition rules, knobs 5-7, size anchors; types.json: fence retired, sacred_tree (site), guardian_figures, lanterns, strength_stones, stage, sumo_ring (optional); buildings.md arch, fence, grove, crop; make building-programs CHECK=1 current. Boxes as T01 (research 122, 124, 126)
- [x] T04 `no_precinct_enclosure` (D7) replaces `fence_not_wall` in `tools/pack_audit/shared.py`,
      `registry.py` and the declaration; tests red first: the walled fixture and a precinct-fence
      fixture fire, a sanctuary-only fence passes
      research: rendering
      verify: DONE. DONE. no_precinct_enclosure replaces fence_not_wall; red fixture hoshigaoka-fenced-precinct-red.svg (the old fenced sheet) fires; a sanctuary-only fence passes (test_shared); the synthetic sheet's fence rings the sanctuary alone

## Phase 3 - the engine (FR-009 to FR-011; D1-D4, D9)

- [x] T05 The pitch (D1, D2): `TORII_PITCH_FT = 12.0` with its why; `TORII_PITCH_MAX_SPANS` retired;
      `_avenue_pitch` lays every avenue at the pitch; `roll.py`'s village avenue through the pitch and
      the threshold; `hoshigaoka.gen.py`'s `SHRINE_TORII` at the pitch for conversion; tests red first
      (a village roll and a wide town avenue both come out at 12 ft, the innermost one pitch off the hall)
      research: rendering
      verify: DONE. DONE. TORII_PITCH_FT 12, cap retired; every avenue laid at the pitch; the village roll via the pitch and threshold; SHRINE_TORII at 6 px; tests: every avenue at the pitch, a village hall one pitch off its face
- [x] T06 The plan-view arch (D3, D4): `_torii` draws the kasagi bar and two post squares, true size with
      the stroke floor; `torii_halfbox` to the new extents; the wall-shortening floor at the drawn depth
      plus one px; tests red first (at 1, 2 and 3 ft/px, neighbors at the pitch do not overlap)
      research: rendering
      verify: DONE. DONE. torii_glyph_dims + torii_plan_svg (beam + post marks), torii_halfbox centered, matrix.py imports it (no mirror), the wayside arch in plan, the wall-shortening floor at the drawn depth + 1 px; parametrized non-overlap test at 1, 2, 3 ft/px
- [x] T07 The crop check's reach (D9): the `on_map` excuse and `frame_is_the_maps` removed; the test
      that an on-map sheet with a wide margin fails; `buildings.md`'s on-map paragraph
      research: rendering
      verify: DONE. DONE. viewbox_cropped runs on on-map sheets (frame_is_the_maps removed); test_the_crop_check_runs_on_a_sheet_drawn_to_a_map; the old sheet failed it (90 px margin)

## Phase 4 - the map and the sheet (FR-007, FR-008)

- [x] T08 The Hoshigaoka village map by hand (D6, D8): the mirror's svg backed up and edited (grove,
      sacred tree, basin, the seven arches at 12 ft), the png re-rasterized, the manifest brought to it,
      the grove's area measured on its outline; the map's notes and `migration-plan.md`
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. DONE. the frozen map edited by hand from one seeded layout shared with the sheet: 51 canopies on a ragged floor, 137 x 223 ft (about 858 tsubo, measured), a ragged clearing, the path, the approach gravel, the roped sacred tree, the basin (6 ft, a convention), the arches at 6 px in plan; manifest and notes; matches_map OK. Boxes as T01 (research 122, 124, 126)
- [x] T09 The Hoshigaoka shrine sheet redrawn: no fence; the grove from the well to the outermost arch;
      the swept clearing; the sacred tree and the basin; the arches in plan at 12 ft, the innermost one
      pitch off the hall; the frame cropped to the ink; `make seat-label SHEET=... WRITE=1`; the pack
      audit green (program, map-match, crop, SC-002's whole-frame reading by eye and by the audit's
      margins); the notes rewritten with every knob
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. DONE. the sheet redrawn: no enclosure, the grove, a ragged clearing with a 37 ft forecourt, the arches in plan at 12 ft outermost first, the basin, the sacred tree, cropped, captions seated (9, 0 off seat); pack audit all green. Boxes as T01

## Phase 5 - reviews and close (FR-012; SC-001 to SC-005)

- [x] T10 `size-audit` (after `make size-table`) and `building-review` on the sheet, `settlement-review`
      on the village map's edited region, in the background, one map per agent; ledger rows in
      `docs/review-ledger.md`; findings applied; anything for the GM through `escalation-check`
      research: rendering
      verify: DONE. DONE. size-audit (4 findings applied), building-review (5 errors: 4 applied, the Kaie-ji layout recorded as a deviation), settlement-review x3 (round 3: all but the flank depth fixed, then fixed); escalation-check on every relay; the canopy-overlap question carried to the GM
- [x] T11 Close: `make perf LABEL=268-end`, `make perf-report AGAINST=268-start`; the XII closing bookend on
      the rendered PNGs against R1-R4; the spec's Decisions Recorded table; `make done` (background);
      `scripts/sync-with-main.sh done`
      research: rendering
      verify: DONE. DONE. perf 268-end band 1 (total -1.8%), explained and perf-audit CONSISTENT; closing XII bookend read on the rendered sheet and map PNGs against R1-R4 (no enclosure, the grove, the close arches, the tree and basin by the approach); Decisions Recorded in the spec; make done green 2026-09-27T07:00Z
