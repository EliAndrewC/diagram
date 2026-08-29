# Feature Specification: the kosatsuba's placement is a knob, not one objective

**Feature Branch**: none (this project uses `SPECIFY_FEATURE`; CLAUDE.md, GM 2026-07-27)

**Created**: 2026-08-29

**Status**: Draft

**Input**: The GM, 2026-08-29 - *"you should go ahead and implement the notice board task yourself"*,
after pushing back on my claim that it needed research first: *"I thought that our notice board
already was well researched? I would be really surprised if you actually need another research pass
for it."* Their words in full, with the research they were pointing at, are in `gm-request.md`.

## Why this exists

`place_kosatsuba` sites the board by ONE objective - the busiest node among the ways that are not
flagged `web`. The research it is meant to implement names FIVE attested placements, and the busiest
node is only one of them. Two consequences, both measured on shipped maps:

1. **Variance is thrown away.** Principle XII: where the record supports more than one form, the rule
   is a knob rolled from the map's own seed, never a session picking the reading it prefers. Five
   attested placements is five ways two hamlets can honestly differ, and today every hamlet gets the
   same answer to a question the record answers five ways.
2. **A single objective picks seats the record does not attest.** Sawada's board stands 9.0 ft off an
   **81.7 ft dead-end spur** whose far end is 70 ft from any other way: **7 of 19** dwellings within
   250 ft where the busiest point on the web has **13**. A cul-de-sac head is not a center, an
   entrance, a bridgehead, a shrine precinct or an official's frontage. It is outside what the record
   attests - not at one end of a supported range.

The research is already done, READ and cited (feature 133 T13, four sources). **This feature adds no
research.** It implements what is on file.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Two hamlets put their board in different places, for reasons the record attests (Priority: P1)

A reader opening two hamlet maps finds the board in materially different positions - one on the
frontage where the village gathers, another at the approach where the track enters - and the
interactive map can tell them which attested placement each is and why.

**Why this priority**: it is the whole point. Maps exist for players who must tell one settlement
from another at a glance, and this is a place the record permits difference.

**Independent Test**: roll one map per knob VALUE (the feature owes one map per value, not a cohort -
CLAUDE.md) and confirm the board's seat differs between them by more than its own glyph.

**Acceptance Scenarios**:

1. **Given** two hamlets whose seeds select different placements, **When** each is rolled, **Then**
   their boards sit at positions answering to different anchors, and each map records which.
2. **Given** one hamlet rolled twice from the same seed, **When** the manifests are compared,
   **Then** the placement and the seat are identical - the knob is seeded, not random.

---

### User Story 2 - The board never stands somewhere the record does not attest (Priority: P1)

**Why this priority**: this is the defect on the sheet today. It is independently valuable even if
only one placement is ever selected.

**Independent Test**: on Sawada, confirm the board no longer sits at the head of a dead-end spur.

**Acceptance Scenarios**:

1. **Given** a settlement with a short dead-end spur off its network, **When** the board is sited,
   **Then** the spur head is not chosen while any seat answering the selected placement exists.
2. **Given** any settlement, **When** the board is sited, **Then** it still stands ON a way at the
   recorded verge distance - every attested site is a verge, a gate front or a bridge foot.

---

### User Story 3 - A map is only offered placements it actually affords (Priority: P2)

**Why this priority**: rolling `bridgehead` on a hamlet with no crossing would either fail to site
the board or site it somewhere arbitrary, which is worse than not offering it.

**Independent Test**: build settlements missing a bridge, a shrine and a distinguishable headman's
house, and confirm the selection never returns those placements.

**Acceptance Scenarios**:

1. **Given** a settlement with no crossing recorded, **When** the placement is rolled, **Then**
   `bridgehead` is not selected.
2. **Given** a settlement affording no placement but the centre, **When** the placement is rolled,
   **Then** the centre is selected and the board is still sited.

## Requirements *(mandatory)*

- **FR-001**: The settlement MUST select its kosatsuba placement from the placements ATTESTED in
  `research/urban-features.md`: the settlement centre or assembly place, the entrance/approach, a
  bridgehead, the shrine precinct, and the frontage of the village official's house.
- **FR-002**: The placement MUST be rolled from the map's own seed, deterministically, so the same
  seed yields the same placement, and MUST NOT perturb any other rolled value on the map.
- **FR-003**: A placement the map does not afford MUST NOT be selected. Affordance is read from the
  manifest the validator reads (the same-source doctrine), never assumed.
- **FR-004**: Every placement MUST keep the board ON a way at the recorded verge distance
  (`KOSATSUBA_VERGE_FT`), preserving `kosatsuba_by_the_road` and the caption machinery unchanged.
  The placement chooses WHICH way and WHERE along it; it never moves the board off the verge.
- **FR-005**: The selected placement MUST be recorded in the manifest so the interactive map, the
  checks and a later reader can all name it, and MUST be classed accurate / deviation / guess with
  its sources, per constitution XII.
- **FR-006**: A dead-end spur MUST NOT be preferred over a seat answering the selected placement.
- **FR-007**: The feature MUST NOT run a new research pass and MUST NOT add a source. It implements
  `research/urban-features.md` as it stands. Any finding that the record is insufficient is escalated
  to the GM rather than resolved by searching.
- **FR-008**: `sawada.notes.md`'s OPEN entry MUST be closed with the measured outcome, and the
  research doc's placement bullet MUST gain the pointer to the knob that implements it.

### Key Entities

- **Placement**: one attested kind of site, with an ANCHOR derived from the manifest (a point or set
  of points) and an affordance test.
- **Anchor**: what the placement is measured to - the dwelling centroid, the connector's mouth, a
  crossing, a shrine, the official's house.

## Success Criteria *(mandatory)*

- **SC-001**: On Sawada, the board's dwellings-within-250-ft count rises from 7 of 19, OR the board
  stands at a seat answering a named attested placement other than the centre; the spur head is not
  the seat either way.
- **SC-002**: Rolling one map per knob value produces at least two materially different board seats
  (further apart than the board's own drawn width).
- **SC-003**: Every live pool map still passes `kosatsuba_by_the_road` and `kosatsuba_on_a_main_way`,
  and the gate is green.
- **SC-004**: Re-rolling any map from its seed reproduces its placement and seat exactly.
- **SC-005**: No source is added to `research/SOURCES.md` by this feature.

## Assumptions

- The board remains auto-sited at the hamlet and village tiers only; town and city maps keep their
  hand placement, which this feature does not touch.
- "The village official's house" is approximated by the settlement's largest dwelling where the
  manifest records no explicit headman. That approximation is a GUESS in the constitution-XII sense
  and must be labeled one, not presented as a finding.
- Where a selected placement affords no seat that fits, the siter falls back rather than returning
  None - a board that is placed and reported is better than a map with no board at all, which is the
  ruling `place_kosatsuba` already follows.
