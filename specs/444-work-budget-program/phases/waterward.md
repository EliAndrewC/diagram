# Phase checklist - waterward (feature 444)

Copy to `specs/444-work-budget-program/phases/<stage>.md` and tick each box, in order, as its step is done; each box carries
the evidence beside it (a path, a ledger row, a figure with its run). `make land` refuses a `phase: <stage>` task of feature 444
while this file is absent, short of any of the eight boxes, or holds one unticked (feature 443 FR-010). The steps are section 3 of
the design the GM approved on 2026-10-28 (`specs/443-work-budget-tooling/request.md`).

- [x] 1. **Contract.** What the phase reads from the manifest and what it writes; the research claims that govern it (from the
  claims index); the cohort properties it must keep.
  Evidence: `phases/waterward_greenfield.derivation.md` (the valley form) and `phases/waterward_polder.derivation.md` (the polder form, its bounded n 10-20) ## Contract; the claims governing it - 0019, 0027, 0058, 0061, 0074 - held at the Rust that decides the strips (`rust/phases/src/waterward.rs`) and at the marsh's drawing (`settlement/land/wet.py`, `outline.py`); impl-drift rounds of 2026-11-04 IN-STEP
- [x] 2. **Minimal algorithm.** Pseudocode and its operation count, factor by factor (S7), written from the contract alone,
  before the current code's numbers are read, in the derivation template (`.specify/templates/derivation.md`: each factor's
  scope, value, reason and worst case, and the cheaper algorithms considered), copied to `phases/<stage>.derivation.md`.
  Evidence: the valley form's one test (`waterward_greenfield.derivation.md`, SOUND at verdict-1); the polder form derived for the first time at its bounded n (`waterward_polder.derivation.md`), as the field's polder is (ask:444-polder-sizes)
- [x] 3. **Budget review, MODE BUDGET.** The `work-budget` agent's SOUND on the derivation (`make work-budget-bundle MODE=budget`);
  the budget and exponent pinned (`make budget-set`).
  Evidence: the valley form SOUND (`waterward_greenfield.verdict-1.txt`), pinned at 1; the polder form SOUND twice blind (`waterward_polder.verdict-3.txt`, `-4.txt`), pinned at 17,813 / 24,059 at 10 / 20, exponent 0.43 (`make budget-set PHASE=waterward.polder`, 2026-11-04)
- [x] 4. **Today's measurement.** `make work-budget` for the stage - its ratio to budget and its exponent; the hot chains from
  `make perf-fanout`.
  Evidence: the valley rolls 0 at every size (`dev/work-budget.md`); the polder rolls (`make work-budget SPEC='{"field_archetype": "polder_grid"}' SIZES=10,20`, `dev/work-budget/20261104T151331Z-e9fe2a0101ab-spec.json`) 16,437 / 22,063 at 10 / 20, 0.92x the budget; `make perf-fanout STAGES=waterward`
- [x] 5. **Rebuild.** Behind the manifest seam (`STAGES` in `driver.py`): the same input, the same output, no repair passes (S4);
  the old implementation deleted in the same landing, with no fallback path. The old Python owes no coverage on the way out (feature
  448, the GM 2026-11-02: "We can relax that for the engine code at this pooint since that's going away"): `dev/coverage-exempt.json` names it, so no test is added only to cover a line of it; the landing's
  `make coverage-exempt PRUNE=1` drops its entries once the stage is accepted, and the stage's thin door keeps the floor.
  Evidence: `rust/phases/src/waterward.rs` (the flanks, the face, the fringe) behind `hamletgen/waterward_stage.py` (STAGES unchanged); the old `dike_face` and Python stage in `water/waterward.py` deleted, `waterward_flanks` asking the Rust; no fallback path
- [ ] 6. **Acceptance.** Basic operations at most the budget at 40 and 80 households - or at most twice it on the MODE AUDIT's
  LEEWAY, and work the derivation missed re-derived and raised (`make budget-set RAISE=1`), never squeezed (feature 444 FR-022) - and
  the exponent at most the budget's, with no leeway; every seed of
  the Rust stage gate passing where the Rust stages complete (`make rust-gate`, feature 444 FR-019; the whole-pipeline cohort a
  rate, refusing nothing); the phase's claims round IN-STEP, with no open claim finding in a file the landing changes (feature 444 FR-021, refused at `make land`); the reviews
  its occasions owe; `make perf-ab`'s time recorded, as a record and not a gate.
  Evidence: pending the MODE AUDIT; met so far - the polder form at 0.92x its budget at 10 and 20, exponent 0.43; `make rust-gate` 0 failing; the claims rounds IN-STEP on every changed file (2026-11-04: the flanks claim rewritten on 0019's drawing page; the sty's bank seat and the plank crossings fixed in the files the delta changes); no review owed; `make perf-ab`: the stage under 0.01 s
- [ ] 7. **Audit review, MODE AUDIT.** The `work-budget` agent's WITHIN, or LEEWAY, on the landed code (`make work-budget-bundle MODE=audit`).
  Evidence: pending: the MODE AUDIT of waterward.polder (round 2, after `waterward.audit-1.txt`'s UNCOUNTED)
- [ ] 8. **Standing record updated.** `dev/work-budget.md`, for this phase and for the whole roll; the stage accepted.
  Evidence: pending: the polder form's and the valley form's acceptance on that audit
