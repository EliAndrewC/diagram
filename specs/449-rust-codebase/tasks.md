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
- [ ] T158 Phase 4 S13, the deletion close (ask:449-phase4-slices) Q10: tools/claims.py and claims_context, claims_counters, claims_scope, claims_stale, tunables, gates/codeid.py, dead_closure, bundle_door, tools/__init__, l7r/diagram/__init__ deleted (2,443 lines), the claims re-keyed by claims carry, ruff, pyproject's list and the requirements files gone; the phase-4 close; and the Python left with no importer or reader after T222 (found 2026-11-19): l7r/diagram/interactive/, work_counts.py and knobs.json (no reader found), the shapely and scipy dependencies, scripts/gates/codeid.py's split_ids, l7r/diagram/CLAUDE.md's row for a switches.py that does not exist, and the make-only guard's pattern for the deleted hamletgen/__main__.py - each deleted after a measured check that nothing reads it; and `l7r-gate cohort fresh-seed`, whose one outside caller was the deleted make probe (T230, 2026-11-19), deleted if nothing else calls it
      research: rendering
- [ ] T197 Record corrections the T187 checks found outside their change, in a record session (research/CLAUDE.md; each a citation that does not support its sentence, or a term a reader cannot place): 0004's main page - kotobank-inkyo cited for 'in much of the country' and for the heir's handing-over and leaving the heir's roof, which its quotation does not say (narrow the sentences or cite what does); okada-bitchu-2004 not matched verbatim in the 2026-10-02 archived text, its PDF uncached (checked by hand); 'Echizen' with no glossary term beside Bitchu and Nihonmatsu; 'divided-residence retirement' in kotobank-inkyo-3 unglossed; 0222's main page: 'small temple halls of the Edo period that have been measured run from about 21 to 35 ft on a side' against its own Chikusei 13 ft side hall and Ehime's ~32 by ~35 ft, and its 21 ft low end against the drawing page's 18 ft from Hie Shrine; 'a subsidiary hall, not one where a village gathered' unfootnoted; l7r-median-domain's citation line naming 'Hierarchies', where the hamlet headman's house is said; 0004's 'the furniture inside a gate' made plain; and T187's claims round's wording (each fix: claim, effect: none - restatements, not defects under constitution XIV): the well-curb claim moved from the Country shrine section to the magistracy's `well` row, the storehouse (W) 16 x 19 ft named a departure toward Yokota's larger store, the doorless tub's end order stated per facing, claims for docs/building-programs.md's sanctuary band and the magistracy `well` row's four figures; and that doc's `guest` row describing the county example's detached 40 x 42 ft guest house as 0091's drawing page does; 0222's main notes' chikusei-saishoji-yakushido 'ridge plaque' made 'ridge tag' as the drawing notes have it; research rows from T187's depiction round: how a shrine dwelling's kitchen is drawn (Hoshigaoka's stippled floor and hearth glyph - earth floor? kamado or irori?), and the sanctuary's vermilion fill and the gray strip before it, recorded on a drawing page as conventions or found; the retirement house's pop-ups (hamlet/retirement-house and choice/family_form--retirement_house) saying its size is not recorded, where 0028's drawing page gives Kakimochi's eight at 3 to 15 tsubo and one of 1820 at 7.7 by 4.6 m - a pop-up telling the reader wrong (modal-depiction, 2026-11-19); 0223's drawing page recording the approach fence (a guess, or a knob under its own rule, since 0223 attests Yasuda Hachiman's late-Edo approach fence) so the procedure's 'no fence along the approach' claim has its page (impl-drift, fix: claim)
      research: rendering
- [ ] T203 make decide's figure lint skips a task section's heading: T202's heading carried '704x its SOUND derived budget' with no measured label, decide passed it, and spec-fidelity returned NOT-REVIEWABLE for it (a review round spent on what the lint exists to catch - a check passing the bad, constitution XIV); the lint reads the section's heading line as it reads the Approach, with a test red on the old lint (2026-11-19) Also (T209, 2026-11-19): a count spelled as a word ("five captions") passed the lint unlabeled and drew a NOT-REVIEWABLE; the lint reads number words as figures.
      research: rendering
- [ ] T216 A make static coverage pass under-reported: during T212 (2026-11-19) the first coverage run after the lockstep tests were deleted reported 5 uncovered lines in rust/mode_a, and the next run named hundreds (report.rs, mapmatch, labels.rs, walls.rs) with no code change between - a check passing the bad (constitution XIV); find why (a stale profile, a cached result keyed too narrowly, a crate's coverage reused across a deletion) and fix it so the first run after a deletion reports what the deletion uncovered, with a test or a replay red on the old behavior
      research: rendering
- [ ] T226 A counted stage far under its budget (found by T224, 2026-11-19): waterward.polder counts 1,392 at 10 households against an accepted 28,232 (0.05x) with only three counters firing, so either the rebuild is that much cheaper or its counters miss work and the push's hold on it means nothing - a work-budget MODE AUDIT of the stage against its derivation, any uncounted work counted (red first), and the accepted figures re-read; dev/work-budget.md's stale run figures (hem at 40 households moved from 15,438 to 17,591) refreshed from make work-budget WRITE=1; and the waterward stage counted (T224 prints it uncounted because the review's reference roll has a pond, so no waterward runs): a reference roll on which it runs added to the review; lands before T158, the step's close (T224's plan review, 2026-11-19); and the polder drawing's three sizes with no claim of their own (impl-drift on T230, 2026-11-19): the sluice gate drawn 8 ft square, the pocket pond's 2.5 ft ring inside a 2.2 ft bund (draw_field claims it, draw_polder does not), the feeder canal 3.0 ft wide - each given its labeled claim
      research: rendering
- [ ] T228 The constitution's passages built on retired tools (found by T225, 2026-11-19): the retired command names in a sentence whose obligation stands are upkeep and take no version (the Governance section's versioning policy) - make roll-audit at the coverage-roll sentence, make perf-ab at the time-as-evidence sentence; but two passages describe obligations whose tools went with the Python engine - the one self-scoping make maps command (1.12.0/1.12.1 and its principle text) and the performance bookends (make perf LABEL= at a feature's start and end, make perf-report, make perf SCALING=1), which feature 443's work budgets and the push's work-budget review replaced - restated to today's tools where the record already holds the replacement, and put to the GM through escalation-check where an obligation would change
      research: rendering
- [ ] T234 The polder's sluice gate drawn as an 8 ft square (found by T226, 2026-11-19): 0179-water-gates-and-sluices-shuimen.drawing.html draws a sluice as a board and frame across its channel, spanning about 16 to 24 ft on a field channel, and T226 labeled the square DEVIATION with no reason for deviating - a drawn size the research contradicts (constitution XIV: a wrong outcome a reader of the map sees); the gate drawn as the page draws it, across the channel at its width, the claim restated to the page, the glyph-check it owes recorded deferred (feature 444 FR-023); lands before T158
      research: rendering
- [ ] T235 The polder waterward stage's budget prices work the Rust never does (T226's audit, 2026-11-20): its derivation (specs/444-work-budget-program/phases/waterward_polder.derivation.md) prices the old marsh drawing - rounding, waving, the clip to open ground, the keep-out grid, the marsh record - which the Rust draws as a plain filled polygon (feature 444's t42-brief.md item 10), so its first budget (17,813 at 10 households) sits 8x over the 2,125 the stage does and a regression of that size would pass as WITHIN; a MODE BUDGET re-derivation dropping the marsh term, judged by the work-budget agent, the budget raised or lowered by its SOUND verdict through the budget tools; lands before T158
      research: rendering
- [ ] GM review (make gm-reviewed F=449) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
