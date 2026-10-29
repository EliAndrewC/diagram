# The language decision for the rebuilt phases (feature 444 FR-008, FR-017)

Load this file when: you rebuild a phase of the hamlet roll, or ask why the rebuilt phases are written in Rust.

**Rust.** The GM's decision, 2026-10-29 (feature 444 amendment 4, `specs/444-work-budget-program/request.md`): "Yeah, I want to
modify the plan so that we don't end up doing any Python rewrites. I think those are just going to slow us down."

The approved design (`specs/444-work-budget-program/request.md`, sections 5.7 and 6) had planned to decide by measurement after
phases 1 and 2: the basic operations per second of the rebuilt Python phases against a Rust spike of the same phase. That
measurement is not run (FR-017). What follows from the decision:

- Every phase from `field` on is rebuilt in Rust, in the shape of FR-010 - one extension module (PyO3, built by maturin), each stage
  a thin Python function calling into it; the driver, `STAGES`, the manifest, rendering, the pool's scripts, the tools and the
  tests stay Python.
- Before the first Rust phase lands, the tooling rows of `dev/rust-tooling.md` are built and proven on a Rust fixture (FR-011),
  and the counters stay behind the Cargo feature `counters` (FR-012).
- `water_frame`, accepted in Python (T15) with only its counting changed, stands; its port to Rust is a later phase's, held to the
  same budget.

The goals the GM set beside it, 2026-10-29: a scripted capital map with thousands of buildings generates in a single-digit number of
seconds (a hard bound); sub-second generation of larger maps in Rust (a goal, not yet measured for feasibility).
