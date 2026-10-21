# T14, the second one-claim experiment, analyzed

The GM, 2026-10-21: *"Yes please do one more claim task and the analyze how long it took afterwards so we can evaluate what
tooling or process improvements, if any, we need to make."* T14 (385 T128): `ways/sweeps.py::_sweep_dangling_ends` popped a
whole vertex at a time where it should walk an end in; the sibling of T12. The first claim landed with `make land` (T33).

## What happened (measured 2026-10-21 from the session's timestamps, the commits, the agents' durations and the run logs)

| UTC | what | cost |
|---|---|---|
| 03:17:44-03:23:05 | `make task-start`, the code read beside T12's fix, the plan section | 5.3 min |
| 03:23:05-03:24:15 | `make decide` refused an unlabeled figure (as on T12), relabeled; the plan review (43 s) CLEAR - in parallel with the fix | 1 refusal, ~1 min |
| 03:22-03:26:50 | the fix (a 4 ft walk, D8; the way the lane left not counted, D9) and four existing tests that asserted the old pops reworked, branch coverage kept; the ways suite green | ~5 min |
| 03:27:06-03:28:33 | `make cohort`, 16/16 | 1.5 min |
| 03:27:20-03:29:00 | the hourly step-back blocked the first claims dispatch: `make step-back`, the arbiter (88 s), a part B owed | ~2.5 min |
| 03:29-03:33:50 | `make done` started early to overlap the claims round; the claims round's own record writes were refused while it ran (gate-write guard), and the claims edits moved the engine under it - killed, its 5 min of machine time wasted | 0 wall, 5 min CPU |
| 03:27:06-03:38:28 | **the claims round: two triages (12 s, 14 s), three impl-drift rounds (45 s, 70 s, 38 s), the session writing claims between them** | **11.4 min** |
| 03:38:44 | `make land` pass 1 refused in 5 s: three impl-drift passes had no ledger row (their prompts named no feature, so `make ledger-owed WRITE=specs/405-...` would not write them) | 1 refusal, ~1 min |
| 03:39:36-03:45:20 | `make land`: preflight (108 s, clean), `make done` FULL (a test script changed since the last green gate) - RED on the 100% floor: `sweeps.py:738` uncovered | 5.7 min |
| 03:45:20-03:45:56 | the line read, a unit test for it (a restored lane whose head reaches), committed | ~1 min |
| 03:45:56-03:57:13 | `make land` again, unattended: preflight 116 s, `make done` FULL green (to 03:51:02), `make cohort-landing` (to 03:55:00, no seed regressed against main), the push, the tick, the ticks' own push (2.2 min for the two pushes) | 11.3 min |

**Start to landed: 39.5 min** (03:17:44-03:57:13). T12 was 35 min (5 fix, 5 review, 4 claims, 15 landing, the rest spec review
and refusals).

| | T12 | T14 |
|---|---|---|
| plan and its review | ~5 (the spec's first review too) | 6.5 (one refusal) |
| the fix and its tests | ~5 | ~5 (overlapped with the plan review) |
| the claims round | ~4 | **11.4** (three impl-drift rounds) |
| the step-back and part B | ~4 (met in the landing) | ~2.5 (met in the claims round) |
| session round trips at the landing | 7 | 2 (the ledger rows; the red floor) |
| the landing, machine time | ~11 (gate, cohort, a foreground render-sync) | 17 (a FULL gate twice, the cohort) |

## Where the time went, against T12

1. **The landing itself is fixed.** One command, one 5-second refusal, then unattended. T12's landing was seven round trips
   and 15 min.
2. **The claims round tripled (4 -> 11.4 min) and is now the largest session cost.** Three impl-drift rounds:
   - round 1: 1 IN-STEP, 2 MISLABELED, 3 UNCLAIMED - two of them on my own new code (a claim saying the page is silent where
     it is not; a new helper `_walk_in` that inherited the module's `NONE` claim), the rest on code T14 did not change;
   - round 2: 7 IN-STEP, 1 DRIFTED, 2 UNCLAIMED - all three on code T14 did not change (the dooryard carry's fallback, the
     restore-whole rule, the grove band), surfaced because the change touched the unit;
   - round 3: 3 IN-STEP.
   **The claims gate counts a finding on a changed UNIT as introduced**, so five decisions that were unclaimed before T14 had to
   be claimed for T14 to land. The GM's standing rule (2026-10-19) is the other way round: *"findings on code a task didn't
   change"* become new tasks. Each round is a session round trip of ~3 min (write claims, bundle, dispatch, record).
3. **The gate cannot overlap the claims round.** Any claim edit is an edit to an engine docstring, which moves the tree under a
   running gate (its tree check voids it), and the claims round's record writes are refused while it runs. So the 5-8 min of
   gate and cohort wait strictly for the claims to settle.
4. **The step-back came due after ~17 minutes of work.** Its clock (`scripts/reviews/checkpoint.py`) counts a wait on the GM
   from a Stop to his next prompt, but a background agent finishing after the turn ended (a `SubagentStop` at 14:14 and 15:05)
   resets the wait; the 12 overnight hours then count as idle gaps, each charged its first 20 minutes as work. ~3 min with
   part B.
5. **Small refusals, ~1 min each:** `make decide`'s unlabeled figure (the second time, same sentence shape); the untraced
   ledger rows.
6. **The preflight passed a line the gate's floor then failed.** Its coverage step asks only the lines the delta CHANGED; line
   738 (`continue` in the dooryard carry) was unchanged, but D9 moved the case that reached it and I reworked the one test
   that had reached it. So the gap surfaced 5.7 min later at the full floor, and the whole gate ran twice.
7. **A guard read a mention as an invocation**: the gate-write guard refused a heredoc writing this draft to the scratchpad
   because its text said "the push, the tick" after "make land". Seconds, but the project's rule is that such a refusal is a
   guard bug.
8. **The full gate was a one-off:** the last green `make done` was T12's; T34 changed `tests/hooks/test-sync-with-main.sh`
   since, which forces FULL. The next claim's gate is incremental again.

## What would make a claim ~15 minutes

| change | saves | kind |
|---|---|---|
| A. The claims gate refuses only findings on the LINES the delta changed; a finding elsewhere in a changed unit is filed as a task of the feature (`make claims-carry`, which exists for page edits) and the push goes ahead | rounds 2+ of the claims round: ~6 min on T14 | tooling (claims gate + impl-drift's bundle carries the hunks) |
| B. `make claims-owed` names a new function whose claim is the inherited module `NONE` before any agent runs | one round on T14 | tooling (a lint) |
| C. The step-back's GM-wait survives a background agent finishing after the turn ended | ~3 min, once per resumed session | tooling bug fix (`checkpoint.gm_waits`) |
| D. A pass dispatched on a claims bundle is traced to the active task's feature for its ledger row | ~1 min, every claims round | tooling (`ledger_owed.belongs`) |
| F. The preflight's coverage step judges every quick-uncovered line of a changed FUNCTION (not only the changed lines), so a test edit that drops an unchanged line's only coverage is caught in the preflight | one whole gate run on T14: ~6 min | tooling (`preflight.coverage_step`) |
| G. The gate-write guard matches the command, not words inside a heredoc's text | a refusal now and then | guard bug |
| E. The gate's tree check and the gate-write guard ignore what the gate does not read (docstring-only engine edits by the stamp's token rule; `dev/claims-index.json`, `specs/`) | lets the gate run beside the claims round: 5-8 min of wall | tooling (riskier: the gate's own correctness) |

With A-D and F the T14 run would have been about 6 plan + 5 fix + ~4 claims + 1 land action, then the unattended landing
(an incremental gate, the cohort, the push, ~9 min): **~16 min of session time and ~25 min to landed**, against 39.5. With E
as well the gate overlaps the claims round, ~20 min.

Not proposed: the plan section (6.5 min) and the fix are the work itself; the cohort (1.5 min) overlapped the step-back; the
two pushes (2.2 min) are each the push's own checks.
