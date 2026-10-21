# T11, the third one-claim experiment, measured - the first after T36-T41

The GM, 2026-10-21: *"When you've landed these performance / process improvements, please work 1 more claims task and then
measure the results ... whether our fixes now take the amount of time they "should" take."* T11 (385 T124):
`ways/web.py::_web_cut_lines._extent` fell back to every house in the cluster when none stood within reach of a cut. Reading
`web_cuts` showed the fallback never runs (every cut lies within reach of the house that called for it), so the fix is its
removal and a test of the invariant.

## What happened (measured 2026-10-21 from the commits, the agents' durations and the run logs)

| UTC | what | cost |
|---|---|---|
| 04:42:47-04:43:23 | `make task-start`, the code read (`_extent`, `web_cuts`, where WEB_REACH_FT comes from), the plan section | 0.6 min |
| 04:43:23-04:44:36 | the plan review (61 s, CLEAR), the fix and an invariant test over 200 rows - in parallel | 1.2 min |
| 04:44:36-04:45:05 | the GM's words recorded, committed | 0.5 min |
| 04:45:05-04:45:32 | `make done` in the background: its preflight refused in seconds - my comment put `web.py` at 1,002 lines | 1 refusal, ~1 min |
| 04:46:22-04:48:44 | **the claims round, beside the running gate (E)**: triage 12 s, impl-drift 27 s - IN-STEP in ONE round - recorded and committed while the gate ran | **2.3 min** |
| 04:46:25-04:51:17 | the gate: RED on the 100% floor, `web.py` 888-889 - lines T11 never touched | 4.9 min |
| 04:51-04:55 | diagnosed: the gen cache served the two row villages and replayed their coverage by line number over lines T11's comment had shifted (a defect older than this feature) | ~4 min |
| 04:55-04:57 | `make land` refused once: an impl-drift pass with no ledger row - D traced it but nothing wrote it; `land.py` now writes the feature's traced rows | 1 refusal, ~2 min |
| 04:57-05:02:38 | `GATE_NO_CACHE=1 make land`: the floor was 100% (the diagnosis confirmed), but the roll census refused the run (Inashiro rolled 20 times) - the old recovery no longer works | 5.7 min |
| 05:03-05:04:51 | T42 filed, planned, reviewed (44 s, CLEAR), built and tested: a cache hit only over the bytes its coverage measured | ~2 min |
| 05:04:51-05:06:55 | `make land`: the preflight refused `gencache.py:765` - a changed line no quick test runs, though the gate's pool sweep does; F now asks the baseline about the FUNCTION too | 1 refusal, ~2 min |
| 05:09:12-05:19:45 | `make land`, unattended: preflight 109 s, the gate green (to 05:14:17, every pool map re-rolled under T42), hooks-test, the landing cohort (to 05:17:25), the push, the ticks, their push | 10.6 min |

**Start to landed: 37 min** (04:42:47-05:19:45), against T14's 39.5 and T12's 35. But the shape is new:

| | T12 | T14 | T11 |
|---|---|---|---|
| plan, fix and tests | ~10 | ~11.5 | **2.3** |
| the claims round | ~4 | 11.4 (three rounds) | **2.3 (one round, beside the gate)** |
| the step-back | ~4 | ~2.5 | 0 (inside the hour) |
| session round trips at the landing | 7 | 2 | 4 - each a defect found and fixed |
| landing machine time | ~11 | 17 | 10.6 clean, plus 10.6 of red runs |

**The claim itself took 6 minutes** (04:42:47-04:48:44: code read, plan, review, fix, test, claims round recorded), and the
clean landing 10.6 unattended. **What T11 "should" take is ~17 minutes; it took 37 because the run found and fixed four
defects** - one mine, three in the tooling, two of those introduced by T36-T41 themselves:

1. **My comment pushed `web.py` past the 1,000-line bar** (1,002). The preflight caught it in seconds - the cheap-refusal-first
   order working - but a session should see a file's size before it adds lines to a file at 998. A one-minute cost.
2. **The gen cache replayed coverage over shifted lines (T42, filed and fixed).** Older than 405: a map is served while no
   function it executed changed, but an edit to ANOTHER function in a file it measured shifts the lines under its stored
   coverage. Any claim task whose edit adds or removes lines in a hamlet-path module above code only some maps run would have
   met it. It cost one red gate (4.9 min) and the bypass run (5.7 min), and `GATE_NO_CACHE=1`, its documented recovery, is
   refused by the roll census. **Its fix has a cost the next gates will show**: an edit anywhere in a file a map measured now
   re-rolls that map (all five re-rolled here, the gate 192 s).
3. **D was half done**: it traced a claims pass to the feature, but `make land` wrote only the plan reviews' rows. Fixed in
   `land.py`; T11's own landing then wrote T42's plan review row itself.
4. **F refused a line the gate's own tests reach**: a changed line in a module off the hamlet path, which only the pool sweep
   runs. The rule was older than F; F's baseline now answers it too (a changed line whose function a gate-tier test ran at the
   last green gate is the gate's to judge).

## The fixes, measured

| fix | on T11 |
|---|---|
| A - findings outside the change carried | not exercised: the one claim came back IN-STEP; the outside finding was filed as a row (`found.jsonl`) |
| B - a new unit's inherited NONE named | not exercised: no new unit |
| C - the step-back clock | not exercised: the run began a minute after the 04:41 ruling and ended 38 minutes later, inside the hour; its test replays 405's overnight events |
| D - claims passes traced | **worked after its gap was fixed**: the last landing wrote its ledger rows unasked |
| E - the gate beside the claims round | **worked**: `claims-triaged`, `claims-checked` and a commit of their records all passed the guard while the gate ran, and the gate's tree check read the run as unmoved |
| F - the preflight judges changed functions | **worked after its gap was fixed**: refused `gencache.py:765` wrongly, then left it to the gate, which covered it |
| `make land` | one command per attempt; every refusal was named in seconds, and the clean run went start to ticked unattended |

## What is left, and what I would do next

- **Run one more claim with nothing new to find.** The process for a claim is now ~6 minutes of session work plus ~11 of
  unattended landing; T11's 37 was the debugging of four defects, each fixed and landed. The next run should show ~17.
- **T42's whole-file rule re-rolls more maps than it must** (the plan review's aside). Remapping the stored lines through a diff
  (as F maps the baseline) would keep a map served across an edit to a function it never runs; deferred in T42's plan, worth
  doing if the gates' times show it.
- **The file-size bar**: `check-file-scale` could be asked by the same hook that runs after an Edit (a line count at 990+ is a
  warning at the edit, not a refusal at the gate). Not filed - a one-minute cost, seen once.
