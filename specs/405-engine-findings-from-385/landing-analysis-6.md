# T49, the sixth one-claim experiment, measured - the first with the claims round beside the landing, one push, and no coverage step in the gate

The GM, 2026-10-21: *"Now please do one more claims task and measure its timing."* After amendment 6: T50 (the claims round
beside the landing), T51 (one push carrying the ticks) and T47 (the preflight's coverage step out of the gate) landed at 11:56:34.

T49 (found in T13's round): `settle.settle_street_ends` counted only lane END points as joints, so a street crossing a way
mid-run and dangling past it was cut back past the crossing; a crossing is now a joint (0246 §6: a lane runs on to another way).

## What happened (measured 2026-10-21 from the commands' timestamps, the run record and the cohort's log)

| UTC | what | cost |
|---|---|---|
| 11:58:09 | the clock starts: the task chosen (T18 weighed and passed over - it moves a clearance rule, likely maps), `make task-start` | - |
| 11:58:09-11:59:30 | code read, plan section, `make decide`; the plan review (45 s, CLEAR) beside the fix and its test; committed | 1.4 min |
| 11:59:51-12:00:16 | `make land` - **its preflight refused in 25 s**: `settle.py` at 1,009 lines. My one-line edit, over the 200-character line, was re-wrapped to nine lines by the formatter after I had counted 1,000 | 1 refusal |
| 12:00:16-12:01:46 | the line folded into two, a blank docstring line taken out (1,000), committed, `make land` started again | 1.5 min |
| 12:01:46-12:05:14 | **the gate** (preflight 13 s - was 111-121 s; the run 177 s) and **the landing cohort** (12 workers, to 12:05:47) side by side | 4 min, unattended |
| 12:01:50-12:03:17 | **the claims round beside them**: bundle, impl-drift 24 s IN-STEP in one round, recorded and committed at 12:02:53; its ledger row written by hand at 12:03:17 (a gap, fixed as T52) | 1.5 min, overlapped |
| 12:05:47-12:06:17 | the claims wait already satisfied; the tick and **one push** | 0.5 min |

**Start to landed: 8.1 minutes** (11:58:09-12:06:17), against T13's 11.3, T19's 14.1, and 35-39.5 for the first three. Without
my file-size slip (about 1.5 minutes) it would have been about 6.5. **Session work: about 3 minutes**, the task's choice included.

## The three fixes, measured

| fix | T13 (before) | T49 (after) |
|---|---|---|
| T47 - the coverage step out of the gate | preflight 121 s | **13 s** |
| T50 - the claims round beside the landing | 1.5 min in series before `make land` | **overlapped** with the gate |
| T51 - one push | the push, the tick, its push: 2.3 min | the tick and one push: **0.5 min** |
| the landing, `make land` to pushed | 7.6 min | **4.5 min** |

The gate (177 s) and the cohort (4.0 min, 12 workers) still ran side by side; the cohort is now the longer of the two by about
30 s. The fresh block failed 4 of 48 (8%), against 15% on the last two.

## What is left

- **T52** (filed and fixed now): `make land` wrote the ledger rows only in its first pass, so the claims round's pass beside the
  gate owed a row at the push; it writes them again after the claims wait.
- **A long line re-wrapped past the file bar** cost 1.5 minutes here, and a 1,002-line file cost T11 one. Both times the file
  stood at the bar before the edit. Not filed: two minutes in six runs.
- **The landing cohort** is now the landing's longest step (4 min). Its fixed seeds come from the roll cache only where nothing
  they execute changed, so an edit to a hamlet-path module re-rolls all 102.
