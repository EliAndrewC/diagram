# Feature Specification: Grow outward, never restart

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=318-grow-outward-no-restart`)

**Created**: 2026-10-03

**Status**: Draft (amended 2026-10-03)

**Input**: the GM's request, verbatim in `request.md`: *"we should eliminate the throwaway and then redraw logic for farmhouses
specifically"*; *"it probably makes sense to get rid of this pattern completely"*; *"we can start with a nucleation and then just
keep placing houses outside of the boundary"*; and, once the record showed the 700 ft is no researched limit: *"let's just keep
going at the edge ... if we have multiple options in our placement, and one option is closer to the fields, then we should take
the one that is closer to the fields ... but that is not any kind of a limit ... we can get rid of these 700 feet measurement
completely"*.

## Context (observed 2026-10-03, method: the session's read of the engine and the record; a read-only survey of the generator; `margin_census.py`, `margin_trace.py` and `refuse_trace.py` in the session's scratchpad)

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
starting over ... so the houses already placed stay where they are."*

Nor does the record support a distance from the field. Every seat on every form is also refused past 700 ft of its field
(`FIELD_REACH_FT`), its claim citing pages 0029 and 0032, but 0029's drawing page says *"No farmhouse is held to a maximum
distance from its fields"*, and 0032's 700 ft is the back-row distance its own drawn villages showed. Of the cohort's 30 seeds,
29 seat on their first margin; nucleated seed 18 (15 households) seats on its twelfth, because its first eleven held 7-12
homesteads within that reach: on its first margin, with the radius and the growth unbounded, the reach refused 1,996 offered
seats and the crop, water and marsh 1,065, and it seated 12.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A cluster that runs out of room grows at its edge (Priority: P1)

A clustered hamlet seats its households as tightly as the ground allows, nearest the cluster first; when the seats near it run
out, later households are seated further out - at the cluster's edge, as a late arrival in a real village set up beside the
houses already there - never by moving a house already seated, and never refused for its distance from the field. Of the seats
the cluster offers at its edge, the one nearest the field is taken first.

**Why this priority**: it is the GM's request, and the record (0004) already states it as the rule.

**Independent Test**: roll the reference spec at 40 households, seed 47, and cohort seed 18, and read the manifests: every
household seated on the chosen margin, the overflow beyond the old radius, no house seated twice.

**Acceptance Scenarios**:

1. **Given** a nucleated hamlet whose chosen margin seated every household before, **When** it is rolled, **Then** it seats
   the same households on the same margin (its houses may move only where a removed rule had refused or re-laid one).
2. **Given** a nucleated hamlet whose households overflow the old radius, **When** it is rolled, **Then** the overflow stands
   beyond that radius at the cluster's edge, and no seated house is taken back.
3. **Given** the seats a growth level offers round the standing houses, **When** the next household is seated, **Then** the
   seat nearest the field is tried first.
4. **Given** a site where no free ground on the whole map can hold every household, **When** it is rolled, **Then** the map is
   refused with the households it could seat named - not reseated elsewhere.

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
   seat - no recheck re-lays it; a passage the finished map makes unnecessary (the household now has a straight or
   round-the-gable way of its own) is ended in place, the household keeping its house where it stands.

---

### User Story 3 - The record says what the maps now do (Priority: P2)

The drawing pages say the cluster grows at its edge, nearer the field preferred but never limited by it, that the packing figure
is reported rather than enforced, and how a passage is judged on the finished map.

**Why this priority**: every rendering decision is recorded (constitution XII); the record must not describe a rule the
engine no longer keeps.

**Independent Test**: the record checks owed by the edits answer clean.

**Acceptance Scenarios**:

1. **Given** the 0032 drawing page, **When** read, **Then** its quarter-built figure is a measurement the maps report, not a
   rule they keep, and the field reach is no limit.
2. **Given** the 0081 drawing page, **When** read, **Then** it says a passage the finished map makes unnecessary (its drawn
   layout given a way of its own) is ended in place, and nothing in it says a household is re-laid with another layout.
3. **Given** the 0029 drawing page, **When** read, **Then** it says that of the seats the cluster offers at its edge the one
   nearest the field is taken first, and that no distance from the field is a limit.

### Edge Cases

- A margin with no dry way out is skipped before any house is seated - a check, not a take-back - and the next margin is tried.
- A cluster on a narrow strip of dry ground (cohort seed 18) grows along and away from the field until everyone is seated.
- No free ground is left on the whole map: the map is refused, naming the shortfall.
- A cluster grown past the old radius on a narrow strip draws a long cluster: allowed (the 12:1 refusal goes); the declared
  cluster shape records what was drawn.
- The cluster grows past the old radius and its houses thin: the quarter-built figure is reported, not enforced.
- Households reached across a yard stand at tight seats while the share has room, and are never taken back.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The seating MUST NOT take back any farmhouse it has seated - no margin ladder take-back, no rescue re-search of a
  seated margin, no re-seat with the passage withheld, no recheck re-laying a household after the seating. The check that ends
  a passage once the finished seating gives the household a way of its own (moving no house) MUST stay: it holds page 0081's
  condition, "seated only where it has no way of its own".
- **FR-002**: A nucleated cluster MUST keep growing outward from its standing houses, nearest first, while households are left
  and free ground remains; the old seat radius MUST NOT refuse a seat (it may order the offers).
- **FR-003**: No distance from the field MUST refuse a seat, on any form, and the field reach (`FIELD_REACH_FT`) MUST be removed
  (the GM: "we can get rid of these 700 feet measurement completely"). Every use MUST be deleted or re-based on something that
  is not that figure: the predicate `within_field_reach` (the growth's seat test, the nucleated placer, the dispersed form's
  exhaustive pass, the fit test) deleted; the seat window the growth's seat region is built over, the free-ground grid's box and
  the manifest's `site_boundary.window` sized from the map's own extent; the placement-stages page's legend and the tests
  pinning the figure updated. The hard limits that remain are every rule a seat asks today, with the field reach the only
  exception: dry ground, nothing on crop or water, the canvas, the reserved corridors, the standing homesteads, the household's
  water and its way to the access tree.
- **FR-003a**: Of the seats a nucleated growth level offers round its standing houses, the one nearest the field MUST be tried
  first (the GM: "if we have multiple options in our placement, and one option is closer to the fields, then we should take the
  one that is closer to the fields"); the growth still widens level by level from the cluster outward, so the cluster stays as
  tight as its ground allows.
- **FR-004**: The site (margin) choice MUST be kept; a margin that cannot start (no dry way out) MUST still be skipped before any
  house is seated on it.
- **FR-005**: Where no free ground on the map can hold every household, the map MUST be refused, naming the households seated
  and the margin, never seated on another margin after houses were placed. The other forms seat in their own passes (a
  dispersed hamlet's exhaustive pass, a row village's rows), now unbounded by the field reach, and are refused the same way where
  those run short; the premise, measured 2026-10-03 (`margin_census.py`, the cohort's specs, seeds 1-30): none of the 15
  non-nucleated cohort seeds (8 dispersed, 7 linear) nor the pool's two row villages seated past its first margin.
- **FR-006**: The cluster-shape refusal (a seating past 12:1) MUST go; the drawn shape MUST still be recorded.
- **FR-007**: Page 0032's quarter-built figure MUST be reported for each nucleated map (built share inside the houses' outline)
  and MUST NOT refuse or alter a seating.
- **FR-008**: The drawing pages MUST state what the maps now do (0004 already does; 0029, 0032 and 0081 as above), each value in
  its class, and every code claim citing the field reach as a researched maximum MUST be corrected or removed with it.
- **FR-009**: No pool map or cohort seed may fail a rule it passed before or seat fewer households; maps may move within the rules
  (GM 2026-09-30, feature 297).
- **FR-010**: The homesteads stage MUST be timed against main at 15 and 40 households, alternated per seed, and recorded; the
  larger maps' spread MUST be measured (the farthest house from the cluster's first house and from the field, and the
  quarter-built figure).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001): a test fails if the seated-house count falls during any seating; it passes on the cohort and the pool.
- **SC-002** (FR-002, FR-003): on the reference spec at 40 households, seeds 4, 25, 39 and 47, and on cohort seed 18, every
  household is seated on the chosen margin; no seat is refused for its distance from the field; no `FIELD_REACH_FT` remains in
  `settlement/rolling/fit.py` and nothing imports it; the ways law's own reach of a way to the field (`ways/law.py`'s `FIELD_REACH_FT`) is unchanged.
- **SC-002a** (FR-003a): a test fails if, of the seats one growth level offers, a seat farther from the field is tried before a
  nearer one.
- **SC-003** (FR-005): a constructed site with too little free ground is refused with the shortfall named.
- **SC-004** (FR-007, FR-008): the record checks owed by the page edits answer clean; each nucleated pool map's manifest carries
  its quarter-built figure.
- **SC-005** (FR-009): the cohort passes every seed main passes; the pool passes its rules.
- **SC-006** (FR-010): the bookends and the spread recorded in research.md; seed 47 at 40 households no longer pays a thrown-away
  seating.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| A cluster grows at its edge; no house is moved for a late one | canon: the GM's ruling of 2026-10-03 ("when someone else moved in, everyone did not move their houses"), as 0004's drawing page already states the maps' rule | the GM's request | 0004's drawing page; this spec; the seating's comment |
| No distance from the field refuses a seat; nearer the field preferred | the record holds no maximum (0029: "No farmhouse is held to a maximum distance from its fields"); the preference is canon, the GM's ruling of 2026-10-03 | the field reach was the drawn villages' back row, not a source's figure | 0029's and 0032's drawing pages |
| The quarter-built figure reported, not enforced | calibration against the drawn villages (0032 says so) | the GM chose it as soft | 0032's drawing page |
| A passage no longer re-laid after the seating; one the finished map makes unnecessary ended in place | historically accurate for the condition (0081: "seated only where it has no way of its own"); the re-lay removed as a take-back (the GM's request) | the re-lay moved a seated house | 0081's drawing page |

## Assumptions

- The seed and the rolled knobs are unchanged; maps that seated on their first margin may still move where a removed rule acted.
- The field acreage solvers and the lane settle rounds are out of scope (the solvers fit a target and never fired on the cohort;
  the settle rounds are a separate redesign the GM was told of).

## Review history
- Round 1 (spec-fidelity, 2026-10-03): CHANGES REQUIRED, 3 items - the passage recheck's in-place ending is not a take-back and
  holds 0081's condition (kept; only the re-lay goes); the other forms' behavior without the ladder unstated (FR-005: the
  measured premise, refused the same way); the growth model labeled historically accurate where it is the GM's ruling (canon).
- Round 2 (spec-fidelity-verify, 2026-10-03): FAITHFUL - the three items confirmed against the diff; aside: the 0081 sentence
  for US3 scenario 2 says the finished map's check asks the drawn layout only.
- Amendment (2026-10-03, the GM's rulings in `request.md`): the field reach removed as a limit on every form, nearness
  to the field a preference; cohort seed 18 grows on its first margin. The review counter restarts with this amendment.
- Amendment round 1 (spec-fidelity, 2026-10-03): CHANGES REQUIRED, 3 items - FR-003 left the reach's constant alive (every use
  now listed and deleted or re-based; seed 18 seats on its first margin only once the window and the grid box are re-based too,
  observed 2026-10-03, method: `bound_probe.py` in the session's scratchpad with the constant enlarged); "otherwise equal" a tie that never occurs (FR-003a: the nearest the
  field first among a growth level's seats, with SC-002a); 0029's statement unspecified (US3 scenario 3).
- Amendment round 2 (spec-fidelity-verify, 2026-10-03): CHANGES REQUIRED, 2 small items - SC-002's name check caught the ways
  law's unrelated reach of a way to the field (scoped to the seating's constant); FR-003's closed list of remaining limits left out the
  household's water and its way to the tree (every rule a seat asks today but the reach).
- Amendment round 3 (spec-fidelity-verify, 2026-10-03): FAITHFUL - both items confirmed; the amended spec accepted.
