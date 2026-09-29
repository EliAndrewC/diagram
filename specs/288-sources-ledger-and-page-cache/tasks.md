# Tasks - feature 288, a sources-consulted ledger and a saved-page cache keyed by URL

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D13).

- [x] T01 `scripts/_sources.py`: the ledger (D2), the lookup and outcome (D4), the fill pass (D5), the cache and `CachedPages` (D6-D8), the seed and import (D9), the command line (FR-001, FR-002, FR-004, FR-006, FR-007, FR-008, FR-009, FR-012)
      research: rendering
      verify: DONE. scripts/_sources.py: the ledger, lookup, outcome, fill pass, cache and CachedPages, seed and import, command line; tests/tooling/test_sources.py 37 passing, every new line covered
- [x] T02 `make source-pages` prints each URL's earlier reads before its fetch, appends `pending`, takes `QUESTION=`, reads and fills the cache; the saved form moves to `_sources` (D1, D3; FR-003, FR-008)
      research: rendering
      verify: DONE. _source_pages.py prints each URL's earlier reads before its fetch, appends pending with QUESTION=, reads and fills the cache (a cached row says so); wrapped/parts moved to _sources, and a Latin stop now wraps only before whitespace (3.5 stays whole)
- [x] T03 `make quote-verbatim` and every `make check-bundle` mode read the cache; `KEY= WHOLE=1` ledgers with `QUESTION=`, the excerpt bundle does not (D3, D8; FR-003, FR-010)
      research: rendering
      verify: DONE. quote-verbatim reads through an EXACT CachedPages (an imported copy is fetched afresh; refused passes through); check-bundle KEY= WHOLE=1 ledgers with QUESTION=, the excerpt passes --no-ledger, and the quote-check entry bundle carries the cached text of each residue page (cache only)
- [x] T04 `make reserve KIND=registry ... URL=`: the stub names the pointer and the ledger marks it cited; `make record` runs the fill pass (D5; FR-005)
      research: rendering
      verify: DONE. reserve-prefix.py --url: the registry stub names the pointer and the ledger marks it cited; make record runs the fill pass (not under CHECK=1)
- [x] T05 The Makefile targets and variables, `.gitignore` (D12; FR-014, FR-015)
      research: rendering
      verify: DONE. Makefile: source-outcome, sources-consulted, sources-import; QUESTION= on source-pages and check-bundle, URL= on reserve; .gitignore gains the ledger and the cache
- [x] T06 `quote-check` and `source-reader`: read the bundle's cached text before any WebFetch (D10; FR-011)
      research: rendering
      verify: DONE. quote-check step 2 and source-reader step 0 read the bundle's cached text before any WebFetch; frontmatter untouched, test_agent_models green
- [x] T07 The process text: `research/CLAUDE.md`, `page-session-rules.md`, the root CLAUDE.md clause, the drift test's phrase (D11; FR-013)
      research: rendering
      verify: DONE. research/CLAUDE.md and page-session-rules.md carry the ledger rules; the root CLAUDE.md clause; test_page_session_rules asserts make source-outcome and the rejected rule
- [x] T08 Tests: `test_sources.py`, and additions to the source-pages, check-bundle, quote-verbatim and reserve tests; full coverage of the new and changed code (D13; FR-015, SC-001, SC-002, SC-003, SC-005, SC-007, SC-008, SC-009)
      research: rendering
      verify: DONE. test_sources.py plus additions to the source-pages, check-bundle, quote-verbatim and reserve tests: 96+ passing, the new code fully covered (make cov-file with the engine config bypassed)
- [x] T09 Run the one-time seed and import on the host; record the counts in research.md R2 (D9; FR-007, FR-012, SC-004, SC-006)
      research: rendering
      verify: DONE. make sources-import on the host: 7,161 seed lines over 4,282 URLs, 2,365 pages imported (106 MB); research.md R2
