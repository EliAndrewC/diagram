# Research - 221 the gate's fixed costs

## R1 - the profile before (2026-09-09, this clone, warm caches, 22-CPU container)

**The gate, phase by phase** (each target timed on its own):

| phase | time | notes |
|---|---|---|
| static, format, typecheck | 1.4 + 0.1 + 0.6 s | autocorrecting |
| `_reference` | 9.4 s cold (the roll), ~2 s warm | |
| `hooks-test` | 26.7 s (guard scripts had changed); 0 s when stamped; 63 s for all 21 suites | |
| `test-full`, incremental with nothing reachable | 21.4 s | 2.9 s planning, ~10 s pytest, ~8 s bookkeeping |
| `test-full`, full, under the gate (the 220 landing run) | pytest 47 s, 3,496 tests, 6 workers | whole-engine coverage with per-test contexts |
| after pytest: combine, merge, three `coverage report` tables, the hamlet floor, the roll census, the baseline save | ~8 s | the tables ~2.5 s each |

A warm full gate lands at 60-70 s; cold rolls add 10-20 s; a guard change adds 27-63 s.

**The suite three ways:**

| run | tests | wall |
|---|---|---|
| everything but rolling tests, no coverage (`make durations FULL=1`) | 2,777 | 19.4 s |
| the same, scoped coverage, no contexts (`make test INCREMENTAL=0`) | 2,777 | 14.7 s |
| the rolling tests alone, no coverage (`MARK=rolls_map`) | 26 | 15.9 s |
| the full gate run: every tree, whole-engine coverage, contexts | 3,496 | 47 s |

Slowest tests (no coverage): `test_every_glossary_term_is_used_by_a_modal_or_a_record_page` 5.3 s,
`test_a_linear_hamlet_strings_its_houses_along_the_connector` 3.3 s, the browser test 2.9 + 1.2 s setup,
the driver's AST scan 1.7 s; nothing else over 1.5 s. The rolling tail: `test_roll_village_is_deterministic...`
6.7 s and `test_pinned_knob_is_byte_identical...` 5.2 s (both `tests/full/settlement/test_rolling.py`,
village-tier rolls), then 3.2 s and 3.1 s.

**`make roll-audit` on the landed baseline:** `test_pinned_knob...` 15 unique lines (`settlement/rolling/roll.py`);
`test_roll_village_is_deterministic...` **1** unique line (`settlement/_geom/water_index.py`) for two
6.7 s rolls; `test_roll_village_honors_a_pinned_knob` (gate tree) 0 unique; the cohort test 95; the pool
sweep's Mizuguchi 13, Sawada 13, Kashikawa 5.

**The worker cap's origin** (`Makefile`, `XDIST_WORKERS`): feature 213 measured the full test phase at
4 / 6 / 8 workers as 346 / 301 / 297-322 s and took "the smallest count within 10% of the fastest", with
~250 MiB back to other sessions as the tie-break - on the gate of 2026-09-07, which rolled 37 hamlets at
~24 s each. Today's gate rolls three at ~7 s.

## R2 - the worker count (2026-09-09)

`make test-full INCREMENTAL=0 XDIST_WORKERS=<n>` on identical content, the box checked quiet (no other
gate; the container at a 3.1 GiB base with the sessions' own memory in it), pytest's own wall time; each
worker's per-test peak RSS from a plugin sampling `/proc/self/statm` every 20 ms (feature 208's method,
rewritten: its plugin was never committed); the container's `memory.current` sampled every 0.5 s.

| workers | pytest wall (runs) | mean | worker peak RSS | gate footprint above the base | two gates |
|---|---|---|---|---|---|
| 6 (the cap) | 49.1, 48.6, 45.3, 45.6 s | 47.2 s | 189 MB | 0.95 GiB | 5.0 GiB |
| 8 | 47.0, 45.8, 42.8 s | 45.2 s | 168 MB | 1.14 GiB | 5.4 GiB |
| 10 | 43.3, 38.8, 38.9 s | **40.3 s** | 191 MB | 1.39 GiB | **5.9 GiB** |
| 12 | 44.8 s | 44.8 s | 166 MB | 1.52 GiB | 6.1 GiB |

Feature 213's rule - the smallest count within 10% of the fastest - picks **10**: 8 is 12% off it. The
GM's condition holds: two gates at 10 workers are 5.9 GiB against the 8 GiB bar (the container's cap is
10 GiB). So the cap is raised to `min(10, nproc)`; the reasoning is at the point of change (the
`XDIST_WORKERS` comment). Against the GM's yardstick (47 s near 30 s): **40 s**, a shortfall reported as
such - past ten workers the suite's tail (the 5 s glossary scan, the 3 s seating, the browser test) and
each worker's spawn-and-collect bound the phase, not the cores.

**A first attempt was voided:** the sampling plugin used the builtin `open` at teardown, and the tests that
stub `open` to fail (`tests/test_invocation.py`) errored 175-677 tests per run; the plugin now binds
`open` at import. **An anomaly, recorded and not used:** the gate's suite with coverage OFF
(`COV_SCOPE=--no-cov`) ran in 70 s against 49 s traced, on one run; whatever that measured, it was not
the tracer's overhead, and no conclusion is drawn from it.

## R3 - the coverage contexts

The full tree with `--cov-context=test` and without, 6 workers, two runs each: **48.6 / 45.3 s with,
44.3 / 45.6 s without** - about 2 s, under the GM's 10 s. Nothing changes (spec FR-002's second branch);
the incremental gate keeps recording per-test contexts on every run. For the record, the merge in
`ci/incremental.py` drops the selected tests' and affected fixtures' contexts from the baseline copy and
adds the fresh run's data; on an incremental run the baseline itself is not replaced, so the fresh
contexts feed only the merged total - a future feature could drop them on incremental runs if their cost
ever grew, but at 2 s the question the GM posed does not need answering.

## R4 - one coverage table

`--cov-report=term` left `pyproject.toml`'s addopts (the Makefile's note that `--cov-report=` "does not"
silence it is corrected: pytest-cov keeps a `term` given in addopts whatever the command line says, so
it is removed rather than overridden), and `hamlet_floor.check` asks `cov.report` for its per-module
table only when a module is under 100% - the verdict came from `analysis2` all along. A passing gated
run prints one table, the merged `coverage report -m --fail-under=100`. Measured on the R1 profile, the
two tables cost ~2.5 s each; R6 has the gate after.

## R5 - the two village rolls

`make roll-audit` (R1): `test_pinned_knob_is_byte_identical_across_regens_and_rejects_incompatible_pins`
reaches 15 lines of `settlement/rolling/roll.py` nothing else reaches and stays;
`test_roll_village_is_deterministic_and_seed_varies_the_combination` reached one -
`settlement/_geom/water_index.py:49`, `WaterIndex.clear`'s grid-path refusal (found by reading the
baseline's contexts for that file: 15 contexts touch the module, one line has a single one). That line is
`tests/settlement/test_geom.py::test_water_index_refuses_a_narrow_fixture_from_its_grid_cell`, and the
determinism test is `tests/soak/test_village_determinism.py` with its reason, taking its 6.7 s roll pair -
the two longest tests in the gate - out of every ordinary run.
