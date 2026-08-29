# The checks audit for feature 150, under the GM's rule (2026-08-29)

**The rule, in the GM's own words**: *"if there is an automated check, which is checking for something
which the placement rules are responsible for always getting right, then the automated check is not
serving any purpose. The unit tests will still serve the purpose of validating the placement code. that
the automated checks are really only there for things which can come about systemically without any
single placement rule having failed to fire. So we should be careful and cautious about what automated
checks we add since most of the ones that we used to have are no longer valid."*

The test each check must pass, therefore, is not "does it catch a real defect" but: **can the defect arise
with every placement rule working as written?** If one placer is responsible for it, the placer's unit
test owns it and the gate check is dead weight - it runs on every map forever to re-assert something that
cannot vary.

## What feature 150 actually added: one check, and it is 149's

Measured off the check-name fixture between this clone's merge base and its head: **139 added no check
names at all.** Every dike-pond check it appeared to own (`mulberry_banks_clear_of_channels`,
`dikepond_*`, `polder_parcels_are_organic`, `polder_waterward_flanks_wet`) predates it and was retired by
main's own audit (features 141/145/146, 637 check names -> 153). What 139 did was MODIFY existing checks.

| what 139 did | check | main's verdict | ours |
|---|---|---|---|
| read the DRAWN stroke, not only the record | `sluice_gates_on_water` | KEPT | re-apply: it corrects an existing check's fidelity, adds no new rule |
| count the title placard as frame-setting | `crop_hugs_content` -> `map_frame_hugs_its_content` | KEPT (renamed) | re-apply: it prevents a FALSE POSITIVE against 149's title-pocket behavior |
| skip the rule on a map declaring no work yards | `harvest_yards_present` | retired | drop - nothing to modify |
| stand aside on a dike-pond | `paddy_plot_seams_shared` | KEPT | re-apply |
| classify the new families | `every_feature_classified_for_matrix`, `all_ink_is_ruled_on` | KEPT | re-apply - these two are registries, and an unclassified family is exactly a SYSTEMIC gap |
| snap the gate to the drawn water | `sluice_gates_centered_on_their_channel` | retired | drop |
| the dike-pond family | `mulberry_banks_clear_of_channels`, `dikeponds_fed_and_drained`, `dikepond_water_within_banks`, `dikepond_corners_rounded`, `dikepond_is_ponds_in_a_block` | retired | **do not resurrect** |

## Applying the rule to the retired dike-pond family

Each was written by an earlier feature and each fails the GM's test - which is why main was right to cut
them, and why porting 139 must not bring them back:

- **`mulberry_banks_clear_of_channels`** - a bank cannot lap a channel unless `build_polder` puts it
  there. One placer owns the bank's geometry; `tests/waterfields/` owns that placer. Systemic? No.
- **`dikepond_water_within_banks`**, **`dikepond_corners_rounded`**, **`dikepond_is_ponds_in_a_block`** -
  all three assert the SHAPE the conversion draws. The conversion is one function with one set of unit
  tests. Systemic? No.
- **`dikeponds_fed_and_drained`** - the sluice pairs are emitted by one loop. Systemic? No.
- **`polder_parcels_are_organic`** - the wander is one knob in `_polder_parcels`. Systemic? No; a unit
  test on the vertex and square-corner counts is the honest guard, which is what feature 149's
  `make polder-probe` now reports on demand and what `tests/waterfields/test_polder_ring.py` pins.
- **`polder_waterward_flanks_wet`** - the strips are drawn by `stage_waterward` from a declaration it
  makes itself. Systemic? No.
- **`channel_field_anchored`** - the hairline's mouth is placed by `_comb_source_channel`. Systemic? No.
- **`harvest_yards_present`** - the yard is attached by the homestead placer. Systemic? No.

## The one check we keep, and why it passes the rule

**`waterward_strips_run_off_the_frame`** (feature 149). The failure it catches needs no placer to
misbehave: `stage_waterward` draws a band `WATERWARD_DEPTH` deep, correctly, and `crop_to_content` frames
the map from the content, correctly - and the strip's outer edge appears in frame anyway, because the two
independent decisions met on a map whose content happened to be wide. Neither rule failed to fire. No unit
test can see it, because the answer depends on the finished frame of a particular map. That is precisely
the systemic class the GM describes, and it is why the check exists rather than a test.

## What this costs, honestly

The dike-pond map now ships with its shape guarded by unit tests and by the GM's own eye rather than by
nine gate checks. That is the intended trade: the checks were re-asserting on every map, forever, what one
placer decides once. Where a rule turns out to matter and to be systemic, it can be added back - one at a
time, each with this test applied to it in writing.
