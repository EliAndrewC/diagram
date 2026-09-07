# Plan - 208 The raster is a render

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **VI**: before/after measurements of the roll and the gate (FR-005); SC-002 proves the shipped pages
  unchanged.
- **X**: three engine modules touched; 100% coverage holds (the child's code is a string the parent
  sends, not measured engine code - stated at the point of change).
- **XIII**: the pool pages are byte-identical for a rendered roll; the vector-only page is an existing form.
- **XVI**: spec-fidelity before code.
- **Route**: engine code -> GATED (LOCAL-GATED).

## Design

- `interactive/raster.py`: `picture()` writes the PNG to the child's stdin and reads the WebP from its
  stdout; `_WEBP_CHILD` is the PIL-only snippet; a non-zero exit raises `RuntimeError` with stderr.
- `interactive/page.py`: `render_page(..., raster=True)`; the raster block runs only when `raster and vb`.
  `write_html(..., raster=True)` passes it.
- `settlement/finish.py`: `write_html(..., raster=render and not os.environ.get("DIAGRAM_SKIP_RENDER"))`;
  the comment that said the page write "does not skip" under `DIAGRAM_SKIP_RENDER` is corrected: the string
  pass still runs, the raster no longer does.
- FR-003: measure with the scratchpad's per-stage plugin on `tests/gate/test_paddy_fabric.py` with the
  cache bypassed; add `_trim()` in `finish.py` after the page write only if the floor stays.
- Tests: `tests/interactive/test_raster.py` (the child's output, the failure), `tests/interactive/test_page.py`
  (`raster=False`), `tests/settlement/test_finish_raster.py` or beside the existing finish tests (the three
  `finish` cases).
