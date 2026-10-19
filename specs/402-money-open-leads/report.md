# Feature report - 402-money-open-leads

Written by `make feature-report F=402` from 2133 events (2026-10-19T17:53 to 2026-10-19T19:46 UTC), 22 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 h 18 min | 60% |
| idle (over an hour) | 1 h 15 min | - |
| other tool | 26 min | 21% |
| waiting: quote-check | 7 min | 5% |
| waiting: source-reader | 5 min | 4% |
| waiting: source-applicability | 3 min | 2% |
| edit | 2 min | 2% |
| waiting: subagent | 2 min | 1% |
| waiting: translation-check | 1 min | 1% |
| waiting: record-format | 1 min | 1% |
| waiting: round-arbiter | 1 min | 1% |
| writing the spec | 1 min | 1% |
| waiting: intro-check | 0 min | 0% |
| dispatching: record check | 0 min | 0% |
| test file | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| quick test | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 555 subagent tool call(s) (of 974) are counted apart (0 by the subagent transcripts, 555 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 63 run(s), 2 h 12 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 9 min |
| make check-bundle | 3 min |
| make quote-verbatim | 3 min |
| make record | 3 min |
| make apply-edits | 2 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 19 | clean 2, findings 13 |
| translation-check | 13 | FAITHFUL 10 |
| record-format | 11 | findings 11 |
| quote-check | 8 | findings 7 |
| source-applicability | 8 | findings 8 |
| spec-fidelity | 4 | BLOCKED 1, CHANGES REQUIRED 2, CLEAR 1 |
| round-arbiter | 3 | FAITHFUL 1, findings 2 |
| intro-check | 2 | findings 2 |
| research-pass | 2 | - |
| spec-fidelity-verify | 1 | CHANGES REQUIRED 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| translation-check | q-0276 | 4 |
| quote-check | q-0276 | 3 |
| record-format | q-0273 | 3 |
| record-format | q-0275 | 3 |
| record-format | q-0276 | 3 |
| source-reader | key-hirai-2007-myoshinji-yokushitsu-whole | 3 |
| source-reader | key-ruiju-kinsei-fuzokushi-jo-whole | 3 |
| source-reader | key-shomonya-saiko-10-2-salt-whole | 3 |
| translation-check | q-0273 | 3 |
| translation-check | q-0275 | 3 |
| translation-check | q-0277 | 3 |
| quote-check | q-0273 | 2 |
| quote-check | q-0275 | 2 |
| record-format | q-0277 | 2 |
| source-applicability | key-hirai-2007-myoshinji-yokushitsu | 2 |
| source-applicability | key-oishi-1966-tenpo13-bukka-kakiage | 2 |
| source-applicability | key-shomonya-saiko-10-2-salt | 2 |
| source-reader | key-ehime-kenshi-joka-shokunin-whole | 2 |
| source-reader | key-kawakami-1992-shrine-headman-whole | 2 |
| source-reader | key-kitano-2026-osaka-day-labor-whole | 2 |
| source-reader | key-oishi-1966-tenpo13-bukka-kakiage-whole | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 2 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 61 over 356 changed lines: cascade ratio 0.17
- tasks ticked: 6 of 8

## Tripwires (FR-010) - what fired, or would have

- 19:38 round:record-format|q-0273@3
- 19:38 round:record-format|q-0275@3
- 19:38 round:record-format|q-0276@3
- 19:38 round:translation-check|q-0273@3
- 19:38 round:translation-check|q-0276@3

## What each check cost, per changed line (356 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 7 | 17 min | 2928k | 61.4k | 0.020 | 8.2k |
| source-reader | 15 | 19 min | 1919k | 85.4k | 0.042 | 5.4k |
| spec-fidelity | 4 | 13 min | 1423k | 42.5k | 0.011 | 4.0k |
| record-format | 11 | 9 min | 1297k | 48.4k | 0.031 | 3.6k |
| source-applicability | 8 | 14 min | 1109k | 35.6k | 0.022 | 3.1k |
| translation-check | 10 | 4 min | 339k | 20.9k | 0.028 | 1.0k |
| spec-fidelity-verify | 1 | 2 min | 175k | 6.3k | 0.003 | 0.5k |
| intro-check | 2 | 1 min | 39k | 4.3k | 0.006 | 0.1k |

This report took 2.5 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
