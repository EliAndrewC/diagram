# Tasks - feature 265 (moved from feature 250, GM 2026-09-27)

## Phase 0 - the parallel runs (FR-010)

- [x] T12 `make reserve KIND=glossary|registry KEY=<key>` under a host-wide lock; `apply-edits` takes its glossary
      prefix from it; a test that races two allocations
      research: rendering
      verify: DONE. make reserve under a host-wide flock; test_reserve_prefix 3/3 incl. an 8-way race across 4 processes; apply-edits reserves
- [x] T13 A guard refuses a new glossary or registry file written without a reservation, with the command; its suite,
      proved red on a mutated copy; registered in the fallback form
      research: rendering
      verify: DONE. new-file-hooks.sh matched by kind, prefix and key; suite 13/13; 5 of 11 red with the refusal removed; registered in the fallback form
- [x] T14 The page briefs and the runner name the reservation and the queue's clone; `make page-queue` starts a queue
      in a sibling clone, and pulling a finished queue back rebuilds the generated pages
      research: rendering
      verify: DONE. page-queue.sh and pull-queue.sh; test_pull_queue 2/2 on real repos; plan review round 2 CLEAR

## Phase 1 - the pages (FR-002, FR-006, FR-007; was 250's T19)

- [ ] T01 FR-002 and FR-006 for `ways`, by 250's process
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited  - [ ] quote-check confirmed  - [ ] source-applicability confirmed
- [ ] T02 FR-002 and FR-006 for `buildings`, by 250's process
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited  - [ ] quote-check confirmed  - [ ] source-applicability confirmed
- [ ] T03 FR-002 and FR-006 for `cities/river-cities`, by 250's process
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited  - [ ] quote-check confirmed  - [ ] source-applicability confirmed
- [x] T04 FR-002 and FR-006 for `towns`, by 250's process
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. towns closed: quote-check and record-format on 040, 080, 090, 100, 130 (two groups), source-applicability APPLICABLE-WITH-LIMITS (honest) on thepaper-night-gates; group 2b: 090 3 PARTIAL narrowed to the quotes (1 more narrowed on re-check, then SUPPORTS), 130 1 PARTIAL resolved by labeling the no-per-farm-groves rule a guess with an absence statement, 2 glossary terms added (omotedana, dispersed settlement) and nucleus/nuclei made variants of nucleated; FR-006 14 items: 12 FOOTNOTED, 1 NOT-LOCATED (the 090 sentence rewritten this round, now footnoted), 1 LOCATED (070 hinomi-yagura sentence, outside the changed questions)
- [ ] T05 FR-002 and FR-006 for `urban-features`, by 250's process
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited  - [ ] quote-check confirmed  - [ ] source-applicability confirmed
- [ ] T06 FR-006 for `cities/capitals`, by 250's process
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited  - [ ] quote-check confirmed  - [ ] source-applicability confirmed

## Phase 2 - the sweeps (was 250's T20-T22)

- [ ] T07 FR-003, the rest of the vocabulary findings and the two variants (`ochiba`, `fire-gap`)
      research: rendering
- [ ] T08 FR-004, the history passages into comments
      research: rendering
- [ ] T09 FR-005, the registry's citation lines carry English titles, one mechanical sweep
      research: rendering

## Phase 3 - the close (was 250's T24, and 265's own)

- [ ] T10 FR-008, the download list grown at its end
      research: rendering
- [ ] T11 FR-007, the checks owed by what phases 1 and 2 changed (`quote-check` and `record-format` over the sections the sweeps changed, `source-applicability` over new keys); every `_entry_owed.py` pair answered; FR-009, the closing report; `make page-check`; the push
      research: rendering
