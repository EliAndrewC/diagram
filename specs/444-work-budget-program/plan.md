# Implementation Plan: the work-budget program - every phase rebuilt to an algorithmic budget

**Branch**: `444-work-budget-program` (no branch; `main` in the clone) | **Date**: 2026-10-28 | **Spec**: `spec.md`

**Input**: `spec.md` (the round arbiter's accept at the round cap, ask:444-spec-round-3), `request.md` (the design the GM approved,
steps 3 to 6). The instrument and the check are feature 443's, closed 2026-10-28.

## Summary

Step 3 first: every stage of `STAGES` gets a derivation on paper in the template's form (`.specify/templates/derivation.md`), a
MODE BUDGET verdict of SOUND from the `work-budget` agent, or the round arbiter's accept of its derivation (FR-013), and a budget in `dev/work-budget.json`; their sum and the whole roll's
exponent go to the GM through `escalation-check` - the program's CHECKPOINT, before any rebuild (FR-001, FR-002). Then the phases,
one task each in `STAGES` order, through the phase checklist (FR-003 to FR-006), the whole-table bundle before the first phase
lands (FR-007), the language decision after phases 1 and 2 (FR-008), and, if Rust, the ports proven first (FR-010 to FR-012).

This plan plans step 3 in full (T01-T06, with T07 and T08 added since: the pre-dispatch checks and the accept pin). The phase tasks are filed after the GM's checkpoint, each with its plan section and its
own plan review (`make task-add`, `make plan-delta`), because each phase's approach rests on the target he approves and on its own
derivation - planning them now would plan against a budget that does not yet exist.

## Technical Context

**Language/Version**: Python 3.14 (the language decision at step 5 may add Rust, FR-008, FR-010). **Testing**: the tests of
`scripts/budget_change.py`, `l7r/diagram/tools/work_budget.py` and `scripts/reviews/work_budget_bundle.py`; `make quick`, `make
hooks-test`. **Project Type**: the hamlet generator's engine; step 3 changes no engine code (one tooling change, D2).

**Single-artifact target**: step 3 rebuilds nothing; the phases' target is the reference hamlet `make work-budget` rolls
(`perf_snapshot.REFERENCE`, seed 25 and the snapshot's reference seeds, at 10/20/40/80 households).

## Performance bookends

Step 3 changes no code a roll runs. Each phase takes `make perf LABEL=444-<stage>-start` / `-end` in its own task (the phase
checklist's box 6 records `make perf-ab`); the program's opening record is `dev/work-budget.md` as 443 wrote it (run
`20261028T152105Z-45aa176ec9b8`).

## Constitution Check

- **I, II**: N/A - no UI in this repository. **III, IV**: N/A - no pool content or GM source moves in step 3.
- **V, VII-IX, XI**: N/A - no map, no setting prose in step 3; each phase's own section answers them.
- **VI**: PASS - each derivation passes the bundle's refusals (443 FR-008, T13) before its verdict; D2's tooling change has its
  tests and `make quick`.
- **X**: PASS - D2's changed lines owe 100% coverage.
- **XII**: PASS - a derivation's figures come from the stage's contract and the research claims that govern it; a figure no claim
  states is labeled a guess in the derivation's reason column.
- **XIII, XIV**: PASS - no regression is possible in step 3 (no engine code runs differently).
- **XVI**: PASS - the GM's words: the design, steps 3 to 6 (`request.md`); the checkpoint is his ("The GM approves the target").

## Decisions

**D1 - A derivation per stage, from its contract alone** (FR-001): `specs/444-work-budget-program/phases/<stage>.derivation.md`,
the template copied and filled. The CONTRACT is read from what the stage takes and leaves - its docstring, the `plan` fields it
reads, the manifest keys and registries it writes (`dev/placement.md`'s `STAGES` table and draw order), the research claims
that govern it (`make claims-report`'s rows for its modules) and the cohort properties it must keep (the cohort's checks that
read what it places, `cohort_audit`'s rules) - each a rule asked of a candidate before it is placed (S4), so each is a check
of the count - never from its loops or from `dev/work-budget.md`'s counts, which
the bundle's refusal keeps out of the judge's view and the session keeps out of the writing. The ALGORITHM is the minimal one for
that contract (rubric S1-S7); where the derivation finds today's output itself wasteful (a thing placed that a later stage drops),
it says so and the fix goes to the stage that owes it (the spec's Edge Cases).

**D2 - What a budget counts: the derivation's own items** (FR-001, the spec's Edge Cases): today `dev/work-budget.json` holds a
stage's `per_thing` and `make work-budget` multiplies it by the things the stage placed (`perf_profile.placed_counts`), which are
not the derivation's items (a derivation counts houses; the manifest counts every part of every house), and a stage that places
nothing (`seat`, `sink`) gets a budget of 0. So a budgeted stage also records its ITEMS at 20, 40 and 80 households
(`items_at_20`, `items_at_40`, `items_at_80`: the derivation's item count from the contract, 1 for a whole-stage figure), and its
budget at a size is `per_thing x items` at that size - S7's items x candidates x checks x slack. `make budget-set` requires
`ITEMS_AT_20=`, `ITEMS_AT_40=` and `ITEMS_AT_80=`; `make work-budget`'s ratio and the push's ratchet (`work_budget.held`) read them,
and refuse a budgeted or accepted row without them, naming the row and `make budget-change` - the placed-things product is retired,
not kept for older rows. A tooling change in `scripts/budget_change.py` and `l7r/diagram/tools/work_budget.py`, with its tests.

**D3 - The MODE BUDGET verdicts** (FR-001): each derivation is bundled (`make work-budget-bundle MODE=budget PHASE=<stage>
DERIVATION=<file>`) and dispatched to the typed `work-budget` agent once; its first line is saved beside the derivation as
`<stage>.verdict.txt` and its row written to the ledger. LOOSE or UNDERIVED: the derivation is corrected as the verdict states and
dispatched again; the third round on one stage owes the round arbiter's ruling first (the tripwire). SOUND: `make budget-set` pins it; the round arbiter's ACCEPT of the derivation pins it too (FR-013, the GM 2026-10-28), by its
trigger, `make budget-set ARBITER=ask:<id>`, bound to the derivation as it reads - a later change to a figure re-owes the arbiter. The agent is not a wave job (the GM's list, `scripts/container/append-system-prompt.md`), so the dispatches are plain
Agent calls, at most three in one message.

**D4 - Families, as 443 counted them** (the tasks' size): every stage of `STAGES` - 23, measured 2026-10-28 (the `STAGES` tuple of `l7r/diagram/hamletgen/driver.py`, the same list `dev/work-budget.json` holds and `tests/tooling/test_budget_change.py` keeps equal to it) - in the four families 443's T09-T12 used - water (6:
water_frame, field, sink, waterward, pond_stock, pond_bank), homesteads (7: seat, homesteads, appurtenances, burial, lane_wells,
sties, washing), ways (3: track, web, crossings), hinterland and frame (7: hinterland, woodland, windbreak, bamboo, frame, notice,
labels). One task per family, each landing its derivations, verdicts and budgets together.

**D5 - The checkpoint** (FR-002): the target is the sum of the 23 budgets at 40 households, and the whole roll's exponent (the
fit of the summed budgets at 20, 40 and 80 households); with it, the opening record's whole-roll figure and each stage's ratio of
today to budget (the counts are read only now, after every budget is pinned). The draft goes through `escalation-check`, then to
the GM in the turn's final message; his words set it with `make budget-program OPS_AT_40= EXPONENT= WORDS=` (logged in
`dev/work-budget-changes.jsonl`). No phase task is filed before. The draft names each stage pinned on the round arbiter's accept (FR-013) with its rounds and its totals' spread, as the
pin records them (`rounds`, `spread` in `dev/work-budget.json`), so a budget that rests on an accept never reads as a first-round SOUND.

## Task approaches

T01 D2's tooling; T02-T05 the four families' derivations, verdicts and budgets (D1, D3, D4); T06 the checkpoint (D5); amendment 3:
T10 the bundle's refusal of today's names, T11-T14 the four families re-derived greenfield (FR-015, FR-016), before T06.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T10 to T10 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
<!-- plan-archive: T11 to T11 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
<!-- plan-archive: T12 to T12 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
<!-- plan-archive: T13 to T13 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
<!-- plan-archive: T14 to T14 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
<!-- plan-archive: T06 to T06 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
## Project Structure

- Step 3: `specs/444-work-budget-program/phases/<stage>.derivation.md` and `<stage>.verdict.txt` for each of the 23 stages;
  `dev/work-budget.json`; T01's `scripts/budget_change.py`, `l7r/diagram/tools/work_budget.py` and their tests.
- After the checkpoint: one task per phase (FR-003), each with `phases/<stage>.md` from the phase checklist; `make
  work-budget-bundle MODE=table` before the first phase lands (FR-007); `research/language.md` after phases 1 and 2 (FR-008).

## Complexity Tracking

None.

<!-- plan-archive: T07 to T07 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->

<!-- plan-archive: T08 to T08 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->

<!-- plan-archive: T09 to T09 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->

<!-- plan-archive: T15 to T15 moved to plan-done.md, 2026-10-29 (feature 375 FR-044) -->
### T16 - phase: field, in Rust under the single-field cap, through the checklist (FR-003 to FR-006, FR-017, FR-018; step 4)

Occasions: settlement-review on the pool hamlets the rebuilt field moves (a map's form changes - its comb's basins, ditches and brook redrawn); glyph-check only if a glyph is redrawn.

### T16 Approach (checklist part A)

1. **The goal, in the world.** The comb field rebuilt to its greenfield derivation: the brook and its intake, the fan's outline, the comb's ditches and basins cut once with every rule asked before a basin is written, no repair pass.
2. **The constraints.** FR-003 to FR-006; rubric S1-S9; `phases/field_greenfield.derivation.md` and its budget, 23,988 at 40, exponent 0.79 - re-derived
   under the single-field cap by T18 (FR-018: `phases/field_greenfield.verdict-3.txt` SOUND, one field at 20, 40 and 80 households, no
   figure changed, the pin kept; a higher figure would keep the old pin unless the GM's words raise it); the research its contract cites (0005, 0017, 0053, 0054, 0059); the manifest keys today's stage writes (FR-004).
3. **Where each comes from.** G: the GM, 2026-10-29 ("yes please do step 4 and then we can stop and assess how things are going"); the design's step 4.
4. **Do they describe the world here?** Every form the stage writes: the comb archetypes the reference spec rolls (their derivation re-derived under the cap, T18's verdict-3 SOUND), and the polders, which get their own greenfield derivation and MODE BUDGET verdict before the rebuild (`phases/polder_greenfield.derivation.md`, accept-pinned as `field.polder`, ask:444-polder-round-3), and a seed that draws one for the audit.
5. **The order.** After `water_frame`; the last of step 4, then the assessment with the GM.
6. **The exits.** Green: counted operations at most the budget at 40 and 80, every seed of the Rust stage gate passing where the Rust stages complete (`make rust-gate`, FR-019, amendment 5), the claims round IN-STEP, the reviews owed, MODE AUDIT WITHIN, `phases/field.md`'s eight boxes ticked, all of the old field code - comb and polder - deleted. Red, over its budget: rebuilt again, or the budget raised with the GM's words (`make budget-change`, FR-006) - never set down, never an arbiter's accept; a stop to assess goes to the GM, as he asked ("then we can stop and assess how things are going").
7. **The search smell.** none
8. **The budget.** Several landings behind one task is not allowed - one landing; `make cohort` after each increment; one MODE AUDIT pass a round.
9. **Done, measured.** `make work-budget`: field's counted operations at 40 and 80 against 23,988 and 42,070.
10. **Before moving a constant.** The research page each figure cites, read before it moves.
11. **Before fitting things into room.** n/a

**Performance work?** yes - docs/performance-checklist.md's questions follow.

### T16 Decisions

- **D1 - the seam** (FR-004, FR-010): `stage_field(s, plan)` stays a thin Python function. It gathers the plan's fields the stage
  reads (`phases/field.keys.json` and the derivations' Reads), the households and the canvas, and calls `l7r_phases.stage_field`
  (`rust/phases/src/field.rs`, `fn stage_field`, its submodules under `rust/phases/src/field/` held under clippy's
  `too_many_lines`). Rust returns the records; Python writes the same manifest keys with the same record shapes (`field.keys.json`,
  42 keys over the three archetypes) and the same plan fields (`acres`, `envelope`, `net`, and on a comb `brook`), registers each
  footprint with the standing registry (strict, as every hamlet placer does), and files the returned segments in the settlement's
  water index for the stages after. The 6-number `fields[].plots` stays among the 42 keys: no free reader reads it (the free
  readers - `ways/geom.py`, `ways/bund.py`, the hinterland, the lane law - read `outline` and `plot_rings`), and the drawing reads
  the plot rings (D12), so Python writes it from the returned rings, a shape kept, not a reader served.
- **D2 - the single-field cap** (FR-018, SC-011): rolled in Rust by `pyrand::knob_rng(seed, "field_cap")`, uniform between 45 and 60
  ha (research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html#how-our-maps-size-a-settlements-farmland:
  "the cap rolled per settlement between about 45 and 60 ha", a knob), written to the meta and listed in
  `l7r/diagram/interactive/assets/choices.json`'s `not_choices` as a degree, not a form. A settlement whose paddy passes the cap
  draws ceil(paddy / cap) fields, each a comb of its own intake (0017: "a settlement with more farmland had several tracts"); not
  one of water_frame's knobs, so water_frame's accepted pin does not move. The cap holds for EVERY rice paddy field the stage draws,
  the polder's too (a diked rice paddy, the GM's "maximum size of a single rice paddy field" with no exception): a polder settlement
  past the cap draws several polders, each at most the cap. Within the polder's bounded n (10-20 households, 0019's GUESS) its paddy
  is at most about 10.5 ha (20 households at 1.3 acres, 0017's drawing page), under the cap's 45 ha floor, so the branch fires only
  if that range moves; it is unit-tested in the crate all the same. The dike-pond block's fish ponds are not a rice paddy and take
  no cap. SC-011's test rolls a comb settlement past the cap (`beyond_the_band()`, about 100 households) and finds several fields,
  each at most the cap.
- **D3 - the stage's own rolls and the gap's homes**: the knobs the stage rolls itself (`winter_crop`, `town_nearness`,
  `grave_form`, `fan_middle`, `paddy_rest`, `plot_regularity`, `weir_form`, `dry_furrows_vary`, `water_source` and its position;
  on a dike-pond `dike_crop`, `fry_form`, `leftover`, `land_use_overlay`, `dikepond_inset`, `dikepond_split`), the field's graves and
  the coarse-grain dry acres are counted as the stage's work OUTSIDE its derivations, charged to the stage as water_frame's outside
  rolls were (the round arbiter's ruling on ask:444-T19-outside-charges): each knob rolled in Rust from its table (passed from
  Python, as water_frame's are) by `knob_rng`, its count a key of its own, so MODE AUDIT reads them and neither pin moves.
- **D4 - the draws**: `pyrand::knob_rng` for every knob; each positional jitter seeded by the map's seed and the feature's own key
  (positional, so a change upstream re-rolls only what moved). Matching today's draws is not required (amendment 5); the pool
  hamlets the rebuild moves owe their settlement-reviews (the Occasions line).
- **D5 - the water index**: Rust's own index of 64 ft cells for the stage's placements (the derivations' Indexes, their cell size a CONVENTION of the
  index), each segment filed
  in the cells it crosses; the segments returned, and Python files them in the settlement's index for the stages after.
- **D6 - the counters** (FR-012, D9 of T19): one key a derivation row, `<kind>@<row>` (`write@basin`, `candidate@outline_cell`,
  `write@dike_tree` ...) and one a D3 roll, behind the `counters` feature; a seed rolled with the feature on and off writes identical
  manifests, recorded as `phases/field.fr012.md`.
- **D7 - every rule refused where it is decided**: each Keeps rule of both derivations - the basin's shape, its quarter-cell floor, its 25 degree
  headland and the arrowhead (research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html); the four-sided pond
  (research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html); the dike's band of 14-40 ft
  (research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html) - is held by the Rust that places the thing,
  a breach refused by name (`FieldRefused`, the rule in its message), and unit-tested in the crate and its Python driver. The Rust
  stage gate asks few finished-map checks of the field (most read lanes and houses), so the field's rules are held where decided.
- **D8 - the polder** (`phases/polder_greenfield.derivation.md`, pinned `field.polder`): both archetypes in Rust. The acreage rule is
  the derivation's - whole modules at or above the households' paddy (the 190 ft module of
  research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html, the paddy of
  research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html) - in place of today's
  band, so the 10-household polder grid that refuses on every seed today (`phases/polder.sizes.json`) lands a grid.
- **D9 - the 29 open claim findings** (FR-021): the field's 17 own files carry 493 claims, 21 DRIFTED and 8 MISLABELED
  (`phases/field.claims.json`, read from the claims index). Each rule the Rust makes again is claimed again in its doc comments; a
  DRIFTED finding is set right in the Rust (the dike's mulberry row, 0027, drawn with its willow row - today's map draws the willow
  alone, `phases/polder.dike.json`), a MISLABELED one claimed correctly. The landing is refused while one is open (FR-021).
- **D10 - deletion** (FR-005): the field's own Python - `hamletgen/water/` (comb, fit, polder, brook, brook_course, brook_rules),
  `settlement/fields/`'s placement (every PLACEMENT function of D12's table and the placement half of each MIXED method; the
  five DRAWING functions stay, and the MIXED ink moves to `settlement/fields/ink.py`) and `waterfields/` (carve, frame, ring_rules, trunks, seams) - deleted in the
  landing where nothing outside the field path imports it, found by `git grep -l` of each module's name (file names only, no held
  line read) and `make dead-closure`; a shared module (the overlap registry, the geometry indexes, the caches, the web's parts) stays.
  `water/skeleton.py` is water_frame's and stays. The list of what is deleted and what replaced is written in the landing's note.
- **D12 - the ink** (the round arbiter, ask:444-T16-ink-split; the classification `phases/field.md`, "Who draws the field"):
  the field's SVG stays Python's and reads only the records Rust returns (`net`'s plot rings with their fill and `low`, its
  channels, envelope, floor, dry plots, beans and bead ponds; the source; the feature records). The five DRAWING functions -
  `CombMixin.comb_base_fill`, `_comb_draw_beads`, `CombRecordMixin._draw_furrows`, `FieldFeaturesMixin.pond`,
  `_field_feature_ink` - are kept as they are. The eleven MIXED methods (`bund_junctions`, `draw_comb_field`, `_comb_draw_hem`,
  `_comb_draw_paddies`, `settle_beads`, `_comb_draw_source`, `_comb_draw_ditches`, `_plot_pond`, `_plot_rock`,
  `_plot_corner_grave`, `_plot_grave_island`) lose their placement half to Rust (the bund fillet's corners, the hem's and the
  beads' drowning tests, the rest roll, the ditch corridors, the features' seats and the grave's carving), and their ink is
  written NEW in `settlement/fields/ink.py` from the Rust records - the classes and paint the table lists, never lifted from the
  old bodies. A glyph whose mark changes owes glyph-check (the Occasions line). Every PLACEMENT function goes to Rust.
- **D11 - the order**: the comb first, `make rust-gate` as each increment's check (it judges `field` the moment `field.rs` holds
  `stage_field`), `make map GEN=pool/hamlets/inashiro/inashiro.gen.py` for the reference; then the polder; then `make work-budget`
  against 23,988 and 42,070 (exponent 0.79) and `field.polder`'s 4,651 and 6,584 (exponent 0.50), MODE AUDIT, the claims round
  (FR-021), the settlement-reviews of the moved pool hamlets - one landing.

### T16 Approach (2026-10-31T22:16Z)

Restated after D12 and the build (the Decisions re-decided at 19:37Z): the goal, constraints and exits of the first Approach stand.
What the build changed, each recorded at its point of change and in `phases/field.md`:

1. **The fork.** The division point is the brook-side head corner, not the head's middle, so the brook keeps its skirt with a head
   race of `head_lead` (0068's "along the upper edge" and "along the far edge"); canal A runs along the upper edge and down the far
   flank, canal B down the brook's flank.
2. **The comb drawn organic.** Waved flanks and bowed row lines (`fan.rs` `WAVES`, `lattice.rs` `BOW`, GUESS figures for the
   settlement-review), the dry hem on the canal's offset curves, the brook from off the canvas to off it, meandering, off the
   screen's axes - each held to the brook rules the sink asks (`brook_violations`, measured 119 of 120 seeds clean; seed 37 at 15
   households owed, since fixed: one meander carries the wander, and 180 seeds keep every brook rule).
3. **The polder's seam** (the plan review of 2026-10-31T22:2xZ, BLOCKED: a helper the field calls is the field's work). Every
   PLACEMENT the polder makes goes to Rust, `rust/phases/src/field/`: the block, lattice, parcels, ring canal, ditches, sluices and
   wild pond (built); the DIKE - its band 14-40 ft across (research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html), varying, its outer face curved with the water's edge, its crest, its
   gaps at the sluices, its willow row three quarters out at 8.5 ft (research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html) and its mulberry row a quarter out at 4.4 ft (research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html), cut
   at the gaps (`perimeter_dike`'s placement); the OUTFALL's course from the tail's sluice down the fall off the map, turning at most 55
   degrees a turn (research/questions/0060-field-drains-akusuiro.drawing.html; `outfall_run`'s); the RESTING plots' pick (0013; `resting_plots`'s); and the DIKE-POND's conversion - which
   parcels are ponds, rice or fry ponds, each pond's bank and water rounded from its parcel at the village's split, and the bank's
   crop rows (0018, 0020, 0023, 0026; `apply_land_use`'s). Python draws their records (`settlement/fields/ink.py`), as it draws
   the comb's. `marsh` stays Python because it DECIDES NOTHING: it fills, with its reed tile, exactly the polygon the Rust hands it
   (the fringe's ring, placed by the Rust - `polder.rs` `FRINGE_FT` - since the plan review of 2026-11-01), as `rest_basin` and `comb_base_fill` paint a ring they are given. The free
   helpers stay for the other tiers that call them; the field calls none of their placement.
4. **The deletion.** By name, `make dead-closure` against the clone's base; two pure moves on the round arbiter's rulings
   (ask:444-T16-move-drawing, ask:444-T16-brook-predicates) - drawing code (`settlement/fields/drawing.py`, D12's drawing functions) and check-side predicates (`brook_rules.WetLines`, `hem_on_water`), neither placing anything; the old engine's tests with it; the tests' `lay_comb` over the Rust comb.
5. **The order, unchanged.** After `water_frame`; the last of step 4.
6. **The exits.** Green, adding to the first Approach's Green (the budget met at 40 and 80 households, the old code deleted): `make rust-gate` green (54 seeds, 2026-10-31T22:01Z), FR-012 measured, the claims round to zero open
   (FR-021), MODE AUDIT WITHIN, the occasions' reviews, one landing. Red, over its budget: rebuilt again, or the budget raised with the GM's words (`make budget-change`) - never set down, never an arbiter's accept; a claims finding open in a file the landing changes refuses it until the claim or the code is fixed, or the research done (FR-021); only a process stop goes to `make arbiter-ask`, and a stop to assess goes to the GM.
### T16 Approach (2026-11-01T00:39Z)

The claims round's fixes (FR-021, the round arbiter's route (a) on `ask:444-T16-fr021-scope`), answered against the checklist's
part A after the Decisions of 19:37Z and the first wave's verdicts:

1. **The goal, in the world.** The comb and the polder the reader sees are the ones the record describes, line by line: a brook
   narrower than the race it feeds and never ruled straight past ten widths, a polder whose lines each bow on their own, ponds
   ringed by one bank's width, graves the paddy is carved round - every placement's claim true of its code.
2. **The constraints.** Each open finding in a file T16's delta changes (`make claims-report`, FR-021); the brook rules
   (`brook_violations`), the basin rules (`rules::held`), `make rust-gate`'s fresh block, `make quick`, `make static`'s line floor (every line covered).
3. **Where each comes from.** R, each at its page: ten widths (research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.html);
   the creek's width, the delivery's cap and the pond feeder (research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html);
   one inset a village (research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html); the halves short of the mound
   (research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html); tracts apart and rows a right angle apart
   (research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html); the climb (research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html);
   a crossing wherever both ends reach useful ground (research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html); on some maps
   (research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html). O: every GUESS the round
   labeled - the meander's wave, the grave's notch, the outfall's first leg, `WHOLE_IN`, `SEASONAL_IN`.
4. **Whether each holds here.** The ten-widths rule describes a natural brook on open ground, which is the hamlet's brook; the tap's
   straight stride had no page behind it (0059 says only that the brook runs on), so it meanders like the rest.
5. **The order.** The brook, then the fan cut away from it; the lattice, then the features carved from its plots; the parcels, then
   the ponds pushed in from them. No later placement moves an earlier one.
6. **The exits.** (a) the O meander wavelength moved (`MEANDER_WAVE_FT`, a GUESS) to meet R's ten widths; (c) the share-of-view rule replaced by a
   length, which dissolves the view-dependence; (e) conform for the inset, the cap and the notch. Red, over its budget: rebuilt again, or the budget raised with the GM's words (`make budget-change`) - never set down, never an arbiter's accept; a claims finding open in a file the landing changes refuses it until the claim or the code is fixed, or the research done (FR-021); only a process stop goes to `make arbiter-ask`, and a stop to assess goes to the GM.
7. **The search smell.** None added: every fix is a construction (a true inward offset, a fitted half-row, a tract's direction
   chosen from the allowed set, the trough at the intake); the one search left is `apart`'s scan of 70 candidate directions.
8. **The budget.** About three hours for the round's fixes and one wave (a GUESS, the round's own estimate); twice that is part B's trigger.
9. **Done, measured.** `make claims-report` lists no finding in a delta file; baseline: the first wave's 202 open findings at HEAD
   of 2026-10-31. One goal: the claims closed; the stale record sentences are found rows (0031, 0059, 0068, 0069).
10. **Before moving a constant.** `BROOK_DRAWN_W` (to the creek's width at research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html): read by `reserved_box`, `CROSSING_END_TOL`, `sink.drawn_brook`,
    `brook_course.drawn_course` and `field_stage.BROOK_W` (the drawn stroke and the brook's skirt spacing) - each measures the drawn
    brook, so each follows. `RULED_SHARE`/`RULED_MIN_LEN_FT`: the marsh's edges (`land/outline.py`, `tools/marsh_edges.py`) keep them.
11. **Before fitting things into room.** The basins (`ALONG_FT`, research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html): a half-row of breadth h
    holds from h over the band's top to h over its foot of them, rounded inward; where that range is empty the count nearest h over the
    band's middle is taken, a GUESS recorded at `cuts`.

### T16 Approach (2026-11-01T01:55Z)

The claims round's second wave (78 findings open in the port's files) answered, the part A items restated where they moved:

1. **The goal, in the world.** As at 00:39Z, and the intake where 0059 puts it: at a shoulder of the fan's head or straight into
   its middle (research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html,
   "at its left, its center or its right"), which main's comb rolled (`HEAD_OFFSETS`) and the Rust port had dropped.
2. **The constraints.** As at 00:39Z; and the fork, which the 22:16Z item 1 put at the brook-side head corner, now moves with the
   form: at that corner for a shoulder intake, at the head's middle for a middle one (`channels::division`).
3. **Where each comes from.** R: the three places (0059's drawing page); the 8-acre floor of an enclosed field
   (research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html); a delivery capped at 0.8 of its
   canal, the polder's columns too, and a pond feeder at twice the floor
   (research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html); the sweep's limits
   (research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html). O, each a GUESS where it stands: the
   1:2:1 odds (the page's own guess), the brook's swing from a middle intake (`CENTER_SWING_DEG`), the weir's key into the banks.
4. **Whether each holds here.** A middle intake needs a race long enough for the brook to swing out past the head's corner by its
   skirt, so the intake sits that far up the fall (`brook.rs`, the skirt over the swing's cosine).
5. **The order.** Unchanged: the brook and its intake, then the fan's channels from the fork they set.
6. **The exits.** (b) a principled form: the middle intake built rather than dropped, its race the length its geometry needs;
   (e) conform for the floor, the caps and the sweeps. Red, over its budget: rebuilt again, or the budget raised with the GM's
   words (`make budget-change`) - never set down, never an arbiter's accept; a claims finding open in a file the landing changes
   refuses it until the claim or the code is fixed, or the research done (FR-021); only a process stop goes to
   `make arbiter-ask`, and a stop to assess goes to the GM.
7. **The search smell.** None added: the middle intake is placed by construction.
8. **The budget.** About two hours for the second round's fixes and its wave (a GUESS, the round's own estimate).
9. **Done, measured.** `make claims-report` lists no finding in a delta file; baseline the second wave's 78. One goal: the claims
   closed. The overlap registry's own-pieces pass indexed on the way (the field's counted work, the work-budget audit's question):
   the brook's own pieces examined 200,474 pairs at 40 households and 3,294 after (measured 2026-11-01 (a scratch roll of seed 4's
   water frame and field, the counter per key)), `overlap/registry.py`.
10. **Before moving a constant.** `intake_place` is new; `WEIR_HALF_FT`'s use in the stage replaced by `WEIR_HALF`, derived from the
    drawn brook (the old half-length, `WEIR_HALF_FT`, spanned the brook twice over).
11. **Before fitting things into room.** The middle intake: the brook at the head's line stands past the corner by the skirt
    over the swing's cosine plus a station, so the race is that distance up the fall at the swing's slope.

### T16 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** The field stage made about 1.3M Python calls at 40 households and counted 48,335 to 66,214 operations over the four seeds, measured 2026-10-28 (`make work-budget`, `dev/work-budget/20261028T152105Z-45aa176ec9b8.json`), its counted work led by segment crossings, the standing registry's conflicts and segment distances; box 4 adds `make perf-profile` and `make perf-fanout`.
2. **Removes work, or only moves it?** Removes it: the comb's angles read once a row, the cut basins clipped by the water index, a sharp point cut off by rule before the basin is written - no carve, settle or weld pass after.
3. **What do you expect it to save, and why?** The counted operations from today's (item 1) to at most the pinned budget at 40 (`dev/work-budget.json`), and the calls with them, the repair passes gone.
4. **How does the work grow with the settlement?** The rebuild is held to the budget's exponent, the pinned one in `dev/work-budget.json`.
5. **What did the before and after show, and under what conditions?** Recorded at box 6: `make work-budget` and `make perf-ab` against main.
6. **Did any map move, and does it still keep the research?** Yes - every comb map's basins and ditches move; the Rust stage gate (FR-019), the claims round and settlement-review hold them to the research.



<!-- plan-archive: T17 to T17 moved to plan-done.md, 2026-10-30 (feature 375 FR-044) -->
<!-- plan-archive: T18 to T18 moved to plan-done.md, 2026-10-31 (feature 375 FR-044) -->
### T16 part B (2026-10-31T20:43Z)

The trigger: `make cohort` at 20:42Z on the comb in Rust - seeds 9 (`SeatRefused`), 903 (`row_rules`) and 905 (`SiteRefused`)
newly failing, 12 of 16 passing.

1. **What exactly is refusing?** Three Python stages after the field - the seating, the site boundary, the row rules - on a field
   the rebuild moved. No check of the field's own failed on those seeds.
2. **A3 again.** Amendment 5 (FR-019, FR-020; the GM 2026-10-31: "no Rust stage ever ends with any failing checks at the point
   where that stage has completed"): a Python stage after the Rust prefix that fails on a moved map is not the port's to tune.
3. **A4 again.** The Rust stage gate is the port's check: `make rust-gate` at 20:43Z failed one seed at the field (a dry plot on
   the brook), at 20:44Z four, each read in its record; fixed in the Rust that places the dry hem; at 20:45Z 57 seeds through
   water_frame and the field, the failing list and 3 frozen inputs among them, 0 failing (`dev/rust-gate/20261031T204546Z.json`).
4. **Moving something placed earlier to suit something later?** No: the field is not being bent to the seating.
5. **Tuning or changing?** Changing: the dry plot's water test made exact (a segment crossing it), the rule held where decided.
6. **The one-sentence test.** "The comb in Rust passes every check of its own on 57 seeds; the three cohort failures are later
   Python stages on a moved map, which amendment 5 leaves to their own ports."
7. **Done:** the hem's test fixed; the rest of T16 continues (the Python driver's tests, the polder, the deletion, the counts).
8. **Every route measured before the arbiter was asked?** No ruling asked: nothing here is a process stop.
9. **After a ruling, the step it named?** Not applicable.

### T16 part B (2026-11-01T00:41Z)

The trigger: the cohort at 2026-10-31T21:02Z - seeds 7, 9, 902 and 905 newly failing on the polder's seam's build.

1. **What exactly is refusing?** The same three Python stages after the field as at 20:42Z (the seating, the site boundary, the row
   rules) on maps the rebuilt field moved; no check of the field's own, and `make rust-gate` passes the same seeds through the
   Rust prefix (`dev/rust-gate/20261101T002811Z.json`, 54 seeds, 0 failing).
2. **A3 again.** Amendment 5 (FR-019, FR-020; the GM 2026-10-31: "no Rust stage ever ends with any failing checks at the point
   where that stage has completed"): a later Python stage's failure on a moved map is its own port's, not the field's to tune.
3. **A4 again.** The rule that refuses describes the later stage's room on the new field, not the field; the field's own rules
   hold at the places those seeds draw (the stage gate's record).
4. **Moving something placed earlier to suit something later?** No: the field is not being bent to the seating.
5. **Tuning or changing?** Neither on the field for these seeds: the claims round changes the field to its research, not to them.
6. **The one-sentence test.** "The field in Rust passes every check of its own; the cohort's failures are later Python stages on a
   moved map, which amendment 5 leaves to their ports (part B of the plan)."
7. **The next step is a measurement.** The claims wave's verdicts on the round's fixes, then the stage gate again on a fresh block.
8. **Every route measured before the arbiter was asked?** No ruling asked here: nothing is a process stop.
9. **After a ruling, the step it named?** The ruling on `ask:444-T16-fr021-scope` named route (a), taken: the incidental touches
   reverted, T23 filed, the findings in the port's files closed.

### T16 part B (2026-11-01T06:23Z)

The trigger: the cohort at 2026-11-01T06:22Z (`dev/cohort-log/20261101T062233Z-diagram-backlog-2743472.json`) - seeds 3, 4 and 9
newly failing at the seating ("no field margin turns its back to the NW wind clear of the dry hem, the toe and the canvas edge")
and 905 at the site, after the hem was bounded (ask:444-T16-hem-budget, route b).

1. **What exactly is refusing?** The seating (`cluster.seat_cluster`), a Python stage after the field: with the hem's side fixed
   once for the canal's course, every plot along a cleared head stands upslope of it, where before about half flipped onto the
   rice and were refused, leaving the head's margin bare by accident. `make rust-gate` passes the same field on 54 seeds
   (`dev/rust-gate/20261101T061056Z.json`, 0 failing).
2. **A3 again.** Amendment 5 (FR-019, FR-020; the GM 2026-10-31: "no Rust stage ever ends with any failing checks at the point
   where that stage has completed"): a later Python stage's failure on a moved map is its own port's, not the field's to tune.
3. **A4 again.** The rule that refuses is the seating's room beside the hem; the hem stands where research/questions/0006 puts
   it ("a hem of small rectangular plots just upslope of the supply canal that runs along the paddy's high edge"), the whole
   canal on a cleared middle.
4. **Moving something placed earlier to suit something later?** No: the hem is not bent to the seating; its accidental gaps
   are gone.
5. **Tuning or changing?** Neither for these seeds: the change was the hem's bound (the arbiter's ruling), not a seat.
6. **The one-sentence test.** "The field in Rust passes every check of its own; the hem now stands wholly where 0006 puts it,
   and the seating that needed its accidental gaps is the seating port's to meet (amendment 5)."
7. **The next step is a measurement.** The field's MODE BUDGET on the re-derived budget, then the stage gate on a fresh block;
   the seating's margin beside a full hem is noted for its port (`make speckit-todo`'s seat stage) and for the GM's review.
8. **Every route measured before the arbiter was asked?** No new ruling asked: nothing here is a process stop.
9. **After a ruling, the step it named?** The ruling on `ask:444-T16-hem-budget` named route (b): the hem re-derived and bounded,
   now before MODE BUDGET.

### T16 part B (2026-11-01T12:34Z)

The trigger: the cohort at 2026-11-01T12:33Z - seeds 4, 7, 9 and 901 at the seating and 905 at the site, the same five Python-stage
seeds the GM was told of on 444#1's answer, after the claims round's fifth fixes (`hem_bounds`, the merged deck re-tested) and the
MODE AUDIT's counters.

1. **What exactly is refusing?** Later Python stages: the seating (`cluster.seat_cluster`, SeatRefused on 4, 9 and 901), the web
   (7, a lane over a threshing yard) and the site (905). `make rust-gate` passes the field on 54 seeds
   (`dev/rust-gate/20261101T123253Z.json`, 0 failing).
2. **A3 again.** Amendment 5 (the GM 2026-11-01 on 444#1: "it's okay for the Python code to have errors since we will fix those
   when those stages are ported to Rust"): a later Python stage's failure on a moved map waits for its own port.
3. **A4 again.** The rule that refuses is the seating's room beside the hem; the hem stands where 0006 and 0011 put it.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither for these seeds: the changes were the claims' fixes and the counters, not a seat.
6. **The one-sentence test.** "The field in Rust passes every check of its own; the five seeds refuse in Python stages that
   amendment 5 leaves to their ports."
7. **The next step is a measurement.** The second MODE AUDIT on the counted field (42,440 at 40 against 27,238), then the landing.
8. **Every route measured before the arbiter was asked?** No new ruling asked: nothing here is a process stop.
9. **After a ruling, the step it named?** ask:444-T16-claims-round5 named the fifth pass and its fixes, done.

### T21 - the Rust stage gate and the failing-seed list (amendment 5, FR-019, FR-020; the GM 2026-10-31: "Yes, I agree with your proposals and refinements. Please write up that amendment and then implemente it.")

- **Approach**: the roll through the Rust stages alone, the checks asked by what they read, the seeds with no fixed block and the
  failing list with its frozen inputs, and the landing held to it - each pinned by a test (SC-012, SC-013).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| D1-D6 | each test red without its part | n/a (no map moves: the gate judges, it places nothing) | none | n/a |

### T21 Approach (2026-10-31T13:52Z)

1. **The goal, in the world.** No Rust stage ever ends with a failing check, on any seed; a seed that fails one is checked until
   it and the input its stage failed on both pass; the Python stages after the Rust ones refuse no Rust landing.
2. **The constraints.** FR-019, FR-020, SC-012, SC-013; feature 386's landing cohort unchanged for a landing that changes no Rust
   stage; the engine's checks unchanged in what they find (one list, read by both the cohort and the gate).
3. **Where each comes from.** G: the GM's words above and in `request.md` (amendment 5). O: the checks as `cohort_audit.roll_how`
   asks them (read 2026-10-31: refusals raised by name in the stages, and 14 finished-map checks).
4. **Do they describe the world here?** The Rust stages today are water_frame alone; the gate is tested on it and on stub stages.
5. **The order.** After amendment 5 (FAITHFUL); before T18 and T16, so the field port is the first judged by it.
6. **The exits.** Green: every test red without its part and green with it, `make rust-gate` passing on main's engine, `make done`
   and `make hooks-test` green, landed by `make land F=444 T=T21`. Red: what failed recorded and the task set down, a claim that
   it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The tests, and `make rust-gate`'s record on the landed engine with no failing seed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

**Performance work?** no.

### T21 Decisions

- **D1 - the Rust stages and a roll through them** (`hamletgen/rust_prefix.py`): a stage is Rust when `rust/phases/src/<stage>.rs`
  exists, derived; `off_the_front` names one that is not the front of `STAGES`, and the gate refuses then. `roll_through` runs the
  Rust stages on `driver.fresh_settlement` (split out of `build`, unchanged in what it does), stopping where they end, and returns
  a trace: each stage's input pickled as it started (its frozen input; measured 2026-10-31, a throwaway test: 5,838 bytes after
  water_frame, the field stage running on the restored copy) and the parts of the map it wrote. The checks are judged where EACH
  Rust stage completes (the GM: "at the point where that stage has completed"; the plan review of T21, round 2): the map after
  stage i - the next stage's frozen input, or the final map - by the checks the stages up to i own (D2). A stage that raises is
  charged with its own input; a failing check is charged to the FIRST stage at whose completion it fails, with that stage's input,
  so a later stage that rewrites a part cannot hide an earlier stage's failure. A check that reads only parts the fresh settlement
  held fails, if at all, at the first stage's completion and is that stage's. A check reading two stages' parts is the later one's
  to fail where both have written, so its fixture may hold the earlier stage's output - as FR-020 has it.
- **D2 - the checks asked by what they read** (`rust_prefix.Reads`, `held`; `rust_gate.judge`): a check's reads are recorded on the
  map (top-level parts and `meta.<key>`). A check counts at the gate when it read something and everything it read is either a part
  the Rust stages OWN - written by a Rust stage on any seed of the run, so a stage that wrote nothing on one seed is still judged
  on that empty output (D2b) - or a part the fresh settlement already HOLDS with content, an input it may read beside the Rust
  output (D2a); a check that reads a part only a later stage writes is that stage's and is not asked. Ownership is derived from the
  run's trace, never a hand table. A check is handed the map alone, and the plan reaches the map only as its `meta`, whose reads are
  recorded - so no check reads the plan unseen (pinned by `test_a_check_reaches_the_plan_only_through_the_recorded_meta`). The checks are one list, `cohort_audit.POST_CHECKS`, which `roll_how` reads too, each looked up
  by its name when asked.
- **D3 - the gate** (`tools/rust_gate.py`, `make rust-gate`): the fresh block of 48 from `cohort_gate.py fresh-seed`'s start - a hash of
  `ci.delta.engine_key_worktree`, which walks every engine path, `rust/**`'s `.rs` and Cargo files among them (`is_engine`, T17):
  a Rust-only change moves the start, pinned by `test_a_rust_only_change_moves_the_fresh_start` (the plan review, round 3) - the
  six pinned row variants on the next fresh seeds, and the failing list's seeds; a plan that cannot be rolled fails the first Rust
  stage (water_frame rolls the plan, T19). Each run is recorded in `dev/rust-gate/<utc>.json` with the engine key it rolled
  (`ci.delta.engine_key_worktree`); exit 1 on any failing seed or replay.
- **D4 - the failing list and its frozen inputs** (`dev/rust-gate/failing.json`, `dev/rust-gate/frozen/`): a failing seed is added
  with its stage, its first FAIL line and its frozen input; every run rolls it and replays the fixture into its stage and the Rust
  stages after; the entry leaves only when both pass, and its fixture with it. A fixture that no longer loads is a failure, never
  dropped silently.
- **D5 - the landing held to it** (`scripts/gates/cohort_gate.py`): every engine landing is refused without a `rust-gate` record at
  its engine with no failing seed; a landing that changes `rust/**` (against `origin/main`) reads its landing cohort's regressed
  seeds as notes, a rate - refusing nothing; any other landing keeps feature 386's cohort as it stands.
- **D6 - `make land` makes the record** (`scripts/land.py`): on an engine delta, where the record is owed, land runs `make rust-gate`
  and commits `dev/rust-gate/` - the record, the failing list and its fixtures - BEFORE it stops on a failing seed, so the list
  outlives a landing that goes no further.

### T21 part B (2026-10-31T14:46Z)

The trigger: two red gates in a row on T21's landing (14:32Z, 14:42Z), the tripwire ruled `continue` by the round arbiter
(red-gate@2026-10-31T14:42:03Z).

1. **What exactly is refusing?** First gate: `hooks-test` rust-tooling (`cohort_gate.py` reads `.rs` files and no row of
   `dev/rust-tooling.md` named it) and `test_census_matches_pin` (`rust_gate.py` reached `STAGES` through the package surface).
   Second gate: test-full's roll census (the gate's unit tests rolled real water_frame seeds in the test worker).
2. **A3 again.** The project's own rules, unchanged: every reader of `.rs` has its row; the package surface is pinned; the gate
   rolls no map of its own (constitution VI).
3. **A4 again.** Each refusal read in the gate's log.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither: each fixed where it failed, decided nothing new.
6. **The one-sentence test.** "T21's landing found three tooling misses of its own, each fixed."
7. **Done:** the row and its proof added; `STAGES` read from `hamletgen.driver`; the gate's tests on a stand-in water_frame,
   rostered as `InProcess` stubs in `tests/rolls.py`.
8. **Every route measured before the arbiter was asked?** The arbiter was asked by the tripwire, with each fix and its passing
   tests in hand.
9. **After a ruling, the step it named?** Yes: `make done` once more, through `make land F=444 T=T21`.

### T21 part B (2026-10-31T15:00Z)

The trigger: the third red gate in a row (14:56Z), ruled `continue` by the round arbiter (red-gate@2026-10-31T14:56:27Z).

1. **What exactly is refusing?** One test: `tests/test_operations_registry.py::test_every_entry_point_has_a_registry_row` -
   `l7r.diagram.tools.rust_gate` runs as `python3 -m` with no row in `_invocation.OPERATIONS`. The three earlier fixes held.
2. **A3 again.** The registry's rule, unchanged: every runnable tool names its make target.
3. **A4 again.** Read in the gate's log.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither: the row added (`rust-gate`, expensive), its claim re-checked IN-STEP.
6. **The one-sentence test.** "The gate's new tool needed its row in the operations registry."
7. **Done:** the row added, the registry test passing.
8. **Every route measured before the arbiter was asked?** The tripwire asked, with the fix and its passing test in hand.
9. **After a ruling, the step it named?** Yes: `make done` once more; one more fresh red is a process fault (how much new code
   lands before a single `make done`), per the ruling.

### T22 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T22 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T23 (the round arbiter's ruling on ask:444-T16-fr021-scope: T16's delta holds only the port's files, so the code its port leaves dead is deleted in a landing of its own)

- **Approach**: after T16 lands, `make dead-closure BASE=<T16's merge base>` lists what the field's port left with no caller; each name
  it lists is deleted with its tests, in a non-phase landing under the claims switch's report (feature 445). Measured at T16's landing:
  the names the arbiter's ruling lists (`plot_texture`, the old comb's pending slots, `_sharp_corners`, `_toward`, `CITY_TIER_SCALES`,
  the dead constants in `consts.py`, `consts_fields.py` and `consts_water.py`, `dike_crest`, the dead names in `waterfields/banks.py`,
  `frame.py`, `partition.py`, `polder.py` and `seams/pockets.py`), and `water_frame.rs` reaching the shared `counts.rs`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the deletion | each deleted name's test deleted with it; `make dead-closure` empty after | n/a (no live code moves) | none | n/a |

### T23 Approach (checklist part A)

1. **The goal, in the world.** No map changes: the engine sheds code no stage calls.
2. **The constraints.** The round arbiter's ruling on ask:444-T16-fr021-scope; the 100% coverage floor; FR-012 (no counter moves).
3. **Where each comes from.** G: the ruling, routed by the GM's FR-021 ("every Rust stage end its initial implementation with zero open claims"); O: `make dead-closure`'s list.
4. **Do they describe the world here?** `make dead-closure` lists only code no caller reaches, measured at T16's landing.
5. **The order.** After T16's landing, before T22.
6. **The exits.** Green: `make dead-closure` empty and `make done` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: a deletion by list.
8. **The budget.** One landing.
9. **Done, measured.** `make dead-closure` lists nothing T16's port left.
10. **Before moving a constant.** n/a: constants deleted, none moved.
11. **Before fitting things into room.** n/a.

**Performance work?** No.


### T24 (the round arbiter's ruling ask:444-T16-hem-cleared-reprice, 2026-11-01)

- **Approach**: the accepted field derivation (`phases/field_greenfield.derivation.md`) prices the dry hem on the winter crop's
  odds alone - 114 plots at 40. Commit 740aed0ec (T16's third claims round) made a cleared middle (`fan_middle`, 1 map in 4)
  lay one band along the whole canal whatever the need (0011). Measured 2026-11-01 by `make work-budget`
  (`dev/work-budget/20261101T085501Z-39d51a626dd7.json`): hem plots at 40 of 241, 119, 158 and 150 on seeds 4, 25, 39 and 47,
  mean about 167; the stage's total, 27,012 at 40 and 47,513 at 80, under the derivation's 27,238 and 49,631. At the
  derivation's next re-derivation, price the dry hem, the hem's laid plots, the outline by bands and the hem's registry share
  on `fan_middle`'s odds, and name the cleared-middle band in the contract's Writes. Not before: the arbiter forbade editing
  the derivation now (FR-013).
- **Two more rows** (the GM, 2026-11-01, on 444#6: "I go with option (a) - this is well within what we should consider
  acceptable, even if our original estimate was a bit off because of failing to count/consider/calculate everything."): the
  budget stands at 1.9 per thing of the derivation (118,739 at 40, 218,411 at 80; the whole roll 139,987 at 40). The same
  re-derivation prices the dry plots' furrow rows (`pt_test@furrows`, about 23,600 at 40, rows 5 ft apart, a GUESS) and the copy
  of every plot to the Python stages (`write@py_export`, about 18,200 at 40; it goes as those stages port to Rust).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T24 Approach (checklist part A)

1. **The goal, in the world.** No map change; the field's work budget prices the hem as the field lays it.
2. **The constraints.** FR-013 (a figure change re-owes a ruling), FR-014 (the typical case), FR-015 (the standing pin).
3. **Where each comes from.** R: 0011's drawing page (a cleared middle drawn only as the hem along the whole canal); O: the
   2026-11-01 work-budget record above.
4. **Do they describe the world here?** Measured on the four reference seeds, above.
5. **The order.** At the field derivation's next re-derivation, after T16 lands.
6. **The exits.** Green: a MODE BUDGET verdict on the re-priced rows. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The hem rows' expected plots at 40 within the measured mean's band.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

**Performance work?** No - a budget's arithmetic, not the code's.

