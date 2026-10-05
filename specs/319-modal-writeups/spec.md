# Feature Specification: Modal write-ups a reader can take in

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=319-modal-writeups`)

**Created**: 2026-10-03

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: *"if someone clicks on a farmhouse then what do they care about"*;
*"this is kind of just like a hodgepodge of different facts. And there's not really a gestalt to it"*; *"we could have an
overview tab and a guesses tab and a references tab"*; *"the first phase of the feature is going to be figuring out what
guidelines make a good modal. And then writing subagent checks for them"*; *"once we get to a point where I have you do a
rewrite on one map features modal, and then I am happy with it without any tweaks, then I will probably just have you do all
of the rest"*; *"I would expect our settlement maps to just all pull from a standardized set of modals"*; *"magistracy diagrams
would get custom modals"*, with *"a different set of rules for that kind of thing"*.

## Context (observed 2026-10-03, method: the session's read of the page code, the class docstrings and the pool notes)

- A hamlet modal is the docstring of its `Kind` class (`l7r/diagram/interactive/classes/`, 56 classes in five modules): `What:`
  and `Why:` paragraphs, a `Note:` justifying the class's ONE label (accurate / deviation / convention / guess), an optional
  `Caveat:` shown as "On the drawing:", and the sibling line "Not to be confused with ...". A `guess` label makes the modal OPEN
  with "This is a guess - " followed by the whole `Note:` (`interactive/CLAUDE.md`, "The presumption of accuracy"). The label is
  one per FEATURE, so a feature whose existence is read but whose size is guessed (the garden) is announced as a guess.
- The prose has no fixed questions to answer. The farmhouse modal spends most of its words on how a house is turned and reached,
  and does not say what the house was built of, who lived in it or how many.
- **How references are chosen today**: "See references (N)" lists the research pages the class's `Entry:` tag names - the
  pages the docstring's author wrote it FROM, picked by hand when it was written (`interactive/sources.py`
  `research_questions`). Nothing compares that list with what the prose says or with the 472 questions in the record. The
  farmhouse's five are three questions (0029 farmhouses, 0028 the farmstead, 0081 village lanes) and the drawing pages of two
  of them; `research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.html`, which answers how many
  lived in the house, is not among them.
- A hamlet's per-map facts reach its modals through the `## Map notes` / `### Features` block of its `.notes.md` (all five pool
  hamlets carry one, e.g. the burial ground, the retirement-house count, the harvest weather under the threshing yard, a grave
  island; the entries differ map to map). The title card says
  where the place is, its size and its crops; it lists none of the knobs the map rolled (`settlement/_knobs.py` declares 16).
- Magistracy and shrine sheets use a separate registry (`interactive/compound_kinds/`, five modules) in the same docstring form.
  Some kinds are general (a well, a hearth, a genkan); some are particular to one sheet (`particulars.py`: the vermilion
  workshop and its threshold stones); per-sheet facts about general kinds (Ochiba's two-altar Inari hall on the compound
  shrine, Hayakawa's enlarged bath, Ubame's shuttered wing) are in each sheet's `.notes.md` `### Features` block.
- The one check on modal prose is `entry-drift`, which asks only whether a modal still agrees with the pages its `Entry:` names.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader clicks a farmhouse and learns what it was (Priority: P1)

A casual reader clicks a feature on a hamlet map and, in one short read, learns what it was for, what it looked like, and how
many it held - the standard questions for its kind of feature - in plain prose with a shape, not a list of placement rules.

**Why this priority**: the GM's request; the farmhouse is the named pilot.

**Independent Test**: open the farmhouse modal on a pool hamlet page in the clone and read it against the building guidelines.

**Acceptance Scenarios**:

1. **Given** the farmhouse modal, **When** read, **Then** it answers the building questions: its purpose (who lived there, what
   work was done in it, whether animals lived in it); its look (materials, walls, roof, whether its openings close); and its
   occupancy as a typical figure with a low and a high one - each answered from the research, or listed as a guess, or stated
   as not found.
2. **Given** a placement rule the map follows (how a house is turned, how far it stands from the paddy), **When** the modal is
   read, **Then** the rule is not on the About tab unless the guidelines name it as something a reader asks of that kind.
3. **Given** the GM's review of the pilot in the clone, **When** the GM asks for changes, **Then** the guidelines change first
   and the modal is rewritten from them, so every lesson reaches every later modal.

---

### User Story 2 - Guesses are told apart without leading the modal (Priority: P1)

A feature whose existence is well researched never opens with "This is a guess". What the project guessed - a size, a
proportion, a crop list - is a bulleted list on its own tab, shown only when there is one.

**Why this priority**: the GM: the garden's *"this is a guess"* first line *"is extremely misleading"*.

**Independent Test**: open the garden modal: the first tab says what a kitchen garden was without a guess label; the guesses
tab lists the bed's size and crops as guesses.

**Acceptance Scenarios**:

1. **Given** a feature with no guesses, **When** opened, **Then** it has no guesses tab.
2. **Given** a guess, **When** listed, **Then** it is one bullet saying what was guessed and, in a clause, why (what was searched
   and not found, or what it was reckoned from).
3. **Given** a deliberate deviation or a map drawing convention, **When** the modal is read, **Then** it is still told in the
   modal (constitution XII), in the place the guidelines assign it.

---

### User Story 3 - References are exactly what the write-up covers (Priority: P1)

The references tab lists the research questions behind what the modal says - every question a statement rests on, and no
question the modal does not draw on.

**Why this priority**: the GM: *"link specifically to the things which relate to what we decided to cover in the write-up, and
then simply not link to things which are not covered"*.

**Independent Test**: a check maps each statement of the modal to a listed question and each listed question to a statement.

**Acceptance Scenarios**:

1. **Given** a rewritten modal, **When** checked, **Then** every statement is supported by a question on its references tab
   and every listed question supports a statement.
2. **Given** a standard question the modal answers as "not found", **When** checked, **Then** the check searched the record for
   a question that answers it (by tag and by term) and reports one it finds, so research the record holds is not missed.

---

### User Story 3b - The Depiction tab says how the map draws the thing (Priority: P1)

A reader who wonders why every farmhouse looks alike, or why a mark is so bold, opens the Depiction tab and is told how the map
draws the thing - what is drawn larger or bolder so it reads and what it really was like, what is shown one way where reality
varied and why - and finds the "how our maps draw it" pages linked there.

**Why this priority**: the GM, 2026-10-04: *"I think I want 'How we draw it' things on its own tab."*

**Independent Test**: open the farmhouse modal: its Depiction tab links its drawing pages and says nothing the map does not draw;
`modal-depiction` passes it.

**Acceptance Scenarios**:

1. **Given** a kind with drawing pages and nothing notable to explain, **When** its Depiction tab is opened, **Then** it lists
   those pages alone.
2. **Given** a kind with neither, **When** its modal opens, **Then** there is no Depiction tab.
3. **Given** a single drawn form where the research records a variety the engine does not draw, **When** the tab is checked,
   **Then** it is not presented as a deliberate convention, and the drift is a finding in the claims report.

---

### User Story 4 - A title card lists the choices that made this settlement (Priority: P2)

A reader clicks a hamlet's title card and sees what was chosen for this settlement - the settlement form, the field form, the
lane web, the bamboo, the harvest weather and the rest - each value a link to a modal explaining that form.

**Why this priority**: the GM's Inashiro example; it is where the per-settlement differences go, so the feature modals can be
the same on every map, apart from the items FR-015 conditions on the settlement's knobs.

**Independent Test**: open Inashiro's title card; it lists its choices, among them "nucleated", and clicking "nucleated" opens a
modal explaining the nucleated form.

**Acceptance Scenarios**:

1. **Given** a hamlet page, **When** its title card is opened, **Then** it lists every per-settlement choice the map made
   (rolled from the seed or set by its declaration), each with its value.
2. **Given** a listed value, **When** clicked, **Then** a modal for that value opens, written to the same guidelines, with the
   same tabs, and the same on every map.
3. **Given** a hamlet's per-map facts now in its notes' `### Features` block, **When** this feature lands, **Then** each is a
   title-card entry (a choice or a count of this settlement) and no hamlet feature modal varies by map except by FR-015's
   knob-conditioned items.

---

### User Story 5 - Magistracy and estate modals follow their own lighter guidelines (Priority: P2)

A magistracy, shrine or estate sheet keeps custom modals for what is particular to it (the two-sided Inari shrine, the vermilion
workshop), written to a lighter set of guidelines for setting-specific features and checked against the GM's canon rather than
the historical record; its general kinds (a well, a hearth) follow the standard guidelines.

**Why this priority**: the GM asks for both rule sets and for the existing sheet modals to be reviewed.

**Independent Test**: every kind on the pool's magistracy and shrine sheets is classed general or particular, and each has passed
the check for its class.

**Acceptance Scenarios**:

1. **Given** a particular kind, **When** checked, **Then** the check holds it to the particular guidelines and to the GM's canon
   (no contradiction of the setting notes), and any real-world research it draws on is linked.
2. **Given** a general kind, **When** checked, **Then** it is held to the standard guidelines for its general part, like a
   hamlet feature; its per-sheet text is held to the particular guidelines.

---

### User Story 6 - The guidelines are proved one feature at a time, then rolled out (Priority: P1)

The guidelines are written, the checks built, the farmhouse rewritten and iterated with the GM, then a second feature, and only
when a rewrite is accepted with no changes are the rest rewritten.

**Why this priority**: the GM's sequence.

**Independent Test**: the tasks show the GM's verdict on each pilot before the rollout starts; the GM's go-ahead of 2026-10-05
closed the pilot phase (FR-010).

**Acceptance Scenarios**:

1. **Given** a pilot rewrite, **When** it is ready, **Then** the session regenerates the pilot hamlet's page in the clone, gives
   the GM its path, and waits for the GM's verdict; nothing lands on main before the feature closes (except this spec claim).
2. **Given** a pilot whose first rewrite the GM asks to change, **When** it is settled, **Then** a further feature is piloted the
   same way before any rollout - until the GM's go-ahead, which ended the pilots (2026-10-05).
3. **Given** the GM's go-ahead (given 2026-10-05, replacing the "accepted with no changes" condition), **When** the rollout runs, **Then** every hamlet class, every knob value
   and every sheet kind is rewritten and checked.

### Edge Cases

- A feature whose standard question has no answer in the record: the modal says so plainly on the About tab ("no record of ...
  was found") or lists the drawn value as a guess - never silence, never a made-up figure.
- A feature that is not a building and not a field (a stream, a lane, a notice board): the non-building guidelines decide its
  questions; where a kind fits neither set, the guidelines grow a set for it during the rollout and the GM sees it in the
  rollout report.
- A feature with no research behind it at all (`fallow` lists no references today): its references tab is absent, and the check
  confirms the record holds nothing on it.
- A modal's references tab would list a question whose page covers ten things the modal mentions once: it is listed; a question
  is linked for supporting a statement, not for its size.
- A knob a hamlet does not roll (pinned by its declaration or by the GM, as Inashiro's form is): listed on the title card with
  its value all the same; whether it was rolled is not the reader's concern.
- A sheet kind used on several magistracies but particular to the setting (a threshold stone on more than one sheet): classed
  particular; reuse across sheets does not make it general.

## Requirements *(mandatory)*

### Functional Requirements

**Guidelines**

- **FR-001**: The project MUST hold written guidelines for a standardized modal: the reader it is written for, the length, the
  order, and for each kind of feature the questions its About tab answers. For a BUILDING: purpose (residence, workplace, or
  both; whether animals lived inside); appearance (materials, walls, roof, whether the doorways close); and capacity (residents,
  stored goods or animals, as a typical figure with a low and a high one, not record extremes). For a non-building feature the
  questions are set by the guidelines, starting from the garden pilot.
- **FR-002**: The guidelines MUST say how a guess, a deliberate deviation and a map drawing convention appear (FR-005), and that
  nothing is announced as historically accurate (the presumption of accuracy, feature 156, stands).
- **FR-003**: The project MUST hold separate guidelines for a PARTICULAR modal - a kind particular to one sheet or to the setting
  on a magistracy, shrine or estate sheet - and for the particular part of a general kind's modal on such a sheet (its
  `### Features` text), which stays on that sheet's modal: what it explains, how canon is used, how real-world research it draws on is linked,
  and the lighter checking it gets.
- **FR-004**: Every standardized modal on a settlement map MUST be the same on every map: no per-map text in a feature modal;
  the one variation is FR-015's - an item conditioned on the settlement's knobs - so two maps with the same values for those
  knobs show the same modal.
  A settlement's own facts and choices go on its title card (FR-009).

**The modal**

- **FR-005**: A modal MUST be tabs: a first tab carrying the write-up named "About" (the GM's choice, 2026-10-03, FR-013), a
  "Guesses" tab with a bulleted list of what was guessed - shown only when there is a guess - a "Depiction" tab (FR-014) and a
  "References" tab, shown only when there is a reference. A modal MUST NOT open with "This is a guess" because one of its details
  is guessed; a guess is a property of a statement, not of the feature. A deliberate deviation is said in the write-up where it
  applies; how the map draws the thing - a map drawing convention with the true figure, a standardization - is the Depiction
  tab's (amended 2026-10-04: until then a convention was said in the write-up's appearance part).
- **FR-006**: The References tab MUST list exactly the research questions the modal's statements rest on (US3); the "how our
  maps draw it" pages are the Depiction tab's (FR-014), not the References tab's.
- **FR-007**: The sibling distinction ("Not to be confused with ...") and the glossary tooltips MUST keep working in the new
  form.

**Checks**

- **FR-008**: Subagent checks MUST review each rewritten modal, as the research is reviewed: (a) FORM - it answers its kind's
  questions in the guidelines' order and voice, its guesses are on the guesses tab; (b) ACCURACY - each statement is supported
  by the research it links, and each guess is truly absent from the record; (c) REFERENCES - the linked set is exactly what the
  statements rest on, and the record searched for a question answering any question the modal leaves "not found". A particular
  modal gets the particular checks (form, and no contradiction of canon). Each check is a defined agent on a pinned tier, reads a
  bundle, and is OWED by a changed modal and enforced at the push, as entry-drift is.

**The title card**

- **FR-009**: A hamlet's title card MUST list every per-settlement choice its map made (each knob's value, and the per-map
  facts now in `### Features`), each value opening a standardized modal for that value written to FR-001 and FR-005.

**Process and scope**

- **FR-010**: The work MUST run in the GM's order: guidelines and checks; the farmhouse rewritten and iterated with the GM; a
  second feature (the garden, the GM's non-building example) rewritten from the guidelines and iterated. If the GM asks for
  changes on a pilot's first rewrite, a further feature is piloted the same way, one at a time. The rollout starts only on the
  GM's go-ahead after a feature's first rewrite is accepted with no changes. Every change the GM asks of a pilot MUST be made in the guidelines (and the checks where they apply) before the
  modal. **The pilot phase closed with the GM's go-ahead of 2026-10-05**, which replaced the "accepted with no changes" condition
  (the garden took one change, the windbreak the knob change): no further pilot, verdict or example is owed for any kind,
  including a kind whose guidelines are first applied in the rollout (FR-016).
- **FR-011**: The rollout MUST cover every hamlet class (56), every knob value's modal, every general sheet kind, every
  particular sheet kind and every per-sheet `### Features` entry on the pool's magistracy and shrine sheets (reviewed under
  FR-003).
- **FR-012**: Nothing but this spec claim lands on main until the rollout is done; the GM reviewed the pilots in the clone (the
  pilot phase closed 2026-10-05, FR-010).
- **FR-014**: A modal MUST carry a "Depiction" tab (the GM's name, 2026-10-04) saying how the map draws the thing: each map
  drawing convention the glyph uses (a size or color changed so it reads) with what the real thing was like; each way the glyph
  is standardized where the reality varied, with why; and links to the "how our maps draw it" pages the modal rests on. Where
  there is nothing notable to explain, the tab is those links alone; where there are no such pages and nothing to explain, the
  tab is absent. A standardization is written there only where it is a recorded convention; where the research records a
  variety the engine does not draw (a knob the code does not roll), the tab MUST NOT present the single form as deliberate, and
  the gap stays a finding in the claims report (the GM, 2026-10-04, of the farmhouse's single roof: *"NOT a deliberate
  convention ... as long as it ends up on that list for later"*). The guidelines MUST say how the tab is written, and a defined
  check (`modal-depiction`, under FR-008's terms - a pinned tier, a bundle, owed by a changed modal or drawing page and enforced
  at the push) MUST judge whether the tab explains and caveats the rendering as drawn: every convention and standardization the
  glyph uses is told with its real counterpart, nothing is claimed that is not drawn, and its links are exactly the drawing
  pages the modal rests on.
- **FR-015**: An item of a hamlet modal - a guess bullet, or a paragraph of About or Depiction - MAY carry a condition on the
  settlement's knobs (the GM, 2026-10-05: *"make that kind of item still automatic but dependent on the "knobs" for a settlement
  in cases where that is relevant"*), and the page MUST show it only on a map whose recorded knob value meets the condition;
  every other item is the same on every map. A condition names a registered knob and values that knob can take, and a modal
  naming any other is refused when it is read; the checks MUST read each conditional item with its condition. The References
  tab MUST follow what is shown: a question resting only on a hidden item is not listed on that map (FR-006; the GM: *"simply
  not link to things which are not covered"*).
- **FR-016**: The rollout MUST NOT change what any map draws (the GM's go-ahead, 2026-10-05). Where a modal's research shows the
  map drawing something the record contradicts and `make claims-report` does not already show it, the rollout MUST make the
  report show it - the engine's `Research:` claim for that decision cites the research that contradicts it, and `impl-drift`
  records the verdict - so the future feature that fixes every discrepancy finds it. A ruling only the GM can give - one the
  record and the project's guidelines cannot settle - MUST NOT stop the rollout. A point the record is silent on is NOT a
  ruling: the guidelines settle it (a labeled guess, or "not recorded", FR-002 and M8/M11). A ruling is a decision the
  guidelines leave to the GM - whether a single drawn form is a deliberate convention (the 2026-10-04 single-roof call is the
  example), a contradiction between the GM's canon and the record, a choice of what the setting is; the modal states what is
  known, and the question is tracked in a separate feature filed for the GM's rulings, added to it as found, without a spec
  review per addition. No pilot or example sign-off is owed before a kind is rolled out. A contradiction on a HAND-AUTHORED
  sheet (the magistracy plans have no engine decision) goes on the claim of the Mode A procedure that governs that part of the
  plan (`buildings.md`, `buildings/`), or, where none governs it, on a claim added to the procedure section the sheet's kind
  falls under, so `impl-drift` records it. Recording these drifts makes their claims DRIFTED at the push where they were
  IN-STEP at the base; the push records them with `CLAIMS_OK` and a reason citing FR-016, after every owed claim is checked.
- **FR-013**: The session MUST pitch the GM alternative names for the first tab (at least three candidates, Overview among
  them, a line on each) no later than the hand-off of the farmhouse pilot; the GM's choice is applied to the guidelines and
  the pilot before the rollout starts. (Done 2026-10-03: the GM chose "About".)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-003): the two guideline documents exist, and each rule in them is held by a named check (FR-008).
- **SC-002** (FR-002, FR-005): no modal of a feature whose existence is read opens with a guess label; the garden's guesses are on its
  guesses tab; a test holds that a guesses tab appears exactly when a modal carries a guess.
- **SC-003** (FR-006, FR-008): every rewritten modal has passed the three checks, recorded in the review ledger with cost.
- **SC-004** (FR-004, FR-009): every pool hamlet's title card lists its choices; each value opens its modal; no hamlet feature modal
  differs between two pool maps except by items conditioned on a knob whose values the two maps do not share (FR-015).
- **SC-005** (FR-010, FR-012): the GM's verdict on each pilot round is recorded in `tasks.md`; the rollout starts on the GM's go-ahead
  (given 2026-10-05, T12).
- **SC-006** (FR-007, FR-011): every class, knob value and sheet kind is rewritten and checked; `make page-check` is green,
  its browser test holding the sibling links on the About tab and the glossary tooltips on every tab.
- **SC-008** (FR-014): every rewritten modal whose kind has a drawing page or a convention carries a Depiction tab that has
  passed `modal-depiction`, recorded in the review ledger with cost; no References tab lists a "how our maps draw it" page.
- **SC-009** (FR-015): the windbreak's shared-wood guess - the GM's own case - is on a nucleated map's windbreak modal and
  absent from a dispersed map's, and so is the question that guess alone rests on on the References tab (page tests on two
  synthetic maps); a condition naming an unknown knob or value fails when the modal is read.
- **SC-010** (FR-016): the pool's renders are unchanged by the rollout in everything but the page's modal text; every
  research-versus-map contradiction a modal check found is a DRIFTED or NEEDS-RESEARCH row of `make claims-report`; every
  ruling the rollout could not settle is a numbered entry of the rulings feature, each saying what the record and guidelines
  say and why neither they nor a labeled guess can settle it.
- **SC-007** (FR-012, FR-013): nothing but the spec claim is on main until the rollout's last task; the GM's choice of the
  first tab's name is recorded in the spec's Decisions table before the rollout starts.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| A guess is a property of a statement, listed on a guesses tab; the feature-level guess lead goes | presentation (the four classes of constitution XII are kept, per statement) | the GM: the garden's lead *"is extremely misleading"* | this spec; the guidelines; `interactive/CLAUDE.md` |
| Per-settlement facts move from the feature modals to the title card, apart from FR-015's knob-conditioned items | presentation | the GM: settlement maps *"all pull from a standardized set of modals ... not ... customized modals. For anything"* | this spec; the guidelines |
| A drawing convention is told on the Depiction tab with its real counterpart, not in the write-up and not on the guesses tab | presentation | a convention is not a guess; the GM, 2026-10-04: *"I think I want 'How we draw it' things on its own tab"* (until 2026-10-04 it was told in the write-up's appearance part) | this spec; the guidelines |
| The how-it-is-drawn tab is "Depiction" | presentation | the GM, 2026-10-04: *"For the name I do like 'Depiction' so let's use that"* | this spec; the guidelines |
| The farmhouse's single roof is not presented as a convention | presentation; the drift itself stays in the claims report (DRIFTED, `houses.py` `HousesMixin.house`) | the GM, 2026-10-04: *"The single roof is NOT a deliberate convention"*, to be fixed with the other recorded drifts later | this spec; the claims report |
| The first tab is "About" | presentation | pitched About / Overview / At a glance / What it was; the GM, 2026-10-03: *"I like 'About' better than overview. So about guesses and references does seem pretty good"* | this spec; the guidelines |
| An item of a modal may depend on the settlement's knobs, shown only where the map's knob value meets it | presentation | the GM, 2026-10-05: *"still automatic but dependent on the \"knobs\" for a settlement in cases where that is relevant"* | this spec; the guidelines (M9, M22) |

## Assumptions

- No map drawing changes; only what the pages say and how the modal is laid out.
- Where the record does not answer a standard question, the research pass (constitution XII) runs before the answer is
  listed as a guess; what it finds is recorded and cited in the record as usual, and only a question still unanswered becomes a
  guess and an `open-questions` entry.
- The country estate sheets do not exist yet; FR-003's guidelines cover them when they are drawn.

## Review history

- Round 1 (spec-fidelity, 2026-10-03): REVISE - the tab-name pitch required (FR-013); a further pilot when the garden needs
  changes (FR-010, US6, SC-005); per-sheet facts on general kinds held to the particular guidelines (Context, FR-003, US5,
  FR-011); the research pass before a guess (Assumptions). All four applied.
- Round 2 (spec-fidelity, 2026-10-03): ACCEPT (FAITHFUL) - all four round-1 changes confirmed against the diff.
- Amendment 2026-10-04 (the GM's Depiction tab): FR-005, FR-006 amended, FR-014, US3b, SC-008 and two Decisions added; one Decisions row amended (the convention's place).
- Amendment 2026-10-05 (the GM's knob-dependent items): FR-015, SC-009 and one Decisions row added.
- Amendment 2026-10-05, round 1 (spec-fidelity, 2026-10-05): CHANGES REQUIRED - FR-015 is faithful to the GM's ask and does not conflict with "standardized ... not ... customized" (a conditioned item is still one standard text, chosen automatically), but FR-004, SC-004, US4 (its Why and scenario 3) and the per-settlement Decisions row still say no hamlet feature modal varies by map, which SC-009 now requires; References must follow the items shown (FR-006); the windbreak's shared-wood guess, the GM's case, is named only in the plan.
- Amendment 2026-10-05, round 2 (spec-fidelity, 2026-10-05): ACCEPT (FAITHFUL) - all three round-1 changes confirmed against the diff (FR-004, SC-004, US4 Why and scenario 3, the per-settlement Decisions row allow FR-015's items; FR-015 makes References follow what is shown, SC-009 tests it; SC-009 names the windbreak's shared-wood guess).
- Amendment 2026-10-05b (the GM's go-ahead): FR-016 and SC-010 added; T12 met by the go-ahead.
- Amendment 2026-10-05b, round 1 (spec-fidelity, 2026-10-05): CHANGES REQUIRED - FR-016 and SC-010 carry the go-ahead's clauses (no change to what maps draw, contradictions to the claims report, GM-only rulings to a separate feature without a review per entry, no example sign-offs), but FR-010, US6 (Independent Test, scenarios 1-3), SC-005, FR-012, the tasks header and the edge case on a new guideline set still prescribe pilots, verdicts and a further pilot, contradicting FR-016's last sentence; FR-016's parenthetical makes a silent record enough for a GM ruling, though the guidelines settle a silence as a labeled guess; FR-016's route reaches only engine claims, not the hand-authored magistracy and shrine sheets T16 rolls out; T23's push from this clone, and the push of FR-016's newly DRIFTED claims, are refused by sync-with-main's open-task rule and claims-gate's introduced-finding rule, and the spec names no route.
