# Tasks - feature 257, a sheet on a map matches the map, and trees overlap nothing

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D10). Research: [`research.md`](research.md)
(R1-R3). Every prose or code task: American spellings, hyphens only. No task here is
`research: physical`: the feature measures this project's own drawings (R1-R3) and reopens no
historical question.

## Phase 0 - baseline and the parser (D1)

- [ ] T01 The constitution XIII baseline: `git worktree add --detach /tmp/base257 HEAD`; there, `make quick
      ALL=1` and `make hooks-test`; the counts in `specs/257-sheet-matches-map/measurements.json` as
      `m:baseline-quick`; each later failure checked against the clone
      research: rendering
      measure: the worktree's own `make quick ALL=1` output
- [ ] T02 The parser knows a tree and a fence (D1): `l7r/diagram/tools/pack_audit/parse.py` - `TREE_FILL`,
      `ParsedPlan.trees` (a circle with the canopy fill, own or its group's, or in `<g id="trees">`; not a
      glyph) and `ParsedPlan.fence_segs` (the `<g id="fence">` lines as thin rects); `tests/tools/test_parse.py`
      red first (a canopy in a fill group, a bare canopy, a `trees` group, a circle of another fill stays a
      glyph; the fence's lines)
      research: rendering

## Phase 1 - trees overlap nothing (FR-001, FR-002; D2, D5)

- [ ] T03 `shared.trees_overlap` (D2): a canopy against every built footprint, furniture rect, wall band,
      divider, fence segment, non-tree glyph, tub and label by closest-point distance, and against every
      other canopy, with `WALL_OVERLAP_MIN_PX` as the touching tolerance; each finding names the tree, what
      it covers and the depth in feet; `tests/tools/test_shared.py` red first (one case per thing it can
      cover; a canopy on open ground; two canopies touching; two overlapping)
      research: rendering
- [ ] T04 The registry row and the fixture (D5): `tests/fixtures/hoshigaoka-tree-on-fence-red.svg` is the
      Hoshigaoka sheet as committed before this feature (the canopies straddle the fence, two lie on each
      other); the `trees_overlap` row in `registry.py`, shared, with its fix; `test_registry.py` proves it
      fires there; `make pack-audit` on every other pool sheet is quiet (Ubame's garden trees included - a
      finding there is fixed on that sheet in this task)
      research: rendering

## Phase 2 - the map declaration and the map check (FR-003, FR-004, FR-005; D3, D4, D5)

- [ ] T05 The declaration (D3): `report.read_on_map` and `OnMap`; `Context.on_map`; the sweep, the registry
      test and the report pass it; `tests/tools/test_report.py` red first (the line parsed, a malformed
      line refused by name, no line = None); `contracts/on-map.md` is the grammar
      research: rendering
- [ ] T06 `mapmatch.py` (D4): `load_map` (cached), the `CLASSES` table with one reader per manifest key
      (R2), `Transform`, `frame_in_map`, `inventory` (the features inside the frame, per class), and
      `check(ctx)` running directions (b) and (c) with `MAP_GRAIN_PX = 15` (`m:map-grain`, R1), (d) with one map px per side, and the
      declaration refusals (no manifest, no feature of the key at the position, an unknown sheet class);
      the crop check yields to a declared map and the report says so (D11, spec FR-006) - a sheet on a
      map shows what the map shows there, empty ground included;
      `tests/tools/test_mapmatch.py` red first on a synthetic manifest: each direction red then green, a
      feature at the grain's edge, each refusal, the "on no map" line
      research: rendering
- [ ] T07 The registry row and the fixture (D5): `tests/fixtures/hoshigaoka-off-map-red.svg` (the pre-redraw
      sheet) with `hoshigaoka-off-map-red.notes.md` beside it declaring the real Hoshigaoka manifest; the
      `matches_map` row, shared, with its fix; the registry test proves it fires there (the grove trees,
      the burial ground, the hall's size); every sheet with no declaration reports "on no map"
      research: rendering
- [ ] T08 The report prints both checks in registry order (`report.check_lines` needs nothing new if the
      rows are registered - verify with `make pack-audit` on the committed sheet, which now names the
      trees and, with a declaration, the map)
      research: rendering

## Phase 3 - site items (D6)

- [ ] T09 `types.json` items gain `"site": "<class>"` (`grove` = `tree`, `burial_ground` =
      `burial_ground`), the schema and `types.py` follow, `labels.check_program` skips a site item whose
      class the declared map does not show inside the frame (and asks for it with no declaration);
      `tools/building_programs.py` renders the site column and `make building-programs` refreshes
      `buildings/programs.md`; `tests/tools/test_labels.py` and `tests/test_building_types.py` red first
      research: rendering

## Phase 4 - the sheet (FR-006; D7, D9)

- [ ] T10 The Hoshigaoka sheet redrawn to R3 (D7): the hall 60 by 48 ft, the arch 20 ft in front, the well
      108 ft behind on the axis inside a fence carried north, no grove, no burial ground, no lane outside
      the arch, swept ground to the stated frame; the notes gain `**On map**`, the frame and the
      "overridden by the map" list; `make pack-audit` green on every check; the PNG rendered
      research: rendering
- [ ] T11 `make size-table` then `size-audit` (background), and `building-review` (background), one agent
      each, on the redrawn sheet; findings applied or answered in the notes' Review log; two rows in
      `docs/review-ledger.md`
      research: rendering
- [ ] T12 The sweep and the registry test green over every pool sheet; the fixtures of feature 254 still
      fire (they are cut from the old sheet and keep it)
      research: rendering

## Phase 5 - the rule, the gate, the push (FR-007, FR-008, FR-009; D8, D10)

- [ ] T13 The rule written (D8): `buildings.md` (the canopy fill in the vocabulary; the surroundings rule;
      step 5 of "Adding a building type"), `buildings/programs.md` knob 4, `.claude/agents/building-review.md`
      (the map pass)
      research: rendering
- [ ] T14 The sweep's cost re-measured over every sheet (`m:sweep-cost`); `make done` green with both checks
      covered in full; the gate's coverage floor reports 100%
      research: rendering
      measure: `make test-file FILE=tests/test_mode_a_sheets.py` wall time; the gate's own output
- [ ] T15 The writeup for the GM through `escalation-check`: the three answers (what fires, what the sheet
      now shows, what the map itself says), the seven-arch disagreement and the well 108 ft behind the
      hall as the map's own record (FR-009), the reviewer's aside
      procedure
- [ ] T16 Stop-work: commit; `scripts/sync-with-main.sh done` (GATED - engine code); render-sync once green
      procedure
