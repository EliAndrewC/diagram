# Derivation - burial (feature 444)

## Contract

- Reads: the knob `hamlet_burial` (a pinned value must be an attested one).
- Writes: nothing drawn; `meta.hamlet_burial`, the village's ground on a hamlet (0236).
- Keeps: where the dead lie - the village's ground, off the map; no hamlet ground drawn (0236). The cohort's checks read nothing it places.
- Bounds: the same one record at every size (measured 2026-10-28: `village_ground` at 10 and 20 households, the reference manifests). The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell.

## The algorithm

    resolve the knob: a pin, checked against the attested values, or the village's ground
    write it to the manifest

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 at 20, 1 at 40, 1 at 80 | the whole stage: one record | the same at every size |
| the knob | per item | 2 | a pin's test, and its value against the attested ones | always 2 |
| the write | per item | 1 | the one manifest record | always 1 |
| slack | per item | 1 | nothing varies | not applicable |

So: 1 x (2 + 1) x 1, flat in households.

## Totals

- at 20: 1 x (2 + 1) x 1 = 3
- at 40: 1 x (2 + 1) x 1 = 3
- at 80: 1 x (2 + 1) x 1 = 3

- FR-014 re-score: every factor is an exact count, no density or candidate taken at its worst, so the typical case is the derivation as it reads (rubric S8; ask:444-budget-standard)

## Cheaper algorithms considered

- sweep: not used - nothing is placed
- grid or spatial index: not used - nothing is placed
- priority queue: not used - nothing is ranked
- incremental update: not used - one record, once
- memoizing what a scan does not change: not used - there is no scan
