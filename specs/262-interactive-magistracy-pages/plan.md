# Implementation Plan: Interactive magistracy pages

**Feature**: `262-interactive-magistracy-pages` | **Date**: 2026-09-26 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), the GM's words and the accepted design in [request.md](request.md).

## Summary

The hamlet page (feature 134 and its successors) already does everything the GM described; what it
needs from a map is a list of drawn strings and, beside each, the KIND it belongs to. A hamlet gets that
list from its generator. A hand-drawn magistracy gets it from its own SVG: each element or group carries
a `data-kind` attribute, and a small reader flattens the sheet into (string, kind) pairs in draw order
and hands them to the existing `render_page`. What each kind IS lives in one new registry of Mode A
kinds, in the hamlet classes' docstring form, written from the existing research record.

Four pieces:

1. **The reader** (`interactive/sheet.py`): tagged SVG -> strings + tags; the census; `write_sheet_page`.
2. **The registry** (`interactive/compound_kinds/`): the Mode A kinds, one family module per part of a
   compound, plus the setting's particulars; `COMPOUND_CLASSES`.
3. **The program is folded into the registry** (FR-003a): the magistracies items of `buildings/types.json`
   name their kind; their class and why are read back from the kind; the pack audit finds them by tag.
4. **The page takes a registry**: `explanations`, `unregistered_classes`, `render_page` and
   `write_html` take the registry as a parameter defaulting to the hamlet `CLASSES`, so no hamlet caller
   changes and no hamlet page changes.
5. **The five maps**: the three hand-drawn sheets are tagged (and their court ground split into one rect
   per court); the placer's `emit_svg` writes the kind of everything it draws; each `.gen.py` writes its
   page after its PNG.

## Technical Context

**Language/Version**: Python 3.14 (the engine's). **Primary dependencies**: none new - the reader is a
tokenizer over the SVG text (regex), not an XML library, because the page must carry the sheet's own
bytes and an XML round trip rewrites them.

**Storage**: the tagged SVGs (tracked); the pages are derived and gitignored (`pool/*/*/*.html`, already).

**Testing**: pytest - `tests/interactive/` for the reader, the registry and the page; the pool sweep for
the five maps' completeness.

**Performance**: a magistracy SVG is ~40 KB with ~60 labels; the page write is dominated by the raster
(two resvg renders), the same work a hamlet page pays, and only when rendering (feature 208's rule).

**Constraints**: the PNG must not change (FR-009); the pack audit must read every sheet as before (FR-009).

**Single-artifact target**: `pool/magistracies/ochiba-magistracy/` - the GM's named example; rebuild is
one resvg render plus the page (a few seconds). Then the other four maps, as their own task.

**Every step is two steps**: Ochiba first (tag, page, both examples, PNG and audit identical), then
Hayakawa, Ubame and the two placer drafts (T-numbers in tasks.md).

## Performance bookends

**N/A - no settlement-generator change.** The hamlet pipeline is untouched except for a defaulted
parameter threaded through `render_page`; the perf harness measures hamlet rolls, whose bytes this
feature does not move (the hamlet interactive tests and the gate prove it). The placer's `emit_svg`
gains attributes on strings it already writes - 0.17 s end to end today.

## Constitution Check

- **I, II**: N/A - no gm-assistant UI; the page is the existing interactive page.
- **III, VII, VIII**: N/A - no pool content of a recurring kind, no generated in-world prose.
- **IV, V**: PASS - no SOURCE block touched; `request.md` written once from the GM's words.
- **VI. Verify Before Reporting Done**: PASS - each task names its verification; the maps are checked by
  measurement (PNG identity, audit identity, census) and the pages opened; `building-review` runs on
  Ochiba's page at acceptance (one map per agent).
- **IX. Setting Integration**: PASS - particulars (threshold stones, Pact-Bowl, Fox-Fire Lantern, salt
  wards, the Fox border) are written from `/host-l7r-repo/setting/l7r.md` and each map's own notes;
  nothing new is invented about the setting.
- **X. Python Discipline**: PASS - ruff, format, pyrefly, red-green on the reader, 100% coverage. The
  registry modules are docstrings; each family module stays under 1,000 lines by splitting families.
- **XII. Historical Grounding**: PASS, bounded by the GM's instruction - no new research. Every kind's
  label and text are COPIED from the record's existing classification; a kind the record does not cover
  is labeled `guess` and says so. No map draws anything new, so no element's historical truth moves.
- **XIII. No Known Regressions**: PASS with a measured baseline - `make done` on unmodified HEAD in a
  detached worktree (`scratchpad/base-wt`), logged; PNG and pack-audit baselines of all five sheets saved
  before the first edit.

## The design

### D1 - The tag is an attribute on the drawn element, the nearest one wins

`data-kind="<key>"` on any element or `<g>`. An element's kind is its own attribute, else its nearest
tagged ancestor's. `data-kind="-"` is the not-highlighted ruling (sheet background, title, subtitle,
scale bar), which the hamlet page already honors. A drawn label is a child of its feature's group on
every sheet already, so the label lights with its feature and the modal's heading is the registry's
name; relabeling is one edit to the sheet. Serves FR-002 and User Story 3.

Rejected: a side file mapping element ids to kinds (two places to edit - the GM's one constraint);
inferring a kind from the nearest label (the unlabeled tubs, wells and doors would be guesses, and a
moved label would silently re-kind a building).

### D2 - The reader flattens by re-opening ancestors

`sheet.flatten(svg_text)` tokenizes the sheet (comments dropped, tags and text kept byte for byte) into a
tree and walks it. A subtree whose descendants carry no kind of their own is ONE fragment; a group with a
differently-tagged descendant is descended into, and each child fragment is emitted wrapped in the
ancestors' own opening tags and closings, so a `transform` or an inherited `fill` / `stroke` still
applies. The list is in document order, so paint order is unchanged. The first fragment is the `<svg>`
opening tag and the last its closing, both ruled `-`; `<defs>` is ruled `-` and its patterns are not
counted as ink (the census already skips them). An `id` on a re-opened ancestor is dropped from every
copy after the first, so the page never carries a duplicate from the reader.

### D3 - The page takes a registry

`explanations(present, notes, registry=CLASSES)`, `unregistered_classes(counts, registry=CLASSES)`,
`render_page(..., registry=CLASSES)`, `write_html(..., registry=CLASSES)`. Defaulting keeps every hamlet
call site and byte unchanged (FR-011). The place card is not built for a sheet (`meta` empty ->
`place_card` returns None), and the lane default only fires for the hamlet `village lane` key.

### D4 - One registry of Mode A kinds; particulars are kinds too; per-map facts come from notes

`interactive/compound_kinds/` (named so beside the placer module `l7r/diagram/compound.py`) mirrors `interactive/classes/`: `grounds.py` (courts, gardens, the wall and its
gates, roads), `office.py` (office hall, dais, clerks' room, archive, granary, cell, gatehouse, barracks,
notice board, practice ground), `household.py` (residence, karo's house, staff housing, kitchen, bath,
well, latrine, stables, fire-water tubs, shrine), `particulars.py` (what one map has because of its
place in the setting: Ochiba's threshold stones, Fox-Fire Lantern, cinnabar workshop; Hayakawa's river,
landing and salt wards; Ubame's Fox border, parley room, charcoal trade). Each is a `Kind` with the same
tags; `COMPOUND_CLASSES` is built with `install_siblings` from the four modules in that order. Keys may
coincide with hamlet keys (a `well`) because the registries are separate - a compound well's modal is
written about a compound.

What is true of one map only and is not a kind of its own (Ochiba's shrine is a two-altar Inari hall;
Hayakawa's bath was enlarged; Ubame's shuttered wing) goes in that map's `.notes.md` "Map notes /
Features" block keyed by kind, which the page already shows as "on this map" (FR-010). The notes files
already say these things in prose; the bullet is the reader-facing sentence.

### D5 - Classification is carried, never decided

The measurement is `coverage.md` (every proposed kind against every page of the record, the `types.json`
items and the canon). Each kind's `Label:` is what an existing finding already says: a research section
that grounds the thing -> `accurate`; a `types.json` item folded into it -> its class, carried with its why
into the note (a size the item calls a guess or a convention becomes the kind's caveat); a thing made by
the setting's canon or the map's story with no historical counterpart the record covers -> `deviation`
(`Sources: not recorded`); a glyph drawn larger where the record says so -> `convention`; a kind no
finding classifies -> `guess`, its note saying the record has no entry on it. A kind no research section
covers says `Entry: research/buildings.html (no dedicated entry - recorded as silent)` and so lists no
questions - the gap the GM can see. The closing report lists both sets (User Story 4).

Two program items cover a room in one sheet and a building in another (`clerks`: a room of the office hall
on Ochiba and Ubame, a separate building on Hayakawa and the drafts; `guest`: a room of the residence, or
Hayakawa's detached house). Their kinds are `clerks' room` and `guest quarters`, written true of both
forms, and the room's label carries the kind on the sheets that draw it as a room.

### D6 - The courts are ground rects of their own

Each hand sheet's `id="precinct"` court-earth rect is split at the divider into an inner-court rect and an
outer-court rect, both keeping `id="precinct"` (the audit reads the precinct as "the rect(s)" so marked -
Hayakawa already declared two). The ground pattern is in user space, so two rects paint what one did; where
their anti-aliased edges meet, the seam must not show through the divider's gate opening. Which join is
seam-free is MEASURED per sheet, never assumed: on Ochiba the two rects ABUT (0 px differ; a 1 px overlap
left 72 px differing where the seam crosses the opening), on Ubame the inner rect runs 1 unit under the
outer (abutting left the seam visible in its household-door gap). Every sheet's PNG and audit are measured
identical after the split. Ubame's border court is drawn as ground of its own (the receiving garden's rect
under its BORDER COURT label, x 920 y 462, 106 by 94 px), so that rect carries the border court's kind with
its label and lantern.

### D7 - The placer writes kinds

`BuildingSpec` gains `feature: str` (the Mode A kind key); both programs declare it. `emit_svg` writes
`data-kind` on each building, each spine zone (`forecourt` -> outer court, `oshirasu` -> hearing court,
`garden` -> garden, `practice ground`), each point feature, the wall, the divider, the gate, the notice
board; the title and subtitle and scale bar are `-`; the precinct is split at `divider_ft` as in D6. A
building with no `feature` is refused at emit time, naming it.

### D9 - The fold: the audit finds an item by its tag

`RequiredItem` gains `kind`; an item is EITHER labeled (`label`, `class`, `why` - the country-shrine tier,
unchanged) OR kinded (`kind`, and no class, why or label of its own); `_item` refuses a mix. The parser
records every tagged element's kind by the byte offset of its opening tag (`sheet.element_kinds`) - the
same offset a parsed label carries as `pos` - so `matches()` takes a kind item's labels as those the sheet
tags with its kind, `check_program` finds a kind item present when any element carries its kind, and the
size band is measured on the structure the first such label stands on, exactly as before.
`classification(item)` returns the kind's registry label and note, and the band finding and
`programs.md` print those. Measured: every sheet's audit output is identical after the fold.

### D10 - The red fixtures are the tagged sheet plus their own defect

The Mode A red fixtures are frozen copies of the sheets with one defect each; under the fold an untagged
copy would read as "every item missing" and hide the one finding it exists to show. Each is re-derived by a
three-way merge (`git merge-file`: the tagged sheet, the original sheet, the fixture), conflicts resolved
by carrying each tag onto its counterpart line, and checked: no untagged ink, and its audit output
unchanged. The older Ochiba layout fixture and one Ubame fixture needed a few tags by hand.

### D8 - The gens write the page; the tests hold the sheets complete

Each hand `.gen.py` calls `write_sheet_page(svg_path)` after its resvg; the two placer gens after
theirs. `with_raster` follows the render condition (`DIAGRAM_SKIP_RENDER`), as a hamlet's does. A pool
test flattens each of the five sheets and asserts: no unclassed ink (naming the element), no unregistered
kind (naming it), every registered Mode A kind drawn on at least one sheet (FR-007), and that Ochiba's
threshold stones lead with the deviation sentence and its hearing court with none (SC-002).

## Project Structure

```text
.claude/skills/diagram/l7r/diagram/interactive/
  sheet.py                 # NEW - tagged SVG -> strings + tags; census; element_kinds; write_sheet_page
  page.py                  # registry parameter threaded (D3)
  compound_kinds/          # NEW - the Mode A kinds (D4)
    __init__.py  grounds.py  office.py  household.py  particulars.py  siblings.py
.claude/skills/diagram/l7r/diagram/buildings/types.py, types.json   # kind items, classification() (D9)
.claude/skills/diagram/l7r/diagram/tools/pack_audit/parse.py, labels.py; tools/building_programs.py   # D9
.claude/skills/diagram/tests/fixtures/{ochiba,ubame,hayakawa}-*-red.svg   # re-derived, tagged (D10)
.claude/skills/diagram/l7r/diagram/compound.py      # BuildingSpec.feature, emit_svg writes kinds (D7)
.claude/skills/diagram/pool/magistracies/*/         # tagged svgs, notes blocks, gens write the page
.claude/skills/diagram/tests/interactive/test_sheet.py, test_compound_kinds.py   # NEW (the pool sweep is the second)
```

## Complexity Tracking

None.
