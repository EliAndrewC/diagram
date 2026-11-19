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
- [ ] T152 Phase 4 S9a, the Mode A model (ask:449-phase4-slices): buildings/*, compound_model, compound_parts, well_gear (1,480 lines)
      research: rendering
- [ ] T156 Phase 4 S11, the Mode A top and pytest's exit (ask:449-phase4-slices) Q6, Q9: compound*, the six pool .gen.py as one Rust sheet driver with a spec file per map, 335's harness.py, poolmaps, test_mode_a_sheets as Rust tests (2,253 lines); conftest, the __init__.py files, _scope, _gate_failures, _heap, _memory, collect_cost, collect_probe, test_operations_registry deleted (443); resvg pinned as a library
      research: rendering
- [ ] T157 Phase 4 S12, the pipeline (ask:449-phase4-slices) Q8: gencache, regen, pool_index, render_cache (1,764 lines), gencache's key the binary, the spec and the inputs read; rollcache, pipeline/codeid, pipeline/__init__, _census and _invocation deleted (1,006); make scatter-bases' deleted script, render_cache.replate_page and sync-with-main.sh's RENDER_CACHE_MOD fixed or removed
      research: rendering
- [ ] T158 Phase 4 S13, the deletion close (ask:449-phase4-slices) Q10: tools/claims.py and claims_context, claims_counters, claims_scope, claims_stale, tunables, gates/codeid.py, dead_closure, bundle_door, tools/__init__, l7r/diagram/__init__ deleted (2,443 lines), the claims re-keyed by claims carry, ruff, pyproject's list and the requirements files gone; the phase-4 close
      research: rendering
- [ ] T195 Step 3a's last reader gaps T194 found, fixed before step 3b (the GM 2026-11-18: fix all known bugs in each step), in both copies with tests red first: a filled path's hole read as a filled part (Hoshigaoka's grove, one subpath inside another); an unfilled closed part's inside counted as ink; the audit's path walk keeping an arc by its end point, so the viewBox crop misses an arc's bulge; and 0242's drawing page, 222 bytes under its cap after T194's split, split again along its angle and wrap topics; and 0242's place rule ('beyond that the caption is tied to its feature by a thin leader line') linking 0330, where that clause's grounds now sit (quote-check, 2026-11-18); and from T194's impl-drift: subjects' 'which subjects carry ink' citing 0330's drawing page, not 0242, in both copies. Dropped 2026-11-19, the GM's question on the sub-pixel tail answered by root CLAUDE.md's 'a GUESS, UNRESEARCHED or CONVENTION value ... is a goal and a knob, never a target to defend' (escalation-check REWRITE): a dashed closed outline measured solid and a square-capped zero-length stroke in a turned group, which move no caption and contradict no research finding; from here a drift that moves no caption and contradicts no research finding is fixed by restating the claim, not the geometry; and the way weight (T187's impl-drift, CANNOT-TELL): WEIGHT_WAY 500 against WEIGHT_OBSTACLE 1000 lets a seat covering one building beat a seat crossing three ways, against 0242's 'a house or any other building ... is never covered while any other choice exists' - measured first (does any pool caption take a building-covering seat where a seat crossing only ways stands?), the scoring made to rule a building out while any other seat exists if it does, and the 500 recorded on 0242's drawing page as a calibration
      research: rendering
- [ ] T197 Record corrections the T187 checks found outside their change, in a record session (research/CLAUDE.md; each a citation that does not support its sentence, or a term a reader cannot place): 0004's main page - kotobank-inkyo cited for 'in much of the country' and for the heir's handing-over and leaving the heir's roof, which its quotation does not say (narrow the sentences or cite what does); okada-bitchu-2004 not matched verbatim in the 2026-10-02 archived text, its PDF uncached (checked by hand); 'Echizen' with no glossary term beside Bitchu and Nihonmatsu; 'divided-residence retirement' in kotobank-inkyo-3 unglossed; 0222's main page: 'small temple halls of the Edo period that have been measured run from about 21 to 35 ft on a side' against its own Chikusei 13 ft side hall and Ehime's ~32 by ~35 ft, and its 21 ft low end against the drawing page's 18 ft from Hie Shrine; 'a subsidiary hall, not one where a village gathered' unfootnoted; l7r-median-domain's citation line naming 'Hierarchies', where the hamlet headman's house is said; 0004's 'the furniture inside a gate' made plain; and T187's claims round's wording (each fix: claim, effect: none - restatements, not defects under constitution XIV): the well-curb claim moved from the Country shrine section to the magistracy's `well` row, the storehouse (W) 16 x 19 ft named a departure toward Yokota's larger store, the doorless tub's end order stated per facing, claims for docs/building-programs.md's sanctuary band and the magistracy `well` row's four figures; and that doc's `guest` row describing the county example's detached 40 x 42 ft guest house as 0091's drawing page does; 0222's main notes' chikusei-saishoji-yakushido 'ridge plaque' made 'ridge tag' as the drawing notes have it; research rows from T187's depiction round: how a shrine dwelling's kitchen is drawn (Hoshigaoka's stippled floor and hearth glyph - earth floor? kamado or irori?), and the sanctuary's vermilion fill and the gray strip before it, recorded on a drawing page as conventions or found; the retirement house's pop-ups (hamlet/retirement-house and choice/family_form--retirement_house) saying its size is not recorded, where 0028's drawing page gives Kakimochi's eight at 3 to 15 tsubo and one of 1820 at 7.7 by 4.6 m - a pop-up telling the reader wrong (modal-depiction, 2026-11-19); 0223's drawing page recording the approach fence (a guess, or a knob under its own rule, since 0223 attests Yasuda Hachiman's late-Edo approach fence) so the procedure's 'no fence along the approach' claim has its page (impl-drift, fix: claim)
      research: rendering
- [ ] T198 The step-3a caption placer measured against a work budget derived from first principles, before step 3b (the GM 2026-11-19, request.md: "if the 3a step is horribly inefficient then we might need to rip it out and restart  tomake it not terrible"): the Rust placer (rust/mode_a/src/labels/) counted - seats tried, obstacle queries, leader tests, per caption and per sheet - on the six pool sheets, its wall time beside the kept Python's; a budget derived on paper as feature 443/444 derive one (.specify/templates/derivation.md, judged SOUND by the work-budget agent); within the budget it stays, far over it (the derivation says how far) it is rebuilt from that derivation as phase tasks with the phase-source guard on, the GM told either way
      research: rendering
- [ ] T199 Feature 449's engine plan carries the GM's 2026-10-30 rule (specs/444-work-budget-program/request.md: "we are not trying to re-implement the same algorithms"), which the 2026-11-17 plan dropped: engine-plan.md, spec.md and plan.md say step 3b (the Mode A model: buildings, compound - T152) is rebuilt from a derivation as phase tasks, the phase-source guard refusing a read of the old Python while each runs, and step 4's pipeline stays a port only after a check that none of its modules does far more work than needed; the lockstep tests holding a Rust module to the Python's answers are retired as that Python is deleted, the module's tests then pinning research-backed behavior; the GM's words of 2026-11-19 quoted (request.md)
      research: rendering
- [ ] GM review (make gm-reviewed F=449) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
