# Feature 289 - adjacent before diagonal

**Feature**: 289-adjacent-before-diagonal | **Created**: 2026-09-29 | **Status**: Draft
**Input**: the GM's questions and ruling, verbatim in [`request.md`](request.md).

## Summary

The one caption placer (feature 266) names a small thing it cannot name from inside - a notice board, a well, a
latrine - at the first free position of a ranked list, and the list it follows (QGIS's default, after Krygier and Wood)
tries the four diagonal corners first. The GM rules a deliberate deviation for these captions: a name stands ADJACENT
to what it names before it stands diagonal to it - directly above first, then directly below, then left, then right -
and every other position the placer tries today follows, in today's order. Nothing else changes: a caption that fits
inside what it names is placed there exactly as now, and the search's rings, costs, fallback and leaders are as now.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A small thing named beside it, not at its corner (Priority: P1)

A notice board with open ground in front of it and beside it is named directly above or below it, or level beside it,
not at a diagonal corner.

**Independent test**: a small subject with every position free takes "above"; with above blocked, "below"; with both
blocked, "left"; then "right"; only with all four blocked does it take a corner.

### User Story 2 - The deviation is on the record (Priority: P1)

A reader of the research record who asks why a small thing's label stands where it does finds the standard's order,
the GM's deviation from it, and what the research found about other published orders.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: For a caption the placer names from beside its subject (a point subject - a thing too small for its
  name, or one it is not placed inside), the ranked positions MUST be tried in this order: directly above, directly
  below, left, right, and then every position the standard tries today that is not one of those four, in today's
  order (upper right, upper left, lower right, lower left, above slightly right, below slightly left).
- **FR-002**: Everything else about placement MUST be unchanged: a caption that fits inside what it names is placed
  inside as now; the rings (nearer first), the costs, the extended fallback search, the nudge, leaders, and the
  hand-sheet order and repair are as they are. The fallback search's sides follow the same deviation where it walks
  them in an order (above, below, left, right).
- **FR-003**: The deviation MUST be recorded as a deliberate deviation (the GM's ruling, 2026-09-29) in the research
  record's entry on where a caption sits, in the placer's standard where the order is defined, and in this spec, with
  what the research found: the standard's order and its source, and the other published orders read.
- **FR-004**: The change MUST hold on every map the one placer labels: the hand-drawn sheets are regenerated with it,
  and the generated maps take it at their next render.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002): the placer's existing unit tests of rings, costs, the fallback, leaders and inside
  placement pass with only their expected position names changed; and unit tests prove the order on a subject with positions blocked in turn: above, then below, then
  left, then right, then the corners.
- **SC-002** (FR-001, FR-004): on the four hand sheets (Hayakawa, Ochiba and Ubame magistracies, the Hoshigaoka shrine), no notice board's label stands at a diagonal corner where an
  adjacent position at the same ring is free.
- **SC-003** (FR-003): the research record's entry names the deviation and its class; `make done` is green.

## Assumptions

- "Small objects" is what the placer already names from beside: a point subject. Which captions go inside and which
  beside is unchanged (FR-002), so the reordering reaches exactly the captions the GM described.

## Decisions Recorded

- **The order is the GM's as stated** - above, below, left, right. The GM also said it matches Zoraster's oil well labeling
  models (research.md R3); the order the research reader reported for Zoraster's third model (Bobák, Čmolík and Čadík
  2024, Table 1) is top, top right, top left, right, left, bottom right, bottom, bottom left, which differs. The GM
  stated the order twice, explicitly; it is implemented as stated. Its four-way order is a Mapbox documentation example's (top, bottom,
  left, right - an example's settings, not a stated default). Found while writing the record: the one published user
  study (Bobák, Čmolík and Čadík 2024, nearly 800 readers) found readers significantly prefer a name directly above its
  point, and its order runs top, bottom, right, top right, bottom right, left, top left, bottom left - close to the
  GM's, not it; adopting it would follow a published order rather than a deviation. Both raised with the GM at
  hand-back.
- **Scope: the one placer.** The ranked positions live in the placer every map shares (feature 266: "one placer for
  all labels"), and the GM's reasoning - a name adjacent to a small drawn object - holds for the generated hamlets'
  small objects as for the hand sheets'. So the order changes for every point caption; which captions are points is
  unchanged.
- **Class: deliberate deviation** (the GM's ruling), not a new standard: no published source read addresses small
  drawn objects on large-scale plans as their own case.

## Review history

**Round 1** (spec-fidelity, MODE 2, 2026-09-29): FAITHFUL. Implementing the GM's stated order (above, below, left,
right) and raising the Zoraster attribution at hand-back is the faithful reading - Zoraster's reported order puts two
diagonals ahead of left and right, against the GM's stated purpose; nothing may say the order "follows Zoraster".
Applying it to every point caption is within the request: the GM ruled by the kind of object, not the kind of map, and
one placer with one order is the smaller change.

**Round 2** (spec-fidelity-verify, MODE 3, 2026-09-29): FAITHFUL. The amendment corrects the Mapbox wording (an
example's settings, not a stated default) and records the 2024 user study for hand-back without adopting its order;
FR-001 still carries the GM's order. The plan's round 2 (MODE 4): CLEAR - D3 now puts the other published orders in the
record, cited.
