# 444-work-budget-program - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-28 -->
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

