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
