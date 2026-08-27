# Research: what `make done` actually runs, and what each part costs

Feature 135. Every number here is a stopwatch on the dev container (22 threads, 8 xdist workers,
scope LOCKED to the reference hamlet, remote OFF), taken 2026-08-27 on unmodified code at
`6486be5c` unless a row says otherwise. Per-test figures are pytest `--durations` call times;
wall figures are `time`.

## R1 - the phases of an unlocked `make done` (the GM's "four or five minutes")

| phase | what | measured |
|---|---|---|
| `reference` | rolls Inashiro (seed 4) through the gate, in-process, uncached | ~26 s (timings ledger; the run-log's locked `done` totals of 33-39 s are this plus the phases below) |
| `lint` / `format` / `typecheck` | ruff, ruff format, dmypy, the duplicate-defs scan | seconds |
| `hooks-test` | 13 guard suites | 84 s, SKIPPED whenever the guard scripts are unchanged since the last green run |
| `test` (locked) | every non-map-rolling test, EXHAUSTIVE form, `--tier hamlet` | ~10 s of the 33-39 s locked total |
| `test` (unlocked) | the above plus the 31 `rolls_map` tests | measured 2026-08-26 (feature 133 T11): 233 s of a 4.5 min gate |

So the four-to-five minutes IS the map-rolling tests: the locked gate, which defers them, runs in
about 35 s and the run-log shows twenty such runs today. The audit's weight falls on those 31
tests, on the `reference` step, and on anything in the non-rolling set that is neither cheap nor
earning its time.

## R2 - collection (the GM's "something like five seconds")

`make test-file FILE="--collect-only tests"`, 8 workers: **3,755 tests collected in 1.28 s**
(2.4 s wall including make and the state write); the quick tree alone (`tests/` minus the tier,
gate and tooling trees) 2,010 tests in 0.93 s. Collection is ~1.3 s, not five - feature 133's T29
already took most of it (the tier/gate/tooling trees are not collected by quick). What remains is
per-worker import cost, and the three-tree layout cannot lower it further than ~0.3 s; the
reorganization is done for the organizational reason the GM gave, and the collection figure is
recorded so nobody expects a second five seconds from it.

## R3 - the non-rolling gate set, EXHAUSTIVE, `not rolls_map` (top of `--durations`)

| test | s | what it is | verdict |
|---|---|---|---|
| `test_villages.py::test_a_map_is_immune_to_an_upstream_change_in_the_number_of_random_draws` | 214.3 | rolls Kashikawa THREE times, un-marked (calls `runpy`, which the marker guard cannot see); today it runs only under FULL because the whole FILE is deselected | move to the full tree; mark it |
| `test_villages.py::test_village_passes_gate[*]` (4) | 77 / 64 / 41 / 24 | the pool sweep | full tree (already FULL-only via the file deselect) |
| `gate/test_regressions.py::test_full_gate_coverage_sentinel[shiro_daika]` | 10.6 | a whole-capital FULL gate run that exists to carry 33 statements of coverage | full tree - the merge check enforces no coverage floor, so this proves nothing there |
| `tooling/ci/test_state.py::test_the_short_circuit_key_contains_everything_the_stamp_hashes` | 5.1 | hashes the diagram area twice | keep (tooling; skipped when the tooling is unchanged - see R6) |
| `tier_town/tools/test_site_justice.py::test_propose_rejects_a_seat...` | 4.2 | site_justice proposes 40 seats, each gated | keep (town tier only) |
| `settlement/test_land.py::test_hinterland_..._each_cardinal` | 3.4 | four cardinals at the gate, two in quick | keep - the exhaustive form is 3 s and parallel |
| `gate/test_regressions.py::test_full_gate_coverage_sentinel[tango]` | 3.1 | coverage carrier | full tree |
| `test_villages.py::test_slow_gen_budget_fires_and_the_override_silences_it` | 3.1 | the CPU-budget guard, on a 50 ms fake gen; the 3 s is the coverage subprocess | keep; re-home out of the deselected file so the gate runs it |
| `gate/test_regressions.py::test_full_gate_coverage_sentinel[city_samurai]` | 2.6 | coverage carrier | full tree |
| `gate/test_regressions.py::test_frozen_pool_full_gate_coverage_carrier[minami]` | 2.3 | coverage carrier | full tree |
| `settlement/test_core.py::test_build_comb_supply_banks...` | 2.1 | the 5-fan comb (2-fan in quick) | keep |
| corpus replay `test_regression_fixture_still_fires[*]` | 0.2-1.6 each | the targeted bad-map replay | keep - the merge check's core; hamlet+village fixtures only under `--tier hamlet` |
| everything else | < 2 s | | keep |

## R4 - the `rolls_map` tests (31), what each really rolls

Read from the source before measuring (the measurement is R5):

| test | rolls | monkeypatched? | cacheable? |
|---|---|---|---|
| `gate/hamletgen/test_driver.py::test_a_rolled_cohort_passes_the_whole_gate` | seeds 41-44, serial | no | yes (per seed) |
| `...::test_the_fan_out_agrees_with_the_serial_path` | seed 41 twice (pool + serial) | no | pool child: no |
| `...::test_a_map_that_strands_a_farmhouse_is_re_rolled...` | seed 4, 10 hh, twice | fake gate | no |
| `...::test_a_re_roll_that_does_not_help_is_not_kept` | seed 4, 10 hh, three times | fake gate | no |
| `...::test_the_cli_reports_a_single_hamlet` | seed 8, 11 hh via the CLI | no | yes |
| `...::test_the_cli_batch_mode_returns_nonzero_when_a_member_fails` and 6 siblings | NOTHING - `cohort`/`generate` are stubbed; `_as_pinned`/`a_plan` only plan a site | stubbed | mis-marked: the AST guard sees `hg.main(...)`/`hg.cohort(...)` and demands the marker |
| `gate/hamletgen/test_water.py` (3 polders) | seeds 19, 12, 8 at 16 hh | no | yes |
| `gate/hamletgen/test_homesteads.py` (3) | seed 7 / 5 / 5 at 10 hh | yes (row passes silenced) | no |
| `gate/hamletgen/test_sink.py` (1) | seed 23, 12 hh | yes (setback forced) | no |
| `gate/settlement/test_rolling.py` (4) | `roll_village` seed 7 x3, 8; 7; 7; village 40 hh x2 | no | determinism tests must roll twice for real |
| `gate/pipeline/test_gencache.py` (8 toy) | a synthetic 3-line gen in tmp | - | already milliseconds |
| `...::test_the_real_pool_round_trips_through_the_cache` | Inashiro via subprocess + `run_and_record` | no | it IS a cache test |

## R5 - the `rolls_map` measurement

(filled in from `make durations MARK=rolls_map` - see below)

## R6 - defects found on the way (constitution XIV: fixed in this work)

1. **A stale deselect.** `DESELECT = --deselect tests/test_villages.py --deselect
   tests/hamletgen/test_driver.py` - the second path is where the cohort ratchet lived until
   feature 133 T29 moved it to `tests/gate/hamletgen/test_driver.py`. Since then the 4-seed cohort
   (the documented FULL-only "seeds 41-44 ratchet") has run in every UNLOCKED reference-scope
   gate, and the deselect silences seven quick-form tests in the old file for nothing.
2. **Seven mis-marked map-rollers** (R4): stubbed CLI tests carrying `rolls_map` because the
   marker guard matches the call, not whether the callee is real. They are deselected from quick
   and run only at the gate, where they cost milliseconds - the wrong tree by the GM's rule.
3. **An un-marked map-roller**: `test_a_map_is_immune_to_an_upstream_change...` rolls a hamlet
   three times through `runpy` and carries no marker; only the whole-file deselect keeps it out
   of the reference gate.
4. **Coverage carriers in the merge check** (R3): four sentinels and five frozen-pool carriers
   run at every `make done` although the reference scope enforces no floor; the largest is 10.6 s.
5. **`make test-file FILE=--collect-only ...` records a green `test-file` verification** (seen
   while measuring R2): a collection is not a test run. Minor; noted for the ledger.
