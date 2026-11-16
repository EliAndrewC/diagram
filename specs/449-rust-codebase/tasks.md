# Tasks - feature 449, a Rust codebase (phase 1: the guards)

Ticked tasks are archived in `tasks-done.md` (feature 449 T142): `make tick` moves each ticked task there with its lines; this file holds the open ones.

Phases 2-4 are planned to the task in their own plan amendments (plan.md, Summary). Every task here is tooling: a map convention with
nothing behind it in physical reality, so each is `research: rendering`.

## Occasions

- none: phase 1 moves the guards that run on Claude Code's tool calls; no map feature, glyph, placement rule or research page changes.

## Tasks

### Setup (plan work breakdown 1)

### Foundational (plan work breakdown 2-4; blocks every guard)

### User Story 1 - every tool call answers at once (plan work breakdown 5, 7)

Each guard task, in the order below (the measured cost first, research R2, then the settings' order): the guard's decider in `rust/guard/src/guards/<guard>.rs` with its unit tests; its suite `tests/hooks/test-<guard>.sh` run with `HOOK` pointed at `l7r-guard --only <guard>` until every case passes (a case whose verdict changes is a constitution XIV fix, named in the commit - FR-002), the suite's own inline Python replaced in the same task (plan work breakdown 7); then, in ONE commit, the decider registered, `scripts/hooks/<guard>.sh` deleted and its `.claude/settings.json` entry removed (FR-003), landed with `make land-tooling`.

### User Story 1 - the suites' tooling and the close (plan work breakdown 6-8)

### User Story 2 - the gate is Rust (phase 2, opened 2026-11-08 by a plan amendment)

### Phase 3 (moved by the round arbiter's ruling `ask:449-hm-checks-route`, 2026-11-08; ported in one cut with their Python callers, FR-001)

## Dependencies

T001 -> T002 -> T003 -> T004 -> T005 -> the guard tasks (each depends on T002-T005, not on another guard) -> T050, T051 -> T052. A guard task whose decider needs a shared fact the library lacks extends T003's library in the same task.

## Parallel opportunities

The 44 guard tasks are independent of one another once T005 has landed: each touches its own decider, suite and settings entry. They land one at a time (each its own `make land-tooling`), since the settings file is shared.

## Implementation strategy

MVP: T001-T005 and the first guard, `pair-hooks` (T006): the dispatcher in every session with the slowest guard moved, its suite green, the call timed. Then the guards in order, each landed as it passes, so the session speeds up guard by guard.
- [ ] T85 Phase 4, the archive cluster with `interactive/record` (`ask:449-T81-slices`, moved by its test, each carrying the T065 clause and named at the phase-3 close): `quote_verbatim`, `sources`, `attempts`, `source_pages`, `reserve-prefix`, `apply_edits`, `uncited`, `uncited_imports`, `archive_ops`, `archive`, `entry_owed`, `record_prepass`, `style_prepass` (`ask:449-T88-bundles`); Rust `downloads`' by-path run of `reserve-prefix.py` ends here
      research: rendering
- [ ] T122 The idle-tests suite's waits in milliseconds: its fixture waits 1 to 4 s of real time a case (the timer counts awake time in real ticks), 35.0 s alone and the full hook run's longest suite, about 20 s of it waits; a model of the run's eight slots puts the run at 28 s with the suite at 15 s, against 44 s as run (2026-11-12, /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r5/profile.sh and the schedule model) (the GM 2026-11-12, pre-approved: "if you identify concrete targets with significant measured expected savings then go ahead and do them")
      research: rendering
      note: not landed - its plan review (BLOCKED, 2026-11-12) held it to the GM's condition: the suite alone fell from 35.0 s to about 17 s, but the full hook run did not move (52.1 s against 53.1 s and 54.1 s), so no significant saving in the loop he is speeding up; the change is kept as a patch until the run's real bound is found
- [ ] T128 Phase 4, the engine's pipeline package (l7r/diagram/pipeline/: gencache, regen, rollcache, poolmaps, pool_index, render_cache, record_build, with codeid.py going with its last Python caller), moved from phase 3 by ask:449-T90-scope beside the Mode A generators it runs; make map, make pool-index and make render-sync are planned as a whole here, and bundle_door.py's is_current verb leaves when it lands
      research: rendering
- [ ] T138 Phase 3, the research search no task held (phase-3 census, 2026-11-12): research_search.py and semantic_index.py (520 lines), after T85 (both import archive in process)
      research: rendering
- [ ] T140 Phase 4, the tools that reach Mode A or interactive/ (ask:449-phase3-remainder) Q1: building_programs, footnote_census, glossary_asset, notes_census, the pack_audit package, picture_diff, record_asset, source_tags_contract and scripts/gates/memo_check.py (each under the T065 clause, named at the phase-3 close), page_lit onto T85's one browser crate, tools/__init__.py, _census.py and work_counts.py with their last importer, 335's harness.py; and the pytest infrastructure's removal commit with the last kept pytest test (test_mode_a_sheets): conftest.py, the two __init__.py, _scope.py, _gate_failures.py, _heap.py, _memory.py, tooling_reuse_time.py (its three 383 commands retired)
      research: rendering
- [ ] T142 Ticked tasks archived out of tasks.md into tasks-done.md, as ticked tasks' plan sections already go to plan-done.md, and every reader of a feature's tasks reading both (the next free task number, the spec-kit state, the closing check, the tick's already-ticked and landed checks, the research boxes, the feature report): 449's tasks.md holds 131 ticked tasks of 137, about 63 KB read whole by every session and agent that opens it (the GM 2026-11-15: "please do that, because I imagine that will make our long-running featuers with tons of tasks much more token efficient")
      research: rendering
- [ ] GM review (make gm-reviewed F=449) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
