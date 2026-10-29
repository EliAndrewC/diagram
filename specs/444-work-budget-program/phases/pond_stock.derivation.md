# Derivation - pond_stock (feature 444)

## Contract

- Reads: the plan's field archetype (the reference: `valley_paddy`, measured 2026-10-28 from the reference manifests' `meta.field_archetype`).
- Writes: a dike-pond hamlet's pig sties on the dikes of the ponds nearest the houses - nothing on the reference, because a valley comb has no grow-out ponds.
- Keeps: the stage's research rules hold where it draws; on the reference it draws nothing, so no cohort property reads it. The cohort's checks read nothing it places on the reference.
- Bounds: the budget is held on the reference roll, a valley comb at every size; a polder or dike-pond roll is outside it. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell.

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

## Cheaper algorithms considered

- sweep: not used - nothing is placed on the reference
- grid or spatial index: not used - nothing is placed on the reference
- priority queue: not used - nothing is placed on the reference
- incremental update: not used - nothing is placed on the reference
- memoizing what a scan does not change: not used - there is no scan
