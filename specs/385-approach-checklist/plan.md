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

**Lands open**: T02, T03, T04, T05, T06, T07, T08, T09, T10, T11, T12

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

## T04 to T10 - T48, T47's patch, five ranking rows

Each decided at its start, in this order (spec FR-007), its section added here and reviewed by `make decide`.

## T11 - the close

The checklist to `docs/`, the refusals extended to every feature's tasks (FR-001), the final report (SC-001, SC-002).
