# Tasks - feature 443, the work-budget tooling

## Occasions

- none for a map: the counters change no manifest (FR-004 proves it); no glyph, placement or record change. The `work-budget`
  agent's first dispatches are T05's two fixtures.

## Tasks

- [ ] T01 The counters and their attribution: `l7r/diagram/work_counts.py`, the sites in `_geom/primitives.py`, `_geom/indexes.py` and `overlap/registry.py`, every stage's candidate loops (`research/candidate-loops.md`), `driver._run_stages`' per-stage copy; no Python call added (D1-D3; FR-001, FR-002, SC-001)
      research: rendering
- [ ] T02 `make work-budget` and the standing record `dev/work-budget.md` with today's figures for every stage at 10, 20, 40 and 80 households; `make counters-inert` in `make done` (D4, D5; FR-003, FR-004, SC-001, SC-002, SC-004)
      research: rendering
- [ ] T03 The budget table `dev/work-budget.json`, `make budget-set` and `make budget-change`, the WORDS hook `budget-change-hooks.sh`, the table a guard file (D6; FR-005, SC-003)
      research: rendering
- [ ] T04 The ratchet `make work-budget-review` in the push, and the standing record printed by `make land` and `make speckit-todo` (D7, D8; FR-006, FR-007, SC-003, SC-004)
      research: rendering
- [ ] T05 The `work-budget` agent, `docs/work-budget-rubric.md`, `make work-budget-bundle MODE=budget|audit`, the two fixtures dispatched and their rulings held by a test (D9-D11; FR-008, FR-009, SC-005)
      research: rendering
- [ ] T06 `.specify/templates/phase-checklist.md` and `make land`'s refusal of a feature-444 `phase:` task with its checklist absent, short or unticked (D12; FR-010, SC-006)
      research: rendering
- [ ] T07 `dev/rust-tooling.md` and `make rust-tooling` in `make hooks-test`, over every tracked file and the Makefile's recipes (D13; FR-011, SC-007)
      research: rendering
- [ ] T08 `docs/guards.md`, `docs/reviews.md` and each target's help name every change; each guard proven to fire with it deleted; the 443-end bookend; `make feature-report F=443 WRITE=1` (FR-012, SC-008)
      research: rendering
