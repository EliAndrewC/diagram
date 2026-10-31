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
6. **The exits.** Green: counted operations at most the budget at 40 and 80, every seed of the Rust stage gate passing where the Rust stages complete (`make rust-gate`, FR-019, amendment 5), the claims round IN-STEP, the reviews owed, MODE AUDIT WITHIN, `phases/field.md`'s eight boxes ticked, all of the old field code - comb and polder - deleted. Red, over its budget: rebuilt again, or the budget raised with the GM's words (`make budget-change`, FR-006) - never set down, never an arbiter's accept; a stop to assess goes to the GM, as he asked ("then we can stop and assess how things are going").
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
6. **Did any map move, and does it still keep the research?** Yes - every comb map's basins and ditches move; the Rust stage gate (FR-019), the claims round and settlement-review hold them to the research.



<!-- plan-archive: T17 to T17 moved to plan-done.md, 2026-10-30 (feature 375 FR-044) -->
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


<!-- plan-archive: T19 to T19 moved to plan-done.md, 2026-10-31 (feature 375 FR-044) -->

<!-- plan-archive: T20 to T20 moved to plan-done.md, 2026-10-31 (feature 375 FR-044) -->
<!-- plan-archive: T20 to T20 moved to plan-done.md, 2026-10-31 (feature 375 FR-044) -->

### T21 - the Rust stage gate and the failing-seed list (amendment 5, FR-019, FR-020; the GM 2026-10-31: "Yes, I agree with your proposals and refinements. Please write up that amendment and then implemente it.")

- **Approach**: the roll through the Rust stages alone, the checks asked by what they read, the seeds with no fixed block and the
  failing list with its frozen inputs, and the landing held to it - each pinned by a test (SC-012, SC-013).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| D1-D6 | each test red without its part | n/a (no map moves: the gate judges, it places nothing) | none | n/a |

### T21 Approach (2026-10-31T13:52Z)

1. **The goal, in the world.** No Rust stage ever ends with a failing check, on any seed; a seed that fails one is checked until
   it and the input its stage failed on both pass; the Python stages after the Rust ones refuse no Rust landing.
2. **The constraints.** FR-019, FR-020, SC-012, SC-013; feature 386's landing cohort unchanged for a landing that changes no Rust
   stage; the engine's checks unchanged in what they find (one list, read by both the cohort and the gate).
3. **Where each comes from.** G: the GM's words above and in `request.md` (amendment 5). O: the checks as `cohort_audit.roll_how`
   asks them (read 2026-10-31: refusals raised by name in the stages, and 14 finished-map checks).
4. **Do they describe the world here?** The Rust stages today are water_frame alone; the gate is tested on it and on stub stages.
5. **The order.** After amendment 5 (FAITHFUL); before T18 and T16, so the field port is the first judged by it.
6. **The exits.** Green: every test red without its part and green with it, `make rust-gate` passing on main's engine, `make done`
   and `make hooks-test` green, landed by `make land F=444 T=T21`. Red: what failed recorded and the task set down, a claim that
   it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The tests, and `make rust-gate`'s record on the landed engine with no failing seed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

**Performance work?** no.

### T21 Decisions

- **D1 - the Rust stages and a roll through them** (`hamletgen/rust_prefix.py`): a stage is Rust when `rust/phases/src/<stage>.rs`
  exists, derived; `off_the_front` names one that is not the front of `STAGES`, and the gate refuses then. `roll_through` runs the
  Rust stages on `driver.fresh_settlement` (split out of `build`, unchanged in what it does), stopping where they end, and returns
  a trace: each stage's input pickled as it started (its frozen input; measured 2026-10-31, a throwaway test: 5,838 bytes after
  water_frame, the field stage running on the restored copy) and the parts of the map it wrote. The checks are judged where EACH
  Rust stage completes (the GM: "at the point where that stage has completed"; the plan review of T21, round 2): the map after
  stage i - the next stage's frozen input, or the final map - by the checks the stages up to i own (D2). A stage that raises is
  charged with its own input; a failing check is charged to the FIRST stage at whose completion it fails, with that stage's input,
  so a later stage that rewrites a part cannot hide an earlier stage's failure. A check that reads only parts the fresh settlement
  held fails, if at all, at the first stage's completion and is that stage's. A check reading two stages' parts is the later one's
  to fail where both have written, so its fixture may hold the earlier stage's output - as FR-020 has it.
- **D2 - the checks asked by what they read** (`rust_prefix.Reads`, `held`; `rust_gate.judge`): a check's reads are recorded on the
  map (top-level parts and `meta.<key>`). A check counts at the gate when it read something and everything it read is either a part
  the Rust stages OWN - written by a Rust stage on any seed of the run, so a stage that wrote nothing on one seed is still judged
  on that empty output (D2b) - or a part the fresh settlement already HOLDS with content, an input it may read beside the Rust
  output (D2a); a check that reads a part only a later stage writes is that stage's and is not asked. Ownership is derived from the
  run's trace, never a hand table. The checks are one list, `cohort_audit.POST_CHECKS`, which `roll_how` reads too, each looked up
  by its name when asked.
- **D3 - the gate** (`tools/rust_gate.py`, `make rust-gate`): the fresh block of 48 from `cohort_gate.py fresh-seed`'s start - a hash of
  the engine key, so it rotates with the engine (feature 386 D3) - the
  six pinned row variants on the next fresh seeds, and the failing list's seeds; a plan that cannot be rolled fails the first Rust
  stage (water_frame rolls the plan, T19). Each run is recorded in `dev/rust-gate/<utc>.json` with the engine key it rolled
  (`ci.delta.engine_key_worktree`); exit 1 on any failing seed or replay.
- **D4 - the failing list and its frozen inputs** (`dev/rust-gate/failing.json`, `dev/rust-gate/frozen/`): a failing seed is added
  with its stage, its first FAIL line and its frozen input; every run rolls it and replays the fixture into its stage and the Rust
  stages after; the entry leaves only when both pass, and its fixture with it. A fixture that no longer loads is a failure, never
  dropped silently.
- **D5 - the landing held to it** (`scripts/gates/cohort_gate.py`): every engine landing is refused without a `rust-gate` record at
  its engine with no failing seed; a landing that changes `rust/**` (against `origin/main`) reads its landing cohort's regressed
  seeds as notes, a rate - refusing nothing; any other landing keeps feature 386's cohort as it stands.
- **D6 - `make land` makes the record** (`scripts/land.py`): on an engine delta, where the record is owed, land runs `make rust-gate`
  and commits `dev/rust-gate/` - the record, the failing list and its fixtures - BEFORE it stops on a failing seed, so the list
  outlives a landing that goes no further.

