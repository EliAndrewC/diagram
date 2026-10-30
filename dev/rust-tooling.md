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
| research claims | `Research:` in docstrings, the claims index, gate, bundles, triage, carry, stale figures, `make tunables`, `make open-questions` | the same section in `///` doc comments; a new reader (the `syn` parser) writes the same index | rewritten reader; the process unchanged | `l7r/diagram/tools/claims.py` `l7r/diagram/tools/claims_rust.py` `scripts/record/claims*.py` `scripts/record/tunables.py` `scripts/record/open_questions.py` `scripts/record/record_cache.py` |
| the placement-stages page | `STAGES` and `Steps:` docstrings | unchanged for the stages (the thin Python functions stay); a Rust step read through the doc-comment reader | partial: the steps' reader is new | `l7r/diagram/tools/placement_stages.py` |
| cache audit | mutate a literal, compare sweeps | the same audit, mutating `.rs` and rebuilding | one for one, slower | `l7r/diagram/tools/cache_audit.py` |
| dead closure | `make dead-closure` | the compiler's dead-code lint, refused, for private items; the script for the rest | partial | `scripts/measure/dead_closure.py` `scripts/gates/rust_checks.py` |
| the overlap census | per-call comparison counts of each check, from the engine's Python | the work-budget counters, which count inside Rust | replaced | `l7r/diagram/tools/overlap_census.py` |
| the work-budget audit bundle | the stage's modules copied for MODE AUDIT | the stage's `.rs` modules beside its thin Python function | one for one | `scripts/reviews/work_budget_bundle.py` `scripts/gates/phase_sources.py` |
| the make-only guard | the hook refuses a bare interpreter; `_invocation.py` refuses in-process use | the hook also refuses a bare `cargo`; the extension refuses use outside make | one for one | `scripts/hooks/lib/hm_make.py` `scripts/hooks/pair-hooks.sh` `make rust-test` |
| the engine-freeze guard | an engine `.py` edit while a map review runs | `.rs` an engine path | one for one | `scripts/hooks/lib/hm_engine_freeze.py` |
| a wording-only change, a held feature's paths | `wording.py` and `plan_hold.py` read which paths are code | `.rs` code | one for one | `scripts/gates/wording.py` `scripts/gates/plan_hold.py` |
| the interactive classes and their modal checks | the class docstrings read by `inspect`; entry and modal owed, bundles, conditions | unchanged: the interactive page stays Python | unchanged | `l7r/diagram/interactive/classes/_base.py` `l7r/diagram/interactive/conditions.py` `scripts/record/entry_owed.py` `scripts/record/modal_bundle.py` `scripts/record/modal_owed.py` |
| the record's build | `record_build` keyed to the registry and its Python | unchanged: the record stays Python | unchanged | `l7r/diagram/pipeline/record_build.py` |
| the tool yield | `make tool-yield` reads the tools' own files | unchanged: the tools stay Python | unchanged | `scripts/measure/tool_yield.py` |
| this inventory's check | `make rust-tooling` reads the tree for Python readers | the same check, its patterns extended to readers of `.rs` (`syn`, `*.rs`) | one for one | `scripts/gates/check-rust-tooling.py` |
| the pytest suite | tests that read source (`ast`, `inspect`) or glob `*.py`: the surface guards, the namespace portion, the hooks' and tools' tests | unchanged for the Python they read; a test of a stage's own source moves with the stage to its Rust tests (`#[cfg(test)]` in their own file) | partial | `tests/**` `make hooks-test` |

## Proven on the fixture (feature 444 T17)

Each row below fires on `tests/fixtures/rust/fixture` - its check refuses a copy written to break it and passes the fixture - in
`tests/tooling/test_rust_tooling.py`. A row not listed here is not yet proven, and FR-011 holds the first Rust phase until all are.

| row | the check | the test that fires it |
|---|---|---|
| lint | `scripts/gates/rust_checks.py lint` in `make static`: clippy, the crate's `[lints.clippy]` denying all and pedantic | `test_lint_passes_the_fixture_and_refuses_a_pedantic_breach` |
| format | `rust_checks.py format` in `make format` (`--check` refuses) | `test_format_passes_the_fixture_and_refuses_what_rustfmt_would_change` |
| function cap | clippy `too_many_lines` at the root `clippy.toml`'s 100; `allow_attributes_without_reason` denied | `test_the_function_cap_refuses_a_function_past_a_hundred_lines`, `test_an_exception_with_no_reason_is_refused` |
| file cap | `check-file-scale.py` scanning `.rs` | `test_the_file_cap_reads_rust_files` |
| the make-only guard | `hm_make.py` refuses a bare `cargo` (build, test, run, clippy, check, fmt, llvm-cov); `make rust-test` runs `cargo test` | `tests/hooks/test-make-only-hooks.sh` ("a bare cargo test", "a bare cargo clippy, by path"); `test_rust_test_passes_the_fixture_and_refuses_a_failing_test` |
| a wording-only change, a held feature's paths | `wording.py` counts any `.rs` change as what runs; `plan_hold.py` counts `rust/` paths and `.rs` stems as engine | `tests/tooling/test_wording_rust.py`; `test_a_task_whose_plan_section_names_an_engine_path_is_an_engine_task` (red without the change) |
| this inventory's check | `check-rust-tooling.py` also lists a reader of `.rs` files and a Makefile recipe running cargo, clippy, rustfmt, llvm-cov or `rust_checks.py` | `test_a_reader_of_each_kind_with_no_row_fails_and_a_row_clears_it` (the `.rs` cases), `test_a_make_recipe_running_the_rust_tools_needs_its_row` |
| coverage and its floors | `rust_checks.py cover` in `make static`: `cargo llvm-cov --fail-under-lines 100` over the crate's tests AND its Python driver (`tests/py_driver.py`) through the instrumented extension, one report | `test_coverage_counts_the_lines_python_reaches_and_refuses_an_untested_line` (the fixture's own tests reach 40%, its driver the rest; an uncalled line fails) |
| changed modules' coverage | `make cover-changed` (`cover_changed.py`): each changed `.rs` under `rust/`, by its crate, the lines `rust_checks.uncovered` (llvm-cov's LCOV over the crate's tests and Python driver) finds unreached | `test_uncovered_names_the_lines_of_each_file_no_test_reaches`; `test_a_changed_rust_file_is_grouped_by_its_crate_and_its_unreached_lines_named` |
| the work-budget audit bundle | `work_budget_bundle.stage_files` adds the `.rs` under `rust/` defining `fn stage_<phase>` (its module directory's siblings with it); the phase-source guard holds only the `.py` | `tests/tooling/test_work_budget_bundle_rust.py`; `test_a_phase_task_holds_its_stage_its_counted_modules_and_its_old_code_globs` (the `.rs` never held) |
| the engine-freeze guard | `delta.is_engine` counts `rust/**/*.rs`, `Cargo.toml` and `Cargo.lock` as engine (and `codeid.ENGINE` with it, so a Rust delta routes GATED and owes the landing cohort); the tooling fixture under `tests/` is not | `tests/tooling/ci/test_delta.py` (the `rust/` cases, the fixture not engine); `tests/hooks/test-engine-freeze-hooks.sh` ("a Rust phase is engine: refused") |
| the docstring-blind code id | `codeid.rust_tokens`: a `.rs` file's tokens with every comment and doc comment dropped, in `semantic_bytes`, `gate-stamp.py content_id` and the render fingerprint; `gencache.rust_sources` puts `rust/**/*.rs` and the Cargo manifests in the generation key (`engine_files`) and the render fingerprint alike; `.rs` an engine path (row above) | `tests/tooling/test_codeid_rust.py` (wording keeps the id, code moves it, the stamp reads tokens); `test_engine_files_prunes_the_tests_tree`, `test_engine_fingerprint_covers_and_skips` (the Rust cases) |
| research claims | `tools/claims_rust.py` reads each `.rs` item's `///` `Research:` section (else the `//!` module doc's, inherited) into the same `claims.Unit`s, its core the item's comment-free tokens; `claims.all_units` yields them in the scope, so the index, gate, bundles, triage and reports downstream are unchanged. A DEVIATION from the row's "the `syn` parser": a Python brace scan gives the span and doc the units need and stays in the indexing process | `tests/tools/test_claims_rust.py` (units, spans and kinds; own and inherited claims; a doc edit keeps the core, code moves it; the index reads them) |
| the placement-stages page | a `Steps:` name `rust/<crate>/src/<file>.rs::<item>` resolves through `claims_rust.resolve` to a `RustItem` whose `__doc__` is the item's doc comment; `research_of` reads its unit's claims; the stages stay Python | `test_a_rust_step_on_the_placement_page_shows_its_doc_and_its_claims` |
| dead closure | private items: rustc's `dead_code`, an error under `rust_checks.py lint`'s `-D warnings`; public: `rust_checks.py dead` in `make static`, a `pub fn` nothing in Rust or Python calls refused | `test_a_private_item_nothing_calls_is_refused`, `test_a_public_function_nothing_calls_is_refused_and_one_python_calls_is_kept` |
| the change-selected tests | the Rust half: cargo rebuilds and re-tests the changed crate (`make rust-test`, `make static`'s coverage run); the Python half: `rust_checks.py callers` in `make quick` runs every test importing the extension, which testmon cannot select for a `.rs` change | `test_rust_test_passes_the_fixture_and_refuses_a_failing_test`, `test_a_rust_change_selects_every_python_test_that_imports_the_extension`, `test_the_dead_and_callers_commands_run_on_the_named_crate` |
| the pytest suite | a test of a stage's own source moves with the stage into its `#[cfg(test)]` module, run by `make rust-test`; the Python tests of the parts that stay Python unchanged | `test_rust_test_passes_the_fixture_and_refuses_a_failing_test` |

### Not yet proven (2026-10-30), and what each waits for

- **cache audit** (mutate a `.rs` literal, rebuild, compare sweeps): it audits MAPS, and a crate the engine never imports changes no
  sweep - first possible on T19's `water_frame` port.
- **the overlap census** (its replacement, the work-budget counters counted inside Rust): needs the counting interface the Rust
  phases report their operations through, designed with T19, the first phase whose MODE AUDIT reads `.rs`.

**Proven on the first phase, not the fixture** - the round arbiter's ruling on ask:444-T17-rows-need-a-phase (2026-10-30, Route A),
narrowed by the plan review of 2026-10-30: dead closure's public half and the change-selected tests' Python half fire on the
fixture and are proven above; these two need a phase's maps or counters, so T19's port owes them before its tick, each proven as the
rest were. `check-rust-tooling.py` refuses any tree holding a Rust phase while one is unproven
(`test_a_rust_phase_cannot_land_while_a_row_is_unproven`), so no phase lands with a row open.
