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
