# scripts/ - the project's tooling, by purpose

Everything runs through `make` (the targets name these files); the top level holds only what a session runs by hand.
Organized 2026-10-08 at the GM's request: a helper inside a subdirectory has no leading underscore.

| path | what is in it |
|---|---|
| `sync-with-main.sh`, `claim-feature.py`, `tick-task.py`, `make-docs.py`, `patch.py`, `git-askpass-token.sh` | the commands: stop-work and sync, `make claim`, `make tick`, `make docs`, the anchored-edit sweep, git's HTTPS credentials |
| `hooks/` | the guards (`*-hooks.sh`) that `.claude/settings.json` runs on every tool call; `docs/guards.md` is their record |
| `hooks/lib/` | what the guards share: the `hm_*` deciders, `guardlog.sh`, the watchdog's pass, the refusal text |
| `gates/` | what refuses at the gate or the push: `l7r-gate stamp`, the `*-gate.sh` gates, `l7r-gate check <name>` (the text checks and the spec lint, `rust/gate/src/checks/`), `l7r-gate plan` (the plan gates, `rust/gate/src/plan/`; `plan_door.py` is Python's door to them), `l7r-gate lock`, `own-make`, `rust`, `push-gate` and `push-checks` (the gate lock, the Rust crates' checks, the push's checks), `l7r-gate cohort` (the landing cohort, the room table), the `check-*.py` that remain |
| `record/` | the research record's tooling: sources, the archive, downloads, canon, check bundles, what a delta owes |
| `pages/` | page sessions: the runner, its briefs, `pull-queue.sh`, coordination files |
| `reviews/` | the review checks' tooling: what is owed, the snapshot, cost and census, the ledger lint, `moves.py` |
| `measure/` | what things cost: `make inline-census` (feature 449's second census), gate cost, the ratchets, run stats, `make figures`, the guard log, uncovered lines |
| `container/` | the container's setup (`setup-dev-env.sh`), the system-prompt text its `claude()` wrapper loads, the page-session rules |

Each guard's suite is `tests/hooks/test-<guard>.sh`, run by `make hooks-test` (a guard without one fails it); the
suites' recorded command corpora are `tests/hooks/fixtures/`.

Helpers import each other flat (`import record_owed`): a script that imports from another subdirectory adds that
directory to `sys.path` beside its own (search for "the moved scripts it imports").
