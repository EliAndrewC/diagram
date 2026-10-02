# Feature 307 - the sources nested by section and kind

**Feature Branch**: none (main, in the clone `diagram-organization`)
**Created**: 2026-10-02
**Status**: Draft
**Request**: [`request.md`](request.md) - the GM's words verbatim. The record's left-hand navigation and its table of
contents list the sources as one flat run of 2,126 keys under "Sources" (and "Sources" twice). The GM asks for "Sources"
as a top-level section, each works section of feature 305 ("Setting canon", "Premodern Japan", ...) as a subsection of
it, and, where the works carry a tag that is not a section's own - the GM's example: *"Reference" vs "Scholarship"* - a
sub-subsection for each, with the works listed underneath. The question pages' grouped works stay as they are (*"I love
how the sources are broken out on any given page that has them"*).
**Predecessor**: 305 (source tags, the works sections in `research/source-sections.json`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse the sources by section and kind (Priority: P1)

The GM opens the record's sidebar. Under the "Sources" group heading is one "Sources" entry - not a second "Sources"
beneath a "Sources" heading - which opens to the works sections in their order. "Premodern Japan" opens to its kinds
("Primary", "Scholarship", "Reference", ...), and each kind to its works. The one-page record's table of contents and the
sources index page nest the same way.

**Independent Test**: build the record; the sidebar's data, the one-page contents and the sources index each show
Sources -> section -> kind -> works, and every work appears exactly once, under its own section and its primary kind.

**Acceptance Scenarios**:

1. **Given** the sidebar, **When** "Sources" is opened, **Then** its children are the works sections that hold any
   work, in `source-sections.json` order, and the "Sources" label is not repeated as its own child.
2. **Given** a section whose works carry kinds, **When** it is opened, **Then** its children are one node per kind its
   works carry as their primary kind, in the vocabulary's order, each listing its works in registry order.
3. **Given** the Setting canon section, whose works carry no tags, **When** it is opened, **Then** it lists its works
   directly.
4. **Given** a source's own page, **When** it loads, **Then** the sidebar opens to that source's section and kind, with
   the source marked.
5. **Given** the one-page record's contents and the sources index, **When** they are read, **Then** they nest the same
   way, each section and kind a heading or contents entry that links to its place.

### Edge Cases

- A section holding only one kind still shows that kind as its one subsection, so the structure is the same everywhere.
- The registry's other groups (the attested instances, the canon note) hold no keyed works and keep their place.
- A question page's "Works cited here" is unchanged.

## Requirements *(mandatory)*

- **FR-001**: The sidebar's "Sources" group holds one top-level "Sources" node whose children are the works sections
  holding any work, in `source-sections.json` order.
- **FR-002**: A section's children are its kinds - one per primary kind its works carry, in `source-tags.json` order -
  each holding that section's works of that kind in registry order. A section whose works carry no tags (Setting
  canon) holds its works directly.
- **FR-003**: Every section and kind node links to its place on the sources index page, and a source's own page opens
  the sidebar to its section and kind.
- **FR-004**: The sources index page and the one-page record's Sources part, and its table of contents, use the same
  nesting: section headings, then kind headings, then the works.
- **FR-005**: The grouping is derived from the tags and the two files; nothing about it is written elsewhere.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002, FR-005): in the built navigation data, the Sources node's children are the non-empty
  sections in file order; every work appears exactly once in the tree, under its section and its primary kind; kinds
  follow the vocabulary's order.
- **SC-002** (FR-003): every section and kind node's link lands on an id that exists on the sources index; a source
  page's open keys name its section and kind.
- **SC-003** (FR-004): the sources index and the one-page record show section then kind headings in the same order as
  the navigation, and the one-page contents nest them.

## Decisions Recorded

This feature draws nothing on a map; it organizes the record's navigation.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The second level is the primary KIND | the GM's example ("Reference" vs "Scholarship") | kind is the one facet a section's rule does not already fix for every section | FR-002 |
| A one-kind section still shows its kind | session judgment | the same structure everywhere; the GM asked for the levels, not for their omission | Edge Cases |
| Kinds in the vocabulary's order | session judgment | primary sources first, as the vocabulary lists them | FR-002 |

## Assumptions

- The question pages' grouped works (feature 305) are not changed.
