# Implementation Plan: the work-budget program - every phase rebuilt to an algorithmic budget

**Branch**: `444-work-budget-program` (no branch; `main` in the clone) | **Date**: 2026-10-28 | **Spec**: `spec.md`

**Input**: `spec.md` (the round arbiter's accept at the round cap, ask:444-spec-round-3), `request.md` (the design the GM approved,
steps 3 to 6). The instrument and the check are feature 443's, closed 2026-10-28.

## Summary

Step 3 first: every stage of `STAGES` gets a derivation on paper in the template's form (`.specify/templates/derivation.md`), a
MODE BUDGET verdict of SOUND from the `work-budget` agent, or the round arbiter's accept of its derivation (FR-013), and a budget in `dev/work-budget.json`; their sum and the whole roll's
exponent go to the GM through `escalation-check` - the program's CHECKPOINT, before any rebuild (FR-001, FR-002). Then the phases,
one task each in `STAGES` order, through the phase checklist (FR-003 to FR-006), the whole-table bundle before the first phase
lands (FR-007), the language decision after phases 1 and 2 (FR-008), and, if Rust, the ports proven first (FR-010 to FR-012).

This plan plans step 3 in full (T01-T06, with T07 and T08 added since: the pre-dispatch checks and the accept pin). The phase tasks are filed after the GM's checkpoint, each with its plan section and its
own plan review (`make task-add`, `make plan-delta`), because each phase's approach rests on the target he approves and on its own
derivation - planning them now would plan against a budget that does not yet exist.

## Technical Context

**Language/Version**: Python 3.14 (the language decision at step 5 may add Rust, FR-008, FR-010). **Testing**: the tests of
`scripts/budget_change.py`, `l7r/diagram/tools/work_budget.py` and `scripts/reviews/work_budget_bundle.py`; `make quick`, `make
hooks-test`. **Project Type**: the hamlet generator's engine; step 3 changes no engine code (one tooling change, D2).

**Single-artifact target**: step 3 rebuilds nothing; the phases' target is the reference hamlet `make work-budget` rolls
(`perf_snapshot.REFERENCE`, seed 25 and the snapshot's reference seeds, at 10/20/40/80 households).

## Performance bookends

Step 3 changes no code a roll runs. Each phase takes `make perf LABEL=444-<stage>-start` / `-end` in its own task (the phase
checklist's box 6 records `make perf-ab`); the program's opening record is `dev/work-budget.md` as 443 wrote it (run
`20261028T152105Z-45aa176ec9b8`).

## Constitution Check

- **I, II**: N/A - no UI in this repository. **III, IV**: N/A - no pool content or GM source moves in step 3.
- **V, VII-IX, XI**: N/A - no map, no setting prose in step 3; each phase's own section answers them.
- **VI**: PASS - each derivation passes the bundle's refusals (443 FR-008, T13) before its verdict; D2's tooling change has its
  tests and `make quick`.
- **X**: PASS - D2's changed lines owe 100% coverage.
- **XII**: PASS - a derivation's figures come from the stage's contract and the research claims that govern it; a figure no claim
  states is labeled a guess in the derivation's reason column.
- **XIII, XIV**: PASS - no regression is possible in step 3 (no engine code runs differently).
- **XVI**: PASS - the GM's words: the design, steps 3 to 6 (`request.md`); the checkpoint is his ("The GM approves the target").

## Decisions

**D1 - A derivation per stage, from its contract alone** (FR-001): `specs/444-work-budget-program/phases/<stage>.derivation.md`,
the template copied and filled. The CONTRACT is read from what the stage takes and leaves - its docstring, the `plan` fields it
reads, the manifest keys and registries it writes (`dev/placement.md`'s `STAGES` table and draw order), the research claims
that govern it (`make claims-report`'s rows for its modules) and the cohort properties it must keep (the cohort's checks that
read what it places, `cohort_audit`'s rules) - each a rule asked of a candidate before it is placed (S4), so each is a check
of the count - never from its loops or from `dev/work-budget.md`'s counts, which
the bundle's refusal keeps out of the judge's view and the session keeps out of the writing. The ALGORITHM is the minimal one for
that contract (rubric S1-S7); where the derivation finds today's output itself wasteful (a thing placed that a later stage drops),
it says so and the fix goes to the stage that owes it (the spec's Edge Cases).

**D2 - What a budget counts: the derivation's own items** (FR-001, the spec's Edge Cases): today `dev/work-budget.json` holds a
stage's `per_thing` and `make work-budget` multiplies it by the things the stage placed (`perf_profile.placed_counts`), which are
not the derivation's items (a derivation counts houses; the manifest counts every part of every house), and a stage that places
nothing (`seat`, `sink`) gets a budget of 0. So a budgeted stage also records its ITEMS at 20, 40 and 80 households
(`items_at_20`, `items_at_40`, `items_at_80`: the derivation's item count from the contract, 1 for a whole-stage figure), and its
budget at a size is `per_thing x items` at that size - S7's items x candidates x checks x slack. `make budget-set` requires
`ITEMS_AT_20=`, `ITEMS_AT_40=` and `ITEMS_AT_80=`; `make work-budget`'s ratio and the push's ratchet (`work_budget.held`) read them,
and refuse a budgeted or accepted row without them, naming the row and `make budget-change` - the placed-things product is retired,
not kept for older rows. A tooling change in `scripts/budget_change.py` and `l7r/diagram/tools/work_budget.py`, with its tests.

**D3 - The MODE BUDGET verdicts** (FR-001): each derivation is bundled (`make work-budget-bundle MODE=budget PHASE=<stage>
DERIVATION=<file>`) and dispatched to the typed `work-budget` agent once; its first line is saved beside the derivation as
`<stage>.verdict.txt` and its row written to the ledger. LOOSE or UNDERIVED: the derivation is corrected as the verdict states and
dispatched again; the third round on one stage owes the round arbiter's ruling first (the tripwire). SOUND: `make budget-set` pins it; the round arbiter's ACCEPT of the derivation pins it too (FR-013, the GM 2026-10-28), by its
trigger, `make budget-set ARBITER=ask:<id>`, bound to the derivation as it reads - a later change to a figure re-owes the arbiter. The agent is not a wave job (the GM's list, `scripts/container/append-system-prompt.md`), so the dispatches are plain
Agent calls, at most three in one message.

**D4 - Families, as 443 counted them** (the tasks' size): every stage of `STAGES` - 23, measured 2026-10-28 (the `STAGES` tuple of `l7r/diagram/hamletgen/driver.py`, the same list `dev/work-budget.json` holds and `tests/tooling/test_budget_change.py` keeps equal to it) - in the four families 443's T09-T12 used - water (6:
water_frame, field, sink, waterward, pond_stock, pond_bank), homesteads (7: seat, homesteads, appurtenances, burial, lane_wells,
sties, washing), ways (3: track, web, crossings), hinterland and frame (7: hinterland, woodland, windbreak, bamboo, frame, notice,
labels). One task per family, each landing its derivations, verdicts and budgets together.

**D5 - The checkpoint** (FR-002): the target is the sum of the 23 budgets at 40 households, and the whole roll's exponent (the
fit of the summed budgets at 20, 40 and 80 households); with it, the opening record's whole-roll figure and each stage's ratio of
today to budget (the counts are read only now, after every budget is pinned). The draft goes through `escalation-check`, then to
the GM in the turn's final message; his words set it with `make budget-program OPS_AT_40= EXPONENT= WORDS=` (logged in
`dev/work-budget-changes.jsonl`). No phase task is filed before. The draft names each stage pinned on the round arbiter's accept (FR-013) with its rounds and its totals' spread, as the
pin records them (`rounds`, `spread` in `dev/work-budget.json`), so a budget that rests on an accept never reads as a first-round SOUND.

## Task approaches

T01 D2's tooling; T02-T05 the four families' derivations, verdicts and budgets (D1, D3, D4); T06 the checkpoint (D5); amendment 3:
T10 the bundle's refusal of today's names, T11-T14 the four families re-derived greenfield (FR-015, FR-016), before T06.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T10 to T10 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
<!-- plan-archive: T11 to T11 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
<!-- plan-archive: T12 to T12 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
<!-- plan-archive: T13 to T13 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
<!-- plan-archive: T14 to T14 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
<!-- plan-archive: T06 to T06 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
## Project Structure

- Step 3: `specs/444-work-budget-program/phases/<stage>.derivation.md` and `<stage>.verdict.txt` for each of the 23 stages;
  `dev/work-budget.json`; T01's `scripts/budget_change.py`, `l7r/diagram/tools/work_budget.py` and their tests.
- After the checkpoint: one task per phase (FR-003), each with `phases/<stage>.md` from the phase checklist; `make
  work-budget-bundle MODE=table` before the first phase lands (FR-007); `research/language.md` after phases 1 and 2 (FR-008).

## Complexity Tracking

None.

<!-- plan-archive: T07 to T07 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->

<!-- plan-archive: T08 to T08 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->

<!-- plan-archive: T09 to T09 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->

<!-- plan-archive: T15 to T15 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
### T16 - phase: field, in Rust under the single-field cap, through the checklist (FR-003 to FR-006, FR-017, FR-018; step 4)

Occasions: settlement-review on the pool hamlets the rebuilt field moves (a map's form changes - its comb's basins, ditches and brook redrawn); glyph-check only if a glyph is redrawn.

### T16 Approach (checklist part A)

1. **The goal, in the world.** The comb field rebuilt to its greenfield derivation: the brook and its intake, the fan's outline, the comb's ditches and basins cut once with every rule asked before a basin is written, no repair pass.
2. **The constraints.** FR-003 to FR-006; rubric S1-S9; `phases/field_greenfield.derivation.md` and its budget, 23,988 at 40, exponent 0.79; the research its contract cites (0005, 0017, 0053, 0054, 0059); the manifest keys today's stage writes (FR-004).
3. **Where each comes from.** G: the GM, 2026-10-29 ("yes please do step 4 and then we can stop and assess how things are going"); the design's step 4.
4. **Do they describe the world here?** Every form the stage writes: the comb archetypes the reference spec rolls, and the polders, which get their own greenfield derivation and MODE BUDGET verdict before the rebuild, and a seed that draws one for the audit.
5. **The order.** After `water_frame`; the last of step 4, then the assessment with the GM.
6. **The exits.** Green: counted operations at most the budget at 40 and 80, `make cohort-landing` with no regressed seed and the fresh block's rate no worse, the claims round IN-STEP, the reviews owed, MODE AUDIT WITHIN, `phases/field.md`'s eight boxes ticked, all of the old field code - comb and polder - deleted. Red, over its budget: rebuilt again, or the budget raised with the GM's words (`make budget-change`, FR-006) - never set down, never an arbiter's accept; a stop to assess goes to the GM, as he asked ("then we can stop and assess how things are going").
7. **The search smell.** none
8. **The budget.** Several landings behind one task is not allowed - one landing; `make cohort` after each increment; one MODE AUDIT pass a round.
9. **Done, measured.** `make work-budget`: field's counted operations at 40 and 80 against 23,988 and 42,070.
10. **Before moving a constant.** The research page each figure cites, read before it moves.
11. **Before fitting things into room.** n/a

**Performance work?** yes - docs/performance-checklist.md's questions follow.

### T16 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** The field stage made about 1.3M Python calls at 40 households and counted 48,335 to 66,214 operations over the four seeds, measured 2026-10-28 (`make work-budget`, `dev/work-budget/20261028T152105Z-45aa176ec9b8.json`), its counted work led by segment crossings, the standing registry's conflicts and segment distances; box 4 adds `make perf-profile` and `make perf-fanout`.
2. **Removes work, or only moves it?** Removes it: the comb's angles read once a row, the cut basins clipped by the water index, a sharp point cut off by rule before the basin is written - no carve, settle or weld pass after.
3. **What do you expect it to save, and why?** The counted operations from today's (item 1) to at most the pinned budget at 40 (`dev/work-budget.json`), and the calls with them, the repair passes gone.
4. **How does the work grow with the settlement?** The rebuild is held to the budget's exponent, the pinned one in `dev/work-budget.json`.
5. **What did the before and after show, and under what conditions?** Recorded at box 6: `make work-budget` and `make perf-ab` against main.
6. **Did any map move, and does it still keep the research?** Yes - every comb map's basins and ditches move; the cohort, the claims round and settlement-review hold them to the research.



### T17 - FR-011's Rust tooling proven on a Rust fixture (amendment 4; before the first Rust phase lands)

Occasions: none (tooling: no map moves).

### T17 Approach (checklist part A)

(The round arbiter, 2026-10-30, ask:444-T17-rows-need-a-phase, Route A: T17 ticks with every row the fixture can prove; the four that need a real phase are T19's, and the refusal of a Rust phase while any row is unproven lands with T17.)

1. **The goal, in the world.** A Rust fixture crate - one PyO3 extension module built by maturin, a thin Python function calling it,
   a `///` doc comment carrying a `Research:` claim and a `Steps:` list - against which every row of `dev/rust-tooling.md` marked one
   for one, partial, rewritten or replaced is shown to FIRE: each check refuses a fixture written to break it, and passes the fixture
   written to keep it.
2. **The constraints.** FR-010 (the module's shape), FR-011 and FR-017 (proven before the first Rust phase); `dev/rust-tooling.md`'s
   rows and keys; the toolchain pinned in `scripts/container/setup-dev-env.sh` (its pinned versions: clippy, rustfmt, llvm-tools,
   cargo-llvm-cov, maturin).
3. **Where each comes from.** G: the GM, 2026-10-29 ("I want to modify the plan so that we don't end up doing any Python rewrites")
   and 2026-10-30 ("please complete those tooling fixes that are the prerequisites"); the design's section 7.
4. **Do they describe the world here?** The fixture is a stand-in, not a phase: it lives under `tests/fixtures/rust/` and is never
   imported by the engine.
5. **The order.** First of the Rust work: before the `water_frame` port and the field rebuild.
6. **The exits.** Green: every proven row's check named with the fixture case that fires it (a table beside `dev/rust-tooling.md`'s),
   `make hooks-test` and `make done` green. A row that cannot be proven goes to the round arbiter with what blocked it. Red: a row whose check cannot be made to fire on the fixture goes to the round arbiter (`make arbiter-ask`) with what blocked it.
7. **The search smell.** none
8. **The budget.** Rows land in groups as they are proven (the lint and format group; the caps; coverage; the code id and the
   claims reader; the guards); one landing a group.
9. **Done, measured.** Every row of `dev/rust-tooling.md` marked one for one, partial, rewritten or replaced (step 1's four kinds) marked
   proven, with its firing case.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no


### T18 - the field re-derived under the single-field cap (FR-018), its MODE BUDGET verdict

Occasions: none (a derivation and its verdict; no map moves until the field rebuild).

### T18 Approach (checklist part A)

1. **The goal, in the world.** The largest single paddy field the research finds for a settlement of this kind, as the field
   phase's contract (its cap and source), and `phases/field_greenfield.derivation.md` re-derived under it: a settlement whose
   farmland passes the cap draws more than one field.
2. **The constraints.** FR-018, FR-015, FR-016 (rubric S9); the research pass searches the record and the archive first
   (`make research-search`, feature 447); the findings of feature 447's field-size runs (`specs/447-semantic-index/research/t02-*`,
   `t04-validation.md`, `t06-validation-3.md`) as leads, each source written up and checked as the record's rules require.
3. **Where each comes from.** G: the GM, 2026-10-29 ("we can cap out at something approximating whatever that size is, and then
   larger settlements just have multiple fields").
4. **Do they describe the world here?** The cap is for the settlement kind the field draws: a hamlet's or village's comb field.
5. **The order.** Before the field rebuild; after or beside the tooling proof (no engine code).
6. **The exits.** Green: the cap and its source in the record, the derivation's MODE BUDGET SOUND; a figure above the standing pin
   (`dev/work-budget.json`) keeps that pin and is pinned only with the GM's words (`make budget-change`). Red: a derivation judged LOOSE or UNDERIVED twice, or a cap the research cannot settle, goes to the round arbiter (`make arbiter-ask`) with the verdicts.
7. **The search smell.** none
8. **The budget.** The research page through `make page-session`; one MODE BUDGET round a draft.
9. **Done, measured.** The verdict's figure at 40 and its exponent, beside the standing pin.
10. **Before moving a constant.** The research page the cap cites, read before it moves.
11. **Before fitting things into room.** n/a

**Performance work?** no


### T19 - phase: water_frame, its Rust port (FR-017; after the tooling proof)

Occasions: none unless a map moves (its rolls are the same derivation: none should).

### T19 Approach (checklist part A)

(The round arbiter, 2026-10-30, ask:444-T17-rows-need-a-phase, Route A: T19 also proves the four tooling rows T17 could not prove on the fixture - the cache audit, the overlap census's replacement, the change-selected tests' Python half, dead closure's public half - before its tick; `check-rust-tooling.py` refuses the port's landing until they are.)

1. **The goal, in the world.** `water_frame` in the extension module, written from `phases/water_frame_greenfield.derivation.md`
   (its derivation came out the same as today's code: rolls and writes, no search), the stage a thin Python function calling it.
2. **The constraints.** FR-010, FR-017; the derivation's Contract and its pinned budget (`dev/work-budget.json`); the phase-source guard holds its
   old code while this task runs.
3. **Where each comes from.** G: the GM, 2026-10-29 (FR-017: water_frame's Rust port a task of its own, landed before the feature
   closes).
4. **Do they describe the world here?** One stage, one derivation; the manifest keys it writes are today's.
5. **The order.** After the tooling proof; before the field rebuild, so the first Rust landing is the smallest.
6. **The exits.** Green: counted operations within the pinned budget (`dev/work-budget.json`) at every size `make work-budget` rolls, MODE AUDIT
   WITHIN on the `.rs` modules, `make cohort-landing` with no regressed seed, the Rust coverage floor whole. Red: a count over its budget, or MODE AUDIT not WITHIN, goes to the round arbiter (`make arbiter-ask`) with the measurement.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** `make work-budget`: water_frame's count at every size against its pinned budget; `make perf-ab` beside it, recorded.
10. **Before moving a constant.** The research page each rolled knob cites (0054), read before it moves.
11. **Before fitting things into room.** n/a

**Performance work?** yes - docs/performance-checklist.md's questions follow.

### T19 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** <the stage and the loop: `make perf-profile` time beside `make phase-calls` / `make perf-fanout` calls>
2. **Removes work, or only moves it?** <fewer candidates, a screen, a kept result, an index, an early stop, a better algorithm,
   a loop into C - or an inlining, a merge, a builtin written out: never the goal, only where the time evidence shows a gain>
3. **What do you expect it to save, and why?** <a share of the stage's profiled time>
4. **How does the work grow with the settlement?** <the growth exponent between sizes, and whether this bends it>
5. **What did the before and after show, and under what conditions?** <calls; `make perf-ab` best of N with each arm's spread,
   the host's load - evidence, not a pass>
6. **Did any map move, and does it still keep the research?** <`make maps-moved`, the cohort>

