# Feature report - 394-seed-regressions-refuse-a-landing

Written by `make feature-report F=394` from 48 events (2026-10-19T04:29 to 2026-10-19T11:36 UTC), 1 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 6 h 48 min | - |
| thinking | 7 min | 36% |
| waiting: subagent | 6 min | 33% |
| other tool | 4 min | 21% |
| waiting: the GM | 2 min | 10% |

The session's own time above; its 0 subagent tool call(s) (of 21) are counted apart (0 by the subagent transcripts, 0 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 0 run(s), 0 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 1 min |
| make gm-review | 0 min |
| make gm-reviewed | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 0 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 0

## Tripwires (FR-010) - what fired, or would have

- none

This report took 1.0 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
