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
2. A note may link the exact page its passage is read on - an NDL viewer page (`https://dl.ndl.go.jp/pid/<pid>/1/<koma>`),
   a page image, a chapter's spreadsheet - provided that URL is on the source's registry citation line; the registry
   entry's first URL stays the work's own landing link (the works sections, an unread link). A link to a URL on no
   citation line still fails.
3. The Morisada notes (類聚近世風俗志 上 and 下, every money question citing them), the Gamble 1921 survey notes, and the
   Bochum Zhili notes (0260, 0275) link the page or file their passages are read on, each such URL added to the
   source's citation line first.
4. The re-pointed notes pass the record's checks on what changed (quote-check: READABLE on the linked page), so the
   "the passage is not on the linked page" findings of features 400, 402 and 403 are closed.

## Requirements

### Functional Requirements

- **FR-001**: `research/CLAUDE.md`'s citation rule (and `docs/research-record-rules.md` beside it) MUST say a cell of a
  public spreadsheet is a readable page, and that a note may link the exact page or file of its passage when that URL is
  on the source's citation line.
- **FR-002**: `tests/interactive/test_sources.py` MUST accept a note's link to any URL on its key's citation line for a
  read document, and still refuse a URL on no citation line, a bare key, and a registry link for a read document.
- **FR-003**: The Morisada, Gamble and Bochum notes MUST link their passages' pages or files, as in scenario 3.
- **FR-004**: The changed notes MUST pass the record's checks on what changed.
- **FR-005**: Nothing changes engine code (`l7r/`, `pool/`), a map, or the GM's canon.

## Success Criteria

- **SC-001** (FR-001, FR-002): The rule text says both things; the test fails on a link to a URL on no citation line and
  passes on one to a second URL of the line (a test pins each).
- **SC-002** (FR-003, FR-004): Every Morisada, Gamble and Bochum note links a page its passage can be read on, and
  `make record-owed` names no unanswered check.
- **SC-003** (FR-005): The feature's diff touches no file under `l7r/`, `pool/` or the GM's canon.

## Assumptions

- The works sections and the registry keep each entry's first URL as its landing link; only a note's own link changes.
