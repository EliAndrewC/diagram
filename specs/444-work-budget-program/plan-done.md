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

<!-- plan-archive: archived 2026-10-28 -->
### T07 - a derivation's arithmetic and its index cells checked before any dispatch (the GM 2026-10-28)

The GM's rule on a repeated error (`request.md`, 2026-10-28): *"anytime I hear you say that something went wrong and that you will address this by being careful in the future, then I tend to think that that will not work, unless being careful specifically means that our checklist-based process has been updated to include whatever "careful" means in that context"*.

- **Approach**: the derivation template gains a `## Totals` section - one line per size, `- at <20|40|80>: <expression> = <value>` - and `make work-budget-bundle MODE=budget` refuses, naming the line: a missing size; a value that differs from its expression's evaluation, rounded to the integer (exact - a sum written wrong); an expression that leaves out any count row's figure at that size (a total leaving out a term), every row writing its figure as `N at 20, N at 40, N at 80` or one number for every size, a row with none refused; and a derivation whose `Cheaper algorithms considered` says a grid or spatial index is used without a count row whose factor names the cells examined. A figure read at the wrong size or unit (a radius as a diameter, a record's keys as its points) no script can tell, so the `work-budget` agent's MODE BUDGET gains a fourth question asking exactly that. Why: of T02's first twelve rounds on the water family (2026-10-28, `phases/*.verdict-*.txt`), the session's own slips - a sum written wrong (19 + 8 as 26, sink round 2), a total leaving out a term (field round 1), index cells left uncounted (field round 3, sink round 3) - a script refuses; a figure read at the wrong size - the pond's radii read as halves, and a record's keys counted as its points, both found by the session, not the agent - is now the agent's own question.

### T07 Approach (checklist part A)

1. **The goal, in the world.** A derivation reaches the judge with its totals arithmetically true and its index cells counted.
2. **The constraints.** The GM's rule above; the rubric (an index cell examined is a basic operation).
3. **Where each comes from.** G: the GM, 2026-10-28 (`request.md`); O: T02's rounds (`phases/field.verdict-3.txt`, `phases/sink.verdict-2.txt`, `phases/sink.verdict-3.txt`).
4. **Do they describe the world here?** The water family's rounds, measured 2026-10-28 (the twelve verdicts recorded beside the derivations).
5. **The order.** Before T02's next dispatch; it applies to every derivation after it.
6. **The exits.** Green: the bundle refuses a missing size, a total off its expression, a total leaving out a row's figure, a row with no figure and an indexed derivation with no cells row; the agent file asks the fourth question; the fixtures pass in their concrete form, and so do the water family's derivations once their totals are written (T02's next dispatch runs on them); each refusal red with its condition deleted. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** The refusals' tests green.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

<!-- plan-archive: archived 2026-10-28 -->
### T08 - an arbiter accept pins a first budget (FR-013, SC-008)

`make budget-set ARBITER=ask:<id>`: the budget pinned on the round arbiter's ACCEPT of the derivation, refused when the arbiter's log
holds no accept at that trigger naming the stage; the pin records `pinned_on: accept`, the derivation's sha256, its rounds (the
stage's recorded verdicts) and its totals' spread (`SPREAD="<low>-<high> at <households>"`, required), for the program target (D5). `make work-budget`
and the push's ratchet (`work_budget.held`) flag an accept-pinned budget whose derivation changed since its pin, as owing the arbiter's
ruling.

### T08 Approach (checklist part A)

1. **The goal, in the world.** A stage whose total converged but whose verdict never reached SOUND is pinned on the arbiter's accept, and stays bound to the derivation it accepted.
2. **The constraints.** FR-013, SC-008 (amendment 1).
3. **Where each comes from.** G: the GM, 2026-10-28, answering 444#0 (`request.md`).
4. **Do they describe the world here?** field's accept, ask:444-T02-field-round-15 in `arbiter.jsonl`, recorded 2026-10-28.
5. **The order.** Before field's pin and before T03's first review.
6. **The exits.** Green: tests refuse a pin on an accept the log does not hold naming the stage and pass one it does; a changed derivation flagged in the record and the ratchet; each red with its condition deleted. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** SC-008's tests green; field pinned on its accept.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

