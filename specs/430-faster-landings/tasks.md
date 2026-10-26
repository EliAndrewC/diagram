# Tasks - feature 430, faster landings

## Occasions

- none: no map, sheet, glyph or placement changes (tooling only)

## Tasks

- [ ] T01 Pool manifests keep the gate incremental, their readers selected; the readers rule in one engine module `make quick` shares; the 11 `inashiro.json` replays select every test their run failed (D1; FR-001, FR-009; `l7r/diagram/ci/incremental.py`, `l7r/diagram/ci/pool_readers.py`, `scripts/gates/pool-readers.py`)
      research: rendering
- [ ] T02 The test tree's non-module files: a doc adds nothing, a top-level file plans full, another selects its directory's tests and the tests naming it; SC-001's 12 replays plan incremental, the 4 top-level and the 3 configuration ones plan full (D2; FR-002, FR-009, SC-001; `l7r/diagram/ci/incremental.py`)
      research: rendering
- [ ] T03 The coverage check asks every line of each changed module with the floor's tests, the floor's carried coverage honored; the replays of SC-002 measured against their gates (D3; FR-003, FR-003a, FR-009, SC-002; `scripts/gates/cover_changed.py`)
      research: rendering
- [ ] T04 The push gates: nothing to judge exits at once, a pass cached on the delta's content, the gates side by side with every refusal reported; today's pushes replayed (D4; FR-004, FR-009, SC-003; `scripts/gates/push_gates.py`, the three `*-gate.sh`, `scripts/sync-with-main.sh`)
      research: rendering
- [ ] T05 The plan-lint before every plan review bundle: labeled figures, the red exit, an approach block per task; an approach block that decides nothing owes no review (D5; FR-005, SC-004; `scripts/gates/plan_lint.py`, `scripts/gates/plan_sections.py`, `scripts/gates/plan_gate.py`)
      research: rendering
- [ ] T06 A known drift admitted, recorded by `make claims-known` (run by `make land`) and listed in `make gm-review`; a triage of 3 or fewer claims goes to impl-drift, the skip on the ledger (D6; FR-006, SC-005; `scripts/record/claims_carry.py`, `scripts/record/claims.py`, `scripts/land.py`, Makefile)
      research: rendering
- [ ] T07 `make decide` and `make plan-delta` name an owed claims triage to dispatch beside the review; the guard test that decide-first lets it through and holds impl-drift (D7; FR-007; `scripts/gates/plan_gate.py`, `tests/hooks/test-check-bundle-hooks.sh`)
      research: rendering
- [ ] T08 Close: `make feature-report F=430 WRITE=1`, the report's measurements against SC-001 to SC-006
      research: rendering
- [ ] GM review (make gm-reviewed F=430) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
