# Feature Specification: open research questions, derived from the record

**Feature Branch**: `285-open-research-questions` (no branch; committed on `main` in the clone)

**Created**: 2026-09-28

**Status**: Draft

**Input**: the GM, 2026-09-28 ([`request.md`](request.md)): "a make target which assembles a list of guesses that could
use a research pass is better than trying to assemble something by hand, which then will drift out of date due to
repeating ourselves in multiple places."

## User Scenarios & Testing

### User Story 1 - See what research still owes (Priority: P1)

The GM (or a session planning a research pass) runs one make target and gets every place the research record
rests on a guess or on an unfound source, grouped by research page and question, each with the words of the
record that make it open. Nothing in the list is typed by hand: it is read from the record every time.

**Why this priority**: it is the whole request.

**Independent Test**: run the target on the current record; the rack length per household (homesteads 500)
appears, under its question, with its sentence.

**Acceptance Scenarios**:

1. **Given** the current record, **When** the target runs, **Then** every question fragment carrying a visible
   GUESS label or an unsettled absence note is listed, with its page, its question heading, its file, and the
   sentence (for a guess) or the search record (for an absence note).
2. **Given** a guess is replaced in the record by a cited finding, **When** the target runs again, **Then** that
   item is gone - nothing else needs editing.
3. **Given** a new GUESS is written into any question, **When** the target runs, **Then** it appears.

### User Story 2 - Know which map feature an open question touches (Priority: P2)

Each listed question names the map features (the modal classes) whose explanation is written from it, so the
reader can tell an open question that shapes what a map draws from one that does not.

**Independent Test**: the rack-length item names the `threshing yard` class (its `Entry:` names homesteads 505) -
or, where no class names the question, the item says no modal is written from it.

**Acceptance Scenarios**:

1. **Given** a class's `Entry:` names a question, **When** that question has an open item, **Then** the item
   lists that class.

### User Story 3 - Narrow the list (Priority: P3)

A session starting a research pass on one page, or on guesses only, can ask for just that slice.

**Acceptance Scenarios**:

1. **Given** a page name, **When** the target runs with it, **Then** only that page's items are listed.
2. **Given** a kind (guess or absence), **When** the target runs with it, **Then** only that kind is listed.

### Edge Cases

- A GUESS inside an HTML comment (a session note) is not the record's visible claim and is not listed.
- An absence note marked settled (two independent passes on different dates, research/CLAUDE.md) is listed apart,
  as searched twice, so it is not mistaken for a question nobody has tried.
- The word GUESS in a heading or a quoted source passage is still a label the reader sees; it is listed.
- Assembled pages (`research/<page>.html`) and citations pages repeat what the fragments hold; only the fragments
  are read, so nothing is counted twice.
- A GROUNDS note ("no source is owed") and a CONVENTION label are not open research and are not listed.

## Requirements

### Functional Requirements

- **FR-001**: A make target, `make open-questions`, MUST list every open research item derived from the research
  record at the moment it runs, with no hand-kept list anywhere.
- **FR-002**: An open item is (a) a GUESS label in a question's visible text, or (b) an absence note ("no publicly
  readable source") in a question's notes. Each item MUST show the page, the question heading, the fragment's
  path, and the sentence carrying the label (a) or the note's search record (b).
- **FR-003**: Each question listed MUST name the modal classes whose `Entry:` names it, or say none does.
- **FR-004**: The target MUST take optional filters by page and by kind, and MUST print the counts (per page and
  in total) before the list.
- **FR-005**: Settled absence notes MUST be marked as settled, not dropped.
- **FR-006**: Tested: the collector is unit tested on plain inputs (a guess in text, one in a comment, an absence
  note, a settled one, a grounds note, a convention label, a class naming a question), and one test runs it on the
  real record and finds the homesteads 500 rack-length guess.

### Key Entities

- **Open item**: page, question heading, fragment path, kind (guess | absence | absence-settled), the text.
- **Dependent class**: a modal class whose `Entry:` names the item's question.

## Success Criteria

### Measurable Outcomes

- **SC-001**: On the current record, the target lists the homesteads 500 rack-length guess, and its count of guess
  items equals the count of visible GUESS labels in the question fragments (`149` on 2026-09-28, research.md R1).
- **SC-002**: Replacing a guess in a fragment and re-running removes exactly that item (a unit test).
- **SC-003**: The target finishes in under `10 s` on the whole record.

## Decisions Recorded

A tooling feature: it draws and states nothing on a map, so there is no rendering decision.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Read the fragments, never the assembled or citations pages | this project's decision | the fragments are the one home; the assembled pages repeat them | plan D1 |
| A settled absence note is listed apart, not dropped | this project's decision | settled means searched twice, not answered | FR-005 |

## Assumptions

- The list prints to the terminal; no page is published (a session or the GM reads it where they run it).
- GUESS labels are written in capitals, as the record's rules require (research/README.md, four labels); a
  lower-case "guess" in prose is not a label.
- Code comments that say GUESS point at the record (the record is the one home per topic, feature 229), so the
  record alone is read.
