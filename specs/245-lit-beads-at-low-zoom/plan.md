# Plan - 245 Lit beads at low zoom

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **I**: the stylesheet change is checked by a browser test on the synthetic page (FR-005), and the GM
  reads the real map (SC-002); the author is not the reviewer of the picture.
- **VI**: a green `make page-check` for the asset; a green `make done` for the tool (`tools/page_lit.py`
  is engine code); the gate is backgrounded and its notification acted on.
- **X**: no new module; `page_lit.py` keeps 100% through its stub tests and the browser test; every file
  stays under 1,000 lines.
- **XIII**: no pool manifest moves, so no settlement-review is owed (feature 231) and no map re-rolls;
  the baseline is the green `make done` recorded 8 hours before this feature started.
- **XIV**: the tool defect is fixed in this work (spec D5).
- **XVI**: spec-fidelity before code; this plan reviewed (MODE 4) before any tick.
- **Route**: `l7r/diagram/tools/page_lit.py` and the tests are in the delta, so GATED (LOCAL-GATED);
  `assets/page.css` owes `make page-check` at push as well.

## Design

- `interactive/assets/page.css`: one rule after the wash rule, so it wins by order -
  `svg#map[data-mode="raster"] g.f.on.f-bund-beans :is(path, circle):not([fill="none"]) { fill-opacity: 1; }`
  - with the FR-003 comment above it (why the beads and only the beads; the R1 pointer; where a second
  class would be added). The hit discs are `fill="none"` and so excluded by the same test the wash uses;
  the 0.85 group opacity is not named.
- `tools/page_lit.py` `measure`: the `--vector` loop presses `Control+=` through `page.keyboard.press`
  in place of `page.mouse.move` + `page.mouse.wheel`; `ZOOM_STEPS` stays as the cap; the docstring says
  the key and why not the wheel.
- `tests/tools/test_page_lit.py`: `_FakePage` gains a `keyboard` whose `press` logs; the two zoom-loop
  tests assert presses, not wheel turns.
- `tests/full/interactive/page_browser/test_page_lit.py`: the halves page measured through a 100 by 100
  viewport (the `viewport` argument `measure` already takes) so its opening view is raster mode; the
  first test asserts `mode == "raster"`, the vector test asserts `mode == "vector"` and `zoom > 1`.
- `tests/full/interactive/page_browser/_driver.py` `_synthetic()`: one `<circle r="1.4" fill="#2F6B35"/>`
  tagged `bund beans` on clear ground; `test_synthetic.py`: a test that shrinks the viewport, presses fit,
  asserts `data-mode="raster"`, lights the paddy and reads `fill-opacity` 0.45 on its rect, lights the
  beads and reads 1 on the circle, then restores the viewport and asserts both read 1 on the vector page.
- `interactive/CLAUDE.md` raster row and `tools/CLAUDE.md` page-lit row: one clause each.
- SC-002 and SC-003 replayed by hand on the shipped Inashiro page with `make page-lit`, recorded in
  tasks.md.
