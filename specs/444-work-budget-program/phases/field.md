# Phase checklist - field (feature 444, T16)

The template's eight boxes (`.specify/templates/phase-checklist.md`), ticked in order with their evidence. Below them, the
phase's working record: what is measured, what is owed, and where to resume.

- [ ] 1. **Contract.** What the phase reads from the manifest and what it writes; the research claims that govern it (from the
  claims index); the cohort properties it must keep.
  Measured so far (2026-10-31): the keys the stage writes, on all three archetypes - `phases/field.keys.json` (42 keys: 28 on a
  comb, 19 on a polder grid, 26 on a dike-pond); the polder's record and point counts at 10 and 20 households -
  `phases/polder.bounds.json`. Owed: the plan fields the stage writes for later stages (e.g. the brook, read by the seating), and
  the claims that govern each key.
- [ ] 2. **Minimal algorithm.** Pseudocode and its operation count, factor by factor (S7), written from the contract alone,
  before the current code's numbers are read, in the derivation template (`.specify/templates/derivation.md`: each factor's
  scope, value, reason and worst case, and the cheaper algorithms considered), copied to `phases/<stage>.derivation.md`.
  The comb: `phases/field_greenfield.derivation.md` (verdict-3 SOUND, T18, under the single-field cap). Owed: the POLDER's own
  greenfield derivation (the Approach's item 4) - the polder grid and the dike-pond - from 0019, 0022, 0026, 0027 and
  `polder.bounds.json`; and the GAP between the comb derivation's Contract and what the stage writes (below).
- [ ] 3. **Budget review, MODE BUDGET.** The `work-budget` agent's SOUND on the derivation (`make work-budget-bundle MODE=budget`);
  the budget and exponent pinned (`make budget-set`).
  The comb: pinned (23,988 at 40, exponent 0.79). The polder: owed.
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

## Working record (resume here)

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
