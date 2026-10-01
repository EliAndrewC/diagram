# Feature 303 - the record organized by tags

**Feature Branch**: none (main, in the clone `diagram-organization`)
**Created**: 2026-10-01
**Status**: Accepted - FAITHFUL at round 3 (2026-10-01)
**Request**: [`request.md`](request.md) - the GM's words verbatim. The organization of the record today is *"haphazard"*:
a top-level "Research" beside a "Cities" that is also research, "How our maps draw it" beside "How our maps draw cities",
drawing conventions (Presentation) filed as research, and an order that opens on field archetypes for no reason. The GM
asks for an organization that starts where a reader should start (the settlement tiers), groups by what a question is
about, orders by how general it is (*"foundational"* before *"subtype"*, *"detail"* and *"counts and measurements"*) with a
stable tiebreak, and can be regrouped later *"very easily"* once *"we have a functional tagging system"*. And, message 2:
the topic directories no longer earn their place now that every question is its own file, so storage is decided in the
same feature as the tags (*"I don't think that we should do that kind of file reorganization as a separate pass"*). The
building-plan section is named *"Estates and other compounds"*. Message 3: every reference to a research file by path or
by number is rewritten to the new one; no redirects from old locations.
**Predecessors**: 258 (the record written per entry), 292 (the rendering collection and its cross-links), 301 (the record
built as a site; pointers name fragments).

## Summary

The record today is stored as one fragment per question inside topic directories (`fields/`, `cities/capitals/`,
`rendering/cities/capitals/`, ...), and the built site's navigation is those directories: `site.py` maps four directory
prefixes to four groups, and orders the parts within a group by folder name. A question's number is unique only inside
its folder. The research tree and the drawing tree pair question by question, by number.

This feature separates three things that the directories currently fuse:

1. **Identity and storage.** Every question lives in one flat place under one stem with a global identity number: its
   research file, its drawing file ("how our maps draw it"), its notes and its originals side by side. No topic folder.
   The sources registry stays beside it in the same research place. The number means identity, never order.
2. **Classification.** Each question carries tags from a controlled vocabulary in three facets - **subject** (the first
   one listed is primary), **setting** (countryside, town, city) and **level** (foundational, subtype, detail, counts and
   measurements). A drawing file inherits its research file's tags.
3. **Presentation.** One table-of-contents file declares the sections, their order and their nesting, and a rule over
   the tags saying which questions each takes - any facet, any position, not only the primary subject. Within a section, questions order by level, then identity number. The research half and the
   "how our maps draw it" half share the one structure. Every tag also gets its own built page.

Regrouping the record later is an edit to the table-of-contents file (and, where a question's home should change, its
rule) - no question file is edited, nothing moves on disk and no URL changes. The first table of contents takes
questions mostly by primary subject, but a later regrouping may select on any tag (the GM: *"instead of only treating
the first tag as the primary one"*).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read the record in a sensible order (Priority: P1)

The GM opens the record and the navigation begins with the settlement tiers, then the countryside, then the compounds,
towns, cities, the trades and services they share, and religion and the dead. Inside a section, the foundational questions
come first and the counts and measurements last. The drawing half has the same sections in the same order.

**Why this priority**: it is the complaint.

**Independent Test**: build the record; read the home page and the navigation of any page.

**Acceptance Scenarios**:

1. **Given** the built record, **When** the GM opens the home page, **Then** the research half's sections appear in the
   table-of-contents file's order, the first is The settlement tiers, and no group is named for a directory ("Research"
   beside "Cities").
2. **Given** a section, **When** the GM reads its list of questions, **Then** every foundational question precedes every
   subtype question, which precede every detail question, which precede every counts-and-measurements question, and
   questions of one level are in identity-number order.
3. **Given** the drawing half, **When** the GM opens it, **Then** it has the same sections in the same order as the
   research half, plus Map conventions (the former Presentation questions), and nothing labeled "How our maps draw
   cities" stands beside it as a second group.

---

### User Story 2 - Find a question under every tag it carries (Priority: P1)

A question has one home in the navigation, but the GM can find it from any of its tags: a samurai estate's compound plan
lives under Estates and other compounds and appears on the *countryside* page and the *samurai* page.

**Why this priority**: it is what makes a single home acceptable (message 2's farmhouse and country-estate question).

**Independent Test**: build; open a tag page; compare its list against the tags in the fragments.

**Acceptance Scenarios**:

1. **Given** any tag in the vocabulary, **When** the GM opens its page, **Then** it lists exactly the questions carrying
   that tag, each linked to its page, ordered as a section is.
2. **Given** a question's page, **When** the GM reads it, **Then** its tags are shown, each linking to its tag page.

---

### User Story 3 - Regroup without moving anything (Priority: P2)

Later, the GM decides the sections should be grouped differently. The session edits the table-of-contents file and
rebuilds. No fragment moves, no number changes, no pointer changes, no URL changes.

**Why this priority**: the GM's stated reason for tags (*"it is just a straightforward change ... to do a total
reordering of everything"*).

**Independent Test**: reorder two sections in the table-of-contents file and rebuild; diff the trees.

**Acceptance Scenarios**:

1. **Given** the record, **When** two sections are swapped in the table-of-contents file, **Then** the build succeeds,
   the navigation shows them swapped, and every question page's URL is unchanged.
2. **Given** two consecutive builds with nothing changed, **When** their outputs are compared, **Then** they are
   byte-identical.

---

### User Story 4 - Every reference still lands (Priority: P1)

Code comments, `Entry:` lines, map modals, docs, specs, cross-links inside the record, and the research tooling all name
the new stems. A pointer to an old path is gone, not redirected.

**Why this priority**: message 3; a dangling pointer is the record failing its reader.

**Independent Test**: the pointer check over the whole repository; every built map's links; each research make target.

**Acceptance Scenarios**:

1. **Given** the landed feature, **When** the repository is searched for any old research path or old page name used as
   a reference, **Then** none remains outside the GM's verbatim words.
2. **Given** a pool map's interactive page, **When** a reader follows any research link in it, **Then** it reaches the
   question's page.
3. **Given** a peer session that wrote an old-layout path after the move, **When** it pushes, **Then** the push is refused
   with the new path named.

---

### User Story 5 - Write new research into the new layout (Priority: P2)

A research session adds a question. It reserves an identity number, writes the files under one stem, tags it, and the
build places it. Forgetting the tags fails the build, naming the question.

**Independent Test**: add a question through the documented route in a scratch clone; build; remove its tags; build.

**Acceptance Scenarios**:

1. **Given** a new question with valid tags, **When** the record builds, **Then** it appears in the first section, in
   table-of-contents order, whose rule matches its tags, at its level's position.
2. **Given** a question with no tags, an unknown tag, or tags no section's rule takes, **When** the record builds,
   **Then** the build refuses, naming the file and the problem.

### Edge Cases

- **Research and drawing do not pair one to one.** Measured 2026-10-01 against the `<!-- about: -->` declaration each
  drawing page carries (one each, 234): 231 drawing pages are about the research question of the same part and
  number. Three are SECOND drawing pages of a research question - 0002 (about 0001), 0069
  (about 0068), 0032 (about 0031). Six research questions have no drawing page - 0012,
  0052, 0127, 0067, 0133, 0172. So a stem holds a research page
  and at most one drawing page; a further drawing page is its own stem that declares the research stem it is about and
  inherits that stem's tags; a research question with no drawing page appears only in the research half. The plan
  re-measures this exhaustively before migrating.
- **Research questions that are drawing conventions.** The three Presentation questions are research-tree files that
  are drawing conventions; they become drawing-only stems in Map conventions, carrying their own tags. Every other
  research question is audited for the same thing (FR-008a).
- **A question two sections' rules both match**: its home is the first matching section in table-of-contents order;
  its other tags put it on those tag pages.
- **A drawing page that inherits tags but states its own**: refused - a drawing page states tags only when it is about
  no research question.
- **A part opening (the `_front.html` paragraph) that no longer matches any one section**: its reader-facing text moves
  to the description of the section it introduced, or is listed as retired with the reason.
- **In-flight peer work** on old paths (another clone mid-session): the old-to-new mapping is kept as a file the pointer
  check reads, so a late pointer is refused with its new path named; the mapping is migration data, never a redirect.
- **Numbers in prose** ("research 040", "R-entry 210") that mean a research question: rewritten to the new identity
  number with its stem, like a path.

## Requirements *(mandatory)*

### Functional Requirements

**Storage and identity**

- **FR-001** Every question is stored in one flat location under the research place, with no topic subdirectory. A
  question's files share one stem `NNNN-<slug>`: the research page, the drawing page (`.drawing`), the notes and the
  originals. The sources registry stays in the same research place.
- **FR-002** `NNNN` is a global identity number, unique across the record, allocated once at migration and thereafter by
  `make reserve`. It never encodes order and is never reused.
- **FR-003** Each question keeps its heading ids, titles and text. The migration changes a fragment's content only in its
  links, its pointers and its tag marker.
- **FR-004** A built question page's URL is derived from its stem or heading id, never from its section, so a change to
  the table of contents moves no URL.

**Tags**

- **FR-005** A controlled vocabulary in one file defines every tag: its facet (subject, setting, level), its display name
  and a one-line description. Levels are, in order: foundational, subtype, detail, counts and measurements. Settings are
  countryside, town and city.
- **FR-006** Each research page (and each drawing page about no research question) carries its tags: one or more
  subjects (the first primary), one or more settings, exactly one level. A drawing page about a research question - the
  one in its own stem, or the one its own stem declares it is about - inherits that question's tags.
- **FR-007** The build refuses, naming the file: a question with no tags, a tag not in the vocabulary, a missing facet,
  more than one level, or a drawing page stating tags when it inherits them.
- **FR-008** Every question migrated is tagged by this feature. The full tag table (stem, subjects, settings, level, home
  section) is written to the feature's directory for the GM to read, and each primary subject follows the rule: a
  question's home is the place a reader is looking at when they come to it from a map, unless a section that spans
  settings (Estates and other compounds, Trades and services, Religion and the dead) takes its subject.

- **FR-008a** The tagging pass decides, for every research-half question, whether it is a drawing convention rather than
  research; each that is moves to the drawing half (as a drawing-only stem, in the section its tags choose, or Map
  conventions), and the tag table records the ruling for every question.

**Presentation**

- **FR-009** One table-of-contents file declares the sections: their order, their nesting, a title and description for
  each, and the rule by which each takes questions - a rule over any of a question's tags (a primary subject, any
  subject, a setting, a level, or a combination). It is the only place section order and grouping are stated; the builder
  contains no list of groups.
- **FR-010** A question's home is the first section, in table-of-contents order, whose rule matches it. The build
  refuses a question no section's rule matches, and a rule that matches no question at all (a typo, not a regrouping). A
  section whose matching questions were all homed by earlier sections is empty and is omitted (FR-013), not refused.
- **FR-011** Within a section, questions are ordered by level (foundational first), then identity number. The order is
  total and two builds of the same tree are byte-identical.
- **FR-012** The research half and the drawing half are built from the one table of contents: the same sections in the
  same order, each half showing only the sections that hold a page of that half. Map conventions holds the former
  Presentation questions, in the drawing half.
- **FR-013** The initial table of contents is, in order: The settlement tiers; The countryside (Fields, Field archetypes,
  Homesteads, Water, Vegetation and terrain, Ways); Estates and other compounds; Towns; Cities (Domain capitals, City
  defenses, Urban fabric, The government quarter, Outside the walls, River cities, Sizing a city); Trades and services;
  Religion and the dead (Shrines, Temples, The dead); Map conventions; then Sources. A subsection that would be empty is
  omitted, not shown empty.
- **FR-014** Every tag has its own built page listing exactly the questions carrying it, ordered as FR-011, linking each
  question's page in both halves. Each question page shows its tags linked to their pages.
- **FR-015** The single page (`all.html`) follows the table of contents: the research half, the drawing half, the
  citations and the sources, under its linked contents.
- **FR-016** The reader-facing text of each part opening (`_front.html`) is carried into the description of the section
  it introduced, or listed in `research.md` as retired with its reason. Part-level files with no reader in the new layout
  are removed.

**References and tooling**

- **FR-017** Every reference to a research question by old path, old page name or old number - code comments, `Entry:`
  lines, modal text, docs, every `CLAUDE.md`, `SKILL.md`, agent files, scripts, tests, landed specs, and cross-links
  inside the record - is rewritten to the new stem. The GM's verbatim words (`request.md` files, SOURCE blocks) are not
  edited. No redirect is written.
- **FR-018** The pointer check (`check-research-pointers.py`) validates the new form, recognizes old-layout paths and old
  page names as stale, and names the new stem for each from the migration mapping.
- **FR-019** Every research make target and script that took a page (`PAGE=`), and every hook that recognizes a record
  path (record edits, reserving, check bundles, entry drift, open questions, page sessions, fragment moves), works on the
  new layout, taking a question stem, a tag or a section where it took a page.
- **FR-020** The interactive maps' research links resolve after the feature lands.
- **FR-021** The research docs (`research/CLAUDE.md`, `README.md`, `STYLE.md`, the page-session rules, the root and skill
  `CLAUDE.md`) describe the new layout, the tags and the table of contents, including how a new question is tagged.

### Key Entities

- **Question**: one stem; identity number, slug, research page and/or drawing page, notes, originals, tags.
- **Tag vocabulary**: every tag, its facet, display name and description.
- **Table of contents**: ordered, nested sections; each with title, description, and the tag rule that selects its
  questions.
- **Migration mapping**: old path and old page-local number to new stem, kept so late pointers are named, not redirected.

## Success Criteria *(mandatory)*

- **SC-001** (FR-009, FR-012, FR-013) The home page and navigation list exactly the table of contents' sections in its
  order in each half, the first being The settlement tiers; no group name is derived from a directory.
- **SC-002** (FR-005, FR-010, FR-011) In every section, no question of a later level precedes one of an earlier level, and
  same-level questions are in identity order; two consecutive builds are byte-identical.
- **SC-003** (FR-001, FR-002, FR-003) The count of questions and the set of heading ids are the same before and after; no
  topic directory remains under the research place; every identity number is unique; every question body, with links,
  pointers and the tag marker normalized away, is identical to its pre-migration text.
- **SC-004** (FR-006, FR-007, FR-008, FR-008a) Every question carries valid tags; the tag table is in the feature directory; each
  refusal in FR-007 and FR-010 is proven by a test that feeds the build the bad case; the tag table carries a
  drawing-convention ruling for every research question.
- **SC-005** (FR-014) For every tag, its page lists exactly the questions whose tags (inherited or stated) include it.
- **SC-006** (FR-004, FR-009) Swapping two sections in the table-of-contents file and rebuilding changes the navigation
  and changes no question page's URL; changing a section's rule to select on a setting or a non-primary subject moves
  the matching questions without editing any question file; tests hold both.
- **SC-007** (FR-017, FR-018, FR-021) Zero references to old research paths or old page names remain outside the GM's
  verbatim words; the pointer check passes over the whole repository; a test shows it refuses an old path and names the
  new stem.
- **SC-008** (FR-019) Each research make target and hook named in FR-019 has a test run against the new layout, and the
  hooks' self-tests pass (`make hooks-test`).
- **SC-009** (FR-020) Every research link in every pool map's interactive page resolves to a built page.
- **SC-010** (FR-015, FR-016) The single page holds every question once per half in table-of-contents order; every part
  opening's reader-facing sentences are in a section description or listed as retired.
- **SC-011** (spec-wide) `make record CHECK=1` and `make done` are green on the landed tree.

## Decisions Recorded

This feature draws nothing on a map and states nothing new about one; it reorganizes the record. Its decisions:

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Flat storage, one stem per question, global identity number | GM ruling (message 2) | topic folders no longer save anything since every question is its own file; numbers collide across folders | this spec; `research/CLAUDE.md` |
| Three facets: subject (first primary), setting, level | GM's proposal adopted (message 1) | grouping by subject, ordering by level, cross-setting questions findable | the vocabulary file |
| Levels foundational, subtype, detail, counts and measurements | the GM's own names (message 1) | they are the GM's words for the ordering | the vocabulary file |
| Home follows the place seen from the map, except spanning sections | session proposal, GM accepted (message 3) | resolves the farmhouse / country-estate question | FR-008 |
| "Estates and other compounds" for the building-plan section | GM ruling (message 3) | clearer than "Buildings"; covers every compound kind | FR-013 |
| No redirects | GM ruling (message 3) | nothing is bookmarked | FR-017 |
| A drawing page inherits the tags of the research question it is about (its stem's, or the one its `about:` names) | session proposal | 231 of 234 drawing pages share their research question's part and number and the other 3 declare theirs (Edge Cases, measured); one decision per question, no drift | FR-006 |

## Assumptions

- The research and drawing trees pair as measured under Edge Cases; the plan's exhaustive re-measurement is the stated
  source for the migration.
- The existing fragment-move machinery is the basis of the pointer sweep; the plan decides how it is extended.
- Tag assignment is judgment: the plan proposes it from each question's title and opening and reviews the whole table
  before the migration commits; the GM reads the table after landing and a regrouping is a later edit, not a blocker.
- Peer sessions may hold unpushed research work on old paths at landing; the mapping file and the pointer check carry
  them over (Edge Cases).
- The GM's memory files outside the repository are updated where they name an old path, as housekeeping, not as a
  requirement of this feature.

## Review history

- Round 1 (spec-fidelity, 2026-10-01): CHANGES REQUIRED - sections could take questions only by primary subject (the
  GM's "instead of only treating the first tag as the primary one"); only Presentation was audited as a convention;
  the unpaired list was unmeasured. Fixed: FR-009/FR-010 rules over any tag, FR-008a, the measured Edge Case.
- Round 2: CHANGES REQUIRED - three passages still said primary-subject homing or one-to-one pairing; FR-010 refused
  what FR-013 omitted. Fixed.
- Round 3: FAITHFUL.
