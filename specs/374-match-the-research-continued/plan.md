# Implementation Plan: Match the research - continued (feature 374)

**Spec**: `spec.md` | **Request**: `request.md` | **Model**: `specs/372-match-the-research-remaining/plan.md` (its cycle, its batch
close and its bookends, themselves 328's) - this plan records only what differs and each wave's decisions.

## Summary

The work list is 328's ranking's open in-scope rows at 372's close (198: 153 E3, 43 E4, 2 E2 held - counted from `ranking.json` 2026-10-10, rows with no wave in scope), in ranking order, with the
items the spec's "What it carries" lists. Waves are numbered on from 372's (the first is wave 112), so 328's `audit/waves.json`
stays the one column; this feature's measurements are its own `measurements.json`, its decisions its own spec's table. Also
carried, from feature 370's landing (its spec, 2026-10-10): the claims findings on the code 370 split, left in `make
claims-report` for this feature under the claims gate's escape - rows of the work list like any other.

Two of the spec's carried tooling gaps (FR-007) are placed here, not in a wave: the claims-triage reply parser counting
"TOUCHES" anywhere is already fixed by 375's D5 (`scripts/record/claims_triage.py` reads only lines opening with `TOUCHES`,
its test pinning a mid-line mention ignored) - recorded so under SC-006 at batch 1's close; and `make modal-bundle
FOR=modal-depiction`'s crop on a Mode A sheet is fixed, with its test, before the first modal-depiction check on a Mode A
sheet that a wave owes (batch 1 edits no drawing page and owes none, as planned).

## Constitution Check

As 372's (XII research, XIII no known regressions, XIV fix where found, XVI the literal thing). New here: 375's process (decide
first, the freeze, the tripwires, the preflight) is in its first real use, and a guard that refuses correct work is fixed with
its test (spec FR-005).

## The cycle (372's, under 375)

`make task-start F=374 T=<id>` -> the task's section below carries its verdict (this plan's review, or `make decide`) -> the check
first where a rule is drawn (red on the unfixed sheet) -> edit -> `make test-file` -> each Mode A sheet's `make pack-audit` before
and after -> `make cohort N=48` only when the hamlet's stage code changes -> `impl-drift` on the owed claims (`make claims-owed`,
the triage for the rest) -> the record checks a page edit owes (`make record-owed`) -> records -> `make quick` -> tick -> commit. A
batch closes with `make done`, its occasions, the timing pair or its recorded "none owed", `escalation-check`, and LANDS.

<!-- plan-archive: T01 to T09 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 3: the hamlet's code brought to the research

**The work list** is 328's ranking brought current (2026-10-11): batch 2's re-checks closed 39 more rows (36 whose unit
now carries no UNCLAIMED or MISLABELED finding, or whose claim reads IN-STEP; three UNCLAIMED rows whose decisions now
carry claims), marked wave 118 in `audit/waves.json`; then `audit/scope.py` was re-run on today's cache (328 FR-010, the execution
record) and re-marked 14 more open rows `scope: deferred` (the paddy and ribbon builders, a town's kiln, a city's matrix
permissions among them; `scope.py` now counts `docs/building-programs.md` among the Mode A procedures, which it had sent to
deferred), leaving **183 open rows** in scope (126 E3 DRIFTED) at the batch's start; by its close, with the rows its checks filed
(`audit/found-wave120.jsonl`, `found-wave121.jsonl`) and the two a reopened key brought back (`audit/reopen.py`), with waves 119-121's three
E0 rows marked in `audit/waves.json` and the ranking rebuilt, 183 open, 132 of them E3 DRIFTED (`m:batch3-open-rows`). `make claims-report` shows the deferred
units' claims as DEFERRED (158).

**Three rules for every wave of this batch:**
- A row's fix text that says "label it a DEVIATION and have the drawing page record it" predates the plan review's
  ruling (batch 2, W118-2): the code is changed to match the page (328 FR-004). Where a change still looks wrong, the
  exception goes to `spec-fidelity` with the GM's words and is recorded only if ruled LEGITIMATE; otherwise the code
  is changed to match the page.
- Engine discipline: `make quick` per fix; reroll only the maps the change reaches and compare their manifests with
  `git diff HEAD`; one `impl-drift` per wave over the claims the wave's code edits re-owe; the review occasions a
  wave declares in `tasks.md ## Occasions` dispatched on a green gate, with no engine edit while one runs; one `make done`
  at the batch's close with the timing pair, its band a flag mentioned at landing (375 amendment 5: no perf record owed).
- A row whose unit `audit/scope.py` derives DEFERRED (328 FR-010, re-run on today's cache) leaves the work list: its
  ranking row is re-marked `scope: deferred` and no wave takes it.

**Not in this batch:** the two held rows (the door band, `fixture_quota`: the GM's); `oblique_at`'s square crossing,
which waits on the E4 research row beside it (`law_water.py::oblique_at#a channel crossing at its way's angle`, named in its
`after`); and `settle.py::_unkinked#a returning leg of 40 ft or more` with `settle_shapes#no hairpin or zigzag`, which cuts
through it: 0081's drawing page forbids the hairpin a returning leg of 40 ft or more leaves and gives the cut only under
40 ft, its folded spur and joining stub named exceptions to that threshold, so what a longer leg becomes is a research
question (both rows re-tiered E4; meanwhile the code keeps its cut and the claim its GUESS label). And
`comb.py::_comb_draw_source#feeder brook width`: its E1 fix (the brook in feet, `self.px(7.0)`) is in the code, and what
reads DRIFTED today is the E4 question beside it, `#feeder brook width against the ladder` (0068's ladder against its
question page's 7 ft GUESS and 0059's 7 ft, with the "narrower than the head race" bullet), named in its `after`; the code
and both pages stay as they are meanwhile. The three waves take
every E0-E2 row in scope that is neither held, measured DEFERRED nor waiting on research.

<!-- plan-archive: T10 to T12 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 4: the held rows answered, the country shrine's roof and the magistracies' service buildings

**The work list** is 328's ranking rebuilt on 2026-10-12 with the GM's rulings on the two held rows (`audit/overrides.json`,
recorded by the Diagram tooling session): 183 open rows (`m:batch3-open-rows`), all E3 or E4 but those two. The batch takes the
first open rows in ranking order: rows 0-10 of the open list and the two `compound.py` rows (21, 22) that are the same fix as
row 6 on the county example. Rows 11-20 (the sacred features, the gates, the residence's length, the walls and the well's gear)
are batch 5's.

**The rules of batch 3 hold** (the code changed to match the page, W118-2; engine discipline; DEFERRED rows leave the list),
with one for a hand-drawn sheet (328's edge case "A finding about a hand-drawn Mode A sheet"): the procedure
(`docs/buildings.md`, `docs/building-programs.md`) is fixed first, then every sheet the finding names is redrawn to it, the
sheet's comments saying what changed and why, `make pack-audit` before and after on each, and the red fixtures cut from that
sheet re-cut in the same commit. The county example and the round-trip sheet are `compound.py`'s output: their fixes are made in
the program and the emitter, never in the svg.

- **B4-1** (within): ranking order, rows 0-10 then 21-22; 21-22 ride with row 6 because they are its rule on the generated sheet.
- **B4-2** (narrowing, an exception to FR-005's "no wave is taken until 375 has landed"): 375 was reopened on 2026-10-12
  (amendment 6, in the Diagram performance session), and the waves are worked meanwhile. Amendments 1-5 and their tooling are
  on main; amendment 6 (FR-028) only stops the About form owing `modal-depiction`, so a wave taken now owes more checks, never
  fewer; `make tick` still refuses this batch's tasks until 375 closes, and nothing is escaped.
- **B4-3** (within): the batch's occasions (tasks.md `## Occasions`): `building-review` on each magistracy sheet and on
  Hoshigaoka once redrawn, and `glyph-check` on the stable's new form on one sheet (the passage and the grooms' room are new
  to the stable glyph), dispatched at the batch's close on a green gate after the last merge of main, never mid-batch.
- **B4-4** (within): the timing pair is owed only if a wave changes what the pair rolls (the hamlet's stages); W122's page
  reword and rows 2-22's Mode A work do not, so the batch records "none owed" unless W122 moves `fixture_quota`'s code.

<!-- plan-archive: T13 to T18 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 5: the county draft's filed rows, its stores and gate as knobs, the shrine beside its tree

**The work list** is 328's ranking rebuilt after batch 4 landed (179 open rows, 132 E3; `m:batch4-open-rows`): the open list's
rows 0-7 (the county draft's findings batch 4's checks filed) and 18 (its gatehouse), with the gate-form row batch 4's last
impl-drift filed (found.jsonl), then rows 8-12 (the sacred features). The rules of batches 3 and 4 hold.

- **B5-1** (within): a knob the record attests with two forms is ROLLED for the county draft by its name, as Ochiba's sheet rolls
  its own (`random.Random(zlib.crc32(b"county-magistracy-example:<knob>")).choice([...])`), in code beside its forms, the
  roll recorded in the draft's notes - the county servants' row's entry form (batch 4) is the pattern.

<!-- plan-archive: T19 to T23 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 6: the compound's gate, posts, wall clearance and wells, as the record draws them

**The work list** is 328's ranking rebuilt after batch 5 landed (165 open rows, 117 E3 DRIFTED; `m:batch5-open-rows`): the open
list's rows 0 and 2-4, the Mode A rows at its head. Row 1 (the residences redrawn to the record's 49-67 tsubo house, every
compound repacked) is a batch of its own, the next. The rules of batches 3-5 hold (B5-1's knob roll included).

<!-- plan-archive: T24 to T27 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 7: the hamlet's household graves, rack forms, the lane along the water and the chessboard ponds

**The work list** is 328's ranking rebuilt after batch 6 landed (161 open rows, 113 E3 DRIFTED; `m:batch6-open-rows`). Its row 0
(the residences redrawn to the record's 49-67 tsubo house) is HELD for the GM by the round arbiter (ask:b7-residence-route,
2026-10-12): redrawing the three hand sheets wholesale or recording their ~145-tsubo houses as a deviation is a question of what
to build, and the held list goes to the GM at the feature's end (SC-003); `audit/overrides.json` marks it E2 with the routes and
their costs. So batch 7 is the open list's next four rows, all of the hamlet generator. The rules of batches 3-6 hold (B5-1's
knob roll included); the engine changes, so the batch takes its timing bookends (`374-start` taken 2026-10-12 before its first
engine edit, `374-end` at its close) and states the band at landing.

<!-- plan-archive: T28 to T31 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 8: the attested field forms rolled, and the web lane's room and its gap off the crop

**The work list** is 328's ranking rebuilt after batch 7 landed (157 open rows, 1 held at E2, 108 E3 DRIFTED;
`m:batch7-open-rows`). Row 0 stays held for the GM. Batch 8 takes the next three rows, all of the hamlet generator: 771
(`ROLLED_ARCHETYPES`), 772 (`WEB_CLEARANCE`) and 773 (`WEB_HARD_GAP`). Row 771's own fix sets its bar: the two attested forms
join the roll only once their cohort is green. Measured before any edit (2026-10-12, 12 seeds of each at 16 households): the
dike-pond form passes 6 of 12, the polder form 10 of 12, so the row is waves 140-141, and 772 and 773 are waves 142-143. The rules
of batches 3-7 hold (B5-1's knob roll included); the engine changes, so the batch takes its timing bookends and states the band
at landing.

<!-- plan-archive: T32 to T32 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
### Wave 141 (T33) - the polder and the dike-pond rolled beside the valley fan
- **W141-1** (within): every remaining failure of the two forms' rolls is fixed at its placer (measured: dike-pond seed 1
  `NoDryExit`; polder seed 5 `SiteRefused`, 14 of 16 seated; polder seed 12 `WebRefused`, a farmhouse off the network), each
  re-rolled to green, and then both forms join `ROLLED_ARCHETYPES`. The bar is the constant's own: 12 seeds of each form green
  at 16 households, and `make cohort` green with the forms in the mix. Their odds are a GUESS: the valley fan twice, the polder
  once and the dike-pond once, the fan the commonest hamlet setting (no page counts the forms). 0019's drawing page loses its
  "known gap" sentence and says the forms are rolled.
- **W141-2** (within): a failure that cannot be fixed at its placer within the batch goes to the round arbiter with its
  measurement, never into the roll: rolling a form with open failures is what the constant forbids.
- **W141-3** (the round arbiter, ask:b8-w141-archetype-failures, 2026-10-12, route B): the fixes made at their placers land
  with batch 8 - the turned-gateway fallback on every field form (dike-pond seeds 1 and 10 green) and a row street giving up
  an end vertex that closed a needle with its join (`street.unneedled`) - once the cohort shows no regression. Three failures
  stay open (`m:w141-archetype-rolls`): dike-pond seed 4 and polder seed 12, row villages each leaving one farm with no lawful
  door path, and polder seed 5, a capacity refusal. So the polder and the dike-pond stay out of `ROLLED_ARCHETYPES`, row 771
  stays open and T33 lands open, to be taken up in a later batch as two placer guarantees (row-village door seating, polder
  capacity), each with a seed-pinned test that is red first.

<!-- plan-archive: T34 to T35 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 9: the rolled wood drawn on the sheet

**The work list** is 328's ranking rebuilt after batch 8 landed (155 open rows, 1 held at E2, 106 E3 DRIFTED;
`m:batch8-open-rows`). Rows 0 and 771 stay as ruled. The next row, 774 (`BROOK_FLANKS`, the hamlet never astride its brook),
WAITS (the spec's Assumptions: a row whose `after` is open waits for it): its fix makes the brook a tiebreak in `seat_cluster`,
which ranking row `cluster.py::seat_cluster#brook penalty weight` holds at 3.0 until the open row `ways/web.py::stage_web#a
cluster the brook crosses reached` lands. Measured at the tiebreak (0.05, 2026-10-12, `m:b9-before`): 10-household seed 4
still seats astride its brook and leaves one farmhouse unreached (ten when the hold was recorded) - a row-village farm whose
front faces the field and whose grove closes every other side, the same failure as row 771's dike-pond seed 4 and polder
seed 12. So batch 9 takes row 776 (`woodland_on_the_sheet`, a rolled wood left off the sheet) alone; rows 774 and 771 return
together once a row farm's way to its street is a placer guarantee. Measured before any edit (20 valley hamlets at 16
households, seeds 1-20, `m:b9-before`): 7 of 20 roll a wood and draw none of it. The rules of batches 3-8 hold; the engine
changes, so the batch takes its timing bookends and states the band at landing.

<!-- plan-archive: T37 to T37 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 10: a grove farm's way in kept open (row 771's first placer guarantee)

**The work list**: rows 771 and 774 wait on one failure (`m:b9-before`, `m:w141-archetype-rolls`) - a row-village farm whose
door path finds no way to its street (dike-pond seed 4 and polder seed 12 of 771's rolls, the 10-household valley seed 4 of 774's
trial) - and the round arbiter's route B (W141-3) takes 771 up again "as two placer guarantees (row-village door seating,
polder capacity), each with a seed-pinned test that is red first". Batch 10 takes the first. Probed before the fix (2026-10-12):
on polder seed 12 the farm's own privy and manure heap stood between its door and the break in its south grove band, its way
in; on the 10-household valley seed 4 the privy stood on the very point the web's door path starts from. Two placer fixes were tried and measured to fix none and reverted: a door route routed and reserved at the row seat, and a
door path to the whole network. The engine changes, so the batch takes its timing bookends (`374-start` taken on HEAD before the
fix was re-applied).

<!-- plan-archive: T38 to T38 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 11: the grass ground's form from the land - the floodplain meadow

**The work list**: rows 0, 771 and 774 stay as ruled (771 on the polder's capacity and seed 4's waived regression, 774 on the
10-household valley seed's off-ford street). The next free row is 775 (`stage_hinterland#grass ground form`): research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html
gives three attested forms - the grass hill where the map has hills, the floodplain where it has a river flat, and now and then
a small grass plot beside one paddy (the tazuke kusayama) - and the code draws one, hill scrub with scattered pines on every
map, Kuwabata's dike-pond river flat included. Batch 11 takes the floodplain; the paddy's own grass plot, a new drawn element
of its own, is the row's second wave in a later batch. The engine changes, so the batch takes its timing bookends.

<!-- plan-archive: T39 to T39 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 12: the paddy's own grass hill (row 775's second wave)

**The work list**: row 775 (and its twin, row 911) stays open after batch 11 for the third attested form of the grass ground
(research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.html: "Sometimes a small grass hill was set aside for a
particular paddy's sole use, and called a tazuke kusayama"; its drawing page: "now and then, added at random, a small grass plot
beside one paddy ... one grass patch of about the paddy's own size on the slope above it. The plot's size and how often it is
rolled are a GUESS"). Batch 12 draws it, and with it rows 775 and 911 close. The engine changes, so the batch takes its timing
bookends.

<!-- plan-archive: T40 to T40 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 13: the farm's bamboo strip (row 777)

**The work list**: row 777 (`homesteads/bamboo.py::household_bamboo#strip seated after the lanes`, DRIFTED): 0075's drawing page
says "The strip is seated with the sheds and gardens, so the lanes and wells keep off it"; the code seats it in `stage_hinterland`,
after the web, keeping 6 ft off the lanes laid before it. The row's fix: seat the strip with the sheds and gardens, before the
lanes and wells, so the web keeps off it. Rows 0, 771 and 774 stay as already ruled; 700 and 708 are in deferred units (SC-003's
scope is the kept and Mode A rows). The engine changes, so the batch takes its timing bookends.

<!-- plan-archive: T41 to T41 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 14: washing places at the water's edge (the washing-places row)

**The work list**: the next free row (`homesteads/farm_water.py::farm_channels#washing places`, DRIFTED): 0065's drawing page draws
washing places wherever a stream or ditch passes a settlement's houses - shared, or one at each house where a channel runs past
them, a knob - and the code draws none and never rolls the knob. Rows 516 (the residence size), 771 and 774 stay as already
ruled; the bamboo strip's order the GM ruled free on 2026-10-12 ("the ordering is an implementation detail and we can pick whichever ordering makes things easier"), its row judged on the strip's placement. The engine changes, so the batch takes its timing bookends; the pool roll is taken
with every measurement (batch 13's lesson).

<!-- plan-archive: T42 to T42 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 15: the pig sty against the house (the pig-sty row)

**The work list**: the next free row (`homesteads/fixtures.py::FIXTURE_BANDS#pig sty against the house`, DRIFTED): 0049's
drawing page has about two households in three on a plain paddy hamlet keep a small pig sty against the farmhouse or one of
its outbuildings, on the household's own plot, and the code draws no sty on any farmstead. Rows 516 (the residence size) and
774 stay as already ruled; 771 is normal work behind the polder seeds; the bamboo row is judged on placement (the GM,
2026-10-12). Room before packing (the GM, 2026-10-12): where the sties do not find walls, the homestead's ground grows
before any packing. The engine changes, so the batch takes its timing bookends; the pool roll is taken with every
measurement.

<!-- plan-archive: T43 to T43 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 16: the reseated persimmon and its own grove (the persimmon row)

**The work list**: the next free row (`homesteads/persimmon_reseat.py::persimmon_for#under no conifer's crown`, DRIFTED):
0046's drawing page has a farm's persimmon stand at the edge of its own grove behind the house, "and the grove's trees give
way round it"; the seating's persimmon is honored that way (the grove is drawn round it), but a tree short of the hamlet's
roll, given afterwards to a household that rolled none (feature 315's reseat), is refused its own grove's band and every
conifer already drawn there. Measured first: all 647 rolled persimmons are drawn over the 44 rolls and the pool (the
reseat always finds a household), so the change is which household and where, never a count. Rows 516, 771, 774 as ruled.

<!-- plan-archive: T44 to T44 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 17: the row farm sheltered by the grove row across its street (the row-bamboo row, and a citation)

**The work list**: the next free rows. `homesteads/bamboo.py::household_bamboo#row farm's bamboo to the south` (DRIFTED):
0033's drawing page records two forms of a row farm's shelter - the grove kept on the windward sides whichever side the
street runs, and "the bamboo set south where a row of grove farms across the road already broke the wind" - and the map
draws only the first, the second recorded as a deviation. And `plan.py::fall_backs_the_wind#fall square to or away from
the wind` (MISLABELED): cite 0031's drawing page for the predicate. Row 788 (the pond layout) was found done by wave 139
and closed there.

<!-- plan-archive: T45 to T45 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 18: where a clustered hamlet's wells stand (the wells rows)

**The work list**: the next free rows in ranking order. Rows 771 and 774 stay open behind their found rows (batch 13), and
782, 783 and 785 are each a rewrite of the seating, so the wells come first as the smaller form:
`homesteads/wells.py::place_wells#wells among the houses` (DRIFTED, row 786) - 0196's drawing page makes the wells' siting
a knob ("Whether a village's wells stand by the lane or among the houses is a knob": the lane-side form on a lane verge,
clear of the tread, or the cluster form in the open ground among five to ten houses, off every lane), and says "the map
places its wells a little closer than" the 95 ft check, where the lattice seats on the check's own 95. Row 787 (the well
pocket drawn inside its own homestead) waits for this wave and is its own wave: it is a seating change, and on every
clustered map measured (19 of the 44 rolls; Inashiro, Kuwabata and Sawada) the two wells are one pocket and one lattice
well, so this wave moves the lattice well alone.

<!-- plan-archive: T46 to T46 moved to plan-done.md, 2026-10-13 (feature 375 FR-044) -->
## Batch 19: the household's well off its farmstead (row 787)

**The work list**: the next free rows in ranking order, the one batch 18 named as next:
`homesteads/wells.py::place_wells#well pockets drawn first` (DRIFTED, E3 row 79 - the global row 787) and the same defect's
second claim, `settlement/rolling/bundle.py::BundleGeomMixin._lay_well_pocket#household well where none is near` (DRIFTED,
E3 row 218, filed by wave 154). 0028's drawing page draws "the well, shared off the farmstead" and "not one to a farm"
outside a row village, and 0196's two forms stand a shared well on a lane's verge or in the open ground among the houses -
neither inside one household's homestead, which is where the seating lays its pocket today. Measured on the 44 rolls
(r13U, the wave 154 roll): every one of the 19 clustered hamlets draws exactly one pocket (the first household's, which
always carries one) and one lattice well; no roll draws a second pocket. Rows 771 and 774 stay open behind their found
rows (batch 13); 782, 783 and 785 follow.

### Wave 155 (T47) - the pocket well becomes a shared well of the rolled siting
- **W155-1** (within): a clustered hamlet's seating lays no well pocket in any household's homestead: `needs_pocket` asks
  for none and `_lay_well_pocket` lays no wellhead ground, so the homestead gives that room back (room before packing). A
  grove farm's own water (`grove_water`, 0196/0031: a dispersed farm draws from its own channel or well) and a row village's
  `row_water` forms (0033) are untouched.
- **W155-2** (within): the wells `well_target` owes are ALL seated by the rolled siting (wave 154's forms, unchanged: the
  cluster form among five houses off every lane; the lane form on a lane's verge after the web), so the well the pocket
  stood for is now a shared well of the same form as its fellow - "shared off the farmstead" (0028).
- **W155-3** (within): the water-reach guarantee the pocket carried by construction (`WATER_REACH_FT`, 760 ft, 0196: every
  household within reach of a well or open water) moves to the wells: once the rolled form has seated what it owes, any
  household beyond reach of every well and of open water is owed one more shared well, seated by the same form with that
  household inside its reach - more wells where the houses spread, never a household left dry. Where the form finds no
  seat, the wave 154 fallback seats it as a recorded deviation (`form: fallback`, `meta.well_fallback`), off every
  farmstead. Measured on the bar's rolls (W155-4) how many such wells there are; a hamlet that draws more than `well_target`
  wells is recorded (`meta.wells_for_reach`), since 0196 gives a hamlet "one or two".
- **W155-5** (within, found in measuring): with the pocket gone, the first well the lattice seats was its innermost seat,
  the cluster's middle, and the second, held 170 px off it, took three or four households - the first served 12 or 13 on
  four of the 44 rolls (r155, against none at HEAD). Where two or more wells are owed, the first is seated at the middle of
  its own share of the houses, the shares cut along the cluster's long axis (a GUESS: no page says how a hamlet's wells
  divided its houses), so the second, by the worst-served walk as before, takes the other share: 0196's five to ten a well.
  The 40 seats nearest the share's middle are ranked one well ahead (`pair_keeps_ten`: a second seat 170 px off keeping
  both at ten). Measured: three rolls stayed over ten (r155c), the seats near the share's middle refused by the homesteads
  standing there (on valley 17: 40 by threshing yards, 33 by gardens, 25 by houses, 45 by the fit test; no open ground
  among a full share's houses).
- **W155-6** (within, found in measuring): while a well is nearest to more than ten households, one more shared well is
  seated by the same forms and counted (`meta.wells_for_ten`) - a third well for sixteen households is one to five, within
  the record's one to 2-20 households a well for a hamlet (0196's count bullet); a well that leaves the busiest count where
  it was ends the search. The alternative priced first was more room: a shared well's ground reserved at the seating, which
  the room-before-packing rule prefers but which reseats every clustered hamlet; the third well is inside the research's
  own range, so it is taken and the reserved ground is not.
- **W155-4** (the bar): no roll that passes at HEAD refuses (the pool, the cohort, the 44 rolls); no well stands inside a
  homestead on any of them; every household within reach of water; no well over ten; counts measured and recorded
  (`m:w155-wells`). The occasions: a glyph check where a pool map's well moves (placement-changed: well on Inashiro,
  Kuwabata and Sawada - each drew a pocket).

**The round arbiter's ruling** (ask:w155-cohort-seed10, 2026-10-13, route b): wave 155 is REVERTED. Built and measured
(`m:w155-wells`: no well in a homestead, none over ten, the pool clean, the 44 rolls as at HEAD), it took cohort seed 10
from pass to `lane_knots`: the pocket's room leaving the homesteads re-deals the seats, and the web over them knots where no
gather, cut or tee is lawful (the probe: every gather a needle, the stub's cut splits the web, the crossing's cut a needle
join). That is the found row `settle_the_web#a re-deal of the seats` (found-wave149, E4), which rows 777 and 787 now both
wait on, so it is taken next (T48). The wave's diff is kept whole (`w155-pocket-attempt.patch`) and re-lands on the settled
web with no waiver (T47); rows 787 and the pocket's second claim are E4 behind the settle row in 328's `audit/overrides.json`.

### Wave 156 (T48) - the web carries a re-deal of the seats (the settle row)
To be decided (`make decide`) once its measurement is taken: the seeds the found row names (7, 2, 10, 8, and Inashiro and
valley 18 under batch 13's routes), each re-dealt seat's knot or refusal, and what the settle cannot mend on each.

## Landing by batch (375's D18)

374 is the remainder of 328's ranking, too long for one clone, so it lands batch by batch and stays open between them:
`tasks.md` holds the current batch's tasks and one standing task, T99, for the batches still to come. A batch whose
decisions need no new ruling adds its tasks under its own plan section, decided per task (`make decide`).

**Lands open**: T99, T33

## Performance bookends (constitution VI)

| batch | waves | pair | gate | close |
|---|---|---|---|---|
| 1 | 112-114 | none owed: the batch's engine code is the Mode A draft (`compound.py`, `compound_parts.py`, `compound_model.py`: the kitchen ell, the corridor gone), `pack_audit` (`veranda_depths`, the hearth not a door) and `buildings/types.json`'s kitchen band - none in what the timing pair rolls (the hamlet's stages), as 372's batches 3-5 recorded | green 2026-10-10 at engine key 026828713522 | the review occasions running (three building-reviews, two glyph-checks); escalation-check 3 keep |
| 2 | 115-118 | none owed: the batch's engine edits are `Research:` docstrings and claim wording only (no engine token moves, the maps unchanged: `git diff origin/main -- pool/` empty after the gate's roll) | green 2026-10-11 on the merged tree | the record and claims checks answered; no review occasion (no sheet or glyph moved) |
| 3 | 119-121 | taken (the hamlet's stages changed). The pair `374-start` / `374-end` reads band 3 (+25.0%, observed 2026-10-11 by `make perf-report AGAINST=374-start`), a FLAG under 375 amendment 5, never a gate. `perf-audit` (2026-10-11, `dev/perf-log/20261011T105045Z-review-374-confirmation-local-diagram-backlog.json`) found the band is the host's load (load 5-8 on 22 shared cores; its quiet legs level, head 18.0 s against base 17.3 / 18.6 s) plus a real ~+1.2% of the total from T11's wood rule (`wood_rank.py`, `parcels.py`: seats below the houses now ranked, each asked `low_by_the_water`), about +8% of hinterland+woodland; the door router's 4 ft lattice costs nothing measurable (web/rest level) (all `m:batch3-perf-audit-legs`). Its seven alternated legs are `perf-audit-legs/*aud374*.json`; the earlier control `m:batch3-cpu-interleaved` (-9%) rests on one cell and is superseded by them | green 2026-10-11 on the bridge fix; re-gated after the merge of main on 2026-10-12 | the record and claims checks answered; the glyph-checks of the wood on Inashiro (PASS) and the board on Kuwabata (NEEDS-WORK, fixed, PASS); the band mentioned at landing |
