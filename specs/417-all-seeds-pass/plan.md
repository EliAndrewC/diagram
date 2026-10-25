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
  2026-10-24, background); 1,000 at T01 and at the close (~47 min, the same rate). SC-001's N is 500. The landing's own fresh block (FR-009) stays the cohort gate's 48. Rendering:
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

## Order

T01 measure (D1, D2). T02 the hold guard (D4) - small tooling, lands alone. T03 the inventory (D3) and the principle's draft
(D6). T04 onward the engine work in D5's order, one task per inventory group, each landed and followed by a fresh block of
500; their Approaches are added by plan-delta as each starts, numbered on from T04 as the inventory needs. Then the guards, the
two tasks after the last engine task: the fresh block before the push (FR-009), and every archetype form against HEAD (FR-011,
SC-006). The last task closes: 1,000 fresh seeds, T106's seat turn re-applied (User
Story 2), the code-size delta (SC-004), the feature report.

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

## T19 - the track out never stops in open country (T05's claims round, DRIFTED; FR-004)

### T19 Approach (checklist part A)

1. **The goal, in the world.** The track out runs from the settlement's own ways off the map: its inner end is ON a lane of
   the web, never in the grass short of one (0081: "It never stops in open country, which would read as a path to nowhere").
2. **The constraints.** `fabric._pull_back_to_service`, called once from `web/tidy.tidy_lane_ends` (the `kept_connector`
   branch; skipped where the connector starts at the way out's gate), walks the connector's inner end onto the nearest way.
   It leaves the end where it is in two cases (impl-drift, `evidence/impl-T05.txt`): nothing within `_LANE_JOIN_FT`, and a
   snap that would foul the fabric. `kept_connector` then keeps the unpulled run if the pulled one breaks through a
   building. Whether either case reaches a FINISHED map is not known: the settle runs after it (one network, the ways out).
   Measured 2026-10-25 from the five pool manifests (each connector's inner end to the nearest other lane): 0.0 ft on all
   six connectors.
3. **Where each comes from.** O: FR-004 (a pass that repairs a laid web is deleted, or its rule asked by the placer), the
   GM 2026-10-25 (D24), 0081's track-out entry.
4. **Do they describe the world here?** To be measured (D25).
5. **The order.** After T26, before the seed fixes (the GM).
6. **The exits.** Both delete the pull-back call, `_pull_back_to_service`, `kept_connector` and the tests only they
   exercise (FR-004). NEEDLESS (D25: no fixed, pinned or pool verdict moves with the call off, and no finished map's inner
   end is off the web): that alone, and the claim "the track meets the lanes" is moved to what makes the end touch. NEEDED:
   the deletion lands with D26's placer, never with a refusal.
7. **The search smell.** One probe off and one count; no tuning of `_LANE_JOIN_FT` or the fabric gap to make a seed pass.
8. **The budget.** About 3 min a probe (T26's probes, one-shot 2026-10-25: 48 fixed + 6 pinned seeds at 5 workers, then
   the five pool maps), 2 probes; a fresh block of 500 after the landing (D1), background.
9. **Done, measured.** `research.md` R6: the probe's verdicts, the count of inner ends left off the web (in the pull-back,
   and in the finished map), the change made, the landing cohort green, and the fresh block beside R3 and R5.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T19 Decisions

- **D24 (the GM lifts D11 for T19, 2026-10-25)**: the GM: "Changing behavior is fine as long as it is in line with our
  research, so T19 should be worked now before we start on the seed fixes, in the manner you suggest as the next step."
  Read as: T19 is worked now, before any seed fix, by the method the report proposed as the next step - T26's switch-off
  probe on the fixed seeds, the pinned rows and the pool, applied here to T19's own pass. It is not read as a go-ahead for
  the probe of the settle's steps the report also proposed; that goes back to the GM. The behavior may change where 0081
  says so. Rendering: none.
- **D25 (the probe, D22's form)**: in a detached worktree at HEAD, an environment switch that never lands (a) skips the
  `_pull_back_to_service` call (the connector kept as placed) and rolls `make cohort N=48 FRESH=0 JOBS=5` and `make map` on
  the five pool hamlets against the same roll with nothing off; and (b) with nothing off, counts each roll where the
  pull-back returns an inner end more than `JOIN_TOL` (4 ft, read 2026-10-25 from `ways/law.py:133` `JOIN_TOL = _TOUCH_GAP`
  and `ways/geom.py:51` `_TOUCH_GAP = 4.0`) from every other lane, and each FINISHED map (after
  `settle_the_web`) whose connector inner end is that far off the web, over the same seeds and a fresh block of 500. A
  case that never occurs in a finished map is closed by the settle, and the drift goes with the code. Rendering: none.
- **D26 (if NEEDED, the placer; SUPERSEDED by D27(b): the finished maps with the track off the web are drawn so by `settle_reach`, not the pull-back, and their placer is chosen with the GM in T27)**: the track is laid before the web (`stage_track`), so the connector is never moved
  after it is laid: the WEB meets it. Where the count finds a finished map with the track's inner end off the web, that end
  is a point the web's lay must reach - a run laid to it when the web is laid (`lay_reachable_runs`, beside the skeleton
  that already reads the connector as network), asked of `Lawful` before it is drawn like every web lane - and the
  pull-back's deletion lands with it. No pass after the lay re-lays the connector or the run, and no map is refused for it
  (constitution XIX, room before packing). Which seeds need it, and whether `lay_reachable_runs` already has room for the
  run, is what the count shows; a seed it cannot serve without room work is recorded and set down (D11). Rendering: map
  drawing convention (0081's track-out entry).
- **D27 (what the probe found, 2026-10-25; it splits D25's two findings)**: THE PASS IS NEEDLESS. Observed 2026-10-25;
  method: D25 in the worktree `probe19` at `a81dd7ee9` - with the call off, 54 of 54 fixed and pinned seeds passed as with
  it on and the five pool manifests came out byte-identical (`cmp`); with it on, of the 412 connectors it was asked about
  (58 fixed, pinned and pool, 354 in the fresh block of seeds 3001601-3002100), it returned none with an inner end more than
  `JOIN_TOL` off the web. So the call, `_pull_back_to_service`, `kept_connector` and their tests are deleted, and so is the
  claim "the track out runs off the map" there (`law.dangling_lane_ends` carries it). BUT THE RULE IS BROKEN BY ANOTHER
  PLACER. Same observation: 6 of the 377 fresh maps that reached the end of `stage_web` (seeds 3001615, 3001629, 3001674,
  3001847, 3002028 and 3002062, all nucleated, all with a way out's gate) end the track 25-66 ft past the last way to meet
  it, and all six passed every check, because the law exempts the connector (`law.dangling_lane_ends`). A per-step trace of
  the six puts it in the settle's `settle_reach`: it draws the household ways to the stretch of the track near the cluster
  (`homesteads/household_ways.near_the_cluster`), not to the track's start. So:
  (a) the rule becomes ONE predicate, `checks.track_ends_off_the_web(M)` - a connector's inner end (the end nearer the
  other ways) more than `JOIN_TOL` from every other lane, on a map with a web (a lane besides the track and the field
  spur) - asked of the finished map by the cohort only (`tools/cohort_audit.py`'s list beside
  `groves_crossed_by_lanes`, which the settle never reads, so no map is refused for it; constitution XIX), with a two-sided
  unit test; the claim "the track meets the lanes" moves to it;
  (b) the placer that keeps the rule is a choice between two placements - the track drawn from where its households' ways
  meet it, or the ways laid to the track's start - and is set down as T27 for the GM's fixing pass (D11), with the six
  seeds. The fixed and pinned seeds and the pool maps were all at 0.0 ft, so (a) moves no landing verdict; it names a
  fresh failure the record could not see. Rendering: map drawing convention (0081's track-out entry).

- **D28 (the predicate's scope, measured at the first landing, 2026-10-25)**: the first form asked every connector end inside
  the finished manifest's `W` x `H` and named the way-out end on 18 of the 54 landing seeds (observed 2026-10-25; method: `make
  land F=417 T=T19`'s landing cohort; the frame is cropped about the content, so `W` / `H` need not bound the lanes); the
  inner end is read by distance instead. Read so, it named every dispersed seed of the 54 (13; observed the same day, `make
  cohort-landing`): the dispersed form lays no web, only the track and the field spur, and its track ends among the farms
  (seed 5's 154 ft from the nearest house center, read from `make hamlet` seed 5's manifest). Whether that is 0081's "open
  country" is not this task's to rule: the predicate asks only a map with a web, the dispersed track's end goes to the GM
  with T27, and the landing cohort is 54 of 54 so read. Rendering: map drawing convention (0081's track-out entry).

### T19 Approach (re-answered 2026-10-25T11:58Z)

1. **The goal, in the world.** As before: the track out ends on the web, never in the grass. What T19 delivers toward it:
   the pull-back that never kept it there is gone, and the rule is one predicate the cohort asks, so a track that stops short
   is a named failure; drawing it right is T27's.
2. **The constraints.** D27: the pull-back changed nothing measured; the six fresh tracks that stop short are drawn so by
   `settle_reach` (the households' ways laid to `near_the_cluster`'s stretch); the law exempts the connector, and `law.py`
   is at 993 lines (`wc -l l7r/diagram/hamletgen/ways/law.py`, read 2026-10-25), so the predicate goes in `checks.py` (layered below the law) and is read only by `tools/cohort_audit.py`.
3. **Where each comes from.** O: FR-004, constitution XIX (a finished-map check in the cohort and the tests only), D27.
4. **Do they describe the world here?** Yes, measured (R6).
5. **The order.** As before.
6. **The exits.** The deletion lands with the predicate; the landing cohort stays green because every fixed and pinned
   seed and pool map is at 0.0 ft (R6). If it is not green, the landing is set down whole (D11).
7. **The search smell.** No tuning: the predicate's bar is the touch the law already uses (`_TOUCH_GAP`, 4 ft).
8. **The budget.** The landing, then a fresh block of 500 from seed 3002101 (D1), background.
9. **Done, measured.** `make land F=417 T=T19` green; `make dead-closure` clean; R6 with the fresh block after the landing,
   where `track_ends_off_the_web` should name about the six of R6's block's rate.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: T24 to T26 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->

### T19 Approach (re-answered 2026-10-25T12:23Z)

1. **The goal, in the world.** As re-answered at 11:58Z.
2. **The constraints.** As at 11:58Z, and D28: the predicate reads the track's inner end by distance (the finished
   manifest's frame is cropped about the content) and asks only a map with a web; the dispersed form lays none.
3. **Where each comes from.** O: FR-004, constitution XIX, D27, D28.
4. **Do they describe the world here?** Yes, measured (R6, D28).
5. **The order.** As before.
6. **The exits.** The landing cohort is 54 of 54 with the predicate so read (D28); the deletion and the predicate land
   together, or are set down whole (D11).
7. **The search smell.** No tuning: D28's change follows what the predicate asks, not a seed; the bar stays the 4 ft touch.
8. **The budget.** As before.
9. **Done, measured.** As at 11:58Z; and T27's task carries D28's question about the dispersed track for the GM.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
