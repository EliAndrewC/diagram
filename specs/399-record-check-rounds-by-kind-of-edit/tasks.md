# Tasks - feature 399, record-check rounds by kind of edit

Every task changes review tooling; nothing physical is decided, so each is `research: rendering`.

## Occasions

- none: no map element, sheet or pop-up text changes - the feature changes when a record check is owed and when its loop
  goes to the round arbiter

## Tasks

- [ ] T01 Kind C (plan D1, D2, D2b; FR-001, SC-001): `record_units.quotation_key`; quote-check answers keep `qkeys`; `apply_edits.Round` settles another check's blocks outside the quotation and claim; `make record-checked FIXED_BY=`; red-first tests replaying 0251's `-4` (settles) and 去辰 (owed) both ways
      research: rendering
      verify: tests/tooling/test_apply_edits.py and test_record_owed.py, red on HEAD for the new cases, green after
- [ ] T02 Kind B (plan D3-D5; FR-002 - FR-004, FR-006, SC-002, SC-003): the flag count in the check state at `returned`, the trip in `dispatch`, `continue` lets one more round; red-first seeded loop, also across a moved `origin/main`; the no-change NOT-READABLE repeat let through; a new footnote not held
      research: rendering
      verify: tests/tooling/test_hm_checks.py new cases red on HEAD, green after; make hooks-test
- [ ] T03 Docs and land (FR-005): docs/guards.md row, the agent-facing words where a session records a hand fix (quote-check's answer step), make quick, make hooks-test, make docs, the feature report, the DIRECT push; tell the Money session
      research: rendering
      verify: make quick clean, make hooks-test green, route DIRECT
