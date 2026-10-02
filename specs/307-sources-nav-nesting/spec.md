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
Message 2 adds two things to the same feature: every URL a page displays becomes a link opening in a new tab, made by
the build (*"something that our makefile target can do automatically"*); and the GM's campaign-note entries, which said
"URL: none", point at the notes' public home on GitHub, each named section at its heading (the GM's example:
`https://github.com/EliAndrewC/l7r/blob/master/setting/l7r.md#the-median-domain`).
**Predecessor**: 305 (source tags, the works sections in `research/source-sections.json`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse the sources by section and kind (Priority: P1)

The GM opens the record's sidebar. "Sources" appears once, as the group heading, and the works sections sit directly
beneath it in their order, the way the research group's top-level sections sit beneath its heading. "Premodern Japan" opens to its kinds
("Primary", "Scholarship", "Reference", ...), and each kind to its works. The record's home page (its table of contents), the one-page record's
contents and the sources index page nest the same way.

**Independent Test**: build the record; the sidebar's data, the home page's contents, the one-page contents and the
sources index each show
Sources -> section -> kind -> works, and every work appears exactly once, under its own section and its primary kind.

**Acceptance Scenarios**:

1. **Given** the sidebar, **When** it is drawn, **Then** "Sources" appears exactly once, as the group heading, and
   directly beneath it are the works sections that hold any work, in `source-sections.json` order.
2. **Given** a section whose works carry kinds, **When** it is opened, **Then** its children are one node per kind its
   works carry as their primary kind, in the vocabulary's order, each listing its works in registry order.
3. **Given** the Setting canon section, whose works carry no tags, **When** it is opened, **Then** it lists its works
   directly.
4. **Given** a source's own page, **When** it loads, **Then** the sidebar opens to that source's section and kind, with
   the source marked.
5. **Given** the home page's contents, the one-page record's contents and the sources index, **When** they are read,
   **Then** they nest the same way, each section and kind a heading or contents entry that links to its place, and
   "Sources" appears once.

### User Story 2 - A URL is a link, and the GM's notes link to GitHub (Priority: P1)

A reader checking a source clicks the URL in its citation line and the source opens in a new tab. The GM's campaign-note
entries cite the notes on GitHub, each named section linked to its heading.

**Independent Test**: build the record; no page shows a bare URL, and every canon entry links GitHub.

**Acceptance Scenarios**:

1. **Given** a citation line showing `(https://doi.org/10.2355/tetsutohagane1955.91.1_2)`, **When** it is shown on a
   question page, a source's page or the one-page record, **Then** the URL is a link to itself opening in a new tab.
2. **Given** a URL already inside a link, or inside an HTML comment, **When** the page is built, **Then** it is left as
   it is.
3. **Given** the canon entry citing "The Median Domain", "Place Names" and "Samurai Population of the Largest Cities",
   **When** it is shown, **Then** each quoted section links to its heading on GitHub
   (`.../setting/l7r.md#the-median-domain`, ...) and "URL: none" is gone.

### Edge Cases

- A section holding only one kind still shows that kind as its one subsection, so the structure is the same everywhere.
- The registry's other groups (the attested instances, the canon note) hold no keyed works and keep their place.
- A question page's "Works cited here" is unchanged.

## Requirements *(mandatory)*

- **FR-001**: "Sources" appears once in the sidebar, as its group heading, and the works sections holding any work sit
  directly beneath it, in `source-sections.json` order.
- **FR-002**: A section's children are its kinds - one per primary kind its works carry, in `source-tags.json` order -
  each holding that section's works of that kind in registry order. A section whose works carry no tags (Setting
  canon) holds its works directly.
- **FR-003**: Every section and kind node links to its place on the sources index page, and a source's own page opens
  the sidebar to its section and kind.
- **FR-004**: The record's home page (its table of contents), the sources index page and the one-page record's Sources part, and its table of contents, use the same
  nesting: section headings, then kind headings, then the works.
- **FR-005**: The grouping is derived from the tags and the two files; nothing about it is written elsewhere.
- **FR-006**: Every URL shown as text on a built page - question pages, source pages, the sources index, the home page
  and the one-page record, wherever it appears (a citation line, a write-up, a note) - is built into a link to itself
  that opens in a new tab. A URL already inside a link, a tag, a comment, a script or a style is left alone. Nothing is
  typed into the registry or the questions for it.
- **FR-007**: Each campaign-note entry's citation line names the notes' file on GitHub
  (`https://github.com/EliAndrewC/l7r/blob/master/setting/<file>.md`) in place of "URL: none", and each section it
  quotes is followed by its heading's URL, the anchor computed from the file's headings by GitHub's rule. A quoted name
  that matches no heading of the file is refused, not guessed. The canon footnotes keep their registry link (the GM's
  standing ruling); the entry they open now links GitHub.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002, FR-005): in the built navigation data, the Sources group's top-level entries are the
  non-empty works sections in `source-sections.json` order, and no entry beneath the heading is labeled "Sources";
  every work appears exactly once in the tree, under its section and its primary kind; kinds follow the vocabulary's
  order.
- **SC-002** (FR-003): every section and kind node's link lands on an id that exists on the sources index; a source
  page's open keys name its section and kind.
- **SC-003** (FR-004): the home page, the sources index and the one-page record show section then kind in the same
  order as the navigation, "Sources" appears once in each, and the contents nest them.
- **SC-004** (FR-006): on the built site, no `http(s)://` URL appears as text outside a link; every link made from one
  opens in a new tab.
- **SC-005** (FR-007): every canon entry's citation line links its file on GitHub and every quoted section to an anchor
  of that file's headings; none says "URL: none".

## Decisions Recorded

This feature draws nothing on a map; it organizes the record's navigation.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The second level is the primary KIND | the GM's example ("Reference" vs "Scholarship") | kind is the one facet a section's rule does not already fix for every section | FR-002 |
| A one-kind section still shows its kind | session judgment | the same structure everywhere; the GM asked for the levels, not for their omission | Edge Cases |
| Kinds in the vocabulary's order | session judgment | primary sources first, as the vocabulary lists them | FR-002 |
| "Sources" once, the sections directly under the group heading | session judgment (round 1 finding) | the GM's example shows the repeat as the problem; the research group already works this way | FR-001 |
| Canon footnotes keep their registry link; the entry links GitHub | the GM's standing ruling, kept | FR-007 changes the paragraph the GM named, not the footnote rule | FR-007 |
| A quoted section matches its heading by plain text or a unique prefix | session judgment | two entries quote a heading's opening words or a heading carrying a cost suffix; a guess is refused | FR-007 |

## Assumptions

- The question pages' grouped works (feature 305) are not changed, beyond FR-006's links.
- The request's first sentence (*"I really like the idea of having the fiction be its own tag too"*) is already met by
  feature 305's amendment 2 (period *fiction*, region *Rokugan*, the section "The published game setting"); it needs
  nothing here.
- The GitHub repository `EliAndrewC/l7r`, branch `master`, holds the notes the record cites (the GM's message 2).

## Review history

- Round 1 (spec-fidelity, 2026-10-02): CHANGES REQUIRED, 3 items - "Sources" still repeated under FR-001; the home page's
  table of contents left out; the request's first sentence carried nowhere. Addressed: FR-001 and scenario 1 put the
  sections directly under the one "Sources" heading; the home page joins FR-004/SC-003; an assumption records the first
  sentence as met by feature 305. Message 2's two requests added as User Story 2, FR-006, FR-007, SC-004, SC-005.
- Round 2 (spec-fidelity-verify, 2026-10-02): CHANGES REQUIRED, 2 items - SC-001 still tested a "Sources" node; FR-006
  covered citation lines only, while the GM asked that a displayed URL become a link (11 other bare URLs on the site).
  Addressed: SC-001 tests "Sources" once with the sections directly beneath; the Independent Test names the home page;
  FR-006 and SC-004 cover every URL shown as text on any built page.
