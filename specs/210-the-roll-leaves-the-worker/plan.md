# Plan - 210 The roll leaves the worker

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **VI**: before/after per-worker census (FR-006); the child's result compared to an in-process roll.
- **X**: engine code in `clearance.py`, `driver.py`, `rollcache.py` and a small `_memory.py`; 100% coverage
  holds - the child's own coverage is published into the run's data files, as the pool sweep's is.
- **XIII**: the child returns the same plan and manifest; every `obtain` mode keeps its meaning.
- **XVI**: spec-fidelity before code.
- **Route**: engine code -> GATED (LOCAL-GATED).

## Design

- `hamletgen/clearance.py`: `reset()`.
- `l7r/diagram/_memory.py`: `trim_heap() -> bool` (ctypes `malloc_trim(0)`; False on any failure).
- `hamletgen/driver.py`: `roll_scope()` (a `contextmanager` whose `finally` calls `clearance.reset()` and
  `trim_heap()`); `build()`'s stage loop runs inside it, and so do the three tools' loops
  (`perf_snapshot.measure`, `perf_profile.profile_stage`, `placement_stages.build_page`) - the boundary
  every roll crosses (round 1 moved it from `generate()`, round 3 from `build()` alone). A static test in
  `tests/hamletgen/test_driver.py` walks `l7r/` for `for ... in STAGES` and demands each sits under a
  `with roll_scope()`.
- `pipeline/rollcache.py`: `_hamlet_in_child(spec) -> tuple[payload, deps]` (the driver script, the
  pickle in and out, the coverage branch, the failure); `hamlet()` passes `produce=lambda: child()[0]`
  and a new `recorded=` producer to `obtain`, which `_produce_and_store` uses instead of
  `gencache.record(produce)` when given; the shared-roll branches call `produce` as before.
- Tests: `tests/hamletgen/test_clearance.py` (reset), `tests/test_memory.py` (trim), `tests/pipeline/
  test_rollcache.py` (the child's equality with in-process, the failure, the coverage file), a memo
  assertion in the existing `generate` test.
- Measurement: the scratchpad census plugin on the full run and on `tests/gate/test_water_junctions.py`.
