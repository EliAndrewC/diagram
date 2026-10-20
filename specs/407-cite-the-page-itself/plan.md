# Implementation Plan: a note links to the page its passage is read on (feature 407)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-19

## Summary

The record's link rule gains the GM's two rulings: a Morisada or Gamble footnote may link the exact page of its passage,
and any footnote quoting a spreadsheet cell may link the spreadsheet file, each only where that URL is on the key's
citation line. The test, the rule text and the notes change; the notes' checks run on what changed. No engine code.

## Technical Context

- **The test.** `tests/interactive/test_sources.py`: `line_urls` (every URL on a citation line outside its comments),
  `PAGE_KEYS` (the three keys) and `may_link` (notes files only; a PAGE_KEYS key's line URL, or any key's spreadsheet
  file) beside the existing first-URL rule; `test_a_note_may_link_its_page_or_spreadsheet_and_nothing_else` pins the
  passing and failing cases. `link_target` in `l7r/` is unchanged (the works sections keep the first URL).
- **The URLs** are already on the citation lines: Morisada 上 koma 57, 74, 75, 76, 79, 80, 88, 94, 137; 下 koma 228, 229;
  Gamble's page images n19 (p. xiv), n202 (p. 183), n214 (p. 195), n215 (p. 196), n468 (p. 431); Bochum chapters 1, 13,
  15 and 22.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: T02 is `research: physical` with its five boxes. XIII: `make record CHECK=1` and the record tests stay
  green. XVI: built as the spec's FRs.

## D1 - the rule (FR-001, FR-002)

`research/CLAUDE.md`'s citation section and `docs/research-record-rules.md` under the same heading: a cell of a public
spreadsheet is a readable page and a footnote quoting one may link the file; a Morisada or Gamble footnote may link the
exact page of its passage; each URL on the key's citation line; every other link stays the first URL. The test as above.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
## D2 - the notes (FR-003, FR-004)

Each Morisada note links the koma its passage begins on (from its comment: 0259 79, 80, 88; 0262 228, 229, 137, 76, 74,
75, 88; 0265 57, 88; 0275 88; 0276 94); each Gamble note the page image of its page; each Bochum note quoting a chapter's
rows that chapter's spreadsheet (0260 ch. 1 and 13, 0275 ch. 13 and 1, 15); a Bochum note quoting the database's landing
page keeps it. Then `make record-owed`, and the owed checks (quote-check on the changed notes) from bundles; four or more
of one check as one `check-wave` workflow.

### T02 Approach

1. Goal: each Morisada, Gamble and Bochum footnote opens the page or spreadsheet its passage is printed on.
2. Constraints: test_sources (may_link); quote-check READABLE, VERBATIM, SUPPORTS on the linked page; the round cap.
3. Sources: the links G (the GM, 2026-10-19); the checks G (constitution XII, features 194-195); a note links the koma its
   passage begins on O (ours, where a passage runs over two koma).
4. Holds: a note whose passages sit on different pages of different files is split by page, so each link carries its
   passage (0275's Bochum note).
5. Order: re-point, then check on page images and row dumps (the agents cannot run the NDL viewer or decode .xls), then fix.
6. Exits: (e) conform, with (b) a split where one link cannot carry a note's passages.
7. No search loop.
8. Budget: an hour, with two check rounds.
9. Done: every re-pointed note READABLE, VERBATIM and SUPPORTS on its page; make record-owed 0 unanswered.
10. n/a.
11. n/a.

### T03 Approach

1. Goal: the feature lands on main with its report.
2. Constraints: the review gate, the ledger, page-check and hooks-test before the push.
3. Sources: all G (CLAUDE.md's stop-work procedure).
4. Holds as written.
5. Order: report, tick, gates, land, then the note on #9.
6. Exits: (e) conform.
7. No search loop.
8. Budget: 15 minutes.
9. Done: the push lands; origin/main carries 407.
10. n/a.
11. n/a.

## D3 - the note to the asker

None owed: the links change, no verdict does. Mentioned on EliAndrewC/diagram#9 in one line.

## T - the order

1. The rule and the test. 2. The notes, then their checks. 3. Report and land.
