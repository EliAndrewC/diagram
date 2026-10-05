# Implementation Plan: Each tile its own part of the map

**Feature**: 326-tile-clip | **Spec**: spec.md | **Request**: request.md

## Summary

`raster.picture` hands each tile its text with every classed line (`<g class="f ...`) passed through `drop_offmap` against the
tile's box; `TILE_MPX` is lowered to the grid the measurement picks.

## Performance bookends (constitution VI)

Feature 324's lesson (its research R5): on this shared laptop the machine drifts by tens of percent over hours, so both bookends are
taken BACK TO BACK at the end - `make perf LABEL=326-start` in a detached worktree at the pre-feature commit (b8b20e690, the gate's
documented retroactive form), then `make perf-gate` in the clone - in a window arranged with the container's other session by
message. The snapshot times only the roll's stages, which this feature does not touch.

## Decisions

**D1 - The clip, per tile (FR-001).** In `picture`, after the tile's viewBox is set, the text is split on newlines and each line
starting with `<g class="f ` - a classed string as `page.wrap` writes it, the strings the page itself clips - becomes
`drop_offmap(line, tile_box)`; every other line (the sheet, unclassed ink, defs) is untouched, and `drop_offmap` itself leaves a
string with a `transform` or an unreadable path whole. A small, constant-time wrapper `tile_doc(text, box)` holds this, so it is
tested directly.

**D2 - The grid by measurement (FR-002).** On the reference render (the 20-household hamlet, seed 4, as feature 324's R1-R3),
with D1 in place, the peak and the render span at 4 x 4, 5 x 5 and 6 x 6 (by `TILE_MPX`), two runs each, with 3 x 3 clipped as the
reference point. The pick: among the finer grids, the lowest peak whose span is within 3.81 s (SC-002); `TILE_MPX` set to put the
reference at that grid, its measurement written beside it. If none qualifies, or the saving is under 100 MB, the numbers go to the
GM in the landing report (SC-002).

**D3 - Byte identity on the pool (FR-003).** A one-shot run over every live pool map's page text: the tiled picture against the
picture rendered whole (`tiles=1`), recorded in research.md.

**D4 - Research claims.** `tile_doc` inherits the module's claims; owed `impl-drift` only if `make claims-owed` says so.

## Tests

- `tests/interactive/test_raster.py`: `tile_doc` drops a classed line wholly outside the box and keeps one inside, and never touches
  an unclassed line; a tiled picture of a test page whose classed ink lies in one corner equals its single render; the existing
  tiled-equals-single test and `tile_count`'s assertions updated to the new `TILE_MPX`.

## Verification

`make test-file` on the raster tests whole; the measurements; `make done`; the bookends.

## Constitution Check

No map draws or states anything differently; output byte-identical (no Decisions Recorded entries). Not a research question.
100% coverage for the new lines from the tests above.
