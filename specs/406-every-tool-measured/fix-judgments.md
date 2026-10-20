# The 22 fixes judged (feature 406 T07, D166)

**What was asked.** The GM, 2026-10-19, of the 22 tooling fixes that `make fix-yield F=385` read as "saves nothing": "Whether or
not it's doing something for us should be a measurable question, right? And in cases where a tool is too new to have gathered
measurements, then that's fine". The 22 are the rows of the hour-37 step-back's `fix-yield.md`, the table the GM's count came
from (today's old reading has 21: `hour:385-approach-checklist@20` now reads "saving" on the same command rate, which shows
how much that rate moved with the work).

**How each is judged (D166).** Each fix is read by its tools - the guards, checks, targets, reviews and registered steps of the
commit that made it - and what they did since it was made (`make fix-yield F=385`, built on `make tool-yield`). It takes the
first reading that holds: too new to say (made under 7 days ago); doing something (a tool with interventions net of its
misfires); no outcome record; record too new; doing nothing.

**The judgment: all 22 are too new to say.** Every one was made between 2026-10-17 and 2026-10-19, so none has the 7 days the
spec asks before a fix can read "doing nothing". The first ones become readable on 2026-10-24 and the last on 2026-10-26: run
`make fix-yield F=385` then, and each row will take one of the other four readings from the same numbers below. None should be
retired before that on this evidence.

**What the numbers already show, without judging.**
- The old command rate measured several fixes by their own use. `make verify` (fix 4) rose from 0.03 to 0.19 minutes an hour
  because the fix made `make verify-wait`, which sessions then used 10 times. `make arbiter-bundle` (fixes 2 and 11) rose
  because the bundle was used more, not because the fix failed. That is the weakness the GM named.
- Most fixes' tools have uses but no interventions yet. For a target, an intervention is a failed run seen by a session. So a
  fix that makes a bundle better (fixes 3, 6, 7, 10, 17) can only show up as fewer check rounds, which nothing here counts per
  fix. Those will most likely read "no outcome record" or "doing nothing" on 2026-10-25, and that reading should be weighed as
  the record's limit, not the fix's.
- Fix 1 (a roll child's full traceback kept in a file) changed only engine code (`rollcache.py`), which is no tool's. It has
  no tool to read, and will read "no outcome record" when it is old enough.
- Fix 19's tools include the `make-only` guard: 23 firings since 2026-10-19, of which 9 refused and 14 were escaped. Escapes
  are this report's likely misfires, so that guard is worth a look of its own whatever fix 19 is judged.

**The record's limits for this list.** A fix's tools come from its commit's files. A helper named by many recipes (the
`scripts/record/claims*.py` family) maps to every target that names it, so fixes 3, 6, 10, 17, 20 and 21 list ten claims
targets each. Where no commit names the trigger, the files and `make` targets the settling note names stand in for it.

## The 22

### 1. `hour:385-approach-checklist@2`

- **The fix:** make cohort: when a roll's child process raises, write its full traceback to a file named in the cohort log and print that path, instead of a truncated one-line RuntimeError message.
- **Made:** 2026-10-17; readable from 2026-10-24.
- **The old reading (hour 37):** `make cohort\b` at 3.6/h before against 4.11/h after, over 34.5 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): none found
- **Judgment: too new to say.**

### 2. `red-gate@2026-10-17T17:21:08Z`

- **The fix:** `make arbiter-bundle` for a red-gate trigger should list each counted gate's failing tests from that gate's own run record, not from pytest's cumulative .pytest_cache lastfailed (which carries stale zz_probe and other-unit entries), and `make done` should refuse to start while any tests/**/test_zz_probe*.py file exists.
- **Made:** 2026-10-17; readable from 2026-10-24.
- **The old reading (hour 37):** `make arbiter-bundle` at 0.0/h before against 0.05/h after, over 35.8 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): check `preflight`: no outcome record; guard `gate-write` 5/5/0; target `arbiter-ask` 10/0/0; target `arbiter-bundle` 42/0/0; target `done` 42/14/0; target `preflight` 0/0/0
- **Judgment: too new to say.**

### 3. `ask:t01-claim-labels`

- **The fix:** The claims-owed bundler (make claims-owed / the claims triage) must clear, not re-owe, a claim whose only change since the last impl-drift round is the label or citation that round itself prescribed, with a test showing a prescribed-relabel-only diff owes nothing.
- **Made:** 2026-10-17; readable from 2026-10-24.
- **The old reading (hour 37):** `agent:impl-drift` at 0.67/h before against 1.99/h after, over 35.1 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): target `claims-backfill`: no outcome record; target `claims-backfill-sections` 1/0/0; target `claims-bundle` 41/0/0; target `claims-carry` 8/0/0; target `claims-checked` 48/1/0; target `claims-coverage` 0/0/0; target `claims-owed` 44/0/0; target `claims-report` 1/0/0; target `claims-triage` 10/0/0; target `claims-triaged` 13/1/0
- **Judgment: too new to say.**

### 4. `hour:385-approach-checklist@3`

- **The fix:** make verify should start its gate as a run the harness tracks (so finished-run sees it and the normal gate wait applies) and write each run's verdict to its own log or expose a make verify-wait target, instead of appending a detached run to .git/verify-gate.log where a wait matches an earlier run's verdict line.
- **Made:** 2026-10-17; readable from 2026-10-24.
- **The old reading (hour 37):** `make verify\b` at 0.03/h before against 0.19/h after, over 35.0 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): check `one-gate`: no outcome record; check `verify_wait`: no outcome record; target `verify` 5/0/0; target `verify-wait` 10/0/0
- **Judgment: too new to say.**

### 5. `hour:385-approach-checklist@4`

- **The fix:** `make step-back`/`make tick`'s hourly clock (feature 383) stops counting the time between a turn that ends awaiting the GM and the GM's next message, so an hour spent mostly waiting on the GM does not open a step-back; its test is a transcript with a 30-minute GM wait inside a 63-minute window, which must not fire.
- **Made:** 2026-10-17; readable from 2026-10-24.
- **The old reading (hour 37):** `agent:round-arbiter` at 1.5/h before against 1.64/h after, over 33.6 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): guard `event-log`: no outcome record; guard `pair` 300/186/4; target `feature-report` 22/1/0; target `step-back` 61/0/0
- **Judgment: too new to say.**

### 6. `ask:t03-claims-at-landing`

- **The fix:** The claims-check bundle builder (scripts/record/check_bundle.py) adds the bodies of the functions a claimed function calls (here link_survives for _clear_link), so a claims check is never left CANNOT-TELL because a callee is missing.
- **Made:** 2026-10-17; readable from 2026-10-24.
- **The old reading (hour 37):** `agent:impl-drift` at 1.17/h before against 2.2/h after, over 30.4 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): target `claims-backfill`: no outcome record; target `claims-backfill-sections` 1/0/0; target `claims-bundle` 41/0/0; target `claims-carry` 8/0/0; target `claims-checked` 48/1/0; target `claims-coverage` 0/0/0; target `claims-owed` 41/0/0; target `claims-report` 1/0/0; target `claims-triage` 8/0/0; target `claims-triaged` 13/1/0
- **Judgment: too new to say.**

### 7. `ask:t14-plan-round4`

- **The fix:** In scripts/reviews/arbiter_bundle.py, make the `_ROUTES` pool-roll demand fire only when the question names a map change (a map, seed, feature or a changed path under l7r/diagram/), not on the bare word 'route' in its process sense, and have an ask: about a plan or spec review carry that review's rounds (verdicts, findings marked NEW/REPEATED/REVERSING) and the plan diffs, as a round: bundle does, each with a test red without it.
- **Made:** 2026-10-18; readable from 2026-10-25.
- **The old reading (hour 37):** `make cohort\b` at 2.46/h before against 4.34/h after, over 29.3 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): target `arbiter-ask` 7/0/0; target `arbiter-bundle` 41/0/0
- **Judgment: too new to say.**

### 8. `hour:385-approach-checklist@9`

- **The fix:** The round tripwire's spec-fidelity counter (the hook behind make arbiter-bundle's round: triggers) counts a plan review's rounds per task's plan blocks (e.g. T14) and trips round: at the cap CLAUDE.md states, so a plan round past the cap is refused by the guard rather than held back by the session remembering the rule.
- **Made:** 2026-10-18; readable from 2026-10-25.
- **The old reading (hour 37):** `agent:spec-fidelity` at 7.0/h before against 7.29/h after, over 28.8 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): check `approach_gate`: no outcome record; guard `review-round` 336/42/1; target `cohort` 19/0/0
- **Judgment: too new to say.**

### 9. `ask:t05-lane-popup-round3`

- **The fix:** The modal-depiction re-owe guard (the hook that marks a pop-up tab as owing another round after an edit) should treat an edit whose diff matches, line for line, the verbatim EDIT the last round's finding supplied as settling that finding, and should not re-owe a round for it.
- **Made:** 2026-10-18; readable from 2026-10-25.
- **The old reading (hour 37):** `agent:modal-depiction` at 0.83/h before against 1.82/h after, over 27.4 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): guard `check-bundle` 1387/84/22; target `apply-edits` 85/2/0; target `record-checked` 102/0/37; target `record-owed` 164/4/0
- **Judgment: too new to say.**

### 10. `ask:t05-old-drifts-at-landing`

- **The fix:** The impl-drift bundle builder inlines a judged unit's direct callees and every module-level constant they read (transitively one level) whenever a claim's label names a distance, gap or standoff, so a standoff claim is judged in one round instead of asking for its call chain a round at a time.
- **Made:** 2026-10-18; readable from 2026-10-25.
- **The old reading (hour 37):** `agent:impl-drift` at 1.83/h before against 2.29/h after, over 25.7 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): target `claims-backfill`: no outcome record; target `claims-backfill-sections` 1/0/0; target `claims-bundle` 35/0/0; target `claims-carry` 4/0/0; target `claims-checked` 48/1/0; target `claims-coverage` 0/0/0; target `claims-owed` 38/0/0; target `claims-report` 1/0/0; target `claims-triage` 6/0/0; target `claims-triaged` 12/1/0; target `verify` 3/0/0
- **Judgment: too new to say.**

### 11. `red-gate@2026-10-18T12:27:25Z`

- **The fix:** Change the red-gate bundle (make arbiter-bundle, red-gate kind) so it lists each counted red's failed tests and uncovered lines, taken from that gate's log, instead of '? test(s) failed'. The 2026-10-17T22:34 and 2026-10-18T10:10 reds reach the arbiter with no cause, so the arbiter cannot tell whether an earlier cause came back.
- **Made:** 2026-10-18; readable from 2026-10-25.
- **The old reading (hour 37):** `make arbiter-bundle` at 0.01/h before against 0.06/h after, over 23.3 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): target `test`: no outcome record
- **Judgment: too new to say.**

### 12. `red-gate@2026-10-18T12:36:36Z`

- **The fix:** The prompt hook's clone-sync must check a gate-in-progress lock that make done writes on start and removes on exit, and while the lock is held it must postpone the merge of origin/main to the next turn, never merge, so that nothing writes to a tree while its gate runs; its test drives a sync while the lock is held and asserts HEAD and the working tree are unchanged.
- **Made:** 2026-10-18; readable from 2026-10-25.
- **The old reading (hour 37):** `make done\b` at 0.11/h before against 2.08/h after, over 23.3 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): check `gate_lock`: no outcome record; check `land-tooling`: no outcome record; guard `clone-sync` 15/0/0; target `arbiter-fix-done` 34/0/0; target `done` 20/8/0; target `hooks-test` 21/0/0; target `land-tooling` 26/0/0
- **Judgment: too new to say.**

### 13. `red-gate@2026-10-18T16:44:54Z`

- **The fix:** The red-gate counter behind make done / make arbiter-bundle should not count a 'tree moved' abort (test-full never ran, as at 16:45:47Z) as a red make done, and the red-gate bundle should carry the diff between each pair of counted reds, so the arbiter can see what changed between them without the session's own account in the repository.
- **Made:** 2026-10-18; readable from 2026-10-25.
- **The old reading (hour 37):** `make done\b` at 0.24/h before against 2.45/h after, over 19.4 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): target `arbiter-ask` 5/0/0; target `arbiter-bundle` 27/0/0; target `done` 14/5/0
- **Judgment: too new to say.**

### 14. `red-gate@2026-10-18T16:45:47Z`

- **The fix:** The red-gate counter behind make done / make arbiter-bundle should not count a 'tree moved' abort (test-full never ran) as a red make done; with that change this trigger would not have fired.
- **Made:** 2026-10-18; readable from 2026-10-25.
- **The old reading (hour 37):** `make done\b` at 0.24/h before against 2.45/h after, over 19.4 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): target `arbiter-ask` 5/0/0; target `arbiter-bundle` 27/0/0; target `done` 14/5/0
- **Judgment: too new to say.**

### 15. `hour:385-approach-checklist@18`

- **The fix:** The approach gate (make plan-delta and the tick's part-B check) refuses a '### Tnn part B (<stamp>)' heading whose stamp is later than the current UTC clock, with a test that a future-stamped part B is refused and a present one passes.
- **Made:** 2026-10-18; readable from 2026-10-25.
- **The old reading (hour 37):** `agent:spec-fidelity` at 5.0/h before against 7.7/h after, over 19.6 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): check `approach_gate`: no outcome record; check `plan_gate`: no outcome record; guard `check-bundle` 1270/78/22; guard `pair` 220/160/0; target `decide` 29/0/0; target `plan-archive` 1/0/0; target `plan-delta` 18/1/0; target `plan-verdict` 10/0/0; target `section-sha` 0/0/0; target `task-start` 70/4/0
- **Judgment: too new to say.**

### 16. `hour:385-approach-checklist@20`

- **The fix:** The green-gate guard and scripts/sync-with-main.sh done's landing-cohort requirement should count a changed .py file as engine work only when its AST, with docstrings and comments stripped, differs from HEAD's, so a comment- or docstring-only change (whose claims the claims gate already covers) owes neither a full make done nor make cohort-landing.
- **Made:** 2026-10-18; readable from 2026-10-25.
- **The old reading (hour 37):** `make (done\|cohort-landing)\b` at 3.55/h before against 3.78/h after, over 17.7 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): check `gate-stamp` 2/0/-; guard `pair` 209/157/0; target `done` 11/5/0; target `hooks-test` 17/0/0; target `page-check` 8/0/0
- **Judgment: too new to say.**

### 17. `ask:t10-findings-at-landing`

- **The fix:** When a claimed constant's value or derivation changes (here DIKEPOND_WATER_INSET going from a fixed 23 ft to a value derived per map by dikepond_inset), the claims check in scripts/record/claims.py should flag every research drawing page that still states the old figure for that unit, so stale pages like 0022/0024/0025 are caught at the edit rather than at landing.
- **Made:** 2026-10-18; readable from 2026-10-25.
- **The old reading (hour 37):** `agent:impl-drift` at 2.0/h before against 2.48/h after, over 14.9 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): target `claims-backfill`: no outcome record; target `claims-backfill-sections` 1/0/0; target `claims-bundle` 15/0/0; target `claims-carry` 1/0/0; target `claims-checked` 34/0/0; target `claims-coverage` 0/0/0; target `claims-owed` 15/0/0; target `claims-report` 0/0/0; target `claims-triage` 3/0/0; target `claims-triaged` 9/1/0
- **Judgment: too new to say.**

### 18. `hour:385-approach-checklist@25`

- **The fix:** `make tick` refuses a task whose NOTE says 'landed' while any file in that task's last `make land-tooling` FILES still differs from origin/main, or while that landing's log ends in a failure, naming the file and the log.
- **Made:** 2026-10-19; readable from 2026-10-26.
- **The old reading (hour 37):** `make land-tooling\|sync-with-main\.sh done` at 3.59/h before against 6.26/h after, over 12.5 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): target `tick` 61/1/0
- **Judgment: too new to say.**

### 19. `hour:385-approach-checklist@27`

- **The fix:** make land-tooling should run its own lint stage (the same ruff check and format check the landing applies) in the foreground on the files it carries, and refuse before it goes to the background, so a lint failure shows in seconds rather than at the next tick or set-down.
- **Made:** 2026-10-19; readable from 2026-10-26.
- **The old reading (hour 37):** `make land-tooling` at 0.93/h before against 3.68/h after, over 10.2 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): check `land-tooling`: no outcome record; guard `gate` 0/0/0; guard `guard-file` 12/5/7; guard `make-only` 23/9/14; target `arbiter-fix-done` 14/0/0; target `hooks-test` 14/0/0; target `land-tooling` 10/0/0
- **Judgment: too new to say.**

### 20. `hour:385-approach-checklist@29`

- **The fix:** make claims-checked validates each verdict line at record time and refuses the line otherwise: the claim path must resolve to a real claim (06:57: the path was missing 'diagram/'), the verdict token must be one of the known set (07:01: 'UNRESEARCHED IN-STEP'), and every research-page pointer in the note must exist (07:03: '0246-...lanes.html' without '.drawing', found only by make done's preflight).
- **Made:** 2026-10-19; readable from 2026-10-26.
- **The old reading (hour 37):** `make claims-checked` at 0.24/h before against 2.56/h after, over 8.1 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): target `claims-backfill`: no outcome record; target `claims-backfill-sections` 0/0/0; target `claims-bundle` 13/0/0; target `claims-carry` 0/0/0; target `claims-checked` 26/0/0; target `claims-coverage` 0/0/0; target `claims-owed` 7/0/0; target `claims-report` 0/0/0; target `claims-triage` 1/0/0; target `claims-triaged` 7/1/0
- **Judgment: too new to say.**

### 21. `hour:385-approach-checklist@31`

- **The fix:** make claims-bundle empties its bundle directory before it builds and writes MANIFEST.md only on success, so an impl-drift dispatched alongside a failed or refused build finds no bundle and stops instead of judging the previous one; its test builds a bundle, runs a refused build into the same directory, and asserts no MANIFEST.md remains.
- **Made:** 2026-10-19; readable from 2026-10-26.
- **The old reading (hour 37):** `agent:impl-drift` at 2.83/h before against 3.33/h after, over 6.0 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): target `claims-backfill`: no outcome record; target `claims-backfill-sections` 0/0/0; target `claims-bundle` 8/0/0; target `claims-carry` 0/0/0; target `claims-checked` 16/0/0; target `claims-coverage` 0/0/0; target `claims-owed` 5/0/0; target `claims-report` 0/0/0; target `claims-triage` 1/0/0; target `claims-triaged` 7/1/0
- **Judgment: too new to say.**

### 22. `hour:385-approach-checklist@33`

- **The fix:** make tick writes the task id into its l7r-events row, so per-task time can be read from the events instead of rebuilt from tasks.md's git history, which the session had to do at 11:55 to answer the GM's speed question.
- **Made:** 2026-10-19; readable from 2026-10-26.
- **The old reading (hour 37):** `make where-time\|git (-C \S+ )?log -p` at 0.02/h before against 0.74/h after, over 4.3 session hours.
- **Its tools since it was made** (uses / interventions / likely misfires): guard `event-log`: no outcome record
- **Judgment: too new to say.**
