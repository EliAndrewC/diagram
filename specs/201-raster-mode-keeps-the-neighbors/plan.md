# Plan - 201 Raster mode keeps the neighbors

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **VI Verify before done**: unit tests on strings and one real render (FR-005); the browser test on the
  real Kuwabata page asserts the text, the leaves, the placard's font and the wash (FR-006); SC-003
  shows the text assertion fires; feature 200's CPU caps stay in the gate.
- **X Python discipline**: one function added to `raster.py` (`without_text`), one line in `page.py`;
  100% coverage.
- **XII Record the why**: D1-D5, each with its measurement.
- **XIII No regressions**: the vector page is untouched; the raster-mode caps run at the gate.
- **XVI**: spec-fidelity before code; the inexact route is put to it against the GM's own allowance.
- **Route**: `raster.py` and `page.py` are engine code -> GATED (LOCAL-GATED); `page.css` rides along.

## Design

### `raster.py`

`without_text(svg_text) -> str`: `<text ...>...</text>` removed (`re.S`); `LIT_WASH = 0.45` lives here
too, so the number and its why are in one place, and `page.py` writes it into the stylesheet's rule
(`page.css` carries `LIT_WASH` as a placeholder the writer fills, as `--hl` is a constant of the
sheet) - or simpler and chosen: the constant is in `page.css` beside the highlight colors, where
feature 134 already keeps the palette as a recorded rendering decision, and `raster.py` documents it.

### `page.py`

`raster.picture(raster.without_text(svg))`.

### `page.css`

Replace `svg#map[data-mode="raster"] g.f:not(.on) { display: none; }` with the leaf rule
(`:is(path,circle,ellipse,line,rect,polygon,polyline,image):not(g.f.on *):not(g.raster *):not(defs *)`)
and add the wash rule on the lit class's filled shapes.

### Tests

- `tests/interactive/test_raster.py`: `without_text`; the picture of TINY-with-text has no text-colored
  pixel; the id map paints it.
- `tests/full/interactive/test_page_browser.py`: one test on the `kuwabata` fixture for FR-006.
