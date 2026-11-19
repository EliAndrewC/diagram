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
- [ ] T187 Step 1's third claims round's findings, fixed before step 3b (the GM 2026-11-18, request.md: "fix all known bugs in each step"): lodging_entrances lets an undivided barracks or long-house pass as 0097's common room, which 0097 gives the servants' quarters alone; the well curb sized 3 to 4 ft where 0196 gives about 4; the well-and-basin rule's label (0222 and 0196 now answer it); the basin's plan size and roof unclaimed; a doorless building's tub falling back to its end faces where 0100 puts the bath's on its yard side; the basin by the innermost arch (0222); the late-Edo fence along an approach (0223) unruled; the hilltop shrine's well (0196); the sanctuary band past its attested widths; the county example's claims impl-drift found drifted on 2026-11-18 (the hearing court drawn 80 x 26 against its page's 80 x 32; the servants' row claim's 76 ft against the 60 ft drawn; storehouse (W) at 16 x 19 against the page's ~12 x 18 and Yokota's pair; the divider gate's 'narrower than the main gate' rule against a gate rolled at 6 ft; the residence's massing, room order and veranda faces fixed where the pages make each a seeded knob), its stale comments (the gatehouse 18 x 12, the stables door's side, the servants' row's 76 ft), the gate-range roll drawing no range building, the vegetable garden size claim citing its page 0109, and the record's two disagreements it found (building-programs.md's divider width UNRESEARCHED against its claim's GUESS; 0104 §102 calling the service-side well accurate against 0105 §204's GUESS); the corridor's two ends leading to the house's door and privies, and its dotted edge drawn where it does not lie on a room wall (the round-trip's corridor glyph reviews); the size audits' measured rooms (the Matsue 10-mat zashiki and 8-mat next room, the Yokota house's rooms, JAANUS's 6-12-mat main room; their findings files hold the passages) quoted onto 0091 by a record session, so the room pop-ups may name them (the modal-research round of 2026-11-18 found no page carrying them, and they were recast as the plan's guess); the in-house corridor's drawing convention (a lighter strip with a dotted edge) recorded on 0091's drawing page, with what a samurai house's inner corridor looked like if a search finds it (the modal-depiction round of 2026-11-18); 0004's drawing page §13 saying a map's population is its DECLARED households times five, as §25's example and the code have it, and size_sentence's population claim naming the map's own population as the second override (T183's impl-drift, 2026-11-18); 0242's drawing page glossing who Yoeli is in 'Yoeli's scheme' (record-format, 2026-11-18); the room bands on the kinds' pages enforced for generated plans (since ask:449-T182-room-scope no check holds them - the registry's size_bands reads types.json alone); the guest room given a band of its own (45 x 25 ft on Ochiba, unbanded and not faulted; ask:449-T182-room-layout); the placer's choices the round-trip's glyph reviews questioned - the kitchen joining the house at the formal end, away from the family's, the storehouses' backs before the reception's garden face, and the guests' privy reached through the lord's quarters; and for a record session, 0220's innermost-arch label and 0222's hall size against the program band
      research: rendering
      research: rendering
- [ ] T195 Step 3a's last reader gaps T194 found, fixed before step 3b (the GM 2026-11-18: fix all known bugs in each step), in both copies with tests red first: a filled path's hole read as a filled part (Hoshigaoka's grove, one subpath inside another); an unfilled closed part's inside counted as ink; the audit's path walk keeping an arc by its end point, so the viewBox crop misses an arc's bulge; and 0242's drawing page, 222 bytes under its cap after T194's split, split again along its angle and wrap topics; and 0242's place rule ('beyond that the caption is tied to its feature by a thin leader line') linking 0330, where that clause's grounds now sit (quote-check, 2026-11-18); and from T194's impl-drift: subjects' 'which subjects carry ink' citing 0330's drawing page, not 0242, in both copies. Dropped 2026-11-19, the GM's question on the sub-pixel tail answered by root CLAUDE.md's 'a GUESS, UNRESEARCHED or CONVENTION value ... is a goal and a knob, never a target to defend' (escalation-check REWRITE): a dashed closed outline measured solid and a square-capped zero-length stroke in a turned group, which move no caption and contradict no research finding; from here a drift that moves no caption and contradicts no research finding is fixed by restating the claim, not the geometry
      research: rendering
- [ ] T196 A defect is a wrong outcome, not a difference (the GM 2026-11-19, request.md: "don't spent a lot of time 'fixing' things which are not actually wrong like things which are different than you expected but still work perfectly well and are in line with our research and produce maps which look fine"): the constitution's fix-as-we-go principle defines a defect - a map that reads wrong, a research finding contradicted, a check that passes the bad or refuses the good, a tool that crashes, hangs or answers wrongly - and says a difference from expectation, from the Python, from a convention's own wording or a gap no reader sees is not one; a claim the code does not literally match where the behavior is fine is fixed by restating the claim; impl-drift's verdicts name which fix (the claim or the code) and the visible effect; spec-fidelity rules leaving a difference within, not a narrowing; a found-and-left item is filed only with its visible effect or the finding it breaks; the plan template's Approach asks what a reader of the map would see differently; root CLAUDE.md, docs/gm-rulings.md and the review agents carry it
      research: rendering
- [ ] GM review (make gm-reviewed F=449) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
