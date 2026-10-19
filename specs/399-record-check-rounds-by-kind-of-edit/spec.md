# Feature 399: Record-check rounds by kind of edit - another check's small fix owes no new pass; a fix that keeps failing reaches the arbiter

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=399-record-check-rounds-by-kind-of-edit`)

**Created**: 2026-10-19

**Status**: Filed

**Approved**: the GM, 2026-10-19, "Let's go with the first option: a kind-C pass should be skipped wen the only change is another check's few word-fix outside the quotation and its claim."

**Affects**: tooling, review process, research record

**Input**: `request.md` - the three kinds of edit, the GM's choice and his words, verbatim.

## Why

Feature 391 row 5 (the round arbiter's tooling fix at hour `390-money-foundation-research@2`): quote-check ran six
passes on question 0251 across two sessions and the round cap never fired, because any change to the checked words starts
the count again (feature 374 FR-005). The arbiter asked to count every pass; that was declined, and the GM overturned the
decline into this feature with a narrower form. The passes, by the kind of edit before each (`specs/390-money-foundation-research/briefs/w1-checks.md`):

- **Kind A - new material** (new footnotes, new quoted passages: session 3's MAFF caption, the Bu nongshu passages, the
  Okayasu footnote, the 1700 deed's term). A fresh round 1 is right. **No change** (the GM: "kind A needs no tweak").
- **Kind B - fixes of the check's own findings** (a PARTIAL fixed by splitting or extending a quoted passage). One
  confirming pass is right; today each fix restarts the count, so a fix that keeps failing never reaches the arbiter.
- **Kind C - another check's few-word fix** (translation-check's 去辰 correction, record-format's glossary word) that moved a
  footnote outside its quotation and its claim, so the quote-check came due again; the two passes it bought had nothing to find.

## What it is

1. **Kind C is not owed.** A unit whose only change since its check's last answer is another check's applied fix that
   leaves the quotation and the claim it supports unchanged is not owed that check again. (Today `record_owed.settle`
   spares only a round's OWN applied EDIT blocks.)
2. **Kind B counts.** A change that edits an existing footnote's quotation or claim - fixing what a round found - does not
   restart the round count; the rounds on that unit keep counting, so a third pass reaches the round cap and the round
   arbiter judges the loop.
3. **Kind A is unchanged.** A new footnote or a new quoted passage restarts the count as today (feature 374 FR-005), for
   that footnote.

## Requirements

- **FR-001 (kind C)**: the owed-units script (`make record-owed`) does not owe a check on a unit whose change since that
  check's last answer touches neither the quoted passage nor the claim the footnote supports, when the change came from
  another check's applied fix; the record says which fix settled it.
- **FR-002 (kind B)**: the round counter does not rebase on a change to an existing footnote's quotation or claim; the
  cap fires on the third round on that unit, and the arbiter bundle shows each round's finding and the fix that followed.
- **FR-003 (kind A)**: a new footnote or new quoted passage starts its own count, as now.
- **FR-004**: the counts hold across sessions of one feature (0251's passes ran in two sessions of feature 390).
- **FR-005**: each rule is a test proved red on today's code first (the 0251 sequence replayed is the model case).

## Edge cases

- A change that touches both a quotation and another footnote's wording owes the check on the touched quotation only.
- A hand edit (not a check's applied fix) outside the quotation still owes the check, as today: only an applied fix is
  known to be cosmetic to the quote-check.

## Success criteria

- **SC-001**: replaying 0251's session-3 sequence, the two final quote-check passes (after the 去辰 and glossary fixes) are not owed.
- **SC-002**: a seeded loop - a PARTIAL fixed and re-found three times - trips the round cap and owes the arbiter's ruling.
- **SC-003**: a new footnote added after round 2 is owed a check at round 1.
