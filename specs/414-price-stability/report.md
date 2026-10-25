# Feature report - 414-price-stability

Written by `make feature-report F=414` from 3671 events (2026-10-24T16:37 to 2026-10-25T00:51 UTC), 35 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 h 37 min | 62% |
| other tool | 43 min | 28% |
| waiting: source-reader | 4 min | 3% |
| waiting: round-arbiter | 3 min | 2% |
| writing the spec | 2 min | 1% |
| waiting: quote-check | 2 min | 1% |
| edit | 1 min | 1% |
| waiting: record-format | 1 min | 1% |
| dispatching: record check | 1 min | 1% |
| waiting: subagent | 1 min | 0% |
| dispatching: spec review | 0 min | 0% |
| waiting: translation-check | 0 min | 0% |
| test file | 0 min | 0% |
| waiting: intro-check | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 982 subagent tool call(s) (of 1699) are counted apart (0 by the subagent transcripts, 982 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 91 run(s), 3 h 36 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 32 min |
| make record | 5 min |
| make land-tooling | 3 min |
| make apply-edits | 2 min |
| make reserve | 2 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 74 | clean 1, findings 45 |
| record-format | 10 | findings 10 |
| spec-fidelity-verify | 10 | CHANGES REQUIRED 5, FAITHFUL 1 |
| quote-check | 8 | findings 8 |
| source-applicability | 7 | findings 7 |
| translation-check | 7 | FAITHFUL 7 |
| research-pass | 3 | findings 3 |
| intro-check | 2 | clean 1, findings 1 |
| round-arbiter | 2 | FAITHFUL 1, findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| source-reader | s414-sr-allen-2009-china-wages | 3 |
| source-reader | s414-sr-iwahashi-1981-gpih-rice-prices | 3 |
| source-reader | s414r2-sr-rieb | 3 |
| source-reader | s414r2-sr-shinbo | 3 |
| source-applicability | s414-sa6 | 2 |
| source-reader | s414-sr-allen-2010-gpih-beijing-prices | 2 |
| source-reader | s414-sr-bassino-2006-gpih-mitsui | 2 |
| source-reader | s414-sr-coin-walk-edo-kahei-nenpyo | 2 |
| source-reader | s414-sr-gao-shouxian-jiuqing-wuliao | 2 |
| source-reader | s414-sr-jawiki-sanka-seido | 2 |
| source-reader | s414-sr-keller-shiue-wang-appendix | 2 |
| source-reader | s414-sr-liu-2005-gpih-china-rice-prices | 2 |
| source-reader | s414-sr-lu-peng-2004-rice-prices | 2 |
| source-reader | s414-sr-mingshi-80-chafa | 2 |
| source-reader | s414-sr-qian-yong-lvyuan-conghua | 2 |
| source-reader | s414-sr-qingshigao-123-yanfa | 2 |
| source-reader | s414-sr-quan-1957-silver-price-revolution | 2 |
| source-reader | s414-sr-rieb-kinsei-db-data | 2 |
| source-reader | s414-sr-saito-1993-bakumatsu-wages | 2 |
| source-reader | s414-sr-saito-2003-wages | 2 |
| source-reader | s414-sr-shinbo-1975-bakumatsu-prices | 2 |
| source-reader | s414-sr-shiue-2002 | 2 |
| source-reader | s414-sr-shiue-keller-2004-nber-markets | 2 |
| source-reader | s414-sr-washizaki-2012-edo-lot-yields | 2 |
| source-reader | s414-sr-wu-haibo-qing-sishi | 2 |
| source-reader | s414-sr-ye-mengzhu-yueshibian | 2 |

## Process signals

- gates: green 1
- spec rounds: none recorded
- plan reviews BLOCKED: 3 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 108 over 1119 changed lines: cascade ratio 0.10
- tasks ticked: 5 of 8

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (1119 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity-verify | 6 | 15 min | 1340k | 44.2k | 0.005 | 1.2k |
| spec-fidelity | 1 | 6 min | 367k | 13.7k | 0.001 | 0.3k |

This report took 5.1 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
