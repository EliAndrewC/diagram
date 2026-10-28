# Phase checklist - <stage> (feature 444)

Copy to `specs/444-work-budget-program/phases/<stage>.md` and tick each box, in order, as its step is done; each box carries
the evidence beside it (a path, a ledger row, a figure with its run). `make land` refuses a `phase: <stage>` task of feature 444
while this file is absent, short of any of the eight boxes, or holds one unticked (feature 443 FR-010). The steps are section 3 of
the design the GM approved on 2026-10-28 (`specs/443-work-budget-tooling/request.md`).

- [ ] 1. **Contract.** What the phase reads from the manifest and what it writes; the research claims that govern it (from the
  claims index); the cohort properties it must keep.
- [ ] 2. **Minimal algorithm.** Pseudocode and its operation count, factor by factor (S7), written from the contract alone,
  before the current code's numbers are read.
- [ ] 3. **Budget review, MODE BUDGET.** The `work-budget` agent's SOUND on the derivation (`make work-budget-bundle MODE=budget`);
  the budget and exponent pinned (`make budget-set`).
- [ ] 4. **Today's measurement.** `make work-budget` for the stage - its ratio to budget and its exponent; the hot chains from
  `make perf-fanout`.
- [ ] 5. **Rebuild.** Behind the manifest seam (`STAGES` in `driver.py`): the same input, the same output, no repair passes (S4);
  the old implementation deleted in the same landing, with no fallback path.
- [ ] 6. **Acceptance.** Basic operations at most the budget at 40 and 80 households and the exponent at most the budget's; `make
  cohort-landing` with no regressed seed and the fresh block's pass rate no worse; the phase's claims round IN-STEP; the reviews
  its occasions owe; `make perf-ab`'s time recorded, as a record and not a gate.
- [ ] 7. **Audit review, MODE AUDIT.** The `work-budget` agent's WITHIN on the landed code (`make work-budget-bundle MODE=audit`).
- [ ] 8. **Standing record updated.** `dev/work-budget.md`, for this phase and for the whole roll; the stage accepted.
