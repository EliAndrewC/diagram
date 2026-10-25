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

