# `rust/gate/` - the gate's own tools (feature 449 phase 2)

One binary, `l7r-gate`, called from the Makefile through `scripts/gates/l7r-gate.sh`, each subcommand ported from the Python piece it replaces (`specs/449-rust-codebase/tasks.md`, T062-T069). `make static` and `make rust-test` check it beside the other crates.

| file | look here when |
|---|---|
| `src/lib.rs` | the command line, `cli` |
| `src/codeid.rs` | a file's content id, and the id cache shared with the Python callers (T062) |
| `src/stamp.rs` | the green-gate stamps: `stamp --write`, `--fresh`, `--check`, `--selftest`, and what Python callers ask once a process (T063) |
| `src/delta.rs` | the delta, the one list of engine paths (`is_engine`), the engine key (T063) |
| `src/state.rs` | the verification state, `.git/verification-state.json`, and the tooling hash (T72) |
| `src/hashing.rs` | hashing the repository's files by what runs; what decides how the gate's tests run (`config-hash`) (T72) |
| `src/exempt.rs` | the coverage-exemption record, `dev/coverage-exempt.json` (T72) |
| `src/ci.rs`, `src/ci/` | the remote path: the switches, the conditions on a paid run, the dispatcher and its AWS boundary (T064) |
| `src/checks.rs`, `src/checks/` | the text checks and the spec lint: `l7r-gate check <name>` (T065, T066) |
| `src/plan.rs`, `src/plan/` | the plan gates: sections and blocks, what a plan owes, recording a verdict, the review bundle, the approach gate, the engine-edit question (T066); `scripts/plan_door.py` is the Python callers' door |
| `src/main.rs` | the binary: prints `cli`'s reply and exits with its code |
