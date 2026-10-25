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

### T40 (T31's first part, D35): the six settle steps measured needless deleted

- **Approach**: T31's own section, split so its first landing ticks only what it finished (T31's decision preflight ruled CLEAR,
  2026-10-25): the six steps R8 measured NEEDLESS - `settle_husks` (first and last), `settle_street_ends`, `settle_shadows`,
  `settle_joins`, `settle_needles`, `prune_the_tree` - dropped from `settle/stage.py` `STEPS`, and the nine names that leaves
  dead (`make dead-closure`: `settle_shadows`, `drop_stranding`, `settle_needles`, `keeps_the_network`, `left_to_the_tree`,
  `strands_only_ordinary`, `_on_the_connector`, `weld_corner`, `WELD_PX` with `weld.py`) deleted with their tests. The four
  still asked by `last_resort` (`settle_husks`, `settle_street_ends`, `settle_joins`, `prune_the_tree`) stay defined until T31 takes
  them out of it: `last_resort` re-asks the settle's steps once its rounds run out (FR-005), R8 measured only the `STEPS` positions,
  so its calls are T31's - each re-asked step leaves `last_resort` with that step's own conversion or deletion, and these four,
  needless in the rounds, are cut from `last_resort` and deleted in T31's landing, measured there as R8 measured the rounds.
  T31 keeps the four whose removal moved a pool map - needed under D35 and owed its conversion - the six needed ones and `last_resort`'s re-asked steps. R8 holds both of D35's runs: each
  step off alone, and the six off together (observed 2026-10-25, research.md R8: 54 of 54 - the 48 fixed seeds and the six pinned rows of `make cohort-landing` - and no pool manifest moved).
  Rendering: none.

