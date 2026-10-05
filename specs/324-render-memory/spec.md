# Feature Specification: The render's memory

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=324-render-memory`)

**Created**: 2026-10-05

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: *"yes please do all 3 as a single feature, thanks"* - the three fixes of the
session's table quoted there.

## Context

Rendering a map's picture (observed 2026-10-05, method: process-tree RSS sampling, research.md R1) peaks near 1 GB for a 20-household
hamlet: every picture tile is rendered at once, each tile's renderer holding the whole map (~100 MB), and the child that stitches
the tiles keeps every decoded tile until it is done (300 MB). The post-landing render step regenerates the pool's maps 22 at a
time and peaked at 1.7 GB. A prototype of the three fixes (research.md R2) held the map's render to ~540 MB for about a second
more, with byte-identical output.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The picture is stitched a tile at a time (Priority: P1)

The child that joins the tiles into the picture holds one decoded tile at a time.

**Why this priority**: fix 1 of the GM's three.

**Independent Test**: the stitch child's peak on the reference render, before and after; the picture byte-identical.

**Acceptance Scenarios**:

1. **Given** a tiled picture, **When** it is stitched, **Then** the child's peak falls and the picture is byte-identical.

---

### User Story 2 - At most three tiles render at once (Priority: P1)

A picture's tiles are rendered at most three at a time.

**Why this priority**: fix 2.

**Independent Test**: the number of tile renders alive at once never exceeds three; the map's render peak, before and after.

**Acceptance Scenarios**:

1. **Given** a picture of more than three tiles, **When** it is rendered, **Then** no more than three tile renders run at once, and
   the picture is byte-identical.

---

### User Story 3 - The post-landing render step runs at most four maps at once (Priority: P1)

The render step that regenerates the pool after a landing runs at most four generators at a time.

**Why this priority**: fix 3.

**Independent Test**: the render step's parallelism by default; its peak and wall time on the 11 live maps, before and after.

**Acceptance Scenarios**:

1. **Given** the render step with no `--jobs`, **When** it regenerates the pool, **Then** at most four generators run at once; an
   explicit `--jobs` still sets it.

### Edge Cases

- A picture of three tiles or fewer renders as now (all at once).
- A box with fewer than four cores: the render step never runs more generators than the box has cores.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The stitch child MUST decode, paste and release one tile at a time.
- **FR-002**: A picture MUST render at most three tiles at once.
- **FR-003**: The render step MUST run at most four generators at once by default (fewer on a box with fewer cores); `--jobs` still
  overrides.
- **FR-004**: Every picture, PNG and page MUST be byte-identical to before.
- **FR-005**: No map's content moves; no test may fail that passed before.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001): on the reference render, the stitch child's peak falls by at least 80 MB (observed 2026-10-05, method:
  process-tree RSS sampling, research.md R1, R2: 300 MB before, ~185 MB for the prototype; the 80 MB bound is a target).
- **SC-002** (FR-002): on the same render, the map's peak falls by at least 300 MB and the render span grows by no more than 1.5 s
  (observed 2026-10-05, method: as above, research.md R2: ~970 MB and 2.2 s before, ~540 MB and 3.2 s for the prototype; both
  bounds are targets).
- **SC-003** (FR-003): the render step over the 11 live maps peaks lower than with 22 jobs, measured the same way (observed
  2026-10-05, method: as above, research.md R2: 1,459 MB at 22 jobs, 1,219 MB at 4); its wall time is recorded.
- **SC-004** (FR-004): the reference render's PNG and page compared byte for byte, before and after; a test holds that a picture
  rendered with the cap equals the single render.
- **SC-005** (FR-005): `make done` green.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

None: no map draws or states anything differently; the output is byte-identical.

## Assumptions

- The time costs are accepted by the GM as proposed: about a second per rendered map, and about fifteen seconds on the background
  render step (`request.md`).

## Review history
