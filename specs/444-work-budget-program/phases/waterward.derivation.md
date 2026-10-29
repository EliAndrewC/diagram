# Derivation - waterward (feature 444)

## Contract

- Reads: the plan's field archetype (the reference: `valley_paddy`, measured 2026-10-28 from the reference manifests' `meta.field_archetype`).
- Writes: a polder's reed fringe along its water-facing flanks, and `meta.waterward` - nothing on the reference, because a valley comb has no polder dike.
- Keeps: the stage's research rules hold where it draws; on the reference it draws nothing, so no cohort property reads it. The cohort's checks read nothing it places on the reference.
- Bounds: the budget is held on the reference roll, a valley comb at every size; a polder or dike-pond roll is outside it.

## The algorithm

    test the archetype; on a valley comb, return

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 (the whole stage) | it places nothing on the reference | the same at every size |
| the archetype test | per item | 1 | one comparison | always 1 |
| slack | per item | 1 | nothing varies: one test, on the reference always the same | not applicable |

So: 1 x 1 x 1 = 1 basic operation, flat in households.

## Totals

- at 20: 1 x 1 x 1 = 1
- at 40: 1 x 1 x 1 = 1
- at 80: 1 x 1 x 1 = 1

- FR-014 re-score: every factor is an exact count, no density or candidate taken at its worst, so the typical case is the derivation as it reads (rubric S8; ask:444-budget-standard)
- reason above today's count: today's 0 counts nothing: a valley hamlet draws no waterward fringe; the budget is the one test that decides it

## Cheaper algorithms considered

- sweep: not used - nothing is placed on the reference
- grid or spatial index: not used - nothing is placed on the reference
- priority queue: not used - nothing is placed on the reference
- incremental update: not used - nothing is placed on the reference
- memoizing what a scan does not change: not used - there is no scan
