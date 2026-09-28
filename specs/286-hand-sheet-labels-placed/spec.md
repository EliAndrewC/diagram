# Feature 286 - a hand-drawn sheet's labels placed by the one placer

**Feature**: 286-hand-sheet-labels-placed | **Created**: 2026-09-28 | **Status**: Draft
**Input**: the GM's request and answer, verbatim in [`request.md`](request.md).

## Summary

The hand-drawn Mode A sheets (the magistracies, the country shrine) are drawn by hand for variation, but their labels
should be placed by the same code that labels the generated maps - the one caption placer of feature 266
(`l7r/diagram/labels/`, the cartographic standard) - as a step of the pipeline that renders a sheet, not by hand and
not by a tool someone remembers to run. Placement becomes a function of the drawing alone. And since the labels are
placed by an automated process, nothing checks where they stand: the placer's unit tests are what guarantee it (the
GM: "There is no point in having an automated check run against an automated process").

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Labels placed, not drawn (Priority: P1)

A session draws or edits a hand sheet's buildings and grounds and names each thing's caption; it never places a
caption. The sheet's picture and interactive page show every caption where the placer put it.

**Independent test**: move every caption's text on a sheet to an arbitrary point (or strip its coordinates), render
the sheet, and get byte-identical placed labels to rendering it unmoved.

### User Story 2 - The GM's blind test (Priority: P1)

The GM saw a label that "really just does not look well placed" and did not say which. After this feature the GM looks
at the maps and judges whether that label now stands well - the measure of whether the class of issue is fixed.

### User Story 3 - No checks against the placer (Priority: P1)

The checks that judge where a hand sheet's captions stand are gone; the placer's own unit tests cover what they
covered.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every caption on every hand-drawn sheet MUST be placed by the one placer the generated maps use
  (`l7r/diagram/labels/place`), as a step of the pipeline that renders the sheet - its picture and its interactive
  page - with no hand placement and no separate tool to run.
- **FR-002**: A caption's declaration on a sheet MUST carry its text and its subject - what it names, one of several
  like parts included - and nothing that decides where it stands: no coordinates that count, no inside-or-beside. The
  placer decides where, inside its subject or beside it, from the drawing. A sheet's placed labels MUST depend only on
  the drawing and those declarations, never on where a caption's text was left: the hand-seat exception (a caption's
  hand position kept where the placer found no free seat) and every reading of a caption's position (to choose its
  subject, or inside against beside) are removed.
- **FR-003**: Where the placer finds no free seat, its fallback MUST place the caption at least as well as the hand
  seats it replaces - the reason the hand-seat exception existed - improved in the placer itself, with unit tests.
- **FR-004**: Every automated check of caption placement on hand sheets MUST be removed, including: the caption-seat gate test and its
  ledger, the `make seat-label` report, the `building-review` contract's caption-seat step, and the sheet audit's
  checks that judge caption placement (labels overlapping, labels on dark ink, labels buried under later ink, group
  labels adrift). Correctness is carried by the
  placer's unit tests. Checks of things that are still drawn by hand (a glyph buried under later ink) stay.
- **FR-005**: Everything that reads a sheet's captions - the program and size checks that pair a label with the
  structure it names, the review agents that look at a sheet, the interactive page - MUST read the placed captions or
  the declared tags, never the hand coordinates.
- **FR-006**: The operative docs (the skill's Mode A usage, `buildings.md`, the review agents' contracts) MUST say that
  a sheet's labels are placed by the pipeline and how a sheet declares a caption; the review contracts MUST no longer
  judge or ask to move a caption's position. What a label says - its wording, spelling, precision, whether it is
  redundant - is not placement and stays reviewed.

### Edge Cases

- **A caption naming one of several like parts** (two clerks' seats in one group): the declaration says which part.
- **A caption with no free seat anywhere**: placed by the improved fallback, never dropped (feature 266's rule).
- **A sheet a gen composes** (the county example, `emit_svg`): already placed by the placer at generation; unchanged.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002): on every hand sheet, rendering with the captions' coordinates scrambled gives the same
  placed labels as rendering unchanged; the render path calls the one placer.
- **SC-002** (FR-003): the placer's fallback is unit-tested on the crowded cases the hand seats covered; and, as a
  one-time acceptance measurement recorded in the feature's `measurements.json` (not a standing test), no caption on a
  hand sheet covers more ink than its hand seat did when the feature began.
- **SC-003** (FR-004): the listed checks and the ledger are gone; `make done` is green.
- **SC-004** (FR-005, FR-006): no reader of a hand sheet's captions uses their hand coordinates; the docs say so.
- **SC-005** (spec-wide): the blind test of User Story 2 - the GM judges the label they saw.

## Assumptions

- The generated maps' labeling is unchanged except where the placer's fallback improves for everyone (FR-003); a
  change there is measured on the scripted maps too.
- The sheets stay hand-drawn in every other respect.

## Decisions Recorded

- **Scope: the hand-drawn Mode A sheets** (the three magistracies and the Hoshigaoka country shrine), not the
  hand-authored Mode B exhibits in `legacy-hand-authored-pool/`, whose captions are also hand-seated (feature 266 D8).
  Those maps are FROZEN (dev/pool.md: never regenerated; the fix for a frozen map is conversion to scripted generation,
  which already brings the one placer). Put to a MODE 1 fidelity check in round 2. The risk, said to the GM at
  hand-back: if the label the GM saw is on a legacy map, this feature does not reach it.
- **The measurement that shaped FR-003** (observed 2026-09-28; method: the hand-seat exception instrumented over
  every hand sheet): on 7 captions the hand seat covers no ink while the placer's best covers some (Hayakawa's
  RESIDENCE, forecourt, HEARING COURT, guardroom and the Ebisu altar note; Ubame's two Fox-border notes) and on an eighth
  the hand seat covers less (Hayakawa's bath): the placer's search misses free seats a person found.

## Review history

**Round 1** (spec-fidelity, MODE 2, 2026-09-28): CHANGES REQUIRED, four items - FR-002 let a sheet declare
inside-or-beside and kept inference from the drawing (a declaration is now text and subject only; the placer decides);
FR-004 missed the building-review contract's caption-seat step and read "MUST remain" (now named, "MUST NOT remain");
SC-002 could have become a standing check (now a one-time measurement); the scope narrowed to Mode A unrecorded (now a
decision, put to MODE 1).

**Round 2** (spec-fidelity-verify, MODE 3 + MODE 1, 2026-09-28): CHANGES REQUIRED, one item - FR-004's opening clause
still read "MUST remain" (now "Every automated check ... MUST be removed, including:"). The scope exception (the frozen
legacy Mode B exhibits) ruled LEGITIMATE: the request is about maps still drawn by hand; frozen exhibits are never
re-gated or re-rendered, and editing them would be the retrofit the GM's 2026-08-16 ruling forbids. The GM is to be
told at hand-back that the 18 legacy exhibits are untouched.

**Round 3** (spec-fidelity-verify, MODE 3, 2026-09-28): FAITHFUL. The county example and the Ochiba round-trip sheet
are composed by `compound.py` (`emit_svg`), which already places their captions at generation (the Edge Cases).
