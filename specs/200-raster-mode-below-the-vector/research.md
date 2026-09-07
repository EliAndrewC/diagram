# Research - 200 Raster mode below the vector

All RENDERING research (how Chrome paints the page), nothing physical. Measured 2026-09-07 in headless
Chromium through Playwright, viewport 1400 x 1000, on the pool pages as regenerated on main after feature
199 (commit `5a396225`). Two instruments from feature 199's record carry over - the real pointer sweep
(150 `mouse.move`s, mean wall ms per move; floor ~17 ms) - and one is new: a **Chrome DevTools trace**
(CDP `Tracing`, categories `devtools.timeline` + `cc`) summed per event name over one action, so
`RasterTask` is the rasterizer CPU that action cost, added over the worker threads. On this 22-thread
box the wall time is a fraction of it; on a four-core laptop it is close to what the reader waits. The
scratch scripts are `trace.py`, `measure2.py`, `variants2.py`, `proto.py`, `proto2.py`, `measure3.py`
in the session scratchpad; the method is recorded here so it can be re-run from the description.

## R1. What the tiling left: rasterizing the visible ink, on every hover, scroll and zoom

Feature 199 stopped Chromium replaying a whole 87,000-subpath path for every screen tile; the pointer
sweep fell to its floor. The GM: *"that is better but still slow"*. The trace says what is left, on
the tiled Kuwabata page at the opening view (raster CPU, ms):

| action | tiled page |
|---|---|
| hover the scrub (on) | 118-251 |
| hover off | 108-123 |
| hover a farmhouse | 42-52 |
| hover the paddies | 57 |
| one wheel turn, opening view | 163-178 |
| one wheel turn again | 97-105 |
| one zoom step | 57-68 |
| one wheel turn at 2x | 55-63 |
| one wheel turn at 4x | 83-113 |
| one real pointer move at 4x | 38-58 |

(Ranges are three runs of the same measurement.) A hover on a map-spanning class invalidates the
class's box - the viewport - and every tile in it is re-rasterized with ALL the ink it holds; a scroll
rasterizes the newly exposed tiles; a zoom step rasterizes everything. That is the cost the GM feels.
Anti-aliasing is not it: `shape-rendering: optimizeSpeed` on the scatter saved 8% (118 -> 109).

## R2. Where the ink is: 90% of the page's subpaths lie OUTSIDE the viewBox

Censusing every pool page's class groups against the viewBox (a margin of 12 px; transformed groups
excluded - their coordinates are local, and a first census that judged them reported every farmhouse
"outside"):

| page | viewBox | subpaths | outside | scrub outside | marsh outside |
|---|---|---|---|---|---|
| inashiro | 1708 x 1738 | 292,025 | 78% | 191,668 of 230,886 (83%) | 33,556 of 55,421 (61%) |
| kashikawa | 1276 x 2122 | 404,094 | 90% | 280,503 of 301,399 (93%) | 79,885 of 95,393 (84%) |
| kuwabata | 1070 x 1928 | 316,544 | 90% | 249,387 of 259,321 (96%) | 34,117 of 46,922 (73%) |
| mizuguchi | 1648 x 1590 | 236,750 | 75% | 149,789 of 183,066 (82%) | 26,664 of 48,030 (56%) |
| sawada | 2054 x 1214 | 436,034 | 92% | 316,240 of 335,576 (94%) | 81,221 of 93,540 (87%) |

The generator scatters the hinterland commons over the whole commons polygon and the viewBox is cropped
to the settlement, so the page carries the scatter it will never show. Kuwabata's VISIBLE scrub is
7,456 blades. Two consequences: the visible scrub is not what a repaint costs (it is everything -
the dike's 5,071 circles, the ponds, the ditches, the paddies, the marsh); and dropping off-map ink
from the page is invisible by construction (the viewBox clips it) and removes 90% of the path data.

This corrects the offer the GM accepted, which named "the ground cover" as the thing to pre-render.
Per-class ground-cover images were prototyped first (`proto.py`: scrub and marsh as image pairs at
their own z-positions): the scrub image came out 1% opaque because 96% of its blades are off-map, and
with the ground cover as images the wheel turn at the opening view still cost 152-157 ms of raster -
the rest of the map. So the raster has to be the WHOLE picture, and the highlight has to come from
somewhere other than a per-class image pair (47 classes x a full-map image each is 47 x 74 MB decoded).

## R3. Three levers priced on page variants (trace, raster CPU ms, Kuwabata)

| action | tiled (shipped) | pan by compositor transform | ground cover in its own layer | scatter without anti-aliasing |
|---|---|---|---|---|
| hover the scrub | 118 | 148 | 70 | 109 |
| hover a farmhouse | 42 | 44 | 20 | 48 |
| wheel, opening view | 173 | 323 | 251 | 158 |
| wheel again | 98 | 12 | 2 | 97 |
| zoom step | 57 | 176 | 181 | 70 |
| wheel at 2x | 59 | 5 | 5 | 60 |
| real pointer move at 4x | 47 | 85 | 77 | 41 |

A composited layer keeps its tiles across scrolls (the repeated wheel turn falls to nothing) but
pre-rasterizes beyond the viewport, so every zoom step and first exposure costs 2-3x more, and the
main-thread `Paint` rose from 13-30 ms to 43-100 ms per action. Neither layer variant helps the zoom the
GM named. Declined.

## R4. The hybrid, prototyped on the real page (`proto2.py`, `measure3.py`)

The prototype: off-map ink dropped (R2); ONE full-map image of the normal picture, rendered by resvg
(the map's own PNG renderer) at 3 px per map px, lossless WebP, placed above the sheet and below every
class group; while screen scale x devicePixelRatio <= 3 the page is in RASTER MODE - the image shows,
every class group is hidden except the highlighted one, which is drawn lit as vector on top; above that
scale the page is the vector page of feature 199. Hit-testing in raster mode reads a CLASS ID MAP: the
same SVG recolored one flat color per class (fills, strokes, and the hit geometry - widened copies as
strokes of their hit width, region rectangles and polygons as fills), every opacity stripped, rendered
by resvg without anti-aliasing at 1 px per map px, decoded into a canvas at load.

Kuwabata, the same run, shipped page against the prototype (raster CPU ms; wall for the sweep):

| action | shipped | hybrid | |
|---|---|---|---|
| hover the scrub (on) | 221-251 | 32-38 | raster mode: the scrub's 7,456 visible blades drawn lit |
| hover off | 109-123 | 9 | |
| hover a farmhouse | 43-52 | 0-6 | |
| wheel, opening view | 163-178 | 12-14 | |
| wheel again | 97-105 | 11-15 | |
| zoom step (to 2x) | 62-69 | 10-12 | |
| wheel at 2x | 55-63 | 10-12 | still raster mode at DPR 1 |
| zoom step (to 4x) | 42-49 | 47-55 | the switch to vector mode: its first raster |
| wheel at 4x | 83-113 | 90-113 | vector mode, unchanged |
| real pointer move at 4x | 38-58 | 47-59 | vector mode, unchanged |
| pointer sweep, opening (mean / max) | 17.4 / 35 | 16.9 / 34 | both at the instrument's floor |
| load (headless) | 0.33-0.38 s | 0.59-0.67 s | decoding a 2.95 MB WebP and the id map |
| page | 9.8 MB | 6.2 MB | -3.6 MB of off-map ink, +3.9 MB of base64 image, +0.4 MB id map |

So at the opening view and the first zoom step - the views a reader spends most time in - every action
is 5-15x cheaper in raster CPU. Above the switch the page is what feature 199 shipped, and its cost is
the visible ink's; at 4x on a 1400 x 1000 viewport the ink is a 270 x 190 map-px window.

**Resolution.** 3 px per map px. At 2, a DPR-2 laptop's opening view of Kuwabata (screen scale 1.31 x 2
= 2.62) would already be vector mode - the GM would see no change on such a screen; at 4 the decoded
image doubles (Kuwabata 33 Mpx, 132 MB; Sawada 40 Mpx). At 3: Kuwabata 3210 x 5784 = 18.6 Mpx, 74 MB
decoded; the WebP is 2.95 MB (PNG 5.7); the opening view stays raster at DPR 2, and at DPR 1 the first
zoom step too. Lossless WebP over PNG halves the bytes; lossy WebP at q90 was 0.73 MB but rings on line
art and was not used.

**The id map's agreement with DOM hit-testing**, on the same page with the vector groups shown, 2,145
grid points: first cut 73.8% - three systematic gaps (the marks-region rectangles carry their own
`fill="none"`; the wrappers `<g opacity>` OUTSIDE the class groups blended every color off the palette;
pattern fills), then **98.2%**. Of the 38 that remain, 8 are under the zoom buttons (the DOM hits the
button) and the rest are single-pixel boundaries between two classes. Values read from the canvas are
snapped to the palette's 5-grid within +-2, because a PNG round-trip can move a channel by one.

**The picture.** Raster mode is resvg's rendering downscaled to the screen - the same renderer and the
same look as the map's PNG. 52,088 of 1,400,000 pixels differ by more than 8/255 from the vector page at
the opening view (3.7%) - anti-aliasing at every edge, a crop compared by eye is the same picture; above
the switch the vector page is unchanged. A first cut put the image UNDER the sheet and showed bare
parchment (877,945 pixels differing) - the image belongs above the sheet, below the first class group.

**What the hybrid does not change**: hovering the scrub still draws its visible blades lit as vector
(32-38 ms - the largest remaining number at the opening view); the vector mode above the switch.

## R5. What was declined, and why

- **Per-class image pairs** (the offer's letter): R2 - the ground cover is not the cost, and a lit image
  per class does not scale. The highlight is the hovered class's own vector, drawn above the image.
- **Keeping the vector groups hit-testable while hidden** (`pointer-events` tricks on unpainted shapes):
  an unpainted shape is not a target under `visiblePainted`, and `visible`/`all` would let a bund's
  interior take the pointer over its paddy. The id map reproduces the DOM's own rule (painted geometry,
  draw order, the hit copies) in one render.
- **The compositor-layer variants** (R3): help repeated scrolling, hurt zoom and first exposure.
- **Reusing the map's own PNG** as the raster: its width is fixed at 2600 px, so Sawada's would be 1.27
  px per map px - below its opening scale on a DPR-2 screen.
