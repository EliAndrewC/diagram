# Tasks - feature 312, uncited-source catalog

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md).

## Occasions

- none: the feature draws nothing on a map - no element new to a map, no glyph, no placement rule; the record's Sources
  gain a part, and the record checks on the new write-ups are owed by `make record-owed`.

## Phase 1 - blocked domains and banned citations (US1; FR-001 - FR-004)

- [x] T01 [US1] `record/blocked.py`, `blocked-domains.json` (Grokipedia, the GM's approval quoted), `banned-citations.json`
      (empty); the loader's refusal of an unapproved entry; tests (plan D1)
      research: rendering
      verify: DONE. blocked.py loads blocked-domains.json (Grokipedia, GM approval quoted) and banned-citations.json (empty); an unapproved entry is refused; tests/interactive record tests green
- [x] T02 [US1] the Python fetch routes and stores refuse a blocked URL (`_sources`, `_archive`, `_archive_ops`); tests
      (plan D2)
      research: rendering
      verify: DONE. _sources, _archive and _archive_ops refuse a blocked URL; test_record_blocked and test_sources green (171 passed with the feature's tests)
- [x] T03 [US1] `blocked-fetch-hooks.sh` (WebFetch and Bash fetch invocations) with its test companion, registered in
      `.claude/settings.json` and `make hooks-test` (plan D2)
      research: rendering
      verify: DONE. blocked-fetch-hooks.sh registered in .claude/settings.json; scripts/test-blocked-fetch-hooks.sh 18 passed, 0 failed; joins make hooks-test by its glob
- [x] T04 [US1] the build refuses a blocked or banned citation (plan D3); fixtures; `docs/research-doctrine.md` and the
      registry front page point at the lists
      research: rendering
      verify: DONE. the record build refuses a blocked or banned citation; fixtures in test_record_blocked green; the doctrine and the registry front page point at the lists

## Phase 2 - what was tried (US5; FR-015 - FR-018)

- [x] T10 [US5] `scripts/_attempts.py` (seed, append, show), `make attempts`; `.gitattributes` union lines; tests (plan D12)
      research: rendering
      verify: DONE. _attempts.py seed/append/show and make attempts; test_attempts 9 passed; the seed now catches up ledger rows written by sessions on older code
- [x] T11 [US5] `make source-pages` requires `Q=` and `SOUGHT=` and prints attempts and verdict first; `make
      source-outcome` appends the outcome; the hook prints them as context for a WebFetch and appends an attempt for a
      WebFetch or a Bash fetch; `make archive` appends one; `make archive-find` prints the attempts and verdict of each
      source it returns and appends one; tests
      research: rendering
      verify: DONE. make source-pages refuses a ledgered read without Q= and SOUGHT= and prints earlier attempts first; source-outcome, the fetch hook, archive and archive-find append attempts; test_source_pages green
- [x] T12 [US5] seed `source-attempts.jsonl` from the ledger; SC-007 count recorded in `research.md`
      research: rendering
      verify: DONE. source-attempts.jsonl seeded; SC-007 measured 2026-10-02: 4905 ledger URLs, every one with an attempt line after the catch-up seed (3 rows from feature 315 had none before it)

## Phase 3 - the filter (US2, US3; FR-006 - FR-011, FR-022)

- [x] T20 [US2] `scripts/_uncited.py` (set, rule, fetch, bundle, apply, score, report) and `make uncited`; tests (plan D4,
      D5, D7)
      research: rendering
      verify: DONE. _uncited.py set/rule/fetch/bundle/apply/score/report (plus draft/install/merge/dedupe/unkeep/requeue) and make uncited; test_uncited 41 passed
- [x] T21 [US2] FR-022: the 8 cited respellings checked
      research: rendering
      verify: DONE. R4: six of the eight respellings covered by their key's archived URL, one a typo mark, one (minzoku-kinkyu-chosa-jawiki) uncited and judged by the filter
- [x] T22 [US3] `.claude/agents/source-filter.md` and its tier row
      research: rendering
      verify: DONE. .claude/agents/source-filter.md with its tier row (opus, medium) in test_agent_models; green
- [x] T23 [US3] calibration: negatives labeled, three runs, scored (R2); the contract amended until it passes
      research: rendering
      verify: DONE. R2: calibration passed three runs a leg at 19 of 20 or better; the contract amended until it passed
- [x] T24 [US2] the rule verdicts and the fetch of the uncached pages
      research: rendering
      verify: DONE. the rule verdicts applied and the uncached pages fetched; report shows 0 pages not yet judged
- [x] T25 [US2] the filter run over the uncited set; verdicts applied; pre-hold rows removed where not kept; SC-004 holds
      research: rendering
      verify: DONE. the filter ran over the whole uncited set; make uncited DO=report: 0 not yet judged, 1085 kept, 1759 not kept, each URL one verdict
- [ ] T26 [US2] the kept pages archived (plan D8)
      research: rendering

## Phase 4 - write-ups and the Uncited part (US4; FR-012 - FR-014)

- [x] T30 [US4] `KIND=uncited` in `make reserve`; `_record_units`/`_check_bundle` know `040-uncited-works/`; `make
      cite-uncited`; tests (plan D9, D11)
      research: rendering
      verify: DONE. make reserve KIND=uncited; _record_units and _check_bundle know 040-uncited-works; make cite-uncited; test_reserve_prefix, test_check_bundle and test_uncited green
- [x] T31 [US4] the build: the Uncited part, its refusals (canon link, cited uncited entry); tests (plan D3, D10)
      research: rendering
      verify: DONE. the build's Uncited sources part and its refusals (canon link, cited uncited entry); test_record_uncited green
- [x] T32 [US4] the write-ups drafted and installed for every kept page
      research: rendering
      verify: DONE. every kept page written up: report shows 1091 written, 0 kept with no entry (5 entries carry a URL a check corrected)
- [ ] T33 [US4] `source-applicability` on every uncited entry; findings applied; SC-006 holds
      research: rendering

## Phase 5 - citation rules and sources no one can read (US6; FR-005, FR-019, FR-020)

- [x] T40 [US6] FR-005: the inventory table in the doctrine and its test; a tool for each mechanical rule without one,
      a gate-owed check for each non-mechanical rule without one
      research: rendering
      verify: DONE. the citation-rule inventory in docs/research-doctrine.md with tests/test_citation_rule_inventory.py green; each mechanical rule names its tool
- [x] T41 [US6] the push and the gate refuse a footnote citing a source FR-019 names with no recorded confirmation
      (needs 313's report)
      research: rendering
      verify: DONE. check-partial-citations.py run at the push (sync-with-main.sh) and by the gate; exits 0 on the tree; test_check_partial_citations green
- [ ] T42 [US6] the footnotes of FR-019's sources confirmed or removed (plan D14); record checks on every changed question
      research: rendering

## Phase 6 - the high-risk sources (US7; FR-021) - waits on the GM's downloads

- [ ] T50 [US7] each of the 22 ingested or reported not found; `source-reader` and `quote-check` on each; corrections
      applied or the source removed (T42's procedure); SC-009 holds
      research: rendering

## Phase 7 - close

- [ ] T60 `make done` green; the record gate answered; memory and docs updated
      research: rendering
