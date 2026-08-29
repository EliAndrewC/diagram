# Research and measurements - feature 158

## R1. The baseline (2026-08-29, clone `diagram-tests`, merge base `77fc359a`, 8 xdist workers, warm)

| tier | command | tests | wall |
|---|---|---|---|
| 1 - quick | `make quick ALL=1` | 2,206 passed, 5 skipped | **41.4 s** |
| 2 - the gate's test phase | `make test` (coverage tracing ON) | 2,583 passed | **116 s** (10 m 35 s CPU) |
| 2 - the same tree, `--no-cov`, map rolls deselected | `make durations N=45` | 2,390 passed, 139 skipped | **45.2 s** |
| 3 - the full sweep | the FULL gate's test phase | 2,794 passed, **1 failed**, 1 skipped | **390.6 s** (28 m 16 s CPU) |
| 3 - the same tree, `--no-cov`, map rolls deselected | `make durations FULL=1 N=60` | 2,411 passed, 139 skipped | **42.6 s** |

Two readings jump out of that table:

1. **`make quick` has drifted.** Feature 147 measured the cheap loop at 26-29 s earlier the same day.
   It is 41.4 s here, and the cause is a single test (R2).
2. **The coverage tracer is roughly half of tier 2.** The same tree costs 45 s untraced and 116 s
   traced, and 28 minutes of the full tier's CPU goes through the same tracer.

**A PRE-EXISTING FAILURE IN THE FULL TIER, ledgered here, not caused by this feature** (constitution
XIII - it was measured on the merge base, before any change):

    FAILED tests/gate/hamletgen/test_driver.py::test_a_rolled_cohort_passes_the_whole_gate
    REGRESSION seed 42: farmhouses_reach_a_way - not in the pinned baseline

The merge-scope gate rolls seed 41 only and is green; the pin drift is on seed 42, which only the
full tier rolls. Nothing in this feature touches the placer. Because the phase exits at the failure,
the three coverage floors did not evaluate on that run - they are measured separately.

## R2. Where the time is - the per-test duration profile

| test | wall | runs in |
|---|---|---|
| `hamletgen/test_seed_branches_147.py::test_the_fit_gives_a_saturated_best_aspect_the_full_search_it_was_denied` | **39.2 s** | all three tiers |
| `hamletgen/test_water.py::test_a_saturated_aspect_stops_after_the_probe_instead_of_bisecting_a_fan_it_cannot_grow` | 5.1-8.2 s | all three |
| `hamletgen/test_homesteads.py::test_a_linear_hamlet_strings_its_houses_along_the_connector` | 3.9-4.8 s | all three |
| `settlement/test_homestead_parts.py::test_village_grove_keeps_the_windbreak_out_of_a_plots_west_sun_lane` | 3.9-4.5 s | all three |
| `settlement/test_land.py::test_village_grove_skips_the_dike_bank` | 2.3-2.6 s | all three |
| `settlement/test_homestead_parts.py::test_village_grove_keeps_every_clump_and_set_view_decides_which_are_on_the_page` | 1.8-2.3 s | all three |
| `hamletgen/test_hinterland.py::test_a_belt_vertex_in_the_title_pocket_is_pushed_out_of_it` | 1.5-2.0 s | all three |

Below that the tail is flat: everything else is under 1.6 s and 2,380 tests cost essentially nothing.
So the profile is one outlier, a short shoulder, and a long free tail - which is what "audit the
tests" mostly means here.

## R3. Why the 39 s test costs 39 s, and what does NOT fix it

The test sets `plan.target_acres = 500` so every fan aspect saturates - that IS the branch under
test - and `fit_field` then pays 5 aspects x 2 probe carves plus a 9-carve refinement of the best
aspect. Each carve lays the largest fan the aspect can draw.

**Measured, and the first guess was wrong.** Shrinking the test's `plan.envelope` from a 600 px
square down through 400, 300, 200 and 150 changes NOTHING: the drawn fan is 1,985 plots and the
acreage error 0.891 at every one of them.

    side=600  fit_field 61.7 s  plots=1985 | one aspect 6.3 s  err 0.891
    side=400  fit_field 52.4 s  plots=1985 | one aspect 4.4 s  err 0.891
    side=300  fit_field 99.6 s  plots=1985 | one aspect 9.9 s  err 0.891
    side=200  fit_field 81.7 s  plots=1985 | one aspect 4.8 s  err 0.891
    side=150  fit_field 40.3 s  plots=1985 | one aspect 3.9 s  err 0.891

(The wall times above are noisy because a full sweep was running beside them; the invariant `plots`
and `err` columns are the finding.) `plan.envelope` is not what clamps this fan, so "make the test
settlement smaller" in the obvious sense buys nothing here. The cost is the PLOT COUNT, and the plot
count is set by `plot_across` and `row_step` - the two arguments the test itself passes.
