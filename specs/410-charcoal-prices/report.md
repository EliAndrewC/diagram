# Feature report - 410-charcoal-prices

Written by `make feature-report F=410` from 1342 events (2026-10-22T04:08 to 2026-10-22T05:32 UTC), 21 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 h 41 min | 72% |
| other tool | 16 min | 12% |
| waiting: subagent | 7 min | 5% |
| waiting: quote-check | 6 min | 4% |
| waiting: source-applicability | 4 min | 3% |
| waiting: source-reader | 3 min | 2% |
| writing the spec | 1 min | 1% |
| waiting: record-format | 1 min | 1% |
| edit | 1 min | 0% |
| waiting: translation-check | 1 min | 0% |
| waiting: intro-check | 0 min | 0% |
| dispatching: record check | 0 min | 0% |
| test file | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| quick test | 0 min | 0% |

The session's own time above; its 291 subagent tool call(s) (of 602) are counted apart (0 by the subagent transcripts, 291 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 40 run(s), 1 h 15 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 5 min |
| make record | 3 min |
| make glossary | 1 min |
| make check-bundle | 1 min |
| make quote-verbatim | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 13 | findings 12 |
| source-applicability | 9 | findings 9 |
| quote-check | 5 | findings 3 |
| record-format | 5 | findings 4 |
| spec-fidelity | 4 | CHANGES REQUIRED 1, CLEAR 3 |
| translation-check | 4 | FAITHFUL 3 |
| research-pass | 2 | findings 1 |
| intro-check | 1 | findings 1 |
| round-arbiter | 1 | findings 1 |
| spec-fidelity-verify | 1 | FAITHFUL 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| quote-check | q-0279 | 5 |
| record-format | q-0279 | 5 |
| translation-check | q-0279 | 4 |
| source-reader | key-saito-2022-tama-no-sumi-whole | 3 |
| source-applicability | key-gao-shouxian-jiuqing-wuliao | 2 |
| source-applicability | key-oishi-1966-tenpo13-bukka-kakiage | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 37 over 378 changed lines: cascade ratio 0.10
- tasks ticked: 0 of 5

## Tripwires (FR-010) - what fired, or would have

- 05:23 round:record-format|q-0279@3
- 05:30 round:translation-check|q-0279@3
- 05:30 round:record-format|q-0279@4
- 05:30 round:quote-check|q-0279@3

## What each check cost, per changed line (378 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 3 | 13 min | 1679k | 37.8k | 0.008 | 4.4k |
| source-applicability | 9 | 18 min | 1170k | 43.9k | 0.024 | 3.1k |
| source-reader | 12 | 8 min | 1020k | 43.3k | 0.032 | 2.7k |
| record-format | 4 | 4 min | 586k | 19.3k | 0.011 | 1.6k |
| spec-fidelity | 4 | 7 min | 392k | 24.8k | 0.011 | 1.0k |
| spec-fidelity-verify | 1 | 1 min | 146k | 6.5k | 0.003 | 0.4k |
| translation-check | 3 | 2 min | 137k | 13.1k | 0.008 | 0.4k |
| intro-check | 1 | 0 min | 20k | 1.4k | 0.003 | 0.1k |

This report took 3.2 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
