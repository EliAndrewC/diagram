# scripts/ - the project's tooling, by purpose

Everything runs through `make` (the targets name these files); the top level holds only what a session runs by hand.
Organized 2026-10-08 at the GM's request: a helper inside a subdirectory has no leading underscore.

| path | what is in it |
|---|---|
| `sync-with-main.sh`, `git-askpass-token.sh` | the commands: stop-work and sync, git's HTTPS credentials (`make claim`, `make trial`, `make trial-review`, `make docs`, `make task-add`, `make set-down` and the anchored-edit sweep `l7r-gate.sh patch` are `l7r-gate`'s since 449 T135) |
| `record_door.py` | Python's door to the record leaves in Rust (`l7r-gate record moved-only`, `fragments`, `americanize`), one process a run (449 T81) |
| `owed_door.py` | Python's one door to the record's owed tools in Rust (`l7r-gate owed-door`: `ro`, `ru`, `mo`, `mt`; `mb`, `cb` for the bundles' two names `apply_edits` and `sources` read), one process a run (449 T87, T88) |
| `bundle_door.py` | the Rust bundles' one runner of the Python they still reach (`check_bundle`'s helpers, `passages`, the cache-only page save, the knobs; `is_current` for `l7r-gate reviews prereq check`, T89; the claims tools' `.py` half, T82; `make claims-known`'s `gm-review.jsonl` row left with `gm_review.py`'s port, 449 T91), started only when a run needs a verb (449 T88, `ask:449-T88-bundles`, `ask:449-T82-claims`) |
| `hooks/` | the guards (`*-hooks.sh`) that `.claude/settings.json` runs on every tool call; `docs/guards.md` is their record |
| `hooks/lib/` | what the shell around the guards still shares: `guardlog.sh`, `clone-resolve.sh`, `writer-alive.sh`, `lld-path.sh` (the `hm_*` deciders and `usage_log.py` are the guard's `rust/guard/src/shared/` now, feature 449 T129) |
| `gates/` | what refuses at the gate or the push: `l7r-gate stamp`, the `*-gate.sh` gates, `l7r-gate check <name>` (the text checks and the spec lint, `rust/gate/crates/checks/src/checks/`), `l7r-gate plan` (the plan gates, `rust/gate/crates/plan/src/plan/`), `l7r-gate lock`, `own-make`, `rust`, `push-gate` and `push-checks` (the gate lock, the Rust crates' checks, the push's checks), `l7r-gate cohort` (the landing cohort, the room table), the `check-*.py` that remain |
| `record/` | the research record's tooling: sources, the archive, downloads, canon, check bundles, what a delta owes |
| `pages/` | page sessions: the runner, its briefs, `pull-queue.sh`, coordination files |
| `reviews/` | the review checks' tooling left in the shell and Python (`layout_carry.sh`, `size_table.py`); the census and the agent sync (`l7r-gate reviews census`, `agent-sync`, 449 T136), the snapshot (`l7r-gate reviews snapshot`, 449 T132), what is owed, the prerequisites, the verdict record and the hourly checkpoint are `l7r-gate reviews` (`rust/gate/crates/reviews/src/reviews/`, 449 T89), and so are the ledger's lint, a review's cost and the rows a pass owes (`reviews ledger-lint`, `review-cost`, `ledger-owed`, 449 T83) |
| `measure/` | what things cost: `make inline-census` (feature 449's second census), gate cost, the ratchets, run stats, `make figures`, the guard log |
| `container/` | the container's setup (`setup-dev-env.sh`), the system-prompt text its `claude()` wrapper loads, the page-session rules |

Each guard's suite is `tests/hooks/test-<guard>.sh`, run by `make hooks-test` (a guard without one fails it); the
suites' recorded command corpora are `tests/hooks/fixtures/`.

Helpers import each other flat (`import record_prepass`): a script that imports from another subdirectory adds that
directory to `sys.path` beside its own (search for "the moved scripts it imports").
