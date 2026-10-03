# Tasks - feature 316, the implementation cross-referenced with the research, claim by claim

Every task is tooling, docstrings, or a check of code against research the record already holds: no rendering decision
changes, no map's output changes and no research pass is run (an uncovered decision is claimed UNRESEARCHED, spec Decisions
Recorded), so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes - docstrings and string-literal statements execute nothing; the walk-through
  page gains links, not plates; the claim checks are this feature's subject, owed by its own command

## Tasks

- [x] T01 [US1] `l7r/diagram/tools/claims.py` - the grammar, units, inheritance, code fingerprints, the import-graph scope,
  coverage - with `tests/tools/test_claims.py` to 100% (FR-001, FR-002, FR-003, FR-004; plan D1-D3, D9)
      research: rendering
      verify: DONE. claims.py at 100% (tests/tools/test_claims.py, 34 cases); scope 245 modules; coverage 4.2 s (R1, R2)
- [x] T02 [US2] [US3] `scripts/_claims.py` - research fingerprints, the index, `owed`, `bundle`, `record`, `report`; Make
  targets `claims-owed`, `claims-bundle`, `claims-checked`, `claims-report`; `tests/tooling/test_claims_index.py` on fixture
  trees (FR-004, FR-005, FR-006, FR-007, FR-009, FR-011, SC-002; plan D4-D6)
      research: rendering
      verify: DONE. scripts/_claims.py owed/bundle/record/report/coverage; test_claims_index.py 10 cases on fixture trees; Make targets claims-owed/-bundle/-checked/-report/-coverage
- [x] T03 [US4] `scripts/claims-gate.sh` in `sync-with-main.sh` on both routes, `CLAIMS_OK`, the introduced/pre-existing rule;
  `scripts/test-claims-gate.sh` on the hooks-test roster (FR-010, SC-004; plan D7)
      research: rendering
      verify: DONE. claims-gate.sh on both routes in sync-with-main.sh; test-claims-gate.sh 11/11, proven red with the refusal removed; on the hooks-test roster
- [x] T04 [US1] The coverage test `tests/tooling/test_claims_coverage.py` (FR-002, FR-003, SC-001; plan D8)
      research: rendering
      verify: DONE. tests/tooling/test_claims_coverage.py over claims.all_units; make claims-coverage reports every unit claimed
- [x] T05 [US3] `.claude/agents/impl-drift.md`, its tier in `tests/test_agent_models.py`, the ledger lint; the seeded runs,
  three a leg (FR-008, SC-005; plan D11, D14)
      research: rendering
      verify: DONE. impl-drift.md (opus/medium, omitClaudeMd), tier table, ledger lint, bundle guard; seeded runs 3 a leg: 3 seeds 3/3, the drifted seed 1/3 then 3/3 after the named-mismatch rule (R7)
- [x] T06 [US6] The claims written: writer agents per module group over the 245 modules, and the three procedure documents;
  every file that crosses 1,000 lines split; coverage green (FR-002, FR-003, FR-013; plan D12)
      research: rendering
      verify: DONE. 15 writer agents over 245 modules and the procedures; five files split at the bar (R4); coverage green; no executable code changed (R3)
- [x] T07 [US6] The audit checked: `impl-drift` on every group's bundle; MISLABELED and UNCLAIMED applied to the claims and
  re-checked (two rounds at most); every verdict recorded; the report complete with nothing owed (FR-013, SC-003; plan D12)
      research: rendering
      verify: DONE. round 1: 44 batches, round 2: 12; 419 findings applied to the claims; index 5,558 claims, owed 0 (R6)
- [x] T08 [US2] Feature 296 closed as superseded; its two findings DRIFTED in the index (FR-014, SC-007; plan D13)
      research: rendering
      verify: DONE. 296 spec SUPERSEDED by 316; seat_rows#row farm faces its street and #far-row dry-field share DRIFTED in the index (R10)
- [x] T09 [US5] The walk-through renders each stage's and step's claims with links and verdicts; its test; the page rebuilt
  (FR-012, SC-006; plan D10)
      research: rendering
      verify: DONE. walk-through renders each stage's and step's research with links and verdicts; test_every_stage_and_every_step_states_its_research...; page rebuilt (140 research lists)
- [x] T10 The doctrine: the engine dev loop, the research rules, the root guard table, `docs/guards.md`, `dev/reviews.md`
  (FR-015, SC-008; plan D15)
      research: rendering
      verify: DONE. engine dev loop, research CLAUDE.md, root guard table, docs/guards.md, dev/reviews.md
- [x] T11 `make done` green; the push (spec-wide)
      research: rendering
      verify: DONE. make done green (the whole suite, every pool map; 2026-10-03); the push follows
