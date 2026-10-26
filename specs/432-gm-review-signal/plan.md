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
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T07 to T07 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
