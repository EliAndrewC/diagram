# Feature Specification: A leaner site build and a faster clip

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=327-lean-site-fast-clip`)

**Created**: 2026-10-05

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: *"Memory has been tight even after our changes, so let's go ahead and make a
new feature that includes both of these. Which is to say both the site build thing and also the render speed follow-up."* - the two
follow-ups quoted there.

## Context

Two follow-ups from features 323 and 326 (observed 2026-10-04/05, method: tracemalloc over `site.build` and the 50 ms process-tree
sampler over a rendered 20-household hamlet; feature 323 research.md R1-R3, feature 326 research.md R2-R3):

- **The site build's result** is 148 MB of Python strings for 72.6 M characters: every page carries Japanese text, so Python holds
  it at two bytes a character. Held as UTF-8 it would be about half. The build peaks at 236 MB with that result in it.
- **The per-tile clip** (feature 326) re-parses the whole page text once per tile: 0.89 s of Python for 9 tiles, which is most of
  the +0.3 s the clip added to a render.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The built site holds its pages in about half the memory (Priority: P1)

The site build holds each page as UTF-8 bytes from the moment it is built; a reader asking for a page gets its text as before.

**Why this priority**: the first follow-up - option 1 of the two the session described ("Hold pages as UTF-8 bytes"). Option 1 is
taken over option 2 (streaming pages to disk) because it is the contained one the session described as "a modest wrapper": it
changes nothing a caller or a test reads, and it lowers the memory both where `make record` holds the site before writing it and
where the tests hold the built site; option 2 changes what the build is ("a bigger rewrite of the build and of the test helpers"),
though by the session's estimate it would cut more of `make record`'s peak. The difference is how much each changes, not that
one assembles the single page in memory (both do).

**Independent Test**: the build's result size and peak, before and after, on the real record; every file the same text.

**Acceptance Scenarios**:

1. **Given** the real record, **When** the site is built, **Then** its result holds about half the memory it did, and every page
   read from it is the same text as before.
2. **Given** a built site, **When** it is written to disk, compared with another build, or read page by page, **Then** each works as
   before.

---

### User Story 2 - The clip parses the page once, not once per tile (Priority: P1)

The per-tile clip measures each classed line's extents once per picture and reuses them for every tile.

**Why this priority**: the second follow-up - render speed without spending memory.

**Independent Test**: the clip's CPU per render and the render span, before and after, on the reference render; the picture the
same bytes as today's; the render's peak not higher.

**Acceptance Scenarios**:

1. **Given** the reference render, **When** it is rendered, **Then** the clip costs a fraction of its 0.89 s, the render span is
   shorter than feature 326's, the peak is no higher, and the picture is byte-identical to today's.

### Edge Cases

- A page holding no character past ASCII is held as its bytes as well; nothing depends on width.
- A line the off-map rule leaves whole (a `transform`, a path outside the merge grammar, a shape it cannot read) is left whole by
  the once-parsed form too.
- The page's own whole-map clip (`page.write_html`) gives exactly what it gave.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The site build MUST hold each page as UTF-8 bytes once the page is built, and give its text on read; what callers and
  tests read (a path-to-text mapping) MUST NOT change.
- **FR-002**: Every page MUST be the same text as before; writing the site MUST write the same files.
- **FR-003**: The off-map clip MUST parse each line's droppable elements and their extents once per picture and, per tile, keep the
  same ones the per-tile parse kept - its output byte-identical to `drop_offmap`'s for every line and box.
- **FR-004**: The render's picture MUST be byte-identical to today's (feature 326's), and its peak MUST NOT rise.
- **FR-005**: No map's content moves; no test may fail that passed before.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001): the built site's result on the real record at least 40% smaller than its 148 MB, and the build's traced peak
  no higher than 236 MB (observed 2026-10-04, method: tracemalloc, feature 323 research.md R3; the 40% is a target).
- **SC-002** (FR-002): every page of a build of the real record equals main's built site, file for file, and the tests that read the
  built site pass unchanged.
- **SC-003** (FR-003): a test holds the once-parsed clip equal to `drop_offmap` line for line over real pages and many boxes.
- **SC-004** (FR-004): on the reference render (observed 2026-10-05, method: the 50 ms sampler and an in-test timing, feature 326
  research.md R2-R3: clip 0.89 s for 9 tiles, span 3.57 / 3.37 s, peak 371 / 365 MB), the clip's CPU at most a third of 0.89 s, the
  span shorter than feature 326's measured against it alternated, the peak no higher; every live pool map's picture byte-identical
  to today's (the bounds are targets).
- **SC-005** (FR-005): `make done` green.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

None: no map draws or states anything differently; every picture and every page is the same bytes.

## Assumptions

- A page read from the built site briefly exists as text again while it is read; that is the reader's cost, not the build's.

## Review history

- Round 1 (initial acceptance, MODE 2, 2026-10-05): FAITHFUL. The aside applied as a wording fix to User Story 1's rationale (option
  2 would cut more of `make record`'s peak; the choice rests on how much each changes); to be told the GM at landing.
