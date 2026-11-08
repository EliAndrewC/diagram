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
<!-- plan-archive: T16 to T16 moved to plan-done.md, 2026-11-02 (feature 375 FR-044) -->
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
  run's trace, never a hand table. A check is handed the map alone, and the plan reaches the map only as its `meta`, whose reads are
  recorded - so no check reads the plan unseen (pinned by `test_a_check_reaches_the_plan_only_through_the_recorded_meta`). The checks are one list, `cohort_audit.POST_CHECKS`, which `roll_how` reads too, each looked up
  by its name when asked.
- **D3 - the gate** (`tools/rust_gate.py`, `make rust-gate`): the fresh block of 48 from `cohort_gate.py fresh-seed`'s start - a hash of
  `ci.delta.engine_key_worktree`, which walks every engine path, `rust/**`'s `.rs` and Cargo files among them (`is_engine`, T17):
  a Rust-only change moves the start, pinned by `test_a_rust_only_change_moves_the_fresh_start` (the plan review, round 3) - the
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

### T21 part B (2026-10-31T14:46Z)

The trigger: two red gates in a row on T21's landing (14:32Z, 14:42Z), the tripwire ruled `continue` by the round arbiter
(red-gate@2026-10-31T14:42:03Z).

1. **What exactly is refusing?** First gate: `hooks-test` rust-tooling (`cohort_gate.py` reads `.rs` files and no row of
   `dev/rust-tooling.md` named it) and `test_census_matches_pin` (`rust_gate.py` reached `STAGES` through the package surface).
   Second gate: test-full's roll census (the gate's unit tests rolled real water_frame seeds in the test worker).
2. **A3 again.** The project's own rules, unchanged: every reader of `.rs` has its row; the package surface is pinned; the gate
   rolls no map of its own (constitution VI).
3. **A4 again.** Each refusal read in the gate's log.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither: each fixed where it failed, decided nothing new.
6. **The one-sentence test.** "T21's landing found three tooling misses of its own, each fixed."
7. **Done:** the row and its proof added; `STAGES` read from `hamletgen.driver`; the gate's tests on a stand-in water_frame,
   rostered as `InProcess` stubs in `tests/rolls.py`.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire, with each fix and its passing
   tests in hand.
9. **After a ruling, the step it named?** Yes: `make done` once more, through `make land F=444 T=T21`.

### T21 part B (2026-10-31T15:00Z)

The trigger: the third red gate in a row (14:56Z), ruled `continue` by the round arbiter (red-gate@2026-10-31T14:56:27Z).

1. **What exactly is refusing?** One test: `tests/test_operations_registry.py::test_every_entry_point_has_a_registry_row` -
   `l7r.diagram.tools.rust_gate` runs as `python3 -m` with no row in `_invocation.OPERATIONS`. The three earlier fixes held.
2. **A3 again.** The registry's rule, unchanged: every runnable tool names its make target.
3. **A4 again.** Read in the gate's log.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither: the row added (`rust-gate`, expensive), its claim re-checked IN-STEP.
6. **The one-sentence test.** "The gate's new tool needed its row in the operations registry."
7. **Done:** the row added, the registry test passing.
8. **Every route measured before the arbiter was asked?** The tripwire asked, with the fix and its passing test in hand.
9. **After a ruling, the step it named?** Yes: `make done` once more; one more fresh red is a process fault (how much new code
   lands before a single `make done`), per the ruling.

### T22 (FR-021, amendment 6: every open claims finding at water_frame's units - 15 when filed, listed by `make claims-report`)

- **Approach**: each finding fixed in its claim or its code, decided 2026-11-03 by reading the code each names:
  - **D1 - the eight MISLABELED** (six units: `Counts.add`, `KnobIn` and `quarter_deg` each mislabeled under both of the module's
    claims, `admitted_falls` and `applies` under one): each carries its own `Research:` NONE line, so it no longer inherits a claim it does not keep.
  - **D2 - the fall quantized (UNCLAIMED)**: claimed at `admitted` as a CONVENTION - the eight compass points at 45 degrees, the
    four cardinals at 90 on a polder's survey grid.
  - **D3 - the fall backs the wind (DRIFTED)**: the page draws the high windward margin as one case among several, how common a
    GUESS. The record is silent on the share, so the easier route is taken and said (the GM 2026-10-25): the tie kept on every
    hamlet, both ends in, relabeled a DEVIATION of 0031 that says so. No map moves.
  - **D4 - `roll_plan` and `stage_water_frame` (CANNOT-TELL)**: the docstring states what the checker lacked - each draw is even over
    the knob's table, and the settlement form's table repeats its forms 5, 3 and 2 of ten (`consts.SETTLEMENT_FORMS`), the page's
    half, three in ten and two in ten; a pinned form arrives as the table's one entry, so `forms.first()` is the pin.
  - **D5 - `_KNOBS` (CANNOT-TELL)**: a dispersed hamlet reads `lane_skeleton` (the track's gateway, `ways/track.py`) but never
    `lane_web` (`ways/web/stage.py` returns first); `lane_web` moves to a new `not_dispersed` branch (`applies`), so it is rolled
    only where its form uses it. Each knob draws from its own stream (`knob_rng(seed, name)`), so no other knob moves; a dispersed
    map's unread `lane_web` takes its table's first form.
  - **D6 - `_rust_rolls`'s two UNCLAIMED**: claimed - the flood grove table where the spec or the archetype puts the map on flood
    ground (a dike-top hamlet is never rolled, only pinned, so the spec decides it: no rolled-form case exists), and the row fixed
    to the dry edge on flood ground (0033).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| D1-D4, D6 | claims only | no map can move | none | n/a |
| D5 | a dispersed map's `lane_web` value only, unread | to measure at the gate | none expected | n/a |

### T22 Approach (checklist part A)

1. **The goal, in the world.** No place changes: the water frame's claims say what its code does, with zero open findings at its
   units (amendment 6: "every Rust stage end its initial implementation with zero open claims").
2. **The constraints.** FR-021 (no open claim in the units a phase delta changes); constitution XII (every decision labeled).
3. **Where each comes from.** R: 0031, 0033, 0036; G: the GM 2026-10-25 (the easier route where the record is silent); O: the code read.
4. **Do they describe the world here?** Read in the code each finding names (2026-11-03).
5. **The order.** After T26's committed work; independent of T26's landing.
6. **The exits.** Green: `make claims-report` lists no open finding (DRIFTED, MISLABELED, NEEDS-RESEARCH, CANNOT-TELL, UNCLAIMED) at
   water_frame's units in FR-021's sense - its Rust, its seam, its `STAGES` entry and every Python unit they read at run time - after
   T22's own changes, including any those changes raise. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make claims-report` lists no open finding at water_frame's units (FR-021's sense), after T22's own changes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

**Performance work?** No.

<!-- plan-archive: T23 to T16 moved to plan-done.md, 2026-11-02 (feature 375 FR-044) -->
### T24 (the round arbiter's ruling ask:444-T16-hem-cleared-reprice, 2026-11-01)

- **Approach**: the accepted field derivation (`phases/field_greenfield.derivation.md`) prices the dry hem on the winter crop's
  odds alone - 114 plots at 40. Commit 740aed0ec (T16's third claims round) made a cleared middle (`fan_middle`, 1 map in 4 - the knob's weights, cleared 0.25, `settlement/fields/grain.py` `FAN_MIDDLE`)
  lay one band along the whole canal whatever the need (0011). Measured 2026-11-01 by `make work-budget`
  (`dev/work-budget/20261101T085501Z-39d51a626dd7.json`): hem plots at 40 of 241, 119, 158 and 150 on seeds 4, 25, 39 and 47,
  mean about 167; the stage's total, 27,012 at 40 and 47,513 at 80, under the derivation's 27,238 and 49,631 as it stood that
  morning. The derivation was re-derived later that day (`phases/field_greenfield.derivation.md`, the round arbiter's accept on
  ask:444-T16-field-turns-round, the GM's yes on 444#4): 34,656, 62,494 and 114,953 at 20, 40 and 80 households, exponent 0.86 -
  the derivation the 1.9 below multiplies (1.9 x 62,494 = 118,739; 1.9 x 114,953 = 218,411). At the
  derivation's next re-derivation, price the dry hem, the hem's laid plots, the outline by bands and the hem's registry share
  on `fan_middle`'s odds, and name the cleared-middle band in the contract's Writes. Not before: the arbiter forbade editing
  the derivation now (FR-013).
- **Two more rows** (the GM, 2026-11-01, on 444#6: "I go with option (a) - this is well within what we should consider
  acceptable, even if our original estimate was a bit off because of failing to count/consider/calculate everything."): the
  budget stands at 1.9 per thing of the derivation as it stood on 444#6 - 118,739 at 40, 218,411 at 80, the whole roll 139,987 at
  40 (2026-11-01, `make budget-change` and `make budget-program`, `dev/work-budget.json`). THOSE PINS STAY: the re-derivation moves
  the derivation's items, never the pinned budget, which only `make budget-change` with the GM's words moves (FR-015). The same
  re-derivation prices the dry plots' furrow rows (`pt_test@furrows`, 12,254 at 40 after the rows were swept, 26,003 before; rows
  5 px apart, a GUESS) and the copy of every plot to the Python stages (`write@py_export`, 22,046 at 40; it goes as those stages
  port to Rust) (2026-11-01, `make work-budget`, run `dev/work-budget/20261101T224654Z-799b3654eff8.json`, means at 40).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T24 Approach (checklist part A)

1. **The goal, in the world.** No map change; the field's work budget prices the hem as the field lays it.
2. **The constraints.** FR-013 (a figure change re-owes a ruling), FR-014 (the typical case), FR-015 (the standing pin).
3. **Where each comes from.** R: 0011's drawing page (a cleared middle drawn only as the hem along the whole canal); O: the
   2026-11-01 work-budget record above.
4. **Do they describe the world here?** Measured on the four reference seeds, above.
5. **The order.** At the field derivation's next re-derivation, after T16 lands.
6. **The exits.** Green: a MODE BUDGET verdict on the re-priced rows, and the round arbiter's ruling on the changed figures (`make arbiter-ask`, FR-013). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The hem rows' expected plots at 40 within the measured mean's band.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

**Performance work?** No - a budget's arithmetic, not the code's.


### T25 (escalation-check on the T16 glyph check of Inashiro's paddy, F1, 2026-11-02)

- **Approach**: the Rust comb lattice (`rust/phases/src/field/lattice.rs`, `fan.rs`) lays every basin as a whole quadrilateral of its
  lattice to the fan's edge; 0005's drawing page asks for a comb "never as the tidy grid", with triangular basins "on every map".
  Measured 2026-11-02 on the T16 roll of Inashiro against main's (the escalation-check's count on `pool/hamlets/inashiro/inashiro.json`
  and main's): 0 triangles against 2, 563 of 565 basins four-sided against 554 of 622, basin-area CV 0.16 against 0.23, p90 corner
  deviation 12.7 deg against 26.4. The `plot_regularity` knob reaches the lattice: a valley_paddy's edge basins clipped by the fan's
  outline (its triangles) and its bunds wobbled; the regular lattice kept for a planned field.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the knob reaches the lattice | its test red without it | the 48-seed cohort, the Rust gate | the comb maps | n/a |

### T25 Approach (checklist part A)

1. **The goal, in the world.** A valley comb that reads hand-laid: uneven basins, triangles at its edge.
2. **The constraints.** 0005's drawing page; the field's accepted budget (FR-006); FR-021's zero open claims.
3. **Where each comes from.** R: 0005's drawing page; O: the 2026-11-02 counts above.
4. **Do they describe the world here?** The counts above, on the shipped roll and main's.
5. **The order.** After T16 lands; with the field's next re-derivation (T24) if the work moves.
6. **The exits.** Green: the counts within main's on the comb maps, `make rust-gate` and the cohort green, the budget held. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Triangles and the basin-area CV on Inashiro at or past main's.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

**Performance work?** No.


### T26 - phase: sink, in Rust under amendment 7 (the GM 2026-11-03: "then work on converting the next stage with these guidelines in place ... like the entire next phase"; FR-003-FR-006, FR-017, FR-022)

Occasions: settlement-review on the pool hamlets the rebuilt sink moves (a pond, its ditch or the drain's run off the map redrawn); glyph-check only if a glyph is redrawn.

Measured 2026-11-03 before the plan (throwaway probes rolling the first three stages, nothing committed): over cohort seeds 1-48 the sink takes two branches, 24 a pond and 23 a searched run off the map (no confluence, no constructed route), and seed 29 fails in the sink today (its constructed route refused by the overlap matrix); the only standing feature that ever refused the sink is a resting basin (`fallow_patches`, 62 refusals of a drain run on the 8 maps that have one; the pond was never refused). At the reference spec, 40 households, seed 4: of the stage's 167,264 counted operations, laying the pond and its drain is 1,158, rounding the brook 150,314 (the whole brook re-filed in the overlap registry, every piece asked again), and the driver's end-of-stage walk of the manifest 15,792. The session read the old `hamletgen/sink.py` while scoping, before `make task-start`; the rebuild is written from the derivation's contract, the research pages and these measurements.

### T26 Approach (checklist part A)

1. **The goal, in the world.** The field's runoff ends where the record says it does (0060): a pond at the field's foot about three parts in a hundred of the paddy, clear of the crop and the brook, its reeds at the shore (0061), joined to the collector's outfall by a dug ditch that runs downhill and never across the brook; or, on the off-map roll, the drain joining the passing brook where it is in reach, else run off the map out of the collector's exit, turning at most 55 degrees, downhill, never through the rice, a resting basin or a dike off its gap; the brook drawn with its bends rounded (0054).
2. **The constraints.** FR-003 to FR-006, FR-017, FR-019 to FR-022; rubric S1-S10; `phases/sink_greenfield.derivation.md` and its budget, 149 at 40, exponent 0.61; the pages 0060, 0061, 0054, 0068; the manifest keys the stage writes (the probe of 2026-11-03: `streams`, `channels`, `drawn_channels`, `pond`, `pond_layer`, `marshes`, `meta.water_sink`, `meta.pond_role`) and the plan's `water_sink`, `sink_pond`, `sink_brook`, `confluence`.
3. **Where each comes from.** G: amendment 7 and the GM's request of 2026-11-03. R: 0060 (where the runoff goes, the odds, the 55 degrees, downhill), 0061 (the reeds), 0054 (bends rounded, join rather than cross). O: the probes above.
4. **Do they describe the world here?** A hamlet's drain on a valley comb, the reference roll; the off-map branch is outside the reference roll (its `water_sink` is pinned `pond`), held to the same rules by the Rust stage gate's fresh block, which rolls both.
5. **The order.** After `field`, before `seat`. The brook is rounded by the stage that lays it (D2), so nothing after the field re-files it.
6. **The exits.** Green: `make rust-gate` with no failing seed through water_frame, field and sink (seed 29 among them); the counted operations at 40 and 80 at most the (raised) budget, or within amendment 7's LEEWAY; MODE AUDIT WITHIN or LEEWAY; the claims round IN-STEP (FR-021); the reviews owed; `phases/sink.md`'s eight boxes; the old sink Python deleted. Red: over what FR-022 admits - rebuilt again, or the budget raised on a re-derivation naming the missed work (`make budget-set RAISE=1`, past twice the first with a second SOUND), or with the GM's words past ten times; a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** The off-map run is a search over bearings and junction distances (0060's turn and downhill rules); its candidates are derived from the 55 degree turn and the canvas, and it stops at the first that keeps every rule (S9).
8. **The budget.** One landing; `make rust-gate` after each increment; one MODE AUDIT pass a round.
9. **Done, measured.** `make work-budget`: sink at 40 and 80 against its budget; the whole roll's total against 18.3M at 40 (dev/work-budget.md, 2026-11-03).
10. **Before moving a constant.** Each figure the Rust reads is cited to its page at the Rust (0060's 3/100 share and 55 degrees, 0061's reeds, 0068's widths); a GUESS stays a GUESS, a knob where the record gives forms.
11. **Before fitting things into room.** A pond with no clear seat drains off the map (0060: "A map whose pond would have to sit far below the fields sends its drain off the map as well").

**Performance work?** yes - docs/performance-checklist.md's questions follow.

### T26 Decisions

- **D1 - the seam** (FR-004, FR-010): `stage_sink(s, plan)` stays a thin Python function. It gathers what the stage reads - the plan's
  fall, drainage bearing, canvas, scale, households, `water_sink` and the field's outline; the drain collector (`field_ditches`,
  role `drain`); the brook's stations and its taps (the heads of the channels taken off it); the dikes; the resting basins'
  rings - and calls `l7r_phases.stage_sink` (`rust/phases/src/sink.rs`, its submodules under `rust/phases/src/sink/`). Rust
  returns the run (its points and what it ends at), the pond (center and radii) or none, the reeds' ring, the confluence and the
  brook's drawn course where a confluence moved it; Python writes the same keys with the same record shapes (`channels`,
  `drawn_channels` through `field_channel`, `pond`, `pond_layer`, `marshes`, the meta's `water_sink` and `pond_role`, the
  plan's `water_sink`, `sink_pond`, `sink_brook`, `confluence`, the no-build box) and draws them.
- **D2 - the brook rounded where it is laid** (0054; the measurement above): the Rust field returns the brook's drawn course
  beside its stations - every bend filleted at 2.5 drawn widths, each tap held (0054: "every corner filleted"; a tap is a
  junction, not a bend) - and the field's seam writes the stream record on its drawn course with `stations` the course as first
  laid, which the ways and the fords keep reading as today. The sink re-draws the brook only where its confluence adds a held
  vertex, and seats a confluence only on a straight stretch at least the fillet's cut-back from any corner, so holding it leaves
  the drawn course as it was. This changes the field's seam and its Rust: the field's counted work is re-measured against its
  accepted figures (the ratchet) and audited once in MODE AUDIT.
- **D3 - the end-of-stage walk after a Rust stage** (`hamletgen/driver.py`, `tools/work_budget.py`): the registry files each record
  as it is appended (`StandingList`), so the walk at a stage's end only re-records what was reshaped in place; a Rust stage's
  seam reshapes nothing (measured 2026-11-03 over cohort seeds 1-48: after water_frame, field and sink the walk moved no record,
  its whole cost the extents it recomputed to compare), so the driver skips the walk after a Rust stage (`walks_after`). The next
  Python stage's walk still re-records anything reshaped in place, and the Rust stage gate (`rust_prefix.py`) keeps its own.
- **D4 - the pond** (0060, 0061): its area 3/100 of the field's paddy (0060's GUESS), its aspect the plan's, its seat on the
  drainage line beyond the collector's outfall by its own half-length, stepped on by a half-length where its rim or its box meets
  the crop or the brook (the water index's cells), stepped across the fall a long radius each way where the line is blocked, and
  given up past the set-back limit (`POND_SETBACK_LIMIT`, a GUESS) for the off-map branch; its ditch from the outfall bowed off the
  chord, or led round on a curve where the pond lies more than 100 degrees off the collector's heading, never crossing the brook;
  the reeds a ring at the shore (0061; its width a GUESS, 44 ft).
- **D5 - the off-map branch** (0060): the passing brook joined where a point on its course lies within reach, fallen below the
  outfall, with a trunk below it, reached without crossing the crop, on a straight stretch (D2); else the run out of the
  collector's exit searched over bearings round the fall and the collector's heading and junction distances, nearest first, the
  first keeping every rule (turn at most 55 degrees, not through the crop, a resting basin or a dike off its gap, downhill, under 90
  degrees off the drainage bearing, the brook not crossed mid-run nor run beside as its twin); else the constructed route round the
  field's hull. Seed 29's refusal is diagnosed and its rule kept by construction (FR-019).
- **D6 - the draws**: the sink rolls nothing of its own; the plan's `water_sink` is water_frame's knob.
- **D7 - the counters** (FR-012): one key a derivation row, `<kind>@<row>`, behind the `counters` feature; a seed rolled with the
  feature on and off writes identical manifests (`phases/sink.fr012.md`).
- **D8 - the derivation re-derived** (FR-022 rule 2): `phases/sink_greenfield.derivation.md` revised with `## Work the first
  derivation missed` - the ditch to the pond, the reeds' ring, the stage's records filed in the overlap registry, the brook's
  drawn course (D2) where it is drawn, the resting basins asked - each priced from the contract, judged in MODE BUDGET; past twice
  the first budget, a second independent dispatch.
- **D9 - deletion** (FR-005): `hamletgen/sink.py` and what only it reaches (`brook_course.round_the_brooks` and the helpers only it
  calls) deleted in the landing, found by `git grep -l` and `make dead-closure`; the seam stays in a new `hamletgen/sink_stage.py`.

### T26 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In the brook's rounding: 150,314 of the sink's 167,264 counted operations at 40 (seed 4, the
   probe of 2026-11-03), the whole brook re-filed in the overlap registry with every piece asked again; the end-of-stage walk
   15,792; the pond and its drain 1,158.
2. **Removes work, or only moves it?** Removes it: the brook is filed once, on its drawn course, by the stage that lays it (D2),
   where today it is filed raw and then re-filed rounded; the walk after a Rust stage files only what is new (D3).
3. **What do you expect it to save, and why?** About 165,000 operations at 40 from the whole roll (the rounding's re-filing and
   the sink's walk), less what filing a rounded brook costs the field over a raw one (its fillets add vertices).
4. **How does the work grow with the settlement?** The pond's seat grows with its box's cells (x1.41 in each radius a doubling,
   the derivation's 0.61); the brook's filing with its length, once.
5. **What did the before and after show, and under what conditions?** `make perf-ab` recorded at the landing, best of N.
6. **Did any map move, and does it still keep the research?** `make maps-moved`, `make rust-gate`, the settlement-reviews owed.

### T26 part B (2026-11-03T18:01Z)

The trigger: two red gates in a row on T26 (17:43Z, 17:50Z), the tripwire ruled `continue` by the round arbiter
(red-gate@2026-11-03T17:50:56Z).

1. **What exactly is refusing?** First gate: `tests/hamletgen/test_rust_prefix.py` listed the Rust stages as water_frame and
   field, and T26 made sink the third. Second gate: the hamlet-path coverage floor, `settlement/land/wet.py` 503-504 and 514-515
   (`pond_reeds`'s two "no open ground left" drops), unrun since the first gate and hidden by its failure.
2. **A3 again.** The project's own rules, unchanged: the Rust stages are derived from the crate and the test pins them; a module
   on the hamlet path is held at 100%.
3. **A4 again.** Each refusal read in the gate's log.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither: tests added where each failed, and one dead function deleted. As the ruling asked, the other
   spans `make cover-changed` named were closed too: the registry walk after a Python stage (`work_budget.py` 70) and a
   stream's stations (`water.py` 139) are tested, and `brook_rules.turn_deg`, left with no caller by T26, is deleted.
   `tests/tools/test_perf_snapshot.py` already names the sink.
6. **The one-sentence test.** "T26 made the sink a Rust stage; one test listed the old stages, and the reeds' drops had no test."
7. **Done:** the prefix test names three stages; `pond_reeds`'s drops are tested in `tests/settlement/test_wet_ground.py`.
8. **Every route measured before the arbiter was asked?** The tripwire asked, with each fix and its passing tests in hand.
9. **After a ruling, the step it named?** Yes: `make cover-changed` clean on the three files it named, then `make done` once.

### T26 part B (2026-11-03T18:55Z)

The trigger: cohort seed 904 newly failing against main (`dev/cohort-log/20261103T183048Z-diagram-backlog-503049.json`,
groves_crossed_by_lanes 2), at set-down.

1. **What exactly is refusing?** Two bamboo groves of one farm (at about (894, 1646) and (838, 1707)) lie under lanes. The
   sink (pond form) is not the refusing stage: the bamboo strip and the lane web, Python stages after it, judged on the Rust
   sink's moved pond and ditch.
2. **A3 again.** The rule is the bamboo's, unchanged (no grove crossed by a lane).
3. **A4 again.** Read in the cohort's log.
4. **Moving something placed earlier to suit something later?** Declined: the sink's pond is placed by its own research; the
   groves and the lanes are the later stages'.
5. **Tuning or changing?** Neither. Held to the bamboo stage's port, as Kashikawa's bamboo is (found row 358).
6. **The one-sentence test.** "A later Python stage trips on the Rust sink's moved pond at seed 904; held to its own port."
7. **Done:** nothing changed for it; the T26 join-reach change does not reach it (904 is a pond sink).
8. **Every route measured before the arbiter was asked?** The JOIN_REACH change ruled out (pond sink); the room knob
   (`SEATING_GROUND_FT`, a GUESS) not moved, since the failing stage is not the sink's.
9. **After a ruling, the step it named?** Yes: ask:set-down-T26 ruled `continue` - seed 904 recorded as a found row for the household groves' port, kept off the Rust failing list (FR-020), T26's landing left to its budget route.

### T26 Approach (2026-11-04T06:51Z)

The increment after the GM's answer (2026-11-04, "Sounds good, I accept option (a)"): the sink's budget raised on his words to 850 / 1,000 / 1,200, and the landing.

1. **The goal, in the world.** As the T26 Approach above: the field's runoff ends at a pond with its reeds, or joins the passing brook, or runs off the map on a searched run that keeps every rule of 0060 and 0054.
2. **The constraints.** FR-022 (the raise on the GM's words, past twice the first and under ten times; LEEWAY at up to twice the raised figure); rubric S5 (every inner loop counted, work in C per element); FR-021 (no open claims finding in a file the landing changes).
3. **Where each comes from.** G: the GM's answer above. O: MODE AUDIT rounds 3 and 4 (`phases/sink.audit-3.txt`, `-4`), each UNCOUNTED: the keyhole's all-pairs loop and the keep-out's shapely work, uncounted. R: 0060's 55-degree turn, which the constructed route held on its first leg only (impl-drift, 2026-11-04).
4. **Do they describe the world here?** Yes: the uncounted loops ran on every pond roll; the constructed route on no seed of the Rust gate's 54 and no pool map, measured 2026-11-04 (`make rust-gate` and `make map` of the two off-map hamlets with `lay` refusing before the constructed route; `phases/sink.constructed-routes.md`).
5. **The order.** Count first, then cut: the counters added, the work measured (3,271 at 40, measured 2026-11-04 (`make work-budget`)), then the pond cut once in `drawn_ground`, the field cut to the reeds' reach, the closest pair swept by x (1,455 at 40, measured 2026-11-04 (`make work-budget`)).
6. **The exits.** Green: MODE AUDIT LEEWAY (`phases/sink.audit-5.txt`), `make budget-accept`, the claims round IN-STEP on every changed file, `make rust-gate` 0 failing, `make land F=444 T="T22 T26"`. Red: past twice the raised budget - a question for the GM, the raise his own; else what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** The constructed route is deleted on the round arbiter's ruling (ask:444-T26-constructed-turn, route b): where no searched run keeps every rule the sink refuses by name; the remedy for a refusing seed is a finer `SWINGS` or a longer lengthening, both GUESS knobs, never a constructed route again.
8. **The budget.** One MODE AUDIT a change; the round arbiter at the third claims round on one unit (as ruled).
9. **Done, measured.** sink 1,358 / 1,455 / 1,611 at 20 / 40 / 80, measured 2026-11-04 (`make work-budget`), accepted.
10. **Before moving a constant.** None moved: the reeds' reach past their tint (the registry's) now bounds the field's cut too, its claim reworded; the pond's ellipse in the reeds' cut is the 32-point ring the blocks already held.
11. **Before fitting things into room.** Not a room question.

### T22 part B (2026-11-04T07:16Z)

The trigger: red gates in a row on the T22/T26 landing (06:59Z, 07:11Z, 07:13Z), the tripwire ruled `continue` by the round arbiter (red-gate@2026-11-04T07:13:57Z).

1. **What exactly is refusing?** The landing's `make done`, each time a different cheap check: preflight's Python driver (`rust/phases/tests/py_driver.py`) still expecting the deleted constructed route's refusals; static's rustfmt on the rewritten sink test; static's Rust coverage on an `assert!` message line that never runs.
2. **A3 again.** The rules are the checks' own (the driver's named refusals, rustfmt, the Rust line floor), unchanged.
3. **A4 again.** Read in each run's record (`dev/run-log/2026-11/`).
4. **Moving something placed earlier to suit something later?** No: each fix is in the delta that caused it.
5. **Tuning or changing?** Neither: the driver's cases follow the deletion, the test is formatted, the unrun message made a comment.
6. **The one-sentence test.** "Deleting the constructed route left its driver cases, a format and a coverage line behind."
7. **Done:** `make quick` and `make static` clean at the head (2026-11-04).
8. **Every route measured before the arbiter was asked?** Each red was read and fixed in its own commit before the next run.
9. **After a ruling, the step it named?** Yes: `make done` again at the clean head, through `make land F=444 T="T22"`.

### T27 - phase: seat, in Rust under amendment 7 (the GM 2026-11-04: "Once you have finished with this, please do the entire next phase as well"; FR-003-FR-006, FR-017, FR-022)

Occasions: settlement-review on the pool hamlets the rebuilt seat moves (a cluster seated on another margin moves every house); glyph-check only if a glyph is redrawn.

- **Approach**: the seat's search, its way out and the brook's fords rebuilt in Rust (`rust/phases/src/seat/`) behind a thin `hamletgen/seat_stage.py`, to the greenfield derivation re-derived under FR-022 rule 2 (measured 2026-11-04 (`make stage-sizes STAGE=seat`): 30,325 at 40, SOUND twice blind, verdicts 6 and 7). The session read the old `hamletgen/cluster.py` and `ways/track.py::stage_seat` while scoping, before `make task-start`; the rebuild is written from the derivation, the research pages and those measurements.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T27 Decisions

- **D1 - the seam**: the Rust owns the margins, their refusals and score, the ranking, the head's way out, the fords and the streams gapped at them; the thin `seat_stage` gathers what it reads (the outline, the dry plots, the wet toe as the roll derives it, the reed fringes, the brook as first laid, the way out's walls and lines from `cluster.exit_walls`), sets the crossing cost on the router (`set_crossing`, the router's state), and writes the plan's `seat` and `watercourses`, the manifest's `meta.brook_fords`, `meta.seat_offwind` and `meta.lane_skeleton`, and the field's face. A ladder rung's own way out stays the house seating's (`seat_has_dry_exit`), asked when it falls back to one.
- **D2 - the margins** (0031, 0072, 0058, the GM's ruling of 2026-08-28): the candidates the margins facing within 90 degrees of the wind, a flank's back turned just past the 45-degree bar; refused cheapest first - off the frame, the belt off the canvas, on the toe, on the field, centered in the reeds, crop behind - and the rest scored; the brook's share on the band the tie-break 0035 states (a site the brook does not cross preferred only between two otherwise level), where it was a 3.0 weight (closing `cluster.py`'s DRIFTED finding); the back's crop the share of its area clipped from the plots, where it was 21 sample points; the belt's room its rectangle clipped to the canvas. The refusal names how many margins each rule stopped.
- **D3 - the way out** (0081): straight runs off the canvas, then a walk of the way-out cells (20 ft, GUESS: the narrowest dry neck a track takes) aimed at the nearest edge; the cells tested and what was found of them remembered across the margins the head falls back to.
- **D4 - the fords** (0035): the brook walked once, a ford on each straight reach at its spacing (points along it by bisection on the legs' running lengths); each stream segment gapped only by the fords filed near it - where the Python asked every ford of every segment.
- **D5 - the counters** (FR-012): one key a derivation row, `<kind>@<row>`, as the sink's are.
- **D6 - deletion** (FR-005): the old seat search (`seat_cluster`, `margin_candidates`, `back_fouled`, `belt_off_canvas`, `BELT_ROOM_MAX_OFF`, `_seat_frame`, `_seat_center`, `TURN_SLACK`) and what only it reached (`below_drain`, `nearest_within`) deleted with their tests; `track.stage_seat` deleted; `seat_cluster` kept by name in `seat_stage` as the Rust seat without the fords, which the house seating's tests start from.

### T27 Approach (2026-11-04T12:30Z)

1. **The goal, in the world.** The settlement sits on the higher, drier ground beside its paddy (0031), its back to the wind (0072), off the wet toe (0058), never centered in a pond's reeds (the GM's ruling of 2026-08-28), the brook across its band only a tie-break (0035), with a dry way out of the frame (0081); the brook crossed by every later way only at its fords (0035).
2. **The constraints.** FR-003 to FR-006, FR-017, FR-019 to FR-022; rubric S1-S10; `phases/seat_greenfield.derivation.md` (30,325 at 40, exponent 0.89); the pages 0031, 0035, 0058, 0072, 0081; the plan fields the stage writes (`seat` and its ladder, `watercourses`) and the manifest's `meta.brook_fords`, `meta.seat_offwind`, `meta.lane_skeleton`.
3. **Where each comes from.** G: the GM's request of 2026-11-04 and amendment 7. R: the pages above. O: the stage's input, measured 2026-11-04 (`make stage-sizes STAGE=seat`): the outline 96 points at 40, 53 margins facing the wind, 152 dry plots, the brook 450 stations.
4. **Do they describe the world here?** A hamlet's seat on a valley comb, the reference roll; the Rust stage gate's fresh block rolls every form the seat meets, measured 2026-11-04 (`make rust-gate`).
5. **The order.** After the sink, before the waterward stage and the houses: the fords open before any way is routed, the seat decided before any house.
6. **The exits.** Green: `make rust-gate` with no failing seed through water_frame, field, sink and seat; the counted operations at 40 and 80 at most the budget the GM sets (the raise owes his words, past ten times the first), or within amendment 7's LEEWAY; MODE AUDIT WITHIN or LEEWAY; the claims round IN-STEP (FR-021); the reviews owed; `phases/seat.md`'s eight boxes; the old seat search deleted. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** The seat is a search over the outline's margins: its candidates the margins facing within 90 degrees of the wind, each refused cheapest first, every survivor scored because the ladder is the whole ranking (S9); the way out stops at the first clear run, its walk remembered across margins.
8. **The budget.** One landing; `make rust-gate` after each increment; one MODE AUDIT a round.
9. **Done, measured.** The Rust seat counted 15,694 / 25,765 / 48,101 at 20 / 40 / 80, measured 2026-11-04 (`make work-budget`), under the derivation's 18,191 / 30,325 / 62,012.
10. **Before moving a constant.** None moved: every figure the Rust reads keeps its claim at the Rust (the sampling knobs named in the derivation, GUESS); the brook's weight became the tie-break 0035 states, and the back's crop an area share where it was sampled.
11. **Before fitting things into room.** Measured 2026-11-04 (`make rust-gate`, the refusal's tally): on about one seed in ten the dry hem stands behind every margin facing the wind, or the wet toe on it, and the old Python seat refused the same seeds on the Rust field (rolled in a detached worktree at e16522808). A research pass (2026-11-04) attests the houses between the paddy and the dry fields, and the round arbiter (ask:444-T27-seat-hem) ruled the fault the field's: T28 lays the hem after the seat, behind the settlement; with it every seed of the Rust gate seats, measured 2026-11-04 (`make rust-gate`: 69 seeds and 15 replays, 0 failing).

**Performance work?** yes - docs/performance-checklist.md's questions follow.

### T27 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In the walk of the manifest after the seat (`pt_test@Standing.resync` 8,125, `write@Standing.ribbon` 7,496 of the seat's 25,087 counted at 40) and its 41,160 Python calls at 40, measured 2026-11-04 (`make work-budget`); the seat's own ring tests each walk the whole ring (7,249 point tests of up to 96 edges each).
2. **Removes work, or only moves it?** Removes it: every ring test asks its strip or its cells, the back's crop is clipped once, the fords and the gaps are found by bisection and cells, and a Rust stage is followed by no walk of the manifest.
3. **What do you expect it to save, and why?** The seat's Python calls (41,160 to a few hundred) and its share of the roll's time.
4. **How does the work grow with the settlement?** Exponent 0.81 measured, under the derivation's 0.89.
5. **What did the before and after show, and under what conditions?** `make perf-ab` recorded at the landing, best of N.
6. **Did any map move, and does it still keep the research?** `make maps-moved`, `make rust-gate`, the settlement-reviews owed.


### T27 part B (2026-11-04T15:42Z)

The trigger: the second red gate in a row on T27-T29's clone (15:20Z, 15:40Z; the bundle counts four reds since 07:11Z, each a
different defect), ruled `continue` by the round arbiter (red-gate@2026-11-04T15:40:07Z).

1. **What exactly is refusing?** First gate: `tests/test_operations_registry.py::test_every_entry_point_has_a_registry_row` -
   `l7r.diagram.tools.stage_sizes` (added in T27) had no `_invocation.OPERATIONS` row. Second gate: test-full's roll census -
   `tests/tools/test_stage_sizes.py` ran the real water_frame as its stand-in step, in the test worker, with no roster row; and the
   hamlet-path floor found `hamletgen/field_stage.py` 330-331 unrun - the field door's dry-plot filing, unreachable since T28 lays
   every dry plot in the hem.
2. **A3 again.** The project's own rules, unchanged: every runnable tool names its make target; the gate rolls no map of its own
   (constitution VI); a module on the hamlet path keeps 100%.
3. **A4 again.** Each refusal read in the gate's log (`.git/verify-gate-*.log`, the 15:40 run's record
   `dev/run-log/2026-11/20261104T154006919855-314052.json`).
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither: each fixed where it failed, deciding nothing new.
6. **The one-sentence test.** "T27's new tool needed its registry row and its test a stand-in stage, and T28 left the field's dry
   filing unreachable."
7. **Done:** the row added (`stage-sizes`, expensive); the test's step a stand-in with its `InProcess(..., stub=True)` row in
   `tests/rolls.py`; the unreachable lines deleted; `make cover-changed` read for the changed lines before the third gate.
8. **Every route measured before the arbiter was asked?** The tripwire asked, with each fix and its passing test in hand.
9. **After a ruling, the step it named?** Yes: the fixes committed, the unreachable lines removed, `make done` once more.

### T27 part B (2026-11-06T03:18Z)

The trigger: `make cohort` at 03:18Z named pinned row 902 newly failing against main (`groves_crossed_by_lanes` 1) and 901 worsened
(`refused:WebRefused`, main `refused:SeatRefused`).

1. **What exactly is refusing?** Row 902 (linear, a street row on both sides, the water shared): one grove, household 13's, at
   (1101, 2117), is crossed by a lane the Python web lays after the Rust stages; row 901: the web's last resort refuses a kink it
   cannot mend without dropping a tree lane.
2. **A3 again.** The cohort's rule, unchanged: a seed passing on main and failing on the clone is a regression owed before the landing.
3. **A4 again.** Read in the cohort records: both rows fail identically in every clone record since 2026-11-05T16:05Z
   (`dev/cohort-log/20261105T160515Z-*` on), before T31-T33's work, so not this morning's change (the seating's parts asked a
   placer's margin wider, which cleared the Rust gate's seed 820818).
4. **Moving something placed earlier to suit something later?** No: the grove and the web's lane are judged where they are laid.
5. **Tuning or changing?** Neither yet: the two rows are diagnosed before the landing cohort, which refuses them.
6. **The one-sentence test.** "Two pinned rows the Python web judges after the Rust stages regressed on the clone a day ago, and are
   owed a diagnosis before the landing."
7. **Done:** each row's lane traced to its stage (the track's row road or the homesteads' lanes) and fixed where it fails, the
   cohort's two rows passing, before `make cohort-landing`.
8. **Every route measured before the arbiter was asked?** Not yet asked: the rows are diagnosed first; a claim that a row cannot pass
   goes to `make arbiter-ask`.
9. **After a ruling, the step it named?** No ruling yet.

**Measured since (2026-11-06T05:30Z-07:00Z).** The default cohort also named seeds 2 and 3, which pass on main (rolled in a detached
worktree of `origin/main`) and fail on the clone with the grove rule below reverted, so T27-T32's own:
- **Row 902** (`groves_crossed_by_lanes`): a straight field way laid from its farm's dooryard through that farm's own deep band; the
  lane law asked no grove of a tree lane. Now `Lawful.ground_fault` refuses a tread through any farm grove band, by the predicate the
  finished map is held to (`grove_rules.tread_meets_band`). Passes.
- **Seed 2** (`OverlapRefused`, a lane on a threshing yard): `lay.laid_lawfully` re-asked the matrix only of a run other than the
  form it held, so a gathered form (an end moved onto a junction) was drawn unasked. Now `_held` compares against the run the caller
  asked (`asked`). Passes.
- **Seed 3** (`WebRefused`, a street across its brook off a ford): the row street asked at twice its row's length (T30/T31) ran on
  across the brook and a farm was seated on the far bank. Now a street's seats are kept to one stretch between its brook crossings
  and the hard ground its tread meets (`row_seat.rs` `one_reach`). Passes.
- **Row 901**: from main's `SeatRefused` to a seated map whose road meets its street at a hairpin. The street's east end stands short
  of its planned line's brook crossing, which is no ford; the ford is about 300 ft north-east, and the only way to it doubles back
  round a grove band. The next step is `brook_bounds` (street.py and track.rs): end the street short of a crossing the road can
  reach at a ford, or refuse the row form on that stretch - not another road fallback (the advisor, 2026-11-06).

### T27 part B (2026-11-07T05:47Z)

The trigger: two red `make done` runs in a row (red-gate@2026-11-07T05:45:49Z), the round arbiter ruling CONTINUE.

1. **What exactly is refusing?** The static phase, each time before any test ran: first clippy on T33's appurtenances Rust
   (single-letter names, manual midpoints, casts, an iteration style), then rustfmt on the code those fixes rewrote.
2. **A3 again.** The crate's lint and format rules, unchanged: every Rust file clippy-pedantic clean and rustfmt formatted.
3. **A4 again.** Read in the gate's log: `rust_checks.py lint` and `format` now clean on the crate.
4. **Moving something placed earlier to suit something later?** No: lint and format only, the same output.
5. **Tuning or changing?** Neither: the expressions rewritten to their lint-clean forms (`f64::midpoint`), the geometry's names
   excused at their module as the crate's other modules do.
6. **The one-sentence test.** "T33's Rust never met the lint because `make quick` does not run it; it does now, and the gate runs."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire; its ruling: one more `make done`.
9. **After a ruling, the step it named?** `make done` once more, after the lint and the format pass clean.

### T27 part B (2026-11-07T08:56Z)

The trigger: a third red `make done` in a row (red-gate@2026-11-07T06:12:19Z), the round arbiter ruling CONTINUE.

1. **What exactly is refusing?** The static phase's `rust_checks.py cover`: the crate below 100% of its lines, on T32's and T33's
   branches no test or driver call reached (the appurtenances door, the far channel's straight chord, the wells' groups, a row
   reach cut at a brook, the road's and the connector's band fallbacks, the fill's stale entry) and assert messages on their own
   lines, which run only when a test fails.
2. **A3 again.** The crate's floor, unchanged: every line run by its own tests or its Python driver.
3. **A4 again.** Read in `make cover-changed`: no `.rs` line named; then `rust_checks.py lint` and `format` clean.
4. **Moving something placed earlier to suit something later?** No: tests and driver calls added; the branch-free rewrites (a
   point segment's divisor, a never-empty group list, the fill's first pop) give the same output.
5. **Tuning or changing?** Neither: no number or rule moves.
6. **The one-sentence test.** "T32's and T33's fallbacks shipped with no test that reached them; each has one now, and a coverage
   run that fails says why instead of naming every file at line 0."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire; its ruling: cover-changed, lint
   and format clean first, the pool maps checked, then one `make done`.
9. **After a ruling, the step it named?** Those, in its order; a red that a local pass could have caught is a process fault.

### T27 part B (2026-11-07T12:26Z)

The trigger: a red `make done` in a row (red-gate@2026-11-07T12:03:56Z), the round arbiter ruling PROCESS-FAULT.

1. **What exactly is refusing?** The static phase's `rust_checks.py cover`: llvm-cov's summary counted 7 lines missed, six closures
   no test called on lines that run, where `make cover-changed`, reading the LCOV lines alone, had passed.
2. **A3 again.** The crate's floor at the spec's strictness: every line run and every function called, by its own tests.
3. **A4 again.** Read in both `rust_checks.py cover` and `make cover-changed` on one tree, through the one reader
   (`rust_checks.lcov_missed`): both clean.
4. **Moving something placed earlier to suit something later?** No: the six closures each given a test that reaches them (a crop and
   a far ditch for the channels, a third group of wells, a household's well, wells along a row's street, a dry exit walled by the
   wood seats); the Python doors compiled out behind the crate's `python` feature, never dropped by a filename pattern.
5. **Tuning or changing?** Neither: no number or rule moves.
6. **The one-sentence test.** "The gate and cover-changed read one floor by two measures; they read it through one reader now, at the
   gate's strictness, and the closures it found are tested."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire; its ruling: the shared reader and its
   test, the six closures, the doors settled, both floors clean, lint and format, then one `make done`.
9. **After a ruling, the step it named?** Those, in its order.

### T27 part B (2026-11-07T12:33Z)

The trigger: a red `make done` in a row (red-gate@2026-11-07T12:28:52Z), the round arbiter ruling CONTINUE.

1. **What exactly is refusing?** test-full, before any test ran: `/bin/sh: Syntax error: Unterminated quoted string` - the rust-only
   branch of the test recipe's coverage step held a comma its `$(if)` took as the separator; the static phase was green.
2. **A3 again.** The gate's recipes parse at both port states.
3. **A4 again.** Read in `make -n test | sh -n` and `make -n done | sh -n` at rust-only and at `PORT=integrated`, and in
   `pytest --collect-only` with the rust-only selection.
4. **Moving something placed earlier to suit something later?** No: one word of a message, the comma made " - ".
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "A message's comma split a make `if` no gate had run; it is gone, and both port states' recipes parse."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire; its ruling: the parse at both states,
   the rust-only collection, then one `make done`.
9. **After a ruling, the step it named?** Those, in its order.

### T27 part B (2026-11-07T12:45Z)

The trigger: a red `make done` in a row (red-gate@2026-11-07T12:40:50Z), the round arbiter ruling CONTINUE.

1. **What exactly is refusing?** test-full's tests, the first run of the phase to its end at rust-only: 7,586 passed, 5 failed - stale
   tooling assertions this feature's own moves left (bare-GUESS claims, a test module's claim, `KnobIn` public, the default port,
   the track's Steps naming T32's deleted functions).
2. **A3 again.** Each check as it stood, its fixture brought to the tree.
3. **A4 again.** Read in the four files' run (106 passed) and in the next `make done`.
4. **Moving something placed earlier to suit something later?** No: claims and assertions brought to what the code now is.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "Five checks still described the code before this feature moved it; they describe it as it stands."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire; its ruling: one more `make done`.
9. **After a ruling, the step it named?** That, the tree as it stands; T35 filed for the engine trees the rust-only gate leaves out.

### T28 - the dry hem laid behind the settlement (the round arbiter on ask:444-T27-seat-hem, 2026-11-04)

Occasions: settlement-review on the pool hamlets whose dry plots move (Inashiro and Kashikawa, measured 2026-11-04 (`make map`): their manifests moved against HEAD); glyph-check only if a glyph is redrawn (none: the dry plots keep their ink).

- **Approach**: the field hands on what the hem is laid from (`Field.hem`: the canal's course, its side, the fall, the bounds, the seed, with the field's water at its widths) and a new Rust stage `hem` (`rust/phases/src/hem.rs`, behind `hamletgen/hem_stage.py`) lays it after the seat, a column pushed past the settlement's ground where its first strip would stand on it (`field::dry::past_keep`); measured 2026-11-04 (`make rust-gate`): 69 seeds and 15 replays through water_frame, field, sink, seat and hem, 0 failing, where the seat refused about one seed in ten on the field's old hem.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T28 Decisions

- **D1 - the order**: the hem after the seat, before the waterward fringe and the houses: the seat chosen on ground with no dry plot yet, the hem laid behind it (0006, form (b) of the research pass of 2026-11-04: paddy, houses, dry fields behind).
- **D2 - the seam**: the field's Rust hands the hem's inputs on (`Field.hem`, its water as segments with widths), the field's Python door keeps them on the plan (`plan.hem_in`); the hem's door writes the dry plots' records, the no-build registries, the plan's net, the grain drawn and the room left on the title card, and the dry plots' ink (`ink.dry_plots`, the field's own drawing).
- **D3 - the settlement's ground**: the seat's band from the field's margin out past its two half-depths and the belt's far edge (`hem_stage.settlement_ground`: the standoff a GUESS from 0029; the belt's far edge the 0071 convention), the band's length along the margin; a column whose first strip would stand on it laid behind it, a strip's depth at a time, at most the ground's own reach.
- **D4 - the failing list**: the seat's entries re-charged to the field, each with the field's own input frozen (`make rust-gate REFREEZE=field`), so no fixture replays the old field's hem into the seat (the round arbiter's ruling). A moved entry's frozen input is replayed from the field forward through every Rust stage after it - the sink, the seat and the hem (`rust_gate.replay`: the stages from the charged one on) - and the entry leaves the list only when that replay and its seed's roll both pass (FR-020).

### T28 Approach (2026-11-04T12:38Z)

1. **The goal, in the world.** A clustered hamlet's houses stand between the paddy's canal and its dry fields where the settlement stands on the paddy's high edge; the dry hem runs just upslope of the canal along the rest (0006).
2. **The constraints.** FR-005, FR-019 to FR-022; 0006's finding and drawing page as redrawn on 2026-11-04; the round arbiter's ruling on ask:444-T27-seat-hem.
3. **Where each comes from.** R: 0006 (yamamoto-torisu-1984, Torisu Hongo: paddy in front, the dry fields behind the settlement). O: the seat's refusal tallies, measured 2026-11-04 (`make rust-gate`): on every refused seed the dry hem under or behind every wind-facing margin.
4. **Do they describe the world here?** One clustered plateau-edge hamlet attests the order; the hamlet's map is a clustered settlement on its paddy's high edge, the case attested.
5. **The order.** After the seat, before the waterward fringe and the houses.
6. **The exits.** Green: `make rust-gate` 0 failing through hem; the claims round IN-STEP; Inashiro's and Kashikawa's settlement-reviews; the hem's counted work within a budget derived for it. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None new: the hem's own search is the field's, unchanged; the push past the settlement's ground stops at the first clear depth.
8. **The budget.** One landing, with T27 (the hem is a Rust stage after the seat, which must be Rust before it).
9. **Done, measured.** `make rust-gate` 0 failing, measured 2026-11-04 (69 seeds, 15 replays).
10. **Before moving a constant.** None moved: the hem's figures stay the field's (0006, 0011).
11. **Before fitting things into room.** The room is the settlement's ground, kept by the hem rather than the seat squeezed off its margin.

**Performance work?** no - the hem's work moves from the field's count to its own stage's; its budget derived with it.


### T29 - phase: waterward, in Rust under amendment 7 (the GM 2026-11-04: "please take this entire feature to completion"; FR-003-FR-006, FR-017, FR-022)

Occasions: settlement-review on a pool polder the rebuilt fringe moves (Kuwabata, measured 2026-11-04 (`make map`): its manifest unchanged against HEAD, so none owed); glyph-check only if a glyph is redrawn (none).

- **Approach**: the flanks, the dike's outer face and the strips rebuilt in Rust (`rust/phases/src/waterward.rs`) behind a thin `hamletgen/waterward_stage.py`, which draws each strip as the waterside marsh, declares the flanks and reserves the sty's seat; measured 2026-11-04 (`make work-budget`): 0 counted at every reference size against the budget's 1 (a valley hamlet draws no fringe), and `make rust-gate` 54 seeds through the six Rust stages, 0 failing.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T29 Decisions

- **D1 - the seam**: the Rust owns the flanks facing the water (`flanks`), each flank's outer face (`face`) and its strip (`fringe`); the thin door gathers the dikes' rings and notches, the band's widest cut, the fall and the seat's back, draws each strip with `Settlement.marsh` (the waterside role's ink and cover), declares the flanks (`meta.waterward`) and reserves the sty's seat (`reserve_sty_seat`), all as the Python stage did.
- **D2 - deletion** (FR-005): the old `stage_waterward` and `dike_face` deleted with their tests; `polder_flanks` and `waterward_flanks` kept (the house seating's capacity and the crossings' caps read them).
- **D3 - the counters** (FR-012): one key a derivation row, as the seat's are.

### T29 Approach (2026-11-04T13:35Z)

1. **The goal, in the world.** A polder's reed fringe outside its dike on the flanks that face the water it was reclaimed from, stopping at the embankment's outer face and stepping in through each notch; nothing on a valley hamlet (0019, 0027).
2. **The constraints.** FR-003 to FR-006, FR-017, FR-019 to FR-022; `phases/waterward_greenfield.derivation.md` (its budget 1 at 40); the pages 0019 and 0027.
3. **Where each comes from.** R: 0019 (the waterward flanks), 0027 (the band cut at a notch). O: the reference rolls, measured 2026-11-04 (`make work-budget`): 0 at every size.
4. **Do they describe the world here?** A polder hamlet's case; the reference roll draws none, and the pool's polder (Kuwabata) is unchanged, measured 2026-11-04 (`make map`).
5. **The order.** After the hem, before the houses and the track, so both treat the strip as wet ground.
6. **The exits.** Green: `make rust-gate` 0 failing through waterward; the count within the budget; MODE AUDIT WITHIN; the claims round IN-STEP; `phases/waterward.md`'s eight boxes. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the face is one pass over the dike's points into bins.
8. **The budget.** One landing, with T27 and T28.
9. **Done, measured.** 0 counted at 40 and 80, measured 2026-11-04 (`make work-budget`).
10. **Before moving a constant.** None moved: the run past the dike's ends, the bins and the depth keep their claims at the Rust (GUESS and CONVENTION as before).
11. **Before fitting things into room.** Not a room question.

**Performance work?** no - a valley hamlet draws no fringe; the polder's strips are one pass over the dike's points.

### T30 - phase: homesteads, in Rust under amendment 7 (the GM 2026-11-04: "please take this entire feature to completion"; FR-003-FR-006, FR-017, FR-022)

Occasions: settlement-review on the pool hamlets the rebuilt seating moves (every pool hamlet: a house seated a foot off moves the ways and the wood laid round it), at the landing; glyph-check only if a glyph is redrawn (none: the farmsteads keep their ink).

- **Approach**: the whole stage - the site boundary and its free-ground raster, the seat region, every household seated by its form (the cluster grown from its first house, the dispersed rows and ranks, the row village's streets), each homestead's parts laid in its box and held to the rules the parts read, the homestead wood's share, the track out chosen once the last house stands and each household's way laid in the gaps to it under the lane law's rules - rebuilt in Rust behind a thin `homesteads/stages.py` door that writes the records and draws the farmsteads as today; measured 2026-11-04 (`make work-budget`): 1,716,870 at 40 against the budget's 4,118 (416.9x), 17,909,350 Python calls at 40 (`make perf-fanout STAGES=homesteads`), the stage mapped in `phases/homesteads.map.md`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T30 Decisions

- **D1 - the seam** (FR-003 to FR-005, FR-017, FR-019): the whole stage in Rust behind a thin `homesteads/stages.py` door, its output what the stage writes today - every household seated on its own ground while no way stands (0246: "houses before lanes"), then the track out chosen once the last house stands and each household's way laid in the gaps to it (0246), held to the lane law's rules those ways ask (0081). The rules the ways ask are ported as a Rust module of their own (`rust/phases/src/law/`), each one predicate its placer and its test call, as `ways/law/` is in Python, so the web's phase reuses them and the lane law is ported once. The door keeps the ink (`Settlement.farmsteads`) and the overlap registry's records (D2). The ruling of spec-fidelity on 2026-11-04 (plan-444-T30, BLOCKED) refused the split this decision first proposed: the stage's budget is the whole stage's, and the phase writes what the stage writes.
- **D2 - the seating's parts** (0029, 0036-0040, 0043-0048, 0285): the Rust lays each homestead's parts as the bundle lays them today - the house on its size ladder, the yard, the beds, the kura, the byre and the fixtures - and the wood share; the door keeps the ink (`Settlement.farmsteads`) and the overlap registry's records, as the hem's door keeps the dry plots'.
- **D3 - the search** (S9; 0029: nearest the seat first, the field the tie-break): the first house on the free ground nearest the seat's center; each next house offered from a standing one at the distance their footprints part, ring by ring, jittered by the standing house's position; every offer judged against a raster of the free ground painted once and the standing homesteads' boxes in a grid; no house is taken back.
- **D4 - deletion** (FR-005, FR-017): every form the stage seats - the nucleated cluster grown from its first house, the dispersed hamlet's front row and ranks, the row village's streets (0031, 0033) - in Rust, and the Python seating, the track's choice, the gap ways and what only they reached deleted in the same landing, with no fallback path; the Rust stage gate's fresh block and its pinned rows are to roll every form (FR-019, FR-020) - checked at the landing, and a form neither rolls given a pinned row.
- **D5 - the counters** (FR-012): one key a derivation row, `<kind>@<row>`.

### T30 Approach (checklist part A)

1. **The goal, in the world.** Every household seated on its own ground beside its paddy by its settlement's form - a clustered hamlet grown irregularly from its first house nearest the seat, a dispersed one along its paddy's chords, a row village along its streets - each homestead with its yard to the south sun, its beds, its fixtures and its wood behind it, on ground no water, crop, wet or registered way takes (0001, 0029, 0031, 0036, 0038, 0246, 0285).
2. **The constraints.** FR-003 to FR-006, FR-012, FR-017, FR-019 to FR-022; the pages named in D2 and D3; the stage map `phases/homesteads.map.md`; D1's seam.
3. **Where each comes from.** G: the GM's request of 2026-11-04 and amendment 7. R: the pages above. O: the stage's input and work, measured 2026-11-04 (`make stage-sizes STAGE=homesteads`, `make work-budget`, `make perf-fanout STAGES=homesteads`).
4. **Do they describe the world here?** A nucleated valley hamlet, the reference roll; the Rust stage gate's fresh block rolls every form the seating meets.
5. **The order.** After the waterward fringe, before the track and the appurtenances, as today.
6. **The exits.** Green: `make rust-gate` with no failing seed through the stage; the counted operations at 40 and 80 at most the budget (re-derived under FR-022 rule 2; past ten times the first, the GM's words); MODE AUDIT WITHIN or LEEWAY; the claims round IN-STEP; the settlement-reviews owed; `phases/homesteads.md`'s eight boxes. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** A search over offered seats: each offer refused cheapest first, against a raster painted once (S9).
8. **The budget.** One landing; the lane law's module lands with it, and the web's phase reuses it.
9. **Done, measured.** `make work-budget`'s count for the stage at 40 and 80 against its budget, re-derived for the whole stage under FR-022 rule 2.
10. **Before moving a constant.** None moved: each constant keeps its claim at the Rust that reads it.
11. **Before fitting things into room.** Not a room question: every household is seated or the site refused, as today (0001).

**Performance work?** yes - docs/performance-checklist.md's questions follow.

### T30 Approach (re-answered 2026-11-05T19:41Z)

1. **The goal, in the world.** As above: every household seated on its own ground by its settlement's form.
2. **The constraints.** As above, and S4 at every choice the seating makes between candidates: a row's first street and a row
   village's margin are chosen by their room, asked before any farm stands (`row_seat.rs` `row_room`), never by seating each
   and keeping one.
3. **Where each comes from.** As above; spec-fidelity's plan review of 2026-11-05 (S4, FR-004, FR-016).
4. **Do they describe the world here?** The Rust stage gate's fresh blocks and pinned rows, every form.
5. **The order.** As above.
6. **The exits.** As above. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Each offer refused cheapest first against a raster painted once; each row street's and margin's room
   asked once, nothing placed to be dropped.
8. **The budget.** One landing.
9. **Done, measured.** As above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T30 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In the seating's tests of each offered seat and the ways laid after it: 17,909,350 Python calls at 40, measured 2026-11-04 (`make perf-fanout STAGES=homesteads`), the hottest chains the fabric's crossing tests (`fabric_hits_boxed`), the gap ways' leg tests (`gap_ways.leg_ok`, `access.fixtures_clear`), the boundary's line samples (`boundary._samples`, growing 18.7x from 20 to 40) and the fixtures' reach tests (`fixture_seats.within_reach_of`); 1,716,870 counted at 40, measured 2026-11-04 (`make work-budget`).
2. **Removes work, or only moves it?** Removes it: the boundary painted once and each offer read from the raster and a grid of the standing boxes, the parts laid from one template a size, the wood's share by its lattice once a homestead, each way's legs asked of indexed fabric rather than every part.
3. **What do you expect it to save, and why?** The stage's Python calls, and its share of the roll's time (the stage 3.93 s of the roll at 40 on seed 25, measured 2026-11-04 (`make perf-ab`)).
4. **How does the work grow with the settlement?** 0.84 from 20 to 80, measured 2026-11-04 (`make work-budget`); the stage's re-derivation will say its own.
5. **What did the before and after show, and under what conditions?** `make perf-ab` recorded at the landing, best of N.
6. **Did any map move, and does it still keep the research?** `make maps-moved`, `make rust-gate`, the settlement-reviews owed.

### T31 The homesteads seat all 17 households of the Rust gate's seed 778251 on its margin 1

The Rust gate's seed 778251 (17 households) seats 12 of 17 on margin 1 and refuses (SiteRefused). The Rust seat's margin stands
(the round arbiter, ask:444-T30-fresh-seed-refusals, after the probe: the old Python seat's refusal is the 97 dry plots T28 moved
after the seat, `specs/444-work-budget-program/phases/homesteads.gate-seeds.md`). The frozen input is
`dev/rust-gate/frozen/778251-homesteads.pkl`; 778251 stays on the failing list until both its seed and its frozen input pass.

- Done when: the Rust homesteads seat all 17 on this seed and the stage's checks pass there (FR-019; matching Python is not
  required).
- Room comes first from the margin's length or a second margin; the bundle pitch and the researched room for the lane,
  the footpath, the yard's sun and the front row's standoff are not narrowed to make 17 fit (the arbiter's ruling).
- Red: what failed recorded in `homesteads.gate-seeds.md` and the task set down; a claim that it cannot be done is ruled through
  `make arbiter-ask`.

### T31 Approach (checklist part A)

1. **The goal, in the world.** Every declared household of seed 778251 seated beside its paddy (0001).
2. **The constraints.** FR-019; the arbiter's ruling (room from the margin's length or a second margin; no researched room
   narrowed); 0004's no house taken back.
3. **Where each comes from.** G: amendment 5's FR-019. R: 0001, 0004. O: the gate records in `homesteads.gate-seeds.md`.
4. **Do they describe the world here?** A row village on the Rust seat's margin; the ladder's next margins on the same field.
5. **The order.** Inside the homesteads stage's seating (`seat_every_household`).
6. **The exits.** Green: 778251 seats all 17 and the stage's checks pass there (`make rust-gate`). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None placed and dropped (FR-004, S4): each ladder margin's room - its row's frames asked every rule a farm is seated by, nothing stood (`row_seat.rs` `row_room`) - asked before any house, and the row seated once, on the first margin whose room holds every household (FR-016).
8. **The budget.** One commit inside T30's landing.
9. **Done, measured.** `make rust-gate`'s failing list without 778251.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Room from a second margin, the ruling's route, its room asked before any house stands.

- research: rendering


### T32 - phase: track, in Rust under amendment 7 (the GM 2026-11-04: "please take this entire feature to completion"; FR-003-FR-006, FR-017, FR-022)

Occasions: settlement-review on the pool hamlets the stage moves, at the landing (a row village's road: none of the pool's five
is a row village, so none is expected to move; `make maps-moved` says); glyph-check only if a glyph is redrawn (none: the track
keeps its ink).

- **Approach**: the track out is chosen in Rust once the last house stands (T30, `ways/gateway.rs`), so what the stage still
  decides is a row village's road (0033): its first street's drawn span (its farms' span at their reach, stopped short of the
  brook past its end farms), run on off the sheet at both ends along each end's last leg, each run over the brook at the ford
  that makes the walk shortest (0035), threaded through the steadings and squared where it crosses water (0084). That goes
  to Rust (`rust/phases/src/track.rs`), reading what `household_ways.track_inputs` gathers and the planned street; the door
  draws each run it returns (`Settlement.lane`, the ink and the registry), the far run marked `run_on`; every other form draws
  the track out recorded at the homesteads (`way_out_track`), as today.

### T32 Decisions

- **D1 - the seam** (FR-003 to FR-005, FR-017): the row road in Rust behind a thin `ways/track.py` `stage_track` door; its
  output the runs the stage lays today. The Python helpers only the road reached (`thread_over_the_ford`, the track's own use of
  `street_runs_out` and `ford_crossing`) are deleted in the same landing where nothing else reaches them; `street_span` stays
  in Python for the web until the web's phase, its Rust twin shared then.
- **D2 - no new rule**: every constant keeps its claim at the Rust that reads it (the run past the sheet, CONVENTION; the ford landing, GUESS;
  the vertex step; the reach and run in frames, GUESS; `ROW_FRAME_FT`, 0033 - each as its constant's claim reads).
- **D3 - the budget** (FR-022 rule 2): a REVISION of the stage's greenfield derivation (`phases/track_greenfield.derivation.md`),
  never a new one: the track out's choice moved out to the homesteads (T30 D1, whose re-derivation prices it), the registry's
  record of the connector and a row village's road under `## Work the first derivation missed`, revised before the rebuild's
  count is read and judged in MODE BUDGET; a figure past the pin set by `make budget-set RAISE=1`. The stage's first greenfield
  pin, 223 at 40 (verdict-2, SOUND), stays the reference for every FR-022 line - the 2x raise, the two blind dispatches past it,
  the accepted count's ceiling and the ten-times line. The driver's stage-end backstop over the whole map is named there, its
  pricing the MODE BUDGET verdict's to rule.
- **D4 - the counters** (FR-012): one key a derivation row, `<kind>@<row>`.

### T32 Approach (checklist part A)

1. **The goal, in the world.** A row village's road: the street its farms stand along runs on off the map at both ends as the
   road it stands for (0033), over the brook at a ford (0035).
2. **The constraints.** FR-003 to FR-006, FR-012, FR-017, FR-019 to FR-022; 0033, 0035, 0081, 0084; D1's seam.
3. **Where each comes from.** G: the GM's request of 2026-11-04 and amendment 7. R: the pages above. O: `stage_track` today.
4. **Do they describe the world here?** The Rust stage gate's pinned row variants (901-904) and its fresh block's row villages.
5. **The order.** After the homesteads, before the appurtenances, as today.
6. **The exits.** Green: `make rust-gate` with no failing seed through the stage; MODE AUDIT WITHIN or LEEWAY; the claims round
   IN-STEP; `phases/track.md`'s boxes. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the road is laid once, threaded by the ported router.
8. **The budget.** One landing.
9. **Done, measured.** `make work-budget`'s count for the stage at 40 and 80 against its budget.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

- research: rendering


### T33 - phase: appurtenances, in Rust under amendment 7 (the GM 2026-11-04: "please take this entire feature to completion"; FR-003-FR-006, FR-017, FR-022)

Occasions: settlement-review on the pool hamlets the stage moves (a communal well seated a seat off moves the lanes laid round it) -
not owed while the port switch stands at rust-only, owed when it is thrown back to `integrated` (FR-023); glyph-check only if a
glyph is redrawn (none: the wells, byres, fixtures and retirement houses keep their ink).

- **Approach**: what the stage decides - each grove farm's own water (its channel or its well), the communal wells of the rolled
  siting among the houses (the cluster form now; the lane-side form beside the track out, the rest after the lanes), and each
  retirement house off its farmhouse's back or flank - goes to Rust, reading what the door gathers (the houses as seated, the
  free ground, the registry's pieces near the cluster, the water, the crop's box, the reserved wood seats - no belt footprint, D6);
  the door draws what the seating reserved (the byres, the fixtures) and each well and retirement house the Rust seats.

### T33 Decisions

- **D1 - the seam** (FR-003 to FR-005, FR-017): the stage's decisions in Rust behind a thin `homesteads/stages.py`
  `stage_appurtenances` door, its output what the stage writes today; the Python seat searches only the stage reached deleted in
  the same landing (the lane-side wells' later seating stays with `stage_lane_wells` until its own phase).
- **D2 - every rule asked before a well stands** (S4): a seat's verdict is the engine's (`well_at`: off the water, the hard
  ground, every lane, the registry's pieces, the canvas), asked of the Rust's candidates in its ranking's order before the seat
  is drawn; nothing drawn is moved or dropped.
- **D3 - the budget** (FR-022): the stage's greenfield derivation (`phases/appurtenances_greenfield.derivation.md`, SOUND at
  713 at 40) is the pin every FR-022 line reads; work it missed is priced under its `## Work the first derivation missed` and
  raised by `make budget-set RAISE=1`, never squeezed.
- **D4 - the counters** (FR-012): one key a derivation row, `<kind>@<row>`.

### T33 Approach (checklist part A)

1. **The goal, in the world.** Every household watered (a grove farm from its own channel or well, the rest from a shared well
   among them, 0196), the byres and fixtures where the seating laid them, the retirement houses beside their farmhouses (0004).
2. **The constraints.** FR-003 to FR-006, FR-012, FR-017, FR-019 to FR-022; 0004, 0028, 0048, 0072, 0196; D1's seam.
3. **Where each comes from.** G: the GM's request of 2026-11-04 and amendment 7. R: the pages above. O: the stage today.
4. **Do they describe the world here?** The reference roll (nucleated, the cluster form) and the Rust stage gate's fresh blocks
   and pinned rows (the lane-side form, the grove farms).
5. **The order.** After the track, before the pond stock, as today.
6. **The exits.** Green: `make rust-gate` with no failing seed through the stage; MODE AUDIT WITHIN or LEEWAY; the claims round
   IN-STEP; `phases/appurtenances.md`'s boxes. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** A ranked list of well seats from the gaps between each group's houses (D5) and the track's verges (D7a),
   each asked the engine's verdict in order, the first admitted drawn.
8. **The budget.** One landing.
9. **Done, measured.** `make work-budget`'s count for the stage at 40 and 80 against its budget.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T33 Approach (re-answered 2026-11-06T08:04Z)

The stage counts 145,889 to 317,054 at 40, measured 2026-11-06 (`make work-budget`, the reference rolls), against the
713 pinned, and 38,000 to 213,000 of it is one question, the windbreak belt's polygon built in the well seating so a seat inside
it is ranked last (`seat_wells`, `hinterland.belt_polygon`'s crop test, `RingIndex.inside_many`); the rest the lattice sweep's
distance tables and the registry's records. The greenfield's seat - a corner four seated lots share on the lots' lattice - is not
the ground the Rust seating lays: its households are seated on the free ground's cells (`place.rs`), not on a lattice of lots,
so no shared corner is read. The seat search is rebuilt to the derivation's other parts instead:

- **D5 - the cluster form's seats from the houses** (0196, the greenfield's groups): the households a communal well owes
  (`needy`, as today) cut into `well_target` groups by halving the longer side at its median; each group's candidate seats the
  gaps between its houses - the middle of the open ground between each pair of the group's houses whose walls stand within
  twice `WELL_SEAT_FT` of each other (GUESS: 0196's 80 ft seat doubled) - ranked by the neighborhood ladder's rung (the fifth-nearest house within 190, 300, 520
  px, a GUESS of `seat_cluster`'s, then 0196's 760 ft; three then two where fewer than five need it) and then by the distance to the group's middle; each
  asked in that order: off a lane's verge (`on_a_verge`), off the reserved wood floor, inside the crop's box, 170 px off a
  standing well (a GUESS of `seat_wells`'), and the engine's `well_at` (D2), the first admitted drawn. In Rust (`homesteads/wells.rs`): the groups, the
  candidates and their order; the door asks the verdicts. Labeled: the groups the greenfield's (0196's one well to about ten);
  the gap's middle a GUESS (no page says where among the houses), a seat between two houses, which is open ground at a
  dwelling's wall by construction.
- **D6 - no belt polygon in the seating**: a seat in the gap between two of a group's houses stands inside the house cloud, and
  the belt's near face stands `BELT_NEAR_FT` (36 ft, a GUESS on 0071) behind the windward fringe, so no such seat lies in the belt (0072: "not in
  the windbreak", a preference the current ranking keeps by sorting belt seats last) - held by a check on the finished map
  (a well inside the drawn belt counted), not by building the belt here. Deviation recorded: the ranking's minimax walk (a GUESS,
  `PoolScore`) gives way to the groups' halving, which bounds each well's households near ten by construction (0196).
- **D7a - the lane-side form beside the track in Rust, this landing** (spec-fidelity's ruling on the 2026-11-06T08:04Z blocks):
  its candidates the track's verges - points along the track out at its tread's half-width and `WELL_VERGE_FT` either side -
  grouped as D5's are and ranked by the distance to their group's middle, asked in that order by the door as D5's are (the
  engine's `well_at`, D2); no belt polygon (D6). `stage_lane_wells` keeps its own Python copy of `seat_wells` until its phase.
- **D7b - the grove farms' water and the retirement houses, as the Rust decides them**: each grove farm's well pocket is the Rust
  seating's (`homesteads/bundle.rs`, T30), drawn here; the shared row wells' seats (`shared_row_wells`: a mark at the middle of
  each stretch of at most 1.6 reaches, then a half and a quarter lot either way, either side of the tread) and the dispersed
  channel form's channels (`farm_water.farm_channels`) are decided in Rust this landing (`homesteads/wells.rs`,
  `homesteads/farm_water.rs`), the door drawing what they return; each keeper's retirement house is the Rust seating's
  (`Kind::Retirement`, its lots' quota, T30), drawn here.
- **D7c - the retirement search for a settlement whose seating laid none**: reachable - it runs where no plain house carries a
  fixture and the family form is `retirement_house`, and seats one house where the seating's share rounded to none (its
  `max(1, ...)`). Ported, not dropped: the floor of one keeper moves into the Rust lots' quota (`Lots::deal`, the retirement
  kind's carriers at least one where its share is above nothing), so the seating decides every retirement house and the
  Python search is deleted with nothing left that reaches it (`make dead-closure` recorded at the landing).

6. **The exits.** As above (T33's checklist part A item 6: `make rust-gate` with no failing seed through the stage, the claims
   round IN-STEP), and: the cohort's 0196 checks (`settlement_has_wells`, `wells_among_dwellings` and the households a well serves)
on the Rust stage gate's seeds; a well in a drawn belt counted and none found; MODE AUDIT WITHIN or LEEWAY against a re-derivation
that prices the candidates asked (`## Work the first derivation missed`). Red: a seed whose wells the groups cannot seat recorded,
and `make arbiter-ask` on whether the lattice search returns; a claim that it cannot be done ruled through `make arbiter-ask`.

- research: rendering


### T34 - the port switch: the Rust stages iterated alone (amendment 8, the GM 2026-11-07: "we no longer need to join our Rust process of making maps with the Python process"; FR-023)

Occasions: none owed - tooling, no map, glyph or research page changed.

### T34 Decisions

- **D1 - one switch**: a third axis of `dev/switches.json`, `port`: `rust-only` (the default while any stage is Python) or `integrated`; read by `l7r/diagram/switches.py` as the claims switch is, a malformed entry closing to the state in force - the `port` state of the last committed `dev/switches.json` (`git show HEAD:`), `rust-only` only where that too is absent or malformed, thrown by `make switches`, which commits.
- **D2 - make done**: at `rust-only`, the test phase deselects `rolls_map` (as `make quick` does), the reference step rolls no map, and no floor rolls a settlement: the hamlet-path floor and the roll census's verdict are suspended, and the coverage floor is measured on the tests that run, a line only a map-rolling test or the left-out engine trees reached reported as information (as `dev/coverage-exempt.json`'s lines are); no Python settlement-engine test runs (amendment 10, T35: the engine's test trees left out, a test elsewhere that would roll a settlement or regenerate a pool map skipped); static, format, typecheck, hooks-test, counters-inert, the tooling, tools, hooks, labels, pipeline and interactive tests and `make rust-test` run as before.
- **D3 - make land and the push**: at `rust-only`, `scripts/land.py` starts no landing cohort, and `scripts/gates/cohort_gate.py` judges every engine landing by the Rust stage gate's record (FR-019) alone, whether or not the delta touches `rust/`.
- **D4 - what stays, and what waits**: the Rust stage gate, the work budgets and their ratchet (FR-022), the claims rule (FR-021) and the static checks stay; the settlement-reviews FR-019 owes for the pool hamlets a Rust stage moves wait for the switch's throw back to `integrated`, each owed then (T33's among them); the Python stages keep running after the Rust front in `make hamlet` and `make map`, as information.

### T34 Approach (2026-11-07T05:06Z)

1. **The goal, in the world.** Every landing of a Rust stage waits only on what the Rust stages do: no landing cohort, no map-rolling test, no reference map.
2. **The constraints.** FR-019, FR-021, FR-022, FR-023; feature 132's switch rules (one tracked file, written by its make target, which commits; a malformed file fails to the state in force).
3. **Where each comes from.** G: the GM 2026-11-07 (`request.md`, amendment 8). O: `make done` a median of 333 s in November, pytest 235 s of it, measured 2026-11-07 (`dev/run-log/2026-11`); `make cohort` about 6 min, measured 2026-11-06 (the run log's timestamps).
4. **Do they describe the world here?** Tooling only; no map changes.
5. **The order.** Before any further phase; T27-T33's landing then rides it.
6. **The exits.** Green: `make hooks-test` and the new switch tests pass, `make done` green at `rust-only` with no `rolls_map` test run, `make land-tooling` lands the scripts. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: a switch read once a run.
8. **The budget.** One tooling landing.
9. **Done, measured.** `make done`'s wall time at `rust-only`, measured at the landing (`dev/run-log`).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no - tooling; the Rust gate's own time (the row seating's `seat_rows`, 74 s a call on seed 321538, measured 2026-11-07) is a separate task.

### T34 Approach (re-answered 2026-11-07T13:27Z)

1. **The goal, in the world.** Every landing of a Rust stage waits only on what the Rust stages do: no landing cohort, no map rolled, no Python settlement-engine test (amendment 10), and the loop fast.
2. **The constraints.** FR-019, FR-021, FR-022, FR-023 as reworded (T35); feature 132's switch rules.
3. **Where each comes from.** G: the GM 2026-11-07 (`request.md`, amendments 8 and 10). O: `make done` 344 s green at rust-only, pytest 287 s of it (`dev/run-log/2026-11`, measured 2026-11-07); `make cover-changed` 68 min to 14 s, measured 2026-11-07 (its own wall time, `date +%s` either side); the crate's tests 1,058 s to 7 s, measured 2026-11-07 (`make rust-test`'s wall time).
4. **Do they describe the world here?** Tooling and the Rust stages' own speed; the row seating's maps may shift by fractions of a foot (the GM 2026-10-18: speed work may change maps).
5. **The order.** Before any further phase; T27-T33's landing rides it.
6. **The exits.** Green: `make hooks-test` and the switch tests pass, `make done` green at `rust-only`, the landing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: a switch read once a run.
8. **The budget.** One landing.
9. **Done, measured.** `make done`'s wall time at `rust-only` (`dev/run-log`).
10. **Before moving a constant.** `SET_OUT_TOL_FT` and `FEW_SEGMENTS`, drawing grains labeled at their point of change.
11. **Before fitting things into room.** Not a room question.

### T34 part B (2026-11-07T05:47Z)

The trigger: two red `make done` runs in a row (red-gate@2026-11-07T05:45:49Z), the round arbiter ruling CONTINUE.

1. **What exactly is refusing?** The static phase, each time before any test ran: first clippy on T33's appurtenances Rust
   (single-letter names, manual midpoints, casts, an iteration style), then rustfmt on the code those fixes rewrote.
2. **A3 again.** The crate's lint and format rules, unchanged: every Rust file clippy-pedantic clean and rustfmt formatted.
3. **A4 again.** Read in the gate's log: `rust_checks.py lint` and `format` now clean on the crate.
4. **Moving something placed earlier to suit something later?** No: lint and format only, the same output.
5. **Tuning or changing?** Neither: the expressions rewritten to their lint-clean forms (`f64::midpoint`), the geometry's names
   excused at their module as the crate's other modules do.
6. **The one-sentence test.** "T33's Rust never met the lint because `make quick` does not run it; it does now, and the gate runs."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire; its ruling: one more `make done`.
9. **After a ruling, the step it named?** `make done` once more, after the lint and the format pass clean.

### T34 part B (2026-11-07T08:56Z)

The trigger: a third red `make done` in a row (red-gate@2026-11-07T06:12:19Z), the round arbiter ruling CONTINUE.

1. **What exactly is refusing?** The static phase's `rust_checks.py cover`: the crate below 100% of its lines, on T32's and T33's
   branches no test or driver call reached (the appurtenances door, the far channel's straight chord, the wells' groups, a row
   reach cut at a brook, the road's and the connector's band fallbacks, the fill's stale entry) and assert messages on their own
   lines, which run only when a test fails.
2. **A3 again.** The crate's floor, unchanged: every line run by its own tests or its Python driver.
3. **A4 again.** Read in `make cover-changed`: no `.rs` line named; then `rust_checks.py lint` and `format` clean.
4. **Moving something placed earlier to suit something later?** No: tests and driver calls added; the branch-free rewrites (a
   point segment's divisor, a never-empty group list, the fill's first pop) give the same output.
5. **Tuning or changing?** Neither: no number or rule moves.
6. **The one-sentence test.** "T32's and T33's fallbacks shipped with no test that reached them; each has one now, and a coverage
   run that fails says why instead of naming every file at line 0."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire; its ruling: cover-changed, lint
   and format clean first, the pool maps checked, then one `make done`.
9. **After a ruling, the step it named?** Those, in its order; a red that a local pass could have caught is a process fault.

### T34 part B (2026-11-07T12:26Z)

The trigger: a red `make done` in a row (red-gate@2026-11-07T12:03:56Z), the round arbiter ruling PROCESS-FAULT.

1. **What exactly is refusing?** The static phase's `rust_checks.py cover`: llvm-cov's summary counted 7 lines missed, six closures
   no test called on lines that run, where `make cover-changed`, reading the LCOV lines alone, had passed.
2. **A3 again.** The crate's floor at the spec's strictness: every line run and every function called, by its own tests.
3. **A4 again.** Read in both `rust_checks.py cover` and `make cover-changed` on one tree, through the one reader
   (`rust_checks.lcov_missed`): both clean.
4. **Moving something placed earlier to suit something later?** No: the six closures each given a test that reaches them (a crop and
   a far ditch for the channels, a third group of wells, a household's well, wells along a row's street, a dry exit walled by the
   wood seats); the Python doors compiled out behind the crate's `python` feature, never dropped by a filename pattern.
5. **Tuning or changing?** Neither: no number or rule moves.
6. **The one-sentence test.** "The gate and cover-changed read one floor by two measures; they read it through one reader now, at the
   gate's strictness, and the closures it found are tested."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire; its ruling: the shared reader and its
   test, the six closures, the doors settled, both floors clean, lint and format, then one `make done`.
9. **After a ruling, the step it named?** Those, in its order.

### T34 part B (2026-11-07T12:33Z)

The trigger: a red `make done` in a row (red-gate@2026-11-07T12:28:52Z), the round arbiter ruling CONTINUE.

1. **What exactly is refusing?** test-full, before any test ran: `/bin/sh: Syntax error: Unterminated quoted string` - the rust-only
   branch of the test recipe's coverage step held a comma its `$(if)` took as the separator; the static phase was green.
2. **A3 again.** The gate's recipes parse at both port states.
3. **A4 again.** Read in `make -n test | sh -n` and `make -n done | sh -n` at rust-only and at `PORT=integrated`, and in
   `pytest --collect-only` with the rust-only selection.
4. **Moving something placed earlier to suit something later?** No: one word of a message, the comma made " - ".
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "A message's comma split a make `if` no gate had run; it is gone, and both port states' recipes parse."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire; its ruling: the parse at both states,
   the rust-only collection, then one `make done`.
9. **After a ruling, the step it named?** Those, in its order.

### T34 part B (2026-11-07T12:45Z)

The trigger: a red `make done` in a row (red-gate@2026-11-07T12:40:50Z), the round arbiter ruling CONTINUE.

1. **What exactly is refusing?** test-full's tests, the first run of the phase to its end at rust-only: 7,586 passed, 5 failed - stale
   tooling assertions this feature's own moves left (bare-GUESS claims, a test module's claim, `KnobIn` public, the default port,
   the track's Steps naming T32's deleted functions).
2. **A3 again.** Each check as it stood, its fixture brought to the tree.
3. **A4 again.** Read in the four files' run (106 passed) and in the next `make done`.
4. **Moving something placed earlier to suit something later?** No: claims and assertions brought to what the code now is.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "Five checks still described the code before this feature moved it; they describe it as it stands."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire; its ruling: one more `make done`.
9. **After a ruling, the step it named?** That, the tree as it stands; T35 filed for the engine trees the rust-only gate leaves out.


### T35 - the rust-only gate's Python trees (the round arbiter on red-gate@2026-11-07T12:40:50Z)

FR-023 keeps "the Python unit tests that roll no map", while the gate at rust-only leaves out the engine's whole test trees
(`PY_ENGINE_IGNORE`) on the GM's word of 2026-11-07 ("You should immediately stop running all of the python map generating code as
well. That's only slowing us down."), and every test that would regenerate a pool map or roll a settlement is skipped
(`tests/conftest.py`). The spec and the gate are brought to one rule, FR-023's wording changed to the gate's: no Python
settlement-engine test runs at rust-only, as amendment 10 asks ("stop running all of the python map generating code"); putting the
engine's tests back in would contradict it.

### T35 Approach (checklist part A)

1. **The goal, in the world.** None in the map: the gate does what the spec says it does.
2. **The constraints.** FR-023, SC-016; the GM's words of 2026-11-07 (request.md amendment 8 and the session's).
3. **Where each comes from.** G: the GM's words. O: the gate as T34 left it.
4. **Do they describe the world here?** Not a map question.
5. **The order.** After T34, before the feature closes.
6. **The exits.** Green: FR-023's wording and the gate agree, reviewed by spec-fidelity (SC-016). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Not a search.
8. **The budget.** One landing.
9. **Done, measured.** `make done` at rust-only collects what FR-023 names.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T37-T43 - amendment 11: the Python hamlet engine deleted, the Rust stopped at the last efficient stage (FR-024, SC-017; the GM 2026-11-07: "That sounds good. Please proceed with that.")

Occasions: none owed for the deletion, the cut, the gates or the crate split (no map, glyph or research page changes); T42's
first Rust map owes the review gate's glyph-checks when the port switch is thrown back (FR-023 defers them while it stands at
`rust-only`).

### T37-T43 Decisions

- **D1 - the order** (the GM's agreed order): T37 freeze the writeup; T38 park the Rust past the cut; T39 delete the Python hamlet
  engine and its tests, with the code-reading checks (T40) and the gates (T41's switch-offs) in the same landing so the tree stays
  green; T42 the Rust driver; T43 the crate split. One `make done` green before the landing, which carries T27-T33's unlanded
  commits with it.
- **D2 - the cut** (FR-024 part 2): through `waterward`. Measured on `dev/work-budget.md` (2026-11-06, 4 seeds a size): water_frame
  56, field 185,335, sink 2,107, seat 36,892, hem 31,440, waterward 0 at 40 households (the reference spec is a comb field; waterward lays reed strips only on a
  polder, budgeted at 1 and counted on a polder by the crate's tests); homesteads 13,170,400. The seat stands at
  193 times its paper budget of 191 but at 37 thousand operations in all, its overage approved by the GM (2026-11-07, "the seat
  ones sound good too"); it is flagged, not cut. The parked modules (`homesteads`, `track`, `appurtenances`, `law`, `ways`) are
  used by no kept module (each kept module's `crate::` uses, read 2026-11-07: field uses counts, course, hem and pyrand; sink and
  course use field and sink; seat, hem and waterward use field).
- **D3 - the delete set** (FR-024 part 3): by reachability, not by a list - every `l7r/` module the kept roots (the hand-drawn
  maps' `.gen.py`, Mode A's modules and tests, the interactive and labels packages, the kept `scripts/`) do not import once the
  hamlet packages are gone. Measured 2026-11-07 (an `ast` import graph over `l7r/`): the hand-drawn maps' `.gen.py` import only `interactive.sheet`,
  `interactive.compound_kinds`, `labels.hand_sheet` and `compound`, and nothing they reach imports a deleted package but
  `interactive/conditions.py`'s lazy `settlement._knobs`; the `overlap` package is imported only by the engine and its
  tests, so it goes too; the modal conditions import `settlement._knobs` lazily, so the knob registry is exported once, before the
  deletion, to a data file (`l7r/diagram/knobs.json`: each knob's name, value space and default) that the modal checks and the
  Rust driver read. Deleted: `hamletgen`, `settlement`, `sitegen`, `waterfields`, `overlap`, `citybudget`, the `pipeline` and `ci`
  modules and `tools` that roll or read a hamlet, their tests (`tests/hamletgen`, `settlement`, `sitegen`, `waterfields`, `gate`,
  `full`, `tier_city`, `tier_town`, `soak` and the files of the dropped tools), and `pool/hamlets/*/*.gen.py`.
- **D4 - the gates** (FR-024's last paragraph): deleted with the Python they run - `tools.rust_gate` and `dev/rust-gate/frozen/`
  (Python pickles), `make cohort`/`cohort-landing`, the reference map step, the hamlet-path floor, the roll census, `make
  hamlet`/`map`, `make work-budget`'s Python roll, `make placement-stages`'s generator, `PY_ENGINE_IGNORE` (nothing left to ignore);
  the review gate's pool-hamlet units retire with the scripts. Kept: `make rust-test`, the Rust coverage floor, the claims rule on
  the Rust through the cut, the budgets of the stages through the cut (read from the driver's counts once T42 lands; until then
  from the crate's counters test). The `port` switch stays at `rust-only`, now its only state that has an engine.
- **D5 - the driver** (FR-024 part 5): a binary target `hamlet` in the Rust tree; a pool hamlet's spec moves from its `.gen.py`
  call to `pool/hamlets/<name>/<name>.spec.json` (the same fields: name, seed, households, down_deg, water_sink, settlement form,
  pins); `make hamlet SPEC=<path>` runs it, writing `<name>.svg` and `<name>.json` beside the spec. Built stage by stage: the
  plan and the water frame, then the field (the first map), then sink, seat, hem and waterward, each enabled once it draws.
- **D6 - the crate split** (FR-024 part 6): a cargo workspace - one crate for the shared geometry, counts and random stream, one per
  stage, one for the driver; the `python` feature and PyO3 gone (D3). The `counters` feature is OFF by default and on only where the
  counts are read - `make work-budget` and the counters' own test run (the GM 2026-11-07: "We should probably run with counters
  compiled out by default"; it was on in every build before). Measured before and after: `cargo build --timings` from clean and
  after a one-line edit to one stage.
- **D7 - every consumer caught mechanically** (FR-024 part 4; the round arbiter on ask:444-a11-plan-d7, which replaced a hand
  census of every kept file - 464 files on a word-bounded search, "settlement" and "overlap" being prose words - with this rule):
  1. After the deletion the kept suite and every kept make target run green; an import of a deleted module fails loudly.
  2. A new test in the kept suite, under `make done` (`tests/tooling/test_no_deleted_engine.py`), refuses any kept file across
     `l7r/`, `tests/`, `scripts/`, `.claude/`, `pool/`, the `Makefile`, `pyproject.toml` and `dev/*.json` that names a deleted
     package - `hamletgen`, `settlement`, `sitegen`, `waterfields`, `overlap`, `citybudget` - word-bounded, in an import form
     (`import l7r.diagram.X`, `from l7r.diagram import X`, `from l7r.diagram.X`), a relative form (`from .X`, `from . import X`,
     `from ..X`) or a path form (`l7r/diagram/X`, `l7r.diagram.X`, `tests/X`). Its history allowlist is enumerated file by file in
     the test (`scripts/gates/closed-before-375.txt`, `scripts/gates/room_table.json`, the named hook fixtures, the named prose
     `.md` files, the named tests whose fixtures build a tree of the old name); no glob, directory or format is an entry. The
     append-only run, perf and bypass logs are outside the scope (`dev/*.json` is its one `dev/` entry), so none needs an entry.
  3. Every code-reading check keeps a Rust fixture test proving it still fires: the claims index, the claims report and the
     claims gate (SC-017's refuses-with-no-Python test is the gate's), the tunables, the work-budget bundle and `budget_change`,
     the file and function caps.
  Parts 2 and 3, not part 1, catch the silently vacuous class - round 1's `[ -d l7r/diagram/hamletgen ] || exit 0`, which passes
  every run once its directory is gone.

  The code-reading checks, and the tools dropped, each on its own line:

  | consumer | what it reads | fate |
  |---|---|---|
  | `scripts/gates/claims-gate.sh` | its guard tests for `l7r/diagram/hamletgen` | PORTED: the guard reads `rust/`; SC-017's fixture |
  | `scripts/record/claims.py`, `l7r/diagram/tools/claims.py`, `dev/claims-index.json`, `dev/claims-deferred.json` | the `Research:` claims of the Python and the Rust | PORTED: the Rust reader stands (`tools/claims_rust.py`), the Python roots narrowed to the kept code; a Rust fixture |
  | `scripts/record/tunables.py` | GUESS and CONVENTION values in the Python engine | PORTED: the kept Rust's `Research:` lines; a Rust fixture |
  | `scripts/reviews/work_budget_bundle.py`, `scripts/budget_change.py`, `l7r/diagram/tools/work_budget.py` | the stages and their counts | PORTED: the stages through the cut, counted by the crate; a Rust fixture |
  | `scripts/gates/rust_checks.py` | the extension's import path (`phases_ext.py`) | PORTED: the maturin build and the `python` feature dropped (D6) |
  | `scripts/gates/check-file-scale.py`, `scripts/gates/check-function-cap.py` | file and function sizes | ALREADY read `.rs` (`dev/rust-tooling.md`); the fixture kept |
  | `l7r/diagram/tools/counters_inert.py` | the counters change no output | PORTED: the Rust half kept, the Python roll dropped |
  | `scripts/record/modal_bundle.py`, `l7r/diagram/interactive/conditions.py` | the knob registry | PORTED: read `l7r/diagram/knobs.json` (D3) |
  | `l7r/diagram/tools/placement_stages.py` | the Python stages' docstrings, to write the writeup | DROPPED now; its Rust form is the later page that replaces the frozen copy (FR-024 part 1) |
  | `l7r/diagram/tools/cache_audit.py` | the generation cache's candidates over the Python engine's source | DROPPED: what it audits is the Python engine's source as the Python generation cache keys it, and the Rust driver has no generation cache - a port would have nothing to audit |
  | `l7r/diagram/_census.py` | a Python roll (the roll census) | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/_memory.py` | a Python roll's end (`roll_scope`) | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/pipeline/rollcache.py` | Python rolls, cached | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/tools/cohort_audit.py` | a cohort of Python rolls | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/tools/hamlet_floor.py` | coverage of the Python rolls | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/tools/mapcheck.py` | the pool maps, regenerated | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/tools/marsh_edges.py` | a Python-drawn hamlet page's marsh edges | DROPPED: reads a Python-drawn map, not source |
  | `l7r/diagram/tools/notes_census.py` | a Python roll's counts for a `.notes.md` | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/tools/overlap_census.py` | a Python roll's checks | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/tools/perf_fanout.py` | the Python roll's call volumes | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/tools/perf_profile.py` | a Python stage's profile | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/tools/perf_share.py` | the Python roll's kept profiles | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/tools/perf_snapshot.py` | the reference hamlet's Python timings | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/tools/phase_calls.py` | the Python stages' calls | DROPPED: reads a Python roll, not source |
  | `l7r/diagram/tools/rust_gate.py` | the Rust stages driven from Python, with pickled frozen inputs | DROPPED: replaced by the Rust driver's seeds (T42) |
  | `l7r/diagram/tools/scatter_audit.py` | a Python-drawn map's ground cover against the engine's keep-outs | DROPPED: reads a Python-drawn map, not source |
  | `l7r/diagram/tools/see_through.py` | a Python-drawn page's opacities against `settlement/see_through.py` | DROPPED: reads a Python-drawn map, not source |
  | `l7r/diagram/tools/stage_sizes.py` | a Python roll's stage sizes | DROPPED: reads a Python roll, not source |
  | `pool/magistracies/*/*.gen.py`, `pool/country-shrines/*/*.gen.py` | `interactive.sheet`, `interactive.compound_kinds`, `labels.hand_sheet`, `compound` (the measured import walk, 2026-11-07) | ALREADY: nothing from a deleted package; kept unchanged |

### T36 Approach (checklist part A)

1. **The goal, in the world.** `make test-full` runs in significantly under a minute (the GM 2026-11-07).
2. **The constraints.** FR-023, FR-024.
3. **Where each comes from.** G: the GM 2026-11-07 (`request.md`, amendment 10). O: `make test-full` 214 s, measured 2026-11-07 (its wall time); the slowest tests, measured 2026-11-07 (`make durations N=60`).
4. **Do they describe the world here?** Tooling and engine structure; no researched value moves.
5. **The order.** After T41: the deleted trees take most of the suite with them, then the tooling tests' fixture builds.
6. **The exits.** Green: `make test-full`'s wall time, measured at the landing (`date +%s` either side). Red: what failed recorded and the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (D1).
9. **Done, measured.** `make test-full`'s wall time, measured at the landing (`date +%s` either side).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T37 Approach (checklist part A)

1. **The goal, in the world.** The placement-order writeup stays readable as the reference the Rust map is judged against, and nothing regenerates it from Python.
2. **The constraints.** FR-024 part 1.
3. **Where each comes from.** G: the GM's words (`request.md`, amendment 11); the GM's mid-turn word on freezing it.
4. **Do they describe the world here?** Tooling and engine structure; no researched value moves.
5. **The order.** First (D1).
6. **The exits.** Green: `make placement-stages` names the frozen reference and rolls nothing. Red: what failed recorded and the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (D1).
9. **Done, measured.** `make placement-stages` names the frozen reference and rolls nothing.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T38 to T38 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
### T39 Approach (checklist part A)

1. **The goal, in the world.** No Python module rolls or draws a hamlet; the hand-drawn maps and Mode A unchanged.
2. **The constraints.** FR-024 part 3, SC-017.
3. **Where each comes from.** G: the GM's words (`request.md`, amendment 11). O: the import graph over `l7r/`, measured 2026-11-07 (an `ast` walk).
4. **Do they describe the world here?** Tooling and engine structure; no researched value moves.
5. **The order.** After T38, in one landing with T40 and T41 (D1).
6. **The exits.** Green: the kept tests green; `make test-full`'s count and wall time. Red: what failed recorded and the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (D1).
9. **Done, measured.** the kept tests green; `make test-full`'s count and wall time.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T40 to T40 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: T41 to T41 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
### T42 Approach (checklist part A)

1. **The goal, in the world.** `make hamlet SPEC=` draws a pool hamlet through the cut from Rust alone.
2. **The constraints.** FR-004, FR-024 part 5.
3. **Where each comes from.** G: the GM's words (`request.md`, amendment 11); the frozen plates (T37).
4. **Do they describe the world here?** Tooling and engine structure; no researched value moves.
5. **The order.** After the T37-T41 landing.
6. **The exits.** Green: each pool spec's wall time; each enabled stage held to what its frozen plate says the stage does, never to its output (the GM 2026-11-07: "the maps do NOT have to match, they do NOT need to be identical"), and the cohort's map checks clean; a visual defect pass before the GM looks ("you can do your own visual pass first"). Red: what failed recorded and the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (D1).
9. **Done, measured.** each pool spec's wall time; the cohort's map checks clean on 1,000 comb seeds and 300 of each polder; the visual pass's findings fixed or ruled on by the research.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T43 Approach (checklist part A)

1. **The goal, in the world.** An edit to one stage rebuilds only that stage and its dependents.
2. **The constraints.** FR-024 part 6.
3. **Where each comes from.** G: the GM's words (`request.md`, amendment 11) ("no obvious issues like recompiling every single file every time we make a change to one file").
4. **Do they describe the world here?** Tooling and engine structure; no researched value moves.
5. **The order.** After T42, or before it if the driver's builds measure slow.
6. **The exits.** Green: `cargo build --timings` from clean and after a one-line edit, before and after. Red: what failed recorded and the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (D1).
9. **Done, measured.** `cargo build --timings` from clean and after a one-line edit, before and after.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T37-T43 the shared approach

1. **The goal, in the world.** A Rust program draws a hamlet through its sixth stage in well under a second, and the loop around it
   (build, test, gate) runs in well under a minute (the GM 2026-11-07: "significantly under a minute").
2. **The constraints.** FR-021 (claims), FR-022 (budgets), FR-024; the hand-drawn maps' checks and Mode A unchanged.
3. **Where each comes from.** G: the GM's words (`request.md`, amendment 11). O: the budget table, measured 2026-11-06 (`make work-budget`);
   the import graph and the crate's `crate::` uses, measured 2026-11-07 (an `ast` walk, a grep); `make test-full` 214 s, measured
   2026-11-07 (its wall time).
4. **Do they describe the world here?** Tooling and engine structure; the maps drawn by Rust replace the Python's, judged against
   the frozen plates.
5. **The order.** D1.
6. **The exits.** Green: SC-017. Red: what failed recorded and the task set down; a process stop to `make arbiter-ask`.
7. **The search smell.** None new: the driver runs each stage once.
8. **The budget.** One landing for T37-T41, one each for T42 and T43.
9. **Done, measured.** `make done`'s wall time, the driver's wall time on each pool spec, the rebuild after a one-line edit.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T37 part B (2026-11-07T18:14Z)

The trigger: a red `make done` in a row (red-gate@2026-11-07T18:13:02Z), the round arbiter ruling CONTINUE. The gate carried
T37-T41's landing (the frozen writeup, the parked stages, the deletion of the Python hamlet engine and the ported checks).

1. **What exactly is refusing?** Two different one-line defects in two runs: static's Rust coverage (an assertion's message line in
   `water_frame.rs` no test reached, the assertion rewritten for the counters-off build), then test-full's 1 of 9,058 tests
   (`test_file_scale.py::test_the_refusal_prints_the_procedure`: a prose edit dropped the `structures/` its refusal names).
2. **A3 again.** Each check as it stood.
3. **A4 again.** Each fix read in its own check's run (the crate's cover clean; the file-scale tests 21 passed) and in the next
   `make done`.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "Two checks read text this landing's edits had changed; each reads it as it stands."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire; its ruling: one more `make done`.
9. **After a ruling, the step it named?** That, on the commit holding both fixes.

### T27 part B (2026-11-07T18:14Z)

The trigger: red-gate@2026-11-07T18:13:02Z, ruled CONTINUE; T27 (the seat) is an open task this landing carries, its code kept in
the crate through the cut (FR-024 part 2) and unchanged by these fixes.

1. **What exactly is refusing?** Not the seat: the two defects of T37 part B.
2. **A3 again.** Unchanged.
3. **A4 again.** The crate's tests and coverage clean with the seat in it.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "The seat's code is as it was; the gate's reds were elsewhere."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The tripwire asked it; one more `make done`.
9. **After a ruling, the step it named?** That.

### T34 part B (2026-11-07T18:14Z)

The trigger: red-gate@2026-11-07T18:13:02Z, ruled CONTINUE; T34 (the port switch) rides this landing, its rust-only gate now with
no Python engine tree left to leave out.

1. **What exactly is refusing?** Not the switch: the two defects of T37 part B.
2. **A3 again.** Unchanged.
3. **A4 again.** `tests/tooling/test_switches.py` green with the rust-only assertion reading the deleted trees as deleted.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "The switch stands at rust-only; the reds were elsewhere."
7. **Done:** `make done` green at the current tree.
8. **Every route measured before the arbiter was asked?** The tripwire asked it; one more `make done`.
9. **After a ruling, the step it named?** That.
