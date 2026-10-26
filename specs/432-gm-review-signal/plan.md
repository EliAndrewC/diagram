# Implementation Plan: the GM-review queue holds only what is his (feature 432)

**Spec**: `spec.md` | **Request**: `request.md` | **Audit**: `audit/`

## Summary

One source for what reaches the GM - a QUESTION record, owed escalation-check until judged, then kept (his decision) or cut -
written by the arbiter only from `for_gm` and from a declined fix; every other ruling and every fix made stays in
`arbiter.jsonl`. The held list reads those records alone. E measures the claims triage and the pop-up cascade before
changing either. F clears the backlog with his words and carries the three that are his as kept questions.

## Measured before planning (2026-10-26)

- **What the arbiter has recorded** (observed 2026-10-26, method: every `specs/*/arbiter.jsonl` row with a `ruling`): 344
  rulings (166 round, 77 hour, 66 ask, 35 others); 25 carry `for_gm`, all on hour triggers (only the hour's ruling may
  carry one today, `hm_arbiter.record`). Under FR-001 those 25 and the 7 declined fixes are the rows that would have
  reached the door, against 465 open rows queued.
- **The held list** (observed 2026-10-26, method: `scripts/gm_review.py` `held()` and `specs/328-match-the-research/audit/
  overrides.json`): `held()` lists an override whose `flag` opens "Held"; the residence row carries a `held` key and a
  `flag` opening "deviation-tempting", so it is not listed. One override row's flag opens "Held behind" (the tubs row,
  waiting on another row).
- **Claims after a triage** (observed 2026-10-26, method: the impl-drift rows of `dev/review-ledger.md` since 2026-10-10,
  each "impl-drift: N claims - IN-STEP a, ..."): 284 passes over 3,471 claims, 2,664 IN-STEP (77%). The ledger does not say
  which passes a triage fed, so T05 measures that before deciding.

## Constitution Check

Tooling only (no engine path): `scripts/`, `tests/`, the Makefile, `.claude/agents/`, docs and the constitution's text. Lands
by the DIRECT route; no map moves. Every guard keeps its test companion (XVIII).

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
## T04 - E(b): pop-ups that share a paragraph (FR-005 b)

### T04 Approach (checklist part A)

1. **The goal, in the world.** One wording edit to a passage several pop-ups share costs one round of checks, not one a
   pop-up.
2. **The constraints.** No check skipped on a pop-up whose own text changed (FR-005's no-defect rule).
3. **Where each comes from.** O: the audit's 374#81 (about 85 checks on about six pop-ups).
4. **Do they describe the world here?** Not yet known: T04 opens by replaying the bamboo and shelter pop-up batch the
   audit names through `make record-owed`, counting what each edit owed, and why.
5. **The order.** After T03; measured before any change.
6. **The exits.** Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** 90 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** `research.md` R2: the batch's owed checks before and after, with every pop-up whose own text changed
   still owed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

- **D6** Measure first; the change is chosen from what the replay shows owed each check (a shared paragraph, a sibling's
  re-owe, or a rule of the checks) and recorded as a decision before it is made. Rendering: none.

<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
## T07 - the texts that say what reaches the GM, and the close (FR-007)

### T07 Approach (checklist part A)

1. **The goal, in the world.** No document tells a session or the GM that every ruling reaches him.
2. **The constraints.** The constitution's text changes with the amendment rule it carries.
3. **Where each comes from.** O: spec FR-007's search.
4. **Do they describe the world here?** Yes, the search's hits.
5. **The order.** Last.
6. **The exits.** Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** 30 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** Each hit of the search changed or recorded as needing none; `make feature-report F=432 WRITE=1`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T07 Decisions

- **D9** The texts change with the code of the task that makes each true (T01-T03), and T07 sweeps the rest. Rendering: none.
