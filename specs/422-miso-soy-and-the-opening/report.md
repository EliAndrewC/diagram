# Feature report - 422-miso-soy-and-the-opening

Written by `make feature-report F=422` from 2721 events (2026-10-25T20:11 to 2026-10-25T21:38 UTC), 30 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 h 56 min | 65% |
| other tool | 31 min | 18% |
| waiting: source-reader | 10 min | 6% |
| waiting: source-applicability | 5 min | 3% |
| test file | 4 min | 2% |
| waiting: quote-check | 3 min | 2% |
| waiting: translation-check | 2 min | 1% |
| waiting: subagent | 2 min | 1% |
| waiting: record-format | 2 min | 1% |
| waiting: intro-check | 1 min | 0% |
| waiting: round-arbiter | 1 min | 0% |
| edit | 0 min | 0% |
| writing the spec | 0 min | 0% |
| quick test | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| waiting: research-pass | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |

The session's own time above; its 684 subagent tool call(s) (of 1226) are counted apart (0 by the subagent transcripts, 684 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 91 run(s), 2 h 14 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 10 min |
| make record | 5 min |
| make reserve | 2 min |
| make check-bundle | 2 min |
| make apply-edits | 2 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 34 | clean 4, findings 30 |
| source-applicability | 17 | findings 17 |
| record-format | 12 | clean 1, findings 11 |
| quote-check | 8 | findings 8 |
| spec-fidelity | 6 | BLOCKED 1, CLEAR 2, FAITHFUL 1 |
| translation-check | 6 | FAITHFUL 5 |
| research-pass | 5 | findings 5 |
| intro-check | 3 | clean 1, findings 2 |
| round-arbiter | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| translation-check | q-0303 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 3 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 80 over 742 changed lines: cascade ratio 0.11
- tasks ticked: 2 of 5

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (742 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity-verify | 2 | 5 min | 529k | 13.3k | 0.003 | 0.7k |
| spec-fidelity | 4 | 8 min | 474k | 27.3k | 0.005 | 0.6k |

This report took 1.9 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
