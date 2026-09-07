# Tasks - 200 Raster mode below the vector

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - how Chrome paints a
page, nothing about how a place was built.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code; the
      departure from the offer's letter (the whole picture, not the ground cover) put to it explicitly
      research: rendering
      verify: DONE. Round 1 CHANGES REQUIRED (the first load regressed silently; the switch in the wrong units; the drop a ride-along), round 2 CHANGES REQUIRED (FR-010 still raster-first), round 3 CHANGES REQUIRED (FR-007 still raster-first), round 4 FAITHFUL after a whole-spec search for the mechanism; the whole-picture correction of the offer's letter was graded faithful in round 1
- [x] T02 `interactive/raster.py`: the off-map drop (FR-001), the picture render (FR-003, FR-004), the
      id-map render (FR-007); the shared resvg helper with `finish.py`; the why at each point of change
      research: rendering
      verify: DONE. interactive/raster.py: drop_offmap, picture (resvg + lossless WebP), id_map (recolor, opacities stripped, crispEdges), class_keys, resvg_png with the shared RESVG_FONT_ARGS finish.py now imports
- [x] T03 `page.py` wires the drop, the images and the payload (FR-003, FR-006, FR-007); `page.js` the
      mode switch entered only once both images are decoded (FR-016), the id-map decode and the
      raster-mode pointer handling; `page.css` the two modes
      research: rendering
      verify: DONE. page.py drops before wrapping, renders both images from the page's own svg, inserts g.raster above the sheet, payload.raster; page.js mode()/data-mode with rasterReady, the picture's href set from script, the id-map canvas, keyAtPoint, stage pointermove/click in raster mode, the DOM handlers gated to vector mode; page.css the two modes
- [x] T04 unit tests on strings and a tiny real render (FR-009)
      research: rendering
      verify: DONE. tests/interactive/test_raster.py, 13 tests: the drop's every rule, the lossless picture at r px, the id map's every hit form on a tiny real render, every value on the palette grid, the palette refusal, resvg absent, the namespace, the nested-group guard (the one line the first gate found uncovered)
- [x] T05 the browser test on the Kuwabata fixture (FR-010) and the two raster-CPU guards (FR-011);
      both shown to FAIL with raster mode disabled (SC-005)
      research: rendering
      verify: DONE. Five browser tests on the kuwabata fixture: vector first then raster (readyAt 366 ms), id-map hover + click, 98.2% agreement on 2,100 points, ++ is vector and fit is raster, raster-CPU caps (36 / 11 against 100 / 60); the wet-paddy probe now asks the page's own hit-test in its mode. SC-005: with raster mode off, (b) and both caps failed, (a) held (5 failed, 23 passed)
- [x] T06 measurement on the implementation over the pool pages: the trace table, the sweep, load, page
      size, the pixel comparison (SC-001..003, FR-005) into `research.md` R6
      research: rendering
      verify: DONE. R6: every page - hover scrub 208-240 -> 16-36 ms raster CPU, wheel 128-264 -> 11-28, zoom 63-96 -> 11-27, pages 6.0-7.7 MB, raster ready 292-366 ms; SC-001 missed by 1-3 ms on Inashiro and Sawada, SC-003 within the noise floor - both recorded
- [x] T07 documents: `interactive/CLAUDE.md`, the 134 R5 annotation, memory (FR-012)
      research: rendering
      verify: DONE. interactive/CLAUDE.md raster.py row; 134 research.md R5 annotated as superseded for the low-zoom range; memory note project_page_paint_cost_giant_paths.md
- [x] T08 `make done` green, `make page-check` green, the Kuwabata page driven across the switch by the
      session (SC-004); land on the GATED route
      research: rendering
      verify: DONE. make done green (3,024 passed, coverage 100%, 464 s; the first run found one line of raster.py uncovered - the nested-group guard - now tested); the gate's test phase is the page check; the Kuwabata page driven across the switch by the browser tests and by T06's sweep; landing GATED (LOCAL-GATED, remote off)
