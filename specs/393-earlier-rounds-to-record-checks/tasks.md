# Tasks - feature 393, earlier rounds to the record checks

Every task changes review tooling and agent contracts; nothing physical is decided, so each is `research: rendering`.

## Occasions

- none: no map element, sheet or pop-up text changes - the feature changes what a check's bundle carries and its contract

## Tasks

- [x] T01 The module and the bundlers (plan D1-D7; FR-001, FR-002, FR-004, FR-005): `scripts/record/earlier_rounds.py`; `check_bundle.with_earlier` on the question, key and intro bundles; `modal_bundle` per pop-up and the batched pointer
      research: rendering
      verify: DONE. tests/tooling/test_earlier_rounds.py 6 passed; test_check_bundle 33, test_modal_checks 19, test_popup_order 9 passed
- [x] T02 The contract paragraph (plan D8; FR-003): the same paragraph in the ten receiving agent files
      research: rendering
      verify: DONE. test_every_receiving_check_carries_the_same_earlier_rounds_paragraph green (one sha256 across the ten, round 3 confirmed); test_agent_sync 3 passed
- [x] T03 Gate and land (SC-004): make quick, make hooks-test, the feature report, the DIRECT push; tell the Money and Diagram backlog sessions
      research: rendering
      verify: DONE. make quick clean; make hooks-test 50 suites green; no engine paths, route DIRECT; report.md written
