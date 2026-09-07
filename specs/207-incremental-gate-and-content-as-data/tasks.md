# Tasks - 207 The incremental gate, and content as data

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Every task is `research: rendering` or
`research: procedure` - tooling, nothing physical.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: procedure
      verify: DONE. FAITHFUL at round 3 (round 1: `name`/`covers` were kept as attributes on a ground true only of `key`, and the audit's 1.5 KB threshold missed five phrases; round 2: FR-005a's KEEP clause and FR-004's list disagreed with R2)
- [x] T02 the reference page, the pool index and the placement-stages page captured BEFORE any move (FR-008's baseline)
      research: procedure
      verify: DONE. scratchpad/before207/: inashiro.html (7.97 MB), index.html, hamlet-placement.html and the 13 per-stage pages (`make placement-stages`, 3m33s)
- [x] T03 `glossary.json` + loader (FR-001); `siblings.json` + loader (FR-002); `place.json` + loader (FR-004)
      research: rendering
      verify: DONE. assets/glossary.json, siblings.json (two shared texts, 21 pairs, `@` references), place.json (the hamlet's three demographic figures as format fields, asserted equal at dump time); `content.py` the loader with the why; each module keeps the names its consumers use
- [x] T04 `Name:`/`Covers:`/`Label:`/`Sources:`/`Entry:` docstring tags: the parser, `Kind.feature()`, the 51 classes rewritten by an asserted script (FR-003); `assets/page-text.json` + the loaders in `page.py` and `_base.py` (FR-005a)
      research: rendering
      verify: DONE. 51 classes rewritten by AST (each had exactly the six attributes; `key` alone stays); `_base.py` `_DATA_TAGS` required by `Kind.feature()` with the class named; page-text.json holds the two lead-ins, the convention lead, the four label phrases and both rulings lists; the 51-class snapshot test green
- [x] T05 the notes file and the pool-index stylesheet (FR-005)
      research: rendering
      verify: DONE. tools/placement_stages_notes.json (35 stages), pipeline/pool_index.css + pool_index_text.json (the tree banners asserted against `poolmaps`' two tree names at import)
- [x] T06 the asset definition widened: gate-stamp `page` area, the render fingerprint, `test_measured_surface.py`; `ci delta` and the engine key proven blind to a content edit (FR-006, SC-001)
      research: rendering
      verify: DONE. gate-stamp `page` area is `assets/*`; `render_cache.engine_fingerprint` hashes every file in interactive/assets/; test_measured_surface asserts the six assets and that the gate's area holds no `.json`; `ci/delta.is_engine` needed no change (`l7r/**/*.py` only) - the already-verified and warm-cache halves of SC-001 are measured after the baseline gate (T11)
- [x] T07 FR-008: the three pages regenerated and diffed byte-for-byte against T02's capture (SC-002)
      research: procedure
      verify: DONE. inashiro.html IDENTICAL (7.97 MB), pool/index.html IDENTICAL (after the stylesheet's leading newline was kept - the first regeneration differed at byte 170), hamlet-placement.html and all 13 stage pages IDENTICAL
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
