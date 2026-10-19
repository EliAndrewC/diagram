# Implementation Plan: Record-check rounds by kind of edit

**Branch**: none (main, in the clone) | **Date**: 2026-10-19 | **Spec**: `spec.md`

## Summary

Kind C: `apply_edits.Round` also fingerprints the quote-check notes of the questions a reply's blocks touch, and after the
blocks settles each one whose quotation and claim (a new `record_units.quotation_key`) are unchanged; `make record-checked
CHECK=quote-check FIXED_BY=` does the same for a fix made by hand, checked against the keys each quote-check answer now
records. Kind B: the check
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
- **D2 - settled in `apply_edits.Round`, never in `owed` (FR-001).** Provenance is what makes it the GM's rule: a reply's
  applied EDIT blocks are known to be another check's fix, so they settle here automatically; a hand fix is declared (D2b). `Round.__init__` records, for every quote-check note of
  the questions the blocks touch (`touched_questions(found)`), its fingerprint, its quotation key and whether it was owed;
  `Round.settle`, when the reply's checks do not include quote-check, settles each note whose fingerprint moved and whose key
  did not: through `record_owed.settle` where its answer stands at the words before, or with a new answer recorded at the
  words after, `result` naming the fix, where it was not owed before (unchanged since main). Any other note stays owed.
- **D2b - a declared hand fix (FR-001b).** Every quote-check answer now keeps the quotation keys of the notes it answered
  (`qkeys` beside `answered`, as a source-reader answer keeps its `readings`). `record_owed --answer quote-check --q NNNN
  --notes k,k --fixed-by "<check>: <finding>"` (Makefile `FIXED_BY=`) answers each named note at today's words when its key
  is among its unit's `qkeys`, or equals its key at the merge base (it was not owed there); the result reads `settled -
  another check's fix outside the quotation and its claim: <FIXED_BY>`. A note whose key matches neither is refused, named,
  and nothing is written. An answer recorded before this feature has no `qkeys`: such a note is refused with the plain
  command to check it, never guessed.
- **D3 - the flag count lives in the check state (FR-002, FR-004).** `state["flags"]["quote-check|<stem>#<key>"]`: at
  `returned`, a quote-check reply's lines (outside its counts line, its tables and its `OUTSIDE THE CHANGE` section) are
  read for any verdict but a pass (NOT-READABLE, DIFFERS, NOT-ON-PAGE, PARTIAL, DOES-NOT-SUPPORT), and each note key the
  dispatch's `unit:` lines name that stands on such a line as a whole token (longest key first) is flagged. Each flag keeps
  the unit's fingerprint from the dispatch's `unit:` line (what that round read): a flag on a note whose fingerprint differs
  from its previous flag's is a failed fix (count +1); a flag at the same fingerprint (nothing tried, FR-006) leaves the count
  as it is; a named note on no flagged line resets to 0.
  The state is the clone's and kept per feature (a new feature resets the counts, `hm_checks.main`), and nothing in it
  reads `origin/main`, so a landing does not reset it.
- **D4 - the trip (FR-002).** In `dispatch`, for a quote-check bundle, before the existing cap: each named note with a count
  of 2 or more whose fingerprint on this bundle differs from its last flag's (a further change) trips `round:quote-check|q:NNNN@M`, M one past the highest round number any ruling or owed trigger of the
  unit carries (at least 3), detail `footnote <stem>#<key> flagged in 2 rounds in a row: <its two lines>`; the dispatch is
  refused with `hm_arbiter.refusal`. `state["flag_trips"][note]` keeps the trigger: once it is ruled `continue`, the note's
  count drops to 1, so one more round goes and a flag in it after another fix trips again (the cap's own `continue`); an `accept` or `process-fault` closes the unit by the existing `closed` rule.
  `ARBITER_OK` passes as it does for the cap.
- **D5 - nothing tried is no failed fix (FR-006).** A canon note reads NOT-READABLE every round (0251's `l7r-money`,
  `l7r-money-2`) at the same fingerprint: D3 leaves its count where it is, so it is never held; re-linked and still
  NOT-READABLE, it counts.

## Project Structure

Touched: `scripts/record/record_units.py`, `scripts/record/apply_edits.py`, `scripts/hooks/lib/hm_checks.py`,
`tests/tooling/test_record_owed.py` (or the apply-edits test file), `tests/tooling/test_hm_checks.py` (or its suite),
`docs/guards.md` (the guard row), the feature's own records.

## Complexity Tracking

None.
