# `rust/gate/` - the gate's own tools (feature 449 phase 2)

One binary, `l7r-gate`, called from the Makefile through `scripts/gates/l7r-gate.sh`, each subcommand ported from the Python piece it replaces (`specs/449-rust-codebase/tasks.md`, T062-T069). `make static` and `make rust-test` check it beside the other crates.

| file | look here when |
|---|---|
| `src/lib.rs` | the command line, `cli` |
| `src/main.rs` | the binary: prints `cli`'s reply and exits with its code |
