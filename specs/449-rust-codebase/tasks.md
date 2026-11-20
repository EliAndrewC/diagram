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
- [ ] T157 Phase 4 S12, the pipeline (ask:449-phase4-slices) Q8 - split by its scoping of 2026-11-19 into T218 (tooling fixes, T215 and T217 folded in), T219 (the blind derivation of the map walk and generation key), T220 (phase: the pool walk and the index), T221 (phase: one sheet driver and the generation cache) and T222 (phase: render-sync); rollcache, pipeline/codeid, pipeline/__init__, _census and _invocation deleted unported in the landing that removes each one's last importer; T157 is ticked when T218-T222 are
      research: rendering
- [ ] T158 Phase 4 S13, the deletion close (ask:449-phase4-slices) Q10: tools/claims.py and claims_context, claims_counters, claims_scope, claims_stale, tunables, gates/codeid.py, dead_closure, bundle_door, tools/__init__, l7r/diagram/__init__ deleted (2,443 lines), the claims re-keyed by claims carry, ruff, pyproject's list and the requirements files gone; the phase-4 close
      research: rendering
- [ ] T197 Record corrections the T187 checks found outside their change, in a record session (research/CLAUDE.md; each a citation that does not support its sentence, or a term a reader cannot place): 0004's main page - kotobank-inkyo cited for 'in much of the country' and for the heir's handing-over and leaving the heir's roof, which its quotation does not say (narrow the sentences or cite what does); okada-bitchu-2004 not matched verbatim in the 2026-10-02 archived text, its PDF uncached (checked by hand); 'Echizen' with no glossary term beside Bitchu and Nihonmatsu; 'divided-residence retirement' in kotobank-inkyo-3 unglossed; 0222's main page: 'small temple halls of the Edo period that have been measured run from about 21 to 35 ft on a side' against its own Chikusei 13 ft side hall and Ehime's ~32 by ~35 ft, and its 21 ft low end against the drawing page's 18 ft from Hie Shrine; 'a subsidiary hall, not one where a village gathered' unfootnoted; l7r-median-domain's citation line naming 'Hierarchies', where the hamlet headman's house is said; 0004's 'the furniture inside a gate' made plain; and T187's claims round's wording (each fix: claim, effect: none - restatements, not defects under constitution XIV): the well-curb claim moved from the Country shrine section to the magistracy's `well` row, the storehouse (W) 16 x 19 ft named a departure toward Yokota's larger store, the doorless tub's end order stated per facing, claims for docs/building-programs.md's sanctuary band and the magistracy `well` row's four figures; and that doc's `guest` row describing the county example's detached 40 x 42 ft guest house as 0091's drawing page does; 0222's main notes' chikusei-saishoji-yakushido 'ridge plaque' made 'ridge tag' as the drawing notes have it; research rows from T187's depiction round: how a shrine dwelling's kitchen is drawn (Hoshigaoka's stippled floor and hearth glyph - earth floor? kamado or irori?), and the sanctuary's vermilion fill and the gray strip before it, recorded on a drawing page as conventions or found; the retirement house's pop-ups (hamlet/retirement-house and choice/family_form--retirement_house) saying its size is not recorded, where 0028's drawing page gives Kakimochi's eight at 3 to 15 tsubo and one of 1820 at 7.7 by 4.6 m - a pop-up telling the reader wrong (modal-depiction, 2026-11-19); 0223's drawing page recording the approach fence (a guess, or a knob under its own rule, since 0223 attests Yasuda Hachiman's late-Edo approach fence) so the procedure's 'no fence along the approach' claim has its page (impl-drift, fix: claim)
      research: rendering
- [ ] T203 make decide's figure lint skips a task section's heading: T202's heading carried '704x its SOUND derived budget' with no measured label, decide passed it, and spec-fidelity returned NOT-REVIEWABLE for it (a review round spent on what the lint exists to catch - a check passing the bad, constitution XIV); the lint reads the section's heading line as it reads the Approach, with a test red on the old lint (2026-11-19) Also (T209, 2026-11-19): a count spelled as a word ("five captions") passed the lint unlabeled and drew a NOT-REVIEWABLE; the lint reads number words as figures.
      research: rendering
- [ ] T215 Folded into T218 (2026-11-19). make map with no GEN defaults to pool/hamlets/inashiro/inashiro.gen.py, which no longer exists (the hamlets are spec.json since feature 444) - a tool answering wrongly; the default points at a map that exists, or GEN is required with the refusal naming the forms (2026-11-19)
      research: rendering
- [ ] T216 A make static coverage pass under-reported: during T212 (2026-11-19) the first coverage run after the lockstep tests were deleted reported 5 uncovered lines in rust/mode_a, and the next run named hundreds (report.rs, mapmatch, labels.rs, walls.rs) with no code change between - a check passing the bad (constitution XIV); find why (a stale profile, a cached result keyed too narrowly, a crate's coverage reused across a deletion) and fix it so the first run after a deletion reports what the deletion uncovered, with a test or a replay red on the old behavior
      research: rendering
- [ ] T217 Folded into T218 (2026-11-19). Two make targets named but gone (found by T213, 2026-11-19, both broken before it): make done FULL=1 calls make perf-gate, which no Makefile target bears, so a full run fails there; and measure_hooks' messages (pinned by tests/hooks/test-measure-hooks.sh) still name make cov-file, deleted earlier - a tip naming a command that does not run (constitution XIV: a tool answering wrongly); each points at the target that does the job now, or the call is removed, with the suites updated
      research: rendering
- [ ] T221 T157d - phase: one sheet driver and the generation cache (T157's third landing): make map MAP=<folder|spec> runs any pool map (hamlets too) through one Rust driver with the key from T157b's derivation and the cache's publish semantics (atomic, meta last); the six .gen.py, sheet.py, regen.py, gencache.py, rollcache.py and _census.py deleted (raster's census hook and the Python class name in the Rust errors with them), bundle_door's is_current replaced by the Rust cache asked in process, tree/delta.rs and make_only_hooks' .gen.py patterns updated; and the engine's reported reads include the files it looked for and did not find (T219's derivation, 2026-11-19: the Mode A page writer records only files that exist, so a looked-for file created later - a modal text - leaves its sheet cached and stale), a test red first; and a read first reported on a miss is hashed before the engine runs, or held by the racy-file rule against the engine's start, so a file changed while the engine read it is never recorded with a digest of content the entry was not built from (T219's second judgment, 2026-11-19)
      research: rendering
      phase: pipeline
      derivation: specs/449-rust-codebase/derivations/T219-pipeline.md
      old-code: l7r/diagram/pipeline/*.py l7r/diagram/pipeline/pool_index.css l7r/diagram/pipeline/pool_index_text.json
- [ ] T222 T157e - phase: render-sync rebuilt (T157's fourth landing): render-sync on main walks the pool with T157c's walk and keys each map with T157d's key, so a spec edit alone re-renders its map (today a compound spec edit leaves main's svg, png and page stale - found by T157's scoping, 2026-11-19); sync-with-main.sh calls the Rust and the record site directly; render_cache.py, record_build.py, pipeline/codeid.py, _invocation.py, pipeline/__init__.py, buildings/__init__.py and poolmaps.py deleted; pipeline/CLAUDE.md and dev/cache.md updated; the hamlets' png and page, which the Rust driver does not write, recorded against feature 444's open row; and pool_index.py, pool_index.css and pool_index_text.json deleted with it (moved from T220, whose Rust index replaces them), with pyproject.toml's and _invocation.py's names for it; and gencache.py and _census.py deleted with render_cache.py, which imports them (moved from T221: deleting them first breaks main's render-sync); and the checks T221 left reading what no longer exists - measure probe's pool_changes (filters hamlets on .gen.py and compares <name>.json, so it matches nothing), preflight's roll-census read (nothing writes the census), land's L7R_ROLL_CENSUS filter - each moved onto the Rust cache or removed, red first where a check passed the bad; and whether one failing map should stop render-sync before the record site (T221's render-maps prerequisite) decided
      research: rendering
      phase: pipeline
      derivation: specs/449-rust-codebase/derivations/T219-pipeline.md
      old-code: l7r/diagram/pipeline/*.py l7r/diagram/pipeline/pool_index.css l7r/diagram/pipeline/pool_index_text.json
- [ ] T226 A counted stage far under its budget (found by T224, 2026-11-19): waterward.polder counts 1,392 at 10 households against an accepted 28,232 (0.05x) with only three counters firing, so either the rebuild is that much cheaper or its counters miss work and the push's hold on it means nothing - a work-budget MODE AUDIT of the stage against its derivation, any uncounted work counted (red first), and the accepted figures re-read; dev/work-budget.md's stale run figures (hem at 40 households moved from 15,438 to 17,591) refreshed from make work-budget WRITE=1; and the waterward stage counted (T224 prints it uncounted because the review's reference roll has a pond, so no waterward runs): a reference roll on which it runs added to the review; lands before T158, the step's close (T224's plan review, 2026-11-19)
      research: rendering
- [ ] T228 The constitution's passages built on retired tools (found by T225, 2026-11-19): the retired command names in a sentence whose obligation stands are upkeep and take no version (the Governance section's versioning policy) - make roll-audit at the coverage-roll sentence, make perf-ab at the time-as-evidence sentence; but two passages describe obligations whose tools went with the Python engine - the one self-scoping make maps command (1.12.0/1.12.1 and its principle text) and the performance bookends (make perf LABEL= at a feature's start and end, make perf-report, make perf SCALING=1), which feature 443's work budgets and the push's work-budget review replaced - restated to today's tools where the record already holds the replacement, and put to the GM through escalation-check where an obligation would change
      research: rendering
- [ ] T229 The guard sources held (ask:449-guard-sources-held, the round arbiter's ruling continue, 2026-11-19): the port moved what a guard refuses into rust/guard/src/ and the dispatcher, and guard_file_hooks::held did not follow, so an ordinary edit can weaken a guard - add to held every .rs under rust/guard/src/ but the test files (tests.rs and anything under a tests/ directory), rust/guard/Cargo.toml and scripts/hooks/l7r-guard.sh (held() holding its own list); leave tests/hooks/ suites and the Rust guard test files unheld; make guard-edit grants them; a suite case that an Edit of a guard source and of l7r-guard.sh is refused without a permit and an Edit of a guard test file and a suite passes, red first; lands after T221 (whose agent edits guard sources), before T222
      research: rendering
- [ ] GM review (make gm-reviewed F=449) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
