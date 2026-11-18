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
- [ ] T150 Phase 4 S7, the map page writer (ask:449-phase4-slices) Q13: interactive/page, place, raster, extents, notes, tags, sheet, dwellings, picture_diff, page_lit onto S3a's crate, the image crate for PIL and numpy (2,912 lines); interactive/__init__ deleted; what page.py writes today, the Mode A sheets' pages
      research: rendering
- [ ] T151 Phase 4 S8, labels (ask:449-phase4-slices) Q7: labels/* and work_counts (2,397 lines), shapely onto the geo crate, FR-002 binding what is written
      research: rendering
- [ ] T152 Phase 4 S9a, the Mode A model (ask:449-phase4-slices): buildings/*, compound_model, compound_parts, well_gear (1,480 lines)
      research: rendering
- [ ] T156 Phase 4 S11, the Mode A top and pytest's exit (ask:449-phase4-slices) Q6, Q9: compound*, the six pool .gen.py as one Rust sheet driver with a spec file per map, 335's harness.py, poolmaps, test_mode_a_sheets as Rust tests (2,253 lines); conftest, the __init__.py files, _scope, _gate_failures, _heap, _memory, collect_cost, collect_probe, test_operations_registry deleted (443); resvg pinned as a library
      research: rendering
- [ ] T157 Phase 4 S12, the pipeline (ask:449-phase4-slices) Q8: gencache, regen, pool_index, render_cache (1,764 lines), gencache's key the binary, the spec and the inputs read; rollcache, pipeline/codeid, pipeline/__init__, _census and _invocation deleted (1,006); make scatter-bases' deleted script, render_cache.replate_page and sync-with-main.sh's RENDER_CACHE_MOD fixed or removed
      research: rendering
- [ ] T158 Phase 4 S13, the deletion close (ask:449-phase4-slices) Q10: tools/claims.py and claims_context, claims_counters, claims_scope, claims_stale, tunables, gates/codeid.py, dead_closure, bundle_door, tools/__init__, l7r/diagram/__init__ deleted (2,443 lines), the claims re-keyed by claims carry, ruff, pyproject's list and the requirements files gone; the phase-4 close
      research: rendering
- [ ] T171 The notes census's entrance-board line and its freshness test (constitution XIV; found by T170): since feature 444 cut the tool's entrance-board branch, an entrance-seated notice board's census line reads a 250-ft farmhouse count, which feature 261 does not judge a board by - fix the line (the ways-out count ported onto the manifest, or the line left out for an entrance seat, the easier route named); restore the freshness test feature 444 dropped on a wrong label (feature 193 kept notes-census for it); regenerate the four hamlets' notes ROUTES (round arbiter, ask:set-down-449-pilot, 2026-11-17; the GM's to choose): (a) the ways-out count ported onto the manifest - keeps the fact in the four hamlets' notes; the count's Rust is `rust/parked/src/law/routes.rs`'s `departure_routes` over the manifest's `lanes` and `houses`, engine-side work; or (b) the line left out for an entrance-seated board - simpler, drops the fact.
      research: rendering
- [ ] T177 Six audit rules brought to their pages (constitution XIV; found by T175's and T176's claims rounds, DRIFTED): the notice board casts no shadow though 0190 measures it 10-11 ft high; a road refused when wider than its gate though 0088 draws the road at a compound's gate at its own width; arch_on_approach refuses a first arch 0220 lets move inward; gate_widths' fix text gives a width outside 0093's bands; no_precinct_enclosure's message calls a sanctuary fence a donation where 0223 draws none; lodging_entrances passes one door per joined block where 0097 and 0106 give each dwelling its own - each fixed in both the Python and the Rust copy, the pool sheets' verdicts measured before and after
      research: rendering
- [ ] GM review (make gm-reviewed F=449) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
