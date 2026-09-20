# Feature Specification: The record is written per entry and assembled into the pages a reader opens

**Feature**: `258-split-the-record-into-per-entry-files` | **Created**: 2026-09-20 | **Status**: Draft
**Input**: the GM's two messages of 2026-09-20, verbatim in [`request.md`](request.md), after the session
measured where a research page's bytes actually go.

## Summary

The record's pages are hand-authored HTML that has grown to where a whole page is read whenever any part
of it is touched. `SOURCES.html` is 1,150,367 bytes and 920 entries; `citations/cities/capitals.html` is
376,566 bytes; 19 files in the record are over 100,000 bytes (R1).

One premise of the request has to be corrected before stage 3 makes sense. The GM took the citations
page to be *"automatically assembled from a script which reads a couple of JSON files ... So that part is
probably okay"*. It is the other way around: `research/citations/<name>.html` is hand-authored HTML, and
what is derived from it is the hover script `citations/<name>.js` beside it, together with the works
section at its top, which comes from the registry. The 376,566-byte citations page is a file someone
types into, which is why splitting it is stage 3 and not out of scope.

The GM asked whether these should be split into per-entry files that assemble back into the same pages.
The measurement says yes, and says why: it is not the session's own editing that pays - reads of
`research/` are 0.56% of all tool output across 284 transcripts, and 90% of them already ask for a window
rather than a file (R2; observed 2026-09-20, method: `measure.py R2` over every transcript on this
machine - a store that grows, so the totals are a one-shot observation and the shares are what is read). It is the CHECKING AGENTS. One research page was 23-98% of everything that
entered a recorded agent's context, a median of 68% over the 17 recorded runs - `source-applicability`
98%, `quote-check` 90%, `record-format` 88%, `entry-drift` 82% (R3) - and feature 251 measured input at 75-90% of an agent's cost. An agent dispatched
to check one entry reads the other thirty.

This feature makes the per-entry file the thing that is written, and the page the thing that is built:

1. **Sources.** Each `SOURCES.html` registry entry becomes `research/sources/NNNN-<key>.html`.
2. **Questions.** Each research page becomes a directory, one file per question, with the gapped ordering
   prefix the GM asked for.
3. **Notes.** Each citations page's hand-authored notes are split by the SAME question as the prose, so a
   question and its footnotes are siblings, and a note is referenced by a stable key rather than a number.
4. **Numbers.** Footnote numbers are allocated at assembly in document order and are never typed by hand.
   16 of the record's 19 pages currently carry them out of document order, and two pages carry a
   duplicated reference id (R4).
5. **Scoping.** The per-section modes and the agent contracts that let a check read one fragment instead
   of one page - which is where the measured saving is actually collected.

What a reader opens does not change. The assembled pages stay committed, byte for byte, and the assembly
is checked at the gate and at the push.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A checking agent reads the entry it checks, and nothing else (Priority: P1)

A session changes one question on `research/water.html` and dispatches `record-format` and `quote-check`
over it. Today each agent reads the whole 163,008-byte page to check a section of 5,777 bytes on average (R1). After
this feature the agent's contract names the fragment, and the dispatch hands it one file.

**Why this priority**: this is the measured cost the GM asked about. It is also the only part that
recovers tokens rather than merely moving bytes between files.

**Independent Test**: dispatch a check over one changed entry and compare the bytes the agent reads
against the same check on the same entry before the split; the finding it reports must be the same.

**Acceptance Scenarios**:

1. **Given** a record page split into question fragments, **When** `record-format` is dispatched over one
   changed question, **Then** it reads that question's fragment and its notes fragment, not the page.
2. **Given** a source whose write-ups have just been changed, **When** `source-applicability` is
   dispatched, **Then** it reads that source's own file, not the 1,150,367-byte registry (R1).
3. **Given** a check dispatched over a fragment, **When** it reports, **Then** its findings are the ones
   it reported over the whole page for that same section (the seeded-fault re-run, FR-026).

---

### User Story 2 - A session edits one entry without opening the page (Priority: P1)

A session correcting one source's write-up, or one question's prose, opens a file of a few kilobytes,
edits it, and runs the assembly. It never reads the assembled page, and cannot edit it by mistake.

**Why this priority**: it is the GM's own framing of the problem, and it is what makes the fragments the
real source rather than a second copy.

**Independent Test**: correct one write-up end to end; the session's context must never hold the whole
registry.

**Acceptance Scenarios**:

1. **Given** the registry split by key, **When** a session needs the entry for `fei-1939`, **Then** a
   glob on the key names one file and nothing else is read.
2. **Given** an edit aimed at a committed assembled page, **When** exactly one fragment holds the text
   being replaced, **Then** the edit is rewritten to that fragment; where none or several do, it is
   refused with the fragments named.
3. **Given** an edited fragment, **When** the assembly runs, **Then** the committed page carries the
   change and every other byte of it is unchanged.

---

### User Story 3 - A footnote is written without choosing a number (Priority: P2)

A session adding a footnote in the middle of a question writes the note in that question's notes file
with a key, and references the key in the prose. The numbers on both pages, the back links, and the
hover script are allocated at assembly in document order.

**Why this priority**: it removes the hazard the GM accepted into scope, and it is what makes an
insertion cheap - today a note added mid-page either renumbers everything after it or is appended out of
order, which is how 16 of 19 pages came to be out of document order (R4).

**Independent Test**: add a note in the middle of a page and assemble; every number after it moves by
one, on both pages and in the script, with no hand edit.

**Acceptance Scenarios**:

1. **Given** a note referenced by key, **When** the pages are assembled, **Then** the reference, the note,
   the back link and the hover script all carry the same allocated number.
2. **Given** a note that nothing references, or a reference to a key no note defines, **When** the
   assembly runs, **Then** it fails and names the key and its file.
3. **Given** a note referenced twice in one page, **When** the pages are assembled, **Then** each
   reference gets its own id and the note's back link points at the first.

---

### User Story 4 - The reader's pages are unchanged (Priority: P1)

The reader opens `research/water.html` from disk exactly as before, with the same anchors, the same
links from every map modal, and the same hover notes.

**Why this priority**: the record is read by the GM and by players, and the split is an authoring change.
A page that drifted from its fragments would be a second copy of the record - the failure this whole
design exists to avoid.

**Independent Test**: at the landing of stages 1 and 2, the assembled files are byte-identical to the
files they replace; the diff is empty.

**Acceptance Scenarios**:

1. **Given** the split has landed, **When** the assembled pages are compared with the pre-split files,
   **Then** stages 1 and 2 differ in no byte, and stage 3 differs only in footnote numbers and the
   reference ids and back links that carry them.
2. **Given** a committed page that no longer matches its fragments, **When** the gate or a push runs,
   **Then** both refuse and name the page.
3. **Given** a map modal linking to a research section, **When** the reader clicks it, **Then** it opens
   the same anchor on the same page as before.

---

### Edge Cases

- **A question is renamed.** Its heading id is the record's anchor and a map modal's `Entry:` tag names
  its heading. The fragment's filename slug is a convenience; the anchor is the heading itself, exactly as
  today, so a rename is the same operation it is now and breaks nothing new.
- **A question is inserted between two others.** It takes an unused prefix between theirs; nothing else in
  the directory is renamed. Where the gap is exhausted, the assembly reports it and the directory is
  re-spaced deliberately.
- **Two fragments claim the same prefix.** The assembly refuses rather than pick an order.
- **A page with no footnotes at all** (`presentation.html`, 0 references - R4) assembles with no notes
  section and no citations page beyond its front matter, as it stands today.
- **A file in a page directory that is neither a question nor a notes file** is an error, not something
  silently skipped - a skipped fragment is a lost entry.
- **The works section** at the top of a citations page is still derived from the registry by `make
  citations`; the assembly does not re-derive it and does not fight it.
- **A source that no page cites** keeps its registry file: the registry is the roster, not a by-product of
  citation.

## Requirements *(mandatory)*

### Functional Requirements

**The assembly and what holds it**

- **FR-001**: The project MUST provide one command that writes every committed record page from its
  per-entry sources, and a check mode that exits non-zero while any committed page differs from what its
  sources would produce, naming each page.
- **FR-002**: The assembled pages MUST stay committed. A reader opens them from disk, which is the same
  reason `glossary.js` and `citations/<name>.js` are committed rather than built on the fly.
- **FR-003**: The gate MUST fail while any committed page differs from its assembly.
- **FR-004**: Both push routes MUST refuse while any committed page differs from its assembly. A
  record-only change takes the DIRECT route, which does not run the gate, so the gate alone would let a
  stale page reach main.
- **FR-006**: The assembly MUST be deterministic: the same sources produce the same bytes, on any machine
  and in any order of files on disk.

**The registry, one file per source**

- **FR-007**: Each entry of the registry's works roster MUST become one file named by its ordering prefix
  and its source key, in a directory of source files.
- **FR-008**: Everything of the registry that is not an entry MUST keep its text verbatim in a file of
  its own, so that no prose of the registry lives only inside a program: its front matter, each of its
  three visible sections (the works roster's heading and intro, the attested instances, the setting
  canon), and its closing. The front matter includes an 8,021-byte block that is commented OUT, holding
  two further headings and the old citing rules (R1); it is carried verbatim with the front matter, and
  is not a section.
- **FR-008a**: A heading inside an HTML comment MUST NOT be treated as a section, and a heading MUST be
  recognized wherever it stands on its line. The registry carries one of each (R1); a cut on the plain
  text would split a comment in two and invent two sections that no reader sees.
- **FR-009**: The assembled registry MUST carry its entries in the order it carries them today.
- **FR-010**: A source MUST be findable by its key alone, with one glob and no index file to consult.

**The pages, one file per question**

- **FR-011**: Each research page MUST become a directory holding one file per question, each named by a
  gapped numeric prefix and a slug of its heading, plus one file for the page's front matter and one for
  its closing, both verbatim.
- **FR-012**: Prefixes MUST be gapped, three digits a question and four a registry entry, counting by
  ten (`010`, `020`; `0010`, `0020`), so that inserting one between two others renames nothing. The
  authority is decision 1 of the four the GM approved - *"Gapped (`010-`, `020-`) so inserting a question
  doesn't renumber the directory"* - and not their own example *"a prefix like `01-`, `02-`"*, which is
  ungapped.
- **FR-013**: A question fragment MUST hold its heading, its prose and its HTML comments exactly as they
  stand on the page today, with nothing added and nothing normalized.
- **FR-014**: The assembly MUST place the questions in prefix order, and MUST refuse a duplicate prefix
  rather than choose between them.
- **FR-015**: A `cities/` page MUST split the same way, into a directory beside its siblings.

**The notes, beside the question they belong to**

- **FR-016**: Each citations page's hand-authored notes MUST be split by the SAME question as the prose
  and stored beside that question's fragment, so that one question's prose and notes are siblings.
- **FR-017**: A note MUST carry a stable key, unique within its page, and MUST NOT carry a number.
- **FR-018**: A reference in prose MUST name a note by that key, and MUST NOT carry a number.
- **FR-019**: The assembly MUST allocate footnote numbers in the order the references appear in the
  assembled page, from 1, and MUST write those numbers into the reference, the note, the note's back link
  and the hover script.
- **FR-020**: The assembly MUST fail on a reference to a key no note defines, on a note no reference
  names, and on a key defined twice in one page, naming the key and the file in each case.
- **FR-021**: Where one note is referenced more than once on a page, each reference MUST get its own
  document-unique id and the note's back link MUST point at the first. Two pages carry a duplicated
  reference id today (R4), which is invalid HTML and a back link that cannot resolve; this fixes it.
- **FR-022**: A note's back link MUST be produced by the assembly, not typed.

**Collecting the saving**

- **FR-023**: The check-preparing scripts MUST be able to address one question - the sections prepass, the
  quotation prepass and the drift report - and MUST name the fragment files a check should read.
- **FR-024**: The contracts of `record-format`, `quote-check`, `entry-drift` and `source-applicability`
  MUST tell the agent to read the fragment it is given rather than the assembled page. The defined agents
  launch with `omitClaudeMd: true` (feature 256), so their own contract is the only place this rule can
  reach them.
- **FR-025**: The record's own operative doc MUST state how to find an entry without reading a page - a
  glob by key for a source, a grep over a page's directory for a question - and MUST state that an
  assembled page is never hand-edited and where its sources are. This is where that instruction lives,
  together with the guard's own message (FR-028): NOT in the assembled pages themselves, which carry no
  such banner today and whose bytes SC-003 holds unchanged.
- **FR-026**: The saving MUST be demonstrated on a recorded case before the feature lands: one check
  re-run over a fragment against its recorded whole-page run, reporting the bytes read in each and
  whether the findings are the same. A check that reads less but finds less has not been improved
  (feature 255's ruling).

**What must not break**

- **FR-027**: Every existing test over the record MUST pass unchanged against the assembled pages -
  footnote resolution, the works derivation, link resolution, the visible-text rules and the modal's
  `Entry:` resolution - because the assembled page is the same document it was.
- **FR-028**: A guard MUST stop an edit aimed at an assembled page: rewritten to the one fragment that
  holds the text where exactly one does, refused with the candidates named where none or several do.
- **FR-029**: The engine's own reading of the record - the modal's questions and sources, the works
  derivation, the glossary - MUST continue to read the assembled pages, not the fragments, so that the
  split does not become a second parser of the record.

### Key Entities

- **Fragment**: one hand-authored file holding exactly one entry of the record - a source's registry
  entry, a question, or one question's notes. The unit a session edits and a check reads.
- **Page directory**: `research/<page>/`, everything one research page and its citations page are built
  from - the front matter, the questions in prefix order, each question's notes, and the closing.
- **Note key**: a stable name for one footnote, unique within its page, used by the prose to reference the
  note and by the note to identify itself. It survives insertions; the number does not.
- **Assembled page**: a committed file under `research/` that a reader opens and the engine reads. Derived
  from fragments, never hand-edited, checked at the gate and at the push.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The largest hand-edited file in the record falls from 1,150,367 bytes to under 40,000, and
  the entry a session or an agent opens is about 1,200 bytes for a source (the median of 920) and
  between 2,664 and 9,279 for a question, by page average. The bar clears the two largest fragments the
  split will create that are not questions, both measured: the registry's front matter at 8,712 bytes
  (8,021 of them the commented-out block) and the largest notes file any question would get, 28,118
  (R1). (FR-007, FR-008, FR-008a, FR-011, FR-013, FR-016)
- **SC-002**: A check over one entry reads that entry: on the recorded case of FR-026 the RECORD bytes
  entering the agent's context fall by at least 90% against its recorded whole-page run - it reads the
  fragment it was given and its notes, and nothing else under `research/` - and it reports the same
  findings. The fall in the agent's WHOLE input is reported by FR-026's run rather than held to a bar,
  because it depends on how much of a given run is the page: the recorded runs range from 23% to 98%
  (R3). (FR-023, FR-024, FR-026)
- **SC-003**: At the landing of stages 1 and 2, every assembled page is byte-identical to the file it
  replaces: the diff is empty. At stage 3 the only differences are footnote numbers and the reference ids
  and back links that carry them, and the set of (assertion, note) pairs is unchanged. (FR-001, FR-006,
  FR-009, FR-013, FR-014, FR-019)
- **SC-004**: No footnote number is typed by hand anywhere in the sources: a search of the fragments finds
  no `fn-<n>`, `fnref-<n>` or hand-written back link. (FR-017, FR-018, FR-021, FR-022)
- **SC-005**: A stale committed page cannot reach main: it fails the gate and both push routes refuse it,
  each naming the page. (FR-002, FR-003, FR-004)
- **SC-006**: A dangling reference, an unreferenced note, a duplicate key and a duplicate prefix each fail
  the assembly with the offending name and file in the message. (FR-020, FR-014)
- **SC-007**: Every test that reads the record passes unchanged, and the map modals resolve the same
  questions and open the same anchors as before. (FR-027, FR-029)
- **SC-008**: An edit aimed at an assembled page never silently lands: it is rewritten to the fragment or
  refused with the candidates named. (FR-028)
- **SC-009**: A session can find and open any entry without reading a page: one glob by source key, one
  grep over a page directory. (FR-010, FR-012, FR-015, FR-025)
- **SC-010**: The registry's prose survives the split: every word of its five groups is in a file, and
  none of it is inside a program. (FR-008)

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

This feature draws nothing and states nothing on a map. It does change two things a READER of the record
sees, so they are declared here rather than left to the diff.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Footnote numbers are allocated in document order at assembly, which renumbers most pages once | map drawing convention (the record's own presentation) | numbers are out of document order on 16 of 19 pages (R4) because a mid-page insertion cannot renumber by hand; the GM brought the renumbering into scope with *"do that as part of it"* | this spec FR-019, `research/CLAUDE.md`, the assembly's docstring |
| A reference to a note cited twice gets its own id, the back link points at the first | map drawing convention | two pages carry a duplicated reference id today (R4) - invalid HTML, and a back link that can only resolve to one of them | this spec FR-021, the assembly's docstring |
| The assembled pages stay committed and are what the engine and the reader read | map drawing convention | the pages are opened from disk, where a browser will not fetch a sibling; the same reason `glossary.js` and the citations scripts are committed | this spec FR-002, FR-029 |

## Assumptions

- The GM's "identical to what we have now" is taken at its word for the split itself (stages 1 and 2:
  byte-identical), and the renumbering they separately approved is landed as its own change on top, so
  that each diff proves one thing. A single combined landing would leave nobody able to say whether a
  changed byte was the split or the renumbering.
- The registry's works roster is kept in its present order rather than sorted, because its order is
  visible to a reader and sorting it would be a change the GM did not ask for.
- A source file is named by its key so the key alone finds it; the ordering prefix rides in front of the
  key rather than in a separate index, because an index is a second thing to keep in step. The GM raised
  the index question and left it open (*"whether we would have an index or whether the names of the files
  themselves would be things that you would use a find command"*); the session's answer, which they
  accepted, was to have none.
- `SOURCES.html` keeps its name and its place: it is what the engine parses and what a reader opens.
- The questions' headings remain the record's anchors. Filenames are not anchors, so a slug may be
  imperfect without consequence.
- The feature is tooling: no map is regenerated, no rule about a settlement changes, and no research pass
  is owed. Every task is `research: rendering`.

## Review history

- Round 1 (2026-09-20, `spec-fidelity`, Opus): CHANGES REQUIRED, five items, all applied; nothing in the
  request found missing, and every addition cleared as enforcement or as within what the GM approved.
  (1) FR-005 required every assembled page to carry a "this is assembled" notice in its own text, which
  no record page carries today and which would have added reader-visible bytes at the moment SC-003 says
  the diff is empty - deleted, dropped from SC-005's list, and the instruction moved to where it costs no
  byte of the record: FR-025's operative doc and FR-028's guard message. (2) SC-002's 90% bar was
  unreachable under its plain reading (on `255-qc-urban`, swapping a fragment for the page is a 62% fall
  in total input) - it now holds the RECORD bytes to 90% and has FR-026 report the whole-input fall
  rather than bar it. (3) The GM's premise that the citations page is script-assembled is the opposite of
  the truth and stage 3 depends on which is so - the Summary now corrects it, as it already corrected the
  premise R2 answers. (4) FR-012 cited the GM's ungapped example as the authority for gapping - it now
  cites decision 1 of the four they approved, and states the gap. (5) Three figures: the upper per-page
  question average is 9,279 and not 9,290; "19 to 39 a page" contradicted R1's own table and is now "2 to
  39"; and R2's Edit/Write line had no run behind it, so `measure.py R2` now prints it (96 calls, 92,986
  bytes). The reviewer's aside is taken up too: SC-001's bar now cites the two fragments that decide it,
  the registry's largest group of prose (5,443 bytes) and the largest notes file a question would get
  (28,118), both added to `measure.py R1`.
- Round 2 (2026-09-20, `spec-fidelity`, Opus): **FAITHFUL.** All five items confirmed RESOLVED, each
  figure re-run rather than read. On the aside's 28,153 against this session's 28,118: the difference is
  exactly one byte per note, the reviewer's hand count having included the newline between the `<li>`
  elements; the spec keeps the figure that comes out of a command, and both are upper bounds because the
  notes fragment that actually lands carries neither `id="fn-N"` nor the generated back link. The
  reviewer's one hygiene note - `research.md`'s preamble still said "all four" after R5 was added - is
  applied.
- Amendment after acceptance (2026-09-20), which resets the round counter: **the registry is not shaped
  the way a plain `<h2>` count reports it.** Checking the splitter's assumptions against the record
  before writing it turned up an 8,021-byte HTML comment in `SOURCES.html` holding two whole `<h2>`
  groups - the old citing rules and the re-sourcing queue - and one real heading that follows a space
  rather than starting its line. So: FR-008 rewritten to describe the registry as it is (three visible
  sections, the commented block carried verbatim with the front matter); FR-008a added for the cut rule;
  SC-001's cited figures corrected from the group-prose 5,443 to the front matter's 8,712; and the cut
  rule written into `data-model.md` and `contracts/fragment-format.md` with the reason byte-identity
  alone could never have caught it - splitting and rejoining is lossless wherever you cut, so the tests
  assert the section count and the heading ids too.
