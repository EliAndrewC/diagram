# Feature report - 430-faster-landings

Written by `make feature-report F=430` from 968 events (2026-10-26T13:45 to 2026-10-26T16:07 UTC), 22 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 h 31 min | 64% |
| waiting: subagent | 16 min | 11% |
| other tool | 15 min | 11% |
| waiting: a background run | 11 min | 8% |
| gate | 4 min | 3% |
| writing the spec | 2 min | 1% |
| test file | 1 min | 1% |
| edit | 1 min | 1% |
| waiting: spec-fidelity-verify | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| spec-kit step | 0 min | 0% |

The session's own time above; its 93 subagent tool call(s) (of 423) are counted apart (0 by the subagent transcripts, 93 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 13 run(s), 45 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 10 min |
| make land-tooling | 1 min |
| make ledger-owed | 1 min |
| make guard-log | 0 min |
| make land | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity-verify | 9 | CHANGES REQUIRED 4, FAITHFUL 2, NOT-REVIEWABLE 1 |
| spec-fidelity | 5 | BLOCKED 2, CHANGES REQUIRED 1, NOT-REVIEWABLE 1 |
| round-arbiter | 2 | findings 2 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 1, green 1, red 1
- spec rounds: none recorded
- plan reviews BLOCKED: 3 recorded in commits, 2 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 1452 changed lines: cascade ratio 0.00
- tasks ticked: 7 of 9

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 22 min | 0 min | 22 min | 0 | 22 |
| T03 | 55 min | 0 min | 55 min | 0 | 55 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 14:43-15:05 | the tick or the last event | 51 | 14 | 8 | 0 | - |
| T03 | 15:06-16:00 | the tick or the last event | 126 | 42 | 13 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 14:43 | started (`make task-start`) | |
| T01 | 15:05 | ticked | |
| T03 | 15:06 | started (`make task-start`) | |
| T03 | 15:35 | `make done` (4 min) | |
| T03 | 16:00 | ticked | |

## What each check cost, per changed line (1452 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity-verify | 7 | 14 min | 1462k | 42.4k | 0.005 | 1.0k |
| spec-fidelity | 4 | 20 min | 646k | 55.4k | 0.003 | 0.4k |

This report took 1.1 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).

## The success criteria, measured (written by the session)

| criterion | result | measurement |
|---|---|---|
| SC-001 (FR-001, FR-002) | MET: 12 of the 19 full-planned runs re-plan incremental; the 4 top-level `conftest.py` runs and the 3 that changed the gate's configuration plan full | `m:plan-replay`, research R5 |
| SC-002 (FR-003) | MET with one priced gap: the check refuses all 3 in-scope reds in 17-37 s where their gates took 255-442 s, and names 14 of the floor's 18 lines (39ea51383's `gencache.py` 238-241 are reached only by tooling tests the gate reuses); 3 lines beyond the floor on d92ff2c90; the sixth red's tooling rule is a unit test | `m:cover-replay`, research R6 |
| SC-003 (FR-004) | MET: each push gate exits in 0.12-0.14 s on a records-only delta (was 5.7, 2.3 and 8.8 s) | `m:push-gates-records-only`, research R7 |
| SC-004 (FR-005, FR-007) | MET: `make plan-delta` writes no bundle while the lint refuses a block; `make decide` refused as before | `tests/tooling/test_plan_lint.py` |
| SC-005 (FR-006) | MET: a known drift on its open task is admitted once `make claims-known` (run by `make land`) records it in gm-review; a triage of 3 or fewer claims goes to impl-drift | `tests/tooling/test_known_drift.py`, `tests/tooling/test_claims_scoping.py` |
| SC-006 (FR-008, FR-009) | MET: every change's tests went red without it (T01, T02, T03, T05 shown red; T04, T06, T07 by construction); the replays above found no delta a full run fails that a shortcut passes, save the stated narrowings | each task's tests, research R4-R7 |

## Found in the work

- **A gate-machinery landing claimed a gate it never ran** (a defect from feature 415's arbiter fix): `make done`'s reuse branch
  ignores `scripts/`, tests and the Makefile by the GM's 2026-08-25 rule, so the `make done` that `land.py` forced always
  short-circuited. The round arbiter ruled process-fault (ask:430-machinery-gate): land now runs the tooling tests and, where
  stale, hooks-test. That missed run had let a regression of T06 reach main (`test_claims_scoping`, fixed and landed).
- **The plan-lint's first figure check refused a decided size** ("the bath 10 x 8 ft") as an unlabeled measurement: a decided
  figure carries its research label, page or knob, which the lint now accepts.
