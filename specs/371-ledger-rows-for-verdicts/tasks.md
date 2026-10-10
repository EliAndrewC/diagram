# Tasks: a ledger row for every pass of every check (feature 371)

**Input**: plan.md (D1-D6). Tooling only: no map changes.

## Occasions

- none: tooling only - no glyph, placement, map or sheet changes

## Phase 1 - the answer (test first)

- [x] T01 tests/tooling/test_ledger_owed.py written and seen RED; scripts/reviews/ledger_owed.py (D3, D5; FR-002, FR-003, FR-005)
      research: rendering
      verify: DONE. test_ledger_owed 10 passed (seen red before ledger_owed.py existed)
- [x] T02 ledger_lint.CHECKS gains the modal checks and source-filter (D2; FR-001)
      research: rendering
      verify: DONE. ledger_lint on dev/review-ledger.md exit 0 with the four new checks; its tests green

## Phase 2 - the log

- [x] T03 hm_checks.py logs every check's pass with its cells (D1; FR-001); its tests (D5)
      research: rendering
      verify: DONE. test_hm_checks 14 passed, test_review_cost 3 passed; segments verified on a self-resumed agent's transcript (2 returns, 2 segments); make hooks-test green

## Phase 3 - where it runs, and the record

- [x] T04 ledger-hooks.sh reports at commit; sync-with-main.sh refuses at the push with LEDGER_ROWS_OK; make ledger-owed (D4; FR-004); the hook suites (D5)
      research: rendering
      verify: DONE. test-ledger-hooks section 6 green; test-sync-with-main 119 checks green incl. section 17; make ledger-owed runs
- [x] T05 CLAUDE.md, docs/guards.md, docs/reviews.md (D6)
      research: rendering
      verify: DONE. CLAUDE.md ledger-hooks row, docs/guards.md row, docs/reviews.md paragraph read back
- [ ] T06 the gate green; this feature's own checks' passes have their rows (SC-001..SC-004)
      research: rendering
      verify: make done green; make ledger-owed lists nothing for this clone
