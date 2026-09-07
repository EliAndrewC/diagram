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
- [x] T08 `ci/incremental.py` planner + `ci/selection.py` plugin, with unit tests over synthetic coverage data (FR-010, FR-011)
      research: rendering
      verify: DONE. `incremental.py` (manifest by raw blob id, `changed`, `contexts_touching`, `import_time_change`, `plan` with six fallbacks, `prune`/`merge`/`save_baseline`, the command), `selection.py` (fixture contexts, `keep_set`, `fixture_graph`, the writer rule) and `gate_plugin.py` (the two-hook `-p` shim, D12); `tests/tooling/ci/test_incremental.py` 20 tests over synthetic sqlite data and plain fakes; both modules at 100% across the two test files (`make cov-file`)
- [x] T09 the Makefile wiring: contexts on, plan/merge/save-baseline, the run-log `mode`/`selected`, the ratchet and plausibility by mode, `make audit` (FR-009, FR-012, FR-013)
      research: rendering
      verify: DONE. `test`: plan before pytest, `--cov-context=test -p l7r.diagram.ci.gate_plugin` + `COVERAGE_CORE=ctrace` under COV_FLOORS, merge before the floors, save-baseline after green floors; `done`: the mode reaches the plausibility floor (absolute minimum on incremental), the run-log entry (`mode`, `selected`) and the ratchet (full runs only); `_gatecost` excludes incremental rows; `test-full` alone stays a full run (FROM_DONE); `idle-tests` passes INCREMENTAL=0; `make audit` shows mode and k/n. The recipe-comment backtick recursion (D13) found and fixed on the way
- [x] T10 the fixture-project proof, five shapes (FR-014, SC-004)
      research: rendering
      verify: DONE. `tests/tooling/test_incremental_gate.py`, 14 tests on a real git repo with an eight-test engine, through the real planner, plugin (xdist, ctrace, contexts) and merge, judged by `coverage report --fail-under=100`: (a) an uncovered line in a changed function FAILS and selects the fixture's readers too; (b) deleting the only covering test FAILS; (c) an unchanged module's line made unreachable FAILS; (d) a polder-only edit selects the 4 polder tests of 8 and the merge is 100%; (e) no baseline, conftest, manifest, tooling, import-time line and the fraction each force FULL; the baseline is never written by an incremental run; the sysmon core's context loss proved (D8)
- [x] T11 the first FULL gate with contexts: green, baseline saved, the context cost and baseline size recorded (FR-015)
      research: procedure
      verify: DONE. 2026-09-07 21:04, commit 714eaf21: gate green, 3,089 passed, 100% over 22,545 statements, baseline saved under `.git/gate-baseline/` (coverage.db 3.3 MB, tests.json 345 KB for 3,092 tests, manifest.json 59 KB). COST: pytest phase 1,099 s / whole gate 1,273 s (cold roll cache) against 424 s / 589 s the day before - the C tracer with contexts is 2.4-2.6x on a FULL run (research R6); four launches to get here (the `--full` flag eaten by the ci parser, the backtick recursion, the `-p` import-order coverage hole, the module count). THEN RE-TAKEN under the fast core with re-armed events (D8's second fix), 21:57, commit 67f67dbe: green, 3,072 passed, 100% over 22,558 statements, pytest phase 497 s / whole gate 664 s cold - the contexts cost 17% / 13% over the pre-feature run, against the C tracer's 2.4x; baseline 3.3 MB + 343 KB + 59 KB
- [x] T12 three incremental runs measured - polder-only, core placer, a tools module - selected counts and wall clock recorded (FR-015, SC-003)
      research: procedure
      verify: DONE, twice. Under the C tracer (research R7): polder 33 tests / 381 s, core 318 / 1,203 s, tools 11 / 437 s (that one polluted by the core probe overwriting every cache slot) - the core case WORSE than the old gate, which forced the fast-core fix. Under the fast core with re-armed events (R8, the numbers that ship): tools 11 of 3,072 / 32 s, polder 33 / 219 s, core 318 / 595 s, the full baseline 664 s; the old full gate 589 s. Each run green with the merged floors at 100%; each probe restored (tree clean)
- [x] T13 docs: `CLAUDE.md` (the gate's two settings become three), `docs/efficiency-tooling.md`, the interactive package `CLAUDE.md`, `dev/gate.md`; `make done` green; land GATED (SC-005)
      research: procedure
      verify: DONE. Root CLAUDE.md (the docs-only clause: content is data; the gate is incremental, with the measured numbers), docs/efficiency-tooling.md (rows in sections 1 and 2), the skill CLAUDE.md command map (`make done INCREMENTAL=0`), dev/gate.md, tests/CLAUDE.md, the ci package index (three new rows), the interactive package and registry indexes (the content files, the docstring tags); the memory file. Landed GATED (LOCAL-GATED) after a green `make done`
