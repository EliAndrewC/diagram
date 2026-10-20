# Feature 407: a note links to the page its passage is read on

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-19

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-19, "Yes, a cell in a public spreadsheet counts as a readable page. And yes, Morisata and Gamble Notes may link straight to their page."

**Input**: `request.md`

## User Scenarios & Testing

### User Story 1 - A reader clicks a footnote and lands on the passage (Priority: P1)

**Acceptance Scenarios**:

1. A cell of a public spreadsheet (an .xls, .xlsx or .csv anyone can download) is a readable page: a note may quote it,
   naming the sheet and row (or cell), and link the file itself. The record's citation rule says so.
2. A FOOTNOTE citing Morisada (`ruiju-kinsei-fuzokushi-jo`, `ruiju-kinsei-fuzokushi-ge`) or Gamble
   (`gamble-burgess-1921-peking-survey`) may link the exact page its passage is read on - an NDL viewer page
   (`https://dl.ndl.go.jp/pid/<pid>/1/<koma>`), a page image - provided that URL is on the key's registry citation line;
   and a footnote of ANY key quoting a spreadsheet cell may link the public spreadsheet file (.xls, .xlsx, .csv) on its
   key's citation line. Every other link stays the entry's first URL: every other key's notes, and any roster, works
   section or prose link, even of these keys. A link to a URL on no citation line still fails.
3. The Morisada notes (類聚近世風俗志 上 and 下, every money question citing them), the Gamble 1921 survey notes, and the
   Bochum Zhili notes (0260, 0275) link the page or file their passages are read on, each such URL added to the
   source's citation line first.
4. The re-pointed notes pass the record's checks on what changed (quote-check: READABLE on the linked page), so the
   "the passage is not on the linked page" findings of features 400, 402 and 403 are closed.

## Requirements

### Functional Requirements

- **FR-001**: `research/CLAUDE.md`'s citation rule (and `docs/research-record-rules.md` beside it) MUST say a cell of a
  public spreadsheet is a readable page whose file a footnote may link, and that a Morisada or Gamble footnote may link the
  exact page of its passage, each when that URL is on the key's citation line; every other link stays the first URL.
- **FR-002**: `tests/interactive/test_sources.py` MUST accept, in a notes file only, a Morisada or Gamble key's link to any
  URL on its citation line and any key's link to a spreadsheet file on its citation line; and still refuse every other
  key's second URL, any second-URL link outside a notes file, a URL on no citation line, a bare key, and a registry link
  for a read document.
- **FR-003**: The Morisada, Gamble and Bochum notes MUST link their passages' pages or files, as in scenario 3.
- **FR-004**: The changed notes MUST pass the record's checks on what changed.
- **FR-005**: Nothing changes engine code (`l7r/`, `pool/`), a map, or the GM's canon.

## Success Criteria

- **SC-001** (FR-001, FR-002): The rule text says both things; tests pin that a Morisada note's second URL and any key's
  spreadsheet URL pass in a notes file, and that a URL on no line, another key's non-spreadsheet second URL, and a
  second-URL link outside a notes file fail.
- **SC-002** (FR-003, FR-004): Every Morisada, Gamble and Bochum note links a page its passage can be read on, and
  `make record-owed` names no unanswered check.
- **SC-003** (FR-005): The feature's diff touches no file under `l7r/`, `pool/` or the GM's canon.

## Assumptions

- The works sections and the registry keep each entry's first URL as its landing link; only a note's own link changes.

## Review history

- **spec-fidelity round 1 (2026-10-19): CHANGES REQUIRED, 2 items.** The exact-page permission narrowed to the keys the
  GM ruled on (Morisada, Gamble) plus spreadsheet files for any key; the relaxation applies in notes files only, with a
  test that a second URL outside one fails. A record-wide rule is put to the GM as a question, not built.
- **spec-fidelity round 2 (2026-10-19, verify): FAITHFUL.** Both items resolved.
