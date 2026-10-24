# 415-gate-incremental-across-tooling - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-24 -->
## T01 - the run record says what ran, why, and where the time went (FR-002, FR-005)

### T01 Approach (checklist part A)

1. **The goal, in the world.** Anyone reading a gate's run record can tell whether it ran everything, why, how many tests it selected, and how long each phase took - without reconstructing it from a log.
2. **The constraints.** The record is written once per gate run by `LOGRUN`; it must not slow the gate or fail it when a figure is missing.
3. **Where each comes from.** O: the GM's items 2 and 5 (request.md).
4. **Do they describe the world here?** Yes, observed 2026-10-24 (method: T26's landing log): the run record held seconds and mode but no reason, no selection count and no phases, and the phase table had to be rebuilt by hand.
5. **The order.** Phase marks first (runstats), then the plan fields, then the record.
6. **The exits.** (a) read the log after each run - not taken, the record is what tools read; (b) the fields - taken.
7. **The search smell.** None.
8. **The budget.** 60 min with its landing.
9. **Done, measured.** Unit tests of `runstats.py phase`/`end` and of the record's new fields (red without); a real gate run's record carries `plan_mode`, `plan_reason`, `selected` and `phases`.
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** `runstats.py phase <dir> <name> <seconds>` appends a phase mark; `end` returns them as `phases: {name: seconds}`. The `done` recipe marks the preflight, each of static, format and typecheck, the reference step, the hooks suite and the test phase; the `test` recipe marks `pytest` and `floors` (merge, carry, the reports, save-baseline) inside it. Rendering: none.
- **D2** Every run of the gate's test phase writes this run's plan before pytest starts - the planner's, or, for a run that does not go through the planner (`make test-full` by hand, `INCREMENTAL=0`, `FULL=1`, T05's background refresh), its own with its reason - and the selection plugin writes its `result.json` (mode, reason, selected, collected) as today. `LOGRUN` reads only THIS run's result (stamped with the run's start, so an older file is never read) and adds `plan_mode`, `plan_reason`, `selected` and `collected`; the fields are left out only when no test phase ran (the gate stopped before it). Rendering: none.

<!-- plan-archive: archived 2026-10-24 -->
## T02 - a tooling change no longer runs everything (FR-001)

### T02 Approach (checklist part A)

1. **The goal, in the world.** A landing after a tooling change runs the tests its change reaches, plus the tests that read the changed tooling - not the whole suite.
2. **The constraints.** Never miss a test a change can break: the gate's machinery, the test run's configuration and the pinned lockfiles still plan `full`; the planner's other fallbacks are unchanged (spec FR-001).
3. **Where each comes from.** O: the GM's item 1; spec rounds 1-2 (the lockfiles ADDED; the word `scripts` read loosely; `gate-stamp.py` incremental).
4. **Do they describe the world here?** Yes, observed 2026-10-24 (method: the gate's planner asked offline on T26's baseline): T26's two engine files reached 143 of 11,890 baseline tests; the gate ran 10,376 because `scripts/` had moved the tooling hash.
5. **The order.** A planner hash of the gate's configuration beside the tooling hash; the `scripts/` readers; the plan; the tooling-test reuse on an incremental plan; tests.
6. **The exits.** (a) take `scripts/` out of `tooling_hash` - not taken: that hash decides when the tooling tests rerun, which stays; (b) a second hash for the planner - taken.
7. **The search smell.** None: one static scan of the test sources per plan.
8. **The budget.** 120 min with its landing.
9. **Done, measured.** SC-001's fixture cases (red without); `make test-file FILE=tests/tooling/ci/` green; T26's case re-asked of the planner plans incremental.
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D3** `state.gate_config_hash(root)`: a content hash over `l7r/diagram/ci/`, `l7r/diagram/pipeline/`, `l7r/diagram/switches.py`, `l7r/diagram/_invocation.py`, `tests/conftest.py`, `tests/_scope.py`, the pinned lockfiles (`requirements.txt`, `requirements-dev.txt`, `requirements-ci.txt`), `pyproject.toml`'s `[tool.pytest*]` and `[tool.coverage*]` tables, and the Makefile's TEST CONFIGURATION - the recipes of `test` and `test-full` and every variable definition they reference, closed over the variables those reference, with each `##` help comment stripped. `incremental.manifest` records it as `gate_config` and the `scripts/` tree's blob ids as `scripts`; `plan` plans `full` when `gate_config` moved (a baseline without the key counts as moved, once) and no longer on `tooling` alone. Every non-lockfile path it names is already in today's `state.TOOLING_PATHS` (`l7r/diagram/ci`, `l7r/diagram/pipeline`, `l7r/diagram/switches.py`, `l7r/diagram/_invocation.py`, `tests/conftest.py`, `tests/_scope.py`, observed 2026-10-24, method: `state.py:172` read), so it adds no reason to run everything beyond the lockfiles the spec marks ADDED. Rendering: none.
- **D4** Where `scripts` moved and `gate_config` did not, the plan adds to its changed test modules every test module under `tests/tooling/` and `tests/hooks/`, and every other test module whose source - or the source of a module under `tests/` it imports, transitively - contains the substring `scripts` (spec FR-001 read loosely; a substring, so `tests._scripts` and `"scripts"` both match - spec round 3's aside), and carries `reuse_tooling: true`; `_test_deps.gate_full` becomes `gate_reuses`, true on a full plan or one carrying `reuse_tooling`, so the tooling tests whose recorded reads are unchanged are deselected as on a full plan, and `incremental carry` copies their baseline coverage in before the floors on such a plan too (the merge drops a selected test's old contexts, so without the carry a reused test's coverage would be lost). Rendering: none.

<!-- plan-archive: archived 2026-10-24 -->
## T03 - the landing waits only on what can refuse it (FR-003, FR-004)

### T03 Approach (checklist part A)

1. **The goal, in the world.** A landing returns once its work is on main, having waited only on the checks that can refuse it.
2. **The constraints.** The fixed seeds and pinned rows still refuse a regressed seed beside the gate; the fresh block's record still reaches `make cohort-seeds`; an uncovered added line still refuses the landing.
3. **Where each comes from.** O: the GM's items 3 and 4.
4. **Do they describe the world here?** Yes, observed 2026-10-24 (method: T26's landing log): the cohort finished 1.4 min after the gate; `cover-changed` took 48 s before the gate started.
5. **The order.** The cohort split (fixed beside the gate, fresh after the push); `cover-changed` beside the gate with a stop; the cohort gate's record shape.
6. **The exits.** (a) drop the fresh block - not taken, its trend is read; (b) after the push - taken.
7. **The search smell.** None.
8. **The budget.** 90 min with its landing.
9. **Done, measured.** Unit tests: the fresh block started after a push and not before; a failing `cover-changed` stops the gate and refuses; `cohort_gate.check` takes a landing record with no fresh block. A landing's log shows both.
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D5** `make cohort-landing` rolls `N=48 FRESH=0` beside the gate; after a successful push, `land.py` starts `make cohort N=0 FRESH=48` detached (its own process group, its log under the git directory), one at a time (a lock file: a later landing's fresh block WAITS for the running one, never skipped), and the landing returns; its record is committed by the cohort as today and goes out with the next push. `cohort_gate.check` asks the landing record for the fixed seeds and pinned rows only (`landing_shaped(..., need_fresh=False)`). Rendering: none.
- **D6** `land.py` starts `cover_changed.py` beside `make done` (both in their own process groups); when it exits non-zero the gate's group is stopped (as `make land-stop` does) and the landing refused with its lines; `cheap_refusals` no longer runs it. Rendering: none.

