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
- **FR-003**: The sheet audit MUST gain a check, `garden_sun`, run on every hand-drawn building sheet (the GM,
  2026-09-28: "Sheets only" - the frozen settlement maps get the sun rules at their conversion to scripted generation),
  that finds each drawn kitchen garden by its kind, casts the shadows of every drawn thing that stands up over it through
  the day of the record's season, and fails the sheet when the bed's lit hours fall under its kind's threshold. What
  stands up MUST be named by kind: every roofed building (a residence, a hall, a gatehouse, a granary, a stage, a bell
  tower, a privy, a compound shrine), every wall, and every tree - a single crown, the crowns of a wood or grove, a
  sacred tree; what does not (a basin, a well, a door, a veranda, a hearth, low furniture) MUST be listed with why. It
  MUST report the hours, the threshold and the shade makers by kind.
- **FR-004**: The check MUST be proved to fire on a frozen negative fixture (the shrine sheet as drawn before this
  feature), its report naming the wood among the shade makers; to fail a bed shaded by trees alone (a unit test with no
  building); and to pass a sheet whose garden is open, and MUST carry unit tests to the gate's coverage floor.
- **FR-005**: The Hoshigaoka shrine's garden and the Ochiba, Hayakawa and Ubame magistracies' gardens MUST be
  re-seated where the check passes as ordinary sun beds, none declared half-shade (the GM, 2026-09-28: "Move them all";
  the half-shade option was offered and not chosen). Where a garden goes is a research question (the GM, 2026-09-28:
  "This feels like you are asking me something that should be a research question"): a magistracy's seat is taken from
  the attested seats of research buildings 405 (west of the residence, south beside the formal garden, the rear
  service ground, a parcel of its own), the sun ruling out every seat under its hours; a bed that fits its sun only
  smaller takes the size knob's attested low end (research buildings 400), never less than the sheet drew unless that
  low end is itself what fits. Each sheet's notes, program checks and kinds stay true, and each sheet passes a `building-review`, ledgered. A shrine garden's place stays within the sheet's
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
- **SC-002** (FR-003, FR-004): the check fails the negative fixture, naming its hours and its shade makers by kind, with
  the wood among them; it fails a bed shaded by trees alone; it passes the county example; and its tests reach the
  gate's coverage floor.
- **SC-003** (FR-005, FR-007): every hand-drawn building sheet with a kitchen garden passes `garden_sun` as a sun bed; the re-seated sheets
  pass `building-review`; `make done` is green.
- **SC-004** (FR-006): the program and the operative docs name the sun rule where they say where a garden goes.

## Assumptions

- The binding season and sun are the record's (38 degrees north, the autumn shoulder month), as the scripted maps' rules
  use them.
- The scripted maps keep their own placement rules; this feature adds nothing to the placer.

## Decisions Recorded

- **The seats (accurate as seats, a guess that the sun chooses)**: research buildings 405. At Ochiba, Hayakawa and
  Ubame the west and the rear are shaded by the kitchen and the residence, so each bed takes the south court beside the
  formal garden, cut from it; the Hoshigaoka shrine's bed moved to the open ground south-west of the hall (research
  homesteads 044).
- **Ubame's bed at the size knob's low end (accurate)**: the only open ground in its walls with a sun bed's hours (research homesteads 044) holds about
  `1,065 sq ft` (observed 2026-09-28; method: the bed's rect 102 x 94 px at 3 px a foot), the soup-greens plot of research buildings 400; the rear strip held about `2,100 sq ft` (observed 2026-09-28; method: its rect 430 x 44 px at 3 px a foot). Hayakawa keeps the
  `780 sq ft` it drew (observed 2026-09-28; method: its rect 88 x 80 px at 3 px a foot, as the rear strip's 160 x 44): its sunny corner holds no more without moving the roji, and that is recorded in its notes.
- **A found defect fixed (constitution XIV)**: the caption placer weighed ground painted after a caption, inside the
  ground the caption names, as open, and seated Hayakawa's garden name under the new bed; ground painted over a caption
  now weighs as a caption does (`tools/seat_label.py`, with its unit test). No other sheet's seats moved.

## Review history

**Round 1** (spec-fidelity, MODE 2, 2026-09-28): CHANGES REQUIRED, three items. The check itself (hours of sun from
shadows cast by what stands up, against a threshold from the record, reported with its shade makers), the record behind
it and the re-seating of the four failing gardens carry the request and the GM's answer; FR-006 and the half-shade knob
(FR-002, research-driven, sun by default) serve it. Nothing unrequested was found.

1. **FR-003 scope is keyed to the tool, not to the GM's class.** The GM asked for a check "that gets run on hand-drawn
   diagrams that have gardens"; FR-003 says "every hand-drawn sheet the audit reads", which silently leaves out the
   frozen hand-authored Mode B maps in legacy-hand-authored-pool/, several of which draw kitchen gardens (the Hoshigaoka
   village, the Ubame town, Minami). Being frozen is existing behavior the GM did not ask to preserve. FR-003 should
   name the class as the GM did - every hand-drawn diagram with a kitchen garden, the legacy hand-authored maps
   included - and FR-005/SC-003 should say what happens to a failure there: the GM's "move them all" answered for the
   four sheets measured, so a legacy map that fails is measured, reported with its hours, and put to the GM as the same
   fix-scope question (not moved unasked, not exempted). If the session holds that those maps are not what "hand-drawn
   diagrams" means, that is an exception to put to the GM verbatim, not a scope line in an FR.
2. **Nothing proves the trees are counted.** The GM's question is clearance "from the trees", but the shrine sheet as
   drawn fails on the hall alone (request.md: the hall shades the bed until about 10, `2.5 h` lit in all), so a check that
   ignored the wood would pass FR-004 and SC-002 as written. FR-003 should state which drawn kinds count as a building,
   a wall and a tree - a tree including a wood or grove drawn as an area (shrine grove, garden pines, sacred tree), and
   a building every roofed kind (gatehouse, bell tower, stage, granary) - and FR-004 should add a test that a bed shaded
   by trees alone fails, and require the negative fixture's report to name the wood among its shade makers.
3. **FR-005 leaves the rejected fix open.** The GM was offered "declare half-shade beds" and chose "Move them all". As
   written, FR-002's knob would let a re-seated sheet pass by declaring its bed half-shade. FR-005 should say the four
   re-seated gardens pass as sun beds (the default) with no half-shade declaration. FR-002 itself stands.

**Round 2** (spec-fidelity-verify, MODE 3, 2026-09-28): CHANGES REQUIRED, one item. Item 1 RESOLVED - the scope was
put to the GM, who answered "Sheets only (Recommended)" (request.md), and FR-003 now names hand-drawn building sheets
with that answer cited, so no legacy-map failure path is owed. Item 3 RESOLVED - FR-005 requires the four re-seated
gardens to pass as ordinary sun beds, none declared half-shade; SC-003 says "as a sun bed". Item 2 PARTLY RESOLVED -
FR-003 now names what stands up by kind (every roofed kind, every wall, every tree including a wood's or grove's crowns
and a sacred tree, with what does not stand up listed with why), and FR-004 adds the trees-only test and requires the
fixture's report to name the wood; the list of non-casters serves the request. But SC-002, which round 1 named alongside
FR-004 as passing a tree-blind check, is unchanged.

1. **SC-002 still passes a check that ignores trees.** SC-002 (FR-003, FR-004) reads "the check fails the negative
   fixture naming its hours and shade makers" - met by a check that names only the hall. It should read: the check
   fails the negative fixture naming its hours and its shade makers by kind, the wood among them; fails a bed shaded by
   trees alone; and passes the county example; its tests reach the gate's coverage floor.

**Round 3** (spec-fidelity-verify, MODE 3, 2026-09-28): first NOT-REVIEWABLE (three unlabeled figures, labeled), then
CHANGES REQUIRED, one item: FR-005 quoted a GM answer that request.md did not record. request.md now records the
question, its three options and the answer verbatim.

**Round 4** (spec-fidelity-verify, MODE 3, 2026-09-28): FAITHFUL. The answer checked against the session transcript; the
west-side preference was the session's own wording in an option the GM picked, so dropping it sets aside nothing the GM
said.
