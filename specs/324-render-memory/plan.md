# Implementation Plan: The render's memory

**Feature**: 324-render-memory | **Spec**: spec.md | **Request**: request.md

## Summary

Three changes, each where its cost is decided: the picture child stitches one tile at a time (`raster._PICTURE_CHILD`); a
picture renders at most `TILE_WORKERS = 3` tiles at once (`raster.picture`); the render step runs at most `RENDER_JOBS = 4`
generators by default (`render_cache.regen_pool`).

## Performance bookends (constitution VI)

`make perf LABEL=324-start` on unmodified code (8c61b03ae, taken before the first engine edit) and `LABEL=324-end` at the last
commit, taken with nothing else running in the container (feature 323's lesson, research R4 there); `make perf-report
AGAINST=324-start`. The bookend rolls without rendering, so no band is expected from these changes.

## Decisions

**D1 - The child stitches a tile at a time (FR-001, FR-004).** The tiles are still opened lazily first (a PNG's size is in its
header; nothing is decoded), the canvas made from their sizes, then each tile is popped from the dict, converted to RGB, pasted
and closed before the next; the pickled bytes are dropped once the tiles are open. The paste of the same pixels at the same
offsets in the same order writes the same canvas, so the JPEG is the same bytes.

**D2 - At most three tiles at once (FR-002, FR-004).** `TILE_WORKERS = 3` beside `TILE_MPX`, with its measurement (research R2: 3
tiles ~540 MB / +1.0 s; 4 tiles ~635 MB for the same time; 2 tiles ~450 MB / +2.1 s), and `max_workers=min(len(boxes),
TILE_WORKERS)`. Each tile's pixels are its own render; only their scheduling changes.

**D3 - At most four maps at once (FR-003).** `RENDER_JOBS = 4` in `render_cache`, with its measurement, and `max_workers=jobs or
min(RENDER_JOBS, os.cpu_count() or 4)`. The `--jobs` flag and the `jobs=` argument keep their meaning.

**D4 - Research claims.** `TILE_WORKERS` and `RENDER_JOBS` carry `Research: ... - NONE: process plumbing` if `make claims-coverage`
asks for them (UPPER_CASE constants in claims scope); the changed units are owed `impl-drift` only if `make claims-owed` says so.

## Tests

- `tests/interactive/test_raster.py`: a picture of more tiles than `TILE_WORKERS` equals its single render (the existing
  tiled-equals-single test, at a tile count above the cap); the number of tile renders alive at once never exceeds
  `TILE_WORKERS` (counted by wrapping `resvg_png`).
- `tests/pipeline/test_render_cache.py`: with no `jobs`, `regen_pool` runs at most `RENDER_JOBS` generators at once (the executor's
  `max_workers` observed).
- SC-001 to SC-004 measured once on the reference render and the render step, recorded in research.md.

## Verification

`make test-file` on the two test files whole; the measurements; `make done`; the bookends.

## Constitution Check

No map draws or states anything differently; output byte-identical (no Decisions Recorded entries). Not a research question.
100% coverage for the changed lines from the tests above (the child is a snippet run in a subprocess, covered by the stitch's
existing tests as data, as before).
