# `rust/guard/` - the guards on Claude Code's tool calls (feature 449 phase 1)

One binary, `l7r-guard`, replaces the repository's 44 shell guards one task at a time (`specs/449-rust-codebase/tasks.md`,
T006-T049): Claude Code calls it once a hook event through `scripts/hooks/l7r-guard.sh` (T004), it reads the input once and runs
every guard's check in a fixed order, and merges their answers by `specs/449-rust-codebase/contracts/guard-protocol.md`.

| file | look here when |
|---|---|
| `src/lib.rs` | the crate's surface: `guards()` in their fixed order, `cli` - the command line (`<event>`, `--only`, `--self-check`, `--version`) |
| `src/protocol.rs` | the hook protocol: the event, the answers, the merge (`run`); its tests in `src/protocol/tests.rs` |
| `src/main.rs` | the binary: prints `cli`'s reply and exits with its code |

`make rust-test`, `make static` check it beside `rust/phases` (the workspace, `rust/Cargo.toml`).
