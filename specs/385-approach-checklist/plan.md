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

**Lands open**: T02, T03, T04, T05, T06, T07, T08, T09, T10, T11

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

## T03 to T10 - the four seeds failing at HEAD, T48, T47's patch, five ranking rows

Each decided at its start, in this order (spec FR-007), its section added here and reviewed by `make decide`.

## T11 - the close

The checklist to `docs/`, the refusals extended to every feature's tasks (FR-001), the final report (SC-001, SC-002).
