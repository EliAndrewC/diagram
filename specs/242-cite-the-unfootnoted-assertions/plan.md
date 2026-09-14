# Plan - 242 cite the unfootnoted assertions

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **XII**: every item is a RESEARCH question - a `source-reader` pass before any note is written (FR-003),
  the quote at the assertion (FR-004), the source judged by `source-applicability` before it is cited
  (FR-005, FR-007). A guess label is for a record searched and found silent.
- **V**: nothing inside a SOURCE block or `l7r.md` is touched; the GM's `request.md` is verbatim.
- **VI**: the mechanical tests (`tests/interactive/test_footnotes.py`, `test_citations.py`,
  `test_record_format.py`) run per page before its commit; `make page-check` before the push (FR-009, SC-014).
- **XIV**: a defect found on a page while footnoting it (a truncated sentence, a wrong figure) is fixed in
  that page's batch and recorded in `research.md` (FR-006).
- **XVI**: the spec is accepted (FAITHFUL, amended twice with FAITHFUL verdicts); this plan is reviewed
  in MODE 4 before any task is ticked.
- **Route**: no engine code (FR-014) - `research/*.html`, `SOURCES.html`, `citations/`, the derived `.js`,
  this feature's directory, and the GM's `TO-DOWNLOAD.md` outside the repository -> DIRECT.

## Design

- **P1 the work list per page is DERIVED** by `measure/worklist.py <page>`, which imports the census's
  own parsers (`items`, `page_of`, `confidence`, `carries_marker`) so the list is the FR-001 filter
  applied to one page, ordered by tier (FR-012), and for each item locates the quoted sentence in the
  research page's HTML (tags stripped, whitespace normalized, a distinctive window matched) and prints
  the line number or NOT-LOCATED. An item the harness cannot locate is placed by hand from the reader's
  section heading. The twenty-two R7 closures are recognized when met (a sentence already carrying a
  `<sup>`, or one of the named R7 items) and skipped with a note in `research.md`.
- **P2 the reading is dispatched in parallel `source-reader` agents**, background, Opus, eight to
  twelve claims each, one page at a time: each claim verbatim with its section heading and page; the
  agent SEARCHES for a public page that states it (primary and scholarly first), READS it, and returns
  READ with the verbatim passage, the URL, the page's title and author/publisher and date (the material
  for the registry write-ups), or NOT-FOUND with what was searched, or CONTRADICTED with the quote. A
  stalled agent is reported by `agent-stall-hooks.sh` and relaunched with the failed host excluded.
- **P3 the notes are written from the returns.** For each READ: a registry key (new keys get the
  citation line, *What it is*, *Why it applies, and its limits*, *Used for*), a `<li id="fn-n">` on the
  citations page in the CITATION form with the passage 「」 (a foreign-language passage in English
  translation marked as such with the original after), the `<sup class="fn">` at the sentence, the key
  added to the section's `Sources:` roster. For each NOT-FOUND: an ABSENCE note in the exact form
  `no publicly readable source (searched 2026-MM-DD: <what was tried>)`. For a sentence that is a
  drawing convention or this project's decision and carries no physical claim: a GROUNDS note from the
  six reasons - never for a claim about how a place was built or lived in (FR-004). Each CONTRADICTED:
  the sentence rewritten to the finding, the correction recorded in `research.md` (FR-006). New keys go
  to `source-applicability` in one dispatch per page before the page's commit (FR-007).
- **P4 the checks per page**: `make citations`; `make test-file` over the three interactive test
  files; `quote-check` and `record-format` dispatched in parallel over the changed page and its
  citations page; `scripts/_entry_owed.py` for the pairs, each to `entry-drift` or one recorded
  `ENTRY_DRIFT_OK` for a sweep in which no finding moved (FR-008); then the page's commit (FR-009).
- **P5 the unreadable documents** go to `TO-DOWNLOAD.md` Part 4, appended at the END in the GM's format
  (FR-010): heading, the guessed direct link, the uniquely identifying Google-search link, what rests on
  it, what blocked the fetch.
- **P6 the never-searched absence notes** (T18) are listed by `measure/note_census.py --list` (the
  harness that counted them), worked in the same P2-P4 pipeline after the Phase 1 pages, and counted
  separately in the closing report (FR-011, SC-013).
- **P7 the roster disclosures** (T19): each of the fifty-one `Sources:` lines carrying a disclosure a note
  now holds is rewritten to point at the note, no change of meaning; `make citations` and the footnote
  tests after.
- **P8 the closing report** (T21) in `research.md`: per page what closed in each of the three forms,
  per unclosed item searched-and-failed or never-searched, the two settled items named, and the two
  counts (the FR-001 list and the D1 list) reported separately.
