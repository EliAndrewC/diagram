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

Each listed question names the map features that depend on it, so the reader can tell an open question that
shapes what a map draws from one that does not. A question reaches a map feature three ways, each read from what
the repository already records (research.md R2): a modal class's `Entry:` names it; a question a class names links to
it; or the engine's code cites it (its heading or its anchor in a comment or docstring, with file and line).

**Independent Test**: the rack-length item (homesteads 500, which no class's `Entry:` names) names the `threshing
yard` class, reached through 505 - which the class names and which links to 500 - and names any engine file that
cites 500. A question none of the three reaches says so: no map feature was found depending on it.

**Acceptance Scenarios**:

1. **Given** a class's `Entry:` names a question, **When** that question has an open item, **Then** the item
   lists that class.
2. **Given** a question a class names links to another question, **When** the linked one has an open item, **Then**
   the item lists that class, saying it is reached through the linking question.
3. **Given** an engine source file quotes a question's heading or anchor, **When** that question has an open item,
   **Then** the item lists the file and line.

### User Story 3 - Guesses marked outside the record (Priority: P2)

A guess is sometimes marked where the rule is coded or journaled and not in the record (research.md R2: the
kitchen postern's 6 ft passage is a GUESS in `compound.py` and unlabeled in the record). The list takes these too,
so no marked guess is missed.

**Independent Test**: the target lists `compound.py`'s postern GUESS with its file and line.

**Acceptance Scenarios**:

1. **Given** a tracked text file of the skill outside `research/` and `tests/`, other than the tooling's logs,
   carries a GUESS label, **When** the target runs, **Then** the line is listed under its file, with its line number
   and text.

### Edge Cases

- A GUESS inside an HTML comment (a session note) is not the record's visible claim and is not listed.
- An absence note marked settled (two independent passes on different dates, research/CLAUDE.md) is listed apart,
  as searched twice, so it is not mistaken for a question nobody has tried.
- The label GUESS (or its plural GUESSES) in a heading or a quoted source passage is still a label the reader sees; it is listed.
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
- **FR-003**: Each question listed MUST name the map features that depend on it, by the three routes of User Story
  2 (a class's `Entry:`; a link from a question a class names, saying through which; an engine file citing it, with
  file and line), or say that none of the three found one.
- **FR-004**: The target MUST print the counts (per page, per kind, and in total) before the list.
- **FR-007**: The target MUST also list every GUESS label in a tracked text file of the skill outside `research/`
  and `tests/` - engine code and docstrings, the pool's notes, the skill's docs - with file, line and the line's
  text, grouped by file - the hand-drawn plans (the tracked `pool/**/*.svg`, which are sources, not renders) among
  them. Only the logs the tooling writes (`dev/bypass-log/`, `dev/run-log/`, `dev/perf-log/`) are not read: they
  repeat what a session typed elsewhere (research.md R2).
- **FR-005**: Settled absence notes MUST be marked as settled, not dropped.
- **FR-006**: Tested: the collector is unit tested on plain inputs (a guess in text, one in a comment, an absence
  note, a settled one, a grounds note, a convention label, a class naming a question, a question linked from it,
  an engine file quoting a heading, a GUESS in a tracked file outside the record), and one test runs it on the real
  record and finds the homesteads 500 rack-length guess reached through 505 and the `compound.py` postern guess.

### Key Entities

- **Open item**: page, question heading, fragment path, kind (guess | absence | absence-settled), the text.
- **Dependent map feature**: a modal class whose `Entry:` names the item's question; a class whose named question
  links to it (naming that linking question); or an engine file and line citing the question.
- **Guess outside the record**: a file, a line number and the line's text.

## Success Criteria

### Measurable Outcomes

- **SC-001** (FR-001, FR-002, FR-004, FR-005): On the current record, the target lists the homesteads 500 rack-length guess, and every visible GUESS
  label in the question fragments (`149` on 2026-09-28, research.md R1) falls in a listed guess item - the items being
  sentences, one sentence may carry two (research.md R3); the counts print first and a settled absence is marked.
- **SC-002**: Replacing a guess in a fragment and re-running removes exactly that item (a unit test; FR-001, FR-006).
- **SC-003**: The target finishes in under `10 s` on the whole record (FR-001).
- **SC-004** (FR-003, FR-007): On the current tree, the target lists the `compound.py` kitchen-postern GUESS with its file and line, and
  names the `threshing yard` class for the homesteads 500 rack-length item.

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
- The research record is the home of a finding (feature 229), but a guess is not always written there: R2 found
  guesses marked only in code, so the list reads both (FR-007).

## Review history

- Round 1 (spec-fidelity, 2026-09-28): CHANGES REQUIRED - (1) the Assumption that the engine's GUESS comments all point
  at the record, which decides the target's scope, was not measured, and a sample contradicts it (`grep -rn GUESS` over
  `l7r/**/*.py`, observed 2026-09-28: 90 lines; `compound.py:505`, the kitchen postern's `6 ft` passage, has no GUESS in
  the record; `buildings.md` and pool notes carry the word too): measure it in research.md, and either list the guesses
  outside the record or put their exclusion to MODE 1; (2) US2's Independent Test misstates the fact - the rack-length
  GUESS is in homesteads 500, which no class's `Entry:` names; the threshing yard names 505 - so FR-003's `Entry:`-only
  mechanism reports "no modal" for the motivating item, which the map draws: correct the test and make FR-003 find the
  map feature that depends on the question; (3) US3 and FR-004's page and kind filters are UNREQUESTED: cut them.
- Round 2 (spec-fidelity VERIFY, 2026-09-28): CHANGES REQUIRED - round 1's (2) and (3) RESOLVED (505 links to 500
  twice and the threshing yard's `Entry:` names 505, checked; the filters are gone); (1) PARTLY RESOLVED: R2's counts
  re-ran exactly, but FR-007's exclusion of "a rendered sheet" as generated output is false for the tracked `pool/**/*.svg`,
  which are hand-authored plan SOURCE with only the png derived (`hayakawa-magistracy.gen.py`'s docstring), and two
  of their four GUESS lines are found nowhere else (`hayakawa-magistracy.svg:860`, the east room;
  `ubame-magistracy.svg:354`, the period post): read the tracked svgs, correct R2's row, and align US3's scenario
  ("outside `research/`") with FR-007's `research/` and `tests/`; and a new contradiction the change introduced: Key
  Entities still defines the **Dependent class** by `Entry:` alone, against FR-003's three routes, and has no entity
  for FR-007's file-and-line items: redefine it as the map features FR-003 finds and add the outside-the-record item.
- Round 3 (spec-fidelity VERIFY, 2026-09-28): FAITHFUL - round 2's (1) RESOLVED: FR-007, US3's scenario and plan D7
  read every tracked text file outside `research/` and `tests/` but the tooling's logs, the hand-drawn `pool/**/*.svg`
  plans included; R2's svg and bypass-log rows corrected; a re-run of `git ls-files -z` less those paths through
  `grep -I -c -w GUESS` gave `117` lines in `37` files (85/25, 20/5, 8/5, 4/2), R2 exactly, so no tracked generated
  file carries the word and dropping D7's old `*.json`/`*.html` exclusions adds nothing (on round 3's own run);
  (4) RESOLVED: Key Entities define the dependent map feature by FR-003's three routes and add the guess outside
  the record. Plan D3's question-up-to-`?` match implements FR-003's "an engine file citing it" and D6 cites R1's
  dated file counts; no contradiction found.
- Amendment pass, round 1 (spec-fidelity VERIFY, 2026-09-28): CHANGES REQUIRED - the amendment is faithful: SC-001's
  "every visible label falls in a listed guess item" implements FR-002 given D2's sentence items, the plural label
  (spec edge case, plan D2) is the GM's "things marked as guesses", the SCs' FR tags and tasks.md T01-T03 add nothing
  unrequested; `make open-questions` printed `139` guess sentences, `580` absences in `2.1 s` (on this round's own
  run). Three figures and one plan line to correct: (1) R3's `12` GUESSES does not hold by R3's own method - the
  question fragments carry `6` (`5` visible, `1` in a comment); `12` counts the assembled pages too (`144` GUESS +
  `5` GUESSES = `149` visible, on this round's own run); (2) R4's `123` lines outside the record (docs `6`) did not
  reproduce: the collector as committed at 7080a0c92 and at 09968f383, and `git grep -I -c -w -E "GUESS|GUESSES"`
  over the same paths, give `122` (buildings.md 2, dev 1, future-work 2, l7r 92, pool 25; on this round's own run);
  (3) plan D7 still reads "the whole word `GUESS`" although D2 and the spec's edge case now make GUESSES the label
  too and FR-007 lists "every GUESS label" (09968f383's message says D7 names the plural; it does not): D7 should
  read "the whole word `GUESS` or `GUESSES` (D2)".
