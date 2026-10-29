# Derivation - water_frame, greenfield (feature 444 FR-015)

## Contract

- Reads: the map's spec - its name, its households, its scale and the knobs it pins - and the map's seed.
- Writes: the map's plan, drawn nowhere: the ground's fall and the water's drainage bearing, declared apart (0054: "Every map declares its land's fall and its water's bearing, separately"), the wind's quarter, and each knob's form for this map, rolled from the seed (constitution XII: "several attested forms are a knob rolled from the map's seed, never a choice"), into the manifest's `meta` record.
- Keeps: the water's bearing strays from the land's fall by less than a right angle (0054: "the bound is a strict 'under 90'"); a knob's form is one its own page attests for the map's settlement form, and a pinned knob keeps the spec's value; every later stage reads the plan rather than deciding it again.
- Bounds: the knobs a hamlet's plan rolls: 20, the knob names among the reference manifests' `meta` fields at 10 and at 20 households (measured 2026-10-29), the same at every size; three declared bearings (the fall, the drainage bearing, the wind); the spec's three identity fields (name, households, scale); the reference spec pins no knob.

## The algorithm

    the identity fields copied from the spec into the plan (1 each)
    the land's fall rolled from the seed; the drainage bearing rolled from the range within 90 degrees of it, so the bound holds by construction; the wind's quarter rolled
    for each knob: its forms that the settlement form allows read from its table (1), one rolled from the seed or the spec's pin taken (1), written (1)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the plan, once a map | always 1 |
| the identity fields | per item | 3 | name, households and scale, each copied once (1) | always 3 |
| the bearings | per item | 6 | the fall, the drainage bearing and the wind, each rolled and written (2); the bearing's bound against the fall folded into its roll, a range drawn within it | always 6 |
| the knobs | per item | 60 | the 20 knobs, each its allowed forms read (1), rolled or pinned (1), written (1) | always 60: the knobs do not grow with the households |
| slack | per item | 1 | no factor varies: each is a count of the plan's own fields | not applicable |

So: 1 x (3 + 6 + 60) x 1, flat in households.

## Totals

- at 20: 1 x (3 + 6 + 60) x 1 = 69
- at 40: 1 x (3 + 6 + 60) x 1 = 69
- at 80: 1 x (3 + 6 + 60) x 1 = 69

## Growth

Flat: the plan's fields are the same at every size, an exponent of 0.

## Cheaper algorithms considered

- sweep: not used - nothing is ordered
- grid or spatial index: not used - nothing is geometric
- priority queue: not used - nothing is ranked
- incremental update: not used - each field is written once
- memoizing what a scan does not change: not used - there is no scan
