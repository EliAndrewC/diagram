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

### T15 - phase: water_frame, through the checklist (FR-003, FR-004, FR-005; step 4)

Occasions: none - the plan's rolls and the meta it writes are unchanged, so no map moves; no glyph, form or placement rule.

### T15 Approach (checklist part A)

1. **The goal, in the world.** The water frame rebuilt to its greenfield derivation - the plan's rolls counted where they happen, in the first stage, so the roll's count holds the work the plan does, and whatever of the old stage the derivation does not carry deleted.
2. **The constraints.** FR-003, FR-004, FR-005; rubric S5; the greenfield derivation `phases/water_frame_greenfield.derivation.md` and its budget, 69, set with the GM's words.
3. **Where each comes from.** G: the GM, 2026-10-29 ("yes please do step 4 and then we can stop and assess how things are going"); the design's step 4 (`request.md`, section 6).
4. **Do they describe the world here?** The plan's rolls (`plan_site`), today outside any stage's counted window; the stage's meta writes.
5. **The order.** First of step 4; before `field`.
6. **The exits.** Green: the stage counts its rolls at most its budget at 40 and 80, the cohort unmoved, `phases/water_frame.md`'s eight boxes ticked. Red, over its budget: rebuilt again, or the budget raised with the GM's words (`make budget-change`, FR-006) - never set down, never an arbiter's accept; a stop to assess goes to the GM, as he asked ("then we can stop and assess how things are going").
7. **The search smell.** none
8. **The budget.** One landing; one MODE AUDIT pass.
9. **Done, measured.** `make work-budget`: water_frame's counted operations at 40 and 80 against 69, its exponent 0.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a


### T16 - phase: field, through the checklist (FR-003 to FR-006; step 4)

Occasions: settlement-review on the pool hamlets the rebuilt field moves (a map's form changes - its comb's basins, ditches and brook redrawn); glyph-check only if a glyph is redrawn.

### T16 Approach (checklist part A)

1. **The goal, in the world.** The comb field rebuilt to its greenfield derivation: the brook and its intake, the fan's outline, the comb's ditches and basins cut once with every rule asked before a basin is written, no repair pass.
2. **The constraints.** FR-003 to FR-006; rubric S1-S9; `phases/field_greenfield.derivation.md` and its budget, 23,988 at 40, exponent 0.79; the research its contract cites (0005, 0017, 0053, 0054, 0059); the manifest keys today's stage writes (FR-004).
3. **Where each comes from.** G: the GM, 2026-10-29 ("yes please do step 4 and then we can stop and assess how things are going"); the design's step 4.
4. **Do they describe the world here?** The comb field, the form the reference spec rolls - the polder, never dealt at random (0019), is a phase of its own after step 5's language decision (`phase: field_polder`, the round arbiter's ruling ask:444-T16-polder-budget), reached through the plan's declared archetype, never a flag or a fallback from the comb.
5. **The order.** After `water_frame`; the last of step 4, then the assessment with the GM.
6. **The exits.** Green: counted operations at most the budget at 40 and 80, `make cohort-landing` with no regressed seed and the fresh block's rate no worse, the claims round IN-STEP, the reviews owed, MODE AUDIT WITHIN, `phases/field.md`'s eight boxes ticked, the old comb code deleted whole (the old polder engine and what it alone reaches stand until `field_polder` deletes them; if the two share helpers so the comb cannot be deleted clean, the polder is done inside this task, ask:444-T16-polder-budget). Red, over its budget: rebuilt again, or the budget raised with the GM's words (`make budget-change`, FR-006) - never set down, never an arbiter's accept; a stop to assess goes to the GM, as he asked ("then we can stop and assess how things are going").
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


### T17 - phase: field_polder, the polder field, after the language decision (ask:444-T16-polder-budget)

Occasions: settlement-review on the pool's polder hamlets the rebuild moves; glyph-check only if a glyph is redrawn.

### T17 Approach (checklist part A)

1. **The goal, in the world.** The polder field - its ring dike, its sluices, its ring canal, its surveyed grid or dike-pond mosaic - rebuilt to a greenfield derivation of its own, its budget held at the push like any stage's.
2. **The constraints.** FR-003 to FR-006, FR-015, FR-016; the round arbiter's ruling ask:444-T16-polder-budget (route (c) with (a)'s held row); 0019.
3. **Where each comes from.** A: the round arbiter, ask:444-T16-polder-budget; G: the GM, 2026-10-29 ("yes please do step 4 and then we can stop and assess how things are going").
4. **Do they describe the world here?** The pool's polder hamlets (Kuwabata among them); a `field_polder` reference spec added to `make work-budget`, scaled to the sizes the reference is rolled at.
5. **The order.** After step 5's language decision, before `sink` in `STAGES` order, written in the language it picks.
6. **The exits.** Green: its derivation SOUND or accepted, its row pinned (FR-013), its counted operations within it at 40 and 80, the cohort, the claims round and settlement-review, MODE AUDIT WITHIN, the old polder code deleted in its landing. Red, over its budget: rebuilt again, or the budget raised with the GM's words (`make budget-change`, FR-006).
7. **The search smell.** none
8. **The budget.** One landing; one MODE BUDGET pass a round; one MODE AUDIT pass a round.
9. **Done, measured.** `make work-budget`'s `field_polder` row within its budget at 40 and 80.
10. **Before moving a constant.** The research page each figure cites, read before it moves.
11. **Before fitting things into room.** n/a

