# Research - 201 Raster mode keeps the neighbors

RENDERING research, nothing physical. Measured 2026-09-07 in headless Chromium on the feature-200 Kuwabata
page as regenerated on main, with feature 200's instrument: a Chrome DevTools trace summed per action,
`RasterTask` CPU in ms over Chromium's worker threads. Scratch: `proto4.py` and the `hyb3`/`hyb4*` page
variants in the session scratchpad.

## R1. The two defects, and their one mechanism

Both are consequences of feature 200's raster mode drawing the lit class ABOVE an image of the whole
picture and hiding every other class GROUP:

- **The paddy.** The paddy fill polygons are lit above the image, so their solid gold covers the bunds,
  the beans and the field ponds - which in the vector page are drawn AFTER the paddies and so sit above
  them. Feature 200 recorded this as D4 ("a lit feature is drawn above everything"); the GM finds it
  breaks the page's purpose on the paddy, the largest fill class: the reader can no longer see where to
  move the mouse to reach the features on it.
- **The placard and the scale.** The scale bar's text is not in a class group (it is a `-` tagged, never
  highlighted string), so feature 200 hid no part of it: it is drawn as vector text OVER the image's own
  copy of it, rendered by resvg in DejaVu Serif where Chrome draws Georgia or its fallback - two fonts,
  slightly different metrics, on top of each other ("two different lines of text overlapped"). The
  placard's name, in the `place` class, is hidden until lit and then drawn in the browser's font over
  the image's resvg rendering - the "different font" the GM saw on the lit card. The crops
  `placard-shipped-unlit.png` / `placard-shipped-lit.png` (scratchpad) show both.

## R2. Exact stacking was priced and is too dear

The exact answer - while a class is lit, show every class group drawn AFTER it, unlit, so the bunds and
beans sit above the gold as they do on the vector page - was prototyped (`hyb3`), with the groups shown
by `visibility` (so text could stay visible) and by `display`:

| action | shipped 200 | later groups shown |
|---|---|---|
| hover the paddy | 40 | 223 |
| hover the scrub | 30 | 98 |
| hover a bund | 5 | 74 |
| hover a farmhouse | 6 | 51 |
| one wheel turn, nothing lit | 16 | 168 |

Two findings. Showing the groups after the paddy is most of the map's vector ink, so entering the
paddy costs what the vector page cost - the old number back on the largest class. And hiding by
`visibility: hidden` instead of `display: none` made a wheel turn with NOTHING lit ten times dearer
(16 -> 168): Chromium still walks visibility-hidden SVG content at raster. Both declined.

## R3. A mask from an ink-only id map was priced and is unusable in Chrome

A second exact answer: draw the lit class through an SVG `<mask>` whose source is an ink-only id map
(feature 200's id map without the hit geometry) passed through an `feComponentTransfer` that selects
the lit class's palette value - so the gold appears only where the class is really on top, and every
bund, bean and pond stays visible as the image's own pixels (`hyb4a`):

| action | shipped 200 | masked lit class |
|---|---|---|
| hover the paddy | 34 | 424 |
| hover off | 4 | 760 |
| hover a bund | 5 | 267 |
| one wheel turn, nothing lit | 17 | 1,099 |

A masked group with a 2 Mpx filtered image mask costs 300-800 ms per hover and, with the mask element
merely present, a wheel turn with nothing lit went from 17 to 1,099 ms - the mask defeats Chromium's tile
caching for the whole layer. Declined outright.

## R4. What works: leaf hiding, text as vector, a translucent wash

`hyb4b`/`hyb4c`/`hyb4d`, the same run as the shipped numbers:

| action | shipped 200 | leaf hiding + text vector + wash |
|---|---|---|
| hover the paddy | 34 | 21 |
| hover the scrub | 30 | 30 |
| hover a bund | 5 | 5 |
| hover the placard | 1 | 2 |
| one wheel turn, nothing lit | 17 | 12 |

- **Leaf hiding.** Raster mode hides the LEAF INK (`path`, `circle`, `ellipse`, `line`, `rect`,
  `polygon`, `polyline`, `image`) that is not inside a lit group, the raster image or `<defs>` - one
  selector, `:not(g.f.on *)` - instead of hiding class groups. Every `<text>` therefore stays displayed
  in both modes, whatever wraps it, and the sheet-level ink (the scale bar's lines, the sheet) is hidden
  too, which the group rule never reached. Measured: 7 leaf elements displayed with nothing lit, all 4
  text elements displayed, a lit stream inside its `<g opacity>` wrapper shows its 4 leaves (a first
  draft that hid the sheet level by a separate rule would have hidden them).
- **Text is never in the picture.** The picture is rendered from the page's SVG with every `<text>`
  removed, so the only text on the page is the browser's, in both modes and both states: the scale
  reads once, the placard's name is one font lit or unlit. The id map keeps its text (a caption is hit
  as its class).
- **The wash.** In raster mode a lit class's FILLED shapes are drawn at `fill-opacity` 0.45 over the
  image, so the bunds, beans and ponds beneath show through the gold; strokes stay solid gold; text
  stays at full opacity (the first draft put the opacity on the group and the placard's name inherited
  it - `placard-C-lit.png`). Crops: `lit-paddy-shipped.png` against `lit-paddy-C.png`. The GM's words
  allow this: "I don't think that we need to necessarily recreate an exact lit up version"; the exact
  version is R2's cost, and R2's cost is the thing feature 200 exists to remove. The vector page above
  the switch is unchanged: solid gold, the bunds drawn crisply above.

The number 0.45 is a rendering constant chosen by eye on that one crop - the bunds legible through the
gold, the gold still reading as a highlight against the paddy's green - and NOT swept: no other value
was rendered. It is the GM's to move on sight, in one constant.

## R5. The implementation on the regenerated page (T05, SC-004)

Kuwabata as regenerated by the green gate, raster mode at the opening view, crops kept in the session
scratchpad (`201-lit-paddy.png`, `201-lit-well.png`, `201-lit-bund.png`, `201-placard-unlit.png`,
`201-placard-lit.png`): a lit paddy shows the dikes, the pond edges and the ridging through the gold; a
lit well - the review's aside, a small class judged beside the paddy - reads as a pale gold square,
still plainly the highlight; the placard's name is the ink at full opacity in the same font lit and
unlit, and the scale reads once. The gate's own reading of the new browser test: every text element
displayed, no leaf ink outside a lit group, the wash 0.45, a lit stream's ink shown.

The gate found one more thing: `test_page_browser.py` crossed the 1,000-line bar with this feature's
test (1,020) and constitution X clause 13 is gated, so it became the package
`tests/full/interactive/page_browser/` (a conftest with the browser and the three pages, a driver, and
the synthetic, reference and speed test modules), the `page-check` target and its test repointed.
