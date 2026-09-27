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
the rotated board footprint, read from each pool manifest), because its seat search was hand-built on the page's
axes. The cartographic standard for placing a label is documented and readable (research.md R1): ranked candidate
positions around the feature starting at upper right, a small consistent gap measured from the feature's drawn
edge, the nearer position preferred, free space first and otherwise the least important thing to cover, a leader
line for a label that can no longer stand directly beside its feature, an area's name inside the area, and a
rotated feature's label following the feature's angle. This feature writes that standard into the research record,
builds ONE placer that implements it, and seats with it every caption engine code draws and every notice board on
every live map - the hand-drawn sheets' through a tool - so that every caption written from now on goes through it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The notice board's caption sits where the standard puts it (Priority: P1)

The GM opens any pool hamlet or magistracy sheet and the notice board's caption stands close beside the board, at
the board's angle, at the first ranked position that is clear, the same distance off the board on every map.

**Independent Test**: roll the five pool hamlets and draw the two composed magistracy sheets; each board caption's
gap to its board is the preferred offset at the highest-ranked free position, or - where no position at that gap is
free - the nearest free seat further out with a leader line. `make seat-label --check` reports each hand-drawn
magistracy sheet's board caption at its standard seat.

**Acceptance Scenarios**:

1. **Given** a board with clear ground at upper right in its own frame, **When** labels are placed, **Then** the
   caption stands at upper right, its block's nearest edge the preferred offset from the board's drawn footprint,
   with no leader.
2. **Given** upper right is covered by a house, **When** labels are placed, **Then** the caption takes the next
   ranked position that is free at the preferred offset (upper left, then lower right, ...).
3. **Given** no position is free at the preferred offset, **When** labels are placed, **Then** the caption goes to
   the nearest free seat further out and a leader line joins it to the board.
4. **Given** no free seat exists anywhere in reach, **When** labels are placed, **Then** the caption is still drawn,
   at the seat covering the least total weight - it is never dropped.

### User Story 2 - A future labeled feature uses the same placer (Priority: P1)

A session adding a new labeled feature - in the settlement engine, the compound composer or a hand-drawn sheet -
names its SUBJECT (the drawn footprint of a point feature, a line or an area) and the caption text; it writes no
seat of its own.

**Independent Test**: unit tests place captions for synthetic point, rotated-box, line and area subjects through
the one entry point and each lands where the standard says; a static test fails on a caption written outside the
placer anywhere but the named exceptions.

**Acceptance Scenarios**:

1. **Given** a subject and a text, **When** a caption is requested, **Then** the placer chooses the seat, the
   angle, the line breaks and any leader.
2. **Given** the engine after this feature, **When** a new hand-seated `self.label(x, y, ...)` call or a new
   hand-placed caption in `compound.py` is added, **Then** a test fails naming it.

### User Story 3 - The standard is in the record, cited (Priority: P2)

A reader clicking "See references" reaches a research answer saying how captions are placed and why, with every
rule quoted from a page they can open.

**Independent Test**: the presentation page's caption questions carry the standard with footnotes, and
`quote-check`, `record-format` and `source-applicability` pass on them.

### Edge Cases

- A caption much longer than its subject (the 53 ft "notice board" beside a 12 ft board; research.md R4, observed
  2026-09-27, method: read from the code): the ranked positions are defined off the subject's box, so upper right
  means the text starts past the board's right end and above it.
- A subject rotated past 90 degrees: the text is turned to read upright, and "upper" is the upright text's up.
- A seat past the edge of the finished frame: never taken - a clipped caption is unreadable.
- Two captions competing: the earlier-placed caption is an obstacle to the later one (queue order, as today).
- A caption that clears only when wrapped: the GM's wrap rule (research/presentation, "Why does a caption sometimes
  break across two lines?") stands - at a seat, one line is tried first, then two, then three.
- A hand-drawn sheet's caption with no `data-kind` tag (Hayakawa's board caption): it is tagged with its subject's
  kind when it is re-seated, because the tool finds a caption's subject by the tag.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: There MUST be ONE caption placer, a module neither Mode A nor Mode B owns. It MUST seat:
  - every caption engine code draws: in Mode B every caption the settlement engine searches a seat for (the notice
    board, the deferred building captions of `place_caption`, the Imperial road's caption, the field names), and in
    Mode A every caption `compound.py` draws;
  - every notice-board caption on every live map, the hand-drawn sheets' included (through FR-013's tool);
  - every caption written from now on, in either mode.

  The exceptions are D8 and D9, and only those. A sheet's title, its scale-bar text and its draft note are not
  captions (they name no feature) and are not placed. The board's own annulus search and `_best_label_spot`'s
  standoff ladder MUST be removed.
- **FR-002**: The placer MUST take a SUBJECT - a point feature's drawn footprint (level or rotated), a line or an
  area - plus the caption's text and size, and return the seat, the angle, the line breaks and an optional leader.
- **FR-003**: For a point feature the placer MUST try the standard's ranked positions in the standard's order -
  upper right, upper left, lower right, lower left, right, left, above slightly right, below slightly left - in the
  subject's own frame.
- **FR-004**: The gap MUST be measured from the subject's drawn edge to the caption block's nearest edge, and the
  first ring of candidates MUST stand at one PREFERRED OFFSET, the same for every caption of a size.
- **FR-005**: The placer MUST prefer the nearer seat (the standard's default, "Prefer closer labels"): every position
  and line layout at the preferred offset is tried before any seat further out, then the positions ring by ring
  outward to a reach limit. A caption seated at the preferred offset is directly adjacent to its subject and gets no
  leader; a caption seated anywhere further out MUST be joined to its subject by a leader line - which, with every
  adjacent seat tried first, keeps leaders to the cases that need one.
- **FR-006**: Every candidate MUST be scored by the standard's cost, on Esri's 0-to-1,000 scale: another caption, the
  subject itself, a built feature, a wall and a well or other point fixture weigh 1,000 (an obstacle); each way or
  watercourse the block crosses weighs 500 (so crossing one beats crossing two); ground cover, fields and other area
  fills weigh 0 (free space). A seat past the frame is never a candidate. A free candidate (total weight 0) MUST beat
  any candidate that covers weight; among free candidates the nearer ring wins, then the higher-ranked position, then
  fewer lines.
- **FR-007**: A caption MUST never be dropped: when no candidate in reach is free, the one covering the least total
  weight is drawn (ties to the nearer ring, then rank), with its leader if it is not at the preferred offset.
- **FR-008**: A rotated subject's caption MUST take the subject's angle, normalized to read upright; a level subject's
  caption is level; a line subject's caption runs along the line, above it before below it, never upside down; an area
  subject's caption lies inside the area, over its centroid when that is free and otherwise at the free interior seat
  nearest the centroid.
- **FR-009**: The placer MUST build its obstacle index once per label phase (or tool run) and ask it per candidate
  (constitution X clause 15), adding each placed caption to it, never walking a registry per candidate.
- **FR-010**: The research record MUST state the standard - the ranked positions, the gap, nearness, the cost and the
  free-space rule, leader lines, area captions, rotation - with every rule footnoted to a public page it is quoted
  from, and every calibration this feature chose labeled as one.
- **FR-011**: Every hamlet in the pool and both `compound.py` sheets MUST be regenerated under the placer and pass the
  gate.
- **FR-012**: A static test MUST fail on any caption drawn outside the placer except the exempt call sites D8 names by
  file and function, and on any caption `compound.py` draws outside the placer.
- **FR-013**: A `make seat-label` tool MUST run the placer on a hand-drawn Mode A sheet: it reads the sheet's drawn
  shapes, finds each caption's subject by its `data-kind`, and reports (`--check`) or writes (`--write`) each caption's
  standard seat. With it:
  - the notice-board captions of the three hand-drawn magistracy sheets MUST be re-seated in this feature;
  - a gate test MUST hold every hand-drawn sheet to it: a caption is exempt only while it is recorded in a ledger of
    the captions as they stood when this feature landed AND its sheet is unchanged since; a sheet whose content has
    changed has no exemptions, so revising a sheet means re-seating all its captions (D9);
  - the Mode A doctrine (`buildings.md`) and the `building-review` agent's contract MUST say that every caption on a
    hand-drawn sheet is seated with the tool, and that revising a sheet re-seats all of its captions.

- **FR-014**: The GM's standing rule of what a town or city caption may lie on (2026-07-21, research/presentation,
  "What does a town or a city map label, and what may a label cover?") MUST be kept in the weights: a caption's own
  subject weighs 0 for it, and so does every built feature of a group the caption's own wording names - the group
  word of the overlap taxonomy's caption registry (a "temple" caption may lie on a temple, a flophouse caption on a
  flophouse), which is how that rule has always been keyed.

### Key Entities

- **Subject**: what a caption names - a point feature's footprint with its rotation, a polyline, or an area polygon
  - in drawn geometry.
- **Candidate**: a seat, an angle and a line layout for one caption, with its ring (distance) and rank.
- **Placement**: the chosen candidate plus its leader line, if any.
- **Exemption ledger**: the hand-drawn sheets' captions as they stood when this feature landed, with each sheet's
  content hash.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-003, FR-004, FR-005, FR-006, FR-011): on every pool hamlet and both composed magistracy sheets the
  board caption stands at a ranked position at the preferred offset with no leader, or - where no free seat exists at
  that ring - at the nearest free seat with a leader. Measured as in research.md R2 (method: the caption block against
  the board footprint in each manifest or sheet), before and after; the before is observed 2026-09-27.
- **SC-002** (FR-001, FR-002, FR-008, FR-009, FR-012, FR-014): unit tests place captions for a point, a rotated point
  past 90 degrees, a line and an area subject through the one entry point, and a caption naming a group seated over a
  building of that group while one naming another group is kept off it; the static test of FR-012 passes on the tree
  and fails on a planted hand-seated call.
- **SC-003** (FR-005, FR-006, FR-007): unit tests prove, on synthetic sheets: a blocked upper right falls to upper
  left; every preferred-offset seat is tried before any further one; a free far seat beats a covered near one;
  crossing one way beats crossing two; a seat beyond the preferred offset draws a leader and one at it draws none; a
  sheet with no free seat still draws the caption at the least-weight seat.
- **SC-004** (FR-010): `quote-check`, `record-format` and `source-applicability` pass on the changed research
  questions and the new registry entries; the unreadable works (Imhof, Yoeli, Krygier and Wood) are on the GM's
  download list.
- **SC-005** (spec-wide): `make done` is green with 100% coverage and the push lands on main.
- **SC-006** (FR-001, FR-013): `make seat-label --check` reports each hand-drawn magistracy sheet's board caption at
  its standard seat; the ledger gate test passes on the tree, fails on a sheet whose content changed while a caption
  is off its seat, and fails on a new caption off its seat; the doctrine and the review contract name the tool and the
  revision rule.

## Decisions Recorded

- **D1 - The ranked positions and their order: MAP DRAWING CONVENTION, sourced** (research.md R1, QGIS citing
  Krygier and Wood 2011; the eight-position ranking in Christensen, Marks and Shieber 1995 after Yoeli 1972). PSU
  notes authorities differ slightly on the order; QGIS's is the one written down in full and readable, so it is the
  one adopted. Not a knob: the standard's own first rule of spacing is consistency across the map.
- **D2 - The preferred offset: MAP DRAWING CONVENTION, a calibration.** No readable source fixes a number
  (research.md R1). Half the caption's font size (0.5 em) - the air the engine's own house standoff already gave a
  caption by eye (`LABEL_MIN_AIR`, 0.56 em on a 9 pt caption; research.md R4, observed 2026-09-27, method: read from
  `_geom/labels.py`), and inside PSU's "map elements that appear too tightly packed are generally undesirable" and its
  "Most important is maintaining consistency throughout your map design". The same for every caption of a size.
- **D3 - A leader for every caption not at the preferred offset: MAP DRAWING CONVENTION, sourced in rule, calibrated
  in threshold.** The rule is the standard's: QGIS draws a callout for a label "placed outside (or displaced from)" its
  feature, Esri adds one to place a label beyond its preferred offset "to remove ambiguity", and PSU connects "labels
  that do not fit on or directly adjacent to their respective feature" and says to use leaders "sparingly"
  (research.md R1). Reading "directly adjacent" as "at the preferred offset" is this project's calibration; the
  sparing use comes from trying every adjacent seat first (FR-005). Esri's maximum offset is not adopted as a band
  without a leader: its default is 100 percent of the preferred offset, which is this same rule, and its 200 percent
  is only a worked example. The GM: a leader is allowed but "we should follow the standard for deciding whether to do
  it".
- **D4 - The weights: MAP DRAWING CONVENTION, sourced in form, calibrated in value.** Esri's 0-to-1,000 scale and its
  free-space-first rule; its "cross one road instead of several" for ways (research.md R1). Which families weigh 1,000
  and which 0, and the 500 per way crossed, are this project's calibration - the classification follows the record's
  existing rule that ground cover is not an obstacle (research/presentation, the wrap question), and 500 is chosen so
  a way costs less than any obstacle but two ways cost as much as one obstacle.
- **D5 - Never dropped: the GM's ruling, 2026-09-27** - *"for the time being we'll treat labels as mandatory when the
  thing is marked as needing a label."* Esri's and QGIS's "leave unplaced" option is therefore not implemented.
- **D6 - A rotated feature's caption follows its angle: sourced** (Esri, rotation by attribute overrides the
  position) **and the GM's standing ruling** of 2026-08-27 (research/presentation, the tilt question), reaffirmed:
  *"Tilted or horizontal text is okay for small point features like the board."*
- **D7 - The 50 percent pull toward the board (GM 2026-08-27, marked provisional in the record) is superseded** by
  the preferred offset, which is the standard's answer to the same question. To raise with the GM at landing.
- **D8 - SCOPE EXCEPTION (ruled legitimate by `spec-fidelity`, round 1)**: the hand-seated `self.label(x, y, ...)`
  calls of the settlement engine's town, city and capital tiers - 47 calls in 33 functions (research.md R3), listed by
  file and function in the FR-012 test - are on no live map and are not converted now. The GM's scope sentence is
  *"making sure our notice boards use this standard but that other future labels will be able to do so as well"*;
  when a tier is scripted its captions are future labels and go through the placer. Recorded in
  `future-work/cities.md`. To raise with the GM at landing.
- **D9 - SCOPE EXCEPTION (ruled legitimate by `spec-fidelity`, round 1)**: on the three hand-drawn magistracy sheets
  only the notice-board captions are re-seated now, and the hand-drawn country shrine (which has no notice board) is
  not re-seated now. The ground is the same sentence of the GM's: the notice boards must use the standard now, the
  other labels must be able to. Each sheet's other captions are re-seated when the sheet is next revised, which the
  ledger test of FR-013 enforces. To raise with the GM at landing.

## Assumptions

- The label phase (feature 157) is kept: captions still queue and are placed after the last map feature, in queue
  order.
- The drawing of a caption - its typeface, halo, record box and wrap cutting - is unchanged; the placer decides where,
  at what angle, on how many lines, and whether with a leader.
- The existing caption gate tests (the hug cap, the alignment, the lane notch) stay; the notch clearance is part of
  what counts as crossing a way.

## Out of scope

- Line-label curving along a road's bends (the road caption stays straight along its local bearing).
- Dropping captions on crowded maps (D5).
- The captions D8 and D9 name.

## Review history

- Round 0 (2026-09-27, `spec-fidelity`): NOT-REVIEWABLE - two unlabeled figures, and the label census missed every
  Mode A sheet. Both fixed: R3 rewritten over every live map, R4 added, FR-001 and FR-011 extended to Mode A, the tool
  requirement and SC-006 added, D8 narrowed and D9 added.
- Round 1 (2026-09-27, `spec-fidelity`, the first full reading): CHANGES REQUIRED, eight items - the leader rule
  against its sources, FR-001 claiming more than D8 and D9 allow, D8's call-site list inexact, D9's reasons and the
  shrine, D9's promise unenforced, the way weight unstated, D2's quotation not verbatim, and the QGIS option
  misattributed. All eight applied: FR-005 and D3 rewritten on the standard's leader rule, FR-001 scoped with the
  exceptions named, D8 exact with a static test (FR-012), D9 on the GM's sentence with the shrine named and the ledger
  test (FR-013), the 500 weight stated and labeled, D2 verbatim, R1 on QGIS's default. D8 and D9 ruled legitimate.
- Round 2 (2026-09-27, `spec-fidelity-verify`): CHANGES REQUIRED - the round-1 rewrite had dropped the old FR-009, the
  town and city rule of what a caption may lie on, without a record; D8's function count was 34 for 33; one QGIS
  sentence was attributed to the wrong polygon mode. Applied: the rule restored as FR-014 and cited from SC-002, the
  count corrected, R1's attribution corrected.
