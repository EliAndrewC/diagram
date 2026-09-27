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

- [x] T01 FR-002 and FR-006 for `ways`, by 250's process
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. ways closed: 020 checked (16 notes; 1 DIFFERS and 6 PARTIAL fixed, 3 PARTIAL narrowed on the one re-check; 2 unfootnoted assertions answered - one absence note added, one sentence narrowed), 8 record-format findings applied (3 glossary terms, 2 variants), aze-jawiki limits rewritten, thepaper-night-gates HONEST; 020 split at the 20,000-byte cap into 020 and 025; FR-006 worklist 5 items, all FOOTNOTED
- [x] T02 FR-002 and FR-006 for `buildings`, by 250's process
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. buildings closed: question 210 (group 3 of 3) checked by quote-check and record-format, re-checked once; 9 registry write-ups judged by source-applicability (5 edited, 4 passed); 2 glossary terms (randori, Four Books and Five Classics); worklist 19 bare items, 19 FOOTNOTED
- [x] T03 FR-002 and FR-006 for `cities/river-cities`, by 250's process
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. cities/river-cities closed (session 2c, question 040): quote-check 13 citations + 2 absence notes, 10 PARTIAL narrowed or labeled as the page's reading, 1 DIFFERS fixed; record-format 4 VOCABULARY (2 edits, glossary coursing and hiro); one re-check on 5 notes all VERBATIM and SUPPORTS; FR-006 18 bare items, 14 footnoted, 4 reworded out
- [x] T04 FR-002 and FR-006 for `towns`, by 250's process
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. towns closed: quote-check and record-format on 040, 080, 090, 100, 130 (two groups), source-applicability APPLICABLE-WITH-LIMITS (honest) on thepaper-night-gates; group 2b: 090 3 PARTIAL narrowed to the quotes (1 more narrowed on re-check, then SUPPORTS), 130 1 PARTIAL resolved by labeling the no-per-farm-groves rule a guess with an absence statement, 2 glossary terms added (omotedana, dispersed settlement) and nucleus/nuclei made variants of nucleated; FR-006 14 items: 12 FOOTNOTED, 1 NOT-LOCATED (the 090 sentence rewritten this round, now footnoted), 1 LOCATED (070 hinomi-yagura sentence, outside the changed questions)
- [x] T05 FR-002 and FR-006 for `urban-features`, by 250's process
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. urban-features closed: group 2d checked 080 and 170 (4 checks + 1 re-check); 080 re-check 4/4 SUPPORTS, 0 unfootnoted; 170 4 SUPPORTS 1 PARTIAL fixed, 2 Mukoyama notes UNFETCHABLE publicly (read from the GM's copy); 4 glossary terms added; FR-006: 87 bare items, 79 FOOTNOTED, 2 LOCATED, 4 NOT-LOCATED, 1 AMBIGUOUS, 1 TOO-SHORT
- [x] T06 FR-006 for `cities/capitals`, by 250's process
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. cities/capitals group 4 of 4 (session 2d): questions 330 and 336 checked (quote-check x2, record-format x2), 21 EDIT blocks applied, 3 skipped (bracket glosses inside verbatim quotes), 2 labeled by hand; one re-check round (quote-check x2): 330 one clause narrowed, 336 clean; 2 glossary terms (Bunka, Morisada manko); re-check bundle's quote-verbatim cut fixed and tested; FR-006 worklist 92 bare items: 82 FOOTNOTED, 9 NOT-LOCATED, 1 TOO-SHORT

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
