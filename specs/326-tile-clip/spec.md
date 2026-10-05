# Feature Specification: Each tile its own part of the map

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=326-tile-clip`)

**Created**: 2026-10-05

**Status**: Draft - Amendment 2 (2026-10-05, the GM: visually identical accepted, request.md); Amendment 1 (2026-10-05, the GM: "yes please" - clipping only, at 3 x 3; request.md)

**Input**: the GM's request, verbatim in `request.md`: *"sure, go shead and file that as a feature and then work the feaure, thanks"* -
the session's proposal quoted there: clip each tile's map to its own window, and render more, smaller tiles. Amendment 1 (the GM,
"yes please") superseded the smaller tiles: clipping only, at 3 x 3.

## Context

A map's picture is rendered as tiles, three at a time since feature 324, each by a resvg process handed the WHOLE map with only its
window changed. Measured standalone (research.md R1, observed 2026-10-05, method: resvg under `/usr/bin/time`): a 3 x 3 tile holds
~103 MB; clipped to its window ~79 MB on average; a 5 x 5 tile clipped ~52 MB. Most of a tile's memory scales with its pixels, so the
proposal paired clipping with smaller tiles: the render's peak from ~575 MB to roughly 425 MB at about today's render time. Measured in
the pipeline (research.md R2, observed 2026-10-05, method: the 50 ms process-tree sampler), clipping alone did more, and smaller tiles saved only 10-20 MB more while every finer grid broke the
3.81 s span bound; Amendment 1 keeps the 3 x 3 grid.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A tile renders only the part of the map in its window (Priority: P1)

Each tile's renderer receives the map less every element lying wholly outside that tile's window - the same elements and the same
rule the page already uses to drop the ink outside the whole map.

**Why this priority**: the first half of the proposal.

**Independent Test**: a tile's document is smaller than the whole map's; the picture from clipped tiles is visually identical to the picture
from unclipped tiles (today's), measured (SC-003).

**Acceptance Scenarios**:

1. **Given** a tiled picture, **When** a tile is rendered, **Then** its document lacks the elements wholly outside its window, and
   the stitched picture is visually identical to the one stitched from
   unclipped tiles (SC-003).

---

### User Story 2 - The grid stays 3 x 3 (Priority: P1) - Amendment 1

The grid is not changed. Measured (observed 2026-10-05, method: the 50 ms process-tree sampler, research.md R2, R3): with the clip
in place the peak is no longer set by the tiles, so finer grids save 10-20 MB more while breaking the span bound, and a new grid moves tiling's tiny seam differences, so no finer grid can leave the
picture byte-identical. The GM chose clipping only, at 3 x 3 (request.md, Amendment 1).

**Why this priority**: the GM's ruling on the shortfall SC-002 sent them.

**Independent Test**: `TILE_MPX` unchanged; the reference render's peak and span, clipped against unclipped.

**Acceptance Scenarios**:

1. **Given** the reference render, **When** it is rendered, **Then** it is 3 x 3 as today, its peak at SC-002's target, its
   render span within the bound in SC-002, and its picture visually identical to today's (SC-003).

---

### User Story 3 - Feature 223's note says what tiling does (Priority: P2) - Amendment 1

The note at `TILE_MPX` claims the stitched picture is the single render pixel for pixel; it states the measured truth instead.

**Why this priority**: a pre-existing claim found false, corrected where found (research.md R3).

**Independent Test**: the note reads R3's measurement.

### Edge Cases

- A small page that is one tile renders whole, as now, with nothing clipped.
- A string the page does not clip (the sheet, unclassed ink, anything carrying a transform or a path outside the merge grammar) is
  never clipped in a tile either.
- A fractional zoom renders single, as now.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each tile's document MUST omit the classed elements wholly outside its window by the page's own rule (`drop_offmap`,
  its margin included), and nothing else.
- **FR-002** (Amendment 1): The tile grid MUST stay as it is (`TILE_MPX` unchanged, 3 x 3 on the reference render).
- **FR-003** (Amendment 2): Every picture MUST be visually identical to before - checked on every live pool map, clipped tiles against
  unclipped: identical, or differing only by the renderer's anti-aliasing on a trimmed path, the counts recorded (observed
  2026-10-05, method: research.md R4 - at most 34 channel values on a map, at most 10 levels, as the GM accepted).
- **FR-005** (Amendment 1): The note at `TILE_MPX` MUST state what tiling does to the pixels as measured (research.md R3), not that
  the stitched picture is the single render pixel for pixel.
- **FR-004**: No map's content moves; no test may fail that passed before.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001): the tiles' documents together are smaller than the whole map times the tile count, measured on the reference
  render; a test holds that a clipped tile drops what lies outside its window and that, on a synthetic page, the stitched picture equals the
  single render (on a real map the comparison is with unclipped tiles, SC-003 - research.md R3).
- **SC-002** (FR-002, Amendment 1): on the reference render, clipped against unclipped at 3 x 3 alternated, the peak is about 170 MB
  lower, to roughly 370 MB - the GM's approved outcome (request.md, Amendment 1), within a tolerance of 20 MB - and the render span
  within 3.81 s - feature 324's mean span 3.41 s plus 0.4 s (observed 2026-10-05, method:
  process-tree sampling at 50 ms, feature 324 research.md R3, and this feature's research.md R2:
  unclipped 551 / 528 MB and 3.13 / 3.22 s, clipped 371 / 365 MB and 3.57 / 3.37 s; the bounds are targets).
- **SC-003** (FR-003, Amendment 2): every live pool map's picture from clipped tiles against its picture from unclipped tiles, each
  difference counted (observed 2026-10-05, method: research.md R4 - 3 of the 5 tiled maps identical, 2 differing in 34 and 29
  channel values of 20+ million pixels, at most 10 levels); a difference beyond that kind - a lost or moved element - fails it.
- **SC-005** (FR-005): the note at `TILE_MPX` carries R3's measurement.
- **SC-004** (FR-004): `make done` green.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

None: no map draws or states anything differently; the picture is visually identical (SC-003).

## Assumptions

- The page's off-map rule is safe to apply per tile because a tile's window clips exactly as the map's viewBox does; any element the
  rule cannot read is left whole, as the page leaves it.

## Review history

- Round 1 (initial acceptance, MODE 2, 2026-10-05): CHANGES REQUIRED - FR-002 could keep 3 x 3, SC-002 set half the approved
  saving with no consequence, and its span bound named no reference. Applied: finer grids only, the approved outcome as the target,
  a shortfall reported to the GM, the bound from feature 324's mean span. The classed-only carve-out ruled LEGITIMATE.
- Round 2 (initial acceptance, verify, 2026-10-05): FAITHFUL - both round-1 items fixed; nothing new introduced.
- Amendment 1 (2026-10-05): the GM chose clipping only, at 3 x 3 (request.md) after SC-002's shortfall report; FR-002, SC-002,
  SC-003 rewritten, FR-005 / SC-005 added (feature 223's note). The amendment resets the review count.
- Amendment 1, round 1 (2026-10-05): NOT-REVIEWABLE (two unlabeled figures; three passages still equated tiled and single
  renders) - fixed, no round used. Then CHANGES REQUIRED: SC-002 targeted the superseded saving - set to the approved one.
- Amendment 1, round 2 (verify): item resolved; CHANGES REQUIRED on a new Context sentence that said smaller tiles saved nothing more
  (R2 measured a small further saving, every finer grid over the span bound) - corrected; round 3 NOT-REVIEWABLE (that sentence's
  figure unlabeled) - labeled, no round used.
- Amendment 1, round 3 (verify, 2026-10-05): FAITHFUL - round 2's item resolved; the amendment accepted.
- Amendment 2 (2026-10-05): the pool check found trimming not byte-identical on 2 maps (anti-aliasing, R4); the GM chose it as visually
  identical over whole-line clipping. FR-003 and SC-003 rewritten. The amendment resets the review count.
- Amendment 2, round 1 (2026-10-05): CHANGES REQUIRED - tasks.md T03 still said byte identity; FR-003's tolerance understated the
  accepted result. Both corrected (T03 visual identity; FR-003 as R4 measured).
