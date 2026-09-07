# Tasks - 200 Raster mode below the vector

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - how Chrome paints a
page, nothing about how a place was built.

- [ ] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code; the
      departure from the offer's letter (the whole picture, not the ground cover) put to it explicitly
      research: rendering
- [ ] T02 `interactive/raster.py`: the off-map drop (FR-001), the picture render (FR-003, FR-004), the
      id-map render (FR-007); the shared resvg helper with `finish.py`; the why at each point of change
      research: rendering
- [ ] T03 `page.py` wires the drop, the images and the payload (FR-003, FR-006, FR-007); `page.js` the
      mode switch, the id-map decode and the raster-mode pointer handling; `page.css` the two modes
      research: rendering
- [ ] T04 unit tests on strings and a tiny real render (FR-009)
      research: rendering
- [ ] T05 the browser test on the Kuwabata fixture (FR-010) and the two raster-CPU guards (FR-011);
      both shown to FAIL with raster mode disabled (SC-005)
      research: rendering
- [ ] T06 measurement on the implementation over the pool pages: the trace table, the sweep, load, page
      size, the pixel comparison (SC-001..003, FR-005) into `research.md` R6
      research: rendering
- [ ] T07 documents: `interactive/CLAUDE.md`, the 134 R5 annotation, memory (FR-012)
      research: rendering
- [ ] T08 `make done` green, `make page-check` green, the Kuwabata page driven across the switch by the
      session (SC-004); land on the GATED route
      research: rendering
