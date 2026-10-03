# Feature Specification: Grow outward, never restart

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=318-grow-outward-no-restart`)

**Created**: 2026-10-03

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: *"we should eliminate the throwaway and then redraw logic for farmhouses
specifically"*; *"it probably makes sense to get rid of this pattern completely"*; *"we can start with a nucleation and then just
keep placing houses outside of the boundary when that happens within the seven hundred foot field reach"*; and, asked which limit
stays hard, *"700 ft hard, floor soft"*.

## Context (observed 2026-10-03, method: the session's read of the engine and the record; a read-only survey of the generator)

A clustered (nucleated) hamlet is seated on a chosen margin of its field: the cluster grows from its first house, each standing
house offering seats round it, widening through three levels while households are left. Every seat must stand within a radius
of the margin's center - 1.15 times the half-diagonal of a band sized at 162 ft square per household - and both figures are
labeled GUESS / UNRESEARCHED in the code. Where a margin cannot seat every household, or its houses draw no cluster shape's band
(a string past 12:1, UNRESEARCHED), every house it seated is taken back and the next margin is seated from scratch (the margin
ladder); a near-miss margin is first re-searched on a finer grid (the rescue); feature 317 added a re-seat of the same margin
with the passage withheld, and an early stop for a passage seating; and after seating, a household reached across a yard may be
taken back and re-laid (the passage recheck). On seed 47 at 40 households this is the whole of the remaining band-3 cost of
feature 317 (one seating of 33 houses thrown away, research R10 of feature 317), and feature 306 once measured sixteen margins
seated there before one held everyone.

The record does not support the wall. `research/questions/0032-how-our-maps-pack-a-clustered-villages-houses.drawing.html`:
*"How tightly a clustered village packs is a calibration against the drawn villages, not a historical figure: no page we read
gives a clustered village's built share of its ground, its houses to the hectare or the size of its house plots."* Its one rule,
that a clustered village of a dozen houses or more keeps at least a quarter of the ground inside its outline built, is that
calibration. And `research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.drawing.html` already
states the opposite of what the code does: *"When the placer cannot fit enough farmhouses, it searches wider ground rather than
starting over ... so the houses already placed stay where they are."* The one research-backed limit on how far a house stands is
the field reach: 700 ft from its field, held as a maximum (pages 0029 and 0032).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A cluster that runs out of room grows at its edge (Priority: P1)

A clustered hamlet seats its households as tightly as the ground allows, nearest the cluster first; when the seats near it run
out, later households are seated further out - at the cluster's edge, as a late arrival in a real village set up beside the
houses already there - never by moving a house already seated.

**Why this priority**: it is the GM's request, and the record (0004) already states it as the rule.

**Independent Test**: roll a nucleated hamlet whose households do not fit within the old radius (the reference spec at 40
households, seed 47) and read the manifest: every household seated on the chosen margin, the overflow beyond the old radius,
every house within 700 ft of its field, no house seated twice.

**Acceptance Scenarios**:

1. **Given** a nucleated hamlet whose chosen margin seated every household before, **When** it is rolled, **Then** it seats
   the same households on the same margin (its houses may move only where a removed rule had refused or re-laid one).
2. **Given** a nucleated hamlet whose households overflow the old radius, **When** it is rolled, **Then** the overflow stands
   beyond that radius at the cluster's edge, every house within 700 ft of its field, and no seated house is taken back.
3. **Given** a site where no ground within 700 ft of the field can hold every household, **When** it is rolled, **Then** the map
   is refused with the households it could seat named - not reseated elsewhere.

---

### User Story 2 - No placed farmhouse is ever taken back (Priority: P1)

No step of the seating takes back a farmhouse it has seated and seats it again - not a whole margin, not a re-search of one,
not a household re-laid after the seating.

**Why this priority**: the GM: *"it probably makes sense to get rid of this pattern completely"*.

**Independent Test**: a test proves the seating has no take-back: the seated households only ever grow in number during a
seating, on every form, across the cohort.

**Acceptance Scenarios**:

1. **Given** any form (nucleated, dispersed, linear), **When** a hamlet is seated, **Then** the count of seated houses never
   falls during the seating.
2. **Given** a household reached across a neighbor's yard at its seat, **When** the seating finishes, **Then** it keeps its
   seat and its passage (no recheck re-lays it).

---

### User Story 3 - The record says what the maps now do (Priority: P2)

The drawing pages say the cluster grows at its edge within the field reach, that the packing figure is reported rather than
enforced, and that a passage is judged at its seat only.

**Why this priority**: every rendering decision is recorded (constitution XII); the record must not describe a rule the
engine no longer keeps.

**Independent Test**: the record checks owed by the edits answer clean.

**Acceptance Scenarios**:

1. **Given** the 0032 drawing page, **When** read, **Then** its quarter-built figure is a measurement the maps report, not a
   rule they keep.
2. **Given** the 0081 drawing page, **When** read, **Then** nothing in it says a passage is asked again once all are seated.

### Edge Cases

- A margin with no dry way out is skipped before any house is seated - a check, not a take-back - and the next margin is tried.
- The overflow reaches the 700 ft field reach on every side: the map is refused, naming the shortfall.
- A cluster grown past the old radius on a narrow strip of dry ground draws a long cluster: allowed (the 12:1 refusal goes); the
  declared cluster shape records what was drawn.
- The cluster grows past the old radius and its houses thin: the quarter-built figure is reported, not enforced.
- Households reached across a yard stand at tight seats while the share has room, and are never taken back.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The seating MUST NOT take back any farmhouse it has seated - no margin ladder take-back, no rescue re-search of a
  seated margin, no re-seat with the passage withheld, no recheck re-laying a household after the seating.
- **FR-002**: A nucleated cluster MUST keep growing outward from its standing houses, nearest first, while households are left
  and seats remain within the field reach; the old seat radius MUST NOT refuse a seat (it may order the offers).
- **FR-003**: The hard limits on where a house may stand MUST be the research-backed ones and the existing per-house rules: within
  700 ft of its field (pages 0029, 0032), on dry ground, nothing on crop or water, and every rule a seat already asks.
- **FR-004**: The site (margin) choice MUST be kept; a margin that cannot start (no dry way out) MUST still be skipped before any
  house is seated on it.
- **FR-005**: Where the field reach cannot hold every household, the map MUST be refused, naming the households seated and the
  margin, never seated on another margin after houses were placed.
- **FR-006**: The cluster-shape refusal (a seating past 12:1) MUST go; the drawn shape MUST still be recorded.
- **FR-007**: Page 0032's quarter-built figure MUST be reported for each nucleated map (built share inside the houses' outline)
  and MUST NOT refuse or alter a seating.
- **FR-008**: The drawing pages MUST state what the maps now do (0004 already does; 0032 and 0081 as above), each value in its class.
- **FR-009**: No pool map or cohort seed may fail a rule it passed before or seat fewer households; maps may move within the rules
  (GM 2026-09-30, feature 297).
- **FR-010**: The homesteads stage MUST be timed against main at 15 and 40 households, alternated per seed, and recorded; the
  larger maps' spread MUST be measured (the farthest house from the cluster's first house, and the quarter-built figure).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001): a test fails if the seated-house count falls during any seating; it passes on the cohort and the pool.
- **SC-002** (FR-002, FR-003): on the reference spec at 40 households, seeds 4, 25, 39 and 47, every household is seated on the
  chosen margin and every house stands within 700 ft of its field.
- **SC-003** (FR-005): a constructed site with too little ground within the field reach is refused with the shortfall named.
- **SC-004** (FR-007, FR-008): the record checks owed by the page edits answer clean; each nucleated pool map's manifest carries
  its quarter-built figure.
- **SC-005** (FR-009): the cohort passes every seed main passes; the pool passes its rules.
- **SC-006** (FR-010): the bookends and the spread recorded in research.md; seed 47 at 40 households no longer pays a thrown-away
  seating.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| A cluster grows at its edge; no house is moved for a late one | historically accurate in the record's reading (0004's rule); the GM's understanding of how farming communities grew | the GM's request; 0004 | 0004's drawing page; this spec; the seating's comment |
| The 700 ft field reach the one hard extent | historically accurate (0029, 0032: the back-row tolerance held as a maximum) | the GM: "700 ft hard" | 0032's drawing page |
| The quarter-built figure reported, not enforced | calibration against the drawn villages (0032 says so) | the GM: "floor soft" | 0032's drawing page |
| A passage judged at its seat only | canon: the GM's ruling of 2026-10-03 (feature 317), cutting through a yard is no great matter | the recheck was a take-back | 0081's drawing page |

## Assumptions

- The seed and the rolled knobs are unchanged; maps that seated on their first margin may still move where a removed rule acted.
- The field acreage solvers and the lane settle rounds are out of scope (the solvers fit a target and never fired on the cohort;
  the settle rounds are a separate redesign the GM was told of).

## Review history
