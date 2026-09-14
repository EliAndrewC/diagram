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
  in MODE 4 before any task is ticked. **The 2026-09-14 split (spec D7) is the GM's own ruling**, not a
  narrowing by this plan: what this plan defers to feature 250 is exactly what the spec's D7 names, and
  the amended spec and this amended plan are each re-reviewed on a counter reset to zero.
- **Route**: no engine code (FR-014) - `research/*.html`, `SOURCES.html`, `citations/`, the derived `.js`,
  this feature's directory, `.claude/skills/diagram/research/CLAUDE.md` and the root `CLAUDE.md` (FR-015),
  and the GM's `TO-DOWNLOAD.md` outside the repository -> DIRECT.
- **Order (FR-012, SC-010)**: the PAGE is the outer loop and the tier order runs inside it - a page's items
  are finished, checked and committed together (FR-009), and `record-format` and `quote-check` read a page,
  so a strict whole-list tier sweep would leave every page half-noted until the last tier; SC-010 admits
  the departure with this stated reason.

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
  `no publicly readable source (searched 2026-MM-DD: <what was tried>)`. For a worked sentence that
  carries NO claim about how a place was built, farmed, planted, governed or lived in and is not a labeled
  guess about the physical world: a GROUNDS note naming one or more of FR-004's six reasons - measured on
  our own maps, the record's own silence, follows from the definitions, physical necessity, a drawing
  convention, this project's decision - and never for a sentence FR-004 bars from the form. Each CONTRADICTED:
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
- **P9 the guidelines carry the download list's format** (FR-015, T23): the paragraph "A page the
  container cannot fetch is not thereby unreadable" in `.claude/skills/diagram/research/CLAUDE.md` gains
  the rule - whenever a session has a source for the GM to look at or download, it is saved in markdown in
  the FR-010 shape (the named heading, the guessed direct link, the uniquely identifying Google-search
  link, what rests on it, what blocked the fetch), appended at the END of the standing list
  (`/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`), never inserted or handed over only in a chat message -
  with the GM's 2026-09-14 reason quoted and the plain statement that no gate here reads the list; the root
  `CLAUDE.md`'s citation rule gains a pointer to it. Written before the first Part 4 entry is appended, so
  this feature's own hand-over is the first under the rule.
- **P10 the close under the split** (spec D7, D8; the GM's 2026-09-14 ruling in `request.md`). The
  thirteen whole-record check reports are applied where they bear on honesty - every quote-check
  NOT-ON-PAGE, DOES-NOT-SUPPORT, MISPLACED and DIFFERS verdict, every reader-visible defect and
  untranslated quotation the record-format reports name, the batch-1 applicability corrections - and the
  rest is named to feature 250. The confirmation after those edits is one `quote-check` and one
  `record-format` per edited page, each given the changed notes and sections rather than the whole page
  (the page was already checked whole; the feature-249 principle that a later round reads the diff). The
  entry-drift pairs are answered by measurement: `measure/prose_moved.py` classifies every moved section
  as MARKS-ONLY (the reader's prose identical once marks, comments and the roster line are stripped) or
  WORDING-MOVED, `entry-drift` is dispatched at every named pair with a WORDING-MOVED section and the
  prose it calls DRIFTED is rewritten, and the MARKS-ONLY pairs are discharged with one recorded
  `ENTRY_DRIFT_OK` whose reason cites the measurement. `cities/sizing.html` is not footnoted here; T16 is
  removed from `tasks.md` and the page is feature 250's FR-001.
