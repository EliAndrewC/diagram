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
| `src/ci.rs`, `src/ci/` | the route and a gated push's conditions, the switches, the push's credential (T064, T73) |
| `src/checks.rs`, `src/checks/` | the text checks and the spec lint: `l7r-gate check <name>` (T065, T066) |
| `src/plan.rs`, `src/plan/` | the plan gates: sections and blocks, what a plan owes, recording a verdict, the review bundle, the approach gate, the engine-edit question (T066); `scripts/plan_door.py` is the Python callers' door |
| `src/lock.rs` | the host-wide gate lock and whether a make runs in this tree: `lock`, `own-make` (T067) |
| `src/rustc.rs` | the Rust crates' checks: `rust lint`, `format`, `test`, `cover`, `dead`, `uncovered` (T067) |
| `src/push.rs` | the push's checks and what each push gate judges: `push-checks`, `push-gate` (T067) |
| `src/cohort.rs`, `src/cohort/` | the landing cohort, each seed's standing against main's engine, the seed report, the room table: `l7r-gate cohort` (T068) |
| `src/measure.rs`, `src/measure/` | what things cost: `figures`, `gatecost`, `gate-costs`, `ratchet` (its table is `dev/ratchets.json`), `probe` (T75) |
| `src/preflight.rs` | the gate's first phase and its tree check, `preflight` (T071) |
| `src/logs.rs` | the records the gate's shell writes, `log run`, `log bypass`, `log gate-bypass`, `log land-tooling`; `json-field`, `ruff-toml` (T069) |
| `src/record.rs`, `src/record/` | the research record's tools: `canon`, `money-conversions`, `found`, `access-tags`, `downloads`, and the leaves Python reaches through a verb (`leaves.rs`: `edit-route`, `fragments`, `moved-only`, `americanize`; `scripts/record_door.py` is the door) (T79-T81) |
| `src/main.rs` | the binary: prints `cli`'s reply and exits with its code |
