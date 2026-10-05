# Feature Specification: The site build's peak

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=323-site-build-peak`)

**Created**: 2026-10-04

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: *"making the record-site build itself use less memory is good if that seems
achievable as a reasonably straightforward change"*.

## Context

The record's site build (`site.build`) is run by `make record` and by the tests over the real record. Its memory (research.md R1,
observed 2026-10-04, method: tracemalloc): a 312 MB peak and a 148 MB result. The result is the pages themselves, stored two bytes a
character because every page carries Japanese text; shrinking it means changing what the build returns, which is not a
straightforward change. The peak above the result is the single page (`all.html`, 42 MB) held in four to five copies while it is
assembled and its bare URLs made links. A prototype that assembles that page a piece at a time held 236 MB at its peak, with every
file byte-identical (research.md R2).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The build holds less at its peak (Priority: P1)

A build of the real record reaches a lower memory peak, with the same site.

**Why this priority**: it is the request - less memory, by the straightforward change the measurement found.

**Independent Test**: measure the build's traced peak before and after; compare every file with the site built before the change.

**Acceptance Scenarios**:

1. **Given** the real record, **When** the site is built, **Then** its traced peak is lower than before and every file it returns is
   byte-identical to the site built before the change.

### Edge Cases

- A URL written in the single page's text is still made a link, and one already inside a link, a tag, a comment, a script or a style
  is left as it is - on every page, the single page included.
- The other pages (a page per question, section, tag, source; the index) are built as before.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The single page MUST be assembled without holding more than its pieces and the finished page at once - no whole joined
  body, linkified copy or second copy of it beside them.
- **FR-002**: Every file the build returns MUST be byte-identical to what it returned before this feature.
- **FR-003**: What the build returns (a path-to-text dictionary) MUST NOT change, nor what any caller or test reads.
- **FR-004**: No map output moves; no test may fail that passed before.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001): the traced peak of a build of the real record is at least 50 MB below the before figure, measured the same
  way in the same session (observed 2026-10-04, method: tracemalloc, research.md R1 and R2: 312 MB before, 236 MB for the
  prototype; the 50 MB bound is a target).
- **SC-002** (FR-002): every file of a build of the real record equals main's built site file for file (research.md R2's
  comparison, repeated on the final code), and a test holds the single page's links on a small record.
- **SC-003** (FR-003, FR-004): `make done` green.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

None: no map draws or states anything differently, and no page of the record changes. The change is in how one page is assembled.

## Assumptions

- The pieces of the single page are self-contained HTML (a link opens and closes in one piece), so making links in each piece is
  the same as making them in the whole; the byte comparison (SC-002) is what proves it on the real record.
- The 148 MB result stays as it is (research.md R2): a smaller result would change the type `build` returns, outside a
  straightforward change.

## Review history
