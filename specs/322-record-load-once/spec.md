# Feature Specification: The record loaded once

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=322-record-load-once`)

**Created**: 2026-10-04

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: *"Eh, go ahead and fix it now, we might as well, even if it requires a full
feature."* - the fix being the reload described there.

## Context (observed 2026-10-04, method: cProfile of the slow quick tests, session "Diagram performance")

`record_text(rel, research_dir)` (`l7r/diagram/interactive/sources.py`) is how every reader of the research record - the tests, the
prepass script, the record's own checks - gets a page as its reader sees it. Its text is cached per page for the life of the process,
and `clear_caches()` forgets that cache when a build starts. But a first read of a question page calls `store.load(research_dir)`, which
reads and parses the whole record (~480 question files, ~90 ms), to render that one page. A caller reading N question pages loads the
record N times: cProfile measured 475 loads, 42 s of a 44 s test. Three tests were a quarter of a full `make quick` for this reason
and one other; commit `d8851588e` worked around it in the tests (`tests/_record_pages.text_of`, which loads the record once per test
process and renders pages from it). The engine's reader still has the bug, and the tests now restate two of its calls.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reading many pages loads the record once (Priority: P1)

A caller that reads every question page of a record through `record_text` pays for one load of the record, not one per page.

**Why this priority**: it is the bug the GM asked to have fixed.

**Independent Test**: read every question page of the real record through `record_text` in a fresh process and count the record's
loads; time the test that reads every page.

**Acceptance Scenarios**:

1. **Given** a fresh process, **When** every question page of a record is read through `record_text`, **Then** the record is loaded
   once for that record directory.
2. **Given** two different record directories (a test's fixture record and the real one), **When** pages of each are read, **Then**
   each directory's record is loaded once and pages never come from the wrong record.

---

### User Story 2 - A build still sees an edited fragment (Priority: P1)

What a fresh read promised before still holds: after `clear_caches()`, a page reflects fragments edited since the last read.

**Why this priority**: keeping the loaded record across reads must not make an edit invisible to a build or a test that edits and
reads again.

**Independent Test**: read a page of a fixture record, edit one of its fragments, call `clear_caches()`, read again.

**Acceptance Scenarios**:

1. **Given** a page read once, **When** a fragment of that record is edited and `clear_caches()` is called, **Then** the next read
   shows the edit.

---

### User Story 3 - The tests read through the engine again (Priority: P2)

The test helper added as the workaround reads pages through `record_text` again instead of restating the engine's calls.

**Why this priority**: one reader, so the tests test what the engine does.

**Independent Test**: the helper's body is a call to `record_text`; the three tests it sped up stay as fast.

**Acceptance Scenarios**:

1. **Given** the fix, **When** the record tests run, **Then** they read through `record_text` and run as fast as with the workaround.

### Edge Cases

- A record directory named two ways (relative and absolute, a trailing slash) is one record, as the page cache already treats it.
- A question name the record does not hold, and a page that is not a question page (the registry, a drawing page, a fixture's file):
  read exactly as today.
- A process that never reads a question page never loads the record.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `record_text` MUST load a record directory's record at most once per process between calls to `clear_caches()`, and
  render every question page of that directory from it.
- **FR-002**: The loaded record MUST be keyed by the record directory as the page cache keys it, so two directories never share one.
- **FR-003**: `clear_caches()` MUST forget the loaded records as well as the pages.
- **FR-004**: Every page `record_text` returns MUST be byte-identical to what it returned before this feature, for every page of the
  real record and for the fixture records the tests build.
- **FR-005**: `tests/_record_pages.text_of` MUST read through `record_text`, with no restated engine calls.
- **FR-006**: No map output moves; no test may fail that passed before.

### Key Entities

- **Loaded record**: the parsed research record for one directory, held for the life of the process until `clear_caches()`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001): reading all 475 question pages of the real record in a fresh process loads the record once (counted), and
  `test_every_registry_key_cited_in_a_research_page_is_a_link_to_the_right_target` stays under 3 s with the helper reading through
  `record_text` (observed 2026-10-04, method: per-test pytest timing and cProfile, commit d8851588e, research.md R1: it ran 44 s before the
  workaround, 1.0 s with it; the 3 s bound is a target).
- **SC-002** (FR-002): a test reading a fixture record and the real record in one process gets each page from its own record.
- **SC-003** (FR-003): a test edits a fixture fragment after a read, calls `clear_caches()`, and reads the edit.
- **SC-004** (FR-004): every page of the real record, read before and after, is byte-identical (compared over all 475 question pages
  and the registry).
- **SC-005** (FR-005, FR-006): `make done` green; the four record tests commit d8851588e sped up (three through `text_of`, one through its `canon_keys` hoist) stay within 2x of
  their workaround times
  (observed 2026-10-04, method: per-test pytest timing, commit d8851588e, research.md R1: 0.2 / 3.8 / 1.0 / 0.3 s; the 2x bound is a target).

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

None: no map draws or states anything differently. The cache is process plumbing, not a rendering decision.

## Assumptions

- The page cache's existing semantics - a record does not change under a process between `clear_caches()` calls - are the contract.
  What changes: a page not yet read is now rendered from the record as loaded at the first question-page read since the last
  `clear_caches()`, not from the files at the moment it is read. That is safe because no caller edits a fragment and then reads
  without `clear_caches()`: the site build calls it when it starts (`record/site.py`), the prepass and quote scripts are
  short-lived readers, and each test fixture is its own directory (FR-002).
- Memory: holding one loaded record per directory costs what one `store.load` costs while it lives; a test process already held one
  through the workaround.

## Review history

- Round 1 (initial acceptance, MODE 2, 2026-10-04): FAITHFUL. Two non-blocking notes applied: the staleness assumption reworded to
  name the real change and why it is safe; SC-005's four tests attributed (three via `text_of`, one via the `canon_keys` hoist).
  (An earlier dispatch mislabeled MODE 1 returned NOT-REVIEWABLE on unlabeled figures and used no round.)
