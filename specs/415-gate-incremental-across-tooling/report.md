# Feature report - 415-gate-incremental-across-tooling

Written by `make feature-report F=415` from 969 events (2026-10-24T16:45 to 2026-10-26T16:29 UTC), 38 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 2 h 37 min | - |
| other tool | 2 h 04 min | 51% |
| thinking | 1 h 32 min | 38% |
| waiting: a background run | 13 min | 5% |
| test file | 5 min | 2% |
| waiting: subagent | 4 min | 2% |
| edit | 1 min | 1% |
| writing the spec | 1 min | 0% |
| waiting: spec-fidelity-verify | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| gate | 0 min | 0% |
| quick test | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 81 subagent tool call(s) (of 420) are counted apart (0 by the subagent transcripts, 81 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 20 run(s), 38 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 1 h 17 min |
| make ledger-owed | 13 min |
| make cohort | 9 min |
| make cover-changed | 6 min |
| make land-tooling | 5 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 16 | BLOCKED 1, CHANGES REQUIRED 1, CLEAR 9 |
| impl-drift | 2 | findings 2 |
| round-arbiter | 2 | findings 2 |
| claims-triage | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| spec-fidelity | plan-405-engine-findings-from-385-T106 | 4 |
| impl-drift | claims-owed | 2 |

## Process signals

- gates: green 2, red 4
- spec rounds: none recorded
- plan reviews BLOCKED: 6 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 2 over 1329 changed lines: cascade ratio 0.00
- tasks ticked: 7 of 9

## Tripwires (FR-010) - what fired, or would have

- 19:05 red-gate
- 19:17 red-gate

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T06 | 0 min | 0 min | 0 min | 0 | 0 |
| T08 | 2 min | 2 min | 1 min | 1 | 2, 1 |
| T07 | 0 min (open) | 0 min | 0 min | 0 | 0 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T06 | 16:26-16:26 | the tick or the last event | 3 | 0 | 0 | 0 | - |
| T08 | 16:26-16:28 | spec-fidelity CLEAR | 8 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T08 | 16:28-16:29 | the tick or the last event | 3 | 1 | 0 | 0 | - |
| T07 | 16:29-16:29 | the tick or the last event | 0 | 0 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T06 | 16:26 | started (`make task-start`) | |
| T06 | 16:26 | ticked | |
| T08 | 16:26 | started (`make task-start`) | |
| T08 | 16:28 | spec-fidelity returned CLEAR (1 min) | |
| T08 | 16:29 | ticked | |
| T07 | 16:29 | started (`make task-start`) | |

## What each check cost, per changed line (1329 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 1 | 1 min | 81k | 4.0k | 0.001 | 0.1k |

This report took 1.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).

## The close (T07, 2026-10-26)

- **SC-006 measured** (`research.md` R3): 417 T04's landing on 2026-10-25, the first that met D9, took 5.1 minutes end to end
  against R1's 8.8: an incremental gate of 2,023 tests (224 s) in place of the full 10,376.
- **T08** was answered by feature 430 T02's planner, a non-module file below `tests/<dir>/` selecting its readers; this
  feature adds the test that pins the hook-suite case (`test_a_hook_suite_keeps_the_gate_incremental`).
- **Left open, by D12**: 39 of the 45 gate runs between 2026-10-25 and 2026-10-26 15:03Z still planned full. 430 answers the 23
  for manifests, docs and hook suites. A top-level `conftest.py` and an import-time line still plan full by design. Whether
  the gate now stays incremental is for the next landings' run records to show (`make gate-costs`).
