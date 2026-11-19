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
- [ ] T157 Phase 4 S12, the pipeline (ask:449-phase4-slices) Q8: gencache, regen, pool_index, render_cache (1,764 lines), gencache's key the binary, the spec and the inputs read; rollcache, pipeline/codeid, pipeline/__init__, _census and _invocation deleted (1,006); make scatter-bases' deleted script, render_cache.replate_page and sync-with-main.sh's RENDER_CACHE_MOD fixed or removed; and the six pool .gen.py become one Rust sheet driver with a spec file per map (from T156), the pool walk (poolmaps) rebuilt as a walk over each folder's contents (.spec.json, .compound.json, a hand .svg, a legacy .json), not ported: today's walk keys a map on its .gen.py, so pool/index.html lists 6 of the pool's maps, the 5 hamlets and 19 frozen exhibits missing (a defect, found by T156's scoping 2026-11-19)
      research: rendering
- [ ] T158 Phase 4 S13, the deletion close (ask:449-phase4-slices) Q10: tools/claims.py and claims_context, claims_counters, claims_scope, claims_stale, tunables, gates/codeid.py, dead_closure, bundle_door, tools/__init__, l7r/diagram/__init__ deleted (2,443 lines), the claims re-keyed by claims carry, ruff, pyproject's list and the requirements files gone; the phase-4 close
      research: rendering
- [ ] T197 Record corrections the T187 checks found outside their change, in a record session (research/CLAUDE.md; each a citation that does not support its sentence, or a term a reader cannot place): 0004's main page - kotobank-inkyo cited for 'in much of the country' and for the heir's handing-over and leaving the heir's roof, which its quotation does not say (narrow the sentences or cite what does); okada-bitchu-2004 not matched verbatim in the 2026-10-02 archived text, its PDF uncached (checked by hand); 'Echizen' with no glossary term beside Bitchu and Nihonmatsu; 'divided-residence retirement' in kotobank-inkyo-3 unglossed; 0222's main page: 'small temple halls of the Edo period that have been measured run from about 21 to 35 ft on a side' against its own Chikusei 13 ft side hall and Ehime's ~32 by ~35 ft, and its 21 ft low end against the drawing page's 18 ft from Hie Shrine; 'a subsidiary hall, not one where a village gathered' unfootnoted; l7r-median-domain's citation line naming 'Hierarchies', where the hamlet headman's house is said; 0004's 'the furniture inside a gate' made plain; and T187's claims round's wording (each fix: claim, effect: none - restatements, not defects under constitution XIV): the well-curb claim moved from the Country shrine section to the magistracy's `well` row, the storehouse (W) 16 x 19 ft named a departure toward Yokota's larger store, the doorless tub's end order stated per facing, claims for docs/building-programs.md's sanctuary band and the magistracy `well` row's four figures; and that doc's `guest` row describing the county example's detached 40 x 42 ft guest house as 0091's drawing page does; 0222's main notes' chikusei-saishoji-yakushido 'ridge plaque' made 'ridge tag' as the drawing notes have it; research rows from T187's depiction round: how a shrine dwelling's kitchen is drawn (Hoshigaoka's stippled floor and hearth glyph - earth floor? kamado or irori?), and the sanctuary's vermilion fill and the gray strip before it, recorded on a drawing page as conventions or found; the retirement house's pop-ups (hamlet/retirement-house and choice/family_form--retirement_house) saying its size is not recorded, where 0028's drawing page gives Kakimochi's eight at 3 to 15 tsubo and one of 1820 at 7.7 by 4.6 m - a pop-up telling the reader wrong (modal-depiction, 2026-11-19); 0223's drawing page recording the approach fence (a guess, or a knob under its own rule, since 0223 attests Yasuda Hachiman's late-Edo approach fence) so the procedure's 'no fence along the approach' claim has its page (impl-drift, fix: claim)
      research: rendering
- [ ] T203 make decide's figure lint skips a task section's heading: T202's heading carried '704x its SOUND derived budget' with no measured label, decide passed it, and spec-fidelity returned NOT-REVIEWABLE for it (a review round spent on what the lint exists to catch - a check passing the bad, constitution XIV); the lint reads the section's heading line as it reads the Approach, with a test red on the old lint (2026-11-19) Also (T209, 2026-11-19): a count spelled as a word ("five captions") passed the lint unlabeled and drew a NOT-REVIEWABLE; the lint reads number words as figures.
      research: rendering
- [ ] T215 make map with no GEN defaults to pool/hamlets/inashiro/inashiro.gen.py, which no longer exists (the hamlets are spec.json since feature 444) - a tool answering wrongly; the default points at a map that exists, or GEN is required with the refusal naming the forms (2026-11-19)
      research: rendering
- [ ] T216 A make static coverage pass under-reported: during T212 (2026-11-19) the first coverage run after the lockstep tests were deleted reported 5 uncovered lines in rust/mode_a, and the next run named hundreds (report.rs, mapmatch, labels.rs, walls.rs) with no code change between - a check passing the bad (constitution XIV); find why (a stale profile, a cached result keyed too narrowly, a crate's coverage reused across a deletion) and fix it so the first run after a deletion reports what the deletion uncovered, with a test or a replay red on the old behavior
      research: rendering
- [ ] T217 Two make targets named but gone (found by T213, 2026-11-19, both broken before it): make done FULL=1 calls make perf-gate, which no Makefile target bears, so a full run fails there; and measure_hooks' messages (pinned by tests/hooks/test-measure-hooks.sh) still name make cov-file, deleted earlier - a tip naming a command that does not run (constitution XIV: a tool answering wrongly); each points at the target that does the job now, or the call is removed, with the suites updated
      research: rendering
- [ ] GM review (make gm-reviewed F=449) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
