# Plan - feature 405: the engine and record findings moved from 385

Spec: [`spec.md`](spec.md). Tasks: [`tasks.md`](tasks.md). One section per task, written at its start; the approach checklist
is `docs/approach-checklist.md`.

## T12 - `_trim_to_service` walks every end in, never pops a whole segment (385 T126)

### T12 Approach (checklist part A)

1. **The goal, in the world.** A lane that runs on past what it serves ends where it last serves something, not a whole segment short of it: the stretch of its last segment that still comes within reach of a house, a way, the bund or a steading stays drawn.
2. **The constraints.** 0246's drawing page: "a lane end that reaches nothing is pulled back to the last house it serves", with the 60 ft reach to a house or way and 12 ft to a steading's built ground (`WAY_END_REACH_FT`, `end_serves`). `_trim_to_service`'s own claim: "ends trimmed to what serves, 4 ft at a time". The law gate (`lanes_reach_something`) asks the same bar of every end. The gate and the landing cohort.
3. **Where each comes from.** The pull-back to the last house served: R (0246 drawing page, its "Lane ends" section); the 60 ft and 12 ft: R, labeled GUESS on that page; the 4 ft grain: O (the walk's step, `_trim_to_service`).
4. **Do they describe the world here?** Yes - measured 2026-10-20 by reading `ways/geom.py:546-563`: the first two loops pop a whole vertex while the end does not serve, so on a run whose last segment is long and whose inner part passes within 60 ft of a house, the end jumps back to the previous vertex, past the last point that served; the 4 ft walk below, which does stop at that point, runs only after the pops. The impl-drift round of 385 T106 recorded it DRIFTED.
5. **The order.** The two pop loops removed, so the 4 ft walk (which already drops a vertex once the end is within 4 ft of it) is the one pull-back for every end; the claim's line unchanged; a unit test red without it; the cohort; the claims round on the changed unit; the gate and the landing cohort.
6. **The exits.** (e) conform - the research says pull back to the last house served, and the walk already does; (a) a coarser step to save time was weighed and refused until the cohort shows a cost (the walk is per 4 ft per end, run per lane).
7. **The search smell.** None.
8. **The budget.** 45 min with the landing.
9. **Done, measured.** One goal: `_trim_to_service` on a run whose long last segment passes a house within 60 ft partway ends on that segment within 4 ft of its last serving point (a test red at HEAD); the claims round reads the claim IN-STEP; the gate green and the landing cohort refusing no seed against main.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T12 Decisions

**D1 - one walk for every end.** `ways/geom.py::_trim_to_service` loses its two vertex-popping loops (`while len(out) > 2 and not serves(...)`); the existing two-pass 4 ft walk pulls each end in along its own last segment, popping a vertex only when the end is within 4 ft of it, so every end stops within 4 ft of the last point that serves. The comment above the walk says so (it no longer explains a two-point-arm special case). The claim "pulled back to the last house served ... 4 ft at a time" stands as it is.
