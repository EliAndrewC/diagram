# Phase checklist - homesteads (feature 444)

Copy to `specs/444-work-budget-program/phases/<stage>.md` and tick each box, in order, as its step is done; each box carries
the evidence beside it (a path, a ledger row, a figure with its run). `make land` refuses a `phase: <stage>` task of feature 444
while this file is absent, short of any of the eight boxes, or holds one unticked (feature 443 FR-010). The steps are section 3 of
the design the GM approved on 2026-10-28 (`specs/443-work-budget-tooling/request.md`).

- [x] 1. **Contract.** What the phase reads from the manifest and what it writes; the research claims that govern it (from the
  claims index); the cohort properties it must keep.
  Evidence: `phases/homesteads.map.md` (the stage mapped 2026-11-04: its reads, writes, algorithm, constants and repair passes) and `plan.md` T30 (D1-D5, decide CLEAR on round 2); the claims governing it - 0001, 0004, 0028-0040, 0043-0048, 0058, 0071, 0074, 0075, 0081, 0196, 0246, 0285 - to be held at the Rust that decides each; the cohort properties: every household seated or the site refused (0001), every house reached (the access tree), the Rust stage gate through the stage
- [ ] 2. **Minimal algorithm.** Pseudocode and its operation count, factor by factor (S7), written from the contract alone,
  before the current code's numbers are read, in the derivation template (`.specify/templates/derivation.md`: each factor's
  scope, value, reason and worst case, and the cheaper algorithms considered), copied to `phases/<stage>.derivation.md`.
  Evidence: pending: the stage's re-derivation for the whole stage under FR-022 rule 2 (`phases/homesteads_greenfield.derivation.md`)
- [ ] 3. **Budget review, MODE BUDGET.** The `work-budget` agent's SOUND on the derivation (`make work-budget-bundle MODE=budget`);
  the budget and exponent pinned (`make budget-set`).
  Evidence: pending: two blind MODE BUDGET SOUNDs; past ten times the first figure (4,118 at 40), the GM's words
- [x] 4. **Today's measurement.** `make work-budget` for the stage - its ratio to budget and its exponent; the hot chains from
  `make perf-fanout`.
  Evidence: before the rebuild, measured 2026-11-04 (`make work-budget`): 1,303,212 / 1,716,870 / 4,204,265 at 20 / 40 / 80, 416.9x the budget, exponent 0.84; 17,909,350 Python calls at 40. The rebuilt stage, measured 2026-11-05 (`make work-budget`, `dev/work-budget/20261105T143357Z-a0fc83819063.json`): 4,943,654 / 9,881,356 / 26,988,726 / 64,773,280 at 10 / 20 / 40 / 80, 6,553.8x the pinned 4,118 and 18.3x the re-derived 1,477,085, exponent 1.36; 9,621,301 Python calls at 40. On the way the audit's inefficiencies were fixed on their merits (the round arbiter on ask:444-homesteads-repin): the reach's canvas-wide reflood (2.83 billion at 40, then windowed and labeled once, as the derivation has it), the streams and the water rules asked of every course (indexed and box-filtered), the door's corridors asked a cell at a time (vectorized); the largest key left, the door's chain test, is 17% of the stage, under FR-022 rule 4's half
- [x] 5. **Rebuild.** Behind the manifest seam (`STAGES` in `driver.py`): the same input, the same output, no repair passes (S4);
  the old implementation deleted in the same landing, with no fallback path. The old Python owes no coverage on the way out (feature
  448, the GM 2026-11-02: "We can relax that for the engine code at this pooint since that's going away"): `dev/coverage-exempt.json` names it, so no test is added only to cover a line of it; the landing's
  `make coverage-exempt PRUNE=1` drops its entries once the stage is accepted, and the stage's thin door keeps the floor.
  Evidence: the whole stage in Rust behind the `homesteads/stages.py` door (D1): the nucleated growth (485a4ac58, 10114afde, 8b43568df), the dispersed farmstead and its bundle (245313025, 512273f74), the scattered rounds (5012cc76c), the row village (24c4b2f93, 93cb7e39e), the track out's turned gateways (852a81140); Rust the default for every form, the track out and the households' ways (98f28a8f8); the Python they replaced deleted to its dead closure with its tests (ab1677f26, `make dead-closure`); the port's account and its departures `phases/homesteads.port.md`. The landing waits on T27-T29 (444#9, 444#10)
- [ ] 6. **Acceptance.** Basic operations at most the budget at 40 and 80 households - or at most twice it on the MODE AUDIT's
  LEEWAY, and work the derivation missed re-derived and raised (`make budget-set RAISE=1`), never squeezed (feature 444 FR-022) - and
  the exponent at most the budget's, with no leeway; every seed of
  the Rust stage gate passing where the Rust stages complete (`make rust-gate`, feature 444 FR-019; the whole-pipeline cohort a
  rate, refusing nothing); the phase's claims round IN-STEP, with no open claim finding in a file the landing changes (feature 444 FR-021, refused at `make land`); the reviews
  its occasions owe; `make perf-ab`'s time recorded, as a record and not a gate.
  Evidence: pending
- [ ] 7. **Audit review, MODE AUDIT.** The `work-budget` agent's WITHIN, or LEEWAY, on the landed code (`make work-budget-bundle MODE=audit`).
  Evidence: pending
- [ ] 8. **Standing record updated.** `dev/work-budget.md`, for this phase and for the whole roll; the stage accepted.
  Evidence: pending
