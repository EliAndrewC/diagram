# Tasks - feature 378, a research feature ends with its findings checked against the code

Every task is tooling: nothing a map draws changes and no physical decision is made, so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [ ] T01 The reader (plan D1-D3, FR-001, FR-003): `scripts/record/impl_check.py` + `make impl-check F=<n>`
      research: rendering
      verify: tests/tooling/test_impl_check.py; make impl-check on real features (SC-003)
- [ ] T02 Held at every close (plan D4, FR-004): close_check.reasons asks it
      research: rendering
      verify: the closing-check test in test_impl_check.py; test_close_check.py green
- [ ] T03 The text (plan D5, FR-005, FR-006, FR-007): the template task, CLAUDE.md, research/CLAUDE.md, the seven open specs
      research: rendering
      verify: SC-004 - each carries the rule
- [ ] T05 Claimed units outside the hamlet scope (plan D6, FR-009): `tools/claims.py:claimed_outside` in `all_units`; the four claims it brings in checked by impl-drift
      research: rendering
      verify: tests/tools/test_claims.py (SC-005); make claims-owed lists none of the four after their check
- [ ] T04 Close: make done green (an engine file changed); the tooling tests and make hooks-test green; report; landed
      research: rendering
      verify: the push accepted
