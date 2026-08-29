# Plan: feature 148 - the interactive map's hover cost

## Constitution Check

- **VI (verification before done)** - the change is measured on both pages before and after, by the two
  numbers the GM's report names: the geometry the browser hit-tests, and load to first interaction.
  `make done` green; the pool maps gate clean.
- **X (100% on pure logic)** - `page.py` is pure string work over the record streams; every branch the
  change adds is reachable from `tests/interactive/test_page.py` without a browser.
- **XII (record the why)** - this is a RENDERING decision, not a physical one: nothing about how a hamlet
  was built changes. The why goes at the point of change in `page.py` and in `interactive/CLAUDE.md`.
- **XIII (no known regressions)** - the browser test is the oracle for "hover is unchanged", and FR-006
  strengthens it before the change lands rather than after.
- **XVI (build what was asked)** - the spec was narrowed to the GM's two classes at `spec-fidelity`'s
  insistence; the general rule is deferred as a separate ask.

## The mechanism, as it stands today

`render_page` wraps each record-stream string in `<g class="f f-<key>" data-k="<key>">` and inserts the
hit regions just after the sheet, at the BOTTOM of the stack. Hover is the browser's: `pointerover` on
the SVG, `e.target.closest("g.f")`. So every drawn element is a hit-test candidate, and for the scatter
classes those elements are merged `<path>`s carrying tens of thousands of stroked subpaths.

## The change

One attribute, on two classes' ink groups: `pointer-events: none`. The region already beneath them then
resolves the hover, because nothing above it in those two classes can take the pointer any more. Nothing
else moves - not the draw order, not the record, not the SVG or the PNG.

The guard FR-002 asks for is a coverage test at page-write time: for each of the two classes, every mark
the class draws must fall inside the region that will answer for it. Where that does not hold the ink
keeps its hit-testing, and the page is honest rather than fast.

## Sequence

Measure, then change, then measure again - the middle step is one line and the two ends are the feature.
