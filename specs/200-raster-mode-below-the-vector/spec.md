# Feature 200 - raster mode below the vector

**Status**: DRAFT - awaiting `spec-fidelity` (constitution XVI).
**Request**: [`request.md`](request.md) - the GM's words verbatim, and the offer they accepted.
**Research**: [`research.md`](research.md) - the trace, the off-map census, the priced levers, the
prototype's numbers.
**Predecessors**: feature 199 (the tiled merge - the page this builds on, unchanged above the switch);
134 (the page, its FR-010 "the SVG and the PNG are untouched", and R5's refusal of raster layers for
blurring at 16x); 134 T37-T40 (the hit regions and widened copies, which the id map reproduces).

## Summary, and what changed from the offer

The GM accepted "the ground cover as a pre-rendered image at low zoom, the vector tiles above 4x" and
said every action - hover, scroll, zoom, load - still feels slow in Chrome. The measurement that
followed (research.md R1, R2) corrected the offer's mechanism in one respect, and the correction is the
first thing to know about this feature: **the ground cover is not the cost.** 96% of Kuwabata's scrub
blades lie outside the viewBox and are never drawn; the visible scrub is 7,456 blades; what a hover,
a scroll or a zoom costs is re-rasterizing ALL the visible ink - dikes, ponds, ditches, paddies, marsh,
scrub - and a prototype that pre-rendered only the ground cover left a wheel turn at 152-157 ms of
raster against 163-178 shipped. So the image is the WHOLE picture, and the highlight is the hovered
class's own vector drawn above it. The purpose the GM named - every action fast at the views a reader
uses, no loss of crispness at any zoom - is what the prototype measured (R4): 5-15x less raster work per
hover, scroll and zoom step at the opening view and the first zoom step; the vector page of feature 199
unchanged above the switch.

Two things ride along because the census exposed them: the off-map ink is dropped from the page
(invisible by construction, -90% of the path data, the page 9.8 -> 6.2 MB even with the images in), and
hit-testing in raster mode comes from a class id map rendered beside the picture.

## Functional requirements

### Off-map ink (FR-001 to FR-002)

- **FR-001** The page does not carry ink the viewBox clips. Inside a class group, a merged subpath, or
  a primitive with absolute coordinates (`circle`, `ellipse`, `line`, `rect`, `polygon`, `polyline`),
  whose extent lies wholly outside the viewBox expanded by `OFFMAP_MARGIN` (24 map px, wider than any
  stroke width or blob radius the writer emits) is not written. A group under a `<g transform>` ancestor,
  or a path in any grammar but the merge's own `M/L` and `M/a`, is never judged - its coordinates are
  local or its extent is not a matter of reading numbers. Measured (R2): 286,058 subpaths and 2,250
  elements on Kuwabata, all scrub and marsh; the page's vector picture is byte-for-byte the same
  where the viewBox shows it.
- **FR-002** The SVG and the PNG are untouched (feature 134 FR-010): the drop, like the merge and the
  tiling, is the HTML target's.

### The raster (FR-003 to FR-005)

- **FR-003** At page-write time the page's own SVG (every record string, the sheet, the hit regions and
  copies included - they paint nothing) is rendered by resvg, the map's own PNG renderer with the same
  font mapping, at `RASTER_R` = 3 px per map px, encoded as lossless WebP, and inlined as an `<image>`
  covering the viewBox, in a `g.raster` group placed ABOVE the sheet and BELOW the first class group (a
  first cut under the sheet showed bare parchment - R4).
- **FR-004** `RASTER_R` = 3.0, recorded with its measurement (R4): at 2 a DPR-2 screen's opening view of
  Kuwabata (1.31 x 2 = 2.62) is already past the switch; at 4 the decoded image doubles (Kuwabata 132 MB).
  At 3: Kuwabata 18.6 Mpx, 74 MB decoded, 2.95 MB on the page.
- **FR-005** The picture in raster mode is resvg's, downscaled to the screen: the map's PNG look.
  Measured against the vector page at the opening view: 52,088 of 1,400,000 pixels differ by more than
  8/255 (3.7%, anti-aliasing at edges); T06 repeats the comparison on the implementation over the pool
  pages, and a crop of each is compared by eye. This is a stated change to feature 134 FR-002's "the
  picture is unchanged": the GM asked for the hybrid knowing it renders an image at low zoom, and the
  image is the renderer's own picture of the same SVG.

### The two modes (FR-006 to FR-008)

- **FR-006** The page is in RASTER MODE while `screen scale x devicePixelRatio <= RASTER_R`, and in
  VECTOR MODE above it; `apply()` sets `data-mode` on the svg on every view change. In raster mode the
  `g.raster` image shows and every class group is hidden except the one carrying `.on` (hovered, pinned
  by an open modal, or peeked from a sibling link), which is drawn lit above the image by the existing
  highlight rules. In vector mode `g.raster` is hidden and the page is feature 199's, unchanged.
- **FR-007** Hit-testing in raster mode reads a CLASS ID MAP: the same SVG recolored one flat color per
  class (index x 5 in the red channel), with the hit geometry painted as the DOM would hit it - widened
  copies as strokes of their hit width, region rectangles and polygons as fills, the lifted layer and its
  clip as they are - every opacity stripped (inside and OUTSIDE the class groups), rendered by resvg
  with anti-aliasing off at 1 px per map px, PNG, inlined; `page.js` decodes it into a canvas at load and
  answers `pointermove` and `click` in raster mode from the pixel under the pointer, snapping a channel
  value to the palette's grid within +-2. Until the canvas is decoded (a few hundred ms after load) a
  move answers nothing. In vector mode the DOM answers, as today. Agreement with DOM hit-testing on the
  real Kuwabata page, 2,145 grid points: 98.2% (R4); the guard in FR-011 asks for 97%.
- **FR-008** The highlight in raster mode draws the lit class above everything: a crown that overhangs
  a lit farmhouse is under it while it is lit, where in vector mode it stays above. Accepted (D4): a
  highlight is a UI affordance, and the lit feature wholly visible is the more useful reading.

### What is proven, and how (FR-009 to FR-011)

- **FR-009** Unit tests: the drop (a subpath outside dropped, one crossing the margin kept, a transformed
  group untouched, a relative-command path untouched, a circle judged by its disc); the id-map recolor
  (fills, strokes, a widened copy, a region rectangle with its own `fill="none"`, a pattern fill, an
  opacity wrapper outside the group, the palette); the mode rule at DPR 1 and 2.
- **FR-010** The browser test on the Kuwabata fixture (feature 199): the page opens in raster mode; the
  id map is decoded; a real pointer over the scrub lights it and a click opens its modal; the id map
  agrees with the DOM on at least 97% of a grid of points; two zoom steps in switch to vector mode and
  `fit` switches back; the reference page's synthetic mechanics are unchanged.
- **FR-011** The gate's timing guards: feature 199's 40 ms pointer-move cap stays; and a new raster-CPU
  guard from the trace - hovering the scrub at Kuwabata's opening view rasterizes under 100 ms of
  `RasterTask` CPU (prototype 32-38; shipped 221-251), and one wheel turn under 60 ms (12-14; shipped
  163-178). CPU time added over threads is far less load-sensitive than wall time; the caps sit at 2.6x
  and 4x the prototype and fail the shipped page by 2x. Both shown red with raster mode disabled (SC-005
  of feature 199's form).

### Documentation (FR-012)

- **FR-012** `interactive/CLAUDE.md` gains the two modes and the id map; `page.py` carries the why at
  each point of change; feature 134 R5's refusal of raster layers is annotated as superseded for the
  low-zoom range only; the pool pages regenerate on landing.

### What this feature does not do (FR-013 to FR-015)

- **FR-013** It does not change any explanation, class, source or the SVG/PNG.
- **FR-014** It does not touch vector mode: above the switch the page is feature 199's, and its cost is
  the visible ink's (R4: a wheel turn at 4x 90-113 ms of raster, a pointer move 47-59) - the views where a
  1400 x 1000 viewport shows a 270 x 190 map-px window.
- **FR-015** It does not pre-render the highlighted state. Hovering the scrub still draws its visible
  blades lit as vector (32-38 ms of raster at the opening view) - the largest remaining number, and
  one the GM can judge on the page before anything more is built.

## Success criteria

- **SC-001** On Kuwabata's opening view, raster CPU per action (trace): hover the scrub under 60 ms,
  hover off under 20, hover a farmhouse under 15, a wheel turn under 25, a zoom step under 25
  (prototype: 32-38 / 9 / 0-6 / 12-14 / 10-12). Recorded in T06 for every pool page.
- **SC-002** Page size: every pool page smaller than before the feature (Kuwabata 9.8 -> 6.2 MB).
- **SC-003** Load under 1.0 s in the harness (prototype 0.59-0.67 s against 0.33-0.38).
- **SC-004** `make done` green; `make page-check` green; the Kuwabata page opened, hovered, clicked and
  zoomed across the switch by the session before the push.
- **SC-005** With raster mode disabled and nothing else changed, FR-010's mode assertion and FR-011's two
  raster-CPU caps fail; shown once.

## Decisions Recorded

- **D1 - one full-map image, not per-class images.** R2: the ground cover is not the cost; a lit image
  per class does not fit in memory. The highlight is the hovered class's own vector above the image.
- **D2 - 3 px per map px, lossless WebP.** R4's resolution paragraph; PNG is twice the bytes, lossy WebP
  rings on line art.
- **D3 - hit-testing from an id map.** The DOM cannot answer for hidden groups, and every way of keeping
  them answerable while unpainted either fails `visiblePainted` or lets a bund's interior take the
  pointer (R5). The id map reproduces the DOM's own rule in one render and agrees with it on 98.2% of
  points; the disagreements are single-pixel boundaries.
- **D4 - the lit class draws above everything in raster mode** (FR-008). Priced against keeping the
  stacking (which needs the covering elements drawn too, i.e. the vector page) and accepted.
- **D5 - the switch is on screen scale x devicePixelRatio**, so a retina screen leaves raster mode where
  the image would upsample, not where a DPR-1 screen would.
- **D6 - the off-map margin is 24 px**, wider than any stroke or blob the writer emits; a subpath that
  reaches inside by a pixel is kept.
- **D7 - resvg renders both images**, the picture with the PNG's own font mapping; the id map with
  anti-aliasing off (`--shape-rendering crispEdges`) because a blended edge is a wrong class.
- **D8 - the raster-CPU guard is a trace, not a wall clock** (FR-011): the sums over threads move by
  percent under load where wall time moves by multiples (feature 199 R6).
- **D9 - the highlighted state is not pre-rendered** (FR-015): the GM sees the page first.
