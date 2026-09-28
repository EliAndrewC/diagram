# Feature 283 - a garden's sun, checked on hand-drawn sheets

**Feature**: 283-garden-sun-check | **Created**: 2026-09-28 | **Status**: Draft
**Input**: the GM's request and answer, verbatim in [`request.md`](request.md).

## Summary

The scripted maps seat a kitchen bed by sun rules (research homesteads 030, 040, 043); nothing applies them to a
hand-drawn sheet. The GM asked whether the Hoshigaoka shrine's garden has enough clearance from the trees, and for an
automated check, run on hand-drawn diagrams with gardens, of the distance between the gardens and what casts shade -
buildings and trees. Measured (request.md): four of the five gardens drawn fail - the shrine's and three magistracies'.
The GM chose to move them all.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The check (Priority: P1)

A session that draws or edits a hand-drawn sheet with a kitchen garden is told, by the sheet audit the gate already
runs, when the garden gets too little sun - how many hours it gets, how many it needs, and what shades it.

**Independent test**: the check fails a sheet whose garden is shaded (a frozen negative fixture: the shrine sheet as it
is today) and passes one whose garden is open (the county example).

**Acceptance**:
1. **Given** a hand-drawn sheet with a `vegetable garden`, **When** the audit runs, **Then** the check computes the bed's
   hours of direct sun from every drawn building, wall and tree, and fails the sheet when they fall short.
2. **Given** a failure, **When** it is reported, **Then** it names the garden, its hours, the hours it needs and the
   shade makers that take its sun.

### User Story 2 - The record behind it (Priority: P1)

A reader finds, in the research record, how many hours a kitchen bed needs and how the check counts them, each figure
with its source or its label.

### User Story 3 - The sheets fixed (Priority: P1)

The shrine's and the three magistracies' gardens are re-seated where they get their sun; each sheet passes the check
and its reviews.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The research record MUST answer how many hours of direct sun a kitchen bed needs, with the crop classes
  the sources give, and state how the check counts them - the season, the sun, what counts as a lit hour, and the
  heights it gives what casts shade - each with a source or a label (research homesteads 044).
- **FR-002**: Where the sources support more than one kind of bed (sun crops, half-shade crops), the bed's kind MUST
  be a knob a sheet declares, with the sun bed the default.
- **FR-003**: The sheet audit MUST gain a check, `garden_sun`, run on every hand-drawn sheet the audit reads, that
  finds each drawn kitchen garden by its kind, casts the shadows of every drawn building, wall and tree over it through
  the day of the record's season, and fails the sheet when the bed's lit hours fall under its kind's threshold. It MUST
  report the hours, the threshold and the shade makers.
- **FR-004**: The check MUST be proved to fire on a frozen negative fixture (the shrine sheet as drawn before this
  feature) and to pass a sheet whose garden is open, and MUST carry unit tests to the gate's coverage floor.
- **FR-005**: The Hoshigaoka shrine's garden and the Ochiba, Hayakawa and Ubame magistracies' gardens MUST be
  re-seated where the check passes (the GM, 2026-09-28: "Move them all"), a magistracy's preferring the west side of
  its residence, the one side the record attests (research buildings 400); each sheet's notes, program checks and
  kinds stay true, and each sheet passes a `building-review`, ledgered. A shrine garden's place stays within the sheet's
  match to its village map.
- **FR-006**: The program declarations and operative docs that describe where a garden goes MUST name the sun rule,
  so a later sheet is drawn to it.
- **FR-007**: `make done` MUST be green, with the check in the gate.

### Edge Cases

- **A sheet with no kitchen garden** passes the check with nothing to measure, and says so.
- **A garden shaded only by something drawn off the frame** cannot be known; the check reads only what the sheet draws.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002): research homesteads 044 exists, every claim footnoted or labeled, all record checks run
  and applied.
- **SC-002** (FR-003, FR-004): the check fails the negative fixture naming its hours and shade makers, and passes the
  county example; its tests reach the gate's coverage floor.
- **SC-003** (FR-005, FR-007): every hand-drawn sheet with a kitchen garden passes `garden_sun`; the re-seated sheets
  pass `building-review`; `make done` is green.
- **SC-004** (FR-006): the program and the operative docs name the sun rule where they say where a garden goes.

## Assumptions

- The binding season and sun are the record's (38 degrees north, the autumn shoulder month), as the scripted maps' rules
  use them.
- The scripted maps keep their own placement rules; this feature adds nothing to the placer.
