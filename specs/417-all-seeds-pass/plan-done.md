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
<!-- plan-archive: archived 2026-10-25 -->
## T24 - withdrawn (moot since T26)

### T24 Approach (checklist part A)

1. **The goal, in the world.** A doubled lane cut where it comes alongside, not dropped whole (0081). Withdrawn: no pass
   drops a doubled lane whole any more.
2. **The constraints.** `sweeps._sweep_doubled_remnants`, the pass T24 was about, was measured needless and deleted with its
   claim in T26 (research.md R5).
3. **Where each comes from.** The GM 2026-10-25: "You can also close T24 if it is moot."
4. **Do they describe the world here?** n/a - nothing left to change.
5. **The order.** n/a.
6. **The exits.** n/a.
7. **The search smell.** n/a.
8. **The budget.** n/a.
9. **Done, measured.** `grep -rn "def _sweep_doubled_remnants" l7r/` finds nothing (T26's deletion; `stage.py` names it only in the comment that records the deletion).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
<!-- plan-archive: archived 2026-10-25 -->
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

### T19 part B (2026-10-25T12:26Z)

Owed by cohort@20261025T121445Z (18 landing seeds newly failing `track_ends_off_the_web`).

1. **What exactly is refusing?** The new finished-map check, on two cases the probe could not see (D28): the way-out end of
   the track read as "inside" the cropped manifest's `W` x `H` (18 seeds), and, read by distance, every dispersed seed (13),
   whose `stage_web` short-circuits before the probe's log and which lays no web. No other verdict moved; the gate was green.
2. **A3 again.** Yes: 0081's rule is about a track meeting the lanes; a map with no lanes besides the track and the spur has
   none to meet, and whether its end is "open country" is the GM's (D28, T27).
3. **A4 again.** n/a - nothing placed changes.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: the predicate asks what D27(a) defined (the inner end), and the 4 ft bar is unchanged.
6. **The one-sentence test.** "Why did the cohort refuse?" - the check asked the wrong end on a cropped frame, and asked a
   form that has no web.
7. **The next step is a measurement.** `make cohort-landing` with the predicate so read: 54 of 54 (observed 2026-10-25; its
   record committed as `b1133025b`), then `make land`.
8. **Every route measured?** The probe at the end of `stage_web` (R6), the finished manifests in the landing cohort, seed 5's
   manifest from `make hamlet`.
9. **After a ruling:** no arbiter trigger fired (one refused cohort; the gate was green both times).
<!-- plan-archive: archived 2026-10-25 -->
### T28 Approach (checklist part A)

1. **The goal, in the world.** A session fixing a seed sees, for every number it is about to chase, whether the number is the
   record's or ours.
2. **The constraints.** D31: no new class; `make tunables` derived from the claims; the checklist's A3; the 47 map-code and 45
   `pack_audit` constants given claims.
3. **Where each comes from.** G: the GM 2026-10-25 (D29). O: the tool's shape.
4. **Do they describe the world here?** n/a - tooling and labels.
5. **The order.** Before T29's relabels land (the tool reads them), before T31.
6. **The exits.** A drafted claim impl-drift rules wrong is fixed and re-checked once; a second wrong is reverted to no claim
   and listed.
7. **The search smell.** n/a.
8. **The budget.** The tool and its tests land in one tooling landing; the claims, one claims round.
9. **Done, measured.** `make tunables` and `INLINE=1` land and are tested (red without); every one of the 92 constants carries
   a claim impl-drift found IN-STEP; A3 and the doctrine name the tool.
10. **Before moving a constant.** n/a - no value moves.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-25 -->
### T29 Approach (checklist part A)

1. **The goal, in the world.** A claim labeled UNRESEARCHED means no one has looked; one a pass found silent says GUESS and
   which pass.
2. **The constraints.** D32, D36; the claim grammar; impl-drift's verdicts.
3. **Where each comes from.** G: the GM 2026-10-25. R: the passes' replies (`evidence/t29/`).
4. **Do they describe the world here?** Per claim, the pass's reading.
5. **The order.** The 247 first (this landing), T36 after, both before T31's deletion.
6. **The exits.** Silent: GUESS. Answered as a convention: cited. Answered with a departure, or contradicted: cited, landing
   DRIFTED by the round arbiter's ruling, the gap in T32-T35.
7. **The search smell.** No label is changed to make a round pass; a claim impl-drift rules wrong twice keeps its research label with its description reverted, listed in R9.
8. **The budget.** The passes (done), three claims rounds.
9. **Done, measured.** The landing's claims gate green; R9 with the counts.
10. **Before moving a constant.** n/a - no value moves.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-25 -->
### T36 Approach (checklist part A)

1. **The goal, in the world.** Every claim outside the 247's modules says truthfully what research found.
2. **The constraints.** D32, D36, D37; the claim grammar; impl-drift's verdicts.
3. **Where each comes from.** G: the GM 2026-10-25. R: passes P1-P7 (`evidence/t29/`) and P8.
4. **Do they describe the world here?** Per claim, its pass's reading.
5. **The order.** After T29; then T38; then T31 (D37 c).
6. **The exits.** Silent or no source could speak: bare GUESS naming the pass. A page answers as a convention: cited. A page
   answers and the code departs: cited with the departure, landing DRIFTED, its unit named in its T33-T35 row. A source no
   page records yet: recorded on its page by a page session first (D37 b), then cited as above. Not looked into: pass P8, then
   as above.
7. **The search smell.** No label is changed to make a round pass; a claim impl-drift rules wrong twice keeps its research
   label with its description reverted.
8. **The budget.** The passes (done), P8 (done), the page sessions for the 14 sources, two claims rounds.
9. **Done, measured.** The landing's claims gate green; R9 with T36's counts.
10. **Before moving a constant.** n/a - no value moves.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-25 -->
### T38 Approach (checklist part A)

1. **The goal, in the world.** Every number the map code holds is stated in its unit's claims and labeled by what it is, so a
   later pass knows which it may tweak, and which were looked into (the GM 2026-10-25).
2. **The constraints.** D31 (ii) and (iii), D37 (c); the claim grammar; impl-drift's verdicts.
3. **Where each comes from.** G: the GM 2026-10-25. O: the listing `make tunables INLINE=1`. R: the record and research passes.
4. **Do they describe the world here?** Per number, by what it is. A jitter salt, a sentinel or a seed's multiplier decides
   nothing about the place: `NONE`. A drawn size or stroke: `CONVENTION`. Every other number - a distance, a size, a share,
   a search's step or count - is checked against the record first: cited where a page gives it; `GUESS` naming the page
   where the page records it searched and silent; otherwise `UNRESEARCHED`, and the `UNRESEARCHED` ones go to research
   passes grouped by the question they share (D31 (iii)), then labeled by what each pass finds, as T36's were. A search's
   step or count is never `NONE`: it stays on `make tunables`' list.
5. **The order.** After T36; before T31; the numbers in the code T31 deletes skipped (none were listed there, observed
   2026-10-25; method: the listing filtered to `ways/settle/`).
6. **The exits.** Each unit's numbers go into its own claims (a nested function's into its enclosing unit's, which `make
   tunables` reads since the fold landed). A file the claims push past the 1,000-line bar is split into a package, never
   trimmed. What the passes cannot settle is listed by file in R9 with the count (D31 (ii)).
7. **The search smell.** No number moves.
8. **The budget.** 1,289 distinct numbers in 506 functions (observed 2026-10-25; method: the listing, de-duplicated by file,
   function and value); the record check, the passes, and a claims round over the units.
9. **Done, measured.** `make tunables INLINE=1 COUNT=1` lists none outside the skipped code; the claims gate green.
10. **Before moving a constant.** n/a - no value moves.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: T28 to T28 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T29 to T29 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-10-25 -->
### T40 Approach (checklist part A)

1. **The goal, in the world.** The settle's rounds no longer run the six steps that repair nothing a placer leaves wrong, and
   no code they alone used survives them.
2. **The constraints.** D35, D23; T31's decision preflight (CLEAR); the fixed and pinned seeds; the pool maps unmoved.
3. **Where each comes from.** G: the GM 2026-10-25 ("switch off the 16 repair steps"). O: R8's measurement and `make dead-closure`.
4. **Do they describe the world here?** Measured: each step off alone and the six together (R8, observed 2026-10-25).
5. **The order.** T31's first part, before its conversions; the four `last_resort` still asks stay for T31's landing.
6. **The exits.** The landing cohort and the pool gate green: landed. Red: the deletion set down with its seeds (D23).
7. **The search smell.** None: the six are R8's, the nine dead names `make dead-closure`'s.
8. **The budget.** One landing.
9. **Done, measured.** The six out of `STEPS`, the nine names and `weld.py` gone with their tests, `make land` green.
10. **Before moving a constant.** n/a: no constant moves; `WELD_PX` goes with its only user.
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

<!-- plan-archive: archived 2026-10-25 -->
### T43 (T41's regression, constitution XIII): `square_every_crossing` restored to the settle's rounds

- **Approach**: measured 2026-10-26 (method: the fresh block from seed 723759, rolled before T40 at b307a7ed7, 7 of 48 failing,
  rolled again on T42's tree with `make cohort N=48 SEED=723759 FRESH=0 JOBS=3`): 8 of 48 - the same seven and seed 723805,
  `lane_knots` (two ends 20 ft apart). Bisected in detached worktrees: passing after T40 (04b840f20), failing after T41
  (44ee317fa); on T40's tree each of T41's seven removals alone, and only `square_every_crossing` out fails it. T41's 54 fixed
  and pinned seeds never met the unsquared crossing that ties the knot. So it is NEEDED, not needless: restored as it stood at
  T40 (its definition, its re-export, its place first in `STEPS`, its test and the three claims T41 reworded), owed D11's
  conversion under T31 like the other needed steps. With it back, seed 723805 and 54 of 54 pass; Inashiro and Sawada return to
  their pre-T41 drawing order. Rendering: none.

### T43 Approach (checklist part A)

1. **The goal, in the world.** No seed that passed before T40's deletions fails after them.
2. **The constraints.** Constitution XIII (no known regressions); D35 (a step that moves a verdict is needed); D11.
3. **Where each comes from.** G: the constitution. O: the same-block roll and the bisection.
4. **Do they describe the world here?** Measured: one seed, one step.
5. **The order.** Before T31's next conversion: a regression first.
6. **The exits.** The seed, the landing cohort and the pool gate green: landed.
7. **The search smell.** None: bisection, one probe a candidate.
8. **The budget.** One landing.
9. **Done, measured.** Seed 723805 passing, `make land` green.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T49 (FR-005, T48's review): every way squared at its water crossings where its placer lays it

- **Approach**: T48 deleted the settle's `square_every_crossing`; four placers still lay a run without squaring it where it
  crosses the brook or a drawn channel - the skeleton arms (`web/skeleton.py`, `_lay_skeleton`), the web lanes
  (`fabric._draw_web`), the bund and track spurs (`bund.py`, `track.py`'s drawn spur), the field way (`reach.py`) and the connector's dry exit
  (`track.connector_dry_exit`'s runs, returned unsquared at `track.py`'s two fallbacks - found by T48's impl-drift). Each asks
  `squaring.square_run` of its run before it commits it (as `tree.lanes_of`, the door paths and the connector already do), the
  run then judged as squared by the placer's own tests (`admits_lane`, `Lawful`). A placer whose ways are shown by measurement
  never to cross water (no crossing on any fixed, pinned or fresh seed and none possible by construction) owes nothing, its
  measurement recorded here. Measured with `make cohort-landing`, the fresh block and the pool, against HEAD. Rendering: none.

### T49 Approach (checklist part A)

1. **The goal, in the world.** Every way meets water square, as laid; nothing squares it afterwards.
2. **The constraints.** FR-005, D35, D11, FR-008; 0035 and 0084 (a crossing square to the water).
3. **Where each comes from.** G: the GM 2026-10-24/25 (place correctly in the first place). R: 0035, 0084. O: T48's review.
4. **Do they describe the world here?** Measured per placer, fixed, pinned, fresh and pool.
5. **The order.** After T48; with the other placer conversions (T31, D11).
6. **The exits.** FR-008 green: landed with its fresh rate. Red: set down.
7. **The search smell.** None: one placer at a time.
8. **The budget.** One landing.
9. **Done, measured.** Each of the four squares its run or is measured never to cross water; `make land` green.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
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


<!-- plan-archive: archived 2026-10-26 -->
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


<!-- plan-archive: T52 to T52 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-10-27 -->
### T53 Approach (checklist part A)

1. **The goal, in the world.** The same lane web, its whole-network checks (`served_network`, `lanes_share_tread` and the rest the trial inventory names) asked of the lanes a step added or moved, not of every pair of lanes again.
2. **The constraints.** FR-012, FR-013, User Story 5, FR-008; the lane law's rules unchanged (FR-004).
3. **Where each comes from.** `spec.md` User Story 5's measurement (the check asked of every pair of lanes at each of its calls); the trial inventory.
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage) on the then-current engine scopes the
   task to the chains that still stand (FR-012).
5. **The order.** After the settle's probe (T31) and one network asked one way (T58), before T06 (the round arbiter's ruling on ask:417-T06-order, 2026-10-27): the largest single search by trial left in the web. `settle_reach` stays a placer, so its `reach.py` callers stay and are made incremental here; a caller T06 later deletes is a small loss the ruling accepts. The web's serve now asks `served_network` per run laid (T58), a caller this task makes incremental too.
6. **The exits.** Green: the web's whole-network checks asked incrementally, their calls at least tenfold down, the fixed cohort and the pinned rows passing (FR-008), the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the same predicate asked of a smaller set. DECIDED 2026-10-27 on the re-measure (item 4; `make perf-profile SEED=39 STAGE=web HOUSEHOLDS=40`, `dev/perf-raw/20261027T045320Z-seed39-web.prof`): after T58 `served_network` is asked 67 times on seed 39 (`lay_door_paths` 40, `_lay_web_lane` 22, `unreached_houses` 5), each regrowing every pair of lanes. Between two asks a lane or two is appended, edited or dropped: 764 asks on the 48-seed cohort and pinned rows, 603 after appends only, 45 after an edit, 55 after a drop, 23 after both, the largest web 24 lanes - measured 2026-10-27 (a throwaway log in the memo, `make cohort N=48 FRESH=0 JOBS=3`). So `checks.served_lanes` asks a memo (`NetworkMemo`, one per process, started over at another join tolerance or past `KEEP` pairs) that KEEPS each pair's answer to `geom.lanes_share_tread` by the two lanes' points: an ask judges only the pairs a new or changed lane is in, whatever changed - appended, edited, dropped or reordered - and the union-find over the answers is rebuilt each ask from the lanes' boxes (inline arithmetic, no call). The answer is the set a fresh `_components` gives (a test holds the two equal on random appended, edited and dropped webs). No index beyond the per-lane box, the webs measured being tens of lanes. Measured after (same profile, 2026-10-27): `lanes_share_tread` 2,976 -> 91 calls, `served_network` 0.24 -> 0.02 profiled s; the web stage 8,101,851 -> 7,208,472 calls (`make perf-fanout STAGES=web`).
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


<!-- plan-archive: archived 2026-10-27 -->
### T54 Approach (checklist part A)

1. **The goal, in the world.** The same household ways, each household's candidate exits refused by the tests that need no traced way - its corridor's ground, its own parts, the tree's reach - before any is traced, pulled taut and judged by the ways tree.
2. **The constraints.** FR-012, FR-013, User Story 5, FR-008; the ways' admission rules unchanged (the tree's `judge` stays the verdict).
3. **Where each comes from.** `spec.md` User Story 5's measurement (the households' ways traced and judged); the trial inventory.
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage) on the then-current engine scopes the
   task to the chains that still stand (FR-012).
5. **The order.** After the web's laying (the households' ways are the web's first layer).
6. **The exits.** Green (amended by the round arbiter's accept on ask:417-T54-exit, 2026-10-27; it was "`gap_ways`' admission chain at least tenfold down", the plan's split of SC-009, which the measurement showed this route cannot reach): the candidates' cheap refusals asked before any trace and the judgment's scans asked box-first, each chain's calls measured before and after, the fixed cohort and the pinned rows passing (FR-008), the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the candidates' cheap refusals asked as one array or index pass; no new search. DECIDED 2026-10-27 on the re-measure (`t54-measured.md` in the arbiter's bundle, measured 2026-10-27: `make perf-profile SEED=39 STAGE=homesteads HOUSEHOLDS=40`, a throwaway call counter in `gap_ways`, a throwaway log in `tree.admits` over `make cohort N=12 FRESH=0 JOBS=3`): of 177 candidate runs on seed 39, 74 stall in the taut pull (45,164 calls in all), 63 are refused by the tree, 40 admitted; the refused-after-a-pull runs cost 626,443 calls, the admitted 1,202,725, the tracing 172,780 - the trial is about a third of the chain, and the refusals already stop at the tree's first clause (76 of 115 on 12 seeds). So the cheap refusals stand as they are, and the judgment's scans are asked box-first, the same verdicts: `tree.rejoined`'s water legs, `fabric.house_hit`'s houses, `law.free_end`'s ways, and `access._seg_box_gap` written out as a clip and squared sums (an oracle test holds it to the old construction). Measured after (2026-10-27, `make perf-fanout STAGES="homesteads web"`): homesteads 6,940,189 -> 6,172,193 calls, web 7,208,472 -> 6,942,717; every pool manifest unchanged (`make maps-moved`), the landing cohort 54/54. What is left of the chain - about 1.2M calls of the admitted ways' own judgment (`Lawful` against the whole tree, `tree_base.judged`, `needles_with`, `as_joined`) - is T06's predicate, made incremental there.
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


<!-- plan-archive: archived 2026-10-27 -->
### T59 Approach (checklist part A)

1. **The goal, in the world.** The three claims the claims gate carried on unchanged code made true: `lane_breaches`' 3 ft tread where a lane records none claimed against 0081's drawing page (the MISLABELED and UNCLAIMED findings on it), and `settle_network`'s network of the greatest length, where no connector is drawn, claimed as a GUESS.
2. **The constraints.** Constitution XII (every rendering decision labeled); FR-006.
3. **Where each comes from.** impl-drift's findings on T58's claims round (2026-10-27), carried by `make land`.
4. **Do they describe the world here?** Yes: the code the claims name is unchanged; only their text is written.
5. **The order.** Beside T54's landing, the claims round that owes them.
6. **The exits.** Green: each claim checked IN-STEP by impl-drift, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: claim text only.
8. **The budget.** No landing of its own.
9. **Done, measured.** The claims round's verdicts.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| each claim | impl-drift's verdict in the claims round |

<!-- plan-archive: archived 2026-10-27 -->
### T61 Approach (checklist part A)

1. **The goal, in the world.** The same lane web, its settle's exit question and its trims asking each rule's predicate of only the legs, ways and fixtures that can bear on the point or leg asked - by their boxes first - so no verdict changes and no map moves.
2. **The constraints.** FR-012 (an index asked per candidate), FR-013 (speed first), FR-008 (no seed regressed); maps unchanged, the lane law's rules unchanged (FR-004).
3. **Where each comes from.** T06's re-measure (measured 2026-10-27, a throwaway call counter round `settle_the_web` on `make perf-profile SEED=39 STAGE=web HOUSEHOLDS=40`): the settle 3,244,838 of the web's 6,942,846 calls - its exit question (`keeper.unsettled`) 1,309,157, half of it `over_fixtures` (619,222).
4. **Do they describe the world here?** Yes: `make perf-fanout STAGES=web` names each chain (dev/perf-log/*-fanout-417-T06*.txt, measured 2026-10-27).
5. **The order.** T06's first conversions, before its settle steps are converted at lay (T31 part C): the predicates those conversions ask at lay are the same ones made cheap here.
6. **The exits.** Green: every pool manifest unchanged (`make maps-moved`), the landing cohort passing, the calls measured before and after, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: each predicate asks the same test of fewer candidates, each passed over only where its box stands beyond the rule's reach - `law.over_a_fixture` (each fixture's box), `geom.end_serves` (each leg's box, and `_trim_to_service`'s far-end filter kept per end), `law.needle_ends` (each tread leg's box), `law.fronting_ends` (`free_end`'s boxes), `law.dangling_lane_ends` (the legs within the end's reach first), `checks.unreached_houses` (a house a leg within the reach serves is served; the nearest distance asked only of one none serves), `geom.end_components` (as `_components`: boxes beyond the tolerance, a pair already joined), `web._reachable_runs` (the skeleton's legs within the run's box).
8. **The budget.** One landing.
9. **Done, measured.** The web 6,942,846 -> 4,830,229 calls at 40 households (seed 39), the roll 25,419,527 -> 23,204,610, measured 2026-10-27 (`make perf-fanout`, dev/perf-log/20261027T072724Z-fanout-417-T61.txt); no pool manifest moved and the landing cohort 54/54, observed 2026-10-27, method: `make maps`, `make maps-moved`, `make cohort-landing`.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| each predicate asked box-first | its chain in `make perf-fanout STAGES=web` |
| no map moved | `make maps-moved` |
| no seed regressed | `make cohort-landing` (in `make land`) |

<!-- plan-archive: archived 2026-10-27 -->
### T62 Approach (checklist part A)

1. **The goal, in the world.** The carried claim made true: `_reachable_runs`' network grown from the first candidate run where no skeleton stands, claimed as a GUESS.
2. **The constraints.** Constitution XII (every rendering decision labeled).
3. **Where each comes from.** impl-drift's UNCLAIMED finding on T61's claims round (2026-10-27), carried by `make land`.
4. **Do they describe the world here?** Yes: the code is unchanged; only its claim is written.
5. **The order.** Beside T63's landing, the claims round that owes it.
6. **The exits.** Green: the claim checked IN-STEP by impl-drift, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: claim text only.
8. **The budget.** No landing of its own.
9. **Done, measured.** The claims round's verdict.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the claim | impl-drift's verdict in the claims round |
<!-- plan-archive: archived 2026-10-27 -->
### T63 Approach (checklist part A)

1. **The goal, in the world.** The same maps, the wells' seats and the engine's most-asked geometry answering with fewer calls: the overlap registry's `admits` stopping at the first forbidden overlap, the verge test's distance written out, and the two primitives every stage asks (`seg_dist` with `seg_closest`, `segments_cross`) written without their inner calls - the same arithmetic, the same floats, no map moved.
2. **The constraints.** FR-012, FR-013, FR-008; the overlap matrix and every rule unchanged (FR-004).
3. **Where each comes from.** T56's re-measure (measured 2026-10-27, a throwaway call counter in `well_at` on `make perf-profile SEED=39 STAGE=lane_wells HOUSEHOLDS=40`): of 2,566 well seats asked, 2,231 refused by the registry at 499 calls each, 335 by `_fits`, 4 seated - the stage 2,175,770 calls.
4. **Do they describe the world here?** Yes: `make perf-fanout` (every stage), dev/perf-log/*-fanout-417-T56*.txt, measured 2026-10-27.
5. **The order.** T56's first part, the arbiter's ruling on ask:417-T11-route sending the session to T56.
6. **The exits.** Green: every pool manifest unchanged, the landing cohort passing, each chain's calls measured before and after, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: `Standing.conflicts(first=True)` returns at the first forbidden pair, all `admits` asks; `wells.ok` compares the squared distance to the squared reach; `seg_closest`'s clamp a conditional, `seg_dist` with it written in, `segments_cross`'s four orientation tests written in - each the same comparison in the same order.
8. **The budget.** One landing.
9. **Done, measured.** lane_wells 2,175,770 -> 1,542,780 calls at 40 households (seed 39), appurtenances 1,008,774 -> 901,554 (with the early exit alone), the roll 23,204,610 -> 21,520,104, measured 2026-10-27 (`make perf-fanout`); no pool manifest moved and the landing cohort 54/54, observed 2026-10-27, method: `make maps`, `make maps-moved`, `make cohort-landing`.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| each chain | `make perf-fanout` |
| no map moved | `make maps-moved` |
| no seed regressed | `make cohort-landing` (in `make land`) |


<!-- plan-archive: T62 to T62 moved to plan-done.md, 2026-10-27 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-10-27 -->
### T64 Approach (checklist part A)

1. **The goal, in the world.** The same maps, the engine's hottest loops asking fewer builtin calls: the spatial grid read and filed by `in` and a subscript (`PointGrid.near`, `PointGrid.extend`, `RingIndex`'s rows and edge boxes), the router's memos the same (`route.lattice_search`), and the boxes and band tests that called `min`, `max` or `abs` per item written as comparisons (`tree.rejoined`, `belt`'s disc test, `access.point_clear`, `wet.toe_band`) - the same values, no map moved.
2. **The constraints.** FR-012, FR-013, FR-008; every rule unchanged (FR-004).
3. **Where each comes from.** The roll's call counts by function across its eight heaviest stages (measured 2026-10-27, `make perf-profile SEED=39 STAGE=<stage> HOUSEHOLDS=40` for each, the profiles summed): builtins were over half the calls - `dict.get` 2,188,300 (`PointGrid.near` 760,812, `lattice_search` 531,251), `max` 1,421,093 and `min` 1,277,265 (`rejoined` 193,070 each, `RingIndex` 163,021 each), `setdefault` and `append` 553,430 in `PointGrid.extend`, `abs` 566,827 (`belt` 206,080, `toe_band` 122,892, `point_clear` 95,732).
4. **Do they describe the world here?** Yes: the same profiles, summed after each step.
5. **The order.** T56's second part, after T63.
6. **The exits.** Green: every pool manifest unchanged, the landing cohort passing, the calls measured before and after, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: each loop asks the same test of the same items; a dictionary read where the key is absent returns what `.get` gave, a new cell's list is made whole where `setdefault` made it empty, and `-r <= x <= r` is `abs(x) <= r`.
8. **The budget.** One landing.
9. **Done, measured.** The roll 21,520,104 -> 18,522,470 calls at 40 households (seed 39), measured 2026-10-27 (`make perf-fanout`, dev/perf-log/20261027T081533Z-fanout-417-T64b.txt); no pool manifest moved and the landing cohort 54/54, observed 2026-10-27, method: `make maps`, `make maps-moved`, `make cohort-landing`.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| each loop | the summed profiles' call counts by function |
| no map moved | `make maps-moved` |
| no seed regressed | `make cohort-landing` (in `make land`) |

<!-- plan-archive: archived 2026-10-27 -->
### T65 Approach (checklist part A)

1. **The goal, in the world.** The same maps, more of the hottest loops without builtin calls: `sat_overlap`'s projections reduced as made, `crossing_points`' leg boxes and `patches._ok`'s window and overlap by comparison, `convex_hull`'s chains counted, `chain_violated` and `banks._nearest_segment` comparing squared distances (the root taken only where a nearer segment is kept) - the same verdicts, no map moved.
2. **The constraints.** FR-012, FR-013, FR-008; every rule unchanged (FR-004).
3. **Where each comes from.** The summed profiles of the roll's eight heaviest stages after T64 (measured 2026-10-27, `make perf-profile SEED=39 STAGE=<stage> HOUSEHOLDS=40`): `sat_overlap` 67,711 each of `max` and `min`, `patches._ok` 75,534 and 50,356, `convex_hull` 91,550 `len`, `_nearest_segment` 127,377 and `chain_violated` 103,415 `hypot`.
4. **Do they describe the world here?** Yes: the same profiles, re-summed.
5. **The order.** T56's third part, after T64.
6. **The exits.** Green: every pool manifest unchanged, the landing cohort passing, the calls measured before and after, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: each loop asks the same test of the same items.
8. **The budget.** One landing.
9. **Done, measured.** The roll 18,522,470 -> 17,913,531 calls at 40 households (seed 39), measured 2026-10-27 (`make perf-fanout`, dev/perf-log/20261027T083303Z-fanout-417-T65b.txt); no pool manifest moved, observed 2026-10-27, method: `make maps`, `make maps-moved`; the landing cohort in `make land`.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| each loop | the summed profiles' call counts by function |
| no map moved | `make maps-moved` |
| no seed regressed | `make cohort-landing` (in `make land`) |

<!-- plan-archive: archived 2026-10-27 -->
### T56 Approach (checklist part A)

1. **The goal, in the world.** The rest of the trial inventory's sites converted, largest first (`inventory/trial.md` rows 6-11): the wells' registry admission and the open-ground patches here; the bamboo strips, the grove clumps and the notice board's seats in T66 (item 6).
2. **The constraints.** FR-012, FR-013, User Story 5, FR-008; each placer's rules unchanged.
3. **Where each comes from.** The trial inventory.
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage) on the then-current engine scopes the
   task to the chains that still stand (FR-012).
5. **The order.** After the field, before the overlap registry's resync.
6. **The exits.** Green (restated by the round arbiter's ruling on ask:417-lane-close, 2026-10-27; it was "each site converted, its chain at least tenfold down", the plan's split of SC-009): the sites' measured share removed - the wells' registry admission and the most-asked geometry (T63, T64, T65), the open-ground patches' lattice asked of the region at once - each chain measured before and after, the fixed cohort and the pinned rows passing (FR-008), the claims round clean; the grove clumps (the stands' `_seat`, inventory row 10), the notice board's route seats and the bamboo strips, each a few hundred thousand calls at most (measured 2026-10-27 by `make perf-profile` and the subtree estimator, which over-counts), DEFERRED to T66 in the correctness phase, not dropped. The ruling (ask:417-lane-close, 2026-10-27, `arbiter.jsonl`; its shares measured 2026-10-27 (`make perf-profile`, throwaway call counters)): "The T11/T12 precedent moves a pool-wide rewrite that buys about 1% to the correctness phase. T56's remaining sites (a few hundred thousand calls at most, by an estimator that over-counts) and T14 ... fall under it"; "Land T56's measured part (the patches' lattice, -52k, no manifest moved) and close T56 at that share."
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: each site's cheap refusals asked of its candidate set at once. The patches: the scan's lattice asked of the open-ground region in one array read (`Region.taken_many`), `_ok` asked only of the seats it leaves open - a taken seat fails `_ok`, and with no crop every seat does - the same seats qualifying (hinterland 2,596,223 -> 2,543,957 calls at 40 households on seed 39, measured 2026-10-27 by `make perf-fanout STAGES=hinterland`; no pool manifest moved, observed 2026-10-27, method: `make maps`, `make maps-moved`).
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


