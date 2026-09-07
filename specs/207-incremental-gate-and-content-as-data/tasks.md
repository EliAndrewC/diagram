# Tasks - 207 The incremental gate, and content as data

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Every task is `research: rendering` or
`research: procedure` - tooling, nothing physical.

- [ ] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: procedure
- [ ] T02 the reference page, the pool index and the placement-stages page captured BEFORE any move (FR-008's baseline)
      research: procedure
- [ ] T03 `glossary.json` + loader (FR-001); `siblings.json` + loader (FR-002); `place.json` + loader (FR-004)
      research: rendering
- [ ] T04 `Label:`/`Sources:`/`Entry:` docstring tags: the parser, `Kind.feature()`, the 51 classes rewritten by an asserted script (FR-003)
      research: rendering
- [ ] T05 the notes file and the pool-index stylesheet (FR-005)
      research: rendering
- [ ] T06 the asset definition widened: gate-stamp `page` area, the render fingerprint, `test_measured_surface.py`; `ci delta` and the engine key proven blind to a content edit (FR-006, SC-001)
      research: rendering
- [ ] T07 FR-008: the three pages regenerated and diffed byte-for-byte against T02's capture (SC-002)
      research: procedure
- [ ] T08 `ci/incremental.py` planner + `ci/selection.py` plugin, with unit tests over synthetic coverage data (FR-010, FR-011)
      research: rendering
- [ ] T09 the Makefile wiring: contexts on, plan/merge/save-baseline, the run-log `mode`/`selected`, the ratchet and plausibility by mode, `make audit` (FR-009, FR-012, FR-013)
      research: rendering
- [ ] T10 the fixture-project proof, five shapes (FR-014, SC-004)
      research: rendering
- [ ] T11 the first FULL gate with contexts: green, baseline saved, the context cost and baseline size recorded (FR-015)
      research: procedure
- [ ] T12 three incremental runs measured - polder-only, core placer, a tools module - selected counts and wall clock recorded (FR-015, SC-003)
      research: procedure
- [ ] T13 docs: `CLAUDE.md` (the gate's two settings become three), `docs/efficiency-tooling.md`, the interactive package `CLAUDE.md`, `dev/gate.md`; `make done` green; land GATED (SC-005)
      research: procedure
