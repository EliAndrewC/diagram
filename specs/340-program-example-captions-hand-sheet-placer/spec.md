# Feature Specification: One view of the sheet for the program example's captions (compound.py seats through the hand-sheet placer)

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=340-program-example-captions-hand-sheet-placer`)

**Created**: 2026-10-08 (filed by feature 330); specified 2026-10-11

**Status**: Draft (specified 2026-10-11 from its filed form)

**Affects**: magistracy

**Input**: `request.md` - the GM, 2026-10-11: *"Please implement features 355, 339, 340, 341, and 342. You can do them in
whatever order makes sense. If some of them should be undled together that's fine, or you can do them sequentially, whatever
makes the most sense."* 340 is done on its own, after 335 (which carries 339, 341, 342): it is engine work on the generated
draft, not the hand sheets.

## The entry, as filed (the GM's words this feature is judged against)

- **The program example's captions and the hand-sheet placer (`labels.hand_sheet`, `seat_label` until feature 286) disagreed on 9** (feature 267, 2026-09-27: striking posts, residence, well, gatehouse, practice ground, both clerks, straw mats' seat and leader). `compound.py` seats through the one placer but with its own view: a caption's subject is one chosen shape (the rear alley, one seat, one mat) where the hand-sheet placer takes what the caption declares; it counts invisible stand-ins for tubs and stones and blocks the roofed court only after the court's own captions; and it measures every caption at the standard's character width where the hand-sheet placer measures bold, capitals and spacing (feature 267's rules). The reasons are read from the code, not measured. The fix is one view: `compound.py` builds its obstacle index with `hand_sheet.classify` over the sheet it is drawing, or `hand_sheet` gains the composer's subjects; measure first which disagreements each removes.

## What today's draft allows (measured 2026-10-11)

The entry's measurement cannot be run on today's draft as written: the composed sheet carries no hand-sheet declarations - its
captions have no `data-names` and do not stand alone in the tagged group they name - so `hand_sheet.placed` refuses it ("caption
'garden' (garden) names nothing"). Feature 267's nine were read from the code, as the entry says. So the measurement is made in
three steps: the draft first emits its captions as declarations (additive: nothing moves); then, on that one declared draft,
the composer's seats are compared with the hand-sheet placer's, each difference attributed by toggling the three sources the
entry names (the obstacle view, the subject, the character width); then the seating is switched to the one view.

## User Scenarios & Testing

### User Story 1 - The draft and the hand sheets are read by one view (Priority: P1)

The GM sees the program example's captions seated exactly as the hand-sheet placer seats the same declarations: one
classification of the drawn sheet, one reading of what a caption names, one measure of its width.

**Independent Test**: `harness.py` - the draft's captions against `hand_sheet.seat` on the same declared draft: N disagreements
before (each attributed), 0 after.

### User Story 2 - The draft's strictness survives (Priority: P1)

Feature 287 (L15): no caption of a composed draft lies on a feature it does not name; a draft whose caption has no clean seat
grows its foot, then refuses the program by name. The one view keeps that rule - judged against the ink a caption does NOT
name, never against its own parts.

**Independent Test**: the existing refusal test (`tests/test_compound.py`, the text "has no seat clear of every feature ...
change the program") passes unchanged; every seated caption of the example lies on no obstacle outside its own subject.

## Requirements

- **FR-001**: the composed draft MUST declare each caption the way a hand sheet does (`data-id` on the shapes it names,
  `data-names` on the caption, or the caption alone in the tagged group it names), so `hand_sheet` can read it.
- **FR-002**: a harness MUST measure, on that declared draft, every caption whose seat differs between `compound.py` and
  `hand_sheet.seat`, and attribute each difference to the obstacle view, the subject or the character width by toggling each.
- **FR-003**: `compound.py` MUST then seat its captions through the hand-sheet placer's one view (its classification, its reading
  of the declared subject, its width measure), with no second obstacle index of its own; the entry's two sketches are measured
  beside it in the harness, and the one taken is recorded with its measurement.
- **FR-004**: the strict rule (feature 287) MUST hold under the one view: a seat touching ink the caption does not name is not
  free; the foot grows up to `CAPTION_GROWTHS` steps; then the program is refused with today's message.
- **FR-005**: the example's generation MUST stay inside its `GEN_TIME_BUDGETS` entry; any performance band the change crosses is
  explained and audited (constitution VI).

## Success Criteria

- **SC-001** (FR-001, FR-002, FR-003): disagreements between the draft's seats and the hand-sheet placer's on the declared draft:
  N -> 0 (harness), each of the N attributed.
- **SC-002** (FR-004): the refusal test passes unchanged, and no seated caption overlaps ink outside its subject.
- **SC-003** (FR-005): the example's gen time within its budget; `make perf-report` band recorded.

## Occasions (expected)

- layout-revised: county-magistracy-example - its captions re-seated by the one view (`building-review`).

## Review history

- (spec-fidelity rounds are recorded here)
