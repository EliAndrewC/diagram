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
2. **Tier 2 looks like it is half coverage tracing** - 45 s untraced against 116 s traced - **and it
   is not.** That reading is wrong and R5 is where it was corrected: the 116 s run had a COLD roll
   cache in it, while `make durations` rolls no maps at all, so the two differ in two variables at
   once. On a warm tree the same target is 16-23 s, and the tracer's share of it is small. Recorded
   as the reading it was, because it is the one that sent this feature after `COVERAGE_CORE=sysmon`.

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

## R4. What the plot grid buys (the lever that DOES work)

Same test, same branch, same envelope; only `plot_across` and `row_step` change. Wall times were
taken with other work on the machine and are indicative; `plots` and `err` are exact.

    across=46   step=(26,30)   fit_field 35.0 s   plots=1985   err 0.891
    across=92   step=(52,60)   fit_field 16.5 s   plots= 539   err 0.891
    across=138  step=(78,90)   fit_field 17.2 s   plots= 257   err 0.891
    across=184  step=(104,120) fit_field 13.1 s   plots= 148   err 0.891
    across=276  step=(156,180) fit_field  4.9 s   plots=  30   err 0.969

138 was taken: it is a 7.7x cut in the plot count with the acreage error, the winning aspect and the
legality verdict all unchanged, and it keeps a fan large enough that the carve is doing real work.
276 was declined - the error moves, which means the fan has stopped being the thing the branch is
about. `make cov-file FILE=tests/hamletgen/test_seed_branches_147.py MOD=l7r/diagram/hamletgen/water.py`
confirms lines 128-135 (the re-search branch this test exists for) are still executed.

## R5. The coverage core: sysmon is slower here

Python 3.14, coverage 7.15.2, line coverage only (no `branch = true`) - the configuration
`sys.monitoring` exists for. Same tree, same selection, back to back:

| core | wall | CPU | coverage table |
|---|---|---|---|
| the C tracer (default) | **16.2 s** | 1 m 30 s | - |
| `COVERAGE_CORE=sysmon` | **20.1 s** | 1 m 59 s | byte-identical to the above |

REJECTED. And the premise behind trying it was itself wrong: the "coverage roughly doubles the gate"
reading in R1 came from a baseline `make test` whose roll cache was cold. On a warm tree the tracer's
share is small, so there was never a large win to chase here.

## R6. The proof census, corrected

Round 2 of `spec-fidelity` reported 42 registered checks with no firing proof of any kind. That count
looked at `tests/gate/test_scripted_fixtures.py` and `pool/regressions/` only; it did not count
`tests/check_village/test_segments_*.py`, where most checks are proved to fire on a hand-built
manifest. Measured over all three sources:

| | before this feature | after |
|---|---|---|
| registered check names | 154 | 151 |
| with a firing proof somewhere | 144 | 138 |
| with none | **10** | **13** |

Six of the 13 are a naming artifact rather than a check: `capital_/city_/town_/village_has_kosatsuba`
and the `*_has_no_headman` family are ONE segment each emitting `check(f"{scale}_has_...")`, whose
hamlet variant is live and proved. Nothing to delete and nothing to save.
