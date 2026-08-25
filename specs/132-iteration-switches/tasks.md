# Tasks: The Iteration Switches (132)

Checked off only when verified. `make done` (reference scope) is the gate; `make hooks-test` for the
shell guards.

## Phase 0 - review

- [ ] T01 `spec-fidelity` round 1 verdict recorded in spec.md (FAITHFUL required before T03+)

## Phase 1 - the setting and the module

- [ ] T02 `l7r/diagram/switches.py`: dataclasses, `read` (absent -> defaults, malformed -> closed), `write`, `check`, CLI `show|set|check`; registered in `_invocation.OPERATIONS`
- [ ] T03 `tests/test_switches.py` at 100% on the module

## Phase 2 - the Makefile

- [ ] T04 targets `ci-off`, `ci-on`, `scope-lock`, `scope-unlock`, `switches` (REASON required, file committed by the target)
- [ ] T05 `SWEEP_OK` first in `cohort`, `tripwire`, `test-full`; conditional in `done`/`ci-check`/`ci-merge` (FULL), `ci-check` (TARGET), `maps` (SCOPE=all); `REMOTE_OK` first in `ci-check`, `ci-image`; `audit` shows switches
- [ ] T06 fixture test proving each Makefile refusal fires under the lock / remote off and that `reference`, `quick`, `done` are untouched

## Phase 3 - the dispatcher and the ritual

- [ ] T07 `decision.decide` gains `remote_off`; verdict table; tests
- [ ] T08 `ci/__main__.py`: remote off -> no client constructed; check/image refuse; merge -> LOCAL-GATED verdict; `--route` prints GATED-LOCAL; tests
- [ ] T09 `sync-with-main.sh`: GATED-LOCAL route name and line; `scripts/test-sync-with-main.sh` case

## Phase 4 - the Python sweeps

- [ ] T10 `mapcheck`: lock -> reference only, no widening, `--scope all` refused; tests
- [ ] T11 `cohort_audit`: lock refused first; tests

## Phase 5 - guards and records

- [ ] T12 `guard-file-hooks.sh` pattern + test case for `dev/switches.json`
- [ ] T13 `dev/switches.md` (the why, the fail-closed rule, the single-map decision with priced alternatives), ci `CLAUDE.md` sixth condition, root `CLAUDE.md` enforcement row + ladder note, `dev/loop.md`
- [ ] T14 prove-it-fires: delete each refusal in turn, watch a test go red (record which test here)
- [ ] T15 `make hooks-test` green; `make done` green; bypass-log audit for the feature (none expected)

## Phase 6 - throw the switches for feature 133

- [ ] T16 `make ci-off REASON=...` and `make scope-lock REASON=...` on the GM's instruction of 2026-08-25, committed
- [ ] T17 stop-work ritual: `sync-with-main.sh done` lands 132 (gated route, local-done rule)
