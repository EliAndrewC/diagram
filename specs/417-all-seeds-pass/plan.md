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

## T05 - one lane rule, one constant, where the copies agree (R2 G1, first part; FR-006)

### T05 Approach (checklist part A)

1. **The goal, in the world.** Each lane rule the web codes in several places with the SAME value reads one named constant, so
   a later change to the rule cannot leave a copy behind.
2. **The constraints.** The copies found by T03 (`inventory/ways.md`, TWICE 4, 5, 6, 8, 14) with equal values: the 40 ft tail
   past a crossing or junction (`sweeps._PAST_CONNECTOR_FT`, `bund._PAST_JUNCTION_FT`, `settle/shapes._CROSSING_TAIL_FT`,
   `knots._TAIL_CUT_FT`, the literal `40.0` at `serve.py:234` and `touch.py:286`); the 25 ft join (`fabric._LANE_JOIN_FT`,
   `joints._MEET_FT`, against `consts_ways.LANE_JOIN_FT`); the knot margin (`knots._KNOT_MARGIN` against the imported
   `gap_ways.KNOT_MARGIN`, both 1.0); the 100 ft serve (`sweeps._SERVE_FT` against `consts_ways.WEB_REACH_FT`); the bend
   (`route.py`'s literal 140 / 50 / 40 against `clearance._HAIRPIN_DEG`, `_ZIGZAG_DEG`, `_ZIGZAG_RUN_FT`); the field reach
   (`thread.SPUR_REACH_FT` and `law.FIELD_REACH_FT`, both 6.0). The layer order of `ways/` (every reference points backwards;
   `law.py` imports no lower module's rule but `thread` may not import `law`).
3. **Where each comes from.** O: FR-006 ("a second implementation of a rule is deleted"), R2 G1, D11 (the copies that agree go
   first: they move no map).
4. **Do they describe the world here?** Yes, measured 2026-10-25 (each copy's definition read off its module by grep, and
   its research line beside it): each pair holds the same number for the same research line (0081's 40 ft tail and 25 ft join,
   0246's 100 ft, 0081's 140 / 50 / 40 bend, 0014's 6 ft join to the bund).
5. **The order.** After T04; before T16 (the copies that differ) and T06.
6. **The exits.** A copy whose RULE differs although its number agrees (`clearance._ARM_FT`, a hairpin's arm; `_ZIGZAG_RUN_FT`;
   `joints._SHORT_LEG_FT`, a returning leg; `touch._ALONG_STEP_FT`, a sample spacing) is not merged: different rules.
7. **The search smell.** None.
8. **The budget.** 1 h plus the landing.
9. **Done, measured.** A test asserts each former copy IS the one constant and that `route.py` holds no bare 140.0 / 50.0 /
   40.0; the reference map's manifest unchanged against HEAD (`git diff` on its manifest after `make map`); the landing cohort
   green with the same verdicts.
10. **Before moving a constant.** No value moves.
11. **Before fitting things into room.** n/a.

### T05 Decisions

- **D13** `consts_ways.TAIL_CUT_FT = 40.0` (0081: "A tail of under 40 ft beyond a crossing is cut") is the one tail
  constant; `sweeps`, `bund`, `settle/shapes`, `knots`, `serve` and `touch` read it. Rendering: none.
- **D14** `fabric._LANE_JOIN_FT` and `joints._MEET_FT` are `consts_ways.LANE_JOIN_FT` (0081's 25 ft); `knots` uses the
  imported `KNOT_MARGIN` and its own `_KNOT_MARGIN` is deleted; `sweeps._SERVE_FT` is `consts_ways.WEB_REACH_FT`.
  Rendering: none.
- **D15** `route.py` asks `clearance._HAIRPIN_DEG`, `_ZIGZAG_DEG` and `_ZIGZAG_RUN_FT` in place of its literals.
  Rendering: none.
- **D16** `consts_ways.FIELD_REACH_FT = 6.0` (0014's join to the bund) is read by `thread.SPUR_REACH_FT` and
  `law.FIELD_REACH_FT`. Rendering: none.

## T17 - a fixture in a grove band, one predicate (R2 G6, first part; FR-006)

### T17 Approach (checklist part A)

1. **The goal, in the world.** "No farm fixture stands in a grove band" is asked by ONE body, `grove_rules.fixture_on_band`,
   wherever it is asked - the audit, the sty's placer, the field pit's placer and the bundle fit - so the placing and the check
   cannot disagree.
2. **The constraints.** `fixture_on_band(f, g)` turns `f`'s box by its `rot` and tests the two centered boxes with strict `<`
   (its docstring: the sty's placer already asks it, 385 T03 D18). Two copies remain (`inventory/homesteads-water.md`, TWICE):
   `hamletgen/homesteads/fixtures.py` `_flexible_clear` (a pit's unturned box, inline) and `settlement/rolling/fit.py`
   `_fixtures_in_bands` (boxes already turned and rounded by `fit_index.recorded_box`, its inline `meet`). The persimmon's own
   neighbor-grove test (`persimmon_reseat.persimmon_for`) is a crown, which `fixture_on_band` does not judge (a tree has no
   box) - a different rule, not merged.
3. **Where each comes from.** O: FR-006, R2 G6, D11.
4. **Do they describe the world here?** Yes, measured 2026-10-25 (the three bodies read side by side): each copy is the same
   strict overlap of two centered boxes; the pit's box is unturned (`rot` 0) and the fit's boxes arrive turned, so each copy is
   `fixture_on_band` on a record with `rot` 0.
5. **The order.** After T05; moves no map.
6. **The exits.** The persimmon's crown test stays (item 2).
7. **The search smell.** None.
8. **The budget.** 45 min plus the landing.
9. **Done, measured.** Both placers call `fixture_on_band`; a test patches it and sees each asked; Inashiro and the grove pool
   map regenerated unchanged against HEAD; the landing cohort green.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T17 Decisions

- **D17** `fixtures._flexible_clear` asks `fixture_on_band({"x": q[0], "y": q[1], "w": ext[0], "h": ext[1]}, g)` over
  `grove_bands(s.M)`; `fit._fixtures_in_bands` asks `fixture_on_band` of each recorded box (as `x, y, w, h`, `rot` 0: already
  turned) against each band (rounded as it is now). Rendering: none.

## T18 - the overlap matrix's dead mirrors (R2 G11, first part; FR-006)

### T18 Approach (checklist part A)

1. **The goal, in the world.** No hand-kept mirror of an engine rule is left to drift.
2. **The constraints.** `overlap/matrix.py` keeps `forest_reveal_x`, `FOREST_REVEAL_FT` and `CANOPY_STRUCT_KEYS` as
   "Mirror of settlement... (keep in sync)"; nothing in `l7r/` or `scripts/` reads them (measured 2026-10-25, grep), one test
   imports `forest_reveal_x` from the matrix, and `CANOPY_STRUCT_KEYS` has already drifted: 27 keys against the engine's 34
   (`Settlement._CANOPY_STRUCT_KEYS`; measured 2026-10-25, the two tuples compared in Python).
3. **Where each comes from.** O: FR-006, R2 G11.
4. **Do they describe the world here?** Yes (item 2's measurements).
5. **The order.** After T17; moves no map.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** 20 min plus the landing.
9. **Done, measured.** The three names are gone from the matrix; the test imports `settlement._geom.forest_reveal_x`; a test
   asserts the matrix carries no mirror; the gate green.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T18 Decisions

- **D18** `matrix.forest_reveal_x`, `matrix.FOREST_REVEAL_FT` and `matrix.CANOPY_STRUCT_KEYS` are deleted;
  `tests/settlement/test_overlap_taxonomy.py` imports `forest_reveal_x` from `l7r.diagram.settlement._geom`. Rendering: none.
