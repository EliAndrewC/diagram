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


### T19 - phase: water_frame, its Rust port (FR-017; after the tooling proof)

Occasions: settlement-review on each pool hamlet the port moves (D7: every plan rolls anew, so the layouts downstream move).

### T19 Approach (checklist part A)

(The round arbiter, 2026-10-30, ask:444-T17-rows-need-a-phase, Route A, narrowed by the plan review of 2026-10-30: T19 also proves the two tooling rows the fixture cannot fire - `cache audit` (it audits maps, and the fixture draws none) and `the overlap census` (its replacement, the counters inside Rust, designed with this port) - before its tick; `check-rust-tooling.py` refuses the port's landing until they are.)

1. **The goal, in the world.** `water_frame` in the extension module, written from `phases/water_frame_greenfield.derivation.md`
   (its derivation came out the same as today's code: rolls and writes, no search), the stage a thin Python function calling it.
2. **The constraints.** FR-010, FR-017; the derivation's Contract and its pinned budget (`dev/work-budget.json`); the phase-source guard holds its
   old code while this task runs.
3. **Where each comes from.** G: the GM, 2026-10-29 (FR-017: water_frame's Rust port a task of its own, landed before the feature
   closes).
4. **Do they describe the world here?** One stage, one derivation; the manifest keys it writes are today's.
5. **The order.** After the tooling proof; before the field rebuild, so the first Rust landing is the smallest.
6. **The exits.** Green: counted operations within the pinned budget (`dev/work-budget.json`) at every size `make work-budget` rolls, MODE AUDIT
   WITHIN on the `.rs` modules, `cache audit` and `the overlap census` proven on the port (each check refusing a copy of the port
   written to break it, named in `dev/rust-tooling.md`'s "Proven" table - not merely run green), `make cohort-landing` with no regressed seed, the Rust coverage floor whole. Red: a count over its budget, or MODE AUDIT not WITHIN, goes to the round arbiter (`make arbiter-ask`) with the measurement -
   a route, never an acceptance: a phase over its budget is rebuilt or its budget changed with the GM's words (FR-006).
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** `make work-budget`: water_frame's count at every size against its pinned budget; `cache audit` and `the overlap census` in the "Proven" table with their firing cases; `make perf-ab` beside it, recorded.
10. **Before moving a constant.** The research page each rolled knob cites (0054), read before it moves.
11. **Before fitting things into room.** n/a

**Performance work?** yes - docs/performance-checklist.md's questions follow.

### T19 part B (2026-10-31T02:51Z)

The trigger: `make cohort-landing` under the port (`phases/water_frame.cohort-landing-1.txt`, dev/cohort-log/20261031T025046Z): 47 of
54 pass the whole gate, against main's 54 of 54 on the same seeds; seeds 3, 20, 21, 36, 37, 903 and 904 newly failing.

1. **What exactly is refusing?** Not water_frame: its own checks hold (56 counted, MODE AUDIT WITHIN, FR-004, FR-012). Later stages
   refuse, each with a kind main's cohort knows - seed 3 and 36 `SiteRefused` (the seating), 20 and 21 `lane_knots 1`, 904
   `lane_knots 2`, 37 `OverlapRefused`, 903 `WebRefused`. Seeds 3 and 903 are named by an open found row,
   `l7r/diagram/hamletgen/ways/web.py::stage_web` (E3, a footpath to every farmhouse 7 ft off a plot): that row is read before any
   probe. The geometry of each refusal is NOT yet dumped - item 7.
2. **A3 again.** The rules refusing are the later stages' own (R: research-backed), unchanged by the port.
3. **A4 again.** Not yet looked at on the map, seed by seed - item 7.
4. **Moving something placed earlier to suit something later?** Not proposed: no fix is drafted.
5. **Tuning or changing?** Neither yet.
6. **The one-sentence test.** "The port re-rolls every plan; seven seeds now refuse in later stages" - the GM would ask whether the
   later stages fail on new rolls generally. Measured: main's own fresh-seed cohort (dev/cohort-log/20261030T233704Z, seeds from
   355289, commit 81a8dbc39) passes 46 of 54, on the same refusal kinds. Recorded as a number beside the diagnosis owed, not as an
   explanation (constitution XIII: a rotated residue is no defense).
7. **The next step is a measurement:** each of the seven seeds rolled on the port and dumped where it refuses (the lanes and what
   stands near them, the seat band for the two SiteRefused), the open found row read for 3 and 903; then each named as a defect of a
   later stage, with its fix, before any route is put to the round arbiter.

   **Item 7, begun (2026-10-31T03Z).** The open found row for seeds 3 and 903 (`specs/328-match-the-research/claims-followup.md`,
   E3, DRIFTED) is a known defect of the web: footpaths held 7 ft off a garden fence (0246) leave farmhouses off the network -
   "WebRefused at (3024, 3004) and (3265, 2589)" on Kashikawa, "re-route or re-seat so the gap holds". Seed 903's `WebRefused` is that
   row's kind; seed 3 refuses earlier, in the seating (`SiteRefused`), so the row does not explain it alone. The five others are
   not yet dumped.

   **Item 7, each seed rolled alone on the port (`make cohort N=1 SEED=<s> FRESH=0`, 2026-10-31T03Z):** seed 3 and 36 `SiteRefused`
   - "seated 19 of 20 households on margin 1", one house short of the band; 20, 21 and 904 `lane_knots` - 1, 1 and 2 knots, two
   lanes within the 25 ft join reach left unjoined (15.2, 18.9 and 20.6 ft); 37 `OverlapRefused` - "lanes would be recorded on a
   gardens at (1545, 2814)"; 903 `WebRefused` - "lanes 1, 2 (skeleton: dangling_ends) still break a rule of the lane law", the E3
   row's kind. All seven refuse in the seating, the lane knots or the web - none in water_frame - each a class main's own fresh-seed
   cohort fails on (46 of 54). The lanes and the seat band at each place are not yet dumped.

### T19 part B (2026-10-31T03:05Z)

The trigger: the round arbiter's fair comparison (ruling on ask:444-T19-cohort-regression), the port rolled on main's own fresh block
(`make cohort N=48 SEED=355289 FRESH=0`, dev/cohort-log/20261031T030442Z): 44 of 54 pass against main's 46 of 54 at 81a8dbc39
(dev/cohort-log/20261030T233704Z); 7 of main's failures pass, 9 seeds newly fail (355298, 355302, 355305, 355306, 355327, 355329,
355334, 903, 904), and seed 355306 refuses `SiteRefused`, a class main's block never shows - the ruling's branch 3, a fault in the
port's rolls.

1. **What exactly is refusing?** Later stages, as before - `lane_knots` 4, `WebRefused` 4, `row_rules` 1, `SiteRefused` 1 (355306, a
   linear map of 19 households). The forms rolled match main's (nucleated 28 / linear 15 / dispersed 11 against 27 / 13 / 14), so the
   settlement form's odds are not the fault; every dispersed map passes on both.
2. **A3 again.** The refusing rules are the later stages' own, unchanged by the port.
3. **A4 again.** Read in the port's caller, against the old `plan_site` (81a8dbc39): the old code rolled every knob on every form;
   the port rolls a knob only on its derivation branch, else writes its table's first form. A branch is right only where no stage
   reads the knob off it.
4. **Moving something placed earlier to suit something later?** No: the fix is in water_frame's own rolls.
5. **Tuning or changing?** Changing: a wrong branch, not a value.
6. **The one-sentence test.** "Every row and farm hamlet was seated in the stubbiest band, because the port held the cluster's shape
   at round outside a cluster" - a defect the GM would recognize as one.
7. **Found:** `cluster_shape` was on the nucleated branch, but `seat_cluster` (`ways/track.py`, every form) and `seat_room` size
   every map's margin band and canvas through `band_extent(households, cluster_shape)`; on the port every linear and dispersed map
   took "round" (aspect 2.2, against elongated's 5.0). The grove knobs are read only by the row seating (`homesteads/rows.py`), the
   row and farm-water knobs only behind their form, `well_siting` only by the nucleated wells: those branches stand. Fixed
   (`_KNOBS`: `cluster_shape` on `all`), with `test_the_cluster_shape_rolls_on_every_form_since_every_band_is_sized_by_it`
   red on the unfixed branch (`('linear', {'round'})`); the derivation's per-form note corrected (linear 57; the reference's 56
   unchanged). Next: the same block re-rolled on the fix, and the ruling's branch read again.

### T19 Decisions

**D6 - The boundary: Python gathers, Rust rolls, Python writes** (FR-010, FR-004): `stage_water_frame` stays a thin Python function
in `STAGES`. It gathers the derivation's Reads into one record - the map's seed, the spec's name, households and scale, and for
each of the 20 knobs the forms its own table allows for the settlement form and the spec's pin if any - and calls
`l7r_phases.water_frame(record)`. Rust rolls the three bearings (the drainage bearing drawn within 90 degrees of the fall, so the
bound holds by construction) and each knob's form, and returns them with its counted operations. Python writes them where the
manifest keys are today (FR-004: the keys unchanged). The knob tables stay Python data: they are the research's tables, and one
copy of each is the rule.

**D7 - The rolls: a seeded SplitMix64 in Rust** (FR-017): seeded from the map's seed and the stage's name, no crate dependency,
the same draws on every platform. The port cannot reproduce today's draws without reading today's Python's random calls, which
the phase-source guard holds (the GM, 2026-10-30), so every map's plan rolls once anew - its fall, drainage bearing, wind and knob
forms - and the layouts downstream move. The GM's ruling of 2026-10-18 lets maps change
where they keep the research (the root CLAUDE.md, its speed-work rule under Verification and iteration): `make cohort-landing` and the claims round hold them to the research, and each pool hamlet that moves owes
its settlement-review (docs/reviews.md: a map's form changes) - this task's Occasions line is corrected to say so.

**D8 - The build: maturin into a repository-local folder, keyed to the Rust sources** (FR-010): `rust/phases/` is the crate
(`l7r_phases`); `make rust-build` builds it with maturin into `.rust-ext/` (gitignored) when its sources' code id moved, and every
target that rolls a map or runs the tests depends on it; `l7r/diagram/hamletgen` puts `.rust-ext/` on the import path. The
generation key already holds the Rust sources (T17, `gencache.rust_sources`), so a Rust change re-keys every map.

**D9 - The counts: Rust counts as Python does, and hands them back** (FR-003, FR-012; `dev/rust-tooling.md` "the overlap
census"): behind the crate's Cargo feature `counters` (FR-012: compiled out of the deployed build), the crate keeps an operation counter keyed `<kind>@<function>` as the Python counters are, returns it with the stage's result, and the
thin function adds it to the roll's counts, so `make work-budget` and MODE AUDIT read a Rust stage as they read a Python one -
the replacement for the overlap census, proven on this port by a copy that does work it does not count.

### T19 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** <the stage and the loop: `make perf-profile` time beside `make phase-calls` / `make perf-fanout` calls>
2. **Removes work, or only moves it?** <fewer candidates, a screen, a kept result, an index, an early stop, a better algorithm,
   a loop into C - or an inlining, a merge, a builtin written out: never the goal, only where the time evidence shows a gain>
3. **What do you expect it to save, and why?** <a share of the stage's profiled time>
4. **How does the work grow with the settlement?** <the growth exponent between sizes, and whether this bends it>
5. **What did the before and after show, and under what conditions?** <calls; `make perf-ab` best of N with each arm's spread,
   the host's load - evidence, not a pass>
6. **Did any map move, and does it still keep the research?** <`make maps-moved`, the cohort>


### T19 part B (2026-10-31T03:10Z)

The trigger: the same block re-rolled on the `cluster_shape` fix (dev/cohort-log/20261031T031013Z): 45 of 54 against main's 46; the
SiteRefused gone, every refusal a class main's block shows (`lane_knots` 4, `WebRefused` 4, `row_rules` 1); 8 seeds still newly
failing (355298, 355302, 355305, 355327, 355329, 355334, 903, 904), 7 of main's failures passing.

1. **What exactly is refusing?** The later stages' rules only, each a kind main's block shows; still one seat under the ruling's 46.
2. **A3 again.** Unchanged rules.
3. **A4 again.** The audit of 03:05Z item 7 carried to every off-branch knob: `well_siting` is the second of the same fault -
   `place_wells` (`homesteads/stages.py`, every form) seats the communal wells of every house without a grove, and both its first
   seating and the reach loop (`wells.py`) read `plan.well_siting`; the old `plan_site` rolled it on every form, the port held it at
   "lane" outside a cluster. The rest hold: the row knobs are read in `rows.py` and behind the linear form in `wells.py`, `farm_water`
   behind the dispersed form, the grove knobs by the row seating alone.
4. **Moving something placed earlier to suit something later?** No: water_frame's own branch.
5. **Tuning or changing?** Changing a wrong branch.
6. **The one-sentence test.** "The row and farm hamlets' shared wells were always sited by the lane, because the port held the
   siting at its first form outside a cluster."
7. **Fixed** (`_KNOBS`: `well_siting` on `all`), the test widened to
   `test_the_knobs_every_form_reads_roll_on_every_form`, red on the unfixed branch (`AssertionError: linear`); the derivation's
   per-form note now linear 59 (the reference's 56 unchanged). Next: the block re-rolled on both fixes and the ruling's branch read
   from that run.
