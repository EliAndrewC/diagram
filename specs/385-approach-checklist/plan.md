# Implementation Plan: the approach checklist - the front of 384, one task at a time (feature 385)

**Approach checklist**: specs/385-approach-checklist/checklist.md

**Spec**: `spec.md` | **Request**: `request.md` | **Checklist**: `checklist.md` | **Audit**: `audit.md` | **Builds on**: the lane
law (`l7r/diagram/hamletgen/ways/law.py`, `law_water.py`), its settle (`settle.py`, `last_resort.py`), 384's FR-000 and User
Story 0, and the event log behind `make feature-report` (feature 375).

## Summary

The tasks run one at a time, in the GM's order (2026-10-17: *"make the plan, then do the lane law as task one, work that under the
checklist with a retro afterwards, and then let's see how it goes"*). Each task's section below opens with its **Approach** block,
checklist part A answered, and the task is not ticked until its retro row is in `retro.md` and any change the row names is made.
The tooling that enforces this (FR-003 to FR-005) is T02, built after T01 so its first retro can shape it; T01's Approach block
and retro are kept by hand, and T02's per-task split is proven by replaying T01's events.

After T01 the session stops and reports to the GM before T02 (his "let's see how it goes").

## Constitution Check

- I-V: no SOURCE block or hand map is touched; pool hamlets re-roll as the engine changes (VI), measured on the cohort.
- XII: T01's decisions are classed in its rule table (research, the GM's ruling, a convention of ours); each changed rule's why
  is written at the predicate and on the lane drawing pages (0081, 0246).
- XIII: a seed that passes at HEAD and fails after T01 is a regression, measured on the 48-seed cohort against HEAD's run.
- XIV: the refusal that named lanes but not the rules they break (found while measuring T01) is fixed in T01 (D3).
- XVI: built as asked: the angle rules admit a meeting an obstruction forces, side-by-side lanes merge; no other rule is
  loosened.

## T01 - the lane law describes how people walk (384 FR-000, User Story 0)

### T01 Approach (checklist part A)

1. **The goal, in the world.** A reader sees footpaths that are the routes villagers walk round what already stands: a sharp
   meeting or a bend only where a house, a fence, a fixture or water makes it, and never two paths running side by side a
   few feet apart (those become one path). The web settles what the homesteads leave it; a seed is never refused for a path
   shape the ground explains.
2. **The constraints, listed.** The 28 entries of `LAW` (`law.py`) and the per-lane rules `last_resort.lanes_breaking` asks; the
   thresholds they read (`DOUBLE_BACK_DEG` 140, `KINK_DEG` 50, `BEND_RUN_FT` 40, `_HOOK_DEG` 90 / `_HOOK_FT` 12, `NEEDLE_DEG` 20 /
   `NEEDLE_FT` 20, `_DOUBLED_DEG` 15, `CONNECTOR_START_FT` 1.5, `DOORSTEP_FT` 80); the 48-seed cohort (2 refused at HEAD: 17, 21) and
   the pool's five hamlets.
3. **Where each comes from (checked).** The principles are research: 0081's findings - *"A worn path usually takes the shortest or
   easiest way"*, the London study's *"fewest turns or the least change of angle"*, never doubling back. Every NUMBER is ours: 0081's
   drawing page says *"Every turn limit and distance in these bullets is chosen at the scale of a dozen paces, not measured"*, and
   the claims at `NEEDLE_DEG`, `NEEDLE_FT`, `_DOUBLED_DEG`, `DOORSTEP_FT` read CONVENTION or UNRESEARCHED. That two paths side by
   side become one is the GM's ruling (G, 2026-10-17, `request.md`), not in the record; that lanes follow the houses is the GM's
   (2026-10-02) and 0246's. The full table is T01's first output (D1).
4. **What each describes, and whether it holds here.** "Fewest turns" and "no doubling back" describe open ground. Where a house,
   a garden fence, a fixture, a crop or water stands between a lane and the straighter line, the easiest way IS the sharper one,
   so the rule as written (a fixed angle anywhere) does not describe the world there. Two treads under 20 degrees apart over open
   grass describe nothing anyone walks: they would wear into one.
5. **The order of operations.** Nothing moves a homestead or its fixtures. The change is wholly inside the web's law and settle,
   after every house stands (GM 2026-10-02, 2026-10-17).
6. **The exits, weighed.**
   - (a) refine a number: a smaller `NEEDLE_DEG` only moves the line; it does not tell forced from idle. Not chosen alone.
   - (b) a principled exception: **chosen** for the angle rules - a turn or meeting is lawful where the straighter way is
     blocked by mapped ground (D2).
   - (c) a rule that dissolves the case: **chosen** for the needle and the doubled band - an end running nearly along another
     way over open ground is merged onto it, the two one tread (D4).
   - (d) more room: not the lever here; the homesteads stay where they are (5).
   - (e) conform: kept for every rule not about angles or doubling (the network, the reach, the crossings, the fabric).
7. **The search smell.** The settle's repair rounds and the last resort are a repair loop against fixed angle thresholds; the
   exception and the merge make the lawful shape something the settle can write once rather than search for.
8. **The budget.** About six hours of session time to a green gate and a re-rolled cohort (a guess). Twice that triggers part B.
9. **Done, measured.** The table (D1); unit tests on a forced meeting and a side-by-side pair, red on HEAD's law (D2, D4); the
   48-seed cohort at HEAD (`m:w156-redeal-cohort`'s method) and after: no seed newly failing, 17 and 21 passing or refused by a
   rule the table keeps and the refusal naming it (D3); the pool's hamlets re-rolled; seed 10 under the wave 155 patch re-rolled.

### T01 Decisions

**D1 - The rule table first.** `specs/385-approach-checklist/lane-law-table.md`: one row per `LAW` entry and per rule
`lanes_breaking` asks - its predicate, what it describes, its class (R with the question file, G with the ruling, O with its claim's
words), its thresholds, and its verdict: kept / made obstruction-aware / merged / retired. Built from the predicates' `Research:`
claims (they already carry the class) and 0081's and 0246's drawing pages; the rows not about angles or doubling are expected kept.

**The order (checklist B1 applied to this plan).** D3 is the first edit and the measurement follows it: the baseline (D6) is
taken with D3 in place, and is shown to equal HEAD's seed by seed before it is called HEAD's (D6). D2's and D4's exact shape is
then fixed against the cases the named refusals show (seed 21's lanes, and the pool's violations); seed 17's refusal is a reach (the
field reached by no way), not an angle, and is T03's unless D2-D4 mend it. If the named rules on seed 21 are not angle or doubling
rules, the session stops at part B before writing D2 or D4.

**D2 - "Forced" is one predicate, asked by every angle rule - two shapes.** The ground is what the settle itself routes round,
its two obstacle families (`clearance.py`, the clear-stretch scan): `obstacles` - crop, marsh, the wet toe - and `tight` - the
houses, yards, gardens and groves - with the fixtures (`fixture_quads`) and solid boxes (`solid_boxes`) the fabric rules read. A
kind the settle routes round and this ground left out would be a shape the settle made and the law refused, so the two are one
set; `lane-law-table.md` says at its row why any kind is out. The test asked is the settle's own, `Lawful.on_lawful_ground` on the
chord (built from the manifest alone: its fabric and worked ground read only `M`), so the law and the settle cannot differ on it; the ground is indexed once per manifest
(`settlement/_geom/indexes.py`, the overlap-check rule) and asked two ways:
- **a TURN** (a kink, a hairpin, a hook, a folded joint, a connector hairpin): forced when the chord past the turn - from the
  vertex before it to the vertex after, swept at the lane's width - crosses that ground;
- **a MEETING** (a needle): forced when the sliver of ground between the arriving end leg and the tread it meets, back to
  `NEEDLE_FT` along the leg, holds that ground - a fence or a corner standing between two paths that meet at its end.
The filter is applied where a manifest is judged - `law.lanes_that_kink`, `law.hooked_ends`, `law.folded_joint_pairs`,
`law.connector_hairpin_ends`, `law.needle_ends`, and `last_resort.lanes_breaking` - never by widening the pure detectors
(`clearance.kink_spans`, `law.kinks`, `law.hooked`), which `keeper`, `clearance` and their tests call on bare points. A turn or a
meeting with open ground is judged exactly as today. The repair passes with their own hairpin or hook tests (`joints.py` 172, 222,
319, 640; `smooth.py` 232; `track.py` 71; `sweeps.py` 374; `geom.door_unhooked`) are read against the change: each straightens only
where its own clearance allows, so a forced shape stands; any that would still cut one is given the same filter, with a test.
Class: deliberate reading of 0081's research ("the shortest or easiest way") - the drawing page says so.

**D3 - A refusal names its rules.** `last_resort.lanes_breaking` returns `{lane: [rule names]}` (its set is the keys, so every
caller is unchanged), and `refuse_unmended` writes `lane 3 (access): needle_joins, kinks`. Found while measuring T01 (constitution
XIV): seed 21's refusal named lanes and no rule (`.git/cohort48-head.log` in diagram-backlog, the 2026-10-13 run behind
`m:w156-redeal-cohort`).

**D4 - Side by side becomes one, never refused.** Every needle D2 does not call forced is merged: the two treads become one path
from where they come alongside. The settle's needle repair already is that merge for an ordinary lane: `settle.reaimed` lays the
end from the last vertex before it whose leg to its foot on the tread meets cleanly, dropping the stretch that ran beside the
tread (and `tails.along_tail` / `cut_at_tail` do it for a doubled tail). Measured (part B, 16:00, `retro.md`), what is NOT merged
today, and is made so:
- **a household's way** (a tree lane, `ACCESS_ROLE`): its foot - never its door end - is re-aimed by the same `reaimed`, its
  reserved corridor rewritten with it (`tree.set_corridor`, as the knot gather already does for a foot), so it ends on the way it
  ran beside and its household stays reached through that way. A tree lane other than a household's way (the connector, a street,
  the field way, a target's spur) is never cut; where such a lane is one of the two, the OTHER lane is the one re-aimed;
- **a shallow crossing**: a lane crossing another way at under `NEEDLE_DEG` is two paths side by side (seed 10 under the wave 155
  patch: a household's way crossing the field way at about 19 degrees and running on beside it to the field way's start). It is
  cut at the crossing on its foot's side - the run past the crossing beside the way is the same path doubled - and the end left on
  the way is then a needle, merged as above.
A needle or shallow crossing that is not forced is never left as a violation and never reaches `last_resort` or `refuse_unmended`.
Which lane is re-aimed is chosen to keep every reach: if re-aiming the one would strand a house or a join, the other is re-aimed;
if measurement finds a case where no re-aim keeps every reach, it goes to an exception check (constitution XVI) with that case
before anything else is done with it. The GM's ruling (G, 2026-10-17): *"if there are two different footpaths that are nearly
parallel to each other and very close together, then that is the kind of situation in which a single footpath would emerge"*;
384's User Story 0: *"merged into one path, never refused"*.

**D4b - The knot rule reads the ground.** The knot rule (`knots.knots`, the settle's gather, and
`knots.lane_knots`, the cohort's and the pool test's verdict) counts two ends within `_KNOT_FT` as a knot only where the straight
join between them stands on lawful ground (`Lawful.on_lawful_ground`, the D2 ground): two ends with a garden, a yard or a house
between them are two paths either side of a fence, not *"three lanes ... a few feet apart in a knot"* (0081). CORRECTED 16:24: seed
24 is NOT this case - its two ends (a household way's T-foot on lane 6 and the field way's start 24.8 ft along the same lane)
have lawful ground between them; the gather was refused for the fabric beside its own moved leg, and the straight join is clear
(measured in the scratch worktree; `retro.md`). Seed 24 is a staggered junction under the re-deal, so it is T04's (T48). D4b stands
on the GM's principle and its own unit test (two ends a house parts), with no cohort seed yet showing it. The callers hand the manifest in
(`lane_knots(lanes, M)`); with no manifest the rule reads as today. Class: deliberate reading of 0081's knot rule, the drawing page
says so.

**D5 - Nothing else moves.** No threshold changes value, no rule outside the angle and doubling rules and the knot rule (D4b) changes, and no homestead,
fixture or seat moves. A rule the table finds describing no walker's behavior is retired only with its reason at the predicate
and on the drawing page; none is expected.

**D6 - Measured.** With D3 in place and before any other engine edit: the 48-seed cohort (`make cohort N=48`, logged), compared
seed by seed, pass or fail, against `m:w156-redeal-cohort`'s HEAD run - called HEAD's baseline only once that comparison shows D3
changed no verdict - with seed 10 under the wave 155 patch, and the pool's hamlets' lane violations. After: the same three. Two
workers while the containers sit near their memory cap (2026-10-17's memguard notices).

**D7 - The record.** 0081's and 0246's drawing pages say what the maps now draw: a turn the ground forces is drawn as walked, and
two paths side by side are drawn as one. Their record checks run as `make record-owed` names them.

### T01 retro

Written in `retro.md` when T01 closes: where the time went (from the event log, `make feature-report F=385`, split by hand at
the decision points until T02 builds the split), which checklist items fired, which should have, and the change made.

## Landing

Each task lands when it closes, with its retro row, while the tasks after it stay open: the feature is worked one task at a time by
design (FR-006), and each task's change - T01's lane law first - reaches main before the next starts, so the next task's
measurements are taken on it.

**Lands open**: T02, T03, T04, T05, T06, T07, T08, T09, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T46

## T02 - the tooling: the Approach block required, the triggers, the split, and the check costs T01 measured (FR-003 to FR-005, FR-008 to FR-011)

### T02 Approach (checklist part A)

1. **The goal, in the world.** The next task (T03) costs what its change needs, not what the tooling multiplies it into: a
   session answers the checklist when a task starts and when the work resists, the report shows where each task's time went, and
   one small change to a widely cited page no longer re-owes everything that cites it.
2. **The constraints.** Every guard has a test that is red without it (`docs/guards.md`); every refusal names the compliant
   command; tooling lands alone by `make land-tooling`; the five rules FR-003, FR-004, FR-005, FR-008 to FR-011, and the round
   arbiter's tooling fix on hour:385-approach-checklist@4 (the hourly clock stops counting the GM's waits).
3. **Where each comes from.** The requirements are the GM's (G, spec and amendment 1). Every number below is ours (O): which
   checklist items count as answered, the per-line cost table's columns.
4. **Do they describe the world here?** Yes - each is measured on T01's own record (`retro.md`): the cascade from one page, the
   gates voided by writes, the hour that counted the GM's wait.
5. **The order.** Measure first (FR-008: confirm why the triage diffed against an old baseline before changing it), then the
   cheapest fix that removes the measured cost; no item builds a new subsystem where a field on an existing record serves.
6. **The exits.** (a) refine an O number - n/a; (b) an exception - n/a; (c) a rule that dissolves the case - **chosen** for FR-008
   (keep what a check read, so a re-check diffs against it) and FR-009 (a page-wide unit rides one batch); (d) more room - n/a;
   (e) conform - for the guard rules (tests red without them).
7. **The search smell.** None: each item is a record kept or a refusal added.
8. **The budget.** About four hours (a guess: nine items at 20-30 min each with their tests); twice that is part B. Each item lands
   alone by `make land-tooling` as it goes green, in value order - the hourly clock (owed before the tick), the gate-write guard,
   D11, D12, D10, D8, D9 - so a stop part-way leaves landed work, not a half-built batch.
9. **Done, measured.** Each item's test red without it; `make hooks-test` and the tooling tests green; FR-011's table printed for
   T01 from its own record (the baseline T03 is compared with).

### T02 Decisions

**D8 - FR-003, the Approach block required.** A plan that opts in - the line `**Approach checklist**: <path>` (385's plan carries
it; FR-001's close makes it every feature's) - has each task section hold a `### Txx Approach` block answering every numbered
item of that checklist's part A; `make tick` refuses a task whose block is missing or answers fewer items, naming the missing
numbers (`scripts/gates/plan_gate.py`, beside the plan-review check `make tick` already asks).

**D9 - FR-004, a fresh answer after a trigger.** A trigger writes `<git dir>/approach-owed.json` (the task, the trigger, its
time, and which part it owes), and its message names that part of the checklist; `make tick` refuses the task until its plan
section holds the owed block stamped after the trigger. The triggers, each with a floor so it never fires on correct work:
- a round-arbiter ruling on an `hour:` or `red-gate@` trigger - owes `### Txx part B (<UTC>)`;
- a `make cohort` run of any size whose failing seeds include one that does not fail at the baseline - a seed the change newly
  refuses; a seed already failing at HEAD, rolled as diagnosis, is in the baseline and fires nothing - owes part B;
- a re-review of a task's Decisions block after an earlier CLEAR verdict on it - a changed approach, not a first review or a
  figure label - owes the `### Txx Approach` block answered again and stamped after the trigger (FR-003: "a re-decided plan
  section carries the block answered afresh").

**D10 - FR-005 and FR-011, the report per task.** `make task-start` appends its task and time to `<git dir>/task-starts.jsonl`;
`make feature-report` adds a table per task - start to tick, the decision points (plan verdicts and part B stamps), the time to
the last one and after it, each segment between two decision points, re-decides and re-answers - and a table per check kind - dispatches, tokens and wall time, each per
changed line. Its source is the feature's own event log (its dispatches, each timed and feature-scoped), each dispatch costed
from its transcript by the function `make ledger-owed` uses - not the review ledger, whose rows carry a date and no feature.
Replayed for T01 as the baseline.

**D11 - FR-008, a re-check against what the last check read.** Measured first (2026-10-17, the record store under
`.git/record-checks/`): the pop-up triage already diffs against "the page as the unit's last answer read it (its kept blob)"
(`modal_triage.before`), but (1) a triage's own answer (`make modal-triaged`, "triage: untouched") is written with NO pages, so it
erases the blob the check before it kept - after T01's first triage, eight of the nine depiction-answered pop-ups held none -
and (2) the triage bundle lists a page's changed blocks once for every unit naming it, so one unit diffed against the merge base
(`sheet/road`, never agent-checked) showed every unit both new bullets. So: a triage answer keeps the pages it read (their
blobs as they stand); the triage bundle groups its units by baseline and lists each group's own changed blocks; the claims triage
gets the same grouping. Tests: an answer then a one-word change shows that block alone; a triage answer leaves a baseline in
place.

**D12 - FR-009, one check where several are spent.** The cause first: `make record-owed` lists every unit the delta owes,
answered or not, and that listing sent T01 looking for three more quote-check batches after one had answered. So the default
listing marks each unit answered or owed (`UNANSWERED=1` stays the short form); `make check-bundle ... FOR=quote-check` puts a
page-wide unit (`#unfootnoted`) in the first batch alone; and `make modal-bundle` takes several `KIND=`s for one check and writes
one bundle holding each pop-up, answered unit by unit.

**D13 - FR-010, no write while the session's own gate runs.** A PreToolUse guard (`scripts/hooks/gate-write-hooks.sh`) refuses,
while a `make done` of this tree runs (`own-make.sh`), what moves what the gate's end checks (`preflight.py`'s `tree()`: HEAD and
`git diff --name-only HEAD`): an Edit or Write into the clone, and a Bash command that commits or stages (`git commit`, `git add` -
a staged new file enters that list) or writes a tracked record (`make append` - the ledger; `make claims-checked` and `make
claims-triaged` - the claims index; `make record-checked` - with `REPLY=` it files rows in a tracked `found.jsonl`; `make tick` -
tasks.md; `make accept` - gm-review.jsonl), naming `make verify-wait`. Not refused: `make modal-triaged`, which writes only under
`.git/`. Both refusals the round-2 review measured are in its test. Escape `GATE_WRITE_OK`.

**D14 - the hourly clock counts the session's time, not the GM's.** The event-log hook records whether a prompt is the GM's or
a background notification (`"gm": true`); `checkpoint.py` subtracts every Stop-to-GM-prompt gap from the hour; the feature
report's "waiting: the GM" reads the same field. The arbiter's test: a 63-minute window holding a 30-minute GM wait opens no
step-back.

**D15 - nothing in the engine.** Every item is tooling under `scripts/`, `tests/` and the Makefile, landed by `make land-tooling`;
no map changes, so no review check is owed.

### T02 part B (2026-10-17T20:46Z)

Owed by the hour-5 step-back (`hour:385-approach-checklist@5`, ruled `continue`) - D9's first firing on real work.

1. **What is refusing?** Nothing: every item landed on main with its test; the only refusal was `make tick` itself, holding the
   tick for this hour's step-back.
2. **A3 again.** The rules T02 is judged by are the GM's (FR-003 to FR-005, FR-008 to FR-011) and the guard doctrine's; none is O.
3. **A4 again.** n/a - no map, no place on the ground.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither; no item was tuned twice.
6. **The one-sentence test.** "Each tooling item landed alone, with a test red without it" - nothing for the GM to question.
7. **The next step is a measurement.** T03 is measured by the per-task table T02 built, against T01's row.
8. **Routes measured before asking?** Nothing is being asked.
9. **After a ruling.** The ruling is `continue`; the step it names is the tick, then T03.

## T03 - the four seeds failing at HEAD and the side-by-side shape (FR-012 first)

### T03 Approach (checklist part A)

Written blind (FR-012) by a fresh Opus agent, 2026-10-17 20:47Z-20:59Z, from the task text, `checklist.md`, `retro.md`,
`lane-law-table.md`, the code and the record; copied here verbatim. The comparison with the session's sealed conclusions is in
`retro.md` (SC-006).

1. **The goal, in the world.** Paths look the way people actually wear them. Two households walking side by side over open grass wear one path, so the reader sees one, not two treads joined by a rung. Each of the four seeds draws what the research describes: a row farm reaches its street, a sty stands clear of its farm's grove, a way reaches the field, and each household's way stays off its neighbors' yards.

2. **The constraints.** None of the four seeds is refused by an angle rule. They fall to four different rule families: `row_rules` farm_not_on_its_street (seed 40), `grove_rules.fixtures_on_groves` (seed 45), `last_resort.refuse_unreached` / `law.field_unreached` (seed 17), and the `fabric` probe `settle.fouled_segment` on five access lanes (seed 21). Only the side-by-side shape belongs to the lane law, through `tails.along_tail`: `_ALONG_FT` 14, `_ALONG_MIN_FT` 30, `_DOUBLED_DEG` 15. The other numbers involved are `NEEDLE_DEG`/`NEEDLE_FT` 20, `FIELD_REACH_FT` 60, `WEB_FABRIC_GAP` 7, `DOOR_REACH_FT` 60 and `ALIGN_TOL_DEG` 10. The cohort is 54 seeds.

3. **Where each comes from.** Each is classed in the per-seed list below. The GM's merge ruling (2026-10-17) can only be quoted as lane-law-table.md renders it: *"two paths running side by side become one"*. The exact words are in files this experiment forbids me. One claim is mislabeled. `FIELD_REACH_FT` cites 0014's drawing page "within 60 ft", but neither 0014 page contains "60 ft". The figure is O (it matches 0246's lane-end reach GUESS).

4. **Does each rule hold here?** Each is judged on the geometry in the per-seed list. Two cases differ from the rest. The side-by-side pair is open grass, where 0081's rule holds. Seed 45 is a mismatch between the placer and the check, not a sty standing in the trees.

5. **Order of operations.** Homesteads come before lanes, so nothing T03 does moves a homestead. Any exit that re-seats a house or re-deals seats (exit d, re-deal) goes to T04, as T01's retro did with seed 24. T03 works in the web, the door paths, the sty seat and the checks. Merging the later of two ways onto the earlier one keeps that order.

6. **The exits**, weighed per seed below. For the shape, (c) is the clear choice, and the GM named it.

7. **The search smell.** It is the risk for seeds 17 and 21: retrying field runs and re-routing ways against a 7 ft gap. The direct constructions are 0014's own fallback (*"Where no path is left to draw, the hamlet's nearest lane runs on to the bund"*) and 0246's ways laid "along the middle of the gaps". For seed 45 the construction is one predicate shared by placer and check. Nothing here reserves ground in advance.

8. **The budget.** About 4 h. The first hour is measurement: two of the five subjects (seeds 17 and 21) are refused rolls with no manifest, so nothing can be seen without a dump. The merge test is about 1.5 h, and seeds 40 and 45 are about 0.5 h each.

9. **Done, measured.**
   - **Baseline:** `.git/cohort48-t01b.log`, 50/54 passed, failing exactly 17, 21, 40 and 45.
   - **Merge test:** written first and red now on Inashiro lanes 8 and 14 (and F2's pairs).
   - **Seeds:** each of the four passes `make cohort N=1 SEED=n`, or carries a recorded exit. `make hamlet` prints OK for 40 and 45 because the grove and row rules belong to `cohort_audit`, not the generator, so it is not the oracle.
   - **Whole cohort:** no seed regresses from the baseline.
   - **Glyph-check:** the Inashiro village-lane check is re-run, with F1-F3 gone.

**Per seed**

- **Seed 40, `farm_not_on_its_street` at (2403, 1968)** (`homesteads/row_rules.py`).
  - **Class:** R 0033 for the principle (*"A farm whose grove stands between it and the street reaches the street by a path round the grove"*, where the path is a GUESS). The 60 ft door reach is a GUESS from 0246. Leaving the join out of "own street" (`street_index None`, `street.py`) is O: its stated reason is seed 904's "behind another" judgment, not research.
  - **Geometry:** this is the end farm of street 1. Its north band and its west band (x≈2307, y 1928-2021) stand between it and lane 3, which is 143-217 ft away. The join, lane 4, is a 6 ft street-rank way leaving the street's end at (2201, 2030), and it passes about 75 ft south of the farm's south door. No lane `serves` this farm, though every other farm has a door path. To a reader, lane 4 is the street turning east past the farm.
  - **Holds here?** Yes in principle; the farm needs a path to its street. The O definition is what refuses it.
  - **Exit:** (b)/(c). A row farm may take its street's own join as its street, in both `lay_door_paths` (`streets`) and `row_rules` (`drawn_st`), as one predicate.
  - **Unsettled:** which `door_path` candidate failed, and on what rule. That dump is the first measurement. The two found rows the cohort named for seed 40 are a different rule (wave 96, `refuse_unreached`); I am noting them, not chasing them.

- **Seed 45, `fixtures_on_groves`, two sties** (`settlement/homestead_parts/grove_rules.py`; the placer is `homesteads/sties.py`).
  - **Class:** R 0036 for the principle (a GUESS there). `ALIGN_TOL_DEG` 10 is UNRESEARCHED, and the `in_frame` docstring calls itself plumbing.
  - **Geometry:** the sty at (1879.3, 1766.5) overlaps its north band by about 0.5 ft, and the one at (1616.8, 1291.7) by about 2.7 ft. Both should clear by the 3.5 ft wall gap. The houses are turned 7-8°. `in_frame` treats a band under 10° of skew as square to the house and uses its unturned box; across a 185 ft band that is about 12 ft off at the ends. The check reads the band's axis-aligned box against the sty's turned box.
  - **Holds here?** Yes. The fault is that placer and check read different boxes, against the rule that placement and its test import the same predicate.
  - **Exit:** (e), conform by fixing the placer to test the band as drawn. No room and no new number are needed.

- **Seed 17, the field reached by no way** (`last_resort.refuse_unreached`, after `reach.settle_field` found nothing).
  - **Class:** R 0014 for the principle (*"the field path runs from the hamlet to the paddy's outer bund and joins it"*). The 60 ft is O, mislabeled as R.
  - **Holds here?** Yes; a hamlet beside its field walks to it. The real refusal is hidden: every candidate run was turned down by `Lawful`, and the refusal does not say for which rule.
  - **Unsettled:** I found no facility that keeps a refused roll's manifest; my grep for one found nothing. This is the same tooling gap T01's retro named for `settle_knots`.
  - **Exit:** measure first, by recording why each candidate was refused. Then (b), 0014's own fallback of the nearest lane running on to the bund. If a candidate was refused for running beside a lane, the general merge may dissolve it, but that is only a hypothesis.

- **Seed 21, `fabric` on access lanes 3, 4, 5, 7 and 9, lane skeleton Y.**
  - **Class:** R 0246 for the principle (*"Its way leaves its dooryard round its own garden beds and fixtures"*; *"Nothing is built on a lane"*). The 7 ft gap is O; 0246 calls it *"a map drawing convention, not a measured figure"*. An open E3 found row already names that gap.
  - **Holds here?** Unseen: there is no manifest. My hypothesis, unverified, is that the ways chosen against stand-ins for the farmsteads (`household_ways.seated_parts`) are judged later against the farmsteads as drawn.
  - **Exit:** the dump first. Then (a), the O gap, weighed against (d), more room, with room first under the GM's 2026-10-12 ruling. 0246's own fallback is reaching the house across a neighbor's yard. Room is a seating change, so it goes to T04.

- **The side-by-side shape (Inashiro F1-F3).**
  - **Geometry:** lane 8 is a door stub of house (2388, 2151); its samples sit 14.4, 12.3 and 11.1 ft from lane 14. Lane 14 was laid after lane 8 (z 1045 against 1039). It runs west and then turns 90° to end in a T on lane 8 at (2332, 2201); that turn is the rung. Between the two lanes is open grass, with the household's own garden and threshing yard on lane 8's other side.
  - **Why it escapes:** `along_tail` breaks at its first sample, because 14.4 ft is past `_ALONG_FT` 14 by 0.4 ft, before `_ALONG_MIN_FT` 30 is even asked. Both numbers are O; the merge principle is G, and 0081 ("Two paths running side by side are drawn as one") is a convention.
  - **Holds here?** Yes: open ground, which is exactly where 0081 applies.
  - **Exit:** (c), as one general test rather than a fourth detector. Two treads within a reach of each other, near parallel, over ground that the settle's obstacle families leave empty, for longer than a junction's approach, become one path. The later way is cut to a T where it comes alongside, and a household's way is cut at its far end, never at its door. On F1, lane 14 would end on lane 8's start, and lane 8's stub would carry both households.
  - **Open:** the reach. 0246's lane room (18-20 ft) is the only researched figure in that range, and F2's pairs at 18-25 ft fall partly outside it. This is the shape's one unsettled number.

### T03 part B (2026-10-17T21:40Z)

Owed by the checklist, not by D9: the same refusal family a third time on one attempt (REACH 20 ft, then the door guard, then
`Lawful` at 14 ft), and seed 49 found failing.

1. **What is refusing?** With REACH in `along_tail`, the reference map: a farmhouse (2573, 1981) unreached, then a household's
   way (lane 11) breaking `doubled_tails` that the settle may not cut.
2. **A3 again.** REACH: O (anchored on 0246). The doubled-tail rule's 14 ft: O. "Two paths side by side become one": the GM's.
3. **A4 again.** The rule describes the world: two ways 18 ft apart over open grass are one path. But a REFUSAL at 20 ft
   describes nothing - the world has no refused maps; it merges them.
4. **Moving earlier for later?** No.
5. **Tuning or changing?** Three tunings of one number's reach in a row: stop. Back to A6.
6. **The one-sentence test.** "Widening the tail test refuses more ways" - the GM would ask why a merge refuses anything.
7. **The next step is a measurement**: the merge as its own step that never refuses (D17 re-decided), tested red first.
8. **Routes measured?** The cohort's 59/60 is the matrix; seed 49 measured at HEAD (failing there too).
9. **After a ruling.** None asked.

### T03 Approach (re-answered 2026-10-17T21:40Z)

1. **The goal.** Unchanged, plus seed 49 (D24).
2. **The constraints.** As the blind block, with REACH 20 ft for the merge and the law's 14 ft kept.
3. **Where each comes from.** REACH: O, anchored on 0246's lane room. The fence gap's own-garden exemption: O, a DEVIATION on 0246's
   drawing page.
4. **Does each hold here?** A merge holds on open ground. A refusal at 20 ft does not (part B, 3).
5. **The order.** The merge runs after the reach and before the network rule. Nothing placed earlier moves.
6. **The exits.** (c), a merge that dissolves the pair. The law is not widened.
7. **The search smell.** None. One step, one predicate, and a cut written only where lawful.
8. **The budget.** About 1 h used of 4 h. About 1 h more for the merge and its tests, then the gate.
9. **Done, measured.** D22, and seed 49.

### T03 part B (2026-10-17T22:20Z)

Owed by the hour-6 step-back (`hour:385-approach-checklist@6`, ruled `change-route`), D9's second firing on real work.

1. **What is refusing?** D17's merge, tried as its own step: 58/66, with six seeds regressed. Without it: 63/66, with seeds 49, 55
   and 57 refused, all three at HEAD too. Seed 57 got worse under T03's fixes (1 knot to 4).
2. **A3 again.** REACH (20 ft, then 25 ft fitted to F1-F3): O, a convenience number. `_ALONG_MIN_FT` 30: UNRESEARCHED. The merge
   principle is the GM's. The lane-knot rule is the lane law's (R 0081). The own-garden exemption is O, a DEVIATION recorded
   on 0246.
3. **A4 again.** The merge describes the world. The way it was built does not yet: the later passes act on the junctions it
   makes and strand households.
4. **Moving earlier for later?** No.
5. **Tuning or changing?** REACH was moved twice. A third move is not taken. The merge leaves T03 (the rulings: route (a)).
6. **The one-sentence test.** "The merge is right but the passes after it break the web" - the GM would ask why those passes
   are not fixed. That is the carried task's first item.
7. **The next step is a measurement**: seed 57 bisected (done). The join order in the last resort alone takes it to 2 knots.
8. **Routes measured?** Yes: the cohort with and without the merge, and seed 57's bisection (`t03-d17-evidence.md`).
9. **After a ruling.** The steps it names are the bisection, then land the four with the rest carried. Its condition (57 no
   worse than HEAD) is put back to the arbiter with the measurement (`ask:t03-seed57-residue`).

### T03 Approach (re-answered 2026-10-17T22:23Z)

1. **The goal.** The four seeds' maps produced as the research describes. Two paths side by side made one is carried to T12.
2. **The constraints.** As the blind block, less D17's REACH, which T12 takes.
3. **Where each comes from.** The own-garden exemption is O, a DEVIATION on 0246. The join order is no number. The band predicate
   is the check's own.
4. **Does each hold here?** Yes for the four. The merge's later passes do not yet (T12).
5. **The order.** Nothing placed earlier moves. The settle's own rounds keep HEAD's order.
6. **The exits.** (e) for 45, (a) for the fence gap, (c) for the join order. The merge goes to T12 by ruling.
7. **The search smell.** None left in T03: the merge loop was stopped at its third tuning.
8. **The budget.** About 1 h 50 min used of 4 h. The gate, the checks and the retro remain.
9. **Done, measured.** D25: the four pass, nothing newly fails against HEAD, every exit owned by T12.

### T03 part B (2026-10-17T23:08Z)

Owed by the hour-7 step-back (`hour:385-approach-checklist@7`, ruled `continue`).

1. **What is refusing?** Nothing in the map: the gate is green, and every claims and record check is answered. The tick was held
   only by this hour's step-back and its tooling fix (now landed).
2. **A3 again.** Unchanged since the 22:20 block: the merge's reach is O and T12's; the two known gaps (`FIELD_REACH_FT`'s
   reach, the doubled tail's 15 degrees) are DRIFTED against 0014 and 0081 and carried to T12.
3. **A4 again.** n/a - no rule refused anything this hour.
4. **Moving earlier for later?** No.
5. **Tuning or changing?** Neither: three claims rounds and two pop-up rounds, each answering the last, the third pop-up round
   accepted by the arbiter.
6. **The one-sentence test.** "T03 lands its four seeds and carries the merge" - the rulings say so.
7. **The next step is a measurement**: the tick, then the per-task table compared with T01's.
8. **Routes measured?** Nothing is being asked.
9. **After a ruling.** `continue`: tick and land.

### T03 Decisions

Written by the session from the blind block (FR-012). Where the block and the session's sealed notes differ (seeds 17 and 21),
the decision names the measurement that settles it, not a side.

**D16 - measure before any fix (B1, A7).** Seeds 17 and 21 are refused rolls with no manifest, so the first step is to see the
ground. A refused roll's refusal names, for every candidate it turned down, the rule that turned it down and where (as T01's
`lane_breaches` did for the knots), and the session dumps the refusing geometry (the ways, the yards and beds near them, the
field's outer bund) in a detached worktree before naming a cause. The per-candidate refusal is engine code and lands with the
task. No fix to 17 or 21 is written before its dump is read.

**D17 - the side-by-side merge is one settle step; the law's refusal is left as it is.** Re-decided 2026-10-17 after the part B
below. Measured: REACH put into `along_tail` itself (the plan's first D17) reached all five of its callers. At 20 ft the lane law's
doubled-tail rule and `Lawful` refused household ways the settle may not cut, and the reference map refused a farmhouse.
So the merge and the refusal are two questions.
(1) **The merge**, a settle step run after the reach is drawn and before the network rule (`settle_side_by_side`). Where a
way's end runs beside an earlier way within REACH, within `_DOUBLED_DEG` of parallel, past the junction's own approach, over
ground the settle's two obstacle families leave empty, that way is cut to a T where it first comes alongside. The cut way is
the later of the two, and its far end is cut. A household's way is never cut at its door. A cut is written only where the cut
way keeps the law (`Lawful`, the way left out of what it meets), so the step never refuses and never strands a house. REACH is
20 ft, anchored on 0246's lane room (18-20 ft) and labeled a convention anchored there. F2's 18-25 ft pairs are measured against
it, and REACH is moved (an O number) rather than F2 kept.
(2) **The law's doubled-tail rule keeps its 14 ft** (`_ALONG_FT`, O), the refusal it was. That is not a narrowing of "two
paths running side by side become one": the merge makes them one, and the rule only refuses a pair the merge could not mend.
The test, written first: Inashiro's lanes 8 and 14 and seed 49's root way, each red before the step. T01's three detectors are
kept as they are; the step merges only what they leave.

**D18 - seed 45: one predicate for placer and check.** The sty placer (`homesteads/sties.py`) tests the grove band as drawn,
the same turned box `grove_rules.fixtures_on_groves` reads, through one shared predicate. The 10-degree `in_frame` skew stays
for what else uses it. No new number, no room.

**D19 - seed 40: the street's join is the row farm's street.** The dump first: which `door_path` candidate failed, and on
what rule. Then a row farm may take its own street's join as its street, in `lay_door_paths` and `row_rules` alike, through one
predicate. Nothing re-seats a homestead (A5). If the dump shows the farm cannot be reached without a re-seat, that is T04's.

**D20 - seed 21: the exit follows the dump.** The dump (D16) is read first. It measures, for each fouled access lane, whether
the lane is a household's only route to the network and whether that route runs through a neighbor's yard. The exits, in order:
(1) **Where it does, the household is reached across its neighbor.** 0246's drawing page, as it stands, says where the gaps
leave no lawful way the household *"is reached across the yard of its nearest neighbor with a way, the walk not drawn: a
household cut through a neighbor's yard in a pinch"*. That rests on the GM's ruling of 2026-10-03 (feature 318 amendment 2): *"it's
okay for people to cut through neighbors' yards in a pinch"*. Its research is 0081's finding that a household with no way of
its own crossed a neighbor's land by custom. "The walk not drawn" is that page's drawing convention, not a finding, and T03
keeps it as the page states it. Whether the walk across the yard should be DRAWN is a drawing question the page decides, not
this task. This is the session's difference from the blind block, marked as FR-012 asks: the blind block names this fallback
but chooses the gap or room first, and the session puts the record's own fallback first because the record states it for
exactly this case. The dump decides whether the case applies.
(1b) **Measured 21:22: seed 21's five ways come near only their own household's garden and yard.** So the O gap applies,
and the decision is that a household's own way is exempt from the 7 ft fence gap beside its own garden, kept off its beds by the
overlap matrix (`fabric.owned_gardens`). It is recorded as a DEVIATION on 0246's drawing page. More room would not help: the
distance is between a household and its own beds, not between homesteads.
(2) Else the 7 ft gap (O, a convention) is weighed against more room (the GM's 2026-10-12 ruling: room first), and a room
change is T04's.
Before choosing, it is asked whether a reader of the research would call the drawn place wrong. That is the question the
blind block did not reach (`retro.md`, SC-006).

**D21 - seed 17: measure, then the record's own fallback.** The per-candidate refusal (D16) says why each field run was turned
down. The exits, in order:
(1) Where a run was refused for coming alongside a lane, D17's merge dissolves it.
(2) Else 0014's fallback, the hamlet's nearest lane run on to the bund (R).
(3) Else, if the field's own bunds already reach the hamlet's edge, it is asked whether the refusal should exist at all.
`FIELD_REACH_FT`'s claim is corrected in T03: 60 ft is O (no 0014 page says it), relabeled with what was searched
(constitution XIV).

**D24 - seed 49, found failing at HEAD (constitution XIV).** The 60-seed cohort (21:32) refused seed 49, and a detached worktree at
HEAD refuses it too (the fence gap on its own garden, like 21). The own-garden change clears that cause. Its second cause is
D17's own shape: its root household's way ran 18 ft beside the skeleton and ended unjoined, so the network rule dropped it with
the three ways hanging from it. It is fixed by D17's merge and held by D22's cohort like the four.

**D22 - done.**
- The baseline: `.git/cohort48-t01b.log`, 50/54, failing 17, 21, 40 and 45; and seed 49, failing at HEAD in a detached worktree (D24).
- Each seed passes `make cohort N=1 SEED=n`, or carries its recorded exit to T04 (a re-seat or room change, T04's own task);
  an exit no task of this feature owns is not done.
- The whole cohort regresses no seed.
- The merge test is red without its change.
- The Inashiro village-lane glyph-check is re-run with F1-F3 gone.
- `make done` is green, and the claims, records and checks it owes are answered.
- The task lands with its retro row.

**D23 - budget.** About 4 h, the blind block's. Twice that (8 h) triggers part B. So does every trigger D9 names.

**D25 - what T03 lands, and what it carries (the rulings of 2026-10-17: hour:385-approach-checklist@6, ask:t03-d17-route,
ask:t03-seed57-residue).** T03 lands the four seeds' fixes in their narrowed form:
- the own-garden exemption (`fabric.owned_gardens`, D20);
- the join steps after the reach in the last resort's passes only (the settle's own rounds as at HEAD: joining there added
  lane knots to seed 57);
- the shared band predicate (D18);
- D16's refusals;
- `FIELD_REACH_FT` relabeled (D21).
Against HEAD: 17, 21, 40 and 45 fixed, nothing newly failing, the pool clean with Kashikawa's lane 9 straightened. D17's merge
(saved; it merged F1-F3 and fixed seed 49 but regressed six seeds, because the later settle passes are blind to the junctions it
makes) and D24's seed 49 are NOT done in T03. With seed 55 (one lane knot, as at HEAD) and seed 57's residue they are carried
to T12, as the arbiter ruled: seed 57's residue is lanes 1/13, ends 21.6 ft apart, `settle_knots`' gather of lane 13 refused by
`needle_loops`, brought in by the own-garden fix; 57 stands at 2 knots against HEAD's 1, waived by ask:t03-seed57-residue.
D22's done is read accordingly: the four seeds pass, no seed newly fails against HEAD, and every exit is owned by T12.

## T13 - a finding on unchanged code is carried, not refused (amendment 3, FR-013)

### T13 Approach (checklist part A)

1. **The goal, in the world.** A research page can be corrected without the correction blocking the task that made it on code
   that task never touched, and without the findings it surfaces being lost: each is an open task, so its feature cannot close
   until the code or the claim agrees with the research again.
2. **The constraints.** The GM's option 3 (amendment 3); a finding on changed code or a changed claim still refuses; a finding at
   the base still warns; every refusal names its compliant command (CLAUDE.md, "What is enforced"); the open-task refusal
   (`speckit-todo.py` `holding`) honors a `[lands-open]` box only where the tooling or a reviewed plan put it; a test red without
   each rule; `CLAIMS_OK` stays the escape.
3. **Where each comes from.** The rule is the GM's (G, 2026-10-17, "Yes, please lock in option three."), the strict half kept from
   feature 316 (G). The record file's name and the task box's words are ours (O).
4. **Do they describe the world here?** Yes - measured on T03's landing (`ask:t03-claims-at-landing`): three findings, all on code
   T03 left unchanged, all surfaced by one page paragraph.
5. **The order.** The rule in `classify` first (the decider), then the record and the command that writes it, then the open-task
   honor, then the gate's message; T03's three findings filed through the new command last, as its first real use.
6. **The exits.** (c) a rule that dissolves the case - **chosen**: the GM's option 3 replaces "introduced" with "carried" for this
   case. (a), (b), (d) n/a; (e) conform - the strict rule the GM declined.
7. **The search smell.** None: one classification and one record.
8. **The budget.** About one hour; twice that is part B.
9. **Done, measured.** The tests in `tests/tooling/test_claims_index.py` red without each rule (carried vs introduced vs
   pre-existing; a filed carry passes; an unfiled one refuses naming `make claims-carry`; the carried box honored by `holding`);
   `make hooks-test` green; `make claims-carry F=385 T=T12` files T03's three, and the push lands without `CLAIMS_OK`.

### T13 Decisions

**D26 - carried, decided in `classify`.** A finding that did not stand at the base (no base row, or a base verdict that is no
finding) is CARRIED when its unit's code and claim are unchanged: with a base row, the row's `code` fingerprint (code plus
claim) equals the head's, whether its research moved or the claim was only judged again (spec-fidelity, T13 round 2: a
re-judgment is a finding on unchanged code, which option 3 never blocks); with none, the unit's core
under the same key at the base matches the head's and `research_fp` against the base questions differs. A unit moved or
renamed is never carried: a finding on it is introduced or pre-existing as today (spec-fidelity, T13 round 1). Every other first
finding keeps today's verdict: introduced where the code or the claim changed; pre-existing where neither the code nor the
research moved and the base had no row (it warns, as today). `classify` returns (introduced, pre-existing, carried).

**D27 - filed by one command, held in a record.** `make claims-carry F=<n> [T=<Txx>]` (`claims.py carry`) files every carried
finding not yet filed, into the feature being landed only - the active task's feature (`plan_gate.active_task`); another
`F=` is refused, so a finding cannot be parked in a long-lived feature while this one closes (spec-fidelity, T13 round 1):
into the open task `T=` names, its keys appended to that box's text, or, without `T=`, a new box at the end of the feature's tasks - `- [ ] T<next>
Carried by the claims gate (FR-013): findings a page edit surfaced on code left unchanged - fix the code or the claim and re-check
each: <keys> [lands-open]` with its `research: rendering` line - and appends `{"task", "keys", "utc"}` to
`specs/<feature>/claims-carried.jsonl`. A key is FILED while a row of the active feature's record names it and that row's
task is still an open box in its `tasks.md` (no active task: no key is filed); a ticked task un-files it, so a finding still standing refuses again.

**D28 - the push.** `gate` refuses an unfiled carried finding as `carry: <line>`, the message naming `make claims-carry
F=<the active feature>` (`plan_gate.active_task`, `<n>` when none); a filed one warns as `carried (<feature> <task>): <line>`.
`claims-gate.sh`'s footer names the command for a carry. `holding` honors an open `[lands-open]` box whose id a row of the
feature's `claims-carried.jsonl` names - the tooling put it there, as the open-task rule requires.

**D29 - T03's three.** `settle.py::theirs`, the doubled tail and `_clear_link` are already in T12's words; they are filed into T12
(`T=T12`), not a second box. `docs/guards.md`'s claims-gate rows say carried. Nothing in the engine: the route is DIRECT.

### T13 part B (2026-10-18T01:29Z)

Owed by the hour-8 step-back (`hour:385-approach-checklist@8`, ruled `continue`).

1. **What is refusing?** Nothing in the code yet; the plan review (round 1) BLOCKED two clauses - D26's move clause and D27's
   filing into any feature - both narrowed now as it asked.
2. **A3 again.** The rule is the GM's option 3 (G); the record file and the box's words are ours (O).
3. **A4 again.** n/a - no map, no place on the ground.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither; one round of review, each point taken as written.
6. **The one-sentence test.** "A page edit's finding on untouched code is filed as an open task of this feature instead of
   blocking the landing" - the GM's own option.
7. **The next step is a measurement.** The round-2 plan review, then the tests red without each rule.
8. **Routes measured before asking?** Nothing is being asked.
9. **After a ruling.** The ruling is `continue`; the step it names is T13 once its plan is reviewed.

## T14 - T03 measured again: whose time, each phase, the decision log printed (amendment 4, FR-014 to FR-016)

### T14 Approach (checklist part A)

1. **The goal, in the world.** The GM reads a task's row and sees where its time went - the session working, the session
   waiting, the reviewers' own work - phase by phase, and a retro's decision log is filled from a printed skeleton, so the next
   question ("why did four seeds take 2 h 25?") is answered by `make feature-report`, not by hand.
2. **The constraints.** FR-014 to FR-016 (the GM's, amendment 4); the event log never refuses and never prints (event_log.py's
   contract); the report reads, never writes, but for `WRITE=1`; a test red without each rule; tooling lands by
   `scripts/sync-with-main.sh done` (no engine code).
3. **Where each comes from.** The requirements are the GM's (G, 2026-10-18). The attribution by transcript is a measurement
   (2026-10-18: 202 of T03's 549 calls matched a subagent transcript's tool id, 347 the session's, none unmatched); the table columns and the window
   fallback's form are ours (O); the idle cap is the report's existing hour (`IDLE_CAP_S`).
4. **Do they describe the world here?** Yes - each is T03's own measured gap: the "thinking 64%" that was not the session's (the report's own output, `make feature-report F=385
SINCE=2026-10-17T20:44:00Z UNTIL=2026-10-17T23:10:00Z`, run 2026-10-18 before this task),
   the merge a second goal, the decision log reconstructed wrong.
5. **The order.** Attribution first (every other table reads it), then the phase table, then the skeleton, then the checklist
   line; T03 replayed last as the acceptance.
6. **The exits.** (c) a rule that dissolves the case - **chosen**: the transcripts already say whose each call was, so no
   heuristic is the primary source. (a), (b), (d) n/a; (e) conform - n/a.
7. **The search smell.** None: a join on recorded ids.
8. **The budget.** About 90 min; twice that is part B.
9. **Done, measured.** ONE goal: the report shows T03 as the hand count did. Tests in `tests/tooling/test_feature_report.py`
   red without each rule; `make feature-report F=385` on T03 attributes 202 calls to subagents and prints its phases and its
   skeleton; `make hooks-test` green.

### T14 Decisions

**D30 - whose call, from the transcripts.** A tool event is a SUBAGENT's when its `id` (the tool_use id) appears in a subagent
transcript of its session - `<projects dir>/<sid>/subagents/agent-<aid>.jsonl`, the session's transcripts found under
`~/.claude/projects/*/` by `sid`. The event-log hook also records `by` on a tool event whose payload carries `agent_id`, so a
log whose transcripts are gone still says it. WHERE NEITHER SAYS, decided per subagent RUN (spec-fidelity, T14 round 2): a
call with no `by`, inside the start-to-stop window (`SubagentStart` to `SubagentStop`) of a run whose own transcript
(`agent-<aid>.jsonl`) is not found, is that run's, counted as an ESTIMATE - never the session's own `Agent` call, which launches it; where the windows of several such runs overlap,
the earliest-started's (the GM's "otherwise use each agent's start and stop window";
spec-fidelity, T14 round 1). A call no transcript names, inside the window of a run whose transcript was found, is
the session's; a call outside every window is the session's. `split_time` counts only the session's events; the subagents' calls are counted apart, and the line under "Where the
time went" says how many were attributed by transcript, by the hook and by window.

**D31 - the session's time split three ways.** "Where the time went" gains a line naming how many tool calls were subagents'
and how they were attributed, and its categories separate: the session working (its tool time and its gaps between its own
calls, a gap with a `Stop` in it excepted), the session waiting (a `Stop` until the next event: on a subagent, a background run
or the GM, as `_waiting` already names) - and, waiting too, the span of the session's own `Agent` call (a foreground run: no `Stop`
comes, the call lasts from launch to return), and every gap inside it (spec-fidelity, T14 round 2: never its working time) -
and the subagents' own work (each run's start to stop, from `SubagentStart` /
`SubagentStop`, summed, shown beside the session's and never added to its share). A session gap past the hour cap
(`IDLE_CAP_S`) is IDLE, counted apart in both tables, never dropped - so a task's whole time is split.

**D32 - each task's phases.** Per task, a table of its segments between decision points (the cuts `task_rows` already makes):
the span (UTC), what ended it (the agent and verdict, or the tick), the session's calls, its working minutes, its waiting
minutes, its idle minutes, and the subagents that ran in it (`type x n, minutes`).

**D33 - the decision-log skeleton.** Per task, in time order: its start (`task-start`), every agent returned (type, verdict,
minutes), every cohort and gate run - every make run whose target starts `cohort`, and every run the event log files under the
`gate` category or names `verify` (its minutes; spec-fidelity, T14 round 1: "every" is the rule, not a list), every plan heading stamped
`part B (<UTC>)` or `Approach (re-answered <UTC>)`, its tick - each row with a blank "what decided it" cell for the retro to
fill. Checklist C8 points at it.

**D34 - one goal a task.** Checklist part A item 9 ("Done, measured") gains: it names ONE goal; a second goal found in the task
becomes its own task (a new box, or a carried row) before any work on it - T03's merge was the second goal that cost 21 min (the event log, read 2026-10-18 - `retro.md`'s T03 phases, 21:45-22:06)
and
pulled the seeds' landing into arbiter rulings. A judgment, not a guard: no mechanical test tells two goals from one.

## T04 to T10 - T48, T47's patch, five ranking rows

Each decided at its start, in this order (spec FR-007), its section added here and reviewed by `make decide`.

## T04 - T48: the web carries a re-deal of the seats (384 User Story 2, SC-004)

### T04 Approach (checklist part A)

1. **The goal, in the world.** Wave 155's pocket-well change (the well off the farmstead, `w155-pocket-attempt.patch`) moves
   where homesteads are seated; the lanes are trodden after the houses stand, so whatever seats the re-deal produces, the web
   walks round them - no seed refused for a web that could have been walked.
2. **The constraints.** SC-004: the re-deal cohort (`m:w156-redeal-cohort`'s method - `make cohort N=48`, then the patch applied
   and the same cohort) fails no seed that passes at HEAD; the lane law's rules (`ways/law.py`); the pool; 384 FR-002 (374's rules
   as amended). Baseline 2026-10-13: HEAD 50/54, patched 49/54 - 10 and 24 newly failing, 17 mended. T03 has since fixed 17, 21,
   40 and 45 at HEAD, so the baseline is retaken first.
3. **Where each comes from.** SC-004 is the GM's (G, 384). Each lane-law rule a refusal names is checked, R/G/O, from its claim,
   when it refuses (B2) - not listed in advance from memory.
4. **Do they describe the world here?** Asked of each refusal at the place it refuses, from a dump of the geometry (B1, B3):
   would a reader of the research call that map wrong?
5. **The order.** Homesteads first, then lanes (GM 2026-10-02): the fix is in the web, never a re-deal moved to suit a lane.
6. **The exits.** Weighed per refusal once measured: (a) an O number, (b) an exception the ground forces (`forced.py`), (c) a
   rule that dissolves it, (e) conform. (d) more room is the re-deal's own business, not the web's.
7. **The search smell.** Watch for a retry or re-order loop in the settle; the third tuning of one thing is a step back (B5).
8. **The budget.** About two hours (a guess: the retaken baseline, two seeds' causes, their fixes, one cohort, the landing).
9. **Done, measured.** ONE goal: the patched 48-seed cohort fails no seed that passes at HEAD, both rolled now, compared by
   `cohort_known` (FIXED / NEWLY FAILING / WORSENED / PRE-EXISTING). T05 (re-landing the patch itself) is a separate task.

### T04 Decisions

**D35 - measured first, and the web already carries the re-deal: no engine change.** Retaken 2026-10-18 by
`m:w156-redeal-cohort`'s method on today's HEAD (055a12b5c): `make cohort N=48` passes 54/54
(`dev/cohort-log/20261018T023923Z-diagram-backlog-373625.json`); with `w155-pocket-attempt.patch` applied (it applies cleanly) the
same cohort passes 54/54 (`dev/cohort-log/20261018T024147Z-diagram-backlog-378026.json`; the reference map a roll-cache MISS, so
the patched engine rolled). Seeds 10 and 24, newly failing under the patch on 2026-10-13, pass: T03's fixes (the own-garden gap,
the last resort's join order, the sty band) were what the re-deal had been knotting on. SC-004 is met as the code stands;
building a web change to meet it would be a fix with nothing to fix. The patch is reverted in the tree - re-landing it, with its
pool and record checks, is T05's one goal (D34).

The tooling fix this task's measurement found (a cohort record rolled over an uncommitted engine diff reads as its commit's)
is its own task, T15 (D34: one goal a task; spec-fidelity, T04 round 1); the hour-9 step-back's tooling fix is T16. T04's goal is
384's SC-004 (here FR-007, SC-003).


### T04 part B (2026-10-18T02:49Z)

Owed by the hour-9 step-back (`hour:385-approach-checklist@9`, ruled `continue`).

1. **What is refusing?** Nothing in the maps: both cohorts pass 54/54. The plan review (round 1) BLOCKED D36 as a second goal.
2. **A3 again.** SC-004 is the GM's (G, 384); no lane-law rule refused, so none to place.
3. **A4 again.** n/a - no refusal on the ground.
4. **Moving something earlier for something later?** No: nothing moved.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "The re-deal already passes; nothing to build" - nothing for the GM to question but the measurement,
   which names both records.
7. **The next step is a measurement.** None owed: SC-004 is measured. The next step is T04's tick.
8. **Routes measured before asking?** Nothing is being asked.
9. **After a ruling.** `continue`; the step it names is T04's plan review, then the stamp - moved to T15 by that review.

## T05 - T47: the wave 155 pocket-well patch re-landed, no waiver (384 FR-007)

### T05 Approach (checklist part A)

1. **The goal, in the world.** A clustered hamlet's well stands off every farmstead, shared, as 0028 and 0196 describe ("shared
   off the farmstead"; "one or two" a hamlet, five to ten households a well); no household's homestead holds a pocket well.
2. **The constraints.** 374's W155-4 bar: no roll passing at HEAD refuses (the pool, the cohort); no well inside a homestead; every
   household within reach of water (`WATER_REACH_FT`, 760 ft, 0196); no well over ten households; the counts recorded. The lane
   law; the claims and record checks the patch's changes owe; three glyph-check occasions (a pool map's well moved: Inashiro,
   Kuwabata, Sawada - 374's tasks.md); the gate, green.
3. **Where each comes from.** The bar is the GM's process (G, 374) over research rules: 0028/0196 (R) for off the farmstead and the
   count; 760 ft (R, 0196); the shares cut along the long axis (GUESS, W155-5, recorded); the third well for ten (R, 0196's range).
4. **Do they describe the world here?** Measured by T04 on today's engine: the patched cohort passes 54/54. Each refusal the pool
   or a check names is asked again at the place it refuses (B1-B3).
5. **The order.** The seating lays no pocket; the wells are seated after the houses (wave 154's forms) - nothing placed earlier
   moves for a well.
6. **The exits.** The patch's own were priced in 374 (W155-6: more room priced first, the third well inside the research range
   taken). Here: (e) conform - re-land as built, no waiver.
7. **The search smell.** None new: the patch's searches are wave 154's, measured.
8. **The budget.** About 90 min (the pool, the record and claims checks, three glyph checks, the gate).
9. **Done, measured.** One goal: the patch on main with no waiver - the pool clean, the cohort as HEAD (T04: 54/54 both), the
   wells measured (`m:w155-wells`'s quantities on the pool), every owed check answered, the gate green.

### T05 Decisions

**D41 - the patch re-landed as built.** `w155-pocket-attempt.patch` applies cleanly to today's HEAD (2026-10-18; the engine
unchanged since T04's cohorts). Its decisions are 374's W155-1 to W155-6, each ruled within by 374's plan review; nothing in
them changes here. Its bar is W155-4, measured on the pool and the 54-seed cohort (T04: 54/54 at HEAD and patched); the 44 rolls
of 374's scratch tooling (`tools13/roll13.sh`) are not reproducible from the repository, so the cohort stands in for them, as
384's SC-004 already did. The occasions are 374's three (placement-changed: well on Inashiro, Kuwabata, Sawada), each a
glyph-check of its map's wells.

### T05 part B (2026-10-18T03:50Z)

Owed by the hour-10 step-back (`hour:385-approach-checklist@10`, ruled `continue`).

1. **What is refusing?** Nothing on the maps: the pool rolls clean with the patch; no well on any homestead piece. The record
   checks found three wordings in 0196's changed block (applied together); the hour guard split one batch of dispatches (T20).
2. **A3 again.** The bar's rules as part A: 0028/0196 (R), 760 ft (R), the shares (GUESS, recorded).
3. **A4 again.** Asked at the pool's wells: they stand off every farmstead, each serving 3 to 10 households.
4. **Moving something earlier for something later?** No: the wells are seated after the houses.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "The patch re-lands as built, measured as 374 measured it" - nothing to question but the bar's
   numbers, recorded beside it.
7. **The next step is a measurement.** The remaining checks' answers, then the gate.
8. **Routes measured before asking?** Nothing is being asked.
9. **After a ruling.** `continue`; the step it names is re-dispatching the three refused checks (done) and the landing.

### T05 part B (2026-10-18T10:25Z)

Owed by the hour-12 step-back (`hour:385-approach-checklist@12`, ruled `continue`).

1. **What is refusing?** Nothing on the maps: the pool rolled on T05's tree is clean (`make maps SCOPE=all`, 2026-10-18), the gate
   green (199 s) after three reds of three causes (a reviewer's British spelling in a record, a stale notes census with Sawada's
   door zigzag gone - its strict xfail cleared - and `seat_wells`' early return uncovered), and the three well glyph-checks PASS.
   The claims gate refused only old behavior the patch's unit touched (the front row's size, the standoff), carried into T06 by
   ask:t05-old-drifts-at-landing.
2. **A3 again.** The bar's rules as part A; the claims relabeled to what the record says (0031 for the cluster shape, the 80 ft
   seat a GUESS 0196 names), the standoff split (house and yard on 0029; the shed in and the garden out UNRESEARCHED).
3. **A4 again.** Asked at the drawn wells by the glyph-checks: none stands in a farmstead, each serves 3 to 10 households; two seats
   read near a lane (Inashiro F6/F7, Kuwabata F8) - filed as found rows of wave 155, not tuned here.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: no number moved; every change since part A was a label, a test or a record.
6. **The one-sentence test.** "The patch re-lands as built, its claims saying what the record says" - true.
7. **The next step is a measurement.** The landing cohort (`make cohort-landing`), then the push.
8. **Routes measured before asking?** Yes - the pool rolled before ask:t05-old-drifts-at-landing.
9. **After a ruling.** `continue` (hour 12) and `continue` (the ask): land T05; its fixes T25 (landed) and T26 (in review).

## T06 - a scattered hamlet seated in single file round its fields (the ranking row `_seat_households#a scattered hamlet's seating`)

### T06 Approach (checklist part A)

1. **The goal, in the world.** A scattered hamlet's farms stand each by its own fields, in one line round the cultivated ground,
   not in ranks behind a front row - where that line can hold every farm.
2. **The constraints.** 0031's drawing rule ("the whole line is hugged to the field edge in single file ... do not squeeze the
   homesteads"); the field's area (0017, 1.3 acres a household); every household seated or the site refused, no farm taken back
   (feature 318); no seed passing at HEAD may fail (XIII); the two arbiter rulings (ask:t06-scattered-single-file,
   ask:t06-single-file-short); carried from T05: the standoff claim, judged on the 6 ft floor only (10 to 13 ft is a drawn
   figure, not a maximum), and the row village's whole-farmstead standoff UNCLAIMED.
3. **Where each comes from.** Single file is 0031's drawing rule, which the page itself calls "a rule about fitting the drawing"
   (O, a convention); "each farm amid its own fields" is 0031's finding (R); the area is 0017's (R); the fallback is the
   arbiter's (G); the farmstead's width with its grove as the line's step is ours (O), the page's "keeps its own spacing".
4. **Do they describe the world here?** Measured 2026-10-18 (`t06-evidence.md`): the margin a hamlet faces holds 3 to 6
   farmsteads at their own width (205-273 ft), against 12 to 20 households; round the paddy alone the north seats fell on the dry
   plots; round the paddy and its dry plots the line holds every farm on 4 of the cohort's 18 dispersed seeds (1, 19, 31, 46),
   1 to 8 short on the other 14. No pool map is dispersed.
5. **The order.** The line is tried before any farm is seated, on a copy, so the fallback seats nothing twice and takes nothing
   back.
6. **The exits.** (e) conform where the line holds; (c) the fallback where it does not (the arbiter's); (a) the field's area is
   researched and stays; (b), (d) n/a.
7. **The search smell.** Two routes measured and taken to the arbiter rather than tuned (step-back hour 13: "has not packed").
8. **The budget.** 2-3 h (the arbiter's estimate); the line round all the cultivated ground was the third measurement.
9. **Done, measured.** One goal: the cohort 54/54 with every dispersed seed seated either in single file (all its households,
   no rank) or as at HEAD (`meta.dispersed_seating` says which); the seeds whose line falls short, seated in ranks, named on a
   found row as 0031's known gap.

### T06 part B (2026-10-18T12:40Z)

Owed by the red-gate rulings red-gate@2026-10-18T12:27:25Z and red-gate@2026-10-18T12:36:36Z and the hour-14 step-back
(hour:385-approach-checklist@14), all `continue`; the step-back's next steps - the gate on the stable tree, this part B, the
landing cohort, the gated landing, then T30's lock - are done in that order but the landing (T30 landed first, the lock).

1. **What is refusing?** Three red gates, three causes, each fixed once: T25's own bundle test named the seating body by its old
   name (`_seat_households`, moved to `_seat_households_as`); the single-file line's two branches had no unit test (the gate rolls
   no dispersed map); and the prompt hook's clone-sync merged main (feature 387's ways refactor) into the clone under the running
   gate, so the tests and the coverage report read two trees. The rerun on the stable tree is green (221 s).
2. **A3 again.** Unchanged: single file is 0031's drawing rule (O), each farm amid its own fields 0031's finding (R), the area
   0017's (R), the fallback the arbiter's (G).
3. **A4 again.** Unchanged; measured again by the cohort, 54/54.
4. **Moving something earlier for something later?** No - the line is tried before any farm is seated.
5. **Tuning or changing?** Neither since part A: the reds were a test's name, a missing test and a merge, not a number.
6. **The one-sentence test.** "A scattered hamlet is seated in single file round its fields where the line holds every farm" -
   true on 4 of the cohort's 18 dispersed seeds, the rest the filed gap.
7. **The next step is a measurement.** The landing cohort (`make cohort-landing`), then the gated push.
8. **Routes measured before asking?** Yes - both asks carried the cohort; this part B's rulings were on the run log.
9. **After a ruling.** `continue` both: rerun the gate (done, green), land T06; the merge-under-a-gate fix is T30 (owed).

### T06 Decisions

**D51 - the line round the cultivated ground, tried first.** For a dispersed hamlet, `_seat_households` seats the margin on a
deep copy of the map in single file (`_seat_households_as(..., single_file=True)`), and seats the real map that way only if the
copy seated every household; otherwise as before. In single file: the site boundary asks the field by containment on every side
(`site_boundary(..., ringed=True)`, the fit test's ring path, its cache keyed on it); seats are offered along every outward chord
of the paddy and its dry plots unioned (`ring_chords`), one farmstead's box apart (its grove in it), with no seat-radius bound
(ours, UNRESEARCHED: it refused 10 of seed 1's 23 ring seats, the far side's, recorded at the point of change);
no ranks, no cloud, no exhaustive pass. `meta.dispersed_seating` records "single file" or "ranks".

**D52 - the gap filed, the research answer proposed.** The dispersed seeds seated in ranks are 0031's known gap, filed as a found
row (status quo, not a DEVIATION); farmsteads carved within the paddy, amid their own holdings (0031's finding), is proposed to
the GM as a feature of its own, which first settles whether 0017's 1.3 acres include the farmstead and whether the farmstead's
205-273 ft is researched (ask:t06-single-file-short).

## T07 - the clearance between a farmhouse wall and a lane's tread, researched (the ranking row `houses.py::HousesMixin._on_a_tread#no building corner on a lane`)

### T07 Approach (checklist part A)

1. **The goal, in the world.** The gap a map keeps between a farmhouse wall and the lane beside it is the one villages kept - or,
   where no source says, it is labeled ours.
2. **The constraints.** The ranking row ("the 4 ft wall-to-tread margin (`TREAD_WALL_FT`) has no source; research the clearance or
   claim it UNRESEARCHED"); the research rules (a search pass before a guess is written; the archive before the web; a citation
   quotes its source verbatim); 0246's "no corner of a house stands on its tread" (R); the pool rolls clean and the cohort keeps
   every seed passing at HEAD (XIII) if the number moves.
3. **Where each comes from.** 4 ft is ours - `TREAD_WALL_FT`'s own claim, "GUESS: 4 ft, on a townhouse's three-shaku eaves strip
   with a margin" (O); "no corner on the tread" is 0246's (R).
4. **Do they describe the world here?** To be measured: the search pass answers whether a farmhouse's eaves line, its drip strip
   or a set-back stood between its wall and a village lane, in China first, Japan as the tiebreaker.
5. **The order.** The search pass first; then the label (or the number and the record) from what it finds.
6. **The exits.** (a) the number is ours and moves to the research if the research gives one; (e) conform the label if it gives
   none; (b), (c), (d) n/a.
7. **The search smell.** One pass; a second only on a lead the first names.
8. **The budget.** 60 min (a pass, then a label or a record edit).
9. **Done, measured.** One goal: `TREAD_WALL_FT`'s claim cites what the pass found, or says UNRESEARCHED with the pass named; the
   ranking row marked with its wave.

### T07 part B (2026-10-18T15:05Z)

Owed by the hour-16 step-back (hour:385-approach-checklist@16, `continue`, ruled 14:49Z); the asks ask:t07-two-findings-at-landing
(`continue`) and ask:t07-span-walkable-cannot-tell (`accept`) ruled on the claims left at landing.

1. **What is refusing?** Nothing on the maps: the pool rolls clean and the cohort holds 54/54 at 3 ft. The claims rounds found the
   joint gap held only the narrower lane's half-width (fixed: the wider), a threshing yard folded into the garden's claim (split,
   UNRESEARCHED), and `_on_a_tread` measuring a footprint's corners and center only, so a footpath could cross a long house 10 ft
   off its center (fixed: each wall measured whole, `poly_seg_dist`; Inashiro re-rolled, pool clean, cohort 54/54). Three findings
   on code T07 did not write the rule of are carried into T43 by the rulings.
2. **A3 again.** Unchanged: 3 ft is 0247's and 0081's drawing page (R); 0246's "nothing built on a lane" (R); the 7 ft corner hold
   ours (GUESS, carried in T43).
3. **A4 again.** Measured: the pass found a Japanese village house set back about 3 ft from a road and a north Chinese drip strip
   of 2-3 chi; the record carries both (0247).
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Changing a number to the research (4 to 3 ft), and fixing a predicate that measured a different
   footprint than the one drawn - neither a tune.
6. **The one-sentence test.** "A lane's tread keeps 3 ft off a farmhouse wall, measured to every wall" - true by the unit tests
   (each red without its rule) and on the pool.
7. **The next step is a measurement.** The gate, then the landing cohort, then the gated push.
8. **Routes measured before asking?** Yes - each ask carried the pool and cohort results; one measurement I gave the arbiter was
   wrong (the far end of a household's own lane does reach `span_walkable`), and the ruling corrected it.
9. **After a ruling.** `continue` / `accept`: land T07 under CLAIMS_OK with T43 carrying the three findings.

### T07 Decisions

**D55 - research, then label.** A `research-pass` agent searches the archive, then the web (Chinese, Japanese, English), for the
clearance between a village house's wall or eaves and a lane: an eaves-drip strip (amaochi / 滴水), a lane's set-back, a building
line. If it finds an attested figure, the record gains it (a page session), `TREAD_WALL_FT` moves to it if the figure differs and
the pool and cohort are rolled; if it finds none, the claim reads UNRESEARCHED naming the pass, and the 4 ft stays.

## T15 - a cohort rolled over an uncommitted engine diff says so (found by T04)

### T15 Approach (checklist part A)

1. **The goal, in the world.** A cohort record says what was rolled: a roll over an uncommitted engine diff is never read as its
   commit's baseline, so FIXED / NEWLY FAILING stays true.
2. **The constraints.** The records are append-only once committed; a test red without the rule; tooling only.
3. **Where each comes from.** The baseline rule is ours (O, feature 385 T03's tooling fix); "No known regressions" (G, XIII).
4. **Do they describe the world here?** Yes - T04's patched record named HEAD's commit and nothing else.
5. **The order.** The stamp before the record is committed, then the readers skip it.
6. **The exits.** (c) - the record carries the diff's digest; (e) n/a.
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: `tests/tooling/test_cohort_known.py` and `test_approach_gate.py` red without the stamp or the skip.

### T15 Decisions

**D36 - the stamp and the skip.** The patched record names HEAD's commit and nothing else, so
it read as a second baseline of HEAD's engine. `make cohort` now runs `cohort_known.py --stamp` before committing the record: when
`git diff HEAD -- l7r pool` is not empty, the newest record gains `engine_diff` (the diff's digest), and `cohort_known.baselines`
and `approach_gate.newly_failing` skip any record carrying it. Tooling only (`scripts/`, the Makefile, tests). The record already
committed without the stamp stays as written (append-only); it passes every seed, as HEAD's does, and stops counting once
main's engine moves.

## T16 - a plan review's third round on one task waits for the round arbiter (the round arbiter's fix on hour:385-approach-checklist@9)

### T16 Approach (checklist part A)

1. **The goal, in the world.** A plan review past CLAUDE.md's tripwire ("a check's third round on one subject") is refused by
   the guard, not held back by the session remembering the rule (T14's fourth round was).
2. **The constraints.** CLAUDE.md's tripwire (G, 375); every refusal names its compliant step; `ARBITER_OK` with a reason the
   escape, as for a spec review's cap; a test red without it.
3. **Where each comes from.** The cap is the GM's (G, 375's tripwires); counting per task is the arbiter's ruling (hour 9).
4. **Do they describe the world here?** Yes - T13 and T14 ran three and four plan rounds.
5. **The order.** The count, then the refusal, then the escape.
6. **The exits.** (c) - count per task from `plan-review.json`'s block reviews; (e) n/a.
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: `tests/tooling/test_plan_round_cap.py` red without the cap; `make hooks-test` green.

### T16 Decisions

**D37 - a task's plan rounds, counted back to its CLEAR.** On a MODE 4 dispatch the review-round guard
(`hm_review_round.plan_cap_refusal`) counts the active task's rounds: the newest entries of `plan-review.json`'s block reviews
naming one of its blocks (`## Txx` / `### Txx`), back to one CLEAR. The dispatch that would be round 3 trips
`round:spec-fidelity|plan:<feature>#<task>@3` and is refused with the arbiter's step; each `continue` ruling lifts the cap by one
round; `ARBITER_OK="<reason>"` passes it, recorded.

## T17 - the make-targets page checked on every route (amendment 5, FR-017)

### T17 Approach (checklist part A)

1. **The goal, in the world.** A Makefile change that leaves `docs/make-targets.html` stale is refused at the push it arrives in, not a task later.
2. **The constraints.** FR-017 (G, amendment 5); the push checks run in one process (`push_checks.py`, feature 383); every refusal names its compliant command; a test red without it; tooling only.
3. **Where each comes from.** FR-017 is the GM's (G); the check is the gate's own `test_make_docs`, moved earlier (O).
4. **Do they describe the world here?** Yes - each is one of T04's four landing refusals (its phase table, 02:51-02:57).
5. **The order.** The check added to `push_checks.CHECKS`, then its test.
6. **The exits.** (c) - the push runs the gate's check. (a), (b), (d) n/a; (e) n/a.
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: a push with a stale page refused, naming `make docs`; a test red without the entry.

### T17 Decisions

**D38 - `make-docs` in the push checks.** `push_checks.CHECKS` gains `("make-docs", "make-docs.py", ("--check",), ...)`, its refusal
naming `make docs` and a commit; it runs from the clone's root on both routes, as every other entry does.

## T18 - an arbiter's fix landed, settled and its task ticked in one command (amendment 5, FR-018)

### T18 Approach (checklist part A)

1. **The goal, in the world.** Closing a task whose arbiter fix is tooling is one command: the files land with their test, the fix settles, the task is ticked.
2. **The constraints.** FR-018 (G); `make land-tooling`'s own checks unchanged; the fix's test must be on main before it settles (feature 379); every refusal names its compliant command; a test red without it; tooling only.
3. **Where each comes from.** FR-018 is the GM's (G); the order land-then-settle is feature 379's (G).
4. **Do they describe the world here?** Yes - each is one of T04's four landing refusals (its phase table, 02:51-02:57).
5. **The order.** `LAND=` and `TICK=` in the recipe, then the refusal texts.
6. **The exits.** (c) - the one command runs the three steps in order, each only after the one before succeeds. (a), (b), (d) n/a; (e) n/a.
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: `make arbiter-fix-done ... LAND="<files>" F=<n> TICK=<Txx>` lands, settles and ticks, in that
   order; `TICK=` without `F=` is refused naming it; the refusal for a test not on main and `make tick`'s open-fix refusal both
   name the full form - each with a test red without it (`tests/tooling/test_arbiter_fix.py`).

### T18 Decisions

**D39 - `LAND=` and `TICK=`: the three steps, one command.** `make arbiter-fix-done ID= NOTE= TEST= LAND="<the fix's files>" F=<n>
TICK=<Txx>` runs `scripts/land-tooling.sh` on the files and the test, settles the fix only when they land, then runs `make tick` on
the task with the same NOTE - each step only after the one before succeeds, so the order cannot be got wrong; `TICK=` without
`F=` is refused naming it; without `LAND=` or `TICK=` the command behaves as today. The refusal for a test not on main
(`hm_arbiter.settle_fix`) and `make tick`'s open-fix refusal name the full form (spec-fidelity, amendment 5 round 1: the GM's
"One command could do all three").

## T19 - a ledger row written from the record (amendment 5, FR-019)

### T19 Approach (checklist part A)

1. **The goal, in the world.** An owed ledger row is written by one command from the agent's own reply, not typed.
2. **The constraints.** FR-019 (G); the row's cost cells stay `make review-cost`'s (feature 371); what the push refuses is unchanged; every refusal names its compliant command; a test red without it; tooling only.
3. **Where each comes from.** FR-019 is the GM's (G); `ledger_owed.filled_row` already writes rows for page sessions (feature 371).
4. **Do they describe the world here?** Yes - each is one of T04's four landing refusals (its phase table, 02:51-02:57).
5. **The order.** `WRITE=` on the make target, then the refusal texts.
6. **The exits.** (c) - the page sessions' command, offered to every session. (a), (b), (d) n/a; (e) n/a.
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: the refusal names `make ledger-owed WRITE=`; the target writes the rows; a test red without each.

### T19 Decisions

**D40 - `make ledger-owed WRITE=`.** The target passes `WRITE="<where the session recorded what it did>"` to `ledger_owed.py
--write`, which appends each owed row filled from the agent's reply (its verdict, its first line, `nothing` when clean); the push
check's refusal and the hook's notice name that command in place of "add the row printed, its ?s filled". A row the session
wants to word itself can still be added by hand.

## T20 - the hour decided once per message (the round arbiter's fix on hour:385-approach-checklist@10)

### T20 Approach (checklist part A)

1. **The goal, in the world.** A message's dispatches are admitted or refused together at the hour, and the step-back sees the
   hour guard's own refusals.
2. **The constraints.** The hourly step-back (G, 383); every refusal names its step; a test red without each; tooling only.
3. **Where each comes from.** The step-back is the GM's (G); the 5 s window is ours (O, the batching hook's same-turn window,
   widened).
4. **Do they describe the world here?** Yes - T05's five dispatches in one message were split two and three.
5. **The order.** The admission mark, then the refusal list.
6. **The exits.** (c) - an admitted dispatch admits its message's others. (a), (b), (d) n/a; (e) n/a.
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: `tests/tooling/test_checkpoint.py` red without the window or the `refused` read.

### T20 Decisions

**D42 - one decision per message.** `checkpoint.due` marks each admitted dispatch's time (`<git dir>/checkpoint-admitted`); past
the hour, a dispatch within `SAME_MESSAGE_S` (5 s) of an admitted one is admitted - the rest of the message it began. A gate is
never admitted by the window. `stepback_bundle.refusals` reads `refused` as well as `blocked`, the pair guard's own word.

## T21 - a batch reply's own EDITs settle its units (the round arbiter's fix on ask:t05-lane-popup-round3)

### T21 Approach (checklist part A)

1. **The goal, in the world.** A check's own verbatim fix, applied, owes no round that reads the check's words back.
2. **The constraints.** The round settling `apply-edits` already does (feature 335's arbiter, 375 amendment 3); a unit whose diff departs
   from the round's EDIT stays owed; every refusal names its step; a test red without it; tooling only.
3. **Where each comes from.** The settling is the arbiter's rule (G, 335/375); the batch's counts-line read is ours (O).
4. **Do they describe the world here?** Yes - measured on T05 (2026-10-18): the settling exists, but the session applied page 0196's
   EDITs from a hand-made file with no counts line, and the pop-ups' by hand; and a batch reply (FR-009) opens with prose, so even
   `apply-edits` on it named no check. Both round-2 page checks and one pop-up round followed.
5. **The order.** The batch read first, then the tip in `make record-owed`'s footer.
6. **The exits.** (c) - the existing settling reaches batch replies; (e) n/a.
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: `tests/tooling/test_apply_edits.py` red without the batch read; the footer names `make apply-edits
   FROM=<reply or transcript>`.

### T21 Decisions

**D43 - the batch read and the tip.** `record_owed.reply_checks` names a reply's check from its first line, else from the first
counts line of a known check anywhere in it (`modal-depiction: <unit> - COVERAGE ...`), so `make apply-edits FROM=<a batch's reply
or transcript>` settles each unit its own EDITs alone moved. An EDIT already applied by hand settles too, through the same command (spec-fidelity, T21
round 1: the arbiter's test is the diff matching the EDIT line for line, however it got there): a block whose new text stands
once in its file and whose old text is gone is put back to its old text, so the settling sees the round's own blocks move the
unit, and is re-applied - the file ends as it was. A hand edit that departs from the EDIT, or one with no reply to read, still
re-owes its unit. `make record-owed`'s footer names the command for both.

## T22 - a refused dispatch is not lost (the round arbiter's fix on hour:385-approach-checklist@11)

### T22 Approach (checklist part A)

1. **The goal, in the world.** A check the session meant to run is never silently left unrun: a dispatch a guard refused is sent
   again or recorded as dropped before the session ends a turn.
2. **The constraints.** The arbiter's ruling on hour:385-approach-checklist@11 (two changes); a guard matches invocations, its
   message names the compliant command, its escape carries a reason of two words, every firing logged (root CLAUDE.md); a
   test red without each; tooling only.
3. **Where each comes from.** The two changes are the arbiter's (G, feature 379 stands it where the GM was asked); the matching
   rule below (same agent type and same bundle) is ours (O).
4. **Do they describe the world here?** Yes - measured on T05 (2026-10-18, the session transcript): of seven agents sent at 03:57
   four were refused by the decide-first guard with identical lines naming no check; three were re-sent at 04:02, impl-drift round
   2 was not, and the session ended its turn "waiting on" it; about 5 h passed idle.
5. **The order.** The refusal's text first (it names the check and its bundle), then the Stop layer.
6. **The exits.** (c) - one Stop guard; (a), (b), (d), (e) n/a.
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: a turn whose refused dispatch was neither re-sent nor recorded cannot end, shown by a hook test
   red without the Stop layer; the decide-first refusal names the agent type and bundle, shown by a test red without it.

### T22 Approach (re-answered 2026-10-18T09:33Z)

1. **The goal, in the world.** Unchanged: a check the session meant to run is never silently left unrun.
2. **The constraints.** Unchanged, plus round 2's: the window is the arbiter's "since the last turn end", read literally.
3. **Where each comes from.** The window's start is the arbiter's (G); reading turn ends from the transcript's `turn_duration`
   entries is ours (O), measured on three transcripts (spec-fidelity, round 2).
4. **Do they describe the world here?** Yes - measured on d2dc8c63: the last turn end before the incident at 03:50:51, the
   GM's prompt queued at 03:57:47 into the running turn, the four refusals 03:57:57-03:58:06, the turn's end at 03:59:25. A
   window from that prompt starts after the refusals; one from the last turn end holds them.
5. **The order.** Unchanged.
6. **The exits.** (c), unchanged.
7. **The search smell.** None; round 2 is the first change of the window, no tuning loop.
8. **The budget.** 40 min, unchanged; 35 spent at round 2.
9. **Done, measured.** Unchanged, plus: the hook test holds a refusal taken after a mid-turn prompt, and one in a session
   with no turn ended yet.

### T22 Decisions

**D44 - the refused dispatch held at the turn's end.** `pair-hooks.sh stop` (a no-op since feature 383) reads the session's
transcript from its last turn end (the harness's `system`/`turn_duration` entry, written only for a turn that ended), or
from the session's start when none has, and lists each Agent call a hook refused (its result the harness's
`PreToolUse:Agent hook error`, whatever the hook's wording). Never from the GM's last prompt: measured, the incident's
refusals (03:57:57-03:58:06) came after a prompt queued at 03:57:47 and taken into the running turn, so that window would
have missed them; a turn end this guard blocks writes no `turn_duration`, so a refusal stays in the window until answered.
No state file: the transcript is the record of turn ends. A refusal is answered when a later Agent call of the same
`subagent_type` naming the same bundle (the first `/tmp/l7r-check/...` path in its prompt; the description when the prompt names
none) was not refused, or when `make dispatch-dropped TYPE=<agent type> BUNDLE=<path> WHY="<reason>"` recorded it dropped in
`<gitdir>/dropped-dispatches.jsonl`. While one is unanswered the turn's end is blocked, every time, naming each refused check
with both commands - always satisfiable, so no once-only valve. The check-bundle and pair hooks' decide-first refusals name the
check (`<agent type> on <bundle>`) instead of "dispatch".

## T23 - a relabel answers its MISLABELED at the gate too (found by T05)

### T23 Approach (checklist part A)

1. **The goal, in the world.** A claim relabeled as its MISLABELED verdict prescribed is answered: not re-owed (as today) and not
   refused at the claims gate.
2. **The constraints.** `relabeled_only` (feature 374): a relabel after MISLABELED, the unit's body unchanged, owes no new round;
   the gate's three classes (FR-010, FR-013) otherwise unchanged; a test red without it; tooling only.
3. **Where each comes from.** The owed side's rule is feature 374's (G); applying it at the gate is ours (O), its other half.
4. **Do they describe the world here?** Yes - measured on T05 (2026-10-18): three claims relabeled from round 2's MISLABELED
   (`stage_homesteads#the declared cluster shape`, `WELL_SEAT_FT` and `seat_wells`'s `seated a little closer than the check`)
   were not re-owed by `make claims-owed`, yet `claims.py gate` refused all three as introduced MISLABELED - no command clears them.
5. **The order.** The gate's skip, then its test.
6. **The exits.** (c) - one rule shared by both sides; (a), (b), (d), (e) n/a.
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: the gate passes a MISLABELED whose claim text changed since the verdict with the unit's body
   unchanged, and still refuses one whose text did not change; a test red without the skip.

### T23 Decisions

**D45 - the gate reads `relabeled_only`'s answer.** `claims.classify` skips a MISLABELED finding whose current claim text differs
from the text its verdict was recorded against (`claim` in the index row) while the unit's body is the one judged (`body`) - the
relabel that verdict prescribed, as `relabeled_only` already rules for `owed`. A relabel with the body moved stays owed and is
judged again; a MISLABELED with its text unchanged is refused as before.

## T24 - a tooling landing merges main in first (found landing T21, T22 and T23)

### T24 Approach (checklist part A)

1. **The goal, in the world.** `make land-tooling` lands on the first try whenever the clone's files merge with main: it is never
   refused only because main moved since the clone last merged it.
2. **The constraints.** Feature 379's route unchanged: a new commit on the latest main, built in a detached worktree, every push
   check run; never rewrite history; a real conflict still refuses, naming the files; a test red without it; tooling only.
3. **Where each comes from.** The route is feature 379's (G); merging main in first is the step its refusal already tells the
   session to take by hand (`sync-in`, then run this again) - ours to automate (O).
4. **Do they describe the world here?** Yes - measured on 2026-10-18 (this session's logs `land-t21`, `land-t22`, `land-t23`):
   three of three landings were first refused "FILES do not apply cleanly onto the latest main" (the ledger and the make-targets
   page moved on main), and each landed unchanged after a `sync-in` - about 2 min and two commands each.
5. **The order.** The merge before the patch is built, then the test.
6. **The exits.** (c) - the refusal's own remedy, run by the script; (a), (b), (d), (e) n/a.
7. **The search smell.** None.
8. **The budget.** 25 min.
9. **Done, measured.** One goal: a clone whose patch went stale on main lands its tooling in one `make land-tooling`; a
   conflicting merge still refuses and is aborted; `tests/hooks/test-land-tooling.sh` red without the merge.

### T24 Approach (re-answered 2026-10-18T09:52Z)

1. **The goal, in the world.** Unchanged: a tooling landing never refused only because main moved.
2. **The constraints.** Unchanged, plus round 2's: the clone's history is left as it was when the patch applies.
3. **Where each comes from.** Unchanged; merging only on a failed apply is ours (O), the route's own rule kept (G, feature 379).
4. **Do they describe the world here?** Yes - its first use (T26's landing, 2026-10-18) met a real conflict, main's comment strip
   of the Makefile, and refused with the merge aborted, as designed.
5. **The order.** Unchanged.
6. **The exits.** (c), unchanged.
7. **The search smell.** None.
8. **The budget.** 25 min; about 20 spent.
9. **Done, measured.** Unchanged: `tests/hooks/test-land-tooling.sh` case 3c (a stale base lands) and case 3 (a conflict refuses,
   the merge aborted), red without the merge.

### T24 Decisions

**D46 - main merged in when the patch no longer applies.** When FILES' patch fails to apply onto the latest main,
`land-tooling.sh` merges `origin/main` into the clone (`git merge --no-edit`: a merge commit, never a rebase), takes the merge
base and the patch again, and applies it once more. Only then, not whenever the clone is behind: a patch that applies needs no
merge, and the route's own rule (feature 379) is that the clone's history is left as it was - its test "the clone's history is
untouched" stands. `sync-in` itself is not run: its mirror refresh and render steps are not the merge's, and a plain merge is
what its refusal named. A merge that conflicts is aborted (the clone left as it was) and refuses, naming `sync-in` to resolve
by hand; a second failed apply refuses as today; FILES uncommitted still refuse before anything runs.

## T25 - a claims bundle carries what the unit's code reads from other modules (the round arbiter's fix on ask:t05-old-drifts-at-landing)

### T25 Approach (checklist part A)

1. **The goal, in the world.** impl-drift judges a claim on the first round whenever the code it turns on is in the repository:
   no CANNOT-TELL only because the bundle left out a function or constant the unit reads.
2. **The constraints.** `callees` (the arbiter's fix on ask:t03-claims-at-landing): the unit's own module's functions, at most
   `CALLEES_MAX`; a bundle stays a bundle (copied out, read once); a test red without it; tooling only.
3. **Where each comes from.** `callees` is the arbiter's (G); so is this fix (G, ask:t05-old-drifts-at-landing: "inlines a judged
   unit's direct callees and every module-level constant they read (transitively one level) whenever a claim's label names a
   distance, gap or standoff"); doing it for every claim, not only those labels, is ours (O) - a CANNOT-TELL for want of a callee
   is not a distance claim's alone (T03's `_clear_link` was a link test).
4. **Do they describe the world here?** Yes - measured on T05 (2026-10-18): the standoff claim on `_seat_households` came back
   CANNOT-TELL three rounds running, each for the next layer - `front_row` and `turn_the_seat` (imported from sibling modules), then
   `_front_row_from_chains` and `install_site_boundary`, then `HOUSE_PADDY_GAP_FT` and `STANDOFF_SLACK_PX` (module constants) -
   three dispatches, about 8 min of agent time (their ledger rows' wall times, 122 s, 272 s and 83 s), and a tripwire.
5. **The order.** The measurement, then (a), (b) and (c), then the tests.
6. **The exits.** (c); (a) n/a - the arbiter's level is uncapped; (b), (d), (e) n/a.
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: the standoff claim's FIRST bundle (no CANNOT-TELL before it, no `WITH=`) carries `front_row`,
   `turn_the_seat`, `_front_row_from_chains`, `install_site_boundary`, `STANDOFF_SLACK_PX` and `HOUSE_PADDY_GAP_FT`
   (`m:t25-bundle`: 154 KB, 118 entries, each once); a test red without each of (a), (b) and (c).

### T25 Decisions

**D47 - a distance claim's first bundle reaches the call that reads its constant.** Measured (2026-10-18, `m:t25-bundle` -
`make claims-bundle UNITS=<the standoff key>` on `_seat_households`, its size and its CONTEXT headings): one level of direct
callees is 29 (48 KB of source) and misses `HOUSE_PADDY_GAP_FT`, read two calls down (`front_row` -> `_front_row_from_chains` ->
it); two levels, with the constants read there, is a 154 KB bundle of 118 context entries that carries every name the standoff's
three CANNOT-TELL rounds asked for. No bundle size limit is set (T05's 44-claim round-2 bundle was 232 KB - measured 2026-10-18,
`ls -l` on its MANIFEST.md), so (a) goes two levels.
In `scripts/record/claims_context.py` (`claims.py` is at 982 of its 1,000 lines):
- **(a) the arbiter's fix, reaching its purpose** - for a claim whose label names a distance, gap or standoff (`DISTANCE`:
  distance, gap, standoff, apart, reach, clear of, off the, ft, feet), the bundle carries every engine function the unit calls,
  its own module's and imported, and theirs - two calls down - with every module constant any of them reads, UNCAPPED (`direct`;
  round 1: a cap drops what "every" names; round 2: one level stops short of the standoff's constant).
- **(b) every claim's first bundle** carries, beside its own module's callees (at most `CALLEES_MAX`, 6, as before), every module
  constant the unit reads, imported ones too (`callees`) - ours (O), for claims the label trigger misses (T03's `_clear_link`).
- **(c) a re-bundle of a claim last judged CANNOT-TELL** carries each engine name its note puts in backticks - resolved through the
  unit's imports, else by its module-level definition anywhere under `l7r/` (at most three) - and, breadth first through each
  function found, the functions and constants it calls or reads, within `CHASE_CHARS` (30,000) (`chase`) - ours (O), for what a
  check still names past (a)'s two levels or (b).
A name from outside `l7r/` is never followed (LEGITIMATE, rounds 1 and 2). Nothing in (a) is capped; (c)'s budget bounds only its
own chase. Each context entry appears once.

## T26 - a review never reads an absent or stale render (the round arbiter's fix on hour:385-approach-checklist@12)

### T26 Approach (checklist part A)

1. **The goal, in the world.** A glyph or settlement check judges the map as its manifest stands: its render is there, and newer
   than what it renders.
2. **The constraints.** The arbiter's fix (render first, or refuse naming `make map GEN=...`); one map rendered by `make map`, the
   one command that renders; the snapshot and its prompts unchanged otherwise; a test red without it; tooling only.
3. **Where each comes from.** The fix is the arbiter's (G); rendering rather than refusing is the first of its two options (G);
   newer-than read by file times is ours (O).
4. **Do they describe the world here?** Yes - measured on T05 (2026-10-18, 10:17): `make maps SCOPE=all` regenerated the pool
   without renders (the `.png` and `.html` are untracked and the roll cache evicts them), so `make verify` wrote three glyph
   prompts noting "missing in the clone: .png .html"; a render pass and a second verify followed, about 4 min (the
   session transcript's timestamps, 10:17 to 10:21).
5. **The order.** The staleness test, then verify's loop, then the test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 25 min.
9. **Done, measured.** One goal: `review_snapshot.py --stale-renders` names each owed map whose `.png` or `.html` is missing or
   older than its `.gen.py` or `.json`, `make verify` runs `make map` on each before the snapshot, and a test is red without it.

### T26 Decisions

**D48 - render, then snapshot.** `review_snapshot.stale_renders(root, units)` returns the generator of each owed unit's map whose
`.png` or `.html` is missing or older than the map's `.gen.py` or `.json` (the `.json` is what a pool roll writes per map, beside
the tracked `.gen.py`, `.svg` and `.notes.md`); `--stale-renders` prints them; `make verify` runs `$(MAKE) map GEN=<each>` before
it takes the snapshot and writes the prompts. Every unit is asked (round 1: "every unit"): an entry with no generator - none in
the pool, measured 2026-10-18 (every `pool/*/*/` and `legacy-hand-authored-pool/*/*/` directory holds its `.gen.py`) - whose
`.png` is missing is listed as `sheet:<its .svg>`, and `make verify` refuses it, naming `make sheet-render SHEET=<svg> OUT=<png>`,
the arbiter's second option.

## T27 - the heading the tool asks for passes its own check (found ticking T05 and T22)

### T27 Approach (checklist part A)

1. **The goal, in the world.** A task given an owed Approach or part B block, headed as the refusal says, ticks.
2. **The constraints.** D9 (feature 385): an owed part is answered by a block stamped at or after its trigger; the stamp format
   `owe` prints; a test red without it; tooling only.
3. **Where each comes from.** D9 is ours (O, plan D9); comparing to the minute is ours (O).
4. **Do they describe the world here?** Yes - measured 2026-10-18 at 11:05: `make tick` refused T05 ("hour:385-approach-checklist@12
   at 2026-10-18T10:25:14Z ... no block stamped after it") with `### T05 part B (2026-10-18T10:25Z)` in place - the heading `owe`
   printed, to the minute - and T22 the same at 09:33:15Z against `09:33Z`.
5. **The order.** The comparison, then the test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 10 min.
9. **Done, measured.** One goal: a block headed as `owe` prints passes `make tick`; a test red without it.

### T27 Decisions

**D49 - to the minute.** `approach_gate.refusal` compares an owed row's time truncated to the minute, the precision `owe` prints in
the heading it asks for; a block stamped a minute earlier still refuses.

## T28 - an ask's bundle shows which numbers are researched (the round arbiter's fix on ask:t06-scattered-single-file)

### T28 Approach (checklist part A)

1. **The goal, in the world.** The round arbiter rules on an ask knowing, from its bundle alone, which numbers the question turns
   on are researched and which are ours.
2. **The constraints.** The arbiter's fix ("copies into the bundle the claim rows (source class: research, GM ruling, ours,
   convention) for every number its evidence file names"); the bundle read without the repository; a test red without it.
3. **Where each comes from.** The fix is the arbiter's (G); naming a number by its constant or a backticked identifier is ours (O).
4. **Do they describe the world here?** Yes - measured on T06 (2026-10-18): the ask named the dispersed field's size and the
   farmstead pitch, the ruling turned on whether the field's size was researched, and the bundle carried only the session's
   evidence; the claims say `GROSS_ACRES_PER_HOUSEHOLD` rests on 0017 (IN-STEP). The "farmstead pitch" of 205-273 ft is not
   `BUNDLE_PITCH` (the nucleated row pitch, 100 ft, on 0038): it is a scattered farmstead's own box, house, yard, garden and grove
   bands together, read off its geometry (`_g0["bbox"]`) - each part claimed on its own, the sum stated by no claim (measured
   2026-10-18: `make claims-report` holds no line with "273 ft" or "205 ft").
5. **The order.** The section, then the test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: the ruled ask's own words (ask:t06-scattered-single-file: "the field's size, is researched
   (0017's 1.3 acres a household)", the pitch "273 ft") give `GROSS_ACRES_PER_HOUSEHOLD`'s claim, class and last verdict beside
   "1.3 acres", and "no claim states it" beside "273 ft"; a test red without it.

### T28 Decisions

**D50 - the claims on what an ask names.** `arbiter_bundle.claims_section` reads every ALL_CAPS constant and backticked
identifier in the ask's question and its evidence files, and lists each research claim on a unit of that name: its key, its
class (a research page, GUESS, UNRESEARCHED, CONVENTION, DEVIATION, CANON, NONE - the registry's own `CLASSES`; a number the GM
set carries CANON, his setting's canon, or DEVIATION, a departure he ruled, as its claim records it) with the claim line, and its
last verdict. And every number with a unit the words give ("1.3 acres", "273 ft") is looked up by its VALUE: the claims whose line
states that value and unit are listed beside it, and a value no claim states is said to be one ("a measurement, or a value
derived from others") - so no number reaches the arbiter without its claim row or the word that it has none (rounds 1 and 2).

## T29 - each plan review its own bundle (the round arbiter's fix on hour:385-approach-checklist@13)

### T29 Approach (checklist part A)

1. **The goal, in the world.** A second plan review can be built and sent while another is still reading its bundle.
2. **The constraints.** The arbiter's fix ("writes each plan review's bundle to a path keyed by its tasks"); the bundle's contents
   unchanged; a test red without it; tooling only.
3. **Where each comes from.** The fix is the arbiter's (G); adding the blocks' digest to the key is ours (O), so two rounds on the
   same task's blocks never share a directory either.
4. **Do they describe the world here?** Yes - measured on 2026-10-18 (hour 13's bundle): T26's review waited on T25's twice, and
   one round's verdict was refused because the shared `plan-385-approach-checklist-blocks` changed under it.
5. **The order.** The path, then the test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: two `make plan-delta` runs on different blocks write two bundles, the first left whole; a test
   red without it.

### T29 Decisions

**D53 - the bundle's directory names its tasks and its blocks.** `plan_bundle.delta_prompt` writes to
`/tmp/l7r-check/plan-<feature>-blocks-<the tasks its block headings name, or "plan">-<the first 8 of the blocks' digest>`; the
dispatch it prints names that MANIFEST, as before. The decision preflight (`make decide`, keyed by its one task) is unchanged.

## T30 - nothing merged under a running gate (the round arbiter's fix on red-gate@2026-10-18T12:36:36Z)

### T30 Approach (checklist part A)

1. **The goal, in the world.** A gate's verdict belongs to one tree: nothing is merged into a clone while its gate runs.
2. **The constraints.** The arbiter's fix (clone-sync checks a gate-in-progress lock `make done` writes; while it is held the merge
   waits, never runs; a test holds the lock and asserts HEAD and the tree unchanged); FR-010 (no write to a tree while its gate
   runs); feature 212's fast-forward kept for a clone with no gate; a test red without each; tooling only.
3. **Where each comes from.** The fix is the arbiter's (G). The lock exists: `make done` acquires `<git dir>/gate.lock` with its
   own pid at its first line (`gate_lock.py`, feature 375's follow-up), a dead owner holding nothing - so the fix asks it (G).
   Fixing the test that set the merge off is ours (O), and constitution XIV's.
4. **Do they describe the world here?** Measured 2026-10-18 (the clone's reflog, `.git/land-tooling-steps.jsonl`, the guard log):
   main was merged in at 08:21:02 and 08:35:10 local, each under a running gate; the guard log holds no clone-sync `synced-in`
   for this clone then, and land-tooling's run log holds two runs in THIS clone inside each gate (12:26, 12:35, 12:44 UTC), each
   ending `push-exit-1`. The cause: `tests/tooling/test_arbiter_fix.py` ran `make -n -C <the real repository> arbiter-fix-done
   LAND=... F=385 TICK=T18`; a `-n` recipe line holding `$(MAKE)` is executed, and that line also runs `land-tooling.sh` - so
   every gate ran a real land-tooling in the clone it tested, and since T24 a stale patch there merged main in. After the fix,
   all 1,924 tooling tests run with no land-tooling run and HEAD unchanged.
5. **The order.** The test first (the cause), then the lock asked by clone-sync on both paths and by land-tooling, then the tests.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: no merge into a clone under its gate - the tooling suite runs no land-tooling; with a live gate's
   lock the prompt path skips the merge (HEAD unchanged), the tool-call path merges and refuses nothing, and land-tooling refuses
   a stale patch with nothing merged; each test red without it.

### T30 Decisions

**D54 - the cause removed, and the gate's lock asked before any merge.** (a) `test_arbiter_fix.py` reads the `arbiter-fix-done`
recipe's text for the land-settle-tick order instead of running `make -n` on it in the real repository. (b) `gate_lock.py held
<git dir>` (exit 0 while a live `make done` owns the clone); clone-sync's prompt path counts a held lock as mid-task, as it counts
uncommitted work and a live make (feature 310); its tool-call path (feature 212's fast-forward) asks both the lock and the live
make and, while either holds, merges nothing and refuses nothing, telling the session the merge waits; `land-tooling.sh` refuses
to merge main under a held lock. A dead owner holds nothing, so no stale lock is ever cleared by hand.

## T41 - a refused dispatch is no round (the round arbiter's fix on round:source-reader|q:0081@3)

### T41 Approach (checklist part A)

1. **The goal, in the world.** A record check's round cap counts readings, not attempts: a dispatch a hook refused before any
   agent started uses no round.
2. **The constraints.** The arbiter's fix ("count only dispatches that started an agent and kept a reply, and not those the pair
   hook refused ... with a test where a refused dispatch leaves the count unchanged"); feature 375's cap of two rounds per subject;
   `hm_checks.dispatch` runs as the check-bundle hook, before the pair hook decides; a test red without it; tooling only.
3. **Where each comes from.** The fix is the arbiter's (G), and counting at the reply is its own wording ("started an agent and
   kept a reply") made the moment of counting (round 1: a count refunded on a timer narrowed it).
4. **Do they describe the world here?** Yes - measured on T07's write session (2026-10-18, the ruling on q:0081@3): the two
   source-reader dispatches the pair hook refused for its step-back were counted as rounds 1 and 2, and the cap fired on zero
   readings.
5. **The order.** The count moved to the reply, then its test and the tests that counted by dispatch.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: a refused dispatch and a dispatch whose agent kept no reply leave the count unchanged, and a
   reading counts once; `tests/tooling/test_hm_checks.py` red without it.

### T41 Decisions

**D56 - a round counted when it is read.** `hm_checks.dispatch` no longer counts a round: it records on the dispatch the units it
would count (`counted`, after the same batch, fresh-reading and first-look tests as before), and `returned` - the agent's
SubagentStop, or a foreground check's PostToolUse - counts them once (`rounded`) when the agent comes back with a non-empty reply.
So a dispatch a later hook refused (it never launches) and one whose agent kept no reply leave the count unchanged, as the fix
says ("count only dispatches that started an agent and kept a reply"); no timer. The cap is still asked at dispatch against the
rounds read so far, and a re-dispatch into a round still running is refused as before (FR-003c), so no round in flight is
double-booked. The tests that counted a round by dispatch alone now read each round (`_read`: launched, then returned with a reply).

## T42 - an absence note owes no source-reader (the round arbiter's fix on round:source-reader|q:0081@5)

### T42 Approach (checklist part A)

1. **The goal, in the world.** A source-reader round is owed only where there is a page to read.
2. **The constraints.** The arbiter's fix (three parts: "stop owing a source-reader round when a 'no publicly readable source'
   (absence) note's wording changes, since there is no page to read; take a READ on the sibling note it defers to as settling it,
   and net out of the owed list any note that the latest returned round READ with no edit since"); the record's other checks on an
   absence note unchanged (its quote-check, the page's record-format); a test red without it; tooling only.
3. **Where each comes from.** The fix is the arbiter's (G).
4. **Do they describe the world here?** Yes - measured on T07's check session (2026-10-18, the ruling on q:0081@5): the round-6
   source-reader came back 9 READ, 0 CONTRADICTED, yet five notes stood owed - two absence notes re-worded to defer to the
   2.2-chi figure, and three notes round 6 had READ with no edit since.
5. **The order.** The absence rule, then its tests.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: no source-reader unit is owed on an absence note, new or changed; a note READ at its current words
   is not owed; `tests/tooling/test_record_owed.py` red without it.

### T42 Decisions

**D57 - the three parts.** (a) `record_units.owed` owes no `source-reader` unit on a note whose words carry "no publicly readable
source" (`ABSENCE`), new or changed; its quote-check and the page's record-format are owed as before. (b) What such a note defers
to is its sibling notes' own reading - each is owed and read on its own words, so a READ on the sibling settles the absence note's
content with no unit of its own. (c) A note the latest returned round READ, unchanged since, is answered at its fingerprint (the
existing `answered` rule, `record_owed.py`). Measured 2026-10-18 on HEAD (`.git/record-checks/`, then `make record-owed
UNANSWERED=1`): the three notes the ruling found owed - 0081.drawing#wang-2021-qing-huabei-dishui-2, 0247#...-6 and -7 - each carry
round 6's own answer ("9 READ, 0 CONTRADICTED", recorded 14:17:55Z) at its current fingerprint, and none is unanswered: they stood
owed in the ruling's bundle only because round 6's answers were not yet recorded when it was built. So the netting is the existing
rule; `test_a_note_read_at_its_words_is_netted_and_an_absence_note_owes_no_reading` reproduces the q:0081 case (a READ note
netted, a re-worded absence note owing no reading - red without (a)).

### T44 Approach (checklist part A)

1. **The goal, in the world.** The hourly step-back's arbiter reads what every session working the feature said and did in the
   hour.
2. **The constraints.** The arbiter's fix: "make step-back's words.md should take the words from every session transcript of the
   feature that was active in the hour, keeping the newest ... and should list any transcript it left out or cut"; the replay flags
   (`--transcript`, SC-008) unchanged; tooling only; a test red without it.
3. **Where each comes from.** The fix is the arbiter's (G).
4. **Do they describe the world here?** Yes - measured on hour:385-approach-checklist@16 (13:47-14:47Z): the feature's event log
   has three sessions in the window - the T07 page session's check run (439 events, from 14:03), this session (322) and the write
   run (169, from 13:47). `session_of` took the busiest, so `words.md` held the check run's words (14:03-14:27) and none of this
   session's, while `dispatches.md`, read from the event log, ran to 14:47.
5. **The order.** Sessions, then words, refusals and time over them, then the tests.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: a bundle built over an hour of two sessions carries both sessions' words, each labeled, and names
   a session whose transcript it could not find; `tests/tooling/test_checkpoint.py` red without it.

### T44 Decisions

**D58 - every session of the hour.** `stepback_bundle.sessions_of` lists every `sid` with events in the window, busiest first.
Without `--transcript`, `build` reads each one's transcript (`transcript_of`) and merges their records by timestamp, each tagged
with its session. `words.md` labels each entry with the session's first 8 characters when the hour has more than one, keeps the
newest over the cap (the existing shrink, then the cut, whose notice stays), and opens with the sessions it read and any whose
transcript it did not find ("left out"). `refusals.md` takes every session's refusals. `time.md` sums over the sessions read and
says so, since parallel sessions can sum past the hour. With `--transcript` (a replay) the one transcript is read as before.

## T08 - a pond's bank planted sparsely with mulberry and cudrania, or bare (the ranking row `hamletgen/sink.py::lay_sink#pond bank form`)

### T08 Approach (checklist part A)

1. **The goal, in the world.** A hamlet's tail pond stands with one of the two banks the record attests: bare, or planted
   sparsely with mulberry and cudrania, rolled per map.
2. **The constraints.** The ranking row ("add the pond bank knob: roll the Song manual's sparsely treed bank (mulberry and
   cudrania) against the bare bank, drawing its trees"); several attested forms are a knob rolled from the seed (CLAUDE.md); the
   reeds and wet tint stay off the bank (0061); a tree keeps out of a yard's or bed's sun (0038, `thin_planted_trees`); nothing
   seated on a house, way, crop or water (the overlap matrix); a new element owes its pop-up, its record line and a glyph-check;
   no known regression (XIII).
3. **Where each comes from.** The two forms are 0061's (R: Chen Fu's *Nongshu*, Song, "on the bank plant mulberry and cudrania
   sparsely, to which cattle can be tethered"; the bare bank from the same passage's cattle-trodden bank and today's mown bank);
   the knob rule the GM's (G); the spacing "sparsely" has no figure (O - ours, labeled GUESS); the crown size ours (CONVENTION, the
   dike's standard tree).
4. **Do they describe the world here?** To be measured: how many tail ponds the pool and cohort draw, and how much bank ring stays
   free of houses, ways and fields at each, before the trees are seated.
5. **The order.** Measure the free bank; the knob and its roll; the trees, seated late (after the ways) round the reed fringe's
   outer edge, each asked of the matrix; the pop-up and the record line; tests; pool and cohort.
6. **The exits.** (a) the spacing is ours - a knob band, never a target; (b)-(e) n/a.
7. **The search smell.** One search pass only if the spacing or the share of planted banks is asked for (0061 gives neither).
8. **The budget.** 3 hours.
9. **Done, measured.** One goal: across the cohort, both forms are drawn, each planted bank's trees stand on the ring beyond its
   reeds, clear of every house, way, crop and water; the knob recorded in the manifest; tests red without the knob and the seat
   rule.

### T08 part B (2026-10-18T16:31Z)

Owed by the hour-17 step-back (hour:385-approach-checklist@17, `continue`, ruled 15:53Z); the ask ask:t08-overlap-exempt-drifts
(`continue`) ruled on the claims left at landing.

1. **What is refusing?** Nothing on the maps: the pool rolls clean, the cohort holds 54/54, both forms come up (seeds 4, 9, 11
   planted with 30 trees each, seed 7 bare; Inashiro planted 30, Mizuguchi 24). Claims round 1 found the drawing page behind the
   code (the page session brought it up), the bank mulberry held to the canopy sun rule though 0038 exempts field mulberry (the
   claim now reads 0061's shade tree for cattle - a tree, not a trained bush), the trunk rule labeled plumbing (now UNRESEARCHED),
   and four older `_OVERLAP_EXEMPT` drifts re-opened by the one added key (carried into T43).
2. **A3 again.** Unchanged: the two forms 0061's (R); even odds, the pitch, the crown, the alternation ours (GUESS); the two greens
   CONVENTION.
3. **A4 again.** Measured: every planted bank in the pool and the six rolled seeds held every seat free - the tail pond stands
   below the fields, away from the farms.
4. **Moving something earlier for something later?** No - the trees are seated after the houses, ways and wells.
5. **Tuning or changing?** Changing: a new element on its knob.
6. **The one-sentence test.** "A tail pond's bank is bare or planted sparsely with mulberry and cudrania, rolled" - true on the
   pool and the rolled seeds.
7. **The next step is a measurement.** Claims round 2, the gate, the glyph check, the landing cohort.
8. **Routes measured before asking?** Yes - the ask carried the pool and cohort.
9. **After a ruling.** `continue`: carry the four into T43, land under CLAIMS_OK; the per-entry keying declined to the GM's review
   (an overhaul of the claims record).

### T08 Approach (re-answered 2026-10-18T17:08Z)

Owed by the re-decided D61b (the glyph check's NEEDS-WORK on Inashiro).

1. **The goal, in the world.** Unchanged: a tail pond's bank is bare or planted sparsely with mulberry and cudrania - and now the
   bank itself stands dry beyond the reeds, as 0061's drawing page says it is kept.
2. **The constraints.** Part A's, and 0061's "reeds and the wet tint are kept off the embankment ... nor on any raised rim around
   a pond"; the glyph check's F1 (no trunk in the marsh) and F2 (no ruled ring).
3. **Where each comes from.** The dry bank is 0061's (R); its width, 18 ft, ours (GUESS); the radial jitter ours (GUESS).
4. **Do they describe the world here?** Measured by the glyph check: on Inashiro all 30 trunks stood in the toe marsh, laid by
   the hinterland after the trees; the toe marsh was cut only by the pond's ellipse.
5. **The order.** The bank's block, then the trees' radial jitter, then the tests, the pool, the cohort, and the glyph check again.
6. **The exits.** (a) the bank width is ours, a knob band; (e) n/a.
7. **The search smell.** None.
8. **The budget.** 90 min.
9. **Done, measured.** One goal: every tail pond's bank is dry beyond its reeds (no toe-marsh ground inside the bank's ellipse)
   and no bank tree's trunk stands in any marsh, on the pool and the cohort; the glyph check passes.

### T08 part B (2026-10-18T17:45Z)

Owed by the hour-18 step-back (hour:385-approach-checklist@18, `continue`, 16:57Z).

1. **What is refusing?** The glyph check's NEEDS-WORK on Inashiro: every bank tree stood in the toe marsh, laid after the trees,
   and the ring read as ruled. Fixed by D61b (the bank kept dry beyond the reeds for every tail pond; the trees jittered across it):
   0 trunks in any marsh on Inashiro and Mizuguchi, pool clean, cohort-landing 54/54, the gate green. Two reds on the way had
   separate causes (a 0.92 crown, an unreached line) and a third gate went red on a test race (fixed as T51).
2. **A3 again.** Unchanged, plus 0061's dry embankment (R) and its 18 ft width (GUESS).
3. **A4 again.** Measured: the toe marsh was cut only by the pond's ellipse - a drift older than T08.
4. **Moving something earlier for something later?** No - the bank is reserved in the trees' own stage, before the hinterland.
5. **Tuning or changing?** Changing: the bank's ground follows the page.
6. **The one-sentence test.** "A tail pond's bank stands dry beyond its reeds, bare or planted" - true on the pool.
7. **The next step is a measurement.** The glyph check again, at the landing.
8. **Routes measured before asking?** n/a - no ask.
9. **After a ruling.** `continue`: land T08; its tooling fix was T50.

### T08 Decisions

**D60 - the knob.** `POND_BANKS = ("bare", "planted")` in `consts.py`, rolled per hamlet from the seed (`_roll(seed, "pond_bank",
...)`, a `HamletSpec.pond_bank` override), recorded as `meta.pond_bank`. Even odds: 0061 attests both forms and gives no share
(GUESS, labeled at the constant). Only a hamlet whose sink is a pond rolls it; an off-map sink has no bank.

**D61 - where the trees stand.** A new stage `stage_pond_bank`, after `stage_lane_wells` and before `stage_hinterland`: the houses,
ways and wells stand, so a tree is seated against them, and the hinterland's scrub and copse work round the trees. The ring is the
reed fringe's outer edge (the pond's radii plus the fringe margin `pond_fringe_ring` takes) plus half a crown, so a crown stands on
the bank, never in the reeds (0061: reeds and tint kept off the bank). Seats are walked round that ring at `POND_BANK_PITCH_FT`, a
GUESS "sparsely" (no figure in 0061: one tree about every 30 ft of bank), each jittered by position (`_hjit`). A seat is kept only
where its crown stands clear of every building, wellhead and way and its trunk off crop and water - the canopy keepouts the
farmstead trees already use (`_canopy_keepouts`, the lanes' treads) - so no tree is forced onto anything; a ring with no free seat
draws none, recorded (`meta.pond_bank_trees`).

**D61b - the bank kept dry, and the trees off a ruled ring** (the glyph check's NEEDS-WORK on Inashiro, 2026-10-18: all 30 trunks
stood in the hinterland's toe marsh, laid after the trees, and the ring read as a ruled dotted border). 0061's drawing page already
says "reeds and the wet tint are kept off the embankment ... nor on any raised rim around a pond", and the toe marsh was cut only by
the pond's ellipse - a drift older than T08 that the trees made visible. So `stage_pond_bank` adds, for every tail pond whether
its bank is bare or planted, the bank's ellipse - the pond's radii plus the reed fringe (`SINK_FRINGE`) plus `POND_BANK_FT` - to
the no-build blocks the toe marsh and the scatters already subtract (`block_polys`; `pond_cut` keeps every block but the pond's
own box), so the bank stands dry beyond the reeds and nothing later is built on it. `POND_BANK_FT` is 18 ft, a GUESS (no width
recorded for a tameike's crest; room for a crown and a little play). Each tree's seat is jittered across the bank as well as
along it, within the 6 ft the crown leaves, so the trees do not stand on one ellipse.

**D62 - the mark, the record and the pop-up.** Each tree is the dike's standard tree (a crown of `POND_BANK_CROWN_FT`, a GUESS from
the habit of a pollarded mulberry; the mark CONVENTION), held at seating to the sun rule `thin_planted_trees` applies (0038: a
canopy tree; the bank mulberry is 0061's shade tree for cattle, not 0038's field bush) - amended at implementation: `_plant_run`
records a tree only in `planted_trees`, which `structures_clear_of_trees` does not read - its crown in `tree_crowns` so the
structure tests see it, the trees with their kinds in `pond_bank_trees`. Mulberry and cudrania alternate
round the ring (0061 names both; the alternation is ours, GUESS), the cudrania a shade darker. A new feature class, "pond-bank
tree", carries the pop-up (its About from 0061, its Depiction the mark, its Guesses the pitch, the crown and the alternation).

**D63 - the record.** 0061's drawing bullet "A bank with a few trees on it is not drawn yet" becomes the knob's own: both forms are
rolled, the pitch, crown and alternation labeled GUESS - written by a page session, then its checks.

## T09 - the hamlet's row pitch is 0038's sum, and `BUNDLE_PITCH` is no row pitch (the ranking row `hamletgen/consts.py::BUNDLE_PITCH#row pitch`)

### T09 Approach (checklist part A)

1. **The goal, in the world.** A hamlet's rows of houses stand 92 ft apart, as 0038 sets them, and the record says which number
   does that.
2. **The constraints.** The ranking row ("BUNDLE_PITCH 100.0 -> 92.0 (0038: rows set 92 ft apart); re-derive HOMESTEAD_GROUND_FT
   and WEB_REACH_FT ties"); room before packing; no known regression (XIII).
3. **Where each comes from.** 92 ft is 0038's (R: "Rows are set 92 ft apart, and a house (28 ft deep), its yard (about 26 ft) and
   39 ft of sun come to about 93 ft"). The hamlet's rank-to-rank step is `stages._rank_step` - an envelope's depth plus the larger
   of the lane's room and `SUN_CORRIDOR_FT` (39 ft, 0038) - already claimed on 0038 as "the page's rows 92 ft apart". `BUNDLE_PITCH`
   (100, ours, O) is the step ALONG a row (`seats.front_row`'s offers), a homestead's floor in the row aspect, the capacity grid
   and its exclusion radius, the web's doubled-run and tie spans - none of them the distance between rows. `WEB_REACH_FT` is 0246's
   "within 100 ft"; `HOMESTEAD_GROUND_FT` (104) the band, UNRESEARCHED.
4. **Do they describe the world here?** Measured 2026-10-18: moving `BUNDLE_PITCH` itself to 92 - pool clean, cohort 52/54 (seed 17
   refused at the web, seed 43 seated 10 of 14) - shrinks the along-row and grid spans, not the rows; and the row-to-row step
   already follows 0038 through `_rank_step`.
5. **The order.** The claim relabeled; the claims checked; no map changes.
6. **The exits.** (e) conform the label: the code already does what the research says, through another number.
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** One goal: `BUNDLE_PITCH`'s claim says what it is - the along-row and grid span, UNRESEARCHED - and names
   `_rank_step` as the row pitch on 0038; the claims check IN-STEP; no map changes.

### T09 Decisions

**D73 - the label conformed, not the number.** `BUNDLE_PITCH` keeps 100 ft. Its claim "row pitch - 0038: 100 ft, house, yard and
the yard's 39 ft of sun" - MISLABELED, since the row-to-row step is `_rank_step` and 0038 gives 92 - becomes "the along-row span -
UNRESEARCHED: 100 ft, the step along a row and the grids' spacing; the rows themselves stand `_rank_step` apart, 0038's house, yard
and 39 ft of sun". The comments that call it "the ground one homestead takes" or "the row pitch" are corrected to match. Moving the
along-row span is not asked by the research and regressed two seeds when tried, so it stays (room before packing).

## T45 - a box the round arbiter filed lands open (found by T07's landing)

### T45 Approach (checklist part A)

1. **The goal, in the world.** A task holding findings a round-arbiter ruling carried holds no landing, as a box the claims gate
   filed holds none, without the session editing a reviewed plan line to say so.
2. **The constraints.** FR-013 and D28 (a box the tooling filed is not a hand-typed mark); a hand-typed `[lands-open]` still
   holds; tooling only; a test red without it.
3. **Where each comes from.** FR-013 is the GM's (G, amendment 3, option 3); honoring the arbiter's filings is ours (O).
4. **Do they describe the world here?** Yes - measured at T07's landing (2026-10-18): T43 (filed by ask:t07-two-findings-at-landing)
   and T44 (filed by hour:385-approach-checklist@16) were refused as hand-typed marks, and naming them on the plan's Lands open line
   cost a plan review round of its own.
5. **The order.** The rule, then its test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: a box filed by `make claims-carry KEYS= RULING=` holds nothing; a RULING the record does not
   hold is refused; a hand-typed box citing a recorded trigger still holds; `tests/tooling/test_lands_open.py` red without it.

### T45 Decisions

**D59 - the filing command writes the box and its record together** (round 1 BLOCKED the first form: a box naming a trigger
let a hand-typed mark through, and a tooling fix needs no open box - it lands and is ticked in one command, `make
arbiter-fix-done LAND=`). `make claims-carry F=<n> KEYS="<key>;<key>" RULING=<trigger> [T=<open task>]` files findings the gate
counts as introduced, which a round-arbiter ruling carried, as `claims-carry` files the gate's own carried ones: into the named open
task or a new box, and a `claims-carried.jsonl` row naming the task, its keys and the ruling. It refuses a RULING that is not a
`trigger` in the feature's `arbiter.jsonl`. `holding` honors the box by its id from that row (D28's rule, unchanged), so a
hand-typed box citing any trigger still holds the landing. The push's claims gate is unchanged: an introduced finding still needs
CLAIMS_OK citing the ruling. T43 is filed this way (`T=T43`), and its id comes off the Lands open line at T45's next plan edit.

## T46 - a landed Makefile brings its make-targets page (the arbiter's fix on hour:385-approach-checklist@17)

### T46 Approach (checklist part A)

1. **The goal, in the world.** A Makefile landed alone by `make land-tooling` never leaves the clone's make-targets page stale,
   so the clone's next push is not refused for it.
2. **The constraints.** The arbiter's fix: "scripts/land-tooling.sh (make land-tooling) runs make docs and lands the regenerated
   make-targets page together with a changed Makefile, refusing to land when the page would be stale, with a test in
   tests/hooks"; tooling only; a test red without it.
3. **Where each comes from.** The fix is the arbiter's (G).
4. **Do they describe the world here?** Measured at T45's landing (2026-10-18): `land-tooling` already regenerates the page in its
   worktree, so main's copy was current; the clone's own copy was stale (T45 changed a `##` line and never ran `make docs`), so
   the clone's next `sync-with-main.sh done` refused it ("docs/make-targets.html is stale against the Makefile").
5. **The order.** The refusal, the page added to FILES, then the tests.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: `land-tooling` with the Makefile in FILES refuses while the clone's page is stale (naming `make
   docs`), and lands the clone's page beside the Makefile when it is current; `tests/hooks/test-land-tooling.sh` red without each.

### T46 part B (2026-10-18T16:48Z)

Owed by the red-gate rulings red-gate@2026-10-18T16:44:54Z and red-gate@2026-10-18T16:45:47Z (`continue` both), which fell while
T46 was the active task; the reds were T08's (`t08-red-gates.md`), and T46 itself landed before them.

1. **What is refusing?** Nothing of T46's: it landed (the arbiter's fix settled); its tick waits on T08's glyph check, which the
   last checkpoint owes.
2. **A3 again.** Unchanged: the fix is the arbiter's (G).
3. **A4 again.** Unchanged; measured at T45's landing.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither since part A.
6. **The one-sentence test.** "A landed Makefile brings a current make-targets page" - true by its test, red without each half.
7. **The next step is a measurement.** T08's gate, then its glyph check, then T46's tick.
8. **Routes measured before asking?** n/a - no ask.
9. **After a ruling.** `continue`: a local `make test-full` green before T08's next gate.

### T46 Decisions

**D64 - the page checked in the clone and landed with the Makefile.** With `Makefile` in FILES, `land-tooling` runs the
make-docs check in the clone (`LAND_TOOLING_DOCS_CHECK`, default `python3 scripts/make-docs.py . --check`) before it builds the
patch; a stale page is refused with the fix ("run `make docs`, commit, and land again"). A current page that differs from main's
is added to FILES, as the ledger is. The worktree's own regeneration stays, so main's page is current in either case.

## T49 - a tree-moved abort is no red gate, and the red-gate bundle shows what changed between reds (the arbiter's fix on red-gate@2026-10-18T16:44:54Z)

### T49 Approach (checklist part A)

1. **The goal, in the world.** The red-gate tripwire fires on two gates that ran and failed in a row, never on a gate that aborted
   because the tree moved, and its arbiter sees what changed between the reds it counts.
2. **The constraints.** The arbiter's fix: "The red-gate counter behind make done / make arbiter-bundle should not count a 'tree
   moved' abort (test-full never ran, as at 16:45:47Z) as a red make done, and the red-gate bundle should carry the diff between
   each pair of counted reds"; a tree-moved run still never vouches for the tree (FR-004: the push refuses it); tooling only; a
   test red without each half.
3. **Where each comes from.** The fix is the arbiter's (G); FR-004 and FR-010 are 375's (G).
4. **Do they describe the world here?** Yes - measured 2026-10-18: the Makefile's tree-check abort (line 84) records
   `failed-gate done`, which `ci/state.py` counts in its "red in a row" slot; a `make done --dry-run` at 16:45:47Z recorded such an
   abort after 2 s and owed a second red-gate trigger; and `red_gate_runs` listed it among the reds.
5. **The order.** The Makefile's abort record, the bundle's filter and diffs, then the tests.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: a tree-moved abort leaves the red-in-a-row slot as it was and is not listed among the bundle's
   reds, and the bundle carries the diff between each pair of listed reds; tests red without each half.

### T49 Decisions

**D66 - the abort recorded as its own target, the bundle reading only gates that ran.** (a) The Makefile's tree-check abort
records `failed-gate tree-moved` (its own target): `ci/state.py` counts only a `done` toward the red-in-a-row slot, so the abort
never owes a trigger, while the failed record still overwrites the green slot, so nothing vouches for the moved tree - no engine
change. (b) `arbiter_bundle.red_gate_runs` passes over a run whose result is "failed: tree moved", and between each pair of the
reds it lists writes the diff between their recorded commits - `git diff <earlier> <later>`, its `--stat` as a header - into the
bundle (round 1 BLOCKED a `--stat` alone: the arbiter asked for "the diff"). A run record keeps its commit and no tree state, so two
reds on one commit say so ("the same commit; uncommitted edits between them are not recorded") rather than showing an empty diff.

## T50 - a part B stamped in the future is refused (the arbiter's fix on hour:385-approach-checklist@18)

### T50 Approach (checklist part A)

1. **The goal, in the world.** A part B's stamp says when it was written, so "written after its trigger" is a fact the gate
   checks, not a time the session typed.
2. **The constraints.** The arbiter's fix: "The approach gate (make plan-delta and the tick's part-B check) refuses a '### Tnn
   part B (<stamp>)' heading whose stamp is later than the current UTC clock, with a test that a future-stamped part B is refused
   and a present one passes"; T27's minute rule unchanged; tooling only.
3. **Where each comes from.** The fix is the arbiter's (G); part B and its stamp are 385's (G, plan D9; T27).
4. **Do they describe the world here?** Yes - measured 2026-10-18: T08's part B was stamped 16:40Z at 16:31 and T46's 16:52Z at
   16:48, each caught by eye; the gate compares only that the stamp is not before its trigger.
5. **The order.** The rule in `approach_gate.py`, then its test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: a part B stamped past the current UTC minute is refused by the tick's check and by
   `make plan-delta`, naming the stamp and the clock; `tests/tooling/test_approach_gate.py` red without it.

### T50 Decisions

**D67 - the clock bounds the stamp.** `approach_gate.py`'s part-B reader compares each stamp, truncated to the minute as T27's
rule does, with the current UTC minute; a later stamp is refused with "stamped <stamp>, after the clock (<now>) - stamp a part B
with the time it is written". `make plan-delta` asks the same reader, so both refuse it.

## T51 - the plan-gate tests write their own bundles (found by T08's gate)

### T51 Approach (checklist part A)

1. **The goal, in the world.** The tooling suite gives the same answer however its tests are spread across workers.
2. **The constraints.** The bundles a session dispatches stay where they are (`/tmp/l7r-check`); only the tests move theirs;
   tooling only.
3. **Where each comes from.** The defect is ours (O): two tests writing one shared path.
4. **Do they describe the world here?** Yes - measured on T08's gate (2026-10-18): `test_a_check_waits_for_its_task_s_decisions`
   failed with `FileNotFoundError: /tmp/l7r-check/plan-375-x-T05`, and passed alone; `decide_prompt` writes that path, as does
   `test_the_decide_commands` in the same module, so two workers raced on it. (The same gate's formatter sorted T49's test imports;
   that is T49's own defect and re-lands with T49 - round 1's ruling.)
5. **The order.** The fixture, then the module run.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: `tests/tooling/test_plan_gate.py` writes no bundle under `/tmp/l7r-check`.

### T51 Decisions

**D68 - each test's own bundle directory.** An autouse fixture in `tests/tooling/test_plan_gate.py` points `plan_bundle.OUT` at the
test's `tmp_path`, so no two tests share a bundle path.

## T52 - make land-tooling lints the Python it lands (found by T49 and T51)

### T52 Approach (checklist part A)

1. **The goal, in the world.** A file `make land-tooling` puts on main passes the lint and the formatter every gate runs, so no
   session's next gate fails on another's landing.
2. **The constraints.** The checks run in the landing's worktree, on the landed files only, as its tooling tests do; a failure
   lands nothing and names the fix (`ruff format <file>` / the ruff rule); tooling only; a test red without it.
3. **Where each comes from.** `land-tooling`'s checks step is feature 379's (O); the lint and format rules are the gate's (G,
   constitution: ruff and ruff format).
4. **Do they describe the world here?** Yes - measured 2026-10-18: T49's test landed with its imports unsorted, and a merge then
   left a duplicate `import subprocess` that landed too; T51's fixture landed with the wrong blank lines. Each was caught only by
   the next `make done`'s formatter, after it was on main.
5. **The order.** The check in the worktree's checks step, then its test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: `make land-tooling` refuses a Python file that fails `ruff check` or `ruff format --check`,
   naming the file and the fix; `tests/hooks/test-land-tooling.sh` red without it.

### T52 Decisions

**D69 - the landed Python linted in the worktree.** `land-tooling`'s checks step adds `ruff check` and `ruff format --check` on the
`.py` files among FILES, in the worktree (`LAND_TOOLING_LINT`, default those two commands, a seam for the test); a failure is one of
the checks that fail, so nothing lands and the message names the files and `ruff format <file>` or the rule.

## T53 - owed ledger rows refused before the checks (the arbiter's fix on hour:385-approach-checklist@19)

### T53 Approach (checklist part A)

1. **The goal, in the world.** A landing that will be refused for owed ledger rows is refused at once, not after its checks run.
2. **The constraints.** The arbiter's fix: "scripts/land-tooling.sh (and so make arbiter-fix-done, which lands through it) runs the
   make ledger-owed check before it starts its timed checks and refuses at once naming the owed rows, instead of after the checks
   have run, at the push"; the push's own check stays (it is the rule); `LEDGER_ROWS_OK` waives both, as it waives the push's;
   tooling only; a test red without it.
3. **Where each comes from.** The fix is the arbiter's (G); the ledger rule is 385 FR-019 (G).
4. **Do they describe the world here?** Yes - measured 2026-10-18: landings at 17:07, 17:18 and 17:54 each ran about 35 s of
   checks, then the push refused for owed rows.
5. **The order.** The early check, then its test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 25 min.
9. **Done, measured.** One goal: `make land-tooling` with an owed pass refuses before any check runs, naming the rows and the
   command; `tests/hooks/test-land-tooling.sh` red without it.

### T53 Decisions

**D70 - the ledger asked first, as it will land.** Before its worktree, `land-tooling` runs `ledger_owed.py --refuse` against the
ledger as committed at HEAD - what the landing carries - (`LAND_TOOLING_LEDGER`, a seam for the test); an owed pass refuses with
its rows and `make ledger-owed WRITE=...`, unless `LEDGER_ROWS_OK` is set, which the push honors too.

## T54 - a ticked task is no active task (found by T52's and T53's ticks)

### T54 Approach (checklist part A)

1. **The goal, in the world.** What a trigger owes - a part B, a decision check - lands on a task that still has work, never on
   one already ticked.
2. **The constraints.** `make task-start`'s mark is the session's choice and wins while its task is open; FR-003a and D9 unchanged;
   tooling only; a test red without it.
3. **Where each comes from.** The mark and its fallback are 375's and 385's (O).
4. **Do they describe the world here?** Yes - measured 2026-10-18: the hour-19 ruling owed T52 a part B after T52 was ticked, and
   the next cohort owed ticked T53 a part B for seeds 17 and 43 (T09's first measurement) - in each case the mark still named the
   ticked task.
5. **The order.** The fallback in `plan_gate.active_task`, then its test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: with the mark naming a ticked task, `active_task` returns the first open task;
   `tests/tooling/test_plan_gate.py` red without it.

### T54 Decisions

**D71 - a stale mark falls back.** `plan_gate.active_task` honors `.git/active-task` only while its task's box is open; a mark
naming a ticked (or missing) task falls back to the first open task, as no mark does. Every reader of the active task - the
approach gate's triggers, the decide-first guards - gets the same answer.

## T55 - the landing's lint keeps the gate's scope (a defect in T52)

### T55 Approach (checklist part A)

1. **The goal, in the world.** `make land-tooling` refuses only what the gate itself would fail on, so a fix to a script lands.
2. **The constraints.** T52's purpose (no landed file fails the gate's lint); `pyproject.toml`'s `extend-exclude` is the scope the
   gate lints (scripts/, tests/hooks/ and the rest left out on purpose, `tests/tooling/test_lint_scope.py`); tooling only; a test
   red without it.
3. **Where each comes from.** The lint scope is the project's (O, pinned by its own test); T52's check is ours (O).
4. **Do they describe the world here?** Yes - measured 2026-10-18: ruff lints an explicitly named file even when excluded, so
   T52's check would refuse `scripts/gates/plan_gate.py` (T54's fix) for a SIM905 and a format the gate never checks there.
5. **The order.** The flag, then its test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: an excluded `.py` that ruff would flag lands; an included one that fails is still refused;
   `tests/hooks/test-land-tooling.sh` red without it.

### T55 Decisions

**D72 - `--force-exclude`.** T52's two ruff commands carry `--force-exclude`, so the project's excludes hold for the files a landing
names, as they hold for the gate's own `ruff check .`.

## T11 - the close

The checklist to `docs/`, the refusals extended to every feature's tasks (FR-001), the final report (SC-001, SC-002).
