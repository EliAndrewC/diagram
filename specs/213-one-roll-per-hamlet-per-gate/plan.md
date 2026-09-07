# Plan - 213 One roll per hamlet per gate

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **VI**: before/after on the census, the gate's time and peak (FR-012); every refusal shown once.
- **X**: engine code in `pipeline/rollcache.py`, `hamletgen/driver.py` (`Report`), `pipeline/gencache.py`
  (the regen child), a new `ci/rollcensus.py`; 100% coverage; files under 1,000 lines (rollcache is at
  ~330 and grows - split into a package if it passes 700).
- **XIII**: the maps are unchanged (a roll is the same roll wherever it runs); the child equality is
  asserted per lifted closure.
- **XVI**: spec-fidelity before code.
- **Route**: engine code -> GATED (LOCAL-GATED). Merge main before the Makefile edits (207 shares the
  `test` recipe).

## Design, in task order

1. `ci/rollcensus.py`: the plugin (records to `$L7R_ROLL_CENSUS`), the aggregation and verdict
   (`python3 -m l7r.diagram.ci rollcensus verdict`), the roster reader. `tests/rolls.py`: the roster.
   Makefile: `-p l7r.diagram.ci.rollcensus` on the gate's pytest line, the verdict after it.
2. `rollcache`: the unified roll (plan, manifest, report) in one child; `hamlet()`/`report()` read it;
   the per-subject lock; the slot semaphore; `Report.manifest`.
3. The lifted closures and their child mode (`keyed_to(..., child=name)`); the immune and CLI tests.
4. `tests/conftest.py`: the render default; the tests of rendering opt out.
5. The regen child in `gencache.run_and_record`.
6. Collection order in the plugin; the seed moves.
7. Measurements: the pool-sweep child profile; 4/6/8 workers; the roll cap count.
8. The record; the gate; land.
