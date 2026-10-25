# 417-all-seeds-pass - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-24 -->
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

<!-- plan-archive: archived 2026-10-25 -->
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

<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-24 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-10-25 -->
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

<!-- plan-archive: archived 2026-10-25 -->
## T04 - one stream-crossing rule (R2 G7; FR-006)

### T04 Approach (checklist part A)

1. **The goal, in the world.** The cohort's "a farmstead part across the brook from its house" asks the same predicate the
   placers ask (`_geom/water_index.crosses_a_stream`), so the check and the placing cannot disagree.
2. **The constraints.** `crosses_a_stream(house, part, streams)` is the one predicate (its docstring: "all three now call
   this" - the audit's copy was missed); the audit's `parts_across_brook` keeps its part list and its count.
3. **Where each comes from.** O: FR-006 (a second implementation of a rule is deleted), R2 G7.
4. **Do they describe the world here?** Yes: the audit's `_cross` is a strict orientation test; `segments_cross` is the same
   test with one side non-strict, so they differ only for a part or house exactly on a stream's line.
5. **The order.** First of the engine tasks: it moves no map (the audit is not the generator).
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** 30 min plus the landing.
9. **Done, measured.** `cohort_audit.parts_across_brook` calls `crosses_a_stream`; its test pins a part across a reach
   counted and one on the house's bank not; the landing cohort green (FR-008).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

- **D12** `parts_across_brook` counts the parts `r` (with `of`) for which `crosses_a_stream(r["of"], (r["x"], r["y"]),
  manifest["streams"])`; its local `_cross` is deleted. The streams with fewer than two points are skipped by the predicate
  itself. Rendering: none.
<!-- plan-archive: archived 2026-10-25 -->
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

<!-- plan-archive: archived 2026-10-25 -->
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

<!-- plan-archive: archived 2026-10-25 -->
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
<!-- plan-archive: archived 2026-10-25 -->
## T23 - three claims labeled as their pages answer them (T05's claims round, MISLABELED; arbiter ask 417-T05-claims)

### T23 Approach (checklist part A)

1. **The goal, in the world.** Each claim says what its page says: the reader of the record sees a guess as a guess and a
   drawing convention as one.
2. **The constraints.** impl-drift's verdicts on T05's round (`evidence/impl-T05.txt`): `bund.cut_stub_ends#a stub that
   reaches the bund kept` is answered by 0014 ("A lane end that stops within 6 ft of the paddy's edge is drawn as joining
   it") - GUESS 0014, not UNRESEARCHED; `sweeps._bridge_collinear_breaks#bridge width` and `sweeps._join_orphan_ways#link
   width` are lane widths by role, which 0081 calls a map drawing convention - CONVENTION, as `serve.join_width` labels the
   same rule. The fourth, `sweeps._sweep_doubled_remnants#doubled lane dropped`, cannot be made true by a label: once it cites
   0081 it reads as drifted against the page's cut-to-a-T, so its label goes with the behavior, in T24.
3. **Where each comes from.** O: the arbiter's ruling on ask 417-T05-claims, items (2), (3), (5).
4. **Do they describe the world here?** Yes (impl-drift's quotes of 0014 and 0081, recorded 2026-10-25).
5. **The order.** With T25; label-only, no map moves.
6. **The exits.** The fourth claim goes to T24 (item 2).
7. **The search smell.** None.
8. **The budget.** 15 min plus the claims round.
9. **Done, measured.** The three claims carry the labels above; their claims round IN-STEP.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T23 Approach (re-answered 2026-10-25T06:18Z)

1. **The goal, in the world.** Unchanged: each claim says what its page says.
2. **The constraints.** As before, with impl-drift's round 1 (2026-10-25): the link-width claim's new text, "the width of the
   way it joins", described less than the code does - `_join_orphan_ways` takes the widest lane within `_LANE_JOIN_FT` of the
   link - so the label now states that.
3. **Where each comes from.** O: the arbiter's ruling on ask 417-T05-claims; impl-drift's round 1 on T23.
4. **Do they describe the world here?** Yes, measured 2026-10-25 (impl-drift quoted the code's `max(...)` over the lanes within
   reach).
5. **The order.** Unchanged.
6. **The exits.** Unchanged (the fourth claim in T24).
7. **The search smell.** None.
8. **The budget.** Unchanged.
9. **Done, measured.** The three claims IN-STEP in their claims round.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T23 Decisions

- **D21** `bund.cut_stub_ends#a stub that reaches the bund kept - GUESS research/questions/0014-bunds-between-the-paddies-aze.drawing.html: within 6 ft of the worked ground's edge`;
  `sweeps._bridge_collinear_breaks#bridge width - CONVENTION`; `sweeps._join_orphan_ways#link width - CONVENTION: the widest way within `_LANE_JOIN_FT` of the link` (impl-drift, round 1: the
  code takes the widest lane within the join reach, not only the way it joins). Rendering:
  none.

<!-- plan-archive: archived 2026-10-25 -->
## T25 - the bund reach and the stub's tail, one rule each (T05's claims round, outside the change; FR-006)

### T25 Approach (checklist part A)

1. **The goal, in the world.** The 6 ft "an end this near the paddy's edge joins it" is one constant, and every reader of the
   40 ft tail asks it the way the page words it ("under 40 ft").
2. **The constraints.** `settlement/water_ways/_helpers.BUND_REACH_FT = 6.0` is read by `settlement/water_ways/lanes`,
   `hamletgen/ways/geom.end_serves` and `ways/bund`; T05 made `hamletgen/consts_ways.FIELD_REACH_FT = 6.0` the reach of
   `thread` and `law` - two 6.0s for one rule (impl-drift's note on T05's round, `evidence/impl-T05.txt`). `bund.cut_stub_ends`
   cuts a tail `<= _PAST_JUNCTION_FT` where `settle/shapes.reaimed` and `sweeps.cut_past_connector` cut `< TAIL_CUT_FT`
   (measured 2026-10-25, the three tests read side by side). `settlement` is the lower layer: `hamletgen` imports it, never
   the reverse.
3. **Where each comes from.** O: FR-006; the arbiter's ruling on ask 417-T05-claims (item "OUTSIDE THE CHANGE"); 0014 (6 ft),
   0081 ("A tail of under 40 ft beyond a crossing is cut").
4. **Do they describe the world here?** Yes (item 2's reading).
5. **The order.** After T17 and T18.
6. **The exits.** The `sweeps` comments that give `_LANE_JOIN_FT` as 30 are history notes ("Written first against
   `_LANE_JOIN_FT` (30)"), true of when they were written - not stale, left.
7. **The search smell.** None.
8. **The budget.** 30 min plus the landing.
9. **Done, measured.** `FIELD_REACH_FT` is assigned from `BUND_REACH_FT`; `cut_stub_ends` cuts a tail `< TAIL_CUT_FT`; a test
   checks both; the reference map and the bund-touching pool maps regenerated (a map moves only where a stub's tail is exactly
   40 ft, measured by the regeneration); the landing cohort green.
10. **Before moving a constant.** No value moves; the comparison moves at exactly 40 ft only, to the page's wording.
11. **Before fitting things into room.** n/a.

### T25 Decisions

- **D19** `consts_ways.FIELD_REACH_FT = BUND_REACH_FT` (imported from `settlement.water_ways._helpers`), the one 6 ft bund
  reach, its research line kept where it now stands. Rendering: none.
- **D20** `bund.cut_stub_ends` cuts a free end's run `< TAIL_CUT_FT` past its first junction, as the other two readers do and
  as 0081 words it ("under 40 ft"); the value is unchanged. Rendering: none.
