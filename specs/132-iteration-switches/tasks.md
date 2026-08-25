# Tasks: The Iteration Switches (132)

Checked off only when verified. `make done` (reference scope) is the gate; `make hooks-test` for the
shell guards.

## Phase 0 - review

- [x] T01 `spec-fidelity`: round 1 NOT FAITHFUL, round 2 NOT FAITHFUL, round 3 FAITHFUL - recorded in spec.md

## Phase 1 - the setting and the module

- [x] T02 `l7r/diagram/switches.py`: dataclasses, `read` (absent -> defaults, malformed -> closed), `write`, `check`, CLI `show|set|check`; registered in `_invocation.OPERATIONS`
- [x] T03 `tests/test_switches.py` at 100% on the module

## Phase 2 - the Makefile

- [x] T04 targets `ci-off`, `ci-on`, `scope-lock`, `scope-unlock`, `switches` (REASON required, file committed by the target)
- [x] T05 `SWEEP_OK` first in `cohort`, `tripwire`, `test-full`; conditional in `done`/`ci-check`/`ci-merge` (FULL), `ci-check` (TARGET), `maps` (SCOPE=all); `REMOTE_OK` first in `ci-check`, `ci-image`; `audit` shows switches
- [x] T06 fixture test proving each Makefile refusal fires under the lock / remote off and that `reference`, `quick`, `done` are untouched

## Phase 3 - the dispatcher and the ritual

- [x] T07 `decision.decide` gains `remote_off`; verdict table; tests
- [x] T08 `ci/__main__.py`: remote off -> no client constructed; check/image refuse; merge -> LOCAL-GATED verdict; `--route` prints GATED-LOCAL; tests
- [x] T09 `sync-with-main.sh`: GATED-LOCAL route name and line; `scripts/test-sync-with-main.sh` case

## Phase 4 - the Python sweeps

- [x] T10 `mapcheck`: lock -> reference only, no widening, `--scope all` refused; tests
- [x] T11 `cohort_audit`: lock refused first; tests
- [x] T11b `pipeline.regen` (more than one gen refused), `cache_audit`, `make_regressions` refuse under the lock; `SWEEP_OK` on `cache-audit`/`regressions`; tests
- [x] T11c `sync-with-main.sh` seams honored only in a tree with no diagram skill Makefile; test case

## Phase 5 - guards and records

- [x] T12 `guard-file-hooks.sh` pattern + test case for `dev/switches.json`
- [x] T13 `dev/switches.md` (the why, the fail-closed rule, the single-map decision with priced alternatives), ci `CLAUDE.md` sixth condition, root `CLAUDE.md` enforcement row + ladder note, `dev/loop.md`
- [x] T14 prove-it-fires (2026-08-25, each deletion restored with `git checkout`): removing `$(SWEEP_OK)` from `cohort` -> `tests/test_switches.py::test_make_sweeps_refuse_under_the_lock[cohort]` RED; dropping the `elif remote_off` branch in `decision.py` -> `test_remote_off_never_dispatches` + `test_remote_off_does_not_short_circuit_a_full_scope_on_a_reference_record` RED; dropping the lock check in `cohort_audit.main` -> `tests/tools/test_scope_lock.py::test_cohort_refuses_first` RED; honoring `CI_ROUTE` in every tree again -> `scripts/test-sync-with-main.sh` 7c RED (3 checks)
- [x] T15 `make hooks-test` green (14 suites); `make done` green twice (301 s pre-amendment, 304 s on the amended code), then `already verified` in 1.2 s on the docs-only tail - the amendment proven on its own feature; bypass-log audit: no entries added by this feature

## Phase 5b - the amendment (GM 2026-08-25: `make done` short-circuits like the remote gate)

- [x] T18 amendment recorded verbatim in gm-request.md; FR-019..FR-023; fidelity round 1 CHANGES REQUIRED (four, applied), round 2 pending at the time of writing
- [x] T19 `delta.is_gate` / `gate_key_worktree` (a RULE: every .py under the skill, tests, pool data, Makefile, pyproject, lockfiles, scripts/); `state.gate_key` + `already_verified`; `ci verified-done`; the `done` recipe's one-shell short-circuit; no FORCE
- [x] T20 tests: is_gate kinds incl. `.explain.py`/`wip/*.gen.py`; key moves with the Makefile not docs; `already_verified` table; stamp containment against gate-stamp's own file lists; CLI; the real Makefile short-circuits in a fixture and FULL never does
- [x] T21 records: dev/switches.md section, skill CLAUDE.md `make done` row, root CLAUDE.md docs-only bullet

## Phase 6 - throw the switches for feature 133

- [x] T16 `make ci-off` and `make scope-lock` thrown on the GM's instruction of 2026-08-25 (the two commits before this feature's landing)
- [x] T17 stop-work ritual: `sync-with-main.sh done` lands 132 through the new GATED-LOCAL route (remote already off) on the local-done rule
