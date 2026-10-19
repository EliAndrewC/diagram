# Feature report - 399-record-check-rounds-by-kind-of-edit

Written by `make feature-report F=399` from 253 events (2026-10-19T11:36 to 2026-10-19T12:18 UTC), 7 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 27 min | 65% |
| other tool | 10 min | 23% |
| waiting: the GM | 4 min | 9% |
| quick test | 1 min | 2% |
| test file | 0 min | 1% |
| dispatching: spec review | 0 min | 0% |
| waiting: subagent | 0 min | 0% |
| edit | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| writing the spec | 0 min | 0% |

The session's own time above; its 23 subagent tool call(s) (of 115) are counted apart (0 by the subagent transcripts, 23 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 3 run(s), 11 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 4 min |
| make docs | 3 min |
| make hooks-test | 1 min |
| make ledger-owed | 0 min |
| make plan-delta | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 4 | CHANGES REQUIRED 1, CLEAR 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 447 changed lines: cascade ratio 0.00
- tasks ticked: 2 of 3

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (447 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 2 | 10 min | 826k | 29.6k | 0.004 | 1.8k |
| spec-fidelity-verify | 1 | 1 min | 96k | 5.5k | 0.002 | 0.2k |

This report took 0.7 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).

## For the GM

- **The 去辰 example was wrong.** The session showed 去辰 as a kind-C fix. Measured, it changed the English rendering INSIDE
  the 「」 of the 1700 deed's quotation, so under your rule ("outside the quotation and its claim") that pass stays owed. Of
  0251's last two passes, only the Okayasu locator fix ("the collection's back cover" -> "the back cover of document 102") is
  skipped now.
- **"Few-word" is read as describing the case, not as a limit.** The operative test is "outside the quotation and its claim":
  quote-check judges only the link, the quoted passages and the claim sentences, so a fix of any length outside them gives
  it nothing new to judge. **Settled by the GM, 2026-10-19:** *"I don't think we should have an explicit word limit."*
- **A hand fix is declared.** source-reader words no EDIT blocks, so the Okayasu fix was made by hand. Such a fix is declared
  with `make record-checked CHECK=quote-check Q=<NNNN> NOTES=<k> FIXED_BY="<check>: <its finding>"`; the tool verifies the
  quotation and claim unchanged and refuses, naming the note, when either moved. Another check's EDIT blocks settle the same
  way at `make apply-edits` without a declaration.
- **Kind B counts per footnote.** The per-question round counter restarts whenever main moves or a hand fix of the check's
  own finding goes in; both are kept, since pop-up checks rely on them. The new hold counts each footnote's flags instead, so
  neither resets it.
