# `rust/guard/` - the guards on Claude Code's tool calls (feature 449 phase 1)

One binary, `l7r-guard`, replaces the repository's 44 shell guards one task at a time (`specs/449-rust-codebase/tasks.md`,
T006-T049): Claude Code calls it once a hook event through `scripts/hooks/l7r-guard.sh` (T004), it reads the input once and runs
every guard's check in a fixed order, and merges their answers by `specs/449-rust-codebase/contracts/guard-protocol.md`.

| file | look here when |
|---|---|
| `src/lib.rs` | the crate's surface: `guards()` in their fixed order, `cli` - the command line (`<event>`, `--only`, `--idle-tests`, `--agent-stall`, `--stall-watchdog`, `--finished-run`, `--self-check`, `--version`) |
| `src/protocol.rs` | the hook protocol: the event, the answers, the merge (`run`); its tests in `src/protocol/tests.rs` |
| `src/shared/` | what every guard reads (T003): `shape` (heredoc and quote stripping), `escape` (the tokens' two-word reasons), `session` (the facts read once a process - the mirror, the clone, the transcript, the GM's messages - each read counted), `transcript` (`gm_messages`), `log` (the guard log, `guardlog.sh`'s format), `tool` (asking a tool the guards consult, T006 decision (a)), `sha256`, `make` (the make targets a command invokes, `hm_make.py`'s parts T007 reads), `state` (a session's state file, an input field), `wait` (the shapes of a wait, `hm_shape.py`'s wait half), `tree` (where a command's writes land, `hm_tree.py`), `sha1` |
| `src/guards.rs`, `src/guards/` | the guards, one module each in their fixed order: `pair_hooks` (T006) - the gate and its review together, its state (`state.rs`) and its review checks (`review.rs`); `gate_hooks` (T007) - no `-k` subset as the only run before the gate, quick and done combined; `measure_hooks` (T008) - the expensive measurement batched; `no_poll_hooks` (T009) - no busy-wait, the file wait made safe; `main_tree_hooks` (T010) - a write landing in the mirror moved to the clone; `event_log_hooks` (T012) - a line of the feature's event log on every event; `clone_sync_hooks` (T013) - the session's clone synced on a prompt, an edit routed to its own clone on a current base (`resolve` alone stays in `scripts/hooks/clone-sync-hooks.sh` until T051); `idle_tests_hooks` (T014) - a Stop arms the idle run, disabled by the GM's switch, a prompt disarms it; `agent_stall_hooks` (T015) - a stalled subagent reported at the next prompt; `stall_watchdog_hooks` (T016) - any prompt keeps the loop outside every session running; `finished_run_hooks` (T017) - a finished run surfaced, a turn not closed over a run nothing will wake, `runs.rs` the `/proc` walks |
| `src/main.rs` | the binary: prints `cli`'s reply and exits with its code |

`make rust-test`, `make static` check it beside `rust/phases` (the workspace, `rust/Cargo.toml`).

A guard's suite replays through its link `tests/hooks/<guard>.sh` -> `tests/hooks/guard-shim.sh`, which runs
`l7r-guard --only <guard> <event>`; `make hooks-test` finds a ported guard by that link.
