# Implementation Plan: Record-check rounds by kind of edit

**Branch**: none (main, in the clone) | **Date**: 2026-10-19 | **Spec**: `spec.md`

## Summary

Kind C: `apply_edits.Round` also fingerprints the quote-check notes of the questions a reply's blocks touch, and after the
blocks settles each one whose quotation and claim (a new `record_units.quotation_key`) are unchanged. Kind B: the check
guard (`scripts/hooks/lib/hm_checks.py`) keeps, per quote-check footnote, how many rounds in a row flagged it, read from each
returned reply, and refuses a dispatch carrying a footnote flagged twice with the unit's round trigger.

## Technical Context

Python 3 tooling under `scripts/`; tests under `tests/tooling/` and the guard suite `tests/hooks/`. No engine code (`l7r/`,
`pool/`): the landing route is DIRECT. No map changes; no research rendering decision.

## Performance bookends

None taken: no engine code and no roll. Kind C adds one fingerprint pass over the touched questions' notes per
`make apply-edits`; kind B one regex pass over each returned quote-check reply.

## Constitution Check

- I-IX, XI: N/A - no UI, no pool content, no in-world prose, no kanji.
- X: PASS - ruff and format; a red-first test per rule.
- XII: PASS - no rendering decision; the tasks are `research: rendering` (tooling).
- XIII: PASS - nothing that settles or counts today stops doing so; both rules only add.
- XIV: the counter's two leaks (`first_look` on a hand fix, `new_cause` on any landing) are recorded in the spec; FR-002
  sits beside them rather than rewriting them, since modal checks depend on both (feature 374 batches 9 and 11).
- XVI: PASS - the literal reading is the spec's "What it is"; the narrowing decisions went to spec-fidelity.

## Decisions

- **D1 - the quotation and its claim, one key (FR-001).** `record_units.quotation_key(rec, slug)`: a digest of the note's
  cited keys (`rec.cites`), every quoted run in the note's words (「...」, "...", “...”: the stored originals are restored
  into the words as 「...」 runs, and each English rendering is quoted), and `claims_of` over the blocks carrying the mark.
  The locator, the "(translated; ...)" framing and any gloss outside the quotes are left out: they are what the GM's rule
  calls outside the quotation.
- **D2 - settled in `apply_edits.Round`, never in `owed` (FR-001).** Provenance is what makes it the GM's rule: only a
  reply's applied EDIT blocks are known to be another check's fix. `Round.__init__` records, for every quote-check note of
  the questions the blocks touch (`touched_questions(found)`), its fingerprint, its quotation key and whether it was owed;
  `Round.settle`, when the reply's checks do not include quote-check, settles each note whose fingerprint moved and whose key
  did not: through `record_owed.settle` where its answer stands at the words before, or with a new answer recorded at the
  words after, `result` naming the fix, where it was not owed before (unchanged since main). Any other note stays owed.
- **D3 - the flag count lives in the check state (FR-002, FR-004).** `state["flags"]["quote-check|<stem>#<key>"]`: at
  `returned`, a quote-check reply's lines (outside its counts line, its tables and its `OUTSIDE THE CHANGE` section) are
  read for PARTIAL, DOES-NOT-SUPPORT, DIFFERS or NOT-ON-PAGE, and each note key the dispatch's `unit:` lines name that stands
  on such a line as a whole token (longest key first) is flagged: count +1; each named note on no flagged line resets to 0.
  The state is the clone's and kept per feature (a new feature resets the counts, `hm_checks.main`), and nothing in it
  reads `origin/main`, so a landing does not reset it.
- **D4 - the trip (FR-002).** In `dispatch`, for a quote-check bundle, before the existing cap: each named note with a count
  of 2 or more trips `round:quote-check|q:NNNN@M`, M one past the highest round number any ruling or owed trigger of the
  unit carries (at least 3), detail `footnote <stem>#<key> flagged in 2 rounds in a row: <its two lines>`; the dispatch is
  refused with `hm_arbiter.refusal`. `state["flag_trips"][note]` keeps the trigger: once it is ruled `continue`, the note's
  count resets and the dispatch goes; an `accept` or `process-fault` closes the unit by the existing `closed` rule.
  `ARBITER_OK` passes as it does for the cap.
- **D5 - not NOT-READABLE (FR-006).** A canon note reads NOT-READABLE every round (0251's `l7r-money`, `l7r-money-2`); the
  readability verdict is not a flag.

## Project Structure

Touched: `scripts/record/record_units.py`, `scripts/record/apply_edits.py`, `scripts/hooks/lib/hm_checks.py`,
`tests/tooling/test_record_owed.py` (or the apply-edits test file), `tests/tooling/test_hm_checks.py` (or its suite),
`docs/guards.md` (the guard row), the feature's own records.

## Complexity Tracking

None.
