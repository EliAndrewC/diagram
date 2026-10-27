# Implementation Plan: all seeds pass (feature 417)

**Spec**: `spec.md` | **Request**: `request.md` | **Research**: `research.md` | **Date**: 2026-10-24

## Summary

Fresh seeds fail at 9-14% (R1, one-shot 2026-10-24: 9 of 100 at main; the spec's tally, 360 of 2,544) because the engine places and then repairs (the lane web's settle) or never asks a rule until
the finished map is audited (row, brook and grove rules). The plan measures first (a fresh block of 1,000 at main, by form
and cause), inventories every repair pass and audit-only rule, then rebuilds them biggest share first so each rule is one
predicate asked before placing, deleting the repair code and the mid-map checks, and giving room where nothing fits. Once a
fresh block of 500 passes whole, the landing guards go on: the fresh block before the push (FR-009) and every archetype
form diffed against HEAD (FR-011, feature 394). Engine tasks land through `make land`.

## Technical Context

- **The lane web**: `l7r/diagram/hamletgen/ways/` (15,982 lines, `wc -l` of `ways/*.py ways/*/*.py`, one-shot 2026-10-24). `web/stage.py` `stage_web` lays the web;
  `settle/stage.py` `settle_the_web` loops `STEPS` (sixteen repair functions) to a fixpoint, then `last_resort.py` drops
  ordinary lanes or raises `WebRefused`. `law.py` / `law_water.py` hold every lane-law rule as one predicate (`LAW`,
  `violations`); `keeper.py` keeps each lane's verdict; `tree.py` `admits` is the one predicate the seating asks of a
  corridor (tree lanes are admitted lawful at seating).
- **Seating**: `hamletgen/homesteads/stages.py` (`stage_homesteads`, `SiteRefused`), `capacity.py` (the exhaustive pass),
  `growth.py` (the nucleated cluster); room knobs `SEATING_GROUND_FT`, `HOMESTEAD_GROUND_FT`, `grow_gap`.
- **Audit-only rules**: `hamletgen/homesteads/row_rules.py`, `settlement/homestead_parts/grove_rules.py`, wired in
  `l7r/diagram/tools/cohort_audit.py:166`; `farmstead_across_brook` at `cohort_audit.py:146`.
- **Overlap**: `overlap/registry.py` (`admits` first, `OverlapRefused` the backstop at record time).
- **The cohort**: `make cohort` (`tools/cohort_audit`), `scripts/gates/cohort_gate.py` (fixed 48, pinned rows, the fresh
  block), `scripts/land.py` (`start_fresh_block` after the push, feature 415 D5), `dev/cohort-log/*.json` per seed.
- **Field forms**: `hamletgen/consts_fields.py` `FIELD_ARCHETYPES` (three), `ROLLED_ARCHETYPES = ("valley_paddy",)`.

**Single-artifact target**: the reference settlement, Inashiro (`pool/hamlets/inashiro.gen.py`, seed 4; the cohort's own 60 s budget for it), then
the cohort; each engine task is two steps - the reference map, then the cohort and a fresh block.

## Performance bookends

`make perf LABEL=417-start` before the first engine edit (T04), `make perf LABEL=417-end` before the close (the last task). Speed is a
flag, never a gate (375 amendment 5): a by-construction placer that is slower is mentioned at its landing, with the number.

## Constitution Check

- I, II: N/A - no UI. III, IV, V, VII, VIII, IX: N/A - no pool content, SOURCE block or in-world prose.
- VI: each engine task runs the reference map, `make land` (the gate, the landing cohort, the claims round) and a fresh block
  of 500 after its landing (D1); the review checks its map delta owes (`make verify`).
- X: ruff, pyrefly, red-green tests, 100% coverage; every overlap a new placer asks goes through an index built once (the
  registry, `keeper`, `settlement/_geom/indexes.py`) - each task's Approach names it. Deleting code deletes its tests.
- XII: the lane law's rules and the research claims do not change - the rules are asked earlier, not altered; maps change and
  are held to the claims (`make land`'s claims round). A rule that cannot be asked before placing is a research question and
  goes to the record first.
- XIII: the baseline is T01's 1,000-seed fresh block at main plus the fixed 48 (green); a fixed or pinned seed that regresses
  blocks a landing (the landing cohort already refuses it). Where a rebuild re-deals the maps, the fresh rate must not rise and
  each newly failing seed is diagnosed in the task's notes.
- XIV: a defect found in code a task does not change becomes a task here (feature 405's rule, "found work stays in the
  feature").
- XVI: built as the spec's FRs; FR-002's inventory decides the engine tasks, each added through `make plan-delta`.

## Decisions

- **D1 (block sizes, R1)**: a fresh block of 500 after each engine landing (~23 min at 12 workers, R1's 2.8 s a seed, one-shot
  2026-10-24, background); 1,000 at T01 and at the close (~47 min at the same rate, one-shot 2026-10-24, from R1). SC-001's N is 500. The landing's own fresh block (FR-009) stays the cohort gate's 48. Rendering:
  none.
- **D2 (the tally)**: `scripts/measure/fresh_tally.py` (`make fresh-tally [SINCE=] [COMMIT=]`) reads `dev/cohort-log/*.json`,
  counts each record's seeds at or above its `fresh_first` by `verdict`, and prints the pooled rate by form and by cause - the
  spec's gap method, so its numbers reproduce. Rendering: none.
- **D3 (the inventory's method)**: the entries are found, not remembered - every function in `settle/stage.py` `STEPS` and
  every pass `ways/CLAUDE.md` names as after-the-web; every rule `cohort_audit` asks, with its callers inside `l7r/` (a rule
  no placer calls is audit-only); every caller of `law.violations`, `lane_violators`, `row_rules`, `grove_rules` and the
  overlap matrix inside the generator's run (a mid-map check); every pair of functions judging one rule. The search also lists
  every site where a placer that finds no admitted candidate drops, relaxes or refuses instead of being given room
  (`last_resort`'s drops and `WebRefused`, `SiteRefused`, the `OverlapRefused` backstop, and the rest it finds). Each entry
  records where it is (file and function) and which of the rule's four points it breaks (1 not asked before placing, 2 placed then repaired, 3 a finished-map
  check run in the generator, 4 a refusal or drop where room is the remedy) or that its rule is coded twice, with its share of
  R1's failures; an entry that breaks none is listed as kept with the predicate that makes it so. Every entry that breaks a
  point becomes a task. Rendering: none.
- **D4 (the hold, made)**: FR-010 is enforced, not remembered (it reaches a held feature once its status line says so; each claims
  feature found later is marked when found): `make task-start` refuses a task of a feature whose status
  says `ON HOLD ... until feature NNN ... closes` while NNN is open, naming it; `HOLD_OK="<reason>"` admits only a task that does not
  change the engine (the guard checks the task's `research:` line and refuses `HOLD_OK` on an engine task); an engine task of
  a held feature has no escape (FR-010).
  Rendering: none.
- **D5 (order)**: the engine tasks run by share of R1's failures - the lane web (about 60%, the spec's tally, one-shot 2026-10-24), then seating room
  (15%, same tally), then the
  row, brook and grove rules into their placers, then the rest the inventory finds. Each task's own design is decided in its
  Approach before its code (decide first), on the inventory's entries. Rendering: per task.
  SUPERSEDED FOR THE ORDER BY FR-013 (the GM 2026-10-26: "order our remaining tasks in 417 to prioritize the things that will
  make us go faster before the things that will make us correct"): the speed tasks run first, ranked by the calls each removes,
  in the order the GM confirmed that day (T52, T31, T06, T53, T54, T55, T12, T11, T56, T14, then T57's check-in); the order by
  share of failures above holds only among the tasks that make seeds pass, once the GM lifts the stop line.
- **D6 (the principle)**: FR-003's text is drafted by T03 and goes to the GM; the constitution is amended only with the GM's
  words. Rendering: none.

- **D11 (the stop line, the GM 2026-10-25, ruled by spec-fidelity MODE 1)**: the GM: "definitely finish out doing the tasks
  that involve, turning off automated checks, and then replacing them with just having the algorithm place correctly in the
  first place ... and then stop so we can slowly and deliberately go through the actual fixing where we get more seeds to
  pass". So the FR-004/FR-005/FR-006 conversions are done; a rule coded twice with different values is made one at the lane
  law's (or the rule's own recorded) value, and one with no recorded value waits for the GM; each conversion lands through
  `make land` when FR-008 holds (the fixed cohort, the pinned rows, the pool maps), its fresh rate recorded either way; one
  that cannot land green without seed-by-seed work or room (FR-007) is recorded and set down, never iterated on. No work aimed
  at the fresh rate, no FR-007 room work, no T20/T21 until the GM resumes it. The tasks that move no map go first. Rendering:
  none.
  AMENDED (the GM's later words): a rule with no recorded value no longer waits for the GM - "make it a tunable knob, or we can
  just do whatever is algorithmically easier", such questions "should not come to my attention for an answer in this way"
  (2026-10-25, `request.md`), "if our research findings do not indicate that things were any particular way" - so the
  downloaded research is checked first and, where nothing was ever looked for, a research pass is run (T29's and T36's method);
  only where both find nothing conclusive is it made one at a chosen value labeled a GUESS, or a tunable knob, as the GM allowed
  (T16). And the speed tasks (FR-013, the GM
  2026-10-26: "work all 10 of those tasks ... From start to finish") run whole, each landed through `make land` under FR-008;
  the stop line holds after them, at T57's check-in.

## Order

T01 measure (D1, D2). T02 the hold guard (D4) - small tooling, lands alone. T03 the inventory (D3) and the principle's draft
(D6). T04 onward the engine work in D5's order, one task per inventory group, each landed and followed by a fresh block of
500; their Approaches are added by plan-delta as each starts, numbered on from T04 as the inventory needs. Then the guards, the
two tasks after the last engine task: the fresh block before the push (FR-009), and every archetype form against HEAD (FR-011,
SC-006). The last task closes: 1,000 fresh seeds, T106's seat turn re-applied (User
Story 2), the code-size delta (SC-004), the feature report.

THE ORDER SINCE 2026-10-26 (FR-013; the GM, `request.md` "Speed first"): the open tasks run speed first, the tasks that cut a
roll's calls ordered by what each removes - T52 (the trial inventory), T31, T06, T53, T54, T55, T12, T11, T56, T14, T57 (the
checkpoint) - then the tasks that make every seed pass, in `tasks.md`'s order. Each task's Approach states its place. THE
WORK STOPS AT T57 for the GM's check-in ("then we can check in once that is all done", `request.md`); the tasks after it start
on his word.

### T31 conversion C2 (2026-10-26): the joins stop short because the tree is drawn after the links (measured; not yet built)

Measured 2026-10-26 (method: a throwaway trace in a detached worktree at a391e87ab logging, after each `STEPS` step, every
`join-orphans` link end standing more than 2 ft off any lane; seed 25 rolled with the last resort's `settle_joins` cut, as the
probe that refused it): every link is laid touching the network; the ends come off it after `settle_reach` (the tree lanes
drawn) and `settle_defer` (the ordinary lanes that break a rule against the tree cut) - on seed 25 links 3, 4, 20 and 22 end
7-15 ft off any lane after those two steps, and the last resort's `settle_joins` carries them back. So `settle_joins`' rule
(`law.near_misses`, `joins_short`) has no one placer to move into: the links are laid before the ways they depend on. The
conversion D11 owes is an ORDER: the access tree (`settle_tree`, `settle_targets`, `settle_field` - the household ways the
seating already judged, `tree.admits`) laid first in `stage_web`, then the skeleton, the orphan links and the door paths laid
onto it, each asked the lane law at lay (`Lawful`, as a tree lane is) - after which `settle_defer`, `settle_joins` and the
web stage's sweeps (`_join_orphan_ways` as a repair, `_sweep_dangling_ends`, `_sweep_doubled_tails`, `tidy_lane_ends`) are each
probed off as R8 probed the rounds. The next session starts here: plan the reorder as its own task (decide first), measured on
the landing cohort, a pre-change fresh block (seed 723759) and the five pool maps. Rendering: none until built.

**Probed 2026-10-26** (method: the patch `evidence/c2/tree-first-no-joins.patch` - `settle_tree` called at the head of `stage_web`,
before the skeleton, and `settle_joins` cut from the last resort - rolled with `make cohort-landing JOBS=3`, `make cohort N=48
SEED=723759 FRESH=0 JOBS=3` and `make map` on the five pool hamlets): the landing cohort 54 of 54 with the tree first, and 54 of 54
with the joins cut as well - `settle_joins` is NEEDLESS once the tree is drawn first. The pre-change fresh block: 7 of 48 failing
as before (b307a7ed7's seven), but not the same seven - seed 723789 now passes and seed 723775 newly fails: `WebRefused`, two
access lanes (1, 2) closing a `needle_loops` sliver, and a `joins_short`. With the joins kept it still fails, so the TREE-FIRST
ORDER causes it, not the cut. FR-008 as measured: the landing cohort's 48 fixed seeds and its pinned rows pass (54 of 54); the
five pool maps generate (Inashiro, Kuwabata and Sawada move; the pool gate, `make done`, not yet run on them). By D11 a conversion
whose FR-008 holds lands with its fresh rate recorded (7 of 48 here, before and after); constitution XIII refuses a known
regression (seed 723775). Which governs a fresh seed that newly fails while the rate holds is a PROCESS question for the round
arbiter (`make arbiter-ask`), asked next session before landing - not iterated on here. Either way, the needle rule asked of a
tree lane where `lanes_of` draws it (`law.needle_loops`, FR-005) is its own conversion task, filed and decided on its own account.

### T44 part B (2026-10-26T03:16Z)

The trigger: two red gates in a row on T44's landing (red-gate@2026-10-26T03:11:45Z; the round arbiter ruled continue).

1. **What exactly is refusing?** Two different things, neither T44's code: a stale notes census on Inashiro
   (`tests/test_notes_census.py`, the census block written before the map moved), then
   `tests/tooling/test_tick_task.py::test_the_changed_modules_coverage_runs_beside_the_gate_and_stops_it`, which read the
   landing's own `COVER_OK` escape from its environment and so found the check it tests never started.
2. **A3 again.** O: both are tooling's rules, not research.
3. **A4 again.** The census rule holds (a moved map's census is rewritten); the test's rule holds once it owns its environment.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither: two separate fixes, each once.
6. **The one-sentence test.** "The landing's escape leaked into a test of that escape" - no question it raises.
7. **The next step is a measurement.** `make land` again: the census refreshed (`make notes-census`), the test clearing
   `COVER_OK` (landed on main as tooling).
8. **Routes measured?** One route, the arbiter's ruling.
9. **After a ruling.** The step it names: `make done` once more.

### T44 part B (2026-10-26T03:26Z)

The trigger: a second red gate in a row (red-gate@2026-10-26T03:22:48Z; the round arbiter ruled continue, with a stop condition).

1. **What exactly is refusing?** Coverage of `ways/tree.py` 298-300 (`as_joined`'s loop): T44's deletion of `settle_joins`' tests
   also dropped `test_the_tree_is_asked_again_with_its_ends_joined_as_the_web_joins_them`, matched by its docstring's mention of
   the step, though its body never called it. The same cause as two earlier reds in this feature: tests dropped by name.
2. **A3 again.** O: the coverage floor.
3. **A4 again.** The lines are live (`tree_base.Faces` and `admits` call `as_joined`), so they owe a test.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither: the test restored.
6. **The one-sentence test.** "A test was deleted for mentioning a removed step" - no question it raises.
7. **The next step is a measurement.** Every other test T44 dropped checked by its BODY (2026-10-26): four call `settle_joins`
   or its helpers; one only asserted the step's place in the last resort's list, reaching no engine line. Then `make land`.
8. **Routes measured?** One route, the arbiter's.
9. **After a ruling.** Its step: the gate again; and from now, a test is deleted only on what its body calls.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->

<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T17 to T17 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T18 to T18 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->

<!-- plan-archive: T23 to T05 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T25 to T05 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->

## T26 - the web's post-lay passes the placers already make needless, measured off and deleted (R2 G2, first part; FR-004, FR-006)

### T26 Approach (checklist part A)

1. **The goal, in the world.** Every pass `stage_web` runs after the lay that changes nothing a placer did not already get right
   is gone: the web is laid as it stands, with no repair standing in for a rule its placers already keep.
2. **The constraints.** `ways/web/stage.py` `stage_web` runs about 25 passes after `lay_reachable_runs` (`inventory/ways.md`,
   web/stage.py), several two or three times: `_join_orphan_ways`, `_bridge_collinear_breaks`, `_touch_junctions`,
   `tidy_lane_ends`, `_smooth_web`, `_drop_collapsed`, `_sweep_debris`, `_drop_end_nubs`, `_sweep_steading_fouls`,
   `_sweep_doubled_remnants`, `_sweep_dangling_ends`, `_keep_the_route_wide`, `straighten_joints`,
   `fold_the_connector_hairpin`, `_sweep_doubled_tails`, `center_lane_ends`, `cut_the_overruns`, `cut_past_the_junction`,
   `split_at_crossings`, `meet_end_to_end`, `trim_streets`. Which are needless is not known: it is MEASURED, one pass (each of
   its call sites) turned off at a time.
3. **Where each comes from.** O: FR-004 (the passes that repair a laid web are deleted), FR-008 (no regression), D11 (land green
   or set down, never iterate).
4. **Do they describe the world here?** To be measured.
5. **The order.** After T23/T25; before T06 (which rebuilds what the needed passes stand in for).
6. **The exits.** A pass whose removal turns any fixed or pinned seed red, or changes a pool map's verdict, is NEEDED today: it
   is recorded with the seeds it fails and set down for T06 / the GM's fixing pass, untouched.
7. **The search smell.** One probe per pass, no tuning: a pass is deleted only as it stands, never adjusted to pass.
8. **The budget.** About 3 min a probe (48 fixed + 6 pinned seeds at 5 workers, R1's rate), about 21 passes; 1.5 h, background.
9. **Done, measured.** `research.md` R5: each pass, its probe's fixed-and-pinned result; the needless ones deleted (with their
   tests), the landing cohort green and the pool maps' verdicts unchanged; a fresh block of 500 after the landing, its rate
   recorded beside R3.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T26 Decisions

- **D22** Each probe runs in a detached worktree at the landed HEAD, with that pass's call sites in `stage_web` guarded by an
  environment switch the probe sets (the instrumentation never lands), and rolls `make cohort N=48 FRESH=0` (the fixed seeds
  and the pinned rows). A pass is NEEDLESS when every seed's verdict is the baseline's; the baseline is the same roll with no
  pass off. Rendering: none.
- **D23** The needless passes are deleted together, with their call sites and the tests that only exercised them, in one
  landing; if the landing cohort is then red, the deletion is set down whole and recorded (no pass-by-pass iteration). Maps
  may change (held to the claims and the cohort). Rendering: none.

### T26 part B (2026-10-25T08:19Z)

Owed by red-gate@2026-10-25T08:17:19Z (the round arbiter: continue).

1. **What exactly is refusing?** The coverage floor only, both runs: lines of surviving definitions whose only covering
   tests went with the deleted passes - `clearance._clear_touch`'s chord under a foot (a unit test added), `joints._key` and
   `_rounded` and `street.nearest_on` (no live caller: each kept alive in `make dead-closure` by a name another module
   defines, `washing.nearest_on` for the last; deleted). Run 1's table named all three; the session fixed two (its miss).
   The landing cohort was not red.
2. **A3 again.** No rule moves: the deleted code ran in no roll (dead) or is reached by a unit test.
3. **A4 again.** n/a - nothing placed changes.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: coverage of what stands, and dead code removed.
6. **The one-sentence test.** "Why was the gate red?" - the deletion took the only tests of three live helpers' corners and
   left three dead ones a name collision hid.
7. **The next step is a measurement.** `make done` once more, inside `make land`.
8. **Every route measured?** The gate's coverage table lists every uncovered line in one run (the arbiter); none other.
9. **After a ruling:** continue (red-gate@2026-10-25T08:17:19Z).

<!-- plan-archive: T19 to T05 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->

## The GM's 2026-10-25 afternoon message - T16, T28-T31 (the arbitrary numbers marked, the settle probe)

### Decisions

- **D29 (the GM's word, 2026-10-25, the afternoon)**: the GM: "I accept your recommendation of 20% as the correct angle for
  the double-tailed rule, but I think we should be careful to document this as an approximation ... we need to avoid falling
  into the trap where we set a number arbitrarily and then end up going through enormous iterations and difficulty to try to
  make that number work when the number is arbitrary and not an actual hard requirement ... it's important that in our
  checklist-based iteration, as we try to fix things, that we have these kinds of numbers marked." ("20%" is degrees.) And:
  "please proceed with all of this ... and then after all of that, you should switch off the 16 repair steps in whatever
  manner you find most efficient." This lifts D11's stop line for T16, T28-T31; it does not lift it for seed-by-seed fixing
  (T06-T15, T27's placer). Rendering: none.
- **D30 (T16: the doubled tail's one angle)**: `tails._DOUBLED_DEG` and `tails._ALONG_DEG` become ONE constant at 20 deg, the
  page's (0081), labeled bare `GUESS` - searched, silent (R7) - with the GM's words beside it: a goal, free to move to 15 or 25
  if that is what the placements or the look need. It is measured on the 54 fixed and pinned seeds and the pool before it
  lands; if 20 reds a seed that passes today (the comment's seeds 10 and 40, 2026-10-21), the value change is set down, the
  measurement recorded, and the two stay unmerged at their values (15 and 25), each with the goal of 20 and the measurement
  beside it - observed 2026-10-25 (method: D35's worktree, both at 20, `make cohort N=48 FRESH=0 JOBS=3` and the pool): seed 40
  newly refused (`WebRefused`, a shallow crossing left), the pool unchanged - an arbitrary number is not chased
  (the GM). The `GUESS` label, the GM's words and the pointer to R7 land EITHER WAY: documenting the number as an
  approximation is the request itself. Rendering: map drawing convention (0081).
- **D31 (no new claims class; the existing split made honest - T28, T29)**: the claim grammar already has the GM's two
  categories (`l7r/diagram/tools/claims.py:54-56`): `GUESS` - searched, silent, a value of our own - and `UNRESEARCHED` - not
  yet searched. So no class is added. What is missing is the use: (a) a derived list of every claim whose value is ours -
  `GUESS`, `UNRESEARCHED`, `CONVENTION` - with its figure, `make tunables`, read from the claims index (never a hand list,
  constitution X clause 14); (b) part A item 3 of `docs/approach-checklist.md` names those three labels as **O** - a goal and a
  knob, never a target to defend - and so too a number no claim states, and points at both `make tunables` and `make
  tunables INLINE=1` (written 2026-10-25); `docs/research-doctrine.md`'s "unresearched number is a
  knob" line gains GUESS and CONVENTION; (c) the `UNRESEARCHED` labels are checked for truth (T29); (d) a number with NO
  claim is the audit's blind spot, so it is counted and listed, in two places (observed 2026-10-25; method: AST walks of
  `l7r/**/*.py` against `claims.current`, the second now `make tunables INLINE=1`). (i) MODULE CONSTANTS: of 810, 141 carry
  no claim of their own - 47 in code that draws a map (`compound_model.py` 15, `labels/hand_sheet.py` 11, `compound_parts.py`
  11, `compound.py` 5, `compound_example.py` 3, `well_gear.py` 1, `settlement/see_through.py` 1), each given a claim in T28;
  and 94 in the tooling, by file: `tools/pack_audit/` 45 (the sheet audit's tolerances), `tools/` otherwise 23 (perf bands
  and snapshots, page and marsh audits, census, cohort and roll audits, diffs), `ci/` 10 (cache lifetimes, poll and park
  seconds, the rate per minute, the incremental fraction, a stub's seconds), `pipeline/` 4 (cache sizes), `interactive/` 3
  (glossary and archive limits) - each a run's time, cost, cache or an audit's own tolerance; none places or draws anything on
  a map. Of these, the AUDIT TOLERANCES were checked one by one for whether they decide a verdict the fixing is measured
  against (observed 2026-10-25; method: reading each constant's use): `tools/pack_audit/`'s 45 DO - they grade a Mode A sheet
  (a veranda's 3-6 ft, the coverage band, a gate's 5-16 ft, the sun's latitude) - so they get (ii)'s treatment and a claim
  each in T28, and `tools/pack_audit/` joins `make tunables INLINE=1`'s map code; `cohort_audit.py`'s two (the pinned rows'
  first seed, how many rolls before an undrawn knob value is reported), `mapcheck.py`'s one (which seeds the tripwire rolls)
  and `overlap_census.py`'s two (a census flag and its reference size) choose what is rolled or reported, never whether a map
  passes; the perf bands and snapshots flag time, never a map. (ii) NUMBERS INSIDE FUNCTIONS of the map code (the `MAP_CODE` prefixes of
  `scripts/record/tunables.py`): 1,793 non-trivial ones in 141 files that their unit's claims never state (trivial: 0-4, 10,
  100, 90, 180, 360, 255, a half, under 0.001, and subscripts). These are ours by DEFAULT - an unstated number is a knob like
  a GUESS - and `make tunables INLINE=1` lists them file, line and function, derived each run, so the audit is never stale.
  Each is given a claim (stated in its unit's account, labeled by what it is) in T29 as the claims of its unit are worked:
  the 247 units' first, then the rest, before T31's deletion; what T29 cannot reach is listed by file in R9 with the count.
  (iii) Every `UNRESEARCHED` label T28 or T29 writes is T29's to research, as the 726 are. D28's "goes to the GM" (plan-done.md) is superseded by D33 (b).
  Rendering: none.
- **D32 (T29: are the UNRESEARCHED labels true - the order)**: 726 claims are labeled `UNRESEARCHED` (observed 2026-10-25;
  method: `grep` of `Research:` lines over `l7r`, `pool`, `docs`), 247 of them in the modules this feature changes
  (`hamletgen/ways`, `homesteads`, `consts_ways`, `cluster`; `make claims-report` filtered). Those 247 go first, grouped by
  the question they share into research passes (`research-pass`, archive first, then the web), each pass told the claims it
  covers. A claim a pass answers is cited when the page states it (its page edit queued to a page session under the record's
  rules); a claim a pass finds silent becomes bare `GUESS` naming the pass in its account; a claim that decides nothing about
  the place (an algorithmic tolerance, an order of search) becomes `NONE` or `CONVENTION` by what it is. The other 479 are
  T29's too, done after the 247 and before T31's deletion (the GM: "and then after all of that, you should switch off the
  16 repair steps"); only the probe's MEASUREMENT runs beside them, since it decides nothing. Rendering: per claim, as above.
- **D33 (the two questions the GM declined, decided by the record - T27's decision)**: (a) T27's placer: 0246 lays "each
  household's way ... from its dooryard along the middle of the gaps to the track out or an earlier way, joined at a T", and
  0081's track "never stops in open country"; no page says where along the track the ways meet it. So by the GM's rule (the
  record silent: a knob, or what is algorithmically easier) the easier placement is taken: the track is DRAWN from the
  innermost T its households' ways make, decided once those ways are laid and before the track is drawn - the ways stay as
  laid. (b) The dispersed form: 0031's drawing page draws "no lane network inside it at all: the road out joins it to the
  world, and the field paths join the farms to one another", so 0081's rule applies there too: the track's inner end ends at
  a farm or on a field path. `track_ends_off_the_web` is widened to ask that when T27's placer lands (widened now, it reds the
  13 dispersed landing seeds, D28). Both are T27's placer work, set down under D11. Rendering: map drawing convention (0081,
  0031).
- **D34 (T30: the process gap - two questions that were the record's reached the GM)**: the turn's final message carried
  four questions and no `escalation-check` ran, which CLAUDE.md requires. The fix is a rule where the check is: two CUT rules
  in `.claude/agents/escalation-check.md` - a question whether a finding applies to a case, form or map goes to the research
  pass and the reviewers, never the GM; a choice the record is silent on is a knob or the algorithmically easier route, never
  the GM - each with the GM's 2026-10-25 words; one line in the root `CLAUDE.md` Research list; and `escalation-check` run on
  this turn's own final message. Rendering: none.
- **D35 (T31: the settle's steps, D22's probe)**: each of the 16 named steps of `settle/stage.py` `STEPS` (17 positions:
  `settle_husks` runs first and last; every position of a name is switched together) is switched off alone, in a detached
  worktree with a switch that never lands, and `make cohort N=48 FRESH=0 JOBS=3` and the five pool maps are rolled against the
  same roll with nothing off; then the NEEDLESS ones (no verdict and no pool manifest moved) all off together. `settle_reach`
  is a placer (it draws the reach the web owes), not a repair: it is probed as the others, and recorded as such. The needless
  are deleted together with their tests and dead closure (D23), landed through `make land`. Each NEEDED step then gets
  D11's conversion, decided before its code: its rule asked by the placer that lays what the step mends (the predicate
  named, the placer named), landed through `make land` once FR-008 holds; only a conversion that cannot land green without
  seed-by-seed work or room work is recorded with its failing seeds and set down - and that claim, for each step it is made
  of, is written as an exception and ruled (`make arbiter-ask`), never assumed. Workers at 3, not 5: the containers stood at 9.1 of 10 GB (memwatch, 2026-10-25).
  Rendering: none.

### Decisions (the work's own shape, 2026-10-25T11:05Z)

- **D36 (T29 split at its landing)**: T29 lands the 247 claims of the modules this feature changes (passes A1-D and E, R9), the
  numbers no claim states inside those modules listed by `make tunables INLINE=1 UNDER=...`, and T16's two angle claims; the
  other 479 `UNRESEARCHED` claims (observed 2026-10-25; method: `grep` of ` - UNRESEARCHED` over `l7r`, `pool`, `docs`
  after the first relabels - 580, less the 101 left in the 247's modules) and the inline numbers of the other modules are a
  new task, T36, done the same way before T31's deletion. A started task holds every landing until it is ticked (feature 405
  T32), so the split is what lets the 247's relabels and T28's claims land now. A claim whose page answers it but whose code
  departs from the page is CITED, and lands with the DRIFTED verdict impl-drift gives it - the record's mark that the code has
  drifted from the research and needs fixing (the GM 2026-10-25) - each filed in T32-T35 with its page and pass; the code is
  not changed. The claims gate refuses an introduced DRIFTED claim, so landing them is put to the round arbiter
  (`make arbiter-ask`) as the exception it is, never by keeping a label that hides the departure. Pass E's 30 claims (observed 2026-10-25; method: a keyword sort of the 247 before the
  passes, listed in `evidence/t29/pass-E-algorithmic.txt`) are split by what each decides. The MECHANICS (a search order, a
  tie-break, which node, vertex, side or lane, a trim's step, a salt, a retry's breadth - 19) are bare `GUESS`, naming E as
  the passes' no-source claims name their pass, so `make tunables` lists them. The ones that SHAPE how the hamlet and its
  lanes look (the ranks' jitter, lean, growth and gap fill; a corner's easing; a bend round what stands; the bamboo's slide -
  8) go to a research pass, E2, and are labeled by what it finds; a claim whose text records a page already searched is
  `GUESS` naming that page. The 3 that a page answers (two read "beside" at 30 ft where 0081 measures 20 degrees, one keeps a
  lattice 14 ft off water where 0055 and 0014 put the path on the bank) are cited with their departures, as above. R9 counts each kind,
  and every claim whose description is reverted after a second wrong verdict - its research label kept (GUESS naming its pass, or the citation), never restored to UNRESEARCHED. Rendering: none.

- **D37 (T36 and T38 before T31; a source no page holds yet)**: (a) T36 lands the relabels of the 479 claims D36 left
  `UNRESEARCHED` (observed 2026-10-25; method: `grep` of ` - UNRESEARCHED` over `l7r`, `pool`, `docs`): 476 are on passes P1-P7's
  lists (method: the `- ` lines of `evidence/t29/pass-P*.txt`) and 3 are not - `wood_rank.py`'s median house,
  `castle_civic.py`'s martial hall compound, and `tools/claims.py`'s docstring example of the grammar, which describes no map. The
  8 claims no pass looked into (6 on the lists, the first two of those 3) go to a further pass, P8 (`evidence/t29/pass-P8-unlooked.md`),
  and are labeled by what it finds; the grammar example stays as written. (b) A claim a source answers that no page holds yet -
  37 claims resting on 14 sources (observed 2026-10-25; method: `grep` of T36's heads naming a pass's source rather than a page)
  - has its source recorded on the page its question belongs to first, through a page session under the record's rules
  (`make page-session`, as D32 queues page edits), and is cited once the page stands: as a convention where the code follows it,
  and with its departure stated, landing DRIFTED with its unit named in its T33-T35 row, where the code departs. A GUESS label
  naming such a source is not used. (c) The numbers no claim states (1,809 in 149 files, observed 2026-10-25; method: `make
  tunables INLINE=1 COUNT=1`) are given claims in T38, BEFORE T31, as D31 (ii) orders - except those in the code T31 deletes,
  which no later pass will tweak and so need none; T31's deletion is listed first (its six needless steps' definitions, R8) so
  T38 skips them. The order is T36, T38, T31. Rendering: none.

<!-- plan-archive: T36 to T36 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T38 to T38 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
### T30 Approach (checklist part A)

1. **The goal, in the world.** A question whether a finding applies to a form, or a choice the record is silent on, never
   reaches the GM.
2. **The constraints.** D34.
3. **Where each comes from.** G: the GM 2026-10-25.
4. **Do they describe the world here?** n/a.
5. **The order.** Before this turn's final message.
6. **The exits.** n/a.
7. **The search smell.** n/a.
8. **The budget.** Done (landed as tooling, main `fef7b611f`); the check run on the final message.
9. **Done, measured.** escalation-check's tests 4-5 and the CLAUDE.md line on main; escalation-check run on this turn's
   final message, its verdict applied.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T31 Approach (checklist part A)

1. **The goal, in the world.** The settle repairs nothing a placer already gets right: every step that changes no verdict is
   gone; every needed one has its rule moved into the placer that lays what it mends, or is ruled an exception.
2. **The constraints.** D35, D22, D23, D11; the fixed and pinned seeds, the pool maps' gate.
3. **Where each comes from.** G: the GM 2026-10-25 ("switch off the 16 repair steps"). O: the probe's method.
4. **Do they describe the world here?** Measured per step (R8).
5. **The order.** After T29, T36 and T38 (D37 c), as the GM ordered; the probe's measurement runs beside them, deciding nothing.
6. **The exits.** Needless (no fixed or pinned verdict moved, the pool's gate green): deleted together. Needed: a conversion
   decided before code, or an exception ruled by the arbiter.
7. **The search smell.** One probe a step, no tuning.
8. **The budget.** 16 probes at about 13 min (3 workers, observed 2026-10-25); the deletion a T26-sized landing.
9. **Done, measured.** R8 complete; the needless deleted and landed green; each needed one converted or ruled.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.


### T31 part B (2026-10-25T23:42Z)

The trigger: the landing cohort (cohort@20261025T234214Z) refused seeds 10, 25 and 37 with `square_every_crossing`,
`settle_shapes`, `settle_way_outs` and `settle_widths` out of `STEPS` and `last_resort`'s re-asked `settle_street_ends`,
`settle_joins` (twice), `prune_the_tree`, `settle_widths` and `settle_husks` cut.

1. **What exactly is refusing?** `refuse_unmended` in the last resort: seed 10 `width_steps` (lanes 1, 3; skeleton cross),
   seed 25 `joins_short` (lane 20 at (2287, 2064); skeleton Y), seed 37 both (skeleton waterside) - each manifest at the refusal
   in `/tmp/l7r-refused/`. Two rules, the two whose menders (`settle_widths`, `settle_joins`) were cut from the last resort; R8
   had the four out of `STEPS` alone at 54 of 54, so the cut re-asks are the cause.
2. **A3 again.** O: `width_steps` and `joins_short` are lane-law rules (`law.py`), not research; their menders are the cut steps.
3. **A4 again.** They describe the web as laid here: a width step at a skeleton crossing, a join stopping short of its way.
4. **Moving something placed earlier to suit something later?** No: the measurement restores a mender and moves nothing.
5. **Tuning or changing?** Neither: one removal measured, then one narrower.
6. **The one-sentence test.** "The last resort still needs the join and width menders, so they stay until their rules move into
   the placer" - D35's needed route; it raises no question.
7. **The next step is a measurement.** The landing cohort with `settle_joins` and `settle_widths` back in the last resort and
   the rest of the cut kept: does it return to 54 of 54?
8. **Routes measured?** None offered: the measurement first.
9. **After a ruling.** None yet.

### T31 conversion C1 (2026-10-26): one width a way, asked where the orphan link is laid

D11's conversion of `settle_widths`, which only the last resort still asks (T41). Measured first (observed 2026-10-25; method:
the refusal manifests `/tmp/l7r-refused/Audit-10-*.json`, `Audit-37-*.json` of the cut probe, T31 part B): every `width_steps`
joint on seeds 10 and 37 is a `join-orphans` link (6 ft) meeting a narrower lane end to end (a 3 ft skeleton arm, a 5 ft way) -
`_join_orphan_ways` drew the link at the widest way within `_LANE_JOIN_FT`, so where the link CONTINUES a lane from its end it
steps. The rule (`law.width_steps`, 0081's one width a way) is asked by that placer: a link whose end meets another lane's end
takes that lane's width (the orphan's end first); a link meeting only treads (tees, where a step is lawful) keeps the widest way
within reach, as before. Then `settle_widths` is probed off the last resort as R8 probed the rounds: the landing cohort and the
five pool maps. Needless: deleted with its dead closure. Still needed: the next placer the refusals name gets the same rule,
or the step is set down with its seeds and ruled (`make arbiter-ask`). Rendering: none (a link's width; no glyph).

<!-- plan-archive: T40 to T40 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->

### T41 (T31's second part, D35): the four map-moving steps and the last resort's three needless re-asks deleted

- **Approach**: T31's section, split so its second landing ticks only what it finished. Measured 2026-10-25 (method: the landing
  cohort, `make cohort-landing JOBS=3`, record `dev/cohort-log/20261025T234826Z-diagram-backlog-3803029.json`, and `make map` on
  the five pool hamlets compared with `git diff`): with `square_every_crossing`, `settle_shapes`, `settle_way_outs` and
  `settle_widths` out of `STEPS`, and `settle_husks`, `settle_street_ends` and `prune_the_tree` out of `last_resort`, 54 of 54
  pass; Inashiro, Kashikawa and Sawada move in their drawing order (`z`) alone, every lane's points unchanged, and one Kashikawa
  lane's width 5 -> 6 ft, the lane law still kept (the settle refuses a map that breaks it). Cutting `settle_joins` and
  `settle_widths` from `last_resort` as well refused seeds 10, 25 and 37 (`width_steps`, `joins_short`: T31 part B), so those
  two stay in `last_resort` - NEEDED, owed D11's conversion under T31. The fourteen names `make dead-closure` then found dead
  are deleted with their tests. T31 keeps the six needed steps and the last resort's `settle_joins` and `settle_widths`.
  Rendering: none (no glyph changes; three pool maps redrawn in a new order).

### T41 Approach (checklist part A)

1. **The goal, in the world.** The settle's rounds no longer run the four steps the placers already keep, nor the last resort
   the three re-asks it does not need, and no code they alone used survives.
2. **The constraints.** D35, D23, D11; the fixed and pinned seeds; the pool maps held to the lane law.
3. **Where each comes from.** G: the GM 2026-10-25 ("switch off the 16 repair steps"). O: the measurement above.
4. **Do they describe the world here?** Measured (the landing cohort and the five pool maps).
5. **The order.** After T40; before T31's conversions of the needed steps.
6. **The exits.** The landing cohort and the pool gate green: landed. Red: set down with its seeds (D23).
7. **The search smell.** None: one removal measured, then one narrower (T31 part B).
8. **The budget.** One landing.
9. **Done, measured.** The four out of `STEPS`, the three out of `last_resort`, the fourteen dead names gone, `make land` green.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.


### T42 (T31's conversion C1, D11): one width a way, asked where the orphan link is laid

- **Approach**: T31's conversion C1 (its decision in T31's section). Measured 2026-10-26 (method: the landing cohort, `make
  cohort-landing JOBS=3`, and `make map` on the five pool hamlets compared with `git diff`): with `link_width` asked by
  `_join_orphan_ways` (a link continuing a lane end to end takes that lane's width; tees keep the widest way within reach) and
  `settle_widths` out of `last_resort`, 54 of 54 pass, and Inashiro's and Kashikawa's one orphan link each is drawn 5 ft where
  it was 6, continuing a 5 ft way (Inashiro's commons redrawn round it). `settle_widths` and `rewidth`, left dead, are deleted
  with their tests; the fragments test they shared is kept on its own. Rendering: none (a link's width).

### T42 Approach (checklist part A)

1. **The goal, in the world.** A link joining an orphan piece is drawn at the width of the way it continues, so no way changes
   width at a bare joint and nothing widens it afterwards.
2. **The constraints.** D11, D35; `law.width_steps` (0081: one width a way); the fixed and pinned seeds; the pool maps.
3. **Where each comes from.** R: 0081's one width a way. G: the GM 2026-10-25 (the repairs replaced by placing correctly). O: the measurement.
4. **Do they describe the world here?** Measured: every width step the cut probe refused was such a link.
5. **The order.** After T41; the first of T31's conversions.
6. **The exits.** The landing cohort and the pool gate green: landed. Red: set down with its seeds.
7. **The search smell.** None: one rule moved into one placer.
8. **The budget.** One landing.
9. **Done, measured.** `link_width` asked at the link, `settle_widths` gone, `make land` green.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.


### T46 part B (2026-10-26T05:20Z)

The trigger: cohort@20261026T051100Z, seeds 11, 12, 23, 29, 901 and 903 newly failing - the probe of the end trim's street call.

1. **What exactly is refusing?** `dangling_ends` at a skeleton lane on six linear seeds: with `tidy_lane_ends(..., streets=True)`
   off, a row's street runs on past its last farm. The probe never landed; T46 keeps the call.
2. **A3 again.** O: the lane law's dangling-end rule; R: 0033's row street.
3. **A4 again.** It describes the map here: `lay_row_streets` lays the street long and the trim cuts it back.
4. **Moving something placed earlier to suit something later?** No: the trim was restored, nothing moved.
5. **Tuning or changing?** Neither: one probe, then the call kept and its conversion filed.
6. **The one-sentence test.** "The street trim is a repair still needed; T47 lays the street to its last farm" - no question.
7. **The next step is a measurement.** T46 lands as measured with the call kept; T47 measures its own conversion.
8. **Routes measured?** One route: keep and convert.
9. **After a ruling.** The plan review ruled CLEAR on T46/T47 with this route.

<!-- plan-archive: T43 to T41 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->

### T44 (T31 C2, the round arbiter's accept on ask:417-T31-C2-regression): the access tree drawn first; `settle_joins` deleted

- **Approach**: land `evidence/c2/tree-first-no-joins.patch` as the ruling says (binding, 2026-10-26): measured, the landing cohort
  54 of 54, the five pool maps passing `test_village_passes_gate` (Inashiro, Kuwabata and Sawada move), the pre-change fresh block
  7 of 48 before and after (723789 newly green, 723775 newly red - `WebRefused`, `needle_loops` between two access lanes - the
  ruling's waiver). Before landing: the probe comment made a plain one; `settle_tree` run once a map (if `settle_reach`'s call is
  then redundant, probe it off and remove it); `settle_joins` deleted with its tests if nothing else calls it; the fresh rate
  recorded with the landing (D11). Blocked first on the arbiter's tooling fix (the roll census counting the CLI test's re-roll of
  Inashiro as a second roll: narrow it to count each roll once, its test pinning that - `make arbiter-fix-done`).
  Rendering: none.


### T44 Approach (checklist part A)

1. **The goal, in the world.** The households' ways stand before any other lane is laid, so a link never loses the way it joined
   and nothing carries it back afterwards.
2. **The constraints.** D11, D35, FR-008; the round arbiter's accept on ask:417-T31-C2-regression (binding, with seed 723775's waiver).
3. **Where each comes from.** G: the GM 2026-10-25 (repairs replaced by placing correctly). O: the C2 trace and probes.
4. **Do they describe the world here?** Measured: the trace on seed 25; the landing cohort; the fresh block; the pool gate.
5. **The order.** After the arbiter's tooling fix (landed: a pool map obtained once a test); before T45.
6. **The exits.** FR-008 green: landed with the fresh rate recorded (7 of 48). Red: set down.
7. **The search smell.** One probe the arbiter's step (b) named - `settle_reach`'s own `settle_tree` call off - measured
   2026-10-26 on the fresh block from seed 723759: 8 of 48, seed 723790 newly failing; restored, 723790 passes. The call stays:
   the tree is drawn again after the cuts, not merely twice.
8. **The budget.** One landing.
9. **Done, measured.** `settle_tree` first in `stage_web`, `settle_joins` and its closure gone, `make land` green.
10. **Before moving a constant.** n/a: `JOIN_BACK_PAD_FT` goes with its only user.
11. **Before fitting things into room.** n/a.

### T45 (FR-005, the round arbiter's ruling on ask:417-T31-C2-regression): the needle rule asked where a tree lane is drawn

- **Approach**: `law.needle_loops` asked of the candidate where `lanes_of` draws a tree lane, so two household ways never close a
  sliver between them (fresh seed 723775 under the tree-first order: access lanes 1 and 2). Its first step, per the ruling: read
  `needle_loops`' sliver threshold in the tunables record (`make tunables`) - if it is unresearched, research it first (the
  result recorded in the tunables record), then proceed by what the research finds; if it is ours, moving it is tried before
  anything more elaborate, judged by the cohort, the pinned rows and the pool maps, never by seed 723775 passing. Never iterated on 723775 inside C2 (D11). Rendering: none.
- **The threshold, read 2026-10-26** (method: `law.py` `NEEDLE_LOOP_FT` and its claim): 20 ft mean width, `CONVENTION` - a map
  drawing convention calibrated on two settlement-reviews (Sawada's 16 ft triangle read as a street forking round nothing); ours,
  not a research figure. Not moved: the needle seed 723775 makes is 3 ft wide, far under any value the convention could take.
- **The geometry, measured 2026-10-26** (method: seed 723775 rolled on main at T44, `make cohort N=1 SEED=723775`, the refusal's
  manifest polygonized with shapely as `law.needle_loops` does): the one needle is a face of 66 sq ft, mean width 3.0 ft, at the
  connector's start (1503-1520, 1252-1263), bounded by access lanes 1 and 2 - both households' ways end on the connector's start,
  lane 1's last leg running about 7 ft beside lane 2's last stretch. **The rule asked at lay**: in `lanes_of`, a tree lane whose
  carried end would close a needle (`law.is_needle`) with a tree lane already drawn ends instead on that lane's tread at the
  nearest point, a tee - the way joins the way beside it rather than running on beside it to a shared end (0081's doubled way,
  drawn as one). Measured on the landing cohort, the fresh block from seed 723759 and the pool maps.

### T45 Approach (checklist part A)

1. **The goal, in the world.** No two households' ways close a sliver of grass between them: a way that would run on beside
   another to a shared end ends on that way instead.
2. **The constraints.** FR-005, D11; `law.needle_loops` (a 20 ft CONVENTION); the arbiter's ruling on ask:417-T31-C2-regression.
3. **Where each comes from.** R: 0081's doubled way drawn as one. G: the GM 2026-10-25. O: the measured needle on seed 723775.
4. **Do they describe the world here?** Measured (observed 2026-10-26 UTC; method: seed 723775 rolled on main at T44, the refusal's
   manifest polygonized as `law.needle_loops` does - T45's section): the needle a face of mean width 3.0 ft at the connector's
   start, bounded by two access lanes.
5. **The order.** After T44 (the tree first); its own task, not iterated inside C2.
6. **The exits.** FR-008 green: landed, its fresh rate recorded. Red: set down.
7. **The search smell.** None: one rule asked at one placer (`lanes_of`, `off_the_needle`).
8. **The budget.** One landing.
9. **Done, measured** (observed 2026-10-26 UTC; method: `make cohort-landing JOBS=3`, `make cohort N=48 SEED=723759 FRESH=0 JOBS=3`,
   `make map` on the five pool hamlets): 54 of 54; the fresh block 7 of 48, the same seven (723775 now refused on `joins_short`
   at a skeleton end, its needle gone); no pool map moved.
10. **Before moving a constant.** One value, `law.NEEDLE_LOOP_FT` (20 ft mean width, a CONVENTION), read and kept: it was set
   to catch the 16 ft triangle two settlement-reviews read as a street forking round nothing - the 16 ft is the example it was
   calibrated on, not a second value - and the measured face (3.0 ft, item 4's run) is under it either way. `off_the_needle`
   asks the law's own predicate (`law.is_needle`) and reach (`law.NEEDLE_LOOP_FT / 2`), so the placer and the finished-map check
   share one implementation (SC-003).
11. **Before fitting things into room.** n/a.

### T46 (T31 C2's probe step, D35): five web passes deleted once the households' ways are drawn first

- **Approach**: C2 named it (T31's section): with the access tree laid first (T44), the passes that repaired after the web was
  laid are probed off. Measured 2026-10-26 UTC (method: a detached worktree at T45's tree, each off alone with `make
  cohort-landing JOBS=3`, then all off together with `make cohort-landing JOBS=3`, `make cohort N=48 SEED=723759 FRESH=0 JOBS=3`
  and `make map` on the five pool hamlets): `settle_defer` out of `STEPS`, the orphan joins (`_join_orphan_ways`, twice), the end
  trims (`tidy_lane_ends`, the two non-street calls), the dangling-end sweeps (`_sweep_dangling_ends`, twice) and the doubled-tail
  sweep (`_sweep_doubled_tails`) - each alone 54 of 54; all together 54 of 54 and the fresh block 7 of 48, the same seven.
  Inashiro, Kashikawa and Sawada move: Kashikawa drops a 492 ft orphan link and a 410 ft lane and the settle draws a 272 ft field
  way in their place, every house and the field still reached. The fourteen names `make dead-closure` then found dead (T42's
  `link_width` among them, its link gone) deleted, with the tests whose BODY calls one (the arbiter's rule on T44). `settle_defer`
  stays defined: `settle_tree` asks it. The end trim's STREET call (`tidy_lane_ends(..., streets=True)`, a row map's) stays and is
  NEEDED, measured 2026-10-26 UTC (method: it alone off, `make cohort-landing JOBS=3`): 48 of 54 - six linear seeds (11, 12, 23,
  29, 901 among them) refused `dangling_ends`, a row's street running on past its last farm. It is a repair: the street is laid
  long and cut back. Its conversion, the street laid ending at its last farm where `lay_row_streets` lays it, is T47's.
  Rendering: none (no glyph; three pool maps redrawn).

### T46 Approach (checklist part A)

1. **The goal, in the world.** Nothing mends the web after it is laid: the households' ways stand first and the rest is laid
   onto them.
2. **The constraints.** D35, D23, FR-004, FR-008; the arbiter's rule that a test goes only on what its body calls.
3. **Where each comes from.** G: the GM 2026-10-25 (the repairs replaced by placing correctly). O: the probes above.
4. **Do they describe the world here?** Measured: each pass alone and all together, fixed, pinned, fresh and pool.
5. **The order.** After T44 (tree first) and T45 (the needle rule); before the settle's remaining steps.
6. **The exits.** FR-008 green: landed with its fresh rate. Red: set down.
7. **The search smell.** None: one probe a pass, then all together.
8. **The budget.** One landing.
9. **Done, measured.** The five gone with their dead closure, `make land` green.
10. **Before moving a constant.** n/a: the constants go with their only users.
11. **Before fitting things into room.** n/a.


### T47 (FR-004, T46's measurement): a row's street laid ending at its last farm, and the street trim deleted

- **Approach**: measured 2026-10-26 UTC (T46: the end trim's street call alone off, `make cohort-landing JOBS=3`): six linear
  seeds refuse `dangling_ends` - `lay_row_streets` lays each street past its last farm and `tidy_lane_ends(..., streets=True)`
  cuts it back. The rule (`law.dangling_lane_ends`, 0033: a row's street ends at its last farm, or runs off the map as the road
  into it) asked where the street is laid, then the street call probed off and deleted as T46 deleted the others. Rendering:
  none.


- **Probed 2026-10-26 UTC** (method: a detached worktree at T49's tree, `make cohort-landing JOBS=3` each; the trim's street call
  off, 48 of 54 before): (P2) the street spanning its end farms' center projections, no half frame past them (`row_reach`'s pad
  0): 52 of 54 - seed 904's one-farm second street came out 24 ft (cut at whole 8 ft vertices of the planned line, under
  `_WEB_MIN_FT`) and was not drawn (`street_not_drawn`); seed 04's second street ended 132 ft from any house (`dangling_ends`).
  (P3) the same keeping `run_lanes_on_to_the_bund` (which only `tidy_lane_ends` calls): identical, 52 of 54. (P4) the span
  between the end farms' FRONT-DOOR projections, ending exactly there, at least 30 ft: 52 of 54 - seed 12's end farm's door
  path is routed round its grove and meets the street 72 ft from the door's projection (`dangling_ends` at the street's end),
  and seed 904's 30 ft street still fell short and a 32 ft floor only moved its failure to a skeleton end. FINDING: a street's
  lawful end is where its end farm's door path meets it, which is known only once that path is laid (after the street, which it
  joins), so no span computed from the farms alone ends lawfully. OPEN: the end made a junction by construction - an end farm's
  door path laid to the street's end point first (`lay_door_paths`), the street spanning the door projections; if that cannot
  land green, the failing seeds are recorded and the task set down, a claim that it cannot be placed correctly being an exception
  ruled through `make arbiter-ask` (D11, D35), never the trim kept. Set down 2026-10-26 for the settle's needed steps; its probes'
  edits are not on main.

### T48 (T31's D11 probe, D35): two settle steps deleted that alone off move no pool lane and no verdict

- **Approach**: after T44-T46 the settle's remaining repairs are probed off one at a time. Measured 2026-10-26 UTC (method: a
  detached worktree at T46's tree, each off ALONE with `make cohort-landing JOBS=3`, `make cohort N=48 SEED=723759 FRESH=0
  JOBS=3` - the block rolled before T44, baseline failing 723767 723770 723775 723777 723794 723799 723804 - and `make map` on
  the five pool hamlets, each manifest diffed field by field against HEAD):
  - `square_every_crossing` alone off: 54 of 54, the fresh block's verdicts identical to HEAD's seed by seed, no pool lane
    moved - Inashiro's manifest moves only in the settle's own tally (`meta.web_settle.changed` 19 -> 18). NEEDLESS (D35). The
    tree's lanes (`tree.lanes_of`, the seating's `Lawful.squared`), the door paths and the connector are squared as laid
    (`squaring.square_run`); the skeleton arms (`web/skeleton.py`), the web lanes (`fabric._draw_web`), the bund and track spurs
    and the field way (`reach.py`) are NOT, and each OWES its squaring as laid, unconditionally - T49 (FR-005), in D11's order
    after this task; until it lands the law (`law.oblique_crossings`) is asked of the finished web as before (on no measured
    map does one of them cross water off square), never this step back. T45's needle rule now holds fresh seed 723805,
    for which T43 had restored it.
  - `settle_fragments` alone off `STEPS`: the same - 54 of 54, the same seven, Inashiro's tally alone (19 -> 18). NEEDLESS.
    It stays defined: the last resort asks it.
  - Both together (this task's change, measured in the clone 2026-10-26 UTC): `make cohort-landing JOBS=3` 54 of 54; the fresh
    block 47 of 54, its seven failures identical to HEAD's seed by seed and check by check (HEAD rolled on the same block in a
    detached worktree; 723775 is refused `joins_short` at a skeleton arm's end on both, the block's older record's `lane_knots`
    being from before T44 - its conversion stays owed); Inashiro's tally 19 -> 17, nothing else on any pool manifest.
  - Measured NEEDED, kept, conversions owed (T31, D11): `settle_ends` alone off moves Kuwabata's access lane (66 -> 69 ft) and the
    last resort then drops a lane on Inashiro; the tree's own `settle_defer` call alone off leaves the last resort dropping a lane
    on Kuwabata and Sawada (its work moved into the backstop, not gone); `settle_network` (36 of 54 without it), `settle_knots`
    (40 of 54) and the web's `trim_lane_stubs` (fresh seed 723805 refused without it).
  - The last resort itself (`last_resort.py`, which asks `settle_reach`, `settle_knots`, `settle_defer`, `settle_network` and
    `settle_fragments`) still repairs a laid web: it stays OWED under FR-004 as FR-007's backstop, converted once the steps it
    re-asks are, never an exemption.
  `make dead-closure` then finds `square_every_crossing` alone dead; it goes with the one test whose BODY calls it (the arbiter's
  rule on T44). Rendering: none (no glyph; no lane redrawn).

### T48 Approach (checklist part A)

1. **The goal, in the world.** Nothing mends the web after it is laid: each way is laid lawful, square at its crossings.
2. **The constraints.** D35 (needless = alone off, no verdict and no pool manifest moved), D23, FR-004, FR-008; the arbiter's rule
   that a test goes only on what its body calls; the same-block rule (a pre-change fresh block rolled seed by seed).
3. **Where each comes from.** G: the GM 2026-10-25 (the repairs replaced by placing correctly). O: the probes above.
4. **Do they describe the world here?** Measured: each repair alone - fixed and pinned seeds, the pre-change fresh block, and
   every pool manifest diffed field by field - then the two together.
5. **The order.** After T46; it moves no map's lanes, so it may precede T47 (D11: tasks that move no map first).
6. **The exits.** FR-008 green: landed with its fresh rate. Red: set down.
7. **The search smell.** None: one probe a repair, then the two together.
8. **The budget.** One landing.
9. **Done, measured.** The two gone, `square_every_crossing`'s closure with it, the fresh block 723759 the same seven, `make
   land` green.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: T49 to T48 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->

### T50 (T31's D11, settle_network's first conversion): the track's field spur no longer laid unjoined, and the bund's carry-on squared

- **Approach**: `settle_network` (36 of 54 without it) drops every lane off the connector's network. Measured 2026-10-26 UTC
  (method: a detached worktree at T49's tree, the lanes off the network logged at `settle_the_web`'s entry and the lanes
  `settle_network` drops, `make cohort-landing JOBS=3`): 32 of the 54 maps reach the settle with lanes already off the network -
  laid unjoined, not cut loose by a repair. By placer: the track's field spur (`stage_track`, laid before the web, "judged against
  the finished network" by the sweeps T26 deleted) on 28 maps; web lanes of the skeleton pass on 18; skeleton arms on 13; the
  bund's field branch on 4. This task takes the first: the spur is laid before anything it could join is on the map (the
  connector is drawn after it, the web two stages later), so on 28 maps it stood alone until `settle_network` dropped it, and the
  field was reached by the web's own way onto the bund (`a_way_onto_the_bund`: run on, branch) or the settle's field way
  (`settle_field`). Probed off (the spur not drawn): 53 of 54 - seed 42's door path, carried on to the bund over the brook by
  `bund.carry_on`, crossed it 23.6 degrees off square (`oblique_brook`): `carry_on`'s step is squared against the drawn channels
  only (`squared_step`), and a sixth placer T49 missed. With `carry_on` asking `squaring.square_run` of the run it lays or
  lengthens too: 54 of 54, the fresh block from 723759 identical to HEAD seed by seed, the pool passing - Inashiro's field path
  `joined` -> `run_on` and Kashikawa's `joined` -> `branch` (their lanes as drawn unchanged), Mizuguchi's field way replaced by
  a branch 70 ft along the lane, Sawada's lanes unchanged; the last resort drops one lane on Kashikawa and Sawada where
  `settle_network` dropped one before (their drawn lanes identical). The spur's code and the names it leaves dead (`make
  dead-closure`) go with the tests whose BODY calls one. The other placers' unjoined lanes (the skeleton pass's web lanes, the
  arms, the bund branch) are the next conversions, measured the same way. Rendering: none (no glyph; four pool maps redrawn).

### T50 Approach (checklist part A)

1. **The goal, in the world.** Each way is laid joined to the ways it serves (the lane law's one network, `law.lane_networks` at
   `law.JOIN_TOL`, as `settle.ends.connector_component` reads it); nothing is laid only to be dropped.
2. **The constraints.** D35, D11, D23, FR-004, FR-005, FR-008; 0014 (the field path runs on to the bund), 0035 and 0084 (a
   crossing square to the water); the arbiter's rule that a test goes only on what its body calls; the same-block rule.
3. **Where each comes from.** G: the GM 2026-10-25 (the repairs replaced by placing correctly). R: 0014, 0035, 0084. O: the
   probes above.
4. **Do they describe the world here?** Measured: fixed, pinned, the pre-change fresh block and the pool, field by field.
5. **The order.** After T49 (the placers squared); before the other unjoined placers.
6. **The exits.** FR-008 green: landed with its fresh rate. Red: the failing seeds recorded and the task set down, a claim that it
   cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None: one placer, one squaring gap the probe found.
8. **The budget.** One landing.
9. **Done, measured.** The spur not laid and its dead code gone, `carry_on` squared, `make land` green.
10. **Before moving a constant.** n/a: the spur's constants go with their only users.
11. **Before fitting things into room.** n/a.


### T52 Approach (checklist part A)

1. **The goal, in the world.** Every search by trial in the engine known and costed before any is converted: each placer that
   lays a candidate out in full and then refuses it, and each check asked again of a whole network as it grows.
2. **The constraints.** FR-012, FR-013, User Story 5; the GM 2026-10-26 (`request.md` "Speed first").
3. **Where each comes from.** The GM's words; the session's measurements of 2026-10-26 (`spec.md` User Story 5).
4. **Do they describe the world here?** Measured first: `make perf-fanout` (every stage, both sizes) and `make perf-profile` of
   each stage at the survey's larger size, on the engine as it stands.
5. **The order.** First of the speed tasks (FR-013): it ranks the rest.
6. **The exits.** Green: `inventory/trial.md` lists each site with where it is, what it lays out before refusing, its calls and
   seconds at 40 households, and the task that converts it; every site over 50,000 calls has a task.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: a measurement and a list.
8. **The budget.** No engine change; one commit.
9. **Done, measured.** The list's rows against the survey's chains.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the sites found | `make perf-fanout`, `make perf-profile` per stage |
| each site's cost | its calls and profiled seconds in the record |


### T53 Approach (checklist part A)

1. **The goal, in the world.** The same lane web, its whole-network checks (`served_network`, `lanes_share_tread` and the rest the trial inventory names) asked of the lanes a step added or moved, not of every pair of lanes again.
2. **The constraints.** FR-012, FR-013, User Story 5, FR-008; the lane law's rules unchanged (FR-004).
3. **Where each comes from.** `spec.md` User Story 5's measurement (the check asked of every pair of lanes at each of its calls); the trial inventory.
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage) on the then-current engine scopes the
   task to the chains that still stand (FR-012).
5. **The order.** Fourth of the speed tasks, after the settle's probe (T31) and the web laid by the law (T06), which may delete some of these checks' callers (FR-006): the largest single search by trial left in the web.
6. **The exits.** Green: the web's whole-network checks asked incrementally, their calls at least tenfold down, the fixed cohort and the pinned rows passing (FR-008), the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the same predicate asked of a smaller set; an index the plan names (`settlement/_geom/indexes.py`).
8. **The budget.** One landing per chain group; a group that moves a map judged by the cohort.
9. **Done, measured.** Each chain's calls before and after from `make perf-fanout`, recorded in `research/`.
10. **Before moving a constant.** n/a: the rules' figures stay as they are.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the chains re-scoped | `make perf-fanout` (every stage) |
| each converted | its calls in `make perf-fanout`, `make maps-moved` |
| no seed regressed | `make cohort-landing` (in `make land`) |


### T54 Approach (checklist part A)

1. **The goal, in the world.** The same household ways, each household's candidate exits refused by the tests that need no traced way - its corridor's ground, its own parts, the tree's reach - before any is traced, pulled taut and judged by the ways tree.
2. **The constraints.** FR-012, FR-013, User Story 5, FR-008; the ways' admission rules unchanged (the tree's `judge` stays the verdict).
3. **Where each comes from.** `spec.md` User Story 5's measurement (the households' ways traced and judged); the trial inventory.
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage) on the then-current engine scopes the
   task to the chains that still stand (FR-012).
5. **The order.** After the web's laying (the households' ways are the web's first layer).
6. **The exits.** Green: `gap_ways`' admission chain at least tenfold down, the fixed cohort and the pinned rows passing (FR-008), the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the candidates' cheap refusals asked as one array or index pass; no new search.
8. **The budget.** One landing per chain group; a group that moves a map judged by the cohort.
9. **Done, measured.** Each chain's calls before and after from `make perf-fanout`, recorded in `research/`.
10. **Before moving a constant.** n/a: the rules' figures stay as they are.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the chains re-scoped | `make perf-fanout` (every stage) |
| each converted | its calls in `make perf-fanout`, `make maps-moved` |
| no seed regressed | `make cohort-landing` (in `make land`) |


### T55 Approach (checklist part A)

1. **The goal, in the world.** The same homesteads seated, a candidate seat's refusals that need no layout - the envelope off the ground, the placed boxes, the region - asked of every candidate at once, so a homestead is laid out in full (its reach, its four garden sides, its fixtures) only at a seat that can stand; the per-seat rolls kept (feature 297 plan C, research R9).
2. **The constraints.** FR-012, FR-013, User Story 5, FR-008; R4's per-seat rolls (feature 427 T12, `ask:427-T12-r4`).
3. **Where each comes from.** `spec.md` User Story 5's measurement (the seating's placements and reach measures); feature 427's `research/t12-r4.md`; the trial inventory.
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage) on the then-current engine scopes the
   task to the chains that still stand (FR-012).
5. **The order.** After the households' ways, before the field.
6. **The exits.** Green: the seating's full layouts at least tenfold down, the fixed cohort and the pinned rows passing (FR-008), the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the refusals asked of the candidate set through the seat region (feature 297) and the placed-box index.
8. **The budget.** One landing per chain group; a group that moves a map judged by the cohort.
9. **Done, measured.** Each chain's calls before and after from `make perf-fanout`, recorded in `research/`.
10. **Before moving a constant.** n/a: the rules' figures stay as they are.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the chains re-scoped | `make perf-fanout` (every stage) |
| each converted | its calls in `make perf-fanout`, `make maps-moved` |
| no seed regressed | `make cohort-landing` (in `make land`) |


### T56 Approach (checklist part A)

1. **The goal, in the world.** The rest of the trial inventory's sites converted, largest first: the wells' registry admission, the bamboo strips, the open-ground patches, the grove clumps and the notice board's seats, as the inventory ranks them (`inventory/trial.md` rows 6-11).
2. **The constraints.** FR-012, FR-013, User Story 5, FR-008; each placer's rules unchanged.
3. **Where each comes from.** The trial inventory.
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage) on the then-current engine scopes the
   task to the chains that still stand (FR-012).
5. **The order.** After the field, before the overlap registry's resync.
6. **The exits.** Green: each site converted, its chain at least tenfold down (a site already gone when item 4 re-measures counts), the fixed cohort and the pinned rows passing (FR-008), the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: each site's cheap refusals asked of its candidate set at once.
8. **The budget.** One landing per chain group; a group that moves a map judged by the cohort.
9. **Done, measured.** Each chain's calls before and after from `make perf-fanout`, recorded in `research/`.
10. **Before moving a constant.** n/a: the rules' figures stay as they are.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the chains re-scoped | `make perf-fanout` (every stage) |
| each converted | its calls in `make perf-fanout`, `make maps-moved` |
| no seed regressed | `make cohort-landing` (in `make land`) |


### T57 Approach (checklist part A)

1. **The goal, in the world.** Where SC-009 stands once the speed tasks have landed, before the correctness tasks start.
2. **The constraints.** SC-009, FR-013.
3. **Where each comes from.** `spec.md` SC-009, the GM 2026-10-26.
4. **Do they describe the world here?** Yes: feature 427's start survey is committed (`dev/perf-log/`), so the cut compares.
5. **The order.** Last of the speed tasks, first before the correctness tasks.
6. **The exits.** Green: SC-009 met, measured, and reported.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: a measurement.
8. **The budget.** One survey, one snapshot.
9. **Done, measured.** `make perf-fanout` at 40 households against feature 427's start; `make perf LABEL=417-speed SCALING=1` for the stage times, reported, gating nothing.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the calls | `make perf-fanout` |
| the stage times | `make perf LABEL=417-speed SCALING=1` |

### T06 Approach (checklist part A)

1. **The goal, in the world.** The same lane web, each ordinary lane admitted whole by the lane law before it is drawn, so no pass after the lay and no settle step repairs it.
2. **The constraints.** FR-004, FR-006, FR-013, SC-002.
3. **Where each comes from.** the inventory (`inventory/ways.md`, G2); T26's and T31's measured deletions; D5, D11, D35.
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage) on the then-current engine scopes the task to what still stands (FR-012).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): third of the speed tasks, after the trial inventory and the settle's probe (T31), before the web's whole-network checks (T53).
6. **The exits.** Green: the web laid by the law with no repair pass left, its calls measured before and after, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the law's predicates asked of a candidate lane before it is drawn.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T12 Approach (checklist part A)

1. **The goal, in the world.** The same paddy cells, cut where the ring rules admit them: no cell cut then merged or left bare, no ring split and welded after, no twin or stub drawn then dropped, the needle one predicate.
2. **The constraints.** FR-004, FR-005, FR-013.
3. **Where each comes from.** the inventory (`inventory/homesteads-water.md`, G9); feature 427 T09's measurements (`specs/427-call-volume-refactors/research/t09-water.md`).
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage) on the then-current engine scopes the task to what still stands (FR-012).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): seventh of the speed tasks, after the homesteads (T55), before the field's courses (T11).
6. **The exits.** Green: the cells cut by their rules with the settle's merges gone, the field stage's calls measured before and after, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the ring rules asked of a cell before it is cut.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T11 Approach (checklist part A)

1. **The goal, in the world.** The same brook, sink, field and polder, placed by their rules: no course repaired then judged, the field not judged as a finished net, the polder's wander held to its rule.
2. **The constraints.** FR-004, FR-006, FR-007, FR-013.
3. **Where each comes from.** the inventory (`inventory/homesteads-water.md`, G8).
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage) on the then-current engine scopes the task to what still stands (FR-012).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): eighth of the speed tasks, after the paddy cells (T12).
6. **The exits.** Green: the courses placed by their rules with the repair gone, the field stage's calls measured before and after, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: each course's rules asked of its candidate before it is laid.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T14 Approach (checklist part A)

1. **The goal, in the world.** The same overlap registry, its per-stage resync's checking and its record-time refusal taken out of the run: each placer asks the overlap matrix of its candidate before it is placed, the overlap rule's finished-map check runs in the cohort and the tests only, calling the same predicate (FR-006), and the hand mirrors made one.
2. **The constraints.** FR-006, FR-013.
3. **Where each comes from.** the inventory (`inventory/cross.md`, G11); T18's deletions.
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage) on the then-current engine scopes the task to what still stands (FR-012).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): tenth of the speed tasks, before the checkpoint (T57).
6. **The exits.** Green: the resync's checking and the record-time refusal gone from the generator, the finished-map overlap check in the cohort and the tests calling the placers' predicate, the hand mirrors one, the calls measured before and after, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the matrix asked by each placer of its candidate.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T16 Approach (checklist part A)

1. **The goal, in the world.** The lane rules whose copies differ, each made one predicate at the rule's recorded value - or, where the downloaded research checked first and a research pass where nothing was ever looked for find no recorded
   value (the GM 2026-10-25: "if our research findings do not indicate that things were any particular way"), at a chosen value
   labeled a GUESS, or a tunable knob (the GM 2026-10-25: "make it a tunable knob, or ... whatever is algorithmically easier"; the doubled tail at the 20 degrees the GM accepted, documented as an approximation), never set down for the GM.
2. **The constraints.** FR-006, FR-008.
3. **Where each comes from.** the inventory (`inventory/ways.md`, G1); the GM's 2026-10-25 words on arbitrary values (`request.md`), which supersede D11's hold for this task.
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): first of the tasks after the speed tasks.
6. **The exits.** Green: each differing copy made one, at its recorded value or a labeled GUESS, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one predicate where several stood.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T07 Approach (checklist part A)

1. **The goal, in the world.** The ways' drops and refusals gone: no ordinary lane dropped, no `WebRefused` or `NoDryExit`, no spur given up, no angle rule waived, no wood seat released - room within the research the remedy.
2. **The constraints.** FR-007, SC-001.
3. **Where each comes from.** the inventory (`inventory/ways.md`, G3); FR-007's room before repair.
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the lane rules made one (T16).
6. **The exits.** Green: the drops and refusals the inventory names gone, the fresh block's ways failures measured before and after, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: room, not a new search.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T08 Approach (checklist part A)

1. **The goal, in the world.** Seating room: no `SiteRefused` on a short margin, no dry-spell give-up, no rank round's drop, no pinched passage - more room within the research the remedy.
2. **The constraints.** FR-007, SC-001.
3. **Where each comes from.** the inventory (`inventory/homesteads-water.md`, G4); the room-before-packing rule (the GM 2026-10-12).
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the ways' drops (T07).
6. **The exits.** Green: the seating's refusals the inventory names gone, the fresh block's seating failures measured before and after, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: room, not a new search.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T09 Approach (checklist part A)

1. **The goal, in the world.** The row village's rules asked of its candidates: `row_rules`, `water_rules` and `bamboo_mismatch` by the row placer, the wells' dry-household check out of the run.
2. **The constraints.** FR-005, FR-006, SC-001.
3. **Where each comes from.** the inventory (`inventory/homesteads-water.md`, G5).
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the seating room (T08).
6. **The exits.** Green: each rule asked by the row placer and its finished-map check its predicate, the fresh block's linear-form failures measured before and after, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the rules asked of a candidate row.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T10 Approach (checklist part A)

1. **The goal, in the world.** The grove rules asked by the grove placers: the five audit-only grove rules before placing, `fixtures_on_groves` and `gardens_east_shaded` one predicate each, the belt, copse and persimmon repairs deleted.
2. **The constraints.** FR-004, FR-005, FR-006, SC-001.
3. **Where each comes from.** the inventory (`inventory/homesteads-water.md`, G6); T17's first part.
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the row village (T09).
6. **The exits.** Green: the grove rules asked before placing and the repairs deleted, the fresh block's grove failures measured before and after, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the rules asked of a candidate clump.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T13 Approach (checklist part A)

1. **The goal, in the world.** The hinterland and land placed by their rules: no dike tree thinned after, no hole filled to a share in the run, the belt's ladder, the parcels, the marsh and the wet lanes asked before placing.
2. **The constraints.** FR-004, FR-006, FR-007, SC-001.
3. **Where each comes from.** the inventory (`inventory/rest.md`, G10).
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the grove rules (T10).
6. **The exits.** Green: the passes the inventory names gone, the fresh block's failures measured before and after, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the rules asked of a candidate.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T15 Approach (checklist part A)

1. **The goal, in the world.** The rest of the inventory placed by its rules: the labels' repair and least-cost seat, the beads dropped twice, the bridges' reseat and refusal, the byres' relaxed tiers, the wells' and pond stock's rules asked twice, the cluster's belt and dry-exit copies.
2. **The constraints.** FR-004, FR-005, FR-006, FR-007, SC-001.
3. **Where each comes from.** the inventory (`inventory/rest.md`, G12).
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the hinterland (T13).
6. **The exits.** Green: each site the inventory names converted, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: each rule asked of its candidate.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T27 Approach (checklist part A)

1. **The goal, in the world.** The track out drawn ending on the web, never stopping in open country past the households' ways.
2. **The constraints.** FR-004, SC-001.
3. **Where each comes from.** T19's probe and D27; research 0081 ("It never stops in open country").
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the rest of the inventory (T15).
6. **The exits.** Green: the six named fresh seeds' track ending on the web, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the track's end placed where its ways meet it.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T32 Approach (checklist part A)

1. **The goal, in the world.** The lanes and the track standing where the record puts them, where T29's passes A1, A2 and D found the code contradicting it.
2. **The constraints.** FR-008 (the research claims hold), SC-001.
3. **Where each comes from.** T29's passes A1, A2, D; the pages the task names (0014, 0035, 0037, 0055, 0084, 0089).
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the track (T27).
6. **The exits.** Green: each contradiction the task lists made to agree with the record or ruled by the arbiter, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the record's values, no search.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T33 Approach (checklist part A)

1. **The goal, in the world.** The homestead's parts standing where the record puts them, where T29's passes B, C and P1 found the code contradicting it.
2. **The constraints.** FR-008, SC-001.
3. **Where each comes from.** T29's passes B, C, P1; the pages the task names (0029, 0036, 0042, 0196).
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the lanes and track (T32).
6. **The exits.** Green: each contradiction the task lists made to agree with the record or ruled by the arbiter, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the record's values, no search.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T34 Approach (checklist part A)

1. **The goal, in the world.** The water and the fields as the record has them, where T29's passes P2a and P2b found the code contradicting it.
2. **The constraints.** FR-008, SC-001.
3. **Where each comes from.** T29's passes P2a, P2b; T36; the pages the task names (0013, 0020).
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the homestead's parts (T33).
6. **The exits.** Green: each contradiction the task lists made to agree with the record or ruled by the arbiter, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the record's values, no search.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T35 Approach (checklist part A)

1. **The goal, in the world.** The town's walls and wards as the record has them, where T29's pass P7 found the code contradicting it.
2. **The constraints.** FR-008.
3. **Where each comes from.** T29's pass P7; T36; the pages the task names (0087, 0151, 0160).
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the water and fields (T34).
6. **The exits.** Green: each contradiction the task lists made to agree with the record or ruled by the arbiter, the town tests and pool maps passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the record's values, no search.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T47 Approach (checklist part A)

1. **The goal, in the world.** A row's street laid ending at its last farm where `lay_row_streets` lays it, and the end trim's street call deleted.
2. **The constraints.** FR-004, SC-001.
3. **Where each comes from.** T46's claims round and measurement.
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the town (T35).
6. **The exits.** Green: the street laid to its end with the trim's call gone, the fixed cohort and pinned rows passing, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the street's end placed where it is laid.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T37 Approach (checklist part A)

1. **The goal, in the world.** The claims findings the claims gate carried on code a change left unchanged, each fixed in the code or the claim and re-checked.
2. **The constraints.** FR-008 (385 FR-013).
3. **Where each comes from.** the claims gate's carry (385 FR-013).
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the row street (T47), with the other carried findings.
6. **The exits.** Green: every finding the task names fixed and re-checked IN-STEP, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: a claim or a line at a time.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T39 Approach (checklist part A)

1. **The goal, in the world.** The claims findings the claims gate carried on code a change left unchanged, each fixed in the code or the claim and re-checked.
2. **The constraints.** FR-008 (385 FR-013).
3. **Where each comes from.** the claims gate's carry (385 FR-013).
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after T37, with the other carried findings.
6. **The exits.** Green: every finding the task names fixed and re-checked IN-STEP, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: a claim or a line at a time.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T51 Approach (checklist part A)

1. **The goal, in the world.** The claims finding the claims gate carried on `stage_track`'s way-in end, fixed in the code or the claim and re-checked.
2. **The constraints.** FR-008 (385 FR-013).
3. **Where each comes from.** the claims gate's carry (385 FR-013).
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after T39, with the other carried findings.
6. **The exits.** Green: the finding fixed and re-checked IN-STEP, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one claim.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T20 Approach (checklist part A)

1. **The goal, in the world.** The fresh block run inside `make land` before the push, any fresh failure refusing the landing, once a fresh block of 500 passes whole.
2. **The constraints.** FR-009, SC-005.
3. **Where each comes from.** FR-009; the GM 2026-10-24.
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the last engine task.
6. **The exits.** Green: `make land` refusing a landing one of whose fresh seeds fails, with a test that proves it on a seeded failure.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: tooling.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T21 Approach (checklist part A)

1. **The goal, in the world.** Every archetype form's seeds recorded per seed and diffed against HEAD, a newly red unrolled-form seed with no filed row or waiver refusing.
2. **The constraints.** FR-011, SC-006.
3. **Where each comes from.** FR-011; feature 394's request.
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): after the fresh block in the landing (T20).
6. **The exits.** Green: SC-006's two test landings, the refused one and the one a filed row lets land.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: tooling.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |

### T22 Approach (checklist part A)

1. **The goal, in the world.** The feature closed: 1,000 fresh seeds, T106's seat turn re-applied, the code-size delta, SC-009 measured, the feature report.
2. **The constraints.** SC-001, SC-004, SC-009, User Story 2.
3. **Where each comes from.** the spec's success criteria.
4. **Do they describe the world here?** Re-measured first: the inventory's rows for this task read against the then-current engine, and the latest fresh block's failures by cause (`make cohort-seeds`).
5. **The order.** In the speed-first order (FR-013; the GM 2026-10-26, `request.md` "Speed first"): last.
6. **The exits.** Green: SC-001 on 1,000 fresh seeds, SC-004's delta and SC-009 measured, the report written.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: measurement and the report.
8. **The budget.** One landing per group the task names; a group that moves a map judged by the cohort.
9. **Done, measured.** Its exit's measures recorded in `research/` beside the task.
10. **Before moving a constant.** Its research claim read first; a GUESS is a knob, free to move within the research (`make tunables`; the GM 2026-10-25).
11. **Before fitting things into room.** More room within the research first (the GM 2026-10-12, FR-007).

Each step measured alone:

| step | measured by |
|---|---|
| what still stands | the re-measure in item 4 |
| each change | `make maps-moved`, `make perf-fanout` |
| no seed regressed | `make cohort-landing` (in `make land`) |
