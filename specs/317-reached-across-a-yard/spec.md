# Feature Specification: Reached across a yard

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=317-reached-across-a-yard`)

**Created**: 2026-10-02

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: is it research, or an imposed requirement, that a lane reached every house
in a clustered village - *"if that is what the research bears out, then we should go with it"* - and *"I do want all known bugs to
be fixed."*

## Context (observed 2026-10-02, method: the session's research pass, `request.md`; feature 314 research R12, R15)

The engine seats a nucleated household only where a corridor from its door reaches the access tree as a lane the lane law admits
(features 287, 308), and its research entry says why: *"In the villages we have read about, yes, though no page we read states it
as a rule"* (`research/questions/0081-village-lanes.html`), on one twentieth-century northern village. The research pass found no
source stating it as a rule, and found customary rights of passage over a neighbor's land for landlocked plots in five provinces
(Wigmore 1892, Part V). The corridor search and the lane law over the tree are about 45% of the homesteads stage at 15 households
(feature 314 R15). Separately, feature 314 R12 found the seating admitting a corridor the web then cannot draw.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The record says what the research found (Priority: P1)

The village-lanes entry answers "was every house reached by a lane?" from what the research pass read - no source states it as a
rule; customary passage over a neighbor's land is attested (cited, verbatim, translated where the source is not English) - and the
drawing page says what the maps now draw, each value in its class.

**Why this priority**: the GM's question is a research question first; the engine follows the record.

**Independent Test**: the entry and its drawing page pass the record checks the edit owes.

**Acceptance Scenarios**:

1. **Given** the entry, **When** a reader asks whether every house was reached by a lane, **Then** it says what was read and found,
   with the passages quoted and their limits (date, place, rural or not) stated.

---

### User Story 2 - A household may be reached across a neighbor's yard (Priority: P1)

In a nucleated settlement some households are reached not by a lane to their own door but across a neighbor's dooryard to the
neighbor's way, the share of them rolled per settlement (the record attests the custom, not how common it was). A household so
reached has no lane of its own; the neighbor's yard is not built over, and no house, bed, shed or fixture is crossed.

**Why this priority**: the GM's *"we should go with it"*; it relieves the costliest part of the seating (feature 314 R15).

**Independent Test**: the reference at 15 and 40 households, base and clone alternated: the homesteads stage's time, the households
seated, and the share reached across a yard against the rolled share.

**Acceptance Scenarios**:

1. **Given** a settlement whose rolled share is above zero, **When** it is rolled, **Then** some households are reached across a
   neighbor's yard, never more than the share allows, and every household still reaches the access tree, directly or through one
   neighbor.
2. **Given** a share of zero, **When** the settlement is rolled, **Then** every household is reached by its own lane, as before.

---

### User Story 3 - The known bugs fixed (Priority: P1)

The seating admits a corridor only in the form the web will draw it, so a corridor admitted at seating never breaks the lane law
once drawn (feature 314 R12); and every other known bug on main is fixed, by this session or - by agreement - by the session that
owns it (the cohort failures from features 310 and 315 are the Diagram (Inashiro) session's, agreed 2026-10-02).

**Why this priority**: the GM's *"I do want all known bugs to be fixed."*

**Independent Test**: feature 314 R12's case - the route searched off its own parts, seed 13 at 20 households - rolls without
`WebRefused`; the cohort passes every seed the base passes.

**Acceptance Scenarios**:

1. **Given** the seating, **When** it admits a corridor, **Then** the web draws it without a lane-law fault on the reference at 10,
   15, 20 and 40 households and the cohort.

### Edge Cases

- A household reached across a neighbor's yard whose neighbor is itself reached across a yard: a chain is not attested; one
  neighbor at most, unless the record finds more (Wigmore's Echigo plot C passes over B and A - a plot, not a house; the plan
  decides on the record's reading).
- The dispersed and linear forms: a dispersed farm stands in its own holding and a row farm fronts its street - neither has a
  neighbor's yard between it and a way; the change is the nucleated form's.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The village-lanes entry MUST record the research pass's findings with citations (verbatim passages, translations
  marked), including their limits, and the drawing page MUST state the maps' rule for reaching a house, each value in its class.
- **FR-002**: A nucleated settlement MUST be able to seat a household reached across one neighbor's dooryard to that neighbor's
  way, never across a house, a garden bed, a shed or a fixture; the share of such households rolled per settlement within a band
  the record supports or labels as a guess.
- **FR-003**: Every household MUST still reach the access tree - by its own lane, or across one neighbor's yard to the neighbor's
  way.
- **FR-004**: The seating MUST admit a corridor only as the web will draw it, so no admitted corridor breaks the lane law once
  drawn (feature 314 R12).
- **FR-005**: No pool map or cohort seed may fail a rule it passed before or seat fewer households; maps may move within the
  rules (GM 2026-09-30, feature 297).
- **FR-006**: The homesteads stage MUST be timed against the base, alternated per seed, at 15 and 40 households, and recorded.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001): the entry and its drawing page pass the record checks their edit owes.
- **SC-002** (FR-002, FR-003): on the reference at 15 households, seeds 1-16, every household is seated and reaches the tree, and
  the share reached across a yard stays within each settlement's rolled share.
- **SC-003** (FR-004): feature 314 R12's case rolls without `WebRefused`, and no corridor the seating admitted is cut by the web's
  last resort on the reference legs or the cohort.
- **SC-004** (FR-005): the cohort passes every seed the base passes; the pool passes its rules.
- **SC-005** (FR-006): the homesteads stage at 15 and 40 households, base against clone, recorded in research.md.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Some households reached across a neighbor's dooryard | historically accurate (customary passage over a neighbor's land, Wigmore 1892) | the GM: go with what the research bears out | research 0081; this spec; the seating's comment |
| The share of such households, rolled per settlement | guess, labeled (the record attests the custom, not its frequency) | calibrated liberty along a degree (constitution XII) | the plan; the constant's comment |

## Assumptions

- Feature 314's harnesses (`refusals.py`, `abab.sh`) are the measure; the Diagram (Inashiro) session owns the cohort failures
  from features 310 and 315 (agreed by message, 2026-10-02).
