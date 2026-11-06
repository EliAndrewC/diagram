# Phase checklist - appurtenances (feature 444)

Copy to `specs/444-work-budget-program/phases/appurtenances.md` and tick each box, in order, as its step is done; each box carries
the evidence beside it (a path, a ledger row, a figure with its run). `make land` refuses a `phase: appurtenances` task of feature 444
while this file is absent, short of any of the eight boxes, or holds one unticked (feature 443 FR-010). The steps are section 3 of
the design the GM approved on 2026-10-28 (`specs/443-work-budget-tooling/request.md`).

- [x] 1. **Contract.** What the phase reads from the manifest and what it writes; the research claims that govern it (from the
  claims index); the cohort properties it must keep.
  Evidence: the stage reads the houses as seated (each lot's yard, beds, byre, shed, fixtures and well pocket, laid by the Rust seating, T30), the free ground and the registry of what stands (`well_at`), the water (`watered_by_open_water`), the crop's box, the reserved wood seats, the recorded track out, a row village's planned streets and its farms; it writes the communal wells (the cluster form among the houses, the lane-side form beside the track), a row's shared wells, each grove farm's own well or channel, the byres, the drawn fixtures and the retirement houses. Claims: 0196 (wells among the houses, a dwelling's wall within 80 ft, one to about ten households, off every lane), 0072 (not in the windbreak), 0031 (a scattered farm's channel or its own well), 0033 (a row's shared wells), 0004 and 0028 (the retirement house). Plan T33 D1-D7c.

- [x] 2. **Minimal algorithm.** Pseudocode and its operation count, factor by factor (S7), written from the contract alone,
  before the current code's numbers are read, in the derivation template (`.specify/templates/derivation.md`: each factor's
  scope, value, reason and worst case, and the cheaper algorithms considered), copied to `phases/appurtenances.derivation.md`.
  Evidence: `phases/appurtenances_greenfield.derivation.md` (the stage's greenfield derivation): 347 / 713 / 1,466 at 20 / 40 / 80

- [x] 3. **Budget review, MODE BUDGET.** The `work-budget` agent's SOUND on the derivation (`make work-budget-bundle MODE=budget`);
  the budget and exponent pinned (`make budget-set`).
  Evidence: `phases/appurtenances_greenfield.verdict-2.txt` SOUND, the first pin 713 at 40, exponent 1.04

- [x] 4. **Today's measurement.** `make work-budget` for the stage - its ratio to budget and its exponent; the hot chains from
  `make perf-fanout`.
  Evidence: measured 2026-11-06 (`make work-budget`, `dev/work-budget/20261106T064532Z-38c97ec4feb1.json`): 59,398 / 107,200 / 231,676 / 396,565 at 10 / 20 / 40 / 80, 324.9x the budget, exponent 0.94 - 38,000 to 213,000 of it at 40 the windbreak belt's polygon built for the well seating's ranking (`RingIndex.inside_many`), the rest the lattice sweep's distance tables and the registry's records

- [ ] 5. **Rebuild.** Behind the manifest seam (`STAGES` in `driver.py`): the same input, the same output, no repair passes (S4);
  the old implementation deleted in the same landing, with no fallback path. The old Python owes no coverage on the way out (feature
  448, the GM 2026-11-02: "We can relax that for the engine code at this pooint since that's going away"): `dev/coverage-exempt.json` names it, so no test is added only to cover a line of it; the landing's
  `make coverage-exempt PRUNE=1` drops its entries once the stage is accepted, and the stage's thin door keeps the floor.
- [ ] 6. **Acceptance.** Basic operations at most the budget at 40 and 80 households - or at most twice it on the MODE AUDIT's
  LEEWAY, and work the derivation missed re-derived and raised (`make budget-set RAISE=1`), never squeezed (feature 444 FR-022) - and
  the exponent at most the budget's, with no leeway; every seed of
  the Rust stage gate passing where the Rust stages complete (`make rust-gate`, feature 444 FR-019; the whole-pipeline cohort a
  rate, refusing nothing); the phase's claims round IN-STEP, with no open claim finding in a file the landing changes (feature 444 FR-021, refused at `make land`); the reviews
  its occasions owe; `make perf-ab`'s time recorded, as a record and not a gate.
- [ ] 7. **Audit review, MODE AUDIT.** The `work-budget` agent's WITHIN, or LEEWAY, on the landed code (`make work-budget-bundle MODE=audit`).
- [ ] 8. **Standing record updated.** `dev/work-budget.md`, for this phase and for the whole roll; the stage accepted.
