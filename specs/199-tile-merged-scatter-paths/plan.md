# Plan - 199 Tile the merged scatter paths

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **I / II**: not applicable in this repository.
- **VI Verify before done**: the mechanism has unit tests on synthetic strings (FR-006), a structural
  guard on the real rolled page in the gate (FR-007), and the recorded browser timing in the FULL tree
  (FR-008); the pixel comparison of R4 is repeated on the implementation (FR-004, T05); the Kuwabata
  page is opened and hovered by the session before the push (SC-004).
- **X Python discipline**: one function and two constants in `page.py` (790 lines, stays under the
  1,000 bar); 100% coverage owed on every new line, and the new branch is reached by the unit tests.
- **XII Record the why**: a rendering decision - the cell size, the threshold, the anchor rule - each
  with its measurement at the point of change and in `research.md`; nothing physical.
- **XIII No regressions**: the page differs from today's by the tiling alone; the existing merge
  tests, the census tests (`ink_census` counts elements per class - the count RISES by the added
  tiles, and any test pinning an element count on a real page is re-measured) and the browser test
  run at the gate. Baseline: `make done` on the unchanged clone is the last green record; this feature
  lands only on a green `make done` of its own.
- **XV / XVI**: spec-fidelity before code; the request is an analysis and then "run that feature end
  to end", and the spec adds nothing beyond the fix the analysis named.
- **Iteration cost**: one engine function; the gate once at the end; `make quick` while iterating.
- **Route**: `l7r/diagram/interactive/page.py` is engine code -> GATED; a green local `make done` is the
  verification when main adds no engine content to the merge. `export SPECIFY_FEATURE` for the push.

## Design

### `merge_primitives` (page.py)

Today's emit loop, per bucket with 2+ members:

```
d = "".join(_sub(tag, elems[k][3]) for k in members)
repl[first] = f'<path d="{d}" {attrs}{tail}/>'
```

Becomes: if `len(members) >= TILE_MIN`, group the members by `_cell(tag, at)` - `(floor(ax / TILE),
floor(ay / TILE))` of the anchor (`x1,y1` for a line; `cx,cy` for a circle or ellipse) - in order of
first appearance, and write one `<path>` per group, concatenated, at `repl[first]`. The attribute
string and the `fill="none"` tail are computed once and repeated. Under the threshold, unchanged.

`_cell` and `_tiles` are module-level functions (feature 146: no closures). No guard for an unreadable
anchor: `_sub` already reads the same attributes to write the subpath, so a member without them never
reaches the emit loop, and a guard nothing can reach would be an uncovered line.

### Tests

- `tests/interactive/test_page.py`: FR-006 - build 450 lines in three 400 px cells, assert three
  paths, each `d` anchored in one cell, 450 `M` in total, attributes on all three; 199 lines -> one
  path; a mix.
- `tests/interactive/test_page.py` (or the roll-backed test module that already renders the reference
  hamlet's page at the gate - T03 finds it): FR-007 - parse every `<path d=...>` on the real page,
  compute each subpath's anchor, assert all anchors of one path share a cell whenever the path has
  `TILE_MIN` or more subpaths.
- `tests/full/interactive/test_page_browser.py`: FR-008 - a `kuwabata` fixture built like `inashiro`
  from the pool declaration (seed 21, 16 households, `mulberry_dike_fishpond`, `pond_layout="mosaic"`,
  `dike_crop="mulberry"`), a new timings test with the pointer sweep at the opening view, median per
  move printed and capped at 40 ms; `test_reference_hamlet_timings` prints the same sweep uncapped.

### Measurement (T05)

Re-run `zoomcmp.py` (scratchpad) on the regenerated pool pages: the move cost table of R2 and the
pixel comparison of R4, written into `research.md` R6 as the implementation's numbers.

### Documents

`interactive/CLAUDE.md` `merge_primitives` row; the point-of-change paragraph in `page.py`.
