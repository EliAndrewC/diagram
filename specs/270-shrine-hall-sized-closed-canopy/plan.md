# Implementation Plan: 270 - crowns may overlap; the shrine hall sized from the research

**Branch**: none (`export SPECIFY_FEATURE=270-shrine-hall-sized-closed-canopy`) | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

## Summary

Drop the crown-on-crown test from `trees_overlap`; redraw the Hoshigaoka grove as a closed wood; size the
hall-and-dwelling from the record's bands (72 by 32 ft) on the sheet and the frozen village map, moving the arches,
the forecourt, the basin, the clearing and the grove to the new face; write the sizing rule into `buildings.md`
and the program.

## Technical context

- **Surface**: `tools/pack_audit/shared.py` (`trees_overlap`), its tests; the sheet (hand-authored SVG from the
  268 layout scripts, kept in the session scratchpad and re-run); the frozen map's svg/png (mirror) and manifest;
  `buildings.md`, `buildings/programs.md`, `types.json` (the hall item's why).
- **No settlement engine change**: the pack audit is a tool; no map rolls; no perf bookends owed (the generator
  is untouched).
- **Single artifact**: the Hoshigaoka shrine sheet; then `make done`.

## Constitution check

- I-V, VII, VIII: N/A or PASS as in 268 (no UI, no pool content, no SOURCE blocks, no in-world prose).
- VI: PASS - pack audit on the sheet, size-audit and building-review on it, settlement-review on the map region,
  `make done`.
- IX: PASS - the GM's notes say nothing of the hall's size.
- X: PASS - a red-green test for the crown-on-crown change; 100% coverage.
- XII: PASS - opening bookend: the record's question 120 (the bands below); closing: the rendered PNGs read.
- XIII: PASS - baseline is main's green gate; no roll moves.

## Decisions

- **D1 - crowns may overlap each other; a duplicated tree may not.** `trees_overlap` keeps every "a canopy over X"
  test; its pair test reports only a duplicated tree - two trunks closer than a third of the smaller crown's radius,
  one tree drawn on top of another (a GUESS: no source read gives how close two trees grow; a third of a crown's
  radius is well inside any spacing a kept wood's trees stand at, and it catches the concentric pair of feature
  257). Class: rendering, the threshold a guess. The test is rewritten: a partly overlapping pair passes, a
  concentric pair is reported.
- **D2 - the grove's crowns overlap** so the canopy covers most of the ground they may cover: placement accepts a
  crown whose center stands at least about half the two radii from every other (the target is a closed canopy,
  measured on the layout, reported in the notes). Class: guess in degree (a kept wood's canopy is closed; its
  density is not measured by any source read).
- **D3 - the building 66 by 32 ft**, 2,112 sq ft, from question 120: the villagers' hall at the center 28 ft wide
  by 32 ft deep (the village-hall band, about 20 to 35 ft on a side: accurate as a band, the value a guess), the
  kitchen end 16 ft (a farmhouse's earthen floor, about a third of its 46 ft - the size-audit of 2026-09-27 found a
  22 ft kitchen end half again that) and the dwelling end 22 ft (together 1,216 sq ft against the farmhouse's 46 by
  28 ft, 1,288 sq ft: form accurate, size a guess), the depth 32 ft (inside Kaie-ji's 8 to 13 m, near the
  farmhouse's 28 ft), the whole inside the one-roof band of 2,100 to 3,600 sq ft. The hall stays centered on the
  map's approach axis. Interior: the hall's rear 10 ft an altar bay, its worship floor 28 by 22 ft; the dwelling
  end the monk's rooms (22 by 20 ft), an 18 by 12 ft writing room along the front, a 4 ft entry at the east door.
- **D4 - the map follows the sheet**: the shrine glyph 33 by 16 map px, its hall room on the same axis; the manifest's
  `religious` and `shrines` records to it; the arches one pitch off the new face (map y 1088 to 1124); the grove's
  far edge at the outermost arch. The frozen map's svg/png are edited in the mirror as in 268.
- **D5 - the sizing rule**: a building's dimensions on a sheet come from the research unless the GM gave them,
  and never from a map's glyph as a measurement; where a map's glyph differs, the map is edited to the sheet (buildings.md, the
  program).

(Figures observed 2026-09-27; method: read from the record's question 120 and the 268 sheet's notes; the new ones
this plan's arithmetic on those bands.)

## Phases

1. T01: `trees_overlap` drops the crown-on-crown test; its pair test reports only a duplicated tree (the test rewritten red first); docs.
2. T02: the layout re-run - the building 72 by 32, the clearing, the arches, the grove closed - the sheet and the
   map (svg, png, manifest), the notes; pack audit and `matches_map` green.
3. T03: `buildings.md`, the program and the hall item's why (D5, D3).
4. T04: size-audit and building-review on the sheet, settlement-review on the map region; ledger rows; findings
   applied; anything for the GM through escalation-check.
5. T05: `make done`; `sync-with-main.sh done`.
