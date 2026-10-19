# Feature report - 401-knives-and-copper-rate

Written by `make feature-report F=401` from 1534 events (2026-10-19T13:13 to 2026-10-19T17:31 UTC), 18 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 4 h 16 min | - |
| thinking | 49 min | 53% |
| other tool | 17 min | 19% |
| waiting: quote-check | 8 min | 9% |
| waiting: source-applicability | 6 min | 7% |
| waiting: source-reader | 4 min | 5% |
| waiting: round-arbiter | 2 min | 2% |
| edit | 2 min | 2% |
| waiting: translation-check | 1 min | 1% |
| writing the spec | 1 min | 1% |
| waiting: intro-check | 1 min | 1% |
| test file | 1 min | 1% |
| waiting: record-format | 1 min | 1% |
| dispatching: record check | 0 min | 0% |
| waiting: a background run | 0 min | 0% |

The session's own time above; its 318 subagent tool call(s) (of 719) are counted apart (0 by the subagent transcripts, 318 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 62 run(s), 1 h 13 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 7 min |
| make glossary | 2 min |
| make record | 2 min |
| make apply-edits | 1 min |
| make check-bundle | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 21 | clean 1, findings 19 |
| source-applicability | 19 | clean 2, findings 16 |
| translation-check | 7 | FAITHFUL 7 |
| quote-check | 6 | findings 5 |
| record-format | 6 | findings 6 |
| intro-check | 4 | clean 2, findings 2 |
| round-arbiter | 2 | findings 2 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| source-applicability | key-takekoshi-1935-keizaishi-9 | 2 |
| source-reader | key-rieb-kinsei-db-data-whole | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 63 over 577 changed lines: cascade ratio 0.11
- tasks ticked: 4 of 6

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (577 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 5 | 11 min | 2408k | 41.5k | 0.009 | 4.2k |
| source-applicability | 18 | 26 min | 1987k | 80.2k | 0.031 | 3.4k |
| source-reader | 20 | 17 min | 1841k | 81.9k | 0.035 | 3.2k |
| record-format | 6 | 6 min | 586k | 28.5k | 0.010 | 1.0k |
| translation-check | 7 | 5 min | 311k | 30.4k | 0.012 | 0.5k |
| intro-check | 4 | 1 min | 102k | 5.6k | 0.007 | 0.2k |

This report took 1.9 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
