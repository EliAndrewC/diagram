# Tasks - feature 257, a sheet on a map matches the map, and trees overlap nothing

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D12). Research: [`research.md`](research.md)
(R1-R3). Every prose or code task: American spellings, hyphens only. No task here is
`research: physical`: the feature measures this project's own drawings (R1-R3) and reopens no
historical question.

## Phase 0 - baseline and the parser (D1)

- [x] T01 The constitution XIII baseline: `git worktree add --detach /tmp/base257 HEAD`; there, `make quick
      ALL=1` and `make hooks-test`; the counts in `specs/257-sheet-matches-map/measurements.json` as
      `m:baseline-quick`; each later failure checked against the clone
      research: rendering
      measure: the worktree's own `make quick ALL=1` output
      verify: DONE. 3755 passed, 5 skipped in the detached worktree at 6dfce73b; hooks-test 26 suites green; recorded as m:baseline-quick
- [x] T02 The parser knows a tree and a fence (D1): `l7r/diagram/tools/pack_audit/parse.py` - `TREE_FILL`,
      `ParsedPlan.trees` (a circle with the canopy fill, own or its group's, or in `<g id="trees">`; not a
      glyph) and `ParsedPlan.fence_segs` (the `<g id="fence">` lines as thin rects); `tests/tools/test_parse.py`
      red first (a canopy in a fill group, a bare canopy, a `trees` group, a circle of another fill stays a
      glyph; the fence's lines)
      research: rendering
      verify: DONE. parse.py TREE_FILL, ParsedPlan.trees (fill or group, pattern dots and dots under 4 px excluded) and fence_segs; tests/tools/test_pack_audit.py 95 passed

## Phase 1 - trees overlap nothing (FR-001, FR-002; D2, D5)

- [x] T03 `shared.trees_overlap` (D2): a canopy against every built footprint, furniture rect, wall band,
      divider, fence segment, non-tree glyph, tub and label by closest-point distance, and against every
      other canopy, with `WALL_OVERLAP_MIN_PX` as the touching tolerance; each finding names the tree, what
      it covers and the depth in feet; `tests/tools/test_shared.py` red first (one case per thing it can
      cover; a canopy on open ground; two canopies touching; two overlapping)
      research: rendering
      verify: DONE. shared.trees_overlap with WALL_OVERLAP_MIN_PX as the touching tolerance; tests/tools/test_shared.py 22 passed (building, fence, label, glyph, tub, canopy on a bed, touching vs covering)
- [x] T04 The registry row and the fixture (D5): `tests/fixtures/hoshigaoka-tree-on-fence-red.svg` is the
      Hoshigaoka sheet as committed before this feature (the canopies straddle the fence, two lie on each
      other); the `trees_overlap` row in `registry.py`, shared, with its fix; `test_registry.py` proves it
      fires there; `make pack-audit` on every other pool sheet is quiet (Ubame's garden trees included - a
      finding there is fixed on that sheet in this task)
      research: rendering
      verify: DONE. fixture hoshigaoka-tree-on-fence-red.svg = the sheet as committed; the row fires there (test_registry 54 passed); Ubame's shrine wood moved onto open ground, its audit quiet

## Phase 2 - the map declaration and the map check (FR-003, FR-004, FR-005; D3, D4, D5)

- [x] T05 The declaration (D3): `report.read_on_map` and `OnMap`; `Context.on_map`; the sweep, the registry
      test and the report pass it; `tests/tools/test_report.py` red first (the line parsed, a malformed
      line refused by name, no line = None); `contracts/on-map.md` is the grammar
      research: rendering
      verify: DONE. onmap.py OnMap/parse_on_map/read_on_map, Context.on_map, the sweep, the registry test and the report pass it; tests in test_mapmatch.py (parsed, refused by name, None)
- [x] T06 `mapmatch.py` (D4): `load_map` (cached), the `CLASSES` table with one reader per manifest key
      (R2), `Transform`, `frame_in_map`, `inventory` (the features inside the frame, per class), and
      `check(ctx)` running directions (b) and (c) with `MAP_GRAIN_PX = 15` (`m:map-grain`, R1), (d) with one map px per side, and the
      declaration refusals (no manifest, no feature of the key at the position, an unknown sheet class);
      the crop check yields to a declared map and the report says so (D11, spec FR-006) - a sheet on a
      map shows what the map shows there, empty ground included;
      `tests/tools/test_mapmatch.py` red first on a synthetic manifest: each direction red then green, a
      feature at the grain's edge, each refusal, the "on no map" line
      research: rendering
      verify: DONE. mapmatch.py: CLASSES, Transform, inventory, the three directions (15 px position grain, 1 px size), the refusals, on no map; the crop check yields to a declared map; test_mapmatch.py 9 passed
- [x] T07 The registry row and the fixture (D5): `tests/fixtures/hoshigaoka-off-map-red.svg` (the pre-redraw
      sheet) with `hoshigaoka-off-map-red.notes.md` beside it declaring the real Hoshigaoka manifest; the
      `matches_map` row, shared, with its fix; the registry test proves it fires there (the grove trees,
      the burial ground, the hall's size); every sheet with no declaration reports "on no map"
      research: rendering
      verify: DONE. fixture hoshigaoka-off-map-red.svg + notes declaring the real manifest; matches_map fires there (the grove trees, the burial ground, the hall's size); registry test 54 passed; magistracies report on no map
- [x] T08 The report prints both checks in registry order (`report.check_lines` needs nothing new if the
      rows are registered - verify with `make pack-audit` on the committed sheet, which now names the
      trees and, with a declaration, the map)
      research: rendering
      verify: DONE. make pack-audit prints trees_overlap and matches_map in registry order, and viewbox_cropped: skipped - the frame is the map's on the declared sheet

## Phase 3 - site items (D6)

- [x] T09 `types.json` items gain `"site": "<class>"` (`grove` = `tree`, `burial_ground` =
      `burial_ground`), the schema and `types.py` follow, `labels.check_program` skips a site item whose
      class the declared map does not show inside the frame (and asks for it with no declaration);
      `tools/building_programs.py` renders the site column and `make building-programs` refreshes
      `buildings/programs.md`; `tests/tools/test_labels.py` and `tests/test_building_types.py` red first
      research: rendering
      verify: DONE. types.json site on grove and burial_ground, types.py and the schema, check_program takes the map inventory, the programs table renders the site note (CHECK=1 current); tests/tools/test_site_items.py 3 passed, test_building_types 17 passed

## Phase 4 - the sheet (FR-006; D7, D9)

- [x] T10 The Hoshigaoka sheet redrawn to R3 (D7): the hall 60 by 48 ft, the arch 20 ft in front, the well
      108 ft behind on the axis OUTSIDE the fence, which closes behind the sanctuary (the size-audit's
      ruling of 2026-09-20; FR-006 as amended), no grove, no burial ground, no lane outside
      the arch, swept ground to the stated frame; the notes gain `**On map**`, the frame and the
      "overridden by the map" list; `make pack-audit` green on every check; the PNG rendered
      research: rendering
      verify: DONE. the sheet redrawn to R3 and the two reviews: hall 60x48 at map (392,1074), the arch at the map's torii, the well outside the fence at the map's well, bare ground, no grove, burial ground or lane; frame 100/60/20 ft as stated; pack-audit all OK; PNG rendered
- [x] T11 `make size-table` then `size-audit` (background), and `building-review` (background), one agent
      each, on the redrawn sheet; findings applied or answered in the notes' Review log; two rows in
      `docs/review-ledger.md`
      research: rendering
      verify: DONE. size-table then size-audit and building-review in the background, one agent each; findings applied or answered in the notes' Review log; two ledger rows in docs/review-ledger.md
- [x] T12 The sweep and the registry test green over every pool sheet; the fixtures of feature 254 still
      fire (they are cut from the old sheet and keep it); the village map's directory unchanged (`git diff
      --stat` over `legacy-hand-authored-pool/villages/hoshigaoka/` against the claim commit is empty - SC-003)
      research: rendering
      verify: DONE. tests/test_mode_a_sheets.py 7 passed and test_registry 54 passed over every pool sheet; the 254 fixtures still fire; git diff --stat against 6dfce73b over the village map's directory is empty

## Phase 5 - the rule, the gate, the push (FR-007, FR-008, FR-009; D8, D10)

- [x] T13 The rule written (D8): `buildings.md` (the canopy fill in the vocabulary; the surroundings rule;
      step 5 of "Adding a building type"), `buildings/programs.md` knob 4, `.claude/agents/building-review.md`
      (the map pass)
      research: rendering
      verify: DONE. buildings.md (the surroundings rule, the Trees entry, step 5), programs.md knob 4 and the burial-ground sentence, building-review.md's map pass
- [x] T14 The sweep's cost re-measured over every sheet (`m:sweep-cost`); `make done` green with both checks
      covered in full; the gate's coverage floor reports 100%
      research: rendering
      measure: `make test-file FILE=tests/test_mode_a_sheets.py` wall time; the gate's own output
      verify: DONE. make done green (done257b.log: 4085 passed, every module at 100%, the roll census green, hamlet floor 99 modules at 100%); m:sweep-cost 4.671 s recorded
- [x] T15 The writeup for the GM through `escalation-check`: the three answers (what fires, what the sheet
      now shows, what the map itself says), the seven-arch disagreement and the well 108 ft behind the
      hall as the map's own record (FR-009), the reviewer's aside
      procedure
      verify: DONE. the writeup drafted and judged by escalation-check (4 keep, 2 rewrite, 3 cut): the two checks and the two sheets they changed kept; the seven-arch conflict kept as two GM rulings in conflict; the well and frame questions cut (the record answered them); the 48 ft block a measurement; sent as the final message
- [x] T16 Stop-work: commit; `scripts/sync-with-main.sh done` (GATED - engine code); render-sync once green
      procedure
      verify: DONE. commit; scripts/sync-with-main.sh done on the green gate (GATED route - engine code); render-sync after
