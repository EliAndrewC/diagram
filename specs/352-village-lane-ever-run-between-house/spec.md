# Feature Specification: Did a village lane ever run between a house and its own grove?

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-08 (filed); specified 2026-10-11
**Status**: In progress - specified

**Affects**: hamlet, research record

**Input**: the GM's request, verbatim in `request.md`: the filed entry (feature 287's woods review, 2026-09-29), the GM's
scoping of 2026-10-10 (*"just do the research and update the implementation's tagging so that it shows up on the claims
report as either something with evidence or which is not implemented in accordance with our research"*) and the go-ahead of
2026-10-11.

## Why

A reviewer of feature 287's woods found dooryard-copse crowns whose nearest farmhouse stood across a lane. The maps settle
it by construction: feature 287 reserves each household's copse seats and keeps every later lane off them (woods W25,
`overlap/reserved.py`, `Reservations.conflicts`), so a lane never runs through a household's own wood share. But no research
page says whether a real village lane ever ran between a farmhouse and its own grove. The question is neither answered nor
recorded as a guess or an absence, so `make open-questions` cannot list it and the code's claim rests on a drawing page
(0071's) that does not ask it.

## User Scenarios & Testing

### User Story 1 - The record answers the question (Priority: P1)

A reader of question 0036 (groves around farmhouses) who wonders whether a lane could pass between a house and its grove
finds the answer: what the sources show, or a stated absence naming what was searched.

**Acceptance Scenarios**:

1. **Given** 0036's findings page, **When** a reader looks for whether a lane ran between a farmhouse and its own grove,
   **Then** the page states it with a footnoted source, or states that no source read says, with an absence note naming
   the search.

### User Story 2 - The claims report shows where the code stands (Priority: P1)

The GM opens `make claims-report` and sees the code that keeps lanes off a household's wood share judged against that
finding: IN-STEP with its evidence, or DRIFTED from it.

**Acceptance Scenarios**:

1. **Given** the reservation's code, **When** `make claims-report` runs, **Then** a `Research:` claim of that code cites
   0036's findings page and carries an `impl-drift` verdict.

### Edge Cases

- The sources show both forms (a lane between a house and its grove in some villages, not in others): the record says so,
  and the claim is judged against it; per the project's knob doctrine that is a DRIFTED verdict on code that draws one form
  only, recorded, not fixed.
- The record is silent: the absence note is the finding, and the claim cites it as the code's guess.

## Requirements

### Functional Requirements

- **FR-001 - The research pass.** The archive first (`make archive-find`), then the web, for whether a village lane or path
  ran between a farmhouse and its own homestead grove (yashikirin, a dooryard grove or copse), in Japan and in the setting's
  first reference, China.
- **FR-002 - The finding recorded on 0036.** `research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html`
  gains the answer under a heading a reader would ask, each assertion footnoted to a passage quoted verbatim from a page the
  reader can open, or, where nothing is found, an absence note naming the searches. The record's checks owed by the change
  are answered (`make record-owed`).
- **FR-003 - The claim.** The code that decides the question - `Reservations.conflicts` in `l7r/diagram/overlap/reserved.py`,
  whose wood-seat rule keeps a lane off a household's reserved copse seats - carries a `Research:` claim citing 0036's
  findings page, and `impl-drift` judges it, so `make claims-report` lists it IN-STEP or DRIFTED.
- **FR-004 - No map change.** No generator, placer or map changes; a DRIFTED verdict is recorded, not fixed (the GM's scope).
- **FR-005 - The implementation check.** `make impl-check F=352` reports nothing missing.

## Success Criteria

- **SC-001** (FR-001, FR-002): 0036's findings page answers the question or states its absence with the search named, and
  `make record-owed UNANSWERED=1` lists nothing.
- **SC-002** (FR-003, FR-005): `make claims-report` lists the reservation's claim citing 0036 with a verdict, and
  `make impl-check F=352` reports nothing missing.
- **SC-003** (FR-004): the delta changes no engine line beyond a docstring's claim, and no map.

## Assumptions

- 0036 is the question the filed entry names; the copse's own drawing question (0071) keeps its claim.
- The research may find nothing; an absence is a finding.

## Decisions Recorded

(none yet)
