# Implementation Plan: Each tile its own part of the map

**Feature**: 326-tile-clip | **Spec**: spec.md | **Request**: request.md

## Summary

`raster.picture` hands each tile its text with every classed line (`<g class="f ...`) passed through `drop_offmap` against the
tile's box. The grid stays 3 x 3 with `TILE_MPX` unchanged (D2, Amendment 1), and the note at `TILE_MPX` is corrected to what
tiling measurably does to the pixels (D5).

## Performance bookends (constitution VI)

Feature 324's lesson (its research R5): on this shared laptop the machine drifts by tens of percent over hours, so both bookends are
taken BACK TO BACK at the end - `make perf LABEL=326-start` in a detached worktree at the pre-feature commit (b8b20e690, the gate's
documented retroactive form), then `make perf-gate` in the clone - in a window arranged with the container's other session by
message. The snapshot times only the roll's stages, which this feature does not touch.

## Decisions

**D1 - The clip, per tile (FR-001).** In `picture`, after the tile's viewBox is set, the text is split on newlines and each line
starting with `<g class="f ` - a classed string as `page.wrap` writes it, the strings the page itself clips - becomes
`drop_offmap(line, tile_box)`; every other line (the sheet, unclassed ink, defs) is untouched, and `drop_offmap` itself leaves a
string with a `transform` or an unreadable path whole. A small wrapper `tile_doc(text, box)`, one pass over the lines, holds this, so it is
tested directly.

**D2 - The grid stays 3 x 3 (FR-002, Amendment 1).** `TILE_MPX` is not changed. The grid measurement was taken (research.md R2):
finer grids saved 10-20 MB more and broke the span bound, and moved tiling's seam differences (R3); the GM chose clipping only, at
3 x 3. SC-002 is the clipped-against-unclipped A/B of R2.

**D3 - Byte identity on the pool (FR-003).** A one-shot run over every live pool map's picture text: the picture from clipped tiles
against the picture from unclipped tiles (today's), byte for byte, recorded in research.md.

**D5 - Feature 223's note (FR-005, Amendment 1).** The note at `TILE_MPX` says what R3 measured: the stitched picture differs from the
single render by tiling's own seam differences - 4,319 pixels on the reference render at 3 x 3, most (about 80%) within two levels,
none above 39 (research.md R3) - which is why a grid change is never byte-identical; the clip changes no pixel.

**D4 - Research claims.** `tile_doc` inherits the module's claims; owed `impl-drift` only if `make claims-owed` says so.

## Tests

- `tests/interactive/test_raster.py`: `tile_doc` drops a classed line wholly outside the box and keeps one inside, and never touches
  an unclassed line; a tiled picture of a test page whose classed ink lies in one corner equals its single render.

## Verification

`make test-file` on the raster tests whole; the measurements; `make done`; the bookends.

## Constitution Check

No map draws or states anything differently; output byte-identical (no Decisions Recorded entries). Not a research question.
100% coverage for the new lines from the tests above.
