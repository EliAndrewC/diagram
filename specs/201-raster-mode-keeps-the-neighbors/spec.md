# Feature 201 - raster mode keeps the neighbors

**Status**: FAITHFUL (`spec-fidelity`, round 1 of 5) - implemented. Its aside - a crop of a small lit class
beside the paddy's, so the wash constant can be judged on both - is taken in research.md R5.
**Request**: [`request.md`](request.md) - the GM's words verbatim, two defects seen on the feature-200
pages.
**Research**: [`research.md`](research.md) - the mechanism, the two exact answers priced and declined,
and the answer that costs nothing.
**Predecessors**: feature 200 (raster mode: the image, the lit class above it, the hidden groups, the id
map - and its D4, "the lit class draws above everything", which this feature revises); 134 (the highlight
rules in `page.css`, and "the name stays readable on the lit placard").

## Summary

Two defects, one mechanism (research.md R1). Feature 200 draws the lit class above an image of the whole
picture and hides every other class GROUP. So a lit paddy's solid gold covers the bunds, beans and field
ponds that the vector page draws above it - the GM: *"I can no longer see where the earthen bunds are
Or the bund beans or the field ponds"* - and the scale bar, which is in no class group, is drawn as
vector text over the image's own copy of it in a different font, while the placard's name is hidden
until lit and then drawn in the browser's font over the image's - *"two different lines of text are
overlapped"*, *"the font and font size of the lit up version of the title card is different"*.

Three changes to raster mode, none to the vector page: text is never in the picture and always vector
(so there is one scale, and one placard name in one font, lit or unlit); raster mode hides LEAF INK
outside the lit class rather than class groups (so text stays, whatever wraps it, and the sheet-level
ink is hidden too); and a lit class's filled shapes are drawn as a translucent wash, so the bunds,
beans and ponds beneath show through the gold. The GM allowed the inexact route (*"I don't think that we
need to necessarily recreate an exact lit up version"*) provided the exact one was not easy; both exact
answers were priced (R2, R3) and cost the very thing feature 200 removed - the wash costs nothing (R4).

## Functional requirements

### Text is vector (FR-001 to FR-002)

- **FR-001** The picture is rendered from the page's SVG with every `<text>` element removed. The id map
  keeps its text: a caption is hit as its class, as on the vector page.
- **FR-002** In raster mode, what is hidden is LEAF INK - `path`, `circle`, `ellipse`, `line`, `rect`,
  `polygon`, `polyline`, `image` - that is not inside a lit (`.on`) class group, not the raster image and
  not inside `<defs>`; one selector. Every `<text>` on the page is displayed in both modes and both
  states, so the scale reads once, in the browser's font, and the placard's name is the same font and
  size lit or unlit. The sheet-level ink - the scale bar's lines, the sheet - is hidden by the same rule,
  which feature 200's group rule never reached. Measured (R4): 7 leaves displayed with nothing lit, all
  text displayed, a lit class inside an opacity wrapper shows its ink.

### The lit class over the image (FR-003 to FR-004)

- **FR-003** In raster mode a lit class's FILLED shapes (`path`, `circle`, `ellipse`, `rect`, `polygon`,
  `polyline` with a fill) are drawn at `fill-opacity` `LIT_WASH` = 0.45; strokes stay the solid highlight
  stroke; text stays at full opacity and the placard's name in the map's ink (feature 134's rule). So
  the bunds, beans and ponds beneath a lit paddy show through the gold, and the reader can see where to
  move the mouse. The opacity is on the shapes, never on the group - a first draft put it on the group
  and the placard's name inherited it (R4).
- **FR-004** The vector page above the switch is unchanged: a lit class is solid gold and the classes
  drawn after it sit above it, exactly as before.

### What is proven (FR-005 to FR-006)

- **FR-005** Unit tests: `raster.without_text` strips every `<text>`, multi-line and attributed, and
  nothing else; a rendered picture of a document with text has none of its pixels (the text's color is
  absent) while the id map of the same document paints the text in its class's color.
- **FR-006** The browser test on the Kuwabata fixture, in raster mode: every `<text>` on the page is
  displayed and every displayed leaf outside `<defs>` and the raster image is inside a lit group (with
  nothing lit, at most the handful `<defs>` holds); the placard's name lit has the ink fill at opacity 1
  and the same computed font as unlit; a lit paddy shape has fill-opacity 0.45 and a lit stream inside
  its opacity wrapper has its ink displayed; the feature-200 raster-CPU caps still hold (R4: unchanged).
  With the leaf rule reverted to feature 200's group rule, the text assertion fails - shown once (SC-003).

### Documentation (FR-007)

- **FR-007** `interactive/CLAUDE.md`'s `raster.py` row and feature 200's D4 are amended; the why at each
  point of change in `page.css` and `raster.py`.

### What this feature does not do (FR-008 to FR-009)

- **FR-008** It does not recreate the exact lit picture in raster mode (R2, R3: 170-220 ms per entry
  into the paddy, or 300-1,100 ms per action with a mask). The GM's words allow this and the trade is
  recorded in D1; the vector page is the exact picture, one zoom step past the switch.
- **FR-009** It does not change the highlight colors, the id map, the switch, or anything on the vector
  page.

## Success criteria

- **SC-001** Kuwabata's opening view: raster CPU per action within feature 200's figures (hover the paddy
  under 60 ms, the scrub under 60, a wheel turn under 25); R4 measured 21 / 30 / 12.
- **SC-002** The page carries one scale text and one placard name, each displayed exactly once in each
  mode, and the lit placard's computed font equals the unlit one's.
- **SC-003** With FR-002's rule replaced by feature 200's group rule, the text assertion of FR-006 fails;
  shown once.
- **SC-004** `make done` green; the Kuwabata page opened by the session in raster mode with the paddy
  and the placard lit, crops kept in research.md.

## Decisions Recorded

- **D1 - a wash, not the exact stacking.** Exact stacking by showing the later groups costs 223 ms of
  raster on the paddy (R2); exact stacking by a mask costs 300-1,100 ms and breaks tile caching (R3). The
  GM allowed the inexact version; the wash costs nothing and shows what the GM asked to see. If the GM
  wants the exact picture on the paddy, R2's mechanism is the one to build and its cost is the number
  above.
- **D2 - `LIT_WASH` = 0.45**, chosen by eye on one crop and not swept (R4); one constant for the GM to
  move on sight.
- **D3 - text is vector everywhere**, and the picture carries none: the only way two fonts never meet.
  Its cost is nothing measurable (the page's four text elements).
- **D4 - leaf hiding replaces group hiding**, so text survives and the sheet level is covered; the
  `visibility` alternative was measured at ten times the wheel cost and declined (R2).
- **D5 - feature 200's D4 is revised**: a lit class is still drawn above everything in raster mode, but
  translucently, so what it covers remains visible.
