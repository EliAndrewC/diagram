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

<!-- plan-archive: archived 2026-10-21 -->
## T42 - a served map's coverage is replayed only onto the lines it measured (found landing T11)

### T42 Approach (checklist part A)

1. **The goal, in the world.** The gate's 100% floor reads the lines each pool map actually ran, so a change in a function a map never runs neither fails the floor on that map's lines nor costs a re-roll of maps the change did not reach in any other way.
2. **The constraints.** The gen cache (features 026, 149, 167): a map is served while no function it executed changed, and its stored coverage is replayed into the gate; feature 149: coverage is a set of LINE NUMBERS, so a replay after the source moved marks the wrong lines; the roll census (one roll of a spec per gate, feature 213), which refuses `GATE_NO_CACHE=1`'s re-rolls.
3. **Where each comes from.** O (features 026, 149, 167, 213).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T11's gate log): Kashikawa and Mizuguchi were served from the gen cache, T11's two-line comment above `stage_web`'s row-village branch shifted it, and the floor named `web.py` 888-889 unrun; with every map rolled (`GATE_NO_CACHE=1`) the floor was 100% and the roll census refused the run (Inashiro rolled 20 times).
5. **The order.** `store` writes, beside the coverage it stores, the sha256 of each file that coverage measures; `gate_obtain` serves a hit only when every one is unchanged (an entry without the record regenerates once); tests; the gate and the landing cohort with T11.
6. **The exits.** (c) - regenerate on a moved file; remapping the stored lines through a diff (`difflib`, as the preflight's T40 does) was weighed and deferred: sound for the lines a map ran (they lie in functions whose source did not change), but arcs and contexts make it a larger change than the defect.
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: an entry whose measured file changed since its coverage was recorded is a miss, not a replay (a test red at HEAD); T11's gate green on the floor without `GATE_NO_CACHE`.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T42 Decisions

**D17 - a hit only on the bytes it measured.** `gencache.store`, when it stores `coverage_data`, also writes `coverage.files.json` - each measured file's sha256 - and removes it with the coverage; `gate_obtain` adds `_coverage_files_unchanged(gen)` to its hit test: every recorded file still hashes the same (a missing record is doubt, and doubt regenerates).
<!-- plan-archive: archived 2026-10-21 -->
## T46 - `make land` writes the make-targets page (found landing T43)

### T46 Approach (checklist part A)

1. **The goal, in the world.** A landing that changed the Makefile is not refused at its push for a page a command writes in a second.
2. **The constraints.** The push's `make-docs` check (385 FR-017); `make land`'s first pass, every cheap refusal before anything runs (405 T33).
3. **Where each comes from.** O (features 385, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21: T43's `make land` ran hooks-test (about 4 min), then the push refused on `docs/make-targets.html`, stale since T43 added two targets.
5. **The order.** The check and the write in `cheap_refusals`, beside the ledger rows; a test.
6. **The exits.** (c) - the landing writes what it can write, as it writes the ledger rows; a refusal naming `make docs` was weighed and refused (a guard that can produce the compliant result produces it).
7. **The search smell.** None.
8. **The budget.** 10 min.
9. **Done, measured.** One goal: with the page stale, the first pass regenerates and commits it; fresh, it touches nothing (test); T43's landing then passes the push.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T46 Decisions

**D19 - the landing writes the page.** `land.cheap_refusals` asks `make-docs.py --check`; when the page is stale it runs `make-docs.py --write` and commits `docs/make-targets.html` alone, before the gates and the push are asked.
<!-- plan-archive: archived 2026-10-21 -->
## T48 - the landing cohort beside the gate (amendment 5)

### T48 Approach (checklist part A)

1. **The goal, in the world.** An engine landing waits for the longer of the gate and the landing cohort, not for both in turn.
2. **The constraints.** The gate's tree check (375 FR-004, 405 D15) - a commit while the gate runs voids it unless the gate does not see it; the roll census (feature 213), set by the gate for its own children; the cohort gate (feature 386) - a record rolled on exactly the engine that lands, whose key includes the pool's manifests; the container's 10 GB memory cap, shared; the dev loop's "never run a test beside a running gate" (two writers on the same pool maps).
3. **Where each comes from.** O (features 213, 375, 386, 405) and the GM (amendment 5).
4. **Do they describe the world here?** Yes - measured 2026-10-21: T19's landing ran the cohort (4.4 min) after a green gate (about 5 min); the gate rolls only the five pool maps and the cohort only `Audit-<n>` seeds and the pinned rows, through the roll cache (atomic, locked writes), and writes no pool map; the cohort commits one new record under `dev/cohort-log/`, which no test reads (the tests use temporary trees); the gate peaked at 3.1 GB on six workers (measured 2026-10-04) and a roll is 115-180 MB; `MemAvailable` was about 9 GB.
5. **The order.** `preflight.unseen` reads a new record under `dev/cohort-log/` as unseen; `_reference` leaves `roll-cache-class` alone when the cohort's own run says so; `land.long_runs` starts `make cohort-landing` in its own process group before the gate when the landing carries engine code and has no cohort on this engine, runs the gates, waits for the cohort, kills it on a red gate or any exit; the existing check after re-runs the cohort only when the gate's regenerated pool maps moved the engine key; tests; the dev loop's rule given its exception.
6. **The exits.** (c) - two background runs, as the claims round already runs beside the gate; folding the cohort into the gate was weighed and refused (the gate is every session's, the landing cohort only a landing's).
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** One goal: `land.py` starts the cohort before `make done` and waits for both, kills it on a red gate, starts none on a tooling landing (tests); a gate with a cohort record committed beside it reads unmoved (test); live, the fifth claim's landing reports the gate's and the cohort's wall times, `JOBS` and `MemAvailable`, against T19's 5 + 4.4 minutes in turn.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T48 Decisions

**D21 - the cohort beside the gate.** `land.long_runs`: when the green-gate stamp names `make done`, the landing carries engine code and `cohort_gate.py check` refuses, `make cohort-landing JOBS=<n>` starts first (`start_new_session`, its output to `<git dir>/land-cohort.log`, `L7R_ROLL_CENSUS` removed from its environment, `L7R_REF_NO_CLASS=1` so its reference check does not overwrite the gate's `roll-cache-class`); `n` is the lesser of the cpus less two and the gate's six workers, and (`MemAvailable` less 3.5 GB for the gate) over 0.5 GB a roll, at least 2, printed. The gates run in the foreground; a red gate, or any exit, kills the cohort's process group; after a green gate `land.py` waits for the cohort and prints its rate line, and refuses on its failure. The existing check then re-runs the cohort only where the gate committed regenerated pool maps (the key moved; its seeds come from the roll cache). `preflight.unseen` reads a path under `dev/cohort-log/` that did not exist before (a new `.json` record) as unseen; a change to an existing one is seen.
<!-- plan-archive: archived 2026-10-21 -->
## T50 - the claims round beside the landing (amendment 6)

### T50 Approach (checklist part A)

1. **The goal, in the world.** The session commits the code and starts `make land`; the claims round runs while the gate and the landing cohort do, and the landing pushes as soon as all three are done.
2. **The constraints.** The claims gate (feature 316), asked before every push; `make land`'s first pass, every cheap refusal together (405 T33); the gate beside the claims round (405 T41, D15: the round's records and claim docstrings are unseen by the gate); the push refuses uncommitted work.
3. **Where each comes from.** O (features 316, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T13): the round took 1.5 min (11:31:00-11:32:29) in series, because `make land` refuses while a claim is owed.
5. **The order.** `cheap_refusals` sets a claims-gate refusal aside instead of stopping on it; `long_runs` runs; then `land.py` asks the claims gate again, and while it refuses or the tree is not clean, waits and asks again, up to a bound, before the push; tests; the dev loop's line on the order.
6. **The exits.** (c) - the landing waits on the claims gate it already asks; a second command for the session to remember was refused.
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: with a claims-gate refusal at the start, `make land` runs the gate and the cohort, then pushes once the gate passes and the tree is clean, and refuses with the gate's words past the bound (tests); live, the next claim's round overlaps its gate.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T50 Decisions

**D23 - the claims gate asked last, waited on.** `land.cheap_refusals` returns a claims-gate refusal apart from the others (they still stop the landing); `land.main` runs the long runs, then `wait_for_claims`: the claims gate passing and `git status --porcelain` empty, asked every `CLAIMS_POLL_S` (15 s) for up to `CLAIMS_WAIT_S` (20 min), printing once what it waits for; past the bound nothing lands and the gate's words are printed. A claims-round edit that the gate does see (code) leaves the green-gate stamp stale, which the push refuses as today.

<!-- plan-archive: archived 2026-10-21 -->
## T51 - one push (amendment 6)

### T51 Approach (checklist part A)

1. **The goal, in the world.** A landing is one push, carrying its work and its ticks.
2. **The constraints.** The tick's landed check (`tick-task.landed_refusal`, 385 T79/T113: a note saying "landed" over work not on main is refused); history is never rewritten (no amend, reset or force push); "a failed landing ticks nothing" (405 T33).
3. **Where each comes from.** O (features 385, 405) and the GM's standing rule on history.
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T13): 11:37:45-11:40:03, two `sync-with-main.sh done` runs, the second only for the tick.
5. **The order.** `tick-task.py --landing` skips the landed check, which `make land` asks of each task before it lands them; `land.main` ticks, commits the feature's records, pushes once; on a failed push it reverts the tick commit with a new commit; tests.
6. **The exits.** (c) - the tick goes into the push; a lighter second push was weighed and refused (it still re-asks every push check).
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: one push per landing, the ticks in it; a failed push leaves the tasks open by a revert commit (tests); live, the next claim's landing has one push.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T51 Decisions

**D24 - tick, then push.** `tick-task.py <f> <task> <note> --landing` asks every refusal but the landed one (`refusal(..., landed=False)`); `land.main`, after the long runs and the claims wait, ticks each task with it, commits the feature directory, and pushes once with `L7R_LAND_TICKS` set. A failed push runs `git revert --no-edit` on the tick commit (a new commit; nothing rewritten), so the tasks read open again.

<!-- plan-archive: archived 2026-10-21 -->
## T47 - the preflight's coverage step leaves the gate (amendment 6)

### T47 Approach (checklist part A)

1. **The goal, in the world.** The gate spends its first minutes only on checks that refuse often enough to pay for themselves; the coverage step stays available on demand.
2. **The constraints.** The gate's 100% floor (feature 174), which judges every changed line minutes later; the preflight's cheap-refusal-first order (375 FR-004); `make preflight`, its standalone target.
3. **Where each comes from.** O (features 174, 375, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (the clones' `tool-usage.jsonl` and the session transcripts): the step cost 98 s (T19) and 107 s (T13) of each gate; since 2026-10-20 the preflight ran 46 times and refused 8, of which the coverage step refused about 2 in the transcripts' whole record - one of them wrong (`gencache.py:765`, fixed by F's follow-up); its other lines are informational ("the gate's floor judges"). A catch saves the gate's run, about 3 min.
5. **The order.** `preflight.py --no-coverage` skips the step; the `done` recipe passes it; `make preflight` keeps the step; tests; the target's line.
6. **The exits.** (c) - the step leaves the gate, kept on demand; reusing its pass in the gate was weighed and refused (the gate measures coverage over the full suite, a different run).
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: the gate's preflight no longer runs the coverage step, `make preflight` still does (tests); live, the next claim's preflight is about 100 s shorter.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T47 Decisions

**D25 - on demand, not in the gate.** `preflight.py` takes `--no-coverage`, which ends it after the quick tier; the `done` recipe passes it, `make preflight` does not. The gate's own floor judges every changed line, as it did before the step existed.
<!-- plan-archive: archived 2026-10-21 -->
## T49 - a street's dangling end may stop where it crosses a way (found in T13's round)

### T49 Approach (checklist part A)

1. **The goal, in the world.** A street that crosses another way and runs on past it to nothing ends at that crossing, on the way, not back at an earlier joint.
2. **The constraints.** 0246's drawing page (§6: a lane runs on to the last house it serves or to another way; an end reaching nothing is pulled back); `settle_street_ends` and its joints (405 T13, D22: other lanes' ends and the served farms' points); `law.crossing_points`, the one crossing test.
3. **Where each comes from.** R (0246) and O (features 291, 293, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (a read of `settle.py` and `street.joints_along`): the joints are lane END points and the farms' points only, so a way crossing the street mid-run is no joint, and a dangling end past it is cut back further than 0246 asks (impl-drift's note outside the change, T13's round).
5. **The order.** Each point where the street crosses another way joins its joints, in place (the file stands at the 1,000-line bar); a unit test of a street crossing a way and dangling past it; `make land` started at once, the claims round beside its gate.
6. **The exits.** (e) conform - the research lets a street end on a way.
7. **The search smell.** None.
8. **The budget.** 20 min with the landing.
9. **Done, measured.** One goal: a dangling street end past a crossing is cut to the crossing (test); the claims round reads `settle_street_ends` IN-STEP; the gate green and the landing cohort refusing no seed against main.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T49 Decisions

**D26 - a crossing is a joint.** `settle.settle_street_ends` adds every point where the street's run crosses another way (`law.crossing_points`) to the joints it passes `street.end_to_its_joint`, beside the other lanes' ends and the served farms' points; the docstring and its claim name it.
<!-- plan-archive: archived 2026-10-21 -->
## T52 - the ledger rows written again after the claims wait (found landing T49)

### T52 Approach (checklist part A)

1. **The goal, in the world.** A claims round run beside the landing's gate needs no ledger row written by hand.
2. **The constraints.** The push's ledger check (features 371, 385 FR-019); `make land`'s writing of the feature's traced passes (405 T39, D13); the claims wait (405 T50, D23).
3. **Where each comes from.** O (features 371, 385, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T49's landing): the impl-drift pass came after `make land`'s first pass, so its row was owed at the push; I wrote it with `make ledger-owed` at 12:03:17.
5. **The order.** The two writes and their commit lifted into `write_ledger`, asked in the first pass and again after the claims wait; a test.
6. **The exits.** (c) - the landing writes what it can write.
7. **The search smell.** None.
8. **The budget.** 10 min.
9. **Done, measured.** One goal: after the claims wait the rows are written again, before the ticks and the push (test).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T52 Decisions

**D27 - written twice.** `land.write_ledger(root, d)` writes the plan reviews' rows and the feature's traced passes and commits the ledger; `cheap_refusals` asks it first, and `main` again after `wait_for_claims`, before the ticks.
<!-- plan-archive: archived 2026-10-21 -->
## T53 - split at the file bar, never trim to it (amendment 7)

### T53 Approach (checklist part A)

1. **The goal, in the world.** A file that passes the 1,000-line bar is split once into a package with room to grow, so the next edits do not meet the bar again.
2. **The constraints.** Constitution Principle X clause 13 (the bar, gated since feature 173) and its two carve-outs (ordered data, a derived roster); `check-file-scale.py`'s refusal, which already prescribes a directory-module; the house rule that a guard's message carries the concrete fix, pinned by a test; the GM's words (amendment 7).
3. **Where each comes from.** O (features 173, 329) and the GM (amendment 7).
4. **Do they describe the world here?** Yes - measured 2026-10-21: T11's comment put `web.py` at 1,002 and was trimmed to 1,000; T49's edit put `settle.py` at 1,009 and was folded to 1,000 - each a refusal and a minute or two, and both files stand at the bar for the next edit.
5. **The order.** The refusal's text: the target of about 650 lines a submodule, the `__init__.py` re-exporting every name so no importer changes, and "never trim to just under the bar"; the test pinning those words; the root CLAUDE.md line.
6. **The exits.** (c) - the check's own message steers the split; a hard 650-line rule was not asked for (the GM: "doesn't need to be a hard limit").
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: the refusal names the ~650-line submodules, the re-exporting `__init__.py` and the rule against trimming (test); the root CLAUDE.md says the same.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T53 Decisions

**D28 - the refusal says split, to about 650.** `check-file-scale.GUIDANCE` adds: split now, never fold or cut lines to land just under the bar; aim each submodule at about 650 lines (2/3 of the bar - a guideline, not a check); the package's `__init__.py` re-exports every name importers used, so no importer changes. The root CLAUDE.md's file-bar line says the same in one sentence. The bar stays 1,000 and the carve-outs stay.
<!-- plan-archive: archived 2026-10-21 -->
### T16 Approach (checklist part A)

1. **The goal, in the world.** Every rule of the field run-on and the dangling-end test is claimed.
2. **The constraints.** 0246 (an end runs on to a field path, a bund or another way); 0014 (the path joins the paddy's bund, never ends short of it); 0081 (the track out runs off the map).
3. **Where each comes from.** R (0246, 0014, 0081).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (a read of `bund.py` and `law.py`): `run_lanes_on_to_the_bund` skips a row street and carries an end within `RUN_ON_REACH_FT` onto the worked ground's edge, the dry hem's as well as the paddy's, unclaimed; `run_on_target`'s reach and its stop outside the ground are unclaimed; `dangling_lane_ends` exempts the connector unclaimed.
5. **The order.** A claim for each, labeled as the pages give it.
6. **The exits.** (a) claim - the behavior stands; the dry hem is claimed UNRESEARCHED (0014 speaks of the paddy and is silent on a dry plot; T22 carries the field's reach).
7. **The search smell.** None.
8. **The budget.** With T17.
9. **Done, measured.** The claims round reads the new claims IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T16 Approach (re-answered 2026-10-21T12:56Z)

1. **The goal, in the world.** As before: every claim says what the code does, labeled as its page labels it.
2. **The constraints.** As before, and 0033's drawing page (a row street "runs on off the map as the road into it") and 0081's (lanes along the hem of dry fields; the spur stops at the hem's edge), which the round read.
3. **Where each comes from.** R (0246, 0033, 0014, 0081).
4. **Do they describe the world here?** Yes - the round, 2026-10-21 (impl-drift, 27 claims): where a claim's page disagrees with the CODE, the code's drift is a task of its own; where it disagrees with the label, the label follows the page.
5. **The order.** The street skip cited to 0033, the dry hem to 0081 as a GUESS; the claims round.
6. **The exits.** (e) conform - words and labels; the code's drift carried (T54, T55).
7. **The search smell.** None.
8. **The budget.** With the batch.
9. **Done, measured.** The claims round reads the new claims IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T27 Approach (checklist part A)

1. **The goal, in the world.** The farm-fixture claims say where the fixtures stand and cite the page that says so.
2. **The constraints.** 0038 (the bed's sides), 0039 (the kitchen garden), 0043 (the wood shed a ken beyond the wall strip, about 9.5 ft off), 0047 (the privy's places and the front seat's 8 ft GUESS), 0219 (the shrine's corner).
3. **Where each comes from.** R.
4. **Do they describe the world here?** Yes - measured 2026-10-21 (a read of `taxonomy.py` and `fixture_seats.py`): the exemption's text seats every fixture "against its own farmhouse" (the shed 9.5 ft off, the shrine and grave a plot corner, the privy out to 48 ft); its claim cites 0039 for the bed beside the house, which 0038 gives; `CANOPY_PAD` and `SHADE_MARGIN_FT` carry no claim; `_seats`' privy front step and stable seat are unclaimed.
5. **The order.** The text and the claim reworded, the citations put right, the four claims added.
6. **The exits.** (e) conform - words to the code and the pages.
7. **The search smell.** None.
8. **The budget.** With T17.
9. **Done, measured.** The claims round reads them IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T16 Decisions

**D30 - the run-on claimed.** `run_lanes_on_to_the_bund` claims: a row street not carried onto the field (0033: the street runs on off the map as the road); the reach (GUESS: `RUN_ON_REACH_FT`, 0246's 60 ft reused for the field); the dry hem's edge (GUESS, 0081: lanes run along the hem of dry fields and the spur stops at its edge). `run_on_target` claims its reach (GUESS, the same) and its stop (CONVENTION: the half-tread and `TIP_MARGIN_FT` outside the ground). `dangling_lane_ends` claims the connector exempt (0081: the track out runs off the map).

<!-- plan-archive: T27 to T27 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-10-21 -->
### T58 Approach (checklist part A)

1. **The goal, in the world.** A split at the bar costs no claims round for the code it only moved.
2. **The constraints.** The claims index and `claims_owed.owed` (features 316, 385 T116); the claims gate's "introduced" reading, already asked across keys (a unit moved with its code intact matches its base unit).
3. **Where each comes from.** O (features 316, 385).
4. **Do they describe the world here?** Yes - measured 2026-10-21: splitting `web.py` owed its claims in full as "new", every one at its new key.
5. **The order.** `claims_owed.moved` (the same unit and claim, the old key gone, the same code fingerprint, one candidate), read by `owed`; `rekey` copies each row to its new key and drops the old; `make claims-rekey`; `make land` runs it first; a test.
6. **The exits.** (c) - the index learns a move; nothing it judged is re-judged.
7. **The search smell.** None.
8. **The budget.** With T57.
9. **Done, measured.** One goal: a unit moved with its code intact owes nothing and its row moves; one whose code changed is still owed (test); live, 61 of `web.py`'s rows carried.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
## T61 - the gate-write suite waits for its own fixture's gate (found landing the T17 batch)

### T61 Approach (checklist part A)

1. **The goal, in the world.** hooks-test reads the same whether or not another gate runs on the machine.
2. **The constraints.** The gate-write guard (385 FR-010, 405 T41), which asks `lib/own-make.sh` whether THIS tree's `make done` runs; its suite; the landing's gate beside its cohort (405 T48).
3. **Where each comes from.** O (features 385, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21: the T17 batch's gate ran hooks-test while it itself ran; the suite's `pgrep -f "make done"` found that gate at once, so its first three cases ran before the fixture's gate started and read "let through" (19 passed, 3 failed).
5. **The order.** Both waits ask `own-make.sh done` from the fixture's directory; the suite run.
6. **The exits.** (c) - the test asks what the guard asks.
7. **The search smell.** None.
8. **The budget.** 10 min.
9. **Done, measured.** The suite passes 22 of 22, run while another gate runs.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T61 Decisions

**D35 - the fixture's own gate.** `tests/hooks/test-gate-write-hooks.sh` waits until `scripts/hooks/lib/own-make.sh done`, run from the fixture tree, says the fixture's gate runs - the question the guard itself asks - in both sections.
<!-- plan-archive: archived 2026-10-21 -->
### T28 Approach (checklist part A)

1. **The goal, in the world.** No finding of 385 or 405 sits open with no task.
2. **The constraints.** FR-002 (found work stays in the feature); T29's tool.
3. **Where each comes from.** The GM (FR-002) and the spec review of 405 (2026-10-20).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (a read-only mapping of all 76 rows against both task lists and the current code and record): 22 carried by 405 tasks, 9 by 385 tasks, 11 no longer holding - each measured against the file it names, the cited text gone or corrected (its reason records what stands there now) - and 34 unfiled.
5. **The order.** The 34 unfiled rows grouped into six tasks by unit and complaint (T65-T70); every row closed with its outcome.
6. **The exits.** (c) - filed, not fixed here; each new task is worked in this feature.
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** `make found-list` shows 0 open in 385's and 405's logs.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T28 Decisions

**D37 - six tasks for 34 rows.** T65 (the 4 ft touch gap against 0246 §16's 7 ft), T66 (stale words in `track.py` and `route.py`), T67 (the dry exit's claims and crossings), T68 (`_trim_to_service` and the sweeps' claims against 0246 §6), T69 (the web cut counting a household reached across a yard), T70 (three record wordings). A row filed in 385's log names its 405 task with the feature (`405 T17`).

### T45 Approach (checklist part A)

1. **The goal, in the world.** The reference map's message offers no recovery the gate refuses.
2. **The constraints.** The roll census (feature 213), which refuses a `GATE_NO_CACHE=1` gate's re-rolls (405 T11's 05:02 gate); `_reference`'s message.
3. **Where each comes from.** O (features 213, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21: the 05:02 gate under `GATE_NO_CACHE=1` was refused by the census; the message still offers it.
5. **The order.** The message's offer removed; the reason it is served stays.
6. **The exits.** (c) - the message stops offering it; making the census accept a declared no-cache run was weighed and refused (T42 made the cache right, so the bypass has no work left).
7. **The search smell.** None.
8. **The budget.** 5 min.
9. **Done, measured.** The message names no `GATE_NO_CACHE`.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

## T29, T28, T45 - the findings log closes, 385's rows mapped, the reference message (found and filed work)

### T29 Approach (checklist part A)

1. **The goal, in the world.** A feature's `found.jsonl` says, for every finding, whether it is filed (and as what) or settled (and why).
2. **The constraints.** `found.jsonl`, written by `record_owed` and the checks (open rows, never edited, 385); the found-work rule (the GM 2026-10-19, FR-002).
3. **Where each comes from.** O (feature 385) and the GM (FR-002).
4. **Do they describe the world here?** Yes - measured 2026-10-21: 385's 63 rows and 405's 13 all read `open`, filed or not; nothing wrote a row's outcome.
5. **The order.** `scripts/record/found.py` (`list`, `close --task | --why`), `make found-list` and `make found-close`; a test.
6. **The exits.** (c) - a row gains its outcome; nothing is deleted.
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** A row closes as filed (a task of 405, or of 385 - the two features the GM's routing names) or settled only where it no longer holds (the reason records the measurement), once; `list` counts what is open (test).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T29 Decisions

**D36 - a row's outcome on the row.** `found.py close` sets `status` to `filed` with `task` (`T61`, `385 T12` or `405 T17` - no other feature, the GM's routing), or `settled` with `why`, and `closed_utc`; it refuses a row already closed. SETTLED ONLY WHERE THE FINDING NO LONGER HOLDS (the plan review of D36, FR-002): the reason starts "no longer holds" and records what was measured against the current file; a finding that still holds is filed as a task. `found.py list` numbers the open rows in file order.

<!-- plan-archive: T28 to T28 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T28 Decisions

**D37 - six tasks for 34 rows.** T65 (the 4 ft touch gap against 0246 §16's 7 ft), T66 (stale words in `track.py` and `route.py`), T67 (the dry exit's claims and crossings), T68 (`_trim_to_service` and the sweeps' claims against 0246 §6), T69 (the web cut counting a household reached across a yard), T70 (three record wordings). A row filed in 385's log names its 405 task with the feature (`405 T17`).

### T45 Approach (checklist part A)

1. **The goal, in the world.** The reference map's message offers no recovery the gate refuses.
2. **The constraints.** The roll census (feature 213), which refuses a `GATE_NO_CACHE=1` gate's re-rolls (405 T11's 05:02 gate); `_reference`'s message.
3. **Where each comes from.** O (features 213, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21: the 05:02 gate under `GATE_NO_CACHE=1` was refused by the census; the message still offers it.
5. **The order.** The message's offer removed; the reason it is served stays.
6. **The exits.** (c) - the message stops offering it; making the census accept a declared no-cache run was weighed and refused (T42 made the cache right, so the bypass has no work left).
7. **The search smell.** None.
8. **The budget.** 5 min.
9. **Done, measured.** The message names no `GATE_NO_CACHE`.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T45 Decisions

**D38 - the offer removed.** `_reference`'s served line reads "served from the roll cache: nothing the roll executes changed" without "GATE_NO_CACHE=1 rolls it".
<!-- plan-archive: archived 2026-10-21 -->
### T63 Approach (checklist part A)

1. **The goal, in the world.** A skeleton arm's end that reaches the bund or a way already laid stays where it reaches.
2. **The constraints.** 0246 §6 (only "a lane end that reaches nothing is pulled back"; an end runs on to a field path, a bund or another way); `_trim_to_service`, which takes ways and the worked ground; `served_arm`.
3. **Where each comes from.** R (0246).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (impl-drift, the T17 batch's round 2): `served_arm` passes no ways and no ground, so an arm's end on the connector, the spur or the bund is trimmed back to its last house.
5. **The order.** `served_arm` passes the ways drawn so far (`_net_segs`) and the worked ground (where the map has a field); its claims; the unit tests; the gate and the cohort.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** With T62.
9. **Done, measured.** One goal: an arm ending on a way or the bund is not trimmed (test); the cohort refuses no seed against main.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T63 Decisions

**D40 - judged against what it reaches.** `served_arm(s, arm)` calls `_trim_to_service(arm, _net_segs(s), houses, ground=<the worked ground where the map has a field>, steadings=...)`; its claim and `_lay_skeleton`'s name the ways and the bund.

### T69 Approach (checklist part A)

1. **The goal, in the world.** A web lane's span counts only the houses owed a lane.
2. **The constraints.** 0246 (a household reached across a neighbor's yard is owed no lane); `stage_web`, which builds the cut lines' arcs and stands.
3. **Where each comes from.** R (0246).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (a read of `web/stage.py`): `stage_web` already leaves out every house `reached_across` before it computes the arcs and stands it passes to `_web_cut_lines`, so the finding does not hold in the code; the claim does not say so.
5. **The order.** The claim says where the exclusion is made.
6. **The exits.** (a) claim.
7. **The search smell.** None.
8. **The budget.** With T62.
9. **Done, measured.** The claims round reads it IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

## T62, T63, T69 - the run-on to the paddy, the arm trims against what they reach, the cut lines' houses (the T17 batch's round 2; T28)

### T62 Approach (checklist part A)

1. **The goal, in the world.** An inner lane that runs on to the field ends at the paddy's bund, not on a dry plot's edge.
2. **The constraints.** 0081's drawing page ("the settlement's own inner lanes may end in the cluster or at the paddy"; only the spur to the fields stops at the hem's edge); 0014 (the path joins the paddy's outer bund); `bund.run_lanes_on_to_the_bund` and `paddy_ground`.
3. **Where each comes from.** R (0081, 0014).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (impl-drift, the T17 batch's round 2): the run-on carries an inner lane's end to `ground.nearest`, the worked ground's, a dry plot's edge included.
5. **The order.** The run-on target read on the paddy (`paddy_ground`), the pull out of the worked ground unchanged; its claim; the unit tests; the gate and the cohort.
6. **The exits.** (e) conform - the research names the paddy.
7. **The search smell.** None.
8. **The budget.** 30 min for the batch with its landing.
9. **Done, measured.** One goal: a run-on aims at the paddy, never a dry plot (test); the cohort refuses no seed against main.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T62 Decisions

**D39 - the paddy, not the hem.** `run_lanes_on_to_the_bund` aims `run_on_target` at `paddy_ground(s)` (built once a pass); an end standing in the worked ground is still pulled out of it; the claim "the dry hem's edge too" becomes "to the paddy" (0081).

<!-- plan-archive: T63 to T63 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T63 Decisions

**D40 - judged against what it reaches.** `served_arm(s, arm)` calls `_trim_to_service(arm, _net_segs(s), houses, ground=<the worked ground where the map has a field>, steadings=...)`; its claim and `_lay_skeleton`'s name the ways and the bund.

### T69 Approach (checklist part A)

1. **The goal, in the world.** A web lane's span counts only the houses owed a lane.
2. **The constraints.** 0246 (a household reached across a neighbor's yard is owed no lane); `stage_web`, which builds the cut lines' arcs and stands.
3. **Where each comes from.** R (0246).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (a read of `web/stage.py`): `stage_web` already leaves out every house `reached_across` before it computes the arcs and stands it passes to `_web_cut_lines`, so the finding does not hold in the code; the claim does not say so.
5. **The order.** The claim says where the exclusion is made.
6. **The exits.** (a) claim.
7. **The search smell.** None.
8. **The budget.** With T62.
9. **Done, measured.** The claims round reads it IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T69 Decisions

**D41 - said where it is done.** `_web_cut_lines`' claim "a web lane's span" adds that its arcs and stands are every house but one reached across a yard (`stage_web` leaves those out).
<!-- plan-archive: archived 2026-10-21 -->
## T72 - the cohort's workers sized to the container's memory (found landing batch 3)

### T72 Approach (checklist part A)

1. **The goal, in the world.** The landing cohort beside the gate never takes the containers to their memory cap.
2. **The constraints.** The containers' shared 10 GB cgroup limit (the host has 15 GB); the gate's peak (3.1 GB on six workers, measured 2026-10-04); a roll's allowance (the Makefile's 0.5 GB); 405 T48's sizing.
3. **Where each comes from.** O (feature 405, the test RAM profile of 2026-10-04) and the host.
4. **Do they describe the world here?** Yes - measured 2026-10-21: the batch-3 landing sized 12 workers from MemAvailable 9,500 MB; the memwatch hook reported the containers at 9.0 of 10.0 GB; `/sys/fs/cgroup/memory.max` reads 10 GiB.
5. **The order.** `land.memory_free_mb` (the host's MemAvailable, bounded by the cgroup's limit less what it holds plus its inactive file cache); `cohort_jobs` reads it; a test.
6. **The exits.** (c) - the sizing reads the limit that kills.
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** A 10 GiB limit holding 8 with 1 of cache counts 3 GiB free and sizes 2 workers (test); with no limit, the host's figure.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T72 Decisions

**D42 - the limit that kills.** `memory_free_mb(cgroup)` = min(MemAvailable, memory.max - memory.current + inactive_file) where `memory.max` is a number; `cohort_jobs` sizes from it; the landing prints the figure.

<!-- plan-archive: archived 2026-10-21 -->
### T66 Approach (checklist part A)

1. **The goal, in the world.** The track's words say what its code does.
2. **The constraints.** `TRACK_FABRIC_GAP = WEB_FABRIC_GAP` (0246's 7 ft); `ROUTE_CELL` 10 ft; `CONNECTOR_BAND_GAP_FT` (0036's 9.5 ft working room past the connector's half-width); `WEB_HARD_GAP` 8 ft off wet ground.
3. **Where each comes from.** R (0246, 0036) and O.
4. **Do they describe the world here?** Yes - measured 2026-10-21 (385 found rows 12-15, 27, 28, each re-read in the code: the docstring calling the track's gap not the web's; the steadings claim; the band gap held for the spur; `_route`'s 12 ft cells; `wet_grown_by_the_lane`'s 8 px).
5. **The order.** Each wording put right where it stands.
6. **The exits.** (e) conform - words only.
7. **The search smell.** None.
8. **The budget.** With the batch (claims and words only, one landing).
9. **Done, measured.** the claims round reads every changed claim IN-STEP; no code token changes.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T66 Decisions

**D44 - the track's words.** `_thread_the_fabric`'s gap paragraph says the gap is the web's and the route is what differs; its steadings claim names `gap` for the clip and the fabric test, the router walling the steadings; the band claim says the spur keeps the connector's 12.5 ft; `_route` reads 10 ft cells; `wet_grown_by_the_lane` reads 8 px, 8 ft on a hamlet's sheet (1 ft a px), `WEB_HARD_GAP`'s bar.

### T59 Approach (checklist part A)

1. **The goal, in the world.** `_trim_to_service`'s rule that an end does not count as reaching the way it left is claimed.
2. **The constraints.** 0246 §6, which records no such case (the T28 mapping's 405 row 9).
3. **Where each comes from.** O (feature 261's settlement-review of Mizuguchi).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (the claims gate carried it from the T17 batch's round 1: UNCLAIMED).
5. **The order.** The claim, UNRESEARCHED with its origin.
6. **The exits.** (a) claim.
7. **The search smell.** None.
8. **The budget.** With the batch (claims and words only, one landing).
9. **Done, measured.** the claims round reads every changed claim IN-STEP; no code token changes.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T59 Decisions

**D45 - claimed where it is decided.** `_trim_to_service` claims "not the way it left", UNRESEARCHED: the page records no such case; the rule came from the settlement-review of Mizuguchi (feature 261).

### T68 Approach (checklist part A)

1. **The goal, in the world.** Every claim on the trims and the sweeps cites a page only for what that page records.
2. **The constraints.** 0246 §6 (an end that reaches nothing pulled back to the last house it serves - a GUESS; reaches of 60 ft and 12 ft).
3. **Where each comes from.** R (0246, 0033).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (the T28 mapping's 405 rows 1-6, 8, 9, 11, 12, each re-read in the code).
5. **The order.** The step, the keep and keep-whole exceptions, the closest-approach cut, the departure way, the track-out and street exemption and the carry's reach labeled UNRESEARCHED where the page records none; the carry comment and the 60/100 ft comment put right; the grove-band rule labeled GUESS where it is held beyond 0033's row villages.
6. **The exits.** (e) conform - labels and words; no behavior changes (a page record for any of them is the record's own work, not this task's).
7. **The search smell.** None.
8. **The budget.** With the batch (claims and words only, one landing).
9. **Done, measured.** the claims round reads every changed claim IN-STEP; no code token changes.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T68 Decisions

**D46 - cited for what the page records.** `_trim_to_service`: the 4 ft step, "an outlying house keeps its way" and "a short way kept whole" UNRESEARCHED; `_stop_at_closest_approach` UNRESEARCHED; `_sweep_dangling_ends`: "not the way it left", the track-out and street exemption and the 120 ft carry UNRESEARCHED, the grove band GUESS 0033 held for every settlement; the two comments reworded. The house's center as the 60 ft's point stands in `_trim_to_service`'s own comment.

### T71 Approach (checklist part A)

1. **The goal, in the world.** The two rules batch 3's round found unclaimed are claimed.
2. **The constraints.** 0246 (WEB_REACH_FT for back lanes), 0081 (the 3 ft footpath).
3. **Where each comes from.** R (0246, 0081).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (impl-drift outside the change, batch 3's round).
5. **The order.** Two claims.
6. **The exits.** (a) claim.
7. **The search smell.** None.
8. **The budget.** With the batch (claims and words only, one landing).
9. **Done, measured.** the claims round reads every changed claim IN-STEP; no code token changes.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
## T64, T66, T59, T68, T71, T56 - claims and words brought to the pages (the T17 batch's and batch 3's rounds; T28)

### T64 Approach (checklist part A)

1. **The goal, in the world.** One rule carries one label, and the span floor's claim names both drops.
2. **The constraints.** 0246 §16 (a lane's middle at least 7 ft from a garden fence, a map drawing convention it states).
3. **Where each comes from.** R (0246).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (impl-drift, the T17 batch's round 2): `route._route` and `clearance._clear_link` label the 7 ft DEVIATION, `_lay_skeleton`'s clip cites it plainly (IN-STEP); the span floor's claim names a 30 ft piece where `clip_to_clear` first drops a run under 70 ft).
5. **The order.** Both DEVIATION labels cited plainly, the fence-to-middle reading named; the span floor names the 70 ft drop.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** With the batch (claims and words only, one landing).
9. **Done, measured.** the claims round reads every changed claim IN-STEP; no code token changes.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T64 Decisions

**D43 - one label.** `_route` and `_clear_link` cite 0246 plainly for the 7 ft; `_lay_skeleton`'s span floor names `clip_to_clear`'s 70 ft drop and `_WEB_MIN_FT`'s 30 ft.

<!-- plan-archive: T66 to T66 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T66 to T59 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T59 to T68 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T68 to T71 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T71 Decisions

**D47 - two claims.** `_web_cut_lines` claims the side lanes' reach (GUESS: 0246's back-lane 100 ft reused); `run_lanes_on_to_the_bund` claims a lane with no width read as 0081's 3 ft footpath.

### T56 Approach (checklist part A)

1. **The goal, in the world.** The run-on's join point is claimed as the page guesses it.
2. **The constraints.** 0014 ("the path joins the bund at its point nearest the hamlet", a GUESS).
3. **Where each comes from.** R (0014).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (impl-drift outside the change, the T16 round and batch 3's: the code joins at the point nearest the lane's END).
5. **The order.** The claim labels the code's rule a DEVIATION from 0014's guess, with its reason.
6. **The exits.** (a) claim as a DEVIATION - the page's guess is about the one field path from the hamlet; the run-on carries each lane end on its own, joining where that end reaches the bund soonest. Changing the code to the hamlet's nearest point was weighed: it would carry an end past nearer bund to another point. (The plan review of D48: no reading that makes the page say what the code does.)
7. **The search smell.** None.
8. **The budget.** With the batch (claims and words only, one landing).
9. **Done, measured.** the claims round reads every changed claim IN-STEP; no code token changes.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T56 Decisions

**D48 - a DEVIATION, named.** `run_on_target`'s "joins at the nearest point" is labeled DEVIATION from 0014: the page guesses the field path joins at the bund's point nearest the hamlet; each run-on end joins at the point nearest itself.
<!-- plan-archive: archived 2026-10-21 -->
### T65 Approach (checklist part A)

1. **The goal, in the world.** A join link and the route's straightening keep a lane's middle 7 ft off a garden fence, as every lane does.
2. **The constraints.** 0246 §16 (a lane's middle at least 7 ft from a garden fence); `touch._detour_links`, `touch._join_piece`, `route._unjog`; the 4 ft junction margin they kept (feature 137 T03: seed 37 and 26 of 48 then needed it).
3. **Where each comes from.** R (0246) and O (feature 137).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (385 found rows 9-11, 16, 17: the three sites at `_TOUCH_GAP`, unclaimed; with all three at 7 ft, seeds 1-48 and the pinned rows 54/54 and the measured block unchanged, so the exception no longer earns its place).
5. **The order.** The three at `WEB_FABRIC_GAP`; their claims; the two comments that defended 4 ft rewritten with the measurement; the cohort.
6. **The exits.** (e) conform - measured first: the exception's reason (stubs that could not join) no longer occurs.
7. **The search smell.** None.
8. **The budget.** 45 min for the batch with its landing.
9. **Done, measured.** One goal: no join routes or straightens at 4 ft; the cohort as above.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T65 Decisions

**D50 - one margin for every lane.** `_detour_links`' first try, `_join_piece`'s bar and `_unjog`'s default at `WEB_FABRIC_GAP`; each claims 0246's 7 ft; the comments in `fabric.py` and `touch.py` record the change and its measurement.

### T73 Approach (checklist part A)

1. **The goal, in the world.** The sweeps' claims say what the page records.
2. **The constraints.** 0246 §10 (back lanes bring every farmhouse within 100 ft of one), §6, §78 (no lane through a farm's own wood), 0036.
3. **Where each comes from.** R (0246, 0036).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (impl-drift outside the change, batch 4's rounds: "a house served" said "where the page says 60 ft" though its 100 ft is §10's; `_walk_in`'s line credited the 4 ft step to 0246; the grove fallback's line held about 13.5 ft; the bands built from `groves` only - a village copse is `village_groves`, common ground, not a farm's own wood).
5. **The order.** The two "a house served" claims cite §10; `_walk_in` names its step as the code's; the band claim names the 13.5 ft; the bands' comment says why a copse is not among them.
6. **The exits.** (e) conform - words; the connector's inner end is `_pull_back_to_service`'s, the sweep's exemption standing.
7. **The search smell.** None.
8. **The budget.** 45 min for the batch with its landing.
9. **Done, measured.** The claims round reads them IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

## T55, T65, T73 - a lane end at the house it serves, join links at the page's 7 ft, the sweeps' notes (the T17 round; T28; batch 4's round)

### T55 Approach (checklist part A)

1. **The goal, in the world.** A lane end pulled back to the last house it serves stops beside that house, not up to 60 ft short of it.
2. **The constraints.** 0246 §6 (an end that reaches nothing is pulled back to the last house it serves, a GUESS; a lane a house needs ends at its dooryard); `water_ways._pull_back` and `trim_lane_stubs`.
3. **Where each comes from.** R (0246).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (impl-drift DRIFTED x2, the T17 round: `_pull_back` keeps the SHORTEST end still in reach, on the far edge of the house's 60 ft zone; a unit test shows the end at 440 where the house stands at 500).
5. **The order.** `_pull_back` takes `near`; among the ends that still reach the last thing served it keeps the one nearest it; `trim_lane_stubs` passes the distance to a served house's footprint (a way or a field keeps the old shortest end, already its junction or bund - a first cut measuring ways too collapsed a through lane onto a bar and failed three unit tests); the claim; the cohort.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 45 min for the batch with its landing.
9. **Done, measured.** One goal: the end held at the house (unit test); the quick cohort's fixed seeds and pinned rows 16/16; seeds 1-48 and the pinned rows 54/54; the measured block 645695-645742 the same 10 failures as before (D49's measure).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T55 Decisions

**D49 - nearest the house.** `_pull_back(..., near=None)`: with `near`, the kept end is the reaching one nearest the served thing; `trim_lane_stubs._nearness` gives a house's footprint distance (`dooryard_dist`), 0 for a way or a field; the claim reads "to the end nearest the last house it serves, else the shortest end still reaching a way or the field" (GUESS 0246).

<!-- plan-archive: T65 to T65 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T65 Decisions

**D50 - one margin for every lane.** `_detour_links`' first try, `_join_piece`'s bar and `_unjog`'s default at `WEB_FABRIC_GAP`; each claims 0246's 7 ft; the comments in `fabric.py` and `touch.py` record the change and its measurement.

### T73 Approach (checklist part A)

1. **The goal, in the world.** The sweeps' claims say what the page records.
2. **The constraints.** 0246 §10 (back lanes bring every farmhouse within 100 ft of one), §6, §78 (no lane through a farm's own wood), 0036.
3. **Where each comes from.** R (0246, 0036).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (impl-drift outside the change, batch 4's rounds: "a house served" said "where the page says 60 ft" though its 100 ft is §10's; `_walk_in`'s line credited the 4 ft step to 0246; the grove fallback's line held about 13.5 ft; the bands built from `groves` only - a village copse is `village_groves`, common ground, not a farm's own wood).
5. **The order.** The two "a house served" claims cite §10; `_walk_in` names its step as the code's; the band claim names the 13.5 ft; the bands' comment says why a copse is not among them.
6. **The exits.** (e) conform - words; the connector's inner end is `_pull_back_to_service`'s, the sweep's exemption standing.
7. **The search smell.** None.
8. **The budget.** 45 min for the batch with its landing.
9. **Done, measured.** The claims round reads them IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T73 Decisions

**D51 - the sweeps' words.** As the order says; no code token changes.
<!-- plan-archive: archived 2026-10-21 -->
### T76 Approach (checklist part A)

1. **The goal, in the world.** The findings the claims gate carried from batch 5 are claimed or relabeled.
2. **The constraints.** 0246 §34 (the pull-back a GUESS); the code's own figures.
3. **Where each comes from.** R (0246) and O.
4. **Do they describe the world here?** Yes - measured 2026-10-21 (the claims gate's carries, batch 5: `trim_lane_stubs`' pull-back claim not labeled GUESS; `_detour_links`' 150 ft reach and `_join_piece`'s refused-splice lane unclaimed; the two served-house claims are T75's, which waits on T78: the page does not state its serving test, and the plan review of D53 ruled that keeping the code's 100 ft for consistency is no reason to set §6 aside).
5. **The order.** The label and two claims.
6. **The exits.** (a) claim.
7. **The search smell.** None.
8. **The budget.** 40 min for the batch with its landing.
9. **Done, measured.** The claims round reads them IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T76 Decisions

**D54 - the carries claimed.** `trim_lane_stubs`' claim GUESS 0246; `_detour_links` claims `_ORPHAN_REACH` (UNRESEARCHED); `_join_piece` claims the refused splice drawn as its own lane (UNRESEARCHED).

### T77 Approach (checklist part A)

1. **The goal, in the world.** A landing whose claims round ends in carries alone pushes without a hand step.
2. **The constraints.** `make land`'s first pass files carries (405 T36); the claims wait (405 T50).
3. **Where each comes from.** O (feature 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (batch 5's landing: the wait asked on until `make claims-carry` was run by hand).
5. **The order.** `file_carries` lifted out of the first pass and asked in the wait when the gate refuses only carries; a test.
6. **The exits.** (c) - the landing does what it can.
7. **The search smell.** None.
8. **The budget.** 40 min for the batch with its landing.
9. **Done, measured.** A carry-only refusal is filed and committed in the wait; an owed claim is still waited on (test).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T79 Approach (checklist part A)

1. **The goal, in the world.** A landing stopped by hand leaves no gate or cohort running.
2. **The constraints.** `land.py`'s cleanup (`stop_cohort` in a `finally`, 405 T48); Python's default SIGTERM, which ends the process without running `finally`.
3. **Where each comes from.** O (feature 405) and Python.
4. **Do they describe the world here?** Yes - measured 2026-10-21: batch 6's landing, stopped with SIGTERM to fix a flaw its round found, left its gate (pytest) and its cohort running in this clone; they were ended by hand.
5. **The order.** `land.main` installs a SIGTERM handler raising SystemExit(143); a test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 10 min.
9. **Done, measured.** The handler is installed, stops the landing's own process group (the gate) and raises SystemExit(143) (test).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T79 Approach (re-answered 2026-10-21T14:52Z)

1. **The goal, in the world.** As before: a landing stopped by hand leaves no gate or cohort running.
2. **The constraints.** As before, and where each run lives: the gate (`make done`) in the landing's own process group, the cohort in its own session.
3. **Where each comes from.** O (feature 405) and Python.
4. **Do they describe the world here?** Yes - the plan review's aside, 2026-10-21: the first handler raised SystemExit alone, which stops the cohort through the `finally` but not the gate.
5. **The order.** The handler ignores SIGTERM, sends it to its own group and raises SystemExit(143); the test holds the group stopped.
6. **The exits.** (c) - a landing is stopped whole; a `make land` run in the foreground shares the group with its caller, which is stopped with it, as the person stopping the landing asked.
7. **The search smell.** None.
8. **The budget.** With the batch.
9. **Done, measured.** The handler stops the landing's group and raises SystemExit(143) (test).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T80 Approach (checklist part A)

1. **The goal, in the world.** `_join_piece` reads a lane with no width one way, and draws the link at the piece's width.
2. **The constraints.** 0081's 3 ft footpath; 0246 §16's 7 ft fence to the middle.
3. **Where each comes from.** R (0081, 0246).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (batch 6's round: `_bar` read a missing width as 5 ft and the link as 3; the link's width truncated by `int`; the bar's half-width-plus-2 term unclaimed).
5. **The order.** Both read 3 ft; the width rounded; the bar's wide-lane term claimed. The bar is `max(7, w/2 + 2)`, 7 ft at any width up to 10 ft, so no drawn lane moves.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 40 min for the batch with its landing.
9. **Done, measured.** The ways tests pass; the claims round reads `_join_piece` IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T80 Decisions

**D59 - one width.** `_bar` and the two link draws read `lanes[i].get("w") or 3.0`; the link drawn at `round(...)`; the claim names the bar's half-width-plus-2 term for a lane over 10 ft (UNRESEARCHED, none drawn here).

### T82 Approach (checklist part A)

1. **The goal, in the world.** A short link off a way walks on to the house it serves; only another way holds it.
2. **The constraints.** `_reaches` and "not the way it left" (an end does not count as reaching the way its far end stands on); 405 T74's walk-on.
3. **Where each comes from.** O (features 261, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (batch 6's round 3: `_near` held the walk within 60 ft of ANY way, the one the lane left included, so a link off a way stopped up to 60 ft past its house).
5. **The order.** `_near(q, far)` filters out the way the far end stands on (by `_TOUCH_GAP`), as `_reaches` does; `_walk_in` passes the lane's other end; the claim; "not the way it left" labeled GUESS 0246 (the page read and silent); a test; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 40 min for the batch with its landing.
9. **Done, measured.** A link off a way reaches its closest approach to the house, not the way's 60 ft edge (test); seeds 1-48 and the pinned rows pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T82 Decisions

**D58 - the way it left is no other way.** `_walk_in`'s `near` takes the lane's other end; `_sweep_dangling_ends._near` skips segments within `_TOUCH_GAP` of it.

### T20 Approach (checklist part A)

1. **The goal, in the world.** The touch a street's joints are judged at, and what counts as a joint, are claimed.
2. **The constraints.** 0246 §6 (an end runs on to a field path, a bund or another way).
3. **Where each comes from.** R (0246) and O.
4. **Do they describe the world here?** Yes - measured 2026-10-21 (385 T138's finding: `to_its_joints`' touch arrives from its callers unclaimed; whether field-path and bund ends count).
5. **The order.** Claims at `trim_streets` and `settle_street_ends`: the 4 ft touch (CONVENTION, the ink's), the anchors at 1 ft; a field path's end a joint (a field path is a lane); a street end at the bund no dangling end (`end_serves`), so never cut.
6. **The exits.** (a) claim.
7. **The search smell.** None.
8. **The budget.** 40 min for the batch with its landing.
9. **Done, measured.** The claims round reads them IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T20 Approach (re-answered 2026-10-21T15:19Z)

1. **The goal, in the world.** As before.
2. **The constraints.** As before.
3. **Where each comes from.** As before.
4. **Do they describe the world here?** Yes - the claims round, 2026-10-21: `trim_streets` never asks `end_serves`, so the bund clause was untrue; its touch claim named a 1 ft anchor it does not read.
5. **The order.** As D60 now reads.
6. **The exits.** (a) claim - words only.
7. **The search smell.** None.
8. **The budget.** With the batch.
9. **Done, measured.** The claims round reads the claims IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T08 Approach (checklist part A)

1. **The goal, in the world.** Whose farm gets a door path is claimed as the pages give it.
2. **The constraints.** 0033 (a door path for a near-row farm whose grove stands between it and its street); 0246 (every farmhouse reached by a way).
3. **Where each comes from.** R (0033, 0246).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (385 T111's finding: the code lays one for every grove farm no way arrives at).
5. **The order.** The claim: a door path wherever no way arrives (GUESS 0033), every farmhouse being reached by a way (0246), 0033's near-row case among them.
6. **The exits.** (a) claim - the wider rule is 0246's every-farmhouse rule applied; narrowing it to 0033's case would leave farms with no way.
7. **The search smell.** None.
8. **The budget.** 40 min for the batch with its landing.
9. **Done, measured.** The claims round reads it IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T20 Decisions

**D60 - the touch and the joints claimed.** `trim_streets` claims its joints' touch (the caller's `_TOUCH_GAP`, 4 ft, the ink's - CONVENTION; a front door's nearest point within `reach` a joint too) and a field path's end a joint (0246); `settle_street_ends` its 4 ft touch. The bund clause first written was dropped: `trim_streets` cuts to its joints and never asks `end_serves` (the claims round). No code token changes.

<!-- plan-archive: T08 to T08 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T08 Approach (re-answered 2026-10-21T15:19Z)

1. **The goal, in the world.** As before.
2. **The constraints.** As before.
3. **Where each comes from.** As before.
4. **Do they describe the world here?** Yes - the claims round, 2026-10-21: the new claim duplicated the unit's own, and 0246 answers it (every other farmhouse has a lane of its own from its dooryard).
5. **The order.** As D61 now reads.
6. **The exits.** (a) claim - words only.
7. **The search smell.** None.
8. **The budget.** With the batch.
9. **Done, measured.** The claims round reads the claims IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T27 Decisions

**D31 - the fixtures where they stand.** `_OVERLAP_EXEMPT['farm_fixtures']` reads "each seated on its own farmstead near its farmhouse - against a wall or a set step off it"; the exemptions' claim "yard, garden and fixtures beside the house" cites 0038 for the bed's sides and drops 0039 from it; `CANOPY_PAD` and `SHADE_MARGIN_FT` are claimed CONVENTION; `_seats` claims the front privy's 8 ft (GUESS, 0047) and the stable seat (0047: by the stable).


### T58 Decisions

**D33 - a move is not new.** `claims_owed.moved(cur, index)`: {new key: old key} where the `unit#claim` suffix matches, the old key is gone from the tree, the code fingerprints are equal and there is one such row; `owed` reads the old row for a moved key; `rekey` copies each row to its new key and drops the old ones; `make claims-rekey`, and `land.py`'s first pass runs it and commits the index.

## T57, T58 - `web.py` split at the bar, and the claim rows carried with it (T53's rule)

### T57 Approach (checklist part A)

1. **The goal, in the world.** `ways/web.py`, past the bar, is a package with room to grow, and nothing that imports it changes.
2. **The constraints.** The 1,000-line bar and T53's rule (split into ~650-line submodules, `__init__.py` re-exporting); the claims index, keyed by file; the tests' monkeypatches, which patch a name where it is looked up.
3. **Where each comes from.** O (features 173, 405 T53) and the GM (amendment 7).
4. **Do they describe the world here?** Yes - measured 2026-10-21: `web.py` stood at 1,001 lines after T17's claim split; 65 index rows were keyed to it; seven monkeypatches in `test_web.py` patched names the moved functions look up.
5. **The order.** `skeleton.py` (the skeleton and the cut lines), `tidy.py` (the end trims, `kept_connector` with them - `tidy` calls it), `stage.py` (`stage_web` and its runs), each with the import block it uses; `__init__.py` re-exporting every name; the monkeypatches pointed at the submodules; the package's CLAUDE.md and the `ways/` index row; `make claims-rekey`.
6. **The exits.** (c) - a split along the module's own three concerns.
7. **The search smell.** None.
8. **The budget.** 45 min with T58.
9. **Done, measured.** One goal: the `ways/` tests green (576), every submodule under 650 lines, the claim rows carried (61), the gate green.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T57 Decisions

**D32 - three submodules, one surface.** `ways/web/` = `skeleton` (`SKELETON_ARM_WIDTH`, `water_along_side`, `lane_skeleton_for`, `oriented_skeleton`, `_lay_skeleton`, `served_arm`, `_web_cut_lines`), `tidy` (`_drop_collapsed`, `cut_the_overruns`, `tidy_lane_ends`, `unsplitting_drops`, `kept_connector`), `stage` (`stage_web`, `seat_wall_reach`, `lay_reachable_runs`, `_reachable_runs`, `resettle_straightened`); `__init__.py` re-exports each name and the submodules themselves; each submodule keeps the module's `web plumbing - NONE`.

<!-- plan-archive: T58 to T58 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T58 Decisions

**D33 - a move is not new.** `claims_owed.moved(cur, index)`: {new key: old key} where the `unit#claim` suffix matches, the old key is gone from the tree, the code fingerprints are equal and there is one such row; `owed` reads the old row for a moved key; `rekey` copies each row to its new key and drops the old ones; `make claims-rekey`, and `land.py`'s first pass runs it and commits the index.

## T29, T28, T45 - the findings log closes, 385's rows mapped, the reference message (found and filed work)

### T29 Approach (checklist part A)

1. **The goal, in the world.** A feature's `found.jsonl` says, for every finding, whether it is filed (and as what) or settled (and why).
2. **The constraints.** `found.jsonl`, written by `record_owed` and the checks (open rows, never edited, 385); the found-work rule (the GM 2026-10-19, FR-002).
3. **Where each comes from.** O (feature 385) and the GM (FR-002).
4. **Do they describe the world here?** Yes - measured 2026-10-21: 385's 63 rows and 405's 13 all read `open`, filed or not; nothing wrote a row's outcome.
5. **The order.** `scripts/record/found.py` (`list`, `close --task | --why`), `make found-list` and `make found-close`; a test.
6. **The exits.** (c) - a row gains its outcome; nothing is deleted.
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** A row closes as filed (a task of 405, or of 385 - the two features the GM's routing names) or settled only where it no longer holds (the reason records the measurement), once; `list` counts what is open (test).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T29 Decisions

**D36 - a row's outcome on the row.** `found.py close` sets `status` to `filed` with `task` (`T61`, `385 T12` or `405 T17` - no other feature, the GM's routing), or `settled` with `why`, and `closed_utc`; it refuses a row already closed. SETTLED ONLY WHERE THE FINDING NO LONGER HOLDS (the plan review of D36, FR-002): the reason starts "no longer holds" and records what was measured against the current file; a finding that still holds is filed as a task. `found.py list` numbers the open rows in file order.

<!-- plan-archive: T28 to T28 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T28 to T45 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T45 Decisions

**D38 - the offer removed.** `_reference`'s served line reads "served from the roll cache: nothing the roll executes changed" without "GATE_NO_CACHE=1 rolls it".

## T62, T63, T69 - the run-on to the paddy, the arm trims against what they reach, the cut lines' houses (the T17 batch's round 2; T28)

### T62 Approach (checklist part A)

1. **The goal, in the world.** An inner lane that runs on to the field ends at the paddy's bund, not on a dry plot's edge.
2. **The constraints.** 0081's drawing page ("the settlement's own inner lanes may end in the cluster or at the paddy"; only the spur to the fields stops at the hem's edge); 0014 (the path joins the paddy's outer bund); `bund.run_lanes_on_to_the_bund` and `paddy_ground`.
3. **Where each comes from.** R (0081, 0014).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (impl-drift, the T17 batch's round 2): the run-on carries an inner lane's end to `ground.nearest`, the worked ground's, a dry plot's edge included.
5. **The order.** The run-on target read on the paddy (`paddy_ground`), the pull out of the worked ground unchanged; its claim; the unit tests; the gate and the cohort.
6. **The exits.** (e) conform - the research names the paddy.
7. **The search smell.** None.
8. **The budget.** 30 min for the batch with its landing.
9. **Done, measured.** One goal: a run-on aims at the paddy, never a dry plot (test); the cohort refuses no seed against main.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T62 Decisions

**D39 - the paddy, not the hem.** `run_lanes_on_to_the_bund` aims `run_on_target` at `paddy_ground(s)` (built once a pass); an end standing in the worked ground is still pulled out of it; the claim "the dry hem's edge too" becomes "to the paddy" (0081).

<!-- plan-archive: T63 to T63 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T63 to T69 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T69 Decisions

**D41 - said where it is done.** `_web_cut_lines`' claim "a web lane's span" adds that its arcs and stands are every house but one reached across a yard (`stage_web` leaves those out).

<!-- plan-archive: T72 to T72 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T64 to T28 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->

## T55, T65, T73 - a lane end at the house it serves, join links at the page's 7 ft, the sweeps' notes (the T17 round; T28; batch 4's round)

### T55 Approach (checklist part A)

1. **The goal, in the world.** A lane end pulled back to the last house it serves stops beside that house, not up to 60 ft short of it.
2. **The constraints.** 0246 §6 (an end that reaches nothing is pulled back to the last house it serves, a GUESS; a lane a house needs ends at its dooryard); `water_ways._pull_back` and `trim_lane_stubs`.
3. **Where each comes from.** R (0246).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (impl-drift DRIFTED x2, the T17 round: `_pull_back` keeps the SHORTEST end still in reach, on the far edge of the house's 60 ft zone; a unit test shows the end at 440 where the house stands at 500).
5. **The order.** `_pull_back` takes `near`; among the ends that still reach the last thing served it keeps the one nearest it; `trim_lane_stubs` passes the distance to a served house's footprint (a way or a field keeps the old shortest end, already its junction or bund - a first cut measuring ways too collapsed a through lane onto a bar and failed three unit tests); the claim; the cohort.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 45 min for the batch with its landing.
9. **Done, measured.** One goal: the end held at the house (unit test); the quick cohort's fixed seeds and pinned rows 16/16; seeds 1-48 and the pinned rows 54/54; the measured block 645695-645742 the same 10 failures as before (D49's measure).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T55 Decisions

**D49 - nearest the house.** `_pull_back(..., near=None)`: with `near`, the kept end is the reaching one nearest the served thing; `trim_lane_stubs._nearness` gives a house's footprint distance (`dooryard_dist`), 0 for a way or a field; the claim reads "to the end nearest the last house it serves, else the shortest end still reaching a way or the field" (GUESS 0246).

<!-- plan-archive: T65 to T65 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T65 to T73 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T73 Decisions

**D51 - the sweeps' words.** As the order says; no code token changes.

## T74, T76, T77 - the sweeps' end at the house, the carried claims, carries filed in the wait (batch 5's rounds)

### T74 Approach (checklist part A)

1. **The goal, in the world.** A lane end the sweeps walk in stops beside the house it serves, as T55 made the trims do.
2. **The constraints.** 0246 §6 (a lane ends at the dooryard; the pull-back a GUESS); `sweeps._walk_in`; the 269 E4 hold at a junction.
3. **Where each comes from.** R (0246) and O (features 269, 405 T14).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (impl-drift DRIFTED, batch 5's round: `_walk_in` stops at the first point that reaches, the far edge of the house's 60 ft zone; unit tests show the end at 552 for a house at 500 and T14's tests pinned 84.0 and -208.0).
5. **The order.** `_walk_in` takes `near`; after the end first reaches it walks on while it still reaches and comes nearer a house it serves, held at a junction; `_near` is infinite within reach of another way, so a junction end stays; T14's two tests updated to the house (64.0 short of the connector's reach, -152.0); a unit test; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 40 min for the batch with its landing.
9. **Done, measured.** One goal: the end held beside the house (unit test); a junction end not moved (the existing tests); seeds 1-48 and the pinned rows pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T74 Approach (re-answered 2026-10-21T14:50Z)

1. **The goal, in the world.** As before: a swept lane end stops beside the house it serves.
2. **The constraints.** As before, and the dooryard carry's reach (2 x `_REACH_FT`, 120 ft), which bounds the houses an end may walk toward.
3. **Where each comes from.** R (0246) and O (features 269, 405 T14).
4. **Do they describe the world here?** Yes - batch 6's round, 2026-10-21: `_near` measured to the nearest owed house at any distance, so an end reaching only the field could be walked toward a house it does not serve; and the walk-on itself was unclaimed.
5. **The order.** `_near` bounded to houses within the carry's reach; the walk-on claimed; seeds 1-48 again.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** With the batch.
9. **Done, measured.** Seeds 1-48 and the pinned rows 54/54 on the bounded walk (2026-10-21); the claims round reads the walk-on IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T74 Decisions

**D52 - on to the house.** `_walk_in(pts, reaches, tails, near=None)` walks on, 4 ft at a time, while `reaches` holds and `near` falls; `_sweep_dangling_ends` passes `_near` (the nearest owed house within the dooryard carry's 120 ft, infinite within `_REACH_FT` of another way - an end reaching only the field is never walked toward a house it does not serve, batch 6's round); the claims "held nearest the house it serves" (GUESS 0246) and "walked on to the house it serves".

<!-- plan-archive: T76 to T76 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T76 to T77 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T77 Decisions

**D55 - carries filed in the wait.** `land.file_carries(root, d)`; `wait_for_claims(root, tasks, d)` runs it when the gate's refusal holds carries and no owed or introduced finding, then asks again.

<!-- plan-archive: T79 to T79 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T79 to T79 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T79 Decisions

**D56 - SIGTERM runs the cleanup.** `land.main` installs a SIGTERM handler first: it ignores SIGTERM, sends it to its own process group (the gate, `make done`, runs there) and raises SystemExit(143), so `long_runs`' `finally` stops the cohort's own process group too.

### T08 Decisions

**D61 - the existing claim holds.** `lay_door_paths`' own claim "every grove farm reached at its door" (0246, 0081) already says whose farm gets a door path - 0246 gives every other farmhouse a lane of its own from its dooryard, so the claims round read the new claim as a duplicate of it and as 0246's, not a GUESS: no claim is added; 0033's near-row case is one of 0246's.

## T44 - the red-gate hold reaches every gate (amendment 4)

### T44 Approach (checklist part A)

1. **The goal, in the world.** After a second red gate in a row, no gate runs - typed, inside `make land` or from any other wrapper - until the round arbiter has ruled on it.
2. **The constraints.** Feature 375 FR-010/FR-011 (the red-gate tripwire, its ruling before the next gate); `ci/state.py::second_red_gate`, which writes the trigger (engine code, unchanged here); `hm_arbiter.blocking(gate=True)`; the hook's hold on a typed `make done` (`hm_checks.py`); `make land` (405 T33), whose gate is a subprocess no hook sees; the `ARBITER_OK` escape.
3. **Where each comes from.** O (features 375, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21: the 04:51 and 05:02 gates were red in a row; `arbiter-owed.json` holds `red-gate@2026-10-21T05:02:38Z`, never ruled; the 05:09 `make land` ran the gate green and landed past it.
5. **The order.** A `gate-held` verb in `hm_arbiter.py` (the hook's own question and refusal text); the `done` recipe asks it first, before the gate lock; `land.py` names it among its cheap refusals when the landing carries engine code; tests; the guard table's row.
6. **The exits.** (c) - the gate's own first step is the one place every route passes; adding `land` to the hook's pattern alone was weighed and refused (a landing with no engine code runs no gate and must not be held).
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: with a red-gate trigger owed, `make done` refuses in its first step naming the trigger and the arbiter's commands, `land.py`'s cheap refusals name it on an engine landing and not on a tooling one, and `ARBITER_OK` passes; live, this task's own landing meets the 05:02 trigger and is held until it is ruled (tests and the live refusal).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T44 Decisions

**D18 - the gate asks.** `hm_arbiter.py gate-held` exits 1 printing `refusal(blocking(root, gate=True))` while a red-gate trigger of the active feature is owed. The `done` recipe runs it as its first step (an `ARBITER_OK=<reason>` passes and is logged as an escape), so `make land`, `idle-tests` and a typed `make done` all meet it; `land.py`'s cheap refusals ask it when the landing carries engine code, so the refusal comes with the others before anything runs. The trigger's writer (`ci/state.py`) is unchanged.

<!-- plan-archive: T46 to T43 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->

## T60 - another feature's requirement, named by its feature (found landing the T17 batch)

### T60 Approach (checklist part A)

1. **The goal, in the world.** A carried claims finding filed into any feature's task list passes that feature's spec-lint.
2. **The constraints.** spec-lint's check 4 (a task citing an id its spec lacks, feature 236); the claims carry (385 amendment 3, 405 T36), which names 385's requirement in the task it files.
3. **Where each comes from.** O (features 236, 385, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21: `make land` for the T17 batch ran the gate, and its preflight's spec-lint refused 405's T59, filed by the carry with 385's bare id.
5. **The order.** The carry names the id with its feature; spec-lint skips an id named by its feature (three digits, or "NNN's", just before it); tests.
6. **The exits.** (c) - both: the carry's words and the lint's reading.
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: "385 FR-013" in a task passes 405's spec-lint, a bare unknown id still fails (test); the carry's text and its tests name 385.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T60 Decisions

**D34 - named by its feature.** `claims_carry`'s three texts cite "385 FR-013"; `spec-lint.check_stale_tasks` skips an id preceded by a feature number (`NNN ` or `NNN's `); T59's line reads "385 FR-013".

<!-- plan-archive: T61 to T17 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->

### T54 Approach (checklist part A)

1. **The goal, in the world.** A row village's first street runs on off the map as the road into it; a further street is pulled back to the last way or farm it serves.
2. **The constraints.** 0033's drawing page: "The street runs on off the map as the road into it", further streets run parallel to the first and the page says nothing of their ends; 0246: an end reaching nothing is pulled back to the last house it serves (a GUESS).
3. **Where each comes from.** R (0033, 0246).
4. **Do they describe the world here?** Yes - measured 2026-10-21: Kashikawa's first street is 2,928 ft and uncut (the task's "2,800 to 1,400" read a layout before the road's two runs, feature 328 wave 5); it escapes `trim_streets` only because the road runs' ends stand on its ends (batch 7's round).
5. **The order.** `trim_streets` and `settle_street_ends` pass by the row's first street by name (`first_street`: the lowest `street_index` drawn - only it takes the road, `lay_row_streets`); `to_its_joints` / `end_to_its_joint` / `settle_street_ends` claims labeled GUESS 0246 for a further street's cut; tests; seeds 1-48.
6. **The exits.** (e) conform, with the claims.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** The first street is never cut by the trim or the settle, joints or none (tests); seeds 1-48 and the pinned rows pass; the pool's first streets unchanged.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
## T57, T58 - `web.py` split at the bar, and the claim rows carried with it (T53's rule)

### T57 Approach (checklist part A)

1. **The goal, in the world.** `ways/web.py`, past the bar, is a package with room to grow, and nothing that imports it changes.
2. **The constraints.** The 1,000-line bar and T53's rule (split into ~650-line submodules, `__init__.py` re-exporting); the claims index, keyed by file; the tests' monkeypatches, which patch a name where it is looked up.
3. **Where each comes from.** O (features 173, 405 T53) and the GM (amendment 7).
4. **Do they describe the world here?** Yes - measured 2026-10-21: `web.py` stood at 1,001 lines after T17's claim split; 65 index rows were keyed to it; seven monkeypatches in `test_web.py` patched names the moved functions look up.
5. **The order.** `skeleton.py` (the skeleton and the cut lines), `tidy.py` (the end trims, `kept_connector` with them - `tidy` calls it), `stage.py` (`stage_web` and its runs), each with the import block it uses; `__init__.py` re-exporting every name; the monkeypatches pointed at the submodules; the package's CLAUDE.md and the `ways/` index row; `make claims-rekey`.
6. **The exits.** (c) - a split along the module's own three concerns.
7. **The search smell.** None.
8. **The budget.** 45 min with T58.
9. **Done, measured.** One goal: the `ways/` tests green (576), every submodule under 650 lines, the claim rows carried (61), the gate green.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T57 Decisions

**D32 - three submodules, one surface.** `ways/web/` = `skeleton` (`SKELETON_ARM_WIDTH`, `water_along_side`, `lane_skeleton_for`, `oriented_skeleton`, `_lay_skeleton`, `served_arm`, `_web_cut_lines`), `tidy` (`_drop_collapsed`, `cut_the_overruns`, `tidy_lane_ends`, `unsplitting_drops`, `kept_connector`), `stage` (`stage_web`, `seat_wall_reach`, `lay_reachable_runs`, `_reachable_runs`, `resettle_straightened`); `__init__.py` re-exports each name and the submodules themselves; each submodule keeps the module's `web plumbing - NONE`.

<!-- plan-archive: T58 to T58 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T57 to T08 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T54 Decisions

**D63 - the first street passed by.** `trim_streets` and `settle_street_ends` both skip the street with the lowest drawn `street_index` (the one that met the road, `first_street`): 0033 runs it on off the map as the road into it, and no 0246 pull-back is put in its place. A further street is cut to its joints, and its dangling end to its last joint, as before. Measured on seeds 1-48 and the pinned rows: a first street whose end the settle would have cut would now be left to the law, so a seed that needed that cut fails the cohort. The claims: `to_its_joints`, `end_to_its_joint` and `settle_street_ends` GUESS 0246 (a further street); `trim_streets`' "the first street runs on" true by the code.

### T83 Approach (checklist part A)

1. **The goal, in the world.** The sweep and the door path agree on where a grove farm's wood stands.
2. **The constraints.** 0036 / 0033: no lane runs through a farm's own wood, its grove and its share of the dooryard copse counted as one wood (0036); the grove band is recorded with its rotation (`rot`).
3. **Where each comes from.** R (0036, 0033) and O (the manifest's band).
4. **Do they describe the world here?** Yes - batch 7's round: `_sweep_dangling_ends` builds axis-aligned boxes from `x, y, w, h`, `lay_door_paths` `rot_rect(..., rot)`.
5. **The order.** The sweep's bands as `rot_rect(x, y, w, h, rot)`, and the farm's share of the dooryard copse with them (0036: one wood); the stale "their boxes are unrotated" comment goes; the claims cite 0036; a test with a rotated band and a copse clump.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** A carry across a rotated band's true footprint is refused, one across the unrotated box's phantom corner is not (test); seeds 1-48 pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T83 Decisions

**D64 - one band, and the farm's whole wood.** `_sweep_dangling_ends`' `_bands` = `farm_bands(M)`: each grove band `rot_rect(g["x"], g["y"], g["w"], g["h"], g.get("rot") or 0.0)`, ungrown (the sweep asks only whether a carry crosses the wood; the door path's grow is its own tread's clearance), and each clump of the dooryard copse (`village_groves` role `copse`) as an octagon of its radius - 0036 counts a farm's grove and its share of the copse as one wood, its clumps kept beside its house and free of lanes (the claims round: 405 T73 had left the copse out as common ground, which 0036 does not say). The "grove band not crossed" claims cite 0036.

### T84 Approach (checklist part A)

1. **The goal, in the world.** The splice keeps a lane as far off the fabric as before, measured along the fabric's edges, not only at its corners.
2. **The constraints.** 0246 §41: a lane's middle 7 ft from a garden fence; `_join_piece`'s rule - the splice no nearer the fabric than the piece was, or than its bar.
3. **Where each comes from.** R (0246) and O (feature 134 T50).
4. **Do they describe the world here?** Yes - batch 7's round: `_clear_within` measures fabric VERTICES to the run, so a run passing a long fence between two far corners reads clear.
5. **The order.** `_clear_within` measures the run's segments against the fabric's EDGES, filed boxed once (`_fabric_edges`), segment to segment (0 where they cross), capped at the bar as before; the oracle test's old scan becomes segment to segment; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** A run past a long edge's middle reads its true clearance (test); the index equals the full segment scan below the cap (test); seeds 1-48 pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T84 Decisions

**D65 - edges, not corners.** `_fabric_edges(fab)` files each polygon edge as `(a, b, box)` in a `PointGrid`; `_clear_within(run, edges, cap)` takes the least segment-to-segment distance (0 where `segments_cross`), queried at samples every `cell` along each run segment, padded `cap + cell/2 + 1` - exact below the cap (the nearest pair's point on the run lies within half a cell of a sample, its partner within `cap` of that point, so inside the edge's box padded by the query). Maps may change (the splice is stricter).

### T85 Approach (checklist part A)

1. **The goal, in the world.** An unwidthed lane is judged as the 3 ft footpath it is drawn as, wherever a join reads its width.
2. **The constraints.** 0246 §43: a footpath 3 ft; `_one_network` and `_join_piece` read `or 3.0`.
3. **Where each comes from.** R (0246).
4. **Do they describe the world here?** Yes - batch 7's round 3: `_touch_junctions` reads `or 5.0` in its two bars and in `may_write`'s stroke.
5. **The order.** `or 5.0` -> `or 3.0` at the three places in `_touch_junctions`; the claim; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** The three reads agree (grep); seeds 1-48 pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T83 Approach (re-answered 2026-10-21T16:24Z)

1. **The goal, in the world.** The sweep and the door path agree on where a grove farm's wood stands, and that wood is the farm's grove and its share of the dooryard copse.
2. **The constraints.** 0036: a farm's grove and its share of the dooryard copse are one wood, its clumps kept beside its house and free of lanes; 0033: a near-row farm's path walks round its grove; the band is recorded with its rotation.
3. **Where each comes from.** R (0036, 0033) and O (the manifest's band and copse clumps).
4. **Do they describe the world here?** Yes - batch 8's claims round: the sweep read unrotated boxes and left the copse out as common ground, which 0036 does not say.
5. **The order.** `farm_bands(M)`: each band rotated, and each farm's share of the copse - every copse clump, each seated beside its own house - as an octagon of the clump radius; the claims cite 0036; a test.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** With batch 8.
9. **Done, measured.** A rotated band and a copse clump read as the wood (test); seeds 1-48 and the pinned rows 54/54 (measured 2026-10-21).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T85 Decisions

**D66 - a footpath is 3 ft.** `_touch_junctions` reads an unwidthed lane as 3 ft (its bars are unchanged: max(7, w/2 + 2) is 7 below 10 ft; `may_write`'s stroke narrows to the drawn tread).

### T87 Approach (checklist part A)

1. **The goal, in the world.** The archive and the decide guard read a plan block the same way.
2. **The constraints.** `_section_clear` (T81), which forgives a typo-scale change from the reviewed text; `archivable`, which read the exact digest.
3. **Where each comes from.** O (features 375, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21: after batch 7's landing T81's ticked sections stayed in plan.md.
5. **The order.** `archivable` asks `_section_clear(review, sec, History(plan))`; a test, red on the unfixed archive.
6. **The exits.** (c) - one reading.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** A ticked section a blank line from its reviewed text is archived (test, red before).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T87 Decisions

**D67 - the archive reads as the guard does.** `archivable`'s per-block exact-digest test replaced by `_section_clear` with the plan's history.

<!-- plan-archive: T83 to T83 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T90 Approach (checklist part A)

1. **The goal, in the world.** A landing stopped by hand stops its gate and cohort.
2. **The constraints.** T79's SIGTERM handler, which runs only in the python `land.py`.
3. **Where each comes from.** O (feature 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21: stopping batch 8's landing, the SIGTERM went to the recipe's `sh -c` (the first process match), the handler never ran and the gate ran on.
5. **The order.** `land.py --stop` (`make land-stop`) SIGTERMs this tree's python running `scripts/land.py`, never its own; a test on a fake `/proc`.
6. **The exits.** (c) - a command, not a habit.
7. **The search smell.** None.
8. **The budget.** With batch 8.
9. **Done, measured.** Only the python in this tree is found (test); `make land-stop` with none running says so.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T90 Decisions

**D68 - stop the landing by its python.** `landing_pids(root)` reads `/proc`: a process whose argv[0] is a python, whose first argument ends `scripts/land.py`, whose cwd is the tree, and which is not the caller; `make land-stop` SIGTERMs each.

### T18 Approach (checklist part A)

1. **The goal, in the world.** A lane keeps 7 ft off every garden but its own household's.
2. **The constraints.** 0246: the gap is kept from another household's garden; a household's own way may run beside its own fence, kept only off the beds (a DEVIATION the page records).
3. **Where each comes from.** R (0246).
4. **Do they describe the world here?** Yes - T108's round: `settle.theirs` exempts every steading within `DOORSTEP_FT` (80 ft) of either end, a neighbor's garden at a junction too.
5. **The order.** `theirs` exempts at each end only the farmhouse that end reaches as 0246 measures it (`law.reach_to_steading`), the nearest where two do; the claim GUESS 0246; a test with a neighbor beside the junction and a farm past the reach; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** A neighbor's garden within 80 ft of an end is no longer exempt (test); seeds 1-48 and the pinned rows pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T18 Decisions

**D69 - its own household only.** A lane's household is the one its RECORD names - `of` (a household's way the tree draws) or `serves` (a grove farm's door path), `geom.lane_owner` - and only a lane that names one exempts that household's yards and gardens from the fence gap (`theirs(yards, owner)`); a back lane, a cross lane, the track out name none and keep the gap off every garden (0246: the gap is kept from another household's garden, and "a household's own way" may run beside its own - the claims round: an owner read from an end's reach gave back and cross lanes one). The owner reaches every place a household's way is judged: `Lawful.owner` set on a copy by `tree.admits` and `lay_door_paths`, a run replacing a lane (`skip`) is that lane's, `settle_ends`' re-aim and `last_resort` pass their lane's. Measured on seeds 1-48 and the pinned rows (54/54, 2026-10-21); the claim cites 0246.

### T86 Approach (checklist part A)

1. **The goal, in the world.** The join links' 7 ft keep is claimed as what it is.
2. **The constraints.** 0246 §41: the gap is kept from another household's garden; a household's own way may run beside its own fence (a DEVIATION the page records).
3. **Where each comes from.** R (0246).
4. **Do they describe the world here?** Yes - batch 7's round 3: `_clear_touch` / `_clear_within` keep a join link 7 ft from all fabric, own garden included.
5. **The order.** A claim at `_clear_touch` and `_join_piece`: a join link keeps the gap from every garden - GUESS 0246: a link joins a way to the network and belongs to no one household, so no garden is its own.
6. **The exits.** (a) claim.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** The claims round reads it IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T86 Decisions

**D70 - a join link has no household.** No code change: a join link closes a gap between two ways and belongs to no one household, so the own-garden exemption (0246's DEVIATION for a household's own way) does not reach it; claimed GUESS 0246 at `_clear_touch` and `_join_piece`.

### T89 Approach (checklist part A)

1. **The goal, in the world.** Every tolerance a join reads is claimed.
2. **The constraints.** The ink's touch (`_TOUCH_GAP`, 4 ft, CONVENTION).
3. **Where each comes from.** O.
4. **Do they describe the world here?** Yes - batch 8's round: `_touch_junctions` leaves an end within 2 ft of a way as it is, unclaimed.
5. **The order.** A claim: an end within 2 ft of a way already stands on it - CONVENTION, half the ink's touch: moving it would draw a link shorter than the tread.
6. **The exits.** (a) claim.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** The claims round reads it IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T18 Approach (re-answered 2026-10-21T17:14Z)

1. **The goal, in the world.** A lane keeps 7 ft off every garden but its own household's, and a lane has one household.
2. **The constraints.** 0246: the gap is kept from another household's garden; a household's own way leaves its own dooryard round its beds and joins a way at a T; an end reaches a farmhouse within 60 ft of the house or 12 ft of its built ground (the page's GUESS).
3. **Where each comes from.** R (0246).
4. **Do they describe the world here?** Yes - the claims rounds: every steading within 80 ft of either end was exempt, then a farmhouse at each end, so a door path's junction end exempted the neighbor beside it.
5. **The order.** `theirs` exempts only the farmhouse nearest an end among those its ends reach (`law.reach_to_steading`); the claim GUESS 0246; tests with a neighbor beside the junction and a farm past the reach; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** With batch 9.
9. **Done, measured.** A neighbor beside the junction end keeps the gap, a farm 75 ft off is no household's own (tests); seeds 1-48 and the pinned rows pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T89 Decisions

**D71 - an end already on a way.** No code change: `_touch_junctions`' 2 ft claimed CONVENTION (an end that near a way already reads as on it at the map's scale; a link under 2 ft is shorter than any tread).

### T22 Approach (checklist part A)

1. **The goal, in the world.** A way reaches the field only where it joins the paddy's bund, as 0014 draws it.
2. **The constraints.** 0014: the field path runs from the hamlet to the paddy's outer bund and joins it; a lane end within 6 ft of the paddy's edge is drawn as joining it (a GUESS); where no path is left to draw, the hamlet's nearest lane runs on to the bund.
3. **Where each comes from.** R (0014).
4. **Do they describe the world here?** Yes - T33's rounds: `law.FIELD_REACH_FT` (60 ft) counts a way that far off as reaching the field, five claims DRIFTED on it; `track.SPUR_REACH_FT` the same 60 ft for a folded spur.
5. **The order.** `FIELD_REACH_FT` 60 -> 6 ft (0014's join, a GUESS); `SPUR_REACH_FT` reads it; the claims at `FIELD_REACH_FT`, `field_unreached`, `refuse_unreached`, `settle_field`, `settle_reach` and the spur; a dry plot's edge still counts (the field's dry hem, worked ground the path may end on - 0014 is silent on dry plots: GUESS); tests; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** A way 10 ft off the paddy no longer reaches it (test); seeds 1-48 and the pinned rows pass - the settle draws the field way where none joins.
10. **Before moving a constant.** Measured: the reach is read by `field_unreached`, `settle_field`, `refuse_unreached`, the tree's pruning and the folded spur; seeds 1-48 and the pinned rows say what the move costs.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T18 part B (2026-10-21T17:38Z)

Owed by the cohort (cohort@20261021T172647Z, then cohort@20261021T173654Z: seeds newly failing), taken while T18 was the active task.

1. **What is refusing?** The cohort: with a lane's household read from its record (`of`, `serves`) and no exemption for a lane without one, seeds 12, 21, 22, 24, 38 and 901 failed - `Lawful` judged a household's way before it was a lane record (no owner), so its own garden kept the gap and the tree could not draw it (seed 12: 13 farmhouses unreached). With the owner set by the tree's `admits` and the door paths, three remained (21, 24, 38: `lane_knots`) - the knots' and the ends' repairs judged an existing household way without its owner.
2. **A3 again.** Unchanged: 0246 gives the own-garden exemption to "a household's own way"; a back or cross lane belongs to no household (the claims round).
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Changing: the owner reaches every place a household's way is judged - `Lawful.owner` set on a copy by `tree.admits` and `lay_door_paths`, a run replacing a lane (`skip`) is that lane's, the ends' re-aim passes its lane's owner.
6. **The one-sentence test.** "Only a household's own way runs beside its own garden" - true by the tests.
7. **The next step is a measurement.** Seeds 1-48 and the pinned rows.
8. **Every route measured before offering one?** The geometric owner (the farmhouse an end reaches) was measured 54/54 and judged DRIFTED; the record owner is the page's.
9. **After a ruling: the step it names?** No ruling yet; the claims round's third round on `theirs` goes to the round arbiter before the next check.

<!-- plan-archive: archived 2026-10-21 -->
### T22 Decisions

**D72 - the field reached at 6 ft.** `law.FIELD_REACH_FT = 6.0` (0014: a lane end within 6 ft of the paddy's edge is drawn as joining it, a GUESS); `track.SPUR_REACH_FT = law.FIELD_REACH_FT`, one distance for the law and the placer. A dry plot's edge counts as the field's (GUESS: the dry hem is the field's worked ground; 0014 speaks of the paddy and says nothing of the dry plots). Where no way joins, the settle's field way (`settle_field`, 0014's "the hamlet's nearest lane runs on to the bund") draws one; a map it cannot draw is refused, as now.

### T23 Approach (checklist part A)

1. **The goal, in the world.** A spur's tip never stands short of the bund in open ground.
2. **The constraints.** 0014: the path never ends in open ground short of the bund; where no path is left to draw, the hamlet's nearest lane runs on to it; 0246: an end reaching nothing is pulled back (a GUESS).
3. **Where each comes from.** R (0014, 0246).
4. **Do they describe the world here?** Yes - T33's round: `tip_onto_the_bund` returns a tip it cannot carry on (past the run-on's reach, turning back, or blocked) as it came.
5. **The order.** The fallback named in the claim: a tip the run-on cannot carry is left for the settle - the law calls a short end dangling and 0246's pull-back takes it, and the field is reached by `a_way_onto_the_bund` (0014's nearest lane run on); no code change.
6. **The exits.** (a) claim, the fallback named.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** The claims round reads it IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T18 Approach (re-answered 2026-10-21T17:42Z)

1. **The goal, in the world.** Only a household's own way runs beside its own garden; every other lane keeps 7 ft off every garden.
2. **The constraints.** 0246: the gap is kept from another household's garden; "a household's own way" may run beside its own fence; a back lane or cross lane is laid after the household ways and belongs to no household.
3. **Where each comes from.** R (0246) and O (the lane's record: `of`, `serves`).
4. **Do they describe the world here?** Yes - the claims rounds (three): every steading within 80 ft, then the farmhouse an end reaches, each gave lanes owners the page does not; the record owner is the page's.
5. **The order.** `geom.lane_owner` from the record; `theirs(yards, owner)`; `fouled_segment(..., owner)`; `Lawful.owner` and the `skip` lane's owner; the tree's `admits`, the door paths, the ends' re-aim and the last resort pass theirs; tests; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** The first record-owner roll failed six seeds - measured (part B), not searched: the owner was missing where a household's way is judged before it is a record.
8. **The budget.** With batch 9.
9. **Done, measured.** A household's own way exempts its own garden, a back lane none (tests); seeds 1-48 and the pinned rows 54/54 (measured 2026-10-21).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
## T41 - the gate runs beside the claims round (E)

### T41 Approach (checklist part A)

1. **The goal, in the world.** The gate and the landing cohort can start as soon as the code is final and run while the claims round settles the claims, so the landing waits for whichever is longer, not for both.
2. **The constraints.** The gate's tree check (375 FR-004: a run that saw half of one change vouches for neither); the gate-write guard (385 FR-010); the stamp's semantic id (features 133, 385 T57: a docstring or comment edit is not a change the gate exercised; the `page` and `browser` areas hash bytes).
3. **Where each comes from.** O (features 133, 375, 385).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T14): the claims round's edits were docstring claims and records, none of which the gate exercises, yet the guard refused the records and the docstring edits voided a running gate (5 min of machine time, killed).
5. **The order.** One predicate, "a move the gate does not see": a `.py` change whose semantic id is unchanged and that is in no byte-hashed area, or a path among the claims round's records; the tree check passes such moves (HEAD may move by commits holding only them); the gate-write guard passes the claims round's targets and a commit, add, Edit or Write whose changes are all such moves; tests.
6. **The exits.** (c) - the stamp's own semantic id decides, so the gate's tree check and its stamp cannot disagree; widening to any file was weighed and refused.
7. **The search smell.** None.
8. **The budget.** 60 min.
9. **Done, measured.** One goal: with a gate of this tree running, `make claims-checked`, a commit of a docstring-only engine edit with the claims index, and an Edit of a claim docstring pass the guard, and the tree check reads that run as unmoved; a code-token edit, or a record outside the list, still refuses and still voids it (tests).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T41 Decisions

**D15 - a move the gate does not see.** `preflight.unseen(root, path, old, new)`: a `.py` file outside the `page`/`browser` areas whose `gate-stamp.semantic_bytes` are equal, or a path in the claims round's records (`dev/claims-index.json`, `dev/claims-pages.json`, `dev/review-ledger.md`, and the ACTIVE feature's `found.jsonl`, `arbiter.jsonl`, `claims-carried.jsonl` and `tasks.md` - the last the claims carry's box (385 FR-013); no feature's `plan.md`, which the gate's spec-lint reads). The tree snapshot keeps every differing file's blob; the check compares the before and after trees across a HEAD move and calls the run moved only when a path that differs is not unseen. The gate-write guard lets `make claims-checked`, `claims-triaged` and `append` through, and a `git add`/`git commit`, Edit or Write when every resulting change is unseen (an Edit's result is computed from its old and new strings).

### T36 part B (2026-10-21T04:41Z)

Owed by the round arbiter's ruling on hour:405-engine-findings-from-385@4 (continue), taken while T36 was the active task.

1. **What is refusing?** Nothing in the code: tests/tooling (2085) and hooks-test green. `make land` refused once, on the hour's step-back.
2. **A3 again.** Unchanged: the found-work rule (G), FR-010 and FR-013 (O).
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: D10-D15 as reviewed.
6. **The one-sentence test.** "A finding outside the change is filed, not refused" - true by the tests.
7. **The next step is a measurement.** `make land` on T36-T41, then T11 measured against T14.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** Yes - land T36-T41, then T11; WEB_REACH_FT's source asked first.

## T43 - the hourly step-back suspended (amendment 4)

### T43 Approach (checklist part A)

1. **The goal, in the world.** A claim task runs start to landed with no hourly step-back, and the step-back comes back with one command, its machinery intact.
2. **The constraints.** The GM's words (amendment 4: "suspend but not remove"); feature 383's checkpoint (`scripts/reviews/checkpoint.py`, FR-011's hold on `make tick`, the `due` refusal of a gate or a dispatch); the tripwire rulings of feature 375 (round, reversal, cascade, red gate), which the GM kept; `dev/switches.json`, read by engine code (`l7r/diagram/switches.py`) that names only `remote`.
3. **Where each comes from.** O (features 375, 383) and the GM (amendment 4).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (`landing-analysis-3.md`): in 405 four hourly firings changed no route and made no fix, and the last 11 rulings across features were all `continue` with nothing.
5. **The order.** The switch file and its reader in `checkpoint.py`; `state()` reports the hour never due while suspended (which quiets `hold`, `due` and `open`); `make step-back` prints the suspension; the two make targets; tests.
6. **The exits.** (c) - a switch beside the checkpoint, so nothing is removed; an axis in `dev/switches.json` was weighed and refused (its writer and `make switches` are engine code naming only `remote`, and an engine change is never a tweak).
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: with the switch off, `checkpoint.state` is not due past the hour, `hold` and `due` say nothing and `open` refuses naming the suspension; with it on, the existing checkpoint tests hold unchanged; a red-gate trigger still blocks the gate either way (tests).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T43 Decisions

**D17 - a switch beside the checkpoint.** `dev/step-back.json` (`{"state": "off"|"on", "why", "who", "utc"}`; absent means on) is read by `checkpoint.suspended(root)`; while off, `state()` returns `due: False` with `suspended` set, so the step-back, the hold on `make tick` and the hour's refusal of a gate or a dispatch all stand down. The review units the hour used to call due still come due at the landing (`review-gate.sh`), as they do for a feature under an hour. `make step-back-off REASON=` and `make step-back-on REASON=` write it (a reason required, who and when recorded) and commit it; `make step-back` and `checkpoint.py status` name the suspension and how to resume. A checkpoint already open when the switch goes off stands down with the rest: its record is kept (the clock and the owed `hour:` trigger), and it is owed again only when `make step-back-on` resumes the step-back (the plan review of D17, round 1).

### T43 part B (2026-10-21T10:26Z)

Owed by the round arbiter's ruling on red-gate@2026-10-21T05:02:38Z (accept), taken while T43 was the active task.

1. **What is refusing?** Nothing in the code: the three tooling suites green (73); `hm_arbiter.py gate-held` refused live on that trigger until it was ruled.
2. **A3 again.** Unchanged: features 375 and 383 (O), the GM's amendment 4.
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: D17 and D18 as reviewed.
6. **The one-sentence test.** "Suspended, the hour comes due for nothing; a red gate holds every gate" - true by the tests and the live refusal.
7. **The next step is a measurement.** `make land` on T43 and T44, then the fourth claim measured.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** Yes - T44 lands, and the ruling's `GATE_NO_CACHE=1` row is filed (T45).

<!-- plan-archive: T27 to T27 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T90 part B (2026-10-21T16:46Z)

Owed by the round arbiter's ruling on red-gate@2026-10-21T16:40:44Z (continue), taken while T90 was the active task.

1. **What is refusing?** Not the batch's engine change (seeds 1-48 and the pinned rows 54/54): the gate went red on feature 408's ticked physical tasks with boxes open (from main), on a whole-repo cache test whose tree a commit beside the gate moved, and on the session's own PLAN_REVIEW_OK reaching the hook suites. Each fixed with its test.
2. **A3 again.** Unchanged: T90's constraint is T79's handler (O).
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: D68 as reviewed; the three gate fixes are tooling of their own.
6. **The one-sentence test.** "A landing stopped by hand stops its gate and cohort" - true by the test and by `make land-stop` with none running.
7. **The next step is a measurement.** `make land` once more: its gate shows the three tests green.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** Yes - one more `make done`, through `make land`.

<!-- plan-archive: T18 to T18 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T18 to T86 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T86 to T89 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T89 to T22 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T22 to T23 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T23 Decisions

**D73 - the fallback named.** No code change: `tip_onto_the_bund`'s claim names its fallback - a tip it cannot carry on is left as it came for the settle, whose lane law calls the short end dangling (pulled back, GUESS 0246), and the field is reached by `a_way_onto_the_bund` (0014: the hamlet's nearest lane runs on to the bund).

<!-- plan-archive: T18 to T18 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T18 to T18 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T18 to T18 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T95 Approach (checklist part A)

1. **The goal, in the world.** A join link's margin off the water is claimed.
2. **The constraints.** No page gives a lane's margin off a water line; 0081 keeps a lane off wet ground.
3. **Where each comes from.** O.
4. **Do they describe the world here?** Yes - batch 9's round: `_clear_touch` keeps `clear_runs`' default 14 ft off water lines, unclaimed.
5. **The order.** The claim (written in batch 9: "a join link off the water - UNRESEARCHED: 14 ft"), read IN-STEP; nothing more.
6. **The exits.** (a) claim.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** The claims round read it IN-STEP (batch 9, 2026-10-21).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T95 Decisions

**D74 - the water margin claimed.** No code change: `_clear_touch`'s 14 ft off water lines claimed UNRESEARCHED in batch 9, read IN-STEP.

### T96 Approach (checklist part A)

1. **The goal, in the world.** A hairpin is a turn of more than 140 degrees, as 0081 says, wherever a turn is judged.
2. **The constraints.** 0081 §37: a hairpin is a turn of "more than 140 degrees".
3. **Where each comes from.** R (0081).
4. **Do they describe the world here?** Yes - batch 9's round 3: the spur's fold, `kink_spans`, and the joints' two hook tests cut at exactly 140 as well (`>=`).
5. **The order.** `>=` -> `>` at the four places that compare a turn with `_HAIRPIN_DEG` (`clearance.kink_spans`, `joints` x2, `track.spur_cut_at_the_fold`); their docstrings say "more than"; a test at exactly 140; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** A turn of exactly 140 degrees is no hairpin (test); seeds 1-48 and the pinned rows pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T96 Decisions

**D75 - more than 140, and more than 50.** The four comparisons read `> _HAIRPIN_DEG`; `law.DOUBLE_BACK_DEG` (the same constant) is read by `kink_spans`, so the law and the placers keep one boundary. And `kink_spans`' zigzag turn reads `> _ZIGZAG_DEG` (0081: "two turns of more than 50 degrees"; the claims round found its `>=` beside the hairpin's); `tee`'s hairpin refusal claimed on 0081.

### T97 Approach (checklist part A)

1. **The goal, in the world.** A lane end running back along another way under 20 degrees is a doubled tail and is cut where it comes alongside, as 0081 draws it.
2. **The constraints.** 0081 §25: "A lane whose end runs back along another way at less than 20 degrees ... cut it where it comes alongside".
3. **Where each comes from.** R (0081).
4. **Do they describe the world here?** Yes - batch 9's round 3: `tails._DOUBLED_DEG` is 15 and four claims call the rule UNRESEARCHED.
5. **The order.** `_DOUBLED_DEG` 15 -> 20 (0081); the four claims (`tails._DOUBLED_DEG`, `tails`' and `law`'s doubled-tail predicates, `settle_ends`) cite 0081; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** Seeds 1-48 and the pinned rows pass; the claims round reads the four IN-STEP.
10. **Before moving a constant.** Measured: `_DOUBLED_DEG` is read by the law's refusal, the settle's cut, the tree's deferral and `Lawful`'s tail rule; seeds 1-48 and the pinned rows say what the move costs.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T97 Decisions

**D76 - 0081's rule claimed; its 20 degrees owned by T101.** The four claims cite 0081 (an end running back along another way under 20 degrees is cut where it comes alongside), each naming the known gap: the code asks at `_DOUBLED_DEG` 15. Measured 2026-10-21: at 20, cohort seeds 10 and 40 were refused (a household's way, a tree lane no settle may cut, read as doubled; a shallow crossing left). The move from 15 to 20 is filed as T101, which owns it - done when seeds 1-48 and the pinned rows pass at 20, those two refusals among them - once the side-by-side family (T07) leaves the tree no doubled household way.

### T100 Approach (checklist part A)

1. **The goal, in the world.** A task id names one task in its tasks.md.
2. **The constraints.** Feature 375's task ids; `make task-add` takes the next free id.
3. **Where each comes from.** O.
4. **Do they describe the world here?** Yes - measured 2026-10-21: a hand-filed T93 beside the landing's carried T93, and no check refused it.
5. **The order.** `spec-lint` check: a task id on two task lines of one tasks.md is refused, naming both lines and `make task-add`; a test.
6. **The exits.** (c) - a check, not a habit.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** Two T93 lines refused, one passes (test).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T96 Approach (re-answered 2026-10-21T18:39Z)

1. **The goal, in the world.** A hairpin is a turn of more than 140 degrees and a zigzag two turns of more than 50, as 0081 says, wherever a turn is judged.
2. **The constraints.** 0081 §20, §21, §37: a hairpin is a turn of "more than 140 degrees"; a zigzag is "two turns of more than 50 degrees" within 40 ft.
3. **Where each comes from.** R (0081).
4. **Do they describe the world here?** Yes - batch 9's round 3 (the fold, the kinks and the joints cut at exactly 140) and batch 10's round (the zigzag at exactly 50).
5. **The order.** `>=` -> `>` at the four hairpin comparisons and `kink_spans`' zigzag turn; docstrings say "more than"; `tee`'s hairpin refusal claimed on 0081; a test at exactly 140; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** With batch 10.
9. **Done, measured.** A turn of exactly 140 is no hairpin (test); seeds 1-48 and the pinned rows 54/54 (measured 2026-10-21).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.
<!-- plan-archive: archived 2026-10-21 -->
### T100 Decisions

**D77 - one id, one task.** `spec-lint` `check_duplicate_tasks(tasks)`: every `- [ ] Tnn` / `- [x] Tnn` id seen twice is a finding with both line numbers and the tip `make task-add F=<n> TITLE=...`.

### T97 Approach (re-answered 2026-10-21T18:13Z)

1. **The goal, in the world.** The doubled-tail rule is claimed on the page that gives it, and the figure the code asks at is named against it.
2. **The constraints.** 0081 §25: an end running back along another way under 20 degrees is cut where it comes alongside.
3. **Where each comes from.** R (0081).
4. **Do they describe the world here?** Yes - batch 9's round 3: four claims called it UNRESEARCHED; and measured 2026-10-21, at 20 degrees cohort seeds 10 and 40 were refused (a household's way read as doubled, a shallow crossing).
5. **The order.** The four claims cite 0081 with the known gap (asked at 15); the move to 20 filed as T101, which owns it (done: seeds 1-48 and the pinned rows pass at 20), after the side-by-side family (T07); `_DOUBLED_DEG` stays 15 here.
6. **The exits.** (a) claim, the move filed (T101).
7. **The search smell.** None - one measured roll at 20, then the move filed with its done-check.
8. **The budget.** With batch 10.
9. **Done, measured.** The claims round reads the four; seeds 1-48 and the pinned rows 54/54 at 15 (measured 2026-10-21).
10. **Before moving a constant.** Measured at 20 (two seeds refused); not moved.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T103 Approach (checklist part A)

1. **The goal, in the world.** A join's nub cut is claimed.
2. **The constraints.** The ink's touch (`_TOUCH_GAP`, 4 ft, CONVENTION).
3. **Where each comes from.** O.
4. **Do they describe the world here?** Yes - batch 10's round (carried): `tee` stops a lane at the vertex before the joint when that vertex stands within 4 ft of its foot, unclaimed.
5. **The order.** A claim at `tee`: a vertex within the ink's touch of its foot ends the lane there - CONVENTION, no last leg shorter than a touch.
6. **The exits.** (a) claim.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** The claims round reads it IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T100 part B (2026-10-21T18:13Z)

Owed by the cohort (cohort@20261021T180921Z: seeds 10 and 40 newly failing), taken while T100 was the last task started - the work that resisted was T97's 20 degrees.

1. **What is refusing?** The cohort, on `_DOUBLED_DEG` 20 (T97): seed 10's household way read as a doubled tail, a tree lane no settle may cut; seed 40 a shallow crossing left. Nothing of T100's - a spec-lint check.
2. **A3 again.** Unchanged for T100.
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** T97's figure is left at 15; the move to 20 is filed as T101 (D76); T100 unchanged.
6. **The one-sentence test.** "A task id names one task" - true by the test.
7. **The next step is a measurement.** Seeds 1-48 at 15: 54/54 (measured).
8. **Every route measured before offering one?** The one route (20) was measured and filed as T101.
9. **After a ruling: the step it names?** No ruling.

<!-- plan-archive: T96 to T96 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->

### T103 Decisions

**D79 - the nub claimed.** No code change: `tee`'s stop within `_TOUCH_GAP` of the foot claimed CONVENTION (a leg shorter than the ink's touch reads as no leg).

### T105 Approach (checklist part A)

1. **The goal, in the world.** The joint's mend and an unwidthed lane's judging width are claimed as the record reads them.
2. **The constraints.** 0081: no two turns of more than 50 degrees within 40 ft; a footpath 3 ft; the page names no mend for a Z across a joint.
3. **Where each comes from.** R (0081) and O.
4. **Do they describe the world here?** Yes - batch 10's round: `_one_joint` and `_joint_moved_back` cite 0081 for moving the joint back, which the page does not record; `settle_ends` reads `w or 3.0` unclaimed.
5. **The order.** The mend claimed UNRESEARCHED apart from 0081's zigzag rule (two claims split); `settle_ends`' 3 ft claimed on 0081; no code change.
6. **The exits.** (a) claim.
7. **The search smell.** None.
8. **The budget.** 30 min with its landing.
9. **Done, measured.** The claims round reads them.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-21 -->
### T10 Approach (checklist part A)

1. **The goal, in the world.** The track out's last resort and drawn channels are claimed as they stand against 0084.
2. **The constraints.** 0084 (a path may cross a farm ditch on a plank).
3. **Where each comes from.** R (0084).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (385 T120's finding: `connector_dry_exit` never crosses a drawn channel, unclaimed).
5. **The order.** The claim: a DEVIATION from 0084 - the fill lays no plank, so it keeps to the ground between the channels, and a gateway with no such way is refused (`NoDryExit`).
6. **The exits.** (a) claim as a DEVIATION - 0084 permits a plank and does not require one; laying planks from the fill was weighed and refused here (the last resort runs where no bearing is dry; a refused gateway is re-seated, feature 287 W23).
7. **The search smell.** None.
8. **The budget.** 40 min for the batch with its landing.
9. **Done, measured.** The claims round reads it IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T103 part B (2026-10-21T19:30Z)

Owed by the cohort (cohort@20261021T192759Z: seeds 10, 24, 36 and 47 newly failing), taken while T103 was the last task started - the work that resisted was T26's.

1. **What is refusing?** The cohort, on T26's wood-shed rule (D78): the new seats moved farms so two households' ways ended within 25 ft of one another, and the knots step's every gather was refused - passing within 0246's 7 ft of a neighbor's garden (T18) or splitting the web; with the seat roll the cohort passed and Sawada failed the same way. Nothing of T103's - a claim.
2. **A3 again.** Unchanged for T103.
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** T26's engine change is set down (the shed code and the pool restored to main's) and T107 filed for the knots-versus-gap conflict, which T26 and T106 wait on; T103 lands alone.
6. **The one-sentence test.** "A nub shorter than the ink's touch is not drawn" - claimed, read IN-STEP.
7. **The next step is a measurement.** `make land` for T103: its gate on main's engine.
8. **Every route measured before offering one?** Two T26 routes measured (with and without the roll); both expose the conflict, so neither is offered.
9. **After a ruling: the step it names?** No ruling.

<!-- plan-archive: T105 to T105 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T105 Decisions

**D80 - the mend and the footpath claimed.** No code change: the joint moved back a vertex claimed UNRESEARCHED, beside 0081's zigzag rule it serves; `settle_ends`' unwidthed lane claimed as 0081's 3 ft footpath.

<!-- plan-archive: archived 2026-10-21 -->
### T10 Decisions

**D62 - withdrawn; T10 stays open.** 0084 §116 draws a timber deck as wide as the way where a way crosses a ditch, so the research expects the track out to cross a drawn channel on a deck, which the fill refuses; no claim may call that a departure the page does not record (the claims round). T10 is re-scoped to the deck crossing - a code task - and is not landed with this batch.

<!-- plan-archive: T60 to T17 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T54 to T83 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T83 to T84 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T84 to T85 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T85 to T87 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T87 to T90 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T90 to T90 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T90 to T23 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T67 Approach (checklist part A)

1. **The goal, in the world.** The track out's last resort crosses only the brook at its crossing places, and every rule it keeps is claimed as the record reads it.
2. **The constraints.** 0035: crossing places on the brook every 160 ft or so (a GUESS there), the length of each not given; 0081: a track keeps off wet ground and leaves downslope past its end, on the flank the cluster sits on; 0036: a way keeps a footpath's clearance and working room off a farm's trees; 0084: a way crosses a ditch on a deck (T10).
3. **Where each comes from.** R (0035, 0081, 0036, 0084).
4. **Do they describe the world here?** Yes - 385's found rows 19-26 and 29 (405 T28): the fill gapped every line within `FORD_HALF` of a brook crossing place, drawn channels and the drain too; the downslope rule unclaimed; `clear_of_bands` UNRESEARCHED though 0036 bears on it; no claim for the moved start; `FORD_HALF`'s 60 ft cited to 0035, which records no length.
5. **The order.** `connector_dry_exit` gaps only the lines on the brook's course (`on_course`) at its crossing places, the channels kept whole until T10's last fill; claims: the track past the wet ground's end (0081, its flank a GUESS), the start walked clear of the bands (UNRESEARCHED), `clear_of_bands` on 0036, `FORD_HALF` UNRESEARCHED; a test; seeds 1-48.
6. **The exits.** (e) conform, with the claims.
7. **The search smell.** None.
8. **The budget.** 40 min with its landing.
9. **Done, measured.** A channel beside a crossing place stays whole in the fill open at the crossing places (test); seeds 1-48 and the pinned rows pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

<!-- plan-archive: archived 2026-10-22 -->
### T10 Approach (re-answered 2026-10-21T20:00Z)

1. **The goal, in the world.** Where a settlement's only way out crosses a farm ditch, the track out crosses it on a deck, as 0084 draws a way over a ditch.
2. **The constraints.** 0084 §116: where a way crosses a stream or ditch the map draws a timber deck as wide as the way; 0035: the brook crossed at its crossing places; the law's decks (a crossing seats a deck, `crossing_deck`, or is refused).
3. **Where each comes from.** R (0084, 0035) and O (the law's decks).
4. **Do they describe the world here?** Yes - batch 7's claims round: the fill never crosses a drawn channel, and 0084 expects a deck there.
5. **The order.** `connector_dry_exit`: after the own-bank fill and the fill open at the brook's crossing places, where both find nothing, a third fill with the drawn channels opened (the brook still only at its crossing places); the settle seats the deck as at any crossing; the claim on 0084; a test; seeds 1-48.
6. **The exits.** (e) conform, as a last resort - it only turns a refused gateway into a way out.
7. **The search smell.** None.
8. **The budget.** 40 min with its landing.
9. **Done, measured.** The third fill runs only where the other two find no way, with the channels opened and the brook not (test); seeds 1-48 and the pinned rows pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T67 Decisions

**D82 - the brook alone gapped.** `on_course(seg, plan.brook)` (both ends within 1 ft of the course) sorts the fill's lines into the brook's and the channels'; `gap_segments` opens only the brook's at its crossing places; the channels stay lines until T10's last fill, which drops them. The claims as Approach item 5 lists them; `FORD_HALF` stays 30 ft, now labeled UNRESEARCHED.

<!-- plan-archive: archived 2026-10-22 -->
### T10 Decisions (re-decided 2026-10-21T20:00Z)

**D81 - a ditch crossed on a deck, last.** `connector_dry_exit` runs `dry_exit` a third time with the drawn channels left out of its lines (the brook's segments still gapped only at its crossing places, `gap_segments`) when the own-bank and crossing-place fills both return None; the track it finds crosses a channel, and the settle seats the deck there (`law` decks, `crossing_deck`) or refuses the map as for any undeckable crossing. Claimed on 0084.

<!-- plan-archive: T67 to T67 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T67 to T67 moved to plan-done.md, 2026-10-22 (feature 375 FR-044) -->
## T91 - the 80 ft doorstep against 0246's reach (batch 9's round)

### T91 Approach (checklist part A)

1. **The goal, in the world.** A way that leaves a farmhouse's dooryard is not walled by that dooryard, and the house it leaves is the one its start reaches as 0246 counts reaching; a fan of ways at one door is cut back past the dooryard.
2. **The constraints.** 0246's reach (an end reaches a farmhouse within 60 ft of the house or 12 ft of its steading's built ground, `law.reach_to_steading`); `law.DOORSTEP_FT` (80 ft from the house's center); seeds 1-48 and the pinned rows.
3. **Where each comes from.** 0246's reach: O - the page's own GUESS, labeled so. `DOORSTEP_FT`: U - its claim says UNRESEARCHED, and impl-drift ruled it IN-STEP as that ("this is not 0246's reach test").
4. **Do they describe the world here?** Three readers remain. `field_router`'s `own` asks which house a route STARTS at - a reach question, and its claim cites 0246 for an 80 ft the page does not give (the mislabel the round found). `settle_ends`' fan cut asks how far back an extra end at one door is cut - not a reach; the 80 ft is ours. `Lawful.fault`'s `houses` look-up is a search radius for `house_hit`, and its comment says `theirs` reads it, which stopped being true at T18 (`theirs` reads the lane's owner).
5. **The order.** Nothing moves in the pipeline; the field way is routed where it was.
6. **The exits.** (a) the route's own house by 0246's reach - taken; (b) record 80 ft on 0246 as a second reach - not taken: two figures for one question; (c) the fan cut by 0246's reach - not taken: the cut is a distance back from the door, not whether an end arrives, and the round found no fault in it; (d) more room - n/a, nothing fails to fit; (e) conform - the claim keeps citing 0246 for a figure it does not give.
7. **The search smell.** None: one predicate swapped for the page's own.
8. **The budget.** 30 min with its landing.
9. **Done, measured.** `field_router`'s own house is the one `law.reach_to_steading` admits for the route's start (test); `DOORSTEP_FT`'s docstring names only its live readers; `Lawful.fault`'s comment says what the radius is for; seeds 1-48 and the pinned rows as main.
10. **Before moving a constant.** No constant moves: `DOORSTEP_FT` keeps 80 ft for the fan cut and the search radius.
11. **Before fitting things into room.** n/a - nothing is fitted.

### T91 Decisions

**D84 - a route's own dooryard by 0246's reach.** `corridors.field_router`'s `route` takes as its own the nearest farmhouse whose reach (`law.reach_to_steading`, 60 ft of the house or 12 ft of its built ground, 0246's GUESS) holds the route's start, in place of the nearest house center within `law.DOORSTEP_FT`; its claim cites 0246's reach. `DOORSTEP_FT` stays 80 ft, UNRESEARCHED, for `settle_ends`' fan cut and `Lawful.fault`'s house look-up; its docstring drops the yards exemption it lost at T18, and the look-up's comment says it is a search radius for `house_hit`.

<!-- plan-archive: archived 2026-10-22 -->
## T93 - two claims the claims gate carried (385 FR-013)

### T93 Approach (checklist part A)

1. **The goal, in the world.** A way carried on to the bund keeps the 7 ft off a garden fence any lane keeps, and its claims say so truly; a join link's margin off the crop is said as the research has it.
2. **The constraints.** 0246's 7 ft from a lane's middle to a garden fence (`FOOTPATH_FABRIC_GAP`); 0246's no house on a tread; 0081's lane on the bund that may touch a plot's boundary; the claims gate.
3. **Where each comes from.** 0246's 7 ft: O (a map drawing convention, the page says). No house on a tread: R. 0081's bund: R.
4. **Do they describe the world here?** Item 1: `tip_onto_the_bund` passes `2.0 * half_tread` to `RunOnBlocks.clear` as the run-on's WIDTH - the drawn tread the fixture, crop and house tests read - while `clear` keeps the run-on's middle `FOOTPATH_FABRIC_GAP` (7 ft) off the steadings' fabric, gardens included. The code keeps the page's 7 ft; the claim ("short of 0246's 7 ft") misreads the width as a clearance - MISLABELED, as the round said, but the fault is the claim's words, not the code. Item 2: `_clear_touch`'s 7 ft off the crop, where 0081 lets a lane touch a plot's boundary - the same finding as T98 (which names `_clear_touch`'s 7 ft join link off the crop and asks for the crop margin to reach the edge or be recorded on 0081).
5. **The order.** Nothing moves.
6. **The exits.** (a) item 1's claim rewritten to what the code does, citing 0246 - taken; (b) item 1's code changed - not taken: it already keeps the page's gap; (c) item 2 worked here - not taken: T98 owns it whole (every `clear_runs` crop margin, not one caller), and splitting it would decide the crop margin twice; (d) more room - n/a; (e) conform - n/a.
7. **The search smell.** None.
8. **The budget.** 20 min with its landing.
9. **Done, measured.** Item 1's claim re-checked IN-STEP by impl-drift; item 2 named in T98's text as carried from T93; no engine logic changes (a docstring only).
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a.

### T93 Decisions

**D85 - the run-on's width is its tread; its clearance is the fabric's 7 ft.** `tip_onto_the_bund`'s claim "a run-on leg clear by its tread" is rewritten: the leg is judged at its drawn width (`2.0 * half_tread`, the tread the fixture, crop and house tests read - 0246's no house on a tread), and kept 7 ft off the steadings' fabric, gardens included, by `RunOnBlocks.clear` (`FOOTPATH_FABRIC_GAP`, 0246). No code changes. `_clear_touch`'s crop margin (T93's second item) is carried to T98, which already names it; T98's text says so.
<!-- plan-archive: archived 2026-10-22 -->
## T115 - the field way past its own house (T91's round)

### T115 Approach (checklist part A)

1. **The goal, in the world.** A field way leaving its own door may pass its own house as any path leaves a door, and keeps off its neighbors' steadings; its claims say which rule holds where.
2. **The constraints.** 0246's 7 ft from a way's middle to another household's garden fence (§45); 0246's no house corner on the tread (§36); the router's walls (`field_router`, `FIELD_ROUTE_GAP_FT` 7 ft off every steading's built ground but the route's own dooryard and, where it starts at its door, its own house).
3. **Where each comes from.** The 7 ft: O (the page's convention). No house on the tread: R. The 7 ft off houses, byres, sheds and yards: U - no page sizes a way's margin off a building.
4. **Do they describe the world here?** The finding says the way may pass its own house closer than "the claimed 7 ft". The page's 7 ft is from a garden fence; at a house it asks only that no corner stand on the tread, which `house_hit` keeps (the law refuses the run otherwise). So the code keeps the page; the claim "field way off the steadings" overstates it by calling the 7 ft off all built ground the page's.
5. **The order.** Nothing moves.
6. **The exits.** (a) the claim split: the gardens at the page's 7 ft, the other built ground at 7 ft as a GUESS, the own house at its door by the tread rule - taken; (b) wall the own house again past the start - not taken: the page asks no more than the tread rule of a house, and a door path must leave its wall; (c) record the passing on 0246 - not needed: the page already says it; (d) more room - n/a; (e) conform - n/a.
7. **The search smell.** None.
8. **The budget.** 15 min with its landing.
9. **Done, measured.** `field_router`'s claims re-checked IN-STEP; no code logic changes (a docstring only).
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a.

### T115 Decisions

**D86 - the field way's margins as the page gives them.** `field_router`'s claim "field way off the steadings" is split: off another household's garden, 0246's 7 ft; off the other built ground (houses, byres, sheds, yards), the same 7 ft as a GUESS (no page sizes it); the route's own house where it starts at its door, only 0246's no house corner on the tread (`house_hit`). No code changes.
<!-- plan-archive: archived 2026-10-22 -->
## T116 - a way's own garden walled where the page lets it pass (T93's and T115's rounds)

### T116 Approach (checklist part A)

1. **The goal, in the world.** A way keeps 7 ft off a neighbor's garden fence; where the generator also keeps it off its own household's garden, its claims say that is our stricter choice, not the page's.
2. **The constraints.** 0246 §45/§122: the 7 ft is kept from another household's garden, and a household's own way may run beside its own fence, kept only off the beds; the lanes' fouls take that permission (`owned_gardens`, 385 T03, a DEVIATION recorded beside it).
3. **Where each comes from.** The 7 ft: O (the page's convention). The own-garden permission: O (the page's).
4. **Do they describe the world here?** Two readers wall every garden at 7 ft, the way's own too: `RunOnBlocks.clear` (the run-on to the bund), which is read once per pass with no lane, so cannot tell whose garden is whose; and `_homestead_polys` (the router's and run-on's fabric), which frees only the dooryard. Neither is a passing the page forbids - a way kept farther off its own garden than the page requires - but both claims cite the page as if it asked it.
5. **The order.** Nothing moves.
6. **The exits.** (a) the claims say the own garden is walled too, labeled a DEVIATION of 0246 (the page speaks, so it cannot be a GUESS - T116's claims round), recorded on the page by T114's page session - taken; (b) give both readers the lane's owner - not taken here: the router and the run-on are asked before a lane has its record in several callers, a reach and cohort change for no map defect the page names; (c) record on 0246 - taken through T114, the same page and session as the knot exception; (d) more room - n/a; (e) conform - n/a.
7. **The search smell.** None.
8. **The budget.** 15 min with its landing.
9. **Done, measured.** The two claims re-checked: IN-STEP, or DRIFTED only until 0246 records the departure (T114), landed with `CLAIMS_OK` naming T114 as T107's was; a docstring only.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a.

### T116 Decisions

**D87 - a way's own garden walled, claimed as ours.** `RunOnBlocks.clear`'s "off the steadings" and `_homestead_polys`' "a path leaves its own yard" say they keep 0246's 7 ft off every garden, the way's own included, labeled a DEVIATION of 0246 (the page lets a household's own way run beside its own fence, kept only off the beds) and recorded on the page by T114: the run-on's blocks are read without the lane they judge, and the fabric frees only the dooryard (a garden is an obstacle to its own farm's path, feature 328). No code changes.

### T116 Approach (re-answered 2026-10-22T09:47Z)

1. **The goal, in the world.** A way keeps 7 ft off a neighbor's garden fence; where the generator also keeps it off its own household's garden, its claims say that is our stricter choice, not the page's.
2. **The constraints.** 0246 §45/§122: the 7 ft is kept from another household's garden, and a household's own way may run beside its own fence, kept only off the beds; the lanes' fouls take that permission (`owned_gardens`, 385 T03, a DEVIATION recorded beside it).
3. **Where each comes from.** The 7 ft: O (the page's convention). The own-garden permission: O (the page's).
4. **Do they describe the world here?** Two readers wall every garden at 7 ft, the way's own too: `RunOnBlocks.clear` (the run-on to the bund), which is read once per pass with no lane, so cannot tell whose garden is whose; and `_homestead_polys` (the router's and run-on's fabric), which frees only the dooryard. Neither is a passing the page forbids - a way kept farther off its own garden than the page requires - but both claims cite the page as if it asked it.
5. **The order.** Nothing moves.
6. **The exits.** (a) the claims say the own garden is walled too, labeled a DEVIATION of 0246 (the page speaks, so it cannot be a GUESS - T116's claims round), recorded on the page by T114's page session - taken; (b) give both readers the lane's owner - not taken here: the router and the run-on are asked before a lane has its record in several callers, a reach and cohort change for no map defect the page names; (c) record on 0246 - taken through T114, the same page and session as the knot exception; (d) more room - n/a; (e) conform - n/a.
7. **The search smell.** None.
8. **The budget.** 15 min with its landing.
9. **Done, measured.** The two claims re-checked: IN-STEP, or DRIFTED only until 0246 records the departure (T114), landed with `CLAIMS_OK` naming T114 as T107's was; a docstring only.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a.
<!-- plan-archive: archived 2026-10-22 -->
## T117 - the door release's words (T115's round 4)

### T117 Approach (checklist part A)

1. **The goal, in the world.** A field way that starts beside a house it serves can leave that house; its claim says where the release holds as the code tests it.
2. **The constraints.** 0246's no house corner on the tread (§113, kept by `house_hit`); the router's release of a house within `GABLE_MARGIN_FT` + `FIELD_ROUTE_GAP_FT` (13 ft) of a route's start (`mine()`), a GUESS.
3. **Where each comes from.** The tread rule: R. The 13 ft release: U - the claim already labels it a bare GUESS.
4. **Do they describe the world here?** `mine()` frees the house when the start stands within 13 ft of any of its walls (`edge_dist`), not only its front; the claim says "at its door". The door side is not the release's business: the route only needs to leave the wall it starts beside, and the law still keeps every house corner off the tread, so a start beside a gable or the back is let out the same way and the tread rule holds.
5. **The order.** Nothing moves.
6. **The exits.** (a) the claim drops "at its door" for "beside any wall" - taken; (b) test the front wall - not taken: a house record's door side is not what the release needs, and it would wall a route the law already admits, for no map defect; (c) record on 0246 - n/a (a bare GUESS); (d) more room - n/a; (e) conform - n/a.
7. **The search smell.** None.
8. **The budget.** 10 min with its landing.
9. **Done, measured.** The claim re-checked IN-STEP; a docstring only.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a.

### T117 Decisions

**D88 - the release beside any wall.** `field_router`'s claim "its own house at its door" says a route starting within 13 ft of any wall of a house is not walled by it (`mine()`'s `edge_dist`), a bare GUESS, the law keeping 0246's no house corner on the tread. No code changes.
<!-- plan-archive: archived 2026-10-22 -->
## T118 - four notes on the run-on's blocks and the fabric (T116's rounds)

### T118 Approach (checklist part A)

1. **The goal, in the world.** A way carried on to the bund keeps every house corner off its whole tread, and the run-on's other margins are claimed for what they are.
2. **The constraints.** 0246's no house corner on the tread (§113); the run-on's 7 ft off the fabric (`FOOTPATH_FABRIC_GAP`); the fabric's parts (`_homestead_polys`: houses, yards, gardens, groves, bamboo strips, wells).
3. **Where each comes from.** The tread rule: R. The 7 ft: O at a garden fence (0246); U off groves, strips and wells. The 2 ft start allowance and a house as its own owner: U.
4. **Do they describe the world here?** (a) `RunOnBlocks.clear` passes `int(width)` to `_hits_a_steading`, so a 3.5 ft tread is judged at 3 ft - narrower than the tread the page keeps corners off: a defect, the code is fixed. (b) `_homestead_polys` enters a house with itself as owner, read by `field_router`'s release of the house beside a route's start (T117) - unclaimed. (c) `clear` judges the fabric, crop and steading from 2 ft along the stretch, since the end it grows from may stand at its own dooryard's gap (its comment) - unclaimed. (d) `clear` keeps 7 ft off every fabric part, farm groves, bamboo strips and wells too - unclaimed past the gardens.
5. **The order.** Nothing moves.
6. **The exits.** (a) pass the width whole - taken; (b) claim the owner, the allowance and the 7 ft off the non-garden fabric as bare GUESSes (no page sizes them) - taken; (c) drop the allowance - taken for the houses alone (the claims round: 0246 gives no exception to "no corner of a house stands on its tread" near a way's start), kept for the fabric and the crop, where an end at its own dooryard's gap would refuse its own run-on; (f) the tread's 3 ft off a farmhouse wall (0081) against the house test's 0 ft, and the well's 8 ft fallback - carried to T119: they are the lane law's, not the run-on's; (d) more room - n/a; (e) conform - n/a.
7. **The search smell.** None.
8. **The budget.** 25 min with its landing (a gated one: an engine token changes).
9. **Done, measured.** A unit test: a 3.5 ft run-on whose tread edge would touch a house corner between 1.5 and 1.75 ft off its line is refused (red with `int`); the three claims re-checked IN-STEP; seeds 1-48 and the pinned rows as main.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a.

### T118 Decisions

**D89 - the run-on judged on its whole tread; its unclaimed margins claimed.** `RunOnBlocks.clear` passes the width to `_hits_a_steading` unrounded (its `width` typed float), so the whole tread keeps off the house corners (0246). Claims added as bare GUESSes: `_homestead_polys`' house entered as its own owner (what lets `field_router` free the house beside a route's start); `clear`'s 2 ft start allowance for the fabric and the crop (the end it grows from may stand at its own dooryard's gap), the houses judged from the stretch's own start (0246's no corner on the tread, no exception); and its 7 ft off the farm groves, bamboo strips and wells, which no page sizes.

### T118 Approach (re-answered 2026-10-22T10:04Z)

1. **The goal, in the world.** A way carried on to the bund keeps every house corner off its whole tread, and the run-on's other margins are claimed for what they are.
2. **The constraints.** 0246's no house corner on the tread (§113); the run-on's 7 ft off the fabric (`FOOTPATH_FABRIC_GAP`); the fabric's parts (`_homestead_polys`: houses, yards, gardens, groves, bamboo strips, wells).
3. **Where each comes from.** The tread rule: R. The 7 ft: O at a garden fence (0246); U off groves, strips and wells. The 2 ft start allowance and a house as its own owner: U.
4. **Do they describe the world here?** (a) `RunOnBlocks.clear` passes `int(width)` to `_hits_a_steading`, so a 3.5 ft tread is judged at 3 ft - narrower than the tread the page keeps corners off: a defect, the code is fixed. (b) `_homestead_polys` enters a house with itself as owner, read by `field_router`'s release of the house beside a route's start (T117) - unclaimed. (c) `clear` judges the fabric, crop and steading from 2 ft along the stretch, since the end it grows from may stand at its own dooryard's gap (its comment) - unclaimed. (d) `clear` keeps 7 ft off every fabric part, farm groves, bamboo strips and wells too - unclaimed past the gardens.
5. **The order.** Nothing moves.
6. **The exits.** (a) pass the width whole - taken; (b) claim the owner, the allowance and the 7 ft off the non-garden fabric as bare GUESSes (no page sizes them) - taken; (c) drop the allowance - taken for the houses alone (the claims round: 0246 gives no exception to "no corner of a house stands on its tread" near a way's start), kept for the fabric and the crop, where an end at its own dooryard's gap would refuse its own run-on; (f) the tread's 3 ft off a farmhouse wall (0081) against the house test's 0 ft, and the well's 8 ft fallback - carried to T119: they are the lane law's, not the run-on's; (d) more room - n/a; (e) conform - n/a.
7. **The search smell.** None.
8. **The budget.** 25 min with its landing (a gated one: an engine token changes).
9. **Done, measured.** A unit test: a 3.5 ft run-on whose tread edge would touch a house corner between 1.5 and 1.75 ft off its line is refused (red with `int`); the three claims re-checked IN-STEP; seeds 1-48 and the pinned rows as main.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a.
<!-- plan-archive: archived 2026-10-22 -->
## T108 - one width default at a joint; the joint's mend (T105's round)

### T108 Approach (checklist part A)

1. **The goal, in the world.** Where two lanes meet end to end and are pulled straight past a building, the tread keeps its 3 ft off the wall at the lane's own width; a lane recorded with no width is read as the footpath it is everywhere else.
2. **The constraints.** 0081's 3 ft footpath (the width `settle_ends`, `touch` and the knots read when a lane records none); 0081's tread 3 ft off a farmhouse wall (`TREAD_WALL_FT`); 0081's no-zigzag rule, which asks a mend for a Z at a joint and names none.
3. **Where each comes from.** The footpath's 3 ft: R (0081). The 3 ft off a wall: R (0081). The joint moved back a vertex when the pull fails: U - its claim says UNRESEARCHED.
4. **Do they describe the world here?** `_one_joint` reads a lane with no width as 5 ft (the spine's) for the pulled lane's clearance, where every other reader reads 3 ft: two defaults for one record. The mend is the code's own; 0081 is silent.
5. **The order.** Nothing moves.
6. **The exits.** (a) `_one_joint` reads 3 ft, as the rest do - taken; (b) keep 5 ft as the cautious figure - not taken: one record, one reading; (c) the mend recorded on 0081 as the page's GUESS - carried to T70, the 0081 page session already owed (a page edit, not a code one); (d) more room - n/a; (e) conform - n/a.
7. **The search smell.** None.
8. **The budget.** 20 min with its landing (gated: an engine token).
9. **Done, measured.** A unit test: `_one_joint`'s clearance for two lanes with no width is the 3 ft footpath's (`max(_TOUCH_GAP, 1.5 + TREAD_WALL_FT)`), red at 5; the claim re-checked IN-STEP; seeds 1-48 and the pinned rows as main.
10. **Before moving a constant.** No constant moves: only the fallback for a missing width.
11. **Before fitting things into room.** n/a.

### T108 Decisions

**D90 - a lane with no width is the footpath at a joint too.** `joints._one_joint` reads a lane with no `w` as 3 ft (0081's footpath), as `settle_ends`, `touch` and the knots do; its claim "a pulled lane's clearance" says so. The joint moved back a vertex (UNRESEARCHED) is recorded on 0081 as the page's GUESS by T70's page session; T70's text says so.
<!-- plan-archive: archived 2026-10-22 -->
## T120 - the claim-label lint (the GM, 2026-10-22)

### T120 Approach (checklist part A)

1. **The goal, in the world.** A claim's label is right the first time: a session writing `GUESS`, `GUESS <page>` or `DEVIATION <page>` is told at `make claims-owed`, before any impl-drift round, when the words of the claim contradict its label - so a claims task takes one round, not four (T115 took four, T116 and T118 a re-decided plan each, on labels alone).
2. **The constraints.** The GM's approval of the fix (2026-10-22); the claim grammar (`l7r/diagram/tools/claims.py`, `parse_claim`); a flag, never a refusal - a guard that fires on correct work teaches bypass (root CLAUDE.md); tips live in the error output; `scripts/record/claims.py` is at 988 lines, so the rules go in their own module.
3. **Where each comes from.** The three forms: today's MISLABELED verdicts (T115 round 1, T116 rounds 1-2, T118, T108's round 2, the replies in the session's scratchpad) - R for the process. The word lists: G, read off those verdicts and kept short.
4. **Do they describe the world here?** Yes: every MISLABELED of 2026-10-22 was one of the three, and each would have been flagged at the edit.
5. **The order.** Beside `claims_stale` in `claims.py owed`, on the owed claims only (what is about to go to impl-drift), after the form check.
6. **The exits.** (a) refuse the bundle - not taken: the word match is heuristic and a refusal on a right label teaches bypass; (b) flag on every claim in the engine - not taken: 5,500 claims, mostly checked IN-STEP, would bury the owed ones; (c) teach the agent file - not taken: the agent already rules MISLABELED; the cost is the round, so the fix sits before it.
7. **The search smell.** None.
8. **The budget.** 30 min with its landing.
9. **Done, measured.** One test per flag, each red with its rule deleted; a cited claim, a bare GUESS naming no page, a `GUESS <page>` whose page states its figure and a `DEVIATION` raise nothing.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a.

### T120 Decisions

- **D91** The lint reads each owed claim's backing and account (`Claim.backing`, `Claim.account`) and flags: (1) a GUESS, bare or named, whose account says the code departs from a page (`stricter than`, `looser than`, `short of`, `departs`, `than the page`, `than 0NNN`) - "a departure from a page is `DEVIATION <page>`, recorded on the page"; (2) a bare GUESS whose account names a question number (`0NNN`) - "cite the page if it states this, `GUESS <its .drawing.html>` if it records it as a guess, `DEVIATION <page>` if the code departs"; (3) a `GUESS <page>` whose account states a figure in feet that none of the named pages states - "a page that records a guess states its figure; if it does not, the guess is bare". Printed as `claims-label: <key> - <fix>` lines; the exit code is unchanged. Rendering: n/a (tooling).
<!-- plan-archive: archived 2026-10-22 -->
## T102 - one reading of a plan section, committed or not

### T102 Approach (checklist part A)

1. **The goal, in the world.** The decide guard gives the same answer on the same plan whether or not its reviewed text has been committed, so a check is never refused and then let through minutes later on unchanged work.
2. **The constraints.** The plan record keeps no block text (amendment 11, D63 - kept slim on purpose); a typo since a verdict is forgiven (D6); a tooling fix lands with a test that fails without it.
3. **Where each comes from.** Measured: `plan_gate.History.block` finds a verdict's text only in plan.md's git history, so a block reviewed or accepted before a commit is unknown until one - the T100 refusal (batch 10, 2026-10-21) and its CLEAR minutes later. R for the process.
4. **Do they describe the world here?** Yes: the arbiter's accept and `record-blocks` both write a verdict at the working tree's digest, often before the commit.
5. **The order.** The text is kept when a verdict is written (`record_blocks`, `arbiter_accept`), and read first by `History.block`, the history after it.
6. **The exits.** (a) put the text back in the record - not taken: D63 slimmed it for size; (b) commit the plan at each verdict - not taken: a guard does not commit for the session; (c) a store in the clone's git directory, by digest - taken.
7. **The search smell.** None.
8. **The budget.** 30 min with its landing.
9. **Done, measured.** A typo since an uncommitted accept is forgiven; a changed decision is not (one test, red without the store).
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T102 Decisions

- **D92** Every block a plan verdict is written at keeps its text in `<git common dir>/plan-seen/<digest>.txt` (`scripts/gates/plan_seen.py`); `History.block` returns a kept text whose digest matches before reading the history. A clone with nothing kept reads the history as before. Rendering: n/a (tooling).

<!-- plan-archive: archived 2026-10-22 -->
## T109 - a reply written outside the project is not corrected

### T109 Approach (checklist part A)

1. **The goal, in the world.** A checker's reply, saved to the scratchpad and recorded verbatim, keeps the checker's own words, whatever else shares its command.
2. **The constraints.** The GM's quotation rule (2026-09-06: the house style does not edit other people's quotes); a write outside the project is not project content (the hook's own exemption); a command writing a project file in the same breath is still corrected there.
3. **Where each comes from.** Measured: a heredoc to `/tmp` alone is left as typed, but one followed by `make claims-checked` or `git add` is corrected whole - the outside exemption asks whether EVERY write lands outside. R for the rule.
4. **Do they describe the world here?** Yes: batches 8, 9, 11 and 12 wrote and recorded replies in one command.
5. **The order.** The body of each heredoc whose file lands outside the project is held, like a quotation, before the correction runs.
6. **The exits.** (a) exempt by file name (`REPLY=`) - not taken: the heredoc writes before the recording names it; (b) hold outside heredoc bodies - taken; (c) tell sessions to split the command - not taken: a rule to remember.
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** A reply heredoc beside its recording is left as typed; beside a project heredoc, only the project's is corrected (two cases in the hook's table, red without the hold).
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T109 Decisions

- **D93** `hm_house.held_ranges` holds the body of each heredoc written by `cat`/`tee` (`>`, `>>`) to an absolute path under `/tmp/` or the session state directory; a relative or unknown target is not held. Rendering: n/a (tooling).
<!-- plan-archive: archived 2026-10-22 -->
## T99 - both figures settled by later work

### T99 Approach (checklist part A)

1. **The goal, in the world.** A run-on leg keeps 0246's 7 ft off a garden fence, and no drawing page states a field reach the code no longer uses.
2. **The constraints.** 0246's 7 ft gap; 0014's 6 ft join (T22).
3. **Where each comes from.** R: 0246, 0014.
4. **Do they describe the world here?** Yes.
5. **The order.** Measured before any edit.
6. **The exits.** (a) change the code or the pages - not needed: measured, neither half holds; (b) settle the task with the measurement - taken.
7. **The search smell.** None.
8. **The budget.** 10 min.
9. **Done, measured.** (1) `RunOnBlocks.clear` (bund.py) tests the stretch against the fabric at `FOOTPATH_FABRIC_GAP` (7 ft) since T118, `width` reaching only the house test - so a run-on leg keeps the page's 7 ft off a garden fence, whatever its tread. (2) None of 0006, 0009, 0029, 0057, 0081 or 0246's drawing pages states the field reach's 60 ft: the only "60 ft" left are 0006's plot size and 0246's serving test (§6), neither the field reach; `FIELD_REACH_FT` is 6 ft (law.py).
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T99 Decisions

- **D94** T99 is settled with no change: both its figures no longer hold, as measured in item 9. Rendering: n/a.
<!-- plan-archive: archived 2026-10-22 -->
## T09 - the track's fallbacks walled as its first route is

### T09 Approach (checklist part A)

1. **The goal, in the world.** A track out or field spur never crosses row crops or wet ground, however hard it was to route: what the first route walls, every fallback walls too, or the track is dropped (the spur recorded dropped, the connector taking the dry exit).
2. **The constraints.** 0081: lanes never across row crops or the flooded paddy, and off wet ground - and a way may come up to the bund; 0035: a way crosses water only at a crossing; 0036's room off a grove band (T109, D128); the docstring's own rule: never the offending run.
3. **Where each comes from.** R: 0081, 0035, 0036. G: the order of the three routes and the end walked along its own leg (claimed as GUESSes).
4. **Do they describe the world here?** Yes: the spur's field end stands on the bund, inside the crop's gap - which is why the later routes left the crop out of their walls.
5. **The order.** The first route is unchanged. The swing, the grove fallback's three routes and its far clip each wall the toe band and wet ground, and each is taken only where it crosses no crop plot at 0 ft (a way may touch the bund).
6. **The exits.** (a) wall the crop in all three routes - not taken: the spur's end inside the crop's gap leaves no route at all; (b) test the crop after the route, at 0 ft - taken; (c) more room - n/a, no fit failure; (d) conform - this is conforming.
7. **The search smell.** None.
8. **The budget.** 45 min with a gated landing.
9. **Done, measured.** A route round a band across a crop plot is refused (a test, red without it); `make cohort` 16/16 with the change (2026-10-22).
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T09 Approach (re-answered 2026-10-22T13:07Z)

1. **The goal, in the world.** Unchanged: no fallback of the track crosses row crops, the flooded paddy or wet ground, or adds a water crossing.
2. **The constraints.** As before, and the 1,000-line bar (405 T53: split, never trim).
3. **Where each comes from.** The claims round 1 (impl-drift, 2026-10-22): the fallbacks did not wall the field, and the swing had no water test. R: 0081, 0035.
4. **Do they describe the world here?** Yes: the spur's field end stands on the bund, so the field is tested with each end drawn in 3 ft.
5. **The order.** Unchanged, with the field and toe tested on every fallback and the water on the swing.
6. **The exits.** (a) narrow the claim to crops and wet ground - not taken: 0081 stops a lane at the flooded paddy; (b) test the field with the ends drawn in - taken; (c) a package split - not taken: about 40 test patches on `track` would move for no change in behavior; a sibling module re-exported, the engine's own precedent (`cluster_edge.py`, `reach.py`, `law_water.py`) - taken.
7. **The search smell.** None.
8. **The budget.** 30 min more.
9. **Done, measured.** A route across the field is refused and one ending on its edge taken (a test); `make test-file FILE=tests/hamletgen/ways/` 595 passed; `make cohort` 16/16 (2026-10-22).
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T09 Approach (re-answered 2026-10-22T13:16Z)

1. **The goal, in the world.** Unchanged: no fallback of the track crosses row crops, the flooded paddy, wet ground or reeds, or crosses water anywhere but at a crossing place.
2. **The constraints.** As before; 0081 (no causeway drawn, so no track crosses the reeds); 0035 (a crossing place every 160 ft or so, on a straight reach).
3. **Where each comes from.** The claims round 2 (impl-drift, 2026-10-22): the defense belt was left out of the walls, and the third route and the swing crossed water anywhere. R: 0081, 0035.
4. **Do they describe the world here?** Yes; a scripted hamlet draws no defense belt, so walling it moves no live map.
5. **The order.** As before, less the third route; the swing refused over water.
6. **The exits.** (a) DEVIATIONs of 0081 and 0035 recorded on the pages - not taken: the code can keep both; (b) wall the belt, drop the third route, keep the swing off water - taken, measured.
7. **The search smell.** None.
8. **The budget.** 20 min more.
9. **Done, measured.** `make test-file FILE=tests/hamletgen/ways/` 595 passed; `make cohort` 16/16 and seed 11 (the third route's own case) 7/7 (2026-10-22).
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T09 Approach (re-answered 2026-10-22T13:25Z)

1. **The goal, in the world.** Unchanged, and now for the unrouted clip too (T09's own text names it): no piece of the track crosses the paddy, crops, wet ground or water off a crossing place.
2. **The constraints.** As before.
3. **Where each comes from.** The claims round 3 (impl-drift, 2026-10-22): the unrouted clip was tested for the steadings alone, and the far clip of a raw run never for water. R: 0081, 0035.
4. **Do they describe the world here?** Yes; and testing the field's whole frame refused spurs that end on its bund (four unit tests), so the paddy is read as the fields' outlines, the lane law's own reading.
5. **The order.** As before, with the unrouted clip and the far clip of a raw run held to `_unrouted_clear`.
6. **The exits.** (a) say the run is trusted to cross at crossing places - not taken: nothing guarantees it; (b) test the pieces no route found - taken, measured.
7. **The search smell.** None.
8. **The budget.** 15 min more.
9. **Done, measured.** `_unrouted_clear` refuses a plot and a brook and takes a piece ending on a plot's edge (a test); `make test-file FILE=tests/hamletgen/ways/` 596 passed; `make cohort` 16/16 (2026-10-22).
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T09 Decisions

- **D95** (amended after the claims rounds 1-3, 2026-10-22) In `_thread_the_fabric` (now `ways/thread.py`): every fallback - the unrouted clip (the run as it came, clipped where the router found nothing), the swing's detour, the grove fallback's two routes and its far clip - is taken only where it crosses no paddy (each field's outline, as `law.span_walkable` reads the flooded paddy - not the field's whole frame, on whose bund a spur ends), no crop plot, no toe band and no wet ground (a defense belt's reeds included: no map draws a causeway, 0081), tested at 0 ft with each end drawn in 3 ft (`_inner`); a piece no route found (the unrouted clip, the far clip of a raw run) and the swing are taken only where they cross no water (`_unrouted_clear`), the two routes - searched with the water lines, crossing at the fords - only where they add no crossing the run did not make (0035); the third route (water left out of its search) is dropped. The first route walls the defense belt too. `track.py` passed the 1,000-line bar with the claims, so the thread half is lifted out to a sibling `ways/thread.py`, which `track` re-exports - as `cluster_edge.py` was lifted out of the same file (feature 316). Rendering: historically accurate (0081, 0035), the route order a GUESS.
<!-- plan-archive: archived 2026-10-22 -->
## T70 - the record, written in a page session

### T70 Approach (checklist part A)

1. **The goal, in the world.** 0081's worn-path paragraph agrees with 'A turn the ground forces'; 0196's absence note says only what was read; the isotherm/isohyet glossary error is gone; 0081 records the joint mend (the meeting point moved back one bend) as its GUESS, which `joints._joint_moved_back` cites.
2. **The constraints.** The research record's rules (a fact quoted, a guess labeled); the 20,000-byte question cap; page sessions write, then a fresh session checks and applies (`make page-session`).
3. **Where each comes from.** R: 0081, 0196, the glossary.
4. **Do they describe the world here?** Yes: each item was what an impl-drift or record check found silent or out of step.
5. **The order.** Written in a page session, checked in the next, merged, then the engine's claims repointed where they rest on it.
6. **The exits.** (a) change the code instead - not taken: the page was silent or ambiguous, the code deliberate; (b) record it on the page - taken.
7. **The search smell.** None.
8. **The budget.** Its share of five page sessions.
9. **Done, measured.** page sessions 1-2 (p1 T70, p2 T70); session 3's checks clean.
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T70 Decisions

- **D101** 0081's worn-path paragraph agrees with 'A turn the ground forces'; 0196's absence note says only what was read; the isotherm/isohyet glossary error is gone; 0081 records the joint mend (the meeting point moved back one bend) as its GUESS, which `joints._joint_moved_back` cites. Rendering: as each line is labeled on its page.


### T70 part B (2026-10-22T14:17Z)

Owed by the cohort record of 2026-10-22T03:45Z (seeds 10, 24, 36, 47 newly failing), rolled while T70 was in flight - T26's wood-shed change under test, never landed (set down, its knots carried to T107).

1. **What is refusing?** Nothing of T70's: its work is record text (0081, 0196, the glossary) and one claim's label (`joints._joint_moved_back`); the four seeds failed on T26's uncommitted engine diff, measured then (dev/cohort-log/20261022T034510Z-*), and every landing since passed its cohort (T09, the record batch: 54/54).
2. **A3 again.** Unchanged: 0081, 0196, the glossary (R).
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: D101 as reviewed.
6. **The one-sentence test.** "0081's paragraph agrees with its forced-turn bullet, 0196 says only what was read, isotherm is not isohyet, and the joint mend is the page's GUESS" - true on the pages (session 3's checks clean).
7. **The next step is a measurement.** `make land` on T70.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** No ruling owed.

