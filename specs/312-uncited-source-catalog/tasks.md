# Tasks - feature 312, uncited-source catalog

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md).

## Occasions

- none: the feature draws nothing on a map - no element new to a map, no glyph, no placement rule; the record's Sources
  gain a part, and the record checks on the new write-ups are owed by `make record-owed`.

## Phase 1 - blocked domains and banned citations (US1; FR-001 - FR-004)

- [ ] T01 [US1] `record/blocked.py`, `blocked-domains.json` (Grokipedia, the GM's approval quoted), `banned-citations.json`
      (empty); the loader's refusal of an unapproved entry; tests (plan D1)
      research: rendering
- [ ] T02 [US1] the Python fetch routes and stores refuse a blocked URL (`_sources`, `_archive`, `_archive_ops`); tests
      (plan D2)
      research: rendering
- [ ] T03 [US1] `blocked-fetch-hooks.sh` (WebFetch and Bash fetch invocations) with its test companion, registered in
      `.claude/settings.json` and `make hooks-test` (plan D2)
      research: rendering
- [ ] T04 [US1] the build refuses a blocked or banned citation (plan D3); fixtures; `docs/research-doctrine.md` and the
      registry front page point at the lists
      research: rendering

## Phase 2 - what was tried (US5; FR-015 - FR-018)

- [ ] T10 [US5] `scripts/_attempts.py` (seed, append, show), `make attempts`; `.gitattributes` union lines; tests (plan D12)
      research: rendering
- [ ] T11 [US5] `make source-pages` requires `Q=` and `SOUGHT=` and prints attempts and verdict first; `make
      source-outcome` appends the outcome; the WebFetch hook prints them as context; tests
      research: rendering
- [ ] T12 [US5] seed `source-attempts.jsonl` from the ledger; SC-007 count recorded in `research.md`
      research: rendering

## Phase 3 - the filter (US2, US3; FR-006 - FR-011, FR-022)

- [ ] T20 [US2] `scripts/_uncited.py` (set, rule, fetch, bundle, apply, score, report) and `make uncited`; tests (plan D4,
      D5, D7)
      research: rendering
- [ ] T21 [US2] FR-022: the 8 cited respellings checked
      research: rendering
- [ ] T22 [US3] `.claude/agents/source-filter.md` and its tier row
      research: rendering
- [ ] T23 [US3] calibration: negatives labeled, three runs, scored (R2); the contract amended until it passes
      research: rendering
- [ ] T24 [US2] the rule verdicts and the fetch of the uncached pages
      research: rendering
- [ ] T25 [US2] the filter run over the uncited set; verdicts applied; pre-hold rows removed where not kept; SC-004 holds
      research: rendering
- [ ] T26 [US2] the kept pages archived (plan D8)
      research: rendering

## Phase 4 - write-ups and the Uncited part (US4; FR-012 - FR-014)

- [ ] T30 [US4] `KIND=uncited` in `make reserve`; `_record_units`/`_check_bundle` know `040-uncited-works/`; `make
      cite-uncited`; tests (plan D9, D11)
      research: rendering
- [ ] T31 [US4] the build: the Uncited part, its refusals (canon link, cited uncited entry); tests (plan D3, D10)
      research: rendering
- [ ] T32 [US4] the write-ups drafted and installed for every kept page
      research: rendering
- [ ] T33 [US4] `source-applicability` on every uncited entry; findings applied; SC-006 holds
      research: rendering

## Phase 5 - citation rules and sources no one can read (US6; FR-005, FR-019, FR-020)

- [ ] T40 [US6] FR-005: the inventory table in the doctrine and its test; a tool for each mechanical rule without one
      research: rendering
- [ ] T41 [US6] the build refuses a footnote citing a `paywalled` or `never-read` source (needs 313's tags)
      research: rendering
- [ ] T42 [US6] the paywalled and never-read citations removed (plan D14); record checks on every changed question
      research: rendering

## Phase 6 - the high-risk sources (US7; FR-021) - waits on the GM's downloads

- [ ] T50 [US7] each of the 22 ingested or reported not found; `source-reader` and `quote-check` on each; corrections
      applied or the source removed (T42's procedure); SC-009 holds
      research: rendering

## Phase 7 - close

- [ ] T60 `make done` green; the record gate answered; memory and docs updated
      research: rendering
