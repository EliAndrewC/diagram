# Plan - 200 Raster mode below the vector

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **VI Verify before done**: every mechanism has a unit test on strings (FR-009); the real page is
  driven in the browser test (FR-010); the two raster-CPU guards and the pointer cap run at the gate
  (FR-011); SC-005 shows the guards fire; the pixel comparison and the trace table are repeated on the
  implementation over the pool (T06).
- **X Python discipline**: `page.py` is 830 lines after feature 199; this feature adds a raster
  module rather than growing it past the bar - `interactive/raster.py` (the drop, the id-map recolor,
  the two resvg renders, the encodings), imported by `page.py`. 100% coverage on every new line; the
  resvg subprocess is exercised for real (resvg is a hard requirement of the engine already).
- **XII Record the why**: rendering decisions D1-D9, each with its measurement in research.md and at
  the point of change.
- **XIII No regressions**: the vector page is unchanged above the switch; the browser test's synthetic
  page and the reference-hamlet tests run as before; the feature-199 guards stay.
- **XV / XVI**: spec-fidelity before code; the departure from the offer's letter is stated in the
  spec's first section for the reviewer to grade.
- **Iteration cost**: `make quick` for the string tests; the browser file once; `make done` once. The
  gate's page writes gain two resvg renders per map (about 2 s + 1 s on Kuwabata) - stated in T06.
- **Route**: engine code -> GATED (LOCAL-GATED, remote off). `export SPECIFY_FEATURE` for the push.

## Design

### `interactive/raster.py` (new)

- `drop_offmap(strings, tags, viewbox) -> strings`: per classed record string, unless it (or a
  transformed ancestor - the wrap sees whole record strings, so a string containing `transform=` is
  left alone) carries a transform: filter the merge's `M/L` and `M/a` subpaths and the absolute
  primitives against the expanded viewBox. The viewBox is read from the first string (the `<svg`
  open tag) as the page already reads it for `hit_regions`.
- `picture(svg_text, viewbox, r) -> bytes`: resvg at `--zoom r` with `finish.py`'s font arguments
  (factored into one helper both callers use), then PIL to lossless WebP.
- `id_map(svg_text, keys) -> (png bytes, palette)`: the recolor rules of the prototype, plus the
  global opacity strip and `--shape-rendering crispEdges`.
- Constants: `RASTER_R = 3.0`, `OFFMAP_MARGIN = 24.0`, `PALETTE_STEP = 5`.

### `page.py`

`render_page` calls the drop before wrapping, renders the two images from the joined svg text, inserts
`g.raster` after the sheet and passes the palette and the id map in the JSON payload (`payload.raster`).
A page written with no resvg (a test that builds a synthetic page) gets no raster block and no id map,
and `page.js` then never enters raster mode - `RASTER_R` is 0 in the payload.

### `page.js`

- `apply()` sets `data-mode` from `view.s * devicePixelRatio` against `payload.raster.r`.
- The id map is decoded into an offscreen canvas at load (`Image` + `drawImage` + `getImageData`).
- `keyAtPoint(clientX, clientY)` maps viewport to map px through `view`; `pointermove` and `click` on
  the stage use it in raster mode; the existing `pointerover`/`click` on the svg are gated to vector
  mode. `l7rMap` exposes `mode()`, `keyAtPoint`, `idmapReady()` for the tests.

### `page.css`

`svg[data-mode=raster] g.f:not(.on) { display: none }`, `svg[data-mode=vector] g.raster { display:
none }`, `g.raster image { pointer-events: none }`.

### Tests

- `tests/interactive/test_raster.py`: FR-009 on strings; the renders on a tiny SVG (a real resvg call:
  a 40 x 40 document, the WebP decodes to the right size, the id map's pixel at a known point is the
  class's color and a point outside every class is 0).
- `tests/full/interactive/test_page_browser.py`: FR-010 and FR-011 on the `kuwabata` fixture; the trace
  helper (CDP `Tracing`) as a module function.

### Measurement (T06)

`measure3.py` and `final.py` (scratchpad) on the regenerated pool pages: the trace table, the pointer
sweep, load, page size, pixel comparison, per page; into research.md R6.
