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

## R5 - the `rolls_map` measurement (per file, alone, 8 workers; 2026-08-27)

The whole-set profile (`make durations MARK=rolls_map`) was killed at 1,000 s twice - a second session's
identical profile was running on the same box, and two eight-worker sweeps of 100 s rolls contend past
the cap. Per FILE, alone, every test finishes; no test hangs (each of the six driver tests was also run
in isolation: 3, 37, 60, 58, 35 s and the cohort's cache hit).

| test | s | rolls |
|---|---|---|
| `test_water.py::..inlets_mouth..` (seed 19) | 102.7 | one 16-household polder |
| `test_water.py::..grid_dike_and_reservoir` (seed 8) | 97.2 | one polder |
| `test_water.py::..reservoir_backs_off..` (seed 12) | 48.8 | one polder |
| `test_driver.py::test_a_re_roll_that_does_not_help_is_not_kept` | 59.6 | three 10-household rolls |
| `test_driver.py::test_the_fan_out_agrees_with_the_serial_path` | 57.6 | seed 41 twice (one in a pool) |
| `test_driver.py::test_a_map_that_strands_a_farmhouse..` | 37.2 | two 10-household rolls |
| `test_driver.py::test_the_cli_reports_a_single_hamlet` | 34.9 | one 11-household roll via the CLI |
| `test_homesteads.py::..lane_frontage..` | 31.4 | one 10-household roll (patched) |
| `test_homesteads.py::..cluster_seeds_cloud..` | 27.0 | one (patched) |
| `test_sink.py::..OFF_MAP` | 17.8 | one 12-household roll (patched) |
| `test_homesteads.py::..linear_frontage_pass_stops..` | 15.6 | one (patched) |
| `test_rolling.py::..deterministic..` | 15.6 | `roll_village` x3 |
| `test_rolling.py::..byte_identical..` | 10.0 | a 40-household village x2 |
| `test_rolling.py::..stream_fed..` | 8.1 | one |
| `test_rolling.py::..honors_a_pinned_knob` | 3.8 | one |
| `test_driver.py::test_a_rolled_cohort_passes_the_whole_gate` | (not measured alone at baseline; seeds 41-44 serial: 11, 18, 14, 10 households) | four |
| `test_gencache.py` (7 toy tests) | 0.2-0.8 | a 3-line gen |
| the seven stubbed CLI tests | ms | none |
| `test_the_real_pool_round_trips_through_the_cache` | 58 (marker comment) | Inashiro via subprocess |

## R7 - THE LEDGER: every test the baseline gate ran, its verdict

Phases first, then the pytest set. "after" is measured on the finished work (R8).

| what | before | verdict | after | what changed |
|---|---|---|---|---|
| `make reference` (Inashiro seed 4) | 26-37 s, every run | **cheapen** - through the roll cache | 1.7 s HIT; 37 s on a MISS | `rollcache.report`; `GATE_NO_CACHE=1` rolls |
| lint / format / typecheck | seconds | keep | seconds | - |
| `hooks-test` (13 guard suites) | 84 s, skipped while the stamp is fresh | keep - already stamp-skipped | same | - |
| pool sweep `test_village_passes_gate[4]` (FULL-only via a file deselect) | 24-77 s each | **move to full** | `tests/full/test_villages.py` | the deselect list is gone |
| `test_a_map_is_immune_to_an_upstream_change..` (FULL-only, un-marked) | 214 s | move to full; marked | `tests/full/` | - |
| `test_every_pool_gen_is_classified`, `test_poolmaps_classifies_each_kind`, `test_slow_gen_budget_fires..`, `test_at_least_one_village_exists`, `test_every_scripted_comb_fan_records_its_design_cell` | silenced by the file deselect | **re-home** to quick (defect R6.1) | ms - 3 s, run again | - |
| the cohort ratchet (seeds 41-44, serial) | ~3-4 min, ran in every UNLOCKED gate (defect R6.1) | **cheapen** - one seed (41) at the gate through the cache, four under EXHAUSTIVE / FULL | 1.3-2 s HIT | `subset`, `rollcache.report`, `driver.cohort_specs` |
| fan-out agrees with serial | 57.6 s | move to full (the pool child cannot be cached; the pool path is walked by every regen) | `tests/full/hamletgen/` | - |
| CLI single hamlet | 34.9 s | move to full (the CLI's writing is exercised by every `make map`) | `tests/full/hamletgen/` | - |
| seven stubbed CLI tests (`rolls_map`, gate tree) | ms, deselected from quick | **re-home** to quick (defect R6.2) | ms in quick | the marker guard reads the stub |
| strand-retry (2 rolls) / re-roll-not-kept (3 rolls) | 37 / 60 s | cheapen - `rollcache.keyed_to` (the test's source joins the key) | 1.4 s HIT; 40 / 68 s MISS | plain-data `produce` |
| three polders | 103 / 97 / 49 s | cheapen - `rollcache.hamlet` | 1.3-2.4 s HIT | - |
| homesteads x3, sink (patched) | 31 / 27 / 16 / 18 s | cheapen - `keyed_to` | 1.4-2.1 s HIT | - |
| `roll_village` determinism x2 | 15.6 / 10.0 s | move to full (must roll twice for real) | `tests/full/settlement/` | - |
| `roll_village` stream-fed / pinned-knob | 8.1 / 3.8 s | cheapen - `rollcache.obtain` | 0.02-1.7 s HIT | - |
| 7 toy gencache tests | 0.2-0.8 s | keep | same | - |
| real-pool cache round trip | 58 s | move to full | `tests/full/pipeline/` | - |
| 4 full-gate coverage sentinels + 5 frozen carriers (`coverage_only`) | 10.6, 3.1, 2.6, 2.3 s ... | move to full (no floor at the gate; defect R6.4) | `tests/full/test_coverage_carriers.py` | - |
| the bad-map corpus (targeted replay) | 0.2-1.6 s per fixture, hamlet+village under `--tier hamlet` | keep - the merge check's core | same | - |
| tooling tests (`tests/tooling/`, ~168) | ran at every gate (5.1 s the largest) | cheapen - skipped at the gate while the tooling hash is unchanged since a GREEN gate; never in FULL | 0 when unchanged | `tests/conftest.py`; `state.py` vouches only on green (defect found here) |
| `test_hinterland..each_cardinal` (3.4 s), `test_build_comb_supply_banks` (2.1 s), `test_propose_rejects_a_seat` (4.2 s), the rest under 2 s | | keep - exhaustive forms, parallel, under 5 s | same | - |
| every other collected test (~2,300) | < 0.5 s | keep | same | - |

Every key computation parses the ~180 engine files (1.2 s); memoized on content hash in
`gencache.split_sources` (2.4 s -> ~1.4 s per served roll, and every pool-sweep key benefits).

## R8 - after (2026-08-28, same box, same 8 workers)

| figure | baseline | after |
|---|---|---|
| locked `make done`, end to end | 33-39 s (run-log, twenty runs) | **24 s** (`hooks-test` stamp-skipped both times; test phase 16 s, 2,382 tests) |
| `make reference` | 26-37 s | 1.7 s (HIT) |
| the map-rolling gate set (`make durations MARK=rolls_map`) | 233 s (T11's measurement; killed at 1,000 s here) | **5.4 s warm** (13 tests); 72 s cold after an engine change reaching every hamlet roll |
| gate tree whole (`tests/gate`, corpus skipped) | - | 7 s warm / 61-72 s cold |
| unlocked gate, phase sum (SC-001) | ~270 s (4.5 min) | ~35 s warm (24 + ~10); ~130 s cold after a hamletgen-wide change (24 + 37 + 72) |
| collection, gate scope | 3,755 tests in 1.28 s | 3,736 tests (the full tree is 19) - unchanged floor |
| quick tree | 2,010 tests, ~20 s wall | 2,177 tests (+7 CLI tests, +5 pool ratchets, +6 rollcache), 10.3 s pytest |

SC-001 holds warm (13% of baseline) and after a change that re-rolls everything (48%): the second
figure is the honest cost of "re-roll only when the code the roll executes changed", and it is the
figure the GM should judge - a hamletgen-wide edit is exactly when the rolls have something to say.
SC-004 holds (24 s vs 33-39 s). SC-005 holds (collection unchanged).

## R9 - what the whole-set profile taught (the "hang")

Feature 133's lock note says the unlocked gate "hangs in one 24-seed cohort roll". Two whole-set
`rolls_map` profiles here ran past 1,000 s while a sibling session's profile shared the box; per file,
alone, every test finished and the slowest was 103 s. Under xdist's default `load` scheduler two 50-100 s
rollers land on one worker; `make test-file` now passes `--dist worksteal` like `test` does. Whether
the lock note's hang is contention or a real deadlock is for the session isolating it; the roll cache
removes both the contention and the repeated rolls from the merge check.

## R10 - THE SECOND PASS (GM 2026-08-28: *"just literally redoing the same audit in order to see whether there are still more performance benefits"*)

Where the 24 s locked gate went, measured before touching anything: `make reference` 2.0 s (HIT - but 1.2 s of
it re-parsing ~180 engine files for the key, in a fresh interpreter every time), lint 1.24 s (1.04 s the
whole-repo duplicate-defs scan), format 0.07, typecheck 0.4 (dmypy), test phase 22.6 s wall: 18 s pytest of
which ~6 s was COVERAGE TRACING (10.5 s with coverage narrowed to one module) plus ~3 s of combine/report,
on 62 CPU-s of tests - settlement 22.4 s (90 tests), the corpus replay 17.5 s (194 fixtures), tooling 12.8 s
(176 tests, skipped in steady state), everything else under 4 s - and a ~5 s xdist floor.

| change | before | after | principle |
|---|---|---|---|
| the AST memo persists to disk (`.gencache/ast/<content-sha>.json`) | `make reference` 2.0 s; each xdist worker's first key 1.2 s CPU | **0.55 s**; ~10 ms | recomputing what could be cached |
| the corpus replay served from the roll cache (`_served_replay`: fixture bytes + `fires` -> the verdict set, deps = the check functions executed) | 17.5 CPU-s, 8.7 s wall alone | 3.4 s wall (the assertion still runs on the served set; FULL replays) | the first pass's principle applied where it was not |
| coverage follows the diff (`ci cov-scope`: the packages changed since the merge base or in the worktree; `--no-cov` when none; FULL traces all) | 6 s tracing + 3 s report at every gate | 0 with no engine change; a few packages otherwise | the reference scope enforces no floor - its coverage feeds `uncovered-in-diff.py`, which reads only the diff |
| the cohort ratchet's sweep keyed to FULL, not EXHAUSTIVE | 4 seeds at every unlocked gate (the gate is always EXHAUSTIVE - a first-pass slip) | 1 seed; 4 in FULL | a seed sweep is a different test |
| `COVERAGE_CORE=sysmon` | 18.0 s | 19.6 s - DECLINED, slower here | measured, not assumed |
| caching the hinterland / draw_comb_field settlement tests (~10 CPU-s over 20 tests) | | DECLINED - ~1.2 s of wall across 8 workers for a cache keyed to each test's source; below the noise of the xdist floor | cost/benefit |
| the duplicate-defs scan (1.0 s) | | kept - a merge guard, one second | |

Coverage-source names were tried first and hit *"cannot load module more than once per process"* (97 errors):
coverage resolves a module-name source by importing it, and under the `l7r` namespace-portion layout that
loaded the engine a second time. Package DIRECTORIES are matched by path and import nothing.

**End to end, locked, after the second pass (the verification record deleted so nothing short-circuits):
`make done` 0m17.333s (2553 passed in 12.50s, coverage over the three packages this diff touched, the 176 tooling tests RUN because the
measurement deleted the record that lets them skip - steady state is ~1.5 s lower still).** The run before it took 51.8 s because the reference roll MISSED: a new
module-level constant in `ci/delta.py` moved every roll's key, by design (the pool cache hashes every
engine module's top level, conservatively) - the honest cost of any module-level edit anywhere in the engine. Steady state - a one-module engine edit, tooling unchanged - is lower
still: the test phase alone measured 11.9 s wall with coverage narrowed to one module.

## R11 - THE THIRD PASS (GM 2026-08-28: *"redo the whole thing for a third time"*)

Where the 17 s locked gate went: reference 0.56, lint 1.16 (1.0 the duplicate-defs scan), format 0.06,
typecheck 0.26, hooks-test 0.1 when stamped (but **90 s whenever ANY guard script changed** - all 15 suites
re-ran for a one-line edit), test phase 12 s wall = 9.8 s pytest on 36 CPU-s over 8 workers (settlement
16.9 s, the corpus 6.6 s served, check_village 4.1 s; a 1.9 s xdist floor; engine import 0.63 s per worker)
plus 0.15 s combine and 0.59 s `uncovered-in-diff` even with nothing traced. The make/Python glue is 50 ms
per call - not the problem it looked like. `-n 12` vs 8: 9.5 vs 9.9 s - not worth the shared box.

| change | before | after | principle |
|---|---|---|---|
| per-suite `hooks-test` freshness (`.git/hooks-test/<guard>` = sha of guard + test + shared helpers; the three suites that drive other scripts key on all of scripts/; `HOOKS_ALL=1` runs everything) | 90 s for any scripts edit | 0.4 s unchanged; ~16 s for one guard (its suite + the three all-scripts suites) | recompute only what changed |
| `test_slow_gen_budget_fires..` on a stubbed `gate_obtain` | 2.6 s (two real `coverage run` subprocesses on a 50 ms gen) | ms | the assert reads one number; the number's measurement is `gate_obtain`'s own test |
| the registry round trip on ten rows | 2.2 s | ~0.3 s (one full derivation kept for the disagreement guard; the full rebuild proof stays exhaustive) | size, not repetition |
| no `coverage combine` / `uncovered-in-diff` when nothing was traced | 0.75 s | 0 | |
| `tests/tier_town` / `tests/tier_city` not collected under the lock (the `--tier` deselect happened after collection) | ~700 items collected per worker | not collected | decide before collecting |
| the cohort pin judged only for seeds this scope rolled | (merge of 133 T92's pin: "STALE PIN seed 42..44" on a one-seed gate) | clean; FULL judges all four | |
| DECLINED: `-n 12` (0.4 s, shared box); the duplicate-defs scan (1 s, a merge guard); a persistent runner (the GM declined it 2026-08-26) | | | |

**Main's unlock arrived mid-pass (feature 136 / 133 T92 merged in): the gate is UNLOCKED now, so these are the
real merge check's numbers, every map-rolling test included (T42):**

| | baseline (2026-08-27) | after three passes |
|---|---|---|
| unlocked `make done`, warm, end to end | ~270 s (4.5 min; 233 s of rolls) | **21.7 s** (3,750 tests, 16.2 s pytest) - 8% |
| unlocked `make done` after a main merge that changed the engine (every cached roll re-rolled, 5 hook suites changed) | ~270 s | 5 m 42 s - the honest cold cost: every roll keyed on its executed functions re-rolls at once, 4-wide on 8 workers, plus hooks |
| locked `make done` | 33-39 s | 17 s |

The cold figure is worth a sentence: a merge from main that touches hamletgen re-keys every gate roll
(and the reference) in the same run; the rolls are bounded by the polders (~100 s each) and the serial
re-roll ladders, and they all land in one gate. The first pass's ledger says the same. If the GM wants
that cheaper, the lever is the rolls themselves (`GEN_TIME_BUDGETS` says the polder's cost is inherent),
not the tests - or the idle-tests hook (feature 136) warming the cache after a sync.
