# Tasks - feature 399, record-check rounds by kind of edit

Every task changes review tooling; nothing physical is decided, so each is `research: rendering`.

## Occasions

- none: no map element, sheet or pop-up text changes - the feature changes when a record check is owed and when its loop
  goes to the round arbiter

## Tasks

- [x] T01 Kind C (plan D1, D2, D2b; FR-001, SC-001): `record_units.quotation_key`; quote-check answers keep `qkeys`; `apply_edits.Round` settles another check's blocks outside the quotation and claim; `make record-checked FIXED_BY=`; red-first tests replaying 0251's `-4` (settles) and 去辰 (owed) both ways
      research: rendering
      verify: DONE. DONE. test_apply_edits 26 passed (5 new: red on HEAD's scripts, green now - the 0251 locator settles both ways, the 去辰 rendering stays owed and its declaration is refused); test_record_owed 35 passed
- [x] T02 Kind B (plan D3-D5; FR-002 - FR-004, FR-006, SC-002, SC-003): the flag count in the check state at `returned`, the trip in `dispatch`, `continue` lets one more round; red-first seeded loop, also across a moved `origin/main`; the no-change NOT-READABLE repeat let through; a new footnote not held
      research: rendering
      verify: DONE. DONE. test_hm_checks 37 passed (5 new; 3 red on HEAD's hm_checks - the loop held though main moved each round, a pass starts clean, a no-change NOT-READABLE repeat is not held; a new footnote goes; flags read from real reply lines incl. a table row)
- [x] T03 Docs and land (FR-005): docs/guards.md row, the agent-facing words where a session records a hand fix (quote-check's answer step), make quick, make hooks-test, make docs, the feature report, the DIRECT push; tell the Money session
      research: rendering
      verify: DONE. DONE. make quick green on the rerun (754 passed; the first run hit quick's 15 s ceiling at load 9.5); make hooks-test green (guard-file suite isolated from a live guard-edit permit); make docs; report.md with For the GM; route DIRECT (no engine paths)
