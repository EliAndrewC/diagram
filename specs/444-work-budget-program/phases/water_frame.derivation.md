# Derivation - water_frame (feature 444)

## Contract

- Reads: the plan `plan_site` resolved before the first stage - the drainage bearing, the fall, the wind, the settlement form and its knobs, and the field archetype (a polder has no brook, so the brook's two fields are written empty there) - and the spec's pinned knobs (`plan.spec.pins`).
- Writes: nothing drawn; the manifest's `meta` record of the rolled plan (36 named fields: the bearing, the fall, the form, the grove, the row, the well siting, the water, the yards, the weather, the sitings), one pinned knob per pin, and three flags on the settlement that later stages read rather than the manifest (work yards, house racks, nucleated).
- Keeps: every later stage reads these values (the claims "fall and drainage declared first", 0054; "manifest record", NONE); no cohort property reads this stage beyond the fields' presence. The cohort's checks read none of its fields directly.
- Bounds: the same 36 fields at every size; the pins are the spec's own, and the reference spec pins none. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell.

## The algorithm

    write each of the 36 plan fields to the manifest's meta record
    for each pin the spec names: pin the knob to its value

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 (the whole stage) | it places nothing; its work is one record | the same at every size |
| fields written | per item | 36 | the contract's meta fields, one write each | 36: the record does not grow |
| pins | per item | 0 | one write per pinned knob, and the reference spec - the roll the budget is held on, at every size - pins none | 0 at every size |
| flags and the archetype test | per item | 4 | the contract's three settlement flags, one write each, and its one archetype test | 4 at every size |
| slack | per item | 1 | no factor varies: each is a count of the contract's own fields | not applicable |

So: 1 x (36 + 0 + 4) x 1 = 40 basic operations, flat in households.

## Totals

- at 20: 1 x (36 + 0 + 4) x 1 = 40
- at 40: 1 x (36 + 0 + 4) x 1 = 40
- at 80: 1 x (36 + 0 + 4) x 1 = 40

- FR-014 re-score: every factor is an exact count, no density or candidate taken at its worst, so the typical case is the derivation as it reads (rubric S8; ask:444-budget-standard)

## Earlier findings

- verdict-1, finding 1: fixed - carried from the verdict as it stood (its notes stand); the derivation re-scored to the typical case under FR-014
- verdict-1, finding 2: fixed - carried from the verdict as it stood (its notes stand); the derivation re-scored to the typical case under FR-014
- verdict-2, finding 1: fixed - carried from the verdict as it stood (its notes stand); the derivation re-scored to the typical case under FR-014

## Cheaper algorithms considered

- sweep: not used - nothing is ordered
- grid or spatial index: not used - nothing is geometric
- priority queue: not used - nothing is ranked
- incremental update: not used - one write per field, once
- memoizing what a scan does not change: not used - there is no scan
