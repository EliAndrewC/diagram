# Feature 405 - the engine and record findings moved from 385

**Feature Branch**: none (worked on `main` in a session clone)

**Created**: 2026-10-19

**Status**: Filed, not started - it starts after 385 closes and is on main (the GM, 2026-10-19)

**Approved**: the GM, 2026-10-19, "Let's keep the current round of process tasks such that all open process tasks stay in 385 and everything else moves into a new feature.  Then we can finish and land our process tasks and then start the new feature after that ends up in main."

**Affects**: hamlet, research record, waterfields

## The request

The GM, 2026-10-19, verbatim:

> Let's keep the current round of process tasks such that all open process tasks stay in 385 and everything else moves into a new feature.  Then we can finish and land our process tasks and then start the new feature after that ends up in main.

> But don't you start the new feature, just file it.

## What it holds

Every open task of feature 385 that was not process work, moved verbatim to `tasks.md` on 2026-10-19, each keeping its 385 id:

- the six remaining ranking rows of 385's FR-020 (385 T35-T40) and the one replacing T32's dead row (385 T144): ten claims on
  328's ranking, read as the round arbiter ruled on ask:t33-ranking-pick (live rows only; a kind not yet tried where one is left);
- D17's side-by-side merge carried from 385 T03 (385 T12);
- the findings the claims and record checks of 385's tasks raised on code and pages those tasks did not change (385 T111-T147):
  lane ends and their trims, the bund and the field reach, the fixture seats, the track's fallbacks, and three record wordings.

## Requirements

- **FR-001 (each moved task)**: each task is worked as 385 worked its tasks - the checklist's part A answered, its decisions
  reviewed (or declared wording only), its checks run and recorded, a retro row - and lands by the route its change owes.
- **FR-002 (found work stays here)**: a finding a task's checks raise on code it did not change is filed as a new task of this
  feature (the GM, 2026-10-19, on 385: "Yes we should keep findings on code a task didn't change as new tasks in 385." - carried
  here with the work it governed).

- **FR-003 (the ranking rows)**: the seven ranking rows (385 T35-T40, T144) are taken from 328's ranking as the round arbiter
  read 385's amendment 7 on ask:t33-ranking-pick - live rows only, a kind not yet tried where one is left, else the top-ranked
  live row, said so in the task's Approach - each marked with its wave in 328's `audit/waves.json`.

## Success Criteria

- **SC-001** (FR-001, FR-002, FR-003): every task in `tasks.md` ticked with its retro row, each finding its checks raised on
  unchanged code filed here, each ranking row marked with its wave, and the GM's review box.
