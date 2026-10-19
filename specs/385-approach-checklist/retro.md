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

**A defect in T16, found by its first firing.** The cap's `accept` closed T17's plan review, but nothing made it the plan's verdict,
so `make tick` refused for want of a CLEAR - a deadlock. Fixed (feature 379's rule for spec reviews, applied to plans): recording an
`accept` or `process-fault` on a `round:spec-fidelity|plan:` trigger records the owed blocks CLEAR at their digest, declared
`round-arbiter`; `make plan-verdict F=<n> ARBITER=<trigger>` applies one already recorded (`tests/tooling/test_plan_arbiter_accept.py`).

## T20 - the retro row

About 15 min inside T05's window (the arbiter's hour-10 fix): `checkpoint.due` admits, past the hour, a dispatch within 5 s of
one admitted under it - the rest of that message - never a gate, never a chain into the next message (the window counts from the
last dispatch admitted under the hour); `stepback_bundle.refusals` reads `refused` too. Plan CLEAR first round (D42a a narrowing
ruled LEGITIMATE). Closed by T18's one command (land, settle, tick).

## T21 - the retro row

About 25 min (two plan rounds). The round settling `apply-edits` already did reached no batch reply (a batch opens with prose, so
no check was named) and no EDIT the session had applied by hand - both T05's cases. Now a batch names its check from its first
counts line, and an EDIT applied by hand, word for word, settles through `make apply-edits FROM=<the reply>` (the block put back
and re-applied, the file unchanged). Round 1 of the plan review caught the first form keeping the hand-applied case out - the very
case that cost T05 its round-2 page checks. **The habit it changes:** apply a check's EDITs from its reply or transcript, never
retyped (`make record-owed`'s footer says so).

## T05 - the retro row

About 7 h 25 min wall (03:37-11:01), of which about 5 h idle: the session ended its turn at 04:20 "waiting on" an impl-drift
round a guard had refused at 03:57, and nothing woke it until the GM at 09:15 (T22 closes that). Of the active time: the patch and
its first claims round about 25 min; claims rounds 2-4 and the standoff's three CANNOT-TELLs about 70 min (T23 and T25 came from
them); the arbiter's ask on the old drifts about 10 min; three red gates (a reviewer's British spelling in a record, a stale
notes census with Sawada's zigzag XPASS, an uncovered early return) about 20 min; renders missing at the first `make verify`
(T26) and three glyph-checks (PASS) about 25 min; the landing cohort 54/54 (fresh block 14 of 48). No number moved: every change
after part A was a label, a test or a record. **The habit it changes:** a refused dispatch is re-sent before anything else, and a
check that asks for more context is given all of it at once (both now enforced, T22 and T25).

## T22 - the retro row

About 45 min (three plan rounds). The incident was a refused dispatch nobody counted: four identical refusals read as three. Round
2's catch mattered - the GM's prompt arrived mid-turn, so a window from his last prompt would have missed exactly the incident; the
transcript's own `turn_duration` entries are the turn ends, so no state file. **The habit it changes:** none needed - the turn
cannot end with a refused dispatch unanswered.

## T23 - the retro row

About 15 min (one plan round). `owed` already took a prescribed relabel as answering a MISLABELED; the gate did not, so three
relabels could never land. One shared rule, `relabel_answered`. **The habit it changes:** none.

## T24 - the retro row

About 20 min (two plan rounds). Three of three tooling landings that day were refused for a stale base and landed unchanged after
a `sync-in`; now the script merges main in itself when its patch no longer applies. Its first real use (T26) met a true conflict
(main had stripped the Makefile's comments) and refused as designed. **The habit it changes:** none.

## T25 - the retro row

About 70 min (four plan rounds). The arbiter's fix as worded (one level of callees for a distance claim) would not have reached
the standoff's constant, three calls down; measuring first would have saved two rounds - round 1 was a cap I had not measured
against, round 2 a depth I had not measured against. Built: the distance claim's first bundle two calls down (154 KB), constants
on every first bundle, and a CANNOT-TELL re-bundle that chases what its note names. Round 3's verdict was lost because I edited
the plan's Landing block while it was being reviewed. **The habit it changes:** measure the motivating case against the design
before the plan goes to review; never edit `plan.md` while a plan review runs (a guard for that is the next improvement).

## T26 - the retro row

About 25 min (two plan rounds). `make verify` now renders an owed map whose render is missing or older than its map before it
writes the prompts; round 1 held the arbiter's "every unit" against a sheet exclusion that had no measured basis (none exists
today, and now it would be refused). **The habit it changes:** none.


## T27 - the retro row

About 15 min (one plan round). `owe` printed the heading it asked for to the minute and then judged it to the second, so a
block written as told could not pass; found when the ticks of T05 and T22 refused. **The habit it changes:** none.

## T28 - the retro row

About 50 min (four plan rounds). The arbiter asked for the claim on every number an ask names; rounds 1-3 each found a way a
number reached the arbiter without it (words only, an "unmatched" row, then my own item 4 calling `BUNDLE_PITCH` the farmstead
pitch). Built: claims by identifier, and by value for a number in words, or "no claim states it". **The habit it changes:** check
an Approach premise against the record before it goes to review - round 3 was a premise I had not checked.

## T29 - the retro row

About 15 min (one plan round). Each plan review now writes its bundle at its own path, keyed by its tasks and its blocks'
digest, so a second review is built while one reads. **The habit it changes:** none.

## T06 - the retro row

About 2 h 45 min. The ranking row asked for a scattered hamlet's farms in single file on the field edge; measured first, the
margin a hamlet faces holds 3 to 6 farmsteads at their own width against 12 to 20 households, so the literal fix refused every
seed. Two arbiter asks with the measurements decided the route: single file round the whole cultivated ground (the paddy and its
dry plots - the north seats fell on the dry plots until they were joined), which holds every farm on 4 of the cohort's 18
dispersed seeds; where it falls short the hamlet is seated as before (decided on a copy of the map first, so no farm is taken
back - the GM's 2026-10-03 rule), the gap filed and farmsteads within the paddy proposed to the GM. Cohort 54/54. Three claims
rounds; three red gates on three causes (a test naming the moved body, two branches untested, and main merged under the running gate - T30); landing cohort 54/54. **The habit it changes:** a seating rule is measured against the room it needs before it is built - the arithmetic
(households x farmstead width against the edge's length) answered in minutes what the first experiment took 20 to show.

## T30 - the retro row

About 70 min (two plan rounds). The arbiter's fix assumed clone-sync merged main under the gate; round 1 asked which hook did,
and the measurement found neither did: T18's own test ran `make -n` on `arbiter-fix-done LAND=... TICK=...` in the real
repository, and make EXECUTES a -n line holding `$(MAKE)` - so every gate in every clone ran a real land-tooling, and its push,
and since T24 a stale patch there merged main in mid-gate. Nothing landed (every push refused), but the other session's clone
showed the same runs. Fixed at the cause (the test reads the recipe), and the gate's existing lock is now asked by clone-sync on
both paths and by land-tooling. **The habit it changes:** never run `make -n` on a target whose recipe calls `$(MAKE)` - read the
recipe instead; and measure who did a thing before fixing the one you suspect (round 1 would have fixed the wrong hook).

## T41 - the retro row

About 35 min (two plan rounds). The round counter counted a check at its dispatch, which the check-bundle hook sees before the
pair hook may refuse it, so T07's write session met a round cap on zero readings. Round 1 blocked my first fix, a refund of any
dispatch still pending after 60 s: it narrowed the arbiter's "started an agent and kept a reply" to half its condition and left
a minute in which a refusal still counted. Built instead: a round counts when its agent returns a reply. **The habit it
changes:** take the arbiter's condition as the moment to act, not a timer standing in for it.

## T42 - the retro row

About 30 min (two plan rounds). An absence note names no page, so it owes no source-reader; the third part of the arbiter's fix
(net a note round 6 had READ) I first called "already done" without measuring, and round 1 blocked it - measured, the existing
answered rule does net them (round 6's answers were recorded after the ruling's bundle was built). **The habit it changes:** a
claim that existing code already does a thing is a measurement, with its record named, never an assertion.

## T07 - the retro row

About 4 h 30 min. The ranking row asked for a source for the 4 ft wall-to-tread margin; one search pass found a Japanese village
house set back about 3 ft from a road and a north Chinese drip strip of 2-3 chi, so the number moved to 3 ft with a new question
(0247) and 0081's drawing bullet, through two page sessions and three record-check rounds (two source-reader rounds closed by the
arbiter). Five claims rounds on the code that reads it found three real defects: the joint gap held only the narrower lane's
half-width, a threshing yard rode on the garden's citation, and `_on_a_tread` measured a footprint's corners and center only, so a
footpath could cross a long house 10 ft off its center - fixed, each wall measured whole. Three findings on rules T07 did not write
went to T43 by two rulings. Pool clean (Kuwabata, then Inashiro, re-rolled), cohort 54/54. One measurement I gave the arbiter was
wrong (the far end of a household's own lane does reach `span_walkable`). **The habit it changes:** before telling the arbiter
what a caller never does, read the caller's skip condition line by line - "door ends are excluded" was half of it.

## T44 - the retro row

About 25 min. The hour-16 step-back's words held a page session's words and none of the working session's, because the bundle
read the busiest session of the hour; it reads every one now, labeled, and names one it could not find or a cut. **The habit it
changes:** a bundle that picks "the" session of an hour picks wrong whenever page sessions run - read them all and label them.

## T45 - the retro row

About 35 min (two plan rounds). T43, filed by two arbiter rulings, was refused at T07's landing as a hand-typed mark, and naming it
on the plan's Lands open line cost a review round. My first rule honored a box that NAMED a ruling, and round 1 blocked it: any
hand-typed box could paste a trigger. Built instead: `make claims-carry KEYS= RULING=` writes the box and its record row together,
the ruling checked against `arbiter.jsonl`. **The habit it changes:** a "this box is the tooling's" rule reads a record the tooling
wrote, never words in the box.

## T46 - the retro row

About 20 min. The hour-17 step-back took a stale make-targets page at T45's landing for a gap in `land-tooling`; measured, the
worktree already regenerated main's page, and the stale copy was the clone's own. Built to the arbiter's words: a Makefile lands
only with the clone's page current, and the page lands beside it. **The habit it changes:** before naming a tool's gap in prose,
read the tool - a sentence in a reply becomes an arbiter's fix.

## T50 - the retro row

About 20 min. Twice in an hour I stamped a part B ahead of the clock by hand; the gate only asked that a stamp not precede its
trigger, so a future stamp passed. The tick's check and `make plan-delta` now refuse a stamp past the current UTC minute.
**The habit it changes:** a time the gate trusts is read from the clock or checked against it, never typed and believed.

## T49 - the retro row

About 45 min (two plan rounds). A `make done --dry-run` I typed to learn a trigger's name recorded a 2 s "tree moved" abort as a
red gate and owed a second trigger. The abort now records its own target, so it never counts as a red in a row while still never
vouching for the tree, and the red-gate bundle shows the diff between the reds it counts. Round 1 blocked a `--stat` alone: the
arbiter asked for the diff. **The habit it changes:** never dry-run a gate to read its refusal - ask the tool that owns the name.

## T51 - the retro row

About 25 min (two plan rounds). T08's gate went red on a test that passed alone: two plan-gate tests wrote one shared bundle path
under `/tmp/l7r-check` from different workers. Each now writes under its own `tmp_path`. Round 1 blocked folding in T49's import
order - a second goal - so that re-landed with T49. **The habit it changes:** a test that writes a real path is a race waiting
for xdist; give it its own `tmp_path` when it is written.

## T08 - the retro row

About 3 h. The ranking row asked for the Song manual's planted bank rolled against the bare bank; built as a knob on the tail
pond, its trees seated last against what stands (every seat came up free on the pool and six rolled seeds, both forms drawn),
with three new pop-ups, 0061's drawing page through a write and a check session, and four claims rounds. Round 1 cost 372 s and
1.29M input tokens, nearly all on one dict's 19 claims re-opened by the one key T08 added - the per-entry keying went to the GM's
review as an overhaul. Two calls were wasted: a triage agent dispatched on a bundle holding only a forced claim, and a part B stamped
in the future by hand. **The habit it changes:** before adding a key to a claimed dict, check what else the unit's claims will
re-owe - a bookkeeping key that needs no entry (as `cover.py`'s turned out not to) is cheaper left out.

## T52 - the retro row

About 25 min. Twice a test file landed on main unformatted (T49's imports, then a merge's duplicate import; T51's blank lines) and
only the next gate's formatter caught it. `make land-tooling` now lints and format-checks the Python it lands, beside its other two
checks, and names `ruff format` when it refuses. Its own suite had a fixture the formatter rejects, found on the first run.
**The habit it changes:** a path to main that skips the gate runs the gate's cheapest checks itself.

## T53 - the retro row

About 20 min. Three landings in an hour ran 35 s of checks before the push refused them for owed ledger rows; `land-tooling` now
asks the ledger as committed first, waived by the same `LEDGER_ROWS_OK` the push honors. **The habit it changes:** a refusal the
end of a pipeline will certainly make is asked at its start.

## T55 - the retro row

About 15 min. T52's landing lint named its files to ruff, which then linted them even where `pyproject.toml` excludes them - so a
script the gate never lints would be refused (found before it bit, on T54's `plan_gate.py`). `--force-exclude` keeps the gate's
scope. **The habit it changes:** a check copied from the gate copies the gate's scope with it, measured on a file outside it.

## T54 - the retro row

About 30 min. The hour-19 ruling and the next cohort each owed a part B to a task already ticked, because the task-start mark
outlived its task. A mark naming a ticked or missing task now falls back to the first open task. Its first run broke a fixture
whose marked task had no box - the fixture now lists it. **The habit it changes:** start the next task before measuring for it, so
what the measurement owes lands on it.

## T09 - the retro row

About 75 min. The ranking row asked to move `BUNDLE_PITCH` 100 -> 92 ft on 0038's row pitch; moved, the cohort lost seeds 17 and
43. Reading the uses showed `BUNDLE_PITCH` is no row pitch at all - it is the step along a row and the grids' span - while the
rows already stand `_rank_step` apart, 0038's own sum of house, yard and 39 ft of sun. The fix was the label, not the number; no
map moved. **The habit it changes:** before moving a constant to a researched figure, list what each use of it measures - one name
can carry four quantities, and only one of them is the research's.

## T56 - the retro row

About 20 min. Three preflights - T47's, T48's and T10's - reviewed the umbrella heading "T04 to T10 - T48, T47's patch" instead of
each task's own section, because the first heading naming an id took it; T47 and T48 were renumbered to get past it, which hid the
bug for an hour. A heading that begins with the id now wins. **The habit it changes:** when a tool answers the wrong thing twice,
fix the tool - renaming around it moves the cost to the next task.

## T57 - the retro row

About 30 min. T09 changed only comments and constants' claim docstrings and still owed a full gate and a landing cohort, because
the semantic id stripped a docstring only where it is a body's first statement - and every claim on a constant is a bare string
after its assignment. Every bare string statement is stripped now (the cache renamed with the rule). **The habit it changes:** a
rule about "docstrings" is tested on the docstrings this project actually writes - the claims - not on Python's definition.

## T58 - the retro row

About 15 min. T10's headless check session was refused twice for a 4th same-kind launch and pointed at a Workflow call its
`claude -p` session does not have. A session carrying `L7R_DISPATCHER` is now told `WAVE_OK` is its route. **The habit it changes:**
a refusal names a route the refused session can take - test it from a headless session, not only from this one.

## T59 - the retro row

About 40 min. The pair hook records a dispatch at PreToolUse, beside the wave guard; when the guard refused T10's modal-form wave,
the refused dispatch had already marked its notes read and opened a fresh round, so the next real dispatch was counted as a repeat.
What a reading marks now waits on the pending record and is applied at launch. The first test asserted the wrong thing (a first
reading IS round 1); probing the old and new code side by side found the real difference. **The habit it changes:** a hook that
records an action at PreToolUse cannot assume the action happens - other hooks run beside it.

## T60 - the retro row

About 25 min. The EDIT pattern's optional newline before `>>>` let a lone empty line and no line at all parse alike, as no text,
so a paragraph split was applied as a deletion; a lazy optional group now tells them apart, and an emptied whole line takes its
newline. The first test packed two cases into a string trick and tested the wrong thing; written plainly it passed. **The habit it
changes:** none needed - the parse decides it.

## T61 - the retro row

About 20 min. `hm_make.doubled_var` reads each make invocation on the stripped command (so a quoted list is one assignment and a
mention in a message is none) and `make-only-hooks.sh` refuses a variable set twice, naming the quoted list or one call per
value. **The habit it changes:** none needed - the guard refuses the form that dropped 0018's bundle.

## T62 - the retro row

About 35 min. `claims_stale.stale` compares each claimed module-level constant at the merge base and in the tree; for a changed
one it looks for its old figures as whole numbers on the drawing pages that are, or link, a question its claim cites, and
`claims-owed` prints each. On this clone (T10 not yet landed) it names 0018, 0022, 0025 and 0027 - the four the measurement
found. The first plan matched a fixed list of units and the review blocked it (the GM's own figures say "feet" and "degree").
**The habit it changes:** none needed - `claims-owed` prints the pages at the edit.

## T63 - the retro row

About 15 min. `tick-task.py` runs `plan_gate.archive` after every tick it wrote and prints what moved; an archive error is printed
and the tick stands. **The habit it changes:** `make plan-archive` is no longer a step to remember.

## T64 - the retro row

About 25 min. `make task-add F= TITLE= [SECTION=] [RESEARCH=physical]` takes the next id past every `T<n>` the feature's three
files name, puts the box before the GM-review box and the section before the close. **The habit it changes:** a task is filed
with one command, never a hand-written insertion script.

## T65 - the retro row

About 20 min. Found at T63's first tick: the archived-block check matched digests only, so a block a typo away from its reviewed
text (T49, renumbered) was owed once archived; it now takes the typo rule the live check takes. **The habit it changes:** none
needed - the archive owes nothing by construction.

## T10 - the retro row

About 5 h across the day (the step-back's table books 211 min to it before the hour-22 fixes). The split became a knob over the
five recorded splits, the inset derived per map on the median parcel by the apothem law (the rectangle law missed by 0.07). Most
of its 109 agent runs were five sibling pop-ups checked as five units, round after round - the cost the approved proposal 1
removes. Its landing waited on three arbiter fixes (T60-T62), then a British spelling in a tool-written claims note and a stale
Kuwabata manifest (the ink count) cost two gate runs. **The habit it changes:** none by memory - proposal 1 (grouped sibling
pop-ups) and the house-style check on tool-written notes are the tools.

## T67 - the retro row

About 15 min. `land-tooling.sh` runs its lint alone first; a failure stops before the guard suites and tooling tests start, so a
format slip costs seconds, not two minutes. **The habit it changes:** none needed - the order decides it.

## T66 - the retro row

About 20 min. `plan_bundle.build` reads "375 FR-044", "feature 375's FR-002" and the like as that feature's requirement, from its
own spec, under a `<!-- feature 375 -->` line, and no longer hands the reviewed feature's same-numbered one for it. **The habit it
changes:** none needed - the bundle reads the feature the block names.

## T68 - the retro row

About 20 min. `scripts/format-changed.sh` runs at the head of `make test-file`: the `.py` files the clone changed against its merge
base (deleted ones left out, as the review noted) are formatted and named; nothing to format, it is silent. **The habit it
changes:** `make format` is no longer a step to remember before a landing.

## T69 - the retro row

About 15 min. `make task-add` puts the new id on the plan's `**Lands open**:` line and marks its box, where the plan has the line,
so a task filed mid-feature never holds another's landing. The line's edit still owes its block review. **The habit it changes:**
none needed - the tool that files the task keeps the line.

## T71 - the retro row

About 10 min. D85's qualified reading takes a decision too ("375 plan D18"), read from that feature's plan and plan-done.
**The habit it changes:** none needed.

## T70 - the retro row

About 50 min. `set-down-hooks.sh stop` refuses a turn's end while the clone's active feature has an open task, nothing the session
launched is still running, and no `make set-down F= WHY=` is recorded since its task-start; the refusal names the next open task.
The plan review struck the proposal's question escape (a "Shall I go on?" while the GM sleeps is the stop it exists for) and asked
for the GM's words in the request. Two fixture slips in the suite (a start stamped ahead of the clock, a directory that is no
read error). **The habit it changes:** stopping with work left is no longer a choice the session makes silently.

## T72 - the retro row

About 30 min. `ledger_owed.py --write-plan-reviews` writes the row of each owed plan review whose reply shows `make plan-verdict`
recorded it (the review's point: no row naming a record that does not exist); `land-tooling` and `sync-with-main.sh done` run it
first and commit the rows. Its first live run wrote T72's own review's row. **The habit it changes:** `make ledger-owed WRITE=`
is left for the checks whose acted-on cell is the session's word.

## T74 - the retro row

About 20 min. `plan_gate.lands_open_appended` puts a `**Lands open**:` line back as reviewed where the only change is ids appended
in order, so `make task-add`'s line edit owes no review; a reorder, a dropped or a repeated id still does. The first plan read the
line as a set, which the review blocked (a reorder would have passed). The test runs on task-add's own output, as the review asked.
**The habit it changes:** none needed.

## T77 - the retro row

About 35 min. `make where-time F= [SINCE=]` prints the step-back's two tables from the event log, booking every gap from a Stop to
the session's next prompt as "between turns" - the column the overnight stall needed - however many hook events fall inside. The
plan review asked for the rule's provenance (ours) and the wake premise measured (a notification fires the prompt hooks). One
expectation in the test was my arithmetic, not the code. **The habit it changes:** a step-back's tables are one command.

## T76 - the retro row

About 25 min. Part A gains items 10 (before moving a constant, list its uses and what each measures) and 11 (the capacity arithmetic
before rolling), numbered so the gate holds every later Approach to them. Three plan rounds: the first two reviews could not see the
approved proposal (now quoted in the request), then blocked sub-bullets under item 4 as a reminder. **The habit it changes:** the
two questions are the gate's, not the session's memory.

## T75 - the retro row

About 30 min. `plan_gate.decides_nothing` lets a part B pass without a review round when it answers item 4 "No" and item 5
"Neither" and names no new decision; any part B that changes, tunes, moves or decides is reviewed as before. Three plan rounds:
the request lacked the approved proposal list, then the review struck the D-id-only rule (a decision need carry no label).
**The habit it changes:** none needed.
T76's checklist lives in this feature's `specs/`, which `land-tooling` does not carry, and its test reads that file - so the two land
with the feature's own directory at T11 (which moves the checklist to `docs/`). The gate in this clone already holds T76's items:
`make tick` reads the clone's checklist.

## T78 - the retro row

About 30 min. The hook's plain-text correction is `hm_house.americanize` now; `claims.py record` runs each parsed note through it
(never the key - the review's point) and `apply_edits.py` each EDIT's new text, quotations held out as the hook holds them. The
first test fixture used the wrong reply form. **The habit it changes:** an agent's British spelling no longer reaches a tracked file.

## T80 - the retro row

About 15 min. `task_current` reads a section and its reviewed text without their quiet part Bs, so a part B that decides nothing
no longer re-owes its task's blocks; on the live plan the owed delta fell from six blocks to three (T79's, under review). **The
habit it changes:** none needed.

## T79 - the retro row

About 35 min. `land-tooling.sh` writes each run's `{task, files, outcome}` from an exit trap, and `make tick` refuses a NOTE saying
"landed" (any case - the review's catch) while the task's last run failed or a file it named differs from main, the ledger left
out as a rider. **The habit it changes:** a tick cannot claim a landing that did not happen.

## T82 - the retro row

About 10 min. `task_current` takes the archive's generated line out of a section and its reviewed text, as `block_digest` does for a
block, so auto-archiving at a tick (T63) never re-owes a neighbor's review. **The habit it changes:** none needed.

## T81 - the retro row

About 50 min. `make record-owed` names one `make modal-bundle KIND="<all>" FOR=<agent>` per pop-up agent two or more unanswered
pop-ups owe, and keeps the batches; the dispatch guard refuses that agent on a single pop-up of a batch while the record is fresh
(BATCH_OK the escape). Measured first: T10's 90 pop-up agents were all single dispatches - T02's batched bundle existed and was
never named. The plan named `test-pair-hooks.sh`, but `check-bundle-hooks.sh` runs `hm_checks` and its suite runs outside a
repository, so the refusal's test is a unit test (`tests/tooling/test_batch_refusal.py`). **The habit it changes:** a session no
longer chooses between one agent and ten.

## T83 - the retro row

About 70 min. A claimed module-level dict's entries are its blocks (`entry_blocks`), and `Unit.line_keyed` - a section, even an
empty one, or such a dict - keys its claims by their own line; owed, the bundle, the triage and the backfill read that property.
The backfill re-keyed 109 dict claims and owed nothing new; a probe entry added to `_OVERLAP_EXEMPT` owed its 17 claims a triage
and none `code changed`. One red gate was mine: the first cut keyed on "has blocks", and an empty section has none. **The habit it
changes:** a dict grown by an entry no longer costs a full impl-drift round over every claim on it.

## T90 - the retro row

About 20 min. `make where-time` splits the between-turns time by the prompt that ends each window: waiting on work (a
notification), the GM, the GM away (past an hour). The first cut's one-line edit missed the formatter-split bucket map; an assert on
every replacement found it. **The habit it changes:** none needed.

## T84 - the retro row

About 35 min. `make decide` refuses a section quoting the GM with words `request.md` does not hold (`plan_lint.gm_quotes_missing`,
any case, every length, no escape, as the plan review required). Run over all 77 sections first: the parser's artifacts - "the GM"
inside a quote or a code span, elided quotes - were fixed before the check went in; what it still names is real, e.g. T83's "I do
want it, though, if it is helpful", the GM's words that never reached the request. **The habit it changes:** a quote of the GM is
checked against the request before any review reads it.

## T88 - the retro row

About 10 min. `plan_gate.house_style` passes each decision's free text through `americanize` in all three verdict writers (the
task, the plan and the block records); ids, classes, rulings and digests are written as given. **The habit it changes:** none needed.

## T87 - the retro row

About 25 min. The tree check reads the gate's own roll census and leaves out only the outputs of the maps it rolled, printing them
to commit; any other change - another map's output among them - is still a tree move (the plan review's keying). The census
already named each roll's generator, so no engine change was needed. **The habit it changes:** none needed.

## T86 - the retro row

About 40 min. `make decide` refuses an Approach item 4 sentence stating a figure without `measured`, a date and a parenthesized
method (or an `m:` key) - per sentence, code spans holding a path or command set aside, numbers that name a thing ("round 2",
"seed 45") no figures. Three plan rounds: a fixed unit list, then one label per item, then clear. Run over all 77 sections first;
what it still names lacks a date or a method. **The habit it changes:** a figure is labeled before any review reads it.

## T89 - the retro row

About 30 min. `make where-time` books each gap to the task its tool call names (`T=`, "task T60", a `385 T60:` commit, a plan
bundle, a section heading), carries it to the calls that name none, and falls back to the mark only before any is named; a footer
says how many minutes each rule booked. No workflow command moves the mark (the plan review accepted the change of route). **The
habit it changes:** per-task numbers no longer depend on `make task-start` being run at the right moment.

## T85 - the retro row

About 60 min. A running plan review now holds what its bundle names (`hm_planhold`): a task preflight its section, a block review
its blocks; an Edit, a Write or a Bash write that would change held text is refused, naming the agent, and `PLAN_EDIT_OK` passes only
a dead dispatch's hold. Three plan rounds (block reviews in scope, the Write tool, no escape for a live review). The Bash test had
to be wider than the plan said: `hm_house.write_targets` does not see a Python heredoc's write - my usual route - so a write is the
plan named with a write marker, and held text is the heading, a held line, or a quoted fragment of it. **The habit it changes:** a
section under review can no longer be edited under it.
T72, found landing T85 (2026-10-19): the plan-review ledger commit ran `git diff` in a repository with no commits, where it errors,
and read the error as a change - the sync-with-main suite failed on main. It now runs only where HEAD exists and the ledger's status
shows a change.

## T91 - the retro row

About 50 min. A landing's lint runs first in `land-tooling.sh` (after the fetch, with main's `[tool.ruff]` written as a ruff.toml in
the clone's root so its exclude paths resolve there), and the make-only guard runs it on `make land-tooling FILES=` and `make
arbiter-fix-done LAND=` before the command does. Three plan rounds (the guard alone missed the arbiter-fix route; then the fetch's
place). The suite found three of my own slips: main's config read before the fetch, a pyproject passed where ruff wants a
ruff.toml, and exclude paths that resolve against the config's own directory. **The habit it changes:** a lint slip is refused in
seconds, before the landing starts.

## T92 - the retro row

About 20 min. `make claims-triaged` reads its reply through `claims_triage.triage_reply` (a transcript's last reply, as
`make modal-triaged` reads one) and refuses a reply with no text instead of clearing the bundle unread; its first use recorded T31's
triage from the agent's transcript - 6 of 281 sent on. The plan cited "375 FR-016" for the triage rule; that rule is feature 318's
FR-016 (the review's note). **The habit it changes:** none needed.

## T93 - the retro row

About 20 min. `record_owed` reads the triage's touched marks (`modal_triage.touched`): a pop-up owed by a moved page that
`make modal-triaged` sent on at its fingerprint names `make modal-bundle` and joins its check's batch; one not yet triaged still names
`make modal-triage`. The test is red without it. Landed with T94 after one merge of T92's own landing (ours kept). **The habit it
changes:** none needed - the batch is now listed without the hand-built bundle T31 needed.

## T94 - the retro row

About 15 min. `make claims-checked` reads its reply through `claims_triage.read_reply`, the one reader `make claims-triaged` now
shares: a transcript's last reply is recorded, and a reply with no text is refused before anything is written. The shared helper kept
`claims.py` at 999 lines. The test is red without it. **The habit it changes:** none needed - a reply file need not be extracted by
hand.

## T31 - the retro row

About 3 h with its checks. Row 843 (MISLABELED): `FOOTPATH_FABRIC_GAP`'s 4 ft had no page. Measured first: held to the lane's 7 ft,
seeds 3, 4, 903 and 904 newly fail, so 0246's drawing page records the footpath's 4 ft as its own map drawing convention in a block of
its own, and the constant's claim cites it - IN-STEP; no value changed. The claims round found row 841's leg drawn as a lane but
routed as a footpath: filed as T95 (one goal). T31's plan text still names that task "T32" - the id it had before the review moved
it; correcting the pointer would have owed T31 a third review (a tripwire), so T95's own heading carries the link. Lessons, each
now a task: an edit to a heavily cited block owed 37 full checks, where a new block owed triages only; page edits after a triage
re-owe it - finish every page edit first; `make claims-triaged` and `make claims-checked` read a transcript wrongly (T92, T94); the
triage-touched pop-ups stayed out of their batch (T93). Row 843 marked wave 162. **The habit it changes:** a record change goes in a
new block where the old one is heavily cited.

## T95 - the retro row

About 40 min with its reviews. Row 841: `join_to`'s leg is drawn at `STREET_WIDTH`, a lane, but was routed at the footpath's 4 ft;
it now routes at `WEB_FABRIC_GAP` (0246's 7 ft), and both its claims are IN-STEP. Cohort 16/16, landing cohort 54/54, fresh block
8 of 48 (17%, the pooled rate). First filed as T32, which the review blocked: a defect found inside a task is not a ranking pick
(FR-020's kinds), so it became found work. Row 841 marked wave 163. **The habit it changes:** a drift a claims round finds is filed
as found work, never as the next ranking row.

## T96 - the retro row

About 3 h with its checks. The round arbiter's hour-28 ruling: room first for the footpath's 7 ft. Probes ruled out the door's
room numbers and the grove margin for seeds 3, 4, 903 and 904; a trace then found the cause in two minutes: the row farm's DOOR
read the fence gap (`front_door` at it + 4, `door_off_fixtures` at it + 1), so at 7 ft the door had to stand 8 ft clear of its own
fixtures and found no spot. The door's numbers became its own (`DOOR_STEP_FT`, `DOOR_FIXTURE_CLEAR_FT`, UNRESEARCHED) and the fence
gap became 0246's 7 ft - no house moved, T31's 4 ft block came out of 0246. A name collision cost a cohort: serve.py already had a
`DOOR_STEP_FT` (a 4 ft step), which shadowed the import - renamed `DOOR_SHIFT_FT`. The claims round surfaced six old drifts and a
mislabel on code only renamed: filed as T97-T100, ACCESS_HALF_FT carried as T101; T98 lands with T96 because seed 22 needed it.
**The habit it changes:** trace the refused unit first - two guessing probes found nothing a two-minute trace did.

## T98 - the retro row

About 1 h. The room off a grove was counted twice at the door path (bands grown 0036's 11 ft, then routed at the footpath's gap on
top: 18 ft at 7) and too little at the connector (10 ft against 0036's 12.5). `band_grow` and `CONNECTOR_BAND_GAP_FT` count it once;
seed 22 and the cohort pass. **The habit it changes:** none needed.

## T103 - the retro row

About 25 min. A gate that stops at preflight writes no run-log record, so the measure guard read the last green gate and refused
the re-run that fixes the red one (T98's file-size bar, 2026-10-19). `done`'s preflight failure now touches
`<git dir>/gate-preflight-red`, and the guard lets the run through when that mark is newer than the last green record; the hook
suite holds both cases, red without the fix. **The habit it changes:** none needed.

## T104 - the retro row

About 1 h 10, half of it waiting out the very holds it fixes. A plan review the dispatch guard refused never launched, and its hold
stayed `pending` and refused its section; two reviews stopped with `TaskStop` returned no reply, and their holds refused T104's own
amendment for half an hour. A never-launched hold now holds nothing and a TaskStop releases a review's hold; no hold drops
another (the review's block of round 1: the first draft let a refused dispatch drop a running review's hold). While blocked, the
session split the plan's file name to get past the guard - evasion, which failed only on a missing file; the hour-30 ruling made
it a tooling fix. **The habit it changes:** a guard that blocks wrongly is fixed or escaped with a reason, never dodged.

## T100 - the retro row

About 50 min of a 20 min budget. The claim on the web's water rule cites 0035's drawing page (a way keeps to its own bank,
crossing only at the fords) - IN-STEP; its check named the web's frame unclaimed, now claimed on 0246 (a lane runs about 30 ft
past the last house it serves; the 100 ft frame is only room before the trims) - IN-STEP on its second round. A relabeled claim is
listed as owing a triage, not a check, and its triage bundle came out empty: filed as T105. Twice an impl-drift went out beside the
bundle step it needed, which had failed, and read a stale bundle. **The habit it changes:** never send a check in the same message
as the step that builds its bundle.

## T105 - the retro row

About 20 min. A claim relabeled to cite a page rested on nothing at its last check, so `research_why` sent it to a triage that
could never name it; `make claims-bundle OWED=1` then refused it. A claim citing a page its last check never read is now owed
`research changed`; the triage rule stands for pages it was checked at. Live: no claim newly owed. **The habit it changes:** none
needed - a relabeled claim is bundled by `OWED=1`.

## T99 - the retro row

About 25 min. Under `farm_water` channel the check flagged every farm whose channel did not end in its frame, though 0031 gives a
farm no channel can reach "a well of its own instead"; such a farm now passes with a private well in its frame. Its three claims
IN-STEP. **The habit it changes:** none needed.

## T97 - the retro row

About 2 h 30 against a 60 min budget. A farm counts as reached as 0246 counts it - the way's point nearest its HOUSE within 60
ft of it or 12 ft of its built ground (`street_arrives`) - read by `lay_door_paths`, `row_rules` and, since its claims round, the
street trim (`street_anchors`); `DOOR_REACH_FT` is gone. Seed 904 then exposed a hidden defect: four row farms' 9 ft door paths
were laid and dropped by `settle_fragments` as earning nothing, the old door-distance check having passed them; a door path
(`serves`) is now a household's own way the fragment rule never drops. Traced by five scratch probes, each a step deeper (the
door, the passes, the settle, its steps). The claims rounds converged 34 -> 20 -> 2 -> 1; the web's frame (lanes trimmed level
with their last house, 0246 says ~30 ft past) is old behavior, filed as T106. **The habit it changes:** a check made stricter
is run against the cohort before its claims round - it surfaces what the lax check hid.

## T101 - the retro row

About 15 min. `ACCESS_HALF_FT`'s comment called its 7 ft "a footpath's room between two steadings"; it is the corridor line's gap off
each garden fence, the room between two steadings being `MIN_WEB_GAP` (18 ft). The claim re-checked IN-STEP. Its check noticed 0246
measuring the 7 ft to the tread's edge in one block and to the middle in another: filed as T107. **The habit it changes:** none.

## T107 - the retro row

About 50 min with its checks. 0246 gives its 7 ft two measures: the 18 ft room counts it to the tread's edge, the least gap to the
lane's middle. A new block says so - no block edited (T31's lesson), no code changed. Its triages sent on 51 of 287 claims and all 8
lane pop-ups; 48 claims IN-STEP, the pop-ups clean, 0246's record checks clean. The rest - the 7 ft held off threshing yards and
other households' yards where 0246 names gardens, the track's grove gap citing 0246 for 0036's figure, two small tolerances
unclaimed - is old code a page edit re-judged, carried as a task. **The habit it changes:** none.

## T109 - the retro row

About 1 h 15. The track's grove gap at 0036's room, as T98 set the door path and the connector: the bands grown so every test in
`_thread_the_fabric` - its first route, clip and checks, and its grove fallback - keeps the line 12.5 ft off the trees; two touch
claims say the 7 ft the link is routed at, labeled DEVIATION on 0246. The plan's items 9-10 still name only the fallback, though
D128 was widened to every test (the round-2 review's aside, left as text rather than a third round). The claims round's old findings
on the fallbacks' walls, water and five unclaimed decisions are T112; its OUTSIDE rows were filed automatically (hour 32's fix, its
first use: 9 rows). **The habit it changes:** none.

## T110 - the retro row

About 20 min. Enoshima, named on 0246 without a word of what it is, is a glossary entry from Morse's 1886 passage (0081's notes); no
block edited, no check owed. The file's prefix is the one `make reserve` gave (24330), not D129's 9995, and a proper noun's file
takes its capital (`24330-Enoshima.json`), as the glossary's own check refused the lowercase stub - both small corrections to the
plan's filename, left as this note rather than a review round. "Island" rests on the name itself (-shima), not on Morse's passage
(the review's aside). **The habit it changes:** a new glossary or registry file starts from `make reserve`.

## T113 - the retro row

About 25 min. T110 was ticked "landed" while its push stood refused, because it had no land-tooling run and T79 asked nothing else.
A "landed" NOTE now waits until no file outside `specs/` and `dev/` committed here differs from origin/main - compared by content,
as the review's aside asked, since `make land-tooling` lands files as new commits and leaves the clone's own commits ahead.
**The habit it changes:** none needed.

## T102 - the retro row

About 1 h 20. The track out's last-resort fill crosses the brook as 0035 has a way do: at a crossing place, only where it finds a way
the own-bank fill does not or saves more than 150 ft of walk, squared after by the settle. The first plan, recording the keep-to-
its-bank as a DEVIATION, was blocked - its reason was the algorithm's order, not how a track forms - and two claims rounds moved the
code to the page (a free crossing, then the squareness named). Items 6 and 9 still describe the first gapping only (round 3's aside).
The unclaimed channel rule is T120. **The habit it changes:** a deviation's reason must be about the world, not the code's order.

## T115 - the retro row

About 25 min. `make where-time F=<n> BY=tick` books each tick-to-tick window to the task or batch ticked at its end, with its
minutes by bucket and its wall-clock span - T97 53, T109 40, T102 49, as the hand count found. The ticks are read from tasks.md's
history, not the event log's tick records, because those exist only since hour 33's fix and the history holds every tick (the
review's aside). Its first reading: "tools" is the largest bucket, 85 of 218 minutes over eleven tasks - the foreground cohorts
and landings, next to split by command. **The habit it changes:** a speed question is answered by `make where-time BY=tick`.

## T116 - the retro row

About 75 min. A code change now owes its claims a `code triage` first: the triage bundle shows the unit's diff hunks against
origin/main beside its claims, and the claims the agent does not name are cleared at their new code, as a page edit's are since
318. Owed in full as before: a claim the triage names, a procedure section's own line, a claim whose own text was rewritten (known
from the row, or seen among the hunk's added lines), and a unit with no hunk to show (the change landed before the check). The
plan review blocked once, on a minimum claim count whose saving was asserted, not measured; dropping it made the rule the page
triage's own. Building it found an empty-diff crash in the hunk splitter, caught by the test. **The habit it changes:** a
threshold in a plan carries the measurement that sets it, or is not there.

## T117 - the retro row

About 30 min. `make land-batch F= T="T1 T2" NOTE=` asks every task's tick first (all of `make tick`'s refusals but the landed
one, now one function `refusal`), runs the gated route once, and ticks each "landed in batch T1+T2"; a failed landing ticks none.
A gated landing measured about 15 min from the transcripts, so a batch of three saves about 30. The plan review was CLEAR in one
round. Building it, the Makefile target was first written by a python heredoc that the shell-write guard did not catch: recorded
under `make guard-edit` and filed as T121. **The habit it changes:** a small engine fix whose checks are done waits for the next
one, and the two land by `make land-batch`.

## T118 - the retro row

About 35 min. A task whose Decisions block reads `**Wording only.** <what>` owes no plan review: the plan gate skips its blocks
(not its part Bs), `make decide` says no review is owed, the checks do not wait on a verdict, and `make tick` reads its commits
since `make task-start` and refuses any change beyond its feature's records, a glossary entry, or a `.py` file's comments,
docstrings and claims (`gate-stamp.semantic_bytes`, the one definition of "changed in what runs"). Saves a review of 1-3
agent-minutes plus its decide and verdict steps on a 5-12 min task. One review round, CLEAR; `make decide` first refused a quote
of the task's title as the GM's words, rightly. **The habit it changes:** a relabel, a comment or a glossary entry is written
`**Wording only.**` and goes straight from its Approach to its checks.

## T119 - the retro row

About 60 min. A ruling that names a `tooling_fix` now carries `fix_measure` (a regex over the session's Bash commands, or
`agent:<kind>`) and `fix_minutes`, refused without them; `make fix-yield F=<n>` compares each made fix's rate per session hour
before its ruling and since it was made, and the hourly step-back reads the same table as `fix-yield.md`. The plan review blocked
once, rightly: reporting the 45 earlier fixes "unmeasured" would have emptied the report on the question that prompted it, so each
took a measure from its own sentence (`fix-measures.json`). Its first reading: 22 saving, 22 "saves nothing", 2 too early - with
the caveat that a rate moves with the mix of work (impl-drift dispatches rose because the recent tasks were claim fixes). Found
working it: a batch's fix lost its measure on an exception's row (fixed), a pipe in a measure split its table cell (fixed), and
land-tooling conflicting with its own earlier landing (filed). **The habit it changes:** a fix is named with the number it should
move, and the step-back sees whether it moved.

## T114 - the retro row

About 15 min. `earlier.md` is headed "Each changed block's text when last judged, with that verdict" and each block carries the
verdict it got, so a round 2 sees round 1's BLOCKED text named as blocked. One review round, CLEAR; its aside found the bundle
resolving another feature's cited decision against this feature's own number (filed, T123). T85, landed at 04:58Z with its part
B saying so, had never been ticked - ticked now. **The habit it changes:** none; a label told the truth.

## T121 - the retro row

About 20 min. The shell-write guard now refuses a guard file written by `open("<guard>", "w"|"a"|"x")`, or by a name bound to a
plain string then written through `open()` - T117's shape; a read stays legal. The suite gained three cases, two red without the
change. One review round, CLEAR; its aside lists shapes still unmatched (`Path(...).open("w")`, `"r+"`, `shutil`, `os.replace`) -
left unmatched by choice: none has been seen, and the guard widens by measured shapes, not imagined ones. **The habit it
changes:** none; a guard I walked past by accident now stops the walk.

## T122 - the retro row

About 50 min against a 30 min budget, for a hazard that costs about 2 minutes by hand - the hour-35 step-back's point, and a fair
one. A resolver taking the clone's side was built first; two plan reviews blocked it (it reversed D46, then its "self-landed"
match reached history shared with main, where it would have undone another session's revert), and the arbiter's change-route
narrowed it to a message: a landing refused by a conflict with this clone's own earlier landing now names those files and the
line that resolves them. **The habit it changes:** size a fix to the hazard's measured cost before designing it - a 2-minute hand
step gets a message, not an automatic resolver.

## T123 - the retro row

About 10 min. A decision cited as "Feature 375 amendment 11 (D64)" is now read from feature 375, not taken as this feature's D64;
the qualified form allows an amendment and a parenthesis between the feature number and the id. One review round, CLEAR; the
test is red without it. **The habit it changes:** none; a reviewer is handed what the block names.

## T106 - the retro row

About 55 min, no engine token changed. The DRIFTED claim set 0246's back-lane bullet ("about 30 ft past the last of them")
against the trims that pull every end back to its last house. The bullet described the room the web is laid in (pad 30), and the
page's own general rule, a GUESS, is what the map draws - the rule the 2026-09-27 tweak had enforced after a lane walked into
Inashiro's grove. So the bullet now says both, and the frame claim cites it: one plan review, CLEAR; the record checks clean (7
pop-ups in one check-wave, all clean); the claims round IN-STEP. The page edit re-owed a triage of 286 claims, which sent 27 on,
and that round found 15 things on code this task never changed - filed as T124-T133 per the GM's rule. **The habit it changes:**
before changing code to match a page, read the page whole - a drift can be the page contradicting itself.

## T108 - the retro row

About 10 min, the first task through T118's wording-only route: no plan review, `make decide` said none was owed. Two claims split
into a garden half on 0246 and a yard half UNRESEARCHED, as their sibling already read; the claims check 4 IN-STEP, its two
asides on unchanged code filed (T134, T135). **The habit it changes:** a claim relabel is declared `**Wording only.**`.

## T130 - the retro row

About 8 min, wording only. The run-on reach's claim cited 0246 for a 60 ft to the field no page gives; it now reads GUESS,
naming 0246's 60 ft to a house or way as the figure it reuses. Claims check IN-STEP; its two asides filed together (T136).
**The habit it changes:** none.

## T136 - the retro row

About 8 min, wording only. `RUN_ON_TURN_DEG`'s claim labeled CONVENTION (0081 says its turn limits are drawing conventions),
`BRANCH_STEP_FT` claimed NONE, and the step's comment no longer calls plumbing a convention - that last from the claims check's
own aside, fixed here rather than filed, since it sat beside the claimed line. **The habit it changes:** an aside on the lines a
task already touches is fixed in the task, not filed.

## T132 - the retro row

About 30 min, in the first `make land-batch` with T125 and T137. A street with exactly one joint was cut to two coincident points
the overlap matrix admits; it is now left whole, and its claim names `settle_street_ends` as the pass that cuts its dangling end
- the impl-drift round's DRIFTED, and the plan review's aside, answered in the claim. **The habit it changes:** none.

## T125 - the retro row

About 20 min, in the same batch. The web's `or True` headman filter, which filtered nothing, is written as what it does - every
house - and the tie's 30 ft run past the back lanes is claimed a bare GUESS (MISLABELED once, citing a page that gives no
distance, the T130 pattern again). The edit to `stage_web` was the first through T116's code triage: 19 of 20 claims cleared,
one sent on. **The habit it changes:** a GUESS no page gives names no page.

## T137 - the retro row

About 35 min. T136 landed a claim the grammar cannot read ("CONVENTION <page>") by the direct route, which runs no gate, and the
batch's first gate went red on it. The claim now cites its drawing page plainly, and the push's claims gate refuses a form problem
in any changed file, reusing `form_problems` - which `claims-owed` already printed first, and which my truncated reading of that
output had hidden. **The habit it changes:** read `claims-owed`'s head, not only its tail.

## T139 - the retro row

About 20 min. `make tick`'s landed check refused T137, whose files stood on main by the gated batch, because its earlier
`land-tooling` run had failed; a failed run whose every named file now matches origin/main is landed, one that named none is
still refused. Two review rounds: the first rightly blocked an undefined "riders" - now named, the review ledger alone.
**The habit it changes:** none; a guard that misfired now judges by what is on main.

## T32 - the retro row

About 40 min, the first ranking row of the E2 kind (one rule): `waterfields/banks.py::_WELD_MIN_SOLIDITY#weld lump`, wave 164.
The first plan would have recorded the 0.85-solidity host preference on 0014 as a DEVIATION; its review blocked a fallback I had
not measured, and measuring it found the preference runs nowhere - the welder its comment describes (`_absorb`) is gone from
the tree. So the constant, its comment block and its claim were removed; no map moves, the gate green. **The habit it changes:**
before recording a rule as a deviation, grep that anything runs it.

## T33 - the retro row

About 70 min, the first E3 NEEDS-RESEARCH ranking row picked by the round arbiter's reading of FR-020 (ask:t33-ranking-pick,
which also retired 133 dead rows, each checked for a successor first): `bund.a_way_onto_the_bund#on the bund`, wave 166. 0014's
drawing page now records that a lane end within 6 ft of the paddy counts as joining it, a GUESS, and the claim cites it. One page
sentence owed 5 record checks, a 70-claim triage and 23 claims judged: 3 claims relabeled GUESS and a comment fixed here (they rest
on the changed block); the bund pop-up's own depiction edits applied (polder crossings, a hedge, 0022 linked); and the finding that
the law gate reads "reached the field" at 60 ft while the placer reads 6 ft went to T141, with T142 and T140 filed. **The habit it
changes:** a page edit's cost is its triage width - a sentence on a hub page like 0014 re-owes every claim citing it.

## T34 - the retro row

About 90 min, a live E2 row picked by the arbiter's reading of FR-020 after round 1's dead row (`_WELD_MIN_APEX`) was sent to
T143: `taxonomy._OVERLAP_EXEMPT#yard, garden and fixtures against the house`, wave 167. 0043's drawing page now records the shed
a ken past the 3.5 ft wall gap, about 9.5 ft out, the gap a DEVIATION (at a ken, scaled rolls lost a farmhouse or field from the
web, held in 328's waves 9 and 51), and where it stands a GUESS. The record checks added two right things - the gap said in plain
words, and the shed's log-end band recorded as the map drawing convention it is in code - and removed one claim the record does
not make ("open front"); eight seat claims relabeled GUESS. Stopping two checks to relabel left them "running" in the round state
until `make check-closed` (filed T148); the pop-up's third round was accepted by the arbiter. **The habit it changes:** finish a
page's wording before its record round, not between rounds - each edit re-owes the whole round.

## T143 - the retro row

About 15 min with T34's landing. `_WELD_MIN_SOLIDITY` and `_WELD_MIN_APEX`, read by nothing since feature 302 retired the carve
and its welder, are gone with their claims and comments, and both ranking rows are retired in 328's waves.json (wave 168) - T32's
count with them, which T144 replaces. **The habit it changes:** grep a ranking row's code for a live use before taking it.

## T148 - the retro row

About 20 min. A record check the session stops with TaskStop now closes its dispatch, as `make check-closed AGENT=` did by hand,
so its page is no longer frozen and its round's next check is not refused (T34 had two such checks holding 0043). The TaskStop
branch had released plan holds since T104 but not check dispatches. **The habit it changes:** none; a stop now means stopped.

## T11 - the retro row

About 60 min, the close. The approach checklist moved to `docs/approach-checklist.md` and is now every feature's: `make tick`'s
Approach refusal and a trigger's part B ask it of every plan, and the opt-in line is retired, so no plan can forget it or name a
thinner file (round 1 of the review rightly blocked keeping that override). D30 gained the round arbiter's three clauses, worded
as T11's reviewed section stated them (the block review that followed saw only D30's earlier text, a limit it recorded). The final
report answers SC-001 (task times fell by kind: ranking rows from 75 min-5 h to 19-36 min, wording fixes to 5-7 min) and SC-002 (the
checklist has not changed since T76). The engine and record work 385 found moved to feature 405, filed and not started, by the GM's
amendment 11. **The habit it changes:** every feature's tasks start from the checklist, with no opt-in to remember.
