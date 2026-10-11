# Feature Specification: One view of the sheet for the program example's captions (compound.py seats through the hand-sheet placer)

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=340-program-example-captions-hand-sheet-placer`)

**Created**: 2026-10-08 (filed by feature 330); specified 2026-10-11

**Status**: Done (2026-10-11) - every task ticked (T01-T04); the program example's captions seated by the hand-sheet placer's one view: 11 of 45 seated apart before, 10 of them from the entry's three sources; 3 apart after, none from the three (m:caption-disagreements, m:caption-disagreements-after); building-review PASS

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

The GM sees the program example's captions read by one view with the hand sheets wherever the entry's three sources made
them differ: one classification of the drawn sheet, one reading of what a caption names, one measure of its width. What
still differs for another reason (the draft's strict seating, the placers' order, clearance or repair) is reported with that
cause.

**Independent Test**: `harness.py` - the draft's captions against `hand_sheet.seat` on the same declared draft: the
disagreements the three sources explain, N before (each attributed), 0 after; every remaining one listed with its own cause.

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
  `hand_sheet.seat`, attribute each difference to the obstacle view, the subject or the character width by toggling each, and
  report which disagreements each of the entry's two fixes removes (the composer indexing with `hand_sheet.classify`; the
  hand-sheet placer taking the composer's subjects). A difference none of the three explains is reported with its own cause
  (strictness, order, clearance, repair) - the entry's reasons were read from the code, not measured.
- **FR-003**: the seating MUST then switch to whichever of the entry's two fixes the FR-002 measurement supports - one of them,
  or a mix per source - so the three sources no longer differ; the fix taken is named and recorded with its measurement. The
  placers' other differences (order, clearance, repair) are not unified by this feature.
- **FR-004**: the strict rule (feature 287) MUST hold under the one view: a seat touching ink the caption does not name is not
  free; the foot grows up to `CAPTION_GROWTHS` steps; then the program is refused with today's message.
- **FR-005**: the example's generation MUST stay inside its `GEN_TIME_BUDGETS` entry; any performance band the change crosses is
  explained and audited (constitution VI).

## Success Criteria

- **SC-001** (FR-001, FR-002, FR-003): disagreements the three sources explain between the draft's seats and the hand-sheet
  placer's on the declared draft: N -> 0 (harness), each attributed; every remaining disagreement reported with its cause and not
  counted in N.
- **SC-002** (FR-004): the refusal test passes unchanged, and no seated caption overlaps ink outside its subject.
- **SC-003** (FR-005): the example's gen time within its budget; `make perf-report` band recorded.

## Occasions (expected)

- layout-revised: county-magistracy-example - its captions re-seated by the one view (`building-review`).

## Review history

- 2026-10-11, round 1: CHANGES REQUIRED - FR-003 chose the fix before measuring (now the measured one, per source); N -> 0
  could not hold under FR-004 (now only the three sources' disagreements, the rest reported with their cause). FR-004 within.
- 2026-10-11, round 2 (spec-fidelity-verify): FAITHFUL - both items resolved.
