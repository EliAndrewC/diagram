# 461 T03: only a session's own clone lands alone (451 T302 part 1, plan D11)

Load this file when: you are retiring land-alone (461 T30) and need every place that asks it, runs it or reads it.

Read 2026-11-27 by the 461 T03 builder in diagram-backlog-t271 at f412c319b7. Nothing in the engine or the tooling changed.

## What was run

From the clone's root: `bash dev/measurements/2026-11-27/461-t03-land-alone-callers/callers.sh > dev/measurements/2026-11-27/461-t03-land-alone-callers/output.txt`.
The output is `output.txt`. Re-running it gives the same lines while the code it reads is unchanged.

## What it shows

- **`alone_owed` is asked once.** It is defined in `rust/gate/crates/land/src/land/alone.rs` and asked only in `Land::land`
  (`land.rs`). It answers true only where the run is not the landing worktree's own run (`INNER` unset) and the tree is dirty.
- **`land-alone.sh` is run once.** Its one runner is `alone.rs`'s `SCRIPT`, used in `Land::alone`. The land crate's
  `Cargo.toml` names it only as a file its tests read.
- **`Land::land` is reached only by `make land` and `make land-batch`.** Both run `$(LAND_RUN) "$(F)" "$(T)"`, and
  `land-batch` is the same command under feature 385's name. The other callers of `l7r-gate land` never reach it: `make carry`
  (`--carry`), `make land-stop` (`--stop`) and `scripts/sync-with-main.sh` (`--unfinished`) each return in `land::cli`
  before the landing.
- **Where those run.** A builder lands nothing; its tree is committed by `make builder-done` and carried by the session
  (`scripts/container/builder-brief.md`). So `make land`, and with it land-alone, runs only in a session's own clone. T302
  part 1 is confirmed.

## Found beside it

- `scripts/gates/review-tree.sh` lines 109-110 do not run `land-alone.sh`, but they read its `PYLIB` (step 3, the attribution
  of uncommitted files by the event log) and run its `split`. When T30 retires step 3, `make review-tree` would die with
  "holds no PYLIB". Filed as 461 T36; it lands before T30.
