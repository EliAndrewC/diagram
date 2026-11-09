# Feature 449 phase 1 closed: the guards are Rust

Load this file when: you need what phase 1 of the Rust port measured at its close, what it left in Python and why, or which verdicts it changed on purpose.

The figures are `specs/449-rust-codebase/measurements.json`, by key. FR-010 asks for them in `dev/` as well.

## The timings

| what | at the start | at the close | key |
|---|---|---|---|
| guards before a Bash `ls`, the slowest guard then and the whole dispatch now | 175 ms | 15.4 ms | `m:hooks-bash`, `m:t054-plain-bash` |
| CPU summed over those guards, on that `ls` | 1,045 ms | 15.6 ms, against the 52 ms bound | `m:hooks-bash`, `m:t054-plain-bash` |
| `pair-hooks`' runs in its own suite | mean 441 ms, 39.7 s summed | mean 242 ms, 22.3 s summed over 92 runs | `m:pair-hooks-suite` |
| the same suite's wall time | 8.2 s | 5.0 s | `m:pair-hooks-suite` |

**SC-001 is met on `m:hooks-bash`'s sample, `ls`, alone**, by the named exception `ask:449-T054-sc001`, and not on real commands. A quoted `git` command is 19.0 ms. Over 400 real commands from this project's transcripts the median is 23.0 ms, the 90th percentile 109 ms, and 7.2 percent are under 17.5 ms. Of those 400, 48 name a `git ... commit` and 29 of them start Python: `ledger_hooks::judge`, once `commit_root` finds a real `git commit` in a tree holding the ledger, asks `ledger_owed.py` on every such commit and `ledger_lint.py` when it stages the ledger (T027 decision (b)). That branch is T027's and is not one of T044's two; no command without a commit starts it. Near the 90th percentile are `feature-approval` and `conflict-marker` asking git over a large staged commit (40 to 54 ms each), `make-only` on a guard-file write in a long heredoc (62 ms), and `record-edit-gate` running its guard on an `apply-edits` (56 ms). The real-command distribution is measured again at phase 3's close, when the by-path Python is ported.

## The calls that still start Python, and FR-007 and Story 1

FR-007 and Story 1 ask for one process on a tool call. The round arbiter's ruling `ask:449-hm-checks-route` moved `check-bundle`, `checks` and `record-edit` to phase 3 with their libraries, so these calls run more than one process until then, each timed here by the median of 20 spawns (load 2 to 5), `m:phase-1-other-calls`:

| the call | time |
|---|---|
| an Edit of a record page, through `record-edit-gate` and `record-edit-hooks.sh` | 108.3 ms (a plain Edit: 37.9 ms) |
| a subagent's return, `checks-hooks.sh returned` | 56.6 ms |
| a subagent's launch, `checks-hooks.sh launched` | 50.3 ms |

## What phase 1 leaves in Python

Both censuses, re-run: 845 tracked Python files (872 at the start), none under `tests/hooks/`, and 13 under `scripts/hooks/lib/`, each placed by name in FR-001 (`m:phase-1-python-share`). The search by use found two more, each placed in FR-001 by the ruling `ask:449-T052-round3`: `scripts/gates/engine_edit.py`, a wrapper over phase-2 code that goes with it in phase 2, and `tests/tooling/test_guard_firing_log.py`, a test of the firing log that goes with `guardlog.sh` in phase 3. The second census is `make inline-census`: 57 sites under `scripts/hooks/` and `tests/hooks/`, 27 of them a guard's input (not a run, by exact line in `tests/hooks/census-guard-inputs.txt`), 27 in a file that moves whole with a later piece, 3 that go with their only caller, none outside (`ask:449-T052-inline-census`).

The guards still ask these by path, each on a branch that is not a plain Bash call or a plain Edit, until the phase that owns the file:

| guard | asks | on |
|---|---|---|
| `ledger_hooks` | `ledger_owed.py`, `ledger_lint.py`, `review_cost.py` | a real `git commit` in a tree holding the ledger |
| `escalation_hooks` | `ledger_lint.py` | a review arming, an armed turn's end |
| `review_round_hooks` | `hm_arbiter.py`, `plan_gate.py`, `stale_terms.py` | a spec-fidelity dispatch |
| `pair_hooks` | `checkpoint.py`, `plan_gate.py`, `review_owed.py`, `review_prereq.py`, `gate-stamp.py` | a gate command, an Agent dispatch |
| `blocked_fetch_hooks` | `attempts.py` | a fetch |
| `set_down_hooks` | `speckit-todo.py` | a turn's end with a feature begun |
| `workflow_hooks` | `hm_checks.py`'s `drop_run` | a Workflow call |
| `make_only_hooks` | `ruff` | a landing's lint |
| `clone_sync_hooks` | `gate_lock.py`, `usage_log.py` | a mid-task prompt, a merge just made |
| `engine_freeze_hooks` | `engine_edit.py` | an edit of engine code |
| `gate_write_hooks` | `preflight.py` | a write while a gate runs |
| `measure_hooks` | `gatecost.py` | an expensive measurement |
| `stall_watchdog_hooks` | `page_session_runner.py` | a page session's watch |
| `record_edit_gate` | `record-edit-hooks.sh` and what it imports | a call that concerns it |
| `l7r-guard trace` | `python3` for `sys.version` | a `make hooks-test`, never a hook; goes by phase 3's end |

## What changed on purpose, and the bugs found

- One suite verdict changed: `test-wakeup-hooks.sh`'s input that is not JSON now passes (`ask:449-T038-garbage`, FR-002 names it).
- Two defects fixed under constitution XIV: `make-only` no longer refuses a search that names pytest (T028), and `guard-file` no longer refuses a lone storing `cat`/`tee`, a quoted delimiter, a plain target or a shell-read assignment name (T029).
- `make audit` crashed on a run record whose selected count was a number and on `tests/rolls.py`, deleted by feature 444. Both fixed (T051).
- A guard binary that read stdin to its end hung any tool that inherited an open socket: tool verbs read none, and each suite gets an empty stdin.
- Three stale-state defects kept Python running on every Bash call: the empty `plan_holds` key, snapshots outliving their holds, and holds whose dispatch never launched (T053).
