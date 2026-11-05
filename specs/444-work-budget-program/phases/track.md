# Phase checklist - track (feature 444)

Copy to `specs/444-work-budget-program/phases/track.md` and tick each box, in order, as its step is done; each box carries
the evidence beside it (a path, a ledger row, a figure with its run). `make land` refuses a `phase: track` task of feature 444
while this file is absent, short of any of the eight boxes, or holds one unticked (feature 443 FR-010). The steps are section 3 of
the design the GM approved on 2026-10-28 (`specs/443-work-budget-tooling/request.md`).

- [x] 1. **Contract.** What the phase reads from the manifest and what it writes; the research claims that govern it (from the
  claims index); the cohort properties it must keep.
  Evidence: the stage reads the recorded track out (`way_out_track`, chosen at the homesteads, T30) and - a row village - the first planned street (`_row_streets[0]`), its farms (`_row_street_farms[0]`), the houses' frames, the brook and its fords, and what `household_ways.track_inputs` gathers for the thread; it writes the connector lane(s) (`Settlement.lane`, `connector`, `worn`, the far run `run_on`). Claims: 0033 (the street runs on off the map as the road into it), 0035 (crossed at a ford, the shortest walk), 0081 (the track off the wet, out past the frame), 0084 (square at a ditch), 0246 (the connector after every house). Plan T32 D1-D4.

- [x] 2. **Minimal algorithm.** Pseudocode and its operation count, factor by factor (S7), written from the contract alone,
  before the current code's numbers are read, in the derivation template (`.specify/templates/derivation.md`: each factor's
  scope, value, reason and worst case, and the cheaper algorithms considered), copied to `phases/track.derivation.md`.
  Evidence: `phases/track_greenfield.derivation.md` (the stage's greenfield derivation, measured 2026-10-29 on the reference manifests): 157 a map at 20, 223 at 40; revised 2026-11-05 under FR-022 rule 2 for the stage after T30 (165 / 248 / 477 at 20 / 40 / 80)

- [x] 3. **Budget review, MODE BUDGET.** The `work-budget` agent's SOUND on the derivation (`make work-budget-bundle MODE=budget`);
  the budget and exponent pinned (`make budget-set`).
  Evidence: `phases/track_greenfield.verdict-2.txt` SOUND, the first pin 223 at 40; the revision `phases/track_greenfield.verdict-4.txt` SOUND (verdict-3 UNDERIVED on the registry's cells, fixed), raised to 248 at 40, exponent 0.77 (`make budget-set RAISE=1`, x1.11 the first)

- [x] 4. **Today's measurement.** `make work-budget` for the stage - its ratio to budget and its exponent; the hot chains from
  `make perf-fanout`.
  Evidence: measured 2026-11-05 (`make work-budget`, `dev/work-budget/20261105T183734Z-63e30741f4af.json`): 12,659 / 18,893 / 26,163 at 20 / 40 / 80, 84.7x the budget, exponent 0.52 - all of it the registry's records of the one lane drawn (`Standing.resync` 8,658, `Standing.ribbon` 7,523 at 40), the door's; the reference roll is nucleated, so the row road the stage still decides is not in it (the gate's pinned row variants roll it)

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
