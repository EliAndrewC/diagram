# Feature 279 - the shape of a village shrine's grove

**Feature**: 279-shrine-grove-shape | **Created**: 2026-09-28 | **Status**: Draft
**Input**: the GM's request, verbatim in [`request.md`](request.md).

## Summary

The Hoshigaoka village map draws its shrine's grove as a rectangle of trees, 137 by 215 ft (observed 2026-09-28; method: the manifest's `village_groves` record of role
`shrine`, w 68.3 by h 107.7 map px at the map's 2 ft to the px, read from `hoshigaoka.json`), filling the
precinct box from the shrine's well to the outermost arch. The GM asked whether that was a research finding -
the rectangle, and a shrine wooded on every side. It was neither: research 124 found the precinct's size and
that the buildings cover little of it, the GM ruled (2026-09-27) to draw a grove, and the crowns were thrown
into the precinct box; no source was read on the grove's outline or on which sides of the hall it stands, and
the record never labeled the shape.

The GM asked for the research pass, the findings recorded, and the updates made - the hand-drawn map included,
because it "looks very visually wrong" - and stressed knowing "what tunable knobs we will have for villages when
we eventually go to start scripting them".

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The research is on the record (Priority: P1)

A reader who opens the shrine grove's modal, or the religion-and-death page, finds what a village shrine's wood
looked like from above: on which sides of the hall it stands, what its outline was, and how that varied - each
with a quoted footnote or an absence note, each rule labeled.

**Independent test**: the new question is on the page with its footnotes; every source it cites is registered,
read (source-reader), quoted verbatim (quote-check), judged applicable (source-applicability) and checked for
its reader (record-format).

**Acceptance**:
1. **Given** the religion-and-death page, **When** a reader looks for the grove's shape, **Then** a question
   answers which sides of the hall the wood stands on, what outline it has, and which forms are attested.
2. **Given** research 124's decision, **When** it describes the grove, **Then** it no longer says or implies
   the wood fills the precinct on every side, and it points at the new question.

### User Story 2 - The map and the sheet show the grove as it was (Priority: P1)

The GM, looking at Hoshigaoka, sees the shrine in a wood of the researched form, with an outline no one would
take for a surveyed rectangle.

**Independent test**: on the village map and on the shrine sheet, the grove's trees stand in the form the
research and the map's terrain give; no straight run of crown edges traces a side of the old precinct box.

**Acceptance**:
1. **Given** the Hoshigaoka map, **When** the grove is drawn, **Then** it stands in a researched form (US3)
   chosen for the shrine's ground, with an irregular outline.
2. **Given** the shrine sheet, **When** it is compared with the map, **Then** it draws the same trees, one for
   one (the GM's rule of 2026-09-20 that a sheet shows what its map shows; feature 257's `matches_map`).

### User Story 3 - The knobs a scripted village will roll (Priority: P1)

A session scripting villages later finds, in the program and the operative docs, the grove's knobs: each form
the research supports, what it depends on (the ground, the seed), and how it is drawn.

**Independent test**: the country-shrines program in `types.json` / `programs.md` names the knob and its forms
with their labels; the village conversion's owed list (`future-work/farming-communities.md`, `migration-plan.md`
step 5) names it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The research record MUST gain, on the religion-and-death page beside research 124, a question on
  the shape of a village shrine's wood: which sides of the hall it stands on; its outline; the forms the sources
  attest and what each depends on (the ground's slope, flat paddy land, a hill); and how common each is where a
  source counts it. Each claim carries a quoted footnote or an absence note; each rule a label.
- **FR-002**: Research 124's decision paragraph MUST stop implying the wood fills the precinct on every side, and
  MUST point at FR-001's question for the grove's form and outline.
- **FR-003**: Every new source MUST be registered (what it is; why it applies and its limits) and pass
  source-reader, quote-check, source-applicability and record-format before its content reaches the map or a
  rule. A modern survey used for a rate states that it is modern and where it was taken.
- **FR-004**: Where the sources support more than one form of grove, the form MUST be a knob with per-settlement
  variance (constitution XII): the country-shrines program MUST declare it with its forms, what constrains the
  choice (the ground), and each form's label; a degree along a continuum (how far the wood reaches down the
  sides, how many trees) is calibrated liberty, not a knob.
- **FR-005**: The grove's outline MUST be drawn irregular, never ruled, and the choice labeled with its class
  (accurate, deviation, convention or guess) and its reason.
- **FR-006**: The frozen Hoshigaoka village map MUST be edited by hand - its drawing and its manifest together -
  to draw the grove in the form FR-004 gives for its shrine's ground, with FR-005's outline; the GM authorized
  this edit (2026-09-28, `request.md`). Nothing else on the map moves except what the grove's new extent frees
  or covers (the scrub scatter where the wood leaves or arrives), and the change is recorded in the map's notes.
- **FR-007**: The Hoshigaoka shrine sheet MUST be redrawn to match the map's grove tree for tree, and its notes,
  its kinds' write-ups (`shrine grove`) and its Map notes block updated to the new form.
- **FR-008**: The village conversion's owed list MUST name the grove knob (`future-work/farming-communities.md`;
  `migration-plan.md` step 5), so the scripted village rolls it.
- **FR-009**: The edited map MUST pass a `settlement-review` and the redrawn sheet a `building-review`, each
  ledgered; `make done` MUST be green.

### Edge Cases

- **The precinct is larger than the wood.** Research 124's precinct size stays: the precinct is the tax-exempt
  ground (jochi), and the wood is what stands on part of it. Where the form leaves the front open, the open
  front is still precinct.
- **Only one form is attested for ground like Hoshigaoka's.** Then that form is drawn and the knob is still
  declared for the forms other ground takes.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001-FR-003): The new question exists with at least one READ, quote-checked footnote per claim
  it rests on, or an absence note; all four checks have run on it and their findings are applied.
- **SC-002** (FR-005, FR-006, FR-007): On the map and the sheet, the grove's trees stand in the declared form;
  the outline, measured on the tree list, has no straight run - the bar `STRAIGHT_RUN`: no four consecutive
  hull-edge crowns lie within `2 ft` of one line (a named bar, not a measurement: about a third of the smallest
  crown's radius, so a run that tight reads as a ruled edge).
- **SC-003** (FR-006, FR-007): The sheet's trees match the map's one for one (the `matches_map` test stays green).
- **SC-004** (FR-004, FR-008): The program and the owed list name the knob, its forms and labels.
- **SC-005** (FR-009): the reviews are ledgered and `make done` is green.

## Assumptions

- The research is Japan-first; Chinese village woods are already on the record (vegetation 010-050) and are
  cited for comparison only where they bear on a shrine's grove.
- The sweep of scrub around the grove is redrawn only where the wood's new extent requires it.

## Decisions Recorded

(Filled as the research lands.)

## Review history

- First reading (spec-fidelity, MODE 2, 2026-09-28): NOT-REVIEWABLE - not a round; the substance was not read.
  Two figures with a unit stand in operative sections with no measurement key and no one-shot label (feature 239,
  spec-lint check 5): (1) the Summary's grove size, `137 by 215 ft`, a measurement of the frozen map - record it
  from the map's manifest with the command that reads it and cite the key, or label it with the date observed and
  the method; (2) SC-002's crown-to-line tolerance, "within 2 ft", a chosen bar rather than a measurement - state it
  as the bar it is (a backticked name, or a label saying why that tolerance) so check 5 does not read it as an
  unmeasured figure. Re-dispatch as a first reading once both carry their pointer or label.
