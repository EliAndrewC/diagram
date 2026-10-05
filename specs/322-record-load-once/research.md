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
