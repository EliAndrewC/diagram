# scripts/ - the project's tooling, by purpose

Everything runs through `make` (the targets name these files); the top level holds only what a session runs by hand.
Organized 2026-10-08 at the GM's request: a helper inside a subdirectory has no leading underscore.

| path | what is in it |
|---|---|
| `sync-with-main.sh`, `git-askpass-token.sh` | the commands: stop-work and sync, git's HTTPS credentials (`make claim`, `make trial`, `make trial-review`, `make docs`, `make task-add`, `make set-down` and the anchored-edit sweep `l7r-gate.sh patch` are `l7r-gate`'s since 449 T135; `record_door.py` and `owed_door.py`, Python's doors to the record tools in Rust, left with their last caller, `entry_owed.py`, 449 T149) |
| `hooks/` | the guards (`*-hooks.sh`) that `.claude/settings.json` runs on every tool call; `docs/guards.md` is their record |
| `hooks/lib/` | what the shell around the guards still shares: `guardlog.sh` (`guard_log`, over the gate's `log guard` since feature 449 T143, `clone-resolve.sh` deleted), `writer-alive.sh`, `lld-path.sh` (the `hm_*` deciders and `usage_log.py` are the guard's `rust/guard/shared/src/` now, feature 449 T129) |
| `gates/` | what refuses at the gate or the push: `l7r-gate stamp`, the `*-gate.sh` gates, `l7r-gate check <name>` (the text checks and the spec lint, `rust/gate/crates/checks/src/checks/`), `l7r-gate plan` (the plan gates, `rust/gate/crates/plan/src/plan/`), `l7r-gate lock`, `own-make`, `rust`, `push-gate` and `push-checks` (the gate lock, the Rust crates' checks, the push's checks), `closing-checks.sh` (`make closing-checks T=<task>`: make static, hooks-test and quick at once, one result, 451 T55; the task's files and crates judged, another task's red apart, 451 T86), `l7r-gate cohort` (the landing cohort, the room table) |
| `record/` | the research record's tooling: sources, the archive, downloads, canon, check bundles, what a delta owes |
| `pages/` | page sessions: `page-session.sh` (`make page-session`, which execs the runner, `l7r-gate page-session`), `pull-queue.sh`; the runner, the write cap's count, `make lines`/`append`, the claims sheet and the escape log are `l7r-gate`'s (`rust/gate/crates/pages/`, 449 T137) |
| `reviews/` | the review checks' tooling left in the shell (`layout_carry.sh`; `size_table.py` is `l7r-mode-a size-table` since 449 T174); the census and the agent sync (`l7r-gate reviews census`, `agent-sync`, 449 T136), the snapshot (`l7r-gate reviews snapshot`, 449 T132), what is owed, the prerequisites, the verdict record and the hourly checkpoint are `l7r-gate reviews` (`rust/gate/crates/reviews/src/reviews/`, 449 T89), and so are the ledger's lint, a review's cost and the rows a pass owes (`reviews ledger-lint`, `review-cost`, `ledger-owed`, 449 T83) |
| `measure/` | what things cost: `make inline-census` (feature 449's second census), gate cost, the ratchets, run stats, `make figures`, the guard log |
| `container/` | the container's setup (`setup-dev-env.sh`; the browser crate's Chromium `install-chromium.sh`, its version `chromium.pin`, 449 T146; the embedder crate's ONNX Runtime `install-onnxruntime.sh`, its version `onnxruntime.pin`, 449 T138), the system-prompt text its `claude()` wrapper loads, the page-session rules |

Each guard's suite is `tests/hooks/test-<guard>.sh`, run by `make hooks-test` (a guard without one fails it); the
suites' recorded command corpora are `tests/hooks/fixtures/`.

