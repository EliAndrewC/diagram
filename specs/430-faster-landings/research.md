# Research: Faster landings

## R1 - Did today's `cover-changed` miss the coverage reds? (FR-003a)

- **Finding** (`m:coverage-reds-replay`): of today's 6 coverage reds, the 5 that name lines name 8 spans (20 lines), and every one is EXISTING
  lines that lost their coverage - a test or caller deleted with its pass, or code moved behind a new branch - none added. The
  sixth was the gate not counting new tests marked `tooling`, which `cover-changed`'s run counted.
- **Which modules** (same key, re-run by `bash specs/430-faster-landings/replay-reds.sh`): THREE of the five name lines in a module
  their delta changed (31f739f5d, d92ff2c90, 39ea51383); TWO name a module their delta did not touch - 7f209090b `law.py:933`
  (its delta changed the modules that called it) and 449e7df7b `checks.py:141` (its delta deleted the field spur that reached it).
- **So**: `cover-changed` asks only the lines a change ADDS, by design (its docstring), so it could see none of the five; and it
  runs a different selection from the floor's. FR-003's check asks EVERY line of each changed module (the GM's "on the changed
  modules") with the tests the gate's floor counts for it: it catches three of the five line-naming reds and the sixth. The two
  whose lost line sits in an unchanged module stay the gate's to catch - the narrowing FR-009 asks stated, at a price of 2 of
  today's 6 reds (one gate each, 4-5 minutes - observed 2026-10-26, method: `dev/run-log`, the GM's figure in `request.md` item 3).

## R2 - What holds a claims triage back until the plan review returns? (FR-007)

- **Finding** (read 2026-10-26, method: the guards' agent lists and the guard log): nothing does. The decide-first test runs for
  the agents in `scripts/hooks/check-bundle-hooks.sh` `CHECKS` and `scripts/hooks/pair-hooks.sh` `REVIEW_AGENTS`; `claims-triage`
  is in neither (`impl-drift` is in `CHECKS`). `make guard-log` holds no decide-first refusal of a `claims-triage` dispatch, only
  three `step-back-due` refusals (2026-10-19 twice, 2026-10-21).
- **So**: the triage ran after the plan review because the session's own order put it there - the claims round was begun at the
  landing. FR-007 is met by the guards as they stand; what is missing is the prompt to start it: `make decide` and `make
  plan-delta` name the owed triage, so it is dispatched beside the review (D7), and a guard test pins that decide-first lets it
  through while impl-drift still waits.

## R3 - The non-module files of today's test-tree full runs (FR-002)

- **Finding** (`m:full-plan-reasons`): 4 the top-level `tests/conftest.py`, 2 `tests/hooks/test-cohort-gate.sh` (a guard suite
  `make hooks-test` runs, no pytest test), 1 `tests/hamletgen/ways/CLAUDE.md`, 1 `tests/tooling/ci/conftest.py`.
- **And** the fixture data under `tests/` is read across directories (observed 2026-10-26, method: `find tests/fixtures -type f`
  and a grep of `tests/**/test_*.py` for `fixtures/`): `tests/fixtures/` (56 files) holds no test module of its own, so "the tests of that directory" alone would select nothing for a change there.
- **So**: a data file selects its own directory's tests AND every test module that names it (its file name or its directory
  under `tests/`), a superset of FR-002's directory - the narrowing FR-009 forbids otherwise (D2).

## R4 - T01's replay: what did the 11 manifest-only full runs fail? (FR-001, FR-009)

- **Finding** (observed 2026-10-26, method: the 11 `dev/run-log/2026-10/20261026*.json` records of target `done` whose plan
  reason named `inashiro.json`, their `result`): 8 green; 3 red, each on the coverage floor alone (31f739f5d, 7f209090b,
  449e7df7b - the lines R1 lists), none on a failing test.
- **So**: no test that a full run failed lies outside the new selection - there was none. The three coverage reds are judged
  by the incremental merge's floor as any code change's are: the tests that reached the lost lines touched the changed modules
  at the baseline, so they re-run and their old contexts are dropped (`incremental.py`'s argument, "THE MERGE" (b)). The gate's
  readers for a manifest number 42 modules today (observed 2026-10-26, method: `pool_readers.readers` on this clone).

## R5 - SC-001's replay (T01, T02)

- **Finding** (`m:plan-replay`): of the 19 runs, the current planner plans 12 incremental (the 11 `inashiro.json` runs and the
  `CLAUDE.md` one), 4 full for the top-level `tests/conftest.py`, and 3 full for the gate's configuration - SC-001 to the run.
- **A trap in the replay itself**: the run records do not name the clone, and each clone keeps its own baseline, so taking "the
  last green full run" as the base replayed two of the conftest runs as incremental against another clone's baseline. The base
  is now the latest earlier green full run at which the file the run's own reason names differs.

## R7 - T04: the push gates on a records-only delta (SC-003, FR-009)

- **Finding** (`m:push-gates-records-only`): each of the three gates exits in 0.14 s or less, saying it has nothing to judge,
  where they took 5.7 s, 2.3 s and 8.8 s (observed 2026-10-26, method: each gate timed alone, `request.md`).
- **FR-009's replay**: a delta that holds nothing a gate judges is one that gate could not refuse on its own content: its verdict
  is the merge base's, which every push since has passed. A tree with no `origin/main` to read a delta from skips nothing (the
  guard suites' fixtures caught the first form, which fell back to HEAD and read every delta as empty: 3 cohort-gate and 1
  claims-gate cases). A stored pass is served only for the same committed content, the same merge base and the same `scripts/`
  tree; an escaped pass (`ENTRY_DRIFT_OK`) is never stored.

## R6 - T03's replay: the new coverage check on the in-scope reds (SC-002, FR-009)

- **Finding** (`m:cover-replay`): the check refuses all 3 reds whose lines lie in a changed module, each against a gate
  baseline of its own base, in 17 s to 37 s where their gates took 255 s to 442 s. It names 14 of the floor's 18 lines: all of
  31f739f5d's and d92ff2c90's, and 2 of 39ea51383's 6 (`gencache.py` 227-228; not 238-241).
- **Beyond the floor**: 3 lines of `web/stage.py` on d92ff2c90 the floor did not name - lines a roll reaches whose roll test
  changed with the delta, so the floor's carried coverage is not honored for them. A landing meeting one passes with `COVER_OK`.
- **Short of the floor, priced** (FR-009): `gencache.py` 238-241 are reached only by tooling tests the gate REUSES instead of
  re-running (feature 383 amendment 5), whose coverage of a changed file the floor drops; the check runs those tests, so it counts
  the lines. The landing is refused either way - one named line stops it - so what this costs is the first message naming 2 of
  the 6 lines; the gate names the rest, as now.
- **Three traps in building the replay**, each fixed in the check or the script and named at its point of change: a baseline
  taken from another day's tree (its coverage paths name another tree, its contexts tests the red had deleted); `--cov-context=test`
  without the gate's own plugins (an xdist worker crashed, "no such table: context"); and `COVERAGE_FILE` in the environment (the
  tooling tests that run coverage in a fixture clone inherited it - 15 errors).
- **The sixth red** (9a157cc4b) is the floor's tooling rule, `floor_markers`, pinned by a unit test; its replay would need the
  gate stamp its tooling decision read, which no record keeps.
