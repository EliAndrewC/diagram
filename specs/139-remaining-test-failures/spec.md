# Feature Specification: The Remaining Test Failures Pass

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=139-remaining-test-failures`)

**Created**: 2026-08-28

**Status**: APPROVED by `spec-fidelity` - round 1 verdict **FAITHFUL** (2026-08-28). Reviewer's aside for the GM: SC-002's "48-seed audit 48 of 48" is the widest reading of "all of the tests which we do have" (a tool run, not a suite test; carried from 137's approved FR-005) - the GM may narrow it.

**Input**: [`gm-request.md`](gm-request.md), verbatim. The goal is feature 137's - *"one hundred percent of those tests passing"* - re-cut on 2026-08-28 at the GM's instruction so that 137 could land what it had fixed while the residue stays an OPEN feature, *"to reflect the fact that we know that there are still failing tests"*.

## The feature, in one sentence

Every diagram test that still fails or is pinned as an expected failure after feature 137 landed is fixed - the pins removed, the seeds green - so that the whole suite the project HAS at completion passes with no waiver; a test the efficiency session retires as no longer valid leaves the inventory by that retirement, not by a fix.

## The inventory (measured 2026-08-28 on 137's landing commit)

| where | seeds and checks |
|---|---|
| `TRIPWIRE_EXPECTED` (`tools/mapcheck.py`) | 47: `lanes_form_one_network`, `lanes_reach_something`, `long_ditches_have_a_footbridge` |
| `GATE_COHORT_EXPECTED` (`tests/gate/hamletgen/test_driver.py`) | 42: `farmhouses_reach_a_way`; 43: `lanes_bend_like_paths`, `lanes_form_one_network`, `title_clear_of_features`; 44: `houses_clear_of_paddies` - re-measure each on the landing commit; any now green is a stale pin and comes out first |
| `COHORT_BASELINE` (`hamletgen/driver.py`) | 22: `field_ringed`; 24: `paddy_bunds_clear_the_supply_channels` |
| the 48-seed audit (`--batch 48`, households `10 + (seed * 7) % 11`) | 25 of 48 pass: `lanes_form_one_network` 8, `lanes_bend_like_paths` 7, `farmhouses_reach_a_way` 7, `kosatsuba_by_the_road` 2, `paddy_bunds_do_not_stagger` 2, `lanes_reach_something` 2, and one each of `houses_clear_of_paddies`, `title_clear_of_features`, `features_do_not_overlap`, `long_ditches_have_a_footbridge` (per-seed list in 137's tasks.md T03/T04 notes) |
| the pool hamlets (FULL-only) | Kashikawa, Mizuguchi, Sawada as measured in 137 T10 - re-measure on the landing commit |

Anything a later measurement adds joins by a task, never silently. **Reproduce a cohort seed with the batch's own household count** - a `Cohort-14` rolled at the default 15 households is a different map from the batch's seed 14 at 20 (137 lost time to this).

## User Scenarios & Testing

### User Story 1 - the pins come out (Priority: P1)

**Acceptance**: **Given** the inventory, **When** the feature is complete, **Then** every row's checks pass on its seed under the current engine, the pin rows are DELETED, and the unlocked gate, the tripwire and the 24-seed `cohort` are green with no expected failure anywhere.

### User Story 2 - a retired test leaves the inventory honestly (Priority: P1)

**Acceptance**: **Given** the "Diagram tests" session retires a test as no longer valid (the GM: *"part of what we are doing is eliminating tests which are no longer valid"*), **When** that lands on main, **Then** its inventory row is closed with a pointer to the retiring commit - never ticked as fixed, and never re-added.

### User Story 3 - no fix is a rotation (Priority: P1)

**Acceptance**: as 137 US3 - each fix is measured on the tripwire, the gate cohort and the 24-seed cohort before it is kept; a fix that closes one seed and opens another is not a fix.

### Edge Cases

- A pinned check is a WRONG RULE: fix the check, with its research recorded; the pin still comes out.
- A seed that cannot be fixed without an architectural change: deferred as constitution XIV requires (measurement, mechanism, sketch) and put before the GM - never re-pinned quietly.

## Requirements

- **FR-001**: each inventory row is a task with its own measurement, fixed in the engine or the check with the research recorded where the rule lives, and verified on the whole tripwire + gate cohort + 24-seed cohort (no rotation).
- **FR-002**: a pin row is removed in the same commit as the fix that makes it stale.
- **FR-003**: handoffs with the "Diagram tests" session continue in [`handoffs.md`](handoffs.md) under 137's rules: this session hands off only a green-gate commit; it pulls only commits that session names safe.
- **FR-004**: the feature is complete when every test the suite then has passes with no expected-failure pin and no waiver anywhere, each proven by the run that owns it; the result is reported to the GM.

## Success Criteria

- **SC-001**: no expected-failure pin or waiver of a failing check remains; the runs prove it.
- **SC-002**: the tripwire reports every seed `ok`; the cohort reports 24 of 24; the 48-seed audit 48 of 48.
- **SC-003**: `handoffs.md` has a line per pull and per handoff.

## Decisions Recorded

Carried from 137 (see its table); new rows are added here as fixes land.

## Assumptions

- The GM's waivers of 2026-08-27 stay in force for the remaining pins until each is fixed here.
- The starting point for the straggler residue is recorded in `hamletgen/ways.py` `_serve_stragglers` (137, seed 14 at 20 households: the router finds NO path for a rank of houses behind another rank, at any box size measured; a wider box alone was tried and buys nothing at 4x the time).
