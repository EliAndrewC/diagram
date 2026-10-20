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

### T01 Approach

1. Goal: a reader clicking a Morisada, Gamble or spreadsheet footnote lands on the page or file the passage is on.
2. Constraints: test_sources' first-URL rule (feature 190); feature 195's readable-page rule; the GM's 2026-10-19 rulings.
3. Sources: first-URL rule G (feature 190, "Any reference ... should be a link to that external document"); the new
   permission G (2026-10-19, quoted in request.md); notes-only and citation-line-only O (spec-fidelity round 1's scope).
4. The rule holds: a works section or roster has no single page, so the first URL stays right there.
5. Order: rule and test first, then the notes, then their checks.
6. Exits: (b) a principled exception for the keys the GM named and for spreadsheets - chosen; (e) conform - rejected,
   the GM ruled.
7. No search or packing loop.
8. Budget: 30 minutes for T01.
9. Done: test_a_note_may_link_its_page_or_spreadsheet_and_nothing_else green; the record tests green with the notes
   re-pointed (they failed on the Bochum xls link before, feature 404's landing).
10. n/a: no constant moved.
11. n/a: nothing fitted into room.

## D2 - the notes (FR-003, FR-004)

Each Morisada note links the koma its passage begins on (from its comment: 0259 79, 80, 88; 0262 228, 229, 137, 76, 74,
75, 88; 0265 57, 88; 0275 88; 0276 94); each Gamble note the page image of its page; each Bochum note quoting a chapter's
rows that chapter's spreadsheet (0260 ch. 1 and 13, 0275 ch. 13 and 1, 15); a Bochum note quoting the database's landing
page keeps it. Then `make record-owed`, and the owed checks (quote-check on the changed notes) from bundles; four or more
of one check as one `check-wave` workflow.

## D3 - the note to the asker

None owed: the links change, no verdict does. Mentioned on EliAndrewC/diagram#9 in one line.

## T - the order

1. The rule and the test. 2. The notes, then their checks. 3. Report and land.
