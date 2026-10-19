# Tasks - feature 393, earlier rounds to the record checks

Every task changes review tooling and agent contracts; nothing physical is decided, so each is `research: rendering`.

## Occasions

- none: no map element, sheet or pop-up text changes - the feature changes what a check's bundle carries and its contract

## Tasks

- [ ] T01 The module and the bundlers (plan D1-D7; FR-001, FR-002, FR-004, FR-005): `scripts/record/earlier_rounds.py`; `check_bundle.with_earlier` on the question, key and intro bundles; `modal_bundle` per pop-up and the batched pointer
      research: rendering
      verify: tests/tooling/test_earlier_rounds.py green (SC-001, SC-002); test_check_bundle, test_modal_checks, test_popup_order green
- [ ] T02 The contract paragraph (plan D8; FR-003): the same paragraph in the ten receiving agent files
      research: rendering
      verify: the paragraph test green (SC-003); test_agent_sync green
- [ ] T03 Gate and land (SC-004): make quick, make hooks-test, the feature report, the DIRECT push; tell the Money and Diagram backlog sessions
      research: rendering
      verify: make quick and make hooks-test green; pushed
- [ ] GM review (make gm-reviewed F=393) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
