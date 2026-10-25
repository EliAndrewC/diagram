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

## Order

T01 measure (D1, D2). T02 the hold guard (D4) - small tooling, lands alone. T03 the inventory (D3) and the principle's draft
(D6). T04 onward the engine work in D5's order, one task per inventory group, each landed and followed by a fresh block of
500; their Approaches are added by plan-delta as each starts, numbered on from T04 as the inventory needs. Then the guards, the
two tasks after the last engine task: the fresh block before the push (FR-009), and every archetype form against HEAD (FR-011,
SC-006). The last task closes: 1,000 fresh seeds, T106's seat turn re-applied (User
Story 2), the code-size delta (SC-004), the feature report.

## T01 - the baseline and the tally (FR-001)

### T01 Approach (checklist part A)

1. **The goal, in the world.** The GM can read how often a seed nobody has used fails, by form and by cause, at main.
2. **The constraints.** Seeds the gate has never used; the cohort's sizes, forms and pins; main's engine, no diff.
3. **Where each comes from.** O: the spec's FR-001 and D1; the tally's method is the spec's gap section.
4. **Do they describe the world here?** Yes: `make cohort ... FRESH=0` rolls exactly that and records per seed.
5. **The order.** First: every later task is measured against it.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** The 1,000-seed roll (background) plus 30 min for the tally.
9. **Done, measured.** `research.md` R3 holds the 1,000-seed table by form and cause from `make fresh-tally`, and the tally's
   test is red without it.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D7** The baseline is seeds 3000101-3001100, rolled in a detached worktree at main (`make cohort N=1000 SEED=3000101
  FRESH=0 JOBS=5`; five workers, the containers' memory at the cap). Rendering: none.
- **D8** `make fresh-tally` takes `COMMIT=` (records at that engine commit) and `SINCE=` (records at or after a UTC stamp),
  and counts a seed as fresh when it is at or above its record's `fresh_first`, or, for a `FRESH=0` roll, when the record's
  first seed is above the fixed range and the pinned rows (`cohort_gate`'s fresh start); one seed counted once per commit.
  Rendering: none.

## T02 - the hold made (FR-010)

### T02 Approach (checklist part A)

1. **The goal, in the world.** No engine task of a held claims feature can be started while 417 is open.
2. **The constraints.** `make task-start` is the one place a task becomes active (`plan_gate.task_start`).
3. **Where each comes from.** O: FR-010 and D4.
4. **Do they describe the world here?** Yes: a landing needs the active task, and the active task comes only from task-start.
5. **The order.** Second, small, lands alone (`make land-tooling`).
6. **The exits.** `HOLD_OK` for a non-engine task only.
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** 405, 372 and 384 carry the ON HOLD status (all three marked 2026-10-24); a test starts a 405 engine
   task and is refused, naming 417; a `HOLD_OK` on it is refused; a non-engine
   task with `HOLD_OK` starts; each red without the guard.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D9** A held feature is one whose `**Status**` line holds `ON HOLD` and `until feature NNN`; NNN open by `speckit-todo`'s
  own open/closed rule. An engine task is one whose text names a path under `l7r/` or `pool/`, or whose `research:` line is
  `physical`, or that names a decision whose plan section names such a path; unsure counts as engine. Rendering: none.

## T03 - the inventory (FR-002, FR-003)

### T03 Approach (checklist part A)

1. **The goal, in the world.** Every place the engine places-then-repairs, asks a rule too late, codes a rule twice or
   refuses where room is the remedy is listed, with where it is and the point it breaks.
2. **The constraints.** D3's method; found, not remembered.
3. **Where each comes from.** O: FR-002, D3.
4. **Do they describe the world here?** To be found.
5. **The order.** After T01 (its causes rank the entries).
6. **The exits.** An entry that breaks no point is kept with the predicate that makes it so.
7. **The search smell.** None.
8. **The budget.** 3 h.
9. **Done, measured.** `research.md` R2 complete; one task per breaking group in `tasks.md`, each with its Approach added by
   plan-delta when it starts; the principle's draft text in R4 for the GM.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D10** The reading is split by package (ways, homesteads and homestead_parts, waterfields, the overlap registry and the
  rest), each read by an `Explore` agent on `sonnet` given D3's whole method - its five searches and its five classes (the four
  points, and a rule coded twice) - and every entry it reports checked by the session against the code before it goes in R2
  (a fetched claim is not an entry). The three searches that cross packages are run by the session itself over the whole
  tree - every `cohort_audit` rule with its callers in `l7r/`; every caller of `law.violations`, `lane_violators`,
  `row_rules`, `grove_rules` and the overlap matrix inside the generator's run; every pair of functions judging one rule -
  and their hits reconciled against R2 before T03 is done. Rendering: none.
