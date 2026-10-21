# Retros - feature 405

One row per closed task.

## T12 - the retro row

The first round of FR-004: one claim, through the whole route. The fix was two deleted loops: `_trim_to_service` now walks
every end in 4 ft at a time instead of popping a whole last segment first. Its test was red at HEAD (the end stopped at
(450, 0), 50 ft short of the house); the ways package (574 tests) and the cohort (16/16) were green. The process around it
cost more than the fix did. The feature had never had its spec reviewed (two rounds, the first CHANGES REQUIRED: today's
scope, a miscount, 63 unfiled findings), the first plan review stopped without a verdict because 405 had no request.md, the
claims round named an UNCLAIMED rule in the same function that the gate would refuse (a second impl-drift round on the new
claim), and five tooling or record findings were filed rather than worked (T28-T31 and the found.jsonl rows). **The habit it
changes:** none yet; the numbers go to the GM before a second task starts.

## T30 - the retro row

About 5 min. `plan_bundle.build` refuses a feature with no `request.md` before writing anything, naming the file and what goes
in it; T12's first plan review had run on such a bundle and returned no verdict. Five plan-gate test fixtures gained a request.md.

## T31 - the retro row

About 5 min. `task-add.next_id` reads the ids of the boxes and the plan's `## T<n>` sections only, so a title quoting "(385
T147)" no longer numbers the next task T148.

## T32 - the retro row

About 30 min, the largest. What holds a landing is now the clone's active task, while it (or a box nested under it) is open
and the landing does not tick it; tasks nobody has started hold nothing, the GM-review box never does, and the `**Lands open**:`
line, its review and the tick's "mark the tooling did not put here" refusal are gone (the GM: no Lands open line). The push
suite's in-progress cases now start their task; the CI merge reads the same rule. **The habit it changes:** `make task-start`
is what makes a task's work held until it lands - a session that skips it lands mid-task work unheld (the plan review's limit).

## T33 - the retro row

About 25 min. `make land F= T="<one or more>" NOTE=` (and `make land-batch`, the same script) asks every cheap refusal first
and prints them together, then runs `make done` and `make cohort-landing` only where their records do not cover the content,
commits what they regenerate under `pool/`, pushes with the tasks named and ticks them. `land-batch.py` is gone.

## T34 - the retro row

About 10 min. The push fetches, takes its delta and asks the holding rule, the review gate and the plan gate before
`push_checks.py` and the claims gate; a held push refuses before any of those run.

## T35 - the retro row

About 10 min. `sync-with-main.sh done` starts main's render-sync in the background (the prompt hook's lock and log) and returns
once the work is on main; T12's push spent 2.5 min there on other sessions' maps.

## T14 - the retro row

The second one-claim experiment (the GM, 2026-10-20), the first landed with `make land`. The plan's `make decide` refused an
unlabeled figure again, as on T12; the walk alone would have kept stubs off a way, so D9 brought `_trim_to_service`'s
feature-261 rule into the sweep. The step-back met the claims round. Timings: `landing-analysis-2.md`.

## T36 - the retro row

About 35 min with B. The bundle marks the change's lines; the check tags what rests on none of them; the gate carries it and
`make land` files the carry. Measured on the next claim task.

## T37 - the retro row

About 5 min. A notice in `claims-owed` and `claims-bundle`; `claims.py main` sat at the 100-statement cap and needed one fold.

## T38 - the retro row

About 10 min. A `SubagentStop` no longer ends a wait on the GM; the test replays 405's own overnight events.

## T39 - the retro row

About 5 min. A claims-bundle pass is the active feature's.

## T40 - the retro row

About 25 min. A changed function is judged whole; an unchanged line of it is refused only on the gate baseline's evidence that
quick-tier tests alone reached it (`sweeps.py:738` was exactly that).

## T41 - the retro row

About 35 min. One predicate (`preflight.unseen`) for the tree check and the gate-write guard. The first plan review blocked
`plan.md` and every feature's `tasks.md` as unseen; narrowed to the active feature's records. An apostrophe in a comment inside
the guard's single-quoted Python broke every case of its suite until removed.

## T11 - the retro row

The third one-claim experiment (the GM, 2026-10-21), the first after T36-T41. The fallback the claim called DRIFTED never ran
(`web_cuts` puts every cut within reach of a house), so the fix is its removal and a test of the invariant. Timings:
`landing-analysis-3.md`.
