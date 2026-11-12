# scripts/ - the project's tooling, by purpose

Everything runs through `make` (the targets name these files); the top level holds only what a session runs by hand.
Organized 2026-10-08 at the GM's request: a helper inside a subdirectory has no leading underscore.

| path | what is in it |
|---|---|
| `sync-with-main.sh`, `claim-feature.py`, `tick-task.py`, `make-docs.py`, `patch.py`, `git-askpass-token.sh` | the commands: stop-work and sync, `make claim`, `make tick`, `make docs`, the anchored-edit sweep, git's HTTPS credentials |
| `checks_door.py` | Python's one door to the check state and the arbiter in Rust (`l7r-gate checks-door`), one process a run (449 T86); also `review_hold` and `review_owed`, `tick-task.py`'s and `review_snapshot.py`'s reach into the reviews' port (449 T89) |
| `record_door.py` | Python's door to the record leaves in Rust (`l7r-gate record moved-only`, `fragments`, `americanize`), one process a run (449 T81) |
| `owed_door.py` | Python's one door to the record's owed tools in Rust (`l7r-gate owed-door`: `ro`, `ru`, `mo`, `mt`; `mb`, `cb` for the bundles' two names `apply_edits` and `sources` read), one process a run (449 T87, T88) |
| `bundle_door.py` | the Rust bundles' one runner of the Python they still reach (`check_bundle`'s helpers, `passages`, the cache-only page save, the knobs; `is_current` for `l7r-gate reviews prereq check`, T89; the claims tools' `.py` half and `make claims-known`'s `gm-review.jsonl` row, T82), started only when a run needs a verb (449 T88, `ask:449-T88-bundles`, `ask:449-T82-claims`) |
| `claims_door.py` | Python's door to the claims tools in Rust (`l7r-gate claims-door`: `current`, `owed`, `load_index`, `load_store` and the constants), for `impl_check.py` (449 T82, `ask:449-T82-claims`; `land.py`'s and `replay_owing.py`'s verbs left with their Rust ports, 449 T121) |
| `hooks/` | the guards (`*-hooks.sh`) that `.claude/settings.json` runs on every tool call; `docs/guards.md` is their record |
| `hooks/lib/` | what the guards share: the `hm_*` deciders, `guardlog.sh`, the watchdog's pass, the refusal text |
| `gates/` | what refuses at the gate or the push: `l7r-gate stamp`, the `*-gate.sh` gates, `l7r-gate check <name>` (the text checks and the spec lint, `rust/gate/crates/checks/src/checks/`), `l7r-gate plan` (the plan gates, `rust/gate/crates/plan/src/plan/`; `plan_door.py` is Python's door to them), `l7r-gate lock`, `own-make`, `rust`, `push-gate` and `push-checks` (the gate lock, the Rust crates' checks, the push's checks), `l7r-gate cohort` (the landing cohort, the room table), the `check-*.py` that remain |
| `record/` | the research record's tooling: sources, the archive, downloads, canon, check bundles, what a delta owes |
| `pages/` | page sessions: the runner, its briefs, `pull-queue.sh`, coordination files |
| `reviews/` | the review checks' tooling: the snapshot and the census; what is owed, the prerequisites, the verdict record and the hourly checkpoint are `l7r-gate reviews` (`rust/gate/crates/reviews/src/reviews/`, 449 T89), and so are the ledger's lint, a review's cost and the rows a pass owes (`reviews ledger-lint`, `review-cost`, `ledger-owed`, 449 T83) |
| `measure/` | what things cost: `make inline-census` (feature 449's second census), gate cost, the ratchets, run stats, `make figures`, the guard log, uncovered lines |
| `container/` | the container's setup (`setup-dev-env.sh`), the system-prompt text its `claude()` wrapper loads, the page-session rules |

Each guard's suite is `tests/hooks/test-<guard>.sh`, run by `make hooks-test` (a guard without one fails it); the
suites' recorded command corpora are `tests/hooks/fixtures/`.

Helpers import each other flat (`import record_prepass`): a script that imports from another subdirectory adds that
directory to `sys.path` beside its own (search for "the moved scripts it imports").
