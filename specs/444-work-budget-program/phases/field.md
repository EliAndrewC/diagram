# Phase checklist - field (feature 444, T16)

The template's eight boxes (`.specify/templates/phase-checklist.md`), ticked in order with their evidence. Below them, the
phase's working record: what is measured, what is owed, and where to resume.

- [ ] 1. **Contract.** What the phase reads from the manifest and what it writes; the research claims that govern it (from the
  claims index); the cohort properties it must keep.
  Measured so far (2026-10-31): the keys the stage writes, on all three archetypes - `phases/field.keys.json` (42 keys: 28 on a
  comb, 19 on a polder grid, 26 on a dike-pond); the polder's record and point counts at 10 and 20 households -
  `phases/polder.bounds.json`. The plan fields the stage writes for later stages: `acres`, `envelope`, `net` (a dict of the irrigation network - the
  fork, channels, plots, threads, drain, dry plots and reserve, the bund beans, the graves' discs, the pocket pond; on a dike-pond the
  sluice, the dike's sluices and the floor) and, on a comb, `brook` (`field.keys.json` `plan_fields`). The claims that govern it:
  `phases/field.claims.json` - 493 research claims in the field's 17 own files (464 IN-STEP, 21 DRIFTED, 8 MISLABELED, read from
  the claims index, the code unread). Each is a decision the Rust makes again and claims again in its doc comments; the 29 open
  findings cannot be carried: under FR-021 the Rust lands with each set right.
- [ ] 2. **Minimal algorithm.** Pseudocode and its operation count, factor by factor (S7), written from the contract alone,
  before the current code's numbers are read, in the derivation template (`.specify/templates/derivation.md`: each factor's
  scope, value, reason and worst case, and the cheaper algorithms considered), copied to `phases/<stage>.derivation.md`.
  The comb: `phases/field_greenfield.derivation.md` (verdict-3 SOUND, T18, under the single-field cap). Owed: the POLDER's own
  greenfield derivation (the Approach's item 4) - the polder grid and the dike-pond - from 0019, 0022, 0026, 0027 and
  `polder.bounds.json`; and the GAP between the comb derivation's Contract and what the stage writes (below).
- [ ] 3. **Budget review, MODE BUDGET.** The `work-budget` agent's SOUND on the derivation (`make work-budget-bundle MODE=budget`);
  the budget and exponent pinned (`make budget-set`).
  The comb: pinned (23,988 at 40, exponent 0.79). The polder: pinned as `field.polder` (`dev/work-budget.json`), 4,651 at 10 and
  6,584 at 20 households, exponent 0.50, on the round arbiter's accept after two rounds (ask:444-polder-round-3; verdict-1 UNDERIVED,
  verdict-2 LOOSE, every finding closed); `phases/polder_greenfield.derivation.md`.
- [ ] 4. **Today's measurement.** `make work-budget` for the stage - its ratio to budget and its exponent; the hot chains from
  `make perf-fanout`.
  The before, on main's engine: `make perf LABEL=444-start SCALING=1` (`dev/perf-log/20261031T173305Z-444-start-diagram-backlog.json`):
  the field 0.24-0.35 s of a 1.4-2.1 s roll at 10 households, 0.51-1.19 s of 3.4-4.5 s at 20, 0.94-1.26 s of 6.3-7.6 s at 40
  (15-26% of the roll), its Python calls 0.29-0.48M, 0.56-1.03M and 1.0-1.3M (one 40-household seed 2.67 s, 2.35M calls);
  `make work-budget`'s field row (2026-10-31, `dev/work-budget/20261031T045730Z-67f90c16d2de.json`): 57,792 counted at 40 against
  the budget's 23,988 (2.4x). Owed: `make perf-fanout`'s hot chains.
- [ ] 5. **Rebuild.** Behind the manifest seam (`STAGES` in `driver.py`): the same input, the same output, no repair passes (S4);
  the old implementation deleted in the same landing, with no fallback path.
- [ ] 6. **Acceptance.** Basic operations at most the budget at 40 and 80 households and the exponent at most the budget's; every seed of
  the Rust stage gate passing where the Rust stages complete (`make rust-gate`, feature 444 FR-019; the whole-pipeline cohort a
  rate, refusing nothing); the phase's claims round IN-STEP; the reviews
  its occasions owe; `make perf-ab`'s time recorded, as a record and not a gate.
- [ ] 7. **Audit review, MODE AUDIT.** The `work-budget` agent's WITHIN on the landed code (`make work-budget-bundle MODE=audit`).
- [ ] 8. **Standing record updated.** `dev/work-budget.md`, for this phase and for the whole roll; the stage accepted.

## Working record

**Resume here:** (1) settle the two plot forms from the readers OUTSIDE the held set - which reader reads the manifest's 6-number
`fields[].plots`, and whether the held `settlement/fields/` files are the stage's placement or the drawing - before the Rust writes
either form; (2) then the comb, per "The comb's design, next" below. clippy's dead-code lint is EXPECTED to refuse
`rust/phases/src/comb/` until `fn stage_field` calls into it. T16 stays open (the round arbiter, ask:set-down-444-t16-session).


**The gap between the comb derivation and the stage's output** (`field.keys.json` against the derivation's Writes): besides the
brook, intake and weir, outline, basins, ditches, beans, wet/dry/flooded plots, hem, pocket pond and channel records, the stage
writes knobs it rolls itself (`meta.winter_crop`, `town_nearness`, `grave_form`, `fan_middle`, `paddy_rest`, `plot_regularity`,
`weir_form`, `dry_furrows_vary`, `water_source`, `water_source_position`; on a dike-pond `dike_crop`, `fry_form`, `leftover`,
`land_use_overlay`, `dikepond_inset`, `dikepond_split`), the field's graves (`field_graves`), the coarse-grain dry acres
(`meta.coarse_grain_*`), and on a polder its fabric (`dikes`, `marshes`, `planted_trees`, `pond`, `pond_layer`, `dikeponds`,
`land_use`). Each needs a home before the rebuild: in the comb's derivation (a re-derivation and a MODE BUDGET round), in the
polder's, or counted as rolls outside the derivation, as water_frame's were (ask:444-T19-outside-charges).

**The polder at its sizes today** (measured 2026-10-31, a throwaway test on seeds 4-6 at 10, 20 and 40 households,
`phases/polder.sizes.json`):
- a 10-household POLDER GRID refuses on every seed, in the field stage: "no polder grid of 190 px modules lands 13.0 acres within
  12%" - the 190 ft module (0022) too coarse to land a small polder's acreage within the band; the dike-pond's 160 ft paired
  module lands it (19-21 ponds). Under amendment 5 the Rust field must pass every seed: a fit to solve, room first (the root
  CLAUDE.md, "Room before packing") - the band or the module count is a knob to move, never a target to defend.
- NO POLDER EXISTS at 40 households: `plan_site` refuses both archetypes there (0019's GUESS, ten to twenty households a small
  polder). The derivation template asks totals at 20, 40 and 80 - a ruling is owed on how the polder is budgeted: at its own
  sizes (10 and 20), or at 40 and 80 as several polders under the single-field cap. A process question: the round arbiter's.
- at 20 households: a polder grid 48-65 plots, 515-530 trees on its dike; a dike-pond 37-38 ponds, 534-567 trees; at 10, a
  dike-pond 19-21 ponds, 419-424 trees.

**The order owed** (the advisor's review, 2026-10-31): the contract's plan fields and claims (box 1); the polder's greenfield
derivation and its MODE BUDGET (boxes 2-3, its own round subject, not field's); the gap's homes; `### T16 Decisions` (the
Python/Rust seam, the cap's knob rolled in Rust by `pyrand::knob_rng(seed, "field_cap")` and listed in `choices.json`, the
several-fields branch and SC-011's test, the water index, counters one key per derivation row, refusals by name in Rust for every
Keeps rule, which held files are deleted and which replaced - `git grep -l` and `make dead-closure`), then `make decide`; then the
Rust (`fn stage_field`, submodules under `rust/phases/src/field/`), `make rust-gate` as the increment check, `make work-budget`,
MODE AUDIT, the settlement-reviews of the moved pool hamlets, one landing. The old field code stays unread (the phase-source guard;
T19's plan review ruled a read of the old code NOT LEGITIMATE).

**The polder's budget, ruled** (the round arbiter, ask:444-polder-sizes, route a): the polder gets its own greenfield derivation,
its Bounds stating `a bounded n: households 10-20` (0019's GUESS), its totals at 10 and 20, the exponent fitted from 10 to 20, every
row written per module, per foot of dike or per pond; then its own MODE BUDGET round. The comb's pin and the field's acceptance at
40 and 80 stand. Room first for the 10-household grid's refusal: the 190 ft module stays (0022); the 12% band (a GUESS) is what may
move - a 4x4 grid gives 13.3 acres, within 2% of 13.0, so first see whether the band or the grid search's shape rules refuse it;
the derivation writes its own acreage rule (whole modules at or above the households' paddy). Tooling: `make work-budget-bundle`
takes the bounded n (landed, `sizes` in `scripts/reviews/work_budget_bundle.py`); OWED at the pin (box 3): `make budget-set` and
`make work-budget` taking it too, and how a form of the field stage carries a pin of its own (`dev/work-budget.json` holds one
entry a stage).

**The polder pinned, and its tooling** (2026-10-31): `make budget-set` takes a form of a stage (`<stage>.<form>`) at its
derivation's bounded n, its growth across that range, out of the program's sum at 40; `work_budget.missing_items` reads a form's
own `sizes`; `accepted_by` matches a form by its own name. These change `l7r/diagram/tools/work_budget.py` (engine), so they land
WITH T16, not alone: a `field.polder` entry on main without the reader would refuse every push. The residue the arbiter left
standing: the derivation's Writes line gives 0022's 160 by 320 ft parcel while its index row counts about one 160 ft module a pond -
do not edit it before the landing (the accept is bound to the text as pinned, FR-013); the rebuild's measurement settles it.

**Next (superseded by "Where it stands" below - the Decisions are CLEAR):** box 1's owed parts (the plan fields the stage writes; the claims governing each key); the gap's homes (the stage's own
knob rolls, the graves, the coarse-grain acres - a re-derivation of the comb, or outside rolls); then `### T16 Decisions` and
`make decide`.

**Where it stands (2026-10-31, late):** T16's Decisions CLEAR (plan review round 2, 18 decisions; one narrowing LEGITIMATE: the
dike-pond's fish ponds take no cap). One sample of every record the stage writes, on a comb and a dike-pond:
`phases/field.samples.json` (the basins' 6-number records, the fork, the hem's polylines, the channels in the manifest - `frm`/`to` -
and again in the plan's `net` - `pts`). NEXT: the Rust. Each record's MEANING is read from the stages that READ it (sink, cluster,
homesteads, the hinterland - read freely where not held) and from the samples, never from the field's own old code (held). Start
with the comb (D11): the area and the cap (D2), the brook and its intake, the outline, the comb's ditches and basins with their
rules held where decided (D7), the plots drawn apart, the beans, the hem and the pocket pond, the water index (D5) - `make
rust-gate` judging each increment once `rust/phases/src/field.rs` holds `fn stage_field`. Then the polder (D8). One landing.

**The Rust so far** (`rust/phases/src/comb/`, local to the clone, wired at the switch): `mod.rs` - the paddy (1.3 acres a
household, 0017), the single-field cap (uniform 45-60 ha from `knob_rng(seed, "field_cap")`) and the field count past it (D2);
`fan.rs` - the fan's envelope: its area the paddy, its length `fan_aspect` times its mean breadth, falling along `down_deg`, the
head (1 + 1/3) and the foot (1 - 1/3) of the mean breadth (the taper a labeled GUESS), its edge cut a point every 64 ft (a
CONVENTION). Both tested (`make rust-test`); clippy's dead-code lint refuses them until `stage_field` calls in.

**The comb's design, next** (the derivation's algorithm, made concrete; each figure's page named): on the fan's axes - u down the
fall from the fork (0) to the foot (L), s across it in [-1, 1] scaled by the half-breadth at u - the ROWS are lines across the fall
48 ft apart (a basin "about 48 ft across its canal", 0005), turned by the plan's `grain_drift` degrees; the CUTS are lines of fixed s
(so the bunds converge toward the drain, 0005), spaced at the head about 31 ft (the middle of "26 to 36 ft along it", 0005), each
crossing moved by positional jitter; an interior basin is the quadrilateral of four crossings (5 ops); an edge basin is clipped
against the envelope (its new corners only angle-tested), a corner under 25 degrees cut into a headland, a basin under a quarter of
the 1,488 sq ft cell joined to the neighbor it shares most bund with (0014), the arrowhead refused (0005). The CHANNELS (0053):
the head race from the intake to the fork, forking into two supply canals down the flanks; the drain down the low middle to the
foot's outfall; branches leaving the supply canals at the plan's `offtakes_a` and `offtakes_b` fractions, leaning downstream (0054),
each tapering from head to tail (0053), every turn on a sweep of about 2.5 channel widths (0054), no channel crossing another.

**Open before the records are written:** the field writes TWO plot forms - `net["plots"]` (dicts with a `poly`, read by
`sitegen/geom.py`'s area and `settlement/fields/landuse.py`) and the manifest's `fields[].plots` (6 numbers: width, height, center
x, center y and two more); which reader reads the 6-number form, and whether the held `settlement/fields/` files are the stage's
placement or the drawing (a renderer is not the stage's algorithm, and D10 deletes only the field's own placement code), is
settled from the readers outside the held set before the Rust writes either form.
