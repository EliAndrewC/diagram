# Feature 200 - raster mode below the vector

**Status**: FAITHFUL (`spec-fidelity`, round 4 of 5) - implemented; SC-001 missed by 1-3 ms on two pages
and SC-003 within the noise floor, both recorded in research.md R6 rather than moved. Four rounds is one
under the cap: each amendment left a sentence of the earlier draft alive one requirement over, and the
whole-spec search for the mechanism (round 4) is what finally closed it. Round 3 returned one item: FR-007
still said a move "answers nothing" until the id map is decoded - the raster-first draft's clause one
requirement over from the one round 2 fixed (now: no such interval, the DOM answers in vector mode); the
whole spec was then searched for every clause about the pre-decode interval, and that was the last.
Round 2 returned one item: FR-010
still said the page "opens in raster mode" against FR-016's vector-first frame (now an ordered pair of
assertions, (a) vector first, (b) raster entered; SC-005 names (b)); its aside on which reading of
today's load SC-003 measures against is taken. Round 1 returned three items, none
against the design: the first load (one of the GM's four actions) regressed without the spec saying so
(now FR-016, SC-003 and D10 - the page enters raster mode only once the image is decoded, so the first
frame is the vector page at today's cost); the switch was stated in units the offer did not use (now
FR-004/FR-006/D5 give it in zoom multiples at DPR 1 and 2, and say plainly that a DPR-2 screen gets
raster mode at the opening view only); the off-map drop was justified as a ride-along (now FR-001 ties
it to the first-load clause with its measurement, 0.83 -> 0.58 s).
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

Two further requirements follow from the GM's four actions and from the design. The FIRST LOAD is one
of the four, and the image costs a decode the vector page never paid: the page therefore drops the
off-map ink the census exposed (invisible by construction; without it the hybrid loads in 0.83 s
against 0.58 with it, and today's 0.36 - R4), and it enters raster mode only once the image is decoded,
so the first frame is the vector page at today's cost (FR-016). And hiding the class groups takes away
the DOM's answer to "what is under the pointer", so hit-testing in raster mode comes from a class id map
rendered beside the picture (FR-007).

## Functional requirements

### Off-map ink (FR-001 to FR-002)

- **FR-001** The page does not carry ink the viewBox clips - THIS SERVES THE FIRST LOAD, the fourth of
  the GM's four actions: the hybrid's image costs a decode, and the off-map ink is the one cost of the
  page that can be given back without changing a pixel. Measured (R4, four runs each): today's page
  loads in 0.36 s; the hybrid with the off-map ink kept in 0.83 s at 14.2 MB; with it dropped in 0.58 s
  at 6.1 MB. Inside a class group, a merged subpath, or
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
- **FR-004** `RASTER_R` = 3.0 px per map px, recorded with its measurement (R4): at 2 a DPR-2 screen's
  opening view of Kuwabata is already past the switch; at 4 the decoded image doubles (Kuwabata 132 MB).
  At 3: Kuwabata 18.6 Mpx, 74 MB decoded, 2.95 MB on the page. **The switch, in the offer's units.** The
  SCREEN SCALE is `view.s` in `page.js` - CSS px per map px, what the browser draws one map px as; the
  zoom buttons and `data-zoom` count multiples of the FIT scale (`view.s / view.fit`), and the offer's
  "above 4x" was in those multiples. Raster mode holds while `view.s x devicePixelRatio <= RASTER_R`,
  i.e. while the image would not be upsampled. On Kuwabata in a 1400 x 1000 viewport (fit 0.519, the
  opening view 1.308 = 2.5x fit, each `+` doubling): on a DPR-1 screen raster mode holds to 5.8x fit -
  the opening view and the first `+` (5.0x) are raster, the second `+` (10.1x) is vector; on a DPR-2
  screen it holds to 2.9x fit - THE OPENING VIEW ONLY, and the first `+` is vector. The offer's "above
  4x" is met on a DPR-1 screen and not on a DPR-2 one, where the image would blur at the first step.
  D5 records the consequence and the follow-up.
- **FR-005** The picture in raster mode is resvg's, downscaled to the screen: the map's PNG look.
  Measured against the vector page at the opening view: 52,088 of 1,400,000 pixels differ by more than
  8/255 (3.7%, anti-aliasing at edges); T06 repeats the comparison on the implementation over the pool
  pages, and a crop of each is compared by eye. This is a stated change to feature 134 FR-002's "the
  picture is unchanged": the GM asked for the hybrid knowing it renders an image at low zoom, and the
  image is the renderer's own picture of the same SVG.

### The two modes (FR-006 to FR-008)

- **FR-006** The page is in RASTER MODE while `view.s x devicePixelRatio <= RASTER_R` (FR-004 defines
  both), and in VECTOR MODE above it; `apply()` sets `data-mode` on the svg on every view change, and
  never to raster before the image and the id map are decoded (FR-016). In raster mode the
  `g.raster` image shows and every class group is hidden except the one carrying `.on` (hovered, pinned
  by an open modal, or peeked from a sibling link), which is drawn lit above the image by the existing
  highlight rules. In vector mode `g.raster` is hidden and the page is feature 199's, unchanged.
- **FR-007** Hit-testing in raster mode reads a CLASS ID MAP: the same SVG recolored one flat color per
  class (index x 5 in the red channel), with the hit geometry painted as the DOM would hit it - widened
  copies as strokes of their hit width, region rectangles and polygons as fills, the lifted layer and its
  clip as they are - every opacity stripped (inside and OUTSIDE the class groups), rendered by resvg
  with anti-aliasing off at 1 px per map px, PNG, inlined; `page.js` decodes it into a canvas at load and
  answers `pointermove` and `click` in raster mode from the pixel under the pointer, snapping a channel
  value to the palette's grid within +-2. Raster mode is not entered until the canvas is filled
  (FR-010 (a), FR-016), so there is no interval in which a move goes unanswered: before the decode the
  page is in vector mode and the DOM answers, as today, and it keeps answering in vector mode after. Agreement with DOM hit-testing on the
  real Kuwabata page, 2,145 grid points: 98.2% (R4); the guard in FR-011 asks for 97%.
- **FR-008** The highlight in raster mode draws the lit class above everything: a crown that overhangs
  a lit farmhouse is under it while it is lit, where in vector mode it stays above. Accepted (D4): a
  highlight is a UI affordance, and the lit feature wholly visible is the more useful reading.

### What is proven, and how (FR-009 to FR-011)

- **FR-009** Unit tests: the drop (a subpath outside dropped, one crossing the margin kept, a transformed
  group untouched, a relative-command path untouched, a circle judged by its disc); the id-map recolor
  (fills, strokes, a widened copy, a region rectangle with its own `fill="none"`, a pattern fill, an
  opacity wrapper outside the group, the palette); the mode rule at DPR 1 and 2.
- **FR-010** The browser test on the Kuwabata fixture (feature 199), in this order: (a) the page's
  FIRST frame is in vector mode - `data-mode` is not `raster` before the image and the id map have
  decoded (FR-016; this is the assertion SC-003's first half refers to); (b) once both are decoded the
  page ENTERS raster mode at the opening view; (c) a real pointer over the scrub lights it and a click
  opens its modal; (d) the id map agrees with the DOM on at least 97% of a grid of points; (e) two zoom
  steps in switch to vector mode and `fit` switches back; (f) the reference page's synthetic mechanics
  are unchanged. With raster mode disabled, (b) is the assertion that fails (SC-005) - (a) stays true.
- **FR-011** The gate's timing guards: feature 199's 40 ms pointer-move cap stays; and a new raster-CPU
  guard from the trace - hovering the scrub at Kuwabata's opening view rasterizes under 100 ms of
  `RasterTask` CPU (prototype 32-38; shipped 221-251), and one wheel turn under 60 ms (12-14; shipped
  163-178). CPU time added over threads is far less load-sensitive than wall time; the caps sit at 2.6x
  and 4x the prototype and fail the shipped page by 2x. They are deliberately LOOSER than SC-001's
  criteria for the same two measurements (60 and 25): SC-001 is what the session records on an idle
  box, the gate cap is what a loaded FULL run must clear without flaking (feature 199 R6's lesson). Both shown red with raster mode disabled (SC-005
  of feature 199's form).

### The first load (FR-016)

- **FR-016** The first frame costs what it costs today. The page opens in vector mode and enters raster
  mode only when the picture's `<image>` has fired `load` and the id map's canvas is filled; the two
  pictures are the same to the eye (FR-005), so the switch is invisible, and hovering in the interval
  answers from the DOM as today. Measured on the prototype, which decoded before its first frame: load
  event 0.58 s against today's 0.36, the id map ready at 0.62 (R4); with vector-first the first frame
  is today's and raster mode follows within the same interval. The remaining cost of the image is
  stated in D10.

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

- **SC-001** (R6: holds on Kuwabata, Kashikawa, Mizuguchi; the wheel and zoom criteria MISSED by 1-3 ms on
  Inashiro and Sawada - 26/25 and 28/27 against 25 - reported, not moved.) On Kuwabata's opening view, raster CPU per action (trace): hover the scrub under 60 ms,
  hover off under 20, hover a farmhouse under 15, a wheel turn under 25, a zoom step under 25
  (prototype: 32-38 / 9 / 0-6 / 12-14 / 10-12). Recorded in T06 for every pool page.
- **SC-002** Page size: every pool page smaller than before the feature (Kuwabata 9.8 -> 6.2 MB).
- **SC-003** (R6: within +0.10 s on three pages and earlier on two - the run-to-run spread of one page,
  so "the same to within a tenth" rather than a clean pass.) The first frame no later than today's - the median of four harness runs on Kuwabata,
  0.38 s to the first frame (the load event 0.36; R4 records a 0.33-0.38 s spread) - and raster mode
  ready within 0.8 s of navigation (prototype 0.62). Both TIMINGS are recorded in T06 by the same
  instrument on the same day; the MODE of that first frame - vector, which is what keeps its cost at
  today's - is the assertion FR-010 (a) makes in the browser test. Two claims, one criterion.
- **SC-004** `make done` green; `make page-check` green; the Kuwabata page opened, hovered, clicked and
  zoomed across the switch by the session before the push.
- **SC-005** With raster mode disabled and nothing else changed, FR-010 (b) and FR-011's two raster-CPU
  caps fail; shown once.

## Decisions Recorded

- **D1 - one full-map image, not per-class images.** R2: the ground cover is not the cost; a lit image
  per class does not fit in memory. The highlight is the hovered class's own vector above the image.
- **D2 - 3 px per map px, lossless WebP.** R4's resolution paragraph; PNG is twice the bytes, lossy WebP
  rings on line art.
  AMENDED by feature 203 (its R3): the encode is method 0, not 4 - still lossless, 2.2 s instead of 9.6 per
  page write for 8% more bytes; the gate's duration ratchet found the difference.
- **D3 - hit-testing from an id map.** The DOM cannot answer for hidden groups, and every way of keeping
  them answerable while unpainted either fails `visiblePainted` or lets a bund's interior take the
  pointer (R5). The id map reproduces the DOM's own rule in one render and agrees with it on 98.2% of
  points; the disagreements are single-pixel boundaries.
- **D4 - the lit class draws above everything in raster mode** (FR-008). REVISED by feature 201 (GM
  2026-09-07: a solid lit paddy hid its bunds, beans and ponds): still above everything, but its filled
  shapes at 0.45 opacity, so what it covers shows through. Priced against keeping the
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
- **D10 - the image's decode is the first load's new cost, and it is taken off the first frame rather
  than shrunk.** The hybrid adds a 2.95 MB lossless WebP (18.6 Mpx) and a 0.3 MB id map that the browser
  decodes on load; measured 0.36 -> 0.58 s to the load event with the off-map ink dropped (0.83 with it
  kept). Priced: lossy WebP (0.73 MB, rings on line art - declined, D2); a lower resolution (fails a
  DPR-2 screen's opening view - declined, FR-004); deferring the id map (it is 0.04 s of the 0.22). What
  is done instead is FR-016: the page paints the vector picture first, at today's cost, and switches
  when the image is ready. The decode still happens, ~0.25 s after the first frame, and the GM is shown
  the number.
- **D5, continued - a DPR-2 screen.** If the GM's screen is DPR 2 (Chrome reports it as
  `devicePixelRatio`), raster mode covers the opening view and no zoom step, and the improvement they
  see is bounded to that view. The follow-up, not built here because it doubles the page again, is a
  second image at 6 px per map px decoded on first use - a two-level pyramid that would carry a DPR-2
  screen through the first `+`.
