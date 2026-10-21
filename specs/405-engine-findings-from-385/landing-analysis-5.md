# T13, the fifth one-claim experiment, measured - the first with the gate and the landing cohort side by side

The GM, 2026-10-21 (amendment 5): *"make the make done and the make landing run in parallel.  Then do 1 more claims task and
measure how long it takes."* T48 landed at 11:27:28 (`make land` starts `make cohort-landing` beside `make done`). T47, the
preflight's coverage step, is filed at low priority as the GM asked.

T13 (385 T127): `settle.settle_street_ends` cut a dangling street end back to other lanes' ends only, so a farm the street served
without a door path, past the last such end, was cut off its street. The web's own trim already counted each served farm's
point (`street_anchors`) as a joint; the settle now does too. Unlike T19, a code change with a claims round.

## What happened (measured 2026-10-21 from the commands' timestamps, the run record and the cohort's log)

| UTC | what | cost |
|---|---|---|
| 11:28:48 | `make task-start` | - |
| 11:28:48-11:29:58 | code read (`settle_street_ends`, `street_anchors`, `end_to_its_joint`, the trim's call), plan section, `make decide` | 1.2 min |
| 11:29:58-11:31:00 | plan review (47 s, CLEAR) beside the fix and its unit test; the file at 1,001 lines, a docstring folded to 1,000; committed | 1.0 min |
| 11:31:00-11:32:29 | the claims round: one claim owed, no triage owed, impl-drift 21 s IN-STEP in one round, recorded; its one note outside the change filed (T49) | 1.5 min |
| 11:32:29-11:37:45 | `make land`: **the gate and the landing cohort side by side** - the cohort (`JOBS=11`, MemAvailable 9,066 MB) done at 11:37:38, its record committed beside the gate; the gate green at 11:37:45 (preflight 121 s, the run 175 s) | 5.3 min, unattended |
| 11:37:45-11:40:03 | the push, the tick, its push | 2.3 min, unattended |

**Start to landed: 11.3 minutes**, against T19's 14.1 (a deletion with no claims round), T11's 37, T14's 39.5 and T12's 35.
**Session work: 3.7 minutes**, the claims round included. **The landing: 7.6 minutes** unattended, against T19's 12 (its gate and
its landing's cohort in turn).

## The parallel run, measured

| | T19 (in turn) | T13 (side by side) |
|---|---|---|
| the gate's preflight | 111 s | 121 s |
| the gate's run | 174 s | 175 s |
| the landing cohort | 4.4 min alone (20 workers) | ~5.2 min beside the gate (11 workers) |
| gate and cohort, wall | ~9.4 min | **5.3 min** |
| load at the gate's start/end | 4.4 / 4.8 | 8.3 / 7.2 |

The gate barely slowed (preflight +10 s); the cohort, on 11 workers beside it, took about 0.8 min longer than alone - and both
finished within seven seconds of each other, so the landing now waits for one, not both. MemAvailable stayed above 8 GB at the
gate's end. The tree check read the cohort's record, committed seven seconds before the gate ended, as unseen (D21), as designed.

## What is left, and what I would do next

- **The claims round runs before the landing now, not beside the gate.** `make land` refuses while a claim is owed, so the gate
  (and with it the cohort) starts only once the round is recorded: 1.5 minutes here, in series. Letting `make land` start the
  gate and the cohort first and ask the claims gate before the push would fold that in, about 1.5 minutes on a claim with a round.
- **The push and its tick take 2.3 minutes**: two `sync-with-main.sh done` runs (the landing, then the tick's own push), each
  re-asking the claims gate and the push checks. One push carrying the tick would save about a minute.
- **The fresh-block rate**: 15% again (7 of 48), against 15% (T19), 17% (T11), 12% (T14). A rate, not a refusal.
- **T47** (low priority) and **T49** (filed from this round: a street end that crosses a way mid-run) are open.
