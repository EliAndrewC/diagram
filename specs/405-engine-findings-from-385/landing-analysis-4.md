# T19, the fourth one-claim experiment, measured - the first with the step-back suspended and the red-gate hold fixed

The GM, 2026-10-21 (amendment 4): *"let's suspend but not remove the hourly step-back arbitur for now.  Then let's fix the
"second red gate" tripwire so that it fires properly when it should fire.  Then you can do 1 more claims task and measure how
long it takes."* T43 (the switch), T44 (the gate asks `gate-held` itself) and T46 (found landing T43: `make land` writes a stale
make-targets page) landed at 10:34:36 in one `make land` of 1 min 40 s. T44's hold refused live on T11's unruled
`red-gate@2026-10-21T05:02:38Z` until the round arbiter ruled it (accept).

T19 (385 T135): impl-drift found `law.fouls_fabric`'s `own` exemption dropping a household's own garden. A grep found no caller
at all - its one reader was its own test, and the live rule is `settle.fouled_segment` - so the fix is its removal.

## What happened (measured 2026-10-21 from the commands' timestamps and the run records)

| UTC | what | cost |
|---|---|---|
| 10:34:50 | `make task-start` (the checkpoint reads `suspended: true`) | - |
| 10:34:50-10:35:29 | the plan section (the code read happened while T43's landing ran, about 2 min, not counted) | 0.7 min |
| 10:35:29-10:35:50 | `make decide` refused once: an unlabeled "7 ft" in item 4; reworded | 0.3 min |
| 10:35:50-10:36:41 | the plan review (45 s, CLEAR) and the removal, in parallel; test file, ruff, format green; committed | 0.9 min |
| 10:36:41-10:41:39 | `make done` in the background, green (174 s); meanwhile the claims round: **no claim owed** (a deleted unit leaves none), the claims gate clean | 5 min, unattended |
| 10:42:01-10:48:58 | `make land`: the landing cohort (to 10:46:24, fresh block 7 of 48, 15%), the push, the tick, its push | 7 min, unattended |

**Start to landed: 14.1 minutes** (10:34:50-10:48:58), against T11's 37, T14's 39.5 and T12's 35, and under the ~17 that
`landing-analysis-3.md` said a clean claim should take. **Session work: about 2 minutes.** The rest was the gate (5) and the
landing (7), both unattended. No defect was found; no refusal took more than a reword.

## The caveat

T19 was an easier claim than T11: a deletion, so no claims round to run (T11's took 2.3 min beside the gate) and no map changed.
A claim that changes code and owes a claims round should still fit in about the same time, since the round runs beside the gate.

## What the fixes did here

| fix | on T19 |
|---|---|
| T43 - step-back suspended | **worked**: the checkpoint read `suspended`; nothing held the tick or the gate. T14 and T12 each paid 2.5-4 min to it |
| T44 - the red-gate hold | **worked before T19 started**: it refused the unruled 05:02 trigger live; T19's gate was green, so it had nothing to hold |
| T46 - the page written at landing | **worked on T43's landing** (its own): the second `make land` regenerated the page in its first pass |
| E - the gate beside the claims round | not needed: no claim was owed |
| `make land` | one command, unattended, first try |

## What is left, and what I would do next

- **The landing is now the largest part: 7 of 14 minutes**, 4.4 of them the landing cohort, which `make land` starts only after
  the gate. Starting `make cohort-landing` beside `make done` (two background runs, as the claims round now runs beside the gate)
  would bring a claim like this to about 10 minutes. Not filed: the GM decides whether the next step is this or the next claim.
- **The fresh-block failure rate**: 15% (7 of 48) here, against 12% (T14) and 17% (T11). A rate, not a refusal; no trend yet.
- **T45** (filed from the arbiter's ruling): the reference-settlement message still offers `GATE_NO_CACHE=1`, which the roll
  census refuses.
