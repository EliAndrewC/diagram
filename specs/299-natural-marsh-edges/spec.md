# Feature 299 - natural marsh edges

**Feature Branch**: none (main, in the clone `diagram-performance`)
**Created**: 2026-10-01
**Status**: Draft
**Request**: [`request.md`](request.md) - the GM's words verbatim: the scrub-marsh boundary "is just a straight line which is
not how that would actually look"; "the marshland on the top left side of the marsh just stopping at a sharp right angle ...
It would be more like a rounded curve"; the two ways the GM offered ("make the boundary a more complicated shape", "boundary
tiles ... [that] show a more gradual transition"); "Could you do the same thing with the marshland?" (the scrub's varied look);
and, to the session's three-part proposal, "Yes, please. Go ahead and build the feature and then work it start to finish".
**Predecessors**: 298 (the cover tiles), 287 (the marsh's record is its drawn ground).

## Summary

Feature 298 drew the marsh's reeds as a tile with a hard edge, and that edge exposed the marsh's outline: the wet-toe band is
laid as straight strips, so it meets the scrub on a ruled line and stops at right-angled corners (Inashiro: the east-west line
on the right, the right angle at the top left). This feature gives the marsh a natural outline (rounded corners and a slow
irregular wave along its open edges), draws a mixed fringe of reeds and grass where scrub meets marsh, and lays a second, larger,
sparse tile over the marsh (denser reed clumps and small open-water patches) and over the scrub (denser grass clumps), so
neither repeats visibly. The session's correction is recorded: there is one scrub tile; the scrub's variety is its scattered
pines and the ground cut out of it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The marsh has a natural outline (Priority: P1)

**Independent Test**: regenerate Inashiro; read the marsh's recorded outline and the map.

**Acceptance Scenarios**:

1. **Given** a toe, waterside or defense marsh laid from straight strips, **When** it is drawn, **Then** none of its outline's
   corners on open ground is a sharp angle - each is a curve - and its open edges wave in and out rather than run straight.
2. **Given** a marsh laid against a paddy, a pond or a dike, **When** it is drawn, **Then** it still stops at that feature's
   edge (the cut-outs happen after the outline is shaped).
3. **Given** a pond's reed fringe, **When** it is drawn, **Then** it keeps its ring: it is laid as an ellipse round the pond and
   has no straight edge or right angle for the shaping to mend.

### User Story 2 - Scrub grades into marsh through a mixed fringe (Priority: P1)

**Acceptance Scenarios**:

1. **Given** scrub meeting a marsh, **When** the map is drawn, **Then** a band about 30 ft wide along their boundary - half on each
   side - is filled with a fringe tile of sparse reeds mixed with grass, in place of the two tiles meeting on a line.
2. **Given** a marsh edge that meets a field, a pond or bare ground rather than scrub, **When** it is drawn, **Then** no fringe is
   drawn there.

### User Story 3 - Marsh and scrub look varied (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a marsh, **When** it is drawn, **Then** over its reed tile lies a second sparse tile of a different, larger repeat
   with denser reed clumps and small open-water patches, so the texture does not visibly repeat at the base tile's period.
2. **Given** scrub, **When** it is drawn, **Then** it carries the same kind of second layer (denser grass clumps).

### Edge Cases

- A marsh too small to shape (narrower than the rounding) keeps the largest rounding it can take, or its own outline.
- The shaping only ever takes ground away from the marsh's laid outline, never adds to it, so every rule that reads the marsh -
  a lane's end off it, a house off it, the no-build ground - holds as before (the scrub fills what the marsh gives up).
- The fringe's scrub half and marsh half keep their own classes, so hovering either still lights scrub or marsh.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A toe, waterside or defense marsh's outline MUST be shaped before the fields, dikes, ponds, blocks and clearings
  are cut out of it: its corners rounded and its edges given a slow irregular inward wave (the approved proposal's targets for both, and
  the figures as built, are research R1's table), rolled from the map's seed per marsh, so the shaped open edge meets the
  laid straight line at single points at most, never along a run. A pond's fringe is not shaped (it is laid as an ellipse). The
  targets are the approved proposal's; calibration by eye may move them, and a material departure is recorded with its reason
  (research R1).
- **FR-002**: The shaped outline MUST lie within the laid outline (shaping removes ground, never adds it).
- **FR-003**: Where scrub meets marsh, a band straddling the boundary, half its width into each, MUST be drawn with a fringe tile
  of sparse reeds and grass, in each side's class, in place of the scrub and marsh tiles there; nowhere else.
- **FR-004**: The marsh MUST carry a second tile over its reed tile - a larger, different repeat than the base's with denser reed
  clumps and small open-water patches - and the scrub a second tile over its grass tile with denser grass clumps. The reed base
  tile itself grows from feature 298's repeat to a larger one with an even wet haze, a recorded departure (research R1:
  at feature 298's repeat its tint patches read as a lattice); the reed overlay's repeat is larger than that new base's. Targets, as-built
  figures and departures are in research R1.
- **FR-005**: The record (`M["marshes"][].poly`, the no-build ground, `marsh_ground`) MUST be the shaped outline, so every reader
  of the marsh reads what is drawn.
- **FR-006**: The pool MUST regenerate and pass the gate; maps may move within the rules (the GM 2026-09-30).
- **FR-007**: The research record and the modals that describe the marsh's and the scrub's drawing MUST say what is drawn now.

### Key Entities

- **Shaped outline**: the laid marsh ring, rounded and waved, before its cut-outs.
- **Fringe band**: the strip either side of the scrub-marsh boundary, drawn with the fringe tile in each side's class.
- **Overlay tile**: the second, larger, sparse tile drawn over the marsh's and the scrub's base tiles.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002, FR-005): every shaped outline lies within its laid outline and has no straight run along it longer
  than a quarter of the wave's shortest length (a unit test of the shaping on a laid rectangle); on Inashiro, the toe marsh's
  edge on the right (laid as a straight east-west line) and its top-left corner (laid as a right angle) are shaped - no corner
  sharper than 120 degrees on open ground, and no straight run of the laid line (a test on the regenerated manifest).
- **SC-002** (FR-003): on the pool hamlets with scrub and marsh, the fringe tile is drawn in both the scrub's and the marsh's slot;
  a unit test shows no fringe where the marsh meets anything but scrub.
- **SC-003** (FR-004): every marsh and scrub cover path is drawn with its overlay tile.
- **SC-004** (FR-006, FR-007): `make done` green; `entry-drift` and `record-format` on what the record says; the GM's look at Inashiro.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The marsh's outline rounded and waved | map drawing convention | the GM: a marsh would show "a rounded curve", not a ruled line; the laid band's straight strips are this engine's construction, not a finding | `land/wet.py` |
| The wave only takes ground away | map drawing convention | every rule that reads the marsh holds; the scrub takes what the marsh gives up | `land/wet.py` |
| A mixed fringe tile at the scrub-marsh boundary | map drawing convention (the margin's grading - grass into sedge into reed - is the record's finding, research/vegetation 120) | the GM's "more gradual transition" | `settlement/finish.py` |
| A second, larger tile over the marsh and the scrub | map drawing convention | the GM's "a little bit more varied" | `land/tiles.py` |

## Assumptions

- The figures' targets are the approved proposal's (`request.md`); they are calibrated by eye on Inashiro, and the as-built figures
  and every material departure, with its reason, are in research R1. They are drawing choices, not findings.

## Review history

- Round 1 (spec-fidelity, 2026-10-01): CHANGES REQUIRED - the wave must not leave straight runs and the GM's line must be
  measured; the approved figures stated as targets; (advised) the pond fringe's reason. Addressed: FR-001, FR-004, SC-001,
  User Story 1 scenario 3.
- Round 2 (spec-fidelity-verify): CHANGES REQUIRED - the reed base tile grew past the overlay's repeat and no FR stated it; the
  Assumptions still said "recorded in the plan". Addressed: FR-004 states the base change as a departure, the reed overlay is
  larger than the new base (research R1), the Assumptions point at R1.
