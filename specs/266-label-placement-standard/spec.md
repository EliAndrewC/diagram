# Feature Specification: Labels placed by the cartographic standard

**Feature Branch**: `266-label-placement-standard` (no branch - `main`, per CLAUDE.md)

**Created**: 2026-09-27

**Status**: Draft

**Input**: the GM's request, verbatim in [`request.md`](request.md): *"Yes please adopt this standard into our
project, after looking up the details enough to be able to implement it faithfully. I also agree with one placed for
all labels."* - with tilted text allowed for tilted features, a leader line allowed where the standard calls for
one, labels never dropped, and *"making sure our notice boards use this standard but that other future labels will
be able to do so as well."*

## Summary

Every hamlet's notice-board caption stands 12 to 20 ft off its board (1.5x to 2.4x its own text height) and two of
five are also slid along the board (research.md R2; observed 2026-09-27, method: the rotated caption block against
the rotated board footprint, read from each pool manifest), because its seat search was hand-built on the page's axes. The
cartographic standard for placing a label is well documented and readable (research.md R1): ranked candidate
positions around the feature starting at upper right, a small consistent gap measured from the feature's drawn
edge, a cost that prefers free space and otherwise the least important thing to cover, a maximum offset past which
a leader line ties the label to its feature, and a rotated feature's label following the feature's angle. This
feature writes that standard down in the research record, builds ONE placer that implements it, and routes every
searched caption through it - the notice board first.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The notice board's caption sits where the standard puts it (Priority: P1)

The GM opens any pool hamlet and the notice board's caption stands close beside the board, at the board's angle,
at the first ranked position that is clear, the same distance off the board on every map.

**Independent Test**: roll the five pool hamlets; each board caption's gap to its board is the preferred offset
(or, where that seat is blocked, within the maximum offset, or joined by a leader line), and its position is the
highest-ranked free one.

**Acceptance Scenarios**:

1. **Given** a board with clear ground at upper right in its own frame, **When** labels are placed, **Then** the
   caption stands at upper right, its block's nearest edge the preferred offset from the board's drawn footprint.
2. **Given** upper right is covered by a house, **When** labels are placed, **Then** the caption takes the next
   ranked position that is free (upper left, then lower right, ...).
3. **Given** no position is free within the maximum offset, **When** labels are placed, **Then** the caption goes
   to the nearest free seat further out and a leader line joins it to the board.
4. **Given** no free seat exists anywhere in reach, **When** labels are placed, **Then** the caption is still
   drawn, at the seat covering the least total weight - it is never dropped.

### User Story 2 - A future labeled feature uses the same placer (Priority: P1)

A session adding a new labeled feature names its SUBJECT (the drawn footprint, a point, a line or an area) and the
caption text; it writes no seat search of its own.

**Independent Test**: a unit test places captions for a synthetic point, box, rotated box, line and area subject
through the one entry point and each lands where the standard says.

**Acceptance Scenarios**:

1. **Given** a subject and a text, **When** a caption is requested, **Then** the placer chooses the seat, the
   angle, the line breaks and any leader, and the caption is drawn in the label phase.
2. **Given** the engine after this feature, **When** it is searched for another caption seat search, **Then**
   there is none: the board's annulus and the standoff ladder behind `place_caption` and the road caption are gone.

### User Story 3 - The standard is in the record, cited (Priority: P2)

A reader clicking "See references" on the notice board reaches a research answer saying how captions are placed
and why, with every rule quoted from a page they can open.

**Independent Test**: the presentation page's caption questions carry the standard with footnotes, and
`quote-check`, `record-format` and `source-applicability` pass on them.

### Edge Cases

- A caption much longer than its subject (the 53 ft "notice board" beside a 12 ft board): the ranked positions are
  defined off the subject's box, so upper right means the text starts past the board's right end and above it.
- A subject rotated past 90 degrees: the text is turned to read upright, and "upper" is the upright text's up.
- A seat past the edge of the finished frame: forbidden - a clipped caption is unreadable.
- Two captions competing: the earlier-placed caption is an obstacle to the later one (queue order, as today).
- A caption that clears only when wrapped: the GM's wrap rule (research/presentation, "Why does a caption
  sometimes break across two lines?") stands - at a seat, one line is tried first, then two, then three.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST have ONE caption placer, and every caption whose seat the engine searches for - the
  notice board, the deferred building captions (`place_caption`), the Imperial road's caption and the field names -
  MUST be placed by it. The board's own annulus search and `_best_label_spot`'s standoff ladder MUST be removed.
- **FR-002**: The placer MUST take a SUBJECT - a point, a box (level or rotated), a line or an area - plus the
  caption's text, size and style, and return the seat, the angle, the line breaks and an optional leader.
- **FR-003**: For a point or box subject the placer MUST try the standard's ranked positions in the standard's order
  - upper right, upper left, lower right, lower left, right, left, above slightly right, below slightly left -
  defined in the subject's own frame.
- **FR-004**: The gap MUST be measured from the subject's drawn edge to the caption block's nearest edge, and the
  first ring of candidates MUST stand at one PREFERRED OFFSET, the same for every caption of a size.
- **FR-005**: Candidate seats beyond the preferred offset MUST be tried ring by ring outward; the MAXIMUM OFFSET is
  twice the preferred offset (Esri's 200 percent), and a caption seated beyond it MUST be joined to its subject by
  a leader line.
- **FR-006**: Every candidate MUST be scored by the standard's cost: the weights of what it covers (another caption,
  the subject itself, a built feature, a well or other point fixture: 1,000 - an obstacle; a way or a watercourse:
  a weight per way crossed, so crossing one beats crossing several; ground cover, fields and other area fills: 0 -
  free space), the frame edge forbidden. A free candidate (total weight 0) MUST beat any candidate that covers
  weight; among free candidates the nearer ring wins, then the higher-ranked position, then fewer lines.
- **FR-007**: A caption MUST never be dropped: when no candidate in reach is free, the one covering the least total
  weight is drawn (ties to the nearer ring, then rank).
- **FR-008**: A rotated subject's caption MUST take the subject's angle, normalized to read upright; a level
  subject's caption is level; a line subject's caption runs along the line above it before below it and never
  upside down; an area subject's caption lies inside the area.
- **FR-009**: The town and city rule of what a caption may lie on (research/presentation, "What does a town or a
  city map label, and what may a label cover?") MUST be kept by the weights: a built feature the caption's group
  may cover weighs 0 for that caption.
- **FR-010**: The placer MUST build its obstacle index once per caption request batch and ask it per candidate
  (constitution X clause 15), never walking a registry per candidate.
- **FR-011**: The research record MUST state the standard - the ranked positions, the offset and its maximum, the
  cost and the free-space rule, leader lines, rotation - with every rule footnoted to a public page it is quoted
  from, and every calibration this feature chose labeled as one.
- **FR-012**: Every hamlet in the pool MUST be regenerated under the placer and pass the gate.

### Key Entities

- **Subject**: what a caption names - a point, a box with a rotation, a polyline, or an area polygon - in drawn
  (not recorded-center) geometry.
- **Candidate**: a seat, an angle and a line layout for one caption, with its ring (distance) and rank.
- **Placement**: the chosen candidate plus its leader line, if any.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-003, FR-004, FR-006, FR-012): on every pool hamlet the board caption stands at a ranked position
  with its gap equal to the preferred offset, or - where no free seat exists at that ring - at the nearest free
  ring, with a leader past the maximum offset. Measured as in research.md R2 (method: the caption block against the
  board footprint in each manifest), before and after; the before is observed 2026-09-27.
- **SC-002** (FR-001, FR-002, FR-008, FR-009, FR-010): unit tests place captions for a point, a level box, a rotated
  box past 90 degrees, a line and an area subject through the one entry point, and a test proves the engine holds
  no other seat search (the removed functions are gone and no caption path bypasses the placer).
- **SC-003** (FR-005, FR-006, FR-007): unit tests prove, on synthetic sheets: a blocked upper right falls to upper
  left; a free far seat beats a covered near one; crossing one way beats crossing two; a seat beyond the maximum
  offset draws a leader and one within it draws none; a sheet with no free seat still draws the caption at the
  least-weight seat.
- **SC-004** (FR-011): `quote-check`, `record-format` and `source-applicability` pass on the changed research
  questions and the new registry entries; the unreadable works (Imhof, Yoeli) are on the GM's download list.
- **SC-005** (spec-wide): `make done` is green with 100% coverage and the push lands on main.

## Decisions Recorded

- **D1 - The ranked positions and their order: MAP DRAWING CONVENTION, sourced** (research.md R1, QGIS citing
  Krygier and Wood 2011; the eight-position ranking in Christensen, Marks and Shieber 1995 after Yoeli 1972). PSU
  notes authorities differ slightly on the order; QGIS's is the one written down in full and readable, so it is the
  one adopted. Not a knob: the standard's own first rule of spacing is consistency across the map.
- **D2 - The preferred offset: MAP DRAWING CONVENTION, a calibration.** No readable source fixes a number
  (research.md R1). Half the caption's font size (0.5 em) - the air the engine's own house standoff already gave a
  caption by eye (`LABEL_MIN_AIR`, about 0.55 em on a 9 pt caption), and inside PSU's "not too tightly packed" and
  "consistent". It is the same for every caption of a size.
- **D3 - The maximum offset is twice the preferred, and a leader past it: MAP DRAWING CONVENTION, sourced** - Esri's
  documented 200 percent maximum, and the leader both tools use for a label displaced beyond its normal offset. The
  GM: a leader is allowed but "we should follow the standard for deciding whether to do it".
- **D4 - The weights: MAP DRAWING CONVENTION, sourced in form, calibrated in value.** Esri's 0-to-1,000 scale and
  its free-space-first rule; its "cross one road instead of several" for ways (research.md R1). Which families are
  1,000 and which are 0 is this project's classification, following the record's existing rule that ground cover is
  not an obstacle (research/presentation, the wrap question).
- **D5 - Never dropped: the GM's ruling, 2026-09-27** - *"for the time being we'll treat labels as mandatory when the
  thing is marked as needing a label."* Esri's and QGIS's "leave unplaced" option is therefore not implemented.
- **D6 - A rotated feature's caption follows its angle: sourced** (Esri, rotation by attribute overrides the
  position) **and the GM's standing ruling** of 2026-08-27 (research/presentation, the tilt question), reaffirmed:
  *"Tilted or horizontal text is okay for small point features like the board."*
- **D7 - The 50 percent pull toward the board (GM 2026-08-27, marked provisional in the record) is superseded** by
  the preferred offset, which is the standard's answer to the same question.
- **D8 - SCOPE EXCEPTION, put to `spec-fidelity`**: about 50 captions in the town, city and capital tiers are
  hand-seated by their calling code (research.md R3) - a ministry's name written across its own roof, a hall's
  caption at a fixed drop - and no live generator runs any of them. They are not a seat SEARCH, so FR-001 does not
  reach them; each will name its subject and go through the placer when its tier is scripted. Recorded in
  `future-work/cities.md`. Converting them now would change code no map exercises, verified only by tests written
  for the conversion.

## Assumptions

- The label phase (feature 157) is kept: captions still queue and are placed after the last map feature, in queue
  order.
- The drawing of a caption - its typeface, halo, record box and wrap cutting - is unchanged; the placer decides
  where, at what angle, on how many lines, and whether with a leader.
- The existing caption gate tests (the hug cap, the alignment, the lane notch) stay; the notch clearance is part of
  what counts as covering a way.

## Out of scope

- Line-label curving along a road's bends (the road caption stays straight along its local bearing).
- Dropping captions on crowded maps (D5).
- Converting the hand-seated captions of the unscripted tiers (D8).

## Review history

(none yet)
