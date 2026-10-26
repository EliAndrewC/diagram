# Feature report - 432-gm-review-signal

Written by `make feature-report F=432` from 455 events (2026-10-26T17:22 to 2026-10-26T18:28 UTC), 19 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| other tool | 33 min | 50% |
| thinking | 26 min | 39% |
| test file | 3 min | 5% |
| writing the spec | 2 min | 3% |
| edit | 1 min | 1% |
| waiting: a background run | 1 min | 1% |
| waiting: subagent | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| gate | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 49 subagent tool call(s) (of 205) are counted apart (0 by the subagent transcripts, 49 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 7 run(s), 19 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 22 min |
| make gm-review | 6 min |
| make ledger-owed | 6 min |
| make task-start | 0 min |
| make arbiter-ask | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity-verify | 4 | CHANGES REQUIRED 1, FAITHFUL 1 |
| spec-fidelity | 3 | BLOCKED 1, CLEAR 1, findings 1 |
| round-arbiter | 2 | findings 2 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 2 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 680 changed lines: cascade ratio 0.00
- tasks ticked: 5 of 7

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 6 min | 0 min | 6 min | 0 | 6 |
| T06 | 7 min | 0 min | 7 min | 0 | 7 |
| T05 | 18 min | 2 min | 16 min | 1 | 2, 16 |
| T04 | 5 min (open) | 2 min | 3 min | 1 | 2, 3 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 17:45-17:51 | the tick or the last event | 0 | 6 | 0 | 0 | - |
| T06 | 17:54-18:01 | the tick or the last event | 6 | 7 | 0 | 0 | - |
| T05 | 18:04-18:06 | round-arbiter findings | 13 | 2 | 0 | 0 | round-arbiter x1 (1 min) |
| T05 | 18:06-18:23 | the tick or the last event | 25 | 16 | 0 | 0 | - |
| T04 | 18:24-18:25 | round-arbiter findings | 10 | 1 | 1 | 0 | round-arbiter x1 (2 min) |
| T04 | 18:25-18:28 | the tick or the last event | 6 | 3 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 17:45 | started (`make task-start`) | |
| T01 | 17:51 | ticked | |
| T06 | 17:54 | started (`make task-start`) | |
| T06 | 18:01 | ticked | |
| T05 | 18:04 | started (`make task-start`) | |
| T05 | 18:06 | round-arbiter returned findings (1 min) | |
| T05 | 18:23 | ticked | |
| T04 | 18:24 | started (`make task-start`) | |
| T04 | 18:25 | round-arbiter returned findings (2 min) | |

## What each check cost, per changed line (680 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 3 | 14 min | 1339k | 39.2k | 0.004 | 2.0k |
| spec-fidelity-verify | 2 | 2 min | 207k | 12.9k | 0.003 | 0.3k |

This report took 0.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).

## What was asked, and what was built (T07, 2026-10-26)

The GM asked for the GM-review queue to hold only what is his (A-F, `request.md`). The audit read 465 open rows; 443 were not
his, and of the 22 flagged, three were still live and his.

- **A, B, C (T01-T03)**: a ruling reaches the GM only as a `for_gm` question (any trigger) or a declined fix, written owed
  escalation-check; `make gm-escalated` keeps (his decision) or cuts it; a push with an owed question is refused, and a kept
  question must be named in that turn's final message. Every other ruling and fix stays in `arbiter.jsonl`. A ruling whose
  prose hands him a decision without `for_gm` is refused. Found live while building it: the naming check and the
  unfiltered-question check refused each other's message; a kept question is now filtered (landed on its own).
- **D (T01)**: the GM's decisions come from one source, the kept questions; 328's hand-edited override rows no longer list
  themselves (the residence question was dropped by a `held` key the old reader ignored).
- **E (T04, T05)**: claims a page move alone owes are cleared mechanically, the cleared rows recorded - the 0081 edit's triage
  271 claims -> 35; the price, 7 findings in 5,304 re-checks, ruled not material by the round arbiter. The pop-up half was
  measured and not built: its premise was false (R2), waived by the round arbiter.
- **F (T06)**: the 465 rows reviewed with the GM's words; his three carried as kept questions 374#90, 385#107 and 397#11.
- **Texts (T07)**: constitution 2.32.2, the root CLAUDE.md, docs, the agent contracts and messages say the one door.
