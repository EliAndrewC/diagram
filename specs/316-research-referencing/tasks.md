# Tasks - feature 316, the implementation cross-referenced with the research, claim by claim

Every task is tooling, docstrings, or a check of code against research the record already holds: no rendering decision
changes, no map's output changes and no research pass is run (an uncovered decision is claimed UNRESEARCHED, spec Decisions
Recorded), so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes - docstrings and string-literal statements execute nothing; the walk-through
  page gains links, not plates; the claim checks are this feature's subject, owed by its own command

## Tasks

- [ ] T01 [US1] `l7r/diagram/tools/claims.py` - the grammar, units, inheritance, code fingerprints, the import-graph scope,
  coverage - with `tests/tools/test_claims.py` to 100% (FR-001, FR-002, FR-003, FR-004; plan D1-D3, D9)
      research: rendering
- [ ] T02 [US2] [US3] `scripts/_claims.py` - research fingerprints, the index, `owed`, `bundle`, `record`, `report`; Make
  targets `claims-owed`, `claims-bundle`, `claims-checked`, `claims-report`; `tests/tooling/test_claims_index.py` on fixture
  trees (FR-004, FR-005, FR-006, FR-007, FR-009, FR-011, SC-002; plan D4-D6)
      research: rendering
- [ ] T03 [US4] `scripts/claims-gate.sh` in `sync-with-main.sh` on both routes, `CLAIMS_OK`, the introduced/pre-existing rule;
  `scripts/test-claims-gate.sh` on the hooks-test roster (FR-010, SC-004; plan D7)
      research: rendering
- [ ] T04 [US1] The coverage test `tests/tooling/test_claims_coverage.py` (FR-002, FR-003, SC-001; plan D8)
      research: rendering
- [ ] T05 [US3] `.claude/agents/impl-drift.md`, its tier in `tests/test_agent_models.py`, the ledger lint; the seeded runs,
  three a leg (FR-008, SC-005; plan D11, D14)
      research: rendering
- [ ] T06 [US6] The claims written: writer agents per module group over the 241 modules, and the three procedure documents;
  every file that crosses 1,000 lines split; coverage green (FR-002, FR-003, FR-013; plan D12)
      research: rendering
- [ ] T07 [US6] The audit checked: `impl-drift` on every group's bundle; MISLABELED and UNCLAIMED applied to the claims and
  re-checked (two rounds at most); every verdict recorded; the report complete with nothing owed (FR-013, SC-003; plan D12)
      research: rendering
- [ ] T08 [US2] Feature 296 closed as superseded; its two findings DRIFTED in the index (FR-014, SC-007; plan D13)
      research: rendering
- [ ] T09 [US5] The walk-through renders each stage's and step's claims with links and verdicts; its test; the page rebuilt
  (FR-012, SC-006; plan D10)
      research: rendering
- [ ] T10 The doctrine: the engine dev loop, the research rules, the root guard table, `docs/guards.md`, `dev/reviews.md`
  (FR-015, SC-008; plan D15)
      research: rendering
- [ ] T11 `make done` green; the push (spec-wide)
      research: rendering
