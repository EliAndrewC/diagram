# Feature 291 - how many sides a homestead grove takes

**Feature**: 291-homestead-grove-sides | **Created**: 2026-09-29 | **Status**: Draft
**Input**: the GM's request and rulings, verbatim in [`request.md`](request.md).

## Summary

The research record says, flatly, that before 1868 a farmstead's grove went round the whole house, and that the
windward-only belt is the modern form. Its evidence does not bear that out: the full ring is reported firmly for one
region (the Izumo plain, tied to its flood banks), a 1625 domain order is ambiguous, and the same record holds the
Sendai grove on the north and west, "often lacking the south or the east side", planted that way under the first
Sendai lord and kept for centuries, the Tonami grove open on its east front, and other regions' groves on one or two
sides. No source counts farmsteads by grove shape.

This feature (1) corrects the record so each shape is cited to the region and date that attest it; (2) makes the
homestead grove's sides a per-settlement knob - two sides 50%, three sides 30%, four sides 20%, the four-sided share
rising to 40% where the farmsteads stand on flood-prone ground - with the windward side the deep one; and (3) fixes
the per-house grove placement that has kept the dispersed and linear settlement forms (the forms whose farms carry
their own grove) switched off since feature 126, and switches them back on, so the knob reaches maps.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The record says what its sources say (Priority: P1)

A reader following a grove's "See references" from a map reaches an answer that says which regions put the grove on
two sides, which on three, and which all the way round, each with its footnote, and that no source says how common
each was.

**Independent Test**: read the corrected entries; `quote-check` and `record-format` confirm them.

**Acceptance Scenarios**:

1. **Given** the homestead grove entries, **When** a reader looks for the grove's shape before 1868, **Then** they find
   the Sendai two-sided form, the Tonami front-open form and the Izumo full ring, each attributed to its region and
   footnoted, and no sentence saying all premodern groves went round the house.
2. **Given** the shelter-belt entry holding the GM's 2026-08-29 hook ruling, **When** a reader reads it, **Then** it
   says the GM's 2026-09-29 ruling reverses it for the farmstead grove, whose sides are now a rolled knob, quoting
   both rulings; and that the village belt stays on one or two windward sides on that entry's own evidence and the
   GM's 2026-09-29 approval of "the homestead grove only".

### User Story 2 - Farmstead groves take two, three or four sides (Priority: P1)

The GM opens a generated hamlet whose farms carry their own groves and sees groves on two, three or all four sides of
the house, the same shape at every farm in that hamlet, with the deep stand on the windward side.

**Independent Test**: roll many settlements and count the forms; draw one of each and look.

**Acceptance Scenarios**:

1. **Given** a settlement whose farms carry groves, **When** it is generated, **Then** every farm's grove has the one
   side count rolled for that settlement.
2. **Given** a three-sided grove, **When** drawn, **Then** the open side is the front - the lee side where the farm's
   yard and way in are.
3. **Given** a three- or four-sided grove, **When** drawn, **Then** the windward arms are the full depth and the other
   planted sides a thinner band.
4. **Given** a settlement on flood-prone ground, **When** rolled, **Then** four sides comes up at 40%.

### User Story 3 - Dispersed and linear hamlets come back (Priority: P1)

The generator rolls the dispersed and linear settlement forms again, at the weights feature 126 set, and their
per-house groves pass every check a grove answers to.

**Independent Test**: the hamlet cohort passes with the forms in the roll.

**Acceptance Scenarios**:

1. **Given** the settlement-form roll, **When** a hamlet is generated without a pinned form, **Then** it can come up
   nucleated, dispersed or linear at feature 126's weights (5 : 3 : 2).
2. **Given** a dispersed or linear hamlet, **When** generated, **Then** every farm carries its rolled grove, no grove
   lies on a lane, over a byre or other structure, or across a garden's morning sun, and every household is seated.

### Edge Cases

- A map whose windward key is a single cardinal (N, S, E, W): two sides still means two - the windward face and one
  flank.
- A nucleated hamlet: its farms still shelter behind the village belt and carry no grove of their own; the knob is
  rolled and recorded but draws nothing.
- The village-scale shelter belt is not this knob and keeps one or two windward sides.

## Requirements *(mandatory)*

### Functional Requirements

**The record**

- **FR-001**: Every entry of the research record that says the premodern farmstead grove went round the whole house, or
  that the windward-only grove is only the modern form, MUST be corrected so each shape is attributed to the region
  and date its source gives: the Izumo full ring before Meiji; the Sendai north-and-west grove, lacking the south or
  east, planted under the first Sendai lord and kept for several hundred years; the Tonami grove open on its east front
  (undated); the 1625 Takada order read as it is written (cedar around the homestead, camellia and bamboo grass on the
  south). Each assertion is footnoted; the record says no source counts farmsteads by grove shape.
- **FR-002**: The record MUST state the decision: the farmstead grove's sides are a knob rolled per settlement at 50 / 30
  / 20 (two / three / four), four sides at 40% on flood-prone ground, the weights a GUESS by the GM's ruling of
  2026-09-29, quoted; the windward arms deep and the rest thinner (Tonami's pattern, a GUESS for the full ring); the
  open side of three the front.
- **FR-003**: The shelter-belt entry holding the 2026-08-29 hook ruling MUST record the GM's 2026-09-29 ruling as
  reversing it for the farmstead grove, both quoted; the village belt stays on one or two windward sides on that
  entry's own evidence and by the GM's approval of "the homestead grove only".
- **FR-004**: Every map modal written from a changed entry MUST be checked for drift and rewritten where it drifted.

**The knob**

- **FR-005**: The homestead grove's side count MUST be a per-settlement knob, pinnable by a map, otherwise rolled from
  the map's seed: two sides 50%, three 30%, four 20%.
- **FR-006**: On flood-prone ground the four-sided share MUST be 40%, the other two keeping their 5 : 3 ratio.
  Flood-prone ground MUST be a site property a map can pin, and is otherwise set from the site: true where the fields
  are reclaimed low ground behind dikes (the polder archetypes, the grid polder and the dike-and-pond) or the houses
  stand on a dike.
- **FR-007**: Two sides MUST be the windward pair (for a diagonal windward key, its two faces; for a cardinal, that face
  and one flank). The FRONT is the lee side where the farm's yard and way in are, and a three-sided grove leaves it
  open: three sides MUST add the one remaining face that is not the front. Four sides MUST close the ring.
- **FR-008**: The windward arms MUST keep today's depth; every other planted side MUST be a thinner band.
- **FR-009**: The rolled side count MUST be recorded on the map and stated in the grove's modal.

**The placement**

- **FR-010**: Each farm MUST be seated with room for the grove its settlement rolled, and every rolled side planted,
  for every side count; and the per-house grove MUST pass every rule feature 126 measured failing: it lies on no lane
  tread (`groves_clear_of_lanes`), stands on the windward side it was rolled for (`groves_on_windward_side`), leaves
  every garden its morning sun (`gardens_unshaded_from_east`), lies on no structure and puts no crown over one,
  byres and later-seated fixtures included (`groves_clear_of_structures`, `structures_clear_of_trees`), and every
  household is seated.
- **FR-011**: The settlement-form roll MUST restore feature 126's weights (nucleated 5, dispersed 3, linear 2), and the
  hamlet cohort MUST pass with them, as the bar feature 126 set for switching them back on.
- **FR-012**: The pool hamlets MUST be regenerated from their specs as they are; a hamlet whose seed now rolls another
  form takes it.

### Key Entities

- **Grove side count**: 2, 3 or 4; one per settlement; recorded on the map.
- **Flood-prone ground**: a property of the settlement's site - pinned by the map, or set from its polder fields or
  dike-top houses (FR-006); recorded on the map.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001-FR-003): no entry of the record asserts a universal premodern full ring; the corrected entries
  pass `quote-check` and `record-format`.
- **SC-002** (FR-004): every modal the push names as owed is answered by an `entry-drift` check.
- **SC-003** (FR-005, FR-006): over 1,000 rolled seeds the counts sit within three standard errors of 50/30/20 off
  flood ground and 37.5/22.5/40 on it; and a test rolls a real polder site and finds it flood-prone, reading the
  flood table.
- **SC-004** (FR-007, FR-008): unit tests prove the faces planted for each side count and windward key, and that the
  non-windward bands are thinner than the windward arms.
- **SC-005** (FR-010, FR-011): the cohort passes (every seed's checks green, every household seated) with the three
  forms rolled and each side count present among its non-nucleated seeds.
- **SC-006** (FR-012): the pool is regenerated, `make done` is green, and every regenerated pool map whose layout moved
  gets its settlement-review.

## Decisions Recorded

- **Weights**: 50 / 30 / 20, a GUESS, the GM's ruling of 2026-09-29. Two sides is the form reported in the most regions
  and the only one with a general statement and an early-Edo date; three is Tonami's; four is Izumo's.
- **Flood ground**: four sides at 40%, the other two scaled to keep 5 : 3 (37.5 / 22.5 / 40) - the Izumo ring's own
  stated cause was flood; the scaling is a GUESS.
- **Per settlement, not per farm**: grove shape is reported as regional custom.
- **Windward deep, rest thinner**: Tonami's tall cedar on the windward faces and lesser trees elsewhere; a GUESS for the
  Izumo ring; the thinner depth is a GUESS.
- **The front is the open side of three**: Tonami's east front had little grove.
- **The 2026-08-29 hook ruling is reversed for the farmstead grove** (the GM approved "This reverses the GM's
  2026-08-29 hook ruling"); both rulings are recorded. **The village belt is not this knob**: it stays on one or two
  windward sides on `vegetation/030`'s own evidence, and the GM approved "the homestead grove only".
- **Flood-prone ground is the polder site** (FR-006): the Izumo ring stood on a flood plain behind an earth bank; the
  engine's diked low ground is the polder archetypes and the dike-top line. Reading it from those is this project's
  decision (a GUESS as to where else floods threatened farms), and a map may pin it either way.
- **Every farm carries its settlement's grove** (FR-010, spec-fidelity round 1): no farm quietly loses sides for want
  of room; a farm is seated where its grove fits.
- **The pool takes its seed's roll** (FR-012): the GM asked for the forms "rolled again"; pinning the existing hamlets
  to nucleated would be an exception not asked for. Which hamlets change is reported at hand-back.

## Review history

**Round 1** (spec-fidelity, MODE 2, 2026-09-29): CHANGES. (a) flood weights, (b) the cardinal reading and (c) FR-012
faithful. Changes applied: the 2026-08-29 ruling recorded as REVERSED for the farmstead grove, not recast as standing
for the belt; the no-room edge case deleted and FR-010 requiring every farm seated with room for its rolled grove;
FR-010 naming every rule feature 126 measured failing, `groves_on_windward_side` included; flood-prone ground defined
(pinnable, else the polder archetypes or dike-top houses) with a test on a real polder site; the front defined as the
lee side with the yard and the way in, the side three leaves open.
