# The Rust tooling inventory - every Python-only check, and what it becomes in the Rust phases (feature 443 FR-011)

Load this file when: you add a check, hook, gate or make target that reads `.py` files or Python's syntax tree (`make rust-tooling`
refuses one with no row here), or you plan the language decision (feature 444's step 5).

The shape assumed (the design the GM approved on 2026-10-28, `specs/443-work-budget-tooling/request.md` section 7): Rust holds only
the rebuilt phases, compiled into one extension module Python imports (PyO3, built by maturin); the driver and `STAGES`, the
manifest, rendering and the interactive page, the pool's `.gen.py` scripts, the tools and the pytest suite stay Python. So a check
that reads only the tooling's own Python, or the parts that stay Python, is `unchanged`; one that reads the engine's stage code is
ported, partly ported, rewritten or dropped.

`make rust-tooling` (a step of `make hooks-test`, `scripts/gates/check-rust-tooling.py`) lists every tracked file outside `specs/`,
`research/`, `dev/` and the pools that imports `ast`, `tokenize`, `inspect` or `symtable`, calls `compile(` or reads `.py` files,
and every Makefile target whose recipe runs ruff, pyrefly, pytest, coverage, testmon or vulture or globs `*.py`; it fails on any
that no row's KEYS name (a path, a glob, or `make <target>`). **Before the first Rust phase lands**, every row marked one for one,
partial or rewritten is proven to fire on a Rust fixture (the design's section 7; carried to feature 444's step 5, the language
decision).

| check | today (Python) | in the Rust phases | fate | keys |
|---|---|---|---|---|
| lint | ruff | clippy, all and pedantic, warnings refused | one for one | `make static` `make quick` `make done` `make format` `scripts/format-changed.sh` |
| format | ruff format | rustfmt | one for one | `make format` `scripts/format-changed.sh` |
| types | pyrefly | the Rust compiler, which is stricter | dropped, replaced by the compiler | `make static` |
| function cap | PLR0915 and `check-function-cap.py`, 100 statements, a suppression says why | clippy `too_many_lines` (100 lines); `#[expect(lint, reason = "...")]` and `allow_attributes_without_reason` | one for one, counts lines | `scripts/gates/check-function-cap.py` |
| file cap | `check-file-scale.py`, 1,000 raw lines | the same script, reading `.rs` | one for one | `scripts/gates/check-file-scale.py` |
| duplicate top-level definitions | `check-duplicate-defs.py` | the compiler refuses them | dropped, replaced by the compiler | `scripts/gates/check-duplicate-defs.py` |
| coverage and its floors | 100% line coverage, the floors, the gate's phases | `cargo llvm-cov --fail-under-lines 100`, plus the Rust lines pytest reaches through the extension | one for one; an argued exclusion only partial (`#[coverage(off)]` needs nightly) | `make done` `make test` `make tooling` `make cov-file` `make claims-coverage` `make soak` `make durations` |
| changed modules' coverage | `make cover-changed` | llvm-cov per changed `.rs` file | one for one | `scripts/gates/cover_changed.py` |
| the change-selected tests | `quick`'s testmon selection, the gate's incremental plan and its preflight | cargo rebuilds and re-tests the changed crate; pytest's selection covers the Python callers | partial | `make quick` `make test-file` `make page-check` `make spec-harness` `l7r/diagram/ci/incremental.py` `l7r/diagram/ci/gate_config.py` `scripts/gates/preflight.py` |
| the docstring-blind code id | `codeid`, `gate-stamp`, the cache's engine hash, the delta's engine test, the land route | a hash of the Rust token stream without comments; the built extension added to `gencache.engine_files()`; `.rs` an engine path | rewritten | `scripts/gates/codeid.py` `scripts/gates/gate-stamp.py` `l7r/diagram/pipeline/gencache.py` `l7r/diagram/pipeline/rollcache.py` `l7r/diagram/pipeline/render_cache.py` `l7r/diagram/ci/delta.py` `l7r/diagram/ci/state.py` `scripts/land.py` |
| research claims | `Research:` in docstrings, the claims index, gate, bundles, triage, carry, stale figures, `make tunables`, `make open-questions` | the same section in `///` doc comments; a new reader (the `syn` parser) writes the same index | rewritten reader; the process unchanged | `l7r/diagram/tools/claims.py` `scripts/record/claims*.py` `scripts/record/tunables.py` `scripts/record/open_questions.py` `scripts/record/record_cache.py` |
| the placement-stages page | `STAGES` and `Steps:` docstrings | unchanged for the stages (the thin Python functions stay); a Rust step read through the doc-comment reader | partial: the steps' reader is new | `l7r/diagram/tools/placement_stages.py` |
| cache audit | mutate a literal, compare sweeps | the same audit, mutating `.rs` and rebuilding | one for one, slower | `l7r/diagram/tools/cache_audit.py` |
| dead closure | `make dead-closure` | the compiler's dead-code lint, refused, for private items; the script for the rest | partial | `scripts/measure/dead_closure.py` |
| the overlap census | per-call comparison counts of each check, from the engine's Python | the work-budget counters, which count inside Rust | replaced | `l7r/diagram/tools/overlap_census.py` |
| the work-budget audit bundle | the stage's modules copied for MODE AUDIT | the stage's `.rs` modules beside its thin Python function | one for one | `scripts/reviews/work_budget_bundle.py` |
| the make-only guard | the hook refuses a bare interpreter; `_invocation.py` refuses in-process use | the hook also refuses a bare `cargo`; the extension refuses use outside make | one for one | `scripts/hooks/lib/hm_make.py` `scripts/hooks/pair-hooks.sh` |
| the engine-freeze guard | an engine `.py` edit while a map review runs | `.rs` an engine path | one for one | `scripts/hooks/lib/hm_engine_freeze.py` |
| a wording-only change, a held feature's paths | `wording.py` and `plan_hold.py` read which paths are code | `.rs` code | one for one | `scripts/gates/wording.py` `scripts/gates/plan_hold.py` |
| the interactive classes and their modal checks | the class docstrings read by `inspect`; entry and modal owed, bundles, conditions | unchanged: the interactive page stays Python | unchanged | `l7r/diagram/interactive/classes/_base.py` `l7r/diagram/interactive/conditions.py` `scripts/record/entry_owed.py` `scripts/record/modal_bundle.py` `scripts/record/modal_owed.py` |
| the record's build | `record_build` keyed to the registry and its Python | unchanged: the record stays Python | unchanged | `l7r/diagram/pipeline/record_build.py` |
| the tool yield | `make tool-yield` reads the tools' own files | unchanged: the tools stay Python | unchanged | `scripts/measure/tool_yield.py` |
| this inventory's check | `make rust-tooling` reads the tree for Python readers | the same check, its patterns extended to readers of `.rs` (`syn`, `*.rs`) | one for one | `scripts/gates/check-rust-tooling.py` |
| the pytest suite | tests that read source (`ast`, `inspect`) or glob `*.py`: the surface guards, the namespace portion, the hooks' and tools' tests | unchanged for the Python they read; a test of a stage's own source moves with the stage to its Rust tests (`#[cfg(test)]` in their own file) | partial | `tests/**` `make hooks-test` |
