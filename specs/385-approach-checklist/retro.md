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

## T03 - the blind Approach compared with the sealed conclusions (SC-006)

The blind block (FR-012) was written by a fresh Opus agent between 20:47Z and 20:59Z from the task text, `checklist.md`, this
file, `lane-law-table.md`, the code and the record; it is copied into plan.md as `### T03 Approach`. The session's own
conclusions were sealed before amendment 2, outside the repository. Rule by rule:

| subject | sealed (the session, before) | blind (the checklist, without hindsight) | verdict |
|---|---|---|---|
| seed 21 (`fabric` on five access lanes) | our rules in conflict: research (0081, 0246) lets a household be reached across a neighbor's land, so the exit is to reclassify, not repair | names 0246's fallback "reached across a neighbor" and the 7 ft gap as O (a convention), but chooses: dump first, then the O gap weighed against more room | **partly raised.** A3 found the O number; A4 asked "does it hold here?" but could not look (no manifest), so the exit that dissolves the case was listed, not chosen |
| seed 17 (field reached by no way) | the refusal is ours; question whether refusing the map is right at all, vs a field path or bund counting as reach | finds the 60 ft `FIELD_REACH_FT` is O and **mislabeled** R (neither 0014 page says 60 ft); exit: 0014's own fallback (the nearest lane runs on to the bund), after measuring why each run was refused | **raised, and further than sealed** on the number (the mislabel was not in the sealed notes); did **not** ask whether the refusal itself should exist |
| seed 40 (`farm_not_on_its_street`) | not looked at | the street's join excluded from "own street" is O (seed 904's judgment); one predicate for placer and check | new |
| seed 45 (`fixtures_on_groves`) | not looked at | placer and check read different boxes (the 10-degree `in_frame` skew, UNRESEARCHED) - conform by one predicate | new |
| the side-by-side shape | one general merge test, not a fourth detector | the same; `_ALONG_FT` 14 and `_ALONG_MIN_FT` 30 are O, the merge principle G, the reach the one open number | **match** |

**What the checklist missed, and the change it calls for.** Both misses are one gap: the checklist asks what a rule describes
(A4) and lists the exits (A6), but never asks **whether the refusal itself should exist** - whether a map that breaks the rule
is actually wrong, or the rule is a tidiness we impose. Proposed A4 addition, for the T03 retro to confirm: *"If the map broke
this rule, would a reader of the research call the place wrong? If not, the rule is a preference: a tie-break, not a refusal."*
A second, smaller one: A4 could not be answered for seeds 17 and 21 because a refused roll keeps no manifest - the blind agent
found the same tooling gap T01's retro named.

## T03 - the decision log

Times are the event log's (`<git dir>/l7r-events/385-approach-checklist.jsonl`, each agent's start and stop); a step between two
of them is placed by its order, not given a time of its own. (A first draft of this table carried times written from memory, up
to an hour late; the hour-6 step-back caught it, 2026-10-17.)

| UTC | point | what decided it |
|---|---|---|
| 20:44 | started (`make task-start`) | - |
| 20:45-20:56 | the blind Approach (FR-012) | a fresh Opus agent, 11 min |
| 21:05 | plan round 1 BLOCKED: D20(1) took a side on code alone | spec-fidelity |
| 21:08 | plan round 2 CLEAR | spec-fidelity |
| 21:08-21:41 | D16 built (a refused roll keeps its manifest; refusals name their rule); seed 17's field runs turned down by fabric x122, doubled_tails x88, needle_joins x30; seed 21's five lanes come within 7 ft of nothing but their OWN garden and yard (3.1-6.8 ft) - neither the sealed guess (a neighbor's yard) nor the blind block's (stand-ins); four geometry probes on the dump answered questions nobody had asked, then the refusal made to name the part (`foul_part`) said it at once | the dumps |
| (same) | the cause: a garden is recorded with no owner, so a household's way was held 7 ft off its OWN garden fence; fixed as D20's O gap (`owned_gardens`); seed 21's second refusal (a farmhouse unreached) - **part B** after three attempts; its cause: a way drawn by the reach dropped by the network rule before any join reached it, in the last resort's passes; seed 45 fixed by one band predicate; bisected: the own-garden change fixes 17, 21 and 40 | a temporary drop probe; toggles |
| (same) | the 60-seed cohort read 59/60 (only 49) - but it was `N=54` and never rolled 55-60; seed 49 refused at HEAD too (a detached worktree) | the cohort, the worktree |
| (same) | D17 as first decided (REACH inside `along_tail`): the reference map refused a farmhouse, then a tree lane `doubled_tails` the settle may not cut - **part B**, D17 re-decided | three rolls |
| 21:45 | the re-decide CLEAR | spec-fidelity |
| 21:45-22:02 | the merge as its own step: never fired on Inashiro F1 (its rung corner 21.8 ft off) - REACH 25 ft, the rung as the approach; cuts undone by the reach each round - `set_corridor`; F1's cut stranded lane 15 - carried (`reseat_on_way`); F1-F3 merged, seed 49 passed; **the 60-seed cohort: 58/66, six seeds regressed** - the merge reverted, saved; the confirming cohort 63/66 (49, 55, 57 refused, all three at HEAD too) | rolls, a cut log, cohorts |
| 22:05-22:06 | the hour-6 step-back (route (a) once seed 57 is bisected) and the ask's ruling (route (a)) | round-arbiter, twice |
| 22:06-22:20 | seed 57 bisected: 4 knots with T03's changes, HEAD 1; the join order kept in the last resort alone brings it to 2 (the four seeds still pass); the last +1 comes with the own-garden fix and is refused by `needle_loops` (the carried task's family) - put to the arbiter | toggles, a gather-refusal log |

### Part B, answered between 21:08 and 21:45 (seed 21's farmhouse, the third attempt)

1. **What is refusing?** `unreached_houses`: the household's way is drawn and then dropped by the network rule; its far end stood
   8.6 ft off lane 14's end and 18.8 ft off lane 9.
2. **A3 again.** One network: R (0246). The join reach, 25 ft: R (0081). `AIM_DEG` 60: O.
3. **A4 again.** Yes - on open ground anyone walks the 9 ft; the web failed to join it.
4. **Moving earlier for later?** No.
5. **Tuning or changing?** Two reorders made; a third would be tuning. So the next step was a measurement (who drops it, and in
   which pass) - it found the last resort's own pass list, the third place with the same order.
6. **The one-sentence test.** "The path stops 9 ft short of the lane beside it and the map is refused" - the GM would ask why it
   is not joined; that was the question to answer.
7. **The next step is a measurement**: the drop probe.

## T03 - the retro row

**The numbers (`make feature-report F=385`, the per-task table).** Started 20:44, ticked at 23:09 (the table: 2 h 25 min, 11 decision points, the
last at the tick), against a 4 h budget. Up to the first green gate (22:38): eight decision points (three plan rounds, the re-decide, three arbiter rulings, the landing
form), the last about 15 min before the gate. **The hour on D17's merge (about 21:08-22:02) is T03's own** (the plan review's
condition): it was tried, measured and carried, not avoided. Red gates 1 (two branches the split left uncovered). Check
dispatches: the blind Approach, 5 plan rounds, 3 rulings, 2 triages, quote-check, record-format, impl-drift, modal-depiction.

**What landed.** Seeds 17, 21, 40 and 45 pass. Against HEAD nothing newly fails. The pool is clean, and Kashikawa's lane 9 now
runs straight past its own garden fence instead of bending round it - a result of the fix, not a side effect to undo.
Seed 57 stands at 2 lane knots against HEAD's 1, waived by `ask:t03-seed57-residue`. Its grounds: the refused set is unchanged,
the extra knot comes with the own-garden fix that clears three seeds, and chasing it inside T03 is the side-by-side family
that broke six seeds. The merge, seeds 49 and 55, and 57's residue are T12's (D25).

**The blind Approach (SC-006)** - compared above, rule by rule. It was the better half of the session's own reading. It found
the mislabeled `FIELD_REACH_FT` and the two concrete causes the session had not looked for (40, 45), and matched on the merge.
It missed the question that decided seed 21 - is the refusal itself right? - and so did the sealed notes: both guessed a
neighbor's yard or a stand-in, and the dump said "their own garden". The checklist now asks it (A4).

**Which checklist items fired.** B1 (look at the ground before naming a cause) decided seed 21, 49 and 57 - every guess made
before a dump was wrong. B5 (the third tuning is a step back) stopped the REACH loop at its third move. A3 found the
mislabeled reach. Part B was written three times; each named the measurement that came next.

**Which should have fired, and the changes made to the checklist.**
- A4's new question (above), which would have pointed at the own garden before any probe.
- C7 (new): a cohort's count is not its seed set. "59/60" was `N=54`, and two failing seeds stood outside it.
- C8 (new): times in a log are read from the event log. This retro's first decision log was written from memory, up to an hour
  off; the hourly step-back caught it.

**What the tooling did.** D9's approach gate fired twice on real work (hours 5 and 6), each time a short honest part B. The
arbiter fixed the cohort to compare seed by seed against HEAD with counts. The same-review re-answer fix saved a round.

## T13 - the retro row

**The numbers (`make feature-report F=385`, the per-task table).** Started 01:24Z (`make task-start`), done by 01:42Z: about
20 min against a one-hour budget, 4 decision points (three plan rounds - BLOCKED, BLOCKED, CLEAR - and the hour-8 step-back's
part B). Red gates 0; check dispatches 4 (three plan rounds, one arbiter step-back); regressions 0.

**What landed.** The claims gate carries a finding on a unit whose code and claim are unchanged since the merge base - a page
it cites changed, or it was only judged again - instead of refusing it as introduced (`claims.classify`, D26). An unfiled carry
refuses once, naming `make claims-carry F=<n> [T=<Txx>]`, which files it as an open task of the active feature only, with a row
in `claims-carried.jsonl` (D27); the open-task refusal honors that box, and ticking it un-files the key (D28). Changed code or a
changed claim still refuses; a finding standing at the base still warns.

**SC-007, replayed.** A scratch clone at T03's landed tree (`28d945bb3`), its base the main it was pushed onto (`dd7d619b8`),
the new tooling copied in: of the three findings the arbiter carried by hand, `settle.py::theirs` and `clearance.py::_clear_link`
come back `carry:`, and after `make claims-carry F=385 T=T12` they warn as `carried (385-approach-checklist T12)`. The third,
`Lawful.fault#no doubled tail`, is still introduced - correctly: T03 changed `Lawful.fault` itself (it returns rule names now),
so it is not unchanged code. Under the new rule T03 would still have needed one ruling, on that one finding, not three.
D29's filing into T12 was not needed on the live tree: T03 has landed, so its three findings now stand at the base and warn as
pre-existing (`make claims-carry F=385 T=T12`: "no carried finding is unfiled").

**Which checklist items fired.** A6(c) - the GM's option dissolves the case. B did not fire: nothing resisted but the plan
review, whose three rounds each narrowed the rule toward the GM's words (round 1: no carry for a moved unit, none into another
feature; round 2: a re-judgment on unchanged code is carried too; round 3's aside: with no active task the refusal names
`make task-start` first, not a command that would fail).

**What changed from the plan.** The push's verdict (`gate`, `classified`) moved into `scripts/record/claims_carry.py` to keep
`claims.py` under the 1,000-line bar; `claims.gate` delegates. The checklist needs no change from this task.

## T14 - the retro row

**The numbers (`make feature-report F=385`, its new tables).** Started 01:58Z, done by about 02:22Z: about 24 min against a
90 min budget, 5 decision points (plan rounds BLOCKED, BLOCKED, BLOCKED, the arbiter's `continue` on a last round, CLEAR). The
session made 61 of the window's 82 tool calls; its subagents 21 (all attributed by their transcripts). Red gates 0; check
dispatches 6 (four plan rounds, one arbiter, and none else); regressions 0.

**SC-008, replayed on T03.** `make feature-report F=385 SINCE=2026-10-17T20:44:00Z UNTIL=2026-10-17T23:10:00Z` now says 202 of
the window's 549 tool calls were subagents' (202 by transcript, 0 by window), prints T03's twelve phases and its skeleton. What
the corrected tables show that the old one hid: T03's session was WORKING about 130 of its 145 min and waiting only about 14 -
the reviews mostly ran while it worked on. Its own model time (the gaps between its own calls) was 92 min, spread over 347
calls: the median gap 7.4 s, the fastest tenth 3.7 s - about 18 min of T03 is the fixed cost of a call, paid 347 times (the
event log, read 2026-10-18). The phase 22:27-22:57 (the record checks after the 0246 edit) is 30 min with 8 of it waiting.

**What landed.** Whose call (D30): transcripts exact, the hook's `by` for the future, a run with no transcript of its own
estimated by its window, the session's own `Agent` launch always its own; a foreground run is waited on (D31); idle counted
apart; each task's phases (D32) and decision-log skeleton (D33) printed; checklist A9 one goal (D34) and C8 pointed at the
skeleton. The round arbiter's tooling fix on `ask:t14-plan-round4`: the ask check's pool demand fires only on a map question
(the bare word "route" refused a tooling question), and an ask about a plan review carries its rounds.

**Which checklist items fired.** A5 (measure first): the transcripts were checked for tool ids before any design, which
replaced the proposed window heuristic as the primary source. B did not fire - the work did not resist; the plan review did,
four rounds, each finding a real narrowing of the GM's words (the window fallback per run, a foreground run as waiting, a
contradicting leftover clause). Round 4's three wording rows went to T11 (the code already does each, tested).

**For T04, from these numbers.** Two levers are now measured, not guessed: the per-call cost (fewer, batched calls - the root
CLAUDE.md's "batch the lookups you already know you need"), and the record-check phase after a page edit. T04's row is read
phase by phase against T03's with these tables.

## T04 - the retro row

**The numbers (`make feature-report F=385`, the phase table and skeleton - T04 is the first task measured by them).** Started
02:36Z, ticked about 02:55Z: about 20 min against a two-hour budget (the guess the Approach named), 3 decision points (the hour-9
step-back, plan round 1 BLOCKED, round 2 CLEAR). Of the session's own time: about 15 min working, 1 min waiting; its subagents
3 runs, 7 min. Two cohorts (2 min each, the second a roll-cache miss); red gates 0; regressions 0.

**Against T03 (2 h 25 min), phase by phase.** T03's front (24 min) was 11.5 min of one-time blind Approach and two plan rounds;
T04's front was the Approach block and the HEAD cohort, 5 min. T03's seeds took about 50 min of diagnosis; T04 had none to do -
measured first, the re-deal already passed. T03's merge (21 min, a second goal) has no counterpart: the one second goal T04 found
(the cohort-record stamp) was split out by the plan review before any of its time was T04's (T15). T03's landing was 50 min of
record checks; T04 changed no engine, no page and no pop-up, so it owed none.

**What decided the time.** A5 and part A item 2 - "the baseline is retaken first" - before any design: the measurement ended the
task. Writing a web change from the 2026-10-13 numbers would have built a fix for two seeds that no longer fail.

**Which checklist items fired.** A2 (retake the baseline), A9's one goal (enforced by the plan review on the session's own D36:
the rule the session built an hour earlier, applied to it). B did not fire.

**What the tooling did.** The phase table and skeleton (T14) gave this row's numbers without a hand count. The hook recorded
`by` on every subagent call (12 of 12), confirming the payload carries `agent_id`. The hour-9 step-back found one guard gap,
closed as T16.

## T15 - the retro row

About 10 min (built inside T04's window, ticked once split): `cohort_known --stamp` before the record is committed, `engine_diff`
skipped by `baselines` and `approach_gate.newly_failing`; tests red without each. The record T04 rolled before the stamp existed
stays as written (append-only; 54/54, as HEAD's). No checklist change.

## T16 - the retro row

About 10 min: the review-round guard counts a plan review's rounds per active task back to its CLEAR and trips the round arbiter
at the third (`round:spec-fidelity|plan:<feature>#<task>@3`); `continue` lifts it by one, `ARBITER_OK` passes it. Its first real
use will be the next task whose plan reaches a third round. No checklist change: C-items had asked the session to remember this.

## Amendment 5 - T17, T18, T19, the retro rows

**The batching question first (the GM's).** Measured on the session transcript (2026-10-18): 346 of T03's 354 tool turns made
one call, but only 18 were a bare lookup - the one shape `batching-hooks.sh` blocks; the rest were folded lookups (143), scripts
(127), make steps (43), agents and edits. The hook does its job; the remaining single calls are dependent steps. No batching
change: the lever is fewer rework round trips (a refused command re-sent, a test re-run after a slip), and T17 and T18 remove two.

**The numbers.** About 45 min for the three (02:58Z to about 03:45Z), three plan rounds (BLOCKED, BLOCKED, then the plan-round cap
T16 built firing on its first real use, the round arbiter ruling `accept`). Red gates 0; regressions 0.

- **T17 (FR-017).** The push checks run `make-docs.py --check` wherever the tree keeps the page (`docs/make-targets.html`); a
  stale page is refused naming `make docs`. Its first run found the sync suite's fixture trees have no page - the check keys on
  the page, not the Makefile.
- **T18 (FR-018).** `make arbiter-fix-done ... LAND="<files>" F=<n> TICK=<Txx>` lands the fix, settles it and ticks the task, each
  step only after the one before succeeds; both refusals name it. Round 1 caught the first form leaving the tick out (the GM's
  "all three"); round 2 caught the Approach still saying two.
- **T19 (FR-019).** `make ledger-owed WRITE="<where>"` writes each owed row from the agent's reply; the refusals name it. Its first
  use wrote this amendment's two rows; the finding cell takes the reply's first line, which for a plan review is its verdict
  sentence - less pointed than a hand row, kept: the rows are written, not typed.

**The round arbiter's tooling fix on round:spec-fidelity|plan:385-approach-checklist#T17@3.** The cap's bundle pointed at
spec.md's Review history, which holds no plan rounds; it now carries plan-review.json's rounds (`plan_rounds`, T14's helper).
Settled by T18's one command - its first use.

**Which checklist items fired.** A9's one goal kept the three apart (three tasks, not one). B did not fire. The plan review found
the same miss twice (a two-step leftover) - the arbiter's ruling names it as wording, which the tests settle.
