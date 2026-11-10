# Phase 2 of feature 449, closed: the gate's own tools are Rust

Load this file when: you want what phase 2 of the Rust port measured at its close, and what Python it deliberately left for later.

**The port.** `rust/gate`, the binary `l7r-gate`, holds the stamps, the delta, the cohort, the checks, the plan gates, the push, the preflight and `scripts/measure/`'s tools. The Python unit tests, their planner, the coverage floor over Python and the Python-only static checks were deleted, not ported (FR-001b, the GM 2026-11-10); the old tests stand at the tag `python-tests-before-removal`. The AWS remote test path was deleted (FR-001a).

**SC-002, measured** (`m:done-rust-edit`, `m:done-rust-edit-phase2`, `m:done-unchanged-phase2`, observed 2026-11-10, one run each, one-shots).

| case | first value | now | SC-002 |
|---|---|---|---|
| a one-line Rust edit's `make done`, wall | 30.2 s | 22.0 s | NOT MET: under 15.1 s is owed |
| an unchanged tree's `make done` | ran the tests | 6.5 s, then no test once the preflight stands aside (T070) | met |

The Rust edit's 22.0 s: recorded phases 16 s (preflight 5, the kept pytest 4, static 6 and seeds 8 beside it), the rest make's own start and closing steps. Neither the planner nor a Python test selection is left in it, so what carries the miss is the preflight's and the test phase's two runs of the kept pytest, the Python record and docs tools the preflight still starts, and the seeds' 8 s, which is Rust. Under `ask:449-T071-scope` phase 2 closes with the figure and its shares recorded, SC-002's line unmoved; it is re-measured at the phase-3 close, and is no waiver at the feature's close.

**A make done is judged at the incremental floor.** It reuses each crate's unchanged checks, so a green run under the old 40 s floor is no longer evidence of a skipped gate.

**What phase 2 left in Python, by phase** (each placed by a ruling in FR-001, each carrying the T065 clause as far as its line allows):

- Phase 3: `work_budget_view.py`, `replay_owing.py`, `depiction_replay.py`, `event_log.py`, `feature_report.py`, `turn_time.py`, `fix_yield.py`, `task_phases.py`, `where_time.py`, `tool_yield.py`, `check-partial-citations.py`, `agent_census.py`'s fold, and three of `make audit`'s recipes. `test-claims-gate.sh`'s fixture over `claims.py` and `test-entry-gate.sh`'s `answer_all` over `record_owed.py` go in the same cut as those modules.
- Phase 4: `uncovered-in-diff.py`, `uncovered_marks.py`, `tooling_reuse_time.py`, `collect_cost.py`, `collect_probe.py`, `dead_closure.py`, `check-entry-headings.py`, `_invocation.py`, the `make audit` recipe that reads `CLASSES`, and the gate recipe's pytest line.
- Kept tests, ported with what they test: the ten named in T78's plan.

**Not done, carried to the phases that own it.** The docs that still describe the incremental gate (`docs/efficiency-tooling.md`, `dev/gate.md`, `dev/rust-tooling.md`) are stale in those passages; `dev/coverage-exempt.json`, `l7r-gate coverage-exempt`, `delta cov-scope` and `check stale-dirs` no longer have a caller.
