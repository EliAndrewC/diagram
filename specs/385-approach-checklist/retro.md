# Retros - feature 385

One row per closed task (FR-006), and while a task runs, its decision points as they happen (they are what the per-task split
divides at, FR-005; T01's are kept by hand until T02 builds the split).

## T01 - the lane law (in progress)

### Decision points

| UTC | what was decided | what prompted it |
|---|---|---|
| 15:31 | start; plan drafted with the Approach block (part A) | the GM's go |
| 15:40 | the order changed: name the refusing rules (D3) before shaping D2/D4; D2 split into turn and meeting; D4 reuses the tail cut | the advisor, before the plan review |
| 15:46 | D4: a side-by-side needle is merged, never refused; D2's ground is the settle's two obstacle families | plan review round 1 (BLOCKED) |
| 15:52 | D3 landed in the clone (`lane_breaches`) | plan CLEAR |
| 16:00 | **part B fired** (the plan's own stop): at HEAD no seed is refused by an angle rule - seed 21's five lanes break `fabric` only, seed 17 is a reach. Under the wave 155 patch seeds 10 and 24 fail `lane_knots`: seed 10's gather refused by `needle_loops` (a sliver between two ways, the side-by-side case), seed 24's by `fabric` (the two ends lie either side of a garden or yard: an obstruction) | the D6 baseline (`.git/cohort48-d3.log`, 50/54 as HEAD) and a scratch diagnosis of `settle_knots` in a detached worktree |

### Part B, answered at 16:00

1. **What is refusing?** Not the angle rules. The knot rule (`knots.knots`, the gate's `lane_knots`), whose gathers are refused for a
   sliver (`needle_loops`) or for fabric between the two ends.
2. **Its class, checked:** the knot rule's principle is 0081's (*"Ends within 25 ft of one another are joined at a single point, so
   three lanes never arrive a few feet apart in a knot"*); the 25 ft is O (the page: limits *"chosen at the scale of a dozen paces"*).
3. **Does it describe the world there?** Seed 24: two ends 24.8 ft apart with a garden or yard between them are two paths either side
   of a fence, not three lanes arriving in a knot - the rule describes open ground only. Seed 10: a gather that leaves two ways
   bounding a sliver is two paths side by side - the GM's merge.
4. **Moving something placed earlier?** No - both fixes stay in the web.
5. **Tuning or changing?** Changing: the plan's five rules missed the knot; the plan is amended, not tuned.
6. **The one-sentence test.** "Two path ends either side of a fence must be joined at one point" - the GM would ask why.
7. **Next measurement.** After the amendment: seeds 10 and 24 under the patch, then the cohort.
