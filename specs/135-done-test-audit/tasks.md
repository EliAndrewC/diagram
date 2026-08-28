# Tasks: The `make done` Tests Are Audited and Accepted by the GM (feature 135)

The GM's own instruction: *"the final task of the new spec kit feature should be me taking
acceptance of the current state of the tests. And I plan on adding other tasks to the feature
as we go based on our initial findings and based on other improvements, which I would like to
make."* So this list is OPEN: tasks land as findings and the GM's improvements arrive; T99 is
tickable only on the GM's word, recorded verbatim.

Verification for every code task: `make quick` while iterating, the WHOLE affected test
directory before the gate, ONE locked `make done` per batch (~35 s); the measurement tasks are
the feature's own evidence.

## Phase 0 - the baseline (before any change; research.md R1-R5)

- [x] T01 the phases of `make done` and the non-rolling EXHAUSTIVE durations on unmodified code (R1, R3)
- [x] T02 the `rolls_map` durations by name under the lock, `make durations MARK=rolls_map` (R5)
- [x] T03 collection time, whole tree and quick tree (R2)

## Phase 1 - the defects the audit found (constitution XIV; research R6)

- [x] T10 the stale `DESELECT` path (`tests/hamletgen/test_driver.py` moved under 133 T29): the cohort ratchet runs in every unlocked reference gate; the seven quick-form tests in the old file are silenced. Fix by the tree rule (T20), never by a corrected path
- [x] T11 seven stubbed CLI tests carry `rolls_map` (they stub `cohort`/`generate`): re-home to `tests/hamletgen/test_driver.py` (quick); the marker guard learns that a test which `monkeypatch.setattr(hg.driver, "cohort"|"generate", ...)` before the call rolls nothing - proven by the guard going red on a real roller and staying green on the stubs
- [x] T12 `tests/test_villages.py`: the pool sweep and the immune-to-draws roller (214 s, un-marked, three rolls) move to `tests/full/`; the classification ratchet, the poolmaps kinds and the CPU-budget guard stay in the quick tree so the gate runs them again
- [x] T13 the four full-gate coverage sentinels and five frozen-pool carriers move to `tests/full/` (the merge check enforces no floor)
- [x] T14 `test_the_real_pool_round_trips_through_the_cache` (58 s, a real Inashiro regen) moves to `tests/full/`; the eight toy gencache tests stay at the gate

## Phase 2 - three trees (FR-006, FR-011, FR-012)

- [x] T20 `tests/full/` exists; the Makefile collects by TREE: quick = `tests/` minus `tier_*`, `gate`, `tooling`(when fresh), `full`; the gate = everything minus `full`; `test-full` = everything. `DESELECT` is deleted. `L7R_TESTS_FULL=1` marks the full run for the conftest
- [x] T21 `tests/tooling/test_switches.py` proves each tree's collection (SC-003: a file placed in each tree runs under exactly its targets, three placements)
- [x] T22 tooling tests skip at the gate when the tooling is unchanged since the last green gate (never under `L7R_TESTS_FULL`); `test_the_short_circuit_key...` (5 s) and its siblings then cost the gate nothing on a non-tooling change
- [x] T23 docs: `tests/CLAUDE.md` states "the directory decides when a test runs" with the admission rule per tree; `docs/iteration-loop.md` tree table; `dev/loop.md` and the skill `CLAUDE.md` command map numbers; constitution amendment (v2.12.0) quoting the GM: seed sweeps belong to the full form, the gate runs one representative roll, a rolled subject nothing changed is served from the cache

## Phase 3 - stop re-rolling what nothing changed (FR-004, FR-005)

- [x] T30 `l7r/diagram/pipeline/rollcache.py`: `record(fn)` (the `sys.monitoring` capture generalized from `gencache.run_and_record`), a key over the subject bytes + the same module/function/data hashes `gencache.compute_key` uses, atomic store/load of a pickled payload; bypass under `EXHAUSTIVE` and `GATE_NO_CACHE`; `_NOT_ENGINE` gains it. Red-green: a toy engine in tmp - first call MISSES and records deps, second HITS, editing an executed function MISSES, editing an un-executed one HITS, a vanished dep file MISSES. 100% coverage
- [x] T31 the cacheable gate rollers go through it: the three polders, the cohort's representative seed, the CLI single-hamlet roll; each test asserts on the served plan + manifest exactly as before
- [x] T32 the cohort ratchet: one seed (41) at the gate via `subset`, seeds 41-44 under `EXHAUSTIVE` (the documented FULL "seeds 41-44 ratchet"); the fan-out test (the only pool walk) moves to `tests/full/`
- [x] T33 `make reference` goes through the cache: a hit prints the served verdict and says HIT; `GATE_NO_CACHE=1 make reference` proves the cold roll produces the same verdict and manifest bytes
- [x] T34 `tests/gate/settlement/test_rolling.py`: the two determinism tests move to `tests/full/`; the pinned-knob and stream-fed rolls stay at the gate, cached
- [x] T35 the monkeypatched rollers (homesteads x3, sink, the two re-roll tests): kept at the gate through `rollcache.keyed_to` - the test's own source (where the patch lives) joins the key, so the roll is a function of the engine functions it executed + the test's code, both hashed (research R7)

## Phase 4 - the ledger and the after-measurement (FR-002, SC-001, SC-004, SC-005)

- [x] T40 research R7: one row per test the baseline ran (pytest list + the 13 guard suites + the reference step) - cost before, verdict, cost after, what changed
- [x] T41 the after-measurement, the same way as T01-T03; SC-001's phase sum; the locked `make done` no slower (SC-004); collection no larger (SC-005)
- [ ] T42 the unlocked end-to-end `make done` figure, recorded in the run-log when the GM releases the lock

- [x] T43 defects found while measuring, fixed here (constitution XIV): `state.write` vouched for the tooling on a FAILED gate (now green only, with a test); `make quick`'s `rolls_map` count read `__pycache__`; `make test-file` ran without `worksteal`; `gencache.split_sources` re-parsed ~180 files per key (memoized on content hash)

## Phase 5 - the second pass (GM 2026-08-28: "just literally redoing the same audit")

- [x] T50 re-measure the 24 s locked gate phase by phase, the test phase with and without coverage, the CPU mass by directory (research R10)
- [x] T51 the AST memo persists to disk: `make reference` 2.0 -> 0.55 s; each worker's first key 1.2 s -> 10 ms
- [x] T52 the corpus replay served from the roll cache (194 fixtures, 17.5 CPU-s -> a key each); FULL replays
- [x] T53 coverage follows the diff at reference scope (`ci cov-scope`, `COV_SCOPE` in the Makefile; directories, not module names - the double-import lesson is on `delta.coverage_scope`); FULL traces everything
- [x] T54 the cohort sweep keyed to FULL rather than EXHAUSTIVE (the gate is always EXHAUSTIVE; a first-pass slip that would have rolled four seeds at every unlocked gate)
- [x] T55 declined, measured: `COVERAGE_CORE=sysmon` (slower), caching the ~20 settlement fixture tests (~1 s of wall), the duplicate-defs scan (a 1 s merge guard)
- [x] T56 end to end after the second pass: locked `make done` 0m51.787s with nothing short-circuited (research R10)

## Phase 9 - acceptance

- [ ] T99 **the GM accepts the current state of the tests** - tickable only on the GM's explicit word, recorded here verbatim
