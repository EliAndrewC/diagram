# Feature Specification: The canonical download list, the GM's marked copy, and the access tags

**Feature Branch**: `313-download-list` (no branch - committed on `main` in the clone)

**Created**: 2026-10-02

**Status**: Draft

**Input**: The GM, 2026-10-02 (verbatim in `request.md`): the download list *"deserves to be in source control somewhere"*,
the GM's working file *"should be an actual copy and not the canonical source"*; per entry *"a space that is already set
aside, where I can either check a box (i.e. turning `[ ]` into `[x]`)"* for downloaded, paywalled, partial and found
elsewhere; *"I make a copy myself, and then I would inform you when it's ready to ingest ... and then I could sync your
version to mine"*; this system built first so the GM *"could begin work on this downloading before this feature is
complete"*; and *"do include the access tags thing as part of uh, feature 313."*

## Context (observed 2026-10-02)

- The GM's list is `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`: 2,333 lines, 306 entries headed `### N. <work>`
  (N = 1 to 306, each once), in four parts with a status table from the GM's 2026-09-13 pass over Part 1. It is in no
  repository. Sessions append to its end by hand (the rule in `CLAUDE.md`, `research/CLAUDE.md`, the research doctrine,
  `docs/research-record-rules.md` and `container-scripts/page-session-rules.md`), and nothing holds the rule.
- Feature 312's high-risk list, `specs/312-uncited-source-catalog/high-risk-sources.md`, holds 22 entries headed
  `### H<n>. <work> (`<key>`)`, in the download list's format. Each of them names its registry key.
- Of the 306 entries, 58 name a registry key, or a URL the archive manifest gives a key for. The other 248 name works the
  record has never read, so they have no registry entry yet.
- The registry holds 2,126 keyed works (`research/sources/010-works-cited/`). The archive manifest (feature 309,
  `research/archive/<id[:2]>/<id>.json`) gives 2,124 of them at least one row with a capture date and an outcome: 2,040
  `archived`, 33 `partial` (a bot wall or a page that would not render), 25 `archived-earlier-snapshot`, 14
  `archived-gm-copy`, 6 `unreachable`; a few keys have several rows. The two keys with no row are print works with no URL.
  1,966 entries carry a dated `READ` comment.
- Nothing records, per source, whether the GM holds a copy, whether it is paywalled, or that it was never read: that lives
  in free text across entries' comments and the list's prose.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The GM marks the copy as they work (Priority: P1)

The GM opens their copy of the list, goes down it, and for each entry ticks what happened: downloaded, partial (an abstract
or excerpt), paywalled, not found, and with downloaded or partial, found elsewhere, with where. They save files into
`academic-sources/` as before.

**Why this priority**: it is what the GM asked for, and it must land before 312 so the downloading can start.

**Independent Test**: after a sync, every entry in the GM's copy has its mark lines; ticking a box is a one-character edit.

**Acceptance Scenarios**:

1. **Given** the synced copy, **When** the GM reads any entry, **Then** the marks sit right under its heading, every box
   unticked except where a mark is already recorded.
2. **Given** the high-risk entries, **When** the GM opens the copy, **Then** they are its first section, ahead of everything
   else.

### User Story 2 - "Ingest" records the GM's marks (Priority: P1)

The GM says "ingest". The session runs one command: every changed mark in the copy is recorded in the canonical list with
the date; each source an entry names has its access tag updated; the files dropped in `academic-sources/` are archived
(feature 309's inbox), entries' ids usable in place of keys; and anything the command could not settle is named.

**Acceptance Scenarios**:

1. **Given** the GM ticked "downloaded" on entry 17 and "partial" and "paywalled" on H7, **When** the session ingests,
   **Then** the canonical list records both, dated, and the access report shows H7's source `northampton-tannery-1996` as
   the GM's partial copy.
2. **Given** "found elsewhere" ticked with neither "downloaded" nor "partial", or "not found" ticked with either, **When** the
   session ingests, **Then** that entry is not recorded and is named with the reason; the rest are recorded.
3. **Given** the GM also edited an entry's text, **When** the session ingests, **Then** the text edit is shown, and the
   command records the edit or discards it only on an explicit instruction. It never drops the edit silently.
4. **Given** a session changed an entry in the canonical list since the last sync (a pointer moved, say) and the GM changed
   only its marks, **When** the session ingests, **Then** the marks are recorded and the session's change is kept.

### User Story 3 - "Sync" replaces the GM's copy, never losing a mark (Priority: P1)

The GM says "sync". The session runs one command that writes the canonical list over the GM's copy. It refuses while the
copy holds anything not yet ingested, and names what.

**Acceptance Scenarios**:

1. **Given** the copy unchanged since the last sync or ingest, **When** the session syncs, **Then** the copy is replaced.
2. **Given** a mark ticked since the last ingest, **When** the session syncs, **Then** it refuses, naming the entries, and
   tells the session to ingest first.

### User Story 4 - Sessions add to the canonical list, at its end (Priority: P1)

A research session that finds a source only the GM can fetch adds it with one command. The entry takes the next number
under a host-wide lock, carries the mark lines and is appended at the end of the canonical list. A session never writes the
GM's copy.

**Acceptance Scenarios**:

1. **Given** two sessions in two clones each adding an entry, **When** both push, **Then** the entries have different numbers.
2. **Given** a session editing the GM's copy directly, **When** the edit is attempted, **Then** it is refused with the add
   command.
3. **Given** a push whose canonical list removed or reordered an entry, inserted one before the end, or lost an entry's
   marks, **When** the push runs, **Then** it is refused, naming the entry.

### User Story 5 - Every source carries an access tag (Priority: P1)

Feature 312 and any research pass ask what can be got of a source. One command answers for every registry source, and for
every list entry with no registry key: one of eight states with the date last checked and what it rests on.

**Acceptance Scenarios**:

1. **Given** the record as it stands, **When** the command runs, **Then** every one of the 2,126 registry keys has a state,
   with a count per state.
2. **Given** a key whose only manifest row is `partial` with HTTP 403, **When** it is asked, **Then** it is `bot-refused`,
   dated with that row's capture, resting on the row's reason.
3. **Given** a GM mark recorded on the entry naming a key, **When** it is asked, **Then** the GM's mark decides the state.

### Edge Cases

- An entry in the copy whose id the canonical list lacks (the GM added one): named by ingest, not recorded.
- An entry in the canonical list the copy lacks (added since the sync): not an error; it reaches the GM at the next sync.
- An entry that names several keys: each key takes the entry's mark.
- The first ingest before any sync: refused. The GM's file has no mark lines until the first sync puts them there.
- A file in `academic-sources/` matched to an entry with no registry key: archived under feature 309's inbox with keys `[]`
  and the entry's id recorded beside it, so the copy is found again when the entry's work enters the registry.
- A key with several manifest rows: the most open state wins (below); the date is that row's.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The canonical download list lives in this repository, beside the record, as Markdown. It is first imported
  from the GM's `TO-DOWNLOAD.md` as it stands on the import date, keeping every entry's number and text. The high-risk entries
  from 312's `high-risk-sources.md` are its first section, ahead of the imported parts, keeping their `H<n>` ids.
- **FR-002**: Each entry's identity is its id: the number or `H<n>` in its heading. Ids are never reused or renumbered.
- **FR-003**: Under its heading, every entry carries the GM's mark lines: boxes for downloaded, partial (abstract or
  excerpt), paywalled and not found; a found-elsewhere box with a place for where; and an optional place for the saved file's
  name. A recorded mark shows ticked, with the date it was ingested.
- **FR-004**: The import ticks only what the GM's own file already records: the 2026-09-13 status table and entry 16's
  "You already saved a PDF". Every other box starts unticked.
- **FR-005**: Ingest reads the GM's copy and matches its entries to the canonical list's by id. Against the version last
  synced, it records every changed mark, dated. It refuses an entry whose marks contradict (found elsewhere without
  downloaded or partial; not found with downloaded or partial). It shows every text edit the GM made outside the mark lines,
  and keeps or discards one only when told. It keeps a session's change to the same entry, and names a conflict where both
  changed the same text. It names any id the canonical list lacks. It then runs the archive inbox.
- **FR-006**: The archive inbox (feature 309) accepts a list entry's id where it accepts registry keys. The file is archived
  under that entry's keys, or keyless with the id recorded. A file named on an entry's saved-as line is matched without being
  asked.
- **FR-007**: Sync writes the canonical list over the GM's copy. It refuses while the copy differs from what was last synced or
  ingested, naming the entries. It records what it wrote, so the next ingest can tell the GM's changes from a session's.
- **FR-008**: Adding an entry is one command. It allocates the next number under a host-wide lock that sees every clone. It
  checks that the entry carries a link, a search fallback, what rests on it (as pointers to the record's files) and why it is
  blocked, writes the mark lines, and appends the entry at the end.
- **FR-009**: A session's write to the GM's copy, by Edit, Write or a shell command, is refused with the add command's usage.
  Sync is the one writer.
- **FR-010**: The push refuses a canonical list that, against main, lost an entry, reordered entries, inserted an entry
  anywhere but the end, reused an id, or has an entry without its mark lines. Each refusal names the entry and the fix.
- **FR-011**: The access tag. Every registry key, and every list entry with no registry key, has one state: open (read by
  us), bot-refused (opens in a browser but refuses us), down (timed out or a server error), gone (404, no copy), gm-full (the
  GM's full copy), gm-partial (the GM's partial copy: an abstract or excerpt), paywalled (a paid or institutional login) or
  never-read (referenced only). Each comes with the date last checked and what it rests on. It is derived from what the
  repository records: a GM mark recorded on an entry naming the key decides; otherwise the most open of the key's manifest
  rows; otherwise a dated `READ` comment in its registry entry (open); otherwise never-read. A state recorded by hand, with
  its date and a reason, is kept as evidence and wins when it is newer. The states, their order and their meanings are
  stated in one file.
- **FR-012**: One command reports the access tags: for one key or entry, for all (counts per state), or as JSON for another
  tool (feature 312) to read.
- **FR-013**: The rule "a source only the GM can fetch goes at the END of TO-DOWNLOAD.md" is rewritten wherever it is stated
  (the project and research rules, the research doctrine, the record rules, the page-session rules) to name the add command
  and the canonical list. The GM's "ingest" and "sync" are documented with their commands in the research rules.

### Key Entities

- **Canonical list**: the repository's Markdown list; ids, entry text, mark lines, ingest dates.
- **GM's copy**: `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`; written only by sync, marked only by the GM.
- **Mark**: an entry's boxes and the where and saved-as texts.
- **Sync record**: what was last synced and ingested (content fingerprints, and the commit of the canonical list synced).
- **Access tag**: a state, a date and its basis, per registry key or keyless entry.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002, FR-003, FR-004): The canonical list holds the 22 high-risk entries first, then all 306 imported
  entries in their order. Each has its mark lines. Its text outside the mark lines matches the import's sources, which a
  test checks.
- **SC-002** (FR-005, FR-007): A gate test drives a temporary copy through sync, a GM tick, a GM text edit, a session edit
  and ingest. It asserts the marks recorded, the text edit held for an instruction, the session's edit kept, and sync refused
  before the ingest and allowed after.
- **SC-003** (FR-008, FR-010): Gate tests show two adds taking distinct numbers, and the push check refusing each of the five
  violations.
- **SC-004** (FR-009): The guard's test companion shows an Edit, a Write and a shell redirect to the GM's copy refused, and
  sync allowed.
- **SC-005** (FR-011, FR-012): The report gives every one of the 2,126 registry keys a state with a date. Its per-state
  counts are recorded in this feature, and a gate test pins one key per derivation rule.
- **SC-006** (FR-013): No rule file still tells a session to append to `TO-DOWNLOAD.md` by hand.

## Decisions Recorded

Classes are those of `docs/research-doctrine.md`. Nothing on a map changes, so no decision is a rendering one.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The canonical list sits in the main repository, beside the record, not in the private archive | this project's decision, on the GM's acceptance | it holds no copyrighted text, sessions write it like the record, and the pointer check can read it (the session's answer, which the GM accepted) | `request.md`; this spec |
| The GM's copy is a byte-for-byte copy of the canonical list at sync, not a different rendering | this project's decision | a copy that is the same text is the simplest sync to prove lossless; the GM asked for "an actual copy" | the sync command's docstring |
| "Not found" is a fourth box | the session's addition, offered to the GM in 312 and settled in `request.md` | the GM's earlier "report that I have not been able to find some of them" | `request.md` |
| An optional "saved as" place on each entry | this project's decision, beyond the GM's four boxes | it lets ingest match a download to its entry without asking; optional, so it costs the GM nothing when skipped | this spec |
| The access tag is derived from what the repository records, not stored as a second copy | this project's decision | a stored copy goes stale at the next archive capture and conflicts across clones; deriving keeps "every source has a tag" true by construction. A hand-recorded state is kept for what nothing else records | the access module's docstring |
| A GM mark decides a key's state over an archive row | this project's decision | the GM's judgment (paywalled, partial) is made in a browser, which sees more than our fetch | the access module's docstring |
| Import ticks only what the GM's file already records | this project's decision | marks are the GM's own words; inventing one would be a session speaking for the GM | this spec |
| Access tags are not shown on the built record | this project's decision | not asked for; 312 reads them through the report | this spec |

## Assumptions

- `for-the-gm-fetch-list.md` (feature 232's list, already worked) is not imported; it stays where it is.
- 312's `high-risk-sources.md` is 312's file. This feature imports it and does not edit it; the 312 session is told the
  canonical list now holds those entries.
- Working through the list, and 312's verification, filter and paywalled-citation removal, are not this feature.
- The re-check of paywalled sources for open access is future work, not before 2028 (the GM).
- The first sync, which replaces the GM's current file, happens on the GM's word.

## Review history
