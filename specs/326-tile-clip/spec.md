# Feature Specification: Each tile its own part of the map

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=326-tile-clip`)

**Created**: 2026-10-05

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: *"sure, go shead and file that as a feature and then work the feaure, thanks"* -
the session's proposal quoted there: clip each tile's map to its own window, and render more, smaller tiles.

## Context

A map's picture is rendered as tiles, three at a time since feature 324, each by a resvg process handed the WHOLE map with only its
window changed. Measured standalone (research.md R1, observed 2026-10-05, method: resvg under `/usr/bin/time`): a 3 x 3 tile holds
~103 MB; clipped to its window ~79 MB on average; a 5 x 5 tile clipped ~52 MB. Most of a tile's memory scales with its pixels, so the
proposal paired clipping with smaller tiles: the render's peak from ~575 MB to roughly 425 MB at about today's render time.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A tile renders only the part of the map in its window (Priority: P1)

Each tile's renderer receives the map less every element lying wholly outside that tile's window - the same elements and the same
rule the page already uses to drop the ink outside the whole map.

**Why this priority**: the first half of the proposal.

**Independent Test**: a tile's document is smaller than the whole map's; the stitched picture is byte-identical to the single render.

**Acceptance Scenarios**:

1. **Given** a tiled picture, **When** a tile is rendered, **Then** its document lacks the elements wholly outside its window, and
   the stitched picture equals the picture rendered whole.

---

### User Story 2 - Smaller tiles (Priority: P1)

The picture is cut into more, smaller tiles, the grid chosen by measurement.

**Why this priority**: the second half - the larger lever (R1).

**Independent Test**: the render's peak and span on the reference render at each candidate grid.

**Acceptance Scenarios**:

1. **Given** the reference render, **When** it is rendered with the chosen grid, **Then** it is finer than feature 324's 3 x 3, its peak
   lower by about the approved 150 MB, and its render span within the bound in SC-002.

### Edge Cases

- A small page that is one tile renders whole, as now, with nothing clipped.
- A string the page does not clip (the sheet, unclassed ink, anything carrying a transform or a path outside the merge grammar) is
  never clipped in a tile either.
- A fractional zoom renders single, as now.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each tile's document MUST omit the classed elements wholly outside its window by the page's own rule (`drop_offmap`,
  its margin included), and nothing else.
- **FR-002**: The tile grid MUST be finer than feature 324's 3 x 3, chosen by measurement among the finer grids (4 x 4, 5 x 5 and
  finer as measured): the lowest render peak whose render span is within the SC-002 bound.
- **FR-003**: Every picture MUST be byte-identical to before - checked on every live pool map.
- **FR-004**: No map's content moves; no test may fail that passed before.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001): the tiles' documents together are smaller than the whole map times the tile count, measured on the reference
  render; a test holds that a clipped tile drops what lies outside its window and the stitched picture equals the single render.
- **SC-002** (FR-002): on the reference render, the chosen grid's peak meets the approved outcome - about 150 MB lower, to roughly
  425 MB - with its render span no more than 0.4 s over feature 324's mean (observed 2026-10-05, method: process-tree sampling at
  50 ms, feature 324 research.md R3: peaks 571 / 580 MB, spans 3.60 / 3.21 s, mean 3.41 s - so the bound is 3.81 s; 425 MB and
  150 MB are the proposal's estimate, the 0.4 s a target). If no finer grid keeps the span within the bound, or the measured saving
  falls clearly short of the approved figure (under 100 MB), the measurements go to the GM in the landing report: it is not settled
  by keeping 3 x 3 or by shipping a smaller saving as if it were the one approved.
- **SC-003** (FR-003): every live pool map's picture rendered with the change equals its picture rendered whole (one tile).
- **SC-004** (FR-004): `make done` green.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

None: no map draws or states anything differently; the picture is byte-identical.

## Assumptions

- The page's off-map rule is safe to apply per tile because a tile's window clips exactly as the map's viewBox does; any element the
  rule cannot read is left whole, as the page leaves it.

## Review history

- Round 1 (initial acceptance, MODE 2, 2026-10-05): CHANGES REQUIRED - FR-002 could keep 3 x 3, SC-002 set half the approved
  saving with no consequence, and its span bound named no reference. Applied: finer grids only, the approved outcome as the target,
  a shortfall reported to the GM, the bound from feature 324's mean span (3.81 s). The classed-only carve-out ruled LEGITIMATE.
