# Plan - 214 pack the roster

Tooling only (`research: rendering` throughout). Constitution check: no engine behavior changes; tests move
to shared rolls; every mechanism stays gated (XIII, XIV); the spec is reviewed against the GM's words (XVI);
100% coverage holds (X).

1. `driver.roll_pool(specs, jobs)`; `cohort()` delegates (FR-002).
2. `rollcache`: a module-level perturbed target for the immune test (FR-003); `gencache.run_gen_child` loses
   `perturb`; the CLI test's patched `generate` (FR-004).
3. The tests: the cohort gate test and the lane rules over the plain roster specs; the fan-out; the
   child-equality proof; the immune test; the CLI test; the two perf tests on stand-in stages.
4. `tests/rolls.py`: 12 rows, four duplicates of the reference, the perf modules `stub=True`;
   `tools/hamlet_floor.py` fixed subjects.
5. The record: `dev/loop.md` packing section, 213's research pointer, research R2; `make done`; land.
