# Implementation Plan: the approach checklist - the front of 384, one task at a time (feature 385)

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
taken with D3 in place, since D3 changes no lane, only what a refusal says. D2's and D4's exact shape is then fixed against the
cases the named refusals show (seed 21's five lanes, the pool's violations); seed 17's refusal is a reach (the field reached by no
way), not an angle, and is T03's unless D2-D4 mend it. If the named rules on seed 21 are not angle or doubling rules, the session
stops at part B before writing D2 or D4.

**D2 - "Forced" is one predicate, asked by every angle rule - two shapes.** The ground a lane may not cross - a house or its
steading's built ground (`steading_footprints`), a fixture (`fixture_quads`), the solid boxes (`solid_boxes`), crop or water (the
worked ground the settle already reads) - is indexed once per manifest (`settlement/_geom/indexes.py`, the overlap-check rule) and
asked two ways:
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
XIV): seed 21's refusal named five lanes and no rule.

**D4 - Side by side becomes one, by the cut that exists.** A needle over open ground (not forced by D2) is the doubled tail seen
from the other side, so the merge is the settle's existing cut: `tails.along_tail` walks in from the lane's end to where it came
alongside the way and `cut_at_tail` ends it there on the tread, asked for a needle end at `NEEDLE_DEG` where it is asked today at
`_DOUBLED_DEG` (`settle.py` 380-403) - reuse, not a new pass. A needle the cut cannot mend (it would strand a house or a tree lane's
reach) stays a violation, named by D3. The GM's ruling (G, 2026-10-17): *"if there are two different footpaths that are nearly
parallel to each other and very close together, then that is the kind of situation in which a single footpath would emerge"*.

**D5 - Nothing else moves.** No threshold changes value, no rule outside the angle and doubling rules changes, and no homestead,
fixture or seat moves. A rule the table finds describing no walker's behavior is retired only with its reason at the predicate
and on the drawing page; none is expected.

**D6 - Measured.** With D3 in place and before any other engine edit: the 48-seed cohort at HEAD (`make cohort N=48`, logged), seed 10 under the wave 155 patch,
and the pool's hamlets' lane violations. After: the same three. Two workers while the containers sit near their memory cap
(2026-10-17's memguard notices).

**D7 - The record.** 0081's and 0246's drawing pages say what the maps now draw: a turn the ground forces is drawn as walked, and
two paths side by side are drawn as one. Their record checks run as `make record-owed` names them.

### T01 retro

Written in `retro.md` when T01 closes: where the time went (from the event log, `make feature-report F=385`, split by hand at
the decision points until T02 builds the split), which checklist items fired, which should have, and the change made.

## T02 - the tooling: the Approach block required, the triggers, the split (FR-003 to FR-005)

Decided at its start, after T01's retro: its Approach block and decisions are written here then, and reviewed by `make decide`.

## T03 to T10 - the four seeds failing at HEAD, T48, T47's patch, five ranking rows

Each decided at its start, in this order (spec FR-007), its section added here and reviewed by `make decide`.

## T11 - the close

The checklist to `docs/`, the refusals extended to every feature's tasks (FR-001), the final report (SC-001, SC-002).
