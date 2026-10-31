# Derivation - water_frame, greenfield (feature 444 FR-015)

## Contract

- Reads: the map's spec - its name, its households, its scale and the knobs it pins - and the map's seed.
- Writes: the map's plan, drawn nowhere: the ground's fall and the water's drainage bearing, declared apart (0054: "Every map declares its land's fall and its water's bearing, separately"), the wind's quarter, and each knob's form for this map, rolled from the seed (constitution XII: "several attested forms are a knob rolled from the map's seed, never a choice"), into the manifest's `meta` record.
- Keeps: the water's bearing strays from the land's fall by less than a right angle (0054: "the bound is a strict 'under 90'"); a knob's form is one its own page attests for the map's settlement form, and a pinned knob keeps the spec's value; every later stage reads the plan rather than deciding it again.
- Bounds: the plan's knobs: 21 plan fields, each a `meta` key of the reference manifests (`water_frame.keys.json`; corrected 2026-10-30 by the round arbiter's ruling on ask:444-T19-which-knobs, the first reading's 20 having counted the knob registry's names, most of them rolled by other stages) - settlement_form, cluster_shape, water_sink, lane_skeleton, lane_web, bamboo, grove_sides, grove_flank, row_line, row_sides, row_water, row_shelter, well_siting, farm_water, manure_form, copse_siting, kosatsuba_siting, plot_size, grain_drift, intake, brook_side - the same at every size; a knob that applies only on one branch (a form, a brook, flood ground) is rolled only there, and written alone elsewhere; three declared bearings (the fall, the drainage bearing, the wind, the last declared or regional, never rolled); the spec's three identity fields (name, households, scale); the reference spec (Inashiro: nucleated, brook-fed, not on flood ground) pins no knob.

## The algorithm

    the identity fields copied from the spec into the plan (1 each)
    the land's fall rolled from the seed; the drainage bearing rolled from the range within 90 degrees of it, so the bound holds by construction; the wind's quarter rolled
    for each knob that applies on this map's branch: its allowed forms read (1), one rolled from the seed or the spec's pin taken (1), written (1); a knob with one form left read and written (2); a knob outside its branch written alone (1)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the plan, once a map | always 1 |
| the identity fields | per item | 3 | name, households and scale, each copied once (1) | always 3 |
| the bearings | per item | 6 | the fall, the drainage bearing and the wind, each rolled and written (2); the bearing's bound against the fall folded into its roll, a range drawn within it | always 6 |
| the knobs | per item | 47 | on the reference (nucleated, brook-fed, not on flood ground): 12 that apply - settlement_form, cluster_shape, water_sink, lane_skeleton, lane_web, bamboo, well_siting (nucleated), manure_form, plot_size, grain_drift, intake and brook_side (a brook) - read, rolled, written (3 each, 36); copse_siting and kosatsuba_siting, one form left each, read and written (2 each, 4); 7 outside the branch written alone (1 each, 7): grove_sides, grove_flank and farm_water (the dispersed farm's), row_line, row_sides, row_water and row_shelter (a row's) | a linear row on dry ground: 55 - its four row fields and the two grove fields rolled (18, against the reference's 6 writes), well_siting and cluster_shape written alone (-4); not growing with the households |
| slack | per item | 1 | no factor varies: each is a count of the plan's own fields | not applicable |

So: 1 x (3 + 6 + 47) x 1, flat in households.

## Totals

- at 20: 1 x (3 + 6 + 47) x 1 = 56
- at 40: 1 x (3 + 6 + 47) x 1 = 56
- at 80: 1 x (3 + 6 + 47) x 1 = 56

## Growth

Flat: the plan's fields are the same at every size, an exponent of 0.

## Cheaper algorithms considered

- sweep: not used - nothing is ordered
- grid or spatial index: not used - nothing is geometric
- priority queue: not used - nothing is ranked
- incremental update: not used - each field is written once
- memoizing what a scan does not change: not used - there is no scan

## Earlier findings

- verdict-1, finding 1: fixed - the knob set it judged (the 20 knob-registry names among the reference `meta`) was the wrong set: most of them are rolled and charged by other stages. The round arbiter's ruling on ask:444-T19-which-knobs (2026-10-30) names water_frame's knobs as the 21 plan fields the plan rolls inside the Contract, each charged only for the steps it takes on the reference branch; the bound folded into the drainage roll, as the pseudocode now says (no separate test).
