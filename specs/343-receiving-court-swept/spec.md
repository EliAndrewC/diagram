# Feature 343: Is the receiving court "swept"?

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-08 (filed); specified 2026-10-10
**Status**: In progress - spec under review

**Affects**: magistracy, research record

**Input**: `request.md` (the entry as filed, and the GM's word to take it up, 2026-10-10)

## Why

The receiving (border) court's modal says the plan draws it "as a swept garden". Feature 280 struck "swept earth" from the
practice ground because a swept precinct is recorded only in modern custom (0224). The entry asks whether a receiving
court's - or any gate-to-entrance court's - surface is attested swept or raked before modern times, and for the modal to
be reworded if it is not.

**The research pass** (2026-10-10, an agent, read-only; `research.md` R1): silent. No premodern source read attests the
ground between a residence's or an office's gate and its formal entrance as swept, raked, graveled or sanded, nor as bare
earth. What there is:
- the 1869 Joge drawing shows that ground open, with no surface;
- a Qing yamen's forecourt is planted with junipers;
- the hearing court's white sand or gravel concerns the hearing court, not the approach;
- Morse's "well swept" yards are 1880s gardens;
- one loosely dated drawing, Morse's reproduction of a Sakai garden plan ("nearly two hundred years ago" from 1886), shows a
  stone path through a second gateway to the genkan inside a garden with lanterns: a garden approach, only loosely dated,
  not a receiving court.

## Requirements

- **FR-001 - The finding recorded.** `research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html`
  states, with an absence note naming what was searched, that no source read attests the ground before a formal entrance
  as swept, raked, graveled, sanded or bare earth before modern times. It names Morse's Sakai drawing (a stone path to
  the genkan through a garden, loosely dated) and why it is not counted as a court's surface. It says, as 0224 reads, that
  a precinct's swept surface is a guess there and that grave and shrine cleaning are recorded only as modern custom. The
  sentence that "the one drawing" of that ground (Joge's) shows it open is brought into line with the two drawings now
  known.
- **FR-002 - The modal reworded.** `border-court.md` no longer calls the court "swept". Its Depiction says what the sheet
  draws (a garden-stippled court with a stone lantern). Its Guesses keep the garden as a guess, and say that no source
  attests the court's ground swept, raked, graveled, sanded or bare before modern times. Their "the one drawing found shows that
  ground open" is brought into line with Morse's Sakai drawing (a garden approach, loosely dated).
- **FR-003 - Its checks.** The record checks the change owes (`make record-owed`) and the modal checks (`modal-form`,
  `modal-research`, `modal-depiction`) are run and answered.
- **FR-004 - The implementation check** (feature 378): `make impl-check F=343` reports nothing missing at close.
- **FR-005 - No map change.** No drawn element of the sheet changes: the drawing is the modal's subject, and the court
  stays a guessed garden. The sheet's source comments that still say "swept" (`ubame-magistracy.svg`) are corrected, as
  constitution XIV asks of a defect found.

## Success Criteria

- **SC-001** (FR-001, FR-002): the record states the silence with its search, and the modal no longer says "swept".
- **SC-002** (FR-003): `make record-owed` and the modal checks are answered.
- **SC-003** (FR-004): `make impl-check F=343` reports nothing missing.
- **SC-004** (FR-005): no drawn element of any sheet changes; no source comment of the ubame sheet says "swept".

## Decisions Recorded

- **D1 - The silence goes on 0104**, the question of the gate-to-entrance approach, because 0110 (the border post) defers to
  it for the ground a guest crosses.

## The entry, as filed

The practice ground's "swept earth" was reworded to open earth in feature 280 (M66 found the swept precinct recorded only
in modern custom). The receiving court's modal (`l7r/diagram/interactive/assets/modals/sheet/border-court.md`) still reads
"The plan draws the border court as a swept garden"; research 0224's drawing page finds swept ground at shrines and graves
recorded only in modern custom. Owed: a research pass on whether a receiving court's surface is attested swept or raked
before modern times, and the modal reworded if not.

**Implementation check** (feature 378): owed at its close - each question whose findings this feature changes is cited by a checked `Research:` claim of the code that decides it, or recorded in `implementation-check.md` as implemented nowhere; `make impl-check F=343` says what is owed. The code is fixed only where this spec asks.


## Review history
- spec-fidelity, Mode 2, round 1 (2026-10-10): CHANGES REQUIRED, wording. Applied: the silence is limited to swept, raked,
  graveled, sanded or bare earth; Morse's Sakai drawing is named with its loose date and why it is not counted; "the one
  drawing" sentences follow; 0224 is quoted as it reads; FR-005/SC-004 allow correcting the sheet's "swept" comments.
- spec-fidelity-verify, round 2 (2026-10-10): CHANGES REQUIRED, one wording: the Why bullet on Morse's Sakai drawing
  said "not dated" and named an owner no source gives. Applied, with FR-002's list matching FR-001's.

