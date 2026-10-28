# Implementation Plan: the work-budget program - every phase rebuilt to an algorithmic budget

**Branch**: `444-work-budget-program` (no branch; `main` in the clone) | **Date**: 2026-10-28 | **Spec**: `spec.md`

**Input**: `spec.md` (the round arbiter's accept at the round cap, ask:444-spec-round-3), `request.md` (the design the GM approved,
steps 3 to 6). The instrument and the check are feature 443's, closed 2026-10-28.

## Summary

Step 3 first: every stage of `STAGES` gets a derivation on paper in the template's form (`.specify/templates/derivation.md`), a
MODE BUDGET verdict of SOUND from the `work-budget` agent and a budget in `dev/work-budget.json`; their sum and the whole roll's
exponent go to the GM through `escalation-check` - the program's CHECKPOINT, before any rebuild (FR-001, FR-002). Then the phases,
one task each in `STAGES` order, through the phase checklist (FR-003 to FR-006), the whole-table bundle before the first phase
lands (FR-007), the language decision after phases 1 and 2 (FR-008), and, if Rust, the ports proven first (FR-010 to FR-012).

This plan plans step 3 in full (T01-T06). The phase tasks are filed after the GM's checkpoint, each with its plan section and its
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
dispatched again; the third round on one stage owes the round arbiter's ruling first (the tripwire). SOUND: `make budget-set`
pins it. The agent is not a wave job (the GM's list, `scripts/container/append-system-prompt.md`), so the dispatches are plain
Agent calls, at most three in one message.

**D4 - Families, as 443 counted them** (the tasks' size): every stage of `STAGES` - 23, measured 2026-10-28 (the `STAGES` tuple of `l7r/diagram/hamletgen/driver.py`, the same list `dev/work-budget.json` holds and `tests/tooling/test_budget_change.py` keeps equal to it) - in the four families 443's T09-T12 used - water (6:
water_frame, field, sink, waterward, pond_stock, pond_bank), homesteads (7: seat, homesteads, appurtenances, burial, lane_wells,
sties, washing), ways (3: track, web, crossings), hinterland and frame (7: hinterland, woodland, windbreak, bamboo, frame, notice,
labels). One task per family, each landing its derivations, verdicts and budgets together.

**D5 - The checkpoint** (FR-002): the target is the sum of the 23 budgets at 40 households, and the whole roll's exponent (the
fit of the summed budgets at 20, 40 and 80 households); with it, the opening record's whole-roll figure and each stage's ratio of
today to budget (the counts are read only now, after every budget is pinned). The draft goes through `escalation-check`, then to
the GM in the turn's final message; his words set it with `make budget-program OPS_AT_40= EXPONENT= WORDS=` (logged in
`dev/work-budget-changes.jsonl`). No phase task is filed before.

## Task approaches

T01 D2's tooling; T02-T05 the four families' derivations, verdicts and budgets (D1, D3, D4); T06 the checkpoint (D5).

### T01 - a budget counts the derivation's own items (D2)

`items_at_20`, `items_at_40` and `items_at_80` beside `per_thing`; `make budget-set` requires them; `make work-budget` and the ratchet read them and refuse a budgeted row without them. And the bundle's form check requires the contract's four parts: its `Reads:`, `Writes:` and `Keeps:` lines (the cohort properties and the claims), each filled (the design's checklist box 1).

### T01 Approach (checklist part A)

1. **The goal, in the world.** A stage's budget means the derivation's arithmetic, at each size, whatever the manifest counts.
2. **The constraints.** FR-001; the spec's Edge Cases (a stage that places nothing has a whole-stage figure); D2.
3. **Where each comes from.** G: the design the GM approved, 2026-10-28 (`request.md`, section 2, S7).
4. **Do they describe the world here?** `seat` and `sink` place nothing, measured 2026-10-28 (`make work-budget`, run 20261028T152105Z-45aa176ec9b8, its placed column).
5. **The order.** First: every `budget-set` of T02-T05 needs it.
6. **The exits.** Green: tests set a budget with its items and read its budget at 20, 40 and 80 households in the record and the ratchet; `budget-set` without them refused, and a budgeted row without them refused by the record and the ratchet; red with each condition deleted. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** The tests green.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

### T02 - the water family's budgets (D1, D3, D4)

water_frame, field, sink, waterward, pond_stock, pond_bank: each derived, judged SOUND and pinned.

### T02 Approach (checklist part A)

1. **The goal, in the world.** Each water stage has a budget an independent judge, blind to today's code and counts, found derived.
2. **The constraints.** FR-001; the rubric S1-S7; the template (443 T13); D1, D3.
3. **Where each comes from.** G: the design the GM approved, 2026-10-28 (`request.md`, step 3).
4. **Do they describe the world here?** Each stage's contract, read from its docstring, `dev/placement.md` and its claims when its derivation is written.
5. **The order.** After T01.
6. **The exits.** Green: six SOUND verdicts recorded and six budgets pinned. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; six dispatches, more where a verdict asks a correction.
9. **Done, measured.** Six `budgeted` rows in `dev/work-budget.json`, each with its derivation and verdict.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets; no code a roll runs changes.

### T03 - the homesteads family's budgets (D1, D3, D4)

seat, homesteads, appurtenances, burial, lane_wells, sties, washing: each derived, judged SOUND and pinned.

### T03 Approach (checklist part A)

1. **The goal, in the world.** Each homesteads-family stage has a budget an independent judge found derived.
2. **The constraints.** FR-001; the rubric; the template; D1, D3.
3. **Where each comes from.** G: the design the GM approved, 2026-10-28 (`request.md`, step 3).
4. **Do they describe the world here?** Each stage's contract, read when its derivation is written.
5. **The order.** After T01.
6. **The exits.** Green: seven SOUND verdicts and seven budgets pinned. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; seven dispatches, more where a verdict asks a correction.
9. **Done, measured.** Seven `budgeted` rows.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets.

### T04 - the ways family's budgets (D1, D3, D4)

track, web, crossings: each derived, judged SOUND and pinned.

### T04 Approach (checklist part A)

1. **The goal, in the world.** Each ways stage has a budget an independent judge found derived.
2. **The constraints.** FR-001; the rubric; the template; D1, D3.
3. **Where each comes from.** G: the design the GM approved, 2026-10-28 (`request.md`, step 3).
4. **Do they describe the world here?** Each stage's contract, read when its derivation is written.
5. **The order.** After T01.
6. **The exits.** Green: three SOUND verdicts and three budgets pinned. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; three dispatches, more where a verdict asks a correction.
9. **Done, measured.** Three `budgeted` rows.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets.

### T05 - the hinterland and frame family's budgets (D1, D3, D4)

hinterland, woodland, windbreak, bamboo, frame, notice, labels: each derived, judged SOUND and pinned.

### T05 Approach (checklist part A)

1. **The goal, in the world.** Each hinterland and frame stage has a budget an independent judge found derived.
2. **The constraints.** FR-001; the rubric; the template; D1, D3.
3. **Where each comes from.** G: the design the GM approved, 2026-10-28 (`request.md`, step 3).
4. **Do they describe the world here?** Each stage's contract, read when its derivation is written.
5. **The order.** After T01.
6. **The exits.** Green: seven SOUND verdicts and seven budgets pinned. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; seven dispatches, more where a verdict asks a correction.
9. **Done, measured.** Seven `budgeted` rows.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - paper budgets.

### T06 - the program's target to the GM (D5)

The sum at 40 households and the whole roll's exponent, beside today's figures, through `escalation-check` to the GM; his words
set it with `make budget-program`.

### T06 Approach (checklist part A)

1. **The goal, in the world.** The GM approves, in his own words, what the whole roll should cost before any phase is rebuilt.
2. **The constraints.** FR-002; D5.
3. **Where each comes from.** G: the design the GM approved, 2026-10-28 (`request.md`, step 3: "The GM approves the target").
4. **Do they describe the world here?** The budgets T02-T05 pin, one per stage of `STAGES`, and today's record, read after them.
5. **The order.** After T02-T05; before any phase task is filed.
6. **The exits.** Green: the GM's words recorded by `make budget-program`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; one escalation-check.
9. **Done, measured.** `dev/work-budget.json`'s program row set, its words in `dev/work-budget-changes.jsonl`.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - the target, on paper.

## Project Structure

- Step 3: `specs/444-work-budget-program/phases/<stage>.derivation.md` and `<stage>.verdict.txt` for each of the 23 stages;
  `dev/work-budget.json`; T01's `scripts/budget_change.py`, `l7r/diagram/tools/work_budget.py` and their tests.
- After the checkpoint: one task per phase (FR-003), each with `phases/<stage>.md` from the phase checklist; `make
  work-budget-bundle MODE=table` before the first phase lands (FR-007); `research/language.md` after phases 1 and 2 (FR-008).

## Complexity Tracking

None.
