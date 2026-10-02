# Feature Specification: The record's checks owed by what an edit touches, and the question that says why it is asked

**Feature Branch**: `311-research-checks-owed` (no branch - committed on `main` in the clone)

**Created**: 2026-10-02

**Status**: Accepted - `spec-fidelity` FAITHFUL, round 3 (2026-10-02)

**Input**: The GM, 2026-10-02 (verbatim in `request.md`): *"I think we probably need a new subagent check to run on research
sections in order to see whether an explanation such as this is warranted for a section"*; *"do we have a way to exempt
certain subagent checks from firing when we are making an edit? ... we are adding here is definitionally something that is not
citing any research"*; *"not just do the correct thing, to kind of enforce us doing the correct thing"*; and, on the session's
proposal, *"Yes, please implement that as a spec kit feature and then work the feature from start to finish."*

## Context (observed 2026-10-02)

The record holds 237 questions (a count of the question pages in `research/questions/`, leaving out the `.drawing`,
`.notes` and `.originals` files), each a research page with a drawing page beside it, each with its notes. What the record's
checks are owed, and what holds a session to it, today:

| check | what decides it is owed | what holds it |
|---|---|---|
| `translation-check` | a script: each translation-and-original pair new or changed since the merge base; a pair that only moved owes nothing | the dispatch reads the script's list |
| `entry-drift` | a script: each modal whose section's body changed while its prose did not | the push refuses; one stated reason discharges |
| `quote-check`, `record-format` | the doctrine "every new or changed entry" | nothing at push; only the boxes of a physical research task |
| `source-reader` | the doctrine "every research pass" | the task boxes |
| `source-applicability` | the doctrine "every new or changed write-up, and before a source's numbers reach a map or a rule" | the task boxes |

Nothing refuses the opposite failure: a session may build a check bundle and dispatch a check over every question for a
one-word edit. A `record-format` pass is recorded at about 36k tokens in (`docs/review-ledger.md`, 2026-10-01), so a careless
sweep of the whole record would cost millions of tokens. And a paragraph that cites nothing - the intro the GM drafted for the
parley-room question - would today owe `entry-drift` on every modal written from that question, and, by the doctrine's
wording, `quote-check` and `record-format` on the whole question.

The parley-room question (`research/questions/0094-rooms-for-a-parley-across-a-border.html`) opens straight into its finding,
that no page we read has two powers meeting on the line itself. Its reason for being in the record - our border posts draw a
parley room astride the border, an invention of the setting, said only on its drawing page - is nowhere on the research page.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader knows why a question is in the record (Priority: P1)

A casual reader who opens a research question whose subject is something the setting has and history may not - the parley
room on a border is the example - is told first, in a short paragraph, what Rokugan has and why the question was asked, and that
the research below shows what the historical record holds instead.

**Why this priority**: it is the GM's complaint: *"why is this question here? Why am I being told about a thing which does not
exist?"*

**Independent Test**: open the parley-room question; its first paragraph after the heading (and the "Not to be confused with"
block) says what Rokugan has and that it is the setting's invention.

**Acceptance Scenarios**:

1. **Given** the parley-room question, **When** a reader opens it, **Then** an introductory paragraph in the GM's draft's sense
   stands before the findings.
2. **Given** every question in the record, **When** the new check has been run over all of them once, **Then** each question it
   rules NEEDS-INTRO has an intro, and each intro written has passed the check.
3. **Given** a question whose subject a reader would ask about unprompted (a grove, a ditch, a threshing yard), **When** the
   check reads it, **Then** it rules no intro needed.

---

### User Story 2 - An edit owes only the checks it can change (Priority: P1)

A session that edits the record is told, by one command, which checks the edit owes and on what - and builds no bundle and
dispatches no check that is not owed. The intro paragraph owes the new check and `record-format`, and nothing that reads a
source.

**Why this priority**: the GM: *"it would be a waste of time and tokens ... to add the kind of paragraph that I just explained
and then rerun all of the other subagent checks"*, and the worry of a future session re-running *"every subagent check for all
2,000 something of our resources"* for a formatting tweak.

**Independent Test**: on prepared deltas of each kind below, the command names exactly the owed units the table in FR-004 gives.

**Acceptance Scenarios**:

1. **Given** a delta that adds an intro paragraph to one question, **When** the owed checks are asked, **Then** they are that
   question's new check and its `record-format`, and nothing else.
2. **Given** a delta that changes one footnote's quoted passage, **When** asked, **Then** `source-reader` and `quote-check` are
   owed on that note alone, and `record-format` on the question.
3. **Given** a delta that renames or retags a question, or edits only HTML comments, **When** asked, **Then** nothing is owed
   (a rename changes the heading, so it owes the new check alone).
4. **Given** a whole-record sweep that changes formatting only, **When** asked, **Then** nothing that reads a source is owed.
5. **Given** a request to build a bundle for a check that is not owed, **When** it is made, **Then** it is refused with the owed
   list, unless a stated reason (a backfill, an audit the GM asked for) is given and recorded.

---

### User Story 3 - The push holds it (Priority: P1)

A push whose record delta owes a check that has not been answered is refused, naming each unanswered unit and the command that
builds its bundle; each unit is answered by a record written when its check returned, at the content the push carries, or by a
stated reason that ships with the push.

**Why this priority**: the GM: *"not just do the correct thing, to kind of enforce us doing the correct thing."* And the
project's standing rule that a doctrine without a mechanism is not a doctrine (feature 234).

**Independent Test**: a test pushes (dry) a delta with one owed `quote-check` unanswered and sees the refusal; answers it and
sees the push pass; edits the note again and sees the refusal return.

**Acceptance Scenarios**:

1. **Given** an owed unit with no record, **When** the push runs, **Then** it is refused, naming the unit.
2. **Given** a record written before the unit's content changed again, **When** the push runs, **Then** it is refused as stale.
3. **Given** a stated reason, **When** the push runs, **Then** it passes and the reason is recorded where the bypass log is.
4. **Given** a delta with no record change, **When** the push runs, **Then** the gate is silent.

---

### Edge Cases

- **A question moved between numbers or merged** (`make fragment-move`): a note or a translation pair that exists anywhere in
  the record at the merge base owes nothing; the heading change owes the new check alone.
- **A new question** owes every check: the new check, `record-format`, and `source-reader` and `quote-check` on every note.
- **A note deleted** owes nothing itself; the block that lost its mark changed in its words, so that block owes what FR-004
  gives a changed block (the assertion may now stand uncited).
- **A formatting-only change** - whitespace, line breaks, bold, a tag's attributes other than a note mark - changes no
  block's words and owes nothing.
- **A changed block with no note marks** that is not an intro: it owes `quote-check`'s unfootnoted-assertion reading of that
  question (a historical claim may have been added uncited), and `record-format`.
- **An intro paragraph** is marked as one, so the owed command can tell it from prose that should carry a footnote. It states
  what the setting or the map has and that the research follows, and it may name the class the question's own cited body or its
  drawing page already reaches - "an invention of the setting", as the GM's draft does; it adds no historical claim that body
  does not carry (the new check verifies the match).
- **A drawing page**: the new check reads it for context (it is where the map's choice is said) but is owed only on research
  pages; a drawing page's prose and notes owe `record-format`, `source-reader` and `quote-check` as a research page's do.
- **A source write-up** (`research/sources/`) new or changed in visible text owes `source-applicability` on it.
- **The backfill**: building bundles over every question for the new check is the declared occasion of this feature, so it is
  given its stated reason once.
- **A record written in another clone** does not travel; the push asks of the clone that pushes, as the review records do.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new defined check judges one research question as its casual reader meets it - its heading, its opening, the
  drawing page's account of what the map does, and the map elements written from it - and rules NO-INTRO-NEEDED, NEEDS-INTRO
  (with what the intro must say: what the setting or the map has, and the class the question's cited body or drawing page
  already reaches - attested, a deliberate deviation, a convention, an invention of the setting) or INTRO-PRESENT-OK /
  INTRO-PRESENT-FIX (an intro exists; it does or does not say why the question is asked, and it does or does not add a
  historical claim the cited body does not carry). It is pinned to a tier like every defined check and launches without the project's auto-loaded files.
- **FR-002**: The record has a marked intro paragraph form, placed after the heading and the "Not to be confused with" block,
  stated in the style guide and in the research directory's rules, and recognized by the owed command. The mark carries no
  styling of its own; the reader sees an ordinary opening paragraph.
- **FR-003**: One command names every unit the record delta owes, against the merge base with main, one unit per line with the
  check, the subject (a question, a note of a question, a source, a modal class, a translation pair) and the occasion.
- **FR-004**: What owes what. A heading, a block or a note is CHANGED only when its words change - its text with HTML
  comments, markup and whitespace normalized away, its note marks kept - and only when those words stand nowhere in the record
  at the merge base (so a move, a renumbering or a merge owes nothing):

  | what changed since the merge base | owes |
  |---|---|
  | a question new to the record | the new check, `record-format`, `source-reader` and `quote-check` on every note |
  | a question's heading text | the new check |
  | an intro paragraph added, changed or removed | the new check, `record-format` |
  | a note's text new or changed (its quoted passage, its link, its absence wording), not present anywhere in the record at the base | `source-reader` and `quote-check` on that note, `record-format` on the question |
  | a block carrying a note mark changed | `quote-check` on the notes it carries (SUPPORTS), `record-format` on the question |
  | a changed block with no note mark, other than an intro | `quote-check`'s unfootnoted-assertion reading on the question, `record-format` |
  | only HTML comments, tags, the contents or the numbering | nothing |
  | a source write-up's visible text | `source-applicability` on that source |
  | a translation pair | `translation-check` (as today) |
  | a section a modal's `Entry:` names, its findings changed | `entry-drift` on the modal (as today), but not for a change to its intro or its comments alone |

- **FR-005**: Building a check bundle for a check and subject the delta does not owe is refused with the owed list; a stated
  reason of two words or more overrides it and is recorded. A bundle for `quote-check` with no notes named holds only the owed
  notes.
- **FR-006**: When a check returns, one command records that the unit was answered, with the verdict counts and the content the
  check read; the record is stale once that content changes.
- **FR-007**: The push, on both routes, refuses a record delta with an owed unit unanswered or answered at stale content, naming
  each and the bundle command; one stated reason discharges the refusal and is written to the bypass log; `entry-drift`'s
  existing refusal and reason are folded into this one, not run twice.
- **FR-008**: The new check is run once over every question in the record (the backfill); each NEEDS-INTRO or
  INTRO-PRESENT-FIX ruling gets its intro written or fixed, in the GM's draft's voice and within the setting's canon, and each
  written intro passes the check in at most two rounds.
- **FR-009**: The parley-room question carries its intro: Rokugan's parley room on a border, each side entering by a door in
  its own lands and sitting across a table placed on the line, an invention of the setting, and the research below showing what
  the historical record holds instead.
- **FR-010**: The doctrine that names when each record check runs (the research directory's rules, the research doctrine, the
  page-session rules, the project's guard table, each check's own contract) says it from the owed command, with no wording left
  that a session could read as "every check on every edit".

### Key Entities

- **Owed unit**: a check and its subject, with the occasion that owes it.
- **Answer record**: a unit, the verdict counts, and a fingerprint of the content the check read.
- **Intro paragraph**: the marked opening paragraph saying why a question is in the record; it cites nothing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-002, FR-004, FR-009): For the intro-only delta on the parley-room question, the owed list is exactly two units: the new check and
  `record-format` on that question.
- **SC-002** (FR-003, FR-004): Replayed over the last 30 record-only commits on main, the owed command names no `source-reader`,
  `quote-check` or `source-applicability` unit for any commit that changed no note, no noted block and no write-up; and the
  count of units each commit owes is reported beside what the doctrine's "every new or changed entry" would have owed.
- **SC-003** (FR-001, FR-008): Every question in the record has been read by the new check once, and every question it ruled in need of an
  intro has one that it passed.
- **SC-004** (FR-005, FR-006, FR-007): A dry push of a delta with an unanswered owed unit is refused, and with the unit answered it passes; a bundle
  request for a unit not owed is refused without a reason; both are tests run by the gate.
- **SC-005** (FR-001): The new check, seeded with questions whose ruling is known (the parley room without its intro; a plain farm
  subject; an intro that adds a historical claim its cited body does not carry), returns the known ruling on each, three runs a leg.

- **SC-006** (FR-010): no passage of the research rules, the research doctrine, the page-session rules or the five check
  contracts says a record check runs on "every new or changed entry" or "every research pass" without naming the owed command.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The parley room on a border is introduced as an invention of the setting | deliberate deviation, already recorded | the drawing page records it as this setting's own; no page we read has two parties meeting on the line | `research/questions/0094-rooms-for-a-parley-across-a-border.html` (the intro); its drawing page |
| The new check is owed on a new question, a changed heading or a changed intro, not on every edit to a question | this project's decision, on the GM's acceptance of the proposal | a question's purpose changes with its subject, which its heading names; owing it on every edit is the waste the GM named. Declined: owing it whenever the opening paragraph changes (a sweep's wording edits would owe it on most questions) | this spec; the owed command's docstring |
| A changed block that carries note marks owes `quote-check` on those notes, beyond the proposal's "a changed note owes quote-check on that note" | this project's decision, a departure from the accepted proposal recorded here | rewording an assertion can make a faithful quotation stop supporting it (the check's SUPPORTS half), and only the words count, so a formatting sweep owes nothing | this spec; the owed command's docstring |
| A changed block with no note mark, other than an intro, owes `quote-check`'s unfootnoted-assertion reading, beyond the proposal's "record-format only" | this project's decision, a departure from the accepted proposal recorded here | the proposal gave "record-format only" to all prose with no footnote marks, the intro being its example; this spec keeps it for the marked intro alone, because new uncited prose may carry a historical claim | this spec; the owed command's docstring |
| An intro paragraph is marked, and cites nothing | this project's decision | the GM: an intro is *"definitionally something that is not citing any research"*; marking it is what lets the owed command spare the source-reading checks | the style guide; the research directory's rules |
| Answer records live in the pushing clone, keyed to content | this project's decision, following the review records (feature 294) | a record committed beside the question would churn every file a check touches and conflict across parallel clones | the gate's comment |

## Assumptions

- The map review checks (feature 294) are untouched; this feature is the record's checks only.
- `record-style` stays a sweep check owed by the feature that declares a sweep (feature 292); it is not added to the owed table.
- `source-applicability` before a source's numbers reach a map or a rule stays on the physical research task's box; only the
  write-up half is owed by the delta.
- The intros the backfill calls for are written by this session or by page sessions it starts, from the setting's canon read
  through `make canon`; none invents a setting detail the GM's notes contradict.

## Review history

- **Round 1** (`spec-fidelity`, 2026-10-02): CHANGES REQUIRED - six items: "changed" undefined (a formatting sweep would owe
  quote-check everywhere); the intro's class versus "asserts nothing historical"; rows 5 and 6 departing from the accepted
  proposal unrecorded; "styled on the built site" not asked for; the deleted-note edge case contradicting itself; the 237 with
  no method. All six applied: FR-004 defines CHANGED by words, with the formatting-only edge case; FR-001 and the intro edge
  case let the intro name the class its cited body reaches; two rows added to Decisions Recorded; FR-002 carries no styling;
  the deleted-note case rewritten; the count's method stated.
- **Round 2** (`spec-fidelity-verify`, 2026-10-02): all six round-1 items RESOLVED; two new: SC-005's third seed still on the
  old rule, and the unmarked-block decision row misstating the proposal's scope. Both applied (SC-005 seeds "an intro that adds
  a historical claim its cited body does not carry"; the row says the proposal gave "record-format only" to all unmarked prose).
- **Round 3** (`spec-fidelity-verify`, 2026-10-02): **FAITHFUL** - both round-2 items resolved, no new departure.
- **Lint-only edit after acceptance** (2026-10-02): `spec-lint` required each success criterion to name its FRs; the FR ids
  were added to SC-001..SC-005 and SC-006 states FR-010's existing requirement as a criterion. No requirement changed.
