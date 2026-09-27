# Feature Specification: The compound research owed

**Feature Branch**: `267-compound-research-owed` (no branch - `main`, per CLAUDE.md)

**Created**: 2026-09-27

**Status**: Draft

**Input**: the GM's request, verbatim in [`request.md`](request.md): *"take on whatever future work research we've
been putting off"*, by the research procedures that landed on main (feature 250), reloaded rather than remembered.

## What is owed

Two future-work files hold what the GM put off on 2026-09-26: `future-work/farming-communities.md`'s in-field grave
island, and `future-work/compounds.md` "Research owed" - every research question features 262 and 264 recorded instead
of researching: kinds shown accurate with no section behind them, kinds labeled guess
because the record is silent, parts the research does not reach, sections resting on a source no reader can open,
contradictions between the record and the sheets or within the record, and the questions the building reviews raised.
[`inventory.md`](inventory.md) numbers every item (R01-R53), groups them into research sessions by the record page
they belong on, and separates the three that are canon or rulings for the GM, not research.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A modal that said "the record has no entry" now has one, or says what was searched (Priority: P1)

The GM clicks the garden pond on Ochiba's page. Before, it led "This is a guess - the research record has no entry
on a pond in a residence garden". After, "See references" lists the question the record now asks about a
residence garden's pond, and the modal says what that research found - accurate, a guess with the search behind it,
or a knob if the record shows more than one form.

**Independent Test**: every inventory item names its outcome in [`outcomes.md`](outcomes.md); every kind whose
item was researched has an `Entry:` that resolves, or a guess note that says what was searched and when.

**Acceptance Scenarios**:

1. **Given** an item the research answers decisively, **When** the feature lands, **Then** the record carries the
   question with cited findings, the kind's label and prose follow it, and where the answer contradicts a sheet,
   the sheet is redrawn to it (or the difference is recorded as a deliberate deviation with the GM's ruling).
2. **Given** an item the research shows done more than one way, **When** the feature lands, **Then** it is a KNOB:
   the record names the forms, and the maps take them - differently where the pool's sheets can honestly differ.
3. **Given** an item the record is silent on after a search, **When** the feature lands, **Then** the label stays a
   guess, and its note and the record say what was searched and when (an ABSENCE note).
4. **Given** an item where the record contradicts itself, **When** the feature lands, **Then** the contradiction is
   resolved in the record by the research, or - only if the research cannot - put to the GM saying what was searched.

### User Story 2 - The research follows the procedure that landed (Priority: P1)

Each group of questions is worked in fresh sessions from written briefs (`make page-session`): a write session that
searches canon in one call, saves the pages, reads them through `source-reader`, and writes the questions; then
check-and-apply sessions whose `quote-check`, `record-format`, `source-applicability` and `entry-drift` agents read
bundles (`make check-bundle`) and whose findings are applied with `make apply-edits`.

## Edge Cases

- **Feature 265 is open on the same pages.** Its sections, derived by its own method (`brief.py` `item_questions` and
  `fr006_questions` over each of its six pages, 2026-09-27): buildings 010, 070, 150, 170, 210; cities/river-cities
  010-040; urban-features 010, 020, 030, 050, 060, 070, 080, 160; ways 020; towns 040, 080, 090, 100, 130;
  cities/capitals 040. This feature's research writes its findings in its own questions; an edit a finding OWES one of
  those sections (R27 in buildings 070, R42 in river-cities 040, R46 in ways 020) waits until 265's task for that page is
  ticked and is then MADE here, as its own task - a link alone does not resolve a contradiction.
- An item that is a question of the SETTING (canon) is for the GM, not research (inventory, "For the GM").
- A finding that changes what a sheet draws is a drawing change: the sheet is redrawn, measured (picture and pack
  audit) and reviewed (`building-review`), as any sheet edit.
- A question that grows past the 20,000-byte cap is split along its topics.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every research item of the inventory MUST be researched and end in one of four outcomes: ACCURATE
  (cited), KNOB (two or more attested forms, each cited), SILENT (an absence note with the search), or
  CONTRADICTION-RESOLVED (the record corrected, cited). A contradiction the research cannot resolve is put to the GM.
- **FR-002**: The finding MUST live in the research record as a question a reader would ask (a new fragment, or a
  change to an existing one outside 265's sections), cited by the feature 194/195 rules.
- **FR-003**: Each kind written from an item MUST follow it: its `Entry:` names the new question, its label and
  prose carry the outcome, and an `entry-drift` check reads it against its section.
- **FR-004**: Where an outcome contradicts what a sheet draws, the sheet MUST be redrawn to the finding (or the
  departure recorded as a deviation by the GM's ruling); where it is a knob, the pool's sheets MUST take its forms
  where they can honestly differ, and each sheet's notes record which form it takes.
- **FR-005**: The work MUST follow the procedure that landed on main: page sessions from briefs, checks on bundles,
  reports applied with `make apply-edits`, the canon searched with `make canon`, the size cap held.
- **FR-006**: No section on feature 265's derived list (Edge Cases) MAY be edited while 265's task for its page is open;
  every edit a finding owes such a section MUST be made once that task is ticked, in this feature.
- **FR-009**: Before any research starts, the session MUST re-read from main every file that states the research
  procedure, found by search, and record the list and the main commit ([`reload.md`](reload.md)); the briefs MUST be
  written from that reading.
- **FR-007**: `future-work/compounds.md` "Research owed" MUST end holding only what is still owed, each with why.
- **FR-008**: The items that are the GM's to rule (inventory, "For the GM") MUST be put to the GM, through
  `escalation-check`, saying what the record holds.

### Key Entities

- **Item**: one owed question, R01-R53, with the kinds and sheets it bears on.
- **Outcome**: ACCURATE / KNOB / SILENT / CONTRADICTION-RESOLVED, per item, in `outcomes.md`.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002, FR-007): `outcomes.md` gives every item R01-R53 an outcome and the question(s) it
  landed in; `future-work/compounds.md` "Research owed" lists only what remains, each with why.
- **SC-002** (FR-003): every kind an item bears on names a resolving `Entry:` or a dated absence; `entry-drift` IN-STEP
  on each changed kind.
- **SC-003** (FR-004): every sheet a finding changed is redrawn, its pack audit OK and `building-review` run; every
  knob recorded in each sheet's notes.
- **SC-004** (FR-005): each changed question passes `quote-check`, `record-format` and (for each new key)
  `source-applicability` on its bundle; `make done` green.
- **SC-005** (FR-006): no commit of this feature touches a section on 265's derived list before 265's task for that
  page is ticked (git log against 265's tasks.md); every owed edit to such a section is made and checked.
- **SC-007** (FR-009): `reload.md` names the files and the main commit, and every brief's procedure matches it.
- **SC-006** (FR-008): the GM items reach the GM through `escalation-check`.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Each item's label | as its research outcome | FR-001 | the record; the kind's docstring; `outcomes.md` |
| Two attested forms become a knob | knob | constitution XII | the record; each sheet's notes |
| A silent item stays a guess with its search | guess | constitution XII | the absence note; the kind's note |

## Review history

- Round 1 (2026-09-27, `spec-fidelity`, Opus): CHANGES REQUIRED, four items, all applied: the in-field grave island
  added (R52, held under the same 2026-09-26 hold); the history half of Ubame's collateral-line alcove made research
  (R53); FR-006 rederived by 265's own method on all six of its pages, with every owed edit made later (T17) rather than
  replaced by a link; the reload the GM asked for made a requirement (FR-009, `reload.md`). It ruled FR-004 (redrawing
  sheets to findings, knobs) within the request.
- Round 2 (`spec-fidelity-verify`): CHANGES REQUIRED, three items, applied: plan D4 and R27 still carried the old
  rule; `reload.md` omitted 250's plan and two docs its search finds (reading them corrected the briefs' route to a
  registered source, D19 `WHOLE=1`); T01 named R53.
- Round 3 (`spec-fidelity-verify`): FAITHFUL.
