# Research: the record loaded once (feature 322)

## R1 - The reload, measured (2026-10-04, session "Diagram performance", before this feature)

**Method**: a full `make quick ALL=1` with a per-test timing plugin (6 workers, quiet machine), then cProfile of each slow test
in a `make test-file` run; then the same tests timed after commit d8851588e (the test-side workaround, `tests/_record_pages.text_of`).

**Found** (observed 2026-10-04, method: cProfile): `sources._record_text`'s question branch calls `store.load(research_dir)` on every page-cache miss. In
`test_every_registry_key_cited_in_a_research_page_is_a_link_to_the_right_target`: 475 calls to `store.load`, 42.4 s of a 44.2 s
test (cProfile cumulative); the glossary test the same shape (24 s in `questions._gather` over 475 loads, 48.5 s profiled).

| test (observed 2026-10-04, method: per-test pytest timing) | before | with the workaround |
|---|---|---|
| test_every_canon_entry_links_its_notes_on_github_and_none_says_url_none (canon_keys per entry, fixed in the test) | 55.1 s | 0.2 s |
| test_every_glossary_term_is_used_by_a_modal_or_a_record_page | 37.8 s | 3.8 s |
| test_every_registry_key_cited_in_a_research_page_is_a_link_to_the_right_target | 31.5 s (44 s profiled) | 1.0 s |
| test_every_page_carries_both_entries_of_every_pair | 12.2 s | 0.3 s |

Observed 2026-10-04, method: the targets' own pytest summary - `make quick ALL=1`: 104 s -> 64 s; `make test-full` at 6 workers ~244 s -> 161 s.

## R2 - The fix, measured (2026-10-04, after T02-T03)

**Load count (SC-001)** (observed 2026-10-04, method: `store.load` wrapped and counted in the fixture tests,
`tests/interactive/test_sources.py`): every question page of a fixture record read through `record_text` loads it once; two
directories load once each; an edit is read after `clear_caches()`. Each test was shown to FAIL on the unfixed code: with
`store.load` restored in `_record_text` the two count tests went red, and with `_loaded` dropped from `clear_caches()` the
edit test went red.

**Byte identity (SC-004)** (observed 2026-10-04, method: a one-shot test, run once through `make test-file` and not committed):
every question page of the real record through `record_text`, against a fresh `store.load` and `page_html` per page as the old
code did, and the registry against `store.registry_html` - none differ (22.3 s for the run, almost all of it the per-page
fresh loads). It is one-shot on purpose: the plan's Tests section had it as a permanent test over the real record, but the plan
review noted that a permanent per-page fresh comparison reloads the record ~475 times - the cost this feature removes - and that
SC-004 asks only for a before-and-after comparison; the fixture tests keep the comparison permanently on a small record.

**The four record tests (SC-001, SC-005)** (observed 2026-10-04, method: pytest `--durations`, the helper reading through
`record_text`): glossary 3.81 s, registry links 0.87 s, confusables 0.30 s, canon entries 0.23 s - against the workaround's
3.8 / 1.0 / 0.3 / 0.2 s (R1). `tests/interactive` whole: 5,308 tests in 16 s.

**A note on the key (plan review, round 1)**: `os.path.normpath` makes a directory with and without a trailing slash one key,
but a relative and an absolute path to the same directory stay two keys - a second load of the same record, never a page from
the wrong one. FR-002 asks for the page cache's own keying, which this is; the spec's Edge Cases line overstated it.
