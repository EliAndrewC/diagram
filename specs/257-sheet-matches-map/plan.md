# Implementation Plan: A sheet on a map matches the map, and trees overlap nothing

**Feature**: `257-sheet-matches-map` | **Date**: 2026-09-20 | **Spec**: [spec.md](spec.md)
**Input**: the spec (round 1 applied; round 2 pending), [`research.md`](research.md) R1-R3.

## Summary

Two shared checks join the Mode A registry of feature 254, and the Hoshigaoka shrine sheet is redrawn
to the village map it stands on. `trees_overlap` reads every canopy on a sheet (known by its fill)
against everything that is not open ground, other canopies included. `matches_map` reads a
declaration in the sheet's notes, loads the map's recorded manifest, maps the sheet's frame and
features into map coordinates through the subject's position and the two scales, and reports
disagreement in both directions within the map's measured drawing grain. The shrine's program
items that a map can record (the grove, the burial ground) become site items: asked for only where
the declared map has them. The sheet is redrawn from research.md R3, reviewed, ledgered; the rule is
written where the next sheet is drawn.

## Technical context

- **Language**: Python 3.12, the `pack_audit` tool package (`l7r/diagram/tools/pack_audit/`,
  2,029 lines over eight modules; `shared.py` 352, `parse.py` 336 - the new map check is its own
  module so no file nears the 1,000-line bar).
- **Inputs**: a sheet's SVG text, its `.notes.md`, the declaration `buildings/types.json`, and - new -
  a Mode B map's recorded manifest (`<map>.json`; `meta.ftpx` its scale, every position a center in
  map px, research.md R2).
- **Tests**: `tests/tools/` (unit, quick tree); the sweep `tests/test_mode_a_sheets.py`; the registry
  test `tests/tools/test_registry.py` (every check fires on its fixture, passes every pool sheet).
- **Constraints**: 100% coverage; the registry's contract (a check is `Check(name, run, shared,
  fixture, fix)`; `Context` carries what a check reads); the map is READ, never rolled (constitution
  VI - no map regenerates for a check).
- **Not touched**: the settlement engine, any generator, the research record's pages (the record
  already carries the country-shrine section; this feature's rule is a drawing convention recorded in
  `buildings.md`, and a GM decision recorded in the notes and the spec).

## Performance bookends

Not owed: no diagram-generator change. The one cost that moves is the sweep's (two more checks per
sheet, one of them loading a manifest of about a megabyte for the Hoshigaoka sheet); it is
re-measured at the end as `m:sweep-cost` in `measurements.json` (SC-004).

## Baseline (constitution XIII)

T01: a detached worktree at HEAD, `make quick ALL=1` and `make hooks-test`, the counts recorded as
`m:baseline-quick`; every later failure checked against the clone.

## Constitution check

- I (independent review): `building-review` and `size-audit` on the redrawn sheet, one agent per
  map, findings through `escalation-check`. II-V n/a. VI: no roll. XII (research): the one physical
  question - what stands around a country shrine - was answered by feature 254 and is not reopened;
  R1-R3 are measurements of this project's own drawings; every task is `research: rendering` or
  `procedure`. XIII: the baseline. XIV: the seven-arch disagreement between the generator's comment
  and the map's manifest is a defect found in a frozen legacy map - reported, not fixed (spec
  FR-009), because fixing it means re-rolling a hand-authored map the GM has not asked to move.
  XVI: the literal thing - both sentences, the map's hall and well included (round 1, question 1).

## Decisions this plan makes that the spec left open

- **D1 - a tree is a circle with the canopy fill.** `parse.py` gains `TREE_FILL = "#7A8C5C"` (the fill
  every pool sheet's canopies already carry - the shrine's grove, Ubame's garden trees) and
  `ParsedPlan.trees`: every `<circle>` whose own `fill`, or its enclosing `<g>`'s, is that fill, or
  that stands in a `<g id="trees">`; a tree is not also a point glyph. The fence group's lines
  (`<g id="fence">`) become `fence_segs` (thin rects, as the wall groups' lines are `wall_segs`) so a
  canopy across the fence is an overlap. `buildings.md`'s vocabulary names the fill.
- **D2 - `trees_overlap` in `shared.py`**, one function, exact circle geometry: a canopy against
  every built footprint, furniture rect, wall band, divider, fence segment, non-tree glyph, tub and
  label bbox by closest-point distance (an overlap when the distance is less than the radius by more
  than `WALL_OVERLAP_MIN_PX`, the touching tolerance the built-footprint check owns), and against
  every other canopy by center distance against the radii's sum with the same tolerance. Each finding
  names the tree, what it covers and the depth in feet; the fix says "move the tree onto open ground".
  Red fixture: the Hoshigaoka sheet as committed before this feature, copied to
  `tests/fixtures/hoshigaoka-tree-on-fence-red.svg` - the unfixed artifact is the proof it fires.
- **D3 - the declaration line.** `**On map**: <manifest path from the skill root> - <manifest key> at
  (<x>, <y>) = <sheet id>`; `report.read_on_map(svg_path)` parses it into `OnMap(manifest, key, x, y,
  sheet_id)`, `Context` gains `on_map: OnMap | None`, and the two places that build a Context (the
  sweep, the registry test) and the report pass it. The sheet id names the rect that IS the subject
  (the shrine's `hall`), so the transform's origin is that rect's center.
- **D4 - `mapmatch.py`, a new module.** `load_map(path)` reads the manifest once (cached per path
  for the sweep); a `CLASSES` table - the sheet class, how the sheet marks it, the manifest keys and
  each key's reader (research.md R2: `tree_crowns` triplets, `village_groves[*].clumps`, `cemeteries`
  rects, `wells` circles, `torii` triples, `streams`/`channels`/`lanes` polylines, `pond` and
  `crescent_ponds` polygons, `houses`/`byres`/`farm_sheds`/`storehouses`/`buildings` rects); a
  `Transform` (sheet px to ft to map px, origin at the subject's center); `frame_in_map(viewbox)`;
  `check(ctx)` running the three directions of spec FR-004 with the grain `MAP_GRAIN_PX = 15`
  (`m:map-grain`, R1) - (b) sheet features of a class with no map feature of that class within the
  grain, (c) map features of a class inside the frame with no sheet feature within the grain, (d)
  the subject's sides against the map's. A sheet class the table lacks is a finding; a manifest that
  cannot be read, or a key with no feature at the declared position, is a finding; no declaration is
  the one line "on no map". The sheet marks its classes by id: `burial_ground`, `well` or `basin`,
  `arch`, `water`, `lane`, `building`; trees by D1.
- **D5 - two registry rows, both shared.** `trees_overlap` (fixture D2) and `matches_map` (fixture
  `hoshigaoka-off-map-red.svg` with `hoshigaoka-off-map-red.notes.md` beside it declaring the real
  Hoshigaoka manifest - the pre-redraw sheet, on which the grove, the burial ground and the hall's
  size fire). The report prints both in registry order.
- **D6 - site items.** The declaration's item schema gains `"site": "<class>"`: an item whose
  presence follows the declared map. `check_program` is handed the map inventory inside the frame
  (from D4) and skips a site item whose class the map does not show there; with no declaration a
  site item is required as before. The shrine's `grove` (`site: tree`) and `burial_ground`
  (`site: burial_ground`) are the two; `programs.md`'s rendered table shows the column.
- **D7 - the redraw.** Per research.md R3, in the sheet's own coordinates: the hall 60 by 48 ft with
  the long side east-west, its face south; the arch 20 ft in front of the face on the axis, at the
  fence's south side; the approach 10 ft wide from the arch to the step; the sanctuary on the axis
  behind the hall; the shrine's one water point - the well, marked `id="well"` - 108 ft north of the
  hall's center on the axis, the fence carried north to 10 ft beyond it; the kitchen garden, privy
  and fire-water at the building as before; swept ground to the frame's edge, no grove, no burial
  ground, no lane outside the arch (the map records none there - the sando is swept ground). The
  frame: 100 ft either side of the axis, 60 ft in front of the arch, 20 ft behind the well. The
  title and scale bar stay. The notes gain the `**On map**` line, the frame, and an "overridden by
  the map" list: the grove, the burial ground, the water point's place (the record's basin beside
  the approach), each with the map's reason.
- **D8 - the rule, written.** `buildings.md`: the vocabulary's canopy fill; under "Approaches and
  surroundings" the sentence that a subject a settlement map draws follows the map, program items
  included, and declares it; in "Adding a building type" step 5 the `**On map**` line. `programs.md`
  knob 4 of the shrine: "by the map when the subject stands on one, else by the site". The
  `building-review` agent gains one pass: when the notes declare a map, lay the sheet over the map
  at the subject and list every disagreement. `programs.md`'s rendered table gains the site column
  (`make building-programs`).
- **D9 - reviews and the ledger.** `size-audit` (after `make size-table`) and `building-review` on
  the redrawn sheet, in the background, one agent each; findings applied or answered; two ledger
  rows; `escalation-check` before the writeup.
- **D10 - the gate.** Unit tests for D1 (`tests/tools/test_parse.py`), D2 (`test_shared.py`), D3
  (`test_report.py`), D4 (`test_mapmatch.py`: a synthetic manifest with one feature per class, each
  direction red then green, the grain's edge, the missing manifest, the wrong key, the unknown sheet
  class, the no-declaration line), D6 (`test_labels.py`, `test_building_types.py` for the schema);
  the registry test picks the two rows up; the sweep runs over every pool sheet; `make done` green
  at 100%; `m:sweep-cost` re-measured.

- **D11 - the crop check yields to the map.** `viewbox_cropped` asks for 15-25 px of parchment
  around the ink; a sheet on a map shows what the map shows there, empty ground included (spec
  FR-006's frame), so on a sheet with a declaration the check does not run and the report says why
  (`frame_is_the_maps`); every other sheet is cropped as before.
- **D12 - a size is held to the map's resolution, a position to its grain.** The map records a
  footprint to the pixel and a sheet can draw it exactly, so direction (d) allows one map px per side
  (spec FR-004 as amended after round 2); positions, which the map finds by search, get the grain.

## Phases

- **Phase 0 - baseline and the parser** (T01-T02): the worktree baseline; D1.
- **Phase 1 - trees overlap nothing** (T03-T04): D2, its fixture, its registry row; the check fires
  on the committed sheet.
- **Phase 2 - the map declaration and the map check** (T05-T08): D3, D4, D5, its fixture; the check
  fires on the committed sheet with the declaration.
- **Phase 3 - site items** (T09): D6.
- **Phase 4 - the sheet** (T10-T12): D7; render; `make pack-audit` green; D9 reviews and the ledger.
- **Phase 5 - the rule, the gate, the push** (T13-T16): D8; `make building-programs`; the sweep cost;
  `make done`; the writeup through `escalation-check`; `sync-with-main.sh done` (GATED: engine code).

## Project structure

```text
specs/257-sheet-matches-map/           request.md spec.md plan.md research.md tasks.md data-model.md quickstart.md
                                       measurements.json contracts/on-map.md checklists/requirements.md
.claude/skills/diagram/
  l7r/diagram/tools/pack_audit/        parse.py (TREE_FILL, trees, fence_segs)  shared.py (trees_overlap)
                                       mapmatch.py (NEW)  report.py (read_on_map)  registry.py (two rows, Context.on_map)
                                       labels.py (site items)
  l7r/diagram/buildings/               types.py types.json (site) ; specs/254-.../contracts/types.schema.json (site)
  tools/building_programs.py           (the site column)
  tests/tools/                         test_parse.py test_shared.py test_report.py test_mapmatch.py (NEW) test_labels.py
  tests/fixtures/                      hoshigaoka-tree-on-fence-red.svg  hoshigaoka-off-map-red.svg + .notes.md
  tests/test_mode_a_sheets.py          (Context.on_map)
  pool/country-shrines/hoshigaoka-shrine/   the sheet, its notes, its render
  buildings.md  buildings/programs.md  ../../agents/building-review.md  docs/review-ledger.md
```

## Complexity tracking

None: one new module, two registry rows, one schema field; no new index (the overlap check is a
few dozen canopies against a few dozen rects on a sheet; the map check reads one manifest and a
frame of a few features).
