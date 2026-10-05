# Implementation Plan: The record loaded once

**Feature**: 322-record-load-once | **Spec**: spec.md | **Request**: request.md

## Summary

`sources._record_text` keeps the loaded record per record directory for the life of the process, as it already keeps each page;
`clear_caches()` forgets both. `tests/_record_pages.text_of` goes back to calling `record_text`.

## Performance bookends (constitution VI)

`make perf LABEL=322-start` on unmodified code (d8851588e, before the first engine edit) and `LABEL=322-end` at the last commit;
`make perf-report AGAINST=322-start`. The roll does not read the record, so no band is expected; whatever the report names is owed
its records.

## Decisions

**D1 - The loaded record, cached beside the pages (FR-001, FR-002).** A module-level `@cache` function `_loaded(research_dir)`
returning `store.load(research_dir)`, called by `_record_text`'s question branch in place of `store.load`. Its key is the
`os.path.normpath`'d directory `record_text` already passes `_record_text`, so a directory named two ways is one record and two
directories never share one (the page cache's own keying). A process that reads no question page never calls it.

**D2 - Forgotten with the pages (FR-003).** `_loaded` joins the tuple `clear_caches()` clears. What changes (spec Assumptions): a page not
yet read is rendered from the record as loaded since the last `clear_caches()`, not from the files at that moment - safe because every
caller that edits fragments calls `clear_caches()` first (the site build), and the scripts only read.

**D3 - Byte-identical pages (FR-004).** The question branch still calls `store.page_html(record, record.by_file[name], research_dir)`
with the same arguments, only on a record loaded once; SC-004 compares every page before and after in one run (the base read with a
fresh `store.load` per page, as the old code did).

**D4 - The test helper (FR-005).** `text_of` becomes `record_text(rel)`; its `_real_record` goes. Its callers keep the name, so the
three record tests that use it read through the engine.

**D5 - Research claims.** `_loaded` carries `Research: record load cache - NONE: process plumbing` (feature 316's form, as
`_memory.trim_heap` does); `_record_text` and `clear_caches` keep theirs, owed an `impl-drift` check only if `make claims-owed` says so.

## Tests

- `tests/interactive/test_sources.py`: reading every question page of a fixture record loads it once (`store.load` counted by a
  wrapper), two fixture directories each load once and pages come from their own record (SC-001 count, SC-002), and an edit after
  `clear_caches()` is read (SC-003).
- SC-004 as a test over the real record: every question page and the registry through `record_text` equal a per-page fresh render.
- SC-001's timing and SC-005: the four record tests timed after the change, recorded in research.md.

## Verification

`make quick` while iterating; `make test-file FILE=tests/interactive`; `make done`; the bookends.

## Constitution Check

No map draws or states anything differently (no Decisions Recorded entries). Research-driven (XII): not a research question - a
cache. 100% coverage (owed by the new function the day it lands): the tests above reach every line. Fix-where-found (XIV): what the
change exposes is fixed here.
