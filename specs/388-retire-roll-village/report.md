# Feature report - 388-retire-roll-village

Written by `make feature-report F=388` from 786 events (2026-10-18T19:59 to 2026-10-18T21:30 UTC), 17 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 38 min | 42% |
| waiting: a background run | 33 min | 36% |
| other tool | 14 min | 15% |
| waiting: subagent | 3 min | 3% |
| quick test | 1 min | 2% |
| edit | 0 min | 0% |
| test file | 0 min | 0% |
| writing the spec | 0 min | 0% |
| waiting: impl-drift | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| gate | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 102 subagent tool call(s) (of 348) are counted apart (0 by the subagent transcripts, 102 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 18 run(s), 25 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 8 min |
| make format | 2 min |
| make docs | 1 min |
| make arbiter-fix-done | 1 min |
| make perf | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 11 | BLOCKED 1, CHANGES REQUIRED 3, CLEAR 4, FAITHFUL 2 |
| impl-drift | 4 | findings 2 |
| round-arbiter | 1 | FAITHFUL 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: red 5
- spec rounds: none recorded
- plan reviews BLOCKED: 1 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 4 over 1294 changed lines: cascade ratio 0.00
- tasks ticked: 3 of 4

## Tripwires (FR-010) - what fired, or would have

- 20:36 red-gate
- 20:46 red-gate
- 20:55 red-gate
- 21:00 red-gate

## What each check cost, per changed line (1294 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 10 | 17 min | 1532k | 57.0k | 0.008 | 1.2k |
| impl-drift | 2 | 3 min | 314k | 9.3k | 0.002 | 0.2k |
| spec-fidelity-verify | 1 | 1 min | 87k | 4.1k | 0.001 | 0.1k |

This report took 0.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).

## For the GM

- **Deleted**: `roll_village` (the feature-005 knob engine) and what only it reached - the water-source anchor, the shared
  edge seat, the undeckable-lanes pass, the roller's band pitch - with their tests, the failing village soak test among them.
  Nothing is carried to 380 or 384.
- **Amendment 1 (the GM: "the frozen maps do not need to stay runnable")**: the four helpers the first landing kept for
  the frozen exhibits went too - `build_comb`, `crop_to_content`, `cremation_ground`, `headman`. Their tests of live code now
  call what the scripted hamlet calls (`carve_comb` + `finish_comb`; `content_view` + `crop_to_view`); the surface censuses no
  longer count the legacy pool as a consumer. 18 exhibit scripts no longer run; none was edited.
- **Found by the moved claims, carried to 384**: no jizo at a burial ground's entrance (0238), and canal A's deliveries leave it
  at ~33-51 deg where 0053 has right angles. Both predate 388.
- **Exhibits no longer run**: Honda, Shimizu and Kikuta (drawn with `roll_village`) and, after amendment 1, every exhibit
  calling one of the four helpers; their maps, renders and pages are untouched. They are frozen and never regenerated.
- **Maps**: no live map changed (`make maps` all cached); the landing cohort passed 54/54.
- **Found on the way and fixed**: the gate's carried tooling coverage kept rows for a deleted file and failed its report
  (`ci/incremental.py`); a red run whose coverage report errored recorded no cause; `make dead-closure` added (what a deletion
  leaves dead, what it breaks, and which test pins a deleted path).
