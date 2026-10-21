# 405-engine-findings-from-385 - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-20 -->
## T30 - a plan bundle for a feature with no request.md is refused, naming the file (found working T12)

### T30 Approach (checklist part A)

1. **The goal, in the world.** A plan review never runs on a bundle without the GM's words; the session learns at build time, with the fix.
2. **The constraints.** Feature 383 amendment 8: a plan review reads the request verbatim (`request.md`) beside the blocks. The GM's rule: a tool, never a reminder; tips live in error output. A test red without it.
3. **Where each comes from.** 383 (O); the GM (G).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (T12: `make decide F=405 T=T12` built a bundle whose MANIFEST named `request.md`, absent; the spec-fidelity pass returned no verdict, 63 s).
5. **The order.** The refusal in `plan_bundle.build` before anything is written; the test.
6. **The exits.** (c) - refuse at build time; building the request from the spec's quote was weighed and refused (the spec's quote may be trimmed).
7. **The search smell.** None.
8. **The budget.** 10 min.
9. **Done, measured.** One goal: `make decide` / `make plan-delta` on a feature with no `request.md` exit non-zero naming `specs/<feature>/request.md` and what goes in it; `tests/tooling/` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T30 Decisions

**D2 - no request, no bundle.** `plan_bundle.build` raises `SystemExit` before creating the bundle when `spec_dir/request.md` is missing: "plan bundle: specs/<name>/request.md is missing - write the GM's words there verbatim (the request and every amendment, as the spec's 'The request' quotes them), commit it, and build again".

<!-- plan-archive: archived 2026-10-20 -->
## T31 - task-add numbers a task from the boxes' own ids (found working T12)

### T31 Approach (checklist part A)

1. **The goal, in the world.** `make task-add` gives a new task the next id of the feature's own tasks, whatever the titles quote.
2. **The constraints.** Feature 385 T64 (D83): the next free id, zero-padded as the feature's ids are. A test red without it.
3. **Where each comes from.** 385 (O).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (405's titles quote "(385 T147)"; `next_id` read every `T<n>` in tasks.md and plan.md and gave T148-T154 where T28-T35 were next).
5. **The order.** `next_id` reads the ids of the boxes and of the plan's `## T<n>` headings only; the test.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 10 min.
9. **Done, measured.** One goal: on a tasks.md whose last box is T31 and whose titles name T147, `next_id` returns T32; `tests/tooling/` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T31 Decisions

**D3 - the boxes' ids.** `task-add.next_id` takes the largest id of `^- \[[ x]\] T<n>` boxes in tasks.md and `^## T<n>` headings in plan.md and plan-done.md, plus one.

<!-- plan-archive: archived 2026-10-20 -->
## T33 - `make land`: one command, every cheap refusal first (landing-analysis.md)

### T33 Approach (checklist part A)

1. **The goal, in the world.** Once a task's checks are recorded, one command lands it: what the landing will refuse is known in seconds and all at once, and the long runs start without the session.
2. **The constraints.** The gated route's conditions: a green gate on this content (`gate-stamp.py --check`), the landing cohort on this engine (`cohort_gate.py check`), the claims gate, the review gate, owed ledger rows, a clean tree; each task's tick refusals (385 T117's `land-batch`). The GM, 2026-10-20: "the landing being the biggest cost is something that we need to do something about". A test red without it.
3. **Where each comes from.** The gates (O); the GM (G).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (T12: six refusals one at a time, `make done` and `make cohort-landing` started by hand after their refusals; the checks themselves 7.5 s, 2.0 s, 0.3 s and 0.02 s).
5. **The order.** `scripts/land.py` from `land-batch.py`; `make land` and `make land-batch` both call it; the tests.
6. **The exits.** (c) - one command; running the gate and the cohort in parallel was weighed and left to a measurement of its own (the memory cap, feature 315).
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** One goal: `make land F= T="<one or more>" NOTE=` prints every cheap refusal together and stops; otherwise runs `make done` when the gate stamp does not cover the content and `make cohort-landing` when the cohort gate would refuse, commits the files the gate regenerated under `pool/`, pushes with `L7R_LAND_TICKS` set and ticks each task; `tests/tooling/` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T33 Decisions

**D5 - one landing command.** `scripts/land.py <feature> "<ids>"` (NOTE from `LAND_NOTE`), one task or more. Pass 1, nothing run: each task's tick refusals but the landed one, uncommitted work, owed ledger rows (`ledger_owed`), the claims gate, the review gate, the holding rule with `L7R_LAND_TICKS` - every failure printed, then exit 2. Pass 2: `gate-stamp.py --check origin/main`; when it refuses, `make done`; when the cohort gate's `check` refuses on an engine delta, `make cohort-landing`; changes the runs leave under `pool/` committed as "regenerated by the landing's gate"; then `sync-with-main.sh done` with `L7R_LAND_TICKS`; then each tick, noted "landed: <note>" (or "landed in batch T1+T2: <note>"). `land-batch.py` keeps its name as a shim to `land.py`.

<!-- plan-archive: archived 2026-10-20 -->
## T34 - the push asks its cheap questions first (landing-analysis.md)

### T34 Approach (checklist part A)

1. **The goal, in the world.** A plain `sync-with-main.sh done` that will refuse on the holding rule or undeclared occasions says so in seconds, before its slower checks.
2. **The constraints.** The push's checks and their messages unchanged; only their order. A test red without it.
3. **Where each comes from.** The push (O).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (`push_cmd` runs `push_checks.py` and the claims gate, then the fetch, then the holding rule, then `review-gate.sh`).
5. **The order.** The holding rule and `review-gate.sh` moved ahead of `push_checks.py`, the holding rule judged against the fetched main as now; the test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: a push held by an open active task, or with undeclared occasions, refuses before `push_checks.py` runs; `tests/hooks/test-sync-with-main.sh` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T34 Decisions

**D6 - cheap first.** In `push_cmd`, the fetch, the delta (`ours`), the holding rule and `review-gate.sh` run before `push_checks.py` and `claims-gate.sh`; nothing else moves.

<!-- plan-archive: archived 2026-10-20 -->
## T35 - render-sync after a landing runs in the background (landing-analysis.md)

### T35 Approach (checklist part A)

1. **The goal, in the world.** A landing returns once its work is on main; main's renders refresh behind it.
2. **The constraints.** The GM browses renders in main (2026-08-12: a stale render cost a round trip), so render-sync still runs after every landing; `render_sync_background` already exists for the prompt hook. A test red without it.
3. **Where each comes from.** The GM (G); the push (O).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (T12's push: 2.5 min, most of it render-sync regenerating four magistracy maps other sessions had changed).
5. **The order.** `done` calls `render_sync_background`; its message says where the render's log is; the test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: `sync-with-main.sh done` returns after the push with render-sync started in the background (its lock and log as the prompt hook's); `tests/hooks/test-sync-with-main.sh` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T35 Decisions

**D7 - the render behind the landing.** `sync-with-main.sh done` runs `push_cmd` then `render_sync_background`, printing where the render's progress is logged; `render-sync` itself stays foreground for a hand run.
<!-- plan-archive: archived 2026-10-21 -->
## T36 - the claims gate refuses only what the change made (A)

### T36 Approach (checklist part A)

1. **The goal, in the world.** A task that touches a function lands once its own claims are right; a finding on that function's older code is filed as a task of the feature, as the GM's found-work rule asks, instead of refusing the landing.
2. **The constraints.** The GM, 2026-10-19: "we should keep findings on code a task didn't change as new tasks in 385" (carried to 405 as its FR-002). The claims gate's FR-010 (a finding the delta introduced refuses). 385 FR-013's carry (`claims_carry`), which already files a page edit's findings on unchanged code. impl-drift judges; the gate only counts.
3. **Where each comes from.** The found-work rule: G. FR-010 and FR-013: O (features 316, 385).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T14's claims round, `landing-analysis-2.md`): three findings on code T14 never changed (the dooryard carry's fallback, the restore-whole rule, the grove band) were refused as introduced because the unit's code changed, and cost a third impl-drift round.
5. **The order.** The bundle marks changed lines; the MANIFEST says when to tag; the reply parser and the index keep the tag; `classify` carries a tagged finding whose claim is unchanged from the base (or an UNCLAIMED one); `make land` runs the carry in its first pass; tests for each.
6. **The exits.** (c) - the agent says which findings rest on the change, because only it reads what a finding rests on; a mechanical rule by claim text was weighed and refused (a code change can make an unchanged claim false, which is the gate's whole job).
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: a reply whose DRIFTED and UNCLAIMED findings on an unchanged claim carry `[outside the change]` leaves the claims gate with carried findings, not introduced ones, and `make land` files them as one open task; an untagged one, or a tagged one on a claim the delta reworded, is still introduced (tests).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T36 Decisions

**D10 - the agent tags, the gate carries.** `claims.bundle` shows each unit's source with the lines the delta changed (against the merge base with origin/main) marked `+`, and the MANIFEST asks that a non-IN-STEP verdict or UNCLAIMED line resting on no marked line, and not on a claim the delta added or reworded, begin its note `[outside the change]`. `record` keeps `outside: true` on the row. `classify` carries such a row when it is UNCLAIMED or its claim text matches the merge base's row; otherwise it is classified as before. `land.py`'s first pass runs `claims.py carry --feature <n>` before the claims gate and commits what it files.

<!-- plan-archive: archived 2026-10-21 -->
## T37 - a new unit with only the inherited NONE is named first (B)

### T37 Approach (checklist part A)

1. **The goal, in the world.** A new helper that decides something about the place gets its own claim before the first check, so the check does not spend a round saying so.
2. **The constraints.** Feature 316's claims grammar: a unit with no `Research:` line inherits its module's; a `NONE` claim says the unit decides nothing physical.
3. **Where each comes from.** O (feature 316).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T14's first impl-drift round): `_walk_in`, new, inherited `lane sweep plumbing - NONE` and was judged MISLABELED with two UNCLAIMED decisions.
5. **The order.** The notice in `claims.py owed` (and the bundle command), a test.
6. **The exits.** (b) - a notice, not a refusal: a new helper may truly be plumbing, and a refusal on correct work teaches bypassing.
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: `make claims-owed` on a delta adding a function whose only claim is inherited `NONE` prints a line naming it and what to write (a test).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T37 Decisions

**D11 - named, not refused.** `claims.py owed` (behind `make claims-owed` and `make claims-bundle OWED=1`) prints, for each owed key whose status is `new`, whose unit is `inherited` and whose claim is `NONE`: "<uid> is new and carries only its module's NONE - if it decides anything about the place, give it its own `Research:` line before the check".

<!-- plan-archive: archived 2026-10-21 -->
## T38 - the step-back clock keeps the wait on the GM (C)

### T38 Approach (checklist part A)

1. **The goal, in the world.** The hourly step-back comes due after an hour of the session's work, never because the session waited overnight for the GM.
2. **The constraints.** 383's hour (`CHECKPOINT_S`); 385's GM-wait rule (a Stop to the GM's next prompt is not the session's time); 397's idle rule.
3. **Where each comes from.** O (features 383, 385, 397).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (a read of 405's event log, rows 662-671): after the Stop at 14:11Z two `SubagentStop` events (14:14Z, 15:05Z) reset the GM wait, so the 12 hours to the GM's prompt counted as idle gaps, each charged its first 20 min, and the hour came due after about 17 minutes of work.
5. **The order.** `gm_waits` and `idle` hold a Stop through `SubagentStop`; a test built on that event sequence, red before.
6. **The exits.** (e) conform - the rule already says a wait on the GM is not the session's time.
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: the event sequence Stop, SubagentStop, SubagentStop, the GM's prompt counts as one GM wait and no idle gap, and the hour does not come due on it (a test red at HEAD).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T38 Decisions

**D12 - only the session's own act ends a wait.** In `checkpoint.gm_waits` a `SubagentStop` no longer clears an open Stop (a `PreToolUse` or a non-GM prompt still does); in `checkpoint.idle` a gap after a Stop stays the wait's through `SubagentStop`, so the same span is never counted as both.

<!-- plan-archive: archived 2026-10-21 -->
## T39 - a claims-bundle pass is traced to the active task's feature (D)

### T39 Approach (checklist part A)

1. **The goal, in the world.** A claims round's agent passes get their ledger rows from the landing's own write, with no prompt wording needed.
2. **The constraints.** 371's ledger rows (every pass has one); 395's rule that a feature's write takes only passes traced to it.
3. **Where each comes from.** O (features 371, 395).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T14's landing): `make land` refused once on three impl-drift passes whose prompts named only `/tmp/l7r-check/claims-owed/`, which `belongs` could not trace to 405.
5. **The order.** `belongs` traces a subject naming a claims bundle (`claims-owed`, `claims-triage`) to the clone's active task's feature; a test.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: with 405's task active, a pass whose subject names `/tmp/l7r-check/claims-owed/MANIFEST.md` belongs to 405 and not to another feature (a test red at HEAD).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T39 Decisions

**D13 - the active task owns the claims bundles.** `ledger_owed.belongs(p, num, ...)` is also true when the subject names `l7r-check/claims-owed` or `l7r-check/claims-triage` and the repository's active task (`plan_gate.active_task`) is feature `num`'s.

<!-- plan-archive: archived 2026-10-21 -->
## T40 - the preflight judges a changed function's every line (F)

### T40 Approach (checklist part A)

1. **The goal, in the world.** A coverage gap the gate's 100% floor will refuse is found in the preflight's two minutes, not after the gate's five.
2. **The constraints.** The 100% floor (feature 174); the preflight's coverage step (375 FR-004), which today asks only the changed lines and, on the hamlet path, defers to the gate's rolls.
3. **Where each comes from.** O (features 174, 375).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T14's first landing and the gate baseline's `coverage.db`): `sweeps.py:738`, unchanged, lost its only unit test when T14 reworked it; the preflight passed, the gate failed 5.7 min in, and the baseline shows only `test_sweeps.py` tests ever reached that line, no roll.
5. **The order.** `changed_lines` widened to each changed function's span; for an on-path gap, the line mapped to the baseline's copy of the file (its blob in the baseline manifest) and the baseline's contexts read: reached there only by tests the quick tier runs (or by none) - the preflight refuses it; tests.
6. **The exits.** (c) - the baseline is the last green gate's evidence of what the rolls reach; a line the delta changed has no baseline line and keeps today's rule (the gate judges).
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: a fixture where an unchanged line inside a changed function is uncovered by the quick run and reached at the baseline only by a quick-tier test makes the preflight refuse it; the same line reached at the baseline by a gate-tier test is only printed (tests).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T40 Decisions

**D14 - a changed function, and the baseline's word on the rest.** `preflight.changed_lines` returns, for each changed engine file, the changed lines plus every line of each function or method enclosing one (by `ast` spans). In `coverage_step`, an on-path gap whose line maps (`difflib`, equal blocks) to a line of the baseline's copy of the file is refused when the baseline's `coverage.db` holds no context for that line from a test outside the quick run (a test id under `tests/gate`, `tests/full`, `tests/tier_*`, `tests/tooling`, a test the quick run did not run, or a fixture context); with no baseline, today's rule.

