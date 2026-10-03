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
source stating it as a rule, and found customary rights of passage over a neighbor's land for land with no road access in seven
provinces, three of them towns (Idzumi, Uzen, Kaga), four unmarked (Echigo, Idzumo, Suwo, Chikugo), and passage to a well in three
more (Kai, Rikuzen, Bizen) (Wigmore 1892, Part V Section 8); the one entry naming a house is a town's (Kaga), and Echigo's runs as
a chain (C passes over both B's plot and A's). The corridor search and the lane law over the tree are about 45% of the homesteads stage at 15 households
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

In a nucleated settlement some households are reached not by a lane to their own door but across a neighbor's dooryard - or a
chain of them, as far as the record's reading allows - to a way, the share of them rolled per settlement (the record attests the
custom, not how common it was). A household so
reached has no lane of its own; the neighbor's yard is not built over, and no house, bed, shed or fixture is crossed.

**Why this priority**: the GM's *"we should go with it"*; it relieves the costliest part of the seating (feature 314 R15).

**Independent Test**: the reference at 15 and 40 households, base and clone alternated: the homesteads stage's time, the households
seated, and the share reached across a yard against the rolled share.

**Acceptance Scenarios**:

1. **Given** a settlement whose rolled share is above zero, **When** it is rolled, **Then** some households are reached across a
   neighbor's yard, never more than the share allows, and every household still reaches the access tree, directly or across the
   neighbors' yards the plan allows.
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

- A household reached across a neighbor's yard whose neighbor is itself reached across a yard: Wigmore's Echigo entry is such a
  chain (C over both B's plot and A's), so a chain is allowed; any limit on its length is the plan's, a labeled GUESS citing it.
- The dispersed and linear forms: a dispersed farm stands in its own holding and a row farm fronts its street - neither has a
  neighbor's yard between it and a way; the change is the nucleated form's.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The village-lanes entry MUST record the research pass's findings with citations (verbatim passages, translations
  marked), including their limits, and the drawing page MUST state the maps' rule for reaching a house, each value in its class.
- **FR-002**: A nucleated settlement MUST be able to seat a household reached across a neighbor's dooryard, or a chain of them as
  far as the record's reading allows, to a way - never across a house, a garden bed, a shed or a fixture; the share of such
  households rolled per settlement within a band the record supports or labels as a guess. Any limit on a chain's length is a
  Decision Recorded, labeled. A household has no way of its own where no straight path, nor one round its house, reaches a way;
  no path bending round the homesteads is searched for (amended 2026-10-03, the GM's ruling in `request.md`: cutting through a
  neighbor's yard "is not some kind of huge deal").
- **FR-003**: Every household MUST still reach the access tree - by its own lane, or across the neighbors' yards FR-002 allows.
- **FR-004**: The seating MUST admit a corridor only as the web will draw it, so no admitted corridor breaks the lane law once
  drawn (feature 314 R12).
- **FR-005**: No pool map or cohort seed may fail a rule it passed before or seat fewer households; maps may move within the
  rules (GM 2026-09-30, feature 297).
- **FR-006**: The homesteads stage MUST be timed against the base, alternated per seed, at 15 and 40 households, and recorded.
- **FR-007**: Every known bug on main MUST be listed with its owner and fixed - by this feature, or by the session that owns it by
  agreement. As measured on 2026-10-02 (feature 314 R12, R15; `make cohort N=24` on origin/main): the seating admitting a corridor
  the web cannot draw (this feature, FR-004); cohort seeds 14, 15 and 906 (dispersed: `trees_shading_plots`,
  `gardens_east_shaded`) and seeds 22 and 23 (linear: `WebRefused`) - the Diagram (Inashiro) session, feature 315, agreed by
  message 2026-10-02. A bug found later joins the list with its owner; found 2026-10-03 (this feature): the seating reserving
  wood seats in the afternoon sun lane feature 310 holds the copse out of, so the copse never plants them.
- **FR-008**: The route search's cost the GM ruled on ("Yes, definitely do this", 2026-10-03) MUST be cut inside this feature by
  the lever the measurement supports, its maps unchanged where the lever is exact (research R10, at 40 households: of seed 47's
  509 failed corridor searches the shared reachability map would have answered none, 348 had no branch of the tree in reach;
  seed 25, the cell the GM ruled on, keeps 19 failed searches on the amended engine, none of them answerable by the map). The
  substitution - an exact no-branch-in-reach check built, the map not - MUST be put to the GM in the feature's report as an
  amendment of the 2026-10-03 ruling, with R10's measurement.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001): the entry and its drawing page pass the record checks their edit owes.
- **SC-002** (FR-002, FR-003): on the reference at 15 households, seeds 1-16, every household is seated and reaches the tree, and
  the share reached across a yard stays within each settlement's rolled share.
- **SC-003** (FR-004): feature 314 R12's case rolls without `WebRefused`, and no corridor the seating admitted is cut by the web's
  last resort on the reference legs or the cohort.
- **SC-004** (FR-005): the cohort passes every seed the base passes; the pool passes its rules.
- **SC-005** (FR-006): the homesteads stage at 15 and 40 households, base against clone, recorded in research.md.
- **SC-006** (FR-007): when this feature closes, research.md lists each known bug as fixed, with the run that shows it, or as owned
  and in progress by the agreed session, with that session's last word on it; none without an owner.
- **SC-007** (FR-008): the homesteads stage at 40 households, seeds 25 and 47, before and after `route.tree_in_reach`, recorded in
  research.md; the pool byte-identical with the check on and off.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Some households reached across a neighbor's dooryard | historically accurate: passage over a neighbor's land for land with no road access (Wigmore 1892, seven provinces, three of them towns); that it ran across a dooryard in a clustered village is this record's reading, a GUESS | the GM: go with what the research bears out | research 0081; this spec; the seating's comment |
| The share of such households, rolled per settlement | guess, labeled (the record attests the custom, not its frequency) | calibrated liberty along a degree (constitution XII) | the plan; the constant's comment |
| "No way of its own" asked of straight and round-the-house paths only, no routed search | canon: the GM's ruling, 2026-10-03 (`request.md`) | cutting through a neighbor's yard was ordinary; the routed proof was the passage's cost at 40 households | research 0081's drawing page; plan D2; `passage.landlocked` |

## Assumptions

- Feature 314's harnesses (`refusals.py`, `abab.sh`) are the measure; the Diagram (Inashiro) session owns the cohort failures
  from features 310 and 315 (agreed by message, 2026-10-02).

## Review history

- Round 1 (spec-fidelity, 2026-10-02): CHANGES REQUIRED, 3 items - "one neighbor at most" was a rule the research does not give
  (Wigmore's Echigo entry is a chain); the Decisions row called the dooryard crossing historically accurate where only passage over
  a neighbor's land is attested, and the province count was wrong; "all known bugs fixed" had no FR or SC. Addressed: a chain is
  allowed, any limit a labeled Decision; the row and the Context give seven provinces, three towns, and label the dooryard a GUESS;
  FR-007 lists each known bug with its owner and SC-006 records each at close.
- Round 2 (spec-fidelity, verify, 2026-10-02): FAITHFUL - the three items confirmed against the diff.
- Amendment (2026-10-03, the GM's ruling in `request.md`): FR-002 asks a way of its own of straight and round-the-house paths
  only, no routed search; FR-007 adds the wood seats reserved in the afternoon sun lane; FR-008 cuts the route search's cost inside
  this feature (amended on the measurement, research R10). The review counter restarts with this amendment.
- Amendment round 1 (spec-fidelity, 2026-10-03): CHANGES REQUIRED, 4 items - FR-008 rested on seed 47 alone, not the GM's seed 25;
  FR-008 did not say the GM is told; FR-008 had no success criterion; the wood-seat bug was missing from R5. Addressed: seed 25's
  count in R10 and FR-008, the report owed in FR-008, SC-007 with its measurement, R5's row.
- Amendment round 2 (spec-fidelity-verify, 2026-10-03): FAITHFUL - the four items confirmed against the diff.
- Plan, MODE 4 on the amended plan (2026-10-03): CLEAR, 30 decisions (digest 531a5cf4); D8's substitution LEGITIMATE on the GM's
  standing instruction and R10's measurement, the tight seats' cut near the tree (`TIGHT_TREE_FT`) re-measured under the new test.
