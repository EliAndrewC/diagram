# Plan - 221 the gate's fixed costs

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **I / II / III / IV / V / VII / IX / XI / XII**: N/A - no UI, no content, no SOURCE blocks, no map
  changes, every task `research: rendering`.
- **VI**: PASS. Every change is measured on identical content, three runs where the number decides (the
  contexts, the workers); no bookends (spec D1, no generator touched); `make done` green; the gate's
  time after beside before (R6).
- **X**: PASS. `tests/tooling/` companions for the Makefile change; 100% over `ci/` if it changes; the
  lifted water-index line tested with plain data.
- **XIII / XIV / XV / XVI**: PASS. Spec reviewed first; a measurement that does not support a change
  leaves the code alone and records the number.

## Design

- **Workers (FR-001).** A scratch script runs `make test-full INCREMENTAL=0` at `CPU_COUNT`-overridden
  worker counts (the Makefile derives `XDIST_WORKERS` from `CPU_COUNT`; for counts above 6 the cap line
  is what changes, so the measurement passes the count through a variable the cap reads) with feature
  208's `memprof` plugin (`PYTEST_ADDOPTS="-p memprof"`, `PYTHONPATH` to the scratch dir) and a cgroup
  sampler; the box checked quiet first. The cap line and its comment change to the measured result.
- **Contexts (FR-002).** `INCR_ARGS` carries `--cov-context=test` on floored runs; the measurement toggles
  it through a make variable for the run only. `incremental.py`'s merge is read for which contexts of
  the NEW run it consumes; the arrangement follows.
- **One table (FR-003).** `addopts` loses `--cov-report=term`; `cov-file` keeps `term-missing`; the
  Makefile comment corrected; `tests/tooling/test_coverage_floor.py` (or a sibling) asserts the addopts
  shape and that the gate's verdict table is the merged report.
- **The rolls (FR-004).** `tests/full/settlement/test_rolling.py::test_roll_village_is_deterministic...`
  moves to `tests/soak/` (with `tests/soak/CLAUDE.md`'s row and `tests/rolls.py`'s audit pointer if the
  roster lists it); the `water_index.py` line gets a unit test in `tests/settlement/test_geom.py`.
- **Verification.** `make roll-audit` after; `make done` (detached); R6.
