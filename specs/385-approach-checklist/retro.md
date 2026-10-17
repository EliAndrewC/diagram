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

### Decision points, continued

| UTC | what was decided | what prompted it |
|---|---|---|
| 16:08 | plan amended: D4 made concrete (household way's foot, shallow crossing), D4b the knot rule reads the ground | part B; plan review round 3 CLEAR; the hourly step-back ruled `continue` |
| 16:15 | D4b built and tested | the plan |
| 16:24 | **D4b's evidence was wrong**: seed 24's two ends have clear ground between them - a household way's T-foot on lane 6 and the field way's start 24.8 ft along the same lane, a staggered junction; the gather failed for the fabric beside its own moved leg. Seed 24 goes to T04 (the re-deal); D4b kept on the GM's principle and its own test, its record corrected | seed 24 re-rolled with D4b (still knotted), then the geometry dumped |

**Lesson for the retro row (an audit-grade pitfall):** twice in one task the cause was read from which TEST refused, not from
the ground - the gather's refusal named `fabric`, and "a fence between the ends" was inferred and built. The geometry dump
answered it in one run. `settle_knots` should record why each gather was refused, as D3 now names a refusal's rules: the
diagnosis needed hand instrumentation in a scratch worktree, three times.
| 16:32 | D4 built: shallow crossings cut, a household way's foot re-aimed; seed 10 under the patch passes | seed 10's geometry dump (16:05) |
| 16:40 | D2 built: `ways/forced.py`, the law, the last resort, the settle's repairs and `Lawful` read one ground | the plan |
| 16:44 | D7: 0081's drawing page | the plan |
| 16:50 | **regression found**: cohort seed 38 newly refused (49/54). First guess (a foot re-aim through a yard) was built and did not fix it; bisected by commit (D4), then by half (the shallow cut of a household's way), then the cut dumped: a household's way had been hung on an ordinary lane a repair later cut. Fixed: a household's way is cut only onto the connector or a tree lane | the after-cohort (`.git/cohort48-t01.log`) |

The same lesson as 16:24, a third time: a guess from the refusal's text (16:50's foot-through-a-yard) cost a build and a roll;
the bisection and one dump answered it. Measure first is now three for three in this task.
