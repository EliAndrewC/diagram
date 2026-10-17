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
| 17:05 | three red gates, each a different small cause (claim backing form; a lint the session would have caught with `make quick` first; one uncovered line); the red-gate tripwire's ruling `continue`, with a tooling fix | the gates |
| 17:30 | the pop-up and claim checks the two drawing-page bullets owed: 10 depictions (one EDIT applied, one finding filed), quote and format (one word fixed), 154 claims (13 labels this change introduced, fixed) - then the one-word fix re-owed every one of them, cleared by two triages | the green gate |

## T01 - the retro row

**The split (by hand; T02 builds it).** Task start 15:31. Decision points: 15:40, 15:46, 15:52, 16:00 (part B), 16:08, 16:24 (a
correction), 16:50 (the seed 38 fix), 18:47 (the glyph-check's F1, carried to T03). Up to the seed 38 fix: about 79 min.
After it, to the checks answered (about 18:10):
about 80 min, almost all of it gates and checks. Re-decides: five plan reviews (round 1 BLOCKED, then CHANGES on a corrected
fact, then three block rounds), one part B.

**Where the time went, largest first.**
1. **The check cascade from two bullets on one research page** - about 25 agent dispatches and roughly 6 M input tokens: 10 pop-up
   depictions, two claims triages, three `impl-drift` rounds (154, 27, 7 claims), quote and format checks twice. Most came back
   clean. Then a one-word vocabulary fix the format check asked for re-owed every unit keyed on the page, because each answer is
   keyed to the page as bundled while a triage diffs against an older baseline.
2. **Guessing a cause from a refusal's text, three times** (seed 24's "fence", seed 38's "foot through a yard", and the plan's own
   premise that the angle rules were refusing seeds). Each guess cost a build and a roll; the geometry dump or a bisection answered
   each in one run.
3. **Three red gates** for small mechanical causes, one of which `make quick` would have caught first.
4. **Two guard defects found and fixed** (plan-delta never re-owing a block left BLOCKED; the red-gate bundle reading pytest's
   cumulative cache), and one tooling fix owed by the round arbiter (a crashed roll's traceback kept).

**Which checklist items fired.** A3 (where each number comes from) settled the classification at once - 0081 itself says every
limit is a convention. A6 (the exits) chose the exception and the merge, exactly the GM's two. Part B fired at 16:00 and turned
the task from the angle rules to what was actually refusing - the checklist's best moment.

**Which should have fired, and the changes made to the checklist.**
- B1 was answered from the refusal's TEXT twice. Amended: "look at the geometry - dump the lanes and what stands near them - before
  naming a cause; the refusal names the test, not the ground."
- C2 should have stopped the lint red gate. Amended: "`make quick` before every `make done`, not only while iterating."
- C1 did not cover a fix one check asks for re-owing every other check of the page. Amended: "a check's own fix to a shared page
  is applied only after every check keyed on that page has returned, so they re-run once together."

**Process changes for T02 (tooling, the GM's to approve in T02's plan).** (a) A triage diffs against the page version the last
check READ, not an older baseline - the largest single saving here. (b) One quote-check batch answers a page-wide
`#unfootnoted` unit. (c) The claim-backing form is checked by `make quick`, not only by the full gate.

**After the draft (18:10-18:53).** The village-lane glyph-check on Inashiro returned NEEDS-WORK: Inashiro did not change at all
(none of T01's merges fired there), yet it shows a fourth side-by-side shape - a door stub and a lane running 12-25 ft apart over
open ground, joined by a 90-degree rung - that escapes the doubled-tail cut only by `_ALONG_MIN_FT`, an UNRESEARCHED 30 ft.
Accepted (`make accept`, the GM's review) and carried to T03 as its first item. **This is the task's most important finding:**
"two paths side by side become one" wants the PRINCIPLE implemented - parallel runs within reach over open ground become one
path, whatever joins them - not one detector per shape; T01 built three detectors and the review found the fourth on an
unchanged map. T03 decides whether the merge is one general test.

Also after the draft: two more tooling fixes the round arbiter owed (a crashed roll's traceback kept; `make verify` and
`make verify-wait`, each gate its own log), one bug in the second of those found on its first use (the wait matched the
preflight's own quick line) and fixed, and a deadlock in the arbiter-fix rule fixed (an engine fix can only land with its
feature, so it is now done with its test committed - `ENGINE=1`). The session edited files during a running gate twice, the
second time an hour after the arbiter warned of it: C3 below.

**One more checklist change.** C6 (new): "Nothing is written to the tree while a gate runs - not a record, not a ledger row, not
a fix to the wait itself; queue it and write it after the verdict."

**The numbers for SC-001's comparison (T01, by hand).** Wall time 15:31-18:53, about 3 h 22 min, against a six-hour budget; time to
the last design decision about 79 min; re-decides 5 plan rounds and 1 part B; agent dispatches about 45 (the event log's count for
the feature: `make feature-report F=385`); red gates 3; regressions found by the cohort 1, fixed.

## T02 - the retro row

**The numbers (from `make feature-report F=385`, the per-task table T02 itself built).** Start 19:41Z (backfilled by hand from the
event log: the first edit of T02's plan, written with amendment 2), all seven items landed on main by 20:41Z: about 1 h 05 min
against a four-hour budget. Decision points: the three plan rounds (BLOCKED, BLOCKED, CLEAR by 20:07Z), the time after the last
about 35 min. Red gates 0; check dispatches 3 (the plan rounds); regressions 0.

**Where the time went.** The plan rounds (about 25 min: D13's first form let `git add` and `make record-checked` through, D9 had no
floors) and then straight construction, each item landed alone in value order as the Approach block said (A8) - so the stop
risk the block named never cost anything.

**Which checklist items fired.** A5 (measure first) on D11: the triage already diffed against a kept blob, and the measurement
found the two real causes (a triage answer erasing it; one listing shared by every unit) - the fix was two records kept, not a
new diff. A6(c) chose "keep what a check read" over a smarter diff. B did not fire: nothing resisted.

**What changed from the plan.** D8's refusal lives in a new `scripts/gates/approach_gate.py`, called from `make tick` beside the
plan check, rather than inside `plan_gate.py`: the three triggers share its `owe()` and its block parser, and `plan_gate.py` stays
a plan-review module. Found and fixed on the way: the test-deps monitoring callback raised at interpreter shutdown in every
tooling run (pre-existing; the guard its sibling `_hook` already had). The T02 start was first seeded as 20:05Z, a guess; the
event log put it at 19:41Z - `make task-start` now records it, so T03 on is measured, not reconstructed.

**For T03.** T03 is the first task the whole kit measures: `make task-start F=385 T=T03` first, its Approach block (D8) after the
blind agent's (FR-012), any part B a trigger owes (D9), and its row in the per-task table compared with T01's 3 h 24 min and
11 decision points.
