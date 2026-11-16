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
- [ ] T122 The idle-tests suite's waits in milliseconds: its fixture waits 1 to 4 s of real time a case (the timer counts awake time in real ticks), 35.0 s alone and the full hook run's longest suite, about 20 s of it waits; a model of the run's eight slots puts the run at 28 s with the suite at 15 s, against 44 s as run (2026-11-12, /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r5/profile.sh and the schedule model) (the GM 2026-11-12, pre-approved: "if you identify concrete targets with significant measured expected savings then go ahead and do them")
      research: rendering
      note: not landed - its plan review (BLOCKED, 2026-11-12) held it to the GM's condition: the suite alone fell from 35.0 s to about 17 s, but the full hook run did not move (52.1 s against 53.1 s and 54.1 s), so no significant saving in the loop he is speeding up; the change is kept as a patch until the run's real bound is found
- [ ] T138 Phase 3, the research search no task held (phase-3 census, 2026-11-12): research_search.py and semantic_index.py (520 lines), after T85 (both import archive in process)
      research: rendering
- [ ] T147 Phase 4 S3b, the uncited cluster (ask:449-phase4-slices): scripts/record/uncited, uncited_imports, archive_ops (1,623 lines); retires downloads.rs's by-path run of archive_ops.py inbox
      research: rendering
- [ ] T148 Phase 4 S5, the record's site (ask:449-phase4-slices): record/site, site_pages, site_links, money, citations, glossary, glossary_source, tools/record_asset, glossary_asset, footnote_census, source_tags_contract, scripts/gates/memo_check.py, pipeline/record_build (2,164 lines); retires push.rs's memo_check and record-build runs
      research: rendering
      note: owed from T144's plan review (2026-11-16), where S1's library has no caller: wiring a caller that printed a KeyError's str(e) keeps its quotes; and research::host's tabs and missing NFKC, against urlsplit, need their own decision once live fetch URLs reach it beside the blocked-domain list
- [ ] T149 Phase 4 S6, the registries and their readers (ask:449-phase4-slices) Q5: interactive/classes/*, compound_kinds/*, conditions, choices, entry_owed, check-entry-headings, open_questions (2,225 lines), the modal prose moved verbatim to one Markdown file per class and kind (the FR-002 ruled case, an old-to-new id map); owed_door, record_door and record_cache deleted (756)
      research: rendering
- [ ] T150 Phase 4 S7, the map page writer (ask:449-phase4-slices) Q13: interactive/page, place, raster, extents, notes, tags, sheet, dwellings, picture_diff, page_lit onto S3a's crate, the image crate for PIL and numpy (2,912 lines); interactive/__init__ deleted; what page.py writes today, the Mode A sheets' pages
      research: rendering
- [ ] T151 Phase 4 S8, labels (ask:449-phase4-slices) Q7: labels/* and work_counts (2,397 lines), shapely onto the geo crate, FR-002 binding what is written
      research: rendering
- [ ] T152 Phase 4 S9a, the Mode A model (ask:449-phase4-slices): buildings/*, compound_model, compound_parts, well_gear (1,480 lines)
      research: rendering
- [ ] T153 Phase 4 S9b, pack_audit's leaves (ask:449-phase4-slices): tagged, parse, grids, onmap, labels, marks_drawn, size_marks, sun, palette (1,586 lines)
      research: rendering
- [ ] T154 Phase 4 S10a, pack_audit's core (ask:449-phase4-slices): checks, shared, program_rules, roads, mapmatch (2,142 lines)
      research: rendering
- [ ] T155 Phase 4 S10b, pack_audit's registry (ask:449-phase4-slices): __init__, registry, report, __main__, notes_census, size_table, building_programs (1,123 lines); make pack-audit, notes-census, size-table and building-programs Rust
      research: rendering
- [ ] T156 Phase 4 S11, the Mode A top and pytest's exit (ask:449-phase4-slices) Q6, Q9: compound*, the six pool .gen.py as one Rust sheet driver with a spec file per map, 335's harness.py, poolmaps, test_mode_a_sheets as Rust tests (2,253 lines); conftest, the __init__.py files, _scope, _gate_failures, _heap, _memory, collect_cost, collect_probe, test_operations_registry deleted (443); resvg pinned as a library
      research: rendering
- [ ] T157 Phase 4 S12, the pipeline (ask:449-phase4-slices) Q8: gencache, regen, pool_index, render_cache (1,764 lines), gencache's key the binary, the spec and the inputs read; rollcache, pipeline/codeid, pipeline/__init__, _census and _invocation deleted (1,006); make scatter-bases' deleted script, render_cache.replate_page and sync-with-main.sh's RENDER_CACHE_MOD fixed or removed
      research: rendering
- [ ] T158 Phase 4 S13, the deletion close (ask:449-phase4-slices) Q10: tools/claims.py and claims_context, claims_counters, claims_scope, claims_stale, tunables, gates/codeid.py, dead_closure, bundle_door, tools/__init__, l7r/diagram/__init__ deleted (2,443 lines), the claims re-keyed by claims carry, ruff, pyproject's list and the requirements files gone; the phase-4 close
      research: rendering
- [ ] T159 The pre-review count check: make decide refuses a count (lines, cases, files ...) whose sentence carries no label, the plan review's commonest unreviewable return (request.md 2026-11-16)
      research: rendering
- [ ] T160 Compile and test speed, the GM's third approved proposal (request.md 2026-11-16), ordered last: first measure where compile and test time goes across a port task, then take any target with a significant measured saving
      research: rendering
- [ ] T161 The differential runner, the GM's second approved proposal (request.md 2026-11-16) enforced by tooling (the GM 2026-11-11, 'our tooling must enforce this'): one shared runner in the repository that keys each case by the inputs and code it runs and reruns after a fix only the cases whose key moved, the port briefs from T147 on using it
      research: rendering
- [ ] GM review (make gm-reviewed F=449) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
