# Feature 399: Record-check rounds by kind of edit - another check's small fix owes no new quote-check; a fix that keeps failing reaches the arbiter

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=399-record-check-rounds-by-kind-of-edit`)

**Created**: 2026-10-19

**Status**: In progress

**Approved**: the GM, 2026-10-19, "Let's go with the first option: a kind-C pass should be skipped wen the only change is another check's few word-fix outside the quotation and its claim.  An then also, it sounds like we need a kind-B tweak, where if a fix keeps failed then that should be a loop the arbitur should judge.  It sounds like kind A needs no tweak."

**Affects**: tooling, review process, research record

**Input**: `request.md` - the three kinds of edit, the GM's choice and his words, verbatim.

## Why

Feature 391 row 5 (the round arbiter's tooling fix at hour `390-money-foundation-research@2`): quote-check ran six
passes on question 0251 in feature 390 and the round cap never fired. The arbiter asked to count every pass; that was
declined, and the GM overturned the decline into this feature in a narrower form. The passes, by the kind of edit before
each (`specs/390-money-foundation-research/briefs/w1-checks.md`, and the word diffs of commits `b499788d9` and `051bde09e`):

- **Kind A - new material**: new footnotes and new quoted passages (session 3's MAFF caption, the Bu nongshu passages, the
  Okayasu footnote, the 1700 deed's term). A fresh check is right. The GM: "It sounds like kind A needs no tweak."
- **Kind B - fixes of the check's own findings**: a PARTIAL fixed by splitting or extending a quoted passage. One confirming
  pass is right; a fix that keeps failing is a loop. The GM: "if a fix keeps failed then that should be a loop the arbitur
  should judge" (dictation: failing, arbiter).
- **Kind C - another check's few-word fix**: the last two passes were owed only by other checks' fixes. One of them, the
  Okayasu footnote's locator ("the collection's back cover" -> "the back cover of document 102", after source-reader's
  CONTRADICTED attribution), lies outside the quotation and its claim. The other, translation-check's 去辰 correction ("last
  year" -> "last year, the dragon year [1700]"), lies INSIDE the translated quotation, so the GM's rule leaves that pass owed.

Measured in the code: every pass ran from the one clone, so the per-clone round state did not reset between sessions. The
counter (`scripts/hooks/lib/hm_checks.py`) counts rounds per check and question, and leaves a dispatch uncounted when its
unread sentences are not the check's own EDIT text (`first_look` - a hand fix of the check's own PARTIAL qualifies) or when
`origin/main` moved since the unit's last counted round (`new_cause` - any landing by any session). Both let a fix that
keeps failing slip under the cap.

## What it is

1. **Kind C is not owed.** A quote-check unit changed only by a fix of ANOTHER check's finding settles with its standing
   answer when its quotation and its claim are unchanged. The quotation is the note's link and its quoted passages (the
   stored originals and each quoted English rendering); the claim is the sentences of the blocks that carry the note's mark
   (`record_units.claims_of`). The fix reaches the rule two ways: another check's EDIT blocks applied by `make apply-edits`
   (settled there, automatically), or a fix the session made by hand for a check that words no EDIT blocks - source-reader,
   whose CONTRADICTED attribution gave the Okayasu fix - DECLARED when quote-check's answer is recorded, naming the check
   and its finding; the tool verifies the quotation and claim are unchanged and refuses otherwise. A change matching no fix
   of another check's finding still owes the unit, as today.
   "Few-word" is read as describing the case, not as a bound: the operative test is the GM's "outside the quotation and its
   claim", because those are all quote-check judges (`quote-check.md`: READABLE, VERBATIM, SUPPORTS), and a fix of any
   length outside them gives it nothing new to judge. This reading goes to the GM in the report.
2. **Kind B reaches the arbiter.** A footnote that quote-check FLAGGED (any verdict but READABLE, VERBATIM and SUPPORTS) in
   two rounds of one feature, with the footnote changed between them (a fix was tried), cannot be dispatched to quote-check
   a third time after a further change until the round arbiter rules: the dispatch trips the unit's round trigger, naming the
   footnote and its two findings. A pass on that footnote clears its count. This holds whatever reset the per-question
   counter (a hand fix, a landing on main).
3. **Kind A is unchanged.** A new footnote has no findings to repeat, and a footnote that passed starts clean, so neither
   is held.

## Requirements

- **FR-001 (kind C)**: (a) `make apply-edits` on a reply of any record check other than quote-check settles each
  quote-check unit those blocks alone moved, when its answer stands at the words before them (or it was not owed before
  them) and its quotation and claim are the same after them; it prints each settled unit. (b) `make record-checked
  CHECK=quote-check` with `FIXED_BY="<check>: <its finding>"` on named notes answers each one whose quotation and claim
  are those of an answer quote-check already gave (or of main, where it was not owed), recording the declared fix in the
  answer; a note whose quotation or claim changed is refused, named. A unit whose quotation or claim changed stays owed.
- **FR-002 (kind B)**: the check guard records, for each quote-check reply, the footnotes it flagged (outside its `OUTSIDE
  THE CHANGE` section) and the ones it passed, with the footnote's fingerprint as that round read it; a footnote flagged in
  two rounds, changed between them, and dispatched again changed once more trips `round:quote-check|q:NNNN@N` (a round
  number no ruling of the unit has used), refusing the dispatch until the arbiter rules, its detail naming the footnote and
  its two findings. A `continue` ruling lets one more round through, as the round cap's own `continue` does; a flag in that
  round after another fix trips again.
- **FR-003 (kind A)**: a new footnote, and a footnote whose last round passed it, are never held by FR-002.
- **FR-004**: FR-002's count holds across sessions of one feature in the clone, and across landings on main.
- **FR-005**: each rule has a test that is red on the code before this feature.
- **FR-006 (scope)**: a footnote flagged in two rounds with NO change between them (a canon note read NOT-READABLE every
  round, nothing tried) is no failed fix and is not held; the other record checks' rounds are unchanged.

## Edge cases

- A reply whose footnote lines name no note key the bundle carries flags nothing (the count never guesses).
- One apply-edits run that changes one note's quotation and another note's locator settles only the second.
- A footnote flagged, then removed from the page, carries no count.

## Success criteria

- **SC-001** (FR-001): replaying the `-4` locator change as it was made - by hand, after source-reader's CONTRADICTED finding - and
  declaring it (`FIXED_BY="source-reader: ..."`) answers `quote-check:0251#miyashiro-kumehara-1698-4`; the same change
  as another check's applied EDIT block settles it at `make apply-edits`; the 去辰 change, either way, leaves
  `quote-check:0251#miyashiro-kumehara-1698` owed (refused, named, when declared).
- **SC-002** (FR-002, FR-004, FR-005, FR-006): a seeded loop - one footnote PARTIAL in two quote-check replies, changed before each, then a third dispatch
  on it changed again - is refused with the round trigger, also when `origin/main` moved between the rounds; on the code
  before this feature it is let through. The same two flags with no change between them (NOT-READABLE on a canon note) are
  let through.
- **SC-003** (FR-003): a new footnote added after two flagged rounds on another footnote is dispatched without a hold.
